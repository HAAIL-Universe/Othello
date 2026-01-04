Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Adjust sendMessage UI state handling; add pending goal intent fallback; ensure typed confirm ack; update evidence log
Completed: Added pendingGoalIntent tracking/clearing; added begin/end send UI helpers; updated typed confirm to prefer pending goal then routine with ack; updated goal accept to return success
Remaining: Runtime verification pending deploy; report PASS/FAIL + screenshot/console; commit after runtime PASS
Next Action: Deploy and run runtime checklist; report PASS/FAIL + screenshot/console.
Commit: 254a991328b9a60eb6be7053e441e6ffe7579555 (branch ux/routine-clarify-panel-pending)
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; othello_ui.html; evidence/updatedifflog.md
Anchors:
- pendingGoalIntent state: othello_ui.html:2791
- clearPendingGoalIntent: othello_ui.html:6066
- buildGoalIntentPanel: othello_ui.html:6195
- handleGoalIntentSuggestion: othello_ui.html:6344
- getLatestGoalIntentEntry: othello_ui.html:6660
- resolveGoalIntentDecision: othello_ui.html:6684
- beginSendUI/endSendUI: othello_ui.html:6738
- typed confirm handling: othello_ui.html:6767
Verification:
- Static: manual review (UI-only)
- Runtime: PENDING (deploy-required)
  1) Create routine -> confirm card -> type "confirm" -> routine saved; status not stuck; ack appears
  2) Create goal suggestion ("Want this saved…") -> type "confirm" -> goal saved; status not stuck; ack appears
  3) Type "confirm" with no pending goal/routine -> normal backend message
  4) Ensure goal pending takes priority over routine pending
  5) Send button remains usable after confirm flow

diff --git a/othello_ui.html b/othello_ui.html
index 3b73d4e7..93137824 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2788,6 +2788,7 @@
       messagesByClientId: {},
       dismissedSuggestionIds: new Set(),
       goalIntentSuggestions: {},
+      pendingGoalIntent: null,
       mobileEditorPinned: false,
       mobileBackJustPressedAt: 0,
       creatingRoutine: false,
@@ -6061,7 +6062,13 @@
       return trimmed.length > 60 ? trimmed.slice(0, 60).trim() : trimmed;
     }
 
+    function clearPendingGoalIntent(clientMessageId) {
+      const pending = othelloState.pendingGoalIntent;
+      if (pending && (!clientMessageId || pending.clientMessageId === clientMessageId)) othelloState.pendingGoalIntent = null;
+    }
+
     function clearGoalIntentUI(clientMessageId) {
+      clearPendingGoalIntent(clientMessageId);
       const entry = othelloState.messagesByClientId[clientMessageId];
       if (!entry) return;
       if (entry.bubbleEl) {
@@ -6087,7 +6094,7 @@
       const trimmedDesc = (description || "").trim();
       if (trimmedTitle.length < 3) {
         if (statusEl) statusEl.textContent = "Title is too short.";
-        return;
+        return false;
       }
       disablePanelButtons(panelEl, true);
       if (statusEl) statusEl.textContent = "Saving goal...";
@@ -6111,7 +6118,7 @@
           }
           if (statusEl) statusEl.textContent = errMsg;
           disablePanelButtons(panelEl, false);
-          return;
+          return false;
         }
         const data = await res.json();
         const goal = data && data.goal ? data.goal : null;
@@ -6128,10 +6135,12 @@
             showGoalDetail(goalId);
           }
         }
+        return true;
       } catch (err) {
         console.error("[Othello UI] create goal failed:", err);
         if (statusEl) statusEl.textContent = "Network error.";
         disablePanelButtons(panelEl, false);
+        return false;
       }
     }
 
@@ -6338,7 +6347,8 @@
       if (!clientMessageId) return;
       if (isSuggestionDismissed(suggestion.type, clientMessageId)) return;
       othelloState.goalIntentSuggestions[clientMessageId] = suggestion;
-      const entry = othelloState.messagesByClientId[clientMessageId];
+      const entry = othelloState.messagesByClientId[clientMessageId] || null;
+      othelloState.pendingGoalIntent = { clientMessageId, createdAt: Date.now(), acceptFn: () => createGoalFromSuggestion({ title: pickSuggestionTitle(suggestion, entry ? entry.text : ""), description: pickSuggestionBody(suggestion, entry ? entry.text : ""), clientMessageId, statusEl: null, panelEl: null }) };
       if (!entry || !entry.bubbleEl || !entry.rowEl) return;
       if (entry.panelEl) return;
       entry.bubbleEl.classList.add("ux-goal-intent");
@@ -6406,12 +6416,6 @@
       return visible;
     }
 
-    function isGoalIntentDecisionPending() {
-      const latest = getLatestGoalIntentEntry();
-      if (!latest || !latest.entry || !latest.entry.panelEl) return false;
-      return isElementVisible(latest.entry.panelEl);
-    }
-
     async function acceptRoutineSuggestion(suggestionId, uiRefs) {
       if (!suggestionId) return false;
       const confirmBtn = uiRefs && uiRefs.confirmBtn;
@@ -6731,6 +6735,21 @@
       othelloState.goalUpdateCounts[gid] = (othelloState.goalUpdateCounts[gid] || 0) + 1;
     }
 
+    function beginSendUI(options = {}) {
+      const previousStatus = statusEl ? statusEl.textContent : "", label = options.label || "ThinkingÔÇª", disableSend = options.disableSend !== false;
+      if (disableSend && sendBtn) sendBtn.disabled = true;
+      if (statusEl) statusEl.textContent = label;
+      return { previousStatus, label, disableSend };
+    }
+
+    function endSendUI(state) {
+      if (!state) return;
+      if (state.disableSend !== false && sendBtn) sendBtn.disabled = false;
+      if (statusEl && (!statusEl.textContent || statusEl.textContent === state.label)) {
+        statusEl.textContent = state.previousStatus || "Online";
+      }
+    }
+
     async function sendMessage() {
       const text = input.value.trim();
       if (!text) return;
@@ -6738,55 +6757,53 @@
       const pendingEdit = othelloState.pendingGoalEdit;
       const metaNote = pendingEdit ? `Editing goal #${pendingEdit.goal_id}` : "";
       const clientMessageId = generateClientMessageId();
+      const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim(), isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
       addMessage("user", text, { metaNote, clientMessageId });
       input.value = "";
       input.focus();
-      statusEl.textContent = "ThinkingÔÇª";
-
-      const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim();
-      const isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
-      if (isConfirmSave && !isGoalIntentDecisionPending()) {
-        const routinePanel = findVisiblePendingRoutinePanel();
-        const panelId = routinePanel ? routinePanel.dataset.suggestionId : null;
-        const pendingId = othelloState.pendingRoutineSuggestionId;
-        const canAcceptRoutine = routinePanel &&
-          typeof othelloState.pendingRoutineAcceptFn === "function" &&
-          pendingId && panelId &&
-          String(pendingId) === String(panelId);
-        if (canAcceptRoutine) {
-          const previousStatus = statusEl.textContent;
-          statusEl.textContent = "Saving...";
-          try {
-            const accepted = await othelloState.pendingRoutineAcceptFn();
-            if (accepted) {
-              statusEl.textContent = "Saved";
-              window.setTimeout(() => {
-                statusEl.textContent = previousStatus;
-              }, 800);
-            } else {
-              statusEl.textContent = previousStatus;
+      let sendUiState = beginSendUI({ label: isConfirmSave ? "Saving..." : "ThinkingÔÇª", disableSend: true });
+      try {
+        if (isConfirmSave) {
+          const pendingGoal = othelloState.pendingGoalIntent;
+          if (pendingGoal && typeof pendingGoal.acceptFn === "function") {
+            try {
+              if (await pendingGoal.acceptFn()) addMessage("bot", "Confirmed.");
+            } catch (err) {
+              console.warn("[Othello UI] goal typed confirm failed:", err);
             }
-          } catch (err) {
-            console.warn("[Othello UI] routine typed confirm failed:", err);
-            statusEl.textContent = previousStatus;
+            return;
+          }
+
+          const routinePanel = findVisiblePendingRoutinePanel(), panelId = routinePanel ? routinePanel.dataset.suggestionId : null;
+          const pendingId = othelloState.pendingRoutineSuggestionId;
+          const canAcceptRoutine = routinePanel &&
+            typeof othelloState.pendingRoutineAcceptFn === "function" &&
+            pendingId && panelId &&
+            String(pendingId) === String(panelId);
+          if (canAcceptRoutine) {
+            try {
+              if (await othelloState.pendingRoutineAcceptFn()) addMessage("bot", "Confirmed.");
+            } catch (err) {
+              console.warn("[Othello UI] routine typed confirm failed:", err);
+            }
+            return;
           }
-          return;
         }
-      }
 
-      const goalIntentResolved = await resolveGoalIntentDecision(text);
-      if (goalIntentResolved) {
-        fetch(V1_MESSAGES_API, {
-          method: "POST",
-          headers: { "Content-Type": "application/json" },
-          credentials: "include",
-          body: JSON.stringify({ transcript: text, source: "text" })
-        }).catch(() => {});
-        statusEl.textContent = "Online";
-        return;
-      }
+        if (!isConfirmSave) {
+          const goalIntentResolved = await resolveGoalIntentDecision(text);
+          if (goalIntentResolved) {
+            fetch(V1_MESSAGES_API, {
+              method: "POST",
+              headers: { "Content-Type": "application/json" },
+              credentials: "include",
+              body: JSON.stringify({ transcript: text, source: "text" })
+            }).catch(() => {});
+            statusEl.textContent = "Online";
+            return;
+          }
+        }
 
-      try {
         const mode = (othelloState.currentMode || "companion").toLowerCase();
         const channel = mode === "companion" ? "companion" : "planner";
         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
@@ -6938,6 +6955,8 @@
         console.error("[Othello UI] sendMessage error:", err);
         addMessage("bot", "[Connection error: backend unreachable]");
         statusEl.textContent = "Offline";
+      } finally {
+        endSendUI(sendUiState);
       }
     }
 
