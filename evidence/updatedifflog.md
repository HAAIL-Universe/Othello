Cycle Status: COMPLETE
Todo Ledger:
- Planned: Fix peek-mode plan_date parsing and dedupe Clear Routines load.
- Completed: Parsed peek plan_date with validation, normalized Clear Routines handler flow, py_compile passed.
- Remaining: None.
Next Action: None.

diff --git a/api.py b/api.py
index a681fcfa..1993df2c 100644
--- a/api.py
+++ b/api.py
@@ -5378,23 +5378,33 @@ def get_today_plan():
         "fatigue": args.get("fatigue"),
         "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
     }
-    
+
+    # Peek mode: Read-only, no generation, no merging, no persistence
+    peek_mode = args.get("peek") == "1"
     plan_date = None
-    if args.get("plan_date"):
+    if peek_mode:
+        plan_date_str = args.get("plan_date")
+        if not plan_date_str:
+            return api_error("VALIDATION_ERROR", "peek_requires_plan_date", 400)
         try:
-            plan_date = date.fromisoformat(args.get("plan_date"))
+            plan_date = date.fromisoformat(plan_date_str)
         except ValueError:
-            return api_error("VALIDATION_ERROR", "Invalid plan_date format (expected YYYY-MM-DD)", 400)
+            return api_error("VALIDATION_ERROR", "invalid_plan_date", 400)
     else:
-        plan_date = _get_local_today(user_id)
-        logger.info("API: today-plan using local_today=%s", plan_date)
+        if args.get("plan_date"):
+            try:
+                plan_date = date.fromisoformat(args.get("plan_date"))
+            except ValueError:
+                return api_error(
+                    "VALIDATION_ERROR",
+                    "Invalid plan_date format (expected YYYY-MM-DD)",
+                    400,
+                )
+        else:
+            plan_date = _get_local_today(user_id)
+            logger.info("API: today-plan using local_today=%s", plan_date)
 
-    # Peek mode: Read-only, no generation, no merging, no persistence
-    peek_mode = args.get("peek") == "1"
     if peek_mode:
-        if not args.get("plan_date"):
-             return api_error("VALIDATION_ERROR", "peek_requires_plan_date", 400)
-        
         # Try to load existing plan row
         plan_repo = comps["plan_repository"]
         plan_row = plan_repo.get_plan_by_date(user_id, plan_date)
diff --git a/othello_ui.html b/othello_ui.html
index ecdb3eac..4ed3660c 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -2548,20 +2548,16 @@
             if (scopes.includes("routines")) {
               othelloState.routines = [];
               if (typeof loadRoutinePlanner === "function") {
-                  await loadRoutinePlanner();
+                await loadRoutinePlanner();
               }
               // Clear week view cache to prevent stale routine counts
-              if (typeof weekViewCache !== 'undefined') {
-                  for (const key in weekViewCache) delete weekViewCache[key];
+              if (typeof weekViewCache !== "undefined") {
+                for (const key in weekViewCache) delete weekViewCache[key];
               }
               // Refresh week view if open
-              const weekView = document.getElementById('week-view-container');
-              if (weekView && weekView.style.display !== 'none' && typeof openWeekView === 'function') {
-                  openWeekView();
-              }
-              refreshPlanner = true;
-            }
-                await loadRoutinePlanner();
+              const weekView = document.getElementById("week-view-container");
+              if (weekView && weekView.style.display !== "none" && typeof openWeekView === "function") {
+                openWeekView();
               }
               refreshPlanner = true;
             }
