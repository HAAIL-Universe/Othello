# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location (Identified backend/frontend points)
- [x] Phase 1: Server: Pending Draft Storage (Implemented draft_context, confirm_goal intent)
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring (Implemented activeDraft, focus ribbon, payload)
- [x] Phase 3: Quality Gates (Verified logic)
- [x] Phase 4: Correctness & UX Patch (Fix source_message_id, tighten confirm, add dismiss, type-aware ribbon)

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index c4a76937..abcdef12 100644
--- a/api.py
+++ b/api.py
@@ -1622,13 +1622,23 @@ def _attach_goal_intent_suggestion(
         suggestion["suggestion_id"] = suggestion_id
         suggestion.setdefault("kind", "goal")
 
         # Draft Focus: Return draft context and payload
+        # Payload normalization
+        raw_payload = suggestion.get("payload", {})
+        if isinstance(raw_payload, str):
+            try:
+                import json
+                raw_payload = json.loads(raw_payload)
+            except Exception:
+                raw_payload = {}
+        if not isinstance(raw_payload, dict):
+            raw_payload = {}
+
         response["draft_context"] = {
             "draft_id": suggestion_id,
             "draft_type": "goal",
-            "source_message_id": client_message_id
+            "source_message_id": suggestion_id  # Use stable ID for UI highlight
         }
         response["draft_payload"] = {
-            "title": suggestion.get("title_suggestion") or suggestion.get("payload", {}).get("title"),
-            "target_days": suggestion.get("payload", {}).get("target_days"),
-            "steps": suggestion.get("payload", {}).get("steps"),
-            "body": suggestion.get("body_suggestion") or suggestion.get("payload", {}).get("body")
+            "title": suggestion.get("title_suggestion") or raw_payload.get("title"),
+            "target_days": raw_payload.get("target_days"),
+            "steps": raw_payload.get("steps"),
+            "body": suggestion.get("body_suggestion") or raw_payload.get("body")
         }
 
     meta = response.setdefault("meta", {})
@@ -3987,23 +3997,30 @@ def handle_message():
             user_id = None
 
         # Draft Focus: Confirm Goal Intent
-        if user_id and (user_input.strip().lower() in ("confirm goal", "confirm", "yes, confirm") or data.get("ui_action") == "confirm_draft"):
+        # Tightened routing:
+        # A) data.ui_action == "confirm_draft"
+        # B) user_input == "confirm goal" (exact)
+        # C) user_input == "confirm" ONLY if draft_id is present
+        is_confirm_action = data.get("ui_action") == "confirm_draft"
+        is_confirm_goal_text = user_input.strip().lower() == "confirm goal"
+        is_confirm_text_with_id = user_input.strip().lower() == "confirm" and data.get("draft_id")
+
+        if user_id and (is_confirm_action or is_confirm_goal_text or is_confirm_text_with_id):
             draft_id = data.get("draft_id")
             
             if draft_id:
                 # Verify it exists and is pending
                 try:
                     draft_id = int(draft_id)
                     draft = suggestions_repository.get_suggestion(user_id, draft_id)
                     if not draft or draft.get("status") != "pending":
                         draft = None # Invalid draft_id provided
                 except (ValueError, TypeError):
                     draft = None
-            else:
-                # Find latest pending goal draft
+            elif is_confirm_goal_text:
+                # Find latest pending goal draft ONLY if explicit "confirm goal"
                 pending_drafts = suggestions_repository.list_suggestions(
                     user_id=user_id,
                     status="pending",
                     kind="goal",
                     limit=1
                 )
+                # list_suggestions orders by created_at DESC
                 draft = pending_drafts[0] if pending_drafts else None
+            else:
+                draft = None
             
             if draft:
                 draft_id = draft["id"]
@@ -4037,6 +4054,24 @@ def handle_message():
                 "request_id": request_id
             })
 
+        # Draft Focus: Dismiss Draft
+        if user_id and data.get("ui_action") == "dismiss_draft":
+            draft_id = data.get("draft_id")
+            if draft_id:
+                try:
+                    draft_id = int(draft_id)
+                    suggestions_repository.update_suggestion_status(
+                        user_id, 
+                        draft_id, 
+                        "dismissed", 
+                        decided_reason="user_dismissed_via_ui"
+                    )
+                    return jsonify({
+                        "reply": "Draft dismissed.",
+                        "dismissed_draft_id": draft_id,
+                        "request_id": request_id
+                    })
+                except (ValueError, TypeError):
+                    pass
+            return jsonify({
+                "reply": "Could not dismiss draft.",
+                "request_id": request_id
+            })
+
         # --- Phase 3.2: Chat Command Router ---
         if user_id:
             cmd_text = user_input.strip().lower()
diff --git a/static/othello.js b/static/othello.js
index 605f7b54..abcdef12 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -3722,12 +3722,37 @@
 
       // Draft Focus (Priority over Active Goal)
       if (othelloState.activeDraft) {
-          focusRibbonTitle.textContent = "Drafting Goal..."; 
+          const draftType = othelloState.activeDraft.draft_type || "Goal";
+          const displayType = draftType.charAt(0).toUpperCase() + draftType.slice(1);
+          focusRibbonTitle.textContent = `Drafting ${displayType}...`; 
+          
+          // Add actions if not present
+          if (!focusRibbon.querySelector(".ribbon-actions")) {
+              const actionsDiv = document.createElement("div");
+              actionsDiv.className = "ribbon-actions";
+              actionsDiv.style.marginLeft = "auto";
+              actionsDiv.style.display = "flex";
+              actionsDiv.style.gap = "8px";
+
+              const confirmBtn = document.createElement("button");
+              confirmBtn.textContent = "Confirm";
+              confirmBtn.className = "ribbon-btn confirm-btn";
+              confirmBtn.onclick = (e) => {
+                  e.stopPropagation();
+                  sendMessage("", { ui_action: "confirm_draft" });
+              };
+
+              const dismissBtn = document.createElement("button");
+              dismissBtn.textContent = "Dismiss";
+              dismissBtn.className = "ribbon-btn dismiss-btn";
+              dismissBtn.onclick = (e) => {
+                  e.stopPropagation();
+                  sendMessage("", { ui_action: "dismiss_draft" });
+              };
+
+              actionsDiv.appendChild(confirmBtn);
+              actionsDiv.appendChild(dismissBtn);
+              focusRibbon.appendChild(actionsDiv);
+          }
+
           focusRibbon.classList.add("visible");
           focusRibbon.classList.add("draft-mode");
           return;
       } else {
           focusRibbon.classList.remove("draft-mode");
+          const actions = focusRibbon.querySelector(".ribbon-actions");
+          if (actions) actions.remove();
       }
 
       if (othelloState.activeGoalId !== null) {
@@ -5361,9 +5386,9 @@
-    async function sendMessage() {
-      const text = input.value.trim();
-      if (!text) return;
+    async function sendMessage(overrideText = null, extraData = {}) {
+      const text = overrideText !== null ? overrideText : input.value.trim();
+      if (!text && !extraData.ui_action) return;
 
       // Voice-first save command (Strict Command Mode)
@@ -5402,9 +5427,11 @@
 
       const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim(), isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
-      addMessage("user", text, { metaNote, clientMessageId });
-      input.value = "";
-      input.focus();
+      addMessage("user", text || (extraData.ui_action ? `[Action: ${extraData.ui_action}]` : ""), { metaNote, clientMessageId });
+      if (overrideText === null) {
+          input.value = "";
+          input.focus();
+      }
       let sendUiState = beginSendUI({ label: isConfirmSave ? "Saving..." : "Thinking…", disableSend: true });
       try {
@@ -5480,7 +5507,7 @@
         const mode = (othelloState.currentMode || "companion").toLowerCase();
         const channel = mode === "companion" ? "companion" : "planner";
         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
         console.log("[Othello UI] Sending plain-message payload:", text);
-        const res = await fetch(API, {
-          method: "POST",
-          headers: {"Content-Type": "application/json"},
-          credentials: "include",
-          body: JSON.stringify({ 
-            message: text,
-            channel,
-            goal_id: othelloState.activeGoalId || null,
-            active_goal_id: othelloState.activeGoalId || null,
-            current_mode: othelloState.currentMode,
-            current_view: othelloState.currentView,
-            client_message_id: clientMessageId,
-            conversation_id: othelloState.activeConversationId,
-            draft_id: othelloState.activeDraft ? othelloState.activeDraft.draft_id : null,
-            draft_type: othelloState.activeDraft ? othelloState.activeDraft.draft_type : null
-          })
-        });
+        const payload = { 
+            message: text,
+            channel,
+            goal_id: othelloState.activeGoalId || null,
+            active_goal_id: othelloState.activeGoalId || null,
+            current_mode: othelloState.currentMode,
+            current_view: othelloState.currentView,
+            client_message_id: clientMessageId,
+            conversation_id: othelloState.activeConversationId,
+            draft_id: othelloState.activeDraft ? othelloState.activeDraft.draft_id : null,
+            draft_type: othelloState.activeDraft ? othelloState.activeDraft.draft_type : null,
+            ...extraData
+        };
+        const res = await fetch(API, {
+          method: "POST",
+          headers: {"Content-Type": "application/json"},
+          credentials: "include",
+          body: JSON.stringify(payload)
+        });
 
         console.log("[Othello UI] /api/message status", res.status);
@@ -5664,6 +5691,14 @@
             updateFocusRibbon();
         }
 
+        if (data.dismissed_draft_id) {
+            if (othelloState.activeDraft && othelloState.activeDraft.draft_id === data.dismissed_draft_id) {
+                othelloState.activeDraft = null;
+                localStorage.removeItem("othello_active_draft");
+                updateFocusRibbon();
+            }
+        }
+
         // Always refresh from backend to stay in sync
         await refreshGoals();
```

## Appendix: Suggestions Repository Implementations

```python
def get_suggestion(user_id: str, suggestion_id: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
        FROM suggestions
        WHERE id = %s AND user_id = %s
    """
    return fetch_one(query, (suggestion_id, user_id))


def list_suggestions(
    *,
    user_id: str,
    status: str = "pending",
    kind: Optional[str] = None,
    limit: int = 50,
) -> list[Dict[str, Any]]:
    params = [user_id, status]
    clauses = ["user_id = %s", "status = %s"]
    if kind:
        clauses.append("kind = %s")
        params.append(kind)
    params.append(limit)
    query = f"""
        SELECT id, kind, status, payload, provenance, created_at, decided_at
        FROM suggestions
        WHERE {" AND ".join(clauses)}
        ORDER BY created_at DESC
        LIMIT %s
    """
    return fetch_all(query, tuple(params))
```

## Appendix: addMessage Implementation

```javascript
    function addMessage(role, text, options = {}) {
      // Hide chat placeholder when first message appears
      const chatPlaceholder = document.getElementById("chat-placeholder");
      if (chatPlaceholder && !chatPlaceholder.classList.contains("hidden")) {
        chatPlaceholder.classList.add("hidden");
      }

      const row = document.createElement("div");
      row.className = `msg-row ${role}`;

      // Apply focus highlighting if a goal is focused
      if (othelloState.activeGoalId) {
        row.classList.add("msg--focus-attached");
      }

      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.innerHTML = formatMessageText(text);
      const clientMessageId = options && typeof options.clientMessageId === "string"
        ? options.clientMessageId.trim()
        : "";
      if (clientMessageId) {
        row.dataset.clientMessageId = clientMessageId;
        bubble.dataset.clientMessageId = clientMessageId;
      }

      const meta = document.createElement("div");
      meta.className = "meta";
      const metaNote = options && typeof options.metaNote === "string" ? options.metaNote.trim() : "";
      const metaSuffix = metaNote ? ` | ${metaNote}` : "";
      meta.textContent = role === "user"
        ? "You · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) + metaSuffix
        : "Othello · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

      if (role === "bot" && options && Array.isArray(options.intentMarkers)) {
        renderIntentMarkers(meta, options.intentMarkers);
      }

      bubble.appendChild(meta);

      if (role === "bot" && othelloState.currentMode === "companion") {
        const sourceClientMessageId = options && typeof options.sourceClientMessageId === "string"
          ? options.sourceClientMessageId.trim()
          : "";
        const listItems = extractListItems(text);
        if (hasStructuredList(text) && listItems.length) {
          const convKey = othelloState.activeConversationId ? String(othelloState.activeConversationId) : "default";
          othelloState.lastGoalDraftByConversationId[convKey] = { items: listItems, rawText: text, sourceClientMessageId };
          const bar = createCommitmentBar(listItems, text, sourceClientMessageId);
          bubble.appendChild(bar);
        }
      }

      if (role === "bot" && othelloState.activeGoalId !== null && isPlanLikeText(text)) {
        const planBar = createPlanActionBar(text);
        bubble.appendChild(planBar);
      }

      row.appendChild(bubble);
      chatLog.appendChild(row);

      if (role === "user" && clientMessageId) {
        othelloState.messagesByClientId[clientMessageId] = {
          clientMessageId,
          bubbleEl: bubble,
          rowEl: row,
          text,
          ts: Date.now(),
          panelEl: null,
        };
        refreshSecondarySuggestionUI(othelloState.messagesByClientId[clientMessageId]);
      }

      // Scroll to latest message
      requestAnimationFrame(() => {
        const chatView = document.getElementById("chat-view");
        if (chatView) {
          chatView.scrollTo({
            top: chatView.scrollHeight,
            behavior: "smooth"
          });
        }
      });
      return { row, bubble };
    }
```






