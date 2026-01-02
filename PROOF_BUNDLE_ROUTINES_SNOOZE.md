# PROOF_BUNDLE_ROUTINES_SNOOZE.md

## 0) Revision + Environment

**Command:**
`git rev-parse --show-toplevel; git rev-parse HEAD; git status --porcelain; python --version`

**Output:**
```
Z:/Othello
3b600a0288f7f6b6e99d0258938858183766dd89
Python 3.12.3
```

## 1) Static compile proof

**Command:**
`python -m py_compile api.py core/day_planner.py db/plan_repository.py db/routines_repository.py db/database.py`

**Output:**
(No output indicates success)
Exit Code: 0

## 2) API route presence proof

**Command:**
`Select-String -Path api.py -Pattern '@app.route\("/api/today-plan"'`
`Select-String -Path api.py -Pattern '@app.route\("/api/plan/update"'`
`Select-String -Path api.py -Pattern '@app.route\("/api/routines"'`
`Select-String -Path api.py -Pattern '@app.route\("/api/routines/<routine_id>"'`
`Select-String -Path api.py -Pattern '@app.route\("/api/routines/<routine_id>/steps"'`
`Select-String -Path api.py -Pattern '@app.route\("/api/steps/<step_id>"'`
`Select-String -Path api.py -Pattern 'def require_auth'`
`Select-String -Path api.py -Pattern 'def _get_user_id_or_error'`

**Output:**
```
api.py:4527:@app.route("/api/today-plan", methods=["GET"])
api.py:4748:@app.route("/api/plan/update", methods=["POST"])
api.py:4609:@app.route("/api/routines", methods=["GET"])
api.py:4621:@app.route("/api/routines", methods=["POST"])
api.py:4652:@app.route("/api/routines/<routine_id>", methods=["PATCH"])
api.py:4678:@app.route("/api/routines/<routine_id>", methods=["DELETE"])
api.py:4692:@app.route("/api/routines/<routine_id>/steps", methods=["POST"])
api.py:4719:@app.route("/api/steps/<step_id>", methods=["PATCH"])
api.py:4733:@app.route("/api/steps/<step_id>", methods=["DELETE"])
api.py:1274:def require_auth(f):
api.py:1329:def _get_user_id_or_error():
```

## 3) Snooze feature proof (end-to-end static)

**Command:**
`Select-String -Path api.py -Pattern 'snooze_minutes'`
`Select-String -Path core/day_planner.py -Pattern 'def snooze_plan_item'`
`Select-String -Path core/day_planner.py -Pattern 'snoozed_until'`
`Select-String -Path db/plan_repository.py -Pattern 'def update_plan_item_metadata'`
`Select-String -Path db/plan_repository.py -Pattern 'metadata = COALESCE\(metadata \|\|'`
`Select-String -Path db/plan_repository.py -Pattern 'SET metadata = metadata \|\|'`

**Output:**
```
api.py:4765:    snooze_minutes = data.get("snooze_minutes")
api.py:4770:    if snooze_minutes is not None:
api.py:4775:                snooze_minutes=int(snooze_minutes),
core\day_planner.py:960:    def snooze_plan_item(
core\day_planner.py:968:        Snoozes a plan item by setting 'snoozed_until' in metadata.
core\day_planner.py:987:            {"snoozed_until": snooze_until}
core\day_planner.py:1033:        if existing_item.get("metadata") and "snoozed_until" in existing_item["metadata"]:
core\day_planner.py:1037:             metadata_update["snoozed_until"] = None
db\plan_repository.py:197:def update_plan_item_metadata(
db\plan_repository.py:188:            metadata = COALESCE(metadata || %s::jsonb, metadata),
db\plan_repository.py:204:        SET metadata = metadata || %s::jsonb,
```

## 4) DB schema proof

**Command:**
`Select-String -Path db/database.py -Pattern 'CREATE TABLE IF NOT EXISTS routines' -Context 0,25`
`Select-String -Path db/database.py -Pattern 'CREATE TABLE IF NOT EXISTS routine_steps' -Context 0,35`
`Select-String -Path db/database.py -Pattern 'CREATE TABLE IF NOT EXISTS plan_items' -Context 0,35`
`Select-String -Path db/database.py -Pattern 'ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS order_index' -Context 0,3`

**Output:**
```
db\database.py:387:        CREATE TABLE IF NOT EXISTS routines (
db\database.py:388:            id TEXT PRIMARY KEY,
db\database.py:389:            user_id TEXT NOT NULL,
db\database.py:390:            title TEXT NOT NULL,
db\database.py:391:            schedule_rule JSONB DEFAULT '{}'::jsonb,
db\database.py:392:            enabled BOOLEAN DEFAULT TRUE,
db\database.py:393:            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
db\database.py:394:            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
db\database.py:395:        );

db\database.py:402:        CREATE TABLE IF NOT EXISTS routine_steps (
db\database.py:403:            id TEXT PRIMARY KEY,
db\database.py:404:            user_id TEXT NOT NULL,
db\database.py:405:            routine_id TEXT NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
db\database.py:406:            order_index INTEGER DEFAULT 0,
db\database.py:407:            title TEXT NOT NULL,
db\database.py:408:            est_minutes INTEGER,
db\database.py:409:            energy TEXT,
db\database.py:410:            tags JSONB DEFAULT '[]'::jsonb,
db\database.py:411:            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
db\database.py:412:            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
db\database.py:413:        );

db\database.py:291:        CREATE TABLE IF NOT EXISTS plan_items (
db\database.py:292:            id SERIAL PRIMARY KEY,
db\database.py:293:            plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
db\database.py:294:            item_id TEXT NOT NULL,
db\database.py:295:            type TEXT NOT NULL,
db\database.py:296:            section TEXT,
db\database.py:297:            status TEXT DEFAULT 'planned',
db\database.py:298:            reschedule_to DATE,
db\database.py:299:            skip_reason TEXT,
db\database.py:300:            priority INTEGER,
db\database.py:301:            effort TEXT,
db\database.py:302:            energy TEXT,
db\database.py:303:            metadata JSONB DEFAULT '{}'::jsonb,
db\database.py:304:            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
db\database.py:305:            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
db\database.py:306:            UNIQUE(plan_id, item_id)
db\database.py:307:        );

db\database.py:316:        "ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS order_index INTEGER;",
```

## 5) Planner integration proof

**Command:**
`Select-String -Path core/day_planner.py -Pattern '_PHASE1_DB_ONLY' -Context 0,3`
`Select-String -Path core/day_planner.py -Pattern 'def get_active_routines' -Context 0,40`
`Select-String -Path core/day_planner.py -Pattern 'routines_repository.list_routines_with_steps' -Context 0,20`
`Select-String -Path core/day_planner.py -Pattern 'routines = self._select_routines' -Context 0,3`
`Select-String -Path core/day_planner.py -Pattern 'def _select_routines' -Context 0,40`
`Select-String -Path core/day_planner.py -Pattern '"item_id": sid' -Context 0,10`

**Output:**
```
core\day_planner.py:1127:_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes", "on")

core\day_planner.py:249:    def get_active_routines(
core\day_planner.py:262:        if _PHASE1_DB_ONLY:
core\day_planner.py:265:            db_routines = routines_repository.list_routines_with_steps(user_id)

core\day_planner.py:646:        routines = self._select_routines(user_id, target_date, mood_payload, behavior_snapshot)

core\day_planner.py:832:    def _select_routines(self, user_id: str, target_date: date, mood: Dict[str, Any], behavior_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
core\day_planner.py:836:        active = self.routine_store.get_active_routines(target_date, mood, routine_stats, section_stats, user_id=user_id)
core\day_planner.py:842:                sid = f"routine-{bundle['routine_id']}-variant-{variant.get('id')}-step-{step.get('id')}"
core\day_planner.py:845:                    "item_id": sid,
```

## 6) UI wiring proof

**Command:**
`Select-String -Path othello_ui.html -Pattern 'ROUTINES_API' -Context 0,5`
`Select-String -Path othello_ui.html -Pattern 'function loadRoutinePlanner' -Context 0,25`
`Select-String -Path othello_ui.html -Pattern 'function renderRoutineEditor' -Context 0,40`
`Select-String -Path othello_ui.html -Pattern 'fetch\(PLAN_UPDATE_API' -Context 0,10`
`Select-String -Path othello_ui.html -Pattern 'credentials: "include"'`
`Select-String -Path othello_ui.html -Pattern 'snooze_minutes' -Context 0,8`
`Select-String -Path othello_ui.html -Pattern 'routine-planner-view' -Context 0,20`

**Output:**
```
othello_ui.html:5821:    // ===== ROUTINE PLANNER LOGIC =====
othello_ui.html:5822:    const ROUTINES_API = "/api/routines";

othello_ui.html:5834:    async function loadRoutinePlanner() {
othello_ui.html:5835:      await fetchRoutines();

othello_ui.html:3225:              const resp = await fetch(PLAN_UPDATE_API, {
othello_ui.html:3227:                credentials: "include",

othello_ui.html:3292:                payload.snooze_minutes = action.snooze;
```

## 7) Runtime proof (optional)

ENVIRONMENT_LIMITATION: DB not reachable from this environment
