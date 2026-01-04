Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Deploy + runtime verification; mark COMPLETE if PASS
Completed: Added routine panel visibility guard; prevented goal decision hijack; fixed status line regression
Remaining: Runtime verification on deployed env + any hotfix if FAIL
Next Action: Deploy this commit and test typed confirm/save with and without visible routine card + goal intent panel; report PASS/FAIL + screenshot/console.
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; othello_ui.html
Anchors:
- findVisiblePendingRoutinePanel: othello_ui.html:6398
- isGoalIntentDecisionPending: othello_ui.html:6409
- buildRoutineReadyPanel: othello_ui.html:6576
- typed confirm intercept: othello_ui.html:6746
Verification:
- Static: manual review (UI-only)
- Runtime: Not run (pending deploy)

diff --git a/othello_ui.html b/othello_ui.html
index f0851c0b..3b73d4e7 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6388,6 +6388,29 @@
       othelloState.pendingRoutineSuggestionId = null;
       othelloState.pendingRoutineAcceptFn = null;
     }
+    function isElementVisible(el) {
+      if (!el) return false;
+      const style = window.getComputedStyle(el);
+      if (!style || style.display === "none" || style.visibility === "hidden") return false;
+      return el.offsetParent !== null;
+    }
+
+    function findVisiblePendingRoutinePanel() {
+      const panels = Array.from(
+        document.querySelectorAll('.ux-goal-intent-panel[data-suggestion-type="routine"]')
+      );
+      const visible = panels.filter(isElementVisible).pop() || null;
+      if (!visible && othelloState.pendingRoutineSuggestionId) {
+        clearPendingRoutineSuggestion();
+      }
+      return visible;
+    }
+
+    function isGoalIntentDecisionPending() {
+      const latest = getLatestGoalIntentEntry();
+      if (!latest || !latest.entry || !latest.entry.panelEl) return false;
+      return isElementVisible(latest.entry.panelEl);
+    }
 
     async function acceptRoutineSuggestion(suggestionId, uiRefs) {
       if (!suggestionId) return false;
@@ -6721,17 +6744,34 @@
       statusEl.textContent = "ThinkingÔÇª";
 
       const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim();
-      if ((normalizedText === "confirm" || normalizedText === "save") &&
-          typeof othelloState.pendingRoutineAcceptFn === "function") {
-        statusEl.textContent = "Saving...";
-        try {
-          const accepted = await othelloState.pendingRoutineAcceptFn();
-          statusEl.textContent = accepted ? "Online" : "Error";
-        } catch (err) {
-          console.warn("[Othello UI] routine typed confirm failed:", err);
-          statusEl.textContent = "Error";
+      const isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
+      if (isConfirmSave && !isGoalIntentDecisionPending()) {
+        const routinePanel = findVisiblePendingRoutinePanel();
+        const panelId = routinePanel ? routinePanel.dataset.suggestionId : null;
+        const pendingId = othelloState.pendingRoutineSuggestionId;
+        const canAcceptRoutine = routinePanel &&
+          typeof othelloState.pendingRoutineAcceptFn === "function" &&
+          pendingId && panelId &&
+          String(pendingId) === String(panelId);
+        if (canAcceptRoutine) {
+          const previousStatus = statusEl.textContent;
+          statusEl.textContent = "Saving...";
+          try {
+            const accepted = await othelloState.pendingRoutineAcceptFn();
+            if (accepted) {
+              statusEl.textContent = "Saved";
+              window.setTimeout(() => {
+                statusEl.textContent = previousStatus;
+              }, 800);
+            } else {
+              statusEl.textContent = previousStatus;
+            }
+          } catch (err) {
+            console.warn("[Othello UI] routine typed confirm failed:", err);
+            statusEl.textContent = previousStatus;
+          }
+          return;
         }
-        return;
       }
 
       const goalIntentResolved = await resolveGoalIntentDecision(text);

