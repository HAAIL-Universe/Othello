# Cycle Status: COMPLETE

## Todo Ledger
- [x] Analyze `api.py` read path (confirm it expects query params)
- [x] Analyze `othello.js` `fetchChatHistory` (found missing query params in convo route)
- [x] Apply fix: Append query string to conversation messages URL

## Next Action
Stop and commit.

## Unified Diff
```diff
diff --git a/static/othello.js b/static/othello.js
index 89abcdef..0123456 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -4930,7 +4930,8 @@
     async function fetchChatHistory(limit = 50, channel = "companion") {
       let target = `${V1_MESSAGES_API}?limit=${limit}&channel=${encodeURIComponent(channel)}`;
       if (othelloState.activeConversationId) {
-          target = `/api/conversations/${othelloState.activeConversationId}/messages`;
+          // Bugfix: ensure query params are passed to conversation route too
+          target = `/api/conversations/${othelloState.activeConversationId}/messages?limit=${limit}&channel=${encodeURIComponent(channel)}`;
       }
       const resp = await fetch(target, { credentials: "include", cache: "no-store" });
       if (resp.status === 401 || resp.status === 403) {
```
