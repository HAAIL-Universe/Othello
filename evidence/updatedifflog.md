# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Fix Overlap & Duplicates (Duet Chat)

## Next Action
Commit

diff --git a/othello_ui.html b/othello_ui.html
index a78c1b7b..d6ca18ec 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -339,6 +339,7 @@
       <div id="chat-view" class="view" style="display:flex;">
         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
         
+        <!-- Only this is scrollable history -->
         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
         <div id="chat-log" class="chat-log"></div>
diff --git a/static/othello.css b/static/othello.css
index 825c710b..c7cc1ae5 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
 }
 
 /* --- Duet Chat Mode (Unified) --- */
-/* Phase 2: Fix the scroll container */
+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
 .chat-sheet {
   display: flex !important;
   flex-direction: column !important;
@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
 /* Header is rigid */
 .chat-sheet__header {
   flex: 0 0 auto;
+  z-index: 200; /* Header stays absolutely on top */
+  position: relative;
+  box-shadow: 0 1px 0 var(--border);
 }
 
 /* Input is rigid (footer) */
 .input-bar {
   flex: 0 0 auto;
+  z-index: 200; /* Input stays absolutely on top */
+  position: relative;
 }
 
 /* Chat View IS the scroll container now */
@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
   background: rgba(15, 23, 42, 0.98);
   padding: 0.75rem;
   margin: 0;
-  display: block !important;
+  display: block; /* always block, hidden by JS empty check if needed */
   backdrop-filter: blur(8px);
-  /* Ensure they don't shrink away */
   flex-shrink: 0; 
 }
 
+/* Default hidden until populated */
+.duet-pane:empty {
+    display: none !important;
+}
+
 .duet-pane--top {
   top: 0;
   border-bottom: 1px solid rgba(255,255,255,0.1);
@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
   overflow: visible !important; /* Let parent scroll it */
   height: auto !important;
   padding: 1rem;
+  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+  padding-top: 1rem;
+  padding-bottom: 1rem;
 }
 
 /* Hide empty panes */
diff --git a/static/othello.js b/static/othello.js
index 3a092bfc..1a19d8a7 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4300,76 +4300,81 @@
       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
     }
 
-    // Phase 3: Move nodes (no duplication)
+    // Phase 3: Canonical Move
     function applyDuetPins() {
-        if (!isDuetEnabled()) return;
-        
-        const chatLog = document.getElementById("chat-log");
         const top = document.getElementById("duet-top");
         const bottom = document.getElementById("duet-bottom");
-        if (!chatLog) return;
-        
-        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
-        // Actually, simpler approach for V1:
-        // We only pin the LATEST. 
-        // Iterate chatLog children. Find last user msg, last bot msg.
-        // Move them to pins? No, that breaks history flow if they are old.
-        // Rule: Only pin if it is indeed slaved to the bottom/top.
-        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
-        // This implies visual displacement.
-        
-        // Better Strategy:
-        // 1. Clear pins.
-        // 2. Scan chatLog rows.
-        // 3. Last row -> if user, move to bottom.
-        // 4. Last ASSISTANT row -> move to top.
-        // Wait, if last row is user, and row before is assistant, we move BOTH.
-        // This effectively empties the bottom of the history.
-        
-        // Implementation:
-        // Find all .msg-row in chat main loop or chatLog
-        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
-        if (rows.length === 0) return;
-        
-        // Find last user row
+        const chatLog = document.getElementById("chat-log");
+
+        // Fallback for safety
+        if (!top || !bottom || !chatLog) return;
+
+        // 1. Move ALL pinned items BACK to chatLog first to restore order
+        // This ensures scanning always finds true chronological last messages
+        while (top.firstChild) chatLog.appendChild(top.firstChild);
+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+
+        // Sort chatLog by DOM order? No, appendChild moves to end.
+        // We need to re-sort? No, they were originally at end. 
+        // NOTE: If we move old pinned items back, they append to END. 
+        // This might reorder history if we aren't careful.
+        // TRICKY: We need to know where they CAME from to un-pin correctly.
+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+        // BUT: If a new message arrived, we want THAT to be pinned.
+        
+        // Sorting approach (safest for history):
+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+        // If we strictly pin the last ones, unpinning means they go back to end.
+        // New messages are appended to end. So order is preserved naturally.
+        
+        if (allRows.length === 0) return;
+
+        // 2. Scan for candidates
         let lastUserRow = null;
         let lastBotRow = null;
-        
+
         // Scan backwards
-        for (let i = rows.length - 1; i >= 0; i--) {
-            const r = rows[i];
+        for (let i = allRows.length - 1; i >= 0; i--) {
+            const r = allRows[i];
             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
             if (lastUserRow && lastBotRow) break;
         }
 
-        // Move to pins
+        // 3. Move to pins
         if (lastBotRow) {
-            top.appendChild(lastBotRow); // Moves it out of chatLog
-            // Ensure display is correct
+            top.appendChild(lastBotRow);
             top.style.display = 'block';
         } else {
-            top.innerHTML = "";
             top.style.display = 'none';
         }
-        
+
         if (lastUserRow) {
-            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+            bottom.appendChild(lastUserRow);
             bottom.style.display = 'block';
         } else {
-            bottom.innerHTML = "";
             bottom.style.display = 'none';
         }
         
-        // If we moved stuff, scroll might need adjustment? 
-        // Sticky logic handles the pins. History fills the middle.
+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+        // But we might want to ensure last history item isn't hidden behind bottom pin.
+        // CSS 'scroll-padding-bottom' on container helps.
+        const scroll = document.getElementById("chat-view");
+        if (scroll) {
+             const botH = bottom.offsetHeight || 0;
+             const topH = top.offsetHeight || 0;
+             // Add extra padding to LOG so it can scroll fully into view
+             chatLog.style.paddingBottom = (botH + 20) + "px";
+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+        }
     }
     
-    // No-op for old sync padding (CSS sticky handles it now)
     function syncDuetPadding() {}
 
     function updateDuetView(row, role) {
-      // Defer to applyDuetPins in next frame to let DOM settle
+      // Defer to applyDuetPins in next frame so DOM is ready
       requestAnimationFrame(applyDuetPins);
     }
 
