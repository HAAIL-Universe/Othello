Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response; Add intent markers to UI; Show intent markers on first routine/goal turn via client hints; Add chat background gradient; Add focus mode bubble borders; Fix chat scrolling and focus glow reliability
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional; Added intent markers to UI; Implemented client-side intent hints for immediate marker rendering; Added chat background gradient; Added focus mode bubble borders; Fixed chat scrolling by changing overflow to overflow-x: hidden; Improved focus glow reliability by using getActiveFocusKind
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that the chat background is visible, scrolling works correctly, and message bubbles get a glow/border when a goal is active or a routine draft is pending.

diff --git a/othello_ui.html b/othello_ui.html
index 995253cd..66a75996 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -984,7 +984,7 @@
       padding-bottom: calc(var(--input-height) + max(var(--safe-bottom), 0.5rem));
       position: relative;
       isolation: isolate;
-      overflow: hidden;
+      overflow-x: hidden;
     }
 
     #chat-view::before {
@@ -992,6 +992,7 @@
       position: absolute;
       inset: 0;
       z-index: -2;
+      pointer-events: none;
       background: 
         radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
         radial-gradient(circle at 85% 30%, rgba(124, 58, 237, 0.08), transparent 25%),
@@ -1006,6 +1007,7 @@
       position: absolute;
       inset: -50%;
       z-index: -1;
+      pointer-events: none;
       background: repeating-radial-gradient(
         circle at 50% 50%,
         transparent 0,
@@ -5742,15 +5744,16 @@
       const log = document.getElementById("chat-log");
       if (!log) return;
       
-      const hasGoal = othelloState.activeGoalId !== null;
-      const hasRoutine = !!othelloState.pendingRoutineSuggestionId;
+      const kind = typeof getActiveFocusKind === "function" 
+        ? getActiveFocusKind(othelloState) 
+        : (othelloState.pendingRoutineSuggestionId ? "routine_draft" : (othelloState.activeGoalId ? "goal" : null));
       
       log.classList.remove("focus-mode", "focus-goal", "focus-routine");
       
-      if (hasGoal || hasRoutine) {
+      if (kind === "goal" || kind === "routine_draft") {
         log.classList.add("focus-mode");
-        if (hasGoal) log.classList.add("focus-goal");
-        if (hasRoutine) log.classList.add("focus-routine");
+        if (kind === "goal") log.classList.add("focus-goal");
+        if (kind === "routine_draft") log.classList.add("focus-routine");
       }
     }
