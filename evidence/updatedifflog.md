# Cycle Status: COMPLETE (Phase 22 - Restore Marker)

## Todo Ledger
Planned:
- [x] Phase 22: Unblock vague inputs in api.py.
- [x] Phase 22: Virtual suggestion fall-through in api.py.
- [x] Phase 22: Capture virtual intent in othello.js sendMessage.
- [x] Phase 22: Pass payload in applySecondarySuggestion.
Completed:
- [x] api.py: Removed early return for virtual suggestions.
- [x] othello.js: Added meta capture loop in sendMessage.
- [x] othello.js: Updated createGoalFromSuggestion call.
Remaining:
- [ ] Done.

## Next Action
Stop and commit.

## Root Cause Anchors
- api.py:1865 (Added fall-through for virtual suggestions)
- othello.js:5700 (Logic to capture virtual intent from meta)

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 0d450fc1..661a07fa 100644
--- a/api.py
+++ b/api.py
@@ -1851,7 +1851,8 @@ def _attach_goal_intent_suggestion(
         # We modify the suggestion dict passed by reference so the caller can inject it into meta
         suggestion.update(suggestion_data)
 
-        return True
+        # Phase 22: Allow fall-through to populate generic meta
+        # return True
 
     if suggestion_id is not None:
         suggestion = dict(suggestion)
diff --git a/static/othello.js b/static/othello.js
index 7521f134..ff809bad 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4414,7 +4414,8 @@
           clientMessageId: entry.clientMessageId,
           statusEl,
           panelEl: actionsEl,
-          suggestionId: item.suggestionId
+          suggestionId: item.suggestionId,
+          payload: item.suggestion ? item.suggestion.payload : null
         });
         if (prevActiveGoalId !== othelloState.activeGoalId) {
           setActiveGoal(prevActiveGoalId);
@@ -5701,6 +5702,16 @@
             othelloState.activeConversationId = data.conversation_id;
         }
         const meta = data && data.meta ? data.meta : null;
+
+        // Phase 22: Capture virtual goal intent for User message
+        if (meta && meta.suggestions && Array.isArray(meta.suggestions)) {
+           meta.suggestions.forEach(s => {
+               if (s.type === 'goal_intent' && s.client_message_id) {
+                   addSecondarySuggestion(s.client_message_id, s);
+               }
+           });
+        }
+
         const isRoutineReady = !!(meta && meta.intent === "routine_ready" && meta.routine_suggestion_id);
         let replyText = data.reply || "[no reply]";
         if (isRoutineReady) {
```
