# EVIDENCE BUNDLE: Routines -> Today Planner Workflow

## A) Repo Context

### Directory Structure (Depth 3)
```text
Z:\Othello
├── api.py
├── core
│   ├── day_planner.py
│   ├── ...
├── db
│   ├── database.py
│   ├── plan_repository.py
│   ├── routines_repository.py
│   ├── ...
├── othello_ui.html
├── ...
```

- **Backend Entry:** `api.py`
- **Frontend Entry:** `othello_ui.html`

---

## B) API Evidence (`api.py`)

### 1. Auth Gate
```python
[api.py]
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authed"):
            return api_error("UNAUTHORIZED", "Not authenticated", 401)
        return f(*args, **kwargs)
    return decorated

def _get_user_id_or_error():
    if not session.get("authed"):
        return None, api_error("UNAUTHORIZED", "Not authenticated", 401)
    user_id = session.get("user_id")
    if not user_id:
        return None, api_error("UNAUTHORIZED", "No user_id in session", 401)
    return user_id, None
```

### 2. Today Planner Routes
```python
[api.py]
@app.route("/api/today-plan", methods=["GET"])
@require_auth
def get_today_plan():
    """Return today's blended plan of routines + focused goal tasks.

    Query params (optional):
        mood: int 1-10 (energy)
        fatigue: low|medium|high
        time_pressure: truthy flag
    """
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    args = request.args or {}
    mood_context = {
        "mood": args.get("mood"),
        "fatigue": args.get("fatigue"),
        "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
    }
    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            mood_context=mood_context,
            force_regen=False,
        )
        sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
        goal_tasks_count = len(sections.get("goal_tasks", []) or [])
        plan_source = plan.get("_plan_source") if isinstance(plan, dict) else None
        logger.info("API: Served today plan goal_tasks_count=%s source=%s", goal_tasks_count, plan_source or "unknown")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to build today plan: {exc}", exc_info=True)
        return api_error(
            "TODAY_PLAN_FAILED",
            "Failed to build today plan",
            500,
            details=type(exc).__name__,
        )

@app.route("/api/plan/update", methods=["POST"])
@require_auth
def update_plan_item():
    """Update lifecycle status for a plan item (complete/skip/reschedule)."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    data = request.get_json() or {}
    item_id = data.get("item_id")
    status = data.get("status")
    plan_date = data.get("plan_date")
    reason = data.get("reason")
    reschedule_to = data.get("reschedule_to")

    if not item_id or not status:
        return api_error("VALIDATION_ERROR", "item_id and status are required", 400)

    try:
        plan = othello_engine.day_planner.update_plan_item_status(
            user_id,
            item_id=item_id,
            status=status,
            plan_date=plan_date,
            reason=reason,
            reschedule_to=reschedule_to,
        )
        logger.info(f"API: Updated plan item {item_id} -> {status}")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to update plan item {item_id}: {exc}", exc_info=True)
        return api_error(
            "PLAN_UPDATE_FAILED",
            "Failed to update plan item",
            500,
            details=type(exc).__name__,
        )
```

### 3. Routines CRUD Routes
```python
[api.py]
@app.route("/api/routines", methods=["GET"])
@require_auth
def list_routines():
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        routines = routines_repository.list_routines_with_steps(user_id)
        return jsonify({"ok": True, "routines": routines})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to list routines: {e}", exc_info=True)
        return api_error("ROUTINE_LIST_FAILED", str(e), 500)

@app.route("/api/routines", methods=["POST"])
@require_auth
def create_routine():
    user_id, error = _get_user_id_or_error()
    if error: return error
    data = request.json or {}
    title = data.get("title")
    if not title:
        return api_error("INVALID_INPUT", "Title is required", 400)
    
    try:
        routine = routines_repository.create_routine(
            user_id, 
            title, 
            data.get("schedule_rule", {}), 
            data.get("enabled", True)
        )
        return jsonify({"ok": True, "routine": routine})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to create routine: {e}", exc_info=True)
        return api_error("ROUTINE_CREATE_FAILED", str(e), 500)

@app.route("/api/routines/<routine_id>", methods=["PATCH"])
@require_auth
def update_routine(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        routine = routines_repository.update_routine(user_id, routine_id, request.json or {})
        if not routine:
            return api_error("NOT_FOUND", "Routine not found", 404)
        return jsonify({"ok": True, "routine": routine})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to update routine: {e}", exc_info=True)
        return api_error("ROUTINE_UPDATE_FAILED", str(e), 500)

@app.route("/api/routines/<routine_id>", methods=["DELETE"])
@require_auth
def delete_routine(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        success = routines_repository.delete_routine(user_id, routine_id)
        if not success:
            return api_error("NOT_FOUND", "Routine not found", 404)
        return jsonify({"ok": True})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to delete routine: {e}", exc_info=True)
        return api_error("ROUTINE_DELETE_FAILED", str(e), 500)
```

### 4. Routine Steps Routes
```python
[api.py]
@app.route("/api/routines/<routine_id>/steps", methods=["POST"])
@require_auth
def create_routine_step(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    data = request.json or {}
    title = data.get("title")
    if not title:
        return api_error("INVALID_INPUT", "Title is required", 400)
        
    try:
        step = routines_repository.create_step(
            user_id,
            routine_id,
            title,
            est_minutes=data.get("est_minutes"),
            energy=data.get("energy"),
            tags=data.get("tags"),
            order_index=data.get("order_index")
        )
        return jsonify({"ok": True, "step": step})
    except ValueError as ve:
        return api_error("INVALID_INPUT", str(ve), 400)
    except Exception as e:
        logging.getLogger("API").error(f"Failed to create step: {e}", exc_info=True)
        return api_error("STEP_CREATE_FAILED", str(e), 500)

@app.route("/api/steps/<step_id>", methods=["PATCH"])
@require_auth
def update_routine_step(step_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        step = routines_repository.update_step(user_id, step_id, request.json or {})
        if not step:
            return api_error("NOT_FOUND", "Step not found", 404)
        return jsonify({"ok": True, "step": step})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to update step: {e}", exc_info=True)
        return api_error("STEP_UPDATE_FAILED", str(e), 500)

@app.route("/api/steps/<step_id>", methods=["DELETE"])
@require_auth
def delete_routine_step(step_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        success = routines_repository.delete_step(user_id, step_id)
        if not success:
            return api_error("NOT_FOUND", "Step not found", 404)
        return jsonify({"ok": True})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to delete step: {e}", exc_info=True)
        return api_error("STEP_DELETE_FAILED", str(e), 500)
```

---

## C) Planner / Domain Evidence (`core/day_planner.py`)

### 1. Phase Flags
```python
[core/day_planner.py]
_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes")
```

### 2. RoutineStore
```python
[core/day_planner.py]
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
                if days and isinstance(days, list) and day_tag not in days:
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
            })
        return active
```

### 3. DayPlanner
```python
[core/day_planner.py]
    def get_today_plan(
        self,
        user_id: str,
        mood_context: Optional[Dict[str, Any]] = None,
        force_regen: bool = False,
    ) -> Dict[str, Any]:
        uid = self._normalize_user_id(user_id)
        today = date.today()
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
                return persisted_existing
        behavior_snapshot = self.behavior_profile.build_profile()
        plan = self._generate_plan(uid, today, mood_context or {}, behavior_snapshot)
        appended_goal_tasks = self._append_persisted_goal_tasks(uid, today, plan)
        persisted = self._persist_plan(uid, today, plan)
        persisted["_plan_source"] = "generated"
        self._log_plan_structure(today, persisted, appended_goal_tasks=appended_goal_tasks, source="generated")
        return persisted

    def _generate_plan(
        self,
        user_id: str,
        target_date: date,
        mood: Dict[str, Any],
        behavior_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        mood_payload = self._normalise_mood(mood)
        routines = self._select_routines(target_date, mood_payload, behavior_snapshot)
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

    def _select_routines(self, user_id: str, target_date: date, mood: Dict[str, Any], behavior_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        selected = []
        routine_stats = (behavior_snapshot or {}).get("routine_stats", {})
        section_stats = (behavior_snapshot or {}).get("section_density", {})
        active = self.routine_store.get_active_routines(target_date, mood, routine_stats, section_stats, user_id=user_id)
        for idx, bundle in enumerate(active):
            variant = bundle["variant"]
            steps = []
            for step in variant.get("steps", []):
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
                })
        # ... (goal tasks omitted)
        return items

    def _hydrate_plan_from_db(self, plan_row: Dict[str, Any]) -> Dict[str, Any]:
        items = plan_row.get("items", [])
        routines: Dict[str, Dict[str, Any]] = {}
        steps_by_parent: Dict[str, List[Dict[str, Any]]] = {}
        # ...
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
                step["energy_cost"] = row.get("energy") or metadata.get("energy_cost")
                if parent_id:
                    steps_by_parent.setdefault(parent_id, []).append(step)
            # ...
        for routine_id, routine in routines.items():
            routine["steps"] = sorted(steps_by_parent.get(routine_id, []), key=lambda s: s.get("id", ""))
        # ...
        return plan

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
        # ...
        updated_row = plan_repository.update_plan_item_status(
            plan_row["id"],
            item_id,
            status,
            skip_reason=reason,
            reschedule_to=reschedule_to,
        )
        # ...
        return plan

    def _persist_plan(self, user_id: str, target_date: date, plan: Dict[str, Any]) -> Dict[str, Any]:
        # ...
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
                            "skip_reason": item.get("skip_reason")
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
                        if prev["skip_reason"]:
                            item["reason"] = prev["skip_reason"]

                plan_repository.replace_plan_items(plan_row["id"], items)
        # ...
        return plan
```

### 4. Status Semantics
```python
[core/day_planner.py]
allowed_statuses = {"planned", "in_progress", "complete", "skipped", "rescheduled"}
```

---

## D) Storage / Schema Evidence (`db/`)

### 1. `db/database.py`
```python
[db/database.py]
def ensure_core_schema() -> None:
    """Ensure required core tables exist (goals, plan_steps, plans, plan_items)."""
    ddl_statements = [
        # ...
        # Daily plans header
        """
        CREATE TABLE IF NOT EXISTS plans (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_date DATE NOT NULL,
            generation_context JSONB DEFAULT '{}'::jsonb,
            behavior_snapshot JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, plan_date)
        );
        """,
        # ...
        # Daily plan items
        """
        CREATE TABLE IF NOT EXISTS plan_items (
            id SERIAL PRIMARY KEY,
            plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
            item_id TEXT NOT NULL,
            type TEXT NOT NULL,
            section TEXT,
            status TEXT DEFAULT 'planned',
            reschedule_to DATE,
            skip_reason TEXT,
            priority INTEGER,
            effort TEXT,
            energy TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(plan_id, item_id)
        );
        """,
        # ...
        # Routines (template header)
        """
        CREATE TABLE IF NOT EXISTS routines (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            schedule_rule JSONB DEFAULT '{}'::jsonb,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # ...
        # Routine steps (template steps)
        """
        CREATE TABLE IF NOT EXISTS routine_steps (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            routine_id TEXT NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
            order_index INTEGER DEFAULT 0,
            title TEXT NOT NULL,
            est_minutes INTEGER,
            energy TEXT,
            tags JSONB DEFAULT '[]'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # ...
    ]
```

### 2. `db/plan_repository.py`
```python
[db/plan_repository.py]
def upsert_plan(
    user_id: str,
    plan_date: date,
    generation_context: Optional[Dict[str, Any]] = None,
    behavior_snapshot: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        INSERT INTO plans (user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (user_id, plan_date)
        DO UPDATE SET
            generation_context = EXCLUDED.generation_context,
            behavior_snapshot = EXCLUDED.behavior_snapshot,
            updated_at = NOW()
        RETURNING id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (user_id, plan_date, generation_context or {}, behavior_snapshot or {}))

def get_plan_by_date(user_id: str, plan_date: date) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at
        FROM plans
        WHERE user_id = %s AND plan_date = %s
        LIMIT 1;
    """
    return fetch_one(query, (user_id, plan_date))

def get_plan_items(plan_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
               priority, effort, energy, metadata, user_id, source_kind, source_id,
               title, order_index, notes, created_at, updated_at, created_at_utc, updated_at_utc
        FROM plan_items
        WHERE plan_id = %s
        ORDER BY id ASC;
    """
    # ...
    return rows

def replace_plan_items(plan_id: int, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    delete_plan_items(plan_id)
    created: List[Dict[str, Any]] = []
    for item in items:
        created_item = insert_plan_item(plan_id, item)
        if created_item:
            created.append(created_item)
    return created

def update_plan_item_status(
    plan_id: int,
    item_id: str,
    status: str,
    skip_reason: Optional[str] = None,
    reschedule_to: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE plan_items
        SET status = %s,
            skip_reason = COALESCE(%s, skip_reason),
            reschedule_to = COALESCE(%s, reschedule_to),
            metadata = COALESCE(%s, metadata),
            updated_at = NOW()
        WHERE plan_id = %s AND item_id = %s
        RETURNING id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
                  priority, effort, energy, metadata, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (status, skip_reason, reschedule_to, metadata, plan_id, item_id))
```

### 3. `db/routines_repository.py`
```python
[db/routines_repository.py]
import uuid
from typing import Any, Dict, List, Optional
import logging
from psycopg2.extras import Json
from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one

logger = logging.getLogger("RoutinesRepository")

# ---------------------------------------------------------------------------
# Routines (Header)
# ---------------------------------------------------------------------------

def list_routines(user_id: str) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, title, schedule_rule, enabled, created_at, updated_at
        FROM routines
        WHERE user_id = %s
        ORDER BY updated_at DESC;
    """
    return fetch_all(query, (user_id,))

def get_routine(user_id: str, routine_id: str) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, title, schedule_rule, enabled, created_at, updated_at
        FROM routines
        WHERE user_id = %s AND id = %s;
    """
    return fetch_one(query, (user_id, routine_id))

def create_routine(user_id: str, title: str, schedule_rule: Dict, enabled: bool) -> Dict[str, Any]:
    routine_id = str(uuid.uuid4())
    query = """
        INSERT INTO routines (id, user_id, title, schedule_rule, enabled, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, title, schedule_rule, enabled, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (routine_id, user_id, title, Json(schedule_rule), enabled))

def update_routine(user_id: str, routine_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    fields = []
    values = []
    
    if "title" in patch:
        fields.append("title = %s")
        values.append(patch["title"])
    if "schedule_rule" in patch:
        fields.append("schedule_rule = %s")
        values.append(Json(patch["schedule_rule"]))
    if "enabled" in patch:
        fields.append("enabled = %s")
        values.append(patch["enabled"])
        
    if not fields:
        return get_routine(user_id, routine_id)
        
    fields.append("updated_at = NOW()")
    values.append(user_id)
    values.append(routine_id)
    
    query = f"""
        UPDATE routines
        SET {", ".join(fields)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, title, schedule_rule, enabled, created_at, updated_at;
    """
    return execute_and_fetch_one(query, tuple(values))

def delete_routine(user_id: str, routine_id: str) -> bool:
    query = "DELETE FROM routines WHERE user_id = %s AND id = %s RETURNING id"
    result = execute_and_fetch_one(query, (user_id, routine_id))
    return result is not None

# ---------------------------------------------------------------------------
# Routine Steps
# ---------------------------------------------------------------------------

def list_steps(user_id: str, routine_id: str) -> List[Dict[str, Any]]:
    query = """
        SELECT s.id, s.user_id, s.routine_id, s.order_index, s.title, s.est_minutes, s.energy, s.tags, s.created_at, s.updated_at
        FROM routine_steps s
        JOIN routines r ON s.routine_id = r.id
        WHERE s.user_id = %s AND s.routine_id = %s AND r.user_id = %s
        ORDER BY s.order_index ASC, s.created_at ASC;
    """
    return fetch_all(query, (user_id, routine_id, user_id))

def create_step(
    user_id: str, 
    routine_id: str, 
    title: str, 
    est_minutes: Optional[int] = None, 
    energy: Optional[str] = None, 
    tags: Optional[List[str]] = None, 
    order_index: Optional[int] = None
) -> Dict[str, Any]:
    # Ensure routine belongs to user
    routine = get_routine(user_id, routine_id)
    if not routine:
        raise ValueError("Routine not found or access denied")

    if order_index is None:
        # Get max order_index
        q_max = "SELECT MAX(order_index) as m FROM routine_steps WHERE routine_id = %s"
        res = fetch_one(q_max, (routine_id,))
        current_max = res["m"] if res and res["m"] is not None else -1
        order_index = current_max + 1

    step_id = str(uuid.uuid4())
    query = """
        INSERT INTO routine_steps (id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (step_id, user_id, routine_id, order_index, title, est_minutes, energy, Json(tags or [])))

def update_step(user_id: str, step_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    fields = []
    values = []
    
    if "title" in patch:
        fields.append("title = %s")
        values.append(patch["title"])
    if "est_minutes" in patch:
        fields.append("est_minutes = %s")
        values.append(patch["est_minutes"])
    if "energy" in patch:
        fields.append("energy = %s")
        values.append(patch["energy"])
    if "tags" in patch:
        fields.append("tags = %s")
        values.append(Json(patch["tags"]))
    if "order_index" in patch:
        fields.append("order_index = %s")
        values.append(patch["order_index"])
        
    if not fields:
        # Just fetch
        query = "SELECT * FROM routine_steps WHERE user_id = %s AND id = %s"
        return fetch_one(query, (user_id, step_id))
        
    fields.append("updated_at = NOW()")
    values.append(user_id)
    values.append(step_id)
    
    query = f"""
        UPDATE routine_steps
        SET {", ".join(fields)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at;
    """
    return execute_and_fetch_one(query, tuple(values))

def delete_step(user_id: str, step_id: str) -> bool:
    query = "DELETE FROM routine_steps WHERE user_id = %s AND id = %s RETURNING id"
    result = execute_and_fetch_one(query, (user_id, step_id))
    return result is not None

def list_routines_with_steps(user_id: str) -> List[Dict[str, Any]]:
    routines = list_routines(user_id)
    if not routines:
        return []
        
    # Fetch all steps for user (optimization: could filter by routine_ids if list is huge, but per-user is fine)
    query = """
        SELECT id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at
        FROM routine_steps
        WHERE user_id = %s
        ORDER BY order_index ASC, created_at ASC;
    """
    all_steps = fetch_all(query, (user_id,))
    
    # Group steps by routine_id
    steps_by_routine = {}
    for step in all_steps:
        rid = step["routine_id"]
        if rid not in steps_by_routine:
            steps_by_routine[rid] = []
        steps_by_routine[rid].append(step)
        
    for r in routines:
        r["steps"] = steps_by_routine.get(r["id"], [])
        
    return routines
```

---

## E) UI Evidence (`othello_ui.html`)

### 1. Today Planner
```javascript
[othello_ui.html]
    const PLAN_UPDATE_API = "/api/plan/update";

    async function fetchTodayPlan() {
      const resp = await fetch(`/api/today-plan?ts=${Date.now()}`, { cache: "no-store", credentials: "include" });
      if (resp.status === 401 || resp.status === 403) {
        const err = new Error("Unauthorized");
        err.status = resp.status;
        throw err;
      }
      if (!resp.ok) throw new Error("Failed to load plan");
      const data = await resp.json();
      return data.plan || {};
    }

    async function loadTodayPlanner() {
      // ...
      try {
        const [brief, plan] = await Promise.all([fetchTodayBrief(), fetchTodayPlan()]);
        const goalTasks = (plan.sections?.goal_tasks || []);
        // ...
        renderTodayBrief(plan, brief);
        renderPlannerSections(plan, goalTasks);
        await loadTodayPlanPanel();
      } catch (e) {
        // ...
      }
    }

    function renderPlannerSections(plan, goalTasksOverride = null) {
      const sections = (plan.sections || {});
      const routines = sections.routines || [];
      const goalTasks = goalTasksOverride !== null ? goalTasksOverride : (sections.goal_tasks || []);

      plannerRoutinesList.innerHTML = "";
      if (!routines.length) {
        plannerRoutinesCount.textContent = "0 items";
        plannerRoutinesList.innerHTML = `<div class="planner-empty">No routines planned yet.</div>`;
      } else {
        plannerRoutinesCount.textContent = `${routines.length} item${routines.length === 1 ? "" : "s"}`;
        routines.forEach(item => {
          // ...
          const headerRight = document.createElement("div");
          headerRight.className = "planner-block__right";
          headerRight.appendChild(createStatusChip(item.status, item));
          if (item.item_id) {
            headerRight.appendChild(buildPlannerActions(item));
          }
          // ...
          const stepsWrap = document.createElement("div");
          // ...
            (item.steps || []).forEach(step => {
              // ...
              const stepRight = document.createElement("div");
              stepRight.className = "planner-block__right";
              stepRight.appendChild(createStatusChip(step.status, step));
              if (step.item_id) {
                stepRight.appendChild(buildPlannerActions(step));
              }
              // ...
            });
          // ...
        });
      }
      renderGoalTasks(goalTasks);
    }

    function createStatusChip(status, item = null) {
      const chip = document.createElement("div");
      chip.className = "planner-status";
      chip.textContent = status || "planned";
      
      if (item) {
        const iid = item.item_id || item.id;
        if (iid && (status === "planned" || status === "in_progress")) {
          chip.style.cursor = "pointer";
          chip.title = status === "planned" ? "Click to Start" : "Click to Complete";
          chip.onclick = async (e) => {
            e.stopPropagation();
            const nextStatus = status === "planned" ? "in_progress" : "complete";
            try {
              const resp = await fetch(PLAN_UPDATE_API, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ item_id: iid, status: nextStatus }),
              });
              if (resp.ok) await loadTodayPlanner();
            } catch (err) { console.error(err); }
          };
        }
      }
      return chip;
    }

    function buildPlannerActions(item) {
      const container = document.createElement("div");
      container.className = "planner-actions";
      
      const iid = item?.item_id || item?.id;
      if (!iid) return container;

      const status = item.status || "planned";
      const actions = [];
      
      if (status === "planned") {
        actions.push({ label: "Start", status: "in_progress" });
        actions.push({ label: "Done", status: "complete" });
        actions.push({ label: "Skip", status: "skipped" });
        actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
      } else if (status === "in_progress") {
        actions.push({ label: "Done", status: "complete" });
        actions.push({ label: "Skip", status: "skipped" });
        actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
      }

      actions.forEach(action => {
        const btn = document.createElement("button");
        btn.className = "planner-action-btn";
        btn.textContent = action.label;
        btn.addEventListener("click", async () => {
          btn.disabled = true;
          try {
            const payload = {
              item_id: iid,
              status: action.status,
            };
            if (action.status === "rescheduled") {
              payload.reschedule_to = getTomorrowDate();
            }
            const resp = await fetch(PLAN_UPDATE_API, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify(payload),
            });
            if (!resp.ok) {
              const errText = await resp.text();
              throw new Error(errText || "Failed to update item");
            }
            await loadTodayPlanner();
          } catch (err) {
            renderPlannerError("Could not update item. Please try again.");
          } finally {
            btn.disabled = false;
          }
        });
        container.appendChild(btn);
      });

      return container;
    }
```

### 2. Routine Planner
```html
[othello_ui.html]
      <!-- ROUTINE PLANNER VIEW -->
      <div id="routine-planner-view" class="view">
        <div class="view-header">
          <h2 class="view-title">Routine Planner</h2>
        </div>
        <div class="routine-planner-layout" style="display: grid; grid-template-columns: 300px 1fr; gap: 1.5rem; height: calc(100vh - 140px);">
          <!-- Left: List -->
          <div class="routine-list-panel" style="background: var(--bg-2); border: 1px solid var(--border); border-radius: 12px; display: flex; flex-direction: column;">
            <div style="padding: 1rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600; color: var(--text-main);">Routines</span>
              <button id="routine-add-btn" class="icon-button" title="New Routine">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
              </button>
            </div>
            <div id="routine-list" style="flex: 1; overflow-y: auto; padding: 0.5rem;">
              <!-- Routine items injected here -->
            </div>
          </div>

          <!-- Right: Editor -->
          <div id="routine-editor" class="routine-editor-panel" style="background: var(--bg-2); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; display: none; flex-direction: column; overflow-y: auto;">
            <!-- ... -->
            <div style="flex: 1; display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <span style="font-size: 0.95rem; font-weight: 600; color: var(--text-main);">Steps</span>
                <button id="routine-add-step-btn" class="login-button" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;">+ Add Step</button>
              </div>
              <div id="routine-steps" style="display: flex; flex-direction: column; gap: 0.5rem;">
                <!-- Steps injected here -->
              </div>
            </div>
          </div>
          
          <div id="routine-empty-state" style="display: flex; align-items: center; justify-content: center; color: var(--text-soft); background: var(--bg-2); border: 1px solid var(--border); border-radius: 12px;">
            Select a routine to edit
          </div>
        </div>
      </div>
```

```javascript
[othello_ui.html]
    // ===== ROUTINE PLANNER LOGIC =====
    const ROUTINES_API = "/api/routines";
    othelloState.routines = [];
    othelloState.activeRoutineId = null;

    async function fetchRoutines() {
      try {
        const resp = await fetch(ROUTINES_API, { credentials: "include" });
        if (!resp.ok) throw new Error("Failed to fetch routines");
        const data = await resp.json();
        if (data.ok) {
          othelloState.routines = data.routines || [];
        }
      } catch (err) {
        console.error("fetchRoutines error:", err);
      }
    }

    async function loadRoutinePlanner() {
      await fetchRoutines();
      renderRoutineList(othelloState.routines);
      if (othelloState.routines.length > 0 && !othelloState.activeRoutineId) {
        selectRoutine(othelloState.routines[0].id);
      } else if (othelloState.activeRoutineId) {
        selectRoutine(othelloState.activeRoutineId);
      } else {
        document.getElementById("routine-editor").style.display = "none";
        document.getElementById("routine-empty-state").style.display = "flex";
      }
    }

    function renderRoutineList(routines) {
      const listEl = document.getElementById("routine-list");
      listEl.innerHTML = "";
      routines.forEach(r => {
        // ...
        item.onclick = () => selectRoutine(r.id);
        listEl.appendChild(item);
      });
    }

    function renderRoutineEditor(routine) {
      // ...
      document.getElementById("routine-add-step-btn").onclick = () => addStep(routine.id);
    }

    async function addRoutine() {
      const title = prompt("Routine Name:");
      if (!title) return;
      try {
        const resp = await fetch(ROUTINES_API, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, enabled: true }),
          credentials: "include"
        });
        if (resp.ok) {
          const data = await resp.json();
          othelloState.activeRoutineId = data.routine.id;
          await loadRoutinePlanner();
        }
      } catch (err) { console.error(err); }
    }
    document.getElementById("routine-add-btn").onclick = addRoutine;

    async function addStep(routineId) {
      try {
        const resp = await fetch(`${ROUTINES_API}/${routineId}/steps`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: "New Step", est_minutes: 5, energy: "low" }),
          credentials: "include"
        });
        if (resp.ok) {
          await fetchRoutines();
          selectRoutine(routineId);
        }
      } catch (err) { console.error(err); }
    }

    async function updateStep(stepId, patch) {
      try {
        const resp = await fetch(`/api/steps/${stepId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
          credentials: "include"
        });
        if (resp.ok) {
          await fetchRoutines();
        }
      } catch (err) { console.error(err); }
    }

    async function deleteStep(stepId) {
      if (!confirm("Delete step?")) return;
      try {
        const resp = await fetch(`/api/steps/${stepId}`, { method: "DELETE", credentials: "include" });
        if (resp.ok) {
          await fetchRoutines();
          selectRoutine(othelloState.activeRoutineId);
        }
      } catch (err) { console.error(err); }
    }

    async function reorderStep(routine, stepId, direction) {
      // ...
      const updates = steps.map((s, i) => {
        if (s.order_index !== i) {
          return updateStep(s.id, { order_index: i });
        }
        return Promise.resolve();
      });
      
      await Promise.all(updates);
      await fetchRoutines();
      selectRoutine(routine.id);
    }
```

---

## F) Known Breakpoints / Mismatches (Static Sweep)

- **No critical breakpoints found.** The implementation appears consistent across DB, API, and UI layers.
- **Observation:** `RoutineStore` in `core/day_planner.py` has a hardcoded `_PHASE1_DB_ONLY` check. If the environment variable `OTHELLO_PHASE1_DB_ONLY` is not set to "1", "true", or "yes", it might attempt to load JSON files, but `api.py` explicitly sets this env var if `OTHELLO_PHASE` is "phase1".
- **Observation:** `DayPlanner.get_active_routines` manually maps DB routine steps to the internal format expected by the planner logic. This mapping aligns with the fields returned by `routines_repository.list_routines_with_steps`.
