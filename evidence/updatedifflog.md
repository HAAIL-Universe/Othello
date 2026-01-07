# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Phase 7: Duet Chat Mode Implemented (UI+CSS+JS)

## Next Action
Commit changes

diff --git a/othello_ui.html b/othello_ui.html
index bce50387..92d20c9c 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -335,6 +335,14 @@
 
       <!-- Moved Chat View Content -->
       <div id="chat-view" class="view" style="display:flex;">
+        <!-- DUET MODE WRAPPERS -->
+        <div id="duet-container" class="duet-container">
+          <div id="duet-top" class="duet-part duet-top"></div>
+          <div class="duet-spacer"></div>
+          <div id="duet-bottom" class="duet-part duet-bottom"></div>
+        </div>
+        <!-- END DUET WRAPPERS -->
+
         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
         <div id="chat-log" class="chat-log"></div>
diff --git a/static/othello.css b/static/othello.css
index 0dd5103a..0dae665f 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2179,3 +2179,52 @@ body.chat-open #global-chat-fab {
   }
 }
 
+/* --- Duet Chat Mode --- */
+.duet-container {
+  display: none;
+  flex-direction: column;
+  flex: 1;
+  height: 100%;
+  overflow: hidden;
+  padding: 0.5rem;
+}
+.duet-part {
+  overflow-y: auto;
+  -webkit-overflow-scrolling: touch;
+  padding: 0.25rem;
+}
+.duet-top {
+  max-height: 60%;
+  border-bottom: 1px solid rgba(255,255,255,0.05);
+  margin-bottom: 0.5rem;
+  scrollbar-width: none;
+}
+.duet-bottom {
+  max-height: 35%;
+  margin-top: 0.5rem;
+  border-top: 1px solid rgba(255,255,255,0.05);
+  scrollbar-width: none;
+}
+.duet-spacer {
+  flex: 1;
+  min-height: 1rem;
+}
+.duet-part::-webkit-scrollbar {
+  display: none; 
+}
+
+/* Mode toggling */
+.chat-sheet[data-view-mode="duet"] #chat-log {
+  display: none !important;
+}
+.chat-sheet[data-view-mode="duet"] #duet-container {
+  display: flex !important;
+}
+
+.chat-sheet[data-view-mode="history"] #chat-log {
+  display: flex !important;
+}
+.chat-sheet[data-view-mode="history"] #duet-container {
+  display: none !important;
+}
+
diff --git a/static/othello.js b/static/othello.js
index a4227fef..ee4a5d82 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -836,6 +836,7 @@
 
     // App state
     const othelloState = {
+      chatViewMode: "duet", // "duet" | "history"
       connectivity: 'online', // online | offline | degraded
       currentView: "today-planner",
       currentMode: "today", // companion | today | routine
@@ -4289,6 +4290,93 @@
     }
 
     // ===== CHAT FUNCTIONS =====
+
+    function setChatViewMode(mode, reason) {
+      if (othelloState.chatViewMode === mode) return;
+      othelloState.chatViewMode = mode;
+      
+      const sheet = document.querySelector('.chat-sheet');
+      if (sheet) {
+        sheet.setAttribute('data-view-mode', mode);
+      }
+      
+      const chatLog = document.getElementById("chat-log");
+      if (mode === "history") {
+        if (chatLog) {
+            // Scroll to near bottom but allow seeing history
+            chatLog.scrollTop = chatLog.scrollHeight - chatLog.clientHeight - 50; 
+        }
+      } else if (mode === "duet") {
+         // Ensure latest content is visible in duet parts
+         // (Handled by addMessage or updateDuetView)
+      }
+      console.log(`[Duet] Switched to ${mode} (${reason})`);
+    }
+
+    function updateDuetView(row, role) {
+      // Only applicable if duet wrappers exist
+      const duetTop = document.getElementById("duet-top");
+      const duetBottom = document.getElementById("duet-bottom");
+      if (!duetTop || !duetBottom) return;
+
+      const clone = row.cloneNode(true);
+      
+      if (role === "user") {
+        duetBottom.innerHTML = "";
+        duetBottom.appendChild(clone);
+        duetBottom.scrollTop = duetBottom.scrollHeight; // Pin bottom
+      } else {
+        duetTop.innerHTML = "";
+        duetTop.appendChild(clone);
+        duetTop.scrollTop = 0; // Read from top
+      }
+      
+      // Auto-switch to duet on new turn
+      setChatViewMode("duet", "new_message");
+    }
+
+    function bindDuetListeners() {
+       const duetContainer = document.getElementById("duet-container");
+       const chatLog = document.getElementById("chat-log");
+       
+       if (duetContainer) {
+           duetContainer.addEventListener("wheel", (e) => {
+               if (e.deltaY < -10) { // Scrolling UP significantly
+                   setChatViewMode("history", "scroll_up");
+               }
+           }, { passive: true });
+           
+           // Touch gesture
+           let touchSY = 0;
+           duetContainer.addEventListener("touchstart", e => { touchSY = e.changedTouches[0].clientY; }, {passive: true});
+           duetContainer.addEventListener("touchmove", e => {
+               const dy = e.changedTouches[0].clientY - touchSY;
+               if (dy > 50) { // Dragging DOWN (content moves down) -> wait, scrolling up means content moves down. 
+                   // Dragging DOWN = scrolling UP the viewport? 
+                   // Standard: Swipe DOWN moves content DOWN, revealing TOP. That's scrolling UP.
+                   setChatViewMode("history", "swipe_down"); 
+               }
+           }, {passive: true});
+       }
+       
+       if (chatLog) {
+           chatLog.addEventListener("scroll", () => {
+               if (othelloState.chatViewMode === "history") {
+                   const distFromBottom = chatLog.scrollHeight - (chatLog.scrollTop + chatLog.clientHeight);
+                   if (distFromBottom < 20) {
+                       setChatViewMode("duet", "scrolled_bottom");
+                   }
+               }
+           });
+       }
+       
+       // Init default
+       setChatViewMode("duet", "init");
+    }
+
+    // Call bindDuetListeners on init
+    document.addEventListener("DOMContentLoaded", bindDuetListeners);
+
     function getChatContainer() {
       // B1: Canonical resolution. We strictly use #chat-log.
       // We do NOT fallback to #chat-view (parent) to avoid split-brain messages.
@@ -4569,6 +4657,8 @@
       if (container) {
          container.appendChild(row);
       }
+      
+      updateDuetView(row, role);
 
       if (role === "user" && clientMessageId) {
         othelloState.messagesByClientId[clientMessageId] = {
