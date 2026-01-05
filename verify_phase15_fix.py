import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import json
import sys
import os

# Add workspace root to path
sys.path.append(os.getcwd())

import api

class TestPhase15Fix(unittest.TestCase):
    def setUp(self):
        # Force re-initialization of agent components with mocks
        api._agent_components = None
        
        self.mock_request = MagicMock()
        self.mock_g = MagicMock()
        self.mock_g.user_id = "test_user"
        self.mock_g.session_id = "test_session"
        self.mock_session = {"authed": True, "user_id": "test_user"}
        
        # Patch Flask globals
        self.patcher_request = patch('api.request', self.mock_request)
        self.patcher_g = patch('api.g', self.mock_g)
        self.patcher_session = patch('api.session', self.mock_session)
        
        # Mock jsonify to capture response data
        def mock_jsonify_side_effect(data):
            resp = MagicMock()
            resp.get_json = lambda: data
            resp.__getitem__ = lambda s, k: data[k]
            resp.get = lambda k, d=None: data.get(k, d)
            return resp
            
        self.patcher_jsonify = patch('api.jsonify', side_effect=mock_jsonify_side_effect)
        
        self.patcher_request.start()
        self.patcher_g.start()
        self.patcher_session.start()
        self.patcher_jsonify.start()

    def tearDown(self):
        self.patcher_request.stop()
        self.patcher_g.stop()
        self.patcher_session.stop()
        self.patcher_jsonify.stop()

    @patch('db.suggestions_repository.get_suggestion')
    @patch('db.suggestions_repository.update_suggestion_payload')
    @patch('db.suggestions_repository.update_suggestion_status')
    @patch('db.goals_repository.create_goal')
    @patch('core.llm_wrapper.AsyncLLMWrapper')
    def test_change_step_flow(self, MockAsyncLLMWrapper, mock_create_goal, mock_update_status, mock_update_payload, mock_get_suggestion):
        print("\n=== PHASE 15 VERIFICATION START ===")
        
        # Setup Mock LLM
        mock_llm_instance = MockAsyncLLMWrapper.return_value
        mock_llm_instance.chat = AsyncMock()
        
        # Define the XML response that simulates the LLM generating steps
        xml_response = """
<goal_update>
    <steps>
        <step>Install Python</step>
        <step>Master Loops</step>
        <step>Learn Functions</step>
    </steps>
</goal_update>
"""
        mock_llm_instance.chat.return_value = xml_response
        
        # 1. Setup Initial Draft State
        draft_id = 101
        initial_payload = {
            "title": "Learn Python",
            "target_days": 7,
            "steps": ["Install Python", "Write Hello World", "Learn Functions"],
            "body": "I want to learn python"
        }
        
        # Mock get_suggestion to return this draft
        mock_get_suggestion.return_value = {
            "id": draft_id,
            "user_id": "test_user",
            "kind": "goal",
            "status": "pending",
            "payload": initial_payload
        }
        
        # 2. Change Step Request
        print("\n--- Change Step Request ---")
        self.mock_request.get_json.return_value = {
            "draft_id": draft_id,
            "message": "Change step 2 to Master Loops"
        }
        self.mock_request.json = self.mock_request.get_json.return_value
        
        # Execute
        resp = api.handle_message()
        data = resp.get_json()
        
        print("Response Keys:", data.keys())
        
        # 3. Verify Draft Payload Update
        if "draft_payload" in data:
            steps = data["draft_payload"].get("steps", [])
            print("Updated Steps:", steps)
            
            # Assertions
            self.assertEqual(len(steps), 3)
            self.assertEqual(steps[1], "Master Loops")
            print("SUCCESS: Step 2 was updated to 'Master Loops'")
            
            # Verify DB update was called
            mock_update_payload.assert_called_with("test_user", draft_id, data["draft_payload"])
            print("SUCCESS: Database update called")
        else:
            print("FAILURE: 'draft_payload' missing from response")
            self.fail("'draft_payload' missing from response")

if __name__ == '__main__':
    unittest.main()
