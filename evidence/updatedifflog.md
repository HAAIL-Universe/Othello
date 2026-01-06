# Cycle Status: COMPLETE (Phase 22.1 - Virtual Goal Apply)

## Todo Ledger
Planned:
- [x] Phase 22.1: Frontend: Collect context for virtual goals.
- [x] Phase 22.1: Frontend: Route createGoalFromSuggestion with context.
- [x] Phase 22.1: Backend: Accept virtual inputs in create_goal_from_message.
- [x] Phase 22.1: Backend: Append goal event for context seed.
Completed:
- [x] static/othello.js: Implemented context collection and updated payload.
- [x] api.py: Handled goal_context, virtual payload, and event logging.
Remaining:
- [ ] Done.

## Next Action
Stop and commit.

## Root Cause Anchors
- static/othello.js:4577 (Added collectGoalContext and updated createGoalFromSuggestion)
- api.py:4281 (Updated create_goal_from_message to accept context and virtual payload)

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 661a07fa..11972ec1 100644
--- a/api.py
+++ b/api.py
@@ -26,6 +26,7 @@ from werkzeug.middleware.proxy_fix import ProxyFix
 from db import routines_repository
 from db import suggestions_repository
 from db import goals_repository
+from db import goal_events_repository
 from db.database import get_connection
 import hashlib
 import json
@@ -4280,6 +4281,7 @@ def handle_message():
         # Phase 21: Manual Create Goal (Voice-First Confirmation)
         if user_id and ui_action == "create_goal_from_message":
              source_message_id = data.get("source_message_id")
+             goal_context = data.get("goal_context") # Phase 22: Context seed for goal activity
              override_title = data.get("title")
              override_desc = data.get("description")
              
@@ -4296,17 +4298,34 @@ def handle_message():
                      final_steps = passed_payload.get("steps") or []
                  
                  # Create the goal
-                 goal_id = goals_repository.create_goal(
-                     user_id=user_id,
-                     title=final_title,
-                     description=final_body,
-                     target_days=None 
+                 created_goal = goals_repository.create_goal(
+                     {
+                        "title": final_title,
+                        "description": final_body,
+                        "status": "active"
+                     },
+                     user_id=user_id
                  )
+                 goal_id = created_goal.get("id")
                  
                  # Add steps if present
                  if goal_id and final_steps:
                      for step in final_steps:
                          goals_repository.add_goal_step(user_id, goal_id, str(step))
+
+                 # Phase 22: Seed context if provided
+                 if goal_id and goal_context:
+                      goal_events_repository.append_goal_event(
+                          user_id=user_id,
+                          goal_id=goal_id,
+                          step_id=None,
+                          event_type="context_seed",
+                          payload={
+                              "source_client_message_id": source_message_id,
+                              "context": goal_context
+                          },
+                          request_id=request_id
+                      )
                          
                  return jsonify({
                      "reply": f"Goal '{final_title}' created.",
@@ -4320,7 +4339,7 @@ def handle_message():
              except Exception as e:
                  logger.error("Failed to create goal from message: %s", e)
                  return jsonify({
-                     "reply": "I couldn't create the goal right now.",
+                     "reply": f"I couldn't create the goal right now. Error: {str(e)}",
                      "request_id": request_id
                  })
diff --git a/static/othello.js b/static/othello.js
index ff809bad..14a4337c 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4574,6 +4574,30 @@
       });
     }
 
+    function collectGoalContext(startClientMessageId) {
+       if (!startClientMessageId || !othelloState.messagesByClientId[startClientMessageId]) return null;
+       const context = [];
+       let currentRow = othelloState.messagesByClientId[startClientMessageId].rowEl;
+       while (currentRow) {
+           if (currentRow.classList.contains("msg-row")) {
+               const role = currentRow.classList.contains("user") ? "user" : "assistant";
+               const bubble = currentRow.querySelector(".bubble");
+               if (bubble) {
+                   const clone = bubble.cloneNode(true);
+                   // Cleanup UI elements to get just text
+                   const meta = clone.querySelector(".meta");
+                   if (meta) meta.remove();
+                   const bars = clone.querySelectorAll(".commitment-bar, .plan-action-bar, .planner-card");
+                   bars.forEach(b => b.remove());
+                   
+                   context.push({ role, text: clone.textContent.trim() });
+               }
+           }
+           currentRow = currentRow.nextElementSibling;
+       }
+       return context.length > 0 ? context : null;
+    }
+
     async function createGoalFromSuggestion(opts) {
       const { title, description, clientMessageId, statusEl, panelEl, onSuccess, suggestionId, payload } = opts;
       const trimmedTitle = (title || "").trim();
@@ -4584,6 +4608,9 @@
       }
       disablePanelButtons(panelEl, true);
       if (statusEl) statusEl.textContent = "Saving goal...";
+      
+      const goalContext = collectGoalContext(clientMessageId);
+
       try {
         // Phase 21: Direct Chat Action (No v1/create)
         // If it's a virtual suggestion (no real ID) or even if it is, we prefer the chat action route
@@ -4596,7 +4623,8 @@
                  source_message_id: clientMessageId,
                  title: trimmedTitle,
                  description: trimmedDesc,
-                 payload: payload || (othelloState.goalIntentSuggestions[clientMessageId] ? othelloState.goalIntentSuggestions[clientMessageId].payload : null)
+                 payload: payload || (othelloState.goalIntentSuggestions[clientMessageId] ? othelloState.goalIntentSuggestions[clientMessageId].payload : null),
+                 goal_context: goalContext
              });
              // The API will return 'focus_goal' action which we handle in socket message
              return true;
```
