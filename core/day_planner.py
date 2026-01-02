import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from core.memory_manager import MemoryManager
from core.behavior_profile import BehaviorProfile
from db.db_goal_manager import DbGoalManager
from db import plan_repository
from db import routines_repository


DAY_TAGS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DEFAULT_CAPACITY = {"heavy": 2, "medium": 1, "light": 3}


@dataclass
class RoutineStep:
    id: str
    label: str
    approx_duration_min: Optional[int] = None
    energy_cost: str = "low"  # low|medium|high
    friction: str = "low"     # low|medium|high
    status: str = "planned"   # planned|complete|skipped|rescheduled


@dataclass
class RoutineVariant:
    id: str
    label: str
    approx_duration_min: Optional[int]
    energy_profile: str  # low|medium|high
    dependency_level: str = "low"  # low|medium|high; maps to alertness needed
    tags: List[str] = field(default_factory=list)
    steps: List[RoutineStep] = field(default_factory=list)


@dataclass
class Routine:
    id: str
    name: str
    active: bool = True
    tags: List[str] = field(default_factory=list)  # e.g., ["workday"], ["weekend"], ["recovery"]
    days: List[str] = field(default_factory=list)  # subset of DAY_TAGS
    variants: List[RoutineVariant] = field(default_factory=list)


class RoutineStore:
    """Lightweight JSON-backed routine storage with variant selection.

    A routine is a behavioural scaffold (not a rigid calendar). Each routine can
    expose multiple variants (full/short/micro) that the planner can pick based
    on mood, fatigue, tags, or time pressure.
    """

    def __init__(self, store_path: Optional[Path] = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.store_path = store_path or (root / "data" / "routines.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("RoutineStore")
        self.routines: List[Dict[str, Any]] = self._load_or_seed()

    # ------------------------------------------------------------------
    def _load_or_seed(self) -> List[Dict[str, Any]]:
        global _ROUTINES_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            # In DB-only mode, we don't load JSON routines.
            # Active routines are fetched per-user in get_active_routines.
            if not _ROUTINES_DB_ONLY_WARNED:
                self.logger.info("RoutineStore: JSON routines disabled in Phase-1 DB-only mode (using DB)")
                _ROUTINES_DB_ONLY_WARNED = True
            return []
        if self.store_path.exists():
            try:
                with self.store_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as exc:
                self.logger.warning(f"RoutineStore: failed to load routines file: {exc}")
        seeded = self._seed_examples()
        self._persist(seeded)
        return seeded

    def _persist(self, routines: List[Dict[str, Any]]) -> None:
        try:
            with self.store_path.open("w", encoding="utf-8") as f:
                json.dump(routines, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            self.logger.error(f"RoutineStore: failed to write routines: {exc}")

    def _seed_examples(self) -> List[Dict[str, Any]]:
        """Provide a small starter set so Magistus can use routines immediately."""
        return [
            {
                "id": "morning_reset",
                "name": "Morning Reset",
                "active": True,
                "tags": ["workday"],
                "days": ["mon", "tue", "wed", "thu", "fri"],
                "variants": [
                    {
                        "id": "full",
                        "label": "full",
                        "approx_duration_min": 40,
                        "energy_profile": "medium",
                        "dependency_level": "medium",
                        "tags": ["workday"],
                        "steps": [
                            {"id": "hydrate", "label": "Hydrate + light stretch", "approx_duration_min": 5, "energy_cost": "low", "friction": "low"},
                            {"id": "planning", "label": "10-minute intent + calendar skim", "approx_duration_min": 10, "energy_cost": "medium", "friction": "medium"},
                            {"id": "setup", "label": "Desk reset + open deep-work tool", "approx_duration_min": 10, "energy_cost": "medium", "friction": "medium"},
                            {"id": "warmup", "label": "Short focus warmup (breath / box breathing)", "approx_duration_min": 5, "energy_cost": "low", "friction": "low"}
                        ],
                    },
                    {
                        "id": "short",
                        "label": "short",
                        "approx_duration_min": 20,
                        "energy_profile": "low",
                        "dependency_level": "low",
                        "tags": ["workday", "time-pressed"],
                        "steps": [
                            {"id": "hydrate", "label": "Hydrate", "approx_duration_min": 2, "energy_cost": "low", "friction": "low"},
                            {"id": "planning", "label": "3-minute intent + pick one block", "approx_duration_min": 3, "energy_cost": "low", "friction": "low"},
                            {"id": "setup", "label": "Open today\'s main doc + block distractions", "approx_duration_min": 5, "energy_cost": "medium", "friction": "medium"}
                        ],
                    },
                    {
                        "id": "micro",
                        "label": "micro",
                        "approx_duration_min": 8,
                        "energy_profile": "low",
                        "dependency_level": "low",
                        "tags": ["recovery", "fatigue"],
                        "steps": [
                            {"id": "breathe", "label": "90-second breath reset", "approx_duration_min": 2, "energy_cost": "low", "friction": "low"},
                            {"id": "intent", "label": "Name one non-negotiable for the morning", "approx_duration_min": 2, "energy_cost": "low", "friction": "low"}
                        ],
                    },
                ],
            },
            {
                "id": "evening_winddown",
                "name": "Evening Wind-Down",
                "active": True,
                "tags": ["any"],
                "days": DAY_TAGS,
                "variants": [
                    {
                        "id": "full",
                        "label": "full",
                        "approx_duration_min": 30,
                        "energy_profile": "low",
                        "dependency_level": "low",
                        "tags": ["recovery", "workday"],
                        "steps": [
                            {"id": "tidy", "label": "Tidy workspace + pack for tomorrow", "approx_duration_min": 5, "energy_cost": "low", "friction": "low"},
                            {"id": "journal", "label": "5-minute reflection + wins", "approx_duration_min": 5, "energy_cost": "low", "friction": "low"},
                            {"id": "shutdown", "label": "Device dim + no-notifications", "approx_duration_min": 5, "energy_cost": "low", "friction": "low"}
                        ],
                    },
                    {
                        "id": "short",
                        "label": "short",
                        "approx_duration_min": 12,
                        "energy_profile": "low",
                        "dependency_level": "low",
                        "tags": ["fatigue", "time-pressed"],
                        "steps": [
                            {"id": "tidy", "label": "Quick tidy + pack one thing", "approx_duration_min": 3, "energy_cost": "low", "friction": "low"},
                            {"id": "journal", "label": "2 bullets: done + next", "approx_duration_min": 3, "energy_cost": "low", "friction": "low"}
                        ],
                    },
                ],
            },
        ]

    # ------------------------------------------------------------------
    def list_routines(self) -> List[Dict[str, Any]]:
        return list(self.routines)

    def _is_active_today(self, routine: Dict[str, Any], target_day: str, tags: Optional[List[str]]) -> bool:
        if not routine.get("active", True):
            return False
        allowed_days = routine.get("days") or []
        if allowed_days and target_day not in allowed_days:
            return False
        if tags:
            routine_tags = set(routine.get("tags", []))
            if routine_tags and not routine_tags.intersection(tags):
                return False
        return True

    def choose_variant(
        self,
        routine: Dict[str, Any],
        mood: Dict[str, Any],
        routine_history: Optional[Dict[str, Any]] = None,
        section_success: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Pick the most realistic variant given mood/fatigue/time pressure and past performance."""
        variants = routine.get("variants", []) or []
        if not variants:
            return None

        fatigue = (mood.get("fatigue") or "medium").lower()
        mood_score = mood.get("mood") or mood.get("energy") or 5
        time_pressure = bool(mood.get("time_pressure"))

        success_rate = (routine_history or {}).get("success_rate")

        def score_variant(v: Dict[str, Any]) -> int:
            score = 0
            energy_profile = (v.get("energy_profile") or "medium").lower()
            if fatigue == "high":
                score += 2 if energy_profile in ("low", "medium") else -2
            elif fatigue == "medium":
                score += 1
            else:
                score += 2 if energy_profile == "high" else 1

            if time_pressure and "time-pressed" in (v.get("tags") or []):
                score += 2
            if mood_score <= 3 and "fatigue" in (v.get("tags") or []):
                score += 2
            if mood_score >= 7 and energy_profile == "high":
                score += 1

            # Nudge based on past success: if a routine often fails, penalise ambitious variants
            if success_rate is not None:
                if success_rate < 0.5 and v.get("label") == "full":
                    score -= 3
                elif success_rate < 0.5 and energy_profile == "high":
                    score -= 2
                elif success_rate > 0.7 and energy_profile in ("medium", "high"):
                    score += 1
            if section_success is not None and section_success < 0.5 and energy_profile == "high":
                score -= 2
            return score

        sorted_variants = sorted(variants, key=score_variant, reverse=True)
        return sorted_variants[0]

    def get_active_routines(
        self,
        target_date: date,
        mood: Dict[str, Any],
        routine_stats: Optional[Dict[str, Any]] = None,
        section_stats: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        day_tag = DAY_TAGS[target_date.weekday()]
        tags = mood.get("day_tags") if isinstance(mood.get("day_tags"), list) else None
        active = []

        source_routines = self.routines
        if _PHASE1_DB_ONLY:
            if not user_id:
                raise ValueError("user_id required for routines in Phase1 DB-only mode")
            db_routines = routines_repository.list_routines_with_steps(user_id)
            source_routines = []
            for r in db_routines:
                if not r.get("enabled", True):
                    continue
                
                # Check schedule rule
                schedule = r.get("schedule_rule") or {}
                days = schedule.get("days")
                if isinstance(days, list):
                    if len(days) == 0:
                        continue
                    if day_tag not in days:
                        continue
                
                # Convert to bundle shape
                steps = []
                total_duration = 0
                for s in r.get("steps", []):
                    dur = s.get("est_minutes") or 0
                    total_duration += dur
                    steps.append({
                        "id": s["id"],
                        "label": s["title"],
                        "approx_duration_min": dur,
                        "energy_cost": s.get("energy") or "low",
                        "friction": "low"
                    })
                
                source_routines.append({
                    "id": r["id"],
                    "name": r["title"],
                    "active": True,
                    "tags": [], # Could map from DB if we had tags on routine
                    "days": days or [],
                    "schedule_rule": schedule,
                    "variants": [{
                        "id": "default",
                        "label": "default",
                        "approx_duration_min": total_duration,
                        "energy_profile": "medium", # Default
                        "dependency_level": "low",
                        "tags": [],
                        "steps": steps
                    }]
                })

        for routine in source_routines:
            if not _PHASE1_DB_ONLY and not self._is_active_today(routine, day_tag, tags):
                continue
            routine_id = routine.get("id")
            history = routine_stats.get(routine_id) if (routine_stats and routine_id) else None
            section_success = None
            if section_stats:
                for tag in routine.get("tags", []):
                    if tag in section_stats:
                        section_success = section_stats[tag]
                        break
            variant = self.choose_variant(routine, mood, history, section_success)
            if not variant:
                continue
            active.append({
                "routine_id": routine.get("id"),
                "name": routine.get("name"),
                "variant": variant,
                "section_hint": self._infer_section_hint(routine),
                "schedule_rule": routine.get("schedule_rule"),
            })
        return active

    def _infer_section_hint(self, routine: Dict[str, Any]) -> str:
        schedule = routine.get("schedule_rule", {})
        part = schedule.get("part_of_day")
        if part in ("morning", "afternoon", "evening", "night", "any"):
            if part == "night":
                return "evening"
            return part

        tags = routine.get("tags", [])
        if "morning" in tags:
            return "morning"
        if "evening" in tags:
            return "evening"
        return "any"


# ----------------------------------------------------------------------
# DayPlanner
# ----------------------------------------------------------------------


class DayPlanner:
    """Generate and persist the daily blended plan (routines + goal tasks).

    Schema notes (plan_items rows):
    - item_id: stable external identifier used by API/engine
    - type: routine | routine_step | goal_task | backlog
    - section_hint: e.g., "morning", "deep-work", "creative", "evening", "any"
    - status: "planned" | "complete" | "skipped" | "rescheduled"
    - effort: "heavy" | "medium" | "light" (goal tasks only)
    - energy_cost / friction: qualitative hints
    - goal_id/step_id for goal tasks; routine_id/variant for routines; steps for routine containers
    - optional: reschedule_to, reason (for skips), approx_duration_min

    Public entrypoints:
    - get_today_plan(user_id: str, mood_context: Optional[Dict], force_regen: bool = False)
    - update_plan_item_status(user_id: str, item_id: str, status: str, ...)
    - rebuild_today_plan(user_id: str, mood_context: Optional[Dict])
    """

    def __init__(
        self,
        goal_manager: Optional[DbGoalManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        routine_store: Optional[RoutineStore] = None,
        behavior_profile: Optional[BehaviorProfile] = None,
    ) -> None:
        self.goal_manager = goal_manager or DbGoalManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.routine_store = routine_store or RoutineStore()
        root = Path(__file__).resolve().parent.parent
        self.plan_dir = root / "data" / "day_plans"
        self.plan_dir.mkdir(parents=True, exist_ok=True)
        self.behavior_profile = behavior_profile or BehaviorProfile(self.plan_dir, self.memory_manager)
        self.logger = logging.getLogger("DayPlanner")

    def _normalize_user_id(self, user_id: str) -> str:
        uid = str(user_id or "").strip()
        if not uid:
            raise ValueError("user_id is required")
        return uid

    def _plan_cache_path(self, user_id: str, target_date: date) -> Path:
        # TODO: keep per-user cache partitioned by (user_id, date) to avoid cross-user bleed.
        safe_uid = re.sub(r"[^A-Za-z0-9_.-]+", "_", user_id)
        return self.plan_dir / f"plan_{safe_uid}_{target_date.isoformat()}.json"

    # ------------------------------------------------------------------
    def _is_snoozed_now(self, meta: Dict[str, Any], now_utc: datetime) -> bool:
        if not meta or not meta.get("snoozed_until"):
            return False
        ts = meta["snoozed_until"]
        try:
            # Handle ISO strings that might lack timezone or have Z
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt > now_utc
        except Exception:
            return False

    def _attach_next_action(self, plan: Dict[str, Any]) -> None:
        if not plan:
            return
        flat = self._flatten_plan_items(plan)
        plan["next_action"] = self._pick_next_action(flat, datetime.now(timezone.utc))

    def _pick_next_action(self, flat_items: List[Dict[str, Any]], now_utc: datetime) -> Optional[Dict[str, Any]]:
        candidates = []
        for item in flat_items:
            status = item.get("status", "planned")
            if status in ("complete", "skipped", "rescheduled"):
                continue
            if self._is_snoozed_now(item.get("metadata") or {}, now_utc):
                continue
            
            # Normalize item_id without mutating original
            item_id = item.get("item_id") or item.get("id")
            if not item_id:
                continue

            cand = dict(item)
            cand["item_id"] = item_id
            candidates.append(cand)
        
        if not candidates:
            return None

        # Sort: in_progress > planned
        # Then by type (steps > blocks)
        # Then by section hint (morning < afternoon < evening < any)
        section_order = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3, "any": 4}
        
        def sort_key(i):
            s = i.get("status", "planned")
            status_score = 0 if s == "in_progress" else 1
            
            # Prefer concrete items (routine_step, goal_task) over containers (routine)
            itype = i.get("type", "")
            type_score = 1 if itype == "routine" else 0

            sec = i.get("section") or i.get("section_hint") or "any"
            sec_score = section_order.get(sec, 99)
            
            # Tie-break with order_index if available, else push to end
            idx_raw = i.get("order_index")
            try:
                idx = int(idx_raw) if idx_raw is not None else 10**9
            except Exception:
                idx = 10**9
            
            # Final deterministic tie-break
            iid = str(i.get("item_id", ""))
            
            return (status_score, type_score, sec_score, idx, iid)

        candidates.sort(key=sort_key)
        return candidates[0]

    def get_today_plan(
        self,
        user_id: str,
        mood_context: Optional[Dict[str, Any]] = None,
        force_regen: bool = False,
    ) -> Dict[str, Any]:
        uid = self._normalize_user_id(user_id)
        today = date.today()
        plan = None
        
        if not force_regen:
            existing = self._load_plan(uid, today)
            if existing:
                appended_goal_tasks = self._append_persisted_goal_tasks(uid, today, existing)
                existing["_plan_source"] = existing.get("_plan_source") or "cache"
                persisted_existing = self._persist_plan(uid, today, existing)
                self._log_plan_structure(
                    today,
                    persisted_existing,
                    appended_goal_tasks=appended_goal_tasks,
                    source=persisted_existing.get("_plan_source", "cache"),
                )
                plan = persisted_existing

        if not plan:
            behavior_snapshot = self.behavior_profile.build_profile()
            plan = self._generate_plan(uid, today, mood_context or {}, behavior_snapshot)
            appended_goal_tasks = self._append_persisted_goal_tasks(uid, today, plan)
            persisted = self._persist_plan(uid, today, plan)
            persisted["_plan_source"] = "generated"
            self._log_plan_structure(today, persisted, appended_goal_tasks=appended_goal_tasks, source="generated")
            plan = persisted

        # Compute next action
        if plan:
            self._attach_next_action(plan)
            
        return plan

    def rebuild_today_plan(self, user_id: str, mood_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.get_today_plan(user_id, mood_context=mood_context, force_regen=True)

    # ------------------------------------------------------------------
    def _load_plan(self, user_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        uid = self._normalize_user_id(user_id)
        try:
            plan_row = plan_repository.get_plan_with_items(uid, target_date)
            if plan_row:
                plan = self._hydrate_plan_from_db(plan_row)
                plan["_plan_source"] = "db"
                return plan
        except Exception as exc:
            self.logger.warning(f"DayPlanner: failed to load DB plan for {target_date}: {exc}")

        global _PLAN_CACHE_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _PLAN_CACHE_DB_ONLY_WARNED:
                self.logger.warning("DayPlanner: JSON plan cache disabled in Phase-1 DB-only mode")
                _PLAN_CACHE_DB_ONLY_WARNED = True
            return None

        path = self._plan_cache_path(uid, target_date)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                plan = json.load(f)
                plan["_plan_source"] = "file"
                return plan
        except Exception as exc:
            self.logger.warning(f"DayPlanner: failed to load plan snapshot for {target_date}: {exc}")
            return None

    def _persist_plan(self, user_id: str, target_date: date, plan: Dict[str, Any]) -> Dict[str, Any]:
        generation_context = {**(plan.get("mood_context") or {}), "capacity_model": plan.get("capacity_model")}
        behavior_snapshot = plan.get("behavior_profile") or {}
        uid = self._normalize_user_id(user_id)
        try:
            plan_row = plan_repository.upsert_plan(
                user_id=uid,
                plan_date=target_date,
                generation_context=generation_context,
                behavior_snapshot=behavior_snapshot,
            )
            if plan_row and plan_row.get("id"):
                # Preserve existing statuses
                existing_items = plan_repository.get_plan_items(plan_row["id"])
                status_map = {}
                for item in existing_items:
                    iid = item.get("item_id")
                    if iid:
                        status_map[iid] = {
                            "status": item.get("status"),
                            "reschedule_to": item.get("reschedule_to"),
                            "skip_reason": item.get("skip_reason"),
                            "metadata": item.get("metadata") or {}
                        }

                items = self._flatten_plan_items(plan)
                
                # Apply preserved statuses
                for item in items:
                    iid = item.get("id")
                    if iid and iid in status_map:
                        prev = status_map[iid]
                        if prev["status"] != "planned":
                            item["status"] = prev["status"]
                        if prev["reschedule_to"]:
                            item["reschedule_to"] = prev["reschedule_to"]
                        if prev["skip_reason"] and item["status"] == "skipped":
                            item["reason"] = prev["skip_reason"]
                        
                        # Preserve snoozed_until and execution timestamps
                        prev_meta = prev["metadata"]
                        if prev_meta.get("snoozed_until") or prev_meta.get("started_at") or prev_meta.get("completed_at"):
                            item.setdefault("metadata", {})
                            if prev_meta.get("snoozed_until"):
                                item["metadata"]["snoozed_until"] = prev_meta["snoozed_until"]
                            if prev_meta.get("started_at"):
                                item["metadata"]["started_at"] = prev_meta["started_at"]
                            if prev_meta.get("completed_at"):
                                item["metadata"]["completed_at"] = prev_meta["completed_at"]

                plan_repository.replace_plan_items(plan_row["id"], items)
        except Exception as exc:
            self.logger.error(f"DayPlanner: failed to persist plan to DB for {target_date}: {exc}")

        path = self._plan_cache_path(uid, target_date)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            self.logger.error(f"DayPlanner: failed to persist plan snapshot for {target_date}: {exc}")
        return plan

    def _flatten_plan_items(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        sections = plan.get("sections", {})

        # Routine blocks and steps
        for routine in sections.get("routines", []):
            items.append({
                "id": routine.get("id"),
                "type": routine.get("type", "routine"),
                "section": routine.get("section_hint", "any"),
                "status": routine.get("status", "planned"),
                "priority": None,
                "effort": routine.get("approx_duration_min"),
                "energy": routine.get("energy_profile"),
                "metadata": {k: v for k, v in routine.items() if k != "steps"},
                "schedule_rule": routine.get("schedule_rule"),
            })
            for step in routine.get("steps", []):
                metadata = dict(step)
                metadata["parent_id"] = routine.get("id")
                items.append({
                    "id": step.get("id"),
                    "type": step.get("type", "routine_step"),
                    "section": routine.get("section_hint", "any"),
                    "status": step.get("status", "planned"),
                    "priority": None,
                    "effort": step.get("approx_duration_min"),
                    "energy": step.get("energy_cost"),
                    "metadata": metadata,
                    "reschedule_to": step.get("reschedule_to"),
                    "reason": step.get("reason"),
                    "order_index": step.get("order_index", 0),
                })

        # Goal tasks and optional/backlog entries
        for section_name in ("goal_tasks", "optional"):
            for entry in sections.get(section_name, []):
                items.append({
                    "id": entry.get("id"),
                    "type": entry.get("type") or ("goal_task" if section_name == "goal_tasks" else "backlog"),
                    "section": section_name,
                    "status": entry.get("status", "planned"),
                    "priority": entry.get("priority"),
                    "effort": entry.get("effort"),
                    "energy": entry.get("energy_cost"),
                    "metadata": entry,
                    "reschedule_to": entry.get("reschedule_to"),
                    "reason": entry.get("reason"),
                })

        return items

    def _hydrate_plan_from_db(self, plan_row: Dict[str, Any]) -> Dict[str, Any]:
        items = plan_row.get("items", [])
        routines: Dict[str, Dict[str, Any]] = {}
        steps_by_parent: Dict[str, List[Dict[str, Any]]] = {}
        goal_tasks: List[Dict[str, Any]] = []
        optional: List[Dict[str, Any]] = []

        for row in items:
            item_type = row.get("type")
            metadata = row.get("metadata") or {}
            if item_type in ("routine", "routine_block"):
                routine = {**metadata}
                routine["id"] = row.get("item_id")
                routine["item_id"] = row.get("item_id")
                routine["status"] = row.get("status", routine.get("status", "planned"))
                routine["type"] = routine.get("type") or item_type or "routine"
                routine["section_hint"] = row.get("section") or metadata.get("section_hint", "any")
                routine["energy_profile"] = row.get("energy") or metadata.get("energy_profile")
                routines[routine["id"]] = routine
            elif item_type == "routine_step":
                parent_id = metadata.get("parent_id") or metadata.get("parent_item_id") or metadata.get("routine_id")
                step = {**metadata}
                step["id"] = row.get("item_id")
                step["item_id"] = row.get("item_id")
                step["status"] = row.get("status", step.get("status", "planned"))
                step["type"] = "routine_step"
                step["section_hint"] = row.get("section") or step.get("section_hint")
                step["order_index"] = row.get("order_index") or metadata.get("order_index") or 0
                step["energy_cost"] = row.get("energy") or metadata.get("energy_cost")
                if parent_id:
                    steps_by_parent.setdefault(parent_id, []).append(step)
            else:
                entry = {**metadata}
                entry["id"] = row.get("item_id")
                entry["item_id"] = row.get("item_id")
                entry["status"] = row.get("status", entry.get("status", "planned"))
                entry["type"] = item_type or entry.get("type") or "goal_task"
                entry["section_hint"] = row.get("section") or entry.get("section_hint")
                entry["reschedule_to"] = row.get("reschedule_to") or entry.get("reschedule_to")
                entry["reason"] = row.get("skip_reason") or entry.get("reason")
                if row.get("priority") is not None:
                    entry["priority"] = row.get("priority")
                if row.get("effort"):
                    entry["effort"] = row.get("effort")
                if row.get("energy"):
                    entry["energy_cost"] = row.get("energy")

                if row.get("section") == "optional" or item_type in ("backlog", "optional") or entry.get("priority") == "optional":
                    optional.append(entry)
                else:
                    goal_tasks.append(entry)

        for routine_id, routine in routines.items():
            routine["steps"] = sorted(
                steps_by_parent.get(routine_id, []),
                key=lambda s: (s.get("order_index", 0), s.get("id", "")),
            )

        generation_context = plan_row.get("generation_context") or {}
        mood_context = {k: v for k, v in generation_context.items() if k != "capacity_model"}
        capacity_model = generation_context.get("capacity_model") or {}

        plan_date_value = plan_row.get("plan_date")
        created_at_value = plan_row.get("created_at")

        plan = {
            "date": plan_date_value.isoformat() if (plan_date_value is not None and hasattr(plan_date_value, "isoformat")) else str(plan_date_value or ""),
            "generated_at": (created_at_value.isoformat() + "Z") if (created_at_value is not None and hasattr(created_at_value, "isoformat")) else str(created_at_value or ""),
            "mood_context": mood_context,
            "capacity_model": capacity_model,
            "behavior_profile": plan_row.get("behavior_snapshot") or {},
            "sections": {
                "routines": list(routines.values()),
                "goal_tasks": goal_tasks,
                "optional": optional,
            },
        }
        return plan

    # ------------------------------------------------------------------
    def _generate_plan(
        self,
        user_id: str,
        target_date: date,
        mood: Dict[str, Any],
        behavior_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        mood_payload = self._normalise_mood(mood)
        routines = self._select_routines(user_id, target_date, mood_payload, behavior_snapshot)
        capacity = self._derive_capacity(mood_payload, behavior_snapshot)
        goal_tasks, optional = self._select_goal_tasks(user_id, capacity)

        plan = {
            "date": target_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "mood_context": mood_payload,
            "capacity_model": capacity,
            "behavior_profile": behavior_snapshot,
            "sections": {
                "routines": routines,
                "goal_tasks": goal_tasks,
                "optional": optional,
            },
        }
        try:
            self.logger.debug(
                "DayPlanner: generated base plan keys=%s goal_tasks_len=%s sample=%s",
                list(plan.keys()),
                len(goal_tasks),
                goal_tasks[0] if goal_tasks else None,
            )
        except Exception:
            pass
        return plan

    def _append_persisted_goal_tasks(self, user_id: str, target_date: date, plan: Dict[str, Any]) -> int:
        """Append planned goal_task rows (e.g., from insights) into today's plan.

        This bridges insight-applied plan items that live in plan_items and the
        freshly generated routine scaffold, so the UI always sees them.
        """
        uid = self._normalize_user_id(user_id)
        plan_row = plan_repository.get_plan_by_date(uid, target_date)
        if not plan_row or not plan_row.get("id"):
            self.logger.debug("DayPlanner: no plan row found for %s when merging persisted goal tasks", target_date)
            return 0

        sections = plan.setdefault("sections", {})
        goal_tasks = sections.setdefault("goal_tasks", [])
        existing_ids: Set[str] = {str(item.get("id")) for item in goal_tasks if item.get("id")}
        original_len = len(goal_tasks)

        appended = 0
        try:
            rows = plan_repository.get_plan_items(plan_row["id"])
        except Exception as exc:
            self.logger.warning("DayPlanner: failed to fetch persisted goal tasks for %s: %s", target_date, exc)
            return 0

        total_rows = len(rows)
        filtered_rows = 0
        appended_labels: List[str] = []
        ignore_statuses = {"done", "cancelled", "skipped"}

        for row in rows:
            item_type = (row.get("type") or "").lower()
            status_raw = row.get("status") or "planned"
            status = str(status_raw).lower()
            if item_type != "goal_task":
                continue
            if status in ignore_statuses:
                continue
            filtered_rows += 1

            metadata = row.get("metadata") or {}
            item_id = str(row.get("item_id") or row.get("id") or metadata.get("id") or "").strip()
            if not item_id or item_id in existing_ids:
                continue

            label = (
                metadata.get("label")
                or metadata.get("title")
                or metadata.get("description")
                or metadata.get("summary")
                or metadata.get("content")
            )

            entry = {**metadata}
            entry["id"] = item_id
            entry["item_id"] = item_id
            entry["type"] = "goal_task"
            entry["label"] = label or entry.get("label")
            entry["status"] = row.get("status", entry.get("status", "planned")) or "planned"
            entry["section_hint"] = row.get("section") or metadata.get("section_hint") or "any"
            entry["priority"] = row.get("priority") if row.get("priority") is not None else metadata.get("priority")
            entry["effort"] = row.get("effort") or metadata.get("effort")
            entry["energy_cost"] = row.get("energy") or metadata.get("energy_cost") or metadata.get("energy")
            entry["friction"] = metadata.get("friction", entry.get("friction"))
            entry["reschedule_to"] = row.get("reschedule_to") or metadata.get("reschedule_to")
            entry["reason"] = row.get("skip_reason") or metadata.get("reason")
            entry["metadata"] = {**metadata, "label": entry.get("label")}

            goal_tasks.append(entry)
            existing_ids.add(item_id)
            appended += 1
            appended_labels.append(entry.get("label"))

        self.logger.info(
            "DayPlanner: merged persisted goal_tasks for %s plan_id=%s rows=%s goal_rows=%s appended=%s list_len_before=%s list_len_after=%s labels=%s",
            target_date,
            plan_row.get("id"),
            total_rows,
            filtered_rows,
            appended,
            original_len,
            len(goal_tasks),
            appended_labels,
        )

        return appended

    def _log_plan_structure(
        self,
        target_date: date,
        plan: Dict[str, Any],
        *,
        appended_goal_tasks: int,
        source: str,
    ) -> None:
        sections = plan.get("sections", {})
        routines_count = len(sections.get("routines", []) or [])
        goal_tasks_count = len(sections.get("goal_tasks", []) or [])
        optional_count = len(sections.get("optional", []) or [])
        self.logger.info(
            "DayPlanner: plan ready for %s source=%s routines=%s goal_tasks=%s optional=%s appended_goal_tasks=%s",
            target_date,
            source,
            routines_count,
            goal_tasks_count,
            optional_count,
            appended_goal_tasks,
        )

    def _normalise_mood(self, mood: Dict[str, Any]) -> Dict[str, Any]:
        score = mood.get("mood") or mood.get("energy")
        try:
            score = int(score) if score is not None else 5
        except Exception:
            score = 5
        fatigue = (mood.get("fatigue") or "medium").lower()
        time_pressure = bool(mood.get("time_pressure"))
        return {
            "mood": max(1, min(10, score)),
            "fatigue": fatigue if fatigue in ("low", "medium", "high") else "medium",
            "time_pressure": time_pressure,
            "day_tags": mood.get("day_tags") if isinstance(mood.get("day_tags"), list) else None,
        }

    def _derive_capacity(self, mood: Dict[str, Any], behavior_snapshot: Dict[str, Any]) -> Dict[str, int]:
        capacity = DEFAULT_CAPACITY.copy()
        mood_score = mood.get("mood", 5)
        fatigue = mood.get("fatigue", "medium")
        if mood_score <= 3 or fatigue == "high":
            capacity["heavy"] = 1
            capacity["medium"] = 1
        elif mood_score >= 8 and fatigue == "low":
            capacity["heavy"] = 2
            capacity["medium"] = 2

        throughput = behavior_snapshot.get("throughput_by_effort", {}) if behavior_snapshot else {}
        for effort in ("heavy", "medium", "light"):
            past = throughput.get(effort)
            if past is None:
                continue
            realistic = max(1 if effort != "light" else 2, past + 1)
            capacity[effort] = min(capacity.get(effort, realistic), realistic)

        momentum = behavior_snapshot.get("momentum", {}) if behavior_snapshot else {}
        streak = momentum.get("priority_streak", 0)
        baseline_state = momentum.get("baseline_state")
        misses = momentum.get("recent_misses", 0)

        # If user is on a streak and not below baseline, allow a small bump
        if streak >= 3 and baseline_state != "below_baseline":
            capacity["medium"] = min(capacity.get("medium", 1) + 1, 3)
            capacity["heavy"] = min(capacity.get("heavy", 1) + 1, 3)

        # If recent misses, lighten slightly but keep at least one priority block
        if misses >= 2 or baseline_state == "below_baseline":
            capacity["heavy"] = max(1, capacity.get("heavy", 1) - 1)
            capacity["medium"] = max(1, capacity.get("medium", 1) - 0)
            capacity["light"] = max(1, capacity.get("light", 2))
        return capacity

    def _select_routines(self, user_id: str, target_date: date, mood: Dict[str, Any], behavior_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        selected = []
        routine_stats = (behavior_snapshot or {}).get("routine_stats", {})
        section_stats = (behavior_snapshot or {}).get("section_density", {})
        active = self.routine_store.get_active_routines(target_date, mood, routine_stats, section_stats, user_id=user_id)
        for idx, bundle in enumerate(active):
            variant = bundle["variant"]
            steps = []
            for step_idx, step in enumerate(variant.get("steps", [])):
                # Ensure step has item_id equal to id for UI actions
                sid = f"routine-{bundle['routine_id']}-variant-{variant.get('id')}-step-{step.get('id')}"
                steps.append({
                    "id": sid,
                    "item_id": sid,
                    "label": step.get("label"),
                    "status": "planned",
                    "type": "routine_step",
                    "energy_cost": step.get("energy_cost", "low"),
                    "friction": step.get("friction", "low"),
                    "approx_duration_min": step.get("approx_duration_min"),
                    "order_index": step_idx,
                    "metadata": {"template_step_id": step.get("id")},
                })
            
            rid = f"routine-{bundle['routine_id']}-variant-{variant.get('id')}"
            selected.append({
                "id": rid,
                "item_id": rid,
                "routine_id": bundle.get("routine_id"),
                "name": bundle.get("name"),
                "variant": variant.get("label"),
                "section_hint": bundle.get("section_hint", "any"),
                "type": "routine",
                "status": "planned",
                "energy_profile": variant.get("energy_profile", "medium"),
                "dependency_level": variant.get("dependency_level", "medium"),
                "approx_duration_min": variant.get("approx_duration_min"),
                "steps": steps,
                "success_bias": routine_stats.get(bundle.get("routine_id"), {}),
            })
        return selected

    def _select_goal_tasks(
        self, user_id: str, capacity: Dict[str, int]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        uid = self._normalize_user_id(user_id)
        goals = self.goal_manager.list_goals(uid)
        candidates: List[Dict[str, Any]] = []
        for goal in goals:
            if goal.get("status") not in (None, "active", "in_progress"):
                continue
            goal_id = goal.get("id")
            if goal_id is None:
                continue
            steps = self.goal_manager.get_all_plan_steps(uid, goal_id)
            for step in steps:
                if step.get("status") == "done":
                    continue
                score = self._score_task(goal, step)
                candidates.append({
                    "goal_id": goal_id,
                    "step_id": step.get("id"),
                    "description": step.get("description", ""),
                    "status": step.get("status", "pending"),
                    "due_date": step.get("due_date"),
                    "priority": goal.get("priority", "medium"),
                    "score": score,
                    "step_index": step.get("step_index", 0),
                })
        candidates.sort(key=lambda c: (c["score"], -c.get("step_index", 0)), reverse=True)

        selected: List[Dict[str, Any]] = []
        optional: List[Dict[str, Any]] = []
        used = {"heavy": 0, "medium": 0, "light": 0}
        for item in candidates:
            effort = self._estimate_effort(item)
            if used[effort] < capacity.get(effort, 0):
                used[effort] += 1
                selected.append(self._plan_entry_from_task(item, effort, priority=True))
            elif len(optional) < 2:
                optional.append(self._plan_entry_from_task(item, effort, priority=False))
            if len(selected) >= 3:
                break
        return selected, optional

    def _score_task(self, goal: Dict[str, Any], step: Dict[str, Any]) -> int:
        score = 0
        priority = goal.get("priority", "medium")
        if isinstance(priority, str):
            pr = priority.lower()
            score += 3 if pr == "high" else 1 if pr == "medium" else 0
        else:
            try:
                score += int(priority)
            except Exception:
                score += 1
        due = step.get("due_date")
        if due:
            score += 2
        if step.get("status") == "in_progress":
            score += 2
        score -= step.get("step_index", 0) * 0.1
        return int(score)

    def _estimate_effort(self, step: Dict[str, Any]) -> str:
        text = step.get("description", "")
        length = len(text)
        if length > 160:
            return "heavy"
        if length > 80:
            return "medium"
        return "light"

    def _plan_entry_from_task(self, item: Dict[str, Any], effort: str, priority: bool) -> Dict[str, Any]:
        return {
            "id": f"goal-{item['goal_id']}-step-{item['step_id']}",
            "type": "goal_task",
            "goal_id": item["goal_id"],
            "step_id": item["step_id"],
            "label": item.get("description", ""),
            "status": "planned",
            "priority": "priority" if priority else "optional",
            "effort": effort,
            "section_hint": "deep-work" if effort in ("heavy", "medium") else "any",
            "energy_cost": "medium" if effort == "medium" else "high" if effort == "heavy" else "low",
            "friction": "medium" if effort != "light" else "low",
        }

    def snooze_plan_item(
        self,
        user_id: str,
        item_id: str,
        snooze_minutes: int,
        plan_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Snoozes a plan item by setting 'snoozed_until' in metadata.
        """
        target_date = date.fromisoformat(plan_date) if plan_date else date.today()
        uid = self._normalize_user_id(user_id)
        
        plan_row = plan_repository.get_plan_by_date(uid, target_date)
        if not plan_row:
            raise ValueError(f"No plan stored for {target_date}")

        if snooze_minutes <= 0:
            snooze_until = None
        else:
            # Use timezone-aware UTC and write ISO with Z
            snooze_until = datetime.now(timezone.utc) + timedelta(minutes=snooze_minutes)
            snooze_until = snooze_until.isoformat().replace("+00:00", "Z")
        
        # Update metadata
        plan_repository.update_plan_item_metadata(
            plan_row["id"], 
            item_id, 
            {"snoozed_until": snooze_until}
        )
        
        plan = self._load_plan(uid, target_date)
        if plan:
            self._attach_next_action(plan)
            return plan
        return self.get_today_plan(user_id, mood_context=None, force_regen=False)

    # ------------------------------------------------------------------
    def update_plan_item_status(
        self,
        user_id: str,
        item_id: str,
        status: str,
        *,
        plan_date: Optional[str] = None,
        reason: Optional[str] = None,
        reschedule_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        allowed_statuses = {"planned", "in_progress", "complete", "skipped", "rescheduled"}
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status '{status}'. Allowed: {sorted(allowed_statuses)}")
        target_date = date.fromisoformat(plan_date) if plan_date else date.today()
        if status == "rescheduled" and not reschedule_to:
            reschedule_to = (target_date + timedelta(days=1)).isoformat()

        if status != "rescheduled":
            reschedule_to = None
        if status != "skipped":
            reason = None
        if status in ("complete", "in_progress"):
            reason = None
            reschedule_to = None

        uid = self._normalize_user_id(user_id)
        plan_row = plan_repository.get_plan_by_date(uid, target_date)
        if not plan_row:
            raise ValueError(f"No plan stored for {target_date} to update")

        existing_item = plan_repository.get_plan_item(plan_row["id"], item_id)
        if not existing_item:
            raise ValueError(f"Item {item_id} not found in plan for {target_date}")

        current_status = existing_item.get("status", "planned")
        if current_status == "complete" and status != "complete":
            raise ValueError(f"Cannot transition from complete to {status}")

        # Only apply side effects (snooze clear, timestamps) on actual status transition
        metadata_update = {}
        if status != current_status:
            metadata_update["snoozed_until"] = None
            
            now_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            existing_meta = existing_item.get("metadata") or {}
            
            if status == "in_progress":
                if not existing_meta.get("started_at"):
                    metadata_update["started_at"] = now_ts
            elif status == "complete":
                metadata_update["completed_at"] = now_ts
                # If completing without ever starting, mark started_at = now
                if not existing_meta.get("started_at"):
                    metadata_update["started_at"] = now_ts
            elif status == "planned":
                if existing_meta.get("completed_at"):
                    metadata_update["completed_at"] = None

        updated_row = plan_repository.update_plan_item_status(
            plan_row["id"],
            item_id,
            status,
            skip_reason=reason,
            reschedule_to=reschedule_to,
            metadata=metadata_update if metadata_update else None
        )
        if not updated_row:
            raise ValueError(f"Failed to update item {item_id} for {target_date}")

        if status == "complete" and updated_row.get("type") == "goal_task":
            metadata = updated_row.get("metadata") or {}
            self._mark_goal_step_complete(uid, metadata)

        plan = self._load_plan(uid, target_date) or {}
        if plan:
            self._attach_next_action(plan)
        
        entry, section_name, _ = self._find_item(plan, item_id)

        self._log_lifecycle(
            plan_date=target_date,
            item_id=item_id,
            status=status,
            reason=reason,
            section=section_name,
            entry=entry,
        )
        return plan

    def _find_item(self, plan: Dict[str, Any], item_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[Dict[str, Any]]]:
        for section_name in ("routines", "goal_tasks", "optional"):
            section = plan.get("sections", {}).get(section_name, [])
            for entry in section:
                if entry.get("id") == item_id:
                    return entry, section_name, None
                for step in entry.get("steps", []):
                    if step.get("id") == item_id:
                        return step, section_name, entry
        return None, None, None

    def _mark_goal_step_complete(self, user_id: str, entry: Dict[str, Any]) -> None:
        goal_id = entry.get("goal_id")
        step_id = entry.get("step_id")
        if goal_id is None or step_id is None:
            return
        try:
            uid = self._normalize_user_id(user_id)
            self.goal_manager.update_plan_step_status(uid, goal_id, step_id, "done")
        except Exception as exc:
            self.logger.warning(f"DayPlanner: failed to mark goal step done (goal={goal_id}, step={step_id}): {exc}")

    def _log_lifecycle(
        self,
        plan_date: date,
        item_id: str,
        status: str,
        reason: Optional[str],
        section: Optional[str] = None,
        entry: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = {
            "type": "daily_plan_update",
            "content": f"Plan item {item_id} marked {status} on {plan_date.isoformat()}",
            "metadata": {
                "plan_date": plan_date.isoformat(),
                "item_id": item_id,
                "status": status,
                "reason": reason,
                "section": section,
                "effort": (entry or {}).get("effort"),
                "section_hint": (entry or {}).get("section_hint"),
                "kind": section,
                "reschedule_to": (entry or {}).get("reschedule_to"),
            },
        }
        try:
            self.memory_manager.append_memory(payload)
        except Exception as exc:
            self.logger.warning(f"DayPlanner: failed to log lifecycle update: {exc}")


__all__ = [
    "DayPlanner",
    "RoutineStore",
    "Routine",
    "RoutineVariant",
    "RoutineStep",
]

_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes", "on")
_ROUTINES_DB_ONLY_WARNED = False
_PLAN_CACHE_DB_ONLY_WARNED = False
