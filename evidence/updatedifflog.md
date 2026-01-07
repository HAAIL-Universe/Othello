# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Fixed Duet Chat Layout (Sticky Pinned Top/Bottom)

## Next Action
Commit and Push

diff --git a/othello_ui.html b/othello_ui.html
index 31801668..a78c1b7b 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -337,13 +337,13 @@
 
       <!-- Moved Chat View Content -->
       <div id="chat-view" class="view" style="display:flex;">
-        <div id="duet-top" class="duet-pin-top" style="display:none;"></div>
+        <div id="duet-top" class="duet-pane duet-pane--top" style="display:none;"></div>
         
         <div id="draft-preview" class="draft-preview" style="display:none;"></div>
         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
         <div id="chat-log" class="chat-log"></div>
         
-        <div id="duet-bottom" class="duet-pin-bottom" style="display:none;"></div>
+        <div id="duet-bottom" class="duet-pane duet-pane--bottom" style="display:none;"></div>
       </div>
 
       <!-- Moved Input Bar -->
diff --git a/static/othello.css b/static/othello.css
index e2a9fefb..3ae6edfa 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2180,28 +2180,31 @@ body.chat-open #global-chat-fab {
 }
 
 /* --- Duet Chat Mode (Unified) --- */
-.duet-pin-top {
+.duet-pane {
   position: sticky;
-  top: 0;
-  z-index: 10;
-  background: rgba(15, 23, 42, 0.98); /* Opaque bg */
-  border-bottom: 1px solid rgba(255,255,255,0.1);
+  z-index: 50; /* Above chat bubbles but below header if needed */
+  background: rgba(15, 23, 42, 0.98);
   padding: 0.5rem;
   margin: 0;
-  display: block !important; /* Ensure visibility once populated */
-  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
+  display: block !important;
+  backdrop-filter: blur(8px);
 }
 
-.duet-pin-bottom {
-  position: sticky;
+.duet-pane--top {
+  top: 0;
+  border-bottom: 1px solid rgba(255,255,255,0.1);
+  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
+}
+
+.duet-pane--bottom {
   bottom: 0;
-  z-index: 10;
-  background: rgba(15, 23, 42, 0.98);
   border-top: 1px solid rgba(255,255,255,0.1);
-  padding: 0.5rem;
-  margin: 0;
-  display: block !important;
-  box-shadow: 0 -4px 12px rgba(0,0,0,0.2);
+  box-shadow: 0 -4px 12px rgba(0,0,0,0.3);
+}
+
+/* Hide empty panes */
+#duet-top:empty, #duet-bottom:empty {
+  display: none !important;
 }
 
 /* Ensure chat-log doesn't hide */
@@ -2209,6 +2212,6 @@ body.chat-open #global-chat-fab {
   display: flex !important;
 }
 
-/* Hide original duet container styles */
-.duet-container { display: none; }
+/* Cleanup old classes if any exist */
+.duet-pin-top, .duet-pin-bottom, .duet-container { display: none; }
 
diff --git a/static/othello.js b/static/othello.js
index 9727ab1b..7ac74076 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4297,21 +4297,25 @@
 
     // Unified Duet Logic (Sticky Pins)
     function isDuetEnabled() {
+      // Check for the new IDs from step 3
       return !!document.getElementById("duet-top") && !!document.getElementById("duet-bottom");
     }
 
     function syncDuetPadding() {
-        const scroll = document.getElementById("chat-log"); // chat-log siblings are pinned
+        const scroll = document.getElementById("chat-log");
         const top = document.getElementById("duet-top");
         const bottom = document.getElementById("duet-bottom");
-        if (!scroll || !top || !bottom) return;
         
-        // Add minimal padding so text isn't flush with sticky header/footer
-        const padTop = (top.offsetHeight || 0) + 12;
-        const padBottom = (bottom.offsetHeight || 0) + 12;
+        if (!scroll || !top || !bottom) return;
+
+        // Calc exact heights
+        const topH = top.getBoundingClientRect().height;
+        const botH = bottom.getBoundingClientRect().height;
         
-        scroll.style.paddingTop = padTop + "px";
-        scroll.style.paddingBottom = padBottom + "px";
+        // Pad scroll container so content doesn't hide behind sticky headers
+        // Add +10px breathing room
+        scroll.style.paddingTop = (topH > 0 ? topH + 10 : 0) + "px";
+        scroll.style.paddingBottom = (botH > 0 ? botH + 10 : 0) + "px";
     }
 
     function updateDuetView(row, role) {
@@ -4321,26 +4325,42 @@
       const duetBottom = document.getElementById("duet-bottom");
       
       const clone = row.cloneNode(true);
-      // Remove ID to avoid duplicates if present
-      clone.removeAttribute("id");
+      clone.removeAttribute("id"); // No duplicate IDs
+      clone.classList.add("is-pinned-copy"); // CSS hooks if needed
+      
+      // Duet Logic:
+      // USER -> Bottom pinned
+      // ASSISTANT (bot) -> Top pinned
       
       if (role === "user") {
-        duetBottom.innerHTML = "";
+        duetBottom.innerHTML = ""; // Replace old pinned
         duetBottom.appendChild(clone);
-        duetBottom.style.display = "block";
-      } else {
+      } else if (role === "bot" || role === "assistant") {
         duetTop.innerHTML = "";
         duetTop.appendChild(clone);
-        duetTop.style.display = "block";
       }
       
-      syncDuetPadding();
-      console.log(`[DUET_PIN] updated ${role}`, { topH: duetTop.offsetHeight, bottomH: duetBottom.offsetHeight });
+      // Force layout recalc
+      requestAnimationFrame(() => {
+          syncDuetPadding();
+          // Log verification
+          console.debug(`[DUET] Pinned ${role}`, { 
+              topH: duetTop.offsetHeight, 
+              bottomH: duetBottom.offsetHeight 
+          });
+      });
     }
 
     function bindDuetListeners() {
-       // Legacy listener removal or no-op
-       console.log("Duet listeners no longer required for sticky mode");
+       const chatLog = document.getElementById("chat-log");
+       if (chatLog) {
+           // On scroll: if user scrolls UP significantly away from bottom, 
+           // we could choose to HIDE the pins to show full history.
+           // For V1, we leave them sticky as requested.
+           chatLog.addEventListener("scroll", () => {
+             // Optional: visual effects on shadow
+           }, { passive: true });
+       }
     }
 
     // Call bindDuetListeners on init
