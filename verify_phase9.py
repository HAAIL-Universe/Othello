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

class TestPhase9(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.user_id = "test_user_phase9"
        
    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_generate_steps_fallback(self, MockLLM, MockRepo):
        print("\n--- Testing Generate Steps Fallback ---")
        # Setup Mock LLM to fail
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.chat_completion.side_effect = Exception("LLM Failed")
        
        # Setup Mock Repo
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Test Goal",
                "target_days": 7,
                "steps": [],
                "body": "Test Body"
            }
        }
        MockRepo.update_suggestion_payload.return_value = True
        
        # Simulate Request
        # We need to bypass authentication or set a cookie
        # api.py checks session or cookie.
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
            
        payload = {
            "ui_action": "generate_draft_steps",
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "" # message is required by validation usually, but let's see
        }
        
        response = self.client.post('/api/message', json=payload)
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        print("Response:", json.dumps(data, indent=2))
        
        self.assertIn("reply", data)
        self.assertIn("draft_payload", data)
        self.assertTrue(len(data["draft_payload"]["steps"]) > 0)
        self.assertTrue(data.get("meta", {}).get("used_fallback_steps"))
        
        # Verify fallback steps content
        steps = data["draft_payload"]["steps"]
        self.assertIn("Define success criteria", steps)
        print("Fallback steps verified.")

    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_continuous_edit(self, MockLLM, MockRepo):
        print("\n--- Testing Continuous Edit ---")
        # Setup Mock LLM for edit
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.chat_completion.return_value.choices[0].message.content = json.dumps({
            "title": "Updated Title",
            "target_days": 7,
            "steps": ["Step 1"],
            "body": "Test Body"
        })
        
        # Setup Mock Repo
        draft_id = 123
        MockRepo.get_suggestion.return_value = {
            "id": draft_id,
            "user_id": self.user_id,
            "kind": "goal",
            "status": "pending",
            "payload": {
                "title": "Test Goal",
                "target_days": 7,
                "steps": [],
                "body": "Test Body"
            }
        }
        
        with self.client.session_transaction() as sess:
            sess['authed'] = True
            sess['user_id'] = self.user_id
        
        payload = {
            "draft_id": draft_id,
            "draft_type": "goal",
            "message": "Change title to Updated Title"
        }
        
        response = self.client.post('/api/message', json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print("Response:", json.dumps(data, indent=2))
        
        self.assertEqual(data["draft_payload"]["title"], "Updated Title")
        self.assertIn("draft_context", data)
        print("Continuous edit verified.")

if __name__ == '__main__':
    unittest.main()
