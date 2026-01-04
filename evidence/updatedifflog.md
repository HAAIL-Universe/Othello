Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response; Add intent markers to UI
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional; Added intent markers to UI
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that "🎯 Goal" and "🔁 Routine" markers appear in the bot message metadata when appropriate, without interfering with other UI elements.

diff --git a/othello_ui.html b/othello_ui.html
index 6242c4e7..589e3a78 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -5933,6 +5933,19 @@
       }
     }
 
+    function renderIntentMarkers(metaEl, markers) {
+      if (!metaEl || !markers || !markers.length) return;
+      const span = document.createElement("span");
+      span.className = "ux-intent-marker";
+      span.textContent = markers.join(" · ");
+      span.style.marginLeft = "0.45rem";
+      span.style.fontSize = "0.75rem";
+      span.style.opacity = "0.8";
+      span.style.userSelect = "none";
+      span.style.cursor = "default";
+      metaEl.appendChild(span);
+    }
+
     function addMessage(role, text, options = {}) {
       // Hide chat placeholder when first message appears
       const chatPlaceholder = document.getElementById("chat-placeholder");
@@ -5962,6 +5975,10 @@
         ? "You · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) + metaSuffix
         : "Othello · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
 
+      if (role === "bot" && options && Array.isArray(options.intentMarkers)) {
+        renderIntentMarkers(meta, options.intentMarkers);
+      }
+
       bubble.appendChild(meta);
 
       if (role === "bot" && othelloState.currentMode === "companion") {
@@ -7373,7 +7390,22 @@
         if (isRoutineReady) {
           replyText = "Confirm this routine?";
         }
-        const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId });
+
+        // Compute intent markers
+        const intentMarkers = [];
+        const hasGoalIntent = !!(
+          data.goal_intent_detected ||
+          data.goal_intent_suggestion ||
+          (Array.isArray(meta && meta.suggestions) && meta.suggestions.some(s => (s.type || "").toLowerCase() === "goal_intent"))
+        );
+        const hasRoutineIntent = !!(
+          (meta && typeof meta.intent === "string" && meta.intent.toLowerCase().startsWith("routine")) ||
+          (meta && meta.routine_suggestion_id)
+        );
+        if (hasGoalIntent) intentMarkers.push("🎯 Goal");
+        if (hasRoutineIntent) intentMarkers.push("🔁 Routine");
+
+        const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId, intentMarkers });
         try {
           await applyRoutineMeta(meta, botEntry, clientMessageId);
         } catch (err) {
