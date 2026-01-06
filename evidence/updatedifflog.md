diff --git a/othello_ui.html b/othello_ui.html
index 25854a3f..26a0e185 100644
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
index 54e791ea..e2c944a9 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2053,3 +2053,74 @@ body.chat-open #global-chat-fab {
   outline: none;
   border-color: var(--accent);
 }
+
+/* KITT Scanner (Knight Rider) Effect */
+.kitt-scanner {
+  position: absolute;
+  top: 0;
+  left: 0;
+  right: 0;
+  height: 4px;
+  overflow: hidden;
+  border-radius: 4px 4px 0 0;
+  opacity: 0;
+  transition: opacity 0.3s ease;
+  pointer-events: none;
+  z-index: 50; /* Below controls */
+}
+
+.chat-sheet.is-thinking .kitt-scanner {
+  opacity: 1;
+}
+
+.kitt-scanner::before,
+.kitt-scanner::after {
+  content: '';
+  position: absolute;
+  top: 0;
+  bottom: 0;
+  width: 15%;
+  background: var(--accent, #e5e7eb); /* Fallback color */
+  box-shadow: 0 0 10px var(--accent, #e5e7eb), 0 0 5px var(--accent, #e5e7eb);
+  border-radius: 2px;
+  opacity: 0.8;
+  will-change: left, right;
+}
+
+.chat-sheet.is-thinking .kitt-scanner::before {
+  left: 50%;
+  transform: translateX(-50%);
+  animation: scanner-split-left 1.5s ease-in-out infinite alternate;
+}
+
+.chat-sheet.is-thinking .kitt-scanner::after {
+  right: 50%;
+  transform: translateX(50%);
+  animation: scanner-split-right 1.5s ease-in-out infinite alternate;
+}
+
+@keyframes scanner-split-left {
+  0% { left: 50%; width: 5%; opacity: 0.5; }
+  100% { left: 0%; width: 20%; opacity: 1; }
+}
+
+@keyframes scanner-split-right {
+  0% { right: 50%; width: 5%; opacity: 0.5; }
+  100% { right: 0%; width: 20%; opacity: 1; }
+}
+
+@media (prefers-reduced-motion: reduce) {
+  .chat-sheet.is-thinking .kitt-scanner::before,
+  .chat-sheet.is-thinking .kitt-scanner::after {
+    animation: none;
+    width: 100%;
+    left: 0;
+    right: 0;
+    opacity: 0.2;
+    transform: none;
+  }
+  .chat-sheet.is-thinking .kitt-scanner::after {
+    display: none;
+  }
+}
+
diff --git a/static/othello.js b/static/othello.js
index 7dd8aa7f..91abfd3d 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -8721,3 +8721,33 @@
 
     // ===== INITIALIZATION =====
     // Boot sequence (bootUnified) handles auth + data fetches
+
+// Phase 4: Hook scanner to existing status
+(function() {
+  const statusEl = document.getElementById('status');
+  // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
+  // We need to wait for DOM maybe? No, script is at end of body.
+  const chatSheet = document.querySelector('.chat-sheet');
+  
+  if (!statusEl || !chatSheet) {
+    console.warn('[Othello UI] Scanner init skipped: elements not found.');
+    return;
+  }
+
+  const observer = new MutationObserver(() => {
+    const text = (statusEl.textContent || '').toLowerCase();
+    // Signal 'is-thinking' if text contains active keywords and not just 'Online'/'Offline'
+    // Keywords based on codebase grep: Thinking, Saving, Updating, Dismissing, Adding, Preparing
+    const activeKeywords = ['thinking', 'working', 'saving', 'updating', 'dismissing', 'adding', 'preparing'];
+    const isThinking = activeKeywords.some(k => text.includes(k));
+    
+    if (isThinking) {
+      chatSheet.classList.add('is-thinking');
+    } else {
+      chatSheet.classList.remove('is-thinking');
+    }
+  });
+
+  observer.observe(statusEl, { childList: true, characterData: true, subtree: true });
+})();
+
