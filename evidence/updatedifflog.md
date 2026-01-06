# Cycle Status: COMPLETE (Phase 21)

## Todo Ledger
Planned:
- [x] Phase 21: Voice-first draft polish + Ribbon UI Fix.
- [x] Phase 21: Reliability Hardening (500 Error Fixes).
- [x] Phase 21: Voice Clarification Heuristics.
Completed:
- [x] API: Deterministic "Show Steps" router (supports drafts + goals, prevents LLM calls).
- [x] API: Voice-friendly replies for auto-gen steps ("Got it. Here are...") and edits.
- [x] UI: Fixed "Drafting Goal" ribbon layout (removed fixed height, added wrap, overflow visible).
- [x] API: Added `_normalize_goal_draft_payload` to guarantee `steps` is never null (Fixes 500 error).
- [x] API: Implemented clarification gating in `_attach_goal_intent_suggestion` (skips auto-draft for vague inputs).
- [x] API: Enforced immediate LLM extraction for drafts to persist seed steps.
Remaining:
- [ ] Phase 22 tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index a0dd02aa..95dd8d41 100644
--- a/api.py
+++ b/api.py
@@ -1084,6 +1084,34 @@ def _record_suggestion_dismissal(
     return True
 
 
+def _normalize_goal_draft_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
+    """Ensure draft payload always has valid types."""
+    if not isinstance(payload, dict):
+        payload = {}
+    
+    # Ensure steps is a list
+    steps = payload.get("steps")
+    if not isinstance(steps, list):
+        payload["steps"] = []
+    
+    # Ensure target_days is int or None
+    td = payload.get("target_days")
+    if td is not None:
+        try:
+            payload["target_days"] = int(td)
+        except (ValueError, TypeError):
+            payload["target_days"] = None
+
+    # Normalize strings
+    for k in ["title", "body", "description"]:
+        if payload.get(k) is None:
+            payload[k] = ""
+        else:
+            payload[k] = str(payload[k]).strip()
+
+    return payload
+
+
 def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
     from core.llm_wrapper import LLMWrapper
 
@@ -1109,7 +1137,7 @@ def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
             response_format={"type": "json_object"}
         )
         content = response.choices[0].message.content
-        return json.loads(content)
+        return _normalize_goal_draft_payload(json.loads(content))
     except Exception as e:
         logging.error(f"Failed to generate goal draft payload: {e}")
         # Fallback
@@ -1273,7 +1301,7 @@ def _generate_draft_steps_payload(current_payload: Dict[str, Any]) -> Dict[str,
             response_format={"type": "json_object"}
         )
         content = response.choices[0].message.content
-        return json.loads(content)
+        return _normalize_goal_draft_payload(json.loads(content))
     except Exception as e:
         logging.error(f"Failed to generate draft steps: {e}")
         return current_payload
@@ -1780,14 +1808,25 @@ def _attach_goal_intent_suggestion(
         return False
     suggestion_id = suggestion.get("suggestion_id") or suggestion.get("id")
     if suggestion_id is None and user_id:
-        title = suggestion.get("title_suggestion") or _extract_goal_title_suggestion(user_input)
-        body = suggestion.get("body_suggestion") or (user_input or "").strip()
-        payload = {
-            "title": title,
-            "body": body,
-            "description": body,
-            "confidence": suggestion.get("confidence"),
-        }
+        # Phase 21: Clarification Gating
+        # If the input is too short and lacks planning keywords, defer to regular chat (which will ask questions)
+        raw_text = (user_input or "").strip()
+        is_vague = len(raw_text) < 25 and not any(k in raw_text.lower() for k in ["day", "week", "month", "step", "plan", "build", "create"])
+        
+        if is_vague:
+            logger.info("API: Goal intent detected but input is vague (%d chars). Skipping automatic drafting.", len(raw_text))
+            return False
+
+        # Phase 21: Generating full draft immediately to persist seed steps
+        draft_payload = _generate_goal_draft_payload(raw_text)
+        
+        # Ensure title fallback
+        if not draft_payload.get("title"):
+             draft_payload["title"] = suggestion.get("title_suggestion") or _extract_goal_title_suggestion(raw_text) or "New Goal"
+
+        payload = draft_payload
+        payload["description"] = payload.get("body")
+        payload["confidence"] = suggestion.get("confidence")
+        
+        title = payload["title"] # Required for deduplication below
+
         provenance = {
             "source": "api_message_goal_intent",

```
