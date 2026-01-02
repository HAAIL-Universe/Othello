# Update Diff Log - January 2, 2026

## Core Logic Changes (`core/day_planner.py`)

### Snooze Fix & Timestamp Handling
- Updated `snooze_plan_item` to use `_load_plan` instead of the non-existent `get_day_plan`.
- Changed snooze timestamp generation to use timezone-aware UTC (ISO format with 'Z').

```python
-            snooze_until = (datetime.utcnow() + timedelta(minutes=snooze_minutes)).isoformat()
+            # Use timezone-aware UTC and write ISO with Z
+            snooze_until = datetime.now(timezone.utc) + timedelta(minutes=snooze_minutes)
+            snooze_until = snooze_until.isoformat().replace("+00:00", "Z")
```

### Snooze Persistence
- Updated `_persist_plan` to preserve `snoozed_until` metadata when regenerating the plan.
- Fixed `skip_reason` preservation to only apply when status is 'skipped'.

```python
+                        # Preserve snoozed_until
+                        prev_meta = prev["metadata"]
+                        if prev_meta.get("snoozed_until"):
+                            item.setdefault("metadata", {})
+                            item["metadata"]["snoozed_until"] = prev_meta["snoozed_until"]
```

### Section Hints
- Updated `_infer_section_hint` to prioritize `schedule_rule.part_of_day` over tags.

```python
+        schedule = routine.get("schedule_rule", {})
+        part = schedule.get("part_of_day")
+        if part in ("morning", "afternoon", "evening", "night", "any"):
+            if part == "night":
+                return "evening"
+            return part
```

## UI Changes (`othello_ui.html`)

### Snooze Handling
- Added `isSnoozedNow` helper function.
- Updated `renderGoalTasks` and `renderPlannerSections` to filter out snoozed items from main views.
- Added a new "Snoozed" section at the bottom of the planner.
- Added "Wake" button to snoozed items.

### Next Action Card
- Implemented `renderNextAction` to display a prominent card for the next action.
- Computes next action client-side if not provided by server (prioritizing `in_progress`).
- Added quick actions: Start, Done, +15m, +1h.

### Routine Editor
- Added "Part of Day" dropdown to routine editor.
- Added optional "Time Window" (Start/End) inputs.
- Updates `schedule_rule` in routine definition.

```javascript
+      // Part of Day & Time Window
+      const scheduleRule = routine.schedule_rule || {};
+      // ... UI construction code ...
```
