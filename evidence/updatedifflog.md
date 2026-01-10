Cycle Status: COMPLETE

Todo Ledger:
- Planned: reproduce failure, confirm missing function, add update_suggestion_kind, add regression test, re-verify.
- Completed: reproduced failure and captured stack trace, confirmed missing function, added update_suggestion_kind, added regression test, re-verified build gate.
- Remaining: none.

Evidence Bundle:
- Failing callsite in log: api.py:4926 (stack trace in evidence/server.err shows AttributeError on suggestions_repository.update_suggestion_kind).
- Missing function before fix: db/suggestions_repository.py showed update_suggestion_status at db/suggestions_repository.py:41 and update_suggestion_payload at db/suggestions_repository.py:58 with no update_suggestion_kind.
- Fix location: db/suggestions_repository.py:72 defines update_suggestion_kind.
- OpenAPI confirmation: /api/message is not listed in build_docs/openapi.yaml (UI-only route).

Verification:
- Action: POST /api/message with ui_action=enter_build_mode_from_message, then POST /api/message with draft_type="build" and message="plan".
- Result: 200 response; draft transitioned to plan.
- Evidence: evidence/build_plan_resp_fix.json shows draft_context.draft_type == "plan" and draft_payload.next_question set.

Unified Diff:
`diff
diff --git a/db/suggestions_repository.py b/db/suggestions_repository.py
index 69733a04..ac76fefc 100644
--- a/db/suggestions_repository.py
+++ b/db/suggestions_repository.py
@@ -69,6 +69,22 @@ def update_suggestion_payload(
     return execute_and_fetch_one(query, (Json(payload), suggestion_id, user_id))
 
 
+def update_suggestion_kind(
+    user_id: str,
+    suggestion_id: int,
+    kind: str,
+    payload: Dict[str, Any],
+) -> Optional[Dict[str, Any]]:
+    query = """
+        UPDATE suggestions
+        SET kind = %s,
+            payload = %s
+        WHERE id = %s AND user_id = %s
+        RETURNING id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
+    """
+    return execute_and_fetch_one(query, (kind, Json(payload), suggestion_id, user_id))
+
+
 def list_suggestions(
     *,
     user_id: str,
diff --git a/tests/test_ui_actions.py b/tests/test_ui_actions.py
new file mode 100644
index 00000000..c6bc6e44
--- /dev/null
+++ b/tests/test_ui_actions.py
@@ -0,0 +1,201 @@
+import os
+import sys
+import unittest
+from contextlib import ExitStack
+from unittest.mock import MagicMock, patch
+
+# Ensure we can import api from repo root
+sys.path.append(os.getcwd())
+
+import api  # noqa: E402
+
+
+class TestApiUiActions(unittest.TestCase):
+    def setUp(self):
+        self.app = api.app
+        self.app.config["TESTING"] = True
+        self.client = self.app.test_client()
+
+    def _patch_llmwrapper(self, stack: ExitStack):
+        """
+        Patch LLMWrapper at the location api.py actually references.
+        We try the most likely bindings in-order.
+        """
+        if hasattr(api, "LLMWrapper"):
+            return stack.enter_context(patch.object(api, "LLMWrapper"))
+        if hasattr(api, "llm_wrapper") and hasattr(api.llm_wrapper, "LLMWrapper"):
+            return stack.enter_context(patch.object(api.llm_wrapper, "LLMWrapper"))
+
+        # Fallback (only if present in this repo)
+        try:
+            import core.llm_wrapper as _lw  # noqa: F401
+        except Exception:
+            _lw = None
+        if _lw is not None and hasattr(_lw, "LLMWrapper"):
+            return stack.enter_context(patch("core.llm_wrapper.LLMWrapper"))
+
+        raise RuntimeError(
+            "Could not locate LLMWrapper to patch. Add a patch target that matches api.py imports."
+        )
+
+    def test_enter_build_mode_ui_action_allows_empty_message(self):
+        """
+        Regression test:
+        UI button clicks commonly send message="" with ui_action set.
+        This MUST still trigger enter_build_mode_from_message.
+        UPDATED (Phase 3B): Must return type-pending 'build' draft (Type Gate).
+        """
+
+        with ExitStack() as stack:
+            # Patch LLMWrapper (where api references it)
+            self._patch_llmwrapper(stack)
+
+            # Patch suggestions repo (where api references it)
+            if hasattr(api, "suggestions_repository"):
+                mock_create_suggestion = stack.enter_context(
+                    patch.object(api.suggestions_repository, "create_suggestion", return_value={"id": 999, "kind": "build"}, create=True)
+                )
+            
+            # Patch context lookup
+            if hasattr(api, "messages_repository"):
+                 stack.enter_context(patch.object(api.messages_repository, "get_latest_active_draft_context", return_value=None, create=True))
+                 stack.enter_context(patch.object(api.messages_repository, "get_linked_messages_from_checkpoint", return_value=[], create=True))
+
+            # Authenticate session
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+
+            payload = {
+                "message": "",  # critical regression case
+                "ui_action": "enter_build_mode_from_message",
+                "conversation_id": 123,
+                "channel": "companion",
+            }
+
+            resp = self.client.post("/api/message", json=payload)
+
+            self.assertEqual(resp.status_code, 200, f"Expected 200 OK, got {resp.status_code}: {resp.data}")
+            data = resp.get_json() or {}
+
+            # Assert Type Gate
+            self.assertIn("draft_context", data)
+            self.assertEqual(data["draft_context"]["draft_type"], "build", "Expected draft_type='build' (pending)")
+            self.assertIn("What are we building", data["reply"], "Reply should ask for type")
+
+            # Verify call
+            if hasattr(api, "suggestions_repository"):
+                mock_create_suggestion.assert_called()
+                self.assertEqual(mock_create_suggestion.call_args[1]["kind"], "build")
+
+    def test_build_mode_type_selection_transitions_to_plan(self):
+        with ExitStack() as stack:
+            if hasattr(api, "suggestions_repository"):
+                # Mock update_suggestion_kind
+                mock_update = stack.enter_context(
+                    patch.object(api.suggestions_repository, "update_suggestion_kind", return_value={})
+                )
+
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+            
+            # User replies "Plan" to the gate
+            payload = {
+                "message": "Plan",
+                "draft_id": 999,
+                "draft_type": "build",
+                "conversation_id": 123
+            }
+            resp = self.client.post("/api/message", json=payload)
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json()
+            
+            # Assert Transition
+            self.assertEqual(data["draft_context"]["draft_type"], "plan")
+            
+            # Verify DB update
+            if hasattr(api, "suggestions_repository"):
+                mock_update.assert_called()
+                args = mock_update.call_args[0]
+                self.assertEqual(args[2], "plan")
+
+    def test_build_mode_flow_prompts_objective(self):
+        with ExitStack() as stack:
+            self._patch_llmwrapper(stack)
+
+            if hasattr(api, "suggestions_repository"):
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "create_suggestion",
+                        return_value={"id": 1001, "kind": "build"},
+                        create=True,
+                    )
+                )
+                stack.enter_context(
+                    patch.object(
+                        api.suggestions_repository,
+                        "update_suggestion_kind",
+                        return_value={},
+                        create=True,
+                    )
+                )
+
+            if hasattr(api, "messages_repository"):
+                stack.enter_context(
+                    patch.object(
+                        api.messages_repository,
+                        "get_latest_active_draft_context",
+                        return_value=None,
+                        create=True,
+                    )
+                )
+                stack.enter_context(
+                    patch.object(
+                        api.messages_repository,
+                        "get_linked_messages_from_checkpoint",
+                        return_value=[],
+                        create=True,
+                    )
+                )
+
+            with self.client.session_transaction() as sess:
+                sess["authed"] = True
+                sess["user_id"] = "test_user"
+                sess["conversation_id"] = 123
+
+            resp = self.client.post(
+                "/api/message",
+                json={
+                    "message": "",
+                    "ui_action": "enter_build_mode_from_message",
+                    "conversation_id": 123,
+                    "channel": "companion",
+                },
+            )
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json() or {}
+            self.assertEqual(data["draft_context"]["draft_type"], "build")
+            self.assertIn("What are we building", data["reply"])
+
+            draft_id = data["draft_context"]["draft_id"]
+            resp = self.client.post(
+                "/api/message",
+                json={
+                    "message": "plan",
+                    "draft_id": draft_id,
+                    "draft_type": "build",
+                    "conversation_id": 123,
+                },
+            )
+            self.assertEqual(resp.status_code, 200)
+            data = resp.get_json() or {}
+            self.assertEqual(data["draft_context"]["draft_type"], "plan")
+            self.assertIn("objective", data["reply"].lower())
+
+
+if __name__ == "__main__":
+    unittest.main()

`

Next Action: commit only db/suggestions_repository.py, tests/test_ui_actions.py, and evidence/updatedifflog.md with message "Fix: restore update_suggestion_kind for build-mode gate".
