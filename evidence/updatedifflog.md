# Cycle Status: COMPLETE (UX Re-architecture + Fixes)

## Scope + Constraints
- **Docs Found**: `contracts/EXECUTOR_CONTRACT.md`, `othello_ui.html`, `static/othello.js`.
- **Constraints**: 
    - No changes to `/api/message` endpoint contract.
    - No DB schema modifications.
    - Preserving `goal-intent` "?" marker logic and "create goal from message" flow.
    - Minimal diff, targeting `othello_ui.html`, `static/othello.js`, and `static/othello.css`.

## Todo Ledger
Planned:
- [x] Phase 1: Discover + Anchor (Identify UI entry points and message pipelines).
- [x] Phase 2: Navigation restructure (Planner-first home, remove Chat tab).
- [x] Phase 3: Global chat bubble + overlay shell.
- [x] Phase 4: Unify chat UI + context routing.
- [x] Phase 5: Dialogue selector.
- [x] Fix: Chat Overlay Wiring (Send, Dropdown, Close).

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.
- [x] Phase 2: Removed Chat tab. Split Middle Tab into explicit Today and Goals tabs. Updated default mode to `today-planner`. Refactored badge logic.
- [x] Phase 3: Implemented Global Chat Overlay. Moved `#chat-view` and `#input-bar` into a floating sheet. Added FAB triggering. Updated `switchView` to toggle overlay for 'chat'. Refactored `updateFocusRibbon` to respect overlay state.
- [x] Phase 4: Unified chat UI context routing. Updated `effectiveChannelForView` to map `today-planner` -> `planner` and `goals` -> `companion`. Configured `toggleChatOverlay` to reload chat history based on the underlying view context.
- [x] Phase 5: Implemented Dialogue Selector. Added `<select>` to chat overlay header. Added `manualChannelOverride` to state. Updated `effectiveChannelForView` to respect override. Cleared override on `switchView`.
- [x] Fix: Resolved regression where Send button was disconnected. Added `bindChatOverlayHandlers` to robustly re-attach events. Fixed CSS `pointer-events`/`z-index` for header controls. Safe input lookup in `sendMessage`.

## Next Action
Stop and commit. Cycle complete.

## Full Unified Diff
diff --git a/static/othello.css b/static/othello.css
--- a/static/othello.css
+++ b/static/othello.css
@@ -1911,1 +1911,1 @@
-  overflow: hidden;
+  overflow: hidden;
+  pointer-events: auto; /* Ensure interactivity inside the sheet */
+  position: relative;
+  z-index: 9996;
@@ -1926,1 +1926,4 @@
   background: var(--bg-2);
+  position: relative;
+  z-index: 100; /* Ensure header controls are top-most */
+  flex-shrink: 0; /* Don't shrink header */
 }
 
 .chat-back-btn {
@@ -1932,1 +1932,3 @@
   line-height: 1;
+  padding: 0.5rem; /* larger tap target */
+  z-index: 101; 
 }
 
 /* Re-style existing elements when inside the sheet */

diff --git a/static/othello.js b/static/othello.js
--- a/static/othello.js
+++ b/static/othello.js
@@ -3594,22 +3594,36 @@
-    // Phase 5: Handle selector changes
-    if (chatContextSelector) {
-        chatContextSelector.addEventListener('change', (e) => {
-            const newChannel = e.target.value;
-            console.log(`[Othello UI] Switching chat context to: ${newChannel}`);
-            
-            // Force reload chat history with new channel
-            // Note: We need to make sure effectiveChannelForView respects this override
-            // OR we just pass the channel directly to loadChatHistory if we refactor it.
-            // But strict state management suggests updating the state.
-            
-            // However, effectiveChannelForView derives from View/Mode. 
-            // We should use an override state.
-            othelloState.manualChannelOverride = newChannel;
-            
-            loadChatHistory();
-        });
-    }
-
-    if (globalChatFab) {
-      globalChatFab.addEventListener('click', () => toggleChatOverlay(true));
-    }
-    if (chatBackBtn) {
-      chatBackBtn.addEventListener('click', () => toggleChatOverlay(false));
-    }
-    if (globalChatOverlay) {
-        globalChatOverlay.addEventListener('click', (e) => {
-            if (e.target === globalChatOverlay) {
-                toggleChatOverlay(false);
-            }
-        });
-    }
+    // Phase 5: Handle selector changes
+    // Refactored to bindChatOverlayHandlers for robustness
+    function bindChatOverlayHandlers() {
+        const overlayInput = document.getElementById('user-input');
+        const overlaySend = document.getElementById('send');
+        const overlayClose = document.getElementById('chat-back-btn');
+        const overlaySelector = document.getElementById('chat-context-selector');
+        const fab = document.getElementById('global-chat-fab');
+
+        if (overlaySelector) {
+            overlaySelector.onchange = (e) => {
+                const newChannel = e.target.value;
+                console.log(`[Othello UI] Switching chat context to: ${newChannel}`);
+                othelloState.manualChannelOverride = newChannel;
+                loadChatHistory();
+            };
+        }
+
+        if (overlayClose) {
+            overlayClose.onclick = (e) => {
+                e.stopPropagation();
+                toggleChatOverlay(false);
+            };
+        }
+
+        if (fab) {
+            fab.onclick = () => toggleChatOverlay(true);
+        }
+
+        if (overlaySend) {
+            overlaySend.onclick = () => {
+                console.debug("[Othello UI] Send clicked in overlay");
+                sendMessage();
+            };
+        }
+
+        if (overlayInput) {
+             overlayInput.onkeydown = (e) => {
+                 if (e.key === "Enter" && !e.shiftKey) { // Allow Shift+Enter?
+                     e.preventDefault();
+                     console.debug("[Othello UI] Enter pressed in overlay input");
+                     sendMessage();
+                 }
+             };
+        }
+    }
+    
+    // Initial Bind
+    bindChatOverlayHandlers();
+
+    if (globalChatOverlay) {
+        globalChatOverlay.addEventListener('click', (e) => {
+            if (e.target === globalChatOverlay) {
+                toggleChatOverlay(false);
+            }
+        });
+    }

@@ -5604,5 +5618,7 @@
-      // Canonical text variable
-      let rawText = (override !== null ? override : (input?.value ?? ""));
-      if (typeof rawText !== "string") {
-          rawText = String(rawText ?? "");
-      }
+      // Canonical text variable (Refetch input safely)
+      const currentInput = document.getElementById('user-input');
+      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
+      
+      console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
+      
+      if (typeof rawText !== "string") {
+          rawText = String(rawText ?? "");
+      }
