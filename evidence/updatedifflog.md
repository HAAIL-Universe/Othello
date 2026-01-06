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

Completed:
- [x] Phase 1: Identified `othello_ui.html` and `static/othello.js` as key files. Confirmed `switchView` handles tab switching and `sendMessage` uses `/api/message` with mode-based channel selection.
- [x] Phase 2: Removed Chat tab. Split Middle Tab into explicit Today and Goals tabs. Updated default mode to `today-planner`. Refactored badge logic.
- [x] Phase 3: Implemented Global Chat Overlay. Moved `#chat-view` and `#input-bar` into a floating sheet. Added FAB triggering. Updated `switchView` to toggle overlay for 'chat'. Refactored `updateFocusRibbon` to respect overlay state.
- [x] Phase 4: Unified chat UI context routing. Updated `effectiveChannelForView` to map `today-planner` -> `planner` and `goals` -> `companion`. Configured `toggleChatOverlay` to reload chat history based on the underlying view context.
- [x] Phase 5: Implemented Dialogue Selector. Added `<select>` to chat overlay header. Added `manualChannelOverride` to state. Updated `effectiveChannelForView` to respect override. Cleared override on `switchView`.
- [x] Fix 1: Resolved regression where Send button was disconnected. Added `bindChatOverlayHandlers` to robustly re-attach events. Fixed CSS `pointer-events`/`z-index` for header controls. Safe input lookup in `sendMessage`.
- [x] Fix 2: Corrected Chat Overlay Layout (Flexbox column). Input pinned to bottom. FAB hidden when open. Added Planner Sub-menu for Today/Routine switching.

## Next Action
Stop and commit. Cycle complete.

## Full Unified Diff
diff --git a/othello_ui.html b/othello_ui.html
index 58480722..25854a3f 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -100,7 +100,7 @@
     <!-- TAB NAVIGATION -->
     <nav class="tab-bar">
       <button class="tab active" data-view="today-planner" id="planner-tab">
-        <span class="tab-label">Today</span>
+        <span class="tab-label">Planner</span>
         <span class="tab-badge hidden" id="planner-tab-badge"></span>
       </button>
       <button class="tab" data-view="goals" id="goals-tab">
@@ -111,6 +111,12 @@
         <span class="tab-label">Insights</span>
         <span class="tab-badge hidden" id="insights-tab-badge"></span>
       </button>
+
+      <!-- Planner Sub-Menu -->
+      <div id="planner-menu" class="planner-menu hidden">
+          <button data-subview="today" class="planner-menu-item active">Today</button>
+          <button data-subview="routine" class="planner-menu-item">Routine</button>
+      </div>
     </nav>

diff --git a/static/othello.css b/static/othello.css
index 5cdc01ce..45fd446d 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1953,17 +1953,18 @@
 .chat-sheet #chat-view {
   display: flex !important; /* Force show */
   flex-direction: column;
-  flex: 1;
-  height: auto;
+  flex: 1 1 auto; /* Grow and shrink */
+  height: 0; /* Critical for scrolling in flex column */
   min-height: 0;
   padding: 0;
-  overflow: hidden; /* inner scroll handled by log */
+  overflow-y: hidden; /* Scroll handled by log */
 }
 
 .chat-sheet #chat-log {
-  flex: 1;
-  overflow-y: auto;
+  flex: 1 1 auto;
+  overflow-y: auto; /* The log scrolls */
   padding: 1rem;
+  height: auto;
 }
 
 /* Adjust Input Bar for the sheet */
@@ -1975,11 +1976,48 @@
   border-top: 1px solid var(--border);
   background: var(--bg-2);
   padding: 1rem;
-  box-shadow: none; /* Remove glow that might look weird inside */
+  box-shadow: none; /* Remove glow */
   margin: 0;
+  margin-top: auto; /* Push to bottom just in case */
   transform: none;
+  flex-shrink: 0; /* Don't squash input */
+  z-index: 102;
 }
 
+/* Hide FAB when chat is open (Directive) */
+body.chat-open #global-chat-fab {
+    display: none !important;
+}
+
+/* Planner Menu (Directive Optional) */
+.planner-menu {
+    position: absolute;
+    top: calc(var(--tab-bar-height, 60px) + 5px);
+    left: 10px;
+    background: var(--bg-2);
+    border: 1px solid var(--border);
+    border-radius: 8px;
+    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
+    display: flex;
+    flex-direction: column;
+    min-width: 160px;
+    z-index: 5000;
+}
+.planner-menu.hidden { display: none; }
+.planner-menu-item {
+    background: transparent;
+    border: none;
+    border-bottom: 1px solid var(--border);
+    color: var(--text-main);
+    padding: 12px;
+    text-align: left;
+    cursor: pointer;
+}
+.planner-menu-item:last-child { border-bottom: none; }
+.planner-menu-item:hover { background: var(--bg-1); }
+.planner-menu-item.active { color: var(--accent); font-weight: bold; }

diff --git a/static/othello.js b/static/othello.js
index 03dd2136..38189859 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -3560,6 +3560,9 @@
       const isOpen = typeof show === 'boolean' ? show : !globalChatOverlay.classList.contains('open');
       globalChatOverlay.classList.toggle('open', isOpen);
 
+      // Directive: Hide FAB when open (via body class)
+      document.body.classList.toggle('chat-open', isOpen);
+      
       if (globalChatFab) {
          globalChatFab.classList.toggle('active', isOpen);
       }
@@ -3668,7 +3671,10 @@
       // Update tabs
       if (!tabs || !tabs.length) return;
       tabs.forEach(tab => {
-        if (tab.dataset.view === viewName) {
+        const target = tab.dataset.view;
+        // Planner tab stays active for both planner subviews
+        const isPlannerActive = (viewName === 'today-planner' || viewName === 'routine-planner') && target === 'today-planner';
+        if (tab.dataset.view === viewName || isPlannerActive) {
           tab.classList.add("active");
         } else {
           tab.classList.remove("active");
@@ -3716,10 +3722,52 @@
     if (tabs && tabs.length) {
       tabs.forEach(tab => {
         tab.addEventListener("click", () => {
+          const view = tab.dataset.view;
+          const plannerMenu = document.getElementById('planner-menu');
+
+          // Planner Tab Special Handling (Submenu)
+          if (view === 'today-planner') {
+              if (tab.classList.contains('active')) {
+                   if (plannerMenu) plannerMenu.classList.toggle('hidden');
+              } else {
+                   if (plannerMenu) plannerMenu.classList.add('hidden');
+                   switchView('today-planner');
+              }
+              return;
+          }
+
+          if (plannerMenu) plannerMenu.classList.add('hidden');
           switchView(tab.dataset.view);
         });
       });
     }
+    
+    // Planner Menu Handling
+    const plannerMenu = document.getElementById('planner-menu');
+    if (plannerMenu) {
+        plannerMenu.addEventListener('click', (e) => {
+            const btn = e.target.closest('.planner-menu-item');
+            if (btn) {
+                const sub = btn.dataset.subview;
+                if (sub === 'today') switchView('today-planner');
+                if (sub === 'routine') switchView('routine-planner');
+                plannerMenu.classList.add('hidden');
+
+                // Update active state in menu
+                Array.from(plannerMenu.children).forEach(c => c.classList.remove('active'));
+                btn.classList.add('active');
+            }
+        });
+        
+        // Close menu when clicking outside
+        document.addEventListener('click', (e) => {
+            if (!plannerMenu.classList.contains('hidden') && 
+                !e.target.closest('.planner-menu') && 
+                !e.target.closest('#planner-tab')) {
+                plannerMenu.classList.add('hidden');
+            }
+        });
+    }
@@ -4378,10 +4426,15 @@
 
       // Scroll to latest message
       requestAnimationFrame(() => {
+        // Fix: Scroll #chat-log if in overlay mode, as it's the scroll container
+        const chatLog = document.getElementById("chat-log");
         const chatView = document.getElementById("chat-view");
-        if (chatView) {
-          chatView.scrollTo({
-            top: chatView.scrollHeight,
+        // Prefer chat-log if it exists, otherwise chat-view
+        const scroller = chatLog || chatView;
+        
+        if (scroller) {
+          scroller.scrollTo({
+            top: scroller.scrollHeight,
             behavior: "smooth"
           });
         }

