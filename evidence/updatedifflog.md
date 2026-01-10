Cycle Status: COMPLETE

Todo Ledger:
- Planned: preview and clean untracked evidence; capture plans schema evidence; add updated-fields line + next-first ordering for plan replies; compute changed fields; fix confirm plan routing; update tests; run tests; manual verification.
- Completed: added .gitignore entries for local evidence and cleaned untracked artifacts; captured plans schema evidence in db/schema.sql and db/database.py; added diff_plan_fields + updated plan reply format; added confirm plan routing; updated tests; ran unit tests; completed manual HTTP smoke flow.
- Remaining: none.

Next Action:
- None.

## Repo Hygiene - Untracked Evidence Preview
Would remove evidence/phase1_add_task_req.json
Would remove evidence/phase1_add_task_resp.json
Would remove evidence/phase1_build_enter.json
Would remove evidence/phase1_enter_build_req.json
Would remove evidence/phase1_enter_build_resp.json
Would remove evidence/phase1_login_resp.json
Would remove evidence/phase1_select_plan_req.json
Would remove evidence/phase1_select_plan_resp.json
Would remove evidence/phase1_stt_blob_req.json
Would remove evidence/phase1_stt_blob_resp.json
Would remove evidence/phase1_timeline_req.json
Would remove evidence/phase1_timeline_resp.json
Would remove evidence/phase2_add_task_req.json
Would remove evidence/phase2_add_task_resp.json
Would remove evidence/phase2_enter_build_req.json
Would remove evidence/phase2_enter_build_resp.json
Would remove evidence/phase2_login_resp.json
Would remove evidence/phase2_select_plan_req.json
Would remove evidence/phase2_select_plan_resp.json
Would remove evidence/phase2_stt_blob_req.json
Would remove evidence/phase2_stt_blob_resp.json
Would remove evidence/phase2_timeline_req.json
Would remove evidence/phase2_timeline_resp.json
Would remove evidence/phase3_login_resp.json
Would remove evidence/phase3_plan_reply_resp.json
Would remove evidence/server_phase2.err
Would remove evidence/server_phase2.log
Would remove evidence/server_phase2.pid


## Plans Table - Schema Evidence
- Definition (schema file): db/schema.sql:121-143
  - Columns: id SERIAL PRIMARY KEY; user_id TEXT NOT NULL; plan_date DATE NOT NULL; generation_context JSONB DEFAULT '{}'::jsonb; behavior_snapshot JSONB DEFAULT '{}'::jsonb; created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(); updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW().
  - Constraints: UNIQUE(user_id, plan_date); fk_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE.
  - Added columns (ALTER): plan_id INTEGER GENERATED ALWAYS AS (id) STORED; plan_date_local DATE; timezone TEXT DEFAULT 'UTC'; status TEXT DEFAULT 'draft'; created_at_utc TIMESTAMPTZ DEFAULT NOW(); confirmed_at_utc TIMESTAMPTZ.
  - Indexes: idx_plans_plan_date on plans(plan_date); idx_plans_user_date on plans(user_id, plan_date).
- Definition (bootstrap SQL): db/database.py:294-314 mirrors plan table and alters (plan_id/plan_date_local/timezone/status/created_at_utc/confirmed_at_utc).
- Plan-adjacent tables: plan_items defined at db/schema.sql:145-179 and db/database.py:318-349 (plan_id FK + indexes); goal_task_history defined at db/schema.sql:182-199.
- Repository usage: db/plan_repository.py
  - Upsert/read: upsert_plan (db/plan_repository.py:18-34), get_plan_by_date (db/plan_repository.py:37-44), get_plan_with_items (db/plan_repository.py:47-53), get_plans_since (db/plan_repository.py:75-82).
  - Plan item mutations: insert_plan_item (db/plan_repository.py:96-121), replace_plan_items (db/plan_repository.py:147-156).

Verification Notes:
- Add-task delta: message "Add a task to measure the space and pick dimensions." -> draft_payload.tasks appended (count=5, last="measure the space and pick dimensions").
- Timeline delta: message "Timeline might slip because of deliveries, maybe six weeks instead." -> draft_payload.timeline == "six weeks".
- Reply order: reply begins "**Updated:**" then "**Next:**", with "**Plan Draft**" after (reply prefix: "**Updated:** Timeline

**Next:** ...").
- Confirm plan: message "confirm plan" -> reply "PLAN_CONFIRMED." and plan draft marked accepted.
- Tests: `python -m unittest tests.test_planner_agent` and `python -m unittest tests.test_ui_actions`.

Unified diff (excluding diff log itself):
```diff
diff --git a/api.py b/api.py
index 6e84c37b..4341233d 100644
--- a/api.py
+++ b/api.py
@@ -4632,6 +4632,34 @@ def handle_message():
         is_fuzzy_confirm = "confirm" in norm_input
         is_confirm_text_with_id = is_fuzzy_confirm and data.get("draft_id")
 
+        if user_id and norm_input == "confirm plan" and data.get("draft_type") == "plan":
+            draft_id = data.get("draft_id")
+            draft = None
+            if draft_id:
+                try:
+                    draft_id = int(draft_id)
+                    draft = suggestions_repository.get_suggestion(user_id, draft_id)
+                except (ValueError, TypeError):
+                    draft = None
+
+            if draft and draft.get("status") == "pending" and draft.get("kind") == "plan":
+                suggestions_repository.update_suggestion_status(
+                    user_id,
+                    draft_id,
+                    "accepted",
+                    decided_reason="user_confirmed_plan",
+                )
+                return jsonify({
+                    "reply": "PLAN_CONFIRMED.",
+                    "draft_cleared": True,
+                    "request_id": request_id,
+                })
+
+            return jsonify({
+                "reply": "PENDING_PLAN_DRAFT_MISSING. I couldn't find a pending plan draft to confirm.",
+                "request_id": request_id,
+            })
+
         if user_id and (is_confirm_action or is_confirm_goal_text or is_confirm_text_with_id or is_fuzzy_confirm):
             draft_id = data.get("draft_id")
             
@@ -4964,8 +4992,15 @@ def handle_message():
                                 updated_payload,
                             )
                         suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
-                        
-                        reply_msg = planner_agent.format_plan_draft_reply(updated_payload)
+
+                        changed_fields = planner_agent.diff_plan_fields(
+                            current_payload,
+                            updated_payload,
+                        )
+                        reply_msg = planner_agent.format_plan_draft_reply(
+                            updated_payload,
+                            changed_fields=changed_fields,
+                        )
                         
                         return jsonify({
                             "reply": reply_msg,
diff --git a/planner_agent.py b/planner_agent.py
index 2dfacf5b..332fec87 100644
--- a/planner_agent.py
+++ b/planner_agent.py
@@ -146,6 +146,38 @@ def recompute_plan_missing_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
     return data
 
 
+def diff_plan_fields(
+    before_payload: Dict[str, Any],
+    after_payload: Dict[str, Any],
+) -> list[str]:
+    before = _coerce_payload(before_payload)
+    after = _coerce_payload(after_payload)
+
+    def _normalize_text(value: Any) -> str:
+        if value is None:
+            return ""
+        return str(value).strip()
+
+    before_objective = _normalize_text(before.get("objective"))
+    after_objective = _normalize_text(after.get("objective"))
+
+    before_tasks = _stringify_list(before.get("tasks"))
+    after_tasks = _stringify_list(after.get("tasks"))
+
+    before_timeline = _normalize_text(before.get("timeline"))
+    after_timeline = _normalize_text(after.get("timeline"))
+
+    changed = []
+    if before_objective != after_objective:
+        changed.append("Objective")
+    if before_tasks != after_tasks:
+        changed.append("Tasks")
+    if before_timeline != after_timeline:
+        changed.append("Timeline")
+
+    return changed
+
+
 def patch_plan_draft_payload_deterministic(
     text: str, payload: Dict[str, Any]
 ) -> Tuple[Dict[str, Any], bool]:
@@ -325,7 +357,10 @@ def format_build_mode_reply(draft_payload: Dict[str, Any]) -> str:
     return "\n\n".join(lines)
 
 
-def format_plan_draft_reply(draft_payload: Dict[str, Any]) -> str:
+def format_plan_draft_reply(
+    draft_payload: Dict[str, Any],
+    changed_fields: Optional[list[str]] = None,
+) -> str:
     payload = _coerce_payload(draft_payload)
     objective = payload.get("objective") or "(missing)"
     timeline = payload.get("timeline") or "(missing)"
@@ -333,8 +368,14 @@ def format_plan_draft_reply(draft_payload: Dict[str, Any]) -> str:
     next_line = _format_next_line(payload)
 
     lines = []
+    if changed_fields:
+        cleaned = [str(item).strip() for item in changed_fields if str(item).strip()]
+        if cleaned:
+            lines.append(f"**Updated:** {', '.join(cleaned)}")
+            lines.append("")
     if next_line:
         lines.extend([next_line, ""])
+        lines.append("")
     lines.extend(
         [
             "**Plan Draft**",
diff --git a/tests/test_planner_agent.py b/tests/test_planner_agent.py
index cc6f66f2..9190c802 100644
--- a/tests/test_planner_agent.py
+++ b/tests/test_planner_agent.py
@@ -72,6 +72,8 @@ class TestPlannerAgent(unittest.TestCase):
                 for task in updated.get("tasks", [])
             )
         )
+        changed_fields = planner_agent.diff_plan_fields(payload, updated)
+        self.assertIn("Tasks", changed_fields)
         self.assertEqual(updated.get("missing_fields"), [])
         self.assertIn("confirm plan", updated.get("next_question", "").lower())
 
@@ -87,8 +89,26 @@ class TestPlannerAgent(unittest.TestCase):
         )
         self.assertTrue(changed)
         self.assertIn("six week", (updated.get("timeline") or "").lower())
+        changed_fields = planner_agent.diff_plan_fields(payload, updated)
+        self.assertIn("Timeline", changed_fields)
         self.assertEqual(updated.get("missing_fields"), [])
 
+    def test_format_plan_draft_reply_order(self):
+        payload = {
+            "objective": "Build a platform",
+            "tasks": ["design it"],
+            "timeline": "four weeks",
+            "missing_fields": [],
+            "next_question": "Confirm plan?",
+        }
+        reply = planner_agent.format_plan_draft_reply(
+            payload,
+            changed_fields=["Objective", "Tasks"],
+        )
+        self.assertTrue(reply.startswith("**Updated:** Objective, Tasks"))
+        self.assertIn("**Next:**", reply)
+        self.assertLess(reply.find("**Next:**"), reply.find("**Plan Draft**"))
+
 
 if __name__ == "__main__":
     unittest.main()
diff --git a/tests/test_ui_actions.py b/tests/test_ui_actions.py
index e0bf52f8..f1b796ed 100644
--- a/tests/test_ui_actions.py
+++ b/tests/test_ui_actions.py
@@ -119,6 +119,7 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(data["draft_context"]["draft_type"], "plan")
             self.assertIn("**Plan Draft**", data["reply"])
             self.assertIn("**Next:**", data["reply"])
+            self.assertTrue(data["reply"].startswith("**Next:**"))
             
             # Verify DB update
             if hasattr(api, "suggestions_repository"):
@@ -201,6 +202,7 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(data["draft_context"]["draft_type"], "plan")
             self.assertIn("**Plan Draft**", data["reply"])
             self.assertIn("**Next:**", data["reply"])
+            self.assertTrue(data["reply"].startswith("**Next:**"))
 
     def test_plan_edit_reply_format(self):
         with ExitStack() as stack:
@@ -248,11 +250,55 @@ class TestApiUiActions(unittest.TestCase):
             resp = self.client.post("/api/message", json=payload)
             self.assertEqual(resp.status_code, 200)
             data = resp.get_json() or {}
+            self.assertTrue(data["reply"].startswith("**Updated:**"))
+            self.assertIn("**Next:**", data["reply"])
+            self.assertLess(data["reply"].find("**Next:**"), data["reply"].find("**Plan Draft**"))
             self.assertIn("**Plan Draft**", data["reply"])
             self.assertIn("**Objective:**", data["reply"])
             self.assertIn("**Tasks:**", data["reply"])
             self.assertIn("**Timeline:**", data["reply"])
 
+    def test_confirm_plan_does_not_route_to_goal(self):
+        with ExitStack() as stack:
+            if hasattr(api, "suggestions_repository"):
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "get_suggestion",
+                        return_value={
+                            "id": 999,
+                            "status": "pending",
+                            "kind": "plan",
+                            "payload": {"objective": "Test", "tasks": ["One"], "timeline": "soon"},
+                        },
+                    )
+                )
+                mock_update_status = stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "update_suggestion_status",
+                        return_value={"id": 999, "status": "accepted"},
+                    )
+                )
+
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+
+            payload = {
+                "message": "confirm plan",
+                "draft_id": 999,
+                "draft_type": "plan",
+                "conversation_id": 123,
+            }
+            resp = self.client.post("/api/message", json=payload)
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json() or {}
+            self.assertEqual(data.get("reply"), "PLAN_CONFIRMED.")
+            if hasattr(api, "suggestions_repository"):
+                mock_update_status.assert_called()
+
     def test_goal_edit_reply_format(self):
         with ExitStack() as stack:
             if hasattr(api, "suggestions_repository"):

```
