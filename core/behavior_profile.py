import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.memory_manager import MemoryManager
from db import plan_repository


class BehaviorProfile:
    """Lightweight behavioural heuristics from recent daily plans and lifecycle logs.

    Computes simple aggregates (no ML):
    - Routine success/failure rates (last N days)
    - Skip frequency by kind and effort
    - Average throughput per effort band (heavy/medium/light)
    - Completion density by section_hint (morning/deep-work/evening/etc.)
    """

    def __init__(self, plan_dir: Path, memory_manager: Optional[MemoryManager] = None, user_id: str = "default") -> None:
        self.plan_dir = plan_dir
        self.memory_manager = memory_manager or MemoryManager()
        self.logger = logging.getLogger("BehaviorProfile")
        root = Path(__file__).resolve().parent.parent
        self.reflection_dir = root / "data" / "reflections"
        self.user_id = user_id

    # ------------------------------------------------------------------
    def build_profile(self, days: int = 7) -> Dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        plans = self._load_recent_plans(cutoff)
        profile = {
            "throughput_by_effort": {"heavy": 0, "medium": 0, "light": 0},
            "routine_stats": {},
            "skip_rate_by_kind": {},
            "section_density": {},
            "momentum": {},
        }

        if not plans:
            return profile

        effort_done = defaultdict(int)
        effort_days = set()
        routine_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"complete": 0, "attempts": 0})
        kind_counts = defaultdict(lambda: {"skip": 0, "attempts": 0})
        section_counts = defaultdict(lambda: {"complete": 0, "attempts": 0})

        for plan_date, plan in plans:
            effort_days.add(plan_date.date())
            sections = plan.get("sections", {})
            for section_name, entries in sections.items():
                for entry in entries or []:
                    status = entry.get("status", "planned")
                    section_hint = entry.get("section_hint", "any")
                    section_counts[section_hint]["attempts"] += 1
                    if status == "complete":
                        section_counts[section_hint]["complete"] += 1

                    if section_name == "routines":
                        routine_id = entry.get("routine_id") or entry.get("id")
                        routine_stats[routine_id]["attempts"] += 1
                        if status == "complete":
                            routine_stats[routine_id]["complete"] += 1
                        if status == "skipped":
                            kind_counts["routine"]["skip"] += 1
                        kind_counts["routine"]["attempts"] += 1
                        continue

                    # goal-related tasks
                    effort = entry.get("effort", "medium")
                    if status == "complete":
                        effort_done[effort] += 1
                    if status == "skipped":
                        kind_counts["goal_task"]["skip"] += 1
                    kind_counts["goal_task"]["attempts"] += 1

        days_observed = max(len(effort_days), 1)
        profile["throughput_by_effort"] = {
            band: max(0, round(effort_done.get(band, 0) / days_observed))
            for band in ("heavy", "medium", "light")
        }
        profile["routine_stats"] = {
            rid: {
                "success_rate": (vals["complete"] / vals["attempts"]) if vals["attempts"] else 0,
                "attempts": vals["attempts"],
            }
            for rid, vals in routine_stats.items()
        }
        profile["skip_rate_by_kind"] = {
            kind: (vals["skip"] / vals["attempts"]) if vals["attempts"] else 0
            for kind, vals in kind_counts.items()
        }
        profile["section_density"] = {
            sec: (vals["complete"] / vals["attempts"]) if vals["attempts"] else 0
            for sec, vals in section_counts.items()
        }

        # Momentum from reflections (streaks/baseline/light/heavy run)
        profile["momentum"] = self._derive_momentum()
        return profile

    # ------------------------------------------------------------------
    def _load_recent_plans(self, cutoff: datetime) -> List[tuple]:
        plans: List[tuple] = []
        # Prefer DB-backed plans
        try:
            rows = plan_repository.get_plans_since(self.user_id, cutoff.date())
            for row in rows:
                row["items"] = plan_repository.get_plan_items(row["id"])
                plan = self._hydrate_plan_from_db(row)
                plan_dt = datetime.combine(row.get("plan_date", date.today()), datetime.min.time())
                plans.append((plan_dt, plan))
        except Exception as exc:
            self.logger.warning(f"BehaviorProfile: failed to load DB plans: {exc}")

        if plans:
            return plans

        global _PLAN_FALLBACK_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _PLAN_FALLBACK_DB_ONLY_WARNED:
                self.logger.warning("BehaviorProfile: JSON plan fallback disabled in Phase-1 DB-only mode")
                _PLAN_FALLBACK_DB_ONLY_WARNED = True
            return []

        # Fallback to JSON snapshots
        try:
            for path in sorted(self.plan_dir.glob("plan_*.json")):
                try:
                    date_str = path.stem.replace("plan_", "")
                    plan_date = datetime.fromisoformat(date_str)
                except Exception:
                    continue
                if plan_date < cutoff:
                    continue
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    plans.append((plan_date, data))
        except Exception as exc:
            self.logger.warning(f"BehaviorProfile: failed to load plans: {exc}")
        return plans

    def _hydrate_plan_from_db(self, plan_row: Dict[str, Any]) -> Dict[str, Any]:
        items = plan_row.get("items", [])
        routines: Dict[str, Dict[str, Any]] = {}
        steps_by_parent: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        goal_tasks: List[Dict[str, Any]] = []
        optional: List[Dict[str, Any]] = []

        for row in items:
            item_type = row.get("type")
            metadata = row.get("metadata") or {}
            if item_type in ("routine", "routine_block"):
                routine = {**metadata}
                routine["id"] = row.get("item_id")
                routine["status"] = row.get("status", routine.get("status", "planned"))
                routine["type"] = routine.get("type") or item_type or "routine"
                routine["section_hint"] = row.get("section") or metadata.get("section_hint", "any")
                routines[routine["id"]] = routine
            elif item_type == "routine_step":
                parent_id = metadata.get("parent_id") or metadata.get("parent_item_id") or metadata.get("routine_id")
                step = {**metadata}
                step["id"] = row.get("item_id")
                step["status"] = row.get("status", step.get("status", "planned"))
                if parent_id:
                    steps_by_parent[parent_id].append(step)
            else:
                entry = {**metadata}
                entry["id"] = row.get("item_id")
                entry["status"] = row.get("status", entry.get("status", "planned"))
                entry["type"] = item_type or entry.get("type") or "goal_task"
                entry["section_hint"] = row.get("section") or entry.get("section_hint")
                if row.get("section") == "optional" or item_type in ("backlog", "optional") or entry.get("priority") == "optional":
                    optional.append(entry)
                else:
                    goal_tasks.append(entry)

        for routine_id, routine in routines.items():
            routine["steps"] = sorted(steps_by_parent.get(routine_id, []), key=lambda s: s.get("id", ""))

        return {
            "sections": {
                "routines": list(routines.values()),
                "goal_tasks": goal_tasks,
                "optional": optional,
            }
        }

    def _derive_momentum(self) -> Dict[str, Any]:
        momentum = {
            "priority_streak": 0,
            "rolling_completion": 0.0,
            "baseline_state": "unknown",
            "recent_misses": 0,
        }
        reflections = self._load_recent_reflections()
        if not reflections:
            return momentum

        momentum["priority_streak"] = self._streak_from_reflections(reflections)
        momentum["rolling_completion"] = self._rolling_from_reflections(reflections)
        momentum["baseline_state"] = self._baseline_from_reflections(reflections)
        momentum["recent_misses"] = sum(
            1 for ref in reflections[:3]
            if (ref.get("completion_rate_priority") or 0) < 0.5 and (ref.get("planned_priority") or 0) >= 1
        )
        return momentum

    def _load_recent_reflections(self, days: int = 14) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow().date() - timedelta(days=days)
        refs: List[Dict[str, Any]] = []
        global _REFLECTIONS_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _REFLECTIONS_DB_ONLY_WARNED:
                self.logger.warning("BehaviorProfile: JSON reflections disabled in Phase-1 DB-only mode")
                _REFLECTIONS_DB_ONLY_WARNED = True
            return refs
        if not self.reflection_dir.exists():
            return refs
        for path in sorted(self.reflection_dir.glob("reflection_*.json"), reverse=True):
            try:
                date_str = path.stem.replace("reflection_", "")
                d = datetime.fromisoformat(date_str).date()
            except Exception:
                continue
            if d < cutoff:
                continue
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                refs.append(data)
            except Exception:
                continue
        return refs

    def _streak_from_reflections(self, refs: List[Dict[str, Any]]) -> int:
        streak = 0
        for ref in refs:
            planned = ref.get("planned_priority") or 0
            rate = ref.get("completion_rate_priority") or 0
            if planned == 0:
                continue
            if rate >= 0.99:
                streak += 1
            else:
                break
        return streak

    def _rolling_from_reflections(self, refs: List[Dict[str, Any]]) -> float:
        total_planned = 0
        total_done = 0
        for ref in refs[:7]:
            total_planned += ref.get("planned_priority", 0)
            total_done += ref.get("completed_priority", 0)
        if total_planned == 0:
            return 0.0
        return total_done / total_planned

    def _baseline_from_reflections(self, refs: List[Dict[str, Any]]) -> str:
        if not refs:
            return "unknown"
        latest = refs[0]
        return latest.get("baseline_comparison") or "unknown"


__all__ = ["BehaviorProfile"]

_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes")
_PLAN_FALLBACK_DB_ONLY_WARNED = False
_REFLECTIONS_DB_ONLY_WARNED = False
