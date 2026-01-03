import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.day_planner import DayPlanner
from core.memory_manager import MemoryManager
from db.db_goal_manager import DbGoalManager


class OthelloEngine:
    """Core planning surface for Magistus and API-less integrations.

    Thin wrapper around DayPlanner + shared managers so callers can import and
    use generate_today_plan/update_plan_item without HTTP semantics.
    """

    def __init__(
        self,
        *,
        goal_manager: Optional[DbGoalManager] = None,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:
        self.goal_manager = goal_manager or DbGoalManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.day_planner = DayPlanner(
            goal_manager=self.goal_manager,
            memory_manager=self.memory_manager,
        )
        root = Path(__file__).resolve().parent.parent
        self.reflection_dir = root / "data" / "reflections"
        self.reflection_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("OthelloEngine")

    # ------------------------------------------------------------------
    def generate_today_plan(self, mood_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return today's plan, keeping the cached plan stable for the day."""
        return self.day_planner.get_today_plan(mood_context=mood_context, force_regen=False)

    def rebuild_today_plan(self, mood_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Explicitly regenerate today's plan (used when context shifts)."""
        return self.day_planner.rebuild_today_plan(mood_context=mood_context)

    def update_plan_item(
        self,
        *,
        user_id: str,
        item_id: str,
        status: str,
        plan_date: Optional[str] = None,
        reason: Optional[str] = None,
        reschedule_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update lifecycle for a plan item and return the updated plan."""
        return self.day_planner.update_plan_item_status(
            user_id=user_id,
            item_id=item_id,
            status=status,
            plan_date=plan_date,
            reason=reason,
            reschedule_to=reschedule_to,
        )

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------
    def get_today_brief(self, mood_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        plan = self.generate_today_plan(mood_context=mood_context)
        return self.summarise_today_plan(plan)

    def summarise_today_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a deterministic tactical brief for voice/read-out."""
        sections = plan.get("sections", {})
        routines = sections.get("routines", []) or []
        priority_tasks = sections.get("goal_tasks", []) or []
        optional = sections.get("optional", []) or []

        routine_bits = []
        for r in routines:
            name = r.get("name") or "routine"
            variant = (r.get("variant") or "").lower()
            if variant in ("short", "micro"):
                variant_label = "condensed" if variant == "short" else "micro"
            elif variant == "full":
                variant_label = "full"
            else:
                variant_label = variant or ""
            if variant_label:
                routine_bits.append(f"{variant_label} {name.lower()}")
            else:
                routine_bits.append(name.lower())

        task_bits = [t.get("label", "") for t in priority_tasks][:2]
        backlog_note = "skip the backlog unless you have spare energy" if optional else "no backlog today"

        energy_load = self._describe_energy_load(priority_tasks)

        headline_parts: List[str] = []
        if routine_bits:
            headline_parts.append(", ".join(routine_bits))
        if task_bits:
            headline_parts.append("one or two focus blocks: " + "; ".join(task_bits))
        headline_parts.append(energy_load)
        headline_parts.append(backlog_note)
        headline = "; ".join([p for p in headline_parts if p])

        outline = self._build_outline(routines, priority_tasks)
        priority_list = [t.get("label", "") for t in priority_tasks]
        energy_explainer = self._energy_explainer(priority_tasks, plan.get("mood_context"))

        return {
            "headline": headline,
            "priority_list": priority_list,
            "outline": outline,
            "energy_load": energy_explainer,
            "backlog": backlog_note,
        }

    def _describe_energy_load(self, tasks: List[Dict[str, Any]]) -> str:
        heavy = sum(1 for t in tasks if t.get("effort") == "heavy")
        medium = sum(1 for t in tasks if t.get("effort") == "medium")
        if heavy >= 2:
            return "two heavy blocks"
        if heavy == 1 and medium >= 1:
            return "one heavy and one medium block"
        if heavy == 1:
            return "one heavy block"
        if medium >= 2:
            return "two medium blocks"
        if medium == 1:
            return "one medium block"
        return "light load"

    def _build_outline(self, routines: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> List[str]:
        outline: List[str] = []
        for r in routines:
            variant = r.get("variant") or ""
            name = r.get("name") or "routine"
            outline.append(f"{variant} {name}")
        for t in tasks:
            label = t.get("label", "")
            effort = t.get("effort", "")
            outline.append(f"{effort} focus: {label}")
        return outline

    def _energy_explainer(self, tasks: List[Dict[str, Any]], mood: Optional[Dict[str, Any]]) -> str:
        mood_score = (mood or {}).get("mood")
        fatigue = (mood or {}).get("fatigue")
        heavy = sum(1 for t in tasks if t.get("effort") == "heavy")
        medium = sum(1 for t in tasks if t.get("effort") == "medium")
        load = heavy * 2 + medium
        tone = "balanced" if load <= 2 else "demanding" if load >= 4 else "moderate"
        mood_note = "neutral energy" if mood_score is None else f"mood {mood_score}/10"
        fatigue_note = f"fatigue {fatigue}" if fatigue else "fatigue unknown"
        return f"Energy outlook: {tone}; {mood_note}; {fatigue_note}."

    # ------------------------------------------------------------------
    # Reflection
    # ------------------------------------------------------------------
    def generate_day_reflection(self, plan_date: Optional[str] = None, save: bool = True) -> Dict[str, Any]:
        target_date = date.fromisoformat(plan_date) if plan_date else date.today()
        plan = self.day_planner._load_plan(target_date) or self.generate_today_plan()
        reflection = self._build_reflection(plan, target_date)
        if save:
            self._save_reflection(target_date, reflection)
            self.memory_manager.append_memory(
                {
                    "type": "daily_reflection",
                    "content": f"Reflection for {target_date.isoformat()}: {reflection.get('summary', '')}",
                    "metadata": reflection,
                }
            )
        return reflection

    def _build_reflection(self, plan: Dict[str, Any], target_date: date) -> Dict[str, Any]:
        sections = plan.get("sections", {})
        routines = sections.get("routines", []) or []
        priority = sections.get("goal_tasks", []) or []
        optional = sections.get("optional", []) or []

        planned_priority = len(priority)
        completed_priority = sum(1 for t in priority if t.get("status") == "complete")
        optional_done = sum(1 for t in optional if t.get("status") == "complete")
        routine_run = [
            {
                "id": r.get("routine_id"),
                "name": r.get("name"),
                "variant": r.get("variant"),
                "status": r.get("status"),
            }
            for r in routines
        ]

        completion_rate = (completed_priority / planned_priority) if planned_priority else 0
        streak = self._compute_streak(target_date)
        rolling_rate = self._rolling_completion_rate(window_days=7, include_date=target_date)
        baseline = self._baseline_compare(today_rate=completion_rate, baseline=rolling_rate)

        summary_text = self._reflection_summary(completion_rate, planned_priority, completed_priority, streak, baseline)

        return {
            "date": target_date.isoformat(),
            "planned_priority": planned_priority,
            "completed_priority": completed_priority,
            "optional_completed": optional_done,
            "routines": routine_run,
            "completion_rate_priority": completion_rate,
            "streak_priority_all_done": streak,
            "rolling_7d_completion": rolling_rate,
            "baseline_comparison": baseline,
            "summary": summary_text,
        }

    def _compute_streak(self, target_date: date) -> int:
        global _REFLECTIONS_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _REFLECTIONS_DB_ONLY_WARNED:
                self.logger.warning("OthelloEngine: JSON reflections disabled in Phase-1 DB-only mode")
                _REFLECTIONS_DB_ONLY_WARNED = True
            return 0
        files = sorted(self.reflection_dir.glob("reflection_*.json"), reverse=True)
        streak = 0
        for path in files:
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                rate = data.get("completion_rate_priority") or 0
                planned = data.get("planned_priority") or 0
                if planned == 0:
                    continue
                if rate >= 0.99:
                    streak += 1
                else:
                    break
            except Exception:
                continue
        # include today only if file already present; otherwise streak is based on history
        return streak

    def _rolling_completion_rate(self, window_days: int, include_date: date) -> float:
        global _REFLECTIONS_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _REFLECTIONS_DB_ONLY_WARNED:
                self.logger.warning("OthelloEngine: JSON reflections disabled in Phase-1 DB-only mode")
                _REFLECTIONS_DB_ONLY_WARNED = True
            return 0.0
        cutoff = include_date - timedelta(days=window_days - 1)
        total_planned = 0
        total_done = 0
        for path in self.reflection_dir.glob("reflection_*.json"):
            try:
                date_str = path.stem.replace("reflection_", "")
                d = date.fromisoformat(date_str)
            except Exception:
                continue
            if d < cutoff or d > include_date:
                continue
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                total_planned += data.get("planned_priority", 0)
                total_done += data.get("completed_priority", 0)
            except Exception:
                continue
        if total_planned == 0:
            return 0.0
        return total_done / total_planned

    def _baseline_compare(self, today_rate: float, baseline: float) -> str:
        delta = today_rate - baseline
        if delta > 0.1:
            return "above_baseline"
        if delta < -0.1:
            return "below_baseline"
        return "inline"

    def _reflection_summary(
        self,
        completion_rate: float,
        planned_priority: int,
        completed_priority: int,
        streak: int,
        baseline: str,
    ) -> str:
        parts = []
        if planned_priority == 0:
            parts.append("No priority blocks were scheduled.")
        else:
            parts.append(f"Finished {completed_priority}/{planned_priority} priority blocks ({round(completion_rate*100)}%).")
        if streak >= 1:
            parts.append(f"Priority streak: {streak} days.")
        if baseline == "above_baseline":
            parts.append("Today was above your recent average.")
        elif baseline == "below_baseline":
            parts.append("Today was below your recent average.")
        else:
            parts.append("Today was in line with your recent days.")
        return " ".join(parts)

    def _save_reflection(self, target_date: date, reflection: Dict[str, Any]) -> None:
        path = self.reflection_dir / f"reflection_{target_date.isoformat()}.json"
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(reflection, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            self.logger.warning(f"OthelloEngine: failed to save reflection: {exc}")


__all__ = ["OthelloEngine"]

_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes")
_REFLECTIONS_DB_ONLY_WARNED = False
