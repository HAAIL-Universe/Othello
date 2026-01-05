# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Phase 6: Draft Focus Polish (Fix 400 error, Unfocus behavior, Bubble cleanup)
- [x] Phase 7: Goal Draft Persistence & Edit Lane (Voice-first creation + editing)

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
--- a/api.py
+++ b/api.py
@@ -1086,6 +1086,50 @@
     dismissed.add(key)
     return True
 
+
+def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
+    from core.llm_wrapper import LLMWrapper
+    
+    system_prompt = (
+        "You are a goal extraction engine. Extract goal details from the user's request into a JSON object.\n"
+        "Required keys:\n"
+        "- title: string (concise goal title)\n"
+        "- target_days: integer or null (number of days to achieve)\n"
+        "- steps: array of strings (actionable steps)\n"
+        "- body: string or null (additional context/description)\n"
+        "Return ONLY valid JSON."
+    )
+    
+    try:
+        llm = LLMWrapper()
+        response = llm.chat_completion(
+            messages=[
+                {"role": "system", "content": system_prompt},
+                {"role": "user", "content": user_input}
+            ],
+            temperature=0.1,
+            max_tokens=500,
+            response_format={"type": "json_object"}
+        )
+        content = response.choices[0].message.content
+        return json.loads(content)
+    except Exception as e:
+        logging.error(f"Failed to generate goal draft payload: {e}")
+        # Fallback
+        return {
+            "title": _extract_goal_title_suggestion(user_input) or "New Goal",
+            "target_days": 7,
+            "steps": [],
+            "body": user_input
+        }
+
+
+def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction: str) -> Dict[str, Any]:
+    from core.llm_wrapper import LLMWrapper
+    
+    system_prompt = (
+        "You are a goal editing engine. Update the existing goal draft JSON based on the user's instruction.\n"
+        "Return the FULL updated JSON object with keys: title, target_days, steps, body.\n"
+        "Do not lose existing information unless instructed to change it.\n"
+        "Return ONLY valid JSON."
+    )
+    
+    try:
+        llm = LLMWrapper()
+        response = llm.chat_completion(
+            messages=[
+                {"role": "system", "content": system_prompt},
+                {"role": "user", "content": f"Current Payload: {json.dumps(current_payload)}\nInstruction: {user_instruction}"}
+            ],
+            temperature=0.1,
+            max_tokens=500,
+            response_format={"type": "json_object"}
+        )
+        content = response.choices[0].message.content
+        return json.loads(content)
+    except Exception as e:
+        logging.error(f"Failed to patch goal draft payload: {e}")
+        return current_payload
+
 
 def _extract_goal_title_suggestion(text: str) -> str:
@@ -4160,6 +4204,58 @@
             return jsonify({
                 "reply": "Could not dismiss draft.",
                 "request_id": request_id
             })
 
+        # Draft Focus: Create Draft (Voice-First)
+        # Trigger: "create a goal draft", "start a goal draft", etc.
+        is_create_draft = False
+        if user_id and user_input:
+            norm_input = user_input.strip().lower()
+            if "create a goal draft" in norm_input or "start a goal draft" in norm_input:
+                is_create_draft = True
+            elif re.search(r"\b(create|make|start)\b.*\bgoal\b.*\bdraft\b", norm_input):
+                is_create_draft = True
+        
+        if is_create_draft:
+            payload = _generate_goal_draft_payload(user_input)
+            suggestion = suggestions_repository.create_suggestion(
+                user_id=user_id,
+                kind="goal",
+                payload=payload,
+                provenance={"source": "api_message_create_goal_draft", "original_text": user_input},
+                status="pending"
+            )
+            
+            draft_id = suggestion["id"]
+            
+            # Construct response with draft context
+            response = {
+                "reply": "I've drafted that goal for you. What would you like to change first?",
+                "draft_context": {
+                    "draft_id": draft_id,
+                    "draft_type": "goal",
+                    "source_message_id": client_message_id
+                },
+                "draft_payload": payload,
+                "request_id": request_id
+            }
+            
+            # Add to meta.suggestions for completeness
+            meta = response.setdefault("meta", {})
+            suggestions = meta.setdefault("suggestions", [])
+            suggestion_out = dict(suggestion)
+            suggestion_out["suggestion_id"] = draft_id
+            suggestions.append(suggestion_out)
+            
+            return jsonify(response)
+
+        # Draft Focus: Edit Draft (While Pending)
+        # Trigger: draft_id present + draft_type="goal" + NO ui_action
+        if user_id and data.get("draft_id") and data.get("draft_type") == "goal" and not ui_action:
+            draft_id = data.get("draft_id")
+            try:
+                draft_id = int(draft_id)
+                draft = suggestions_repository.get_suggestion(user_id, draft_id)
+                
+                if draft and draft.get("status") == "pending":
+                    # This is an edit instruction
+                    current_payload = draft.get("payload", {})
+                    updated_payload = _patch_goal_draft_payload(current_payload, user_input)
+                    
+                    # Update DB
+                    updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
+                    
+                    response = {
+                        "reply": "Updated the draft.",
+                        "draft_context": {
+                            "draft_id": draft_id,
+                            "draft_type": "goal",
+                            "source_message_id": client_message_id
+                        },
+                        "draft_payload": updated_payload,
+                        "request_id": request_id
+                    }
+                    return jsonify(response)
+                    
+            except (ValueError, TypeError):
+                pass
+
         # --- Phase 3.2: Chat Command Router ---
```

## Verification Results
- [x] Send: “create a goal draft, title goal flow test, target 7 days, five steps, don’t save yet” → Response includes `draft_context` + `draft_payload`, Draft ribbon appears.
- [x] Send: “change step 2 to ‘Do X’” → Same `draft_id`, payload updated, ribbon remains.
- [x] Click Confirm → Goal is created, draft clears.
- [x] Repeat and click Dismiss/Unfocus → Draft clears and suggestion marked dismissed.
- [x] Refresh page mid-draft → Draft restores from localStorage and still exists server-side.
- [x] No regressions: normal chat messages still work.
