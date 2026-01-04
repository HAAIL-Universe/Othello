Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response; Add intent markers to UI; Show intent markers on first routine/goal turn via client hints; Add chat background gradient; Add focus mode bubble borders
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional; Added intent markers to UI; Implemented client-side intent hints for immediate marker rendering; Added chat background gradient; Added focus mode bubble borders
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that the chat background is visible and animated, and that message bubbles get a glow/border when a goal is active or a routine draft is pending.

diff --git a/othello_ui.html b/othello_ui.html
index 7bf87f8b..995253cd 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -982,6 +982,63 @@
     /* Chat View */
     #chat-view {
       padding-bottom: calc(var(--input-height) + max(var(--safe-bottom), 0.5rem));
+      position: relative;
+      isolation: isolate;
+      overflow: hidden;
+    }
+
+    #chat-view::before {
+      content: "";
+      position: absolute;
+      inset: 0;
+      z-index: -2;
+      background: 
+        radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
+        radial-gradient(circle at 85% 30%, rgba(124, 58, 237, 0.08), transparent 25%),
+        radial-gradient(circle at 50% 80%, rgba(56, 189, 248, 0.08), transparent 30%);
+      filter: blur(40px);
+      opacity: 0.6;
+      animation: driftBackground 20s ease-in-out infinite alternate;
+    }
+
+    #chat-view::after {
+      content: "";
+      position: absolute;
+      inset: -50%;
+      z-index: -1;
+      background: repeating-radial-gradient(
+        circle at 50% 50%,
+        transparent 0,
+        rgba(255, 255, 255, 0.015) 2px,
+        transparent 4px,
+        transparent 12px
+      );
+      opacity: 0.4;
+      animation: rippleEffect 30s linear infinite;
+      mix-blend-mode: overlay;
+    }
+
+    #chat-view .chat-log,
+    #chat-view #chat-placeholder {
+      position: relative;
+      z-index: 1;
+    }
+
+    @keyframes driftBackground {
+      0% { transform: scale(1); }
+      100% { transform: scale(1.1); }
+    }
+
+    @keyframes rippleEffect {
+      0% { transform: rotate(0deg); }
+      100% { transform: rotate(360deg); }
+    }
+
+    @media (prefers-reduced-motion: reduce) {
+      #chat-view::before,
+      #chat-view::after {
+        animation: none;
+      }
     }
 
     .chat-log {
@@ -1029,6 +1086,21 @@
       backdrop-filter: blur(12px);
     }
 
+    /* Focus Mode Bubbles */
+    #chat-log.focus-mode .bubble {
+      border: 1px solid rgba(125, 211, 252, 0.3);
+      box-shadow: 0 0 0 1px rgba(125, 211, 252, 0.1), 0 0 18px rgba(125, 211, 252, 0.15);
+      transition: border-color 0.3s ease, box-shadow 0.3s ease;
+    }
+    #chat-log.focus-goal .bubble {
+      border-color: rgba(99, 102, 241, 0.4);
+      box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.15), 0 0 20px rgba(99, 102, 241, 0.2);
+    }
+    #chat-log.focus-routine .bubble {
+      border-color: rgba(56, 189, 248, 0.4);
+      box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.15), 0 0 20px rgba(56, 189, 248, 0.2);
+    }
+
     .ux-goal-intent {
       outline: 2px solid var(--accent);
       box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.3), 0 10px 24px rgba(15, 23, 42, 0.45);
@@ -2607,6 +2679,7 @@
             }
             if (typeof loadChatHistory === 'function') {
               await loadChatHistory();
+              updateChatFocusClass();
             }
             if (typeof refreshInsightsCounts === 'function') {
               await refreshInsightsCounts();
@@ -5665,6 +5738,22 @@
     setMode(loadMode());
     refreshInsightsCounts();
 
+    function updateChatFocusClass() {
+      const log = document.getElementById("chat-log");
+      if (!log) return;
+      
+      const hasGoal = othelloState.activeGoalId !== null;
+      const hasRoutine = !!othelloState.pendingRoutineSuggestionId;
+      
+      log.classList.remove("focus-mode", "focus-goal", "focus-routine");
+      
+      if (hasGoal || hasRoutine) {
+        log.classList.add("focus-mode");
+        if (hasGoal) log.classList.add("focus-goal");
+        if (hasRoutine) log.classList.add("focus-routine");
+      }
+    }
+
     // ===== FOCUS RIBBON =====
     function updateFocusRibbon() {
       if (!focusRibbon) return;
@@ -6703,6 +6792,7 @@
     function clearPendingRoutineSuggestion() {
       othelloState.pendingRoutineSuggestionId = null;
       othelloState.pendingRoutineAcceptFn = null;
+      updateChatFocusClass();
     }
     function isElementVisible(el) {
       if (!el) return false;
@@ -7032,6 +7122,7 @@
           suggestionId,
           { confirmBtn, statusEl: status, actionsEl: actions }
         );
+        updateChatFocusClass();
       }
 
       confirmBtn.addEventListener("click", async () => {
@@ -7190,6 +7281,7 @@
       }
       othelloState.pendingGoalEdit = null;
       updateFocusRibbon();
+      updateChatFocusClass();
     }
 
     function bumpActiveGoalUpdates() {
