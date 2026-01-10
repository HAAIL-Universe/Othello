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


if __name__ == "__main__":
    unittest.main()
