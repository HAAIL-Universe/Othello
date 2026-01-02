# PROOF_BUNDLE_ROUTINES_SNOOZE.md

## 1) Static compile proof

**Command:**
`python -m py_compile api.py core/day_planner.py db/plan_repository.py`

**Output:**
(No output indicates success)
Exit Code: 0

## 2) Grep proof (feature presence)

**Command:**
`Select-String -Pattern "/api/plan/update" -Path api.py`

**Output:**
```
api.py:4748:@app.route("/api/plan/update", methods=["POST"])
```

**Command:**
`Select-String -Pattern "snooze_minutes" -Path api.py, core/day_planner.py, othello_ui.html`

**Output:**
```
api.py:4765:    snooze_minutes = data.get("snooze_minutes")
api.py:4770:    if snooze_minutes is not None:
api.py:4775:                snooze_minutes=int(snooze_minutes),
core\day_planner.py:964:        snooze_minutes: int,
core\day_planner.py:978:        if snooze_minutes <= 0:
core\day_planner.py:981:            snooze_until = (datetime.utcnow() + timedelta(minutes=snooze_minutes)).isoformat()
othello_ui.html:3292:                payload.snooze_minutes = action.snooze;
```

**Command:**
`Select-String -Pattern "snoozed_until" -Path core/day_planner.py, db/plan_repository.py, othello_ui.html`

**Output:**
```
core\day_planner.py:968:        Snoozes a plan item by setting 'snoozed_until' in metadata.
core\day_planner.py:987:            {"snoozed_until": snooze_until}
core\day_planner.py:1033:        if existing_item.get("metadata") and "snoozed_until" in existing_item["metadata"]:
core\day_planner.py:1037:             metadata_update["snoozed_until"] = None
othello_ui.html:3252:      const snoozedUntil = metadata.snoozed_until;
```

**Command:**
`Select-String -Pattern "metadata.*\|\|" -Path db/plan_repository.py`

**Output:**
```
db\plan_repository.py:188:            metadata = COALESCE(metadata || %s::jsonb, metadata),
db\plan_repository.py:204:        SET metadata = metadata || %s::jsonb,
```

## 3) DB proof (if DB credentials available)

ENVIRONMENT_LIMITATION: DB not reachable from this environment

**DB Config Locations:**
- `api.py`: `DATABASE_URL` env var check.
- `db/database.py`: Connection logic.

## 4) API proof (if server runnable here)

ENVIRONMENT_LIMITATION: server not runnable here

**Run Command:**
`python api.py`
