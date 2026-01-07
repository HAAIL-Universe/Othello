# Cycle Status: COMPLETE

## Todo Ledger
Completed:
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Phase 6: Env Fix (OpenAI Key 401)
- [x] Phase 6: Add deterministic error surfacing for 500s
- [x] Phase 6: Fix 500 error (is_chat_view NameError)

## Next Action
Stop and commit.

diff --git a/api.py b/api.py
index 6ac8ffae..8969d8ac 100644
--- a/api.py
+++ b/api.py
@@ -4323,7 +4323,8 @@ def handle_message():
         current_view = data.get("current_view")
         raw_channel = data.get("channel")
         view_label = str(current_view or "chat")
-        
+        is_chat_view = (view_label == "chat")
+
         # Phase 6: True Auto Routing (Content-based)
         effective_channel = "companion" # Default safe fallback
         incoming_channel = "unknown"
