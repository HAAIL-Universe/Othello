# Cycle Status: IN_PROGRESS

## Todo Ledger
Planned:
- [ ] Reproduce issue
- [ ] Add debug logging
- [ ] Analyze root cause
- [ ] Fix issue
Completed:
- [x] Reproduce issue
- [x] Add debug logging
Remaining:
- [ ] Analyze root cause
- [ ] Fix issue

## Next Action
Analyze root cause of AuthenticationError

diff --git a/core/architect_brain.py b/core/architect_brain.py
index a56669e3..ed5703a3 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -462,7 +462,7 @@ class Architect:
             return user_facing_response, agent_status
 
         except Exception as e:
-            self.logger.error(f"ÔØî Architect failed: {e}")
+            self.logger.error(f"ÔØî Architect failed: {e}", exc_info=True)
             # Return error message with default agent_status
             return "Sorry, something went wrong planning that.", {
                 "planner_active": False,
diff --git a/core/architect_brain.py b/core/architect_brain.py
index a56669e3..ed5703a3 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -462,7 +462,7 @@ class Architect:
             return user_facing_response, agent_status
 
         except Exception as e:
-            self.logger.error(f"ÔØî Architect failed: {e}")
+            self.logger.error(f"ÔØî Architect failed: {e}", exc_info=True)
             # Return error message with default agent_status
             return "Sorry, something went wrong planning that.", {
                 "planner_active": False,
