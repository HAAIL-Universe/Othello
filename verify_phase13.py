import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add workspace root to path
sys.path.append(os.getcwd())

from api import handle_message

class TestPhase13(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_g = MagicMock()
        self.mock_g.user_id = "test_user"
        self.mock_g.session_id = "test_session"
        self.mock_session = {"authed": True, "user_id": "test_user"} # Mock session as dict
        
        # Patch Flask globals
        self.patcher_request = patch('api.request', self.mock_request)
        self.patcher_g = patch('api.g', self.mock_g)
        self.patcher_session = patch('api.session', self.mock_session)
        
        # Mock jsonify to return a MagicMock that behaves like a Response
        def mock_jsonify_side_effect(data):
            resp = MagicMock()
            # Make it subscriptable to access data
            resp.__getitem__ = lambda s, k: data[k]
            resp.get = lambda k, d=None: data.get(k, d)
            # Allow converting to dict for assertions
            resp.to_dict = lambda: data
            return resp
            
        self.patcher_jsonify = patch('api.jsonify', side_effect=mock_jsonify_side_effect)
        
        self.mock_request.start = self.patcher_request.start()
        self.mock_g.start = self.patcher_g.start()
        self.patcher_session.start()
        self.mock_jsonify = self.patcher_jsonify.start()

    def tearDown(self):
        self.patcher_request.stop()
        self.patcher_g.stop()
        self.patcher_session.stop()
        self.patcher_jsonify.stop()

    @patch('api.suggestions_repository')
    @patch('api._apply_suggestion_decisions')
    def test_confirm_draft_sanitization(self, mock_apply, mock_repo):
        # Setup
        draft_id = 123
        payload = {
            "ui_action": "confirm_draft",
            "draft_id": draft_id
        }
        self.mock_request.get_json.return_value = payload
        self.mock_request.json = payload # Fallback if accessed directly
        
        # Mock existing draft with messy payload
        mock_repo.get_suggestion.return_value = {
            "id": draft_id,
            "status": "pending",
            "payload": {
                "title": "  My Goal  ",
                "target_days": "invalid", # Should default to 7
                "steps": ["  Step 1 ", "", "Step 1", "Step 2"], # Should dedupe and trim
                "body": "  Body  "
            }
        }
        
        # Mock apply result
        mock_apply.return_value = [{
            "ok": True,
            "goal": {"id": 999, "title": "My Goal"}
        }]
        
        # Execute
        response = handle_message()
        
        # Verify Sanitization
        # Check what was passed to update_suggestion_payload
        mock_repo.update_suggestion_payload.assert_called_once()
        args = mock_repo.update_suggestion_payload.call_args
        user_id, d_id, payload = args[0]
        
        self.assertEqual(user_id, "test_user")
        self.assertEqual(d_id, draft_id)
        self.assertEqual(payload["title"], "My Goal")
        self.assertEqual(payload["target_days"], 7)
        self.assertEqual(payload["steps"], ["Step 1", "Step 2"])
        self.assertEqual(payload["body"], "Body")
        
        # Verify Response
        self.assertEqual(response["saved_goal"]["goal_id"], 999)
        self.assertTrue(response["draft_cleared"])
        print("Test 1 (Sanitization): PASS")

    @patch('api.suggestions_repository')
    @patch('api._apply_suggestion_decisions')
    def test_confirm_empty_steps(self, mock_apply, mock_repo):
        # Setup
        draft_id = 124
        payload = {
            "ui_action": "confirm_draft",
            "draft_id": draft_id
        }
        self.mock_request.get_json.return_value = payload
        self.mock_request.json = payload
        
        mock_repo.get_suggestion.return_value = {
            "id": draft_id,
            "status": "pending",
            "payload": {
                "title": "Empty Goal",
                "steps": []
            }
        }
        
        mock_apply.return_value = [{
            "ok": True,
            "goal": {"id": 1000, "title": "Empty Goal"}
        }]
        
        # Execute
        response = handle_message()
        
        # Verify
        self.assertEqual(response["saved_goal"]["steps_count"], 0)
        self.assertTrue(response["meta"]["steps_empty"])
        print("Test 2 (Empty Steps): PASS")

if __name__ == '__main__':
    unittest.main()
