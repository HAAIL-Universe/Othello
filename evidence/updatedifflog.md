# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 1: Scanner UI Element
- [x] Phase 2: CSS Animation
- [x] Phase 3: JS Logic Hook
- [x] Integration with sendMessage

## Next Action
Stop and commit.

## Full Diff
```diff
diff --git a/othello_ui.html b/othello_ui.html
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -330,6 +330,7 @@
   <div id="global-chat-overlay" class="global-chat-overlay">
     <div class="chat-sheet">
       <div class="chat-sheet__header">
+        <div class="kitt-scanner" aria-hidden="true"></div>
         <select id="chat-context-selector" class="chat-context-selector">
           <option value="companion">Companion Chat</option>
           <option value="planner">Daily Plan Engine</option>

diff --git a/static/othello.css b/static/othello.css
--- a/static/othello.css
+++ b/static/othello.css
@@ -1943,6 +1943,63 @@
   flex-shrink: 0; /* Don't shrink header */
 }
 
+/* KITT Scanner Effect */
+.chat-sheet { 
+  --kitt-h: 4px; 
+  --kitt-dot: 18px; 
+  --kitt-pad: 6px; 
+  --kitt-ms: 900ms; 
+}
+
+.kitt-scanner {
+  position: absolute;
+  left: 0; 
+  right: 0; 
+  top: 0; /* Top of header */
+  height: var(--kitt-h);
+  border-radius: 999px;
+  overflow: hidden;
+  opacity: 0;
+  transition: opacity 120ms ease;
+  pointer-events: none;
+  z-index: 102; /* Above controls if overlapping slightly, but top focused */
+}
+
+.chat-sheet.is-thinking .kitt-scanner { 
+  opacity: 1; 
+}
+
+.kitt-scanner::before,
+.kitt-scanner::after {
+  content: "";
+  position: absolute;
+  top: 0;
+  width: var(--kitt-dot);
+  height: 100%;
+  border-radius: 999px;
+  background: linear-gradient(90deg, transparent, rgba(255,80,80,.95), transparent);
+  box-shadow: 0 0 10px rgba(255,60,60,.85), 0 0 22px rgba(255,60,60,.45);
+}
+
+@keyframes kitt-left {
+  0%, 100% { left: 50%; transform: translateX(-50%); }
+  50% { left: calc(var(--kitt-pad) + var(--kitt-dot) / 2); transform: translateX(-50%); }
+}
+
+@keyframes kitt-right {
+  0%, 100% { left: 50%; transform: translateX(-50%); }
+  50% { left: calc(100% - var(--kitt-pad) - var(--kitt-dot) / 2); transform: translateX(-50%); }
+}
+
+.chat-sheet.is-thinking .kitt-scanner::before { animation: kitt-left var(--kitt-ms) ease-in-out infinite; }
+.chat-sheet.is-thinking .kitt-scanner::after  { animation: kitt-right var(--kitt-ms) ease-in-out infinite; }
+
+@media (prefers-reduced-motion: reduce) {
+  .chat-sheet.is-thinking .kitt-scanner::before,
+  .chat-sheet.is-thinking .kitt-scanner::after { animation: none; }
+  .chat-sheet.is-thinking .kitt-scanner { opacity: 1; }
+}
+
 .chat-back-btn {
   background: none;
   border: none;

diff --git a/static/othello.js b/static/othello.js
--- a/static/othello.js
+++ b/static/othello.js
@@ -5678,6 +5678,24 @@
       }
     }
 
+    // KITT Scanner Logic
+    let pendingChatRequests = 0;
+    function setChatThinking(isThinking) {
+        const sheet = document.querySelector('.chat-sheet');
+        if(sheet) {
+            if(isThinking) sheet.classList.add('is-thinking');
+            else sheet.classList.remove('is-thinking');
+        }
+    }
+    function beginThinking() {
+        pendingChatRequests++;
+        setChatThinking(true);
+    }
+    function endThinking() {
+        pendingChatRequests = Math.max(0, pendingChatRequests - 1);
+        if (pendingChatRequests === 0) setChatThinking(false);
+    }
+
     async function sendMessage(overrideText = null, extraData = {}) {
       // 1) Robust String Safety & Diagnostic
       let override = overrideText;
@@ -5897,12 +5915,20 @@
             ...extraData
         };
         console.debug("[Othello UI] Sending /api/message payload:", payload);
-        const res = await fetch(API, {
-          method: "POST",
-          headers: {"Content-Type": "application/json"},
-          credentials: "include",
-          body: JSON.stringify(payload)
-        });
+        
+        beginThinking();
+        let res;
+        try {
+            res = await fetch(API, {
+              method: "POST",
+              headers: {"Content-Type": "application/json"},
+              credentials: "include",
+              body: JSON.stringify(payload)
+            });
+        } catch (err) {
+            endThinking();
+            throw err;
+        }
 
         console.log("[Othello UI] /api/message status", res.status);
 
@@ -5935,10 +5961,12 @@
             addMessage("bot", `[Error ${res.status}]: Unable to process your message. Please try again.`);
           }
           statusEl.textContent = "Error";
+          endThinking();
           return;
         }
 
         const data = await res.json();
+        endThinking();
         
         // Phase 22.3: Handle UI Actions from backend (Auto-Focus)
```
