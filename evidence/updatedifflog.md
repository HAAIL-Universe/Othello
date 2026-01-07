# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix
- [x] Phase 6: Auth Fix
- [x] Phase 8: Duet History Constraints (Restored)
- [x] Phase 9: History Bar Repositioning (Restored)

## Next Action
Stop and commit.

diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index 7aae5e35..6a483c3b 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -2,209 +2,17309 @@
 
 ## Todo Ledger
 Completed:
-- [x] Fix Overlap & Duplicates (Duet Chat)
+- [x] Phase 0: Evidence + Location
+- [x] Phase 1: Server: Pending Draft Storage
+- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
+- [x] Phase 3: Quality Gates
+- [x] Phase 5: Runtime Fix
+- [x] Phase 6: Auth Fix
+- [x] Phase 8: Duet History Constraints
+- [x] Phase 9: History Bar Repositioning
+- [x] Phase 12: Split Layout Refactor
 
 ## Next Action
-Commit
+Stop and commit.
 
+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+index 7aae5e35..e569d4f0 100644
+--- a/evidence/updatedifflog.md
++++ b/evidence/updatedifflog.md
+@@ -2,123 +2,16463 @@
+ 
+ ## Todo Ledger
+ Completed:
+-- [x] Fix Overlap & Duplicates (Duet Chat)
++- [x] Phase 0: Evidence + Location
++- [x] Phase 1: Server: Pending Draft Storage
++- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
++- [x] Phase 3: Quality Gates
++- [x] Phase 5: Runtime Fix
++- [x] Phase 6: Auth Fix
++- [x] Phase 8: Duet History Constraints
++- [x] Phase 9: History Bar Repositioning
+ 
+ ## Next Action
+-Commit
++Stop and commit.
+ 
++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++index 7aae5e35..ef6ad871 100644
++--- a/evidence/updatedifflog.md
+++++ b/evidence/updatedifflog.md
++@@ -2,123 +2,15843 @@
++ 
++ ## Todo Ledger
++ Completed:
++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++- [x] Phase 0: Evidence + Location
+++- [x] Phase 1: Server: Pending Draft Storage
+++- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
+++- [x] Phase 3: Quality Gates
+++- [x] Phase 5: Runtime Fix
+++- [x] Phase 6: Auth Fix
+++- [x] Phase 8: Duet History Constraints
++ 
++ ## Next Action
++-Commit
+++Stop and commit.
++ 
+++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++index 7aae5e35..bf172440 100644
+++--- a/evidence/updatedifflog.md
++++++ b/evidence/updatedifflog.md
+++@@ -2,123 +2,15225 @@
+++ 
+++ ## Todo Ledger
+++ Completed:
+++-- [x] Fix Overlap & Duplicates (Duet Chat)
++++- [x] Phase 7: Layout Fixes (Padding, Hiding History)
+++ 
+++ ## Next Action
+++-Commit
++++Fill next action.
+++ 
++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++++index 7aae5e35..92e55a1d 100644
++++--- a/evidence/updatedifflog.md
+++++++ b/evidence/updatedifflog.md
++++@@ -1,124 +1,14670 @@
++++-# Cycle Status: COMPLETE
+++++# Cycle Status: IN_PROGRESS
++++ 
++++ ## Todo Ledger
++++-Completed:
++++-- [x] Fix Overlap & Duplicates (Duet Chat)
++++ 
++++ ## Next Action
++++-Commit
+++++Fill next action.
++++ 
+++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++++index 7aae5e35..7d7e71a1 100644
+++++--- a/evidence/updatedifflog.md
++++++++ b/evidence/updatedifflog.md
+++++@@ -1,124 +1,14152 @@
+++++-# Cycle Status: COMPLETE
++++++# Cycle Status: IN_PROGRESS
+++++ 
+++++ ## Todo Ledger
+++++-Completed:
+++++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++++ 
+++++ ## Next Action
+++++-Commit
++++++Fill next action.
+++++ 
++++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++++++index 7aae5e35..2dc789b7 100644
++++++--- a/evidence/updatedifflog.md
+++++++++ b/evidence/updatedifflog.md
++++++@@ -1,77 +1,13561 @@
++++++-# Cycle Status: COMPLETE
+++++++# Cycle Status: IN_PROGRESS
++++++ 
++++++ ## Todo Ledger
++++++-Completed:
++++++-- [x] Fix Overlap & Duplicates (Duet Chat)
++++++ 
++++++ ## Next Action
++++++-Commit
+++++++Fill next action.
++++++ 
+++++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++++++index 7aae5e35..90e8d157 100644
+++++++--- a/evidence/updatedifflog.md
++++++++++ b/evidence/updatedifflog.md
+++++++@@ -1,210 +1,6716 @@
+++++++-# Cycle Status: COMPLETE
+++++++-
+++++++-## Todo Ledger
+++++++-Completed:
+++++++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++-
+++++++-## Next Action
+++++++-Commit
+++++++-
+++++++-diff --git a/othello_ui.html b/othello_ui.html
+++++++-index a78c1b7b..d6ca18ec 100644
+++++++---- a/othello_ui.html
+++++++-+++ b/othello_ui.html
+++++++-@@ -339,6 +339,7 @@
+++++++-       <div id="chat-view" class="view" style="display:flex;">
+++++++-         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++-         
+++++++-+        <!-- Only this is scrollable history -->
+++++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++-         <div id="chat-log" class="chat-log"></div>
+++++++-diff --git a/static/othello.css b/static/othello.css
+++++++-index 825c710b..c7cc1ae5 100644
+++++++---- a/static/othello.css
+++++++-+++ b/static/othello.css
+++++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++- }
+++++++- 
+++++++- /* --- Duet Chat Mode (Unified) --- */
+++++++--/* Phase 2: Fix the scroll container */
+++++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++- .chat-sheet {
+++++++-   display: flex !important;
+++++++-   flex-direction: column !important;
+++++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++- /* Header is rigid */
+++++++- .chat-sheet__header {
+++++++-   flex: 0 0 auto;
+++++++-+  z-index: 200; /* Header stays absolutely on top */
+++++++-+  position: relative;
+++++++-+  box-shadow: 0 1px 0 var(--border);
+++++++- }
+++++++- 
+++++++- /* Input is rigid (footer) */
+++++++- .input-bar {
+++++++-   flex: 0 0 auto;
+++++++-+  z-index: 200; /* Input stays absolutely on top */
+++++++-+  position: relative;
+++++++- }
+++++++- 
+++++++- /* Chat View IS the scroll container now */
+++++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++-   background: rgba(15, 23, 42, 0.98);
+++++++-   padding: 0.75rem;
+++++++-   margin: 0;
+++++++--  display: block !important;
+++++++-+  display: block; /* always block, hidden by JS empty check if needed */
+++++++-   backdrop-filter: blur(8px);
+++++++--  /* Ensure they don't shrink away */
+++++++-   flex-shrink: 0; 
+++++++- }
+++++++- 
+++++++-+/* Default hidden until populated */
+++++++-+.duet-pane:empty {
+++++++-+    display: none !important;
+++++++-+}
+++++++-+
+++++++- .duet-pane--top {
+++++++-   top: 0;
+++++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++-   overflow: visible !important; /* Let parent scroll it */
+++++++-   height: auto !important;
+++++++-   padding: 1rem;
+++++++-+  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++-+  padding-top: 1rem;
+++++++-+  padding-bottom: 1rem;
+++++++- }
+++++++- 
+++++++- /* Hide empty panes */
+++++++-diff --git a/static/othello.js b/static/othello.js
+++++++-index 3a092bfc..1a19d8a7 100644
+++++++---- a/static/othello.js
+++++++-+++ b/static/othello.js
+++++++-@@ -4300,76 +4300,81 @@
+++++++-       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++-     }
+++++++- 
+++++++--    // Phase 3: Move nodes (no duplication)
+++++++-+    // Phase 3: Canonical Move
+++++++-     function applyDuetPins() {
+++++++--        if (!isDuetEnabled()) return;
+++++++--        
+++++++--        const chatLog = document.getElementById("chat-log");
+++++++-         const top = document.getElementById("duet-top");
+++++++-         const bottom = document.getElementById("duet-bottom");
+++++++--        if (!chatLog) return;
+++++++--        
+++++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++--        // Actually, simpler approach for V1:
+++++++--        // We only pin the LATEST. 
+++++++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++--        // Move them to pins? No, that breaks history flow if they are old.
+++++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++--        // This implies visual displacement.
+++++++--        
+++++++--        // Better Strategy:
+++++++--        // 1. Clear pins.
+++++++--        // 2. Scan chatLog rows.
+++++++--        // 3. Last row -> if user, move to bottom.
+++++++--        // 4. Last ASSISTANT row -> move to top.
+++++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++--        // This effectively empties the bottom of the history.
+++++++--        
+++++++--        // Implementation:
+++++++--        // Find all .msg-row in chat main loop or chatLog
+++++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++--        if (rows.length === 0) return;
+++++++--        
+++++++--        // Find last user row
+++++++-+        const chatLog = document.getElementById("chat-log");
+++++++-+
+++++++-+        // Fallback for safety
+++++++-+        if (!top || !bottom || !chatLog) return;
+++++++-+
+++++++-+        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++-+        // This ensures scanning always finds true chronological last messages
+++++++-+        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++-+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++-+
+++++++-+        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++-+        // We need to re-sort? No, they were originally at end. 
+++++++-+        // NOTE: If we move old pinned items back, they append to END. 
+++++++-+        // This might reorder history if we aren't careful.
+++++++-+        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++-+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++-+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++-+        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++-+        
+++++++-+        // Sorting approach (safest for history):
+++++++-+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++-+        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++-+        // New messages are appended to end. So order is preserved naturally.
+++++++-+        
+++++++-+        if (allRows.length === 0) return;
+++++++-+
+++++++-+        // 2. Scan for candidates
+++++++-         let lastUserRow = null;
+++++++-         let lastBotRow = null;
+++++++--        
+++++++-+
+++++++-         // Scan backwards
+++++++--        for (let i = rows.length - 1; i >= 0; i--) {
+++++++--            const r = rows[i];
+++++++-+        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++-+            const r = allRows[i];
+++++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++-+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++-             if (lastUserRow && lastBotRow) break;
+++++++-         }
+++++++- 
+++++++--        // Move to pins
+++++++-+        // 3. Move to pins
+++++++-         if (lastBotRow) {
+++++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++--            // Ensure display is correct
+++++++-+            top.appendChild(lastBotRow);
+++++++-             top.style.display = 'block';
+++++++-         } else {
+++++++--            top.innerHTML = "";
+++++++-             top.style.display = 'none';
+++++++-         }
+++++++--        
+++++++-+
+++++++-         if (lastUserRow) {
+++++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++-+            bottom.appendChild(lastUserRow);
+++++++-             bottom.style.display = 'block';
+++++++-         } else {
+++++++--            bottom.innerHTML = "";
+++++++-             bottom.style.display = 'none';
+++++++-         }
+++++++-         
+++++++--        // If we moved stuff, scroll might need adjustment? 
+++++++--        // Sticky logic handles the pins. History fills the middle.
+++++++-+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++-+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++-+        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++-+        // CSS 'scroll-padding-bottom' on container helps.
+++++++-+        const scroll = document.getElementById("chat-view");
+++++++-+        if (scroll) {
+++++++-+             const botH = bottom.offsetHeight || 0;
+++++++-+             const topH = top.offsetHeight || 0;
+++++++-+             // Add extra padding to LOG so it can scroll fully into view
+++++++-+             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++-+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++-+        }
+++++++-     }
+++++++-     
+++++++--    // No-op for old sync padding (CSS sticky handles it now)
+++++++-     function syncDuetPadding() {}
+++++++- 
+++++++-     function updateDuetView(row, role) {
+++++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++++-+      // Defer to applyDuetPins in next frame so DOM is ready
+++++++-       requestAnimationFrame(applyDuetPins);
+++++++-     }
+++++++- 
++++++++# Cycle Status: COMPLETE
++++++++
++++++++## Todo Ledger
++++++++Completed:
++++++++- [x] Fix Overlap & Duplicates (Duet Chat)
++++++++
++++++++## Next Action
++++++++Commit
++++++++
++++++++diff --git a/othello_ui.html b/othello_ui.html
++++++++index a78c1b7b..d6ca18ec 100644
++++++++--- a/othello_ui.html
+++++++++++ b/othello_ui.html
++++++++@@ -339,6 +339,7 @@
++++++++       <div id="chat-view" class="view" style="display:flex;">
++++++++         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
++++++++         
+++++++++        <!-- Only this is scrollable history -->
++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++++++         <div id="chat-log" class="chat-log"></div>
++++++++diff --git a/static/othello.css b/static/othello.css
++++++++index 825c710b..c7cc1ae5 100644
++++++++--- a/static/othello.css
+++++++++++ b/static/othello.css
++++++++@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
++++++++ }
++++++++ 
++++++++ /* --- Duet Chat Mode (Unified) --- */
++++++++-/* Phase 2: Fix the scroll container */
+++++++++/* Phase 2b: Fix the scroll container + Z-Index Stacking */
++++++++ .chat-sheet {
++++++++   display: flex !important;
++++++++   flex-direction: column !important;
++++++++@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
++++++++ /* Header is rigid */
++++++++ .chat-sheet__header {
++++++++   flex: 0 0 auto;
+++++++++  z-index: 200; /* Header stays absolutely on top */
+++++++++  position: relative;
+++++++++  box-shadow: 0 1px 0 var(--border);
++++++++ }
++++++++ 
++++++++ /* Input is rigid (footer) */
++++++++ .input-bar {
++++++++   flex: 0 0 auto;
+++++++++  z-index: 200; /* Input stays absolutely on top */
+++++++++  position: relative;
++++++++ }
++++++++ 
++++++++ /* Chat View IS the scroll container now */
++++++++@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
++++++++   background: rgba(15, 23, 42, 0.98);
++++++++   padding: 0.75rem;
++++++++   margin: 0;
++++++++-  display: block !important;
+++++++++  display: block; /* always block, hidden by JS empty check if needed */
++++++++   backdrop-filter: blur(8px);
++++++++-  /* Ensure they don't shrink away */
++++++++   flex-shrink: 0; 
++++++++ }
++++++++ 
+++++++++/* Default hidden until populated */
+++++++++.duet-pane:empty {
+++++++++    display: none !important;
+++++++++}
+++++++++
++++++++ .duet-pane--top {
++++++++   top: 0;
++++++++   border-bottom: 1px solid rgba(255,255,255,0.1);
++++++++@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
++++++++   overflow: visible !important; /* Let parent scroll it */
++++++++   height: auto !important;
++++++++   padding: 1rem;
+++++++++  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++++  padding-top: 1rem;
+++++++++  padding-bottom: 1rem;
++++++++ }
++++++++ 
++++++++ /* Hide empty panes */
++++++++diff --git a/static/othello.js b/static/othello.js
++++++++index 3a092bfc..1a19d8a7 100644
++++++++--- a/static/othello.js
+++++++++++ b/static/othello.js
++++++++@@ -4300,76 +4300,81 @@
++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
++++++++     }
++++++++ 
++++++++-    // Phase 3: Move nodes (no duplication)
+++++++++    // Phase 3: Canonical Move
++++++++     function applyDuetPins() {
++++++++-        if (!isDuetEnabled()) return;
++++++++-        
++++++++-        const chatLog = document.getElementById("chat-log");
++++++++         const top = document.getElementById("duet-top");
++++++++         const bottom = document.getElementById("duet-bottom");
++++++++-        if (!chatLog) return;
++++++++-        
++++++++-        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
++++++++-        // Actually, simpler approach for V1:
++++++++-        // We only pin the LATEST. 
++++++++-        // Iterate chatLog children. Find last user msg, last bot msg.
++++++++-        // Move them to pins? No, that breaks history flow if they are old.
++++++++-        // Rule: Only pin if it is indeed slaved to the bottom/top.
++++++++-        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
++++++++-        // This implies visual displacement.
++++++++-        
++++++++-        // Better Strategy:
++++++++-        // 1. Clear pins.
++++++++-        // 2. Scan chatLog rows.
++++++++-        // 3. Last row -> if user, move to bottom.
++++++++-        // 4. Last ASSISTANT row -> move to top.
++++++++-        // Wait, if last row is user, and row before is assistant, we move BOTH.
++++++++-        // This effectively empties the bottom of the history.
++++++++-        
++++++++-        // Implementation:
++++++++-        // Find all .msg-row in chat main loop or chatLog
++++++++-        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
++++++++-        if (rows.length === 0) return;
++++++++-        
++++++++-        // Find last user row
+++++++++        const chatLog = document.getElementById("chat-log");
+++++++++
+++++++++        // Fallback for safety
+++++++++        if (!top || !bottom || !chatLog) return;
+++++++++
+++++++++        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++++        // This ensures scanning always finds true chronological last messages
+++++++++        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++++        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++++
+++++++++        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++++        // We need to re-sort? No, they were originally at end. 
+++++++++        // NOTE: If we move old pinned items back, they append to END. 
+++++++++        // This might reorder history if we aren't careful.
+++++++++        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++++        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++++        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++++        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++++        
+++++++++        // Sorting approach (safest for history):
+++++++++        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++++        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++++        // New messages are appended to end. So order is preserved naturally.
+++++++++        
+++++++++        if (allRows.length === 0) return;
+++++++++
+++++++++        // 2. Scan for candidates
++++++++         let lastUserRow = null;
++++++++         let lastBotRow = null;
++++++++-        
+++++++++
++++++++         // Scan backwards
++++++++-        for (let i = rows.length - 1; i >= 0; i--) {
++++++++-            const r = rows[i];
+++++++++        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++++            const r = allRows[i];
++++++++             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++++            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
++++++++             if (lastUserRow && lastBotRow) break;
++++++++         }
++++++++ 
++++++++-        // Move to pins
+++++++++        // 3. Move to pins
++++++++         if (lastBotRow) {
++++++++-            top.appendChild(lastBotRow); // Moves it out of chatLog
++++++++-            // Ensure display is correct
+++++++++            top.appendChild(lastBotRow);
++++++++             top.style.display = 'block';
++++++++         } else {
++++++++-            top.innerHTML = "";
++++++++             top.style.display = 'none';
++++++++         }
++++++++-        
+++++++++
++++++++         if (lastUserRow) {
++++++++-            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++++            bottom.appendChild(lastUserRow);
++++++++             bottom.style.display = 'block';
++++++++         } else {
++++++++-            bottom.innerHTML = "";
++++++++             bottom.style.display = 'none';
++++++++         }
++++++++         
++++++++-        // If we moved stuff, scroll might need adjustment? 
++++++++-        // Sticky logic handles the pins. History fills the middle.
+++++++++        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++++        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++++        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++++        // CSS 'scroll-padding-bottom' on container helps.
+++++++++        const scroll = document.getElementById("chat-view");
+++++++++        if (scroll) {
+++++++++             const botH = bottom.offsetHeight || 0;
+++++++++             const topH = top.offsetHeight || 0;
+++++++++             // Add extra padding to LOG so it can scroll fully into view
+++++++++             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++++             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++++        }
++++++++     }
++++++++     
++++++++-    // No-op for old sync padding (CSS sticky handles it now)
++++++++     function syncDuetPadding() {}
++++++++ 
++++++++     function updateDuetView(row, role) {
++++++++-      // Defer to applyDuetPins in next frame to let DOM settle
+++++++++      // Defer to applyDuetPins in next frame so DOM is ready
++++++++       requestAnimationFrame(applyDuetPins);
++++++++     }
++++++++ 
++++++++\n# Refactor: 3-Zone Layout\n
+++++++
++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++index 9b1f8845..382eeb57 100644
+++++++
++++++++--- a/static/othello.css
+++++++
+++++++++++ b/static/othello.css
+++++++
++++++++@@ -2203,65 +2203,64 @@ body.chat-open #global-chat-fab {
+++++++
++++++++   position: relative;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++-/* Chat View IS the scroll container now */
+++++++
+++++++++/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++++
++++++++ #chat-view {
+++++++
++++++++   display: flex !important;
+++++++
++++++++   flex-direction: column;
+++++++
++++++++-  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++++
+++++++++  flex: 1 1 0;
+++++++
++++++++   min-height: 0;
+++++++
++++++++-  overflow-y: auto !important; /* The ONLY scrollbar */
+++++++
++++++++-  overflow-x: hidden;
+++++++
+++++++++  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
++++++++   position: relative;
+++++++
++++++++-  padding: 0; /* Strict */
+++++++
+++++++++  padding: 0;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++-/* Duet Panes (Sticky) - Transparent Rails */
+++++++
+++++++++/* Duet Panes (Static Flex Items) */
+++++++
++++++++ .duet-pane {
+++++++
++++++++-  position: sticky;
+++++++
++++++++-  z-index: 100; /* Must beat messages */
+++++++
++++++++-  background: transparent; /* Transparent background */
+++++++
+++++++++  position: static; /* No longer sticky */
+++++++
+++++++++  flex: 0 0 auto; /* Rigid height based on content */
+++++++
+++++++++  z-index: 100;
+++++++
+++++++++  background: transparent;
+++++++
++++++++   padding: 0.75rem;
+++++++
++++++++   margin: 0;
+++++++
++++++++-  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++-  flex-shrink: 0;
+++++++
++++++++-  pointer-events: none; /* Let clicks pass through empty space */
+++++++
+++++++++  display: block;
+++++++
+++++++++  pointer-events: none;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++-/* Re-enable pointer events on children (the bubbles) */
+++++++
++++++++-.duet-pane > * {
+++++++
++++++++-  pointer-events: auto;
+++++++
++++++++-}
+++++++
+++++++++.duet-pane > * { pointer-events: auto; }
+++++++
+++++++++.duet-pane:empty { display: none !important; }
+++++++
++++++++ 
+++++++
++++++++-/* Default hidden until populated */
+++++++
++++++++-.duet-pane:empty {
+++++++
++++++++-    display: none !important;
+++++++
+++++++++/* Chat Log (Middle Scrollable History) */
+++++++
+++++++++#chat-log {
+++++++
+++++++++  display: flex !important;
+++++++
+++++++++  flex-direction: column;
+++++++
+++++++++  flex: 1 1 0; /* Takes all remaining space */
+++++++
+++++++++  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
+++++++++  min-height: 0;
+++++++
+++++++++  height: auto !important;
+++++++
+++++++++  padding: 1rem;
+++++++
+++++++++  padding-top: 0.5rem;
+++++++
+++++++++  padding-bottom: 0.5rem;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
+++++++++/* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++ .duet-pane--top {
+++++++
++++++++-  top: 0;
+++++++
++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++-  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++-  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++++
+++++++++  order: 1;
+++++++
+++++++++  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
+++++++++}
+++++++
+++++++++
+++++++
+++++++++#chat-log {
+++++++
+++++++++  order: 2; /* Middle */
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ .duet-pane--bottom {
+++++++
++++++++-  bottom: 0;
+++++++
++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++-  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++-  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++++
+++++++++  order: 3;
+++++++
+++++++++  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++-/* Chat Log (History Flow) */
+++++++
++++++++-#chat-log {
+++++++
++++++++-  display: flex !important;
+++++++
++++++++-  flex-direction: column;
+++++++
++++++++-  flex: 1; /* occupy space between pins */
+++++++
++++++++-  overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++-  height: auto !important;
+++++++
++++++++-  padding: 1rem;
+++++++
++++++++-  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++-  padding-top: 1rem;
+++++++
++++++++-  padding-bottom: 1rem;
+++++++
+++++++++/* Ensure empty slots don't take space/border */
+++++++
+++++++++.duet-pane:empty {
+++++++
+++++++++    display: none !important;
+++++++
+++++++++    border: none !important;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ /* Hide empty panes */
+++++++
++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++index 1a19d8a7..2f438318 100644
+++++++
++++++++--- a/static/othello.js
+++++++
+++++++++++ b/static/othello.js
+++++++
++++++++@@ -4300,7 +4300,7 @@
+++++++
++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++-    // Phase 3: Canonical Move
+++++++
+++++++++    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++     function applyDuetPins() {
+++++++
++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++@@ -4308,67 +4308,79 @@
+++++++
++++++++ 
+++++++
++++++++         // Fallback for safety
+++++++
++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++-
+++++++
++++++++-        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++-        // This ensures scanning always finds true chronological last messages
+++++++
++++++++-        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++-        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++-
+++++++
++++++++-        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++-        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++-        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++-        // This might reorder history if we aren't careful.
+++++++
++++++++-        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++-        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++-        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++-        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++-        
+++++++
++++++++-        // Sorting approach (safest for history):
+++++++
++++++++-        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++-        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++-        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++         
+++++++
+++++++++        // 1. Gather ALL message rows from all containers
+++++++
+++++++++        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
+++++++++        const allRows = [
+++++++
+++++++++            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
+++++++++            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
+++++++++            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
+++++++++        ];
+++++++
+++++++++
+++++++
++++++++         if (allRows.length === 0) return;
+++++++
++++++++ 
+++++++
++++++++-        // 2. Scan for candidates
+++++++
++++++++-        let lastUserRow = null;
+++++++
++++++++-        let lastBotRow = null;
+++++++
+++++++++        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
+++++++++        allRows.sort((a, b) => {
+++++++
+++++++++            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
+++++++++            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
+++++++++            if (seqA !== seqB) return seqA - seqB;
+++++++
+++++++++            
+++++++
+++++++++            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
+++++++++            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
+++++++++            return tsA - tsB;
+++++++
+++++++++        });
+++++++
++++++++ 
+++++++
++++++++-        // Scan backwards
+++++++
++++++++-        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-            const r = allRows[i];
+++++++
++++++++-            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++-            if (lastUserRow && lastBotRow) break;
+++++++
++++++++-        }
+++++++
+++++++++        // 3. Identify Candidates
+++++++
+++++++++        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
+++++++++        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
+++++++++        
+++++++
+++++++++        let targetTop = null;
+++++++
+++++++++        let targetBottom = null;
+++++++
++++++++ 
+++++++
++++++++-        // 3. Move to pins
+++++++
++++++++-        if (lastBotRow) {
+++++++
++++++++-            top.appendChild(lastBotRow);
+++++++
++++++++-            top.style.display = 'block';
+++++++
++++++++-        } else {
+++++++
++++++++-            top.style.display = 'none';
+++++++
+++++++++        if (duetActive) {
+++++++
+++++++++             // Find last bot message
+++++++
+++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
+++++++++                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
+++++++++                     targetTop = allRows[i];
+++++++
+++++++++                     break;
+++++++
+++++++++                 }
+++++++
+++++++++             }
+++++++
+++++++++             // Find last user message
+++++++
+++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
+++++++++                 if (allRows[i].classList.contains('user')) {
+++++++
+++++++++                     targetBottom = allRows[i];
+++++++
+++++++++                     break;
+++++++
+++++++++                 }
+++++++
+++++++++             }
+++++++
++++++++         }
+++++++
++++++++ 
+++++++
++++++++-        if (lastUserRow) {
+++++++
++++++++-            bottom.appendChild(lastUserRow);
+++++++
++++++++-            bottom.style.display = 'block';
+++++++
++++++++-        } else {
+++++++
++++++++-            bottom.style.display = 'none';
+++++++
++++++++-        }
+++++++
+++++++++        // 4. Distribute Elements
+++++++
+++++++++        // Since we are sorting, we can just append in order.
+++++++
+++++++++        // However, we want 'chatLog' to have the history.
+++++++
+++++++++        // The pins get pulled out.
+++++++
++++++++         
+++++++
++++++++-        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++-        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++-        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++-        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++-        const scroll = document.getElementById("chat-view");
+++++++
++++++++-        if (scroll) {
+++++++
++++++++-             const botH = bottom.offsetHeight || 0;
+++++++
++++++++-             const topH = top.offsetHeight || 0;
+++++++
++++++++-             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++-             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++-             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++-        }
+++++++
+++++++++        // We must append to history in order FIRST, then move pins out?
+++++++
+++++++++        // Or just iterate and place.
+++++++
+++++++++        
+++++++
+++++++++        allRows.forEach(row => {
+++++++
+++++++++            if (row === targetTop) {
+++++++
+++++++++                if (top.lastChild !== row) top.appendChild(row);
+++++++
+++++++++                top.style.display = 'block';
+++++++
+++++++++            } else if (row === targetBottom) {
+++++++
+++++++++                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
+++++++++                bottom.style.display = 'block';
+++++++
+++++++++            } else {
+++++++
+++++++++                // Everything else goes to history
+++++++
+++++++++                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
+++++++++            }
+++++++
+++++++++        });
+++++++
+++++++++        
+++++++
+++++++++        if (!targetTop) top.style.display = 'none';
+++++++
+++++++++        if (!targetBottom) bottom.style.display = 'none';
+++++++
+++++++++
+++++++
+++++++++        // 5. Scroll Management
+++++++
+++++++++        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
+++++++++        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++     }
+++++++
++++++++     
+++++++
++++++++     function syncDuetPadding() {}
+++++++
++++++++@@ -4601,6 +4613,8 @@
+++++++
++++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
+++++++++    let globalMessageSequence = 0;
+++++++
+++++++++
+++++++
++++++++     function addMessage(role, text, options = {}) {
+++++++
++++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++++
++++++++       // Hide chat placeholder when first message appears
+++++++
++++++++@@ -4617,6 +4631,9 @@
+++++++
++++++++ 
+++++++
++++++++       const row = document.createElement("div");
+++++++
++++++++       row.className = `msg-row ${role}`;
+++++++
+++++++++      // Timestamp and Sequence for robust sorting
+++++++
+++++++++      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++++
+++++++++      row.dataset.sequence = ++globalMessageSequence;
+++++++
++++++++ 
+++++++
++++++++       // Apply focus highlighting if a goal is focused
+++++++
++++++++       if (othelloState.activeGoalId) {
+++++++
++++++++\n# Refactor: Duet History & Archiving\n
+++++++
++++++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++++++
++++++++index 7aae5e35..6431d63e 100644
+++++++
++++++++--- a/evidence/updatedifflog.md
+++++++
+++++++++++ b/evidence/updatedifflog.md
+++++++
++++++++@@ -1,210 +1,484 @@
+++++++
++++++++-# Cycle Status: COMPLETE
+++++++
++++++++-
+++++++
++++++++-## Todo Ledger
+++++++
++++++++-Completed:
+++++++
++++++++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
++++++++-
+++++++
++++++++-## Next Action
+++++++
++++++++-Commit
+++++++
++++++++-
+++++++
++++++++-diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++-index a78c1b7b..d6ca18ec 100644
+++++++
++++++++---- a/othello_ui.html
+++++++
++++++++-+++ b/othello_ui.html
+++++++
++++++++-@@ -339,6 +339,7 @@
+++++++
++++++++-       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++-         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++-         
+++++++
++++++++-+        <!-- Only this is scrollable history -->
+++++++
++++++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++-         <div id="chat-log" class="chat-log"></div>
+++++++
++++++++-diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++-index 825c710b..c7cc1ae5 100644
+++++++
++++++++---- a/static/othello.css
+++++++
++++++++-+++ b/static/othello.css
+++++++
++++++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* --- Duet Chat Mode (Unified) --- */
+++++++
++++++++--/* Phase 2: Fix the scroll container */
+++++++
++++++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
++++++++- .chat-sheet {
+++++++
++++++++-   display: flex !important;
+++++++
++++++++-   flex-direction: column !important;
+++++++
++++++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++- /* Header is rigid */
+++++++
++++++++- .chat-sheet__header {
+++++++
++++++++-   flex: 0 0 auto;
+++++++
++++++++-+  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++-+  position: relative;
+++++++
++++++++-+  box-shadow: 0 1px 0 var(--border);
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Input is rigid (footer) */
+++++++
++++++++- .input-bar {
+++++++
++++++++-   flex: 0 0 auto;
+++++++
++++++++-+  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++-+  position: relative;
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Chat View IS the scroll container now */
+++++++
++++++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++-   background: rgba(15, 23, 42, 0.98);
+++++++
++++++++-   padding: 0.75rem;
+++++++
++++++++-   margin: 0;
+++++++
++++++++--  display: block !important;
+++++++
++++++++-+  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++-   backdrop-filter: blur(8px);
+++++++
++++++++--  /* Ensure they don't shrink away */
+++++++
++++++++-   flex-shrink: 0; 
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++-+/* Default hidden until populated */
+++++++
++++++++-+.duet-pane:empty {
+++++++
++++++++-+    display: none !important;
+++++++
++++++++-+}
+++++++
++++++++-+
+++++++
++++++++- .duet-pane--top {
+++++++
++++++++-   top: 0;
+++++++
++++++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
++++++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++-   overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++-   height: auto !important;
+++++++
++++++++-   padding: 1rem;
+++++++
++++++++-+  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++-+  padding-top: 1rem;
+++++++
++++++++-+  padding-bottom: 1rem;
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Hide empty panes */
+++++++
++++++++-diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++-index 3a092bfc..1a19d8a7 100644
+++++++
++++++++---- a/static/othello.js
+++++++
++++++++-+++ b/static/othello.js
+++++++
++++++++-@@ -4300,76 +4300,81 @@
+++++++
++++++++-       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++-     }
+++++++
++++++++- 
+++++++
++++++++--    // Phase 3: Move nodes (no duplication)
+++++++
++++++++-+    // Phase 3: Canonical Move
+++++++
++++++++-     function applyDuetPins() {
+++++++
++++++++--        if (!isDuetEnabled()) return;
+++++++
++++++++--        
+++++++
++++++++--        const chatLog = document.getElementById("chat-log");
+++++++
++++++++-         const top = document.getElementById("duet-top");
+++++++
++++++++-         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++--        if (!chatLog) return;
+++++++
++++++++--        
+++++++
++++++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
++++++++--        // Actually, simpler approach for V1:
+++++++
++++++++--        // We only pin the LATEST. 
+++++++
++++++++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
++++++++--        // Move them to pins? No, that breaks history flow if they are old.
+++++++
++++++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
++++++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
++++++++--        // This implies visual displacement.
+++++++
++++++++--        
+++++++
++++++++--        // Better Strategy:
+++++++
++++++++--        // 1. Clear pins.
+++++++
++++++++--        // 2. Scan chatLog rows.
+++++++
++++++++--        // 3. Last row -> if user, move to bottom.
+++++++
++++++++--        // 4. Last ASSISTANT row -> move to top.
+++++++
++++++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
++++++++--        // This effectively empties the bottom of the history.
+++++++
++++++++--        
+++++++
++++++++--        // Implementation:
+++++++
++++++++--        // Find all .msg-row in chat main loop or chatLog
+++++++
++++++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
++++++++--        if (rows.length === 0) return;
+++++++
++++++++--        
+++++++
++++++++--        // Find last user row
+++++++
++++++++-+        const chatLog = document.getElementById("chat-log");
+++++++
++++++++-+
+++++++
++++++++-+        // Fallback for safety
+++++++
++++++++-+        if (!top || !bottom || !chatLog) return;
+++++++
++++++++-+
+++++++
++++++++-+        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++-+        // This ensures scanning always finds true chronological last messages
+++++++
++++++++-+        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++-+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++-+
+++++++
++++++++-+        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++-+        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++-+        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++-+        // This might reorder history if we aren't careful.
+++++++
++++++++-+        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++-+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++-+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++-+        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++-+        
+++++++
++++++++-+        // Sorting approach (safest for history):
+++++++
++++++++-+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++-+        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++-+        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++-+        
+++++++
++++++++-+        if (allRows.length === 0) return;
+++++++
++++++++-+
+++++++
++++++++-+        // 2. Scan for candidates
+++++++
++++++++-         let lastUserRow = null;
+++++++
++++++++-         let lastBotRow = null;
+++++++
++++++++--        
+++++++
++++++++-+
+++++++
++++++++-         // Scan backwards
+++++++
++++++++--        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
++++++++--            const r = rows[i];
+++++++
++++++++-+        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-+            const r = allRows[i];
+++++++
++++++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++-+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++-             if (lastUserRow && lastBotRow) break;
+++++++
++++++++-         }
+++++++
++++++++- 
+++++++
++++++++--        // Move to pins
+++++++
++++++++-+        // 3. Move to pins
+++++++
++++++++-         if (lastBotRow) {
+++++++
++++++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
++++++++--            // Ensure display is correct
+++++++
++++++++-+            top.appendChild(lastBotRow);
+++++++
++++++++-             top.style.display = 'block';
+++++++
++++++++-         } else {
+++++++
++++++++--            top.innerHTML = "";
+++++++
++++++++-             top.style.display = 'none';
+++++++
++++++++-         }
+++++++
++++++++--        
+++++++
++++++++-+
+++++++
++++++++-         if (lastUserRow) {
+++++++
++++++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++-+            bottom.appendChild(lastUserRow);
+++++++
++++++++-             bottom.style.display = 'block';
+++++++
++++++++-         } else {
+++++++
++++++++--            bottom.innerHTML = "";
+++++++
++++++++-             bottom.style.display = 'none';
+++++++
++++++++-         }
+++++++
++++++++-         
+++++++
++++++++--        // If we moved stuff, scroll might need adjustment? 
+++++++
++++++++--        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++-+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++-+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++-+        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++-+        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++-+        const scroll = document.getElementById("chat-view");
+++++++
++++++++-+        if (scroll) {
+++++++
++++++++-+             const botH = bottom.offsetHeight || 0;
+++++++
++++++++-+             const topH = top.offsetHeight || 0;
+++++++
++++++++-+             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++-+             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++-+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++-+        }
+++++++
++++++++-     }
+++++++
++++++++-     
+++++++
++++++++--    // No-op for old sync padding (CSS sticky handles it now)
+++++++
++++++++-     function syncDuetPadding() {}
+++++++
++++++++- 
+++++++
++++++++-     function updateDuetView(row, role) {
+++++++
++++++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++-+      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++-       requestAnimationFrame(applyDuetPins);
+++++++
++++++++-     }
+++++++
++++++++- 
+++++++
+++++++++# Cycle Status: COMPLETE
+++++++
+++++++++
+++++++
+++++++++## Todo Ledger
+++++++
+++++++++Completed:
+++++++
+++++++++- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
+++++++++
+++++++
+++++++++## Next Action
+++++++
+++++++++Commit
+++++++
+++++++++
+++++++
+++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
+++++++++index a78c1b7b..d6ca18ec 100644
+++++++
+++++++++--- a/othello_ui.html
+++++++
++++++++++++ b/othello_ui.html
+++++++
+++++++++@@ -339,6 +339,7 @@
+++++++
+++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
+++++++++         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
+++++++++         
+++++++
++++++++++        <!-- Only this is scrollable history -->
+++++++
+++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
+++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
+++++++++         <div id="chat-log" class="chat-log"></div>
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
+++++++++index 825c710b..c7cc1ae5 100644
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++++++ b/static/othello.css
+++++++
+++++++++@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* --- Duet Chat Mode (Unified) --- */
+++++++
+++++++++-/* Phase 2: Fix the scroll container */
+++++++
++++++++++/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
+++++++++ .chat-sheet {
+++++++
+++++++++   display: flex !important;
+++++++
+++++++++   flex-direction: column !important;
+++++++
+++++++++@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++ /* Header is rigid */
+++++++
+++++++++ .chat-sheet__header {
+++++++
+++++++++   flex: 0 0 auto;
+++++++
++++++++++  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++++  position: relative;
+++++++
++++++++++  box-shadow: 0 1px 0 var(--border);
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Input is rigid (footer) */
+++++++
+++++++++ .input-bar {
+++++++
+++++++++   flex: 0 0 auto;
+++++++
++++++++++  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++++  position: relative;
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Chat View IS the scroll container now */
+++++++
+++++++++@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++   background: rgba(15, 23, 42, 0.98);
+++++++
+++++++++   padding: 0.75rem;
+++++++
+++++++++   margin: 0;
+++++++
+++++++++-  display: block !important;
+++++++
++++++++++  display: block; /* always block, hidden by JS empty check if needed */
+++++++
+++++++++   backdrop-filter: blur(8px);
+++++++
+++++++++-  /* Ensure they don't shrink away */
+++++++
+++++++++   flex-shrink: 0; 
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
++++++++++/* Default hidden until populated */
+++++++
++++++++++.duet-pane:empty {
+++++++
++++++++++    display: none !important;
+++++++
++++++++++}
+++++++
++++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
+++++++++   top: 0;
+++++++
+++++++++   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
+++++++++@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++   overflow: visible !important; /* Let parent scroll it */
+++++++
+++++++++   height: auto !important;
+++++++
+++++++++   padding: 1rem;
+++++++
++++++++++  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++++  padding-top: 1rem;
+++++++
++++++++++  padding-bottom: 1rem;
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Hide empty panes */
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
+++++++++index 3a092bfc..1a19d8a7 100644
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++++++ b/static/othello.js
+++++++
+++++++++@@ -4300,76 +4300,81 @@
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
+++++++++     }
+++++++
+++++++++ 
+++++++
+++++++++-    // Phase 3: Move nodes (no duplication)
+++++++
++++++++++    // Phase 3: Canonical Move
+++++++
+++++++++     function applyDuetPins() {
+++++++
+++++++++-        if (!isDuetEnabled()) return;
+++++++
+++++++++-        
+++++++
+++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
+++++++++-        if (!chatLog) return;
+++++++
+++++++++-        
+++++++
+++++++++-        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
+++++++++-        // Actually, simpler approach for V1:
+++++++
+++++++++-        // We only pin the LATEST. 
+++++++
+++++++++-        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
+++++++++-        // Move them to pins? No, that breaks history flow if they are old.
+++++++
+++++++++-        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
+++++++++-        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
+++++++++-        // This implies visual displacement.
+++++++
+++++++++-        
+++++++
+++++++++-        // Better Strategy:
+++++++
+++++++++-        // 1. Clear pins.
+++++++
+++++++++-        // 2. Scan chatLog rows.
+++++++
+++++++++-        // 3. Last row -> if user, move to bottom.
+++++++
+++++++++-        // 4. Last ASSISTANT row -> move to top.
+++++++
+++++++++-        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
+++++++++-        // This effectively empties the bottom of the history.
+++++++
+++++++++-        
+++++++
+++++++++-        // Implementation:
+++++++
+++++++++-        // Find all .msg-row in chat main loop or chatLog
+++++++
+++++++++-        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
+++++++++-        if (rows.length === 0) return;
+++++++
+++++++++-        
+++++++
+++++++++-        // Find last user row
+++++++
++++++++++        const chatLog = document.getElementById("chat-log");
+++++++
++++++++++
+++++++
++++++++++        // Fallback for safety
+++++++
++++++++++        if (!top || !bottom || !chatLog) return;
+++++++
++++++++++
+++++++
++++++++++        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++++        // This ensures scanning always finds true chronological last messages
+++++++
++++++++++        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++++        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++++
+++++++
++++++++++        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++++        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++++        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++++        // This might reorder history if we aren't careful.
+++++++
++++++++++        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++++        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++++        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++++        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++++        
+++++++
++++++++++        // Sorting approach (safest for history):
+++++++
++++++++++        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++++        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++++        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++++        
+++++++
++++++++++        if (allRows.length === 0) return;
+++++++
++++++++++
+++++++
++++++++++        // 2. Scan for candidates
+++++++
+++++++++         let lastUserRow = null;
+++++++
+++++++++         let lastBotRow = null;
+++++++
+++++++++-        
+++++++
++++++++++
+++++++
+++++++++         // Scan backwards
+++++++
+++++++++-        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
+++++++++-            const r = rows[i];
+++++++
++++++++++        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++++            const r = allRows[i];
+++++++
+++++++++             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
+++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++++            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
+++++++++             if (lastUserRow && lastBotRow) break;
+++++++
+++++++++         }
+++++++
+++++++++ 
+++++++
+++++++++-        // Move to pins
+++++++
++++++++++        // 3. Move to pins
+++++++
+++++++++         if (lastBotRow) {
+++++++
+++++++++-            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
+++++++++-            // Ensure display is correct
+++++++
++++++++++            top.appendChild(lastBotRow);
+++++++
+++++++++             top.style.display = 'block';
+++++++
+++++++++         } else {
+++++++
+++++++++-            top.innerHTML = "";
+++++++
+++++++++             top.style.display = 'none';
+++++++
+++++++++         }
+++++++
+++++++++-        
+++++++
++++++++++
+++++++
+++++++++         if (lastUserRow) {
+++++++
+++++++++-            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++++            bottom.appendChild(lastUserRow);
+++++++
+++++++++             bottom.style.display = 'block';
+++++++
+++++++++         } else {
+++++++
+++++++++-            bottom.innerHTML = "";
+++++++
+++++++++             bottom.style.display = 'none';
+++++++
+++++++++         }
+++++++
+++++++++         
+++++++
+++++++++-        // If we moved stuff, scroll might need adjustment? 
+++++++
+++++++++-        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++++        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++++        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++++        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++++        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++++        const scroll = document.getElementById("chat-view");
+++++++
++++++++++        if (scroll) {
+++++++
++++++++++             const botH = bottom.offsetHeight || 0;
+++++++
++++++++++             const topH = top.offsetHeight || 0;
+++++++
++++++++++             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++++             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++++             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++++        }
+++++++
+++++++++     }
+++++++
+++++++++     
+++++++
+++++++++-    // No-op for old sync padding (CSS sticky handles it now)
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
+++++++++ 
+++++++
+++++++++     function updateDuetView(row, role) {
+++++++
+++++++++-      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++++      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
+++++++++       requestAnimationFrame(applyDuetPins);
+++++++
+++++++++     }
+++++++
+++++++++ 
+++++++
+++++++++\n# Refactor: 3-Zone Layout\n
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++index 9b1f8845..382eeb57 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++@@ -2203,65 +2203,64 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Chat View IS the scroll container now */
+++++++
++++++++
+++++++
++++++++++/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++++
++++++++
+++++++
+++++++++ #chat-view {
+++++++
++++++++
+++++++
+++++++++   display: flex !important;
+++++++
++++++++
+++++++
+++++++++   flex-direction: column;
+++++++
++++++++
+++++++
+++++++++-  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++++
++++++++
+++++++
++++++++++  flex: 1 1 0;
+++++++
++++++++
+++++++
+++++++++   min-height: 0;
+++++++
++++++++
+++++++
+++++++++-  overflow-y: auto !important; /* The ONLY scrollbar */
+++++++
++++++++
+++++++
+++++++++-  overflow-x: hidden;
+++++++
++++++++
+++++++
++++++++++  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
++++++++
+++++++
+++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++-  padding: 0; /* Strict */
+++++++
++++++++
+++++++
++++++++++  padding: 0;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Duet Panes (Sticky) - Transparent Rails */
+++++++
++++++++
+++++++
++++++++++/* Duet Panes (Static Flex Items) */
+++++++
++++++++
+++++++
+++++++++ .duet-pane {
+++++++
++++++++
+++++++
+++++++++-  position: sticky;
+++++++
++++++++
+++++++
+++++++++-  z-index: 100; /* Must beat messages */
+++++++
++++++++
+++++++
+++++++++-  background: transparent; /* Transparent background */
+++++++
++++++++
+++++++
++++++++++  position: static; /* No longer sticky */
+++++++
++++++++
+++++++
++++++++++  flex: 0 0 auto; /* Rigid height based on content */
+++++++
++++++++
+++++++
++++++++++  z-index: 100;
+++++++
++++++++
+++++++
++++++++++  background: transparent;
+++++++
++++++++
+++++++
+++++++++   padding: 0.75rem;
+++++++
++++++++
+++++++
+++++++++   margin: 0;
+++++++
++++++++
+++++++
+++++++++-  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++
+++++++
+++++++++-  flex-shrink: 0;
+++++++
++++++++
+++++++
+++++++++-  pointer-events: none; /* Let clicks pass through empty space */
+++++++
++++++++
+++++++
++++++++++  display: block;
+++++++
++++++++
+++++++
++++++++++  pointer-events: none;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Re-enable pointer events on children (the bubbles) */
+++++++
++++++++
+++++++
+++++++++-.duet-pane > * {
+++++++
++++++++
+++++++
+++++++++-  pointer-events: auto;
+++++++
++++++++
+++++++
+++++++++-}
+++++++
++++++++
+++++++
++++++++++.duet-pane > * { pointer-events: auto; }
+++++++
++++++++
+++++++
++++++++++.duet-pane:empty { display: none !important; }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Default hidden until populated */
+++++++
++++++++
+++++++
+++++++++-.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++-    display: none !important;
+++++++
++++++++
+++++++
++++++++++/* Chat Log (Middle Scrollable History) */
+++++++
++++++++
+++++++
++++++++++#chat-log {
+++++++
++++++++
+++++++
++++++++++  display: flex !important;
+++++++
++++++++
+++++++
++++++++++  flex-direction: column;
+++++++
++++++++
+++++++
++++++++++  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++
+++++++
++++++++++  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++
+++++++
++++++++++  min-height: 0;
+++++++
++++++++
+++++++
++++++++++  height: auto !important;
+++++++
++++++++
+++++++
++++++++++  padding: 1rem;
+++++++
++++++++
+++++++
++++++++++  padding-top: 0.5rem;
+++++++
++++++++
+++++++
++++++++++  padding-bottom: 0.5rem;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++/* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++-  top: 0;
+++++++
++++++++
+++++++
+++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++-  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++-  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
++++++++++  order: 1;
+++++++
++++++++
+++++++
++++++++++  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
++++++++++}
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++#chat-log {
+++++++
++++++++
+++++++
++++++++++  order: 2; /* Middle */
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ .duet-pane--bottom {
+++++++
++++++++
+++++++
+++++++++-  bottom: 0;
+++++++
++++++++
+++++++
+++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++-  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++-  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
++++++++++  order: 3;
+++++++
++++++++
+++++++
++++++++++  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Chat Log (History Flow) */
+++++++
++++++++
+++++++
+++++++++-#chat-log {
+++++++
++++++++
+++++++
+++++++++-  display: flex !important;
+++++++
++++++++
+++++++
+++++++++-  flex-direction: column;
+++++++
++++++++
+++++++
+++++++++-  flex: 1; /* occupy space between pins */
+++++++
++++++++
+++++++
+++++++++-  overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++
+++++++
+++++++++-  height: auto !important;
+++++++
++++++++
+++++++
+++++++++-  padding: 1rem;
+++++++
++++++++
+++++++
+++++++++-  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++
+++++++
+++++++++-  padding-top: 1rem;
+++++++
++++++++
+++++++
+++++++++-  padding-bottom: 1rem;
+++++++
++++++++
+++++++
++++++++++/* Ensure empty slots don't take space/border */
+++++++
++++++++
+++++++
++++++++++.duet-pane:empty {
+++++++
++++++++
+++++++
++++++++++    display: none !important;
+++++++
++++++++
+++++++
++++++++++    border: none !important;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ /* Hide empty panes */
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++index 1a19d8a7..2f438318 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++@@ -4300,7 +4300,7 @@
+++++++
++++++++
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    // Phase 3: Canonical Move
+++++++
++++++++
+++++++
++++++++++    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++
+++++++
+++++++++     function applyDuetPins() {
+++++++
++++++++
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++@@ -4308,67 +4308,79 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++         // Fallback for safety
+++++++
++++++++
+++++++
+++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++
+++++++
+++++++++-        // This ensures scanning always finds true chronological last messages
+++++++
++++++++
+++++++
+++++++++-        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++
+++++++
+++++++++-        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++
+++++++
+++++++++-        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++
+++++++
+++++++++-        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++
+++++++
+++++++++-        // This might reorder history if we aren't careful.
+++++++
++++++++
+++++++
+++++++++-        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++
+++++++
+++++++++-        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++
+++++++
+++++++++-        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++
+++++++
+++++++++-        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++
+++++++
+++++++++-        
+++++++
++++++++
+++++++
+++++++++-        // Sorting approach (safest for history):
+++++++
++++++++
+++++++
+++++++++-        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++
+++++++
+++++++++-        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++
+++++++
+++++++++-        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
++++++++++        // 1. Gather ALL message rows from all containers
+++++++
++++++++
+++++++
++++++++++        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++
+++++++
++++++++++        const allRows = [
+++++++
++++++++
+++++++
++++++++++            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
++++++++++            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
++++++++++            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++
+++++++
++++++++++        ];
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++         if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 2. Scan for candidates
+++++++
++++++++
+++++++
+++++++++-        let lastUserRow = null;
+++++++
++++++++
+++++++
+++++++++-        let lastBotRow = null;
+++++++
++++++++
+++++++
++++++++++        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++
+++++++
++++++++++        allRows.sort((a, b) => {
+++++++
++++++++
+++++++
++++++++++            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++
+++++++
++++++++++            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++
+++++++
++++++++++            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++
+++++++
++++++++++            
+++++++
++++++++
+++++++
++++++++++            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++
+++++++
++++++++++            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++
+++++++
++++++++++            return tsA - tsB;
+++++++
++++++++
+++++++
++++++++++        });
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // Scan backwards
+++++++
++++++++
+++++++
+++++++++-        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-            const r = allRows[i];
+++++++
++++++++
+++++++
+++++++++-            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++
+++++++
+++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++
+++++++
+++++++++-            if (lastUserRow && lastBotRow) break;
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // 3. Identify Candidates
+++++++
++++++++
+++++++
++++++++++        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++
+++++++
++++++++++        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        let targetTop = null;
+++++++
++++++++
+++++++
++++++++++        let targetBottom = null;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 3. Move to pins
+++++++
++++++++
+++++++
+++++++++-        if (lastBotRow) {
+++++++
++++++++
+++++++
+++++++++-            top.appendChild(lastBotRow);
+++++++
++++++++
+++++++
+++++++++-            top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++-            top.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        if (duetActive) {
+++++++
++++++++
+++++++
++++++++++             // Find last bot message
+++++++
++++++++
+++++++
++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
++++++++++                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++
+++++++
++++++++++                     targetTop = allRows[i];
+++++++
++++++++
+++++++
++++++++++                     break;
+++++++
++++++++
+++++++
++++++++++                 }
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
++++++++++             // Find last user message
+++++++
++++++++
+++++++
++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
++++++++++                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++
+++++++
++++++++++                     targetBottom = allRows[i];
+++++++
++++++++
+++++++
++++++++++                     break;
+++++++
++++++++
+++++++
++++++++++                 }
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
+++++++++         }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        if (lastUserRow) {
+++++++
++++++++
+++++++
+++++++++-            bottom.appendChild(lastUserRow);
+++++++
++++++++
+++++++
+++++++++-            bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++-            bottom.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // 4. Distribute Elements
+++++++
++++++++
+++++++
++++++++++        // Since we are sorting, we can just append in order.
+++++++
++++++++
+++++++
++++++++++        // However, we want 'chatLog' to have the history.
+++++++
++++++++
+++++++
++++++++++        // The pins get pulled out.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++
+++++++
+++++++++-        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++
+++++++
+++++++++-        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++
+++++++
+++++++++-        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++
+++++++
+++++++++-        const scroll = document.getElementById("chat-view");
+++++++
++++++++
+++++++
+++++++++-        if (scroll) {
+++++++
++++++++
+++++++
+++++++++-             const botH = bottom.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-             const topH = top.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++
+++++++
+++++++++-             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++
+++++++
+++++++++-             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++
+++++++
++++++++++        // Or just iterate and place.
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        allRows.forEach(row => {
+++++++
++++++++
+++++++
++++++++++            if (row === targetTop) {
+++++++
++++++++
+++++++
++++++++++                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                top.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++            } else if (row === targetBottom) {
+++++++
++++++++
+++++++
++++++++++                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                bottom.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++            } else {
+++++++
++++++++
+++++++
++++++++++                // Everything else goes to history
+++++++
++++++++
+++++++
++++++++++                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++
+++++++
++++++++++            }
+++++++
++++++++
+++++++
++++++++++        });
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        if (!targetTop) top.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        if (!targetBottom) bottom.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++        // 5. Scroll Management
+++++++
++++++++
+++++++
++++++++++        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++
+++++++
++++++++++        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++     
+++++++
++++++++
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++@@ -4601,6 +4613,8 @@
+++++++
++++++++
+++++++
+++++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++    let globalMessageSequence = 0;
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++     function addMessage(role, text, options = {}) {
+++++++
++++++++
+++++++
+++++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++++
++++++++
+++++++
+++++++++       // Hide chat placeholder when first message appears
+++++++
++++++++
+++++++
+++++++++@@ -4617,6 +4631,9 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       const row = document.createElement("div");
+++++++
++++++++
+++++++
+++++++++       row.className = `msg-row ${role}`;
+++++++
++++++++
+++++++
++++++++++      // Timestamp and Sequence for robust sorting
+++++++
++++++++
+++++++
++++++++++      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++++
++++++++
+++++++
++++++++++      row.dataset.sequence = ++globalMessageSequence;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       // Apply focus highlighting if a goal is focused
+++++++
++++++++
+++++++
+++++++++       if (othelloState.activeGoalId) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++\ No newline at end of file
+++++++
++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++index d6ca18ec..dce7fa4a 100644
+++++++
++++++++--- a/othello_ui.html
+++++++
+++++++++++ b/othello_ui.html
+++++++
++++++++@@ -342,7 +342,12 @@
+++++++
++++++++         <!-- Only this is scrollable history -->
+++++++
++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++-        <div id="chat-log" class="chat-log"></div>
+++++++
+++++++++        <!-- Renamed/Aliased for clarity as requested, but keeping ID if preferred by CSS. 
+++++++
+++++++++             User asked for #duet-history. Let's make it explicit. 
+++++++
+++++++++             We can keep chat-log class for styling compatibility if needed. -->
+++++++
+++++++++        <div id="duet-history" class="chat-log" style="overflow-y:auto; flex:1 1 auto;">
+++++++
+++++++++           <div id="duet-history-spacer" aria-hidden="true" style="height:0px;"></div>
+++++++
+++++++++        </div>
+++++++
++++++++         
+++++++
++++++++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
++++++++       </div>
+++++++
++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++index 382eeb57..85512fda 100644
+++++++
++++++++--- a/static/othello.css
+++++++
+++++++++++ b/static/othello.css
+++++++
++++++++@@ -2230,7 +2230,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++ .duet-pane:empty { display: none !important; }
+++++++
++++++++ 
+++++++
++++++++ /* Chat Log (Middle Scrollable History) */
+++++++
++++++++-#chat-log {
+++++++
+++++++++/* Changed to #duet-history in DOM, but kept .chat-log class. 
+++++++
+++++++++   Target generic .chat-log or specific #duet-history */
+++++++
+++++++++#chat-log, #duet-history {
+++++++
++++++++   display: flex !important;
+++++++
++++++++   flex-direction: column;
+++++++
++++++++   flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++@@ -2242,6 +2244,11 @@ body.chat-open #global-chat-fab {
+++++++
++++++++   padding-bottom: 0.5rem;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
+++++++++#duet-history-spacer {
+++++++
+++++++++    flex: 0 0 auto;
+++++++
+++++++++    width: 100%;
+++++++
+++++++++}
+++++++
+++++++++
+++++++
++++++++ /* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++ .duet-pane--top {
+++++++
++++++++   order: 1;
+++++++
++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++index 2f438318..618d8127 100644
+++++++
++++++++--- a/static/othello.js
+++++++
+++++++++++ b/static/othello.js
+++++++
++++++++@@ -793,7 +793,8 @@
+++++++
++++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++
++++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++
++++++++ 
+++++++
++++++++-    const chatLog = document.getElementById('chat-log');
+++++++
+++++++++    // Updated to support new Duet History container
+++++++
+++++++++    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++
++++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++
++++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++
++++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++
++++++++@@ -4300,94 +4301,87 @@
+++++++
++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++-    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++-    function applyDuetPins() {
+++++++
+++++++++    // Phase 4: Duet Padding & Spacer Logic
+++++++
+++++++++    function syncDuetHistorySpacer() {
+++++++
+++++++++       const history = document.getElementById("duet-history");
+++++++
+++++++++       const spacer = document.getElementById("duet-history-spacer");
+++++++
+++++++++       if (!history || !spacer) return;
+++++++
+++++++++       // The spacer forces the content to be initially "above the fold" 
+++++++
+++++++++       // if we are scrolled to bottom.
+++++++
+++++++++       spacer.style.height = `${history.clientHeight}px`;
+++++++
+++++++++    }
+++++++
+++++++++
+++++++
+++++++++    function scrollDuetHistoryToBottom() {
+++++++
+++++++++       const history = document.getElementById("duet-history");
+++++++
+++++++++       if (!history) return;
+++++++
+++++++++       history.scrollTop = history.scrollHeight;
+++++++
+++++++++    }
+++++++
+++++++++
+++++++
+++++++++    // Call on resize
+++++++
+++++++++    window.addEventListener("resize", () => {
+++++++
+++++++++        syncDuetHistorySpacer();
+++++++
+++++++++    });
+++++++
+++++++++
+++++++
+++++++++    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++
+++++++++    function archivePinnedToHistory() {
+++++++
++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
+++++++++        const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
+++++++++        const spacer = document.getElementById("duet-history-spacer");
+++++++
++++++++ 
+++++++
++++++++         // Fallback for safety
+++++++
++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++         
+++++++
++++++++-        // 1. Gather ALL message rows from all containers
+++++++
++++++++-        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++-        const allRows = [
+++++++
++++++++-            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++-        ];
+++++++
++++++++-
+++++++
++++++++-        if (allRows.length === 0) return;
+++++++
++++++++-
+++++++
++++++++-        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++-        allRows.sort((a, b) => {
+++++++
++++++++-            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++-            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++-            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++-            
+++++++
++++++++-            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++-            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++-            return tsA - tsB;
+++++++
++++++++-        });
+++++++
+++++++++        // 1. Check if user is at bottom BEFORE modifying
+++++++
+++++++++        // Threshold of 50px
+++++++
+++++++++        const isAtBottom = (chatLog.scrollHeight - chatLog.scrollTop - chatLog.clientHeight) < 50;
+++++++
++++++++ 
+++++++
++++++++-        // 3. Identify Candidates
+++++++
++++++++-        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++-        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
+++++++++        // 2. Archive items from pins to history (chronological insert before spacer)
+++++++
+++++++++        // Note: top messages came BEFORE bottom messages in time (usually).
+++++++
++++++++         
+++++++
++++++++-        let targetTop = null;
+++++++
++++++++-        let targetBottom = null;
+++++++
++++++++-
+++++++
++++++++-        if (duetActive) {
+++++++
++++++++-             // Find last bot message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++-                     targetTop = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
++++++++-             // Find last user message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++-                     targetBottom = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
++++++++-        }
+++++++
++++++++-
+++++++
++++++++-        // 4. Distribute Elements
+++++++
++++++++-        // Since we are sorting, we can just append in order.
+++++++
++++++++-        // However, we want 'chatLog' to have the history.
+++++++
++++++++-        // The pins get pulled out.
+++++++
+++++++++        // We move ALL children of top and bottom to history?
+++++++
+++++++++        // Yes, because this is called "on new send" to clear the stage.
+++++++
+++++++++        // We should sort them? 
+++++++
+++++++++        // If we assume Top is "Last Bot" and Bottom is "Last User", then Top implies an earlier event IF the user just replied.
+++++++
+++++++++        // But usually: Bot (Top) -> User (Bottom).
+++++++
+++++++++        // So correct order is Top content -> Bottom content.
+++++++
+++++++++        
+++++++
+++++++++        const topNodes = Array.from(top.children);
+++++++
+++++++++        const bottomNodes = Array.from(bottom.children);
+++++++
++++++++         
+++++++
++++++++-        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++-        // Or just iterate and place.
+++++++
+++++++++        const fragment = document.createDocumentFragment();
+++++++
+++++++++        topNodes.forEach(n => fragment.appendChild(n));
+++++++
+++++++++        bottomNodes.forEach(n => fragment.appendChild(n));
+++++++
++++++++         
+++++++
++++++++-        allRows.forEach(row => {
+++++++
++++++++-            if (row === targetTop) {
+++++++
++++++++-                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++-                top.style.display = 'block';
+++++++
++++++++-            } else if (row === targetBottom) {
+++++++
++++++++-                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++-                bottom.style.display = 'block';
+++++++
+++++++++        if (fragment.children.length > 0) {
+++++++
+++++++++            if (spacer) {
+++++++
+++++++++                chatLog.insertBefore(fragment, spacer);
+++++++
++++++++             } else {
+++++++
++++++++-                // Everything else goes to history
+++++++
++++++++-                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
+++++++++                chatLog.appendChild(fragment);
+++++++
++++++++             }
+++++++
++++++++-        });
+++++++
+++++++++        }
+++++++
+++++++++        
+++++++
+++++++++        // Clear pins (implicit by appendChild movement, but ensure empty state)
+++++++
+++++++++        // If nodes were cloned, we'd need to clear. appenChild moves them.
+++++++
++++++++         
+++++++
++++++++-        if (!targetTop) top.style.display = 'none';
+++++++
++++++++-        if (!targetBottom) bottom.style.display = 'none';
+++++++
+++++++++        // 3. Maintain Scroll Position
+++++++
+++++++++        if (isAtBottom) {
+++++++
+++++++++             scrollDuetHistoryToBottom();
+++++++
+++++++++        }
+++++++
+++++++++    }
+++++++
++++++++ 
+++++++
++++++++-        // 5. Scroll Management
+++++++
++++++++-        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++-        // But logic is usually handled by scrollChatToBottom separately.
+++++++
+++++++++    // Deprecated / Aliased
+++++++
+++++++++    function applyDuetPins() {
+++++++
+++++++++        // No-op or alias to archive? 
+++++++
+++++++++        // We only want to archive on SPECIFIC events (new send), not every render loop.
+++++++
+++++++++        // So we leave this empty to stop auto-magic behavior.
+++++++
++++++++     }
+++++++
++++++++     
+++++++
++++++++     function syncDuetPadding() {}
+++++++
++++++++ 
+++++++
++++++++     function updateDuetView(row, role) {
+++++++
++++++++-      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++-      requestAnimationFrame(applyDuetPins);
+++++++
+++++++++      // In new model, we don't automatically pin everything.
+++++++
+++++++++      // addMessage handles the routing.
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++     function bindDuetListeners() {
+++++++
++++++++@@ -4399,13 +4393,12 @@
+++++++
++++++++ 
+++++++
++++++++     function getChatContainer() {
+++++++
++++++++       // Phase 4: Target the real scroll container for appending?
+++++++
++++++++-      // No, we append to chat-log. The VIEW is the scroller.
+++++++
++++++++-      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++
++++++++-      const chatLog = document.getElementById("chat-log");
+++++++
+++++++++      // No, we append to chat-log / duet-history.
+++++++
+++++++++      const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
++++++++       
+++++++
++++++++       if (!chatLog) {
+++++++
++++++++          // ... error ...
+++++++
++++++++-        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++
+++++++++        console.error("[Othello UI] CRITICAL: chat container missing (#duet-history or #chat-log).");
+++++++
++++++++         // Visible UI Error (Phase A/B Requirement)
+++++++
++++++++         const toastContainer = document.getElementById("toast-container");
+++++++
++++++++         if (toastContainer) {
+++++++
++++++++@@ -4554,11 +4547,14 @@
+++++++
++++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++
++++++++             if (!text.trim()) return;
+++++++
++++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++
++++++++-            addMessage(role, text);
+++++++
+++++++++            // Pass special flag to force into history backlog
+++++++
+++++++++            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++
++++++++           });
+++++++
++++++++           
+++++++
++++++++-          // Force scroll to bottom after initial load
+++++++
++++++++-          scrollChatToBottom(true);
+++++++
+++++++++          // Force scroll logic for "hidden backlog"
+++++++
+++++++++          syncDuetHistorySpacer();
+++++++
+++++++++          scrollDuetHistoryToBottom();
+++++++
+++++++++          // scrollChatToBottom(true); // Legacy call
+++++++
++++++++         };
+++++++
++++++++         if (renderedCount > 0) {
+++++++
++++++++           renderMessages(messages);
+++++++
++++++++@@ -4685,9 +4681,40 @@
+++++++
++++++++ 
+++++++
++++++++       row.appendChild(bubble);
+++++++
++++++++       
+++++++
++++++++-      // Append to the resolved container
+++++++
++++++++-      if (container) {
+++++++
++++++++-         container.appendChild(row);
+++++++
+++++++++      // Phase 5: Routing for Duet vs Standard
+++++++
+++++++++      const duetTop = document.getElementById("duet-top");
+++++++
+++++++++      const duetBottom = document.getElementById("duet-bottom");
+++++++
+++++++++      const historySpacer = document.getElementById("duet-history-spacer");
+++++++
+++++++++
+++++++
+++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
+++++++++      
+++++++
+++++++++      if (duetTop && duetBottom) {
+++++++
+++++++++          if (isHistoryLoad) {
+++++++
+++++++++             // Append to history container
+++++++
+++++++++             // If spacer exists, insert before it
+++++++
+++++++++             if (container.id === "duet-history" && historySpacer) {
+++++++
+++++++++                 container.insertBefore(row, historySpacer);
+++++++
+++++++++             } else {
+++++++
+++++++++                 container.appendChild(row);
+++++++
+++++++++             }
+++++++
+++++++++          } else {
+++++++
+++++++++             // Live Message: Goes to pins
+++++++
+++++++++             if (role === "user") {
+++++++
+++++++++                 // User creates a new turn. 
+++++++
+++++++++                 // Note: Caller (handleInput) should have archived previous pins.
+++++++
+++++++++                 duetBottom.innerHTML = "";
+++++++
+++++++++                 duetBottom.appendChild(row);
+++++++
+++++++++                 duetBottom.style.display = "block";
+++++++
+++++++++             } else {
+++++++
+++++++++                 // Bot message - Replaces Top Pin
+++++++
+++++++++                 duetTop.innerHTML = "";
+++++++
+++++++++                 duetTop.appendChild(row);
+++++++
+++++++++                 duetTop.style.display = "block";
+++++++
+++++++++             }
+++++++
+++++++++          }
+++++++
+++++++++      } else {
+++++++
+++++++++          // Standard appending
+++++++
+++++++++          if (container) container.appendChild(row);
+++++++
++++++++       }
+++++++
++++++++       
+++++++
++++++++       updateDuetView(row, role);
+++++++
++++++++@@ -5963,6 +5990,13 @@
+++++++
++++++++ 
+++++++
++++++++       if (!text && !extraData.ui_action) return;
+++++++
++++++++ 
+++++++
+++++++++      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++
+++++++++      // This ensures the stage is cleared before the new user bubble appears.
+++++++
+++++++++      // We only do this if it's a genuine user message (text present or ui_action).
+++++++
+++++++++      if (typeof archivePinnedToHistory === "function") {
+++++++
+++++++++          archivePinnedToHistory();
+++++++
+++++++++      }
+++++++
+++++++++
+++++++
++++++++       // Voice-first save command (Strict Command Mode)
+++++++
++++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++++
++++++++       
+++++++
++++++++\n# Refactor: Single Scroll Container\n
+++++++
++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++index 2f438318..a6a50e8b 100644
+++++++
++++++++--- a/static/othello.js
+++++++
+++++++++++ b/static/othello.js
+++++++
++++++++@@ -793,7 +793,8 @@
+++++++
++++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++
++++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++
++++++++ 
+++++++
++++++++-    const chatLog = document.getElementById('chat-log');
+++++++
+++++++++    // Updated to support new Duet History container
+++++++
+++++++++    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++
++++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++
++++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++
++++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++
++++++++@@ -4300,94 +4301,78 @@
+++++++
++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++-    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++-    function applyDuetPins() {
+++++++
+++++++++    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++++++
+++++++++    function syncDuetHistorySpacer() {
+++++++
+++++++++       // Deprecated in Single Scroll model
+++++++
+++++++++    }
+++++++
+++++++++
+++++++
+++++++++    function scrollDuetHistoryToBottom() {
+++++++
+++++++++       // Deprecated - use scrollChatToBottom
+++++++
+++++++++    }
+++++++
+++++++++
+++++++
+++++++++    // Call on resize - harmless
+++++++
+++++++++    window.addEventListener("resize", () => {});
+++++++
+++++++++
+++++++
+++++++++    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++
+++++++++    function archivePinnedToHistory() {
+++++++
++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
+++++++++        const historyContainer = document.getElementById("duet-history"); // The block above
+++++++
+++++++++        const viewport = document.getElementById("chat-view"); // The scrollable parent
+++++++
++++++++ 
+++++++
++++++++         // Fallback for safety
+++++++
++++++++-        if (!top || !bottom || !chatLog) return;
+++++++
++++++++-        
+++++++
++++++++-        // 1. Gather ALL message rows from all containers
+++++++
++++++++-        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++-        const allRows = [
+++++++
++++++++-            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++-        ];
+++++++
++++++++-
+++++++
++++++++-        if (allRows.length === 0) return;
+++++++
++++++++-
+++++++
++++++++-        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++-        allRows.sort((a, b) => {
+++++++
++++++++-            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++-            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++-            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++-            
+++++++
++++++++-            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++-            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++-            return tsA - tsB;
+++++++
++++++++-        });
+++++++
+++++++++        if (!top || !bottom || !historyContainer || !viewport) return;
+++++++
++++++++ 
+++++++
++++++++-        // 3. Identify Candidates
+++++++
++++++++-        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++-        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++-        
+++++++
++++++++-        let targetTop = null;
+++++++
++++++++-        let targetBottom = null;
+++++++
+++++++++        // 1. Capture Scroll State BEFORE modifying DOM
+++++++
+++++++++        const prevScrollHeight = viewport.scrollHeight;
+++++++
+++++++++        const prevScrollTop = viewport.scrollTop;
+++++++
++++++++ 
+++++++
++++++++-        if (duetActive) {
+++++++
++++++++-             // Find last bot message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++-                     targetTop = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
++++++++-             // Find last user message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++-                     targetBottom = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
+++++++++        // 2. Archive items from pins to history
+++++++
+++++++++        // Order: Top (Bot) -> Bottom (User). 
+++++++
+++++++++        // We append to the END of the history container (chronological).
+++++++
+++++++++        
+++++++
+++++++++        const topNodes = Array.from(top.children);
+++++++
+++++++++        const bottomNodes = Array.from(bottom.children);
+++++++
+++++++++        
+++++++
+++++++++        const fragment = document.createDocumentFragment();
+++++++
+++++++++        topNodes.forEach(n => fragment.appendChild(n));
+++++++
+++++++++        bottomNodes.forEach(n => fragment.appendChild(n));
+++++++
+++++++++        
+++++++
+++++++++        if (fragment.children.length > 0) {
+++++++
+++++++++            historyContainer.appendChild(fragment);
+++++++
++++++++         }
+++++++
++++++++-
+++++++
++++++++-        // 4. Distribute Elements
+++++++
++++++++-        // Since we are sorting, we can just append in order.
+++++++
++++++++-        // However, we want 'chatLog' to have the history.
+++++++
++++++++-        // The pins get pulled out.
+++++++
++++++++         
+++++++
++++++++-        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++-        // Or just iterate and place.
+++++++
+++++++++        // Pins are now empty (because appendChild moved them)
+++++++
++++++++         
+++++++
++++++++-        allRows.forEach(row => {
+++++++
++++++++-            if (row === targetTop) {
+++++++
++++++++-                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++-                top.style.display = 'block';
+++++++
++++++++-            } else if (row === targetBottom) {
+++++++
++++++++-                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++-                bottom.style.display = 'block';
+++++++
++++++++-            } else {
+++++++
++++++++-                // Everything else goes to history
+++++++
++++++++-                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++-            }
+++++++
++++++++-        });
+++++++
+++++++++        // 3. Maintain Visual Scroll Position
+++++++
+++++++++        // If content was added ABOVE the current view (inside historyContainer), 
+++++++
+++++++++        // the scrollHeight increased. We must shift scrollTop to keep the user anchor.
+++++++
+++++++++        
+++++++
+++++++++        const newScrollHeight = viewport.scrollHeight;
+++++++
+++++++++        const delta = newScrollHeight - prevScrollHeight;
+++++++
+++++++++        
+++++++
+++++++++        // Only adjust if we weren't already at 0? 
+++++++
+++++++++        // Actually, if we were at the bottom, we want to STAY at the relative bottom of the *previous* content?
+++++++
+++++++++        // No, if we were at bottom looking at "Live", and "Live" moved down, we want to follow it.
+++++++
+++++++++        // So yes, add delta.
+++++++
++++++++         
+++++++
++++++++-        if (!targetTop) top.style.display = 'none';
+++++++
++++++++-        if (!targetBottom) bottom.style.display = 'none';
+++++++
+++++++++        if (delta > 0) {
+++++++
+++++++++            viewport.scrollTop = prevScrollTop + delta;
+++++++
+++++++++        }
+++++++
+++++++++    }
+++++++
++++++++ 
+++++++
++++++++-        // 5. Scroll Management
+++++++
++++++++-        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++-        // But logic is usually handled by scrollChatToBottom separately.
+++++++
+++++++++    // Deprecated / Aliased
+++++++
+++++++++    function applyDuetPins() {
+++++++
+++++++++        // No-op or alias to archive? 
+++++++
+++++++++        // We only want to archive on SPECIFIC events (new send), not every render loop.
+++++++
+++++++++        // So we leave this empty to stop auto-magic behavior.
+++++++
++++++++     }
+++++++
++++++++     
+++++++
++++++++     function syncDuetPadding() {}
+++++++
++++++++ 
+++++++
++++++++     function updateDuetView(row, role) {
+++++++
++++++++-      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++-      requestAnimationFrame(applyDuetPins);
+++++++
+++++++++      // In new model, we don't automatically pin everything.
+++++++
+++++++++      // addMessage handles the routing.
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++     function bindDuetListeners() {
+++++++
++++++++@@ -4399,13 +4384,12 @@
+++++++
++++++++ 
+++++++
++++++++     function getChatContainer() {
+++++++
++++++++       // Phase 4: Target the real scroll container for appending?
+++++++
++++++++-      // No, we append to chat-log. The VIEW is the scroller.
+++++++
++++++++-      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++
++++++++-      const chatLog = document.getElementById("chat-log");
+++++++
+++++++++      // No, we append to chat-log / duet-history.
+++++++
+++++++++      const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
++++++++       
+++++++
++++++++       if (!chatLog) {
+++++++
++++++++          // ... error ...
+++++++
++++++++-        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++
+++++++++        console.error("[Othello UI] CRITICAL: chat container missing (#duet-history or #chat-log).");
+++++++
++++++++         // Visible UI Error (Phase A/B Requirement)
+++++++
++++++++         const toastContainer = document.getElementById("toast-container");
+++++++
++++++++         if (toastContainer) {
+++++++
++++++++@@ -4554,11 +4538,14 @@
+++++++
++++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++
++++++++             if (!text.trim()) return;
+++++++
++++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++
++++++++-            addMessage(role, text);
+++++++
+++++++++            // Pass special flag to force into history backlog
+++++++
+++++++++            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++
++++++++           });
+++++++
++++++++           
+++++++
++++++++-          // Force scroll to bottom after initial load
+++++++
++++++++-          scrollChatToBottom(true);
+++++++
+++++++++          // Force scroll logic for "hidden backlog"
+++++++
+++++++++          syncDuetHistorySpacer();
+++++++
+++++++++          scrollDuetHistoryToBottom();
+++++++
+++++++++          // scrollChatToBottom(true); // Legacy call
+++++++
++++++++         };
+++++++
++++++++         if (renderedCount > 0) {
+++++++
++++++++           renderMessages(messages);
+++++++
++++++++@@ -4685,9 +4672,36 @@
+++++++
++++++++ 
+++++++
++++++++       row.appendChild(bubble);
+++++++
++++++++       
+++++++
++++++++-      // Append to the resolved container
+++++++
++++++++-      if (container) {
+++++++
++++++++-         container.appendChild(row);
+++++++
+++++++++      // Phase 5: Routing for Duet vs Standard
+++++++
+++++++++      const duetTop = document.getElementById("duet-top");
+++++++
+++++++++      const duetBottom = document.getElementById("duet-bottom");
+++++++
+++++++++      const historySpacer = document.getElementById("duet-history-spacer");
+++++++
+++++++++
+++++++
+++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
+++++++++      
+++++++
+++++++++      if (duetTop && duetBottom) {
+++++++
+++++++++          if (isHistoryLoad) {
+++++++
+++++++++             // Append to history container
+++++++
+++++++++             // We just append because history is naturally chronological "above" the live pins
+++++++
+++++++++             container.appendChild(row);
+++++++
+++++++++          } else {
+++++++
+++++++++             // Live Message: Goes to pins
+++++++
+++++++++             if (role === "user") {
+++++++
+++++++++                 // User creates a new turn. 
+++++++
+++++++++                 // Note: Caller (handleInput) should have archived previous pins.
+++++++
+++++++++                 duetBottom.innerHTML = "";
+++++++
+++++++++                 duetBottom.appendChild(row);
+++++++
+++++++++                 duetBottom.style.display = "block";
+++++++
+++++++++             } else {
+++++++
+++++++++                 // Bot message - Replaces Top Pin
+++++++
+++++++++                 duetTop.innerHTML = "";
+++++++
+++++++++                 duetTop.appendChild(row);
+++++++
+++++++++                 duetTop.style.display = "block";
+++++++
+++++++++             }
+++++++
+++++++++          }
+++++++
+++++++++      } else {
+++++++
+++++++++          // Standard appending
+++++++
+++++++++          if (container) container.appendChild(row);
+++++++
++++++++       }
+++++++
++++++++       
+++++++
++++++++       updateDuetView(row, role);
+++++++
++++++++@@ -5963,6 +5977,13 @@
+++++++
++++++++ 
+++++++
++++++++       if (!text && !extraData.ui_action) return;
+++++++
++++++++ 
+++++++
+++++++++      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++
+++++++++      // This ensures the stage is cleared before the new user bubble appears.
+++++++
+++++++++      // We only do this if it's a genuine user message (text present or ui_action).
+++++++
+++++++++      if (typeof archivePinnedToHistory === "function") {
+++++++
+++++++++          archivePinnedToHistory();
+++++++
+++++++++      }
+++++++
+++++++++
+++++++
++++++++       // Voice-first save command (Strict Command Mode)
+++++++
++++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++++
++++++++       
+++++++
++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++index 382eeb57..b4bbe4a8 100644
+++++++
++++++++--- a/static/othello.css
+++++++
+++++++++++ b/static/othello.css
+++++++
++++++++@@ -2209,7 +2209,8 @@ body.chat-open #global-chat-fab {
+++++++
++++++++   flex-direction: column;
+++++++
++++++++   flex: 1 1 0;
+++++++
++++++++   min-height: 0;
+++++++
++++++++-  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
+++++++++  overflow-y: auto !important; /* The SINGLE scroll container */
+++++++
+++++++++  overflow-x: hidden;
+++++++
++++++++   position: relative;
+++++++
++++++++   padding: 0;
+++++++
++++++++ }
+++++++
++++++++@@ -2217,31 +2218,41 @@ body.chat-open #global-chat-fab {
+++++++
++++++++ /* Duet Panes (Static Flex Items) */
+++++++
++++++++ .duet-pane {
+++++++
++++++++   position: static; /* No longer sticky */
+++++++
++++++++-  flex: 0 0 auto; /* Rigid height based on content */
+++++++
+++++++++  flex: 0 0 auto;
+++++++
++++++++   z-index: 100;
+++++++
++++++++   background: transparent;
+++++++
++++++++   padding: 0.75rem;
+++++++
++++++++   margin: 0;
+++++++
++++++++   display: block;
+++++++
++++++++-  pointer-events: none;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ .duet-pane > * { pointer-events: auto; }
+++++++
++++++++ .duet-pane:empty { display: none !important; }
+++++++
++++++++ 
+++++++
++++++++ /* Chat Log (Middle Scrollable History) */
+++++++
++++++++-#chat-log {
+++++++
++++++++-  display: flex !important;
+++++++
++++++++-  flex-direction: column;
+++++++
++++++++-  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++-  min-height: 0;
+++++++
+++++++++/* Changed to #duet-history in DOM, but kept .chat-log class. 
+++++++
+++++++++   Target generic .chat-log or specific #duet-history */
+++++++
+++++++++#chat-log, #duet-history {
+++++++
+++++++++  display: block; /* Normal block inside scroll */
+++++++
+++++++++  flex: 0 0 auto; 
+++++++
+++++++++  overflow: visible !important; /* No internal scroll */
+++++++
++++++++   height: auto !important;
+++++++
++++++++   padding: 1rem;
+++++++
++++++++   padding-top: 0.5rem;
+++++++
++++++++   padding-bottom: 0.5rem;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
+++++++++/* live-chat-container wrapper (optional styling) */
+++++++
+++++++++#live-chat-container {
+++++++
+++++++++    display: flex;
+++++++
+++++++++    flex-direction: column;
+++++++
+++++++++    flex: 0 0 auto;
+++++++
+++++++++}
+++++++
+++++++++
+++++++
+++++++++#duet-history-spacer {
+++++++
+++++++++    display: none; /* Deprecated/Removed */
+++++++
+++++++++}
+++++++
+++++++++
+++++++
++++++++ /* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++ .duet-pane--top {
+++++++
++++++++   order: 1;
+++++++
++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++index d6ca18ec..b5d19621 100644
+++++++
++++++++--- a/othello_ui.html
+++++++
+++++++++++ b/othello_ui.html
+++++++
++++++++@@ -337,14 +337,21 @@
+++++++
++++++++ 
+++++++
++++++++       <!-- Moved Chat View Content -->
+++++++
++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++-        <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++         
+++++++
++++++++-        <!-- Only this is scrollable history -->
+++++++
++++++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++-        <div id="chat-log" class="chat-log"></div>
+++++++
++++++++-        
+++++++
++++++++-        <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
+++++++++        <!-- History Section (Above Fold) -->
+++++++
+++++++++        <div id="duet-history" class="chat-log">
+++++++
+++++++++           <!-- Spacer removed - let natural flow handle it, or JS can pad if strictly needed. 
+++++++
+++++++++                User instruction: "Step 3: ... history container must be a normal block ... DO NOT set any height" -->
+++++++
+++++++++        </div>
+++++++
+++++++++
+++++++
+++++++++        <!-- Live Chat Section (Visible Default) -->
+++++++
+++++++++        <div id="live-chat-container">
+++++++
+++++++++            <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
+++++++++            <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
+++++++++            <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
+++++++++            <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
+++++++++        </div>
+++++++
+++++++++
+++++++
++++++++       </div>
+++++++
++++++++ 
+++++++
++++++++       <!-- Moved Input Bar -->
+++++++
++++++++\n# Refactor: Fix Message Ordering Regression\n
+++++++
++++++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++++++
++++++++index 7aae5e35..28ce2a12 100644
+++++++
++++++++--- a/evidence/updatedifflog.md
+++++++
+++++++++++ b/evidence/updatedifflog.md
+++++++
++++++++@@ -1,210 +1,2119 @@
+++++++
++++++++-# Cycle Status: COMPLETE
+++++++
++++++++-
+++++++
++++++++-## Todo Ledger
+++++++
++++++++-Completed:
+++++++
++++++++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
++++++++-
+++++++
++++++++-## Next Action
+++++++
++++++++-Commit
+++++++
++++++++-
+++++++
++++++++-diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++-index a78c1b7b..d6ca18ec 100644
+++++++
++++++++---- a/othello_ui.html
+++++++
++++++++-+++ b/othello_ui.html
+++++++
++++++++-@@ -339,6 +339,7 @@
+++++++
++++++++-       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++-         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++-         
+++++++
++++++++-+        <!-- Only this is scrollable history -->
+++++++
++++++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++-         <div id="chat-log" class="chat-log"></div>
+++++++
++++++++-diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++-index 825c710b..c7cc1ae5 100644
+++++++
++++++++---- a/static/othello.css
+++++++
++++++++-+++ b/static/othello.css
+++++++
++++++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* --- Duet Chat Mode (Unified) --- */
+++++++
++++++++--/* Phase 2: Fix the scroll container */
+++++++
++++++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
++++++++- .chat-sheet {
+++++++
++++++++-   display: flex !important;
+++++++
++++++++-   flex-direction: column !important;
+++++++
++++++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++- /* Header is rigid */
+++++++
++++++++- .chat-sheet__header {
+++++++
++++++++-   flex: 0 0 auto;
+++++++
++++++++-+  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++-+  position: relative;
+++++++
++++++++-+  box-shadow: 0 1px 0 var(--border);
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Input is rigid (footer) */
+++++++
++++++++- .input-bar {
+++++++
++++++++-   flex: 0 0 auto;
+++++++
++++++++-+  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++-+  position: relative;
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Chat View IS the scroll container now */
+++++++
++++++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++-   background: rgba(15, 23, 42, 0.98);
+++++++
++++++++-   padding: 0.75rem;
+++++++
++++++++-   margin: 0;
+++++++
++++++++--  display: block !important;
+++++++
++++++++-+  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++-   backdrop-filter: blur(8px);
+++++++
++++++++--  /* Ensure they don't shrink away */
+++++++
++++++++-   flex-shrink: 0; 
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++-+/* Default hidden until populated */
+++++++
++++++++-+.duet-pane:empty {
+++++++
++++++++-+    display: none !important;
+++++++
++++++++-+}
+++++++
++++++++-+
+++++++
++++++++- .duet-pane--top {
+++++++
++++++++-   top: 0;
+++++++
++++++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
++++++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++-   overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++-   height: auto !important;
+++++++
++++++++-   padding: 1rem;
+++++++
++++++++-+  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++-+  padding-top: 1rem;
+++++++
++++++++-+  padding-bottom: 1rem;
+++++++
++++++++- }
+++++++
++++++++- 
+++++++
++++++++- /* Hide empty panes */
+++++++
++++++++-diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++-index 3a092bfc..1a19d8a7 100644
+++++++
++++++++---- a/static/othello.js
+++++++
++++++++-+++ b/static/othello.js
+++++++
++++++++-@@ -4300,76 +4300,81 @@
+++++++
++++++++-       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++-     }
+++++++
++++++++- 
+++++++
++++++++--    // Phase 3: Move nodes (no duplication)
+++++++
++++++++-+    // Phase 3: Canonical Move
+++++++
++++++++-     function applyDuetPins() {
+++++++
++++++++--        if (!isDuetEnabled()) return;
+++++++
++++++++--        
+++++++
++++++++--        const chatLog = document.getElementById("chat-log");
+++++++
++++++++-         const top = document.getElementById("duet-top");
+++++++
++++++++-         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++--        if (!chatLog) return;
+++++++
++++++++--        
+++++++
++++++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
++++++++--        // Actually, simpler approach for V1:
+++++++
++++++++--        // We only pin the LATEST. 
+++++++
++++++++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
++++++++--        // Move them to pins? No, that breaks history flow if they are old.
+++++++
++++++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
++++++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
++++++++--        // This implies visual displacement.
+++++++
++++++++--        
+++++++
++++++++--        // Better Strategy:
+++++++
++++++++--        // 1. Clear pins.
+++++++
++++++++--        // 2. Scan chatLog rows.
+++++++
++++++++--        // 3. Last row -> if user, move to bottom.
+++++++
++++++++--        // 4. Last ASSISTANT row -> move to top.
+++++++
++++++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
++++++++--        // This effectively empties the bottom of the history.
+++++++
++++++++--        
+++++++
++++++++--        // Implementation:
+++++++
++++++++--        // Find all .msg-row in chat main loop or chatLog
+++++++
++++++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
++++++++--        if (rows.length === 0) return;
+++++++
++++++++--        
+++++++
++++++++--        // Find last user row
+++++++
++++++++-+        const chatLog = document.getElementById("chat-log");
+++++++
++++++++-+
+++++++
++++++++-+        // Fallback for safety
+++++++
++++++++-+        if (!top || !bottom || !chatLog) return;
+++++++
++++++++-+
+++++++
++++++++-+        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++-+        // This ensures scanning always finds true chronological last messages
+++++++
++++++++-+        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++-+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++-+
+++++++
++++++++-+        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++-+        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++-+        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++-+        // This might reorder history if we aren't careful.
+++++++
++++++++-+        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++-+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++-+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++-+        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++-+        
+++++++
++++++++-+        // Sorting approach (safest for history):
+++++++
++++++++-+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++-+        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++-+        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++-+        
+++++++
++++++++-+        if (allRows.length === 0) return;
+++++++
++++++++-+
+++++++
++++++++-+        // 2. Scan for candidates
+++++++
++++++++-         let lastUserRow = null;
+++++++
++++++++-         let lastBotRow = null;
+++++++
++++++++--        
+++++++
++++++++-+
+++++++
++++++++-         // Scan backwards
+++++++
++++++++--        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
++++++++--            const r = rows[i];
+++++++
++++++++-+        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-+            const r = allRows[i];
+++++++
++++++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++-+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++-             if (lastUserRow && lastBotRow) break;
+++++++
++++++++-         }
+++++++
++++++++- 
+++++++
++++++++--        // Move to pins
+++++++
++++++++-+        // 3. Move to pins
+++++++
++++++++-         if (lastBotRow) {
+++++++
++++++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
++++++++--            // Ensure display is correct
+++++++
++++++++-+            top.appendChild(lastBotRow);
+++++++
++++++++-             top.style.display = 'block';
+++++++
++++++++-         } else {
+++++++
++++++++--            top.innerHTML = "";
+++++++
++++++++-             top.style.display = 'none';
+++++++
++++++++-         }
+++++++
++++++++--        
+++++++
++++++++-+
+++++++
++++++++-         if (lastUserRow) {
+++++++
++++++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++-+            bottom.appendChild(lastUserRow);
+++++++
++++++++-             bottom.style.display = 'block';
+++++++
++++++++-         } else {
+++++++
++++++++--            bottom.innerHTML = "";
+++++++
++++++++-             bottom.style.display = 'none';
+++++++
++++++++-         }
+++++++
++++++++-         
+++++++
++++++++--        // If we moved stuff, scroll might need adjustment? 
+++++++
++++++++--        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++-+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++-+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++-+        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++-+        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++-+        const scroll = document.getElementById("chat-view");
+++++++
++++++++-+        if (scroll) {
+++++++
++++++++-+             const botH = bottom.offsetHeight || 0;
+++++++
++++++++-+             const topH = top.offsetHeight || 0;
+++++++
++++++++-+             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++-+             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++-+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++-+        }
+++++++
++++++++-     }
+++++++
++++++++-     
+++++++
++++++++--    // No-op for old sync padding (CSS sticky handles it now)
+++++++
++++++++-     function syncDuetPadding() {}
+++++++
++++++++- 
+++++++
++++++++-     function updateDuetView(row, role) {
+++++++
++++++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++-+      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++-       requestAnimationFrame(applyDuetPins);
+++++++
++++++++-     }
+++++++
++++++++- 
+++++++
+++++++++# Cycle Status: COMPLETE
+++++++
+++++++++
+++++++
+++++++++## Todo Ledger
+++++++
+++++++++Completed:
+++++++
+++++++++- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
+++++++++
+++++++
+++++++++## Next Action
+++++++
+++++++++Commit
+++++++
+++++++++
+++++++
+++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
+++++++++index a78c1b7b..d6ca18ec 100644
+++++++
+++++++++--- a/othello_ui.html
+++++++
++++++++++++ b/othello_ui.html
+++++++
+++++++++@@ -339,6 +339,7 @@
+++++++
+++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
+++++++++         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
+++++++++         
+++++++
++++++++++        <!-- Only this is scrollable history -->
+++++++
+++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
+++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
+++++++++         <div id="chat-log" class="chat-log"></div>
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
+++++++++index 825c710b..c7cc1ae5 100644
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++++++ b/static/othello.css
+++++++
+++++++++@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* --- Duet Chat Mode (Unified) --- */
+++++++
+++++++++-/* Phase 2: Fix the scroll container */
+++++++
++++++++++/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
+++++++++ .chat-sheet {
+++++++
+++++++++   display: flex !important;
+++++++
+++++++++   flex-direction: column !important;
+++++++
+++++++++@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++ /* Header is rigid */
+++++++
+++++++++ .chat-sheet__header {
+++++++
+++++++++   flex: 0 0 auto;
+++++++
++++++++++  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++++  position: relative;
+++++++
++++++++++  box-shadow: 0 1px 0 var(--border);
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Input is rigid (footer) */
+++++++
+++++++++ .input-bar {
+++++++
+++++++++   flex: 0 0 auto;
+++++++
++++++++++  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++++  position: relative;
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Chat View IS the scroll container now */
+++++++
+++++++++@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++   background: rgba(15, 23, 42, 0.98);
+++++++
+++++++++   padding: 0.75rem;
+++++++
+++++++++   margin: 0;
+++++++
+++++++++-  display: block !important;
+++++++
++++++++++  display: block; /* always block, hidden by JS empty check if needed */
+++++++
+++++++++   backdrop-filter: blur(8px);
+++++++
+++++++++-  /* Ensure they don't shrink away */
+++++++
+++++++++   flex-shrink: 0; 
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
++++++++++/* Default hidden until populated */
+++++++
++++++++++.duet-pane:empty {
+++++++
++++++++++    display: none !important;
+++++++
++++++++++}
+++++++
++++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
+++++++++   top: 0;
+++++++
+++++++++   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
+++++++++@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
+++++++++   overflow: visible !important; /* Let parent scroll it */
+++++++
+++++++++   height: auto !important;
+++++++
+++++++++   padding: 1rem;
+++++++
++++++++++  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++++  padding-top: 1rem;
+++++++
++++++++++  padding-bottom: 1rem;
+++++++
+++++++++ }
+++++++
+++++++++ 
+++++++
+++++++++ /* Hide empty panes */
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
+++++++++index 3a092bfc..1a19d8a7 100644
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++++++ b/static/othello.js
+++++++
+++++++++@@ -4300,76 +4300,81 @@
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
+++++++++     }
+++++++
+++++++++ 
+++++++
+++++++++-    // Phase 3: Move nodes (no duplication)
+++++++
++++++++++    // Phase 3: Canonical Move
+++++++
+++++++++     function applyDuetPins() {
+++++++
+++++++++-        if (!isDuetEnabled()) return;
+++++++
+++++++++-        
+++++++
+++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
+++++++++-        if (!chatLog) return;
+++++++
+++++++++-        
+++++++
+++++++++-        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
+++++++++-        // Actually, simpler approach for V1:
+++++++
+++++++++-        // We only pin the LATEST. 
+++++++
+++++++++-        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
+++++++++-        // Move them to pins? No, that breaks history flow if they are old.
+++++++
+++++++++-        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
+++++++++-        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
+++++++++-        // This implies visual displacement.
+++++++
+++++++++-        
+++++++
+++++++++-        // Better Strategy:
+++++++
+++++++++-        // 1. Clear pins.
+++++++
+++++++++-        // 2. Scan chatLog rows.
+++++++
+++++++++-        // 3. Last row -> if user, move to bottom.
+++++++
+++++++++-        // 4. Last ASSISTANT row -> move to top.
+++++++
+++++++++-        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
+++++++++-        // This effectively empties the bottom of the history.
+++++++
+++++++++-        
+++++++
+++++++++-        // Implementation:
+++++++
+++++++++-        // Find all .msg-row in chat main loop or chatLog
+++++++
+++++++++-        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
+++++++++-        if (rows.length === 0) return;
+++++++
+++++++++-        
+++++++
+++++++++-        // Find last user row
+++++++
++++++++++        const chatLog = document.getElementById("chat-log");
+++++++
++++++++++
+++++++
++++++++++        // Fallback for safety
+++++++
++++++++++        if (!top || !bottom || !chatLog) return;
+++++++
++++++++++
+++++++
++++++++++        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++++        // This ensures scanning always finds true chronological last messages
+++++++
++++++++++        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++++        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++++
+++++++
++++++++++        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++++        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++++        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++++        // This might reorder history if we aren't careful.
+++++++
++++++++++        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++++        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++++        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++++        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++++        
+++++++
++++++++++        // Sorting approach (safest for history):
+++++++
++++++++++        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++++        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++++        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++++        
+++++++
++++++++++        if (allRows.length === 0) return;
+++++++
++++++++++
+++++++
++++++++++        // 2. Scan for candidates
+++++++
+++++++++         let lastUserRow = null;
+++++++
+++++++++         let lastBotRow = null;
+++++++
+++++++++-        
+++++++
++++++++++
+++++++
+++++++++         // Scan backwards
+++++++
+++++++++-        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
+++++++++-            const r = rows[i];
+++++++
++++++++++        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++++            const r = allRows[i];
+++++++
+++++++++             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
+++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++++            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
+++++++++             if (lastUserRow && lastBotRow) break;
+++++++
+++++++++         }
+++++++
+++++++++ 
+++++++
+++++++++-        // Move to pins
+++++++
++++++++++        // 3. Move to pins
+++++++
+++++++++         if (lastBotRow) {
+++++++
+++++++++-            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
+++++++++-            // Ensure display is correct
+++++++
++++++++++            top.appendChild(lastBotRow);
+++++++
+++++++++             top.style.display = 'block';
+++++++
+++++++++         } else {
+++++++
+++++++++-            top.innerHTML = "";
+++++++
+++++++++             top.style.display = 'none';
+++++++
+++++++++         }
+++++++
+++++++++-        
+++++++
++++++++++
+++++++
+++++++++         if (lastUserRow) {
+++++++
+++++++++-            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++++            bottom.appendChild(lastUserRow);
+++++++
+++++++++             bottom.style.display = 'block';
+++++++
+++++++++         } else {
+++++++
+++++++++-            bottom.innerHTML = "";
+++++++
+++++++++             bottom.style.display = 'none';
+++++++
+++++++++         }
+++++++
+++++++++         
+++++++
+++++++++-        // If we moved stuff, scroll might need adjustment? 
+++++++
+++++++++-        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++++        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++++        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++++        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++++        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++++        const scroll = document.getElementById("chat-view");
+++++++
++++++++++        if (scroll) {
+++++++
++++++++++             const botH = bottom.offsetHeight || 0;
+++++++
++++++++++             const topH = top.offsetHeight || 0;
+++++++
++++++++++             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++++             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++++             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++++        }
+++++++
+++++++++     }
+++++++
+++++++++     
+++++++
+++++++++-    // No-op for old sync padding (CSS sticky handles it now)
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
+++++++++ 
+++++++
+++++++++     function updateDuetView(row, role) {
+++++++
+++++++++-      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++++      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
+++++++++       requestAnimationFrame(applyDuetPins);
+++++++
+++++++++     }
+++++++
+++++++++ 
+++++++
+++++++++\n# Refactor: 3-Zone Layout\n
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++index 9b1f8845..382eeb57 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++@@ -2203,65 +2203,64 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Chat View IS the scroll container now */
+++++++
++++++++
+++++++
++++++++++/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++++
++++++++
+++++++
+++++++++ #chat-view {
+++++++
++++++++
+++++++
+++++++++   display: flex !important;
+++++++
++++++++
+++++++
+++++++++   flex-direction: column;
+++++++
++++++++
+++++++
+++++++++-  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++++
++++++++
+++++++
++++++++++  flex: 1 1 0;
+++++++
++++++++
+++++++
+++++++++   min-height: 0;
+++++++
++++++++
+++++++
+++++++++-  overflow-y: auto !important; /* The ONLY scrollbar */
+++++++
++++++++
+++++++
+++++++++-  overflow-x: hidden;
+++++++
++++++++
+++++++
++++++++++  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
++++++++
+++++++
+++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++-  padding: 0; /* Strict */
+++++++
++++++++
+++++++
++++++++++  padding: 0;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Duet Panes (Sticky) - Transparent Rails */
+++++++
++++++++
+++++++
++++++++++/* Duet Panes (Static Flex Items) */
+++++++
++++++++
+++++++
+++++++++ .duet-pane {
+++++++
++++++++
+++++++
+++++++++-  position: sticky;
+++++++
++++++++
+++++++
+++++++++-  z-index: 100; /* Must beat messages */
+++++++
++++++++
+++++++
+++++++++-  background: transparent; /* Transparent background */
+++++++
++++++++
+++++++
++++++++++  position: static; /* No longer sticky */
+++++++
++++++++
+++++++
++++++++++  flex: 0 0 auto; /* Rigid height based on content */
+++++++
++++++++
+++++++
++++++++++  z-index: 100;
+++++++
++++++++
+++++++
++++++++++  background: transparent;
+++++++
++++++++
+++++++
+++++++++   padding: 0.75rem;
+++++++
++++++++
+++++++
+++++++++   margin: 0;
+++++++
++++++++
+++++++
+++++++++-  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++
+++++++
+++++++++-  flex-shrink: 0;
+++++++
++++++++
+++++++
+++++++++-  pointer-events: none; /* Let clicks pass through empty space */
+++++++
++++++++
+++++++
++++++++++  display: block;
+++++++
++++++++
+++++++
++++++++++  pointer-events: none;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Re-enable pointer events on children (the bubbles) */
+++++++
++++++++
+++++++
+++++++++-.duet-pane > * {
+++++++
++++++++
+++++++
+++++++++-  pointer-events: auto;
+++++++
++++++++
+++++++
+++++++++-}
+++++++
++++++++
+++++++
++++++++++.duet-pane > * { pointer-events: auto; }
+++++++
++++++++
+++++++
++++++++++.duet-pane:empty { display: none !important; }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Default hidden until populated */
+++++++
++++++++
+++++++
+++++++++-.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++-    display: none !important;
+++++++
++++++++
+++++++
++++++++++/* Chat Log (Middle Scrollable History) */
+++++++
++++++++
+++++++
++++++++++#chat-log {
+++++++
++++++++
+++++++
++++++++++  display: flex !important;
+++++++
++++++++
+++++++
++++++++++  flex-direction: column;
+++++++
++++++++
+++++++
++++++++++  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++
+++++++
++++++++++  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++
+++++++
++++++++++  min-height: 0;
+++++++
++++++++
+++++++
++++++++++  height: auto !important;
+++++++
++++++++
+++++++
++++++++++  padding: 1rem;
+++++++
++++++++
+++++++
++++++++++  padding-top: 0.5rem;
+++++++
++++++++
+++++++
++++++++++  padding-bottom: 0.5rem;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++/* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++-  top: 0;
+++++++
++++++++
+++++++
+++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++-  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++-  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
++++++++++  order: 1;
+++++++
++++++++
+++++++
++++++++++  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
++++++++++}
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++#chat-log {
+++++++
++++++++
+++++++
++++++++++  order: 2; /* Middle */
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ .duet-pane--bottom {
+++++++
++++++++
+++++++
+++++++++-  bottom: 0;
+++++++
++++++++
+++++++
+++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++-  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++-  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
++++++++++  order: 3;
+++++++
++++++++
+++++++
++++++++++  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-/* Chat Log (History Flow) */
+++++++
++++++++
+++++++
+++++++++-#chat-log {
+++++++
++++++++
+++++++
+++++++++-  display: flex !important;
+++++++
++++++++
+++++++
+++++++++-  flex-direction: column;
+++++++
++++++++
+++++++
+++++++++-  flex: 1; /* occupy space between pins */
+++++++
++++++++
+++++++
+++++++++-  overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++
+++++++
+++++++++-  height: auto !important;
+++++++
++++++++
+++++++
+++++++++-  padding: 1rem;
+++++++
++++++++
+++++++
+++++++++-  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++
+++++++
+++++++++-  padding-top: 1rem;
+++++++
++++++++
+++++++
+++++++++-  padding-bottom: 1rem;
+++++++
++++++++
+++++++
++++++++++/* Ensure empty slots don't take space/border */
+++++++
++++++++
+++++++
++++++++++.duet-pane:empty {
+++++++
++++++++
+++++++
++++++++++    display: none !important;
+++++++
++++++++
+++++++
++++++++++    border: none !important;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ /* Hide empty panes */
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++index 1a19d8a7..2f438318 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++@@ -4300,7 +4300,7 @@
+++++++
++++++++
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    // Phase 3: Canonical Move
+++++++
++++++++
+++++++
++++++++++    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++
+++++++
+++++++++     function applyDuetPins() {
+++++++
++++++++
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++@@ -4308,67 +4308,79 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++         // Fallback for safety
+++++++
++++++++
+++++++
+++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++
+++++++
+++++++++-        // This ensures scanning always finds true chronological last messages
+++++++
++++++++
+++++++
+++++++++-        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++
+++++++
+++++++++-        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++
+++++++
+++++++++-        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++
+++++++
+++++++++-        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++
+++++++
+++++++++-        // This might reorder history if we aren't careful.
+++++++
++++++++
+++++++
+++++++++-        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++
+++++++
+++++++++-        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++
+++++++
+++++++++-        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++
+++++++
+++++++++-        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++
+++++++
+++++++++-        
+++++++
++++++++
+++++++
+++++++++-        // Sorting approach (safest for history):
+++++++
++++++++
+++++++
+++++++++-        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++
+++++++
+++++++++-        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++
+++++++
+++++++++-        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
++++++++++        // 1. Gather ALL message rows from all containers
+++++++
++++++++
+++++++
++++++++++        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++
+++++++
++++++++++        const allRows = [
+++++++
++++++++
+++++++
++++++++++            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
++++++++++            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
++++++++++            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++
+++++++
++++++++++        ];
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++         if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 2. Scan for candidates
+++++++
++++++++
+++++++
+++++++++-        let lastUserRow = null;
+++++++
++++++++
+++++++
+++++++++-        let lastBotRow = null;
+++++++
++++++++
+++++++
++++++++++        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++
+++++++
++++++++++        allRows.sort((a, b) => {
+++++++
++++++++
+++++++
++++++++++            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++
+++++++
++++++++++            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++
+++++++
++++++++++            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++
+++++++
++++++++++            
+++++++
++++++++
+++++++
++++++++++            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++
+++++++
++++++++++            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++
+++++++
++++++++++            return tsA - tsB;
+++++++
++++++++
+++++++
++++++++++        });
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // Scan backwards
+++++++
++++++++
+++++++
+++++++++-        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-            const r = allRows[i];
+++++++
++++++++
+++++++
+++++++++-            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++
+++++++
+++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++
+++++++
+++++++++-            if (lastUserRow && lastBotRow) break;
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // 3. Identify Candidates
+++++++
++++++++
+++++++
++++++++++        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++
+++++++
++++++++++        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        let targetTop = null;
+++++++
++++++++
+++++++
++++++++++        let targetBottom = null;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 3. Move to pins
+++++++
++++++++
+++++++
+++++++++-        if (lastBotRow) {
+++++++
++++++++
+++++++
+++++++++-            top.appendChild(lastBotRow);
+++++++
++++++++
+++++++
+++++++++-            top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++-            top.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        if (duetActive) {
+++++++
++++++++
+++++++
++++++++++             // Find last bot message
+++++++
++++++++
+++++++
++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
++++++++++                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++
+++++++
++++++++++                     targetTop = allRows[i];
+++++++
++++++++
+++++++
++++++++++                     break;
+++++++
++++++++
+++++++
++++++++++                 }
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
++++++++++             // Find last user message
+++++++
++++++++
+++++++
++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
++++++++++                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++
+++++++
++++++++++                     targetBottom = allRows[i];
+++++++
++++++++
+++++++
++++++++++                     break;
+++++++
++++++++
+++++++
++++++++++                 }
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
+++++++++         }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        if (lastUserRow) {
+++++++
++++++++
+++++++
+++++++++-            bottom.appendChild(lastUserRow);
+++++++
++++++++
+++++++
+++++++++-            bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++-            bottom.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // 4. Distribute Elements
+++++++
++++++++
+++++++
++++++++++        // Since we are sorting, we can just append in order.
+++++++
++++++++
+++++++
++++++++++        // However, we want 'chatLog' to have the history.
+++++++
++++++++
+++++++
++++++++++        // The pins get pulled out.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++
+++++++
+++++++++-        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++
+++++++
+++++++++-        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++
+++++++
+++++++++-        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++
+++++++
+++++++++-        const scroll = document.getElementById("chat-view");
+++++++
++++++++
+++++++
+++++++++-        if (scroll) {
+++++++
++++++++
+++++++
+++++++++-             const botH = bottom.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-             const topH = top.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++
+++++++
+++++++++-             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++
+++++++
+++++++++-             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
++++++++++        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++
+++++++
++++++++++        // Or just iterate and place.
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        allRows.forEach(row => {
+++++++
++++++++
+++++++
++++++++++            if (row === targetTop) {
+++++++
++++++++
+++++++
++++++++++                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                top.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++            } else if (row === targetBottom) {
+++++++
++++++++
+++++++
++++++++++                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                bottom.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++            } else {
+++++++
++++++++
+++++++
++++++++++                // Everything else goes to history
+++++++
++++++++
+++++++
++++++++++                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++
+++++++
++++++++++            }
+++++++
++++++++
+++++++
++++++++++        });
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        if (!targetTop) top.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        if (!targetBottom) bottom.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++        // 5. Scroll Management
+++++++
++++++++
+++++++
++++++++++        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++
+++++++
++++++++++        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++     
+++++++
++++++++
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++@@ -4601,6 +4613,8 @@
+++++++
++++++++
+++++++
+++++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++    let globalMessageSequence = 0;
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++     function addMessage(role, text, options = {}) {
+++++++
++++++++
+++++++
+++++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++++
++++++++
+++++++
+++++++++       // Hide chat placeholder when first message appears
+++++++
++++++++
+++++++
+++++++++@@ -4617,6 +4631,9 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       const row = document.createElement("div");
+++++++
++++++++
+++++++
+++++++++       row.className = `msg-row ${role}`;
+++++++
++++++++
+++++++
++++++++++      // Timestamp and Sequence for robust sorting
+++++++
++++++++
+++++++
++++++++++      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++++
++++++++
+++++++
++++++++++      row.dataset.sequence = ++globalMessageSequence;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       // Apply focus highlighting if a goal is focused
+++++++
++++++++
+++++++
+++++++++       if (othelloState.activeGoalId) {
+++++++
++++++++
+++++++
+++++++++\n# Refactor: Duet History & Archiving\n
+++++++
++++++++
+++++++
+++++++++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+++++++
++++++++
+++++++
+++++++++index 7aae5e35..6431d63e 100644
+++++++
++++++++
+++++++
+++++++++--- a/evidence/updatedifflog.md
+++++++
++++++++
+++++++
++++++++++++ b/evidence/updatedifflog.md
+++++++
++++++++
+++++++
+++++++++@@ -1,210 +1,484 @@
+++++++
++++++++
+++++++
+++++++++-# Cycle Status: COMPLETE
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-## Todo Ledger
+++++++
++++++++
+++++++
+++++++++-Completed:
+++++++
++++++++
+++++++
+++++++++-- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-## Next Action
+++++++
++++++++
+++++++
+++++++++-Commit
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++-index a78c1b7b..d6ca18ec 100644
+++++++
++++++++
+++++++
+++++++++---- a/othello_ui.html
+++++++
++++++++
+++++++
+++++++++-+++ b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++-@@ -339,6 +339,7 @@
+++++++
++++++++
+++++++
+++++++++-       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++
+++++++
+++++++++-         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++-         
+++++++
++++++++
+++++++
+++++++++-+        <!-- Only this is scrollable history -->
+++++++
++++++++
+++++++
+++++++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++
+++++++
+++++++++-         <div id="chat-log" class="chat-log"></div>
+++++++
++++++++
+++++++
+++++++++-diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++-index 825c710b..c7cc1ae5 100644
+++++++
++++++++
+++++++
+++++++++---- a/static/othello.css
+++++++
++++++++
+++++++
+++++++++-+++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++- }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++- /* --- Duet Chat Mode (Unified) --- */
+++++++
++++++++
+++++++
+++++++++--/* Phase 2: Fix the scroll container */
+++++++
++++++++
+++++++
+++++++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
++++++++
+++++++
+++++++++- .chat-sheet {
+++++++
++++++++
+++++++
+++++++++-   display: flex !important;
+++++++
++++++++
+++++++
+++++++++-   flex-direction: column !important;
+++++++
++++++++
+++++++
+++++++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++- /* Header is rigid */
+++++++
++++++++
+++++++
+++++++++- .chat-sheet__header {
+++++++
++++++++
+++++++
+++++++++-   flex: 0 0 auto;
+++++++
++++++++
+++++++
+++++++++-+  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++
+++++++
+++++++++-+  position: relative;
+++++++
++++++++
+++++++
+++++++++-+  box-shadow: 0 1px 0 var(--border);
+++++++
++++++++
+++++++
+++++++++- }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++- /* Input is rigid (footer) */
+++++++
++++++++
+++++++
+++++++++- .input-bar {
+++++++
++++++++
+++++++
+++++++++-   flex: 0 0 auto;
+++++++
++++++++
+++++++
+++++++++-+  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++
+++++++
+++++++++-+  position: relative;
+++++++
++++++++
+++++++
+++++++++- }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++- /* Chat View IS the scroll container now */
+++++++
++++++++
+++++++
+++++++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++-   background: rgba(15, 23, 42, 0.98);
+++++++
++++++++
+++++++
+++++++++-   padding: 0.75rem;
+++++++
++++++++
+++++++
+++++++++-   margin: 0;
+++++++
++++++++
+++++++
+++++++++--  display: block !important;
+++++++
++++++++
+++++++
+++++++++-+  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++
+++++++
+++++++++-   backdrop-filter: blur(8px);
+++++++
++++++++
+++++++
+++++++++--  /* Ensure they don't shrink away */
+++++++
++++++++
+++++++
+++++++++-   flex-shrink: 0; 
+++++++
++++++++
+++++++
+++++++++- }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++-+/* Default hidden until populated */
+++++++
++++++++
+++++++
+++++++++-+.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++-+    display: none !important;
+++++++
++++++++
+++++++
+++++++++-+}
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++- .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++-   top: 0;
+++++++
++++++++
+++++++
+++++++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
++++++++
+++++++
+++++++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++-   overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++
+++++++
+++++++++-   height: auto !important;
+++++++
++++++++
+++++++
+++++++++-   padding: 1rem;
+++++++
++++++++
+++++++
+++++++++-+  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++
+++++++
+++++++++-+  padding-top: 1rem;
+++++++
++++++++
+++++++
+++++++++-+  padding-bottom: 1rem;
+++++++
++++++++
+++++++
+++++++++- }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++- /* Hide empty panes */
+++++++
++++++++
+++++++
+++++++++-diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++-index 3a092bfc..1a19d8a7 100644
+++++++
++++++++
+++++++
+++++++++---- a/static/othello.js
+++++++
++++++++
+++++++
+++++++++-+++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++-@@ -4300,76 +4300,81 @@
+++++++
++++++++
+++++++
+++++++++-       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++-     }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++--    // Phase 3: Move nodes (no duplication)
+++++++
++++++++
+++++++
+++++++++-+    // Phase 3: Canonical Move
+++++++
++++++++
+++++++
+++++++++-     function applyDuetPins() {
+++++++
++++++++
+++++++
+++++++++--        if (!isDuetEnabled()) return;
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++--        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
+++++++++-         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++-         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++--        if (!chatLog) return;
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
++++++++
+++++++
+++++++++--        // Actually, simpler approach for V1:
+++++++
++++++++
+++++++
+++++++++--        // We only pin the LATEST. 
+++++++
++++++++
+++++++
+++++++++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
++++++++
+++++++
+++++++++--        // Move them to pins? No, that breaks history flow if they are old.
+++++++
++++++++
+++++++
+++++++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
++++++++
+++++++
+++++++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
++++++++
+++++++
+++++++++--        // This implies visual displacement.
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++--        // Better Strategy:
+++++++
++++++++
+++++++
+++++++++--        // 1. Clear pins.
+++++++
++++++++
+++++++
+++++++++--        // 2. Scan chatLog rows.
+++++++
++++++++
+++++++
+++++++++--        // 3. Last row -> if user, move to bottom.
+++++++
++++++++
+++++++
+++++++++--        // 4. Last ASSISTANT row -> move to top.
+++++++
++++++++
+++++++
+++++++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
++++++++
+++++++
+++++++++--        // This effectively empties the bottom of the history.
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++--        // Implementation:
+++++++
++++++++
+++++++
+++++++++--        // Find all .msg-row in chat main loop or chatLog
+++++++
++++++++
+++++++
+++++++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
++++++++
+++++++
+++++++++--        if (rows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++--        // Find last user row
+++++++
++++++++
+++++++
+++++++++-+        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-+        // Fallback for safety
+++++++
++++++++
+++++++
+++++++++-+        if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-+        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++
+++++++
+++++++++-+        // This ensures scanning always finds true chronological last messages
+++++++
++++++++
+++++++
+++++++++-+        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++
+++++++
+++++++++-+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-+        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++
+++++++
+++++++++-+        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++
+++++++
+++++++++-+        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++
+++++++
+++++++++-+        // This might reorder history if we aren't careful.
+++++++
++++++++
+++++++
+++++++++-+        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++
+++++++
+++++++++-+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++
+++++++
+++++++++-+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++
+++++++
+++++++++-+        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++
+++++++
+++++++++-+        
+++++++
++++++++
+++++++
+++++++++-+        // Sorting approach (safest for history):
+++++++
++++++++
+++++++
+++++++++-+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++
+++++++
+++++++++-+        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++
+++++++
+++++++++-+        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++
+++++++
+++++++++-+        
+++++++
++++++++
+++++++
+++++++++-+        if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-+        // 2. Scan for candidates
+++++++
++++++++
+++++++
+++++++++-         let lastUserRow = null;
+++++++
++++++++
+++++++
+++++++++-         let lastBotRow = null;
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-         // Scan backwards
+++++++
++++++++
+++++++
+++++++++--        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++--            const r = rows[i];
+++++++
++++++++
+++++++
+++++++++-+        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-+            const r = allRows[i];
+++++++
++++++++
+++++++
+++++++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++
+++++++
+++++++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++
+++++++
+++++++++-+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++
+++++++
+++++++++-             if (lastUserRow && lastBotRow) break;
+++++++
++++++++
+++++++
+++++++++-         }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++--        // Move to pins
+++++++
++++++++
+++++++
+++++++++-+        // 3. Move to pins
+++++++
++++++++
+++++++
+++++++++-         if (lastBotRow) {
+++++++
++++++++
+++++++
+++++++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
++++++++
+++++++
+++++++++--            // Ensure display is correct
+++++++
++++++++
+++++++
+++++++++-+            top.appendChild(lastBotRow);
+++++++
++++++++
+++++++
+++++++++-             top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-         } else {
+++++++
++++++++
+++++++
+++++++++--            top.innerHTML = "";
+++++++
++++++++
+++++++
+++++++++-             top.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-         }
+++++++
++++++++
+++++++
+++++++++--        
+++++++
++++++++
+++++++
+++++++++-+
+++++++
++++++++
+++++++
+++++++++-         if (lastUserRow) {
+++++++
++++++++
+++++++
+++++++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++
+++++++
+++++++++-+            bottom.appendChild(lastUserRow);
+++++++
++++++++
+++++++
+++++++++-             bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-         } else {
+++++++
++++++++
+++++++
+++++++++--            bottom.innerHTML = "";
+++++++
++++++++
+++++++
+++++++++-             bottom.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-         }
+++++++
++++++++
+++++++
+++++++++-         
+++++++
++++++++
+++++++
+++++++++--        // If we moved stuff, scroll might need adjustment? 
+++++++
++++++++
+++++++
+++++++++--        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++
+++++++
+++++++++-+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++
+++++++
+++++++++-+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++
+++++++
+++++++++-+        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++
+++++++
+++++++++-+        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++
+++++++
+++++++++-+        const scroll = document.getElementById("chat-view");
+++++++
++++++++
+++++++
+++++++++-+        if (scroll) {
+++++++
++++++++
+++++++
+++++++++-+             const botH = bottom.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-+             const topH = top.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++-+             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++
+++++++
+++++++++-+             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++
+++++++
+++++++++-+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++
+++++++
+++++++++-+        }
+++++++
++++++++
+++++++
+++++++++-     }
+++++++
++++++++
+++++++
+++++++++-     
+++++++
++++++++
+++++++
+++++++++--    // No-op for old sync padding (CSS sticky handles it now)
+++++++
++++++++
+++++++
+++++++++-     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
+++++++++-     function updateDuetView(row, role) {
+++++++
++++++++
+++++++
+++++++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++
+++++++
+++++++++-+      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++
+++++++
+++++++++-       requestAnimationFrame(applyDuetPins);
+++++++
++++++++
+++++++
+++++++++-     }
+++++++
++++++++
+++++++
+++++++++- 
+++++++
++++++++
+++++++
++++++++++# Cycle Status: COMPLETE
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++## Todo Ledger
+++++++
++++++++
+++++++
++++++++++Completed:
+++++++
++++++++
+++++++
++++++++++- [x] Fix Overlap & Duplicates (Duet Chat)
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++## Next Action
+++++++
++++++++
+++++++
++++++++++Commit
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++
+++++++
++++++++++index a78c1b7b..d6ca18ec 100644
+++++++
++++++++
+++++++
++++++++++--- a/othello_ui.html
+++++++
++++++++
+++++++
+++++++++++++ b/othello_ui.html
+++++++
++++++++
+++++++
++++++++++@@ -339,6 +339,7 @@
+++++++
++++++++
+++++++
++++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++
+++++++
++++++++++         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++         
+++++++
++++++++
+++++++
+++++++++++        <!-- Only this is scrollable history -->
+++++++
++++++++
+++++++
++++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++
+++++++
++++++++++         <div id="chat-log" class="chat-log"></div>
+++++++
++++++++
+++++++
++++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
++++++++++index 825c710b..c7cc1ae5 100644
+++++++
++++++++
+++++++
++++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
+++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
++++++++++@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++ /* --- Duet Chat Mode (Unified) --- */
+++++++
++++++++
+++++++
++++++++++-/* Phase 2: Fix the scroll container */
+++++++
++++++++
+++++++
+++++++++++/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++++
++++++++
+++++++
++++++++++ .chat-sheet {
+++++++
++++++++
+++++++
++++++++++   display: flex !important;
+++++++
++++++++
+++++++
++++++++++   flex-direction: column !important;
+++++++
++++++++
+++++++
++++++++++@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
++++++++++ /* Header is rigid */
+++++++
++++++++
+++++++
++++++++++ .chat-sheet__header {
+++++++
++++++++
+++++++
++++++++++   flex: 0 0 auto;
+++++++
++++++++
+++++++
+++++++++++  z-index: 200; /* Header stays absolutely on top */
+++++++
++++++++
+++++++
+++++++++++  position: relative;
+++++++
++++++++
+++++++
+++++++++++  box-shadow: 0 1px 0 var(--border);
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++ /* Input is rigid (footer) */
+++++++
++++++++
+++++++
++++++++++ .input-bar {
+++++++
++++++++
+++++++
++++++++++   flex: 0 0 auto;
+++++++
++++++++
+++++++
+++++++++++  z-index: 200; /* Input stays absolutely on top */
+++++++
++++++++
+++++++
+++++++++++  position: relative;
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++ /* Chat View IS the scroll container now */
+++++++
++++++++
+++++++
++++++++++@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
++++++++++   background: rgba(15, 23, 42, 0.98);
+++++++
++++++++
+++++++
++++++++++   padding: 0.75rem;
+++++++
++++++++
+++++++
++++++++++   margin: 0;
+++++++
++++++++
+++++++
++++++++++-  display: block !important;
+++++++
++++++++
+++++++
+++++++++++  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++
+++++++
++++++++++   backdrop-filter: blur(8px);
+++++++
++++++++
+++++++
++++++++++-  /* Ensure they don't shrink away */
+++++++
++++++++
+++++++
++++++++++   flex-shrink: 0; 
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++++/* Default hidden until populated */
+++++++
++++++++
+++++++
+++++++++++.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++++    display: none !important;
+++++++
++++++++
+++++++
+++++++++++}
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
++++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
++++++++++   top: 0;
+++++++
++++++++
+++++++
++++++++++   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++++
++++++++
+++++++
++++++++++@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
++++++++++   overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++
+++++++
++++++++++   height: auto !important;
+++++++
++++++++
+++++++
++++++++++   padding: 1rem;
+++++++
++++++++
+++++++
+++++++++++  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++
+++++++
+++++++++++  padding-top: 1rem;
+++++++
++++++++
+++++++
+++++++++++  padding-bottom: 1rem;
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++ /* Hide empty panes */
+++++++
++++++++
+++++++
++++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
++++++++++index 3a092bfc..1a19d8a7 100644
+++++++
++++++++
+++++++
++++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
+++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
++++++++++@@ -4300,76 +4300,81 @@
+++++++
++++++++
+++++++
++++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++-    // Phase 3: Move nodes (no duplication)
+++++++
++++++++
+++++++
+++++++++++    // Phase 3: Canonical Move
+++++++
++++++++
+++++++
++++++++++     function applyDuetPins() {
+++++++
++++++++
+++++++
++++++++++-        if (!isDuetEnabled()) return;
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
++++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
++++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
++++++++++-        if (!chatLog) return;
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
++++++++++-        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++++
++++++++
+++++++
++++++++++-        // Actually, simpler approach for V1:
+++++++
++++++++
+++++++
++++++++++-        // We only pin the LATEST. 
+++++++
++++++++
+++++++
++++++++++-        // Iterate chatLog children. Find last user msg, last bot msg.
+++++++
++++++++
+++++++
++++++++++-        // Move them to pins? No, that breaks history flow if they are old.
+++++++
++++++++
+++++++
++++++++++-        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++++
++++++++
+++++++
++++++++++-        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++++
++++++++
+++++++
++++++++++-        // This implies visual displacement.
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
++++++++++-        // Better Strategy:
+++++++
++++++++
+++++++
++++++++++-        // 1. Clear pins.
+++++++
++++++++
+++++++
++++++++++-        // 2. Scan chatLog rows.
+++++++
++++++++
+++++++
++++++++++-        // 3. Last row -> if user, move to bottom.
+++++++
++++++++
+++++++
++++++++++-        // 4. Last ASSISTANT row -> move to top.
+++++++
++++++++
+++++++
++++++++++-        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++++
++++++++
+++++++
++++++++++-        // This effectively empties the bottom of the history.
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
++++++++++-        // Implementation:
+++++++
++++++++
+++++++
++++++++++-        // Find all .msg-row in chat main loop or chatLog
+++++++
++++++++
+++++++
++++++++++-        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++++
++++++++
+++++++
++++++++++-        if (rows.length === 0) return;
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
++++++++++-        // Find last user row
+++++++
++++++++
+++++++
+++++++++++        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++++        // Fallback for safety
+++++++
++++++++
+++++++
+++++++++++        if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++++        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++
+++++++
+++++++++++        // This ensures scanning always finds true chronological last messages
+++++++
++++++++
+++++++
+++++++++++        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++
+++++++
+++++++++++        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++++        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++
+++++++
+++++++++++        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++
+++++++
+++++++++++        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++
+++++++
+++++++++++        // This might reorder history if we aren't careful.
+++++++
++++++++
+++++++
+++++++++++        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++
+++++++
+++++++++++        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++
+++++++
+++++++++++        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++
+++++++
+++++++++++        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++
+++++++
+++++++++++        
+++++++
++++++++
+++++++
+++++++++++        // Sorting approach (safest for history):
+++++++
++++++++
+++++++
+++++++++++        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++
+++++++
+++++++++++        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++
+++++++
+++++++++++        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++
+++++++
+++++++++++        
+++++++
++++++++
+++++++
+++++++++++        if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++++        // 2. Scan for candidates
+++++++
++++++++
+++++++
++++++++++         let lastUserRow = null;
+++++++
++++++++
+++++++
++++++++++         let lastBotRow = null;
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
++++++++++         // Scan backwards
+++++++
++++++++
+++++++
++++++++++-        for (let i = rows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
++++++++++-            const r = rows[i];
+++++++
++++++++
+++++++
+++++++++++        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++++            const r = allRows[i];
+++++++
++++++++
+++++++
++++++++++             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++
+++++++
++++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++
++++++++
+++++++
+++++++++++            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++
+++++++
++++++++++             if (lastUserRow && lastBotRow) break;
+++++++
++++++++
+++++++
++++++++++         }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++-        // Move to pins
+++++++
++++++++
+++++++
+++++++++++        // 3. Move to pins
+++++++
++++++++
+++++++
++++++++++         if (lastBotRow) {
+++++++
++++++++
+++++++
++++++++++-            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++++
++++++++
+++++++
++++++++++-            // Ensure display is correct
+++++++
++++++++
+++++++
+++++++++++            top.appendChild(lastBotRow);
+++++++
++++++++
+++++++
++++++++++             top.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++         } else {
+++++++
++++++++
+++++++
++++++++++-            top.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++             top.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++         }
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
++++++++++         if (lastUserRow) {
+++++++
++++++++
+++++++
++++++++++-            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++
++++++++
+++++++
+++++++++++            bottom.appendChild(lastUserRow);
+++++++
++++++++
+++++++
++++++++++             bottom.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++         } else {
+++++++
++++++++
+++++++
++++++++++-            bottom.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++             bottom.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++         }
+++++++
++++++++
+++++++
++++++++++         
+++++++
++++++++
+++++++
++++++++++-        // If we moved stuff, scroll might need adjustment? 
+++++++
++++++++
+++++++
++++++++++-        // Sticky logic handles the pins. History fills the middle.
+++++++
++++++++
+++++++
+++++++++++        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++
+++++++
+++++++++++        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++
+++++++
+++++++++++        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++
+++++++
+++++++++++        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++
+++++++
+++++++++++        const scroll = document.getElementById("chat-view");
+++++++
++++++++
+++++++
+++++++++++        if (scroll) {
+++++++
++++++++
+++++++
+++++++++++             const botH = bottom.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++++             const topH = top.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++++             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++
+++++++
+++++++++++             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++
+++++++
+++++++++++             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++
+++++++
+++++++++++        }
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
++++++++++     
+++++++
++++++++
+++++++
++++++++++-    // No-op for old sync padding (CSS sticky handles it now)
+++++++
++++++++
+++++++
++++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++     function updateDuetView(row, role) {
+++++++
++++++++
+++++++
++++++++++-      // Defer to applyDuetPins in next frame to let DOM settle
+++++++
++++++++
+++++++
+++++++++++      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++
+++++++
++++++++++       requestAnimationFrame(applyDuetPins);
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
++++++++++\n# Refactor: 3-Zone Layout\n
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++index 9b1f8845..382eeb57 100644
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++@@ -2203,65 +2203,64 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-/* Chat View IS the scroll container now */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ #chat-view {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   display: flex !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   flex-direction: column;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  flex: 1 1 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   min-height: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  overflow-y: auto !important; /* The ONLY scrollbar */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  overflow-x: hidden;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  padding: 0; /* Strict */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  padding: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-/* Duet Panes (Sticky) - Transparent Rails */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++/* Duet Panes (Static Flex Items) */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ .duet-pane {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  position: sticky;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  z-index: 100; /* Must beat messages */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  background: transparent; /* Transparent background */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  position: static; /* No longer sticky */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  flex: 0 0 auto; /* Rigid height based on content */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  z-index: 100;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  background: transparent;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   padding: 0.75rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++   margin: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  display: block; /* always block, hidden by JS empty check if needed */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  flex-shrink: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  pointer-events: none; /* Let clicks pass through empty space */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  display: block;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  pointer-events: none;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-/* Re-enable pointer events on children (the bubbles) */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-.duet-pane > * {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  pointer-events: auto;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-}
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++.duet-pane > * { pointer-events: auto; }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++.duet-pane:empty { display: none !important; }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-/* Default hidden until populated */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-    display: none !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++/* Chat Log (Middle Scrollable History) */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++#chat-log {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  display: flex !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  flex-direction: column;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  min-height: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  height: auto !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  padding: 1rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  padding-top: 0.5rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  padding-bottom: 0.5rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++/* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  top: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  order: 1;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++}
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++#chat-log {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  order: 2; /* Middle */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ .duet-pane--bottom {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  bottom: 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* Removed border/shadow for clean look */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  order: 3;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-/* Chat Log (History Flow) */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-#chat-log {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  display: flex !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  flex-direction: column;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  flex: 1; /* occupy space between pins */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  overflow: visible !important; /* Let parent scroll it */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  height: auto !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  padding: 1rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  padding-top: 1rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-  padding-bottom: 1rem;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++/* Ensure empty slots don't take space/border */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++.duet-pane:empty {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++    display: none !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++    border: none !important;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ /* Hide empty panes */
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++index 1a19d8a7..2f438318 100644
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++@@ -4300,7 +4300,7 @@
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-    // Phase 3: Canonical Move
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     function applyDuetPins() {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++@@ -4308,67 +4308,79 @@
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         // Fallback for safety
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // 1. Move ALL pinned items BACK to chatLog first to restore order
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // This ensures scanning always finds true chronological last messages
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        while (top.firstChild) chatLog.appendChild(top.firstChild);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // Sort chatLog by DOM order? No, appendChild moves to end.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // We need to re-sort? No, they were originally at end. 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // NOTE: If we move old pinned items back, they append to END. 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // This might reorder history if we aren't careful.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // TRICKY: We need to know where they CAME from to un-pin correctly.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // BUT: If a new message arrived, we want THAT to be pinned.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // Sorting approach (safest for history):
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // If we strictly pin the last ones, unpinning means they go back to end.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // New messages are appended to end. So order is preserved naturally.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // 1. Gather ALL message rows from all containers
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        const allRows = [
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        ];
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // 2. Scan for candidates
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        let lastUserRow = null;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        let lastBotRow = null;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        allRows.sort((a, b) => {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            return tsA - tsB;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        });
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // Scan backwards
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            const r = allRows[i];
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            if (lastUserRow && lastBotRow) break;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // 3. Identify Candidates
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        let targetTop = null;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        let targetBottom = null;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // 3. Move to pins
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        if (lastBotRow) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            top.appendChild(lastBotRow);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            top.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        if (duetActive) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             // Find last bot message
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                     targetTop = allRows[i];
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                     break;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                 }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             // Find last user message
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                     targetBottom = allRows[i];
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                     break;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                 }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++             }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        if (lastUserRow) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            bottom.appendChild(lastUserRow);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        } else {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-            bottom.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // 4. Distribute Elements
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // Since we are sorting, we can just append in order.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // However, we want 'chatLog' to have the history.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // The pins get pulled out.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++         
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        // CSS 'scroll-padding-bottom' on container helps.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        const scroll = document.getElementById("chat-view");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        if (scroll) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-             const botH = bottom.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-             const topH = top.offsetHeight || 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-             // Add extra padding to LOG so it can scroll fully into view
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-             chatLog.style.paddingBottom = (botH + 20) + "px";
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++-        }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // Or just iterate and place.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        allRows.forEach(row => {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            if (row === targetTop) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            } else if (row === targetBottom) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            } else {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                // Everything else goes to history
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++            }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        });
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        if (!targetTop) top.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        if (!targetBottom) bottom.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // 5. Scroll Management
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++@@ -4601,6 +4613,8 @@
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     }
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++    let globalMessageSequence = 0;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++     function addMessage(role, text, options = {}) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       // Hide chat placeholder when first message appears
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++@@ -4617,6 +4631,9 @@
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       const row = document.createElement("div");
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       row.className = `msg-row ${role}`;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++      // Timestamp and Sequence for robust sorting
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
+++++++++++      row.dataset.sequence = ++globalMessageSequence;
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++ 
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       // Apply focus highlighting if a goal is focused
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++       if (othelloState.activeGoalId) {
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++\ No newline at end of file
+++++++
++++++++
+++++++
+++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++index d6ca18ec..dce7fa4a 100644
+++++++
++++++++
+++++++
+++++++++--- a/othello_ui.html
+++++++
++++++++
+++++++
++++++++++++ b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++@@ -342,7 +342,12 @@
+++++++
++++++++
+++++++
+++++++++         <!-- Only this is scrollable history -->
+++++++
++++++++
+++++++
+++++++++         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++
+++++++
+++++++++-        <div id="chat-log" class="chat-log"></div>
+++++++
++++++++
+++++++
++++++++++        <!-- Renamed/Aliased for clarity as requested, but keeping ID if preferred by CSS. 
+++++++
++++++++
+++++++
++++++++++             User asked for #duet-history. Let's make it explicit. 
+++++++
++++++++
+++++++
++++++++++             We can keep chat-log class for styling compatibility if needed. -->
+++++++
++++++++
+++++++
++++++++++        <div id="duet-history" class="chat-log" style="overflow-y:auto; flex:1 1 auto;">
+++++++
++++++++
+++++++
++++++++++           <div id="duet-history-spacer" aria-hidden="true" style="height:0px;"></div>
+++++++
++++++++
+++++++
++++++++++        </div>
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++       </div>
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++index 382eeb57..85512fda 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++@@ -2230,7 +2230,9 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++ .duet-pane:empty { display: none !important; }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ /* Chat Log (Middle Scrollable History) */
+++++++
++++++++
+++++++
+++++++++-#chat-log {
+++++++
++++++++
+++++++
++++++++++/* Changed to #duet-history in DOM, but kept .chat-log class. 
+++++++
++++++++
+++++++
++++++++++   Target generic .chat-log or specific #duet-history */
+++++++
++++++++
+++++++
++++++++++#chat-log, #duet-history {
+++++++
++++++++
+++++++
+++++++++   display: flex !important;
+++++++
++++++++
+++++++
+++++++++   flex-direction: column;
+++++++
++++++++
+++++++
+++++++++   flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++
+++++++
+++++++++@@ -2242,6 +2244,11 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++   padding-bottom: 0.5rem;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++#duet-history-spacer {
+++++++
++++++++
+++++++
++++++++++    flex: 0 0 auto;
+++++++
++++++++
+++++++
++++++++++    width: 100%;
+++++++
++++++++
+++++++
++++++++++}
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++ /* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++   order: 1;
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++index 2f438318..618d8127 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++@@ -793,7 +793,8 @@
+++++++
++++++++
+++++++
+++++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++
++++++++
+++++++
+++++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    const chatLog = document.getElementById('chat-log');
+++++++
++++++++
+++++++
++++++++++    // Updated to support new Duet History container
+++++++
++++++++
+++++++
++++++++++    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++
++++++++
+++++++
+++++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++
++++++++
+++++++
+++++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++
++++++++
+++++++
+++++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++
++++++++
+++++++
+++++++++@@ -4300,94 +4301,87 @@
+++++++
++++++++
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++
+++++++
+++++++++-    function applyDuetPins() {
+++++++
++++++++
+++++++
++++++++++    // Phase 4: Duet Padding & Spacer Logic
+++++++
++++++++
+++++++
++++++++++    function syncDuetHistorySpacer() {
+++++++
++++++++
+++++++
++++++++++       const history = document.getElementById("duet-history");
+++++++
++++++++
+++++++
++++++++++       const spacer = document.getElementById("duet-history-spacer");
+++++++
++++++++
+++++++
++++++++++       if (!history || !spacer) return;
+++++++
++++++++
+++++++
++++++++++       // The spacer forces the content to be initially "above the fold" 
+++++++
++++++++
+++++++
++++++++++       // if we are scrolled to bottom.
+++++++
++++++++
+++++++
++++++++++       spacer.style.height = `${history.clientHeight}px`;
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    function scrollDuetHistoryToBottom() {
+++++++
++++++++
+++++++
++++++++++       const history = document.getElementById("duet-history");
+++++++
++++++++
+++++++
++++++++++       if (!history) return;
+++++++
++++++++
+++++++
++++++++++       history.scrollTop = history.scrollHeight;
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    // Call on resize
+++++++
++++++++
+++++++
++++++++++    window.addEventListener("resize", () => {
+++++++
++++++++
+++++++
++++++++++        syncDuetHistorySpacer();
+++++++
++++++++
+++++++
++++++++++    });
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++
++++++++
+++++++
++++++++++    function archivePinnedToHistory() {
+++++++
++++++++
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++        const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++        const spacer = document.getElementById("duet-history-spacer");
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++         // Fallback for safety
+++++++
++++++++
+++++++
+++++++++         if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        // 1. Gather ALL message rows from all containers
+++++++
++++++++
+++++++
+++++++++-        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++
+++++++
+++++++++-        const allRows = [
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++
+++++++
+++++++++-        ];
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++
+++++++
+++++++++-        allRows.sort((a, b) => {
+++++++
++++++++
+++++++
+++++++++-            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++-            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++-            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++
+++++++
+++++++++-            
+++++++
++++++++
+++++++
+++++++++-            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++-            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++-            return tsA - tsB;
+++++++
++++++++
+++++++
+++++++++-        });
+++++++
++++++++
+++++++
++++++++++        // 1. Check if user is at bottom BEFORE modifying
+++++++
++++++++
+++++++
++++++++++        // Threshold of 50px
+++++++
++++++++
+++++++
++++++++++        const isAtBottom = (chatLog.scrollHeight - chatLog.scrollTop - chatLog.clientHeight) < 50;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 3. Identify Candidates
+++++++
++++++++
+++++++
+++++++++-        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++
+++++++
+++++++++-        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++
+++++++
++++++++++        // 2. Archive items from pins to history (chronological insert before spacer)
+++++++
++++++++
+++++++
++++++++++        // Note: top messages came BEFORE bottom messages in time (usually).
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        let targetTop = null;
+++++++
++++++++
+++++++
+++++++++-        let targetBottom = null;
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        if (duetActive) {
+++++++
++++++++
+++++++
+++++++++-             // Find last bot message
+++++++
++++++++
+++++++
+++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++
+++++++
+++++++++-                     targetTop = allRows[i];
+++++++
++++++++
+++++++
+++++++++-                     break;
+++++++
++++++++
+++++++
+++++++++-                 }
+++++++
++++++++
+++++++
+++++++++-             }
+++++++
++++++++
+++++++
+++++++++-             // Find last user message
+++++++
++++++++
+++++++
+++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++
+++++++
+++++++++-                     targetBottom = allRows[i];
+++++++
++++++++
+++++++
+++++++++-                     break;
+++++++
++++++++
+++++++
+++++++++-                 }
+++++++
++++++++
+++++++
+++++++++-             }
+++++++
++++++++
+++++++
+++++++++-        }
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 4. Distribute Elements
+++++++
++++++++
+++++++
+++++++++-        // Since we are sorting, we can just append in order.
+++++++
++++++++
+++++++
+++++++++-        // However, we want 'chatLog' to have the history.
+++++++
++++++++
+++++++
+++++++++-        // The pins get pulled out.
+++++++
++++++++
+++++++
++++++++++        // We move ALL children of top and bottom to history?
+++++++
++++++++
+++++++
++++++++++        // Yes, because this is called "on new send" to clear the stage.
+++++++
++++++++
+++++++
++++++++++        // We should sort them? 
+++++++
++++++++
+++++++
++++++++++        // If we assume Top is "Last Bot" and Bottom is "Last User", then Top implies an earlier event IF the user just replied.
+++++++
++++++++
+++++++
++++++++++        // But usually: Bot (Top) -> User (Bottom).
+++++++
++++++++
+++++++
++++++++++        // So correct order is Top content -> Bottom content.
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        const topNodes = Array.from(top.children);
+++++++
++++++++
+++++++
++++++++++        const bottomNodes = Array.from(bottom.children);
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++
+++++++
+++++++++-        // Or just iterate and place.
+++++++
++++++++
+++++++
++++++++++        const fragment = document.createDocumentFragment();
+++++++
++++++++
+++++++
++++++++++        topNodes.forEach(n => fragment.appendChild(n));
+++++++
++++++++
+++++++
++++++++++        bottomNodes.forEach(n => fragment.appendChild(n));
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        allRows.forEach(row => {
+++++++
++++++++
+++++++
+++++++++-            if (row === targetTop) {
+++++++
++++++++
+++++++
+++++++++-                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++
+++++++
+++++++++-                top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-            } else if (row === targetBottom) {
+++++++
++++++++
+++++++
+++++++++-                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++
+++++++
+++++++++-                bottom.style.display = 'block';
+++++++
++++++++
+++++++
++++++++++        if (fragment.children.length > 0) {
+++++++
++++++++
+++++++
++++++++++            if (spacer) {
+++++++
++++++++
+++++++
++++++++++                chatLog.insertBefore(fragment, spacer);
+++++++
++++++++
+++++++
+++++++++             } else {
+++++++
++++++++
+++++++
+++++++++-                // Everything else goes to history
+++++++
++++++++
+++++++
+++++++++-                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                chatLog.appendChild(fragment);
+++++++
++++++++
+++++++
+++++++++             }
+++++++
++++++++
+++++++
+++++++++-        });
+++++++
++++++++
+++++++
++++++++++        }
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        // Clear pins (implicit by appendChild movement, but ensure empty state)
+++++++
++++++++
+++++++
++++++++++        // If nodes were cloned, we'd need to clear. appenChild moves them.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        if (!targetTop) top.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-        if (!targetBottom) bottom.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        // 3. Maintain Scroll Position
+++++++
++++++++
+++++++
++++++++++        if (isAtBottom) {
+++++++
++++++++
+++++++
++++++++++             scrollDuetHistoryToBottom();
+++++++
++++++++
+++++++
++++++++++        }
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 5. Scroll Management
+++++++
++++++++
+++++++
+++++++++-        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++
+++++++
+++++++++-        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++
+++++++
++++++++++    // Deprecated / Aliased
+++++++
++++++++
+++++++
++++++++++    function applyDuetPins() {
+++++++
++++++++
+++++++
++++++++++        // No-op or alias to archive? 
+++++++
++++++++
+++++++
++++++++++        // We only want to archive on SPECIFIC events (new send), not every render loop.
+++++++
++++++++
+++++++
++++++++++        // So we leave this empty to stop auto-magic behavior.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++     
+++++++
++++++++
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function updateDuetView(row, role) {
+++++++
++++++++
+++++++
+++++++++-      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++
+++++++
+++++++++-      requestAnimationFrame(applyDuetPins);
+++++++
++++++++
+++++++
++++++++++      // In new model, we don't automatically pin everything.
+++++++
++++++++
+++++++
++++++++++      // addMessage handles the routing.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function bindDuetListeners() {
+++++++
++++++++
+++++++
+++++++++@@ -4399,13 +4393,12 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function getChatContainer() {
+++++++
++++++++
+++++++
+++++++++       // Phase 4: Target the real scroll container for appending?
+++++++
++++++++
+++++++
+++++++++-      // No, we append to chat-log. The VIEW is the scroller.
+++++++
++++++++
+++++++
+++++++++-      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++
++++++++
+++++++
+++++++++-      const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++      // No, we append to chat-log / duet-history.
+++++++
++++++++
+++++++
++++++++++      const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++       if (!chatLog) {
+++++++
++++++++
+++++++
+++++++++          // ... error ...
+++++++
++++++++
+++++++
+++++++++-        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++
++++++++
+++++++
++++++++++        console.error("[Othello UI] CRITICAL: chat container missing (#duet-history or #chat-log).");
+++++++
++++++++
+++++++
+++++++++         // Visible UI Error (Phase A/B Requirement)
+++++++
++++++++
+++++++
+++++++++         const toastContainer = document.getElementById("toast-container");
+++++++
++++++++
+++++++
+++++++++         if (toastContainer) {
+++++++
++++++++
+++++++
+++++++++@@ -4554,11 +4547,14 @@
+++++++
++++++++
+++++++
+++++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++
++++++++
+++++++
+++++++++             if (!text.trim()) return;
+++++++
++++++++
+++++++
+++++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++
++++++++
+++++++
+++++++++-            addMessage(role, text);
+++++++
++++++++
+++++++
++++++++++            // Pass special flag to force into history backlog
+++++++
++++++++
+++++++
++++++++++            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++
++++++++
+++++++
+++++++++           });
+++++++
++++++++
+++++++
+++++++++           
+++++++
++++++++
+++++++
+++++++++-          // Force scroll to bottom after initial load
+++++++
++++++++
+++++++
+++++++++-          scrollChatToBottom(true);
+++++++
++++++++
+++++++
++++++++++          // Force scroll logic for "hidden backlog"
+++++++
++++++++
+++++++
++++++++++          syncDuetHistorySpacer();
+++++++
++++++++
+++++++
++++++++++          scrollDuetHistoryToBottom();
+++++++
++++++++
+++++++
++++++++++          // scrollChatToBottom(true); // Legacy call
+++++++
++++++++
+++++++
+++++++++         };
+++++++
++++++++
+++++++
+++++++++         if (renderedCount > 0) {
+++++++
++++++++
+++++++
+++++++++           renderMessages(messages);
+++++++
++++++++
+++++++
+++++++++@@ -4685,9 +4681,40 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       row.appendChild(bubble);
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++-      // Append to the resolved container
+++++++
++++++++
+++++++
+++++++++-      if (container) {
+++++++
++++++++
+++++++
+++++++++-         container.appendChild(row);
+++++++
++++++++
+++++++
++++++++++      // Phase 5: Routing for Duet vs Standard
+++++++
++++++++
+++++++
++++++++++      const duetTop = document.getElementById("duet-top");
+++++++
++++++++
+++++++
++++++++++      const duetBottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
++++++++++      const historySpacer = document.getElementById("duet-history-spacer");
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
++++++++
+++++++
++++++++++      
+++++++
++++++++
+++++++
++++++++++      if (duetTop && duetBottom) {
+++++++
++++++++
+++++++
++++++++++          if (isHistoryLoad) {
+++++++
++++++++
+++++++
++++++++++             // Append to history container
+++++++
++++++++
+++++++
++++++++++             // If spacer exists, insert before it
+++++++
++++++++
+++++++
++++++++++             if (container.id === "duet-history" && historySpacer) {
+++++++
++++++++
+++++++
++++++++++                 container.insertBefore(row, historySpacer);
+++++++
++++++++
+++++++
++++++++++             } else {
+++++++
++++++++
+++++++
++++++++++                 container.appendChild(row);
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
++++++++++          } else {
+++++++
++++++++
+++++++
++++++++++             // Live Message: Goes to pins
+++++++
++++++++
+++++++
++++++++++             if (role === "user") {
+++++++
++++++++
+++++++
++++++++++                 // User creates a new turn. 
+++++++
++++++++
+++++++
++++++++++                 // Note: Caller (handleInput) should have archived previous pins.
+++++++
++++++++
+++++++
++++++++++                 duetBottom.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++                 duetBottom.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                 duetBottom.style.display = "block";
+++++++
++++++++
+++++++
++++++++++             } else {
+++++++
++++++++
+++++++
++++++++++                 // Bot message - Replaces Top Pin
+++++++
++++++++
+++++++
++++++++++                 duetTop.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++                 duetTop.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                 duetTop.style.display = "block";
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
++++++++++          }
+++++++
++++++++
+++++++
++++++++++      } else {
+++++++
++++++++
+++++++
++++++++++          // Standard appending
+++++++
++++++++
+++++++
++++++++++          if (container) container.appendChild(row);
+++++++
++++++++
+++++++
+++++++++       }
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++       updateDuetView(row, role);
+++++++
++++++++
+++++++
+++++++++@@ -5963,6 +5990,13 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       if (!text && !extraData.ui_action) return;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++
++++++++
+++++++
++++++++++      // This ensures the stage is cleared before the new user bubble appears.
+++++++
++++++++
+++++++
++++++++++      // We only do this if it's a genuine user message (text present or ui_action).
+++++++
++++++++
+++++++
++++++++++      if (typeof archivePinnedToHistory === "function") {
+++++++
++++++++
+++++++
++++++++++          archivePinnedToHistory();
+++++++
++++++++
+++++++
++++++++++      }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++       // Voice-first save command (Strict Command Mode)
+++++++
++++++++
+++++++
+++++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++\n# Refactor: Single Scroll Container\n
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++
+++++++
+++++++++index 2f438318..a6a50e8b 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.js
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.js
+++++++
++++++++
+++++++
+++++++++@@ -793,7 +793,8 @@
+++++++
++++++++
+++++++
+++++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++
++++++++
+++++++
+++++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    const chatLog = document.getElementById('chat-log');
+++++++
++++++++
+++++++
++++++++++    // Updated to support new Duet History container
+++++++
++++++++
+++++++
++++++++++    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++
++++++++
+++++++
+++++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++
++++++++
+++++++
+++++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++
++++++++
+++++++
+++++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++
++++++++
+++++++
+++++++++@@ -4300,94 +4301,78 @@
+++++++
++++++++
+++++++
+++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++
+++++++
+++++++++-    function applyDuetPins() {
+++++++
++++++++
+++++++
++++++++++    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++++++
++++++++
+++++++
++++++++++    function syncDuetHistorySpacer() {
+++++++
++++++++
+++++++
++++++++++       // Deprecated in Single Scroll model
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    function scrollDuetHistoryToBottom() {
+++++++
++++++++
+++++++
++++++++++       // Deprecated - use scrollChatToBottom
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    // Call on resize - harmless
+++++++
++++++++
+++++++
++++++++++    window.addEventListener("resize", () => {});
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++
++++++++
+++++++
++++++++++    function archivePinnedToHistory() {
+++++++
++++++++
+++++++
+++++++++         const top = document.getElementById("duet-top");
+++++++
++++++++
+++++++
+++++++++         const bottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
+++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++        const historyContainer = document.getElementById("duet-history"); // The block above
+++++++
++++++++
+++++++
++++++++++        const viewport = document.getElementById("chat-view"); // The scrollable parent
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++         // Fallback for safety
+++++++
++++++++
+++++++
+++++++++-        if (!top || !bottom || !chatLog) return;
+++++++
++++++++
+++++++
+++++++++-        
+++++++
++++++++
+++++++
+++++++++-        // 1. Gather ALL message rows from all containers
+++++++
++++++++
+++++++
+++++++++-        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++
+++++++
+++++++++-        const allRows = [
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++
+++++++
+++++++++-            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++
+++++++
+++++++++-        ];
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        if (allRows.length === 0) return;
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++
+++++++
+++++++++-        allRows.sort((a, b) => {
+++++++
++++++++
+++++++
+++++++++-            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++-            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++
+++++++
+++++++++-            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++
+++++++
+++++++++-            
+++++++
++++++++
+++++++
+++++++++-            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++-            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++
+++++++
+++++++++-            return tsA - tsB;
+++++++
++++++++
+++++++
+++++++++-        });
+++++++
++++++++
+++++++
++++++++++        if (!top || !bottom || !historyContainer || !viewport) return;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 3. Identify Candidates
+++++++
++++++++
+++++++
+++++++++-        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++
+++++++
+++++++++-        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++
+++++++
+++++++++-        
+++++++
++++++++
+++++++
+++++++++-        let targetTop = null;
+++++++
++++++++
+++++++
+++++++++-        let targetBottom = null;
+++++++
++++++++
+++++++
++++++++++        // 1. Capture Scroll State BEFORE modifying DOM
+++++++
++++++++
+++++++
++++++++++        const prevScrollHeight = viewport.scrollHeight;
+++++++
++++++++
+++++++
++++++++++        const prevScrollTop = viewport.scrollTop;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        if (duetActive) {
+++++++
++++++++
+++++++
+++++++++-             // Find last bot message
+++++++
++++++++
+++++++
+++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++
+++++++
+++++++++-                     targetTop = allRows[i];
+++++++
++++++++
+++++++
+++++++++-                     break;
+++++++
++++++++
+++++++
+++++++++-                 }
+++++++
++++++++
+++++++
+++++++++-             }
+++++++
++++++++
+++++++
+++++++++-             // Find last user message
+++++++
++++++++
+++++++
+++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++
+++++++
+++++++++-                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++
+++++++
+++++++++-                     targetBottom = allRows[i];
+++++++
++++++++
+++++++
+++++++++-                     break;
+++++++
++++++++
+++++++
+++++++++-                 }
+++++++
++++++++
+++++++
+++++++++-             }
+++++++
++++++++
+++++++
++++++++++        // 2. Archive items from pins to history
+++++++
++++++++
+++++++
++++++++++        // Order: Top (Bot) -> Bottom (User). 
+++++++
++++++++
+++++++
++++++++++        // We append to the END of the history container (chronological).
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        const topNodes = Array.from(top.children);
+++++++
++++++++
+++++++
++++++++++        const bottomNodes = Array.from(bottom.children);
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        const fragment = document.createDocumentFragment();
+++++++
++++++++
+++++++
++++++++++        topNodes.forEach(n => fragment.appendChild(n));
+++++++
++++++++
+++++++
++++++++++        bottomNodes.forEach(n => fragment.appendChild(n));
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        if (fragment.children.length > 0) {
+++++++
++++++++
+++++++
++++++++++            historyContainer.appendChild(fragment);
+++++++
++++++++
+++++++
+++++++++         }
+++++++
++++++++
+++++++
+++++++++-
+++++++
++++++++
+++++++
+++++++++-        // 4. Distribute Elements
+++++++
++++++++
+++++++
+++++++++-        // Since we are sorting, we can just append in order.
+++++++
++++++++
+++++++
+++++++++-        // However, we want 'chatLog' to have the history.
+++++++
++++++++
+++++++
+++++++++-        // The pins get pulled out.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++
+++++++
+++++++++-        // Or just iterate and place.
+++++++
++++++++
+++++++
++++++++++        // Pins are now empty (because appendChild moved them)
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        allRows.forEach(row => {
+++++++
++++++++
+++++++
+++++++++-            if (row === targetTop) {
+++++++
++++++++
+++++++
+++++++++-                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++
+++++++
+++++++++-                top.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-            } else if (row === targetBottom) {
+++++++
++++++++
+++++++
+++++++++-                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++
+++++++
+++++++++-                bottom.style.display = 'block';
+++++++
++++++++
+++++++
+++++++++-            } else {
+++++++
++++++++
+++++++
+++++++++-                // Everything else goes to history
+++++++
++++++++
+++++++
+++++++++-                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++
+++++++
+++++++++-            }
+++++++
++++++++
+++++++
+++++++++-        });
+++++++
++++++++
+++++++
++++++++++        // 3. Maintain Visual Scroll Position
+++++++
++++++++
+++++++
++++++++++        // If content was added ABOVE the current view (inside historyContainer), 
+++++++
++++++++
+++++++
++++++++++        // the scrollHeight increased. We must shift scrollTop to keep the user anchor.
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        const newScrollHeight = viewport.scrollHeight;
+++++++
++++++++
+++++++
++++++++++        const delta = newScrollHeight - prevScrollHeight;
+++++++
++++++++
+++++++
++++++++++        
+++++++
++++++++
+++++++
++++++++++        // Only adjust if we weren't already at 0? 
+++++++
++++++++
+++++++
++++++++++        // Actually, if we were at the bottom, we want to STAY at the relative bottom of the *previous* content?
+++++++
++++++++
+++++++
++++++++++        // No, if we were at bottom looking at "Live", and "Live" moved down, we want to follow it.
+++++++
++++++++
+++++++
++++++++++        // So yes, add delta.
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        if (!targetTop) top.style.display = 'none';
+++++++
++++++++
+++++++
+++++++++-        if (!targetBottom) bottom.style.display = 'none';
+++++++
++++++++
+++++++
++++++++++        if (delta > 0) {
+++++++
++++++++
+++++++
++++++++++            viewport.scrollTop = prevScrollTop + delta;
+++++++
++++++++
+++++++
++++++++++        }
+++++++
++++++++
+++++++
++++++++++    }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++-        // 5. Scroll Management
+++++++
++++++++
+++++++
+++++++++-        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++
+++++++
+++++++++-        // But logic is usually handled by scrollChatToBottom separately.
+++++++
++++++++
+++++++
++++++++++    // Deprecated / Aliased
+++++++
++++++++
+++++++
++++++++++    function applyDuetPins() {
+++++++
++++++++
+++++++
++++++++++        // No-op or alias to archive? 
+++++++
++++++++
+++++++
++++++++++        // We only want to archive on SPECIFIC events (new send), not every render loop.
+++++++
++++++++
+++++++
++++++++++        // So we leave this empty to stop auto-magic behavior.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++     
+++++++
++++++++
+++++++
+++++++++     function syncDuetPadding() {}
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function updateDuetView(row, role) {
+++++++
++++++++
+++++++
+++++++++-      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++
+++++++
+++++++++-      requestAnimationFrame(applyDuetPins);
+++++++
++++++++
+++++++
++++++++++      // In new model, we don't automatically pin everything.
+++++++
++++++++
+++++++
++++++++++      // addMessage handles the routing.
+++++++
++++++++
+++++++
+++++++++     }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function bindDuetListeners() {
+++++++
++++++++
+++++++
+++++++++@@ -4399,13 +4384,12 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++     function getChatContainer() {
+++++++
++++++++
+++++++
+++++++++       // Phase 4: Target the real scroll container for appending?
+++++++
++++++++
+++++++
+++++++++-      // No, we append to chat-log. The VIEW is the scroller.
+++++++
++++++++
+++++++
+++++++++-      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++
++++++++
+++++++
+++++++++-      const chatLog = document.getElementById("chat-log");
+++++++
++++++++
+++++++
++++++++++      // No, we append to chat-log / duet-history.
+++++++
++++++++
+++++++
++++++++++      const chatLog = document.getElementById("duet-history") || document.getElementById("chat-log");
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++       if (!chatLog) {
+++++++
++++++++
+++++++
+++++++++          // ... error ...
+++++++
++++++++
+++++++
+++++++++-        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++
++++++++
+++++++
++++++++++        console.error("[Othello UI] CRITICAL: chat container missing (#duet-history or #chat-log).");
+++++++
++++++++
+++++++
+++++++++         // Visible UI Error (Phase A/B Requirement)
+++++++
++++++++
+++++++
+++++++++         const toastContainer = document.getElementById("toast-container");
+++++++
++++++++
+++++++
+++++++++         if (toastContainer) {
+++++++
++++++++
+++++++
+++++++++@@ -4554,11 +4538,14 @@
+++++++
++++++++
+++++++
+++++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++
++++++++
+++++++
+++++++++             if (!text.trim()) return;
+++++++
++++++++
+++++++
+++++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++
++++++++
+++++++
+++++++++-            addMessage(role, text);
+++++++
++++++++
+++++++
++++++++++            // Pass special flag to force into history backlog
+++++++
++++++++
+++++++
++++++++++            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++
++++++++
+++++++
+++++++++           });
+++++++
++++++++
+++++++
+++++++++           
+++++++
++++++++
+++++++
+++++++++-          // Force scroll to bottom after initial load
+++++++
++++++++
+++++++
+++++++++-          scrollChatToBottom(true);
+++++++
++++++++
+++++++
++++++++++          // Force scroll logic for "hidden backlog"
+++++++
++++++++
+++++++
++++++++++          syncDuetHistorySpacer();
+++++++
++++++++
+++++++
++++++++++          scrollDuetHistoryToBottom();
+++++++
++++++++
+++++++
++++++++++          // scrollChatToBottom(true); // Legacy call
+++++++
++++++++
+++++++
+++++++++         };
+++++++
++++++++
+++++++
+++++++++         if (renderedCount > 0) {
+++++++
++++++++
+++++++
+++++++++           renderMessages(messages);
+++++++
++++++++
+++++++
+++++++++@@ -4685,9 +4672,36 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       row.appendChild(bubble);
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++-      // Append to the resolved container
+++++++
++++++++
+++++++
+++++++++-      if (container) {
+++++++
++++++++
+++++++
+++++++++-         container.appendChild(row);
+++++++
++++++++
+++++++
++++++++++      // Phase 5: Routing for Duet vs Standard
+++++++
++++++++
+++++++
++++++++++      const duetTop = document.getElementById("duet-top");
+++++++
++++++++
+++++++
++++++++++      const duetBottom = document.getElementById("duet-bottom");
+++++++
++++++++
+++++++
++++++++++      const historySpacer = document.getElementById("duet-history-spacer");
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
++++++++
+++++++
++++++++++      
+++++++
++++++++
+++++++
++++++++++      if (duetTop && duetBottom) {
+++++++
++++++++
+++++++
++++++++++          if (isHistoryLoad) {
+++++++
++++++++
+++++++
++++++++++             // Append to history container
+++++++
++++++++
+++++++
++++++++++             // We just append because history is naturally chronological "above" the live pins
+++++++
++++++++
+++++++
++++++++++             container.appendChild(row);
+++++++
++++++++
+++++++
++++++++++          } else {
+++++++
++++++++
+++++++
++++++++++             // Live Message: Goes to pins
+++++++
++++++++
+++++++
++++++++++             if (role === "user") {
+++++++
++++++++
+++++++
++++++++++                 // User creates a new turn. 
+++++++
++++++++
+++++++
++++++++++                 // Note: Caller (handleInput) should have archived previous pins.
+++++++
++++++++
+++++++
++++++++++                 duetBottom.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++                 duetBottom.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                 duetBottom.style.display = "block";
+++++++
++++++++
+++++++
++++++++++             } else {
+++++++
++++++++
+++++++
++++++++++                 // Bot message - Replaces Top Pin
+++++++
++++++++
+++++++
++++++++++                 duetTop.innerHTML = "";
+++++++
++++++++
+++++++
++++++++++                 duetTop.appendChild(row);
+++++++
++++++++
+++++++
++++++++++                 duetTop.style.display = "block";
+++++++
++++++++
+++++++
++++++++++             }
+++++++
++++++++
+++++++
++++++++++          }
+++++++
++++++++
+++++++
++++++++++      } else {
+++++++
++++++++
+++++++
++++++++++          // Standard appending
+++++++
++++++++
+++++++
++++++++++          if (container) container.appendChild(row);
+++++++
++++++++
+++++++
+++++++++       }
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++       updateDuetView(row, role);
+++++++
++++++++
+++++++
+++++++++@@ -5963,6 +5977,13 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       if (!text && !extraData.ui_action) return;
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++
++++++++
+++++++
++++++++++      // This ensures the stage is cleared before the new user bubble appears.
+++++++
++++++++
+++++++
++++++++++      // We only do this if it's a genuine user message (text present or ui_action).
+++++++
++++++++
+++++++
++++++++++      if (typeof archivePinnedToHistory === "function") {
+++++++
++++++++
+++++++
++++++++++          archivePinnedToHistory();
+++++++
++++++++
+++++++
++++++++++      }
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++       // Voice-first save command (Strict Command Mode)
+++++++
++++++++
+++++++
+++++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++++
++++++++
+++++++
+++++++++       
+++++++
++++++++
+++++++
+++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++
+++++++
+++++++++index 382eeb57..b4bbe4a8 100644
+++++++
++++++++
+++++++
+++++++++--- a/static/othello.css
+++++++
++++++++
+++++++
++++++++++++ b/static/othello.css
+++++++
++++++++
+++++++
+++++++++@@ -2209,7 +2209,8 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++   flex-direction: column;
+++++++
++++++++
+++++++
+++++++++   flex: 1 1 0;
+++++++
++++++++
+++++++
+++++++++   min-height: 0;
+++++++
++++++++
+++++++
+++++++++-  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
++++++++
+++++++
++++++++++  overflow-y: auto !important; /* The SINGLE scroll container */
+++++++
++++++++
+++++++
++++++++++  overflow-x: hidden;
+++++++
++++++++
+++++++
+++++++++   position: relative;
+++++++
++++++++
+++++++
+++++++++   padding: 0;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++@@ -2217,31 +2218,41 @@ body.chat-open #global-chat-fab {
+++++++
++++++++
+++++++
+++++++++ /* Duet Panes (Static Flex Items) */
+++++++
++++++++
+++++++
+++++++++ .duet-pane {
+++++++
++++++++
+++++++
+++++++++   position: static; /* No longer sticky */
+++++++
++++++++
+++++++
+++++++++-  flex: 0 0 auto; /* Rigid height based on content */
+++++++
++++++++
+++++++
++++++++++  flex: 0 0 auto;
+++++++
++++++++
+++++++
+++++++++   z-index: 100;
+++++++
++++++++
+++++++
+++++++++   background: transparent;
+++++++
++++++++
+++++++
+++++++++   padding: 0.75rem;
+++++++
++++++++
+++++++
+++++++++   margin: 0;
+++++++
++++++++
+++++++
+++++++++   display: block;
+++++++
++++++++
+++++++
+++++++++-  pointer-events: none;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ .duet-pane > * { pointer-events: auto; }
+++++++
++++++++
+++++++
+++++++++ .duet-pane:empty { display: none !important; }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++ /* Chat Log (Middle Scrollable History) */
+++++++
++++++++
+++++++
+++++++++-#chat-log {
+++++++
++++++++
+++++++
+++++++++-  display: flex !important;
+++++++
++++++++
+++++++
+++++++++-  flex-direction: column;
+++++++
++++++++
+++++++
+++++++++-  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++
+++++++
+++++++++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++
+++++++
+++++++++-  min-height: 0;
+++++++
++++++++
+++++++
++++++++++/* Changed to #duet-history in DOM, but kept .chat-log class. 
+++++++
++++++++
+++++++
++++++++++   Target generic .chat-log or specific #duet-history */
+++++++
++++++++
+++++++
++++++++++#chat-log, #duet-history {
+++++++
++++++++
+++++++
++++++++++  display: block; /* Normal block inside scroll */
+++++++
++++++++
+++++++
++++++++++  flex: 0 0 auto; 
+++++++
++++++++
+++++++
++++++++++  overflow: visible !important; /* No internal scroll */
+++++++
++++++++
+++++++
+++++++++   height: auto !important;
+++++++
++++++++
+++++++
+++++++++   padding: 1rem;
+++++++
++++++++
+++++++
+++++++++   padding-top: 0.5rem;
+++++++
++++++++
+++++++
+++++++++   padding-bottom: 0.5rem;
+++++++
++++++++
+++++++
+++++++++ }
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
++++++++++/* live-chat-container wrapper (optional styling) */
+++++++
++++++++
+++++++
++++++++++#live-chat-container {
+++++++
++++++++
+++++++
++++++++++    display: flex;
+++++++
++++++++
+++++++
++++++++++    flex-direction: column;
+++++++
++++++++
+++++++
++++++++++    flex: 0 0 auto;
+++++++
++++++++
+++++++
++++++++++}
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++#duet-history-spacer {
+++++++
++++++++
+++++++
++++++++++    display: none; /* Deprecated/Removed */
+++++++
++++++++
+++++++
++++++++++}
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++ /* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
++++++++
+++++++
+++++++++ .duet-pane--top {
+++++++
++++++++
+++++++
+++++++++   order: 1;
+++++++
++++++++
+++++++
+++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++index d6ca18ec..b5d19621 100644
+++++++
++++++++
+++++++
+++++++++--- a/othello_ui.html
+++++++
++++++++
+++++++
++++++++++++ b/othello_ui.html
+++++++
++++++++
+++++++
+++++++++@@ -337,14 +337,21 @@
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       <!-- Moved Chat View Content -->
+++++++
++++++++
+++++++
+++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++
+++++++
+++++++++-        <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++         
+++++++
++++++++
+++++++
+++++++++-        <!-- Only this is scrollable history -->
+++++++
++++++++
+++++++
+++++++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++
+++++++
+++++++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++
+++++++
+++++++++-        <div id="chat-log" class="chat-log"></div>
+++++++
++++++++
+++++++
+++++++++-        
+++++++
++++++++
+++++++
+++++++++-        <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++        <!-- History Section (Above Fold) -->
+++++++
++++++++
+++++++
++++++++++        <div id="duet-history" class="chat-log">
+++++++
++++++++
+++++++
++++++++++           <!-- Spacer removed - let natural flow handle it, or JS can pad if strictly needed. 
+++++++
++++++++
+++++++
++++++++++                User instruction: "Step 3: ... history container must be a normal block ... DO NOT set any height" -->
+++++++
++++++++
+++++++
++++++++++        </div>
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
++++++++++        <!-- Live Chat Section (Visible Default) -->
+++++++
++++++++
+++++++
++++++++++        <div id="live-chat-container">
+++++++
++++++++
+++++++
++++++++++            <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++            <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++            <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++
+++++++
++++++++++            <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
++++++++
+++++++
++++++++++        </div>
+++++++
++++++++
+++++++
++++++++++
+++++++
++++++++
+++++++
+++++++++       </div>
+++++++
++++++++
+++++++
+++++++++ 
+++++++
++++++++
+++++++
+++++++++       <!-- Moved Input Bar -->
+++++++
++++++++
+++++++
+++++++++
+++++++
++++++++\ No newline at end of file
+++++++
++++++++diff --git a/othello_ui.html b/othello_ui.html
+++++++
++++++++index d6ca18ec..421a3949 100644
+++++++
++++++++--- a/othello_ui.html
+++++++
+++++++++++ b/othello_ui.html
+++++++
++++++++@@ -337,14 +337,20 @@
+++++++
++++++++ 
+++++++
++++++++       <!-- Moved Chat View Content -->
+++++++
++++++++       <div id="chat-view" class="view" style="display:flex;">
+++++++
++++++++-        <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
++++++++         
+++++++
++++++++-        <!-- Only this is scrollable history -->
+++++++
++++++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
++++++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
++++++++-        <div id="chat-log" class="chat-log"></div>
+++++++
++++++++-        
+++++++
++++++++-        <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
+++++++++        <!-- History Section (Above Fold) -->
+++++++
+++++++++        <div id="duet-history" class="chat-log"></div>
+++++++
+++++++++
+++++++
+++++++++        <!-- Live Chat Section (Visible Default, Chronological) -->
+++++++
+++++++++        <!-- Renamed live-chat-container to chat-log to act as the primary live container -->
+++++++
+++++++++        <div id="chat-log" class="chat-log">
+++++++
+++++++++            <!-- Legacy Pin containers preserved for safety but unused by new appended messages -->
+++++++
+++++++++            <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++++
+++++++++            <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++
+++++++++            <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++
+++++++++            <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++++
+++++++++        </div>
+++++++
+++++++++
+++++++
++++++++       </div>
+++++++
++++++++ 
+++++++
++++++++       <!-- Moved Input Bar -->
+++++++
++++++++diff --git a/static/othello.css b/static/othello.css
+++++++
++++++++index 382eeb57..4c9595eb 100644
+++++++
++++++++--- a/static/othello.css
+++++++
+++++++++++ b/static/othello.css
+++++++
++++++++@@ -2209,7 +2209,8 @@ body.chat-open #global-chat-fab {
+++++++
++++++++   flex-direction: column;
+++++++
++++++++   flex: 1 1 0;
+++++++
++++++++   min-height: 0;
+++++++
++++++++-  overflow: hidden !important; /* View itself does NOT scroll */
+++++++
+++++++++  overflow-y: auto !important; /* The SINGLE scroll container */
+++++++
+++++++++  overflow-x: hidden;
+++++++
++++++++   position: relative;
+++++++
++++++++   padding: 0;
+++++++
++++++++ }
+++++++
++++++++@@ -2217,43 +2218,54 @@ body.chat-open #global-chat-fab {
+++++++
++++++++ /* Duet Panes (Static Flex Items) */
+++++++
++++++++ .duet-pane {
+++++++
++++++++   position: static; /* No longer sticky */
+++++++
++++++++-  flex: 0 0 auto; /* Rigid height based on content */
+++++++
+++++++++  flex: 0 0 auto;
+++++++
++++++++   z-index: 100;
+++++++
++++++++   background: transparent;
+++++++
++++++++   padding: 0.75rem;
+++++++
++++++++   margin: 0;
+++++++
++++++++   display: block;
+++++++
++++++++-  pointer-events: none;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ .duet-pane > * { pointer-events: auto; }
+++++++
++++++++ .duet-pane:empty { display: none !important; }
+++++++
++++++++ 
+++++++
++++++++ /* Chat Log (Middle Scrollable History) */
+++++++
++++++++-#chat-log {
+++++++
++++++++-  display: flex !important;
+++++++
++++++++-  flex-direction: column;
+++++++
++++++++-  flex: 1 1 0; /* Takes all remaining space */
+++++++
++++++++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++
++++++++-  min-height: 0;
+++++++
+++++++++/* Changed to #duet-history in DOM, but kept .chat-log class. 
+++++++
+++++++++   Target generic .chat-log or specific #duet-history */
+++++++
+++++++++#chat-log, #duet-history {
+++++++
+++++++++  display: block; /* Normal block inside scroll */
+++++++
+++++++++  flex: 0 0 auto; 
+++++++
+++++++++  overflow: visible !important; /* No internal scroll */
+++++++
++++++++   height: auto !important;
+++++++
++++++++   padding: 1rem;
+++++++
++++++++   padding-top: 0.5rem;
+++++++
++++++++   padding-bottom: 0.5rem;
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
+++++++++/* live-chat-container wrapper (optional styling) */
+++++++
+++++++++#live-chat-container {
+++++++
+++++++++    display: flex;
+++++++
+++++++++    flex-direction: column;
+++++++
+++++++++    flex: 0 0 auto;
+++++++
+++++++++}
+++++++
+++++++++
+++++++
+++++++++#duet-history-spacer {
+++++++
+++++++++    display: none; /* Deprecated/Removed */
+++++++
+++++++++}
+++++++
+++++++++
+++++++
++++++++ /* Remove sticky-specific top/bottom since they are just flex order now */
+++++++
+++++++++/* Cleaned up for Single Scroll Flow */
+++++++
++++++++ .duet-pane--top {
+++++++
++++++++-  order: 1;
+++++++
++++++++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
+++++++++  /* order: 1; - REMOVED */
+++++++
+++++++++  border-bottom: 1px solid rgba(255,255,255,0.05);
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ #chat-log {
+++++++
++++++++-  order: 2; /* Middle */
+++++++
+++++++++  /* order: 2; - REMOVED */
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++ .duet-pane--bottom {
+++++++
++++++++-  order: 3;
+++++++
+++++++++  /* order: 3; - REMOVED */
+++++++
++++++++   border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++
++++++++ }
+++++++
++++++++ 
+++++++
++++++++diff --git a/static/othello.js b/static/othello.js
+++++++
++++++++index 2f438318..255b2e0f 100644
+++++++
++++++++--- a/static/othello.js
+++++++
+++++++++++ b/static/othello.js
+++++++
++++++++@@ -793,7 +793,8 @@
+++++++
++++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++
++++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++
++++++++ 
+++++++
++++++++-    const chatLog = document.getElementById('chat-log');
+++++++
+++++++++    // Updated to support new Duet History container
+++++++
+++++++++    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++
++++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++
++++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++
++++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++
++++++++@@ -4300,95 +4301,61 @@
+++++++
++++++++       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++++
++++++++     }
+++++++
++++++++ 
+++++++
++++++++-    // Phase 3: Canonical Move - Refactored for 3-Zone Flex Layout
+++++++
++++++++-    function applyDuetPins() {
+++++++
++++++++-        const top = document.getElementById("duet-top");
+++++++
++++++++-        const bottom = document.getElementById("duet-bottom");
+++++++
++++++++-        const chatLog = document.getElementById("chat-log");
+++++++
+++++++++    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++++++
+++++++++    function syncDuetHistorySpacer() {
+++++++
+++++++++       // Deprecated in Single Scroll model
+++++++
+++++++++    }
+++++++
++++++++ 
+++++++
++++++++-        // Fallback for safety
+++++++
++++++++-        if (!top || !bottom || !chatLog) return;
+++++++
++++++++-        
+++++++
++++++++-        // 1. Gather ALL message rows from all containers
+++++++
++++++++-        // We use Set to avoid duplicates if any weirdness, though querySelectorAll shouldn't overlap if disjoint trees
+++++++
++++++++-        const allRows = [
+++++++
++++++++-            ...Array.from(top.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(bottom.querySelectorAll('.msg-row')),
+++++++
++++++++-            ...Array.from(chatLog.querySelectorAll('.msg-row'))
+++++++
++++++++-        ];
+++++++
+++++++++    function scrollDuetHistoryToBottom() {
+++++++
+++++++++       // Deprecated - use scrollChatToBottom
+++++++
+++++++++    }
+++++++
++++++++ 
+++++++
++++++++-        if (allRows.length === 0) return;
+++++++
+++++++++    // Call on resize - harmless
+++++++
+++++++++    window.addEventListener("resize", () => {});
+++++++
++++++++ 
+++++++
++++++++-        // 2. Sort by sequence (primary) or timestamp (secondary)
+++++++
++++++++-        allRows.sort((a, b) => {
+++++++
++++++++-            const seqA = parseInt(a.dataset.sequence || "0");
+++++++
++++++++-            const seqB = parseInt(b.dataset.sequence || "0");
+++++++
++++++++-            if (seqA !== seqB) return seqA - seqB;
+++++++
++++++++-            
+++++++
++++++++-            const tsA = parseInt(a.dataset.timestamp || "0");
+++++++
++++++++-            const tsB = parseInt(b.dataset.timestamp || "0");
+++++++
++++++++-            return tsA - tsB;
+++++++
++++++++-        });
+++++++
+++++++++    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++
+++++++++    function archivePinnedToHistory() {
+++++++
+++++++++        // Source: Live Chat (#chat-log)
+++++++
+++++++++        // Dest: History (#duet-history)
+++++++
+++++++++        const liveContainer = document.getElementById("chat-log");
+++++++
+++++++++        const historyContainer = document.getElementById("duet-history");
+++++++
+++++++++        const viewport = document.getElementById("chat-view");
+++++++
++++++++ 
+++++++
++++++++-        // 3. Identify Candidates
+++++++
++++++++-        // Duet Mode: Last Bot -> Top, Last User -> Bottom.
+++++++
++++++++-        const duetActive = (typeof isDuetLayout === 'function') ? isDuetLayout() : true;
+++++++
++++++++-        
+++++++
++++++++-        let targetTop = null;
+++++++
++++++++-        let targetBottom = null;
+++++++
+++++++++        if (!liveContainer || !historyContainer || !viewport) return;
+++++++
++++++++ 
+++++++
++++++++-        if (duetActive) {
+++++++
++++++++-             // Find last bot message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (!allRows[i].classList.contains('user')) { // Assuming non-user is bot/system
+++++++
++++++++-                     targetTop = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
++++++++-             // Find last user message
+++++++
++++++++-             for (let i = allRows.length - 1; i >= 0; i--) {
+++++++
++++++++-                 if (allRows[i].classList.contains('user')) {
+++++++
++++++++-                     targetBottom = allRows[i];
+++++++
++++++++-                     break;
+++++++
++++++++-                 }
+++++++
++++++++-             }
+++++++
++++++++-        }
+++++++
+++++++++        // 1. Capture Scroll State
+++++++
+++++++++        const prevScrollHeight = viewport.scrollHeight;
+++++++
+++++++++        const prevScrollTop = viewport.scrollTop;
+++++++
++++++++ 
+++++++
++++++++-        // 4. Distribute Elements
+++++++
++++++++-        // Since we are sorting, we can just append in order.
+++++++
++++++++-        // However, we want 'chatLog' to have the history.
+++++++
++++++++-        // The pins get pulled out.
+++++++
+++++++++        // 2. Archive only valid message rows
+++++++
+++++++++        // We verify direct children to avoid deep grabbing
+++++++
+++++++++        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
+++++++
++++++++         
+++++++
++++++++-        // We must append to history in order FIRST, then move pins out?
+++++++
++++++++-        // Or just iterate and place.
+++++++
++++++++-        
+++++++
++++++++-        allRows.forEach(row => {
+++++++
++++++++-            if (row === targetTop) {
+++++++
++++++++-                if (top.lastChild !== row) top.appendChild(row);
+++++++
++++++++-                top.style.display = 'block';
+++++++
++++++++-            } else if (row === targetBottom) {
+++++++
++++++++-                if (bottom.lastChild !== row) bottom.appendChild(row);
+++++++
++++++++-                bottom.style.display = 'block';
+++++++
++++++++-            } else {
+++++++
++++++++-                // Everything else goes to history
+++++++
++++++++-                if (chatLog.lastElementChild !== row) chatLog.appendChild(row);
+++++++
++++++++-            }
+++++++
++++++++-        });
+++++++
+++++++++        if (rows.length === 0) return;
+++++++
+++++++++
+++++++
+++++++++        const fragment = document.createDocumentFragment();
+++++++
+++++++++        // Since we iterate in DOM order, we preserve chronological order
+++++++
+++++++++        rows.forEach(r => fragment.appendChild(r));
+++++++
++++++++         
+++++++
++++++++-        if (!targetTop) top.style.display = 'none';
+++++++
++++++++-        if (!targetBottom) bottom.style.display = 'none';
+++++++
+++++++++        historyContainer.appendChild(fragment);
+++++++
++++++++ 
+++++++
++++++++-        // 5. Scroll Management
+++++++
++++++++-        // Since history is now independent, we might want to stick to bottom if we were there?
+++++++
++++++++-        // But logic is usually handled by scrollChatToBottom separately.
+++++++
+++++++++        // 3. Maintain Scroll Position
+++++++
+++++++++        const newScrollHeight = viewport.scrollHeight;
+++++++
+++++++++        const delta = newScrollHeight - prevScrollHeight;
+++++++
+++++++++        
+++++++
+++++++++        if (delta > 0) {
+++++++
+++++++++            viewport.scrollTop = prevScrollTop + delta;
+++++++
+++++++++        }
+++++++
+++++++++        
+++++++
+++++++++        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
+++++++
++++++++     }
+++++++
+++++++++
+++++++
+++++++++    // Deprecated / Aliased
+++++++
+++++++++    function applyDuetPins() {}
+++++++
++++++++     
+++++++
++++++++     function syncDuetPadding() {}
+++++++
++++++++ 
+++++++
++++++++-    function updateDuetView(row, role) {
+++++++
++++++++-      // Defer to applyDuetPins in next frame so DOM is ready
+++++++
++++++++-      requestAnimationFrame(applyDuetPins);
+++++++
++++++++-    }
+++++++
+++++++++    function updateDuetView(row, role) {}
+++++++
++++++++ 
+++++++
++++++++     function bindDuetListeners() {
+++++++
++++++++        // Scroll logic is now native overflow
+++++++
++++++++@@ -4398,15 +4365,12 @@
+++++++
++++++++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
+++++++
++++++++ 
+++++++
++++++++     function getChatContainer() {
+++++++
++++++++-      // Phase 4: Target the real scroll container for appending?
+++++++
++++++++-      // No, we append to chat-log. The VIEW is the scroller.
+++++++
++++++++-      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++
+++++++++      // Phase 4: Target the LIVE container (chat-log)
+++++++
++++++++       const chatLog = document.getElementById("chat-log");
+++++++
++++++++       
+++++++
++++++++       if (!chatLog) {
+++++++
++++++++-         // ... error ...
+++++++
++++++++-        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++
++++++++-        // Visible UI Error (Phase A/B Requirement)
+++++++
+++++++++         // Fallback or error
+++++++
+++++++++        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
+++++++
++++++++         const toastContainer = document.getElementById("toast-container");
+++++++
++++++++         if (toastContainer) {
+++++++
++++++++             const errDiv = document.createElement("div");
+++++++
++++++++@@ -4414,7 +4378,7 @@
+++++++
++++++++             errDiv.textContent = "Error: Chat container missing.";
+++++++
++++++++             toastContainer.appendChild(errDiv);
+++++++
++++++++         }
+++++++
++++++++-        return null;
+++++++
+++++++++        return document.getElementById("duet-history"); // Last resort
+++++++
++++++++       }
+++++++
++++++++       return chatLog;
+++++++
++++++++     }
+++++++
++++++++@@ -4554,11 +4518,14 @@
+++++++
++++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++
++++++++             if (!text.trim()) return;
+++++++
++++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++
++++++++-            addMessage(role, text);
+++++++
+++++++++            // Pass special flag to force into history backlog
+++++++
+++++++++            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++
++++++++           });
+++++++
++++++++           
+++++++
++++++++-          // Force scroll to bottom after initial load
+++++++
++++++++-          scrollChatToBottom(true);
+++++++
+++++++++          // Force scroll logic for "hidden backlog"
+++++++
+++++++++          syncDuetHistorySpacer();
+++++++
+++++++++          scrollDuetHistoryToBottom();
+++++++
+++++++++          // scrollChatToBottom(true); // Legacy call
+++++++
++++++++         };
+++++++
++++++++         if (renderedCount > 0) {
+++++++
++++++++           renderMessages(messages);
+++++++
++++++++@@ -4685,9 +4652,24 @@
+++++++
++++++++ 
+++++++
++++++++       row.appendChild(bubble);
+++++++
++++++++       
+++++++
++++++++-      // Append to the resolved container
+++++++
++++++++-      if (container) {
+++++++
++++++++-         container.appendChild(row);
+++++++
+++++++++      // Phase 5: Routing for Duet vs Standard
+++++++
+++++++++      const duetTop = document.getElementById("duet-top");
+++++++
+++++++++      const duetBottom = document.getElementById("duet-bottom");
+++++++
+++++++++      const historySpacer = document.getElementById("duet-history-spacer");
+++++++
+++++++++
+++++++
+++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
+++++++++      
+++++++
+++++++++      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
+++++++
+++++++++      const duetHistory = document.getElementById("duet-history");
+++++++
+++++++++      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++
+++++++++      
+++++++
+++++++++      if (isHistoryLoad && duetHistory) {
+++++++
+++++++++         // History always appends-to-end of the History Block (which is above Live)
+++++++
+++++++++         duetHistory.appendChild(row);
+++++++
+++++++++      } else {
+++++++
+++++++++         // Live messages append strictly to the Live Container (#chat-log)
+++++++
+++++++++         // This ensures standard Top-Down flow.
+++++++
+++++++++         if (container) container.appendChild(row);
+++++++
++++++++       }
+++++++
++++++++       
+++++++
++++++++       updateDuetView(row, role);
+++++++
++++++++@@ -5963,6 +5945,13 @@
+++++++
++++++++ 
+++++++
++++++++       if (!text && !extraData.ui_action) return;
+++++++
++++++++ 
+++++++
+++++++++      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++
+++++++++      // This ensures the stage is cleared before the new user bubble appears.
+++++++
+++++++++      // We only do this if it's a genuine user message (text present or ui_action).
+++++++
+++++++++      if (typeof archivePinnedToHistory === "function") {
+++++++
+++++++++          archivePinnedToHistory();
+++++++
+++++++++      }
+++++++
+++++++++
+++++++
++++++++       // Voice-first save command (Strict Command Mode)
+++++++
++++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++++
++++++++       
+++++++
++++++++
+++++++\ No newline at end of file
++++++ diff --git a/othello_ui.html b/othello_ui.html
++++++-index a78c1b7b..d6ca18ec 100644
+++++++index d6ca18ec..b115d4cd 100644
++++++ --- a/othello_ui.html
++++++ +++ b/othello_ui.html
++++++-@@ -339,6 +339,7 @@
+++++++@@ -339,6 +339,8 @@
++++++        <div id="chat-view" class="view" style="display:flex;">
++++++          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
++++++          
++++++-+        <!-- Only this is scrollable history -->
++++++++        <div id="duet-history" style="display:flex; flex-direction:column; padding:1rem; padding-bottom:0;"></div>
++++++++        
+++++++         <!-- Only this is scrollable history -->
++++++          <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++++          <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++++-         <div id="chat-log" class="chat-log"></div>
++++++ diff --git a/static/othello.css b/static/othello.css
++++++-index 825c710b..c7cc1ae5 100644
+++++++index 382eeb57..9b1f8845 100644
++++++ --- a/static/othello.css
++++++ +++ b/static/othello.css
++++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++++@@ -2203,64 +2203,65 @@ body.chat-open #global-chat-fab {
+++++++   position: relative;
++++++  }
++++++  
++++++- /* --- Duet Chat Mode (Unified) --- */
++++++--/* Phase 2: Fix the scroll container */
++++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
++++++- .chat-sheet {
+++++++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
++++++++/* Chat View IS the scroll container now */
+++++++ #chat-view {
++++++    display: flex !important;
++++++-   flex-direction: column !important;
++++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
++++++- /* Header is rigid */
++++++- .chat-sheet__header {
++++++-   flex: 0 0 auto;
++++++-+  z-index: 200; /* Header stays absolutely on top */
++++++-+  position: relative;
++++++-+  box-shadow: 0 1px 0 var(--border);
++++++- }
++++++- 
++++++- /* Input is rigid (footer) */
++++++- .input-bar {
++++++-   flex: 0 0 auto;
++++++-+  z-index: 200; /* Input stays absolutely on top */
++++++-+  position: relative;
+++++++   flex-direction: column;
+++++++-  flex: 1 1 0;
++++++++  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++++   min-height: 0;
+++++++-  overflow: hidden !important; /* View itself does NOT scroll */
++++++++  overflow-y: auto !important; /* The ONLY scrollbar */
++++++++  overflow-x: hidden;
+++++++   position: relative;
+++++++-  padding: 0;
++++++++  padding: 0; /* Strict */
++++++  }
++++++  
++++++- /* Chat View IS the scroll container now */
++++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
++++++-   background: rgba(15, 23, 42, 0.98);
+++++++-/* Duet Panes (Static Flex Items) */
++++++++/* Duet Panes (Sticky) - Transparent Rails */
+++++++ .duet-pane {
+++++++-  position: static; /* No longer sticky */
+++++++-  flex: 0 0 auto; /* Rigid height based on content */
+++++++-  z-index: 100;
+++++++-  background: transparent;
++++++++  position: sticky;
++++++++  z-index: 100; /* Must beat messages */
++++++++  background: transparent; /* Transparent background */
++++++    padding: 0.75rem;
++++++    margin: 0;
++++++--  display: block !important;
+++++++-  display: block;
+++++++-  pointer-events: none;
++++++ +  display: block; /* always block, hidden by JS empty check if needed */
++++++-   backdrop-filter: blur(8px);
++++++--  /* Ensure they don't shrink away */
++++++-   flex-shrink: 0; 
++++++++  flex-shrink: 0;
++++++++  pointer-events: none; /* Let clicks pass through empty space */
++++++  }
++++++  
+++++++-.duet-pane > * { pointer-events: auto; }
+++++++-.duet-pane:empty { display: none !important; }
+++++++-
+++++++-/* Chat Log (Middle Scrollable History) */
+++++++-#chat-log {
+++++++-  display: flex !important;
+++++++-  flex-direction: column;
+++++++-  flex: 1 1 0; /* Takes all remaining space */
+++++++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++++++-  min-height: 0;
+++++++-  height: auto !important;
+++++++-  padding: 1rem;
+++++++-  padding-top: 0.5rem;
+++++++-  padding-bottom: 0.5rem;
++++++++/* Re-enable pointer events on children (the bubbles) */
++++++++.duet-pane > * {
++++++++  pointer-events: auto;
+++++++ }
+++++++ 
+++++++-/* Remove sticky-specific top/bottom since they are just flex order now */
+++++++-.duet-pane--top {
+++++++-  order: 1;
+++++++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++++ +/* Default hidden until populated */
++++++ +.duet-pane:empty {
++++++ +    display: none !important;
++++++-+}
++++++-+
++++++- .duet-pane--top {
++++++-   top: 0;
++++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
++++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
++++++-   overflow: visible !important; /* Let parent scroll it */
++++++-   height: auto !important;
++++++-   padding: 1rem;
+++++++ }
+++++++ 
+++++++-#chat-log {
+++++++-  order: 2; /* Middle */
++++++++.duet-pane--top {
++++++++  top: 0;
++++++++  /* Removed border/shadow for clean look */
++++++++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
++++++++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++++ }
+++++++ 
+++++++ .duet-pane--bottom {
+++++++-  order: 3;
+++++++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++++++  bottom: 0;
++++++++  /* Removed border/shadow for clean look */
++++++++  /* border-top: 1px solid rgba(255,255,255,0.1); */
++++++++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++++ }
+++++++ 
+++++++-/* Ensure empty slots don't take space/border */
+++++++-.duet-pane:empty {
+++++++-    display: none !important;
+++++++-    border: none !important;
++++++++/* Chat Log (History Flow) */
++++++++#chat-log {
++++++++  display: flex !important;
++++++++  flex-direction: column;
++++++++  flex: 1; /* occupy space between pins */
++++++++  overflow: visible !important; /* Let parent scroll it */
++++++++  height: auto !important;
++++++++  padding: 1rem;
++++++ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
++++++ +  padding-top: 1rem;
++++++ +  padding-bottom: 1rem;
++++++@@ -79,46 +13563,72 @@ index 825c710b..c7cc1ae5 100644
++++++  
++++++  /* Hide empty panes */
++++++ diff --git a/static/othello.js b/static/othello.js
++++++-index 3a092bfc..1a19d8a7 100644
+++++++index 69c723cf..09891ef1 100644
++++++ --- a/static/othello.js
++++++ +++ b/static/othello.js
++++++-@@ -4300,76 +4300,81 @@
+++++++@@ -793,8 +793,7 @@
+++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++++ 
+++++++-    // Updated to support new Duet History container
+++++++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
++++++++    const chatLog = document.getElementById('chat-log');
+++++++     // Relocated status to chat header (Phase 6 Fix)
+++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++++     const modeLabel = document.getElementById('current-mode-label');
+++++++@@ -836,6 +835,7 @@
+++++++     const toastEl = document.getElementById('toast');
+++++++ 
+++++++     // App state
++++++++    let duetTurnIndex = 0;
+++++++     const othelloState = {
+++++++       chatViewMode: "duet", // "duet" | "history"
+++++++       connectivity: 'online', // online | offline | degraded
+++++++@@ -4301,61 +4301,83 @@
++++++        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
++++++      }
++++++  
++++++--    // Phase 3: Move nodes (no duplication)
++++++-+    // Phase 3: Canonical Move
++++++-     function applyDuetPins() {
++++++--        if (!isDuetEnabled()) return;
++++++--        
++++++--        const chatLog = document.getElementById("chat-log");
++++++-         const top = document.getElementById("duet-top");
++++++-         const bottom = document.getElementById("duet-bottom");
++++++--        if (!chatLog) return;
+++++++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++++++-    function syncDuetHistorySpacer() {
+++++++-       // Deprecated in Single Scroll model
+++++++-    }
+++++++-
+++++++-    function scrollDuetHistoryToBottom() {
+++++++-       // Deprecated - use scrollChatToBottom
+++++++-    }
+++++++-
+++++++-    // Call on resize - harmless
+++++++-    window.addEventListener("resize", () => {});
+++++++-
+++++++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++++-    function archivePinnedToHistory() {
+++++++-        // Source: Live Chat (#chat-log)
+++++++-        // Dest: History (#duet-history)
+++++++-        const liveContainer = document.getElementById("chat-log");
+++++++-        const historyContainer = document.getElementById("duet-history");
+++++++-        const viewport = document.getElementById("chat-view");
+++++++-
+++++++-        if (!liveContainer || !historyContainer || !viewport) return;
+++++++-
+++++++-        // 1. Capture Scroll State
+++++++-        const prevScrollHeight = viewport.scrollHeight;
+++++++-        const prevScrollTop = viewport.scrollTop;
+++++++-
+++++++-        // 2. Archive only valid message rows
+++++++-        // We verify direct children to avoid deep grabbing
+++++++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
++++++ -        
++++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
++++++--        // Actually, simpler approach for V1:
++++++--        // We only pin the LATEST. 
++++++--        // Iterate chatLog children. Find last user msg, last bot msg.
++++++--        // Move them to pins? No, that breaks history flow if they are old.
++++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
++++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
++++++--        // This implies visual displacement.
++++++--        
++++++--        // Better Strategy:
++++++--        // 1. Clear pins.
++++++--        // 2. Scan chatLog rows.
++++++--        // 3. Last row -> if user, move to bottom.
++++++--        // 4. Last ASSISTANT row -> move to top.
++++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
++++++--        // This effectively empties the bottom of the history.
++++++--        
++++++--        // Implementation:
++++++--        // Find all .msg-row in chat main loop or chatLog
++++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
++++++ -        if (rows.length === 0) return;
+++++++-
+++++++-        const fragment = document.createDocumentFragment();
+++++++-        // Since we iterate in DOM order, we preserve chronological order
+++++++-        rows.forEach(r => fragment.appendChild(r));
++++++ -        
++++++--        // Find last user row
+++++++-        historyContainer.appendChild(fragment);
++++++++    // Phase 3: Canonical Move
++++++++    function applyDuetPins() {
++++++++        const top = document.getElementById("duet-top");
++++++++        const bottom = document.getElementById("duet-bottom");
++++++ +        const chatLog = document.getElementById("chat-log");
++++++ +
++++++ +        // Fallback for safety
++++++@@ -146,45 +13656,39 @@ index 3a092bfc..1a19d8a7 100644
++++++ +        if (allRows.length === 0) return;
++++++ +
++++++ +        // 2. Scan for candidates
++++++-         let lastUserRow = null;
++++++-         let lastBotRow = null;
++++++--        
++++++++        let lastUserRow = null;
++++++++        let lastBotRow = null;
++++++ +
++++++-         // Scan backwards
++++++--        for (let i = rows.length - 1; i >= 0; i--) {
++++++--            const r = rows[i];
++++++++        // Scan backwards
++++++ +        for (let i = allRows.length - 1; i >= 0; i--) {
++++++ +            const r = allRows[i];
++++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
++++++++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++++++ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
++++++-             if (lastUserRow && lastBotRow) break;
++++++-         }
++++++- 
++++++--        // Move to pins
++++++++            if (lastUserRow && lastBotRow) break;
++++++++        }
++++++++
++++++ +        // 3. Move to pins
++++++-         if (lastBotRow) {
++++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
++++++--            // Ensure display is correct
++++++++        if (lastBotRow) {
++++++ +            top.appendChild(lastBotRow);
++++++-             top.style.display = 'block';
++++++-         } else {
++++++--            top.innerHTML = "";
++++++-             top.style.display = 'none';
++++++-         }
++++++++            top.style.display = 'block';
++++++++        } else {
++++++++            top.style.display = 'none';
++++++++        }
+++++++ 
+++++++-        // 3. Maintain Scroll Position
+++++++-        const newScrollHeight = viewport.scrollHeight;
+++++++-        const delta = newScrollHeight - prevScrollHeight;
++++++ -        
++++++-+
++++++-         if (lastUserRow) {
++++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++++-        if (delta > 0) {
+++++++-            viewport.scrollTop = prevScrollTop + delta;
++++++++        if (lastUserRow) {
++++++ +            bottom.appendChild(lastUserRow);
++++++-             bottom.style.display = 'block';
++++++-         } else {
++++++--            bottom.innerHTML = "";
++++++-             bottom.style.display = 'none';
++++++++            bottom.style.display = 'block';
++++++++        } else {
++++++++            bottom.style.display = 'none';
++++++          }
++++++          
++++++--        // If we moved stuff, scroll might need adjustment? 
++++++--        // Sticky logic handles the pins. History fills the middle.
+++++++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
++++++ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
++++++ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
++++++ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
++++++@@ -198,13 +13702,158 @@ index 3a092bfc..1a19d8a7 100644
++++++ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
++++++ +        }
++++++      }
+++++++-
+++++++-    // Deprecated / Aliased
+++++++-    function applyDuetPins() {}
++++++      
++++++--    // No-op for old sync padding (CSS sticky handles it now)
++++++      function syncDuetPadding() {}
++++++  
++++++-     function updateDuetView(row, role) {
++++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++++-    function updateDuetView(row, role) {}
++++++++    function updateDuetView(row, role) {
++++++ +      // Defer to applyDuetPins in next frame so DOM is ready
++++++-       requestAnimationFrame(applyDuetPins);
++++++++      requestAnimationFrame(applyDuetPins);
++++++++    }
+++++++ 
+++++++     function bindDuetListeners() {
+++++++        // Scroll logic is now native overflow
+++++++@@ -4365,12 +4387,15 @@
+++++++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
+++++++ 
+++++++     function getChatContainer() {
+++++++-      // Phase 4: Target the LIVE container (chat-log)
++++++++      // Phase 4: Target the real scroll container for appending?
++++++++      // No, we append to chat-log. The VIEW is the scroller.
++++++++      // But getChatContainer is usually strictly for finding where to APPEND.
+++++++       const chatLog = document.getElementById("chat-log");
+++++++       
+++++++       if (!chatLog) {
+++++++-         // Fallback or error
+++++++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
++++++++         // ... error ...
++++++++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
++++++++        // Visible UI Error (Phase A/B Requirement)
+++++++         const toastContainer = document.getElementById("toast-container");
+++++++         if (toastContainer) {
+++++++             const errDiv = document.createElement("div");
+++++++@@ -4378,7 +4403,7 @@
+++++++             errDiv.textContent = "Error: Chat container missing.";
+++++++             toastContainer.appendChild(errDiv);
+++++++         }
+++++++-        return document.getElementById("duet-history"); // Last resort
++++++++        return null;
+++++++       }
+++++++       return chatLog;
+++++++     }
+++++++@@ -4518,14 +4543,11 @@
+++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++++             if (!text.trim()) return;
+++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++++-            // Pass special flag to force into history backlog
+++++++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
++++++++            addMessage(role, text);
+++++++           });
+++++++           
+++++++-          // Force scroll logic for "hidden backlog"
+++++++-          syncDuetHistorySpacer();
+++++++-          scrollDuetHistoryToBottom();
+++++++-          // scrollChatToBottom(true); // Legacy call
++++++++          // Force scroll to bottom after initial load
++++++++          scrollChatToBottom(true);
+++++++         };
+++++++         if (renderedCount > 0) {
+++++++           renderMessages(messages);
+++++++@@ -4580,8 +4602,6 @@
+++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
++++++      }
++++++  
+++++++-    let globalMessageSequence = 0;
+++++++-
+++++++     function addMessage(role, text, options = {}) {
+++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++++       // Hide chat placeholder when first message appears
+++++++@@ -4598,9 +4618,6 @@
+++++++ 
+++++++       const row = document.createElement("div");
+++++++       row.className = `msg-row ${role}`;
+++++++-      // Timestamp and Sequence for robust sorting
+++++++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++++-      row.dataset.sequence = ++globalMessageSequence;
+++++++ 
+++++++       // Apply focus highlighting if a goal is focused
+++++++       if (othelloState.activeGoalId) {
+++++++@@ -4652,24 +4669,9 @@
+++++++ 
+++++++       row.appendChild(bubble);
+++++++       
+++++++-      // Phase 5: Routing for Duet vs Standard
+++++++-      const duetTop = document.getElementById("duet-top");
+++++++-      const duetBottom = document.getElementById("duet-bottom");
+++++++-      const historySpacer = document.getElementById("duet-history-spacer");
+++++++-
+++++++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++-      
+++++++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
+++++++-      const duetHistory = document.getElementById("duet-history");
+++++++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++++++-      
+++++++-      if (isHistoryLoad && duetHistory) {
+++++++-         // History always appends-to-end of the History Block (which is above Live)
+++++++-         duetHistory.appendChild(row);
+++++++-      } else {
+++++++-         // Live messages append strictly to the Live Container (#chat-log)
+++++++-         // This ensures standard Top-Down flow.
+++++++-         if (container) container.appendChild(row);
++++++++      // Append to the resolved container
++++++++      if (container) {
++++++++         container.appendChild(row);
+++++++       }
+++++++       
+++++++       updateDuetView(row, role);
+++++++@@ -5933,8 +5935,8 @@
+++++++       }
+++++++ 
+++++++       // Canonical text variable (Refetch input safely)
+++++++-      const input = document.getElementById('user-input');
+++++++-      let rawText = (override !== null ? override : (input?.value ?? ""));
++++++++      const currentInput = document.getElementById('user-input');
++++++++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
+++++++       
+++++++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
+++++++       
+++++++@@ -5945,12 +5947,31 @@
+++++++ 
+++++++       if (!text && !extraData.ui_action) return;
+++++++ 
+++++++-      // Phase B (Cleanup): Auto-archive pins on new user message
+++++++-      // This ensures the stage is cleared before the new user bubble appears.
+++++++-      // We only do this if it's a genuine user message (text present or ui_action).
+++++++-      if (typeof archivePinnedToHistory === "function") {
+++++++-          archivePinnedToHistory();
++++++++      // Duet Phase 2: History Management
++++++++      if (duetTurnIndex >= 1) {
++++++++          const history = document.getElementById("duet-history");
++++++++          const log = document.getElementById("chat-log");
++++++++          const view = document.getElementById("chat-view");
++++++++          
++++++++          if (history && log) {
++++++++              let restoreScroll = false;
++++++++              if (view) {
++++++++                  const dist = view.scrollHeight - (view.scrollTop + view.clientHeight);
++++++++                  restoreScroll = dist < 60;
++++++++              }
++++++++              
++++++++              while (log.firstChild) {
++++++++                  history.appendChild(log.firstChild);
++++++++              }
++++++++
++++++++              if (restoreScroll && view) {
++++++++                   setTimeout(() => {
++++++++                       view.scrollTop = view.scrollHeight;
++++++++                   }, 0);
++++++++              }
++++++++          }
+++++++       }
++++++++      duetTurnIndex++;
+++++++ 
+++++++       // Voice-first save command (Strict Command Mode)
+++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++++ diff --git a/othello_ui.html b/othello_ui.html
+++++-index a78c1b7b..d6ca18ec 100644
++++++index d6ca18ec..5b7fbe43 100644
+++++ --- a/othello_ui.html
+++++ +++ b/othello_ui.html
+++++-@@ -339,6 +339,7 @@
++++++@@ -339,10 +339,14 @@
+++++        <div id="chat-view" class="view" style="display:flex;">
+++++          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++++          
+++++-+        <!-- Only this is scrollable history -->
+++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++-         <div id="chat-log" class="chat-log"></div>
++++++-        <!-- Only this is scrollable history -->
++++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++++-        <div id="chat-log" class="chat-log"></div>
+++++++        <div id="duet-history" style="display:flex; flex-direction:column; padding:1rem; padding-bottom:0;"></div>
+++++++        
+++++++        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
+++++++             <!-- Only this is scrollable history -->
+++++++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++++             <div id="chat-log" class="chat-log"></div>
+++++++        </div>
++++++         
++++++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
++++++       </div>
+++++ diff --git a/static/othello.css b/static/othello.css
+++++-index 825c710b..c7cc1ae5 100644
++++++index 382eeb57..496353b0 100644
+++++ --- a/static/othello.css
+++++ +++ b/static/othello.css
+++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
++++++@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
++++++   position: relative;
+++++  }
+++++  
+++++- /* --- Duet Chat Mode (Unified) --- */
+++++--/* Phase 2: Fix the scroll container */
+++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++++- .chat-sheet {
++++++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++++/* Chat View IS the scroll container now */
++++++ #chat-view {
+++++    display: flex !important;
+++++-   flex-direction: column !important;
+++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++++- /* Header is rigid */
+++++- .chat-sheet__header {
+++++-   flex: 0 0 auto;
+++++-+  z-index: 200; /* Header stays absolutely on top */
+++++-+  position: relative;
+++++-+  box-shadow: 0 1px 0 var(--border);
++++++   flex-direction: column;
++++++-  flex: 1 1 0;
+++++++  flex: 1 1 0; /* Grow, shrink, basis 0 */
++++++   min-height: 0;
++++++-  overflow: hidden !important; /* View itself does NOT scroll */
+++++++  overflow-y: auto !important; /* The ONLY scrollbar */
+++++++  overflow-x: hidden;
++++++   position: relative;
++++++-  padding: 0;
+++++++  padding: 0; /* Strict */
+++++  }
+++++  
+++++- /* Input is rigid (footer) */
+++++- .input-bar {
+++++-   flex: 0 0 auto;
+++++-+  z-index: 200; /* Input stays absolutely on top */
+++++-+  position: relative;
+++++- }
+++++- 
+++++- /* Chat View IS the scroll container now */
+++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++++-   background: rgba(15, 23, 42, 0.98);
++++++-/* Duet Panes (Static Flex Items) */
+++++++/* Duet Panes (Sticky) - Transparent Rails */
++++++ .duet-pane {
++++++-  position: static; /* No longer sticky */
++++++-  flex: 0 0 auto; /* Rigid height based on content */
++++++-  z-index: 100;
++++++-  background: transparent;
+++++++  position: sticky;
+++++++  z-index: 100; /* Must beat messages */
+++++++  background: transparent; /* Transparent background */
+++++    padding: 0.75rem;
+++++    margin: 0;
+++++--  display: block !important;
++++++-  display: block;
++++++-  pointer-events: none;
+++++ +  display: block; /* always block, hidden by JS empty check if needed */
+++++-   backdrop-filter: blur(8px);
+++++--  /* Ensure they don't shrink away */
+++++-   flex-shrink: 0; 
+++++++  flex-shrink: 0;
+++++++  pointer-events: none; /* Let clicks pass through empty space */
+++++  }
+++++  
++++++-.duet-pane > * { pointer-events: auto; }
++++++-.duet-pane:empty { display: none !important; }
+++++++/* Re-enable pointer events on children (the bubbles) */
+++++++.duet-pane > * {
+++++++  pointer-events: auto;
+++++++}
++++++ 
++++++-/* Chat Log (Middle Scrollable History) */
++++++-#chat-log {
++++++-  display: flex !important;
++++++-  flex-direction: column;
++++++-  flex: 1 1 0; /* Takes all remaining space */
++++++-  overflow-y: auto !important; /* HISTORY scrolls here */
++++++-  min-height: 0;
++++++-  height: auto !important;
++++++-  padding: 1rem;
++++++-  padding-top: 0.5rem;
++++++-  padding-bottom: 0.5rem;
+++++ +/* Default hidden until populated */
+++++ +.duet-pane:empty {
+++++ +    display: none !important;
+++++-+}
+++++-+
++++++ }
++++++ 
++++++-/* Remove sticky-specific top/bottom since they are just flex order now */
+++++  .duet-pane--top {
+++++-   top: 0;
+++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++++-   overflow: visible !important; /* Let parent scroll it */
+++++-   height: auto !important;
+++++-   padding: 1rem;
++++++-  order: 1;
++++++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++  top: 0;
+++++++  /* Removed border/shadow for clean look */
+++++++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
++++++ }
++++++ 
++++++-#chat-log {
++++++-  order: 2; /* Middle */
+++++++.duet-pane--bottom {
+++++++  bottom: 0;
+++++++  /* Removed border/shadow for clean look */
+++++++  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
++++++ }
++++++ 
++++++-.duet-pane--bottom {
++++++-  order: 3;
++++++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++++/* Chat Log (History Flow) */
+++++++#chat-log {
+++++++  display: flex !important;
+++++++  flex-direction: column;
+++++++  flex: 1; /* occupy space between pins */
+++++++  overflow: visible !important; /* Let parent scroll it */
+++++++  height: auto !important;
+++++++  padding: 1rem;
+++++ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++++ +  padding-top: 1rem;
+++++ +  padding-bottom: 1rem;
+++++  }
+++++  
++++++-/* Ensure empty slots don't take space/border */
++++++-.duet-pane:empty {
++++++-    display: none !important;
++++++-    border: none !important;
+++++++#chat-sheet {
+++++++  display: flex;
+++++++  flex-direction: column;
+++++++  width: 100%;
++++++ }
++++++ 
+++++  /* Hide empty panes */
+++++ diff --git a/static/othello.js b/static/othello.js
+++++-index 3a092bfc..1a19d8a7 100644
++++++index 69c723cf..b0b18787 100644
+++++ --- a/static/othello.js
+++++ +++ b/static/othello.js
+++++-@@ -4300,76 +4300,81 @@
++++++@@ -793,8 +793,7 @@
++++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
++++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
++++++ 
++++++-    // Updated to support new Duet History container
++++++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++++    const chatLog = document.getElementById('chat-log');
++++++     // Relocated status to chat header (Phase 6 Fix)
++++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
++++++     const modeLabel = document.getElementById('current-mode-label');
++++++@@ -4301,61 +4300,83 @@
+++++        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++++      }
+++++  
+++++--    // Phase 3: Move nodes (no duplication)
+++++-+    // Phase 3: Canonical Move
+++++-     function applyDuetPins() {
+++++--        if (!isDuetEnabled()) return;
++++++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
++++++-    function syncDuetHistorySpacer() {
++++++-       // Deprecated in Single Scroll model
++++++-    }
++++++-
++++++-    function scrollDuetHistoryToBottom() {
++++++-       // Deprecated - use scrollChatToBottom
++++++-    }
++++++-
++++++-    // Call on resize - harmless
++++++-    window.addEventListener("resize", () => {});
++++++-
++++++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
++++++-    function archivePinnedToHistory() {
++++++-        // Source: Live Chat (#chat-log)
++++++-        // Dest: History (#duet-history)
++++++-        const liveContainer = document.getElementById("chat-log");
++++++-        const historyContainer = document.getElementById("duet-history");
++++++-        const viewport = document.getElementById("chat-view");
++++++-
++++++-        if (!liveContainer || !historyContainer || !viewport) return;
++++++-
++++++-        // 1. Capture Scroll State
++++++-        const prevScrollHeight = viewport.scrollHeight;
++++++-        const prevScrollTop = viewport.scrollTop;
++++++-
++++++-        // 2. Archive only valid message rows
++++++-        // We verify direct children to avoid deep grabbing
++++++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
+++++ -        
+++++--        const chatLog = document.getElementById("chat-log");
+++++-         const top = document.getElementById("duet-top");
+++++-         const bottom = document.getElementById("duet-bottom");
+++++--        if (!chatLog) return;
+++++--        
+++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++++--        // Actually, simpler approach for V1:
+++++--        // We only pin the LATEST. 
+++++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++++--        // Move them to pins? No, that breaks history flow if they are old.
+++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++++--        // This implies visual displacement.
+++++--        
+++++--        // Better Strategy:
+++++--        // 1. Clear pins.
+++++--        // 2. Scan chatLog rows.
+++++--        // 3. Last row -> if user, move to bottom.
+++++--        // 4. Last ASSISTANT row -> move to top.
+++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++++--        // This effectively empties the bottom of the history.
+++++--        
+++++--        // Implementation:
+++++--        // Find all .msg-row in chat main loop or chatLog
+++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++++ -        if (rows.length === 0) return;
++++++-
++++++-        const fragment = document.createDocumentFragment();
++++++-        // Since we iterate in DOM order, we preserve chronological order
++++++-        rows.forEach(r => fragment.appendChild(r));
+++++ -        
+++++--        // Find last user row
++++++-        historyContainer.appendChild(fragment);
+++++++    // Phase 3: Canonical Move
+++++++    function applyDuetPins() {
+++++++        const top = document.getElementById("duet-top");
+++++++        const bottom = document.getElementById("duet-bottom");
+++++ +        const chatLog = document.getElementById("chat-log");
+++++ +
+++++ +        // Fallback for safety
+++++@@ -146,45 +14174,39 @@ index 3a092bfc..1a19d8a7 100644
+++++ +        if (allRows.length === 0) return;
+++++ +
+++++ +        // 2. Scan for candidates
+++++-         let lastUserRow = null;
+++++-         let lastBotRow = null;
+++++--        
+++++++        let lastUserRow = null;
+++++++        let lastBotRow = null;
+++++ +
+++++-         // Scan backwards
+++++--        for (let i = rows.length - 1; i >= 0; i--) {
+++++--            const r = rows[i];
+++++++        // Scan backwards
+++++ +        for (let i = allRows.length - 1; i >= 0; i--) {
+++++ +            const r = allRows[i];
+++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++++ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++++-             if (lastUserRow && lastBotRow) break;
+++++-         }
+++++- 
+++++--        // Move to pins
+++++++            if (lastUserRow && lastBotRow) break;
+++++++        }
+++++++
+++++ +        // 3. Move to pins
+++++-         if (lastBotRow) {
+++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++++--            // Ensure display is correct
+++++++        if (lastBotRow) {
+++++ +            top.appendChild(lastBotRow);
+++++-             top.style.display = 'block';
+++++-         } else {
+++++--            top.innerHTML = "";
+++++-             top.style.display = 'none';
+++++-         }
+++++++            top.style.display = 'block';
+++++++        } else {
+++++++            top.style.display = 'none';
+++++++        }
++++++ 
++++++-        // 3. Maintain Scroll Position
++++++-        const newScrollHeight = viewport.scrollHeight;
++++++-        const delta = newScrollHeight - prevScrollHeight;
+++++ -        
+++++-+
+++++-         if (lastUserRow) {
+++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
++++++-        if (delta > 0) {
++++++-            viewport.scrollTop = prevScrollTop + delta;
+++++++        if (lastUserRow) {
+++++ +            bottom.appendChild(lastUserRow);
+++++-             bottom.style.display = 'block';
+++++-         } else {
+++++--            bottom.innerHTML = "";
+++++-             bottom.style.display = 'none';
+++++++            bottom.style.display = 'block';
+++++++        } else {
+++++++            bottom.style.display = 'none';
+++++          }
+++++          
+++++--        // If we moved stuff, scroll might need adjustment? 
+++++--        // Sticky logic handles the pins. History fills the middle.
++++++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
+++++ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++++ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++++ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++++@@ -198,13 +14220,157 @@ index 3a092bfc..1a19d8a7 100644
+++++ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++++ +        }
+++++      }
++++++-
++++++-    // Deprecated / Aliased
++++++-    function applyDuetPins() {}
+++++      
+++++--    // No-op for old sync padding (CSS sticky handles it now)
+++++      function syncDuetPadding() {}
+++++  
+++++-     function updateDuetView(row, role) {
+++++--      // Defer to applyDuetPins in next frame to let DOM settle
++++++-    function updateDuetView(row, role) {}
+++++++    function updateDuetView(row, role) {
+++++ +      // Defer to applyDuetPins in next frame so DOM is ready
+++++-       requestAnimationFrame(applyDuetPins);
+++++++      requestAnimationFrame(applyDuetPins);
+++++++    }
++++++ 
++++++     function bindDuetListeners() {
++++++        // Scroll logic is now native overflow
++++++@@ -4365,12 +4386,15 @@
++++++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
++++++ 
++++++     function getChatContainer() {
++++++-      // Phase 4: Target the LIVE container (chat-log)
+++++++      // Phase 4: Target the real scroll container for appending?
+++++++      // No, we append to chat-log. The VIEW is the scroller.
+++++++      // But getChatContainer is usually strictly for finding where to APPEND.
++++++       const chatLog = document.getElementById("chat-log");
++++++       
++++++       if (!chatLog) {
++++++-         // Fallback or error
++++++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
+++++++         // ... error ...
+++++++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++++        // Visible UI Error (Phase A/B Requirement)
++++++         const toastContainer = document.getElementById("toast-container");
++++++         if (toastContainer) {
++++++             const errDiv = document.createElement("div");
++++++@@ -4378,7 +4402,7 @@
++++++             errDiv.textContent = "Error: Chat container missing.";
++++++             toastContainer.appendChild(errDiv);
++++++         }
++++++-        return document.getElementById("duet-history"); // Last resort
+++++++        return null;
++++++       }
++++++       return chatLog;
++++++     }
++++++@@ -4518,14 +4542,11 @@
++++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
++++++             if (!text.trim()) return;
++++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
++++++-            // Pass special flag to force into history backlog
++++++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++++            addMessage(role, text);
++++++           });
++++++           
++++++-          // Force scroll logic for "hidden backlog"
++++++-          syncDuetHistorySpacer();
++++++-          scrollDuetHistoryToBottom();
++++++-          // scrollChatToBottom(true); // Legacy call
+++++++          // Force scroll to bottom after initial load
+++++++          scrollChatToBottom(true);
++++++         };
++++++         if (renderedCount > 0) {
++++++           renderMessages(messages);
++++++@@ -4580,8 +4601,6 @@
++++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
++++++     }
++++++ 
++++++-    let globalMessageSequence = 0;
++++++-
++++++     function addMessage(role, text, options = {}) {
++++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
++++++       // Hide chat placeholder when first message appears
++++++@@ -4598,9 +4617,6 @@
++++++ 
++++++       const row = document.createElement("div");
++++++       row.className = `msg-row ${role}`;
++++++-      // Timestamp and Sequence for robust sorting
++++++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
++++++-      row.dataset.sequence = ++globalMessageSequence;
++++++ 
++++++       // Apply focus highlighting if a goal is focused
++++++       if (othelloState.activeGoalId) {
++++++@@ -4652,24 +4668,9 @@
++++++ 
++++++       row.appendChild(bubble);
++++++       
++++++-      // Phase 5: Routing for Duet vs Standard
++++++-      const duetTop = document.getElementById("duet-top");
++++++-      const duetBottom = document.getElementById("duet-bottom");
++++++-      const historySpacer = document.getElementById("duet-history-spacer");
++++++-
++++++-      const isHistoryLoad = options && options.isHistoryLoad; 
++++++-      
++++++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
++++++-      const duetHistory = document.getElementById("duet-history");
++++++-      const isHistoryLoad = options && options.isHistoryLoad; 
++++++-      
++++++-      if (isHistoryLoad && duetHistory) {
++++++-         // History always appends-to-end of the History Block (which is above Live)
++++++-         duetHistory.appendChild(row);
++++++-      } else {
++++++-         // Live messages append strictly to the Live Container (#chat-log)
++++++-         // This ensures standard Top-Down flow.
++++++-         if (container) container.appendChild(row);
+++++++      // Append to the resolved container
+++++++      if (container) {
+++++++         container.appendChild(row);
++++++       }
++++++       
++++++       updateDuetView(row, role);
++++++@@ -5920,6 +5921,20 @@
++++++         }
+++++      }
+++++  
+++++++    function maybePromoteDuetToHistory() {
+++++++      const live = document.getElementById("chat-log");
+++++++      const hist = document.getElementById("duet-history");
+++++++      if (live && hist && live.children.length > 0) {
+++++++        // move existing duet into history
+++++++        const nodes = Array.from(live.children);
+++++++        for (const n of nodes) hist.appendChild(n);
+++++++        live.innerHTML = "";
+++++++        console.debug("[duet] promoted", nodes.length, "nodes to history. histChildren=", hist.children.length);
+++++++      } else {
+++++++        console.debug("[duet] no promotion. liveChildren=", live?.children?.length, "hist=", !!hist);
+++++++      }
+++++++    }
+++++++
++++++     async function sendMessage(overrideText = null, extraData = {}) {
++++++       // 1) Robust String Safety & Diagnostic
++++++       let override = overrideText;
++++++@@ -5933,8 +5948,8 @@
++++++       }
++++++ 
++++++       // Canonical text variable (Refetch input safely)
++++++-      const input = document.getElementById('user-input');
++++++-      let rawText = (override !== null ? override : (input?.value ?? ""));
+++++++      const currentInput = document.getElementById('user-input');
+++++++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
++++++       
++++++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
++++++       
++++++@@ -5945,12 +5960,8 @@
++++++ 
++++++       if (!text && !extraData.ui_action) return;
++++++ 
++++++-      // Phase B (Cleanup): Auto-archive pins on new user message
++++++-      // This ensures the stage is cleared before the new user bubble appears.
++++++-      // We only do this if it's a genuine user message (text present or ui_action).
++++++-      if (typeof archivePinnedToHistory === "function") {
++++++-          archivePinnedToHistory();
++++++-      }
+++++++      // Phase 2: History Promotion (Move & Clear)
+++++++      maybePromoteDuetToHistory();
++++++ 
++++++       // Voice-first save command (Strict Command Mode)
++++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
++++ diff --git a/othello_ui.html b/othello_ui.html
++++-index a78c1b7b..d6ca18ec 100644
+++++index d6ca18ec..5b7fbe43 100644
++++ --- a/othello_ui.html
++++ +++ b/othello_ui.html
++++-@@ -339,6 +339,7 @@
+++++@@ -339,10 +339,14 @@
++++        <div id="chat-view" class="view" style="display:flex;">
++++          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
++++          
++++-+        <!-- Only this is scrollable history -->
++++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++-         <div id="chat-log" class="chat-log"></div>
+++++-        <!-- Only this is scrollable history -->
+++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++-        <div id="chat-log" class="chat-log"></div>
++++++        <div id="duet-history" style="display:flex; flex-direction:column; padding:1rem; padding-bottom:0;"></div>
++++++        
++++++        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
++++++             <!-- Only this is scrollable history -->
++++++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++++             <div id="chat-log" class="chat-log"></div>
++++++        </div>
+++++         
+++++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++++       </div>
++++ diff --git a/static/othello.css b/static/othello.css
++++-index 825c710b..c7cc1ae5 100644
+++++index 382eeb57..496353b0 100644
++++ --- a/static/othello.css
++++ +++ b/static/othello.css
++++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++++@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
+++++   position: relative;
++++  }
++++  
++++- /* --- Duet Chat Mode (Unified) --- */
++++--/* Phase 2: Fix the scroll container */
++++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
++++- .chat-sheet {
+++++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
++++++/* Chat View IS the scroll container now */
+++++ #chat-view {
++++    display: flex !important;
++++-   flex-direction: column !important;
++++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
++++- /* Header is rigid */
++++- .chat-sheet__header {
++++-   flex: 0 0 auto;
++++-+  z-index: 200; /* Header stays absolutely on top */
++++-+  position: relative;
++++-+  box-shadow: 0 1px 0 var(--border);
++++- }
++++- 
++++- /* Input is rigid (footer) */
++++- .input-bar {
++++-   flex: 0 0 auto;
++++-+  z-index: 200; /* Input stays absolutely on top */
++++-+  position: relative;
+++++   flex-direction: column;
+++++-  flex: 1 1 0;
++++++  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++++   min-height: 0;
+++++-  overflow: hidden !important; /* View itself does NOT scroll */
++++++  overflow-y: auto !important; /* The ONLY scrollbar */
++++++  overflow-x: hidden;
+++++   position: relative;
+++++-  padding: 0;
++++++  padding: 0; /* Strict */
++++  }
++++  
++++- /* Chat View IS the scroll container now */
++++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
++++-   background: rgba(15, 23, 42, 0.98);
+++++-/* Duet Panes (Static Flex Items) */
++++++/* Duet Panes (Sticky) - Transparent Rails */
+++++ .duet-pane {
+++++-  position: static; /* No longer sticky */
+++++-  flex: 0 0 auto; /* Rigid height based on content */
+++++-  z-index: 100;
+++++-  background: transparent;
++++++  position: sticky;
++++++  z-index: 100; /* Must beat messages */
++++++  background: transparent; /* Transparent background */
++++    padding: 0.75rem;
++++    margin: 0;
++++--  display: block !important;
+++++-  display: block;
+++++-  pointer-events: none;
++++ +  display: block; /* always block, hidden by JS empty check if needed */
++++-   backdrop-filter: blur(8px);
++++--  /* Ensure they don't shrink away */
++++-   flex-shrink: 0; 
++++++  flex-shrink: 0;
++++++  pointer-events: none; /* Let clicks pass through empty space */
++++  }
++++  
+++++-.duet-pane > * { pointer-events: auto; }
+++++-.duet-pane:empty { display: none !important; }
++++++/* Re-enable pointer events on children (the bubbles) */
++++++.duet-pane > * {
++++++  pointer-events: auto;
++++++}
+++++ 
+++++-/* Chat Log (Middle Scrollable History) */
+++++-#chat-log {
+++++-  display: flex !important;
+++++-  flex-direction: column;
+++++-  flex: 1 1 0; /* Takes all remaining space */
+++++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++++-  min-height: 0;
+++++-  height: auto !important;
+++++-  padding: 1rem;
+++++-  padding-top: 0.5rem;
+++++-  padding-bottom: 0.5rem;
++++ +/* Default hidden until populated */
++++ +.duet-pane:empty {
++++ +    display: none !important;
++++-+}
++++-+
+++++ }
+++++ 
+++++-/* Remove sticky-specific top/bottom since they are just flex order now */
++++  .duet-pane--top {
++++-   top: 0;
++++-   border-bottom: 1px solid rgba(255,255,255,0.1);
++++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
++++-   overflow: visible !important; /* Let parent scroll it */
++++-   height: auto !important;
++++-   padding: 1rem;
+++++-  order: 1;
+++++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++++  top: 0;
++++++  /* Removed border/shadow for clean look */
++++++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
++++++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++++ }
+++++ 
+++++-#chat-log {
+++++-  order: 2; /* Middle */
++++++.duet-pane--bottom {
++++++  bottom: 0;
++++++  /* Removed border/shadow for clean look */
++++++  /* border-top: 1px solid rgba(255,255,255,0.1); */
++++++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++++ }
+++++ 
+++++-.duet-pane--bottom {
+++++-  order: 3;
+++++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++++/* Chat Log (History Flow) */
++++++#chat-log {
++++++  display: flex !important;
++++++  flex-direction: column;
++++++  flex: 1; /* occupy space between pins */
++++++  overflow: visible !important; /* Let parent scroll it */
++++++  height: auto !important;
++++++  padding: 1rem;
++++ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
++++ +  padding-top: 1rem;
++++ +  padding-bottom: 1rem;
++++  }
++++  
+++++-/* Ensure empty slots don't take space/border */
+++++-.duet-pane:empty {
+++++-    display: none !important;
+++++-    border: none !important;
++++++#chat-sheet {
++++++  display: flex;
++++++  flex-direction: column;
++++++  width: 100%;
+++++ }
+++++ 
++++  /* Hide empty panes */
++++ diff --git a/static/othello.js b/static/othello.js
++++-index 3a092bfc..1a19d8a7 100644
+++++index 69c723cf..b0b18787 100644
++++ --- a/static/othello.js
++++ +++ b/static/othello.js
++++-@@ -4300,76 +4300,81 @@
+++++@@ -793,8 +793,7 @@
+++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++++ 
+++++-    // Updated to support new Duet History container
+++++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
++++++    const chatLog = document.getElementById('chat-log');
+++++     // Relocated status to chat header (Phase 6 Fix)
+++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++++     const modeLabel = document.getElementById('current-mode-label');
+++++@@ -4301,61 +4300,83 @@
++++        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
++++      }
++++  
++++--    // Phase 3: Move nodes (no duplication)
++++-+    // Phase 3: Canonical Move
++++-     function applyDuetPins() {
++++--        if (!isDuetEnabled()) return;
++++--        
++++--        const chatLog = document.getElementById("chat-log");
++++-         const top = document.getElementById("duet-top");
++++-         const bottom = document.getElementById("duet-bottom");
++++--        if (!chatLog) return;
+++++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++++-    function syncDuetHistorySpacer() {
+++++-       // Deprecated in Single Scroll model
+++++-    }
+++++-
+++++-    function scrollDuetHistoryToBottom() {
+++++-       // Deprecated - use scrollChatToBottom
+++++-    }
+++++-
+++++-    // Call on resize - harmless
+++++-    window.addEventListener("resize", () => {});
+++++-
+++++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++++-    function archivePinnedToHistory() {
+++++-        // Source: Live Chat (#chat-log)
+++++-        // Dest: History (#duet-history)
+++++-        const liveContainer = document.getElementById("chat-log");
+++++-        const historyContainer = document.getElementById("duet-history");
+++++-        const viewport = document.getElementById("chat-view");
+++++-
+++++-        if (!liveContainer || !historyContainer || !viewport) return;
+++++-
+++++-        // 1. Capture Scroll State
+++++-        const prevScrollHeight = viewport.scrollHeight;
+++++-        const prevScrollTop = viewport.scrollTop;
+++++-
+++++-        // 2. Archive only valid message rows
+++++-        // We verify direct children to avoid deep grabbing
+++++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
++++ -        
++++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
++++--        // Actually, simpler approach for V1:
++++--        // We only pin the LATEST. 
++++--        // Iterate chatLog children. Find last user msg, last bot msg.
++++--        // Move them to pins? No, that breaks history flow if they are old.
++++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
++++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
++++--        // This implies visual displacement.
++++--        
++++--        // Better Strategy:
++++--        // 1. Clear pins.
++++--        // 2. Scan chatLog rows.
++++--        // 3. Last row -> if user, move to bottom.
++++--        // 4. Last ASSISTANT row -> move to top.
++++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
++++--        // This effectively empties the bottom of the history.
++++--        
++++--        // Implementation:
++++--        // Find all .msg-row in chat main loop or chatLog
++++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
++++ -        if (rows.length === 0) return;
+++++-
+++++-        const fragment = document.createDocumentFragment();
+++++-        // Since we iterate in DOM order, we preserve chronological order
+++++-        rows.forEach(r => fragment.appendChild(r));
++++ -        
++++--        // Find last user row
+++++-        historyContainer.appendChild(fragment);
++++++    // Phase 3: Canonical Move
++++++    function applyDuetPins() {
++++++        const top = document.getElementById("duet-top");
++++++        const bottom = document.getElementById("duet-bottom");
++++ +        const chatLog = document.getElementById("chat-log");
++++ +
++++ +        // Fallback for safety
++++@@ -146,45 +14692,39 @@ index 3a092bfc..1a19d8a7 100644
++++ +        if (allRows.length === 0) return;
++++ +
++++ +        // 2. Scan for candidates
++++-         let lastUserRow = null;
++++-         let lastBotRow = null;
++++--        
++++++        let lastUserRow = null;
++++++        let lastBotRow = null;
++++ +
++++-         // Scan backwards
++++--        for (let i = rows.length - 1; i >= 0; i--) {
++++--            const r = rows[i];
++++++        // Scan backwards
++++ +        for (let i = allRows.length - 1; i >= 0; i--) {
++++ +            const r = allRows[i];
++++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
++++++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++++ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
++++-             if (lastUserRow && lastBotRow) break;
++++-         }
++++- 
++++--        // Move to pins
++++++            if (lastUserRow && lastBotRow) break;
++++++        }
++++++
++++ +        // 3. Move to pins
++++-         if (lastBotRow) {
++++--            top.appendChild(lastBotRow); // Moves it out of chatLog
++++--            // Ensure display is correct
++++++        if (lastBotRow) {
++++ +            top.appendChild(lastBotRow);
++++-             top.style.display = 'block';
++++-         } else {
++++--            top.innerHTML = "";
++++-             top.style.display = 'none';
++++-         }
++++++            top.style.display = 'block';
++++++        } else {
++++++            top.style.display = 'none';
++++++        }
+++++ 
+++++-        // 3. Maintain Scroll Position
+++++-        const newScrollHeight = viewport.scrollHeight;
+++++-        const delta = newScrollHeight - prevScrollHeight;
++++ -        
++++-+
++++-         if (lastUserRow) {
++++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++++-        if (delta > 0) {
+++++-            viewport.scrollTop = prevScrollTop + delta;
++++++        if (lastUserRow) {
++++ +            bottom.appendChild(lastUserRow);
++++-             bottom.style.display = 'block';
++++-         } else {
++++--            bottom.innerHTML = "";
++++-             bottom.style.display = 'none';
++++++            bottom.style.display = 'block';
++++++        } else {
++++++            bottom.style.display = 'none';
++++          }
++++          
++++--        // If we moved stuff, scroll might need adjustment? 
++++--        // Sticky logic handles the pins. History fills the middle.
+++++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
++++ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
++++ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
++++ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
++++@@ -198,13 +14738,157 @@ index 3a092bfc..1a19d8a7 100644
++++ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
++++ +        }
++++      }
+++++-
+++++-    // Deprecated / Aliased
+++++-    function applyDuetPins() {}
++++      
++++--    // No-op for old sync padding (CSS sticky handles it now)
++++      function syncDuetPadding() {}
++++  
++++-     function updateDuetView(row, role) {
++++--      // Defer to applyDuetPins in next frame to let DOM settle
+++++-    function updateDuetView(row, role) {}
++++++    function updateDuetView(row, role) {
++++ +      // Defer to applyDuetPins in next frame so DOM is ready
++++-       requestAnimationFrame(applyDuetPins);
++++++      requestAnimationFrame(applyDuetPins);
++++++    }
+++++ 
+++++     function bindDuetListeners() {
+++++        // Scroll logic is now native overflow
+++++@@ -4365,12 +4386,15 @@
+++++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
+++++ 
+++++     function getChatContainer() {
+++++-      // Phase 4: Target the LIVE container (chat-log)
++++++      // Phase 4: Target the real scroll container for appending?
++++++      // No, we append to chat-log. The VIEW is the scroller.
++++++      // But getChatContainer is usually strictly for finding where to APPEND.
+++++       const chatLog = document.getElementById("chat-log");
+++++       
+++++       if (!chatLog) {
+++++-         // Fallback or error
+++++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
++++++         // ... error ...
++++++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
++++++        // Visible UI Error (Phase A/B Requirement)
+++++         const toastContainer = document.getElementById("toast-container");
+++++         if (toastContainer) {
+++++             const errDiv = document.createElement("div");
+++++@@ -4378,7 +4402,7 @@
+++++             errDiv.textContent = "Error: Chat container missing.";
+++++             toastContainer.appendChild(errDiv);
+++++         }
+++++-        return document.getElementById("duet-history"); // Last resort
++++++        return null;
+++++       }
+++++       return chatLog;
++++      }
+++++@@ -4518,14 +4542,11 @@
+++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++++             if (!text.trim()) return;
+++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++++-            // Pass special flag to force into history backlog
+++++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
++++++            addMessage(role, text);
+++++           });
+++++           
+++++-          // Force scroll logic for "hidden backlog"
+++++-          syncDuetHistorySpacer();
+++++-          scrollDuetHistoryToBottom();
+++++-          // scrollChatToBottom(true); // Legacy call
++++++          // Force scroll to bottom after initial load
++++++          scrollChatToBottom(true);
+++++         };
+++++         if (renderedCount > 0) {
+++++           renderMessages(messages);
+++++@@ -4580,8 +4601,6 @@
+++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++++     }
+++++ 
+++++-    let globalMessageSequence = 0;
+++++-
+++++     function addMessage(role, text, options = {}) {
+++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++++       // Hide chat placeholder when first message appears
+++++@@ -4598,9 +4617,6 @@
+++++ 
+++++       const row = document.createElement("div");
+++++       row.className = `msg-row ${role}`;
+++++-      // Timestamp and Sequence for robust sorting
+++++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++++-      row.dataset.sequence = ++globalMessageSequence;
+++++ 
+++++       // Apply focus highlighting if a goal is focused
+++++       if (othelloState.activeGoalId) {
+++++@@ -4652,24 +4668,9 @@
+++++ 
+++++       row.appendChild(bubble);
+++++       
+++++-      // Phase 5: Routing for Duet vs Standard
+++++-      const duetTop = document.getElementById("duet-top");
+++++-      const duetBottom = document.getElementById("duet-bottom");
+++++-      const historySpacer = document.getElementById("duet-history-spacer");
+++++-
+++++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++++-      
+++++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
+++++-      const duetHistory = document.getElementById("duet-history");
+++++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++++-      
+++++-      if (isHistoryLoad && duetHistory) {
+++++-         // History always appends-to-end of the History Block (which is above Live)
+++++-         duetHistory.appendChild(row);
+++++-      } else {
+++++-         // Live messages append strictly to the Live Container (#chat-log)
+++++-         // This ensures standard Top-Down flow.
+++++-         if (container) container.appendChild(row);
++++++      // Append to the resolved container
++++++      if (container) {
++++++         container.appendChild(row);
+++++       }
+++++       
+++++       updateDuetView(row, role);
+++++@@ -5920,6 +5921,20 @@
+++++         }
+++++     }
+++++ 
++++++    function maybePromoteDuetToHistory() {
++++++      const live = document.getElementById("chat-log");
++++++      const hist = document.getElementById("duet-history");
++++++      if (live && hist && live.children.length > 0) {
++++++        // move existing duet into history
++++++        const nodes = Array.from(live.children);
++++++        for (const n of nodes) hist.appendChild(n);
++++++        live.innerHTML = "";
++++++        console.debug("[duet] promoted", nodes.length, "nodes to history. histChildren=", hist.children.length);
++++++      } else {
++++++        console.debug("[duet] no promotion. liveChildren=", live?.children?.length, "hist=", !!hist);
++++++      }
++++++    }
++++++
+++++     async function sendMessage(overrideText = null, extraData = {}) {
+++++       // 1) Robust String Safety & Diagnostic
+++++       let override = overrideText;
+++++@@ -5933,8 +5948,8 @@
+++++       }
+++++ 
+++++       // Canonical text variable (Refetch input safely)
+++++-      const input = document.getElementById('user-input');
+++++-      let rawText = (override !== null ? override : (input?.value ?? ""));
++++++      const currentInput = document.getElementById('user-input');
++++++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
+++++       
+++++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
+++++       
+++++@@ -5945,12 +5960,8 @@
+++++ 
+++++       if (!text && !extraData.ui_action) return;
+++++ 
+++++-      // Phase B (Cleanup): Auto-archive pins on new user message
+++++-      // This ensures the stage is cleared before the new user bubble appears.
+++++-      // We only do this if it's a genuine user message (text present or ui_action).
+++++-      if (typeof archivePinnedToHistory === "function") {
+++++-          archivePinnedToHistory();
+++++-      }
++++++      // Phase 2: History Promotion (Move & Clear)
++++++      maybePromoteDuetToHistory();
++++  
+++++       // Voice-first save command (Strict Command Mode)
+++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+++ diff --git a/othello_ui.html b/othello_ui.html
+++-index a78c1b7b..d6ca18ec 100644
++++index d6ca18ec..5b7fbe43 100644
+++ --- a/othello_ui.html
+++ +++ b/othello_ui.html
+++-@@ -339,6 +339,7 @@
++++@@ -339,10 +339,14 @@
+++        <div id="chat-view" class="view" style="display:flex;">
+++          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+++          
+++-+        <!-- Only this is scrollable history -->
+++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++-         <div id="chat-log" class="chat-log"></div>
++++-        <!-- Only this is scrollable history -->
++++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++-        <div id="chat-log" class="chat-log"></div>
+++++        <div id="duet-history" style="display:flex; flex-direction:column; padding:1rem; padding-bottom:0;"></div>
+++++        
+++++        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
+++++             <!-- Only this is scrollable history -->
+++++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++++             <div id="chat-log" class="chat-log"></div>
+++++        </div>
++++         
++++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
++++       </div>
+++ diff --git a/static/othello.css b/static/othello.css
+++-index 825c710b..c7cc1ae5 100644
++++index 382eeb57..940b2b08 100644
+++ --- a/static/othello.css
+++ +++ b/static/othello.css
+++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
++++@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
++++   position: relative;
+++  }
+++  
+++- /* --- Duet Chat Mode (Unified) --- */
+++--/* Phase 2: Fix the scroll container */
+++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+++- .chat-sheet {
++++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++++/* Chat View IS the scroll container now */
++++ #chat-view {
+++    display: flex !important;
+++-   flex-direction: column !important;
+++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+++- /* Header is rigid */
+++- .chat-sheet__header {
+++-   flex: 0 0 auto;
+++-+  z-index: 200; /* Header stays absolutely on top */
+++-+  position: relative;
+++-+  box-shadow: 0 1px 0 var(--border);
++++   flex-direction: column;
++++-  flex: 1 1 0;
+++++  flex: 1 1 0; /* Grow, shrink, basis 0 */
++++   min-height: 0;
++++-  overflow: hidden !important; /* View itself does NOT scroll */
+++++  overflow-y: auto !important; /* The ONLY scrollbar */
+++++  overflow-x: hidden;
++++   position: relative;
++++-  padding: 0;
+++++  padding: 0; /* Strict */
+++  }
+++  
+++- /* Input is rigid (footer) */
+++- .input-bar {
+++-   flex: 0 0 auto;
+++-+  z-index: 200; /* Input stays absolutely on top */
+++-+  position: relative;
+++- }
+++- 
+++- /* Chat View IS the scroll container now */
+++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+++-   background: rgba(15, 23, 42, 0.98);
++++-/* Duet Panes (Static Flex Items) */
+++++/* Duet Panes (Sticky) - Transparent Rails */
++++ .duet-pane {
++++-  position: static; /* No longer sticky */
++++-  flex: 0 0 auto; /* Rigid height based on content */
++++-  z-index: 100;
++++-  background: transparent;
+++++  position: sticky;
+++++  z-index: 100; /* Must beat messages */
+++++  background: transparent; /* Transparent background */
+++    padding: 0.75rem;
+++    margin: 0;
+++--  display: block !important;
++++-  display: block;
++++-  pointer-events: none;
+++ +  display: block; /* always block, hidden by JS empty check if needed */
+++-   backdrop-filter: blur(8px);
+++--  /* Ensure they don't shrink away */
+++-   flex-shrink: 0; 
+++++  flex-shrink: 0;
+++++  pointer-events: none; /* Let clicks pass through empty space */
+++  }
+++  
++++-.duet-pane > * { pointer-events: auto; }
++++-.duet-pane:empty { display: none !important; }
+++++/* Re-enable pointer events on children (the bubbles) */
+++++.duet-pane > * {
+++++  pointer-events: auto;
+++++}
++++ 
++++-/* Chat Log (Middle Scrollable History) */
++++-#chat-log {
++++-  display: flex !important;
++++-  flex-direction: column;
++++-  flex: 1 1 0; /* Takes all remaining space */
++++-  overflow-y: auto !important; /* HISTORY scrolls here */
++++-  min-height: 0;
++++-  height: auto !important;
++++-  padding: 1rem;
++++-  padding-top: 0.5rem;
++++-  padding-bottom: 0.5rem;
+++ +/* Default hidden until populated */
+++ +.duet-pane:empty {
+++ +    display: none !important;
+++-+}
+++-+
++++ }
++++ 
++++-/* Remove sticky-specific top/bottom since they are just flex order now */
+++  .duet-pane--top {
+++-   top: 0;
+++-   border-bottom: 1px solid rgba(255,255,255,0.1);
+++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+++-   overflow: visible !important; /* Let parent scroll it */
+++-   height: auto !important;
+++-   padding: 1rem;
++++-  order: 1;
++++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++  top: 0;
+++++  /* Removed border/shadow for clean look */
+++++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
++++ }
++++ 
++++-#chat-log {
++++-  order: 2; /* Middle */
+++++.duet-pane--bottom {
+++++  bottom: 0;
+++++  /* Removed border/shadow for clean look */
+++++  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
++++ }
++++ 
++++-.duet-pane--bottom {
++++-  order: 3;
++++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++++/* Chat Log (History Flow) */
+++++#chat-log {
+++++  display: flex !important;
+++++  flex-direction: column;
+++++  flex: 1; /* occupy space between pins */
+++++  overflow: visible !important; /* Let parent scroll it */
+++++  height: auto !important;
+++++  padding: 1rem;
+++ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+++ +  padding-top: 1rem;
+++ +  padding-bottom: 1rem;
+++  }
+++  
++++-/* Ensure empty slots don't take space/border */
++++-.duet-pane:empty {
++++-    display: none !important;
++++-    border: none !important;
+++++#chat-sheet {
+++++  display: flex;
+++++  flex-direction: column;
+++++  width: 100%;
++++ }
++++ 
+++  /* Hide empty panes */
++++@@ -2271,3 +2278,35 @@ body.chat-open #global-chat-fab {
++++ /* Cleanup old classes */
++++ .duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
++++ 
+++++/* --- Duet Phase 2 History Fixes --- */
+++++#duet-history {
+++++  display: flex !important;
+++++  flex-direction: column !important;
+++++  padding: 12px 1rem;
+++++  width: 100%;
+++++}
+++++
+++++.history-duet {
+++++  display: flex !important;
+++++  flex-direction: column !important;
+++++  margin-bottom: 24px;
+++++  border-bottom: 1px solid var(--border);
+++++  padding-bottom: 24px;
+++++}
+++++
+++++.history-duet:last-child {
+++++  border-bottom: none;
+++++  margin-bottom: 0;
+++++}
+++++
+++++/* Reserve space: REMOVE fixed padding that creates dead gap. Layout handles height. */
+++++#chat-view {
+++++  padding-bottom: 0px !important;
+++++}
+++++
+++++/* Visual separation for the Live area (Gap between History and Live) */
+++++#chat-sheet {
+++++  margin-top: 12px;
+++++  padding-top: 12px;
+++++}
+++++
+++ diff --git a/static/othello.js b/static/othello.js
+++-index 3a092bfc..1a19d8a7 100644
++++index 69c723cf..2c776ef8 100644
+++ --- a/static/othello.js
+++ +++ b/static/othello.js
+++-@@ -4300,76 +4300,81 @@
++++@@ -793,8 +793,7 @@
++++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
++++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
++++ 
++++-    // Updated to support new Duet History container
++++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++++    const chatLog = document.getElementById('chat-log');
++++     // Relocated status to chat header (Phase 6 Fix)
++++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
++++     const modeLabel = document.getElementById('current-mode-label');
++++@@ -4301,61 +4300,83 @@
+++        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+++      }
+++  
+++--    // Phase 3: Move nodes (no duplication)
+++-+    // Phase 3: Canonical Move
+++-     function applyDuetPins() {
+++--        if (!isDuetEnabled()) return;
+++--        
+++--        const chatLog = document.getElementById("chat-log");
+++-         const top = document.getElementById("duet-top");
+++-         const bottom = document.getElementById("duet-bottom");
+++--        if (!chatLog) return;
+++--        
+++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+++--        // Actually, simpler approach for V1:
+++--        // We only pin the LATEST. 
+++--        // Iterate chatLog children. Find last user msg, last bot msg.
+++--        // Move them to pins? No, that breaks history flow if they are old.
+++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+++--        // This implies visual displacement.
++++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
++++-    function syncDuetHistorySpacer() {
++++-       // Deprecated in Single Scroll model
++++-    }
++++-
++++-    function scrollDuetHistoryToBottom() {
++++-       // Deprecated - use scrollChatToBottom
++++-    }
++++-
++++-    // Call on resize - harmless
++++-    window.addEventListener("resize", () => {});
++++-
++++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
++++-    function archivePinnedToHistory() {
++++-        // Source: Live Chat (#chat-log)
++++-        // Dest: History (#duet-history)
++++-        const liveContainer = document.getElementById("chat-log");
++++-        const historyContainer = document.getElementById("duet-history");
++++-        const viewport = document.getElementById("chat-view");
++++-
++++-        if (!liveContainer || !historyContainer || !viewport) return;
++++-
++++-        // 1. Capture Scroll State
++++-        const prevScrollHeight = viewport.scrollHeight;
++++-        const prevScrollTop = viewport.scrollTop;
++++-
++++-        // 2. Archive only valid message rows
++++-        // We verify direct children to avoid deep grabbing
++++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
+++ -        
+++--        // Better Strategy:
+++--        // 1. Clear pins.
+++--        // 2. Scan chatLog rows.
+++--        // 3. Last row -> if user, move to bottom.
+++--        // 4. Last ASSISTANT row -> move to top.
+++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+++--        // This effectively empties the bottom of the history.
+++--        
+++--        // Implementation:
+++--        // Find all .msg-row in chat main loop or chatLog
+++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+++ -        if (rows.length === 0) return;
++++-
++++-        const fragment = document.createDocumentFragment();
++++-        // Since we iterate in DOM order, we preserve chronological order
++++-        rows.forEach(r => fragment.appendChild(r));
+++ -        
+++--        // Find last user row
++++-        historyContainer.appendChild(fragment);
+++++    // Phase 3: Canonical Move
+++++    function applyDuetPins() {
+++++        const top = document.getElementById("duet-top");
+++++        const bottom = document.getElementById("duet-bottom");
+++ +        const chatLog = document.getElementById("chat-log");
+++ +
+++ +        // Fallback for safety
+++@@ -146,45 +15248,39 @@ index 3a092bfc..1a19d8a7 100644
+++ +        if (allRows.length === 0) return;
+++ +
+++ +        // 2. Scan for candidates
+++-         let lastUserRow = null;
+++-         let lastBotRow = null;
+++--        
+++++        let lastUserRow = null;
+++++        let lastBotRow = null;
+++ +
+++-         // Scan backwards
+++--        for (let i = rows.length - 1; i >= 0; i--) {
+++--            const r = rows[i];
+++++        // Scan backwards
+++ +        for (let i = allRows.length - 1; i >= 0; i--) {
+++ +            const r = allRows[i];
+++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+++ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+++-             if (lastUserRow && lastBotRow) break;
+++-         }
+++- 
+++--        // Move to pins
+++++            if (lastUserRow && lastBotRow) break;
+++++        }
+++++
+++ +        // 3. Move to pins
+++-         if (lastBotRow) {
+++--            top.appendChild(lastBotRow); // Moves it out of chatLog
+++--            // Ensure display is correct
+++++        if (lastBotRow) {
+++ +            top.appendChild(lastBotRow);
+++-             top.style.display = 'block';
+++-         } else {
+++--            top.innerHTML = "";
+++-             top.style.display = 'none';
+++-         }
+++++            top.style.display = 'block';
+++++        } else {
+++++            top.style.display = 'none';
+++++        }
++++ 
++++-        // 3. Maintain Scroll Position
++++-        const newScrollHeight = viewport.scrollHeight;
++++-        const delta = newScrollHeight - prevScrollHeight;
+++ -        
+++-+
+++-         if (lastUserRow) {
+++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
++++-        if (delta > 0) {
++++-            viewport.scrollTop = prevScrollTop + delta;
+++++        if (lastUserRow) {
+++ +            bottom.appendChild(lastUserRow);
+++-             bottom.style.display = 'block';
+++-         } else {
+++--            bottom.innerHTML = "";
+++-             bottom.style.display = 'none';
+++++            bottom.style.display = 'block';
+++++        } else {
+++++            bottom.style.display = 'none';
+++          }
+++          
+++--        // If we moved stuff, scroll might need adjustment? 
+++--        // Sticky logic handles the pins. History fills the middle.
++++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
+++ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+++ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+++ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
+++@@ -198,13 +15294,185 @@ index 3a092bfc..1a19d8a7 100644
+++ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+++ +        }
+++      }
++++-
++++-    // Deprecated / Aliased
++++-    function applyDuetPins() {}
+++      
+++--    // No-op for old sync padding (CSS sticky handles it now)
+++      function syncDuetPadding() {}
+++  
+++-     function updateDuetView(row, role) {
+++--      // Defer to applyDuetPins in next frame to let DOM settle
++++-    function updateDuetView(row, role) {}
+++++    function updateDuetView(row, role) {
+++ +      // Defer to applyDuetPins in next frame so DOM is ready
+++-       requestAnimationFrame(applyDuetPins);
+++++      requestAnimationFrame(applyDuetPins);
+++++    }
++++ 
++++     function bindDuetListeners() {
++++        // Scroll logic is now native overflow
++++@@ -4365,12 +4386,15 @@
++++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
++++ 
++++     function getChatContainer() {
++++-      // Phase 4: Target the LIVE container (chat-log)
+++++      // Phase 4: Target the real scroll container for appending?
+++++      // No, we append to chat-log. The VIEW is the scroller.
+++++      // But getChatContainer is usually strictly for finding where to APPEND.
++++       const chatLog = document.getElementById("chat-log");
++++       
++++       if (!chatLog) {
++++-         // Fallback or error
++++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
+++++         // ... error ...
+++++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++++        // Visible UI Error (Phase A/B Requirement)
++++         const toastContainer = document.getElementById("toast-container");
++++         if (toastContainer) {
++++             const errDiv = document.createElement("div");
++++@@ -4378,7 +4402,7 @@
++++             errDiv.textContent = "Error: Chat container missing.";
++++             toastContainer.appendChild(errDiv);
++++         }
++++-        return document.getElementById("duet-history"); // Last resort
+++++        return null;
++++       }
++++       return chatLog;
++++     }
++++@@ -4518,14 +4542,11 @@
++++             const text = msg && msg.transcript ? String(msg.transcript) : "";
++++             if (!text.trim()) return;
++++             const role = msg && msg.source === "assistant" ? "bot" : "user";
++++-            // Pass special flag to force into history backlog
++++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++++            addMessage(role, text);
++++           });
++++           
++++-          // Force scroll logic for "hidden backlog"
++++-          syncDuetHistorySpacer();
++++-          scrollDuetHistoryToBottom();
++++-          // scrollChatToBottom(true); // Legacy call
+++++          // Force scroll to bottom after initial load
+++++          scrollChatToBottom(true);
++++         };
++++         if (renderedCount > 0) {
++++           renderMessages(messages);
++++@@ -4580,8 +4601,6 @@
++++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++      }
+++  
++++-    let globalMessageSequence = 0;
++++-
++++     function addMessage(role, text, options = {}) {
++++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
++++       // Hide chat placeholder when first message appears
++++@@ -4598,9 +4617,6 @@
++++ 
++++       const row = document.createElement("div");
++++       row.className = `msg-row ${role}`;
++++-      // Timestamp and Sequence for robust sorting
++++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
++++-      row.dataset.sequence = ++globalMessageSequence;
++++ 
++++       // Apply focus highlighting if a goal is focused
++++       if (othelloState.activeGoalId) {
++++@@ -4652,24 +4668,9 @@
++++ 
++++       row.appendChild(bubble);
++++       
++++-      // Phase 5: Routing for Duet vs Standard
++++-      const duetTop = document.getElementById("duet-top");
++++-      const duetBottom = document.getElementById("duet-bottom");
++++-      const historySpacer = document.getElementById("duet-history-spacer");
++++-
++++-      const isHistoryLoad = options && options.isHistoryLoad; 
++++-      
++++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
++++-      const duetHistory = document.getElementById("duet-history");
++++-      const isHistoryLoad = options && options.isHistoryLoad; 
++++-      
++++-      if (isHistoryLoad && duetHistory) {
++++-         // History always appends-to-end of the History Block (which is above Live)
++++-         duetHistory.appendChild(row);
++++-      } else {
++++-         // Live messages append strictly to the Live Container (#chat-log)
++++-         // This ensures standard Top-Down flow.
++++-         if (container) container.appendChild(row);
+++++      // Append to the resolved container
+++++      if (container) {
+++++         container.appendChild(row);
++++       }
++++       
++++       updateDuetView(row, role);
++++@@ -5920,6 +5921,48 @@
++++         }
++++     }
++++ 
+++++    function maybePromoteDuetToHistory() {
+++++      const live = document.getElementById("chat-log");
+++++      const hist = document.getElementById("duet-history");
+++++      const top = document.getElementById("duet-top");
+++++      const bottom = document.getElementById("duet-bottom");
+++++
+++++      // Gather all potential nodes (Live log + Pinned zones)
+++++      // Duet Logic: Bottom usually holds User (Previous Turn Start), Top holds Bot (Previous Turn Reply)
+++++      // Visual order was Top (Bot) ... Bottom (User) [Reverse visual?]
+++++      // Logical History Order: User -> Bot.
+++++      // So we grab Bottom nodes first, then Top nodes.
+++++      const nodes = [];
+++++      
+++++      // 1. User Message (Bottom Pin)
+++++      if (bottom && bottom.children.length > 0) nodes.push(...Array.from(bottom.children));
+++++      
+++++      // 2. Any Intermediates (Live Log - unlikely if purely pinned, but safe to include)
+++++      if (live && live.children.length > 0) nodes.push(...Array.from(live.children));
+++++
+++++      // 3. Bot Message (Top Pin)
+++++      if (top && top.children.length > 0) nodes.push(...Array.from(top.children));
+++++
+++++      if (nodes.length > 0 && hist) {
+++++        // Create wrapper for this duet turn
+++++        const block = document.createElement("div");
+++++        block.className = "history-duet";
+++++
+++++        for (const n of nodes) block.appendChild(n);
+++++        
+++++        hist.appendChild(block);
+++++        
+++++        // Clear all source containers
+++++        if (live) live.innerHTML = "";
+++++        if (top) { top.innerHTML = ""; top.style.display = "none"; }
+++++        if (bottom) { bottom.innerHTML = ""; bottom.style.display = "none"; }
+++++
+++++        console.debug("[duet] promoted", nodes.length, "nodes to history wrapper.");
+++++      } else {
+++++        console.debug("[duet] no promotion. nodes=", nodes.length, "hist=", !!hist);
+++++      }
+++++    }
+++++
++++     async function sendMessage(overrideText = null, extraData = {}) {
++++       // 1) Robust String Safety & Diagnostic
++++       let override = overrideText;
++++@@ -5933,8 +5976,8 @@
++++       }
++++ 
++++       // Canonical text variable (Refetch input safely)
++++-      const input = document.getElementById('user-input');
++++-      let rawText = (override !== null ? override : (input?.value ?? ""));
+++++      const currentInput = document.getElementById('user-input');
+++++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
++++       
++++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
++++       
++++@@ -5945,12 +5988,8 @@
++++ 
++++       if (!text && !extraData.ui_action) return;
++++ 
++++-      // Phase B (Cleanup): Auto-archive pins on new user message
++++-      // This ensures the stage is cleared before the new user bubble appears.
++++-      // We only do this if it's a genuine user message (text present or ui_action).
++++-      if (typeof archivePinnedToHistory === "function") {
++++-          archivePinnedToHistory();
++++-      }
+++++      // Phase 2: History Promotion (Move & Clear)
+++++      maybePromoteDuetToHistory();
++++ 
++++       // Voice-first save command (Strict Command Mode)
++++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
++ diff --git a/othello_ui.html b/othello_ui.html
++-index a78c1b7b..d6ca18ec 100644
+++index d6ca18ec..afbc36e8 100644
++ --- a/othello_ui.html
++ +++ b/othello_ui.html
++-@@ -339,6 +339,7 @@
+++@@ -339,10 +339,16 @@
++        <div id="chat-view" class="view" style="display:flex;">
++          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
++          
++-+        <!-- Only this is scrollable history -->
++-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++-         <div id="chat-log" class="chat-log"></div>
+++-        <!-- Only this is scrollable history -->
+++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++-        <div id="chat-log" class="chat-log"></div>
++++        <div id="duet-history" style="display:flex; flex-direction:column; padding:0;">
++++          <div class="duet-history-bar">History</div>
++++        </div>
++++        
++++        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
++++             <!-- Only this is scrollable history -->
++++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++++             <div id="chat-log" class="chat-log"></div>
++++        </div>
+++         
+++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+++       </div>
++ diff --git a/static/othello.css b/static/othello.css
++-index 825c710b..c7cc1ae5 100644
+++index 382eeb57..097944fc 100644
++ --- a/static/othello.css
++ +++ b/static/othello.css
++-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+++@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
+++   position: relative;
++  }
++  
++- /* --- Duet Chat Mode (Unified) --- */
++--/* Phase 2: Fix the scroll container */
++-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
++- .chat-sheet {
+++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
++++/* Chat View IS the scroll container now */
+++ #chat-view {
++    display: flex !important;
++-   flex-direction: column !important;
++-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
++- /* Header is rigid */
++- .chat-sheet__header {
++-   flex: 0 0 auto;
++-+  z-index: 200; /* Header stays absolutely on top */
++-+  position: relative;
++-+  box-shadow: 0 1px 0 var(--border);
+++   flex-direction: column;
+++-  flex: 1 1 0;
++++  flex: 1 1 0; /* Grow, shrink, basis 0 */
+++   min-height: 0;
+++-  overflow: hidden !important; /* View itself does NOT scroll */
++++  overflow-y: auto !important; /* The ONLY scrollbar */
++++  overflow-x: hidden;
+++   position: relative;
+++-  padding: 0;
++++  padding: 0; /* Strict */
++  }
++  
++- /* Input is rigid (footer) */
++- .input-bar {
++-   flex: 0 0 auto;
++-+  z-index: 200; /* Input stays absolutely on top */
++-+  position: relative;
++- }
++- 
++- /* Chat View IS the scroll container now */
++-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
++-   background: rgba(15, 23, 42, 0.98);
+++-/* Duet Panes (Static Flex Items) */
++++/* Duet Panes (Sticky) - Transparent Rails */
+++ .duet-pane {
+++-  position: static; /* No longer sticky */
+++-  flex: 0 0 auto; /* Rigid height based on content */
+++-  z-index: 100;
+++-  background: transparent;
++++  position: sticky;
++++  z-index: 100; /* Must beat messages */
++++  background: transparent; /* Transparent background */
++    padding: 0.75rem;
++    margin: 0;
++--  display: block !important;
+++-  display: block;
+++-  pointer-events: none;
++ +  display: block; /* always block, hidden by JS empty check if needed */
++-   backdrop-filter: blur(8px);
++--  /* Ensure they don't shrink away */
++-   flex-shrink: 0; 
++++  flex-shrink: 0;
++++  pointer-events: none; /* Let clicks pass through empty space */
++  }
++  
+++-.duet-pane > * { pointer-events: auto; }
+++-.duet-pane:empty { display: none !important; }
++++/* Re-enable pointer events on children (the bubbles) */
++++.duet-pane > * {
++++  pointer-events: auto;
++++}
+++ 
+++-/* Chat Log (Middle Scrollable History) */
+++-#chat-log {
+++-  display: flex !important;
+++-  flex-direction: column;
+++-  flex: 1 1 0; /* Takes all remaining space */
+++-  overflow-y: auto !important; /* HISTORY scrolls here */
+++-  min-height: 0;
+++-  height: auto !important;
+++-  padding: 1rem;
+++-  padding-top: 0.5rem;
+++-  padding-bottom: 0.5rem;
++ +/* Default hidden until populated */
++ +.duet-pane:empty {
++ +    display: none !important;
++-+}
++-+
+++ }
+++ 
+++-/* Remove sticky-specific top/bottom since they are just flex order now */
++  .duet-pane--top {
++-   top: 0;
++-   border-bottom: 1px solid rgba(255,255,255,0.1);
++-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
++-   overflow: visible !important; /* Let parent scroll it */
++-   height: auto !important;
++-   padding: 1rem;
+++-  order: 1;
+++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++  top: 0;
++++  /* Removed border/shadow for clean look */
++++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
++++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+++ }
+++ 
+++-#chat-log {
+++-  order: 2; /* Middle */
++++.duet-pane--bottom {
++++  bottom: 0;
++++  /* Removed border/shadow for clean look */
++++  /* border-top: 1px solid rgba(255,255,255,0.1); */
++++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+++ }
+++ 
+++-.duet-pane--bottom {
+++-  order: 3;
+++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++++/* Chat Log (History Flow) */
++++#chat-log {
++++  display: flex !important;
++++  flex-direction: column;
++++  flex: 1; /* occupy space between pins */
++++  overflow: visible !important; /* Let parent scroll it */
++++  height: auto !important;
++++  padding: 1rem;
++ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
++ +  padding-top: 1rem;
++ +  padding-bottom: 1rem;
++  }
++  
+++-/* Ensure empty slots don't take space/border */
+++-.duet-pane:empty {
+++-    display: none !important;
+++-    border: none !important;
++++#chat-sheet {
++++  display: flex;
++++  flex-direction: column;
++++  width: 100%;
+++ }
+++ 
++  /* Hide empty panes */
+++@@ -2271,3 +2278,54 @@ body.chat-open #global-chat-fab {
+++ /* Cleanup old classes */
+++ .duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
+++ 
++++/* --- Duet Phase 2 History Fixes --- */
++++#duet-history {
++++  display: flex !important;
++++  flex-direction: column !important;
++++  padding: 0 !important; /* Managed by children */
++++  width: 100%;
++++}
++++
++++/* History Bar Lock */
++++.duet-history-bar {
++++  position: sticky;
++++  top: 0;
++++  z-index: 2; /* Layer above scrolling text if needed, though they are siblings */
++++  background: var(--bg-2); /* Match background */
++++  padding: 8px 0;
++++  border-bottom: 1px solid var(--border);
++++  color: var(--text-soft);
++++  font-size: 0.8rem;
++++  text-transform: uppercase;
++++  letter-spacing: 0.05em;
++++  text-align: center;
++++  width: 100%;
++++  margin-bottom: 0;
++++  /* Box shadow for depth when sticky? Optional. */
++++}
++++
++++.history-duet {
++++  display: flex !important;
++++  flex-direction: column !important;
++++  margin-bottom: 24px;
++++  border-bottom: 1px solid var(--border);
++++  padding: 12px 1rem 24px 1rem; /* Add padding here instead of parent */
++++}
++++
++++.history-duet:last-child {
++++  border-bottom: none;
++++  margin-bottom: 0;
++++}
++++
++++/* Reserve space: REMOVE fixed padding that creates dead gap. Layout handles height. */
++++#chat-view {
++++  padding-bottom: 0px !important;
++++}
++++
++++/* Visual separation for the Live area (Gap between History and Live) */
++++#chat-sheet {
++++  margin-top: 12px;
++++  padding-top: 12px;
++++  overflow: visible !important; /* Ensure internal content doesn't scroll */
++++}
++++
++ diff --git a/static/othello.js b/static/othello.js
++-index 3a092bfc..1a19d8a7 100644
+++index 69c723cf..a5c2fe03 100644
++ --- a/static/othello.js
++ +++ b/static/othello.js
++-@@ -4300,76 +4300,81 @@
+++@@ -793,8 +793,7 @@
+++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++ 
+++-    // Updated to support new Duet History container
+++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
++++    const chatLog = document.getElementById('chat-log');
+++     // Relocated status to chat header (Phase 6 Fix)
+++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++     const modeLabel = document.getElementById('current-mode-label');
+++@@ -3656,6 +3655,9 @@
+++               bindComposerActionButton("overlay_open");
+++               requestAnimationFrame(() => bindComposerActionButton("overlay_open_raf"));
+++           }
++++          // Fix: Ensure history starts off-screen by scrolling to bottom immediately
++++          // Force scroll to bottom when opening
++++          scrollChatToBottom(true);
+++       }
+++ 
+++       if (!isOpen) {
+++@@ -4301,61 +4303,83 @@
++        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
++      }
++  
++--    // Phase 3: Move nodes (no duplication)
++-+    // Phase 3: Canonical Move
++-     function applyDuetPins() {
++--        if (!isDuetEnabled()) return;
+++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+++-    function syncDuetHistorySpacer() {
+++-       // Deprecated in Single Scroll model
+++-    }
+++-
+++-    function scrollDuetHistoryToBottom() {
+++-       // Deprecated - use scrollChatToBottom
+++-    }
+++-
+++-    // Call on resize - harmless
+++-    window.addEventListener("resize", () => {});
+++-
+++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
+++-    function archivePinnedToHistory() {
+++-        // Source: Live Chat (#chat-log)
+++-        // Dest: History (#duet-history)
+++-        const liveContainer = document.getElementById("chat-log");
+++-        const historyContainer = document.getElementById("duet-history");
+++-        const viewport = document.getElementById("chat-view");
+++-
+++-        if (!liveContainer || !historyContainer || !viewport) return;
+++-
+++-        // 1. Capture Scroll State
+++-        const prevScrollHeight = viewport.scrollHeight;
+++-        const prevScrollTop = viewport.scrollTop;
+++-
+++-        // 2. Archive only valid message rows
+++-        // We verify direct children to avoid deep grabbing
+++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
++ -        
++--        const chatLog = document.getElementById("chat-log");
++-         const top = document.getElementById("duet-top");
++-         const bottom = document.getElementById("duet-bottom");
++--        if (!chatLog) return;
++--        
++--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
++--        // Actually, simpler approach for V1:
++--        // We only pin the LATEST. 
++--        // Iterate chatLog children. Find last user msg, last bot msg.
++--        // Move them to pins? No, that breaks history flow if they are old.
++--        // Rule: Only pin if it is indeed slaved to the bottom/top.
++--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
++--        // This implies visual displacement.
++--        
++--        // Better Strategy:
++--        // 1. Clear pins.
++--        // 2. Scan chatLog rows.
++--        // 3. Last row -> if user, move to bottom.
++--        // 4. Last ASSISTANT row -> move to top.
++--        // Wait, if last row is user, and row before is assistant, we move BOTH.
++--        // This effectively empties the bottom of the history.
++--        
++--        // Implementation:
++--        // Find all .msg-row in chat main loop or chatLog
++--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
++ -        if (rows.length === 0) return;
+++-
+++-        const fragment = document.createDocumentFragment();
+++-        // Since we iterate in DOM order, we preserve chronological order
+++-        rows.forEach(r => fragment.appendChild(r));
++ -        
++--        // Find last user row
+++-        historyContainer.appendChild(fragment);
++++    // Phase 3: Canonical Move
++++    function applyDuetPins() {
++++        const top = document.getElementById("duet-top");
++++        const bottom = document.getElementById("duet-bottom");
++ +        const chatLog = document.getElementById("chat-log");
++ +
++ +        // Fallback for safety
++@@ -146,45 +15866,39 @@ index 3a092bfc..1a19d8a7 100644
++ +        if (allRows.length === 0) return;
++ +
++ +        // 2. Scan for candidates
++-         let lastUserRow = null;
++-         let lastBotRow = null;
++--        
++++        let lastUserRow = null;
++++        let lastBotRow = null;
++ +
++-         // Scan backwards
++--        for (let i = rows.length - 1; i >= 0; i--) {
++--            const r = rows[i];
++++        // Scan backwards
++ +        for (let i = allRows.length - 1; i >= 0; i--) {
++ +            const r = allRows[i];
++-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
++++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
++ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
++-             if (lastUserRow && lastBotRow) break;
++-         }
++- 
++--        // Move to pins
++++            if (lastUserRow && lastBotRow) break;
++++        }
++++
++ +        // 3. Move to pins
++-         if (lastBotRow) {
++--            top.appendChild(lastBotRow); // Moves it out of chatLog
++--            // Ensure display is correct
++++        if (lastBotRow) {
++ +            top.appendChild(lastBotRow);
++-             top.style.display = 'block';
++-         } else {
++--            top.innerHTML = "";
++-             top.style.display = 'none';
++-         }
++++            top.style.display = 'block';
++++        } else {
++++            top.style.display = 'none';
++++        }
+++ 
+++-        // 3. Maintain Scroll Position
+++-        const newScrollHeight = viewport.scrollHeight;
+++-        const delta = newScrollHeight - prevScrollHeight;
++ -        
++-+
++-         if (lastUserRow) {
++--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
+++-        if (delta > 0) {
+++-            viewport.scrollTop = prevScrollTop + delta;
++++        if (lastUserRow) {
++ +            bottom.appendChild(lastUserRow);
++-             bottom.style.display = 'block';
++-         } else {
++--            bottom.innerHTML = "";
++-             bottom.style.display = 'none';
++++            bottom.style.display = 'block';
++++        } else {
++++            bottom.style.display = 'none';
++          }
++          
++--        // If we moved stuff, scroll might need adjustment? 
++--        // Sticky logic handles the pins. History fills the middle.
+++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
++ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
++ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
++ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
++@@ -198,13 +15912,185 @@ index 3a092bfc..1a19d8a7 100644
++ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
++ +        }
++      }
+++-
+++-    // Deprecated / Aliased
+++-    function applyDuetPins() {}
++      
++--    // No-op for old sync padding (CSS sticky handles it now)
++      function syncDuetPadding() {}
++  
++-     function updateDuetView(row, role) {
++--      // Defer to applyDuetPins in next frame to let DOM settle
+++-    function updateDuetView(row, role) {}
++++    function updateDuetView(row, role) {
++ +      // Defer to applyDuetPins in next frame so DOM is ready
++-       requestAnimationFrame(applyDuetPins);
++++      requestAnimationFrame(applyDuetPins);
++++    }
+++ 
+++     function bindDuetListeners() {
+++        // Scroll logic is now native overflow
+++@@ -4365,12 +4389,15 @@
+++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
+++ 
+++     function getChatContainer() {
+++-      // Phase 4: Target the LIVE container (chat-log)
++++      // Phase 4: Target the real scroll container for appending?
++++      // No, we append to chat-log. The VIEW is the scroller.
++++      // But getChatContainer is usually strictly for finding where to APPEND.
+++       const chatLog = document.getElementById("chat-log");
+++       
+++       if (!chatLog) {
+++-         // Fallback or error
+++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
++++         // ... error ...
++++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
++++        // Visible UI Error (Phase A/B Requirement)
+++         const toastContainer = document.getElementById("toast-container");
+++         if (toastContainer) {
+++             const errDiv = document.createElement("div");
+++@@ -4378,7 +4405,7 @@
+++             errDiv.textContent = "Error: Chat container missing.";
+++             toastContainer.appendChild(errDiv);
+++         }
+++-        return document.getElementById("duet-history"); // Last resort
++++        return null;
+++       }
+++       return chatLog;
++      }
+++@@ -4518,14 +4545,11 @@
+++             const text = msg && msg.transcript ? String(msg.transcript) : "";
+++             if (!text.trim()) return;
+++             const role = msg && msg.source === "assistant" ? "bot" : "user";
+++-            // Pass special flag to force into history backlog
+++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
++++            addMessage(role, text);
+++           });
+++           
+++-          // Force scroll logic for "hidden backlog"
+++-          syncDuetHistorySpacer();
+++-          scrollDuetHistoryToBottom();
+++-          // scrollChatToBottom(true); // Legacy call
++++          // Force scroll to bottom after initial load
++++          scrollChatToBottom(true);
+++         };
+++         if (renderedCount > 0) {
+++           renderMessages(messages);
+++@@ -4580,8 +4604,6 @@
+++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+++     }
+++ 
+++-    let globalMessageSequence = 0;
+++-
+++     function addMessage(role, text, options = {}) {
+++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+++       // Hide chat placeholder when first message appears
+++@@ -4598,9 +4620,6 @@
+++ 
+++       const row = document.createElement("div");
+++       row.className = `msg-row ${role}`;
+++-      // Timestamp and Sequence for robust sorting
+++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+++-      row.dataset.sequence = ++globalMessageSequence;
+++ 
+++       // Apply focus highlighting if a goal is focused
+++       if (othelloState.activeGoalId) {
+++@@ -4652,24 +4671,9 @@
+++ 
+++       row.appendChild(bubble);
+++       
+++-      // Phase 5: Routing for Duet vs Standard
+++-      const duetTop = document.getElementById("duet-top");
+++-      const duetBottom = document.getElementById("duet-bottom");
+++-      const historySpacer = document.getElementById("duet-history-spacer");
+++-
+++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++-      
+++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
+++-      const duetHistory = document.getElementById("duet-history");
+++-      const isHistoryLoad = options && options.isHistoryLoad; 
+++-      
+++-      if (isHistoryLoad && duetHistory) {
+++-         // History always appends-to-end of the History Block (which is above Live)
+++-         duetHistory.appendChild(row);
+++-      } else {
+++-         // Live messages append strictly to the Live Container (#chat-log)
+++-         // This ensures standard Top-Down flow.
+++-         if (container) container.appendChild(row);
++++      // Append to the resolved container
++++      if (container) {
++++         container.appendChild(row);
+++       }
+++       
+++       updateDuetView(row, role);
+++@@ -5920,6 +5924,48 @@
+++         }
+++     }
+++ 
++++    function maybePromoteDuetToHistory() {
++++      const live = document.getElementById("chat-log");
++++      const hist = document.getElementById("duet-history");
++++      const top = document.getElementById("duet-top");
++++      const bottom = document.getElementById("duet-bottom");
++++
++++      // Gather all potential nodes (Live log + Pinned zones)
++++      // Duet Logic: Bottom usually holds User (Previous Turn Start), Top holds Bot (Previous Turn Reply)
++++      // Visual order was Top (Bot) ... Bottom (User) [Reverse visual?]
++++      // Logical History Order: User -> Bot.
++++      // So we grab Bottom nodes first, then Top nodes.
++++      const nodes = [];
++++      
++++      // 1. User Message (Bottom Pin)
++++      if (bottom && bottom.children.length > 0) nodes.push(...Array.from(bottom.children));
++++      
++++      // 2. Any Intermediates (Live Log - unlikely if purely pinned, but safe to include)
++++      if (live && live.children.length > 0) nodes.push(...Array.from(live.children));
++++
++++      // 3. Bot Message (Top Pin)
++++      if (top && top.children.length > 0) nodes.push(...Array.from(top.children));
++++
++++      if (nodes.length > 0 && hist) {
++++        // Create wrapper for this duet turn
++++        const block = document.createElement("div");
++++        block.className = "history-duet";
++++
++++        for (const n of nodes) block.appendChild(n);
++++        
++++        hist.appendChild(block);
++++        
++++        // Clear all source containers
++++        if (live) live.innerHTML = "";
++++        if (top) { top.innerHTML = ""; top.style.display = "none"; }
++++        if (bottom) { bottom.innerHTML = ""; bottom.style.display = "none"; }
++++
++++        console.debug("[duet] promoted", nodes.length, "nodes to history wrapper.");
++++      } else {
++++        console.debug("[duet] no promotion. nodes=", nodes.length, "hist=", !!hist);
++++      }
++++    }
++++
+++     async function sendMessage(overrideText = null, extraData = {}) {
+++       // 1) Robust String Safety & Diagnostic
+++       let override = overrideText;
+++@@ -5933,8 +5979,8 @@
+++       }
+++ 
+++       // Canonical text variable (Refetch input safely)
+++-      const input = document.getElementById('user-input');
+++-      let rawText = (override !== null ? override : (input?.value ?? ""));
++++      const currentInput = document.getElementById('user-input');
++++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
+++       
+++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
+++       
+++@@ -5945,12 +5991,8 @@
+++ 
+++       if (!text && !extraData.ui_action) return;
+++ 
+++-      // Phase B (Cleanup): Auto-archive pins on new user message
+++-      // This ensures the stage is cleared before the new user bubble appears.
+++-      // We only do this if it's a genuine user message (text present or ui_action).
+++-      if (typeof archivePinnedToHistory === "function") {
+++-          archivePinnedToHistory();
+++-      }
++++      // Phase 2: History Promotion (Move & Clear)
++++      maybePromoteDuetToHistory();
++  
+++       // Voice-first save command (Strict Command Mode)
+++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
+ diff --git a/othello_ui.html b/othello_ui.html
+-index a78c1b7b..d6ca18ec 100644
++index d6ca18ec..f0a5ad4e 100644
+ --- a/othello_ui.html
+ +++ b/othello_ui.html
+-@@ -339,6 +339,7 @@
++@@ -339,10 +339,15 @@
+        <div id="chat-view" class="view" style="display:flex;">
+          <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+          
+-+        <!-- Only this is scrollable history -->
+-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+-         <div id="chat-log" class="chat-log"></div>
++-        <!-- Only this is scrollable history -->
++-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++-        <div id="chat-log" class="chat-log"></div>
+++        <div id="duet-history" style="display:flex; flex-direction:column; padding:0;"></div>
+++        <div class="duet-history-bar">HISTORY</div>
+++        
+++        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
+++             <!-- Only this is scrollable history -->
+++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+++             <div id="chat-log" class="chat-log"></div>
+++        </div>
++         
++         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
++       </div>
+ diff --git a/static/othello.css b/static/othello.css
+-index 825c710b..c7cc1ae5 100644
++index 382eeb57..b0341e0e 100644
+ --- a/static/othello.css
+ +++ b/static/othello.css
+-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
++@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
++   position: relative;
+  }
+  
+- /* --- Duet Chat Mode (Unified) --- */
+--/* Phase 2: Fix the scroll container */
+-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
+- .chat-sheet {
++-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
+++/* Chat View IS the scroll container now */
++ #chat-view {
+    display: flex !important;
+-   flex-direction: column !important;
+-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
+- /* Header is rigid */
+- .chat-sheet__header {
+-   flex: 0 0 auto;
+-+  z-index: 200; /* Header stays absolutely on top */
+-+  position: relative;
+-+  box-shadow: 0 1px 0 var(--border);
++   flex-direction: column;
++-  flex: 1 1 0;
+++  flex: 1 1 0; /* Grow, shrink, basis 0 */
++   min-height: 0;
++-  overflow: hidden !important; /* View itself does NOT scroll */
+++  overflow-y: auto !important; /* The ONLY scrollbar */
+++  overflow-x: hidden;
++   position: relative;
++-  padding: 0;
+++  padding: 0; /* Strict */
+  }
+  
+- /* Input is rigid (footer) */
+- .input-bar {
+-   flex: 0 0 auto;
+-+  z-index: 200; /* Input stays absolutely on top */
+-+  position: relative;
+- }
+- 
+- /* Chat View IS the scroll container now */
+-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
+-   background: rgba(15, 23, 42, 0.98);
++-/* Duet Panes (Static Flex Items) */
+++/* Duet Panes (Sticky) - Transparent Rails */
++ .duet-pane {
++-  position: static; /* No longer sticky */
++-  flex: 0 0 auto; /* Rigid height based on content */
++-  z-index: 100;
++-  background: transparent;
+++  position: sticky;
+++  z-index: 100; /* Must beat messages */
+++  background: transparent; /* Transparent background */
+    padding: 0.75rem;
+    margin: 0;
+--  display: block !important;
++-  display: block;
++-  pointer-events: none;
+ +  display: block; /* always block, hidden by JS empty check if needed */
+-   backdrop-filter: blur(8px);
+--  /* Ensure they don't shrink away */
+-   flex-shrink: 0; 
+++  flex-shrink: 0;
+++  pointer-events: none; /* Let clicks pass through empty space */
+  }
+  
++-.duet-pane > * { pointer-events: auto; }
++-.duet-pane:empty { display: none !important; }
+++/* Re-enable pointer events on children (the bubbles) */
+++.duet-pane > * {
+++  pointer-events: auto;
+++}
++ 
++-/* Chat Log (Middle Scrollable History) */
++-#chat-log {
++-  display: flex !important;
++-  flex-direction: column;
++-  flex: 1 1 0; /* Takes all remaining space */
++-  overflow-y: auto !important; /* HISTORY scrolls here */
++-  min-height: 0;
++-  height: auto !important;
++-  padding: 1rem;
++-  padding-top: 0.5rem;
++-  padding-bottom: 0.5rem;
+ +/* Default hidden until populated */
+ +.duet-pane:empty {
+ +    display: none !important;
+-+}
+-+
++ }
++ 
++-/* Remove sticky-specific top/bottom since they are just flex order now */
+  .duet-pane--top {
+-   top: 0;
+-   border-bottom: 1px solid rgba(255,255,255,0.1);
+-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
+-   overflow: visible !important; /* Let parent scroll it */
+-   height: auto !important;
+-   padding: 1rem;
++-  order: 1;
++-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++  top: 0;
+++  /* Removed border/shadow for clean look */
+++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
+++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
++ }
++ 
++-#chat-log {
++-  order: 2; /* Middle */
+++.duet-pane--bottom {
+++  bottom: 0;
+++  /* Removed border/shadow for clean look */
+++  /* border-top: 1px solid rgba(255,255,255,0.1); */
+++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
++ }
++ 
++-.duet-pane--bottom {
++-  order: 3;
++-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
+++/* Chat Log (History Flow) */
+++#chat-log {
+++  display: flex !important;
+++  flex-direction: column;
+++  flex: 1; /* occupy space between pins */
+++  overflow: visible !important; /* Let parent scroll it */
+++  height: auto !important;
+++  padding: 1rem;
+ +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
+ +  padding-top: 1rem;
+ +  padding-bottom: 1rem;
+  }
+  
++-/* Ensure empty slots don't take space/border */
++-.duet-pane:empty {
++-    display: none !important;
++-    border: none !important;
+++#chat-sheet {
+++  display: flex;
+++  flex-direction: column;
+++  width: 100%;
++ }
++ 
+  /* Hide empty panes */
++@@ -2271,3 +2278,56 @@ body.chat-open #global-chat-fab {
++ /* Cleanup old classes */
++ .duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
++ 
+++/* --- Duet Phase 2 History Fixes --- */
+++#duet-history {
+++  display: flex !important;
+++  flex-direction: column !important;
+++  padding: 0 !important; /* Managed by children */
+++  width: 100%;
+++}
+++
+++/* History Bar Lock */
+++.duet-history-bar {
+++  position: sticky;
+++  bottom: 0;
+++  z-index: 2; 
+++  background: var(--bg-2);
+++  padding: 8px 0;
+++  border-bottom: 1px solid var(--border);
+++  color: var(--text-soft);
+++  font-size: 0.8rem;
+++  font-weight: bold;
+++  text-transform: uppercase;
+++  letter-spacing: 0.05em;
+++  text-align: center;
+++  width: 100%;
+++  margin-bottom: 0;
+++  /* Visual separation */
+++  border-top: 1px solid var(--border);
+++}
+++
+++.history-duet {
+++  display: flex !important;
+++  flex-direction: column !important;
+++  margin-bottom: 24px;
+++  border-bottom: 1px solid var(--border);
+++  padding: 12px 1rem 24px 1rem; /* Add padding here instead of parent */
+++}
+++
+++.history-duet:last-child {
+++  border-bottom: none;
+++  margin-bottom: 0;
+++}
+++
+++/* Reserve space: REMOVE fixed padding that creates dead gap. Layout handles height. */
+++#chat-view {
+++  padding-bottom: 0px !important;
+++}
+++
+++/* Visual separation for the Live area (Gap between History and Live) */
+++#chat-sheet {
+++  margin-top: 12px;
+++  padding-top: 12px;
+++  overflow: visible !important; /* Ensure internal content doesn't scroll */
+++}
+++
+ diff --git a/static/othello.js b/static/othello.js
+-index 3a092bfc..1a19d8a7 100644
++index 69c723cf..a5c2fe03 100644
+ --- a/static/othello.js
+ +++ b/static/othello.js
+-@@ -4300,76 +4300,81 @@
++@@ -793,8 +793,7 @@
++     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
++ 
++-    // Updated to support new Duet History container
++-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
+++    const chatLog = document.getElementById('chat-log');
++     // Relocated status to chat header (Phase 6 Fix)
++     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
++     const modeLabel = document.getElementById('current-mode-label');
++@@ -3656,6 +3655,9 @@
++               bindComposerActionButton("overlay_open");
++               requestAnimationFrame(() => bindComposerActionButton("overlay_open_raf"));
++           }
+++          // Fix: Ensure history starts off-screen by scrolling to bottom immediately
+++          // Force scroll to bottom when opening
+++          scrollChatToBottom(true);
++       }
++ 
++       if (!isOpen) {
++@@ -4301,61 +4303,83 @@
+        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
+      }
+  
+--    // Phase 3: Move nodes (no duplication)
+-+    // Phase 3: Canonical Move
+-     function applyDuetPins() {
+--        if (!isDuetEnabled()) return;
++-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
++-    function syncDuetHistorySpacer() {
++-       // Deprecated in Single Scroll model
++-    }
++-
++-    function scrollDuetHistoryToBottom() {
++-       // Deprecated - use scrollChatToBottom
++-    }
++-
++-    // Call on resize - harmless
++-    window.addEventListener("resize", () => {});
++-
++-    // Updated applyDuetPins to act as "archivePinnedToHistory"
++-    function archivePinnedToHistory() {
++-        // Source: Live Chat (#chat-log)
++-        // Dest: History (#duet-history)
++-        const liveContainer = document.getElementById("chat-log");
++-        const historyContainer = document.getElementById("duet-history");
++-        const viewport = document.getElementById("chat-view");
++-
++-        if (!liveContainer || !historyContainer || !viewport) return;
++-
++-        // 1. Capture Scroll State
++-        const prevScrollHeight = viewport.scrollHeight;
++-        const prevScrollTop = viewport.scrollTop;
++-
++-        // 2. Archive only valid message rows
++-        // We verify direct children to avoid deep grabbing
++-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
+ -        
+--        const chatLog = document.getElementById("chat-log");
+-         const top = document.getElementById("duet-top");
+-         const bottom = document.getElementById("duet-bottom");
+--        if (!chatLog) return;
+--        
+--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
+--        // Actually, simpler approach for V1:
+--        // We only pin the LATEST. 
+--        // Iterate chatLog children. Find last user msg, last bot msg.
+--        // Move them to pins? No, that breaks history flow if they are old.
+--        // Rule: Only pin if it is indeed slaved to the bottom/top.
+--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
+--        // This implies visual displacement.
+--        
+--        // Better Strategy:
+--        // 1. Clear pins.
+--        // 2. Scan chatLog rows.
+--        // 3. Last row -> if user, move to bottom.
+--        // 4. Last ASSISTANT row -> move to top.
+--        // Wait, if last row is user, and row before is assistant, we move BOTH.
+--        // This effectively empties the bottom of the history.
+--        
+--        // Implementation:
+--        // Find all .msg-row in chat main loop or chatLog
+--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
+ -        if (rows.length === 0) return;
++-
++-        const fragment = document.createDocumentFragment();
++-        // Since we iterate in DOM order, we preserve chronological order
++-        rows.forEach(r => fragment.appendChild(r));
+ -        
+--        // Find last user row
++-        historyContainer.appendChild(fragment);
+++    // Phase 3: Canonical Move
+++    function applyDuetPins() {
+++        const top = document.getElementById("duet-top");
+++        const bottom = document.getElementById("duet-bottom");
+ +        const chatLog = document.getElementById("chat-log");
+ +
+ +        // Fallback for safety
+@@ -146,45 +16486,39 @@ index 3a092bfc..1a19d8a7 100644
+ +        if (allRows.length === 0) return;
+ +
+ +        // 2. Scan for candidates
+-         let lastUserRow = null;
+-         let lastBotRow = null;
+--        
+++        let lastUserRow = null;
+++        let lastBotRow = null;
+ +
+-         // Scan backwards
+--        for (let i = rows.length - 1; i >= 0; i--) {
+--            const r = rows[i];
+++        // Scan backwards
+ +        for (let i = allRows.length - 1; i >= 0; i--) {
+ +            const r = allRows[i];
+-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
+++            if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
+ +            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
+-             if (lastUserRow && lastBotRow) break;
+-         }
+- 
+--        // Move to pins
+++            if (lastUserRow && lastBotRow) break;
+++        }
+++
+ +        // 3. Move to pins
+-         if (lastBotRow) {
+--            top.appendChild(lastBotRow); // Moves it out of chatLog
+--            // Ensure display is correct
+++        if (lastBotRow) {
+ +            top.appendChild(lastBotRow);
+-             top.style.display = 'block';
+-         } else {
+--            top.innerHTML = "";
+-             top.style.display = 'none';
+-         }
+++            top.style.display = 'block';
+++        } else {
+++            top.style.display = 'none';
+++        }
++ 
++-        // 3. Maintain Scroll Position
++-        const newScrollHeight = viewport.scrollHeight;
++-        const delta = newScrollHeight - prevScrollHeight;
+ -        
+-+
+-         if (lastUserRow) {
+--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
++-        if (delta > 0) {
++-            viewport.scrollTop = prevScrollTop + delta;
+++        if (lastUserRow) {
+ +            bottom.appendChild(lastUserRow);
+-             bottom.style.display = 'block';
+-         } else {
+--            bottom.innerHTML = "";
+-             bottom.style.display = 'none';
+++            bottom.style.display = 'block';
+++        } else {
+++            bottom.style.display = 'none';
+          }
+          
+--        // If we moved stuff, scroll might need adjustment? 
+--        // Sticky logic handles the pins. History fills the middle.
++-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
+ +        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
+ +        // With position:sticky, we don't need manual padding IF the scroll container is correct.
+ +        // But we might want to ensure last history item isn't hidden behind bottom pin.
+@@ -198,13 +16532,185 @@ index 3a092bfc..1a19d8a7 100644
+ +             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
+ +        }
+      }
++-
++-    // Deprecated / Aliased
++-    function applyDuetPins() {}
+      
+--    // No-op for old sync padding (CSS sticky handles it now)
+      function syncDuetPadding() {}
+  
+-     function updateDuetView(row, role) {
+--      // Defer to applyDuetPins in next frame to let DOM settle
++-    function updateDuetView(row, role) {}
+++    function updateDuetView(row, role) {
+ +      // Defer to applyDuetPins in next frame so DOM is ready
+-       requestAnimationFrame(applyDuetPins);
+++      requestAnimationFrame(applyDuetPins);
+++    }
++ 
++     function bindDuetListeners() {
++        // Scroll logic is now native overflow
++@@ -4365,12 +4389,15 @@
++     document.addEventListener("DOMContentLoaded", bindDuetListeners);
++ 
++     function getChatContainer() {
++-      // Phase 4: Target the LIVE container (chat-log)
+++      // Phase 4: Target the real scroll container for appending?
+++      // No, we append to chat-log. The VIEW is the scroller.
+++      // But getChatContainer is usually strictly for finding where to APPEND.
++       const chatLog = document.getElementById("chat-log");
++       
++       if (!chatLog) {
++-         // Fallback or error
++-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
+++         // ... error ...
+++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
+++        // Visible UI Error (Phase A/B Requirement)
++         const toastContainer = document.getElementById("toast-container");
++         if (toastContainer) {
++             const errDiv = document.createElement("div");
++@@ -4378,7 +4405,7 @@
++             errDiv.textContent = "Error: Chat container missing.";
++             toastContainer.appendChild(errDiv);
++         }
++-        return document.getElementById("duet-history"); // Last resort
+++        return null;
++       }
++       return chatLog;
+      }
++@@ -4518,14 +4545,11 @@
++             const text = msg && msg.transcript ? String(msg.transcript) : "";
++             if (!text.trim()) return;
++             const role = msg && msg.source === "assistant" ? "bot" : "user";
++-            // Pass special flag to force into history backlog
++-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
+++            addMessage(role, text);
++           });
++           
++-          // Force scroll logic for "hidden backlog"
++-          syncDuetHistorySpacer();
++-          scrollDuetHistoryToBottom();
++-          // scrollChatToBottom(true); // Legacy call
+++          // Force scroll to bottom after initial load
+++          scrollChatToBottom(true);
++         };
++         if (renderedCount > 0) {
++           renderMessages(messages);
++@@ -4580,8 +4604,6 @@
++       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
++     }
++ 
++-    let globalMessageSequence = 0;
++-
++     function addMessage(role, text, options = {}) {
++       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
++       // Hide chat placeholder when first message appears
++@@ -4598,9 +4620,6 @@
++ 
++       const row = document.createElement("div");
++       row.className = `msg-row ${role}`;
++-      // Timestamp and Sequence for robust sorting
++-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
++-      row.dataset.sequence = ++globalMessageSequence;
++ 
++       // Apply focus highlighting if a goal is focused
++       if (othelloState.activeGoalId) {
++@@ -4652,24 +4671,9 @@
++ 
++       row.appendChild(bubble);
++       
++-      // Phase 5: Routing for Duet vs Standard
++-      const duetTop = document.getElementById("duet-top");
++-      const duetBottom = document.getElementById("duet-bottom");
++-      const historySpacer = document.getElementById("duet-history-spacer");
++-
++-      const isHistoryLoad = options && options.isHistoryLoad; 
++-      
++-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
++-      const duetHistory = document.getElementById("duet-history");
++-      const isHistoryLoad = options && options.isHistoryLoad; 
++-      
++-      if (isHistoryLoad && duetHistory) {
++-         // History always appends-to-end of the History Block (which is above Live)
++-         duetHistory.appendChild(row);
++-      } else {
++-         // Live messages append strictly to the Live Container (#chat-log)
++-         // This ensures standard Top-Down flow.
++-         if (container) container.appendChild(row);
+++      // Append to the resolved container
+++      if (container) {
+++         container.appendChild(row);
++       }
++       
++       updateDuetView(row, role);
++@@ -5920,6 +5924,48 @@
++         }
++     }
++ 
+++    function maybePromoteDuetToHistory() {
+++      const live = document.getElementById("chat-log");
+++      const hist = document.getElementById("duet-history");
+++      const top = document.getElementById("duet-top");
+++      const bottom = document.getElementById("duet-bottom");
+++
+++      // Gather all potential nodes (Live log + Pinned zones)
+++      // Duet Logic: Bottom usually holds User (Previous Turn Start), Top holds Bot (Previous Turn Reply)
+++      // Visual order was Top (Bot) ... Bottom (User) [Reverse visual?]
+++      // Logical History Order: User -> Bot.
+++      // So we grab Bottom nodes first, then Top nodes.
+++      const nodes = [];
+++      
+++      // 1. User Message (Bottom Pin)
+++      if (bottom && bottom.children.length > 0) nodes.push(...Array.from(bottom.children));
+++      
+++      // 2. Any Intermediates (Live Log - unlikely if purely pinned, but safe to include)
+++      if (live && live.children.length > 0) nodes.push(...Array.from(live.children));
+++
+++      // 3. Bot Message (Top Pin)
+++      if (top && top.children.length > 0) nodes.push(...Array.from(top.children));
+++
+++      if (nodes.length > 0 && hist) {
+++        // Create wrapper for this duet turn
+++        const block = document.createElement("div");
+++        block.className = "history-duet";
+++
+++        for (const n of nodes) block.appendChild(n);
+++        
+++        hist.appendChild(block);
+++        
+++        // Clear all source containers
+++        if (live) live.innerHTML = "";
+++        if (top) { top.innerHTML = ""; top.style.display = "none"; }
+++        if (bottom) { bottom.innerHTML = ""; bottom.style.display = "none"; }
+++
+++        console.debug("[duet] promoted", nodes.length, "nodes to history wrapper.");
+++      } else {
+++        console.debug("[duet] no promotion. nodes=", nodes.length, "hist=", !!hist);
+++      }
+++    }
+++
++     async function sendMessage(overrideText = null, extraData = {}) {
++       // 1) Robust String Safety & Diagnostic
++       let override = overrideText;
++@@ -5933,8 +5979,8 @@
++       }
++ 
++       // Canonical text variable (Refetch input safely)
++-      const input = document.getElementById('user-input');
++-      let rawText = (override !== null ? override : (input?.value ?? ""));
+++      const currentInput = document.getElementById('user-input');
+++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
++       
++       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
++       
++@@ -5945,12 +5991,8 @@
++ 
++       if (!text && !extraData.ui_action) return;
++ 
++-      // Phase B (Cleanup): Auto-archive pins on new user message
++-      // This ensures the stage is cleared before the new user bubble appears.
++-      // We only do this if it's a genuine user message (text present or ui_action).
++-      if (typeof archivePinnedToHistory === "function") {
++-          archivePinnedToHistory();
++-      }
+++      // Phase 2: History Promotion (Move & Clear)
+++      maybePromoteDuetToHistory();
+  
++       // Voice-first save command (Strict Command Mode)
++       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
 diff --git a/othello_ui.html b/othello_ui.html
-index a78c1b7b..d6ca18ec 100644
+index d6ca18ec..041220c4 100644
 --- a/othello_ui.html
 +++ b/othello_ui.html
-@@ -339,6 +339,7 @@
+@@ -337,12 +337,23 @@
+ 
+       <!-- Moved Chat View Content -->
        <div id="chat-view" class="view" style="display:flex;">
-         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
+-        <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
++        <!-- A) HISTORY REGION (Scrollable) -->
++        <div id="history-scroll" style="flex:1 1 auto; overflow-y:auto; display:flex; flex-direction:column; position:relative; min-height:0;">
++             <div id="duet-history-region">
++                 <div id="duet-history"></div>
++             </div>
++             <div id="duet-history-bar" class="duet-history-bar">
++                 HISTORY <span class="history-arrow">├ö├Ñ├ª</span>
++             </div>
++        </div>
+         
+-        <!-- Only this is scrollable history -->
+-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+-        <div id="chat-log" class="chat-log"></div>
++        <!-- B) LIVE REGION (Fixed Bottom) -->
++        <div id="chat-sheet" class="chat-sheet" style="flex:0 0 auto;">
++             <!-- Only this is scrollable history -->
++             <div id="draft-preview" class="draft-preview" style="display:none;"></div>
++             <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
++             <div id="chat-log" class="chat-log"></div>
++        </div>
          
-+        <!-- Only this is scrollable history -->
-         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
-         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
-         <div id="chat-log" class="chat-log"></div>
+         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
+       </div>
 diff --git a/static/othello.css b/static/othello.css
-index 825c710b..c7cc1ae5 100644
+index 382eeb57..85ae9b09 100644
 --- a/static/othello.css
 +++ b/static/othello.css
-@@ -2180,7 +2180,7 @@ body.chat-open #global-chat-fab {
+@@ -2203,64 +2203,71 @@ body.chat-open #global-chat-fab {
+   position: relative;
  }
  
- /* --- Duet Chat Mode (Unified) --- */
--/* Phase 2: Fix the scroll container */
-+/* Phase 2b: Fix the scroll container + Z-Index Stacking */
- .chat-sheet {
+-/* Phase 3: 3-Zone Flex Layout (Top - Scrollable - Bottom) */
++/* Chat View IS the scroll container now */
+ #chat-view {
    display: flex !important;
-   flex-direction: column !important;
-@@ -2191,11 +2191,16 @@ body.chat-open #global-chat-fab {
- /* Header is rigid */
- .chat-sheet__header {
-   flex: 0 0 auto;
-+  z-index: 200; /* Header stays absolutely on top */
-+  position: relative;
-+  box-shadow: 0 1px 0 var(--border);
+   flex-direction: column;
+-  flex: 1 1 0;
++  flex: 1 1 0; /* Grow, shrink, basis 0 */
+   min-height: 0;
+-  overflow: hidden !important; /* View itself does NOT scroll */
++  overflow-y: auto !important; /* The ONLY scrollbar */
++  overflow-x: hidden;
+   position: relative;
+-  padding: 0;
++  padding: 0; /* Strict */
  }
  
- /* Input is rigid (footer) */
- .input-bar {
-   flex: 0 0 auto;
-+  z-index: 200; /* Input stays absolutely on top */
-+  position: relative;
- }
- 
- /* Chat View IS the scroll container now */
-@@ -2217,12 +2222,16 @@ body.chat-open #global-chat-fab {
-   background: rgba(15, 23, 42, 0.98);
+-/* Duet Panes (Static Flex Items) */
++/* Duet Panes (Sticky) - Transparent Rails */
+ .duet-pane {
+-  position: static; /* No longer sticky */
+-  flex: 0 0 auto; /* Rigid height based on content */
+-  z-index: 100;
+-  background: transparent;
++  position: sticky;
++  z-index: 100; /* Must beat messages */
++  background: transparent; /* Transparent background */
    padding: 0.75rem;
    margin: 0;
--  display: block !important;
+-  display: block;
+-  pointer-events: none;
 +  display: block; /* always block, hidden by JS empty check if needed */
-   backdrop-filter: blur(8px);
--  /* Ensure they don't shrink away */
-   flex-shrink: 0; 
++  flex-shrink: 0;
++  pointer-events: none; /* Let clicks pass through empty space */
  }
  
+-.duet-pane > * { pointer-events: auto; }
+-.duet-pane:empty { display: none !important; }
++/* Re-enable pointer events on children (the bubbles) */
++.duet-pane > * {
++  pointer-events: auto;
++}
+ 
+-/* Chat Log (Middle Scrollable History) */
+-#chat-log {
+-  display: flex !important;
+-  flex-direction: column;
+-  flex: 1 1 0; /* Takes all remaining space */
+-  overflow-y: auto !important; /* HISTORY scrolls here */
+-  min-height: 0;
+-  height: auto !important;
+-  padding: 1rem;
+-  padding-top: 0.5rem;
+-  padding-bottom: 0.5rem;
 +/* Default hidden until populated */
 +.duet-pane:empty {
 +    display: none !important;
-+}
-+
+ }
+ 
+-/* Remove sticky-specific top/bottom since they are just flex order now */
  .duet-pane--top {
-   top: 0;
-   border-bottom: 1px solid rgba(255,255,255,0.1);
-@@ -2243,6 +2252,9 @@ body.chat-open #global-chat-fab {
-   overflow: visible !important; /* Let parent scroll it */
-   height: auto !important;
-   padding: 1rem;
+-  order: 1;
+-  border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++  top: 0;
++  /* Removed border/shadow for clean look */
++  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
++  /* box-shadow: 0 4px 12px rgba(0,0,0,0.4); */
+ }
+ 
+-#chat-log {
+-  order: 2; /* Middle */
++.duet-pane--bottom {
++  bottom: 0;
++  /* Removed border/shadow for clean look */
++  /* border-top: 1px solid rgba(255,255,255,0.1); */
++  /* box-shadow: 0 -4px 12px rgba(0,0,0,0.4); */
+ }
+ 
+-.duet-pane--bottom {
+-  order: 3;
+-  border-top: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
++/* Chat Log (History Flow) */
++#chat-log {
++  display: flex !important;
++  flex-direction: column;
++  flex: 1; /* occupy space between pins */
++  overflow: visible !important; /* Let parent scroll it */
++  height: auto !important;
++  padding: 1rem;
 +  /* Ensure content doesn't get hidden behind sticky headers due to margin collapse */
 +  padding-top: 1rem;
 +  padding-bottom: 1rem;
  }
  
+-/* Ensure empty slots don't take space/border */
+-.duet-pane:empty {
+-    display: none !important;
+-    border: none !important;
++#chat-sheet {
++  display: flex;
++  flex-direction: column;
++  width: 100%;
+ }
+ 
  /* Hide empty panes */
+@@ -2271,3 +2278,96 @@ body.chat-open #global-chat-fab {
+ /* Cleanup old classes */
+ .duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
+ 
++/* --- Duet Phase 2 History Fixes --- */
++#duet-history {
++  display: flex !important;
++  flex-direction: column !important;
++  padding: 0 !important; /* Managed by children */
++  width: 100%;
++}
++
++/* History Container (A) */
++#history-scroll {
++  /* Scrollable, takes up all top space */
++  scrollbar-width: thin;
++  overscroll-behavior: contain;
++  /* Flex parent for history items + sticky bar */
++}
++
++/* History Bar Lock (Pinned in History Region) */
++.duet-history-bar {
++  position: sticky;
++  bottom: 0px; /* Sticks to bottom of the scroll view */
++  z-index: 5; 
++  background: var(--bg-2); 
++  padding: 8px 0;
++  border-bottom: 1px solid var(--border);
++  color: var(--text-soft);
++  font-size: 0.8rem;
++  font-weight: bold;
++  text-transform: uppercase;
++  letter-spacing: 0.05em;
++  text-align: center;
++  width: 100%;
++  margin: 0;
++  border-top: 1px solid var(--border);
++  order: 999; /* visual safety */
++}
++
++/* Live Region (B) */
++#chat-sheet {
++  /* Fixed height/content, DO NOT SCROLL */
++  margin-top: 0 !important;
++  padding-top: 12px;
++  background: var(--bg-2); /* Opaque to cover anything passing under if necessary */
++  z-index: 10;
++  border-top: none; /* Separation is handled by history bar */
++  overflow: visible !important; 
++}
++
++.history-arrow {
++  display: inline-block;
++  margin-left: 4px;
++  font-size: 0.9em;
++  opacity: 0.7;
++}
++
++#duet-history-region {
++  /* Region wrapper for history blocks */
++  display: block;
++}
++
++#duet-history {
++  display: flex !important;
++  flex-direction: column !important;
++  padding: 0 !important;
++  padding-bottom: 16px !important; /* Ensure last item tucks behind bar */
++  width: 100%;
++}
++
++
++.history-duet {
++  display: flex !important;
++  flex-direction: column !important;
++  margin-bottom: 24px;
++  border-bottom: 1px solid var(--border);
++  padding: 12px 1rem 24px 1rem; /* Add padding here instead of parent */
++}
++
++.history-duet:last-child {
++  border-bottom: none;
++  margin-bottom: 0;
++}
++
++/* Reserve space: REMOVE fixed padding that creates dead gap. Layout handles height. */
++#chat-view {
++  padding-bottom: 0px !important;
++}
++
++/* Visual separation for the Live area (Gap between History and Live) */
++#chat-sheet {
++  margin-top: 12px;
++  padding-top: 12px;
++  overflow: visible !important; /* Ensure internal content doesn't scroll */
++}
++
 diff --git a/static/othello.js b/static/othello.js
-index 3a092bfc..1a19d8a7 100644
+index 69c723cf..f192fb47 100644
 --- a/static/othello.js
 +++ b/static/othello.js
-@@ -4300,76 +4300,81 @@
+@@ -793,8 +793,7 @@
+     const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
+     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+ 
+-    // Updated to support new Duet History container
+-    const chatLog = document.getElementById("duet-history") || document.getElementById('chat-log');
++    const chatLog = document.getElementById('chat-log');
+     // Relocated status to chat header (Phase 6 Fix)
+     const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+     const modeLabel = document.getElementById('current-mode-label');
+@@ -3656,6 +3655,9 @@
+               bindComposerActionButton("overlay_open");
+               requestAnimationFrame(() => bindComposerActionButton("overlay_open_raf"));
+           }
++          // Fix: Ensure history starts off-screen by scrolling to bottom immediately
++          // Force scroll to bottom when opening
++          scrollChatToBottom(true);
+       }
+ 
+       if (!isOpen) {
+@@ -4301,61 +4303,17 @@
        return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
      }
  
--    // Phase 3: Move nodes (no duplication)
-+    // Phase 3: Canonical Move
-     function applyDuetPins() {
--        if (!isDuetEnabled()) return;
--        
--        const chatLog = document.getElementById("chat-log");
-         const top = document.getElementById("duet-top");
-         const bottom = document.getElementById("duet-bottom");
--        if (!chatLog) return;
--        
--        // 1. Move any existing pinned items BACK to chatLog (restore history order if needed)
--        // Actually, simpler approach for V1:
--        // We only pin the LATEST. 
--        // Iterate chatLog children. Find last user msg, last bot msg.
--        // Move them to pins? No, that breaks history flow if they are old.
--        // Rule: Only pin if it is indeed slaved to the bottom/top.
--        // Actually, user wants "Latest assistant to TOP", "Latest user to BOTTOM".
--        // This implies visual displacement.
--        
--        // Better Strategy:
--        // 1. Clear pins.
--        // 2. Scan chatLog rows.
--        // 3. Last row -> if user, move to bottom.
--        // 4. Last ASSISTANT row -> move to top.
--        // Wait, if last row is user, and row before is assistant, we move BOTH.
--        // This effectively empties the bottom of the history.
+-    // Phase 4: Duet Scroll Logic (Single Scroll Container)
+-    function syncDuetHistorySpacer() {
+-       // Deprecated in Single Scroll model
++    // Phase 3: Canonical Move (Deprecated in Phase 12 Refactor)
++    function applyDuetPins() {
++        // No-op: Pins are removed in favor of strict History vs Live regions.
+     }
+-
+-    function scrollDuetHistoryToBottom() {
+-       // Deprecated - use scrollChatToBottom
+-    }
+-
+-    // Call on resize - harmless
+-    window.addEventListener("resize", () => {});
+-
+-    // Updated applyDuetPins to act as "archivePinnedToHistory"
+-    function archivePinnedToHistory() {
+-        // Source: Live Chat (#chat-log)
+-        // Dest: History (#duet-history)
+-        const liveContainer = document.getElementById("chat-log");
+-        const historyContainer = document.getElementById("duet-history");
+-        const viewport = document.getElementById("chat-view");
+-
+-        if (!liveContainer || !historyContainer || !viewport) return;
+-
+-        // 1. Capture Scroll State
+-        const prevScrollHeight = viewport.scrollHeight;
+-        const prevScrollTop = viewport.scrollTop;
+-
+-        // 2. Archive only valid message rows
+-        // We verify direct children to avoid deep grabbing
+-        const rows = Array.from(liveContainer.children).filter(el => el.classList.contains("msg-row"));
 -        
--        // Implementation:
--        // Find all .msg-row in chat main loop or chatLog
--        const rows = Array.from(chatLog.querySelectorAll('.msg-row'));
 -        if (rows.length === 0) return;
+-
+-        const fragment = document.createDocumentFragment();
+-        // Since we iterate in DOM order, we preserve chronological order
+-        rows.forEach(r => fragment.appendChild(r));
 -        
--        // Find last user row
-+        const chatLog = document.getElementById("chat-log");
-+
-+        // Fallback for safety
-+        if (!top || !bottom || !chatLog) return;
-+
-+        // 1. Move ALL pinned items BACK to chatLog first to restore order
-+        // This ensures scanning always finds true chronological last messages
-+        while (top.firstChild) chatLog.appendChild(top.firstChild);
-+        while (bottom.firstChild) chatLog.appendChild(bottom.firstChild);
-+
-+        // Sort chatLog by DOM order? No, appendChild moves to end.
-+        // We need to re-sort? No, they were originally at end. 
-+        // NOTE: If we move old pinned items back, they append to END. 
-+        // This might reorder history if we aren't careful.
-+        // TRICKY: We need to know where they CAME from to un-pin correctly.
-+        // SIMPLE FIX: Just sort all children of chatLog by timestamp?
-+        // OR: Since we only pin the VERY LAST items, when we unpin, we append to end. 
-+        // BUT: If a new message arrived, we want THAT to be pinned.
-+        
-+        // Sorting approach (safest for history):
-+        const allRows = Array.from(chatLog.children).filter(el => el.classList.contains('msg-row'));
-+        // If we strictly pin the last ones, unpinning means they go back to end.
-+        // New messages are appended to end. So order is preserved naturally.
-+        
-+        if (allRows.length === 0) return;
-+
-+        // 2. Scan for candidates
-         let lastUserRow = null;
-         let lastBotRow = null;
+-        historyContainer.appendChild(fragment);
+-
+-        // 3. Maintain Scroll Position
+-        const newScrollHeight = viewport.scrollHeight;
+-        const delta = newScrollHeight - prevScrollHeight;
 -        
-+
-         // Scan backwards
--        for (let i = rows.length - 1; i >= 0; i--) {
--            const r = rows[i];
-+        for (let i = allRows.length - 1; i >= 0; i--) {
-+            const r = allRows[i];
-             if (!lastUserRow && r.classList.contains('user')) lastUserRow = r;
--            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r; // Assume non-user is bot
-+            if (!lastBotRow && !r.classList.contains('user')) lastBotRow = r;
-             if (lastUserRow && lastBotRow) break;
-         }
- 
--        // Move to pins
-+        // 3. Move to pins
-         if (lastBotRow) {
--            top.appendChild(lastBotRow); // Moves it out of chatLog
--            // Ensure display is correct
-+            top.appendChild(lastBotRow);
-             top.style.display = 'block';
-         } else {
--            top.innerHTML = "";
-             top.style.display = 'none';
-         }
+-        if (delta > 0) {
+-            viewport.scrollTop = prevScrollTop + delta;
+-        }
 -        
-+
-         if (lastUserRow) {
--            bottom.appendChild(lastUserRow); // Moves it out of chatLog
-+            bottom.appendChild(lastUserRow);
-             bottom.style.display = 'block';
-         } else {
--            bottom.innerHTML = "";
-             bottom.style.display = 'none';
-         }
-         
--        // If we moved stuff, scroll might need adjustment? 
--        // Sticky logic handles the pins. History fills the middle.
-+        // 4. Update Padding for Scroll (Phase 3c - optional if CSS sticky works well)
-+        // With position:sticky, we don't need manual padding IF the scroll container is correct.
-+        // But we might want to ensure last history item isn't hidden behind bottom pin.
-+        // CSS 'scroll-padding-bottom' on container helps.
-+        const scroll = document.getElementById("chat-view");
-+        if (scroll) {
-+             const botH = bottom.offsetHeight || 0;
-+             const topH = top.offsetHeight || 0;
-+             // Add extra padding to LOG so it can scroll fully into view
-+             chatLog.style.paddingBottom = (botH + 20) + "px";
-+             chatLog.style.paddingTop = (topH + 10) + "px"; // Optional
-+        }
-     }
+-        console.debug(`[Duet] Archived ${rows.length} rows. History children: ${historyContainer.childElementCount}. Live children: ${liveContainer.childElementCount}`);
+-    }
+-
+-    // Deprecated / Aliased
+-    function applyDuetPins() {}
      
--    // No-op for old sync padding (CSS sticky handles it now)
      function syncDuetPadding() {}
  
-     function updateDuetView(row, role) {
--      // Defer to applyDuetPins in next frame to let DOM settle
+-    function updateDuetView(row, role) {}
++    function updateDuetView(row, role) {
 +      // Defer to applyDuetPins in next frame so DOM is ready
-       requestAnimationFrame(applyDuetPins);
++      requestAnimationFrame(applyDuetPins);
++    }
+ 
+     function bindDuetListeners() {
+        // Scroll logic is now native overflow
+@@ -4365,12 +4323,15 @@
+     document.addEventListener("DOMContentLoaded", bindDuetListeners);
+ 
+     function getChatContainer() {
+-      // Phase 4: Target the LIVE container (chat-log)
++      // Phase 4: Target the real scroll container for appending?
++      // No, we append to chat-log. The VIEW is the scroller.
++      // But getChatContainer is usually strictly for finding where to APPEND.
+       const chatLog = document.getElementById("chat-log");
+       
+       if (!chatLog) {
+-         // Fallback or error
+-        console.error("[Othello UI] CRITICAL: chat container missing (#chat-log).");
++         // ... error ...
++        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
++        // Visible UI Error (Phase A/B Requirement)
+         const toastContainer = document.getElementById("toast-container");
+         if (toastContainer) {
+             const errDiv = document.createElement("div");
+@@ -4378,7 +4339,7 @@
+             errDiv.textContent = "Error: Chat container missing.";
+             toastContainer.appendChild(errDiv);
+         }
+-        return document.getElementById("duet-history"); // Last resort
++        return null;
+       }
+       return chatLog;
+     }
+@@ -4518,14 +4479,11 @@
+             const text = msg && msg.transcript ? String(msg.transcript) : "";
+             if (!text.trim()) return;
+             const role = msg && msg.source === "assistant" ? "bot" : "user";
+-            // Pass special flag to force into history backlog
+-            addMessage(role, text, { isHistoryLoad: true, timestamp: msg.timestamp });
++            addMessage(role, text);
+           });
+           
+-          // Force scroll logic for "hidden backlog"
+-          syncDuetHistorySpacer();
+-          scrollDuetHistoryToBottom();
+-          // scrollChatToBottom(true); // Legacy call
++          // Force scroll to bottom after initial load
++          scrollChatToBottom(true);
+         };
+         if (renderedCount > 0) {
+           renderMessages(messages);
+@@ -4580,8 +4538,6 @@
+       return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
+     }
+ 
+-    let globalMessageSequence = 0;
+-
+     function addMessage(role, text, options = {}) {
+       console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
+       // Hide chat placeholder when first message appears
+@@ -4598,9 +4554,6 @@
+ 
+       const row = document.createElement("div");
+       row.className = `msg-row ${role}`;
+-      // Timestamp and Sequence for robust sorting
+-      row.dataset.timestamp = (options && options.timestamp) ? options.timestamp : Date.now();
+-      row.dataset.sequence = ++globalMessageSequence;
+ 
+       // Apply focus highlighting if a goal is focused
+       if (othelloState.activeGoalId) {
+@@ -4652,24 +4605,9 @@
+ 
+       row.appendChild(bubble);
+       
+-      // Phase 5: Routing for Duet vs Standard
+-      const duetTop = document.getElementById("duet-top");
+-      const duetBottom = document.getElementById("duet-bottom");
+-      const historySpacer = document.getElementById("duet-history-spacer");
+-
+-      const isHistoryLoad = options && options.isHistoryLoad; 
+-      
+-      // Phase 5: Routing for Duet vs Standard (SIMPLIFIED for Chronological Flow)
+-      const duetHistory = document.getElementById("duet-history");
+-      const isHistoryLoad = options && options.isHistoryLoad; 
+-      
+-      if (isHistoryLoad && duetHistory) {
+-         // History always appends-to-end of the History Block (which is above Live)
+-         duetHistory.appendChild(row);
+-      } else {
+-         // Live messages append strictly to the Live Container (#chat-log)
+-         // This ensures standard Top-Down flow.
+-         if (container) container.appendChild(row);
++      // Append to the resolved container
++      if (container) {
++         container.appendChild(row);
+       }
+       
+       updateDuetView(row, role);
+@@ -5920,6 +5858,35 @@
+         }
      }
  
++    function maybePromoteDuetToHistory() {
++      const live = document.getElementById("chat-log");
++      const hist = document.getElementById("duet-history");
++
++      if (live && live.children.length > 0 && hist) {
++        // Create wrapper for this duet turn
++        const block = document.createElement("div");
++        block.className = "history-duet";
++
++        // Move all children
++        while (live.firstChild) {
++            block.appendChild(live.firstChild);
++        }
++        
++        hist.appendChild(block);
++
++        console.debug("[duet] promoted nodes to history wrapper.");
++        
++        // Auto-pin history to bottom so bar remains visible at bottom
++        const sc = document.getElementById("history-scroll");
++        if (sc) {
++            // Force scroll to bottom to keep "HISTORY" bar visible as the boundary
++            requestAnimationFrame(() => {
++                sc.scrollTop = sc.scrollHeight;
++            });
++        }
++      }
++    }
++
+     async function sendMessage(overrideText = null, extraData = {}) {
+       // 1) Robust String Safety & Diagnostic
+       let override = overrideText;
+@@ -5933,8 +5900,8 @@
+       }
+ 
+       // Canonical text variable (Refetch input safely)
+-      const input = document.getElementById('user-input');
+-      let rawText = (override !== null ? override : (input?.value ?? ""));
++      const currentInput = document.getElementById('user-input');
++      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
+       
+       console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
+       
+@@ -5945,12 +5912,8 @@
+ 
+       if (!text && !extraData.ui_action) return;
+ 
+-      // Phase B (Cleanup): Auto-archive pins on new user message
+-      // This ensures the stage is cleared before the new user bubble appears.
+-      // We only do this if it's a genuine user message (text present or ui_action).
+-      if (typeof archivePinnedToHistory === "function") {
+-          archivePinnedToHistory();
+-      }
++      // Phase 2: History Promotion (Move & Clear)
++      maybePromoteDuetToHistory();
+ 
+       // Voice-first save command (Strict Command Mode)
+       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
diff --git a/othello_ui.html b/othello_ui.html
index d6ca18ec..92089325 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -339,10 +339,18 @@
       <div id="chat-view" class="view" style="display:flex;">
         <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
         
-        <!-- Only this is scrollable history -->
-        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
-        <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
-        <div id="chat-log" class="chat-log"></div>
+        <div id="duet-history" style="display:flex; flex-direction:column; padding:0;"></div>
+        
+        <div id="duet-history-bar" class="duet-history-bar" style="display:none;">
+          HISTORY <span class="history-arrow">Ôåæ</span>
+        </div>
+        
+        <div id="chat-sheet" class="chat-sheet" style="display: flex; flex-direction: column;">
+            <!-- Only this is scrollable history -->
+            <div id="draft-preview" class="draft-preview" style="display:none;"></div>
+            <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
+            <div id="chat-log" class="chat-log"></div>
+        </div>
         
         <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
       </div>
diff --git a/static/othello.css b/static/othello.css
index 382eeb57..8f90667a 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2271,3 +2271,54 @@ body.chat-open #global-chat-fab {
 /* Cleanup old classes */
 .duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
 
+/* --- Duet Restoration --- */
+#duet-history {
+  display: flex !important;
+  flex-direction: column !important;
+  padding: 0 !important;
+  width: 100%;
+}
+
+.duet-history-bar {
+  position: sticky;
+  bottom: 0;
+  z-index: 5;
+  background: var(--bg-2);
+  padding: 8px 0;
+  border-bottom: 1px solid var(--border);
+  border-top: 1px solid var(--border);
+  color: var(--text-soft);
+  font-size: 0.8rem;
+  font-weight: bold;
+  text-transform: uppercase;
+  letter-spacing: 0.05em;
+  text-align: center;
+  width: 100%;
+  margin-bottom: 0;
+}
+
+.history-arrow {
+  display: inline-block;
+  margin-left: 4px;
+  font-size: 0.9em;
+  opacity: 0.7;
+}
+
+.history-duet {
+  display: flex !important;
+  flex-direction: column !important;
+  margin-bottom: 24px;
+  border-bottom: 1px solid var(--border);
+  padding: 12px 1rem 24px 1rem;
+}
+.history-duet:last-child {
+  border-bottom: none;
+  margin-bottom: 0;
+}
+
+#chat-sheet {
+  margin-top: 12px;
+  padding-top: 12px;
+  overflow: visible !important;
+}
+
diff --git a/static/othello.js b/static/othello.js
index 69c723cf..c938cb1b 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4359,6 +4359,15 @@
 
     function bindDuetListeners() {
        // Scroll logic is now native overflow
+       
+       // Phase 3 Safety: Init Checks
+       const live = document.getElementById("chat-log");
+       const hist = document.getElementById("duet-history");
+       if (!live) console.error("[duet] missing #chat-log on init");
+       if (!hist) console.error("[duet] missing #duet-history on init");
+       
+       // Ensure bar is hidden initially if empty? 
+       // HTML has style="display:none" on bar, so we are good.
     }
 
     // Call bindDuetListeners on init
@@ -5920,6 +5929,49 @@
         }
     }
 
+    function maybePromoteDuetToHistory() {
+      // Guard: Critical Elements
+      const hist = document.getElementById("duet-history");
+      const live = document.getElementById("chat-log");
+      
+      if (!hist) {
+         console.error("[duet] missing #duet-history - Aborting promotion");
+         // Show visible banner as requested
+         const view = document.getElementById("chat-view");
+         if (view && !document.getElementById("duet-error-banner")) {
+             const banner = document.createElement("div");
+             banner.id = "duet-error-banner";
+             banner.style.background = "red";
+             banner.style.color = "white";
+             banner.style.padding = "4px";
+             banner.textContent = "DUET UI MISWIRED (#duet-history missing)";
+             view.prepend(banner);
+         }
+         return;
+      }
+      if (!live) {
+         console.error("[duet] missing #chat-log - Aborting promotion");
+         return;
+      }
+
+      // Promotion Logic
+      if (live.children.length > 0) {
+         const block = document.createElement("div");
+         block.className = "history-duet";
+         while (live.firstChild) block.appendChild(live.firstChild);
+         hist.appendChild(block);
+         
+         const bar = document.getElementById("duet-history-bar");
+         if (bar) bar.style.display = "block";
+
+         // Keep view pinned to bottom
+         const view = document.getElementById("chat-view");
+         if (view) view.scrollTop = view.scrollHeight;
+         
+         console.debug("[duet] promoted nodes to history.");
+      }
+    }
+
     async function sendMessage(overrideText = null, extraData = {}) {
       // 1) Robust String Safety & Diagnostic
       let override = overrideText;
@@ -5945,12 +5997,8 @@
 
       if (!text && !extraData.ui_action) return;
 
-      // Phase B (Cleanup): Auto-archive pins on new user message
-      // This ensures the stage is cleared before the new user bubble appears.
-      // We only do this if it's a genuine user message (text present or ui_action).
-      if (typeof archivePinnedToHistory === "function") {
-          archivePinnedToHistory();
-      }
+      // Phase 2: History Promotion (Move & Clear)
+      maybePromoteDuetToHistory();
 
       // Voice-first save command (Strict Command Mode)
       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
