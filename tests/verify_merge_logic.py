
import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from core.day_planner import DayPlanner

class TestMergeLogic(unittest.TestCase):
    def setUp(self):
        self.planner = DayPlanner()
        self.planner.logger = MagicMock()
        
    @patch('core.day_planner.routines_repository')
    def test_merge_fresh_routines_idempotency(self, mock_repo):
        # Setup
        user_id = "test_user"
        target_date = date(2023, 10, 27) # A Friday
        
        # Mock DB routines
        mock_routines = [
            {
                "id": "r1",
                "title": "Morning Routine",
                "enabled": True,
                "schedule_rule": {"days": ["fri"]},
                "steps": [{"id": "s1", "title": "Step 1", "est_minutes": 10}]
            },
            {
                "id": "r2",
                "title": "Evening Routine",
                "enabled": True,
                "schedule_rule": {"days": ["fri"]},
                "steps": []
            }
        ]
        mock_repo.list_routines_with_steps.return_value = mock_routines
        
        # Initial Plan (Empty)
        plan = {"sections": {"routines": []}}
        
        # 1. First Merge
        self.planner._merge_fresh_routines(user_id, target_date, plan)
        
        # Verify both added
        self.assertEqual(len(plan["sections"]["routines"]), 2)
        self.assertEqual(plan["sections"]["routines"][0]["id"], "r1")
        self.assertEqual(plan["sections"]["routines"][0]["title"], "Morning Routine") # Verify title key
        self.assertEqual(plan["sections"]["routines"][1]["id"], "r2")
        
        # 2. Second Merge (Idempotency Check)
        self.planner._merge_fresh_routines(user_id, target_date, plan)
        
        # Verify count unchanged
        self.assertEqual(len(plan["sections"]["routines"]), 2)
        
    @patch('core.day_planner.routines_repository')
    def test_merge_preserves_progress(self, mock_repo):
        # Setup
        user_id = "test_user"
        target_date = date(2023, 10, 27) # A Friday
        
        # Mock DB routines (r1 is enabled)
        mock_routines = [
            {
                "id": "r1",
                "title": "Morning Routine",
                "enabled": True,
                "schedule_rule": {"days": ["fri"]},
                "steps": []
            }
        ]
        mock_repo.list_routines_with_steps.return_value = mock_routines
        
        # Existing Plan with r1 in progress
        plan = {
            "sections": {
                "routines": [
                    {
                        "id": "r1",
                        "status": "in_progress", # User progress
                        "name": "Morning Routine"
                    }
                ]
            }
        }
        
        # Merge
        self.planner._merge_fresh_routines(user_id, target_date, plan)
        
        # Verify r1 is NOT overwritten
        self.assertEqual(len(plan["sections"]["routines"]), 1)
        self.assertEqual(plan["sections"]["routines"][0]["status"], "in_progress")

if __name__ == '__main__':
    unittest.main()
