# Evidence Bundle: Routine System State

## 1. Repo Proof: Current Data Source
**File:** `data/routines.json`
**Status:** Exists. Contains static routine definitions.
```json
[
  {
    "id": "morning_reset",
    "name": "Morning Reset",
    "active": true,
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
          {
            "id": "hydrate",
            "label": "Hydrate + light stretch",
            "approx_duration_min": 5,
            "energy_cost": "low",
            "friction": "low"
          },
          ...
```

## 2. Phase 1 Toggles
**File:** `api.py`
**Status:** `OTHELLO_PHASE1_DB_ONLY` forces DB-only mode, but `RoutineStore` has a specific check for it.
```python
def _is_phase1_enabled() -> bool:
    phase = (os.environ.get("OTHELLO_PHASE") or "").strip().lower()
    if phase == "phase1":
        return True
    return _is_truthy_env(os.environ.get("OTHELLO_PHASE1"))

_PHASE1_ENABLED = _is_phase1_enabled()
if _PHASE1_ENABLED:
    os.environ["OTHELLO_PHASE1_DB_ONLY"] = "1"
```

**File:** `core/day_planner.py`
**Status:** `RoutineStore` explicitly disables itself if `_PHASE1_DB_ONLY` is set.
```python
    def _load_or_seed(self) -> List[Dict[str, Any]]:
        global _ROUTINES_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _ROUTINES_DB_ONLY_WARNED:
                self.logger.warning("RoutineStore: JSON routines disabled in Phase-1 DB-only mode")
                _ROUTINES_DB_ONLY_WARNED = True
            return []
```

## 3. Routine Storage (Backend)
**File:** `core/day_planner.py`
**Status:** `RoutineStore` is a JSON-backed class.
```python
class RoutineStore:
    """Lightweight JSON-backed routine storage with variant selection."""

    def __init__(self, store_path: Optional[Path] = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.store_path = store_path or (root / "data" / "routines.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("RoutineStore")
        self.routines: List[Dict[str, Any]] = self._load_or_seed()
```

## 4. Today Planner Engine
**File:** `core/day_planner.py`
**Status:** `_select_routines` picks from `RoutineStore`. `_hydrate_plan_from_db` reconstructs plan items from DB rows.
```python
    def _select_routines(self, target_date: date, mood: Dict[str, Any], behavior_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        selected = []
        # ...
        active = self.routine_store.get_active_routines(target_date, mood, routine_stats, section_stats)
        for idx, bundle in enumerate(active):
            # ... constructs routine items ...
        return selected

    def _hydrate_plan_from_db(self, plan_row: Dict[str, Any]) -> Dict[str, Any]:
        items = plan_row.get("items", [])
        # ...
        for row in items:
            item_type = row.get("type")
            if item_type in ("routine", "routine_block"):
                # ... hydrates routine items ...
```

## 5. API Routes
**File:** `api.py`
**Status:** `/api/today-plan` calls `day_planner.get_today_plan`.
```python
@app.route("/api/today-plan", methods=["GET"])
@require_auth
def get_today_plan():
    # ...
    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            mood_context=mood_context,
            force_regen=False,
        )
        # ...
        return jsonify({"plan": plan})
```

## 6. UI Rendering
**File:** `othello_ui.html`
**Status:** `renderPlannerSections` handles `routines` array from the plan JSON.
```javascript
    function renderPlannerSections(plan, goalTasksOverride = null) {
      const sections = (plan.sections || {});
      const routines = sections.routines || [];
      // ...
      if (!routines.length) {
        plannerRoutinesList.innerHTML = `<div class="planner-empty">No routines planned yet.</div>`;
      } else {
        routines.forEach(item => {
          // ... renders routine blocks and steps ...
        });
      }
      // ...
    }

    async function loadTodayPlanner() {
      // ...
      try {
        const [brief, plan] = await Promise.all([fetchTodayBrief(), fetchTodayPlan()]);
        // ...
        renderPlannerSections(plan, goalTasks);
        // ...
      }
      // ...
    }
```

## 7. DB Schema
**File:** `db/schema.sql`
**Status:** Contains `plans`, `plan_items`, `goals`, but **NO** `routine_templates` or `routine_variants` tables.
```sql
-- ============================================================================
-- OTHELLO DATABASE SCHEMA (FULL REPLACEMENT)
-- ============================================================================
-- ...
-- GOALS
-- PLAN STEPS
-- GOAL EVENTS
-- SUGGESTIONS
-- ... (No routine tables found)
```
