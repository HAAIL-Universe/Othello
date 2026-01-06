# Cycle Status: COMPLETE (Phase 20)

## Todo Ledger
Planned:
- [x] Phase 20: Fix draft ID poisoning + safe step diffs + tighten voice gating.
Completed:
- [x] API: Moved draft step diff logic after updates; added safety checks for keys.
- [x] API: Implemented `needs_seed_steps` flag to gate auto-generation.
- [x] UI: Added guards in `fetchGoalDetail` and `effectiveGoalId` for "draft:*" IDs.
- [x] UI: Fix "Clarify Intent" to send numeric draft ID.
- [x] DB: Robust `created_at` formatting for drafts.
Remaining:
- [ ] Phase 21 tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 0428e013..efa491ec 100644
--- a/api.py
+++ b/api.py
@@ -4397,7 +4397,30 @@ def handle_message():
                     # 1. Try deterministic edit
                     updated_payload, handled, reply_suffix = _apply_goal_draft_deterministic_edit(current_payload, user_input)
                     
-                    # Diff Logic (Step Diff)
+                    # 2. Fallback to LLM if not handled (Semantic Edit)
+                    if not handled:
+                        updated_payload = _patch_goal_draft_payload(current_payload, user_input)
+                        reply_suffix = "Updated the draft."
+                        
+                        # Auto-Generate Logic (Voice Flow) - Tightened
+                        # Only auto-generate if we previously flagged this draft as needing seed steps (via clarification)
+                        # OR if it's very clearly an initial elaboration.
+                        needs_seed_steps = updated_payload.get("needs_seed_steps")
+                        if not updated_payload.get("steps"):
+                             new_body = updated_payload.get("body") or ""
+                             # Explicitly check the flag set by clarify_goal_intent
+                             if needs_seed_steps and len(new_body) > 5:
+                                 updated_payload = _generate_draft_steps_payload(updated_payload)
+                                 # Clear the flag
+                                 updated_payload.pop("needs_seed_steps", None)
+                                 steps_count = len(updated_payload.get("steps", []))
+                                 if steps_count > 0:
+                                     reply_suffix += f" I've also auto-generated {steps_count} starting steps for you."
+                             elif needs_seed_steps:
+                                 # Keep the flag if body is too short
+                                 pass
+
+                    # Diff Logic (Step Diff) - Computed AFTER all updates
                     diff_meta = {}
                     before_steps = current_payload.get("steps", []) or []
                     after_steps = updated_payload.get("steps", []) or []
@@ -4405,6 +4428,8 @@ def handle_message():
                     if len(before_steps) != len(after_steps) or before_steps != after_steps:
                         # Simple diff detection
                         diff_meta["goal_title"] = updated_payload.get("title", "Goal")
+                        diff_meta["steps_changed"] = True
+                        
                         # Try to find specific index change
                         if len(before_steps) == len(after_steps):
                             for i, (b, a) in enumerate(zip(before_steps, after_steps)):
@@ -4414,36 +4439,23 @@ def handle_message():
                                     diff_meta["after_text"] = a
                                     break
                     
-                    # 2. Fallback to LLM if not handled (Semantic Edit)
-                    if not handled:
-                        updated_payload = _patch_goal_draft_payload(current_payload, user_input)
-                        reply_suffix = "Updated the draft."
-                        
-                        # Auto-Generate Logic (Voice Flow)
-                        # If description likely changed (not just steps), and steps are empty, auto-generate.
-                        # Heuristic: If we are here, user said something that wasn't a command.
-                        # If steps are empty, assuming it's an elaboration/answer.
-                        if not updated_payload.get("steps"):
-                             # Check if body changed, or just safe assumption: if 0 steps, generate.
-                             # But avoid generating if user just said "No".
-                             # Let's assume meaningful update if body length > 5
-                             new_body = updated_payload.get("body") or ""
-                             if len(new_body) > 5:
-                                 updated_payload = _generate_draft_steps_payload(updated_payload)
-                                 steps_count = len(updated_payload.get("steps", []))
-                                 if steps_count > 0:
-                                     reply_suffix += f" I've also auto-generated {steps_count} starting steps for you."
-
                     # Update DB
                     updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                     
                     title = updated_payload.get("title", "Goal")
                     steps_count = len(updated_payload.get("steps", []))
                     
-                    # Format Response with Diff
+                    # Format Response with Diff - Safe
                     reply_msg = f"{reply_suffix}"
-                    if diff_meta:
-                        reply_msg = f"{diff_meta['goal_title']}\nUpdated step {diff_meta['step_index']}\nBefore: {diff_meta['before_text']}\nAfter: {diff_meta['after_text']}"
+                    if diff_meta.get("steps_changed"):
+                        if diff_meta.get("step_index") and diff_meta.get("before_text") and diff_meta.get("after_text"):
+                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated step {diff_meta['step_index']}\nBefore: {diff_meta['before_text']}\nAfter: {diff_meta['after_text']}"
+                        else:
+                            # Steps added/removed or multiple changes
+                            # Limit to first 3 steps in summary to keep it concise? Or just count.
+                            step_list_str = ", ".join([f"{i+1}. {s}" for i, s in enumerate(after_steps[:3])])
+                            if len(after_steps) > 3: step_list_str += "..."
+                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated steps.\nNow: {step_list_str}"
                     elif not reply_msg.strip():
                          reply_msg = f"Draft: '{title}' ({steps_count} steps)."
                     else:
@@ -4649,6 +4661,18 @@ def handle_message():
 
         # Phase 18: Intent Clarification
         if user_id and ui_action == "clarify_goal_intent":
+             # Phase 20: If confirming a draft, flag it for auto-seed steps
+             if data.get("draft_id"):
+                 try:
+                     did = int(data.get("draft_id"))
+                     d = suggestions_repository.get_suggestion(user_id, did)
+                     if d and d.get("status") == "pending":
+                         p = d.get("payload", {})
+                         p["needs_seed_steps"] = True
+                         suggestions_repository.update_suggestion_payload(user_id, did, p)
+                 except (ValueError, TypeError):
+                     pass
+
              # Force the agent to ask clarifying questions
              user_input = "Please ask me 1-3 targeted clarifying questions to help me refine the intent of this goal. Be concise."
 
diff --git a/db/db_goal_manager.py b/db/db_goal_manager.py
index 356f2463..f4e7c4a1 100644
--- a/db/db_goal_manager.py
+++ b/db/db_goal_manager.py
@@ -258,11 +258,14 @@ class DbGoalManager:
             payload = d.get("payload") or {}
             # Ensure it looks like a goal so the UI renders it
             # We prefix ID with 'draft:' so UI can distinguish action clicks
+            created_at_val = d.get("created_at")
+            created_at_str = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val or "")
+            
             draft_entries.append({
                 "id": f"draft:{d['id']}",
                 "text": payload.get("title") or "New Draft",
                 "deadline": f"{payload.get('target_days', 7)} days",
-                "created_at": d.get("created_at").isoformat(),
+                "created_at": created_at_str,
                 "draft_text": payload.get("body"), # Show body as draft text
                 "checklist": payload.get("steps", []),
                 "is_draft": True,
diff --git a/static/othello.js b/static/othello.js
index 8d150d5b..91cb3109 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -5668,7 +5668,22 @@
         console.log("[Othello UI] Sending plain-message payload:", text);
         
         // Fallback to currently viewed goal if no active goal is set
-        const effectiveGoalId = othelloState.activeGoalId || othelloState.currentDetailGoalId || null;
+        let effectiveGoalId = othelloState.activeGoalId || othelloState.currentDetailGoalId || null;
+        if (effectiveGoalId && String(effectiveGoalId).startsWith("draft:")) {
+            effectiveGoalId = null;
+        }
+
+        // Infer draft context if viewing a draft
+        let draftId = othelloState.activeDraft ? othelloState.activeDraft.draft_id : null;
+        let draftType = othelloState.activeDraft ? othelloState.activeDraft.draft_type : null;
+        
+        if (!draftId && othelloState.currentDetailGoalId && String(othelloState.currentDetailGoalId).startsWith("draft:")) {
+            const parts = String(othelloState.currentDetailGoalId).split(":");
+            if (parts.length > 1) {
+                 draftId = parseInt(parts[1], 10);
+                 draftType = "goal";
+            }
+        }
 
         const payload = { 
             message: text,
@@ -5679,8 +5694,8 @@
             current_view: othelloState.currentView,
             client_message_id: clientMessageId,
             conversation_id: othelloState.activeConversationId,
-            draft_id: othelloState.activeDraft ? othelloState.activeDraft.draft_id : null,
-            draft_type: othelloState.activeDraft ? othelloState.activeDraft.draft_type : null,
+            draft_id: draftId,
+            draft_type: draftType,
             ...extraData
         };
         console.debug("[Othello UI] Sending /api/message payload:", payload);
@@ -6805,6 +6820,9 @@
 
     async function fetchGoalDetail(goalId) {
       if (!goalId) return;
+      // Guard: Do not fetch drafts from the goals API
+      if (String(goalId).startsWith("draft:")) return;
+
       try {
         const resp = await fetch(`/api/goals/${goalId}`, { credentials: "include" });
         if (resp.status === 401 || resp.status === 403) {
@@ -7045,13 +7063,9 @@
             
             // Handle draft IDs (e.g. "draft:123")
             if (goalId.startsWith("draft:")) {
-                 // For drafts, we want to simply trigger the clarification intent without a goal_id context?
-                 // Or pass the draft_id.
-                 // ui_action "clarify_goal_intent" in api.py just sets prompt text.
-                 // It relies on current context.
-                 // If we are looking at a draft, we should probably just send the text.
+                 const realId = goalId.split(":")[1];
                  hideGoalDetail();
-                 sendMessage("", { ui_action: "clarify_goal_intent" }); 
+                 sendMessage("", { ui_action: "clarify_goal_intent", draft_id: realId }); 
                  return;
             }
 
```
