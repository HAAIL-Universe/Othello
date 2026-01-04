Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response; Add intent markers to UI; Show intent markers on first routine/goal turn via client hints
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional; Added intent markers to UI; Implemented client-side intent hints for immediate marker rendering
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that "🔁 Routine" appears on the FIRST bot reply when the user says "I need to add a routine", and that "🎯 Goal" appears for explicit goal statements.

diff --git a/othello_ui.html b/othello_ui.html
index 589e3a78..7bf87f8b 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2789,6 +2789,7 @@
       dismissedSuggestionIds: new Set(),
       goalIntentSuggestions: {},
       secondarySuggestionsByClientId: {},
+      intentHintsByClientId: {},
       mobileEditorPinned: false,
       mobileBackJustPressedAt: 0,
       creatingRoutine: false,
@@ -7197,6 +7198,25 @@
       othelloState.goalUpdateCounts[gid] = (othelloState.goalUpdateCounts[gid] || 0) + 1;
     }
 
+    function detectUserRoutineHint(text) {
+      if (!text) return false;
+      const t = text.toLowerCase();
+      const signals = ["routine", "remind me", "every day", "each day", "daily", "weekly", "habit", "alarm"];
+      return signals.some(s => t.includes(s));
+    }
+
+    function detectUserGoalHint(text) {
+      if (!text) return false;
+      const t = text.toLowerCase();
+      // Disqualify questions
+      if (t.includes("?")) return false;
+      const qWords = ["what", "how", "why", "when", "where", "who", "can", "should", "do", "is", "are"];
+      if (qWords.some(w => t.startsWith(w + " ") || t === w)) return false;
+      
+      const signals = ["goal:", "my goal is", "new goal", "i want to", "i'm going to", "i will", "working towards"];
+      return signals.some(s => t.includes(s));
+    }
+
     function beginSendUI(options = {}) {
       const previousStatus = statusEl ? statusEl.textContent : "", label = options.label || "Thinking…", disableSend = options.disableSend !== false;
       if (disableSend && sendBtn) sendBtn.disabled = true;
@@ -7219,6 +7239,13 @@
       const pendingEdit = othelloState.pendingGoalEdit;
       const metaNote = pendingEdit ? `Editing goal #${pendingEdit.goal_id}` : "";
       const clientMessageId = generateClientMessageId();
+      
+      // Capture intent hints immediately
+      const hint = { goal: detectUserGoalHint(text), routine: detectUserRoutineHint(text) };
+      if (hint.goal || hint.routine) {
+        othelloState.intentHintsByClientId[clientMessageId] = hint;
+      }
+
       const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim(), isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
       addMessage("user", text, { metaNote, clientMessageId });
       input.value = "";
@@ -7393,19 +7420,31 @@
 
         // Compute intent markers
         const intentMarkers = [];
-        const hasGoalIntent = !!(
+        const hint = othelloState.intentHintsByClientId[clientMessageId] || {};
+        
+        const hasGoalIntentFromServer = !!(
           data.goal_intent_detected ||
           data.goal_intent_suggestion ||
           (Array.isArray(meta && meta.suggestions) && meta.suggestions.some(s => (s.type || "").toLowerCase() === "goal_intent"))
         );
-        const hasRoutineIntent = !!(
+        const hasRoutineIntentFromServer = !!(
           (meta && typeof meta.intent === "string" && meta.intent.toLowerCase().startsWith("routine")) ||
           (meta && meta.routine_suggestion_id)
         );
+
+        const hasGoalIntent = hasGoalIntentFromServer || hint.goal;
+        const hasRoutineIntent = hasRoutineIntentFromServer || hint.routine;
+
         if (hasGoalIntent) intentMarkers.push("🎯 Goal");
         if (hasRoutineIntent) intentMarkers.push("🔁 Routine");
 
         const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId, intentMarkers });
+        
+        // Clear hint to prevent reuse
+        if (othelloState.intentHintsByClientId[clientMessageId]) {
+          delete othelloState.intentHintsByClientId[clientMessageId];
+        }
+
         try {
           await applyRoutineMeta(meta, botEntry, clientMessageId);
         } catch (err) {
