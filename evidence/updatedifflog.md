# EVIDENCE REPORT: Backend & DB Analysis for Conversations/Threads

## Cycle Status
IN_PROGRESS

## Todo Ledger
- [x] Phase 0: Evidence Gate
- [x] Phase 1: Fix API Contract (Align conversation messages payload)
- [x] Phase 2: Fix Context Isolation (Scope message context + inserts)
- [x] Phase 3: Fix Inline Styles (Move to CSS classes)
- [ ] Phase 4: Runtime Verification (Pending Render)

## Next Action
Deploy + run checklist + report PASS/FAIL

## FULL unified diff patch
```diff
diff --git a/api.py b/api.py
index fbb4f564..8d7a8247 100644
--- a/api.py
+++ b/api.py
@@ -1275,6 +1275,7 @@ def _load_companion_context(
     channel: str = "companion",
     max_turns: int = CHAT_CONTEXT_TURNS,
     max_chars: int = CHAT_CONTEXT_MAX_CHARS,
+    conversation_id: Optional[int] = None,
 ) -> List[Dict[str, str]]:
     uid = str(user_id or "").strip()
     if not uid:
@@ -1286,8 +1287,11 @@ def _load_companion_context(
     if limit <= 0:
         return []
     try:
-        from db.messages_repository import list_recent_messages
-        rows = list_recent_messages(uid, limit=limit, channel=channel_name)
+        from db.messages_repository import list_recent_messages, list_messages_for_session
+        if conversation_id:
+            rows = list_messages_for_session(uid, conversation_id, limit=limit, channel=channel_name)
+        else:
+            rows = list_recent_messages(uid, limit=limit, channel=channel_name)
     except Exception as exc:
         logger.warning(
             "API: failed to load companion history user_id=%s error=%s",
@@ -3827,9 +3831,24 @@ def list_conversation_messages(conversation_id: int):
     user_id, error = _get_user_id_or_error()
     if error:
         return error
+
+    channel = request.args.get("channel") or "companion"
+    channel = str(channel).strip().lower()
+
+    limit = request.args.get("limit")
+    try:
+        limit_value = int(limit) if limit is not None else 50
+    except (TypeError, ValueError):
+        return _v1_error("VALIDATION_ERROR", "limit must be an integer", 400)
+
     from db.messages_repository import list_messages_for_session
-    rows = list_messages_for_session(user_id, conversation_id)
-    return jsonify({"conversation_id": conversation_id, "messages": rows})
+    rows = list_messages_for_session(user_id, conversation_id, limit=limit_value, channel=channel)
+    
+    provenance = {
+        "requested_channel": channel,
+        "conversation_id": conversation_id
+    }
+    return _v1_envelope(data={"messages": rows, "provenance": provenance, "conversation_id": conversation_id}, status=200)
 
 
 @app.route("/api/message", methods=["POST"])
@@ -4587,7 +4606,7 @@ def handle_message():
         companion_context = None
         persist_enabled = _should_persist_chat()
         if persist_enabled:
-            companion_context = _load_companion_context(user_id, logger, channel=effective_channel)
+            companion_context = _load_companion_context(user_id, logger, channel=effective_channel, conversation_id=conversation_id)
 
         def _persist_chat_exchange(reply_text: Optional[str]) -> None:
             if not reply_text or not _should_persist_chat():
diff --git a/db/messages_repository.py b/db/messages_repository.py
index 18d6d42c..8ef8c186 100644
--- a/db/messages_repository.py
+++ b/db/messages_repository.py
@@ -109,14 +109,19 @@ def list_messages_by_ids(user_id: str, message_ids: List[int]) -> List[Dict[str,
     return fetch_all(query, (user_id, message_ids))
 
 
-def list_messages_for_session(user_id: str, session_id: int) -> List[Dict[str, Any]]:
+def list_messages_for_session(user_id: str, session_id: int, limit: int = 50, channel: str = "companion") -> List[Dict[str, Any]]:
     query = """
-        SELECT id, user_id, session_id, source, transcript, status, created_at
-        FROM messages
-        WHERE user_id = %s AND session_id = %s
-        ORDER BY id ASC
+        SELECT id, user_id, session_id, source, channel, transcript, status, error, created_at
+        FROM (
+            SELECT id, user_id, session_id, source, channel, transcript, status, error, created_at
+            FROM messages
+            WHERE user_id = %s AND session_id = %s AND channel = %s
+            ORDER BY created_at DESC, id DESC
+            LIMIT %s
+        ) recent
+        ORDER BY created_at ASC, id ASC
     """
-    return fetch_all(query, (user_id, session_id))
+    return fetch_all(query, (user_id, session_id, channel, limit))
 
 
 def list_recent_messages(user_id: str, limit: int = 50, channel: str = "companion") -> List[Dict[str, Any]]:
diff --git a/othello_ui.html b/othello_ui.html
index c7480854..b2045946 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -33,10 +33,10 @@
         </div>
         <div class="settings-section">
           <div class="settings-label">Conversations</div>
-          <div id="settings-conversations-list" style="max-height: 200px; overflow-y: auto; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 1rem;">
+          <div id="settings-conversations-list" class="conversations-list">
             <!-- Populated by JS -->
           </div>
-          <button id="new-chat-settings-btn" class="settings-button" type="button" style="width:100%">+ New Chat</button>
+          <button id="new-chat-settings-btn" class="settings-button w-100" type="button">+ New Chat</button>
         </div>
         <div class="settings-section" id="settings-dev-reset" style="display:none;">
           <div class="danger-zone">
diff --git a/static/othello.css b/static/othello.css
index eaa136d7..3991c11b 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1743,3 +1743,46 @@
         max-width: 1100px;
       }
     }
+
+/* Conversations Settings */
+.conversations-list {
+  max-height: 200px;
+  overflow-y: auto;
+  border: 1px solid var(--border);
+  border-radius: 8px;
+  margin-bottom: 1rem;
+}
+
+.conversations-list-empty {
+  padding: 1rem;
+  color: var(--text-muted);
+}
+
+.conversation-row {
+  display: flex;
+  justify-content: space-between;
+  align-items: center;
+  padding: 0.8rem;
+  border-bottom: 1px solid var(--border);
+}
+
+.conversation-info-title {
+  font-weight: normal;
+}
+.conversation-info-title.current {
+  font-weight: bold;
+}
+
+.conversation-info-date {
+  font-size: 0.8rem;
+  color: var(--text-muted);
+}
+
+.conversation-switch-btn {
+  padding: 0.3rem 0.8rem;
+  font-size: 0.8rem;
+}
+
+.w-100 {
+  width: 100%;
+}
diff --git a/static/othello.js b/static/othello.js
index ae0ff730..46dfb294 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -564,31 +564,29 @@
           container.innerHTML = "";
           
           if (!conversations || conversations.length === 0) {
-              container.innerHTML = "<div style='padding:1rem;color:var(--text-muted);'>No conversations found.</div>";
+              container.innerHTML = "<div class='conversations-list-empty'>No conversations found.</div>";
               return;
           }

           conversations.forEach(conv => {
               const row = document.createElement("div");
               row.className = "conversation-row";
-              row.style = "display:flex;justify-content:space-between;align-items:center;padding:0.8rem;border-bottom:1px solid var(--border);";
               
               const info = document.createElement("div");
               const date = new Date(conv.updated_at || conv.created_at).toLocaleString();
               const isCurrent = conv.conversation_id === othelloState.activeConversationId;
               info.innerHTML = `
-                  <div style="font-weight:${isCurrent ? 'bold' : 'normal'}">
+                  <div class="conversation-info-title ${isCurrent ? 'current' : ''}">
                       ${isCurrent ? 'Current: ' : ''}Conversation #${conv.conversation_id}
                   </div>
-                  <div style="font-size:0.8rem;color:var(--text-muted)">${date}</div>
+                  <div class="conversation-info-date">${date}</div>
               `;
               
               const actions = document.createElement("div");
               if (!isCurrent) {
                   const switchBtn = document.createElement("button");
                   switchBtn.textContent = "Open";
-                  switchBtn.className = "btn-secondary";
-                  switchBtn.style = "padding:0.3rem 0.8rem;font-size:0.8rem;";
+                  switchBtn.className = "btn-secondary conversation-switch-btn";
                   switchBtn.onclick = () => switchConversation(conv.conversation_id);
                   actions.appendChild(switchBtn);
               }
```
