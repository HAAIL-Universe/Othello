# Cycle Status: IN_PROGRESS

## Todo Ledger
Planned:
- [ ] Cleanup

## Next Action
Testing cleanup

diff --git a/0dee2034_peek_mode.patch b/build_docs/evidence/0dee2034_peek_mode.patch
similarity index 100%
rename from 0dee2034_peek_mode.patch
rename to build_docs/evidence/0dee2034_peek_mode.patch
diff --git a/BOOT_IMPLEMENTATION_REPORT.md b/build_docs/evidence/BOOT_IMPLEMENTATION_REPORT.md
similarity index 100%
rename from BOOT_IMPLEMENTATION_REPORT.md
rename to build_docs/evidence/BOOT_IMPLEMENTATION_REPORT.md
diff --git a/BRANCH_CONSOLIDATION_AND_API_AUDIT_REPORT.md b/build_docs/evidence/BRANCH_CONSOLIDATION_AND_API_AUDIT_REPORT.md
similarity index 100%
rename from BRANCH_CONSOLIDATION_AND_API_AUDIT_REPORT.md
rename to build_docs/evidence/BRANCH_CONSOLIDATION_AND_API_AUDIT_REPORT.md
diff --git a/DRAFT_CLEANUP_SUMMARY.md b/build_docs/evidence/DRAFT_CLEANUP_SUMMARY.md
similarity index 100%
rename from DRAFT_CLEANUP_SUMMARY.md
rename to build_docs/evidence/DRAFT_CLEANUP_SUMMARY.md
diff --git a/DataFlow.txt b/build_docs/evidence/DataFlow.txt
similarity index 100%
rename from DataFlow.txt
rename to build_docs/evidence/DataFlow.txt
diff --git a/EXPLANATION.md b/build_docs/evidence/EXPLANATION.md
similarity index 100%
rename from EXPLANATION.md
rename to build_docs/evidence/EXPLANATION.md
diff --git a/FLASK_BOOT_FIX_SUMMARY.md b/build_docs/evidence/FLASK_BOOT_FIX_SUMMARY.md
similarity index 100%
rename from FLASK_BOOT_FIX_SUMMARY.md
rename to build_docs/evidence/FLASK_BOOT_FIX_SUMMARY.md
diff --git a/OTHELLO_PROJECT_INDEX.md b/build_docs/evidence/OTHELLO_PROJECT_INDEX.md
similarity index 100%
rename from OTHELLO_PROJECT_INDEX.md
rename to build_docs/evidence/OTHELLO_PROJECT_INDEX.md
diff --git a/OTHELLO_UPDATE_LOG b/build_docs/evidence/OTHELLO_UPDATE_LOG
similarity index 100%
rename from OTHELLO_UPDATE_LOG
rename to build_docs/evidence/OTHELLO_UPDATE_LOG
diff --git a/PLANNING_ENGINE_GUIDE.md b/build_docs/evidence/PLANNING_ENGINE_GUIDE.md
similarity index 100%
rename from PLANNING_ENGINE_GUIDE.md
rename to build_docs/evidence/PLANNING_ENGINE_GUIDE.md
diff --git a/PROOF_BUNDLE_ROUTINES_SNOOZE.md b/build_docs/evidence/PROOF_BUNDLE_ROUTINES_SNOOZE.md
similarity index 100%
rename from PROOF_BUNDLE_ROUTINES_SNOOZE.md
rename to build_docs/evidence/PROOF_BUNDLE_ROUTINES_SNOOZE.md
diff --git a/phase8.diff b/build_docs/evidence/phase8.diff
similarity index 100%
rename from phase8.diff
rename to build_docs/evidence/phase8.diff
diff --git a/phase9.diff b/build_docs/evidence/phase9.diff
similarity index 100%
rename from phase9.diff
rename to build_docs/evidence/phase9.diff
diff --git a/pushme.ps1 b/build_docs/evidence/pushme.ps1
similarity index 100%
rename from pushme.ps1
rename to build_docs/evidence/pushme.ps1
diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index 099a6130..8ca627b4 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -7,88 +7,4 @@
 
 ## Next Action
 Verify in staging.
-
-diff --git a/api.py b/api.py

-index 83f9be4b..10d9e32d 100644

---- a/api.py

-+++ b/api.py

-@@ -2118,16 +2118,16 @@ def parse_goal_selection_request(text: str) -> Optional[int]:

-     """

-     t = text.lower().strip()

-     

--    # Strict patterns that require explicit goal selection intent

-+    # Strict patterns that require explicit goal selection intent (updated to allow trailing punctuation)

-     goal_select_patterns = [

--        r'^goal\s+#?(\d+)$',                    # "goal 1" or "goal #1"

--        r'^select\s+goal\s+#?(\d+)$',           # "select goal 1"

--        r'^switch\s+to\s+goal\s+#?(\d+)$',      # "switch to goal 1"

--        r'^focus\s+on\s+goal\s+#?(\d+)$',       # "focus on goal 1"

--        r'^work\s+on\s+goal\s+#?(\d+)$',        # "work on goal 1"

--        r'^talk\s+about\s+goal\s+#?(\d+)$',     # "talk about goal 1"

--        r'^go\s+to\s+goal\s+#?(\d+)$',          # "go to goal 1"

--        r'^use\s+goal\s+#?(\d+)$',              # "use goal 1"

-+        r'^goal\s+#?(\d+)\s*[.!?]?$',                    # "goal 1"

-+        r'^select\s+goal\s+#?(\d+)\s*[.!?]?$',           # "select goal 1"

-+        r'^switch\s+to\s+goal\s+#?(\d+)\s*[.!?]?$',      # "switch to goal 1"

-+        r'^focus\s+on\s+goal\s+#?(\d+)\s*[.!?]?$',       # "focus on goal 1"

-+        r'^work\s+on\s+goal\s+#?(\d+)\s*[.!?]?$',        # "work on goal 1"

-+        r'^talk\s+about\s+goal\s+#?(\d+)\s*[.!?]?$',     # "talk about goal 1"

-+        r'^go\s+to\s+goal\s+#?(\d+)\s*[.!?]?$',          # "go to goal 1"

-+        r'^use\s+goal\s+#?(\d+)\s*[.!?]?$',              # "use goal 1"

-     ]

-     

-     for pattern in goal_select_patterns:

-@@ -6294,11 +6294,14 @@ def handle_message():

-                     active_goal = server_active_goal

-                     goal_resolution_path = "server_active"

- 

-+        chosen_context = f"goal:{active_goal['id']}" if isinstance(active_goal, dict) else "companion"

-         logger.info(

--            "API: resolved active_goal path=%s request_id=%s goal_id=%s",

--            goal_resolution_path,

--            request_id,

-+            "API: context_decision mode=%s view=%s active_goal_id=%s chosen_context=%s request_id=%s",

-+            current_mode,

-+            current_view,

-             active_goal.get("id") if isinstance(active_goal, dict) else None,

-+            chosen_context,

-+            request_id,

-         )

- 

-         if ui_action == "plan_from_text_append":

-diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md

-index 9b1b8544..8ca627b4 100644

-Binary files a/evidence/updatedifflog.md and b/evidence/updatedifflog.md differ

-diff --git a/static/othello.js b/static/othello.js

-index 6efeb39d..7d95718c 100644

---- a/static/othello.js

-+++ b/static/othello.js

-@@ -5825,6 +5825,27 @@

- 

-       // Voice-first save command (Strict Command Mode)

-       const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");

-+      

-+      // Intercept "Focus on Goal <id>" for immediate UI switching

-+      // Matches: "focus on goal 123", "focus on goal 123."

-+      const focusMatch = lowerText.match(/^focus\s+on\s+goal\s+(\d+)$/);

-+      if (focusMatch) {

-+          const targetId = parseInt(focusMatch[1], 10);

-+          console.log(`[Othello UI] Intercepted focus command for goal ${targetId}`);

-+          

-+          input.value = "";

-+          addMessage("user", text); // Echo user input

-+          

-+          if (typeof setActiveGoal === "function") {

-+             // Activate the goal in UI state (which updates active_goal_id for future messages)

-+             setActiveGoal(targetId);

-+             addMessage("bot", `Focused on Goal ${targetId}.`);

-+          } else {

-+             console.warn("[Othello UI] setActiveGoal not available");

-+          }

-+          return; // Stop processing (do not send as chat)

-+      }

-+

-       const commandPhrases = new Set(["save as long-term goal", "save this as a goal", "create that goal", "save that goal", "lock that in as a goal"]);

-       const isQuestion = text.toLowerCase().match(/^(how|can|should|do) i\b/);

- 

-
\ No newline at end of file
+
