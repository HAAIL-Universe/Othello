# Bug Trace: Routine Draft Trigger

## 1. Issue Description
User reports that "Goal draft only, do not create a routine, no days/times/schedule" triggers a "Routine Draft" UI ("Confirm this routine?" with "Days TBD · 07:00").

## 2. Trace Analysis
- **Frontend (static/othello.js)**: The "Confirm this routine?" card is displayed if meta.intent === "routine_ready".
- **Backend (pi.py)**: outine_ready is set in two places:
    1.  **Pending Suggestion**: If a pending routine suggestion exists and is updated to "complete" status.
    2.  **New Extraction**: If ConversationParser.extract_routines(user_input) returns a candidate with draft_type="schedule".

## 3. Root Cause Investigation
- **Extraction Logic**: ConversationParser._extract_scheduled_routine requires "routine", "every", or "daily". The user's input contains "routine" ("do not create a routine").
- **Time Parsing**: The "07:00" default implies _parse_time_from_text found "morning" or similar. However, reproduction scripts with the exact user string returned [] (no routine found).
- **Hypothesis**: The user's input likely contained a trigger word (like "morning") or the parser behavior in the live environment differs slightly.
- **Defect**: The parser does not handle negative intent ("do not create a routine"). It sees "routine" and proceeds to try extraction.

## 4. Proposed Fix
1.  **Parser Hardening**: Modify core/conversation_parser.py to explicitly reject inputs containing "do not create a routine", "no routine", or "goal draft only".

## 5. Verification
- Reproduction script eproduce_variations.py confirmed that the exact string *should* be safe, but the fix will ensure it *remains* safe even if "morning" is added.
