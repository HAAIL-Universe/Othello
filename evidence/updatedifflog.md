# Cycle Status: COMPLETE (Phase 22.3 - Auto-Focus Goal)

## Todo Ledger
Planned:
- [x] Phase 22.1: Frontend: Collect context for virtual goals.
- [x] Phase 22.1: Frontend: Route createGoalFromSuggestion with context.
- [x] Phase 22.1: Backend: Accept virtual inputs in create_goal_from_message.
- [x] Phase 22.1: Backend: Append goal event for context seed.
- [x] Phase 22.1 Hotfix: Robust goal_id extraction in api.py.
- [x] Phase 22.2: Backend: Hydrate goal.conversation from context_seed if empty.
- [x] Phase 22.3: Frontend: Auto-focus goal after virtual creation.
Completed:
- [x] static/othello.js: Implemented context collection and updated payload.
- [x] api.py: Handled goal_context, virtual payload, and event logging.
- [x] api.py: Added type check for created_goal return value.
- [x] db/db_goal_manager.py: Implemented fallback in _db_to_legacy_format.
- [x] static/othello.js: Added ui_action_call handling in sendMessage.
Remaining:
- [ ] Done.

## Next Action
Stop and commit.

## Root Cause Anchors
- static/othello.js:5724 (Added ui_action_call handling for focus_goal)

## Full Unified Diff
```diff
diff --git a/static/othello.js b/static/othello.js
index 14a4337c..b712211e 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -5722,6 +5722,23 @@
         }
 
         const data = await res.json();
+        
+        // Phase 22.3: Handle UI Actions from backend (Auto-Focus)
+        if (data.ui_action_call === "focus_goal" && data.ui_action_payload && data.ui_action_payload.goal_id) {
+             const goalId = data.ui_action_payload.goal_id;
+             setActiveGoal(goalId);
+             if (othelloState.currentView !== "goals") {
+                 switchView("goals");
+             }
+             // showGoalDetail will render loading state and fetch valid data
+             showGoalDetail(goalId);
+        } else if (data.redirect_to && typeof data.redirect_to === 'string') {
+             const goalMatch = data.redirect_to.match(/\/goals\/(\d+)/);
+             if (goalMatch && goalMatch[1]) {
+                 const goalId = parseInt(goalMatch[1], 10);
+                 setActiveGoal(goalId);
+                 if (othelloState.currentView !== "goals") {
+                     switchView("goals");
+                 }
+                 showGoalDetail(goalId);
+             }
+        }
+
         if (data.conversation_id) {
             othelloState.activeConversationId = data.conversation_id;
         }
```
