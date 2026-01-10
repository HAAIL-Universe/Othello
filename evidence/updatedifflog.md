Cycle Status: COMPLETE

Todo Ledger:
- Planned: loosen confirm plan match to tolerate punctuation; add regression test; run tests; update log; commit.
- Completed: normalized confirm plan input and regex match; added punctuation test; ran `python -m unittest tests.test_ui_actions`.
- Remaining: none.

Next Action:
- Commit with message `Fix: confirm plan punctuation routing`.

Git Status (porcelain):
M api.py
 M tests/test_ui_actions.py

Verification Notes:
- Tests: `python -m unittest tests.test_ui_actions` (pass).

Unified diff (excluding diff log itself):
```diff
diff --git a/api.py b/api.py
index 4341233d..610d0c82 100644
--- a/api.py
+++ b/api.py
@@ -4631,8 +4631,10 @@ def handle_message():
         is_confirm_goal_text = norm_input == "confirm goal"
         is_fuzzy_confirm = "confirm" in norm_input
         is_confirm_text_with_id = is_fuzzy_confirm and data.get("draft_id")
+        clean_norm = re.sub(r"[^a-z0-9\s]", "", norm_input).strip()
+        is_confirm_plan_text = bool(re.search(r"\bconfirm\s+plan\b", clean_norm))
 
-        if user_id and norm_input == "confirm plan" and data.get("draft_type") == "plan":
+        if user_id and is_confirm_plan_text and data.get("draft_type") == "plan":
             draft_id = data.get("draft_id")
             draft = None
             if draft_id:
diff --git a/tests/test_ui_actions.py b/tests/test_ui_actions.py
index f1b796ed..8d6d32c5 100644
--- a/tests/test_ui_actions.py
+++ b/tests/test_ui_actions.py
@@ -299,6 +299,47 @@ class TestApiUiActions(unittest.TestCase):
             if hasattr(api, "suggestions_repository"):
                 mock_update_status.assert_called()
 
+    def test_confirm_plan_with_punctuation(self):
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
+                "message": "Confirm plan.",
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
