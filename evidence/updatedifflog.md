# Forensic Audit Report: Context Injection Integrity (Follow-Up)
**Date**: 2024-10-24
**Status**: INVESTIGATION COMPLETE

## Executive Summary
Two distinct issues were identified during this audit.
1.  **Runtime Crash (BLOCKER)**: The "Fix" previously applied contained a `NameError` (`channel_name` undefined) in `_load_companion_context`, causing the API to crash on valid requests. This had to be hotfixed to proceed.
2.  **Recall Refusal (VERIFIED)**: After fixing the crash, the "KEYWORD_7319" test confirmed that **Recall Fails** (`"I don't have access to past interactions"`) even when `llm_msg_count=11` and the history is demonstrably present in the request context. This indicates the refusal is a **Model Alignment/Hallucination** issue driven by the specific "No Active Goal" system prompt, not a technical data loss.

## Evidence Bundle

### 1. The Broken Fix (Crash)
*   **File**: `z:\Othello\api.py` (Line 1597)
*   **Condition**: `NameError: name 'channel_name' is not defined`.
*   **Status**: Hotfixed during audit to allow tracing.

### 2. Runtime Reproduction (Recall Failure)
*   **Scenario**: User sends "KEYWORD_7319", then asks "What keyword did I say?".
*   **Context State**:
    *   `llm_msg_count` = 11 (History IS present).
    *   `history_ids_peek` = Correct IDs found.
    *   `query_filter_summary` = `WHERE conversation_id = 157 (unified) ...`
*   **Result**: LLM replies: *"I'm sorry, but I don't have access to past interactions..."*

### 3. Trace Analysis

**Reply Assembly**
*   **Mechanism**: Raw LLM output.
*   **File**: `z:\Othello\core\architect_brain.py`
    *   Line 222: `response = self.llm.chat_completion(...)`
    *   Line 223: `return response.content, agent_status`
*   **Evidence**: The log `ARCHITECT raw LLM response: I'm sorry...` matches the API JSON output exactly. No post-processing intervention detected.

**Route Selection**
*   **File**: `z:\Othello\api.py`
    *   `effective_channel` determined as `companion`.
    *   Code Logic: `route_label = "Planner" if effective_channel == "planner" else "Chat"`
*   **Result**: `selected_route` = "Chat". Routing is correct.

## Proof of Injection (New Evidence)
Instrumentation verified that the "KEYWORD_7319" text was literally present in the input memory variable (`companion_context`) passed to the agent.

**File Changed**: `z:\Othello\api.py` (Instrumentation Logic)
**Debug Output Verified**:
```json
"meta": {
  "context_debug": {
    "history_window_note": "Active Injection (companion_context variable)",
    "history_contains_keyword_7319": true,
    "history_user_first_preview": "First(Oldest): KEYWORD_7319",
    "history_user_last_preview": "Last(Newest): KEYWORD_7319",
    "history_count": 12,
    "llm_msg_count": 15
  }
}
```

## Root Cause Candidates (Ranked)

| Rank | Hypothesis | Status | Falsification |
| :--- | :--- | :--- | :--- |
| 1 | **System Prompt Interference** | **Likely** | The 2nd system message ("If user asks... explain there is no active goal context") likely primes the model to refuse *all* context queries when no goal is active, causing it to hallucinate "no memory". |
| 2 | **Application Crash (NameError)** | **Confirmed** | Was the primary blocker preventing testing. Fixed. |
| 3 | **Data Injection Failure** | **DISPROVED** | `history_contains_keyword_7319: true` confirms data integrity. |
| 4 | **Role Mapping Error** | Disproved | `llm_roles_sequence` shows correct `user`/`assistant` alternation. |

## Next Action
Relax the strictness of the "No Active Goal" system prompt in `architect_brain.py`.
**Recommendation**: Change "explain that there is no active goal context available" to "explain that there is no active *Goal* context, but continue chatting normally". This distinction is currently too subtle for the model.


# Final Resolution (2026-01-07)

## Root Cause Discovery
The investigation revealed that the issue was **not** in the database layer or the prompt construction Architect layer, but in the final network transmission layer: core/llm_wrapper.py.

**The Bug**: The AsyncLLMWrapper.chat method contained legacy code that iterated through the messages list and extracted only the *last* system and user prompt strings, discarding all intermediate history messages. Access logs confirmed the history was loaded correctly from the DB, but the wrapper effectively deleted it before calling OpenAI.

## Fix Implemented
Refactored AsyncLLMWrapper.chat to pass the messages list directly to client.chat.completions.create(), preserving the full conversation history.

## Verification
Executed un_test_suite.ps1:
1.  **Context**: User stated 'My favorite fruit is Papaya_cc33'.
2.  **Query**: User asked 'What is my favorite fruit?'
3.  **Result**: Model correctly replied identifying 'papaya'.

**Status**: FIXED. Conversation recall is now functional.

