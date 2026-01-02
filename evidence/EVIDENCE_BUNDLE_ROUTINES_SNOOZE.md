# EVIDENCE_BUNDLE_ROUTINES_SNOOZE.md

## 1) API — /api/plan/update (snooze_minutes path)

### FILE: api.py L4750-L4795
```python
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

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    status = data.get("status")
    plan_date = data.get("plan_date")
    reason = data.get("reason")
    reschedule_to = data.get("reschedule_to")
    snooze_minutes = data.get("snooze_minutes")

    if not item_id:
        return api_error("VALIDATION_ERROR", "item_id is required", 400)

    if snooze_minutes is not None:
        try:
            plan = othello_engine.day_planner.snooze_plan_item(
                user_id,
                item_id=item_id,
                snooze_minutes=int(snooze_minutes),
                plan_date=plan_date
            )
            return jsonify({"plan": plan})
        except Exception as exc:
            logger.error(f"API: Failed to snooze item {item_id}: {exc}", exc_info=True)
            return api_error("PLAN_SNOOZE_FAILED", str(exc), 500)

    if not status:
        return api_error("VALIDATION_ERROR", "status is required", 400)

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
    except ValueError as ve:
        return api_error("INVALID_STATUS", str(ve), 400)
    except Exception as exc:
        logger.error(f"API: Failed to update plan item {item_id}: {exc}", exc_info=True)
        return api_error(
            "PLAN_UPDATE_FAILED",
            "Failed to update plan item",
            500,
            details=type(exc).__name__,
        )
```

## 2) PLANNER — snooze + status normalization + schedule semantics

### FILE: core/day_planner.py L268-L290
```python
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
```

### FILE: core/day_planner.py L960-L990
```python
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

        existing_item = plan_repository.get_plan_item(plan_row["id"], item_id)
        if snooze_minutes <= 0:
            snooze_until = None
        else:
            snooze_until = (datetime.utcnow() + timedelta(minutes=snooze_minutes)).isoformat()
        
        # Update metadata
        plan_repository.update_plan_item_metadata(
            plan_row["id"], 
            item_id, 
            {"snoozed_until": snooze_until}
        )
        
        return self.get_day_plan(user_id, target_date.isoformat())
```

### FILE: core/day_planner.py L993-L1045
```python
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

        # Clear snooze if status changes
        metadata_update = {}
        if existing_item.get("metadata") and "snoozed_until" in existing_item["metadata"]:
             # We can't easily delete a key with jsonb_set or || operator in simple update
             # But we can set it to null or handle it in UI. 
             # For now, let's just overwrite it with null which is explicit enough
             metadata_update["snoozed_until"] = None

        updated_row = plan_repository.update_plan_item_status(
            plan_row["id"],
            item_id,
            status,
            skip_reason=reason,
            reschedule_to=reschedule_to,
            metadata=metadata_update if metadata_update else None
        )
```

## 3) DB — JSONB merge correctness

### FILE: db/plan_repository.py L175-L195
```python
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
            skip_reason = %s,
            reschedule_to = %s,
            metadata = COALESCE(metadata || %s::jsonb, metadata),
            updated_at = NOW()
        WHERE plan_id = %s AND item_id = %s
        RETURNING id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
                  priority, effort, energy, metadata, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (status, skip_reason, reschedule_to, Json(metadata) if metadata else None, plan_id, item_id))
```

### FILE: db/plan_repository.py L197-L210
```python
def update_plan_item_metadata(
    plan_id: int,
    item_id: str,
    metadata: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE plan_items
        SET metadata = metadata || %s::jsonb,
            updated_at = NOW()
        WHERE plan_id = %s AND item_id = %s
        RETURNING id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
                  priority, effort, energy, metadata, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (Json(metadata), plan_id, item_id))
```

## 4) API — routines schedule_rule.days defaulting + normalization

### FILE: api.py L4623-L4650
```python
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
        schedule_rule = data.get("schedule_rule", {})
        # Default to all days if days is missing/null (but respect empty list)
        if "days" not in schedule_rule or schedule_rule["days"] is None:
            schedule_rule["days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        
        if isinstance(schedule_rule.get("days"), list):
            valid = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
            schedule_rule["days"] = [d.strip().lower()[:3] for d in schedule_rule["days"] if str(d).strip().lower()[:3] in valid]

        routine = routines_repository.create_routine(
            user_id, 
            title, 
            schedule_rule, 
            data.get("enabled", True)
        )
        return jsonify({"ok": True, "routine": routine})
```

### FILE: api.py L4653-L4675
```python
@app.route("/api/routines/<routine_id>", methods=["PATCH"])
@require_auth
def update_routine(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        patch = request.json or {}
        if "schedule_rule" in patch:
            schedule_rule = patch["schedule_rule"]
            # If days is explicitly None or missing in a replacement object, default to all
            if "days" not in schedule_rule or schedule_rule["days"] is None:
                 schedule_rule["days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

            if isinstance(schedule_rule.get("days"), list):
                valid = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
                schedule_rule["days"] = [d.strip().lower()[:3] for d in schedule_rule["days"] if str(d).strip().lower()[:3] in valid]
            patch["schedule_rule"] = schedule_rule

        routine = routines_repository.update_routine(user_id, routine_id, patch)
```

## 5) UI — Today Planner snooze UI + suppression logic

### FILE: othello_ui.html L3215-L3240
```javascript
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
```

### FILE: othello_ui.html L3243-L3310
```javascript
    function buildPlannerActions(item) {
      const container = document.createElement("div");
      container.className = "planner-actions";
      
      const iid = item?.item_id || item?.id;
      if (!iid) return container;

      const status = item.status || "planned";
      const metadata = item.metadata || {};
      const snoozedUntil = metadata.snoozed_until;
      const isSnoozed = snoozedUntil && new Date(snoozedUntil) > new Date();

      const actions = [];
      
      if (isSnoozed) {
        // If snoozed, allow waking up (clears snooze) or completing
        actions.push({ label: "Wake", status: status }); // Re-sending status clears snooze
        actions.push({ label: "Done", status: "complete" });
      } else {
        if (status === "planned") {
          actions.push({ label: "Start", status: "in_progress" });
          actions.push({ label: "Done", status: "complete" });
          actions.push({ label: "Snooze 1h", snooze: 60 });
          actions.push({ label: "Skip", status: "skipped" });
          actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
        } else if (status === "in_progress") {
          actions.push({ label: "Done", status: "complete" });
          actions.push({ label: "Snooze 30m", snooze: 30 });
          actions.push({ label: "Skip", status: "skipped" });
          actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
        }
      }

      actions.forEach(action => {
        const btn = document.createElement("button");
        btn.className = "planner-action-btn";
        btn.textContent = action.label;
        
        // Style snooze buttons differently?
        if (action.snooze) {
            btn.style.color = "var(--text-soft)";
        }

        btn.addEventListener("click", async () => {
          btn.disabled = true;
          try {
            const payload = { item_id: iid };
            
            if (action.snooze) {
                payload.snooze_minutes = action.snooze;
            } else {
                payload.status = action.status;
                if (action.status === "rescheduled") {
                  payload.reschedule_to = getTomorrowDate();
                }
            }

            const resp = await fetch(PLAN_UPDATE_API, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify(payload),
            });
```

## 6) UI — Routine Planner editor optimistic updates

### FILE: othello_ui.html L5825-L5832
```javascript
    function debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }
```

### FILE: othello_ui.html L6050-L6070
```javascript
    async function updateRoutine(id, patch, refresh = true) {
      try {
        const resp = await fetch(`${ROUTINES_API}/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
          credentials: "include"
        });
        if (resp.ok) {
          if (refresh) {
            await fetchRoutines();
            selectRoutine(id); // refresh view
          } else {
             // Optimistic update
             const r = othelloState.routines.find(r => r.id === id);
             if (r) {
                 Object.assign(r, patch);
                 if (patch.schedule_rule) {
                     r.schedule_rule = Object.assign(r.schedule_rule || {}, patch.schedule_rule);
                 }
             }
          }
        }
      } catch (err) { console.error(err); }
    }
```
