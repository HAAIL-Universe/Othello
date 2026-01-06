# Cycle Status: COMPLETE (Follow-up 2)

## Todo Ledger
- [x] Connectivity State: Added `othelloState.connectivity`, `updateConnectivity` helper.
- [x] Robust sendMessage: Wrapped fetch in try/catch to distinguish network errors from HTTP errors.
- [x] Ping Loop: Added 15s ping interval when overlay is open.
- [x] UI Updates: Status pill reflects Online/Offline/Degraded automatically.

## Next Action
Stop and commit.

## Follow-up Diff
```diff
diff --git a/static/othello.js b/static/othello.js
--- a/static/othello.js
+++ b/static/othello.js
@@ -811,6 +811,7 @@
 
     // App state
     const othelloState = {
+      connectivity: 'online', // online | offline | degraded
       currentView: "today-planner",
       currentMode: "today", // companion | today | routine
       manualChannelOverride: null, // Phase 5: For Dialogue Selector
@@ -3555,10 +3556,54 @@
     const chatBackBtn = document.getElementById('chat-back-btn');
     const chatContextSelector = document.getElementById('chat-context-selector');
     
+    // Connectivity State Management
+    function updateConnectivity(status, message = "") {
+        othelloState.connectivity = status;
+        const pill = document.querySelector('.status-pill');
+        const text = pill ? pill.querySelector('#status') : null;
+        const dot = pill ? pill.querySelector('.dot') : null;
+        
+        if (text) {
+            if (status === 'online') text.textContent = "Online";
+            else if (status === 'offline') text.textContent = "Offline";
+            else if (status === 'degraded') text.textContent = message || "Degraded";
+        }
+        
+        if (pill) {
+            pill.classList.remove('offline', 'degraded');
+            if (status !== 'online') pill.classList.add(status);
+        }
+    }
+
+    // Ping Logic
+    let pingInterval = null;
+    function startConnectivityPing() {
+        if (pingInterval) return;
+        pingInterval = setInterval(async () => {
+             try {
+                 const res = await fetch('/api/capabilities', { method: 'GET', cache: 'no-store' });
+                 if (res.ok) updateConnectivity('online');
+                 else updateConnectivity('degraded', `Status ${res.status}`);
+             } catch (e) {
+                 updateConnectivity('offline');
+             }
+        }, 15000);
+    }
+
+    function stopConnectivityPing() {
+        if (pingInterval) {
+            clearInterval(pingInterval);
+            pingInterval = null;
+        }
+    }
+
     function toggleChatOverlay(show) {
       if (!globalChatOverlay) return;
       const isOpen = typeof show === 'boolean' ? show : !globalChatOverlay.classList.contains('open');
-      globalChatOverlay.classList.toggle('open', isOpen);
+      if (globalChatOverlay) {
+        globalChatOverlay.classList.toggle('open', isOpen);
+      }
       
       // Directive: Hide FAB when open (via body class)
       document.body.classList.toggle('chat-open', isOpen);
@@ -3567,7 +3612,12 @@
          globalChatFab.classList.toggle('active', isOpen);
       }
 
+      if (!isOpen) {
+          stopConnectivityPing();
+      }
+
       if (isOpen) {
+        startConnectivityPing();
         // Phase 5: Initialize selector based on current effective channel
         // But only if we haven't manually overridden it yet for this session? 
         // Actually, better to reset to context on open, unless user changed it *while* open.
@@ -5918,17 +5968,28 @@
 
         beginThinking();
         let data;
+        let res;
         try {
-            const res = await fetch(API, {
-              method: "POST",
-              headers: {"Content-Type": "application/json"},
-              credentials: "include",
-              body: JSON.stringify(payload)
-            });
+            console.log(`[Othello UI] Fetching ${API}...`);
+            try {
+                res = await fetch(API, {
+                  method: "POST",
+                  headers: {"Content-Type": "application/json"},
+                  credentials: "include",
+                  body: JSON.stringify(payload)
+                });
+            } catch (netErr) {
+                console.error("[Othello UI] Network failure:", netErr);
+                addMessage("bot", "[Connection error: backend unreachable]");
+                updateConnectivity('offline');
+                statusEl.textContent = "Offline";
+                return; // Finally will still run to clear thinking
+            }
 
             console.log("[Othello UI] /api/message status", res.status);
 
             if (!res.ok) {
+              updateConnectivity('degraded', `Error ${res.status}`);
               const contentType = res.headers.get("content-type") || "";
               if (contentType.includes("application/json")) {
                 let errorData = null;
@@ -5956,10 +6017,15 @@
                 console.error("[Othello UI] sendMessage non-JSON error:", res.status, preview);
                 addMessage("bot", `[Error ${res.status}]: Unable to process your message. Please try again.`);
               }
-              statusEl.textContent = "Error";
+              // Do NOT set statusEl to "Error" blindly if we want connectivity state to rule.
+              // But for immediate feedback, "Error" is fine, assuming it reverts to connectivity state later?
+              // Logic: updateConnectivity sets the pill text.
+              // So we should let updateConnectivity win or specifically set it here.
+              // We already called updateConnectivity('degraded').
               return;
             }
 
+            updateConnectivity('online');
             data = await res.json();
         } finally {
             endThinking();
```
