# EVIDENCE REPORT: Backend & DB Analysis for Conversations/Threads

## Cycle Status
IN_PROGRESS

## Todo Ledger
- [x] Phase 0: Evidence Gate
- [x] Phase 1: Backend Implementation (API endpoints)
- [ ] Phase 2: Frontend Implementation (UI for New Chat and switching)
- [ ] Phase 3: Optional Delete
- [ ] Runtime Verification

## Next Action
Implement Phase 2: Frontend "New Chat" and conversation switching.

## FULL unified diff patch
```diff
diff --git a/api.py b/api.py
index c9338b7c..3146c3e2 100644
--- a/api.py
+++ b/api.py
@@ -3799,6 +3799,28 @@ def _process_insights_pipeline(*, user_text: str, assistant_text: str, user_id:
         return meta
 
 
+@app.route("/api/conversations", methods=["POST"])
+@require_auth
+def create_conversation():
+    user_id, error = _get_user_id_or_error()
+    if error:
+        return error
+    from db.messages_repository import create_session
+    session = create_session(user_id)
+    return jsonify({"conversation_id": session.get("id")})
+
+
+@app.route("/api/conversations", methods=["GET"])
+@require_auth
+def list_conversations():
+    user_id, error = _get_user_id_or_error()
+    if error:
+        return error
+    from db.messages_repository import list_sessions
+    sessions = list_sessions(user_id, limit=50)
+    return jsonify({"conversations": sessions})
+
+
 @app.route("/api/message", methods=["POST"])
 @require_auth
 def handle_message():
@@ -3880,14 +3902,23 @@ def handle_message():
         if raw_client_message_id is not None:
             client_message_id = str(raw_client_message_id).strip() or None
 
+        raw_conversation_id = data.get("conversation_id")
+        conversation_id = None
+        if raw_conversation_id is not None:
+            try:
+                conversation_id = int(raw_conversation_id)
+            except (ValueError, TypeError):
+                pass
+
         logger.info(
-            "API: message meta request_id=%s current_view=%s current_mode=%s keys=%s goal_id=%s active_goal_id=%s",
+            "API: message meta request_id=%s current_view=%s current_mode=%s keys=%s goal_id=%s active_goal_id=%s conversation_id=%s",
             request_id,
             current_view,
             current_mode,
             list(data.keys()),
             data.get("goal_id"),
             data.get("active_goal_id"),
+            conversation_id,
         )
 
         _log_request_start(raw_goal_id)
@@ -4562,6 +4593,7 @@ def handle_message():
                     source="text",
                     channel=effective_channel,
                     status="final",
+                    session_id=conversation_id,
                 )
                 create_message(
                     user_id=user_id,
@@ -4569,6 +4601,7 @@ def handle_message():
                     source="assistant",
                     channel=effective_channel,
                     status="final",
+                    session_id=conversation_id,
                 )
             except Exception as exc:
                 logger.warning(
@@ -4581,6 +4614,8 @@ def handle_message():
         def _respond(payload: Dict[str, Any]):
             reply_text = payload.get("reply") if isinstance(payload, dict) else None
             _persist_chat_exchange(reply_text)
+            if isinstance(payload, dict) and conversation_id:
+                payload["conversation_id"] = conversation_id
             return jsonify(payload)
 
         logger.info(
diff --git a/db/messages_repository.py b/db/messages_repository.py
index bec7c15d..18d6d42c 100644
--- a/db/messages_repository.py
+++ b/db/messages_repository.py
@@ -16,6 +16,24 @@ def create_session(user_id: str) -> Dict[str, Any]:
     return execute_and_fetch_one(query, (user_id,)) or {}
 
 
+def list_sessions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
+    """
+    List sessions for a user, ordered by most recent activity.
+    Computes updated_at from max message time if needed.
+    """
+    query = """
+        SELECT s.id as conversation_id, s.created_at,
+               COALESCE(MAX(m.created_at), s.created_at) as updated_at
+        FROM sessions s
+        LEFT JOIN messages m ON s.id = m.session_id
+        WHERE s.user_id = %s
+        GROUP BY s.id, s.created_at
+        ORDER BY updated_at DESC
+        LIMIT %s
+    """
+    return fetch_all(query, (user_id, limit))
+
+
 def create_message(
     *,
     user_id: str,
```
