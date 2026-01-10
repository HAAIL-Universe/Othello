Cycle Status: COMPLETE

Todo Ledger:
- Planned: capture plans schema + repo anchors; fix confirm plan routing + persistence; update plan reply Updated/Next-first; extend build-mode trigger phrases; run tests + manual verification.
- Completed: Phase 1 evidence anchors captured; confirm plan routing + DB persistence (api.py); plan reply Updated/Next-first + diff detection (api.py, planner_agent.py); build-mode trigger phrases extended; unit tests run.
- Remaining: manual UI + DB verification steps from Phase 5.

Next Action: Run manual UI + DB verification steps and record results.

Evidence Bundle:
- /api/message is UI-only (not present in build_docs/openapi.yaml).
- Plans schema (columns + constraints):
  - db/schema.sql:121-138 (plans table columns/constraints), db/schema.sql:142-143 (indexes), db/schema.sql:135-141 (added columns + status/timezone/confirmed_at_utc).
  - db/database.py:294-318 (plans create + indexes + ALTERs).
- Plan items schema:
  - db/schema.sql:147-166 (plan_items columns + FK + unique), db/schema.sql:168-175 (altered columns).
  - db/database.py:319-350 (plan_items create + indexes + ALTERs).
- Plan persistence repo functions:
  - db/plan_repository.py:18 (upsert_plan), db/plan_repository.py:296 (upsert_plan_header), db/plan_repository.py:147 (replace_plan_items), db/plan_repository.py:347 (insert_plan_item_from_payload), db/plan_repository.py:269 (get_user_timezone).
- Plan draft flow (routing + edit lane + reply):
  - api.py:4632-4755 (confirm plan detection + persistence + PLAN_CONFIRMED reply), api.py:4981-5108 (plan edit lane + reply builder), planner_agent.py:46 (init_plan_draft_payload), planner_agent.py:109 (recompute_plan_missing_fields), planner_agent.py:185 (deterministic patcher), planner_agent.py:287 (LLM patcher), planner_agent.py:364 (format_plan_draft_reply).
- Build mode router/offer:
  - api.py:1714-1775 (_should_offer_build_mode_router), api.py:6479-6535 (offer injection + build_mode suggestion).

Verification Notes:
- Tests:
  - python -m unittest tests.test_planner_agent (pass)
  - python -m unittest tests.test_ui_actions (pass)
- Manual UI/DB verification: NOT RUN (ENVIRONMENT_LIMITATION: no UI/DB session in this run).

Unified Diff (excluding evidence/updatedifflog.md):
```
diff --git a/api.py b/api.py
index 610d0c82..96cb0902 100644
--- a/api.py
+++ b/api.py
@@ -1,3 +1,4 @@
+import copy
 import logging
 import os
 import re
@@ -1740,8 +1741,9 @@ def _should_offer_build_mode_router(
 
     # 2. Strong Triggers (Phrase Logic)
     strong_phrases = [
-        "build mode", "help me plan", "help me make a plan", "help me organize", 
-        "make a new plan", "create a new goal", "start a draft",
+        "build mode", "help me plan", "help me make a plan", "help me build a plan",
+        "help me organize", "make a plan", "make a new plan", "build a plan",
+        "plan for my cat", "create a new goal", "start a draft",
         "break this down",
         # Transferred from legacy hard-intercepts:
         "turn this into a goal", "make this a goal", "create a goal draft",
@@ -4632,12 +4634,18 @@ def handle_message():
         is_fuzzy_confirm = "confirm" in norm_input
         is_confirm_text_with_id = is_fuzzy_confirm and data.get("draft_id")
         clean_norm = re.sub(r"[^a-z0-9\s]", "", norm_input).strip()
-        is_confirm_plan_text = bool(re.search(r"\bconfirm\s+plan\b", clean_norm))
+        is_confirm_plan_text = bool(
+            re.search(
+                r"^\s*(?:ok(?:ay)?\s+)?(?:yes\s+)?confirm\s+plan\b",
+                clean_norm,
+            )
+        )
 
         if user_id and is_confirm_plan_text and data.get("draft_type") == "plan":
             draft_id = data.get("draft_id")
             draft = None
             if draft_id:
+                plan_row = None
                 try:
                     draft_id = int(draft_id)
                     draft = suggestions_repository.get_suggestion(user_id, draft_id)
@@ -4645,6 +4653,99 @@ def handle_message():
                     draft = None
 
             if draft and draft.get("status") == "pending" and draft.get("kind") == "plan":
+                draft_payload = draft.get("payload") or {}
+                date_local_input = (
+                    data.get("plan_date_local")
+                    or data.get("plan_date")
+                    or draft_payload.get("plan_date_local")
+                    or draft_payload.get("plan_date")
+                )
+                timezone_input = data.get("timezone") or draft_payload.get("timezone")
+                plan_date_local, timezone_name = _resolve_plan_date_and_timezone(
+                    user_id=user_id,
+                    date_local=date_local_input,
+                    timezone_name=timezone_input,
+                    logger=logger,
+                )
+                confirmed_at_utc = datetime.now(timezone.utc)
+
+                try:
+                    from db import plan_repository
+
+                    plan_row = plan_repository.upsert_plan_header(
+                        user_id=user_id,
+                        plan_date_local=plan_date_local,
+                        timezone=timezone_name,
+                        status="confirmed",
+                        confirmed_at_utc=confirmed_at_utc,
+                    )
+                    if not plan_row:
+                        raise RuntimeError("plan_upsert_failed")
+
+                    raw_tasks = draft_payload.get("tasks")
+                    tasks = (
+                        [str(t).strip() for t in raw_tasks if str(t).strip()]
+                        if isinstance(raw_tasks, list)
+                        else []
+                    )
+                    raw_resources = draft_payload.get("resources")
+                    resources = (
+                        [str(r).strip() for r in raw_resources if str(r).strip()]
+                        if isinstance(raw_resources, list)
+                        else []
+                    )
+                    generation_context = {
+                        "objective": draft_payload.get("objective"),
+                        "timeline": draft_payload.get("timeline"),
+                        "resources": resources,
+                        "tasks": tasks,
+                        "provenance": {
+                            "suggestion_id": draft_id,
+                            "draft_id": draft_id,
+                            "conversation_id": data.get("conversation_id"),
+                        },
+                    }
+                    plan_repository.upsert_plan(
+                        user_id=user_id,
+                        plan_date=plan_date_local,
+                        generation_context=generation_context,
+                        behavior_snapshot={},
+                    )
+
+                    if tasks:
+                        items = []
+                        for idx, task in enumerate(tasks, start=1):
+                            items.append(
+                                {
+                                    "item_id": f"draft:{draft_id}:{idx}",
+                                    "type": "plan_item",
+                                    "status": "planned",
+                                    "title": task,
+                                    "order_index": idx,
+                                    "source_kind": "plan_draft",
+                                    "source_id": str(draft_id),
+                                    "metadata": {
+                                        "label": task,
+                                        "draft_id": draft_id,
+                                    },
+                                }
+                            )
+                        plan_repository.replace_plan_items(
+                            plan_row.get("id"),
+                            items,
+                            user_id=user_id,
+                        )
+                except Exception as exc:
+                    logger.error(
+                        "Plan confirm persistence failed: %s",
+                        exc,
+                        exc_info=True,
+                    )
+                    return jsonify({
+                        "reply": "PLAN_CONFIRM_FAILED. I couldn't save the plan right now.",
+                        "request_id": request_id,
+                    })
+
                 suggestions_repository.update_suggestion_status(
                     user_id,
                     draft_id,
@@ -4654,6 +4755,8 @@ def handle_message():
                 return jsonify({
                     "reply": "PLAN_CONFIRMED.",
                     "draft_cleared": True,
+                    "plan_id": plan_row.get("id") if plan_row else None,
+                    "plan_date": plan_date_local.isoformat(),
                     "request_id": request_id,
                 })
 
@@ -4981,6 +5084,7 @@ def handle_message():
                 if draft and draft.get("status") == "pending":
                     # This is an edit instruction
                     current_payload = draft.get("payload", {})
+                    before_payload = copy.deepcopy(current_payload)
                     
                     # Plan Branch
                     if draft.get("kind") == "plan":
@@ -4996,7 +5100,7 @@ def handle_message():
                         suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
 
                         changed_fields = planner_agent.diff_plan_fields(
-                            current_payload,
+                            before_payload,
                             updated_payload,
                         )
                         reply_msg = planner_agent.format_plan_draft_reply(
diff --git a/planner_agent.py b/planner_agent.py
index 332fec87..03c3b036 100644
--- a/planner_agent.py
+++ b/planner_agent.py
@@ -166,6 +166,8 @@ def diff_plan_fields(
 
     before_timeline = _normalize_text(before.get("timeline"))
     after_timeline = _normalize_text(after.get("timeline"))
+    before_resources = _stringify_list(before.get("resources"))
+    after_resources = _stringify_list(after.get("resources"))
 
     changed = []
     if before_objective != after_objective:
@@ -174,6 +176,8 @@ def diff_plan_fields(
         changed.append("Tasks")
     if before_timeline != after_timeline:
         changed.append("Timeline")
+    if before_resources != after_resources:
+        changed.append("Resources")
 
     return changed
 
@@ -365,6 +369,7 @@ def format_plan_draft_reply(
     objective = payload.get("objective") or "(missing)"
     timeline = payload.get("timeline") or "(missing)"
     tasks = _stringify_list(payload.get("tasks"))
+    resources = _stringify_list(payload.get("resources"))
     next_line = _format_next_line(payload)
 
     lines = []
@@ -391,6 +396,11 @@ def format_plan_draft_reply(
     else:
         lines.append("(missing)")
 
+    if resources:
+        lines.append("**Resources:**")
+        for resource in resources:
+            lines.append(f"- {resource}")
+
     missing_line = _format_missing_line(payload)
     if missing_line:
         lines.append(missing_line)
diff --git a/tests/test_planner_agent.py b/tests/test_planner_agent.py
index 9190c802..e4b93e64 100644
--- a/tests/test_planner_agent.py
+++ b/tests/test_planner_agent.py
@@ -109,6 +109,22 @@ class TestPlannerAgent(unittest.TestCase):
         self.assertIn("**Next:**", reply)
         self.assertLess(reply.find("**Next:**"), reply.find("**Plan Draft**"))
 
+    def test_diff_plan_fields_resources(self):
+        before = {
+            "objective": "Build a platform",
+            "tasks": ["design it"],
+            "timeline": "four weeks",
+            "resources": ["me"],
+        }
+        after = {
+            "objective": "Build a platform",
+            "tasks": ["design it"],
+            "timeline": "four weeks",
+            "resources": ["me", "wood"],
+        }
+        changed_fields = planner_agent.diff_plan_fields(before, after)
+        self.assertIn("Resources", changed_fields)
+
 
 if __name__ == "__main__":
     unittest.main()
diff --git a/tests/test_ui_actions.py b/tests/test_ui_actions.py
index 8d6d32c5..2f1aa28c 100644
--- a/tests/test_ui_actions.py
+++ b/tests/test_ui_actions.py
@@ -280,6 +280,30 @@ class TestApiUiActions(unittest.TestCase):
                         return_value={"id": 999, "status": "accepted"},
                     )
                 )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.upsert_plan_header",
+                    return_value={"id": 321},
+                )
+            )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.get_user_timezone",
+                    return_value="UTC",
+                )
+            )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.upsert_plan",
+                    return_value={"id": 321},
+                )
+            )
+            mock_replace_items = stack.enter_context(
+                patch(
+                    "db.plan_repository.replace_plan_items",
+                    return_value=[],
+                )
+            )
 
             with self.client.session_transaction() as sess:
                 sess["authed"] = True
@@ -298,6 +322,7 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(data.get("reply"), "PLAN_CONFIRMED.")
             if hasattr(api, "suggestions_repository"):
                 mock_update_status.assert_called()
+            mock_replace_items.assert_called()
 
     def test_confirm_plan_with_punctuation(self):
         with ExitStack() as stack:
@@ -321,6 +346,30 @@ class TestApiUiActions(unittest.TestCase):
                         return_value={"id": 999, "status": "accepted"},
                     )
                 )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.upsert_plan_header",
+                    return_value={"id": 321},
+                )
+            )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.get_user_timezone",
+                    return_value="UTC",
+                )
+            )
+            stack.enter_context(
+                patch(
+                    "db.plan_repository.upsert_plan",
+                    return_value={"id": 321},
+                )
+            )
+            mock_replace_items = stack.enter_context(
+                patch(
+                    "db.plan_repository.replace_plan_items",
+                    return_value=[],
+                )
+            )
 
             with self.client.session_transaction() as sess:
                 sess["authed"] = True
@@ -339,6 +388,7 @@ class TestApiUiActions(unittest.TestCase):
             self.assertEqual(data.get("reply"), "PLAN_CONFIRMED.")
             if hasattr(api, "suggestions_repository"):
                 mock_update_status.assert_called()
+            mock_replace_items.assert_called()
 
     def test_goal_edit_reply_format(self):
         with ExitStack() as stack:
```
