# Unified Diff Log

## Manual Verification Checklist

- [ ] **Send message**: Send a message in the chat.
- [ ] **Check visibility**: Verify that the assistant's reply (and your message) is fully visible above the input bar without needing to scroll manually.
- [ ] **Scroll bottom**: Manually scroll to the very bottom and ensure there is a "gutter" of empty space (approx 72px + 1rem) at the end.

## Diff

```diff
diff --git a/static/othello.css b/static/othello.css
index a531c9a2..54e791ea 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1898,6 +1898,7 @@
 
 /* The Chat Container (panel) */
 .chat-sheet {
+  --chat-input-h: 72px;
   width: min(500px, 100%);
   height: min(800px, 85vh); /* Tall sheet on bottom right */
   background: var(--bg-1);
@@ -1968,6 +1969,8 @@
   flex: 1 1 0;
   overflow-y: auto; /* The log scrolls */
   padding: 1rem;
+  padding-bottom: calc(1rem + var(--chat-input-h));
+  scroll-padding-bottom: calc(1rem + var(--chat-input-h));
   display: flex;
   flex-direction: column;
   gap: 0.5rem;
```
