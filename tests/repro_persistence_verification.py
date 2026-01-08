# tests/repro_persistence_verification.py
import sys
import os
import unittest
import random
import string

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app

class TestPersistenceVerification(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Random user id to avoid collisions
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.user_id = f"user_verif_{rand_suffix}"
        self.channel = "companion" # Forced channel
        
        with self.client.session_transaction() as sess:
            sess["authed"] = True
            sess["user_id"] = self.user_id

    def test_send_and_history_consistency(self):
        print(f"\n[Verif] User: {self.user_id}")
        
        # 1. Send Message (First in session)
        msg_text = f"Test message {random.randint(1000,9999)}"
        res = self.client.post("/api/message", json={
            "message": msg_text,
            "channel": self.channel,
            "current_view": "chat"
        })
        # handle_message returns 200, not 201. 
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        # KEY CHECK: Does response contain conversation_id?
        # Note: handle_message returns flat JSON, not wrapped in "data"
        self.assertIn("conversation_id", data, "Response MUST return conversation_id in root")
        conversation_id = data["conversation_id"]
        print(f"[Verif] Created conversation_id: {conversation_id}")
        self.assertIsNotNone(conversation_id)
        
        # 2. Fetch History using that ID
        # Emulate UI refresh
        res_hist = self.client.get(f"/api/conversations/{conversation_id}/messages?channel={self.channel}")
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.get_json()
        
        messages = hist_data["data"]["messages"]
        self.assertTrue(len(messages) > 0, "Should have at least 1 message")
        self.assertEqual(messages[0]["transcript"], msg_text)
        
        # 3. Send Follow-up (Simulating UI latching)
        msg_text_2 = f"Follow up {random.randint(1000,9999)}"
        res2 = self.client.post("/api/message", json={
            "message": msg_text_2,
            "channel": self.channel,
            "session_id": conversation_id, # UI sends this if it latched
            "current_view": "chat"
        })
        # handle_message returns 200
        self.assertEqual(res2.status_code, 200)
        
        # 4. Verify count in that session
        res_hist_2 = self.client.get(f"/api/conversations/{conversation_id}/messages?channel={self.channel}")
        hist_data_2 = res_hist_2.get_json()
        messages_2 = hist_data_2["data"]["messages"]
        # Each exchange creates 2 messages (User + Assistant)
        # 2 exchanges * 2 = 4 messages
        self.assertEqual(len(messages_2), 4, "Should have 4 messages (2 exchanges) in the session now")
        print("[Verif] Persistence and Latching verified.")


if __name__ == "__main__":
    unittest.main()
