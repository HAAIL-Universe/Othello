# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Phase 6: Draft Focus Polish (Fix 400 error, Unfocus behavior, Bubble cleanup)
- [x] Phase 7: Goal Draft Persistence & Edit Lane (Voice-first creation + editing)
- [x] Phase 8: Draft Visibility + Step Generation (Deterministic steps + UI preview)
- [x] Phase 9: Fix Generate Steps (0 steps) + Continuous Draft Editing
- [x] Phase 10: Fix Draft Steps Visibility (Ribbon Overlay + Reply Steps)
- [x] Phase 11: Fix Deterministic Draft Edits (No Regression)
- [x] Phase 12: Fix Step Generation + Step Edit Gaps + Preview Sync
- [x] Phase 13: Confirm Draft End-to-End + State Cleanup + Regenerate UI

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index 34567890..abcdef12 100644
--- a/api.py
+++ b/api.py
@@ -4218,18 +4218,58 @@ def handle_message():
             
             if draft:
                 draft_id = draft["id"]
+                
+                # --- PHASE 13: Sanitize Payload ---
+                current_payload = draft.get("payload") or {}
+                
+                # 1. Title
+                title = str(current_payload.get("title", "")).strip()
+                if not title:
+                    title = "New Goal"
+                
+                # 2. Target Days
+                try:
+                    target_days = int(current_payload.get("target_days", 7))
+                except:
+                    target_days = 7
+                
+                # 3. Steps
+                raw_steps = current_payload.get("steps", [])
+                if not isinstance(raw_steps, list):
+                    raw_steps = []
+                
+                # Filter blanks & Dedupe
+                steps = []
+                seen = set()
+                for s in raw_steps:
+                    s_str = str(s).strip()
+                    if s_str:
+                        k = s_str.lower()
+                        if k not in seen:
+                            seen.add(k)
+                            steps.append(s_str)
+                
+                # 4. Body
+                body = str(current_payload.get("body", "")).strip()
+                
+                # Update Payload
+                sanitized_payload = {
+                    "title": title,
+                    "target_days": target_days,
+                    "steps": steps,
+                    "body": body
+                }
+                
+                # Persist sanitized payload before confirming
+                suggestions_repository.update_suggestion_payload(user_id, draft_id, sanitized_payload)
+
                 # Apply decision (Accept)
                 results = _apply_suggestion_decisions(
                     user_id, 
                     [{"suggestion_id": draft_id, "action": "accept", "reason": "user_confirmed_via_chat"}],
                     event_source="api_message_confirm"
                 )
                 
                 if results and results[0].get("ok"):
                     res = results[0]
                     saved_goal = res.get("goal")
                     goal_id = saved_goal.get("id") if saved_goal else None
                     
+                    meta = {}
+                    if not steps:
+                        meta["steps_empty"] = True
+
                     return jsonify({
                         "reply": f"Goal confirmed! I've saved '{saved_goal.get('title')}' and set it as your active focus.",
-                        "saved_goal": {"goal_id": goal_id, "title": saved_goal.get("title")},
+                        "saved_goal": {
+                            "goal_id": goal_id, 
+                            "title": saved_goal.get("title"),
+                            "target_days": target_days,
+                            "steps_count": len(steps)
+                        },
+                        "draft_cleared": True,
                         "active_goal_id": goal_id,
                         "agent_status": {"planner_active": True},
                         "request_id": request_id,
+                        "meta": meta
                     })
             
             # If no draft found or confirm failed
diff --git a/static/othello.js b/static/othello.js
index 90abcdef..12345678 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -833,7 +833,8 @@
       creatingRoutine: false,
       needsRoutineRefresh: false,
       pendingRoutineSuggestionId: null,
-      pendingRoutineAcceptFn: null
+      pendingRoutineAcceptFn: null,
+      isGeneratingSteps: false
     };
     let devResetEnabled = false;
 
@@ -3791,13 +3792,18 @@
               e.stopPropagation();
               if (othelloState.isGeneratingSteps) return;
               
               othelloState.isGeneratingSteps = true;
               genStepsBtn.disabled = true;
               genStepsBtn.textContent = "Generating...";
+              const regenBtn = actionsDiv.querySelector(".regen-btn");
+              if (regenBtn) regenBtn.disabled = true;
               
               try {
                   await sendMessage("", { ui_action: "generate_draft_steps" });
               } finally {
                   othelloState.isGeneratingSteps = false;
                   if (genStepsBtn) { // Check if still exists
                       genStepsBtn.disabled = false;
                       genStepsBtn.textContent = "Generate Steps";
                   }
+                  if (regenBtn) regenBtn.disabled = false;
               }
           };
           
+          const regenStepsBtn = document.createElement("button");
+          regenStepsBtn.textContent = "Regenerate";
+          regenStepsBtn.className = "ribbon-btn regen-btn";
+          regenStepsBtn.onclick = async (e) => {
+              e.stopPropagation();
+              if (othelloState.isGeneratingSteps) return;
+              
+              othelloState.isGeneratingSteps = true;
+              regenStepsBtn.disabled = true;
+              regenStepsBtn.textContent = "Generating...";
+              genStepsBtn.disabled = true;
+              
+              try {
+                  await sendMessage("", { ui_action: "regenerate_draft_steps" });
+              } finally {
+                  othelloState.isGeneratingSteps = false;
+                  if (regenStepsBtn) {
+                      regenStepsBtn.disabled = false;
+                      regenStepsBtn.textContent = "Regenerate";
+                  }
+                  if (genStepsBtn) genStepsBtn.disabled = false;
+              }
+          };
+          
           const confirmBtn = document.createElement("button");
           confirmBtn.textContent = "Confirm";
           confirmBtn.className = "ribbon-btn confirm-btn";
@@ -3818,6 +3844,7 @@
           };
 
           actionsDiv.appendChild(genStepsBtn);
+          actionsDiv.appendChild(regenStepsBtn);
           actionsDiv.appendChild(confirmBtn);
           actionsDiv.appendChild(dismissBtn);
 
@@ -4000,6 +4027,7 @@
       // Clear draft state on new chat/reset
       othelloState.activeDraft = null;
+      othelloState.activeDraftPayload = null;
       localStorage.removeItem("othello_active_draft");
+      localStorage.removeItem("othello_active_draft_payload");
       updateFocusRibbon();
     }
 
@@ -5830,6 +5858,12 @@
             othelloState.activeDraft = null;
             othelloState.activeDraftPayload = null;
             localStorage.removeItem("othello_active_draft");
             localStorage.removeItem("othello_active_draft_payload");
+            
+            if (data.saved_goal.goal_id) {
+                othelloState.activeGoalId = data.saved_goal.goal_id;
+                showToast(`Goal created: ${data.saved_goal.title || "New Goal"}`);
+            }
+            
             updateFocusRibbon();
         }
```

## Evidence Bundle

### A) Verification Script (verify_phase13.py)
Ran `verify_phase13.py` to test backend confirmation logic.

**Test 1: Confirm Draft Sanitization**
- Input: Draft with messy payload (spaces, blanks, duplicates).
- Result: `update_suggestion_payload` called with sanitized data. Response includes `saved_goal` and `draft_cleared`.
- Status: **PASS**

**Test 2: Confirm Empty Steps**
- Input: Draft with empty steps.
- Result: Response includes `meta.steps_empty=True`.
- Status: **PASS**

### B) Frontend Logic
- **Regenerate Button**: Added to ribbon, shares `isGeneratingSteps` lock with Generate button.
- **Confirm Handling**: Clears draft state (memory + local storage) and switches focus to the new goal.
- **Cleanup**: `clearChatState` now fully clears draft payload.

