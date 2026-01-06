# Cycle Status: COMPLETE (Phase 22.5 - Session Continuity Fix)

## Todo Ledger
Planned:
- [x] Phase 22.5: Implement session resolution logic if definition is missing in `handle_message`.
- [x] Phase 22.5: Ensure `create_message` uses `source="user"` for hygiene.
- [x] Phase 22.5: Verify session usage in persistence and context loading.
Completed:
- [x] api.py: Added fallback to `list_sessions`/`create_session` when `conversation_id` is missing.
- [x] api.py: Updated `_persist_chat_exchange` to set `source="user"`.

## Next Action
Commit and Push.

## Root Cause Anchors
- api.py:5557 (Missing session resolution logic led to fragmented context).

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 517e8337..ed7f05d2 100644
--- a/api.py
+++ b/api.py
@@ -5553,6 +5553,20 @@ def handle_message():
 
         companion_context = None
         persist_enabled = _should_persist_chat()
+
+        # Ensure session continuity: if missing, resume most recent or create new
+        if persist_enabled and not conversation_id:
+            try:
+                from db.messages_repository import list_sessions, create_session
+                _recent_sessions = list_sessions(user_id, limit=1)
+                if _recent_sessions:
+                    conversation_id = _recent_sessions[0]["conversation_id"]
+                else:
+                    _new_sess = create_session(user_id)
+                    conversation_id = _new_sess.get("id")
+            except Exception as e:
+                logger.warning("API: failed to resolve session_id: %s", e)
+
         if persist_enabled:
             companion_context = _load_companion_context(user_id, logger, channel=effective_channel, conversation_id=conversation_id)
 
@@ -5568,7 +5582,7 @@ def handle_message():
                 create_message(
                     user_id=user_id,
                     transcript=user_input,
-                    source="text",
+                    source="user",
                     channel=effective_channel,
                     status="final",
                     session_id=conversation_id,
```
