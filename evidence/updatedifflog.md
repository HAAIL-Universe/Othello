Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Add routine patch endpoint + draft guard; update routine confirm UI; prevent goal modal during routine draft; update evidence log; run static verification
Completed: Added routine draft patch payload builder + v1 patch endpoint; updated routine cards to Confirm/Edit/Dismiss; added routine draft hard guard in send pipeline; guarded goal intent render during routine draft; updated routine day display; ran py_compile
Remaining: Runtime verification pending deploy; update evidence log with runtime PASS/FAIL
Next Action: Deploy and run runtime checklist for routine draft mode; report PASS/FAIL.

Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; api.py; othello_ui.html; db/suggestions_repository.py
Anchors:
- Routine patch payload builder: api.py:1687
- Routine summary day display: api.py:1736
- Routine patch endpoint: api.py:2764
- Goal intent modal guard: othello_ui.html:6390
- Routine clarify panel (chips + dismiss): othello_ui.html:6621
- Routine ready panel (Confirm/Edit/Dismiss): othello_ui.html:6726
- Routine patch request handler: othello_ui.html:6510
- Routine draft hard guard: othello_ui.html:6969
Verification:
- Static: python -m py_compile api.py core/conversation_parser.py (PASS)
- Runtime: PENDING (deploy-required)
  A) Trigger routine draft -> Confirm/Edit/Dismiss visible
  B) Tap 7pm chip -> same card updated; no daily inference
  C) Unrelated message while pending -> guard message, no goal modal
  D) Edit: daily, 2-minute reminder -> patch same draft
  E) Confirm -> single routine saved
  F) Add routine: gym at 3 -> no goal modal
diff --git a/api.py b/api.py
index b1eaae0e..0c90cd8c 100644
--- a/api.py
+++ b/api.py
@@ -1684,6 +1684,37 @@ def _parse_routine_time_answer(text: str, draft: Dict[str, Any]) -> Optional[str
     return None
 
 
+def _build_routine_patch_payload(text: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
+    if not text or not isinstance(payload, dict):
+        return None
+    lower = text.lower()
+    draft = dict(payload.get("draft") or {})
+    if not isinstance(draft, dict):
+        return None
+    missing_fields = list(payload.get("missing_fields") or [])
+    ambiguous_fields = list(payload.get("ambiguous_fields") or [])
+    updates: Dict[str, Any] = {}
+    time_local = _parse_routine_time_answer(text, draft)
+    if time_local:
+        updates["time_local"] = time_local
+        missing_fields = [f for f in missing_fields if f != "time_ampm"]
+        ambiguous_fields = [f for f in ambiguous_fields if f != "time_local"]
+    days = _extract_days_of_week(text)
+    if not days and re.search(r"\bmon(day)?s?\s*-\s*fri(day)?s?\b", lower):
+        days = ["mon", "tue", "wed", "thu", "fri"]
+    if days:
+        updates["days_of_week"] = days
+
+    duration_minutes = _parse_duration_minutes(text)
+    if duration_minutes is not None:
+        updates["duration_minutes"] = duration_minutes
+
+    if not updates:
+        return None
+    draft.update(updates)
+    return _build_routine_suggestion_payload(draft, missing_fields, ambiguous_fields)
+
+
 def _format_routine_summary(draft: Dict[str, Any]) -> str:
     title = draft.get("title") or "Routine"
     days = draft.get("days_of_week") or []
@@ -1696,7 +1727,7 @@ def _format_routine_summary(draft: Dict[str, Any]) -> str:
         "sat": "Sat",
         "sun": "Sun",
     }
-    day_text = ", ".join(day_labels.get(day, day) for day in days) if days else "every day"
+    day_text = ", ".join(day_labels.get(day, day) for day in days) if days else "days TBD"
     time_text = draft.get("time_local") or draft.get("time_text") or "unspecified time"
     return f"Routine draft ready: {title} on {day_text} at {time_text}. Confirm to save."
 
@@ -2712,6 +2743,39 @@ def v1_accept_suggestion(suggestion_id: int):
     return _v1_envelope(data={"results": results}, status=200)
 
 
+@v1.route("/suggestions/<int:suggestion_id>/patch", methods=["POST"])
+@require_auth
+def v1_patch_suggestion(suggestion_id: int):
+    user_id, error = _get_user_id_or_error()
+    if error:
+        return error
+    if not request.is_json:
+        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
+    data = request.get_json(silent=True)
+    if not isinstance(data, dict):
+        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)
+    text = data.get("text")
+    if not isinstance(text, str) or not text.strip():
+        return _v1_error("VALIDATION_ERROR", "text is required", 400)
+    suggestion = suggestions_repository.get_suggestion(user_id, suggestion_id)
+    if not suggestion:
+        return _v1_error("NOT_FOUND", "Suggestion not found", 404, details={"suggestion_id": suggestion_id})
+    if suggestion.get("kind") != "routine":
+        return _v1_error("INVALID_KIND", "Only routine suggestions can be patched", 400)
+    status = (suggestion.get("status") or "").strip().lower()
+    if status != "pending":
+        return _v1_error("INVALID_STATUS", "Suggestion is not pending", 400)
+    payload = suggestion.get("payload") or {}
+    patched_payload = _build_routine_patch_payload(text, payload)
+    if not patched_payload:
+        return _v1_error("NO_PATCH_FIELDS", "No routine fields detected in edit text", 400)
+    updated = suggestions_repository.update_suggestion_payload(user_id, suggestion_id, patched_payload)
+    return _v1_envelope(
+        data={"suggestion_id": suggestion_id, "suggestion": updated or suggestion},
+        status=200,
+    )
+
+
 @v1.route("/capabilities", methods=["GET"])
 def v1_capabilities():
     return jsonify(get_capabilities_payload())
diff --git a/othello_ui.html b/othello_ui.html
index 0590cb20..5089ede8 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6388,12 +6388,15 @@
     }
 
     function applySuggestionMeta(meta) {
+      if (othelloState.pendingRoutineSuggestionId || othelloState.currentView === "routine-planner") {
+        return;
+      }
       const suggestions = meta && Array.isArray(meta.suggestions) ? meta.suggestions : [];
       suggestions.forEach(handleGoalIntentSuggestion);
     }
 
     function formatRoutineDays(days) {
-      if (!Array.isArray(days) || days.length === 0) return "Every day";
+      if (!Array.isArray(days) || days.length === 0) return "Days TBD";
       const labels = {
         mon: "Mon",
         tue: "Tue",
@@ -6440,9 +6443,6 @@
         document.querySelectorAll('.ux-goal-intent-panel[data-suggestion-type="routine"]')
       );
       const visible = panels.filter(isElementVisible).pop() || null;
-      if (!visible && othelloState.pendingRoutineSuggestionId) {
-        clearPendingRoutineSuggestion();
-      }
       return visible;
     }
 
@@ -6488,6 +6488,68 @@
       }
     }
 
+    async function patchRoutineSuggestion(suggestionId, text, panel) {
+      if (!suggestionId) return null;
+      const statusEl = panel ? panel.querySelector(".ux-goal-intent-status") : null;
+      if (statusEl) statusEl.textContent = "Updating...";
+      const payload = await v1Request(
+        `/v1/suggestions/${suggestionId}/patch`,
+        {
+          method: "POST",
+          headers: { "Content-Type": "application/json" },
+          credentials: "include",
+          body: JSON.stringify({ text })
+        },
+        "Update routine suggestion"
+      );
+      const suggestion = payload && payload.data ? payload.data.suggestion : null;
+      const row = panel && panel.parentNode ? panel.parentNode : null;
+      if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
+      if (row && suggestion) {
+        const entry = { row };
+        if (suggestion.payload && suggestion.payload.status === "incomplete") {
+          await buildRoutineClarifyPanel(entry, suggestionId);
+        } else {
+          buildRoutineReadyPanel(entry, suggestion, suggestionId);
+        }
+      }
+      return suggestion;
+    }
+
+    async function rejectRoutineSuggestion(suggestionId, panel) {
+      if (!suggestionId) return false;
+      const statusEl = panel ? panel.querySelector(".ux-goal-intent-status") : null;
+      if (statusEl) statusEl.textContent = "Dismissing...";
+      try {
+        await v1Request(
+          "/v1/confirm",
+          {
+            method: "POST",
+            headers: { "Content-Type": "application/json" },
+            credentials: "include",
+            body: JSON.stringify({
+              decisions: [{ suggestion_id: suggestionId, action: "reject", reason: "dismiss" }]
+            })
+          },
+          "Dismiss routine suggestion"
+        );
+        clearPendingRoutineSuggestion();
+        if (panel && panel.parentNode) {
+          panel.parentNode.removeChild(panel);
+        }
+        return true;
+      } catch (err) {
+        if (err && (err.status === 401 || err.status === 403)) {
+          await handleUnauthorized("routine-dismiss");
+          return false;
+        }
+        if (statusEl) {
+          statusEl.textContent = err && err.message ? err.message : "Dismiss failed.";
+        }
+        return false;
+      }
+    }
+
     function sendQuickReply(text) {
       if (!input) return;
       input.value = text;
@@ -6532,6 +6594,10 @@
       panel.className = "ux-goal-intent-panel";
       panel.dataset.suggestionType = "routine";
       panel.dataset.suggestionId = suggestionId || "";
+      if (suggestionId) {
+        othelloState.pendingRoutineSuggestionId = suggestionId;
+        othelloState.pendingRoutineAcceptFn = null;
+      }
 
       const title = document.createElement("div");
       title.className = "ux-goal-intent-panel__title";
@@ -6590,6 +6656,15 @@
 
       actions.appendChild(amBtn);
       actions.appendChild(pmBtn);
+
+      const dismissBtn = document.createElement("button");
+      dismissBtn.className = "ux-goal-intent-btn link";
+      dismissBtn.dataset.action = "dismiss";
+      dismissBtn.textContent = "Dismiss";
+      dismissBtn.addEventListener("click", async () => {
+        await rejectRoutineSuggestion(suggestionId, panel);
+      });
+      actions.appendChild(dismissBtn);
       panel.appendChild(actions);
 
       entry.row.appendChild(panel);
@@ -6638,7 +6713,26 @@
 
       const confirmBtn = document.createElement("button");
       confirmBtn.className = "ux-goal-intent-btn primary";
-      confirmBtn.textContent = "Confirm & Save";
+      confirmBtn.dataset.action = "confirm";
+      confirmBtn.textContent = "Confirm";
+
+      const editBtn = document.createElement("button");
+      editBtn.className = "ux-goal-intent-btn secondary";
+      editBtn.dataset.action = "edit";
+      editBtn.textContent = "Edit";
+      editBtn.addEventListener("click", () => {
+        if (!input) return;
+        input.value = "Edit: ";
+        input.focus();
+      });
+
+      const dismissBtn = document.createElement("button");
+      dismissBtn.className = "ux-goal-intent-btn link";
+      dismissBtn.dataset.action = "dismiss";
+      dismissBtn.textContent = "Dismiss";
+      dismissBtn.addEventListener("click", async () => {
+        await rejectRoutineSuggestion(suggestionId, panel);
+      });
 
       const status = document.createElement("div");
       status.className = "ux-goal-intent-status";
@@ -6660,6 +6754,8 @@
       });
 
       actions.appendChild(confirmBtn);
+      actions.appendChild(editBtn);
+      actions.appendChild(dismissBtn);
       panel.appendChild(actions);
       panel.appendChild(status);
 
@@ -6829,6 +6925,54 @@
       input.focus();
       let sendUiState = beginSendUI({ label: isConfirmSave ? "Saving..." : "ThinkingÔÇª", disableSend: true });
       try {
+        const pendingRoutineId = othelloState.pendingRoutineSuggestionId;
+        if (pendingRoutineId) {
+          const routinePanel = findVisiblePendingRoutinePanel();
+          const confirmWords = new Set(["confirm", "save", "ok", "okay", "yes"]);
+          const dismissWords = new Set(["dismiss", "cancel", "discard"]);
+          const editMatch = normalizedText.match(/^(edit|change|update)\b/i);
+          if (confirmWords.has(normalizedText)) {
+            try {
+              if (await acceptRoutineSuggestion(pendingRoutineId, {
+                confirmBtn: routinePanel && routinePanel.querySelector('[data-action="confirm"]'),
+                statusEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-status"),
+                actionsEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-panel__actions")
+              })) {
+                addMessage("bot", "Confirmed.");
+              }
+            } catch (err) {
+              console.warn("[Othello UI] routine confirm failed:", err);
+            }
+            return;
+          }
+          if (dismissWords.has(normalizedText)) {
+            await rejectRoutineSuggestion(pendingRoutineId, routinePanel);
+            return;
+          }
+          const patchText = text.toLowerCase();
+          const patchSignal = /(\b([01]?\d|2[0-3]):([0-5]\d)\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(morning|afternoon|evening|tonight)\b|\b(at|around|by)\s+([1-9]|1[0-2])\b|\b(daily|every day|each day|weekday|weekdays|weekend|weekends)\b|\bmon(day)?s?\s*-\s*fri(day)?s?\b|\b(mon|tue|wed|thu|fri|sat|sun)\b|\b\d{1,3}\s*(?:-?\s*)?(?:minutes?|mins?|min)\b)/.test(patchText);
+          if (editMatch || patchSignal) {
+            try {
+              await patchRoutineSuggestion(pendingRoutineId, text, routinePanel);
+            } catch (err) {
+              if (err && (err.status === 401 || err.status === 403)) {
+                await handleUnauthorized("routine-patch");
+              }
+              const statusEl = routinePanel ? routinePanel.querySelector(".ux-goal-intent-status") : null;
+              if (statusEl) {
+                statusEl.textContent = err && err.message ? err.message : "Update failed.";
+              }
+              console.warn("[Othello UI] routine patch failed:", err);
+            }
+            return;
+          }
+          addMessage(
+            "bot",
+            "You have a routine draft pending. Reply Confirm to save, Edit: ... to change it, or Dismiss to discard."
+          );
+          return;
+        }
+
         if (isConfirmSave) {
           const goalDecision = await acceptVisibleGoalIntentSuggestion();
           if (goalDecision.handled) {
