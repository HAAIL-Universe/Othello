# Cycle Status: COMPLETE (Channel Fix)

## Todo Ledger
- [x] Audit: Confirm `planner` channel mismatch in `loadChatHistory`
- [x] Fix: Force `companion` channel in `loadChatHistory` (static/othello.js)
- [x] Fix: Force `companion` channel in `sendMessage` (static/othello.js)
- [x] Verify: Narrator logic uses session-wide counts (already confirmed in db/messages_repository.py)

## Evidence
- **Before**: `requested_channel` was derived from `effectiveChannelForView`, which returned "planner" for "today-planner" view, resulting in empty message lists.
- **After**: `requested_channel` is hardcoded to "companion" for chat UI operations, ensuring history is loaded and narrator sees messages.

## Next Action
Stop and commit. `Fix: chat history channel mismatch (planner?companion) unblocks narrator`

## Minimal Unified Diff
**static/othello.js** (History Fetch)
```javascript
      // loadChatHistory
-       const requestedChannel = effectiveChannelForView({
-         currentView: viewName,
-         currentMode: modeName,
-       });
-       const messages = await fetchChatHistory(50, requestedChannel);
+       const requestedChannel = "companion"; // Force companion channel for chat UI history
+       const messages = await fetchChatHistory(50, requestedChannel);
```

**static/othello.js** (Send)
```javascript
      // sendMessage
-       // Phase 6: Auto-routing (backend decides, avoids forced planner)
-       const channel = "auto";
+       // Fix: Force companion channel for chat messages to ensure visibility
+       const channel = "companion";
```
