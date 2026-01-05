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

class TestPhase12(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.user_id = "test_user_phase12"
        
    @patch('api.suggestions_repository')
    def test_deterministic_edit_gaps(self, MockRepo):
        print("\n--- Testing Deterministic Edit: Gaps ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Test Goal",
                "target_days": 7,
                "steps": [], # Empty steps
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        # Try to set step 2 when no steps exist
        payload = {
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "Change step 2 to Step 2"
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response (Gap):", json.dumps(data, indent=2))
        
        # Should NOT update payload
        self.assertEqual(len(data["draft_payload"]["steps"]), 0)
        self.assertIn("No steps exist yet", data["reply"])

        # Try to set step 1
        payload["message"] = "Change step 1 to Step 1"
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response (Step 1):", json.dumps(data, indent=2))
        
        # Should update payload
        self.assertEqual(len(data["draft_payload"]["steps"]), 1)
        self.assertEqual(data["draft_payload"]["steps"][0], "Step 1")
        self.assertIn("Added step 1", data["reply"])

    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_generate_steps_idempotency(self, MockLLM, MockRepo):
        print("\n--- Testing Generate Steps Idempotency ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Test Goal",
                "target_days": 7,
                "steps": ["1", "2", "3", "4", "5"], # Already 5 steps
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        payload = {
            "ui_action": "generate_draft_steps",
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": ""
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response (Idempotency):", json.dumps(data, indent=2))
        
        # Should return existing steps and not call LLM (mock LLM not set up to return anything, so if called it would fail or return None if not mocked properly, but here we check reply)
        self.assertIn("Steps already generated (5)", data["reply"])
        self.assertEqual(len(data["draft_payload"]["steps"]), 5)
        
        # Verify LLM was NOT called
        MockLLM.return_value.chat_completion.assert_not_called()

    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_regenerate_steps(self, MockLLM, MockRepo):
        print("\n--- Testing Regenerate Steps ---")
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Test Goal",
                "target_days": 7,
                "steps": ["Old Step"],
                "body": "Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        # Mock LLM response
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.chat_completion.return_value.choices[0].message.content = json.dumps({
            "title": "Test Goal",
            "target_days": 7,
            "steps": ["New Step 1", "New Step 2", "New Step 3", "New Step 4", "New Step 5"],
            "body": "Body"
        })
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        payload = {
            "ui_action": "regenerate_draft_steps",
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": ""
        }
        
        response = self.client.post('/api/message', json=payload)
        data = response.get_json()
        
        print("Response (Regenerate):", json.dumps(data, indent=2))
        
        # Should have new steps
        self.assertEqual(len(data["draft_payload"]["steps"]), 5)
        self.assertEqual(data["draft_payload"]["steps"][0], "New Step 1")
        self.assertIn("I've generated 5 steps", data["reply"])

if __name__ == '__main__':
    unittest.main()
