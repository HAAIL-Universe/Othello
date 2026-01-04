Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Deploy + runtime verification; mark COMPLETE if PASS
Completed: Implemented typed confirm/save shortcut; manual static review
Remaining: Runtime verification on deployed env + any hotfix if FAIL
Next Action: Deploy this commit and test typed confirm/save on routine cards; report PASS/FAIL + screenshot/console.
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; othello_ui.html
Anchors:
- acceptRoutineSuggestion: othello_ui.html:6392
- buildRoutineReadyPanel: othello_ui.html:6553
- sendMessage: othello_ui.html:6711
Verification:
- Static: manual review (UI-only)
- Runtime: Not run (pending deploy)

diff --git a/othello_ui.html b/othello_ui.html
index a7c88e21..f0851c0b 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2791,7 +2791,9 @@
       mobileEditorPinned: false,
       mobileBackJustPressedAt: 0,
       creatingRoutine: false,
-      needsRoutineRefresh: false
+      needsRoutineRefresh: false,
+      pendingRoutineSuggestionId: null,
+      pendingRoutineAcceptFn: null
     };
     let devResetEnabled = false;
 
@@ -6382,6 +6384,53 @@
       }
     }
 
+    function clearPendingRoutineSuggestion() {
+      othelloState.pendingRoutineSuggestionId = null;
+      othelloState.pendingRoutineAcceptFn = null;
+    }
+
+    async function acceptRoutineSuggestion(suggestionId, uiRefs) {
+      if (!suggestionId) return false;
+      const confirmBtn = uiRefs && uiRefs.confirmBtn;
+      const statusEl = uiRefs && uiRefs.statusEl;
+      const actionsEl = uiRefs && uiRefs.actionsEl;
+      if (confirmBtn) confirmBtn.disabled = true;
+      if (statusEl) statusEl.textContent = "Saving...";
+      try {
+        const confirmPayload = { reason: "confirm" };
+        await v1Request(
+          `/v1/suggestions/${suggestionId}/accept`,
+          {
+            method: "POST",
+            headers: { "Content-Type": "application/json" },
+            credentials: "include",
+            body: JSON.stringify(confirmPayload)
+          },
+          "Confirm routine suggestion"
+        );
+        if (statusEl) {
+          statusEl.textContent = "Saved";
+          if (actionsEl) {
+            actionsEl.innerHTML = "";
+            actionsEl.appendChild(statusEl);
+          }
+        }
+        requestRoutineRefresh();
+        clearPendingRoutineSuggestion();
+        return true;
+      } catch (err) {
+        if (err && (err.status === 401 || err.status === 403)) {
+          await handleUnauthorized("routine-accept");
+          return false;
+        }
+        if (statusEl) {
+          statusEl.textContent = err && err.message ? err.message : "Save failed.";
+        }
+        if (confirmBtn) confirmBtn.disabled = false;
+        return false;
+      }
+    }
+
     function sendQuickReply(text) {
       if (!input) return;
       input.value = text;
@@ -6537,35 +6586,20 @@
       const status = document.createElement("div");
       status.className = "ux-goal-intent-status";
 
+      if (suggestionId) {
+        othelloState.pendingRoutineSuggestionId = suggestionId;
+        othelloState.pendingRoutineAcceptFn = () => acceptRoutineSuggestion(
+          suggestionId,
+          { confirmBtn, statusEl: status, actionsEl: actions }
+        );
+      }
+
       confirmBtn.addEventListener("click", async () => {
         if (!suggestionId) return;
-        confirmBtn.disabled = true;
-        status.textContent = "Saving...";
-        try {
-          const confirmPayload = { reason: "confirm" };
-          await v1Request(
-            `/v1/suggestions/${suggestionId}/accept`,
-            {
-              method: "POST",
-              headers: { "Content-Type": "application/json" },
-              credentials: "include",
-              body: JSON.stringify(confirmPayload)
-            },
-            "Confirm routine suggestion"
-          );
-          status.textContent = "Saved";
-          confirmBtn.disabled = true;
-          actions.innerHTML = "";
-          actions.appendChild(status);
-          requestRoutineRefresh();
-        } catch (err) {
-          if (err && (err.status === 401 || err.status === 403)) {
-            await handleUnauthorized("routine-accept");
-            return;
-          }
-          status.textContent = err && err.message ? err.message : "Save failed.";
-          confirmBtn.disabled = false;
-        }
+        await acceptRoutineSuggestion(
+          suggestionId,
+          { confirmBtn, statusEl: status, actionsEl: actions }
+        );
       });
 
       actions.appendChild(confirmBtn);
@@ -6686,6 +6720,20 @@
       input.focus();
       statusEl.textContent = "ThinkingÔÇª";
 
+      const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim();
+      if ((normalizedText === "confirm" || normalizedText === "save") &&
+          typeof othelloState.pendingRoutineAcceptFn === "function") {
+        statusEl.textContent = "Saving...";
+        try {
+          const accepted = await othelloState.pendingRoutineAcceptFn();
+          statusEl.textContent = accepted ? "Online" : "Error";
+        } catch (err) {
+          console.warn("[Othello UI] routine typed confirm failed:", err);
+          statusEl.textContent = "Error";
+        }
+        return;
+      }
+
       const goalIntentResolved = await resolveGoalIntentDecision(text);
       if (goalIntentResolved) {
         fetch(V1_MESSAGES_API, {

