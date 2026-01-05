# Phase 14 Evidence: Architect XML Stripping

## Issue Description
When a user requests a change to a goal draft (e.g., "Change step 2 to Master Loops"), the `Architect` agent correctly generates an XML `<goal_update>` block containing the updated steps. However, the `Architect` logic explicitly detects this XML as "unexpected" and strips it from the response, causing the update to be lost.

## Evidence from Simulation (`verify_phase14_evidence.py`)

### 1. Generate Steps (Success)
The initial generation works because it uses `ui_action="generate_draft_steps"`, which bypasses the `Architect` chat loop and uses `_generate_draft_steps_payload` directly.

```
Draft Payload Steps: ['Install Python', 'Define success criteria', 'Break down into sub-tasks', 'Identify resources needed', 'Set milestones']
```

### 2. Change Step (Failure)
The user request "Change step 2 to Master Loops" is routed to `Architect.plan_and_execute`.
The LLM (mocked) returns:
```xml
<goal_update>
    <steps>
        <step>Install Python</step>
        <step>Write Hello World</step>
        <step>Learn Loops</step>
        <step>Learn Functions</step>
        <step>Build Project</step>
    </steps>
</goal_update>
```

The `Architect` logs show:
```
2026-01-05 13:12:43,828 - ARCHITECT - INFO -   → Detected <goal_update> XML in response; removing and ignoring.
```

### 3. Root Cause Code
File: `core/architect_brain.py`
Method: `plan_and_execute`

```python
            # Drop any unexpected XML goal update blocks from the user-facing reply
            if "<goal_update>" in user_facing_response and "</goal_update>" in user_facing_response:
                self.logger.info("  → Detected <goal_update> XML in response; removing and ignoring.")
                start = user_facing_response.find("<goal_update>")
                end = user_facing_response.rfind("</goal_update>")
                if start != -1 and end != -1:
                    end += len("</goal_update>")
                    user_facing_response = (
                        user_facing_response[:start] + user_facing_response[end:]
                    ).strip()
```

This logic unconditionally strips `<goal_update>` XML if it appears in the response, preventing the `handle_message` or frontend from receiving the updated draft payload.

## Impact
- Users cannot modify drafts via natural language (e.g., "Add a step", "Change step X").
- The UI does not update because the backend never sends the updated `draft_payload`.
- Confirming the goal saves the *original* draft (from generation), ignoring any subsequent change requests.

## Recommended Fix
1. Modify `Architect.plan_and_execute` to **parse** the XML before stripping it.
2. Return the parsed goal update in `agent_status` or a separate return field.
3. Update `handle_message` to check for this goal update and apply it to the active draft (if `draft_id` is present).
