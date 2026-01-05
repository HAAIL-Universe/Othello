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

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index 12345678..abcdef12 100644
--- a/api.py
+++ b/api.py
@@ -1148,6 +1148,56 @@ def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
         }
 
 
+def _apply_goal_draft_deterministic_edit(current_payload: Dict[str, Any], user_instruction: str) -> Tuple[Dict[str, Any], bool, str]:
+    """
+    Attempts to apply deterministic edits to the draft payload based on user instruction.
+    Returns (updated_payload, handled, reply_suffix)
+    """
+    updated_payload = current_payload.copy()
+    handled = False
+    reply_suffix = ""
+    
+    # A) Title Change
+    # "change title to X", "update title to X", "set title to X"
+    title_match = re.search(r"\b(change|update|set)\b.*\btitle\b.*\bto\b\s+(.+)", user_instruction, re.IGNORECASE)
+    if title_match:
+        new_title = title_match.group(2).strip()
+        # Remove quotes if present
+        if (new_title.startswith('"') and new_title.endswith('"')) or (new_title.startswith("'") and new_title.endswith("'")):
+            new_title = new_title[1:-1]
+            
+        updated_payload["title"] = new_title
+        return updated_payload, True, f"Updated title to '{new_title}'."
+
+    # B) Target Days Change
+    # "change target to 10 days", "set target days to 10", "make it 14 days"
+    target_match = re.search(r"\b(change|update|set|make)\b.*\b(target|days)\b.*?\b(\d+)\b", user_instruction, re.IGNORECASE)
+    if target_match:
+        days = int(target_match.group(3))
+        updated_payload["target_days"] = days
+        return updated_payload, True, f"Updated target to {days} days."
+
+    # C) Step Change
+    # "change step 2 to X", "update step 3 to X", "set step 1 to X"
+    step_match = re.search(r"\b(change|update|set)\b.*\bstep\b\s+(\d+)\b.*\bto\b\s+(.+)", user_instruction, re.IGNORECASE)
+    if step_match:
+        step_idx = int(step_match.group(2)) - 1 # 0-based
+        new_step_text = step_match.group(3).strip()
+        # Remove quotes
+        if (new_step_text.startswith('"') and new_step_text.endswith('"')) or (new_step_text.startswith("'") and new_step_text.endswith("'")):
+            new_step_text = new_step_text[1:-1]
+            
+        steps = updated_payload.get("steps", [])
+        if not isinstance(steps, list):
+            steps = []
+            
+        # Extend if needed
+        if step_idx >= 0:
+            if step_idx >= len(steps):
+                steps.extend([""] * (step_idx - len(steps) + 1))
+                
+            steps[step_idx] = new_step_text
+            updated_payload["steps"] = steps
+            return updated_payload, True, f"Updated step {step_idx + 1}."
+
+    return current_payload, False, ""
+
+
 def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction: str) -> Dict[str, Any]:
     from core.llm_wrapper import LLMWrapper
     
@@ -1166,7 +1216,23 @@ def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction:
             response_format={"type": "json_object"}
         )
         content = response.choices[0].message.content
-        return json.loads(content)
+        updated_payload = json.loads(content)
+        
+        # Hardening: Prevent regressions
+        norm_input = user_instruction.lower()
+        
+        # If title not mentioned, restore original
+        if "title" not in norm_input and current_payload.get("title"):
+            updated_payload["title"] = current_payload["title"]
+            
+        # If target/days not mentioned, restore original
+        if "target" not in norm_input and "days" not in norm_input and current_payload.get("target_days"):
+            updated_payload["target_days"] = current_payload["target_days"]
+            
+        # If steps not mentioned, restore original steps if new ones are empty/missing
+        if "step" not in norm_input:
+             new_steps = updated_payload.get("steps")
+             if not new_steps or not isinstance(new_steps, list):
+                 updated_payload["steps"] = current_payload.get("steps", [])
+
+        return updated_payload
     except Exception as e:
         logging.error(f"Failed to patch goal draft payload: {e}")
         return current_payload
@@ -4236,14 +4302,19 @@ def handle_message():
                 if draft and draft.get("status") == "pending":
                     # This is an edit instruction
                     current_payload = draft.get("payload", {})
-                    updated_payload = _patch_goal_draft_payload(current_payload, user_input)
+                    
+                    # 1. Try deterministic edit
+                    updated_payload, handled, reply_suffix = _apply_goal_draft_deterministic_edit(current_payload, user_input)
+                    
+                    # 2. Fallback to LLM if not handled
+                    if not handled:
+                        updated_payload = _patch_goal_draft_payload(current_payload, user_input)
+                        reply_suffix = "Updated the draft."
                     
                     # Update DB
                     updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                     
                     title = updated_payload.get("title", "Goal")
                     steps_count = len(updated_payload.get("steps", []))
                     
                     response = {
-                        "reply": f"Updated draft: '{title}' ({steps_count} steps).",
+                        "reply": f"{reply_suffix} Draft: '{title}' ({steps_count} steps).",
                         "draft_context": {
                             "draft_id": draft_id,
                             "draft_type": "goal",
                             "source_message_id": client_message_id
                         },
                         "draft_payload": updated_payload,
-                        "request_id": request_id
+                        "request_id": request_id
                     }
                     return jsonify(response)
```

## Evidence Bundle

### A) Verification Script (verify_phase11.py)
Ran `verify_phase11.py` to test deterministic edits and regression prevention.

**Test 1: Deterministic Title Edit**
- Input: "Change title to New Deterministic Title"
- Result: Payload title updated. Reply: "Updated title to 'New Deterministic Title'..."
- Status: **PASS**

**Test 2: Deterministic Step Edit**
- Input: "Change step 2 to Updated Step 2"
- Result: Payload step 2 updated. Reply: "Updated step 2..."
- Status: **PASS**

**Test 3: LLM Fallback Regression Prevention**
- Input: "Make the description better" (Mock LLM returns bad title/steps)
- Result: Payload title and steps preserved (restored from current_payload).
- Status: **PASS**

