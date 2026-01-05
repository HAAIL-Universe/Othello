import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add workspace to path
sys.path.append(os.getcwd())

# Mock database connection before importing api to avoid connection errors
sys.modules['db.database'] = MagicMock()
sys.modules['db.suggestions_repository'] = MagicMock()

from api import app

class TestPhase11(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.user_id = "test_user_phase11"
        
    @patch('api.suggestions_repository')
    def test_deterministic_edit_title(self, MockRepo):
        print("\n--- Testing Deterministic Edit: Title ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Old Title",
                "target_days": 7,
                "steps": ["Step 1"],
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        payload = {
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "Change title to New Deterministic Title"
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response:", json.dumps(data, indent=2))
        
        self.assertEqual(data["draft_payload"]["title"], "New Deterministic Title")
        self.assertIn("Updated title to 'New Deterministic Title'", data["reply"])
        # Ensure other fields preserved
        self.assertEqual(data["draft_payload"]["target_days"], 7)
        self.assertEqual(data["draft_payload"]["steps"], ["Step 1"])

    @patch('api.suggestions_repository')
    def test_deterministic_edit_step(self, MockRepo):
        print("\n--- Testing Deterministic Edit: Step ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Old Title",
                "target_days": 7,
                "steps": ["Step 1", "Step 2"],
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        payload = {
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "Change step 2 to Updated Step 2"
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response:", json.dumps(data, indent=2))
        
        self.assertEqual(data["draft_payload"]["steps"][1], "Updated Step 2")
        self.assertIn("Updated step 2", data["reply"])
        # Ensure title preserved
        self.assertEqual(data["draft_payload"]["title"], "Old Title")

    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_llm_fallback_regression_prevention(self, MockLLM, MockRepo):
        print("\n--- Testing LLM Fallback Regression Prevention ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Preserved Title",
                "target_days": 7,
                "steps": ["Step 1"],
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        # Mock LLM returning a regression (missing title, wrong steps)
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.chat_completion.return_value.choices[0].message.content = json.dumps({
            "title": "Regressed Title", # Should be ignored if user didn't ask to change title
            "target_days": 7,
            "steps": [], # Should be ignored if user didn't ask to change steps
            "body": "Body"
        })
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        # User asks to change something unrelated to title/steps (e.g. body, or just general chat that triggers edit)
        # Actually, if it's general chat, it might not trigger edit unless it's interpreted as such.
        # But here we are testing _patch_goal_draft_payload logic specifically.
        # Let's say user says "make the description better" (which is body).
        # The regexes won't match, so it goes to LLM.
        
        payload = {
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "Make the description better"
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response:", json.dumps(data, indent=2))
        
        # Title should be preserved because user didn't mention title
        self.assertEqual(data["draft_payload"]["title"], "Preserved Title")
        # Steps should be preserved because user didn't mention steps
        self.assertEqual(data["draft_payload"]["steps"], ["Step 1"])

if __name__ == '__main__':
    unittest.main()
