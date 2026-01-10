# Planning Ref Map

## Entry points
- `/api/message` handler: `api.py:4380`
- UI action `enter_build_mode_from_message` (build gate creation): `api.py:4800`, `api.py:4845`
- Build gate selection (`draft_type="build"`): `api.py:4883`
- Draft edit lane (`draft_type="plan"` or `"goal"`): `api.py:4944`

## Suggestion kinds
- Build mode offer injection (`type="build_mode"`): `api.py:6349`, `api.py:6360`
- Build gate suggestion (`kind="build"`): `api.py:4850`
- Draft kind transitions (`update_suggestion_kind`): `api.py:4926`

## Draft types and transitions
- Build gate response (`draft_type="build"`): `api.py:4865`
- Build -> Goal transition: `api.py:4905`, `api.py:4907`
- Build -> Plan transition: `api.py:4905`, `api.py:4912`

## Payload shapes returned to UI
- Build gate payload: `planner_agent.py:38`
- Plan draft payload: `planner_agent.py:46`
- Goal draft payload (inline): `api.py:4907`
- Plan draft patching (deterministic/LLM): `planner_agent.py:109`, `planner_agent.py:191`

## Repository functions involved
- Suggestions repo: `db/suggestions_repository.py:13`, `db/suggestions_repository.py:32`, `db/suggestions_repository.py:58`, `db/suggestions_repository.py:72`
- Messages repo (draft context + checkpoint linkage): `db/messages_repository.py:208`, `db/messages_repository.py:281`, `db/messages_repository.py:313`
