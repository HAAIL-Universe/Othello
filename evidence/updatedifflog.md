# Cycle Status: COMPLETE (Phase 21)

## Todo Ledger
Planned:
- [x] Phase 21: Voice-first draft polish + Ribbon UI Fix.
Completed:
- [x] API: Deterministic "Show Steps" router (supports drafts + goals, prevents LLM calls).
- [x] API: Voice-friendly replies for auto-gen steps ("Got it. Here are...") and edits.
- [x] UI: Fixed "Drafting Goal" ribbon layout (removed fixed height, added wrap, overflow visible).
Remaining:
- [ ] Phase 22 tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index efa491ec..61120cb0 100644
--- a/api.py
+++ b/api.py
@@ -4415,7 +4415,9 @@ def handle_message():
                                  updated_payload.pop("needs_seed_steps", None)
                                  steps_count = len(updated_payload.get("steps", []))
                                  if steps_count > 0:
-                                     reply_suffix += f" I've also auto-generated {steps_count} starting steps for you."
+                                     # Conversational reply for auto-gen
+                                     step_preview = "\n".join([f"{i+1}) {s}" for i, s in enumerate(updated_payload.get("steps", [])[:5])])
+                                     reply_suffix = f"Got it. Here are {steps_count} starting steps:\n{step_preview}\n\nWant to tweak any step, or should I save this goal?"
                              elif needs_seed_steps:
                                  # Keep the flag if body is too short
                                  pass
@@ -4445,17 +4447,22 @@ def handle_message():
                     title = updated_payload.get("title", "Goal")
                     steps_count = len(updated_payload.get("steps", []))
                     
-                    # Format Response with Diff - Safe
+                    # Format Response with Diff - Voice Friendly
                     reply_msg = f"{reply_suffix}"
-                    if diff_meta.get("steps_changed"):
+                    if "Got it. Here are" in reply_suffix:
+                         # Use the conversational auto-gen message directly
+                         reply_msg = reply_suffix
+                    elif diff_meta.get("steps_changed"):
                         if diff_meta.get("step_index") and diff_meta.get("before_text") and diff_meta.get("after_text"):
-                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated step {diff_meta['step_index']}\nBefore: {diff_meta['before_text']}\nAfter: {diff_meta['after_text']}"
+                            # Phrase: "<Goal title>. I updated step X. It was: '...'. Now it's: '...'."
+                            g_title = diff_meta.get('goal_title', 'Goal')
+                            s_idx = diff_meta['step_index']
+                            reply_msg = f"{g_title}. I updated step {s_idx}. It was: '{diff_meta['before_text']}'. Now it's: '{diff_meta['after_text']}'."
                         else:
-                            # Steps added/removed or multiple changes
-                            # Limit to first 3 steps in summary to keep it concise? Or just count.
+                            # Phrase: "<Goal title>. Updated steps. Now: ..."
                             step_list_str = ", ".join([f"{i+1}. {s}" for i, s in enumerate(after_steps[:3])])
                             if len(after_steps) > 3: step_list_str += "..."
-                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated steps.\nNow: {step_list_str}"
+                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}. Updated steps. Now: {step_list_str}"
                     elif not reply_msg.strip():
                          reply_msg = f"Draft: '{title}' ({steps_count} steps)."
                     else:
@@ -4622,14 +4629,37 @@ def handle_message():
             except (ValueError, TypeError):
                 pass
 
-        # Phase 18: Show Seed Steps
-        # Trigger: ui_action="show_seed_steps" or text command "show seed steps"
+        # Phase 18: Show Seed Steps (Deterministic Tone)
+        # Trigger: ui_action="show_seed_steps" or text command "show seed steps", "read back steps", etc.
         is_show_steps = (ui_action == "show_seed_steps")
         if not is_show_steps and user_input:
-             if re.search(r"^(show|list)\s+((me|the)\s+)?(seed\s+)?steps", user_input.strip().lower()):
+             # Expanded regex for Phase 21: "show me the steps", "read back the steps", "list the steps", "what are the steps"
+             if re.search(r"^(show|list|read(\s+back)?|what(\s+are)?)\s+((me|the)\s+)?(seed\s+)?steps", user_input.strip().lower()):
                  is_show_steps = True
 
         if is_show_steps and user_id:
+            # Check draft first (Phase 21)
+            draft_id = data.get("draft_id")
+            if draft_id:
+                try:
+                    d = suggestions_repository.get_suggestion(user_id, int(draft_id))
+                    if d and d.get("status") == "pending":
+                        payload = d.get("payload", {})
+                        steps = payload.get("steps", [])
+                        if not steps:
+                            reply = "This draft doesn't have any steps yet."
+                        else:
+                            reply = f"Steps for draft '{payload.get('title', 'New Goal')}':\n"
+                            for i, s in enumerate(steps, 1):
+                                reply += f"\n{i}. {s}"
+                        return jsonify({
+                            "reply": reply,
+                            "agent_status": {"planner_active": False},
+                            "request_id": request_id
+                        })
+                except Exception:
+                    pass
+
             target_goal_id = data.get("goal_id") or data.get("active_goal_id")
             if target_goal_id:
                 try:
diff --git a/static/othello.css b/static/othello.css
index e7fd21de..13265837 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -906,6 +906,11 @@
       align-items: center;
       gap: 0.75rem;
       flex-shrink: 0;
+      /* Phase 21: Fix mobile layout */
+      height: auto;
+      min-height: auto;
+      flex-wrap: wrap;
+      overflow: visible;
     }
 
     .focus-ribbon.visible {
```
