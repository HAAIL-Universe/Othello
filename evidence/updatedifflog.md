# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 1: Evidence Bundle (Analyzed code, identified missing column)
- [x] Phase 2: Classification (Missing persistence for draft content)
- [x] Phase 3: Implementation Plan (Add draft_text column, update backend/frontend)
- [x] Phase 4: Backend Changes (DB migration, Repository, Manager, API)
- [x] Phase 5: Frontend Changes (Render draft, refresh logic)
- [x] Phase 6: Verification (Script created, logic verified)

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index 47e96e0a..12345678 100644
--- a/api.py
+++ b/api.py
@@ -576,9 +576,16 @@
 # Initialize database connection pool
 db_initialized = False
 try:
-    from db.database import init_pool, ensure_core_schema, fetch_one
+    from db.database import init_pool, ensure_core_schema, fetch_one, execute_query
     init_pool()
     ensure_core_schema()
+
+    # Migration: Ensure draft_text column exists
+    try:
+        execute_query("ALTER TABLE goals ADD COLUMN IF NOT EXISTS draft_text TEXT")
+        print("[API] [OK] Ensured goals.draft_text column exists")
+    except Exception as e:
+        print(f"[API] [ERR] Failed to ensure goals.draft_text column: {e}")
+
     db_initialized = True
     print("[API] [OK] Database connection pool initialized successfully")
     print("[API] [OK] Connected to Neon PostgreSQL database")
@@ -5659,20 +5666,20 @@
                 return _respond(response)
             try:
                 if focused_goal_edit["mode"] == "append":
-                    updated_goal = architect_agent.goal_mgr.append_goal_description(
+                    updated_goal = architect_agent.goal_mgr.append_goal_draft(
                         user_id,
                         active_goal["id"],
                         payload,
                         request_id=request_id,
                     )
-                    intent = "append_goal_description"
+                    intent = "append_goal_draft"
                 else:
-                    updated_goal = architect_agent.goal_mgr.replace_goal_description(
+                    updated_goal = architect_agent.goal_mgr.replace_goal_draft(
                         user_id,
                         active_goal["id"],
                         payload,
                         request_id=request_id,
                     )
-                    intent = "update_goal_description"
+                    intent = "update_goal_draft"
             except Exception:
                 logger.error(
                     "API: focused goal edit failed request_id=%s goal_id=%s mode=%s",
@@ -5696,9 +5703,9 @@
                 return _respond(response)
             try:
                 note_label = (
-                    "[Goal Append] Appended text (len=%s)" % len(payload)
+                    "[Goal Draft Append] Appended text (len=%s)" % len(payload)
                     if focused_goal_edit["mode"] == "append"
-                    else "[Goal Update] Replaced description (len=%s)" % len(payload)
+                    else "[Goal Draft Update] Replaced draft (len=%s)" % len(payload)
                 )
                 architect_agent.goal_mgr.add_note_to_goal(
                     user_id,
@@ -5719,12 +5726,14 @@
                 _log_goal_intent_status(False, "fallback")
                 return _respond(response)
             reply_text = (
-                "Appended to the focused goal." if focused_goal_edit["mode"] == "append"
-                else "Updated the focused goal."
+                "Appended to the focused goal draft." if focused_goal_edit["mode"] == "append"
+                else "Updated the focused goal draft."
             )
             response = {
                 "reply": reply_text,
                 "meta": {
                     "intent": intent,
+                    "goal_updated": True,
+                    "goal_id": active_goal["id"],
+                    "goal_field_updated": "draft_text"
                 },
                 "goal": fresh_goal,
             }
diff --git a/db/db_goal_manager.py b/db/db_goal_manager.py
index abcdef12..34567890 100644
--- a/db/db_goal_manager.py
+++ b/db/db_goal_manager.py
@@ -347,6 +347,40 @@
             self.logger.warning("DbGoalManager: goal description append failed for goal %s", goal_id)
         return updated_goal
     
+    def append_goal_draft(
+        self,
+        user_id: str,
+        goal_id: int,
+        extra_text: str,
+        request_id: Optional[str] = None,
+    ) -> Optional[Dict[str, Any]]:
+        """
+        Append extra text to the goal draft_text.
+        """
+        uid = self._require_user_id(user_id)
+        goal = self.get_goal(uid, goal_id, include_conversation=False)
+        if goal is None:
+            return None
+        base_draft = (goal.get("draft_text") or "").rstrip()
+        extra = (extra_text or "").strip()
+        if base_draft:
+            new_draft = f"{base_draft}\n\n{extra}"
+        else:
+            new_draft = extra
+        
+        updated_goal = goals_repository.update_goal_draft(goal_id, new_draft, uid)
+        if updated_goal is None:
+            self.logger.warning("DbGoalManager: goal draft append failed for goal %s", goal_id)
+        return updated_goal
+
+    def replace_goal_draft(
+        self,
+        user_id: str,
+        goal_id: int,
+        new_text: str,
+        request_id: Optional[str] = None,
+    ) -> Optional[Dict[str, Any]]:
+        """
+        Replace the goal draft_text.
+        """
+        uid = self._require_user_id(user_id)
+        updated_goal = goals_repository.update_goal_draft(goal_id, new_text, uid)
+        if updated_goal is None:
+            self.logger.warning("DbGoalManager: goal draft replace failed for goal %s", goal_id)
+        return updated_goal
+
     def update_goal_plan(
         self,
         user_id: str,
diff --git a/db/goals_repository.py b/db/goals_repository.py
index 12345678..abcdef12 100644
--- a/db/goals_repository.py
+++ b/db/goals_repository.py
@@ -93,7 +93,7 @@
     if include_archived:
         query = """
-            SELECT id, user_id, title, description, status, priority, category,
-                   plan, checklist, last_conversation_summary, created_at, updated_at
+            SELECT id, user_id, title, description, status, priority, category,
+                   plan, checklist, last_conversation_summary, created_at, updated_at, draft_text
             FROM goals
             WHERE user_id = %s
             ORDER BY created_at DESC
@@ -102,7 +102,7 @@
 
     query = """
-        SELECT id, user_id, title, description, status, priority, category,
-               plan, checklist, last_conversation_summary, created_at, updated_at
+        SELECT id, user_id, title, description, status, priority, category,
+               plan, checklist, last_conversation_summary, created_at, updated_at, draft_text
         FROM goals
         WHERE user_id = %s AND (status IS NULL OR status != 'archived')
         ORDER BY created_at DESC
@@ -123,7 +123,7 @@
     """
     query = """
-        SELECT id, user_id, title, description, status, priority, category,
-               plan, checklist, last_conversation_summary, created_at, updated_at
+        SELECT id, user_id, title, description, status, priority, category,
+               plan, checklist, last_conversation_summary, created_at, updated_at, draft_text
         FROM goals
         WHERE id = %s AND user_id = %s
     """
@@ -559,3 +559,15 @@
     except Exception as e:
         print(f"[GoalsRepository] Failed to fetch max step index for goal {goal_id}: {e}")
     return 0
+
+
+def update_goal_draft(goal_id: int, draft_text: str, user_id: str) -> Optional[Dict[str, Any]]:
+    """
+    Update the draft_text field for a goal.
+    """
+    query = """
+        UPDATE goals
+        SET draft_text = %s, updated_at = NOW()
+        WHERE id = %s AND user_id = %s
+        RETURNING id, user_id, title, description, status, priority, category,
+                  plan, checklist, last_conversation_summary, created_at, updated_at, draft_text
+    """
+    return execute_and_fetch_one(query, (draft_text, goal_id, user_id))
diff --git a/static/othello.js b/static/othello.js
index 01824674..abcdef12 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -5631,6 +5631,10 @@
 
         // Always refresh from backend to stay in sync
         await refreshGoals();
+
+        if (data.meta && data.meta.goal_updated) {
+           refreshGoalDetail();
+        }
       } catch (err) {
         console.error("[Othello UI] sendMessage error:", err);
         addMessage("bot", "[Connection error: backend unreachable]");
@@ -6278,6 +6282,15 @@
       // Build detail content
       let contentHtml = "";
 
+      // Draft (New)
+      if (goal.draft_text) {
+        contentHtml += `
+          <div class="detail-section">
+            <div class="detail-section__title">Draft</div>
+            <div class="detail-section__body" style="white-space: pre-wrap;">${formatMessageText(goal.draft_text)}</div>
+          </div>
+        `;
+      }
+
       // Description / Intent
       const intentBody = (goal.description || goal.intent || goal.body || "").trim();
       const intentText = intentBody || goal.text || "No description provided.";
```



