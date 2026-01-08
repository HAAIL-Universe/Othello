# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Fixed: hydration API call missing conversation_id arg

## Next Action
Stop and commit.

diff --git a/api.py b/api.py
index b6bd9986..da288d6e 100644
--- a/api.py
+++ b/api.py
@@ -4695,7 +4695,10 @@ def handle_message():
             # Phase 23: Context Hydration from Checkpoint (if enabled)
             from db.messages_repository import get_latest_active_draft_context, get_linked_messages_from_checkpoint
             try:
-                latest_dc = get_latest_active_draft_context(user_id)
+                latest_dc = None
+                if conversation_id:
+                    latest_dc = get_latest_active_draft_context(user_id, conversation_id)
+                
                 if latest_dc:
                      start_msg_id = latest_dc["start_message_id"]
                      linked = get_linked_messages_from_checkpoint(user_id, start_msg_id)
