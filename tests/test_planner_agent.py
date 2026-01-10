import os
import sys
import unittest

sys.path.append(os.getcwd())

import planner_agent  # noqa: E402


class TestPlannerAgent(unittest.TestCase):
    def test_determine_build_kind_stt_phrases(self):
        cases = [
            ("uh i think we need a project plan for this", "plan"),
            ("my goal is to run a marathon", "goal"),
            ("daily habit of reading", "routine"),
            ("add this to my to do list", "task"),
            ("not sure yet", None),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(planner_agent.determine_build_kind(text), expected)

    def test_patch_plan_draft_payload_deterministic(self):
        payload = planner_agent.init_plan_draft_payload()
        text = (
            "Objective is to build a physical play platform for my cat Storm. "
            "Main tasks are design it, buy materials, build it, and check safety. "
            "Timeline is four weeks. Resources are just me."
        )
        updated, changed = planner_agent.patch_plan_draft_payload_deterministic(text, payload)
        self.assertTrue(changed)
        self.assertEqual(
            updated.get("objective"),
            "to build a physical play platform for my cat Storm",
        )
        self.assertEqual(
            updated.get("tasks"),
            ["design it", "buy materials", "build it", "check safety"],
        )
        self.assertEqual(updated.get("timeline"), "four weeks")
        self.assertEqual(updated.get("missing_fields"), [])
        self.assertIn("confirm plan", updated.get("next_question", "").lower())

    def test_patch_plan_draft_payload_add_task(self):
        payload = {
            "objective": "Refactor module",
            "tasks": ["outline steps"],
            "timeline": None,
        }
        updated, changed = planner_agent.patch_plan_draft_payload_deterministic(
            "add task write tests",
            payload,
        )
        self.assertTrue(changed)
        self.assertEqual(updated.get("tasks"), ["outline steps", "write tests"])

    def test_patch_plan_draft_payload_add_task_phrase(self):
        payload = {
            "objective": "Build a platform",
            "tasks": ["design it", "buy materials", "build it", "check safety"],
            "timeline": "four weeks",
        }
        updated, changed = planner_agent.patch_plan_draft_payload_deterministic(
            "Add a task to measure the space and pick dimensions.",
            payload,
        )
        self.assertTrue(changed)
        self.assertEqual(len(updated.get("tasks") or []), 5)
        self.assertTrue(
            any(
                "measure the space and pick dimensions" in task.lower()
                for task in updated.get("tasks", [])
            )
        )
        changed_fields = planner_agent.diff_plan_fields(payload, updated)
        self.assertIn("Tasks", changed_fields)
        self.assertEqual(updated.get("missing_fields"), [])
        self.assertIn("confirm plan", updated.get("next_question", "").lower())

    def test_patch_plan_draft_payload_timeline_delta(self):
        payload = {
            "objective": "Build a platform",
            "tasks": ["design it", "buy materials", "build it", "check safety"],
            "timeline": "four weeks",
        }
        updated, changed = planner_agent.patch_plan_draft_payload_deterministic(
            "Timeline might slip because of deliveries, maybe six weeks instead.",
            payload,
        )
        self.assertTrue(changed)
        self.assertIn("six week", (updated.get("timeline") or "").lower())
        changed_fields = planner_agent.diff_plan_fields(payload, updated)
        self.assertIn("Timeline", changed_fields)
        self.assertEqual(updated.get("missing_fields"), [])

    def test_format_plan_draft_reply_order(self):
        payload = {
            "objective": "Build a platform",
            "tasks": ["design it"],
            "timeline": "four weeks",
            "missing_fields": [],
            "next_question": "Confirm plan?",
        }
        reply = planner_agent.format_plan_draft_reply(
            payload,
            changed_fields=["Objective", "Tasks"],
        )
        self.assertTrue(reply.startswith("**Updated:** Objective, Tasks"))
        self.assertIn("**Next:**", reply)
        self.assertLess(reply.find("**Next:**"), reply.find("**Plan Draft**"))

    def test_diff_plan_fields_resources(self):
        before = {
            "objective": "Build a platform",
            "tasks": ["design it"],
            "timeline": "four weeks",
            "resources": ["me"],
        }
        after = {
            "objective": "Build a platform",
            "tasks": ["design it"],
            "timeline": "four weeks",
            "resources": ["me", "wood"],
        }
        changed_fields = planner_agent.diff_plan_fields(before, after)
        self.assertIn("Resources", changed_fields)


if __name__ == "__main__":
    unittest.main()
