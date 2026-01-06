# Cycle Status: COMPLETE

## Todo Ledger
Planned:
- [x] Phase 17: Fix /api/goals/<id> ValueError handling (Prevent 500 crashes)
Completed:
- [x] Phase 17: Patched `api.get_goal_with_plan` to catch ValueErrors and return 500/400 JSON.
Remaining:
- [ ] Next phase tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index bf1aaeb2..047983f9 100644
--- a/api.py
+++ b/api.py
@@ -8776,14 +8776,11 @@ def get_goal_with_plan(goal_id):
     except ValueError as exc:
         reason = str(exc)
-        logger.error("API: Goal detail id normalization failed goal_id=%s reason=%s", goal_id, reason)
-        if reason == "INVALID_GOAL_ID":
-            return api_error("GOAL_ID_INVALID", "Goal id must be an integer", 500)
-        if reason == "INVALID_PLAN_STEP_ID":
-            return api_error("PLAN_STEP_ID_INVALID", "Plan step id must be an integer", 500)
-        if reason == "INVALID_PLAN_STEP_INDEX":
-            return api_error("PLAN_STEP_INDEX_INVALID", "Plan step index must be an integer", 500)
-        return api_error("GOAL_ID_INVALID", "Goal id normalization failed", 500)
+        if reason == "INVALID_GOAL_ID":
+            return api_error("VALIDATION_ERROR", f"Invalid goal ID format: {goal_id}", 400)
+
+        logger.error(f"API: get_goal_with_plan ValueError for {goal_id}: {reason}", exc_info=True)
+        return api_error("INTERNAL_ERROR", "Failed to retrieve goal", 500)
 
     except Exception as e:
         logger.error(f"API: Failed to fetch goal #{goal_id}: {e}", exc_info=True)
```
