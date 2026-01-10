Cycle Status: COMPLETE

Todo Ledger:
- Planned: update tests to assert formatted draft replies; add plan/goal edit format tests; run focused tests; update log.
- Completed: updated `tests/test_ui_actions.py` with build/plan/goal reply assertions; added plan/goal edit format tests; ran `python -m unittest tests.test_ui_actions tests.test_planner_agent`; prepared commit per directive.
- Remaining: none.

Next Action:
- None.

Verification Notes:
- Manual UI flow (evidence from prior cycle):
  - Enter build mode (POST /api/message ui_action=enter_build_mode_from_message) -> reply includes **Build Mode**; evidence/build_gate_resp_fmt.json.
  - Select plan (message="plan") -> reply includes **Plan Draft** and **Next:**; evidence/build_plan_resp_fmt.json.
  - Plan edit STT input: "Objective is to build a play platform for my cat Storm. Main tasks are design it, buy materials, build it, and check safety. Timeline is four weeks. Resources are just me." -> reply includes Objective/Tasks/Timeline/Missing/Next; evidence/plan_edit_resp_fmt.json.
- Tests: `python -m unittest tests.test_ui_actions tests.test_planner_agent` (pass).

Unified diff (excluding diff log itself):
```diff
diff --git a/tests/test_ui_actions.py b/tests/test_ui_actions.py
index c6bc6e44..e0bf52f8 100644
--- a/tests/test_ui_actions.py
+++ b/tests/test_ui_actions.py
@@ -82,7 +82,9 @@ class TestApiUiActions(unittest.TestCase):
             # Assert Type Gate
             self.assertIn("draft_context", data)
             self.assertEqual(data["draft_context"]["draft_type"], "build", "Expected draft_type='build' (pending)")
+            self.assertIn("**Build Mode**", data["reply"])
             self.assertIn("What are we building", data["reply"], "Reply should ask for type")
+            self.assertIn("**Missing:**", data["reply"])
 
             # Verify call
             if hasattr(api, "suggestions_repository"):
@@ -115,6 +117,8 @@ class TestApiUiActions(unittest.TestCase):
             
             # Assert Transition
             self.assertEqual(data["draft_context"]["draft_type"], "plan")
+            self.assertIn("**Plan Draft**", data["reply"])
+            self.assertIn("**Next:**", data["reply"])
             
             # Verify DB update
             if hasattr(api, "suggestions_repository"):
@@ -179,6 +183,7 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(resp.status_code, 200)
             data = resp.get_json() or {}
             self.assertEqual(data["draft_context"]["draft_type"], "build")
+            self.assertIn("**Build Mode**", data["reply"])
             self.assertIn("What are we building", data["reply"])
 
             draft_id = data["draft_context"]["draft_id"]
@@ -194,7 +199,119 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(resp.status_code, 200)
             data = resp.get_json() or {}
             self.assertEqual(data["draft_context"]["draft_type"], "plan")
-            self.assertIn("objective", data["reply"].lower())
+            self.assertIn("**Plan Draft**", data["reply"])
+            self.assertIn("**Next:**", data["reply"])
+
+    def test_plan_edit_reply_format(self):
+        with ExitStack() as stack:
+            if hasattr(api, "suggestions_repository"):
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "get_suggestion",
+                        return_value={
+                            "status": "pending",
+                            "kind": "plan",
+                            "payload": {
+                                "objective": None,
+                                "tasks": [],
+                                "timeline": None,
+                                "missing_fields": ["objective", "tasks", "timeline"],
+                                "next_question": "What is the objective of the plan?",
+                            },
+                        },
+                    )
+                )
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "update_suggestion_payload",
+                        return_value={},
+                    )
+                )
+
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+
+            payload = {
+                "message": (
+                    "Objective is to build a play platform. "
+                    "Main tasks are design it, buy materials. "
+                    "Timeline is four weeks."
+                ),
+                "draft_id": 999,
+                "draft_type": "plan",
+                "conversation_id": 123,
+            }
+            resp = self.client.post("/api/message", json=payload)
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json() or {}
+            self.assertIn("**Plan Draft**", data["reply"])
+            self.assertIn("**Objective:**", data["reply"])
+            self.assertIn("**Tasks:**", data["reply"])
+            self.assertIn("**Timeline:**", data["reply"])
+
+    def test_goal_edit_reply_format(self):
+        with ExitStack() as stack:
+            if hasattr(api, "suggestions_repository"):
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "get_suggestion",
+                        return_value={
+                            "status": "pending",
+                            "kind": "goal",
+                            "payload": {
+                                "title": "Test Goal",
+                                "steps": ["Step one"],
+                                "missing_fields": ["timeline"],
+                                "next_question": "What is the timeline?",
+                            },
+                        },
+                    )
+                )
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "update_suggestion_payload",
+                        return_value={},
+                    )
+                )
+
+            updated_payload = {
+                "title": "Test Goal",
+                "steps": ["Step one", "Step two"],
+                "missing_fields": ["timeline"],
+                "next_question": "What is the timeline?",
+            }
+
+            stack.enter_context(
+                patch.object(
+                    api,
+                    "_apply_goal_draft_deterministic_edit",
+                    return_value=(updated_payload, True, "Updated the draft."),
+                )
+            )
+
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+
+            payload = {
+                "message": "add step",
+                "draft_id": 999,
+                "draft_type": "goal",
+                "conversation_id": 123,
+            }
+            resp = self.client.post("/api/message", json=payload)
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json() or {}
+            self.assertIn("**Goal Draft**", data["reply"])
+            self.assertIn("**Title:**", data["reply"])
+            self.assertIn("**Steps:**", data["reply"])
 
 
 if __name__ == "__main__":

```
