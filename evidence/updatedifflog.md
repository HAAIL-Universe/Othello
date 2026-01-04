Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Locate goal prompt emission + routine suggestion path; create goal suggestion records when prompt emitted; wire UI accept via /v1/suggestions; guard Today Planner insertBefore; update evidence log
Completed: Added fallback goal suggestion creation + DB suggestion id; attached suggestion meta; updated goal accept to use /v1/suggestions with payload override; removed pendingGoalIntent and gated typed confirm on visible goal card; added insertBefore parent guard
Remaining: Runtime verification pending deploy; report PASS/FAIL + screenshot/console
Next Action: Deploy and run runtime checklist; report PASS/FAIL + screenshot/console.
Commit: 48f7a4f5 (branch ux/routine-clarify-panel-pending)

Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; api.py; othello_ui.html; db/suggestions_repository.py; db/goals_repository.py
Root-Cause Classification: BACKEND_NOT_EMITTING_SUGGESTION (primary); UI_DOM_CRASH_IN_LOADTODAYPLANNER (secondary)
Root-Cause Anchors:
- api.py:5867 (goal prompt emitted without guaranteed suggestion payload)
- api.py:1341 (attach goal intent suggestion bails when suggestion None)
- api.py:3512 (/api/message response builder)
- api.py:4365 (routine suggestion emission path for reference)
- othello_ui.html:3667 (planner insertBefore using non-child reference)
Anchors:
- api.py:1201 (_build_goal_intent_fallback)
- api.py:1341 (_attach_goal_intent_suggestion + suggestion_id)
- api.py:2135 (goal suggestion accept payload includes description)
- api.py:2487 (v1_accept_suggestion payload override)
- api.py:4834 (fallback goal suggestion for LLM unavailable prompt)
- api.py:5867 (prompt fallback adds suggestion)
- api.py:5932 (prompt fallback adds suggestion)
- othello_ui.html:6084 (createGoalFromSuggestion handles suggestion_id)
- othello_ui.html:6216 (goal panel stores suggestionId)
- othello_ui.html:6370 (handleGoalIntentSuggestion normalization)
- othello_ui.html:6709 (acceptVisibleGoalIntentSuggestion)
- othello_ui.html:6832 (typed confirm goal precedence)
- othello_ui.html:3667 (renderDayReview insertBefore guard)
- othello_ui.html:4367 (renderCurrentFocus insertBefore guard)
Verification:
- Static: python -m py_compile api.py core/conversation_parser.py (PASS)
- Runtime: PENDING (deploy-required)
  1) Trigger goal prompt "Want this saved as a goal..." -> response includes meta.suggestions with goal_intent + suggestion_id -> confirm card appears.
  2) Click Save/Create (with edits) -> goal saved via /v1/suggestions/<id>/accept override; card clears; no stuck "Thinking...".
  3) Type "confirm" with visible goal card -> goal saved; ack appears; no stuck "Thinking...".
  4) Routine confirm still works; goal confirm takes precedence when goal card visible.
  5) Today Planner loads without insertBefore console error.

diff --git a/api.py b/api.py
index 32f7b08a..4269bc7e 100644
--- a/api.py
+++ b/api.py
@@ -1198,6 +1198,28 @@ def _get_goal_intent_suggestion(
     return suggestion
 
 
+def _build_goal_intent_fallback(
+    user_input: str,
+    client_message_id: Optional[str],
+    user_id: Optional[str],
+) -> Optional[Dict[str, Any]]:
+    if not user_input or not client_message_id:
+        return None
+    raw = str(user_input).strip()
+    if not raw:
+        return None
+    if _is_suggestion_dismissed(user_id, "goal_intent", client_message_id):
+        return None
+    title_suggestion = _extract_goal_title_suggestion(raw)
+    return {
+        "type": "goal_intent",
+        "source_client_message_id": client_message_id,
+        "confidence": 0.45,
+        "title_suggestion": title_suggestion,
+        "body_suggestion": raw,
+    }
+
+
 def _normalize_reply_text(text: str) -> str:
     raw = (text or "").strip().lower()
     normalized = re.sub(r"\s+", " ", raw)
@@ -1331,6 +1353,41 @@ def _attach_goal_intent_suggestion(
         suggestion = _get_goal_intent_suggestion(user_input, client_message_id, user_id)
     if not suggestion:
         return False
+    suggestion_id = suggestion.get("suggestion_id") or suggestion.get("id")
+    if suggestion_id is None and user_id:
+        title = suggestion.get("title_suggestion") or _extract_goal_title_suggestion(user_input)
+        body = suggestion.get("body_suggestion") or (user_input or "").strip()
+        payload = {
+            "title": title,
+            "body": body,
+            "description": body,
+            "confidence": suggestion.get("confidence"),
+        }
+        provenance = {
+            "source": "api_message_goal_intent",
+            "request_id": request_id,
+            "client_message_id": client_message_id,
+        }
+        try:
+            created = suggestions_repository.create_suggestion(
+                user_id=user_id,
+                kind="goal",
+                payload=payload,
+                provenance=provenance,
+            )
+            if isinstance(created, dict):
+                suggestion_id = created.get("id")
+        except Exception:
+            logger.warning(
+                "API: goal suggestion create failed request_id=%s client_message_id=%s",
+                request_id,
+                client_message_id,
+                exc_info=True,
+            )
+    if suggestion_id is not None:
+        suggestion = dict(suggestion)
+        suggestion["suggestion_id"] = suggestion_id
+        suggestion.setdefault("kind", "goal")
     meta = response.setdefault("meta", {})
     suggestions = meta.setdefault("suggestions", [])
     suggestions.append(suggestion)
@@ -2077,7 +2134,8 @@ def _apply_suggestion_decisions(
 
         if kind == "goal":
             title = payload.get("title") or payload.get("body") or "Untitled Goal"
-            goal = create_goal({"title": title}, user_id)
+            description = payload.get("description") or payload.get("body") or ""
+            goal = create_goal({"title": title, "description": description}, user_id)
             if not goal:
                 results.append({"ok": False, "error": "goal_create_failed", "suggestion_id": suggestion_id})
                 continue
@@ -2433,10 +2491,26 @@ def v1_accept_suggestion(suggestion_id: int):
     if error:
         return error
     reason = None
+    payload_override = None
     if request.is_json:
         payload = request.get_json(silent=True)
         if isinstance(payload, dict):
             reason = payload.get("reason")
+            payload_override = payload.get("payload")
+    if payload_override and isinstance(payload_override, dict):
+        try:
+            existing = suggestions_repository.get_suggestion(user_id, suggestion_id)
+            if isinstance(existing, dict):
+                merged = dict(existing.get("payload") or {})
+                merged.update(payload_override)
+                suggestions_repository.update_suggestion_payload(user_id, suggestion_id, merged)
+        except Exception:
+            logger.warning(
+                "API: suggestion payload update failed request_id=%s suggestion_id=%s",
+                request_id,
+                suggestion_id,
+                exc_info=True,
+            )
     results = _apply_suggestion_decisions(
         user_id,
         [{"suggestion_id": suggestion_id, "action": "accept", "reason": reason}],
@@ -4756,6 +4830,12 @@ def handle_message():
                 client_message_id,
                 user_id,
             )
+            if not suggestion and effective_channel == "companion":
+                suggestion = _build_goal_intent_fallback(
+                    user_input,
+                    client_message_id,
+                    user_id,
+                )
             goal_intent_detected = _attach_goal_intent_suggestion(
                 response,
                 user_input=user_input,
                 client_message_id=client_message_id,
@@ -5785,6 +5865,13 @@ def handle_message():
             ):
                 if effective_channel == "companion":
                     agentic_reply = _goal_intent_prompt(active_goal.get("id"))
+                    if not goal_intent_suggestion:
+                        goal_intent_suggestion = _build_goal_intent_fallback(
+                            user_input,
+                            client_message_id,
+                            user_id,
+                        )
+                        goal_intent_detected = bool(goal_intent_suggestion)
                 else:
                     agentic_reply = "Please share a bit more detail so I can help you plan."
                 reply_source = "fallback"
@@ -5843,6 +5930,13 @@ def handle_message():
             ):
                 if effective_channel == "companion":
                     agentic_reply = _goal_intent_prompt(None)
+                    if not goal_intent_suggestion:
+                        goal_intent_suggestion = _build_goal_intent_fallback(
+                            user_input,
+                            client_message_id,
+                            user_id,
+                        )
+                        goal_intent_detected = bool(goal_intent_suggestion)
                 else:
                     agentic_reply = "Please share a bit more detail so I can help you plan."
                 reply_source = "fallback"
diff --git a/othello_ui.html b/othello_ui.html
index 93137824..11b0a710 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2788,7 +2788,6 @@
       messagesByClientId: {},
       dismissedSuggestionIds: new Set(),
       goalIntentSuggestions: {},
-      pendingGoalIntent: null,
       mobileEditorPinned: false,
       mobileBackJustPressedAt: 0,
       creatingRoutine: false,
@@ -3666,7 +3665,7 @@
 
       // Insert after brief
       const brief = document.getElementById("planner-brief");
-      if (brief && brief.nextSibling) {
+      if (brief && brief.parentNode === container && brief.nextSibling) {
          container.insertBefore(strip, brief.nextSibling);
       } else {
          container.prepend(strip);
@@ -4366,7 +4365,7 @@
 
       // Insert after brief
       const brief = document.getElementById("planner-brief");
-      if (brief && brief.nextSibling) {
+      if (brief && brief.parentNode === container && brief.nextSibling) {
         container.insertBefore(card, brief.nextSibling);
       } else {
         container.prepend(card);
@@ -6062,13 +6061,7 @@
       return trimmed.length > 60 ? trimmed.slice(0, 60).trim() : trimmed;
     }
 
-    function clearPendingGoalIntent(clientMessageId) {
-      const pending = othelloState.pendingGoalIntent;
-      if (pending && (!clientMessageId || pending.clientMessageId === clientMessageId)) othelloState.pendingGoalIntent = null;
-    }
-
     function clearGoalIntentUI(clientMessageId) {
-      clearPendingGoalIntent(clientMessageId);
       const entry = othelloState.messagesByClientId[clientMessageId];
       if (!entry) return;
       if (entry.bubbleEl) {
@@ -6089,7 +6082,7 @@
     }
 
     async function createGoalFromSuggestion(opts) {
-      const { title, description, clientMessageId, statusEl, panelEl, onSuccess } = opts;
+      const { title, description, clientMessageId, statusEl, panelEl, onSuccess, suggestionId } = opts;
       const trimmedTitle = (title || "").trim();
       const trimmedDesc = (description || "").trim();
       if (trimmedTitle.length < 3) {
@@ -6099,30 +6092,58 @@
       disablePanelButtons(panelEl, true);
       if (statusEl) statusEl.textContent = "Saving goal...";
       try {
-        const res = await fetch(GOALS_API, {
-          method: "POST",
-          headers: {"Content-Type": "application/json"},
-          credentials: "include",
-          body: JSON.stringify({
-            title: trimmedTitle,
-            description: trimmedDesc,
-            source_client_message_id: clientMessageId
-          })
-        });
-        if (!res.ok) {
-          const contentType = res.headers.get("content-type") || "";
-          let errMsg = "Unable to create goal.";
-          if (contentType.includes("application/json")) {
-            const data = await res.json();
-            errMsg = (data && (data.message || data.error)) || errMsg;
+        let goal = null;
+        let goalId = null;
+        if (suggestionId) {
+          const payload = await v1Request(
+            `/v1/suggestions/${suggestionId}/accept`,
+            {
+              method: "POST",
+              headers: {"Content-Type": "application/json"},
+              credentials: "include",
+              body: JSON.stringify({
+                reason: "confirm",
+                payload: {
+                  title: trimmedTitle,
+                  body: trimmedDesc,
+                  description: trimmedDesc
+                }
+              })
+            },
+            "Confirm goal suggestion"
+          );
+          const results = payload && payload.data && Array.isArray(payload.data.results)
+            ? payload.data.results
+            : [];
+          const result = results[0] || null;
+          goal = result && result.goal ? result.goal : null;
+          goalId = goal && typeof goal.id === "number" ? goal.id : null;
+        } else {
+          const res = await fetch(GOALS_API, {
+            method: "POST",
+            headers: {"Content-Type": "application/json"},
+            credentials: "include",
+            body: JSON.stringify({
+              title: trimmedTitle,
+              description: trimmedDesc,
+              source_client_message_id: clientMessageId
+            })
+          });
+          if (!res.ok) {
+            const contentType = res.headers.get("content-type") || "";
+            let errMsg = "Unable to create goal.";
+            if (contentType.includes("application/json")) {
+              const data = await res.json();
+              errMsg = (data && (data.message || data.error)) || errMsg;
+            }
+            if (statusEl) statusEl.textContent = errMsg;
+            disablePanelButtons(panelEl, false);
+            return false;
           }
-          if (statusEl) statusEl.textContent = errMsg;
-          disablePanelButtons(panelEl, false);
-          return false;
+          const data = await res.json();
+          goal = data && data.goal ? data.goal : null;
+          goalId = goal && typeof goal.id === "number" ? goal.id : data.goal_id;
         }
-        const data = await res.json();
-        const goal = data && data.goal ? data.goal : null;
-        const goalId = goal && typeof goal.id === "number" ? goal.id : data.goal_id;
         clearGoalIntentUI(clientMessageId);
         showToast("Saved as goal");
         await refreshGoals();
@@ -6138,7 +6159,7 @@
         return true;
       } catch (err) {
         console.error("[Othello UI] create goal failed:", err);
-        if (statusEl) statusEl.textContent = "Network error.";
+        if (statusEl) statusEl.textContent = err && err.message ? err.message : "Network error.";
         disablePanelButtons(panelEl, false);
         return false;
       }
@@ -6194,10 +6215,14 @@
 
     function buildGoalIntentPanel(suggestion, entry) {
       const clientMessageId = suggestion.source_client_message_id;
+      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
       const panel = document.createElement("div");
       panel.className = "ux-goal-intent-panel";
       panel.dataset.clientMessageId = clientMessageId;
       panel.dataset.suggestionType = suggestion.type;
+      if (suggestionId != null) {
+        panel.dataset.suggestionId = String(suggestionId);
+      }
@@ -6317,7 +6342,8 @@
           description: bodyInput.value,
           clientMessageId,
           statusEl: status,
-          panelEl: panel
+          panelEl: panel,
+          suggestionId
         });
       });
 
@@ -6342,17 +6368,21 @@
     }
 
     function handleGoalIntentSuggestion(suggestion) {
-      if (!suggestion || suggestion.type !== "goal_intent") return;
-      const clientMessageId = suggestion.source_client_message_id;
+      if (!suggestion) return;
+      const suggestionType = suggestion.type || suggestion.kind;
+      if (suggestionType !== "goal_intent" && suggestionType !== "goal") return;
+      const normalizedSuggestion = suggestionType === "goal"
+        ? { ...suggestion, type: "goal_intent" }
+        : suggestion;
+      const clientMessageId = normalizedSuggestion.source_client_message_id;
       if (!clientMessageId) return;
-      if (isSuggestionDismissed(suggestion.type, clientMessageId)) return;
-      othelloState.goalIntentSuggestions[clientMessageId] = suggestion;
+      if (isSuggestionDismissed(normalizedSuggestion.type, clientMessageId)) return;
+      othelloState.goalIntentSuggestions[clientMessageId] = normalizedSuggestion;
       const entry = othelloState.messagesByClientId[clientMessageId] || null;
-      othelloState.pendingGoalIntent = { clientMessageId, createdAt: Date.now(), acceptFn: () => createGoalFromSuggestion({ title: pickSuggestionTitle(suggestion, entry ? entry.text : ""), description: pickSuggestionBody(suggestion, entry ? entry.text : ""), clientMessageId, statusEl: null, panelEl: null }) };
       if (!entry || !entry.bubbleEl || !entry.rowEl) return;
       if (entry.panelEl) return;
       entry.bubbleEl.classList.add("ux-goal-intent");
-      const panel = buildGoalIntentPanel(suggestion, entry);
+      const panel = buildGoalIntentPanel(normalizedSuggestion, entry);
       entry.panelEl = panel;
       entry.rowEl.appendChild(panel);
     }
@@ -6669,6 +6699,40 @@
       return latest;
     }
 
+    function findVisibleGoalIntentEntry() {
+      const latest = getLatestGoalIntentEntry();
+      if (!latest || !latest.entry || !latest.entry.panelEl) return null;
+      if (!isElementVisible(latest.entry.panelEl)) return null;
+      return latest;
+    }
+
+    async function acceptVisibleGoalIntentSuggestion() {
+      const latest = findVisibleGoalIntentEntry();
+      if (!latest || !latest.entry) return { handled: false, accepted: false };
+      const { clientMessageId, entry } = latest;
+      const suggestion = othelloState.goalIntentSuggestions[clientMessageId];
+      if (!suggestion) return { handled: false, accepted: false };
+      const panelEl = entry.panelEl;
+      const statusEl = panelEl ? panelEl.querySelector(".ux-goal-intent-status") : null;
+      const title = pickSuggestionTitle(suggestion, entry.text);
+      const description = pickSuggestionBody(suggestion, entry.text);
+      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
+      try {
+        const accepted = await createGoalFromSuggestion({
+          title,
+          description,
+          clientMessageId,
+          statusEl,
+          panelEl,
+          suggestionId
+        });
+        return { handled: true, accepted: !!accepted };
+      } catch (err) {
+        console.warn("[Othello UI] goal typed confirm failed:", err);
+        return { handled: true, accepted: false };
+      }
+    }
+
     function parseGoalIntentDecision(text) {
       const normalized = String(text || "")
         .toLowerCase()
@@ -6693,6 +6757,7 @@
       const statusEl = panelEl ? panelEl.querySelector(".ux-goal-intent-status") : null;
       const title = pickSuggestionTitle(suggestion, entry.text);
       const description = pickSuggestionBody(suggestion, entry.text);
+      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
 
       if (decision === "save") {
         await createGoalFromSuggestion({
@@ -6700,7 +6765,8 @@
           description,
           clientMessageId,
           statusEl,
-          panelEl
+          panelEl,
+          suggestionId
         });
         return true;
       }
@@ -6764,13 +6830,9 @@
       let sendUiState = beginSendUI({ label: isConfirmSave ? "Saving..." : "Thinking…", disableSend: true });
       try {
         if (isConfirmSave) {
-          const pendingGoal = othelloState.pendingGoalIntent;
-          if (pendingGoal && typeof pendingGoal.acceptFn === "function") {
-            try {
-              if (await pendingGoal.acceptFn()) addMessage("bot", "Confirmed.");
-            } catch (err) {
-              console.warn("[Othello UI] goal typed confirm failed:", err);
-            }
+          const goalDecision = await acceptVisibleGoalIntentSuggestion();
+          if (goalDecision.handled) {
+            if (goalDecision.accepted) addMessage("bot", "Confirmed.");
             return;
           }
 
