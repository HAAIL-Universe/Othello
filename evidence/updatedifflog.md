# Cycle Status: COMPLETE (Phase 22.4 - Conversation Context Fix)

## Todo Ledger
Planned:
- [x] Phase 22.4: Locate LLM prompt construction in api.py / architect_brain.
- [x] Phase 22.4: Optimize _load_companion_context for relevance and noise reduction.
- [x] Phase 22.4: Filter out non-chat sources (system logs) from LLM context.
- [x] Phase 22.4: Enforce chronological order [Oldest -> Newest] for LLM.
Completed:
- [x] api.py: Updated _load_companion_context to filter sources, trim content, and respect max_turns.
Remaining:
- [ ] Done.

## Next Action
Commit and Push.

## Root Cause Anchors
- api.py:1540 (Refined context loading loop to exclude system noise and ensure token safety)

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 4df74254..771dbba9 100644
--- a/api.py
+++ b/api.py
@@ -1538,20 +1538,35 @@ def _load_companion_context(
         return []
     messages: List[Dict[str, str]] = []
     total_chars = 0
+    # Process Newest -> Oldest (reversed rows)
     for row in reversed(rows):
+        source = (row.get("source") or "").strip().lower()
+        # Filter out internal/system messages
+        if source not in {"user", "assistant", "text"}:
+            continue
+
         content = (row.get("transcript") or "").strip()
         if not content:
             continue
-        source = (row.get("source") or "").strip().lower()
+
         role = "assistant" if source == "assistant" else "user"
-        if total_chars and total_chars + len(content) > max_chars:
+        
+        # Per-message safety cap (e.g. 2000 chars)
+        if len(content) > 2000:
+            content = content[:2000] + "..."
+
+        # Total context cap check (accumulative)
+        if total_chars + len(content) > max_chars:
             break
-        if len(content) > max_chars:
-            content = content[:max_chars]
+
         messages.append({"role": role, "content": content})
         total_chars += len(content)
-        if len(messages) >= limit:
+        
+        # Stop if we hit the turn limit (e.g. 12)
+        if len(messages) >= max_turns:
             break
+
+    # Restore chronological order (Oldest -> Newest)
     messages.reverse()
     if messages:
         logger.debug(
```
