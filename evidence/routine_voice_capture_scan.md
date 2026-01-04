# Routine voice capture scan

## Repo tree snapshot (short)
- build_docs/
- core/
- db/
- interface/
- modules/
- utils/
- evidence/
- api.py
- othello_ui.html

## Governance paths read
- build_docs/theexecutor.md
- build_docs/othello_blueprint.md
- build_docs/othello_directive.md
- build_docs/othello_manifesto.md

## Search log (commands + top hits)
1) rg -n "v1/messages|/v1/messages|messages" -S api.py modules core db interface
   - api.py:2195 @v1.route("/messages", methods=["GET", "POST"])
   - api.py:2547 @v1.route("/messages/<int:message_id>/finalize", methods=["POST"])
   - db/messages_repository.py:19 def create_message(...)
   - core/capabilities_registry.py:16 messages_sessions_v1 (endpoints list)
2) rg -n "api/message" api.py
   - api.py:3095 @app.route("/api/message", methods=["POST"])
3) rg -n "analyze|suggestion|suggestions|confirm" -S api.py core modules db interface
   - api.py:2564 def v1_analyze()
   - api.py:1730 def _apply_suggestion_decisions(...)
   - api.py:2705 def v1_confirm()
   - db/suggestions_repository.py:13 def create_suggestion(...)
4) rg -n "confirm|pending|suggestion|suggestions" -S interface othello_ui.html
   - othello_ui.html:3222 confirm button for plan suggestions
   - othello_ui.html:6182 buildGoalIntentPanel (Save/Create Goal)
   - othello_ui.html:2883 applyInsightsMeta pending counts
5) rg -n "goals" -S db core modules api.py
   - db/goals_repository.py:91 def list_goals(...)
   - db/goals_repository.py:169 def create_goal(...)
   - db/database.py:189 CREATE TABLE IF NOT EXISTS goals
6) rg -n "routine" -S core modules interface db api.py
   - api.py:6651 @app.route("/api/routines", methods=["GET"])
   - db/database.py:387 CREATE TABLE IF NOT EXISTS routines
   - db/routines_repository.py:13 def list_routines(...)
   - core/conversation_parser.py:160 def extract_routines(...)
7) rg -n "InputRouter|route_input|router" -S core api.py interface
   - core/input_router.py:5 class InputRouter
   - api.py:5085 InputRouter.is_plan_request(...)
   - interface/response_router.py:95 def route_input(...)
8) rg -n "ArchitectAgent|architect_agent" -S core modules api.py
   - api.py:665 architect_agent = Architect(model=openai_model)
   - core/architect_brain.py:11 class Architect
9) rg -n "postprocess_and_save" -S api.py utils core
   - api.py:5063 summary = postprocess_and_save(user_input)
   - utils/postprocessor.py:45 def postprocess_and_save(...)
10) rg -n "@v1.route" api.py
   - api.py:2195 /messages
   - api.py:2547 /messages/<int:message_id>/finalize
   - api.py:2564 /analyze

## Phase 1 findings (anchors)

### Message intake endpoints (chat/messages/voice transcript ingestion)
- /api/message (chat entrypoint): api.py:3095
- /v1/messages (message create + list): api.py:2195
- /v1/messages/<id>/finalize (transcript update): api.py:2547

### Agent routing / analysis layer (intent + dispatch)
- Agent wiring and Architect instantiation: api.py:636 and api.py:665
- Architect agent class (LLM orchestration + parser updates): core/architect_brain.py:11
- Chat path routes to Architect for responses: api.py:4535
- InputRouter plan-intent routing (plan request classifier): core/input_router.py:5 and api.py:5085
- Postprocessor extracts goals/traits/routines (analysis only, no persistence): utils/postprocessor.py:45 and api.py:5063

### Existing goal capture + pending suggestion/draft logic
- Heuristic goal intent detection: api.py:958 (_detect_goal_intent_suggestion)
- Goal intent suggestion attachment to responses: api.py:1154 (_attach_goal_intent_suggestion)
- v1 analyze pipeline creates DB-backed suggestions: api.py:2564 and db/suggestions_repository.py:13
- Confirm-gated accept/reject logic: api.py:1730 (_apply_suggestion_decisions) and api.py:2705 (v1_confirm)

### Confirm-before-save UI
- Goal intent panel with Save/Create/Dismiss actions: othello_ui.html:6182
- Plan suggestion confirm button (accepts /v1/suggestions/<id>/accept): othello_ui.html:3222
- Pending counts include routine_pending (badge wiring): othello_ui.html:2883

### DB layer for goals and routines
- Goals repository CRUD (DB truth): db/goals_repository.py:91 and db/goals_repository.py:169
- Goals table definition: db/database.py:189
- Suggestions repository (pending/confirm gate): db/suggestions_repository.py:13
- Routines table definition: db/database.py:387 (routines), db/database.py:402 (routine_steps)
- Routines repository CRUD: db/routines_repository.py:13 and db/routines_repository.py:30
- Routines API endpoints: api.py:6651

### Routine concept exists
- Routine extraction (rules-based) in parser: core/conversation_parser.py:160
- Architect logs extracted routines via RoutineTracker: core/architect_brain.py:216
- Routine planner UI uses /api/routines: othello_ui.html:7690

## Phase 2 ownership analysis (anchored)

### Architect Agent evaluation
- Architect exists and is used for chat responses: core/architect_brain.py:11, api.py:4535
- Architect already parses routines but only logs them (no confirm-gated DB writes): core/architect_brain.py:216
- Goal capture/suggestions are owned by API-layer heuristics and v1 analyze pipeline, not Architect: api.py:958 and api.py:2564
- Conclusion: Architect is not the current owner of goal capture or confirm-gated suggestions; using it as owner for routine capture would mix chat response logic with confirm-gated DB writes. Prefer the existing suggestion pipeline and API confirm flow.

### Recommended insertion points by responsibility
A) RoutineDraft extraction
- Primary: v1 analyze pipeline (api.py:2564) because it already processes transcript messages and creates confirm-gated suggestions (db/suggestions_repository.py:13).
- Parser source: core/conversation_parser.py:160 (existing routine extraction) as a rules baseline; can be extended to return structured RoutineDraft for suggestions.

B) Validation + ambiguity detection
- Locate alongside extraction helper (core/conversation_parser.py:160) to produce missing_fields/ambiguity flags before suggestions are stored.
- API v1 analyze should persist missing_fields in suggestion payload so UI can ask for clarification before confirm (api.py:2564).

C) Clarifying question generation (one at a time)
- Best placed in /api/message (api.py:3095) since it owns interactive chat replies and can surface the next question.
- If using LLM phrasing, keep it behind Architect or a small helper (core/architect_brain.py:11) but only for question phrasing; do not write DB truth there.

D) Pending suggestion storage + confirm UI + DB write on confirm
- Store RoutineDraft as suggestion rows: db/suggestions_repository.py:13 and api.py:2564
- Confirm handler should create routines via db/routines_repository.py:30 when suggestion kind == routine: api.py:1730
- UI should surface routine pending suggestions in Routine Planner (othello_ui.html:7690) and confirm via /v1/suggestions/<id>/accept (api.py:2131)

## Minimal routine flow sequence (target)
transcript -> RoutineDraft -> validate (missing/ambiguous) -> ask clarification -> re-validate -> confirm UI -> save

## Risks / edge cases
- AM/PM ambiguity (e.g., "7 o'clock" without context)
- User timezone interpretation vs stored UTC (timezone rules in directive)
- Duplicate routine capture from repeated transcripts or re-analysis
- Collisions with existing routine titles/schedule_rule overlap
- Vague phrasing without schedule or frequency

## Next patch plan (minimal diff strategy)
1) api.py
   - Extend v1_analyze to emit routine suggestions (kind="routine") using parser output; include missing_fields in payload.
   - Add routine kind handling in _apply_suggestion_decisions to create routines via db/routines_repository.
   - Add a lightweight clarification hook in /api/message to ask the next routine question when a pending routine suggestion is incomplete.
2) core/conversation_parser.py
   - Extend extract_routines to return structured RoutineDraft fields (title, schedule_rule, steps) and ambiguity metadata.
3) db/routines_repository.py
   - Add helper to create routine + steps from a validated RoutineDraft payload.
4) othello_ui.html
   - Add routine pending suggestions panel to Routine Planner and wire to /v1/suggestions?kind=routine; support confirm and clarifying question prompts.
5) core/capabilities_registry.py
   - Document new routine suggestion pipeline in capabilities list for testing/visibility.
