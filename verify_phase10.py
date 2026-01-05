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

class TestPhase10(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.user_id = "test_user_phase10"
        
    @patch('api.suggestions_repository')
    @patch('core.llm_wrapper.LLMWrapper')
    def test_generate_steps_reply_format(self, MockLLM, MockRepo):
        print("\n--- Testing Generate Steps Reply Format ---")
        # Setup Mock LLM to fail (trigger fallback)
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
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        print("Response:", json.dumps(data, indent=2))
        
        reply = data.get("reply", "")
        self.assertIn("I've generated 5 steps for your goal:", reply)
        self.assertIn("1) Define success criteria", reply)
        self.assertIn("2) Break down into sub-tasks", reply)
        
        # Verify meta
        self.assertTrue(data.get("meta", {}).get("used_fallback_steps"))
        
        print("Reply format verified.")

if __name__ == '__main__':
    unittest.main()
