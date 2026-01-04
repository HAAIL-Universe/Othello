Cycle Status: STOPPED:ENVIRONMENT_LIMITATION
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined
Remaining: Runtime verification (deploy-required)
Next Action: Verify changes in runtime environment (specifically that the ReferenceError is gone and secondary suggestions work) and commit with message "UI: focus-safe secondary suggestions for goal/routine intents"

diff --git a/othello_ui.html b/othello_ui.html
index 86b201a3..6242c4e7 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2788,6 +2788,7 @@
       messagesByClientId: {},
       dismissedSuggestionIds: new Set(),
       goalIntentSuggestions: {},
+      secondarySuggestionsByClientId: {},
       mobileEditorPinned: false,
       mobileBackJustPressedAt: 0,
       creatingRoutine: false,
@@ -5984,12 +5985,14 @@
       if (role === "user" && clientMessageId) {
         othelloState.messagesByClientId[clientMessageId] = {
+          clientMessageId,
           bubbleEl: bubble,
           rowEl: row,
           text,
           ts: Date.now(),
           panelEl: null,
         };
+        refreshSecondarySuggestionUI(othelloState.messagesByClientId[clientMessageId]);
       }
 
       // Scroll to latest message
@@ -6039,6 +6042,227 @@
       }
     }
 
+    function getSecondarySuggestions(clientMessageId) {
+      if (!clientMessageId) return [];
+      const store = othelloState.secondarySuggestionsByClientId || {};
+      return store[clientMessageId] || [];
+    }
+
+    function updateSecondaryBadge(entry) {
+      if (!entry || !entry.clientMessageId || !entry.bubbleEl) return;
+      const count = getSecondarySuggestions(entry.clientMessageId).length;
+      const meta = entry.bubbleEl.querySelector(".meta");
+      if (!meta) return;
+      if (!count) {
+        if (entry.secondaryBadgeEl) {
+          entry.secondaryBadgeEl.remove();
+          entry.secondaryBadgeEl = null;
+        }
+        if (entry.secondaryPanelEl) entry.secondaryPanelEl.style.display = "none";
+        return;
+      }
+      let badge = entry.secondaryBadgeEl;
+      if (!badge || !badge.isConnected) {
+        badge = document.createElement("span");
+        badge.style.marginLeft = "0.4rem";
+        badge.style.cursor = "pointer";
+        badge.style.fontSize = "0.75rem";
+        badge.style.userSelect = "none";
+        badge.addEventListener("click", () => toggleSecondarySuggestionPanel(entry));
+        entry.secondaryBadgeEl = badge;
+        meta.appendChild(badge);
+      }
+      badge.textContent = `•${count}`;
+      if (entry.secondaryPanelEl && entry.secondaryPanelEl.style.display === "flex") {
+        renderSecondarySuggestionPanel(entry);
+      }
+    }
+
+    function refreshSecondarySuggestionUI(entry) {
+      updateSecondaryBadge(entry);
+    }
+
+    function addSecondarySuggestion(clientMessageId, suggestion) {
+      if (!clientMessageId || !suggestion) return false;
+      if (!othelloState.secondarySuggestionsByClientId) {
+        othelloState.secondarySuggestionsByClientId = {};
+      }
+      const suggestionType = (suggestion.type || suggestion.kind || "suggestion").toLowerCase();
+      const normalizedType = suggestionType === "goal" ? "goal_intent" : suggestionType;
+      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
+      const key = suggestionId != null ? `${normalizedType}:${suggestionId}` : `${normalizedType}:${clientMessageId}`;
+      const list = othelloState.secondarySuggestionsByClientId[clientMessageId] || [];
+      if (list.some((item) => item.key === key)) return false;
+      list.push({ key, type: normalizedType, suggestionId, suggestion });
+      othelloState.secondarySuggestionsByClientId[clientMessageId] = list;
+      const entry = othelloState.messagesByClientId[clientMessageId];
+      if (entry) {
+        entry.clientMessageId = clientMessageId;
+        updateSecondaryBadge(entry);
+      }
+      return true;
+    }
+
+    function dismissSecondarySuggestion(clientMessageId, suggestionKey) {
+      const list = getSecondarySuggestions(clientMessageId);
+      if (!list.length) return;
+      const item = list.find((entry) => entry.key === suggestionKey);
+      if (item && item.type) {
+        recordSuggestionDismissal(item.type, clientMessageId);
+        postSuggestionDismissal(item.type, clientMessageId);
+      }
+      const next = list.filter((entry) => entry.key !== suggestionKey);
+      if (next.length) {
+        othelloState.secondarySuggestionsByClientId[clientMessageId] = next;
+      } else {
+        delete othelloState.secondarySuggestionsByClientId[clientMessageId];
+      }
+      const entry = othelloState.messagesByClientId[clientMessageId];
+      if (entry) updateSecondaryBadge(entry);
+    }
+
+    async function applySecondarySuggestion(entry, item, uiRefs) {
+      if (!entry || !item) return false;
+      const statusEl = uiRefs && uiRefs.statusEl ? uiRefs.statusEl : null;
+      const actionsEl = uiRefs && uiRefs.actionsEl ? uiRefs.actionsEl : null;
+      const applyBtn = uiRefs && uiRefs.applyBtn ? uiRefs.applyBtn : null;
+      if (item.type === "routine" && item.suggestionId) {
+        const priorPendingId = othelloState.pendingRoutineSuggestionId;
+        const priorAcceptFn = othelloState.pendingRoutineAcceptFn;
+        const accepted = await acceptRoutineSuggestion(item.suggestionId, { confirmBtn: applyBtn, statusEl, actionsEl });
+        if (getActiveFocusKind(othelloState) === "routine_draft" && priorPendingId && priorPendingId !== item.suggestionId) {
+          othelloState.pendingRoutineSuggestionId = priorPendingId;
+          othelloState.pendingRoutineAcceptFn = priorAcceptFn;
+        }
+        return accepted;
+      }
+      if ((item.type === "goal_intent" || item.type === "goal") && item.suggestion) {
+        const prevActiveGoalId = othelloState.activeGoalId;
+        const title = pickSuggestionTitle(item.suggestion, entry.text);
+        const description = pickSuggestionBody(item.suggestion, entry.text);
+        const accepted = await createGoalFromSuggestion({
+          title,
+          description,
+          clientMessageId: entry.clientMessageId,
+          statusEl,
+          panelEl: actionsEl,
+          suggestionId: item.suggestionId
+        });
+        if (prevActiveGoalId !== othelloState.activeGoalId) {
+          setActiveGoal(prevActiveGoalId);
+        }
+        return accepted;
+      }
+      return false;
+    }
+
+    function ensureSecondaryPanel(entry) {
+      if (!entry || !entry.rowEl) return null;
+      if (entry.secondaryPanelEl && entry.secondaryPanelEl.isConnected) return entry.secondaryPanelEl;
+      const panel = document.createElement("div");
+      panel.className = "ux-goal-intent-panel";
+      panel.style.display = "none";
+      panel.addEventListener("click", async (event) => {
+        const button = event.target.closest("button[data-action]");
+        if (!button) return;
+        const itemEl = button.closest("[data-secondary-key]");
+        if (!itemEl) return;
+        const key = itemEl.dataset.secondaryKey;
+        const suggestions = getSecondarySuggestions(entry.clientMessageId);
+        const item = suggestions.find((suggestion) => suggestion.key === key);
+        if (!item) return;
+        if (button.dataset.action === "dismiss") {
+          dismissSecondarySuggestion(entry.clientMessageId, key);
+          renderSecondarySuggestionPanel(entry);
+          return;
+        }
+        const statusEl = itemEl.querySelector(".ux-goal-intent-status");
+        const actionsEl = itemEl.querySelector(".ux-goal-intent-panel__actions");
+        button.disabled = true;
+        try {
+          const accepted = await applySecondarySuggestion(entry, item, {
+            statusEl,
+            actionsEl,
+            applyBtn: button
+          });
+          if (accepted) {
+            dismissSecondarySuggestion(entry.clientMessageId, key);
+          } else {
+            button.disabled = false;
+          }
+        } catch (err) {
+          if (statusEl) {
+            statusEl.textContent = err && err.message ? err.message : "Apply failed.";
+          }
+          button.disabled = false;
+        }
+      });
+      entry.secondaryPanelEl = panel;
+      entry.rowEl.appendChild(panel);
+      return panel;
+    }
+
+    function renderSecondarySuggestionPanel(entry) {
+      if (!entry || !entry.clientMessageId) return;
+      const panel = ensureSecondaryPanel(entry);
+      if (!panel) return;
+      const suggestions = getSecondarySuggestions(entry.clientMessageId);
+      panel.innerHTML = "";
+      if (!suggestions.length) {
+        panel.style.display = "none";
+        return;
+      }
+      suggestions.forEach((item) => {
+        const suggestion = item.suggestion || {};
+        const itemEl = document.createElement("div");
+        itemEl.dataset.secondaryKey = item.key;
+        const title = document.createElement("div");
+        title.className = "ux-goal-intent-panel__title";
+        title.textContent = item.type === "routine" ? "Routine suggestion" : "Goal suggestion";
+        const summary = document.createElement("div");
+        summary.className = "ux-goal-intent-panel__subtitle";
+        if (item.type === "routine") {
+          const draft = suggestion.payload && suggestion.payload.draft ? suggestion.payload.draft : null;
+          const details = [];
+          if (draft && draft.title) details.push(draft.title);
+          if (draft) details.push(formatRoutineTime(draft));
+          summary.textContent = details.filter(Boolean).join(" · ") || entry.text || "Routine draft";
+        } else {
+          summary.textContent = pickSuggestionTitle(suggestion, entry.text);
+        }
+        const actions = document.createElement("div");
+        actions.className = "ux-goal-intent-panel__actions";
+        const applyBtn = document.createElement("button");
+        applyBtn.className = "ux-goal-intent-btn primary";
+        applyBtn.dataset.action = "apply";
+        applyBtn.textContent = "Apply";
+        const dismissBtn = document.createElement("button");
+        dismissBtn.className = "ux-goal-intent-btn link";
+        dismissBtn.dataset.action = "dismiss";
+        dismissBtn.textContent = "Dismiss";
+        const statusEl = document.createElement("div");
+        statusEl.className = "ux-goal-intent-status";
+        actions.appendChild(applyBtn);
+        actions.appendChild(dismissBtn);
+        itemEl.appendChild(title);
+        itemEl.appendChild(summary);
+        itemEl.appendChild(actions);
+        itemEl.appendChild(statusEl);
+        panel.appendChild(itemEl);
+      });
+    }
+
+    function toggleSecondarySuggestionPanel(entry) {
+      const panel = ensureSecondaryPanel(entry);
+      if (!panel) return;
+      if (panel.style.display === "flex") {
+        panel.style.display = "none";
+        return;
+      }
+      renderSecondarySuggestionPanel(entry);
+      panel.style.display = "flex";
+    }
+
     function pickSuggestionBody(suggestion, fallbackText) {
       const raw = suggestion && typeof suggestion.body_suggestion === "string"
         ? suggestion.body_suggestion.trim()
@@ -6388,9 +6612,9 @@
       const routineSignals = /\b(every day|each day|daily|weekly|remind me|alarm|routine|habit|meet at)\b/.test(text);
       const timeSignals = /(\b([01]?\d|2[0-3]):([0-5]\d)\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(at|around|by)\s+([1-9]|1[0-2])\b)/.test(text);
       if (routineSignals || timeSignals) return false;
-      if (uiState && uiState.pendingRoutineSuggestionId) return false;
+      if (!explicitGoal && uiState && uiState.pendingRoutineSuggestionId) return false;
       const routinePanel = document.querySelector('.ux-goal-intent-panel[data-suggestion-type="routine"]');
-      if (routinePanel && routinePanel.offsetParent !== null) return false;
+      if (routinePanel && routinePanel.offsetParent !== null && !explicitGoal) return false;
       return explicitGoal;
     }
 
@@ -6407,6 +6631,11 @@
       const entryText = entry && typeof entry.text === "string" ? entry.text : "";
       if (!shouldSuggestGoalDraft(entryText, normalizedSuggestion, othelloState)) return;
       if (isSuggestionDismissed(normalizedSuggestion.type, clientMessageId)) return;
+      const focusKind = getActiveFocusKind(othelloState);
+      if (focusKind && focusKind !== "goal") {
+        addSecondarySuggestion(clientMessageId, normalizedSuggestion);
+        return;
+      }
       othelloState.goalIntentSuggestions[clientMessageId] = normalizedSuggestion;
       if (!entry || !entry.bubbleEl || !entry.rowEl) return;
       if (entry.panelEl) return;
@@ -6417,9 +6646,6 @@
     }
 
     function applySuggestionMeta(meta) {
-      if (othelloState.pendingRoutineSuggestionId || othelloState.currentView === "routine-planner") {
-        return;
-      }
       const suggestions = meta && Array.isArray(meta.suggestions) ? meta.suggestions : [];
       suggestions.forEach(handleGoalIntentSuggestion);
     }
@@ -6809,11 +7035,22 @@
       return panel;
     }
 
-    async function applyRoutineMeta(meta, entry) {
+    async function applyRoutineMeta(meta, entry, sourceClientMessageId) {
       if (!meta || !entry || !entry.row) return;
       const intent = meta.intent || "";
       const suggestionId = meta.routine_suggestion_id;
       if (!suggestionId) return;
+      const focusKind = getActiveFocusKind(othelloState);
+      const clientMessageId = meta.source_client_message_id || sourceClientMessageId || "";
+      if (focusKind) {
+        if (clientMessageId) {
+          addSecondarySuggestion(clientMessageId, {
+            type: "routine",
+            suggestion_id: suggestionId
+          });
+        }
+        return;
+      }
       if (intent === "routine_clarify") {
         await buildRoutineClarifyPanel(entry, suggestionId);
         return;
@@ -7025,6 +7262,13 @@
             }
             return;
           }
+          if (shouldSuggestGoalDraft(text, null, othelloState)) {
+            addSecondarySuggestion(clientMessageId, {
+              type: "goal_intent",
+              source_client_message_id: clientMessageId,
+              body_suggestion: text
+            });
+          }
           addMessage(
             "bot",
             "You have an unsaved routine draft. Confirm, Edit, Add another, or Dismiss before continuing."
@@ -7131,7 +7375,7 @@
         }
         const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId });
         try {
-          await applyRoutineMeta(meta, botEntry);
+          await applyRoutineMeta(meta, botEntry, clientMessageId);
         } catch (err) {
           console.warn("[Othello UI] routine meta render failed:", err);
         }
