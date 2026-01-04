Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log
Completed: Added getActiveFocusKind focus lock helper
Remaining: Commit Phase 1 checkpoint; implement secondary suggestion capture + focus lock wiring; runtime verification pending deploy
Next Action: Commit checkpoint "UI: establish focus lock signal" and pause for Phase 2 instructions.

Paths Read: build_docs/theexecutor.md; othello_ui.html
Anchors:
- Focus lock helper: othello_ui.html:6370
- Goal-suggestion trigger: othello_ui.html:6397
- shouldSuggestGoalDraft: othello_ui.html:6378
- Routine confirm UI: othello_ui.html:6714
- Routine draft guard: othello_ui.html:6974
Verification:
- Static: not run (UI-only)
- Runtime: PENDING (deploy-required)
- Behavioral: PENDING (focus lock + secondary suggestions not implemented)
- Contract: PENDING (Phase 1 only)

diff --git a/othello_ui.html b/othello_ui.html
index 5089ede8..86b201a3 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6367,6 +6367,33 @@
       return panel;
     }
 
+    function getActiveFocusKind(uiState) {
+      // Routine draft wins; otherwise focused goal; else null.
+      if (!uiState) return null;
+      if (uiState.pendingRoutineSuggestionId != null) return "routine_draft";
+      if (uiState.activeGoalId != null) return "goal";
+      return null;
+    }
+
+    function shouldSuggestGoalDraft(userText, response, uiState) {
+      const raw = String(userText || "").trim();
+      if (!raw) return false;
+      const text = raw.toLowerCase();
+      const tokens = text.split(/\s+/).filter(Boolean);
+      const explicitGoal = /(goal:|my goal is|i want to|i'm going to|im going to|i am going to|i will|new goal|i need to achieve|i'm working towards|im working towards)/.test(text);
+      if (tokens.length <= 4 && !explicitGoal) return false;
+      if (raw.includes("?") || /^(what|why|how|when|where|who|can|should|do|is|are)\b/.test(text)) {
+        return false;
+      }
+      const routineSignals = /\b(every day|each day|daily|weekly|remind me|alarm|routine|habit|meet at)\b/.test(text);
+      const timeSignals = /(\b([01]?\d|2[0-3]):([0-5]\d)\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(at|around|by)\s+([1-9]|1[0-2])\b)/.test(text);
+      if (routineSignals || timeSignals) return false;
+      if (uiState && uiState.pendingRoutineSuggestionId) return false;
+      const routinePanel = document.querySelector('.ux-goal-intent-panel[data-suggestion-type="routine"]');
+      if (routinePanel && routinePanel.offsetParent !== null) return false;
+      return explicitGoal;
+    }
+
     function handleGoalIntentSuggestion(suggestion) {
       if (!suggestion) return;
       const suggestionType = suggestion.type || suggestion.kind;
@@ -6376,9 +6403,11 @@
         : suggestion;
       const clientMessageId = normalizedSuggestion.source_client_message_id;
       if (!clientMessageId) return;
+      const entry = othelloState.messagesByClientId[clientMessageId] || null;
+      const entryText = entry && typeof entry.text === "string" ? entry.text : "";
+      if (!shouldSuggestGoalDraft(entryText, normalizedSuggestion, othelloState)) return;
       if (isSuggestionDismissed(normalizedSuggestion.type, clientMessageId)) return;
       othelloState.goalIntentSuggestions[clientMessageId] = normalizedSuggestion;
-      const entry = othelloState.messagesByClientId[clientMessageId] || null;
       if (!entry || !entry.bubbleEl || !entry.rowEl) return;
       if (entry.panelEl) return;
       entry.bubbleEl.classList.add("ux-goal-intent");
@@ -6726,6 +6755,22 @@
         input.focus();
       });
 
+      const addAnotherBtn = document.createElement("button");
+      addAnotherBtn.className = "ux-goal-intent-btn secondary";
+      addAnotherBtn.dataset.action = "add-another";
+      addAnotherBtn.textContent = "Add another";
+      addAnotherBtn.addEventListener("click", async () => {
+        if (!suggestionId) return;
+        const accepted = await acceptRoutineSuggestion(
+          suggestionId,
+          { confirmBtn: addAnotherBtn, statusEl: status, actionsEl: actions }
+        );
+        if (accepted && input) {
+          input.value = "Add a routine: ";
+          input.focus();
+        }
+      });
+
       const dismissBtn = document.createElement("button");
       dismissBtn.className = "ux-goal-intent-btn link";
       dismissBtn.dataset.action = "dismiss";
@@ -6755,6 +6800,7 @@
 
       actions.appendChild(confirmBtn);
       actions.appendChild(editBtn);
+      actions.appendChild(addAnotherBtn);
       actions.appendChild(dismissBtn);
       panel.appendChild(actions);
       panel.appendChild(status);
@@ -6930,6 +6976,7 @@
           const routinePanel = findVisiblePendingRoutinePanel();
           const confirmWords = new Set(["confirm", "save", "ok", "okay", "yes"]);
           const dismissWords = new Set(["dismiss", "cancel", "discard"]);
+          const addAnotherMatch = normalizedText.startsWith("add another") || normalizedText.startsWith("another routine");
           const editMatch = normalizedText.match(/^(edit|change|update)\b/i);
           if (confirmWords.has(normalizedText)) {
             try {
@@ -6945,6 +6992,18 @@
             }
             return;
           }
+          if (addAnotherMatch) {
+            const accepted = await acceptRoutineSuggestion(pendingRoutineId, {
+              confirmBtn: routinePanel && routinePanel.querySelector('[data-action="add-another"]'),
+              statusEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-status"),
+              actionsEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-panel__actions")
+            });
+            if (accepted && input) {
+              input.value = "Add a routine: ";
+              input.focus();
+            }
+            return;
+          }
           if (dismissWords.has(normalizedText)) {
             await rejectRoutineSuggestion(pendingRoutineId, routinePanel);
             return;
@@ -6968,7 +7027,7 @@
           }
           addMessage(
             "bot",
-            "You have a routine draft pending. Reply Confirm to save, Edit: ... to change it, or Dismiss to discard."
+            "You have an unsaved routine draft. Confirm, Edit, Add another, or Dismiss before continuing."
           );
           return;
         }
