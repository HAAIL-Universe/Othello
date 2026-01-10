Cycle Status: COMPLETE

Todo Ledger:
- Planned: add recompute helper for plan missing_fields/next_question; strengthen add-task parsing; update tests for recompute + add-task delta; verify via unit tests.
- Completed: added recompute_plan_missing_fields; wired recompute into deterministic + LLM patchers; broadened add-task handling; updated planner_agent tests; ran unit tests.
- Remaining: manual UI verification (not run in this session).

File:Line Anchors:
- Plan missing_fields recompute helper: planner_agent.py:109-146
- Add-task regex + append logic: planner_agent.py:208-231
- Recompute call after deterministic patch: planner_agent.py:233
- Recompute call after LLM patch: planner_agent.py:267-271
- Tests for recompute + add-task delta: tests/test_planner_agent.py:23-76

Verification Notes:
- Test 4 (STT blob): "Objective is to build a physical play platform for my cat Storm. Main tasks are design it, buy materials, build it, and check safety. Timeline is four weeks. Resources are just me."
  - Expected: missing_fields [] and next_question confirm/edit prompt.
- Test 5 (delta add-task): "Add a task to measure the space and pick dimensions."
  - Expected: tasks appended with the phrase; missing_fields stays [].
- Unit tests: `python -m unittest tests.test_planner_agent` (pass).
- Manual UI flow: not run in this session.

Unified diff (excluding diff log itself):
```diff
diff --git a/planner_agent.py b/planner_agent.py
index 9954b579..9bb21599 100644
--- a/planner_agent.py
+++ b/planner_agent.py
@@ -106,6 +106,46 @@ def _coerce_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
     return {}
 
 
+def recompute_plan_missing_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
+    data = _coerce_payload(payload)
+    missing = []
+
+    objective = data.get("objective")
+    if not isinstance(objective, str) or not objective.strip():
+        missing.append("objective")
+
+    tasks_value = data.get("tasks")
+    tasks_list = tasks_value if isinstance(tasks_value, list) else []
+    cleaned_tasks = [str(task).strip() for task in tasks_list if str(task).strip()]
+    if cleaned_tasks:
+        data["tasks"] = cleaned_tasks
+    else:
+        missing.append("tasks")
+
+    timeline = data.get("timeline")
+    if not isinstance(timeline, str) or not timeline.strip():
+        missing.append("timeline")
+
+    data["missing_fields"] = missing
+
+    if missing:
+        prompt_map = {
+            "objective": "What is the objective of the plan?",
+            "tasks": "What are the tasks?",
+            "timeline": "What is the timeline?",
+        }
+        data["next_question"] = prompt_map.get(
+            missing[0], "What is the objective of the plan?"
+        )
+    else:
+        data["next_question"] = (
+            "If that looks right, say 'confirm plan'. "
+            "Or tell me what to change (add/remove tasks, change timeline, tweak objective)."
+        )
+
+    return data
+
+
 def patch_plan_draft_payload_deterministic(
     text: str, payload: Dict[str, Any]
 ) -> Tuple[Dict[str, Any], bool]:
@@ -166,7 +206,11 @@ def patch_plan_draft_payload_deterministic(
             break
 
     add_tasks_text = None
-    match = re.search(r"\badd\s+task\s+(?P<value>[^.]+)", text, flags=re.IGNORECASE)
+    match = re.search(
+        r"\b(?:can\s+you\s+)?add\s+(?:another\s+|a\s+|an\s+|new\s+)?task(?:\s+to)?\s+(?P<value>[^.]+)",
+        text,
+        flags=re.IGNORECASE,
+    )
     if match:
         add_tasks_text = _trim_at_keywords(match.group("value"))
 
@@ -178,13 +222,15 @@ def patch_plan_draft_payload_deterministic(
             changed = True
 
     if add_tasks_text:
-        parsed = _split_tasks(add_tasks_text)
-        existing = updated_payload.get("tasks") or []
-        merged = _dedupe_tasks(existing + parsed)
+        task = _clean_fragment(add_tasks_text)
+        existing = updated_payload.get("tasks")
+        existing = existing if isinstance(existing, list) else []
+        merged = _dedupe_tasks(existing + ([task] if task else []))
         if merged != existing:
             updated_payload["tasks"] = merged
             changed = True
 
+    updated_payload = recompute_plan_missing_fields(updated_payload)
     return updated_payload, changed
 
 
@@ -218,10 +264,11 @@ def patch_plan_draft_payload_llm(
             response_format={"type": "json_object"},
         )
         content = response.choices[0].message.content
-        return json.loads(content)
+        updated_payload = json.loads(content)
+        return recompute_plan_missing_fields(updated_payload)
     except Exception as exc:
         logging.error("Failed to patch plan draft payload: %s", exc)
-        return payload
+        return recompute_plan_missing_fields(payload)
 
 
 def _stringify_list(value: Any) -> list[str]:
diff --git a/tests/test_planner_agent.py b/tests/test_planner_agent.py
index 671ec0b8..3d2475cf 100644
--- a/tests/test_planner_agent.py
+++ b/tests/test_planner_agent.py
@@ -38,6 +38,8 @@ class TestPlannerAgent(unittest.TestCase):
             ["design it", "buy materials", "build it", "check safety"],
         )
         self.assertEqual(updated.get("timeline"), "four weeks")
+        self.assertEqual(updated.get("missing_fields"), [])
+        self.assertIn("confirm plan", updated.get("next_question", "").lower())
 
     def test_patch_plan_draft_payload_add_task(self):
         payload = {
@@ -52,6 +54,27 @@ class TestPlannerAgent(unittest.TestCase):
         self.assertTrue(changed)
         self.assertEqual(updated.get("tasks"), ["outline steps", "write tests"])
 
+    def test_patch_plan_draft_payload_add_task_phrase(self):
+        payload = {
+            "objective": "Build a platform",
+            "tasks": ["design it", "buy materials", "build it", "check safety"],
+            "timeline": "four weeks",
+        }
+        updated, changed = planner_agent.patch_plan_draft_payload_deterministic(
+            "Add a task to measure the space and pick dimensions.",
+            payload,
+        )
+        self.assertTrue(changed)
+        self.assertEqual(len(updated.get("tasks") or []), 5)
+        self.assertTrue(
+            any(
+                "measure the space and pick dimensions" in task.lower()
+                for task in updated.get("tasks", [])
+            )
+        )
+        self.assertEqual(updated.get("missing_fields"), [])
+        self.assertIn("confirm plan", updated.get("next_question", "").lower())
+
 
 if __name__ == "__main__":
     unittest.main()

```
