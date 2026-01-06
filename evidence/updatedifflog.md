# Cycle Status: COMPLETE (Phase 21 - Draft Refactor)

## Todo Ledger
Planned:
- [x] Stop auto-draft creation in DB (Keep UI metadata).
- [x] Implement ui_action="create_goal_from_message".
- [x] Wire UI question-mark to "create_goal_from_message".
- [x] Remove drafts from GOALS list.
- [x] Add "clear_pending_drafts" action.
Completed:
- [x] api.py: _attach_goal_intent_suggestion now returns 'virtual' suggestion metdata, no DB row created.
- [x] api.py: Included payload in virtual suggestion so UI can re-submit it.
- [x] api.py: Added ui_action handler for direct goal creation + focus.
- [x] api.py: Updated prompt to be less eager ("1-2 starting steps").
- [x] api.py: Added "clear_pending_drafts".
- [x] otello.js: createGoalFromSuggestion uses sendMessage instead of fetch.
- [x] db_goal_manager.py: list_goals no longer merges drafts.
Remaining:
- [ ] Phase 22 tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 95dd8d41..bdd45340 100644
--- a/api.py
+++ b/api.py
@@ -1120,7 +1120,7 @@ def _generate_goal_draft_payload(user_input: str) -> Dict[s
tr, Any]:                                                                                 "Required keys:\n"
         "- title: string (concise goal title)\n"
         "- target_days: integer or null (number of days to achieve)\n"
-        "- steps: array of strings (actionable steps)\n"
+        "- steps: array of strings (actionable steps) - keep these high-level an
d few (3-5 max). If the user request is vague, provide only 1-2 starting steps.\n"                                                                                         "- body: string or null (additional context/description)\n"
         "Return ONLY valid JSON."
     )
@@ -1818,59 +1818,32 @@ def _attach_goal_intent_suggestion(
         if is_vague:
             logger.info("API: Goal intent detected but input is vague (%d chars). Skipping automatic drafting.", len(raw_text))
             return False

-        # Phase 21: Generating full draft immediately to persist seed steps
-        draft_payload = _generate_goal_draft_payload(raw_text)
-        
-        # Ensure title fallback
-        if not draft_payload.get("title"):
-             draft_payload["title"] = suggestion.get("title_suggestion") or _extract_goal_title_suggestion(raw_text) or "New Goal"
-
-        payload = draft_payload
-        payload["description"] = payload.get("body")
-        payload["confidence"] = suggestion.get("confidence")
-        
-        title = payload["title"] # Required for deduplication below
-
-        provenance = {
-            "source": "api_message_goal_intent",
-            "request_id": request_id,
-            "client_message_id": client_message_id,
-        }
-        
-        # Deduplication: check for existing pending goal suggestions with same title
-        existing_dup = None
-        try:
-            pending_goals = suggestions_repository.list_suggestions(user_id=user_id, kind="goal", status="pending")
-            norm_title = (title or "").strip().lower()
-            for p in pending_goals:
-                p_payload = p.get("payload") or {}
-                p_title = (p_payload.get("title") or "").strip().lower()
-                if p_title == norm_title:
-                    existing_dup = p
-                    break
-        except Exception:
-            pass
-
-        try:
-            if existing_dup:
-                created = existing_dup
-                logger.info("API: Returning existing draft for duplicate title '%s'", title)
-            else:
-                created = suggestions_repository.create_suggestion(
-                    user_id=user_id,
-                    kind="goal",
-                    payload=payload,
-                    provenance=provenance,
-                )
-            if isinstance(created, dict):
-                suggestion_id = created.get("id")
-        except Exception:
-            logger.warning(
-                "API: goal suggestion create failed request_id=%s client_message_id=%s",
-                request_id,
-                client_message_id,
-                exc_info=True,
-            )
+        # Phase 21: No-Persistence "Goal Candidate" (Voice-First)
+        # We do NOT create a draft in the DB. We just return metadata so the UI can show the ? marker.
+        # When confirmed, the UI will call create_goal_from_message.
+        
+        draft_payload = _generate_goal_draft_payload(raw_text)
+        title = draft_payload.get("title") or suggestion.get("title_suggestion") or _extract_goal_title_suggestion(raw_text) or "New Goal"
+        body = draft_payload.get("body") or suggestion.get("body_suggestion") or raw_text
+        
+        # Virtual Suggestion (No ID, Not in DB)
+        # We attach this to the response so the UI knows to offer "Create Goal"
+        # The 'suggestion_id' is deliberately None.
+        suggestion_data = {
+            "title_suggestion": title,
+            "body_suggestion": body,
+            "confidence": suggestion.get("confidence"),
+            "client_message_id": client_message_id,
+            "is_virtual": True,
+            # Pass full payload for the UI to use if it wants
+            "payload": draft_payload
+        }
+        
+        # We modify the suggestion dict passed by reference so the caller can inject it into meta
+        suggestion.update(suggestion_data)
+        
+        return True
+
     if suggestion_id is not None:
         suggestion = dict(suggestion)
         suggestion["suggestion_id"] = suggestion_id
@@ -4294,6 +4267,53 @@ def handle_message():
                 return user_error
             user_id = None
 
+        # Phase 21: Manual Create Goal (Voice-First Confirmation)
+        if user_id and ui_action == "create_goal_from_message":
+             source_message_id = data.get("source_message_id")
+             override_title = data.get("title")
+             override_desc = data.get("description")
+             
+             final_title = (override_title or "New Goal").strip()
+             final_body = (override_desc or "").strip()
+             final_steps = []
+             
+             try:
+                 # If we have a payload passed (e.g. from the virtual suggestion on client), use it
+                 passed_payload = data.get("payload")
+                 if isinstance(passed_payload, dict):
+                     final_title = passed_payload.get("title") or final_title
+                     final_body = passed_payload.get("body") or final_body
+                     final_steps = passed_payload.get("steps") or []
+                 
+                 # Create the goal
+                 goal_id = goals_repository.create_goal(
+                     user_id=user_id,
+                     title=final_title,
+                     description=final_body,
+                     target_days=None 
+                 )
+                 
+                 # Add steps if present
+                 if goal_id and final_steps:
+                     for step in final_steps:
+                         goals_repository.add_goal_step(user_id, goal_id, str(step))
+                         
+                 return jsonify({
+                     "reply": f"Goal '{final_title}' created.",
+                     "goal_id": goal_id,
+                     "ui_action_call": "focus_goal",
+                     "ui_action_payload": {"goal_id": goal_id},
+                     "redirect_to": f"/goals/{goal_id}", 
+                     "agent_status": {"planner_active": True},
+                     "request_id": request_id
+                 })
+             except Exception as e:
+                 logger.error("Failed to create goal from message: %s", e)
+                 return jsonify({
+                     "reply": "I couldn't create the goal right now.",
+                     "request_id": request_id
+                 })
+
         # Draft Focus: Confirm Goal Intent
         # Tightened routing:
         # A) data.ui_action == "confirm_draft"
@@ -4437,6 +4457,29 @@ def handle_message():
                 "request_id": request_id
             })
 
+        # Phase 21: Danger Zone - Clear All Pending Drafts
+        if user_id and data.get("ui_action") == "clear_pending_drafts":
+            try:
+                # Assuming simple SQL delete via direct connection or repo method if exists.
+                # Repo doesn't have delete_all, so we might iterate or use raw SQL.
+                # Let's iterate for safety/audit (though slower).
+                pending = suggestions_repository.list_suggestions(user_id, status="pending", kind="goal")
+                count = 0
+                for p in pending:
+                    suggestions_repository.update_suggestion_status(user_id, p["id"], "dismissed", decided_reason="user_clear_all")
+                    count += 1
+                return jsonify({
+                    "reply": f"Cleared {count} pending drafts.",
+                    "cleared_count": count,
+                    "request_id": request_id
+                })
+            except Exception as e:
+                logger.error("Failed to clear drafts: %s", e)
+                return jsonify({
+                    "reply": "Failed to clear drafts.",
+                    "request_id": request_id
+                })
+
         # Draft Focus: Create Draft (Voice-First)
         # Trigger: "create a goal draft", "start a goal draft", etc.
         is_create_draft = False
diff --git a/db/db_goal_manager.py b/db/db_goal_manager.py
index f4e7c4a1..e49b5d31 100644
--- a/db/db_goal_manager.py
+++ b/db/db_goal_manager.py
@@ -237,10 +237,11 @@ class DbGoalManager:
 
     def list_goals(self, user_id: str) -> List[Dict[str, Any]]:
         """
-        Return all goals for the default user in legacy format, PLUS pending drafts.
+        Return all goals for the default user in legacy format.
+        (Phase 21: Drafts are no longer mixed in.)
         """
         uid = self._require_user_id(user_id)
-        
+
         # 1. Fetch real goals
         db_goals = goals_repository.list_goals(uid, include_archived=False)
         goals = [
@@ -248,31 +249,7 @@ class DbGoalManager:
             for g in db_goals
         ]
 
-        # 2. Fetch pending goal drafts
-        drafts = suggestions_repository.list_suggestions(
-            user_id=uid, status="pending", kind="goal"
-        )
-        
-        draft_entries = []
-        for d in drafts:
-            payload = d.get("payload") or {}
-            # Ensure it looks like a goal so the UI renders it
-            # We prefix ID with 'draft:' so UI can distinguish action clicks
-            created_at_val = d.get("created_at")
-            created_at_str = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val or "")
-            
-            draft_entries.append({
-                "id": f"draft:{d['id']}",
-                "text": payload.get("title") or "New Draft",
-                "deadline": f"{payload.get('target_days', 7)} days",
-                "created_at": created_at_str,
-                "draft_text": payload.get("body"), # Show body as draft text
-                "checklist": payload.get("steps", []),
-                "is_draft": True,
-                "real_draft_id": d["id"]
-            })
-
-        return draft_entries + goals
+        return goals
 
     def get_goal(
         self,
diff --git a/static/othello.js b/static/othello.js
index 98182d46..7521f134 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4574,7 +4574,7 @@
     }
 
     async function createGoalFromSuggestion(opts) {
-      const { title, description, clientMessageId, statusEl, panelEl, onSuccess, suggestionId } = opts;
+      const { title, description, clientMessageId, statusEl, panelEl, onSuccess, suggestionId, payload } = opts;
       const trimmedTitle = (title || "").trim();
       const trimmedDesc = (description || "").trim();
       if (trimmedTitle.length < 3) {
@@ -4584,79 +4584,35 @@
       disablePanelButtons(panelEl, true);
       if (statusEl) statusEl.textContent = "Saving goal...";
       try {
-        let goal = null;
-        let goalId = null;
-        if (suggestionId) {
-          const payload = await v1Request(
-            `/v1/suggestions/${suggestionId}/accept`,
-            {
-              method: "POST",
-              headers: {"Content-Type": "application/json"},
-              credentials: "include",
-              body: JSON.stringify({
-                reason: "confirm",
-                payload: {
-                  title: trimmedTitle,
-                  body: trimmedDesc,
-                  description: trimmedDesc
-                }
-              })
-            },
-            "Confirm goal suggestion"
-          );
-          const results = payload && payload.data && Array.isArray(payload.data.results)
-            ? payload.data.results
-            : [];
-          const result = results[0] || null;
-          goal = result && result.goal ? result.goal : null;
-          goalId = goal && typeof goal.id === "number" ? goal.id : null;
-        } else {
-          const res = await fetch(GOALS_API, {
-            method: "POST",
-            headers: {"Content-Type": "application/json"},
-            credentials: "include",
-            body: JSON.stringify({
-              title: trimmedTitle,
-              description: trimmedDesc,
-              source_client_message_id: clientMessageId
-            })
-          });
-          if (!res.ok) {
-            const contentType = res.headers.get("content-type") || "";
-            let errMsg = "Unable to create goal.";
-            if (contentType.includes("application/json")) {
-              const data = await res.json();
-              errMsg = (data && (data.message || data.error)) || errMsg;
-            }
-            if (statusEl) statusEl.textContent = errMsg;
-            disablePanelButtons(panelEl, false);
-            return false;
-          }
-          const data = await res.json();
-          goal = data && data.goal ? data.goal : null;
-          goalId = goal && typeof goal.id === "number" ? goal.id : data.goal_id;
-        }
-        clearGoalIntentUI(clientMessageId);
-        showToast("Saved as goal");
-        await refreshGoals();
-        if (goalId != null) {
-          setActiveGoal(goalId);
-          if (typeof onSuccess === "function") {
-            await onSuccess(goalId);
-          }
-          if (othelloState.currentView === "goals") {
-            showGoalDetail(goalId);
-          }
+        // Phase 21: Direct Chat Action (No v1/create)
+        // If it's a virtual suggestion (no real ID) or even if it is, we prefer the chat action route
+        // to keep the conversation in sync.
+        
+        // Use global sendMessage if available (it should be)
+        if (typeof sendMessage === 'function') {
+             await sendMessage("", {
+                 ui_action: "create_goal_from_message",
+                 source_message_id: clientMessageId,
+                 title: trimmedTitle,
+                 description: trimmedDesc,
+                 payload: payload || (othelloState.goalIntentSuggestions[clientMessageId] ? othelloState.goalIntentSuggestions[clientMessageId].payload : null)
+             });
+             // The API will return 'focus_goal' action which we handle in socket message
+             return true;
         }
-        return true;
-      } catch (err) {
-        console.error("[Othello UI] create goal failed:", err);
-        if (statusEl) statusEl.textContent = err && err.message ? err.message : "Network error.";
+
+        // Fallback (shouldn't be reached in normal flow)
+        console.warn("sendMessage not found, falling back to legacy create");
+        return false;
+      } catch (e) {
+        console.error("Failed to create goal", e);
+        if (statusEl) statusEl.textContent = "Error saving goal.";
         disablePanelButtons(panelEl, false);
         return false;
       }
     }


```
