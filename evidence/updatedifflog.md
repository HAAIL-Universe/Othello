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
- [x] Fix: Chat Layout (Input Bottom, No Overlap, Hide FAB).
- [x] Feat: Planner Menu (Sub-surface switching).
- [x] Fix: Chat Anchor (Bottom-anchored messages, Smart Scroll).

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.
- [x] Phase 2: Removed Chat tab. Split Middle Tab into explicit Today and Goals tabs. Updated default mode to `today-planner`. Refactored badge logic.
- [x] Phase 3: Implemented Global Chat Overlay. Moved `#chat-view` and `#input-bar` into a floating sheet. Added FAB triggering. Updated `switchView` to toggle overlay for 'chat'. Refactored `updateFocusRibbon` to respect overlay state.
- [x] Phase 4: Unified chat UI context routing. Updated `effectiveChannelForView` to map `today-planner` -> `planner` and `goals` -> `companion`. Configured `toggleChatOverlay` to reload chat history based on the underlying view context.
- [x] Phase 5: Implemented Dialogue Selector. Added `<select>` to chat overlay header. Added `manualChannelOverride` to state. Updated `effectiveChannelForView` to respect override. Cleared override on `switchView`.
- [x] Fix 1: Resolved regression where Send button was disconnected. Added `bindChatOverlayHandlers` to robustly re-attach events. Fixed CSS `pointer-events`/`z-index` for header controls. Safe input lookup in `sendMessage`.
- [x] Fix 2: Corrected Chat Overlay Layout (Flexbox column). Input pinned to bottom. FAB hidden when open. Added Planner Sub-menu for Today/Routine switching.
- [x] Fix 3: Implemented bottom-anchored chat log via CSS `justify-content: flex-end`. Refined auto-scroll to be instant (removing "fly off top" animation) and conditional on position.

## Next Action
Stop and commit. Cycle complete.

## Full Unified Diff
diff --git a/static/othello.css b/static/othello.css
index 45fd446d..0075f2d8 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1965,6 +1965,10 @@
   overflow-y: auto; /* The log scrolls */
   padding: 1rem;
   height: auto;
+  display: flex;
+  flex-direction: column;
+  justify-content: flex-end; /* anchor messages to bottom */
+  gap: 0.5rem;
 }
 
 /* Adjust Input Bar for the sheet */
diff --git a/static/othello.js b/static/othello.js
index 38189859..fd520b75 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4297,6 +4297,16 @@
             const role = msg && msg.source === "assistant" ? "bot" : "user";
             addMessage(role, text);
           });
+
+          // Force scroll to bottom after initial load
+          requestAnimationFrame(() => {
+              const chatLog = document.getElementById("chat-log");
+              const chatView = document.getElementById("chat-view");
+              const scroller = chatLog || chatView;
+              if (scroller) {
+                  scroller.scrollTop = scroller.scrollHeight;
+              }
+          });
         };
         if (renderedCount > 0) {
           renderMessages(messages);
@@ -4424,7 +4434,7 @@
         refreshSecondarySuggestionUI(othelloState.messagesByClientId[clientMessageId]);
       }
 
-      // Scroll to latest message
+      // Scroll to latest message (Smart Scroll)
       requestAnimationFrame(() => {
         // Fix: Scroll #chat-log if in overlay mode, as it's the scroll container
         const chatLog = document.getElementById("chat-log");
@@ -4433,10 +4443,17 @@
         const scroller = chatLog || chatView;
 
         if (scroller) {
-          scroller.scrollTo({
-            top: scroller.scrollHeight,
-            behavior: "smooth"
-          });
+            // Determine if we should auto-scroll
+            const distanceFromBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
+            // If we are somewhat near the bottom (or if the content was just added and it was empty/short)
+            // we force scroll. But if user is reading up history, we leave it be.
+            // For new messages (which this function handles), we usually want to jump if we are close enough.
+            // 80px seems reasonable (about 1-2 messages).
+            // We also scroll if the total height is small (just filling up).
+
+            if (distanceFromBottom < 150 || scroller.scrollHeight <= scroller.clientHeight * 1.5) {
+                 scroller.scrollTop = scroller.scrollHeight; // Instant scroll (no smooth) to prevent "flying"
+            }
         }
       });
       return { row, bubble };

