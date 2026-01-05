# EVIDENCE REPORT: Backend & DB Analysis for Conversations/Threads

## Cycle Status
IN_PROGRESS

## Todo Ledger
- [x] Phase 0: Evidence Gate
- [x] Phase 1: Backend Implementation (API endpoints)
- [x] Phase 2: Frontend Implementation (UI for New Chat and switching)
- [ ] Phase 3: Optional Delete
- [ ] Runtime Verification

## Next Action
Implement Phase 3: Optional Delete (if time permits) or proceed to Runtime Verification.
I will skip Phase 3 for now to ensure stability and verification.

## FULL unified diff patch
```diff
diff --git a/api.py b/api.py
index 3146c3e2..fbb4f564 100644
--- a/api.py
+++ b/api.py
@@ -3821,6 +3821,17 @@ def list_conversations():
     return jsonify({"conversations": sessions})
 
 
+@app.route("/api/conversations/<int:conversation_id>/messages", methods=["GET"])
+@require_auth
+def list_conversation_messages(conversation_id: int):
+    user_id, error = _get_user_id_or_error()
+    if error:
+        return error
+    from db.messages_repository import list_messages_for_session
+    rows = list_messages_for_session(user_id, conversation_id)
+    return jsonify({"conversation_id": conversation_id, "messages": rows})
+
+
 @app.route("/api/message", methods=["POST"])
 @require_auth
 def handle_message():
diff --git a/othello_ui.html b/othello_ui.html
index 32687448..c7480854 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -31,6 +31,13 @@
           <div class="settings-title" id="settings-title">Settings</div>
           <button id="settings-close" class="settings-close" type="button">Close</button>
         </div>
+        <div class="settings-section">
+          <div class="settings-label">Conversations</div>
+          <div id="settings-conversations-list" style="max-height: 200px; overflow-y: auto; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 1rem;">
+            <!-- Populated by JS -->
+          </div>
+          <button id="new-chat-settings-btn" class="settings-button" type="button" style="width:100%">+ New Chat</button>
+        </div>
         <div class="settings-section" id="settings-dev-reset" style="display:none;">
           <div class="danger-zone">
             <div class="danger-zone__title">Danger zone</div>
diff --git a/static/othello.js b/static/othello.js
index dcf17836..ae0ff730 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -510,6 +510,95 @@
         }
       }
 
+      async function loadConversations() {
+        if (!isAuthed) return;
+        try {
+          const resp = await fetch("/api/conversations", { credentials: "include" });
+          if (resp.ok) {
+            const data = await resp.json();
+            const conversations = data.conversations || [];
+            if (conversations.length > 0) {
+               if (!othelloState.activeConversationId) {
+                   othelloState.activeConversationId = conversations[0].conversation_id;
+               }
+            } else {
+               if (!othelloState.activeConversationId) {
+                   await createNewConversation();
+               }
+            }
+            renderConversationsList(conversations);
+          }
+        } catch (e) {
+          console.warn("Failed to load conversations", e);
+        }
+      }
+  
+      async function createNewConversation() {
+          try {
+              const resp = await fetch("/api/conversations", { method: "POST", credentials: "include" });
+              if (resp.ok) {
+                  const data = await resp.json();
+                  othelloState.activeConversationId = data.conversation_id;
+                  clearChatState();
+                  chatHydrated = false;
+                  await loadChatHistory();
+                  await loadConversations(); // Refresh list
+              }
+          } catch (e) {
+              console.error("Failed to create conversation", e);
+          }
+      }
+
+      async function switchConversation(id) {
+          if (othelloState.activeConversationId === id) return;
+          othelloState.activeConversationId = id;
+          clearChatState();
+          chatHydrated = false;
+          await loadChatHistory();
+          closeSettings();
+      }
+
+      function renderConversationsList(conversations) {
+          const container = document.getElementById("settings-conversations-list");
+          if (!container) return;
+          container.innerHTML = "";
+          
+          if (!conversations || conversations.length === 0) {
+              container.innerHTML = "<div style='padding:1rem;color:var(--text-muted);'>No conversations found.</div>";
+              return;
+          }
+
+          conversations.forEach(conv => {
+              const row = document.createElement("div");
+              row.className = "conversation-row";
+              row.style = "display:flex;justify-content:space-between;align-items:center;padding:0.8rem;border-bottom:1px solid var(--border);";
+              
+              const info = document.createElement("div");
+              const date = new Date(conv.updated_at || conv.created_at).toLocaleString();
+              const isCurrent = conv.conversation_id === othelloState.activeConversationId;
+              info.innerHTML = `
+                  <div style="font-weight:${isCurrent ? 'bold' : 'normal'}">
+                      ${isCurrent ? 'Current: ' : ''}Conversation #${conv.conversation_id}
+                  </div>
+                  <div style="font-size:0.8rem;color:var(--text-muted)">${date}</div>
+              `;
+              
+              const actions = document.createElement("div");
+              if (!isCurrent) {
+                  const switchBtn = document.createElement("button");
+                  switchBtn.textContent = "Open";
+                  switchBtn.className = "btn-secondary";
+                  switchBtn.style = "padding:0.3rem 0.8rem;font-size:0.8rem;";
+                  switchBtn.onclick = () => switchConversation(conv.conversation_id);
+                  actions.appendChild(switchBtn);
+              }
+              
+              row.appendChild(info);
+              row.appendChild(actions);
+              container.appendChild(row);
+          });
+      }
+
       function bootApp() {
         setBootState(BOOT_STATE.BOOTING_APP);
         if (BOOT_DEBUG) console.log('[BOOT] Booting app…');
@@ -532,6 +621,7 @@
             if (typeof loadTodayPlanner === 'function') {
               await loadTodayPlanner();
             }
+            await loadConversations();
             await fetchAdminCapabilities();
             setBootState(BOOT_STATE.AUTHENTICATED);
           } catch (e) {
@@ -572,6 +662,27 @@
 
       // Add settings + logout buttons to header (minimal UI)
       const brandRow = document.querySelector('.brand-row');
+      let newChatBtn = document.getElementById('new-chat-btn');
+      if (!newChatBtn) {
+        newChatBtn = document.createElement('button');
+        newChatBtn.id = 'new-chat-btn';
+        newChatBtn.className = 'icon-button';
+        newChatBtn.setAttribute('aria-label', 'New Chat');
+        newChatBtn.textContent = '+';
+        newChatBtn.style.marginRight = '0.5rem';
+        newChatBtn.title = "New Chat";
+        if (brandRow) {
+             // Insert before settings button or at end
+             const settingsBtnRef = document.getElementById('settings-btn');
+             if (settingsBtnRef) {
+                 brandRow.insertBefore(newChatBtn, settingsBtnRef);
+             } else {
+                 brandRow.appendChild(newChatBtn);
+             }
+        }
+      }
+      newChatBtn.onclick = createNewConversation;
+
       let settingsBtn = document.getElementById('settings-btn');
       if (!settingsBtn) {
         settingsBtn = document.createElement('button');
@@ -610,6 +721,13 @@
           });
         }
         if (devResetBtn) devResetBtn.onclick = handleDevReset;
+        const newChatSettingsBtn = document.getElementById("new-chat-settings-btn");
+        if (newChatSettingsBtn) {
+            newChatSettingsBtn.onclick = async () => {
+                await createNewConversation();
+                closeSettings();
+            };
+        }
         if (clearGoalsBtn) clearGoalsBtn.onclick = () => handleClearData(["goals"], "goals");
         if (clearPlansBtn) clearPlansBtn.onclick = () => handleClearData(["plans"], "plans");
         if (clearRoutinesBtn) clearRoutinesBtn.onclick = () => handleClearData(["routines"], "routines");
@@ -698,6 +816,7 @@
       currentMode: "companion", // companion | today | routine
       goals: [],
       activeGoalId: null,
+      activeConversationId: null, // New Chat support
       currentDetailGoalId: null,
       pendingGoalEdit: null,
       goalUpdateCounts: {},
@@ -3783,7 +3902,10 @@
     }
 
     async function fetchChatHistory(limit = 50, channel = "companion") {
-      const target = `${V1_MESSAGES_API}?limit=${limit}&channel=${encodeURIComponent(channel)}`;
+      let target = `${V1_MESSAGES_API}?limit=${limit}&channel=${encodeURIComponent(channel)}`;
+      if (othelloState.activeConversationId) {
+          target = `/api/conversations/${othelloState.activeConversationId}/messages`;
+      }
       const resp = await fetch(target, { credentials: "include", cache: "no-store" });
       if (resp.status === 401 || resp.status === 403) {
         const err = new Error("Unauthorized");
@@ -5314,6 +5436,7 @@
             current_mode: othelloState.currentMode,
             current_view: othelloState.currentView,
             client_message_id: clientMessageId,
+            conversation_id: othelloState.activeConversationId,
           })
         });
 
@@ -5352,6 +5475,9 @@
         }
 
         const data = await res.json();
+        if (data.conversation_id) {
+            othelloState.activeConversationId = data.conversation_id;
+        }
         const meta = data && data.meta ? data.meta : null;
         const isRoutineReady = !!(meta && meta.intent === "routine_ready" && meta.routine_suggestion_id);
         let replyText = data.reply || "[no reply]";
```
