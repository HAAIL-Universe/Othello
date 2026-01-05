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

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index abcdef12..34567890 100644
--- a/api.py
+++ b/api.py
@@ -1187,18 +1187,28 @@ def _apply_goal_draft_deterministic_edit(current_payload: Dict[str, Any], user_i
         steps = updated_payload.get("steps", [])
         if not isinstance(steps, list):
             steps = []
             
-        # Extend if needed
-        if step_idx >= 0:
-            if step_idx >= len(steps):
-                steps.extend([""] * (step_idx - len(steps) + 1))
-                
-            steps[step_idx] = new_step_text
-            updated_payload["steps"] = steps
-            return updated_payload, True, f"Updated step {step_idx + 1}."
+        # Sanitize existing steps (remove blanks)
+        steps = [str(s).strip() for s in steps if str(s).strip()]
+        
+        current_count = len(steps)
+        target_idx = step_idx
+        
+        if current_count == 0:
+            if target_idx == 0:
+                # Set first step
+                steps = [new_step_text]
+                updated_payload["steps"] = steps
+                return updated_payload, True, "Added step 1."
+            else:
+                return current_payload, True, "No steps exist yet. Generate steps first, or set step 1 before step 2."
+        else:
+            if target_idx < current_count:
+                # Edit existing
+                steps[target_idx] = new_step_text
+                updated_payload["steps"] = steps
+                return updated_payload, True, f"Updated step {target_idx + 1}."
+            elif target_idx == current_count:
+                # Append next
+                steps.append(new_step_text)
+                updated_payload["steps"] = steps
+                return updated_payload, True, f"Added step {target_idx + 1}."
+            else:
+                # Gap
+                return current_payload, True, f"You currently have {current_count} steps. Add step {current_count + 1} next (or generate steps)."
 
     return current_payload, False, ""
 
@@ -4326,11 +4336,14 @@ def handle_message():
 
         # Draft Focus: Generate Steps
         # Trigger: ui_action="generate_draft_steps" OR voice command "generate steps" with active draft
         is_generate_steps = (ui_action == "generate_draft_steps")
-        if not is_generate_steps and user_id and data.get("draft_id") and data.get("draft_type") == "goal":
+        is_regenerate_steps = (ui_action == "regenerate_draft_steps")
+        
+        if not (is_generate_steps or is_regenerate_steps) and user_id and data.get("draft_id") and data.get("draft_type") == "goal":
              norm_input = user_input.strip().lower()
              if "generate steps" in norm_input or "suggest steps" in norm_input:
                  is_generate_steps = True
+             elif "regenerate steps" in norm_input:
+                 is_regenerate_steps = True
 
-        if is_generate_steps and user_id and data.get("draft_id"):
+        if (is_generate_steps or is_regenerate_steps) and user_id and data.get("draft_id"):
             draft_id = data.get("draft_id")
             try:
                 draft_id = int(draft_id)
@@ -4343,23 +4356,68 @@ def handle_message():
                         except:
                             current_payload = {}
 
-                    updated_payload = _generate_draft_steps_payload(current_payload)
+                    # Normalize existing steps
+                    existing_steps = current_payload.get("steps", [])
+                    if not isinstance(existing_steps, list):
+                        existing_steps = []
+                    existing_steps = [str(s).strip() for s in existing_steps if str(s).strip()]
+                    
+                    # Idempotency check (only for generate, not regenerate)
+                    if is_generate_steps and len(existing_steps) >= 5:
+                        response = {
+                            "reply": f"Steps already generated ({len(existing_steps)}). Say 'regenerate steps' to replace them.",
+                            "draft_context": {
+                                "draft_id": draft_id,
+                                "draft_type": "goal",
+                                "source_message_id": client_message_id
+                            },
+                            "draft_payload": current_payload,
+                            "request_id": request_id
+                        }
+                        # Update DB with normalized steps to be safe
+                        current_payload["steps"] = existing_steps
+                        suggestions_repository.update_suggestion_payload(user_id, draft_id, current_payload)
+                        response["draft_payload"] = current_payload
+                        return jsonify(response)
+
+                    payload_to_process = current_payload.copy()
+                    payload_to_process["steps"] = existing_steps # Use normalized
+                    
+                    if is_regenerate_steps:
+                        # Clear steps for regeneration so LLM generates fresh ones
+                        payload_to_process["steps"] = []
+                    
+                    updated_payload = _generate_draft_steps_payload(payload_to_process)
                     
                     # Fallback Logic
                     steps = updated_payload.get("steps", [])
                     if not isinstance(steps, list):
                         steps = []
                     
                     # Sanitize steps
-                    steps = [str(s) for s in steps if s]
+                    steps = [str(s).strip() for s in steps if str(s).strip()]
+                    
+                    # Deduplicate (case-insensitive)
+                    seen = set()
+                    deduped_steps = []
+                    for s in steps:
+                        k = s.lower()
+                        if k not in seen:
+                            seen.add(k)
+                            deduped_steps.append(s)
+                    steps = deduped_steps
                     
                     used_fallback = False
                     if not steps:
                         used_fallback = True
                         steps = [
                             "Define success criteria",
                             "Break down into sub-tasks",
                             f"Schedule daily work for {updated_payload.get('target_days', 7)} days",
                             "Execute and track progress",
                             "Review and adjust"
                         ]
                         logging.warning(f"Used fallback steps for draft {draft_id}")
+                    
+                    # Ensure at least 5 steps if we have fewer
+                    if len(steps) < 5:
+                        defaults = [
+                            "Define success criteria",
+                            "Break down into sub-tasks",
+                            "Identify resources needed",
+                            "Set milestones",
+                            "Execute and track progress",
+                            "Review and adjust",
+                            "Celebrate completion"
+                        ]
+                        for d in defaults:
+                            if len(steps) >= 5:
+                                break
+                            if d.lower() not in seen:
+                                steps.append(d)
+                                seen.add(d.lower())
                     
                     updated_payload["steps"] = steps
 
diff --git a/static/othello.js b/static/othello.js
index 12345678..90abcdef 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -3738,7 +3738,8 @@
         }
         
         const p = othelloState.activeDraftPayload;
-        const steps = p.steps || [];
+        // Filter blank steps
+        const steps = (p.steps || []).filter(s => typeof s === "string" && s.trim());
         
         console.debug("[Othello UI] Draft preview steps:", steps.length);
         
@@ -3783,9 +3784,20 @@
           const genStepsBtn = document.createElement("button");
           genStepsBtn.textContent = "Generate Steps";
           genStepsBtn.className = "ribbon-btn";
-          genStepsBtn.onclick = (e) => {
+          genStepsBtn.onclick = async (e) => {
               e.stopPropagation();
-              sendMessage("", { ui_action: "generate_draft_steps" });
+              if (othelloState.isGeneratingSteps) return;
+              
+              othelloState.isGeneratingSteps = true;
+              genStepsBtn.disabled = true;
+              genStepsBtn.textContent = "Generating...";
+              
+              try {
+                  await sendMessage("", { ui_action: "generate_draft_steps" });
+              } finally {
+                  othelloState.isGeneratingSteps = false;
+                  if (genStepsBtn) { // Check if still exists
+                      genStepsBtn.disabled = false;
+                      genStepsBtn.textContent = "Generate Steps";
+                  }
+              }
           };
           
           const confirmBtn = document.createElement("button");
```

## Evidence Bundle

### A) Verification Script (verify_phase12.py)
Ran `verify_phase12.py` to test gap prevention, idempotency, and regeneration.

**Test 1: Deterministic Edit Gaps**
- Input: "Change step 2 to Step 2" (when 0 steps exist)
- Result: Rejected with "No steps exist yet...". Payload unchanged.
- Input: "Change step 1 to Step 1"
- Result: Accepted. Payload updated to `["Step 1"]`.
- Status: **PASS**

**Test 2: Generate Steps Idempotency**
- Input: `ui_action="generate_draft_steps"` (when 5 steps exist)
- Result: "Steps already generated (5)". LLM NOT called.
- Status: **PASS**

**Test 3: Regenerate Steps**
- Input: `ui_action="regenerate_draft_steps"`
- Result: Steps replaced with new list from Mock LLM.
- Status: **PASS**

### B) Frontend Logic
- **Double-Send Prevention**: Added `isGeneratingSteps` flag and button disable logic.
- **Preview Filtering**: `renderDraftPreview` now filters out blank steps, ensuring accurate count and display.

