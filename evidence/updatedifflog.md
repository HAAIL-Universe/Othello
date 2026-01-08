# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Refactor: Hydrate draft context BEFORE payload generation

## Next Action
Stop and commit.

diff --git a/api.py b/api.py
index da288d6e..7b4296b7 100644
--- a/api.py
+++ b/api.py
@@ -4690,15 +4690,21 @@ def handle_message():
                 is_create_draft = True
         
         if is_create_draft:
-            payload = _generate_goal_draft_payload(user_input)
+            # Phase 23: Context Hydration from Checkpoint
+            # We must hydrate BEFORE generating the payload so the generator sees the full context (Title, Steps etc.)
+            hydration_source_msg_id = None
+            generation_text = user_input
             
-            # Phase 23: Context Hydration from Checkpoint (if enabled)
             from db.messages_repository import get_latest_active_draft_context, get_linked_messages_from_checkpoint
             try:
                 latest_dc = None
+                # Try session-scoped context first
                 if conversation_id:
                     latest_dc = get_latest_active_draft_context(user_id, conversation_id)
                 
+                # If no session provided or found, maybe try global active? 
+                # (For now stick to session integrity)
+                
                 if latest_dc:
                      start_msg_id = latest_dc["start_message_id"]
                      linked = get_linked_messages_from_checkpoint(user_id, start_msg_id)
@@ -4709,21 +4715,25 @@ def handle_message():
                              lines.append(f"{role}: {m.get('transcript')}")
                          full_transcript = "\n".join(lines)
                          
-                         # Na├»ve hydration: Append transcript to body so user (and LLM) sees it
-                         current_body = payload.get("body", "")
-                         payload["body"] = (current_body + "\n\nContext:\n" + full_transcript).strip()
-                         
+                         # Prepend context to generation text so the LLM/Heuristic sees it
+                         generation_text = f"{user_input}\n\n[CONTEXT FROM CHECKPOINT]:\n{full_transcript}"
                          hydration_source_msg_id = start_msg_id
-                         # If title is default, try to improve it?
-                         if payload.get("title") == "New Goal":
-                             # Very dumb heuristic: First 5 words of first user message
-                             first_user_msg = next((m for m in linked if m.get("source") == "user"), None)
-                             if first_user_msg:
-                                 txt = first_user_msg.get("transcript", "")
-                                 payload["title"] = " ".join(txt.split()[:5]) + "..."
+                         logger.info("API: Hydrated draft generation with %d chars of context", len(full_transcript))
             except Exception as e:
                 logger.warning("Failed to hydrate draft context: %s", e)
 
+            # Now generate payload with full context
+            payload = _generate_goal_draft_payload(generation_text)
+            
+            # If we hydrated, ensure the body contains the context reference if it wasn't captured
+            if hydration_source_msg_id and "CONTEXT FROM CHECKPOINT" not in str(payload.get("body", "")):
+                # Just to be safe, we can append a clean summary or just rely on the generator having done its job.
+                # Let's trust _generate_goal_draft_payload to extract title/steps from generation_text.
+                # But we might want to store the raw context in the body for the user to see/edit.
+                current_body = payload.get("body", "")
+                if len(current_body) < 10: # If generator returned empty body
+                     payload["body"] = generation_text 
+
             suggestion = suggestions_repository.create_suggestion(
                 user_id=user_id,
                 kind="goal",
