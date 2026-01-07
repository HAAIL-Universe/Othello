# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Phase 6: Consolidate Chat & Status (Global Pill Removal)
- [x] Phase 6: Fix client-side null textContent crash
- [x] Phase 6: Backend Auto-Routing Implementation
- [x] Phase 6: Fix 500 error in auto-routing logic
- [x] Phase 6: Add deterministic error surfacing for 500s

## Next Action
Stop and commit.

diff --git a/api.py b/api.py
index 0bbfbf5b..6ac8ffae 100644
--- a/api.py
+++ b/api.py
@@ -4323,10 +4323,43 @@ def handle_message():
         current_view = data.get("current_view")
         raw_channel = data.get("channel")
         view_label = str(current_view or "chat")
-        is_chat_view = view_label.strip().lower() == "chat"
-        incoming_channel = str(raw_channel or "").strip().lower() or None
-        effective_channel = "companion" if is_chat_view else (incoming_channel or "companion")
-        if effective_channel not in {"companion", "planner"}:
+        
+        # Phase 6: True Auto Routing (Content-based)
+        effective_channel = "companion" # Default safe fallback
+        incoming_channel = "unknown"
+        try:
+            incoming_channel = str(raw_channel or "").strip().lower()
+            if incoming_channel == "auto" or not incoming_channel:
+                # Simple heuristic routing
+                # Guardrail: ensure user_input is safe string (already likely is, but strict compliance)
+                safe_u_in = (user_input or "").lower()
+                
+                planner_keywords = {"plan", "schedule", "routine", "calendar", "agenda", "today", "tomorrow", "week"}
+                
+                # Guardrail: raw_goal_id is usually None or string/int
+                has_goal_focus = raw_goal_id is not None
+                
+                if has_goal_focus:
+                    effective_channel = "companion"
+                elif any(k in safe_u_in for k in planner_keywords):
+                    effective_channel = "planner"
+                else:
+                    effective_channel = "companion"
+            elif incoming_channel in {"companion", "planner"}:
+                effective_channel = incoming_channel
+            else:
+                effective_channel = "companion"
+                
+            # Debug Log for Auto Routing
+            logger.info(
+                "API: routing decision request_id=%s incoming='%s' user_input_len=%d effective=%s",
+                request_id,
+                incoming_channel,
+                len(user_input),
+                effective_channel
+            )
+        except Exception as e:
+            logger.error("API: auto-routing logic crashed request_id=%s", request_id, exc_info=True)
             effective_channel = "companion"
         raw_client_message_id = data.get("client_message_id")
         if raw_client_message_id is None:
@@ -7551,7 +7584,15 @@ def handle_message():
             type(exc).__name__,
             extra={"request_id": request_id},
         )
-        return api_error("INTERNAL_ERROR", "Internal server error", 500)
+        return api_error(
+            "INTERNAL_ERROR",
+            f"Internal server error: {str(exc)}",
+            500,
+            details={
+                "error_type": type(exc).__name__,
+                "request_id": request_id
+            }
+        )
     finally:
         _log_request_end()
 
diff --git a/build_docs/evidence/0dee2034_peek_mode.patch b/build_docs/evidence/0dee2034_peek_mode.patch
deleted file mode 100644
index 551975b5..00000000
--- a/build_docs/evidence/0dee2034_peek_mode.patch
+++ /dev/null
@@ -1 +0,0 @@
-how --patch 0dee2034b678a748a98b0705ecbd2342a9194ad5
diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index 77ef230d..6e2b17ad 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -1,222 +1,713 @@
-# Cycle Status: IN_PROGRESS
+# Cycle Status: COMPLETE
 
 ## Todo Ledger
+Completed:
+- [x] Phase 6: Consolidate Chat & Status (Global Pill Removal)
+- [x] Phase 6: Fix client-side null textContent crash
+- [x] Phase 6: Backend Auto-Routing Implementation
+- [x] Phase 6: Fix 500 error in auto-routing logic (added try/except guard)
 
 ## Next Action
-Fill next action.
+Stop and commit.
 
-diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+diff --git a/api.py b/api.py
+index 0bbfbf5b..f2a6c41d 100644
+--- a/api.py
++++ b/api.py
+@@ -4323,10 +4323,43 @@ def handle_message():
+         current_view = data.get("current_view")
+         raw_channel = data.get("channel")
+         view_label = str(current_view or "chat")
+-        is_chat_view = view_label.strip().lower() == "chat"
+-        incoming_channel = str(raw_channel or "").strip().lower() or None
+-        effective_channel = "companion" if is_chat_view else (incoming_channel or "companion")
+-        if effective_channel not in {"companion", "planner"}:
++        
++        # Phase 6: True Auto Routing (Content-based)
++        effective_channel = "companion" # Default safe fallback
++        incoming_channel = "unknown"
++        try:
++            incoming_channel = str(raw_channel or "").strip().lower()
++            if incoming_channel == "auto" or not incoming_channel:
++                # Simple heuristic routing
++                # Guardrail: ensure user_input is safe string (already likely is, but strict compliance)
++                safe_u_in = (user_input or "").lower()
++                
++                planner_keywords = {"plan", "schedule", "routine", "calendar", "agenda", "today", "tomorrow", "week"}
++                
++                # Guardrail: raw_goal_id is usually None or string/int
++                has_goal_focus = raw_goal_id is not None
++                
++                if has_goal_focus:
++                    effective_channel = "companion"
++                elif any(k in safe_u_in for k in planner_keywords):
++                    effective_channel = "planner"
++                else:
++                    effective_channel = "companion"
++            elif incoming_channel in {"companion", "planner"}:
++                effective_channel = incoming_channel
++            else:
++                effective_channel = "companion"
++                
++            # Debug Log for Auto Routing
++            logger.info(
++                "API: routing decision request_id=%s incoming='%s' user_input_len=%d effective=%s",
++                request_id,
++                incoming_channel,
++                len(user_input),
++                effective_channel
++            )
++        except Exception as e:
++            logger.error("API: auto-routing logic crashed request_id=%s", request_id, exc_info=True)
+             effective_channel = "companion"
+         raw_client_message_id = data.get("client_message_id")
+         if raw_client_message_id is None:
+diff --git a/build_docs/evidence/0dee2034_peek_mode.patch b/build_docs/evidence/0dee2034_peek_mode.patch
 deleted file mode 100644
-index 4aa7f53e..00000000
---- a/evidence/updatedifflog.md
+index 551975b5..00000000
+--- a/build_docs/evidence/0dee2034_peek_mode.patch
 +++ /dev/null
-@@ -1,209 +0,0 @@
--# Cycle Status: COMPLETE
--
--## Todo Ledger
--Completed:
--- [x] Phase A: UI Refactor (Remove dropdown, add pill)
--- [x] Phase B: Wiring (Backend route exposure + Client routing pill)
--
--## Next Action
--Commit
--
--diff --git a/api.py b/api.py
--index 10d9e32d..0bbfbf5b 100644
----- a/api.py
--+++ b/api.py
--@@ -5698,6 +5698,11 @@ def handle_message():
--                          "roles_represented": list(set(m.get("role", "unknown") for m in companion_context))
--                      }
-- 
--+                # Phase A/B: Expose Route
--+                if "selected_route" not in payload:
--+                    route_label = "Planner" if effective_channel == "planner" else "Chat"
--+                    payload["selected_route"] = route_label
--+
--             return jsonify(payload)
-- 
--         logger.info(
--diff --git a/core/architect_brain.py b/core/architect_brain.py
--index ed5703a3..a56669e3 100644
----- a/core/architect_brain.py
--+++ b/core/architect_brain.py
--@@ -462,7 +462,7 @@ class Architect:
--             return user_facing_response, agent_status
-- 
--         except Exception as e:
---            self.logger.error(f"Ôö£├ÂÔö£├┐Ôö£┬½ Architect failed: {e}", exc_info=True)
--+            self.logger.error(f"Ôö£├ÂÔö£├┐Ôö£┬½ Architect failed: {e}")
--             # Return error message with default agent_status
--             return "Sorry, something went wrong planning that.", {
--                 "planner_active": False,
+@@ -1 +0,0 @@
+-how --patch 0dee2034b678a748a98b0705ecbd2342a9194ad5
+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+index 77ef230d..f6b2962c 100644
+--- a/evidence/updatedifflog.md
++++ b/evidence/updatedifflog.md
+@@ -1,222 +1,398 @@
+-# Cycle Status: IN_PROGRESS
++# Cycle Status: COMPLETE
+ 
+ ## Todo Ledger
++Completed:
++- [x] Phase 6: Consolidate Chat & Status (Global Pill Removal)
++- [x] Phase 6: Fix client-side null textContent crash
++- [x] Phase 6: Backend Auto-Routing Implementation
++- [x] Phase 6: Fix 500 error in auto-routing logic
+ 
+ ## Next Action
+-Fill next action.
++Stop and commit.
+ 
 -diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
--index e80434ec..78b50369 100644
++diff --git a/api.py b/api.py
++index 0bbfbf5b..bff3a2be 100644
++--- a/api.py
+++++ b/api.py
++@@ -4323,11 +4323,38 @@ def handle_message():
++         current_view = data.get("current_view")
++         raw_channel = data.get("channel")
++         view_label = str(current_view or "chat")
++-        is_chat_view = view_label.strip().lower() == "chat"
++-        incoming_channel = str(raw_channel or "").strip().lower() or None
++-        effective_channel = "companion" if is_chat_view else (incoming_channel or "companion")
++-        if effective_channel not in {"companion", "planner"}:
+++        
+++        # Phase 6: True Auto Routing (Content-based)
+++        incoming_channel = str(raw_channel or "").strip().lower()
+++        if incoming_channel == "auto" or not incoming_channel:
+++            # Simple heuristic routing
+++            # Guardrail: ensure user_input is safe string (already likely is, but strict compliance)
+++            safe_u_in = user_input.lower() if user_input else ""
+++            
+++            planner_keywords = {"plan", "schedule", "routine", "calendar", "agenda", "today", "tomorrow", "week"}
+++            
+++            # Guardrail: raw_goal_id is usually None or string/int
+++            has_goal_focus = raw_goal_id is not None
+++            
+++            if has_goal_focus:
+++                effective_channel = "companion"
+++            elif any(k in safe_u_in for k in planner_keywords):
+++                effective_channel = "planner"
+++            else:
+++                effective_channel = "companion"
+++        elif incoming_channel in {"companion", "planner"}:
+++            effective_channel = incoming_channel
+++        else:
++             effective_channel = "companion"
+++            
+++        # Debug Log for Auto Routing
+++        logger.info(
+++            "API: routing decision request_id=%s incoming='%s' user_input_len=%d effective=%s",
+++            request_id,
+++            incoming_channel,
+++            len(user_input),
+++            effective_channel
+++        )
++         raw_client_message_id = data.get("client_message_id")
++         if raw_client_message_id is None:
++             raw_client_message_id = data.get("clientMessageId")
++diff --git a/build_docs/evidence/0dee2034_peek_mode.patch b/build_docs/evidence/0dee2034_peek_mode.patch
+ deleted file mode 100644
+-index 4aa7f53e..00000000
 ---- a/evidence/updatedifflog.md
--+++ b/evidence/updatedifflog.md
--@@ -1,44 +1,27 @@
---# Cycle Status: IN_PROGRESS
--+# Cycle Status: COMPLETE
-- 
-- ## Todo Ledger
---Planned:
---- [ ] Reproduce issue
---- [ ] Add debug logging
---- [ ] Analyze root cause
---- [ ] Fix issue
-- Completed:
---- [x] Reproduce issue
---- [x] Add debug logging
---Remaining:
---- [ ] Analyze root cause
---- [ ] Fix issue
--+- [x] Phase 0: Evidence + Location
--+- [x] Phase 1: Server: Pending Draft Storage
--+- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
--+- [x] Phase 3: Quality Gates
--+- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
--+- [x] Phase 6: Env Fix (OpenAI Key 401)
-- 
-- ## Next Action
---Analyze root cause of AuthenticationError
--+Stop and commit.
-- 
-- diff --git a/core/architect_brain.py b/core/architect_brain.py
---index a56669e3..ed5703a3 100644
--+index ed5703a3..a56669e3 100644
-- --- a/core/architect_brain.py
-- +++ b/core/architect_brain.py
-- @@ -462,7 +462,7 @@ class Architect:
--              return user_facing_response, agent_status
--  
--          except Exception as e:
----            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}")
---+            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}", exc_info=True)
---             # Return error message with default agent_status
---             return "Sorry, something went wrong planning that.", {
---                 "planner_active": False,
++index 551975b5..00000000
++--- a/build_docs/evidence/0dee2034_peek_mode.patch
+ +++ /dev/null
+-@@ -1,209 +0,0 @@
+--# Cycle Status: COMPLETE
+--
+--## Todo Ledger
+--Completed:
+--- [x] Phase A: UI Refactor (Remove dropdown, add pill)
+--- [x] Phase B: Wiring (Backend route exposure + Client routing pill)
+--
+--## Next Action
+--Commit
+--
+--diff --git a/api.py b/api.py
+--index 10d9e32d..0bbfbf5b 100644
+----- a/api.py
+--+++ b/api.py
+--@@ -5698,6 +5698,11 @@ def handle_message():
+--                          "roles_represented": list(set(m.get("role", "unknown") for m in companion_context))
+--                      }
+-- 
+--+                # Phase A/B: Expose Route
+--+                if "selected_route" not in payload:
+--+                    route_label = "Planner" if effective_channel == "planner" else "Chat"
+--+                    payload["selected_route"] = route_label
+--+
+--             return jsonify(payload)
+-- 
+--         logger.info(
 --diff --git a/core/architect_brain.py b/core/architect_brain.py
---index a56669e3..ed5703a3 100644
+--index ed5703a3..a56669e3 100644
 ----- a/core/architect_brain.py
 --+++ b/core/architect_brain.py
 --@@ -462,7 +462,7 @@ class Architect:
 --             return user_facing_response, agent_status
 -- 
 --         except Exception as e:
----            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}")
---+            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}", exc_info=True)
--+-            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}", exc_info=True)
--++            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}")
--              # Return error message with default agent_status
--              return "Sorry, something went wrong planning that.", {
--                  "planner_active": False,
--diff --git a/othello_ui.html b/othello_ui.html
--index d7bac5a0..bce50387 100644
----- a/othello_ui.html
--+++ b/othello_ui.html
--@@ -90,11 +90,6 @@
--         </div>
--         <div class="brand-subtitle" id="mode-subtitle">Personal Goal Architect</div>
--       </div>
---
---      <div class="status-pill">
---        <div class="dot"></div>
---        <span id="status">Online</span>
---      </div>
--     </header>
-- 
--     <!-- TAB NAVIGATION -->
--@@ -331,11 +326,10 @@
--     <div class="chat-sheet">
--       <div class="chat-sheet__header">
--         <div class="kitt-scanner" aria-hidden="true"></div>
---        <select id="chat-context-selector" class="chat-context-selector">
---          <option value="companion">Companion Chat</option>
---          <option value="planner">Daily Plan Engine</option>
---          <option value="routine">Routine Coach</option>
---        </select>
--+        <div id="chat-status-pill" class="status-pill" style="margin-right: auto;">
--+          <div class="dot"></div>
--+          <span id="chat-status-text">Online Ôö£├ÂÔö£├ºÔö£Ôöé Chat</span>
--+        </div>
--         <button id="chat-back-btn" class="chat-back-btn">├ö├Â┬úÔö£Ôòú</button>
--       </div>
-- 
--diff --git a/static/othello.js b/static/othello.js
--index 7d95718c..4978ae92 100644
----- a/static/othello.js
--+++ b/static/othello.js
--@@ -3581,20 +3581,33 @@
--     
--     // Connectivity State Management
--     function updateConnectivity(status, message = "") {
--+        console.debug(`[Connectivity] update: ${status} (msg: ${message})`);
--         othelloState.connectivity = status;
---        const pill = document.querySelector('.status-pill');
---        const text = pill ? pill.querySelector('#status') : null;
---        const dot = pill ? pill.querySelector('.dot') : null;
--+        const pill = document.getElementById('chat-status-pill');
--+        const text = document.getElementById('chat-status-text');
--+        
--+        // Provide route context if available, defaulting to "Chat"
--+        const route = othelloState.lastRoute || "Chat";
--         
--         if (text) {
---            if (status === 'online') text.textContent = "Online";
---            else if (status === 'offline') text.textContent = "Offline";
---            else if (status === 'degraded') text.textContent = message || "Degraded";
--+             if (status === 'online') {
--+                 text.textContent = `Online Ôö£├ÂÔö£├ºÔö£Ôöé ${route}`;
--+             } else if (status === 'thinking') {
--+                 text.textContent = `Thinking Ôö£├ÂÔö£├ºÔö£Ôöé ${route}`;
--+             } else if (status === 'offline') {
--+                 text.textContent = "Offline";
--+             } else if (status === 'degraded') {
--+                 text.textContent = message || "Degraded";
--+             } else {
--+                 text.textContent = status;
--+             }
--         }
--         
--         if (pill) {
---            pill.classList.remove('offline', 'degraded');
---            if (status !== 'online') pill.classList.add(status);
--+            pill.classList.remove('offline', 'degraded', 'thinking');
--+            if (status === 'offline') pill.classList.add('offline');
--+            if (status === 'degraded') pill.classList.add('degraded');
--+            if (status === 'thinking') pill.classList.add('thinking'); // Optional styling
--         }
--     }
-- 
--@@ -5791,11 +5804,15 @@
--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
--         pendingChatRequests++;
--         setChatThinking(true);
--+        updateConnectivity('thinking');
--     }
--     function endThinking() {
--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
--         pendingChatRequests = Math.max(0, pendingChatRequests - 1);
---        if (pendingChatRequests === 0) setChatThinking(false);
--+        if (pendingChatRequests === 0) {
--+            setChatThinking(false);
--+            updateConnectivity('online');
--+        }
--     }
-- 
--     async function sendMessage(overrideText = null, extraData = {}) {
--@@ -6088,6 +6105,14 @@
--                 const clone = res.clone();
--                 try {
--                     data = await res.json();
--+                    
--+                    // Route Pill Update (Phase A)
--+                    // If backend returns a route, update our state so the pill reflects it.
--+                    if (data && data.selected_route) {
--+                        othelloState.lastRoute = data.selected_route;
--+                        // Refresh immediately to show new route
--+                        updateConnectivity('online');
--+                    }
--                 } catch (parseErr) {
--                     let textBody = "";
--                     try { textBody = await clone.text(); } catch(e) {}
+---            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}", exc_info=True)
+--+            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£ÔöÉ├ö├Â┬úÔö¼┬¢ Architect failed: {e}")
+--             # Return error message with default agent_status
+--             return "Sorry, something went wrong planning that.", {
+--                 "planner_active": False,
++@@ -1 +0,0 @@
++-how --patch 0dee2034b678a748a98b0705ecbd2342a9194ad5
++diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++index 77ef230d..6e4e4ef9 100644
++--- a/evidence/updatedifflog.md
+++++ b/evidence/updatedifflog.md
++@@ -1,222 +1,77 @@
++-# Cycle Status: IN_PROGRESS
+++# Cycle Status: COMPLETE
++ 
++ ## Todo Ledger
+++Completed:
+++- [x] Phase 6: Consolidate Chat & Status (Global Pill Removal)
+++- [x] Phase 6: Fix client-side null textContent crash
+++- [x] Phase 6: Backend Auto-Routing Implementation
++ 
++ ## Next Action
++-Fill next action.
+++Stop and commit.
++ 
+ -diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+--index e80434ec..78b50369 100644
++-deleted file mode 100644
++-index 4aa7f53e..00000000
+ ---- a/evidence/updatedifflog.md
+--+++ b/evidence/updatedifflog.md
+--@@ -1,44 +1,27 @@
+---# Cycle Status: IN_PROGRESS
+--+# Cycle Status: COMPLETE
+-- 
+-- ## Todo Ledger
+---Planned:
+---- [ ] Reproduce issue
+---- [ ] Add debug logging
+---- [ ] Analyze root cause
+---- [ ] Fix issue
+-- Completed:
+---- [x] Reproduce issue
+---- [x] Add debug logging
+---Remaining:
+---- [ ] Analyze root cause
+---- [ ] Fix issue
+--+- [x] Phase 0: Evidence + Location
+--+- [x] Phase 1: Server: Pending Draft Storage
+--+- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
+--+- [x] Phase 3: Quality Gates
+--+- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
+--+- [x] Phase 6: Env Fix (OpenAI Key 401)
+-- 
+-- ## Next Action
+---Analyze root cause of AuthenticationError
+--+Stop and commit.
+-- 
+-- diff --git a/core/architect_brain.py b/core/architect_brain.py
+---index a56669e3..ed5703a3 100644
+--+index ed5703a3..a56669e3 100644
+-- --- a/core/architect_brain.py
+-- +++ b/core/architect_brain.py
+-- @@ -462,7 +462,7 @@ class Architect:
+--              return user_facing_response, agent_status
+--  
+--          except Exception as e:
+----            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}")
+---+            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}", exc_info=True)
+---             # Return error message with default agent_status
+---             return "Sorry, something went wrong planning that.", {
+---                 "planner_active": False,
++-+++ /dev/null
++-@@ -1,209 +0,0 @@
++--# Cycle Status: COMPLETE
++--
++--## Todo Ledger
++--Completed:
++--- [x] Phase A: UI Refactor (Remove dropdown, add pill)
++--- [x] Phase B: Wiring (Backend route exposure + Client routing pill)
++--
++--## Next Action
++--Commit
++--
++--diff --git a/api.py b/api.py
++--index 10d9e32d..0bbfbf5b 100644
++----- a/api.py
++--+++ b/api.py
++--@@ -5698,6 +5698,11 @@ def handle_message():
++--                          "roles_represented": list(set(m.get("role", "unknown") for m in companion_context))
++--                      }
++-- 
++--+                # Phase A/B: Expose Route
++--+                if "selected_route" not in payload:
++--+                    route_label = "Planner" if effective_channel == "planner" else "Chat"
++--+                    payload["selected_route"] = route_label
++--+
++--             return jsonify(payload)
++-- 
++--         logger.info(
+ --diff --git a/core/architect_brain.py b/core/architect_brain.py
+---index a56669e3..ed5703a3 100644
++--index ed5703a3..a56669e3 100644
+ ----- a/core/architect_brain.py
+ --+++ b/core/architect_brain.py
+ --@@ -462,7 +462,7 @@ class Architect:
+ --             return user_facing_response, agent_status
+ -- 
+ --         except Exception as e:
+----            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}")
+---+            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}", exc_info=True)
+--+-            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}", exc_info=True)
+--++            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}")
+--              # Return error message with default agent_status
+--              return "Sorry, something went wrong planning that.", {
+--                  "planner_active": False,
+--diff --git a/othello_ui.html b/othello_ui.html
+--index d7bac5a0..bce50387 100644
+----- a/othello_ui.html
+--+++ b/othello_ui.html
+--@@ -90,11 +90,6 @@
+--         </div>
+--         <div class="brand-subtitle" id="mode-subtitle">Personal Goal Architect</div>
+--       </div>
+---
+---      <div class="status-pill">
+---        <div class="dot"></div>
+---        <span id="status">Online</span>
+---      </div>
+--     </header>
+-- 
+--     <!-- TAB NAVIGATION -->
+--@@ -331,11 +326,10 @@
+--     <div class="chat-sheet">
+--       <div class="chat-sheet__header">
+--         <div class="kitt-scanner" aria-hidden="true"></div>
+---        <select id="chat-context-selector" class="chat-context-selector">
+---          <option value="companion">Companion Chat</option>
+---          <option value="planner">Daily Plan Engine</option>
+---          <option value="routine">Routine Coach</option>
+---        </select>
+--+        <div id="chat-status-pill" class="status-pill" style="margin-right: auto;">
+--+          <div class="dot"></div>
+--+          <span id="chat-status-text">Online ├ö├Â┬úÔö£├é├ö├Â┬úÔö£┬║├ö├Â┬ú├ö├Â├® Chat</span>
+--+        </div>
+--         <button id="chat-back-btn" class="chat-back-btn">Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├▓├║</button>
+--       </div>
+-- 
+--diff --git a/static/othello.js b/static/othello.js
+--index 7d95718c..4978ae92 100644
+----- a/static/othello.js
+--+++ b/static/othello.js
+--@@ -3581,20 +3581,33 @@
+--     
+--     // Connectivity State Management
+--     function updateConnectivity(status, message = "") {
+--+        console.debug(`[Connectivity] update: ${status} (msg: ${message})`);
+--         othelloState.connectivity = status;
+---        const pill = document.querySelector('.status-pill');
+---        const text = pill ? pill.querySelector('#status') : null;
+---        const dot = pill ? pill.querySelector('.dot') : null;
+--+        const pill = document.getElementById('chat-status-pill');
+--+        const text = document.getElementById('chat-status-text');
+--+        
+--+        // Provide route context if available, defaulting to "Chat"
+--+        const route = othelloState.lastRoute || "Chat";
+--         
+--         if (text) {
+---            if (status === 'online') text.textContent = "Online";
+---            else if (status === 'offline') text.textContent = "Offline";
+---            else if (status === 'degraded') text.textContent = message || "Degraded";
+--+             if (status === 'online') {
+--+                 text.textContent = `Online ├ö├Â┬úÔö£├é├ö├Â┬úÔö£┬║├ö├Â┬ú├ö├Â├® ${route}`;
+--+             } else if (status === 'thinking') {
+--+                 text.textContent = `Thinking ├ö├Â┬úÔö£├é├ö├Â┬úÔö£┬║├ö├Â┬ú├ö├Â├® ${route}`;
+--+             } else if (status === 'offline') {
+--+                 text.textContent = "Offline";
+--+             } else if (status === 'degraded') {
+--+                 text.textContent = message || "Degraded";
+--+             } else {
+--+                 text.textContent = status;
+--+             }
+--         }
+--         
+--         if (pill) {
+---            pill.classList.remove('offline', 'degraded');
+---            if (status !== 'online') pill.classList.add(status);
+--+            pill.classList.remove('offline', 'degraded', 'thinking');
+--+            if (status === 'offline') pill.classList.add('offline');
+--+            if (status === 'degraded') pill.classList.add('degraded');
+--+            if (status === 'thinking') pill.classList.add('thinking'); // Optional styling
+--         }
+--     }
+-- 
+--@@ -5791,11 +5804,15 @@
+--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
+--         pendingChatRequests++;
+--         setChatThinking(true);
+--+        updateConnectivity('thinking');
+--     }
+--     function endThinking() {
+--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
+--         pendingChatRequests = Math.max(0, pendingChatRequests - 1);
+---        if (pendingChatRequests === 0) setChatThinking(false);
+--+        if (pendingChatRequests === 0) {
+--+            setChatThinking(false);
+--+            updateConnectivity('online');
+--+        }
+--     }
+-- 
+--     async function sendMessage(overrideText = null, extraData = {}) {
+--@@ -6088,6 +6105,14 @@
+--                 const clone = res.clone();
+--                 try {
+--                     data = await res.json();
+--+                    
+--+                    // Route Pill Update (Phase A)
+--+                    // If backend returns a route, update our state so the pill reflects it.
+--+                    if (data && data.selected_route) {
+--+                        othelloState.lastRoute = data.selected_route;
+--+                        // Refresh immediately to show new route
+--+                        updateConnectivity('online');
+--+                    }
+--                 } catch (parseErr) {
+--                     let textBody = "";
+--                     try { textBody = await clone.text(); } catch(e) {}
++---            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}", exc_info=True)
++--+            self.logger.error(f"Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬ú├ö├Â├ëÔö£├ÂÔö£├éÔö¼├║├ö├Â┬╝Ôö¼┬ó Architect failed: {e}")
++--             # Return error message with default agent_status
++--             return "Sorry, something went wrong planning that.", {
++--                 "planner_active": False,
++--diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
++--index e80434ec..78b50369 100644
++----- a/evidence/updatedifflog.md
++--+++ b/evidence/updatedifflog.md
++--@@ -1,44 +1,27 @@
++---# Cycle Status: IN_PROGRESS
++--+# Cycle Status: COMPLETE
++-- 
++-- ## Todo Ledger
++---Planned:
++---- [ ] Reproduce issue
++---- [ ] Add debug logging
++---- [ ] Analyze root cause
++---- [ ] Fix issue
++-- Completed:
++---- [x] Reproduce issue
++---- [x] Add debug logging
++---Remaining:
++---- [ ] Analyze root cause
++---- [ ] Fix issue
++--+- [x] Phase 0: Evidence + Location
++--+- [x] Phase 1: Server: Pending Draft Storage
++--+- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
++--+- [x] Phase 3: Quality Gates
++--+- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
++--+- [x] Phase 6: Env Fix (OpenAI Key 401)
++-- 
++-- ## Next Action
++---Analyze root cause of AuthenticationError
++--+Stop and commit.
++-- 
++-- diff --git a/core/architect_brain.py b/core/architect_brain.py
++---index a56669e3..ed5703a3 100644
++--+index ed5703a3..a56669e3 100644
++-- --- a/core/architect_brain.py
++-- +++ b/core/architect_brain.py
++-- @@ -462,7 +462,7 @@ class Architect:
++--              return user_facing_response, agent_status
++--  
++--          except Exception as e:
++----            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}")
++---+            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}", exc_info=True)
++---             # Return error message with default agent_status
++---             return "Sorry, something went wrong planning that.", {
++---                 "planner_active": False,
++---diff --git a/core/architect_brain.py b/core/architect_brain.py
++---index a56669e3..ed5703a3 100644
++------ a/core/architect_brain.py
++---+++ b/core/architect_brain.py
++---@@ -462,7 +462,7 @@ class Architect:
++---             return user_facing_response, agent_status
++--- 
++---         except Exception as e:
++----            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}")
++---+            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}", exc_info=True)
++--+-            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}", exc_info=True)
++--++            self.logger.error(f"├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£┬«├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£├½├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼ÔòØ├ö├Â┬╝Ôö¼├│ Architect failed: {e}")
++--              # Return error message with default agent_status
++--              return "Sorry, something went wrong planning that.", {
++--                  "planner_active": False,
++--diff --git a/othello_ui.html b/othello_ui.html
++--index d7bac5a0..bce50387 100644
++----- a/othello_ui.html
++--+++ b/othello_ui.html
++--@@ -90,11 +90,6 @@
++--         </div>
++--         <div class="brand-subtitle" id="mode-subtitle">Personal Goal Architect</div>
++--       </div>
++---
++---      <div class="status-pill">
++---        <div class="dot"></div>
++---        <span id="status">Online</span>
++---      </div>
++--     </header>
++-- 
++--     <!-- TAB NAVIGATION -->
++--@@ -331,11 +326,10 @@
++--     <div class="chat-sheet">
++--       <div class="chat-sheet__header">
++--         <div class="kitt-scanner" aria-hidden="true"></div>
++---        <select id="chat-context-selector" class="chat-context-selector">
++---          <option value="companion">Companion Chat</option>
++---          <option value="planner">Daily Plan Engine</option>
++---          <option value="routine">Routine Coach</option>
++---        </select>
++--+        <div id="chat-status-pill" class="status-pill" style="margin-right: auto;">
++--+          <div class="dot"></div>
++--+          <span id="chat-status-text">Online Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö¼ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£┬« Chat</span>
++--+        </div>
++--         <button id="chat-back-btn" class="chat-back-btn">├ö├Â┬úÔö£├é├ö├Â┬úÔö£├®├ö├Â┬╝Ôö£ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£ÔûôÔö£Ôòæ</button>
++--       </div>
++-- 
++--diff --git a/static/othello.js b/static/othello.js
++--index 7d95718c..4978ae92 100644
++----- a/static/othello.js
++--+++ b/static/othello.js
++--@@ -3581,20 +3581,33 @@
++--     
++--     // Connectivity State Management
++--     function updateConnectivity(status, message = "") {
++--+        console.debug(`[Connectivity] update: ${status} (msg: ${message})`);
++--         othelloState.connectivity = status;
++---        const pill = document.querySelector('.status-pill');
++---        const text = pill ? pill.querySelector('#status') : null;
++---        const dot = pill ? pill.querySelector('.dot') : null;
++--+        const pill = document.getElementById('chat-status-pill');
++--+        const text = document.getElementById('chat-status-text');
++--+        
++--+        // Provide route context if available, defaulting to "Chat"
++--+        const route = othelloState.lastRoute || "Chat";
++--         
++--         if (text) {
++---            if (status === 'online') text.textContent = "Online";
++---            else if (status === 'offline') text.textContent = "Offline";
++---            else if (status === 'degraded') text.textContent = message || "Degraded";
++--+             if (status === 'online') {
++--+                 text.textContent = `Online Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö¼ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£┬« ${route}`;
++--+             } else if (status === 'thinking') {
++--+                 text.textContent = `Thinking Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö£├®Ôö£├ÂÔö£├éÔö¼├║├ö├Â┬úÔö¼ÔòæÔö£├ÂÔö£├éÔö¼├║Ôö£├ÂÔö£├éÔö£┬« ${route}`;
++--+             } else if (status === 'offline') {
++--+                 text.textContent = "Offline";
++--+             } else if (status === 'degraded') {
++--+                 text.textContent = message || "Degraded";
++--+             } else {
++--+                 text.textContent = status;
++--+             }
++--         }
++--         
++--         if (pill) {
++---            pill.classList.remove('offline', 'degraded');
++---            if (status !== 'online') pill.classList.add(status);
++--+            pill.classList.remove('offline', 'degraded', 'thinking');
++--+            if (status === 'offline') pill.classList.add('offline');
++--+            if (status === 'degraded') pill.classList.add('degraded');
++--+            if (status === 'thinking') pill.classList.add('thinking'); // Optional styling
++--         }
++--     }
++-- 
++--@@ -5791,11 +5804,15 @@
++--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
++--         pendingChatRequests++;
++--         setChatThinking(true);
++--+        updateConnectivity('thinking');
++--     }
++--     function endThinking() {
++--         if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
++--         pendingChatRequests = Math.max(0, pendingChatRequests - 1);
++---        if (pendingChatRequests === 0) setChatThinking(false);
++--+        if (pendingChatRequests === 0) {
++--+            setChatThinking(false);
++--+            updateConnectivity('online');
++--+        }
++--     }
++-- 
++--     async function sendMessage(overrideText = null, extraData = {}) {
++--@@ -6088,6 +6105,14 @@
++--                 const clone = res.clone();
++--                 try {
++--                     data = await res.json();
++--+                    
++--+                    // Route Pill Update (Phase A)
++--+                    // If backend returns a route, update our state so the pill reflects it.
++--+                    if (data && data.selected_route) {
++--+                        othelloState.lastRoute = data.selected_route;
++--+                        // Refresh immediately to show new route
++--+                        updateConnectivity('online');
++--+                    }
++--                 } catch (parseErr) {
++--                     let textBody = "";
++--                     try { textBody = await clone.text(); } catch(e) {}
+++diff --git a/api.py b/api.py
+++index 0bbfbf5b..f5a0f261 100644
+++--- a/api.py
++++++ b/api.py
+++@@ -4323,10 +4323,24 @@ def handle_message():
+++         current_view = data.get("current_view")
+++         raw_channel = data.get("channel")
+++         view_label = str(current_view or "chat")
+++-        is_chat_view = view_label.strip().lower() == "chat"
+++-        incoming_channel = str(raw_channel or "").strip().lower() or None
+++-        effective_channel = "companion" if is_chat_view else (incoming_channel or "companion")
+++-        if effective_channel not in {"companion", "planner"}:
++++        
++++        # Phase 6: True Auto Routing (Content-based)
++++        incoming_channel = str(raw_channel or "").strip().lower()
++++        if incoming_channel == "auto" or not incoming_channel:
++++            # Simple heuristic routing
++++            txt_lower = user_input.lower()
++++            planner_keywords = {"plan", "schedule", "routine", "calendar", "agenda", "today", "tomorrow", "week"}
++++            # If explicit goal focus, prefer companion unless explicitly asking about plan
++++            has_goal_focus = raw_goal_id is not None
++++            if has_goal_focus:
++++                effective_channel = "companion"
++++            elif any(k in txt_lower for k in planner_keywords):
++++                effective_channel = "planner"
++++            else:
++++                effective_channel = "companion"
++++        elif incoming_channel in {"companion", "planner"}:
++++            effective_channel = incoming_channel
++++        else:
+++             effective_channel = "companion"
+++         raw_client_message_id = data.get("client_message_id")
+++         if raw_client_message_id is None:
+++diff --git a/static/othello.js b/static/othello.js
+++index 4978ae92..a4227fef 100644
+++--- a/static/othello.js
++++++ b/static/othello.js
+++@@ -794,7 +794,8 @@
+++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+++ 
+++     const chatLog = document.getElementById('chat-log');
+++-    const statusEl = document.getElementById('status');
++++    // Relocated status to chat header (Phase 6 Fix)
++++    const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+++     const modeLabel = document.getElementById('current-mode-label');
+++     const modeSubtitle = document.getElementById('mode-subtitle');
+++     const plannerTabBadge = document.getElementById('planner-tab-badge');
+++@@ -6019,7 +6020,8 @@
+++         }
+++ 
+++         const mode = (othelloState.currentMode || "companion").toLowerCase();
+++-        const channel = mode === "companion" ? "companion" : "planner";
++++        // Phase 6: Auto-routing (backend decides, avoids forced planner)
++++        const channel = "auto";
+++         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
+++         console.log("[Othello UI] Sending plain-message payload:", text);
+++         
+++@@ -9216,7 +9218,7 @@
+++ 
+++ // Phase 4: Hook scanner to existing status
+++ (function() {
+++-  const statusEl = document.getElementById('status');
++++  const statusEl = document.getElementById('chat-status-text');
+++   // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
+++   // We need to wait for DOM maybe? No, script is at end of body.
+++   const chatSheet = document.querySelector('.chat-sheet');
++diff --git a/static/othello.js b/static/othello.js
++index 4978ae92..a4227fef 100644
++--- a/static/othello.js
+++++ b/static/othello.js
++@@ -794,7 +794,8 @@
++     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
++ 
++     const chatLog = document.getElementById('chat-log');
++-    const statusEl = document.getElementById('status');
+++    // Relocated status to chat header (Phase 6 Fix)
+++    const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
++     const modeLabel = document.getElementById('current-mode-label');
++     const modeSubtitle = document.getElementById('mode-subtitle');
++     const plannerTabBadge = document.getElementById('planner-tab-badge');
++@@ -6019,7 +6020,8 @@
++         }
++ 
++         const mode = (othelloState.currentMode || "companion").toLowerCase();
++-        const channel = mode === "companion" ? "companion" : "planner";
+++        // Phase 6: Auto-routing (backend decides, avoids forced planner)
+++        const channel = "auto";
++         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
++         console.log("[Othello UI] Sending plain-message payload:", text);
++         
++@@ -9216,7 +9218,7 @@
++ 
++ // Phase 4: Hook scanner to existing status
++ (function() {
++-  const statusEl = document.getElementById('status');
+++  const statusEl = document.getElementById('chat-status-text');
++   // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
++   // We need to wait for DOM maybe? No, script is at end of body.
++   const chatSheet = document.querySelector('.chat-sheet');
+diff --git a/static/othello.js b/static/othello.js
+index 4978ae92..a4227fef 100644
+--- a/static/othello.js
++++ b/static/othello.js
+@@ -794,7 +794,8 @@
+     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
+ 
+     const chatLog = document.getElementById('chat-log');
+-    const statusEl = document.getElementById('status');
++    // Relocated status to chat header (Phase 6 Fix)
++    const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
+     const modeLabel = document.getElementById('current-mode-label');
+     const modeSubtitle = document.getElementById('mode-subtitle');
+     const plannerTabBadge = document.getElementById('planner-tab-badge');
+@@ -6019,7 +6020,8 @@
+         }
+ 
+         const mode = (othelloState.currentMode || "companion").toLowerCase();
+-        const channel = mode === "companion" ? "companion" : "planner";
++        // Phase 6: Auto-routing (backend decides, avoids forced planner)
++        const channel = "auto";
+         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
+         console.log("[Othello UI] Sending plain-message payload:", text);
+         
+@@ -9216,7 +9218,7 @@
+ 
+ // Phase 4: Hook scanner to existing status
+ (function() {
+-  const statusEl = document.getElementById('status');
++  const statusEl = document.getElementById('chat-status-text');
+   // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
+   // We need to wait for DOM maybe? No, script is at end of body.
+   const chatSheet = document.querySelector('.chat-sheet');
diff --git a/static/othello.js b/static/othello.js
index 4978ae92..a4227fef 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -794,7 +794,8 @@
     const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };
 
     const chatLog = document.getElementById('chat-log');
-    const statusEl = document.getElementById('status');
+    // Relocated status to chat header (Phase 6 Fix)
+    const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
     const modeLabel = document.getElementById('current-mode-label');
     const modeSubtitle = document.getElementById('mode-subtitle');
     const plannerTabBadge = document.getElementById('planner-tab-badge');
@@ -6019,7 +6020,8 @@
         }
 
         const mode = (othelloState.currentMode || "companion").toLowerCase();
-        const channel = mode === "companion" ? "companion" : "planner";
+        // Phase 6: Auto-routing (backend decides, avoids forced planner)
+        const channel = "auto";
         console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
         console.log("[Othello UI] Sending plain-message payload:", text);
         
@@ -9216,7 +9218,7 @@
 
 // Phase 4: Hook scanner to existing status
 (function() {
-  const statusEl = document.getElementById('status');
+  const statusEl = document.getElementById('chat-status-text');
   // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
   // We need to wait for DOM maybe? No, script is at end of body.
   const chatSheet = document.querySelector('.chat-sheet');
