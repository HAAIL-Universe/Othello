import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add workspace root to path
sys.path.append(os.getcwd())

import api

class TestPhase14Evidence(unittest.TestCase):
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
        
        self.mock_request.start = self.patcher_request.start()
        self.mock_g.start = self.patcher_g.start()
        self.patcher_session.start()
        self.mock_jsonify = self.patcher_jsonify.start()

    def tearDown(self):
        self.patcher_request.stop()
        self.patcher_g.stop()
        self.patcher_session.stop()
        self.patcher_jsonify.stop()

    # Removed test_evidence_collection

    @patch('db.suggestions_repository.get_suggestion')
    @patch('db.suggestions_repository.update_suggestion_payload')
    @patch('db.suggestions_repository.update_suggestion_status')
    @patch('db.goals_repository.create_goal')
    @patch('core.llm_wrapper.AsyncLLMWrapper')
    @patch('core.llm_wrapper.LLMWrapper') 
    def test_full_flow(self, MockLLMWrapper, MockAsyncLLMWrapper, mock_create_goal, mock_update_status, mock_update_payload, mock_get_suggestion):
        print("\n=== EVIDENCE COLLECTION START ===")
        
        # Setup Mock LLM
        # api.py uses AsyncLLMWrapper
        mock_llm_instance = MockAsyncLLMWrapper.return_value
        
        # Setup Mock LLM for synchronous calls (used by _generate_draft_steps_payload)
        mock_sync_llm = MockLLMWrapper.return_value
        mock_sync_response = MagicMock()
        mock_sync_response.choices = [MagicMock()]
        mock_sync_response.choices[0].message.content = json.dumps({
            "title": "Learn Python",
            "target_days": 7,
            "steps": ["Install Python", "Define success criteria", "Break down into sub-tasks", "Identify resources needed", "Set milestones"],
            "body": "I want to learn Python"
        })
        mock_sync_llm.chat_completion.return_value = mock_sync_response
        
        # Configure chat to return XML response
        # Since Architect awaits model.chat, we need an AsyncMock or a coroutine
        from unittest.mock import AsyncMock
        mock_llm_instance.chat = AsyncMock()
        
        # Define the XML response that simulates the LLM generating steps
        xml_response = """
<goal_update>
    <steps>
        <step>Install Python</step>
        <step>Write Hello World</step>
        <step>Learn Loops</step>
        <step>Learn Functions</step>
        <step>Build Project</step>
    </steps>
</goal_update>
"""
        mock_llm_instance.chat.return_value = xml_response
        
        # 1. Create Draft (Simulated)
        # We assume a draft exists for the subsequent steps
        draft_id = 101
        current_payload = {
            "title": "Learn Python",
            "target_days": 7,
            "steps": ["Install Python"],
            "body": "I want to learn python"
        }
        
        mock_get_suggestion.return_value = {
            "id": draft_id,
            "kind": "goal",
            "status": "pending",
            "payload": current_payload
        }
        
        # 2. Generate Steps (Simulated)
        print("\n--- B) Generate Steps Request ---")
        self.mock_request.get_json.return_value = {
            "ui_action": "generate_draft_steps",
            "draft_id": draft_id
        }
        self.mock_request.json = self.mock_request.get_json.return_value
        
        # Mock LLM response for generation
        # Already set up above
        
        resp_gen = api.handle_message()
        print("Response Keys:", resp_gen.get_json().keys())
        if "draft_payload" in resp_gen.get_json():
            print("Draft Payload Steps:", resp_gen.get_json()["draft_payload"].get("steps"))
        
        # Update our mock state
        current_payload = resp_gen.get_json()["draft_payload"]
        mock_get_suggestion.return_value["payload"] = current_payload

        # 3. Change Step (Simulated)
        print("\n--- C) Change Step Request ---")
        # "Change step 2 to Master Loops"
        self.mock_request.get_json.return_value = {
            "draft_id": draft_id,
            "message": "Change step 2 to Master Loops" # This goes to user_input in handle_message
        }
        self.mock_request.json = self.mock_request.get_json.return_value
        
        # We need to simulate the user_input being passed to handle_message
        # handle_message reads request.json.get('message') OR request.json.get('transcript')
        # But wait, handle_message signature is empty, it reads from request global.
        
        # We need to ensure handle_message sees the text.
        # In api.py: user_input = data.get("message") or data.get("transcript") or ...
        
        resp_edit = api.handle_message()
        print("Response Keys:", resp_edit.get_json().keys())
        if "draft_payload" in resp_edit.get_json():
            print("Draft Payload Steps:", resp_edit.get_json()["draft_payload"].get("steps"))
            
        # Update mock state
        current_payload = resp_edit.get_json()["draft_payload"]
        mock_get_suggestion.return_value["payload"] = current_payload

        # 4. Confirm Request (Simulated)
        print("\n--- D) Confirm Request ---")
        self.mock_request.get_json.return_value = {
            "ui_action": "confirm_draft",
            "draft_id": draft_id
        }
        self.mock_request.json = self.mock_request.get_json.return_value
        
        # Mock create_goal to return a goal
        mock_create_goal.return_value = {
            "id": 500,
            "title": current_payload["title"],
            "description": current_payload.get("description", ""),
            "created_at": "2026-01-05T12:00:00"
        }
        
        resp_confirm = api.handle_message()
        print("Response Keys:", resp_confirm.get_json().keys())
        print("Saved Goal:", resp_confirm.get_json().get("saved_goal"))
        
        # 5. Goal Persistence Evidence
        print("\n--- Goal Persistence Check ---")
        # Check what was passed to create_goal
        if mock_create_goal.called:
            args, _ = mock_create_goal.call_args
            goal_data = args[0]
            print("create_goal called with:", json.dumps(goal_data, indent=2))
            if "steps" not in goal_data and "checklist" not in goal_data:
                print("CRITICAL: 'steps' or 'checklist' MISSING in create_goal arguments!")
        else:
            print("create_goal was NOT called!")

if __name__ == '__main__':
    unittest.main()
