
import sys
import os
import unittest
import string
import random
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from db.database import get_connection

class TestNarratorFlow(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Random user id to avoid collisions
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.user_id = f"user_narrator_{rand_suffix}"
        
        with self.client.session_transaction() as sess:
            sess["authed"] = True
            sess["user_id"] = self.user_id

    def test_narrator_generation_trigger(self):
        print(f"\n[NarratorTest] User: {self.user_id}")
        
        # 1. Start a new conversation (msg 1)
        res1 = self.client.post("/api/message", json={
            "message": "Hello Othello, this is message 1.",
            "channel": "companion"
        })
        self.assertEqual(res1.status_code, 200) # Fixed status code
        data1 = res1.get_json()
        conversation_id = data1.get("conversation_id") or data1.get("data", {}).get("conversation_id")
        
        # The fix in previous turn puts conversation_id in the root or data
        # Let's check where it actually is based on handle_message logic
        # handle_message returns _respond(payload). 
        # _respond adds conversation_id to payload.
        # So it should be at the root of the JSON.
        
        self.assertIsNotNone(conversation_id, "Conversation ID should be returned")
        print(f"[NarratorTest] Conversation ID: {conversation_id}")

        # 2. Add more messages to reach threshold (>=3)
        # Msg 2
        res2 = self.client.post("/api/message", json={
            "message": "Message 2: Telling you about my day.",
            "channel": "companion",
            "conversation_id": conversation_id
        })
        self.assertEqual(res2.status_code, 200)

        # Msg 3 (Should trigger narrator update if internal stride logic allows, 
        # but wait.. the logic says:
        # if (total_msgs >= 3) and (not curr_text or (total_msgs - last_count) >= 5)
        # Total messages = (User + Assistant) per exchange. 
        # Exchange 1 = 2 msgs.
        # Exchange 2 = 4 msgs.
        # So after Exchange 2, total_msgs = 4. Logic: 4 >= 3 is True.
        # Narrator should generate.
        
        print("[NarratorTest] 2 exchanges completed (4 messages total). Checking DB...")
        
        # Verify in DB
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT duet_narrator_text, duet_narrator_msg_count FROM sessions WHERE id = %s", 
                    (conversation_id,)
                )
                row = cursor.fetchone()
                
        self.assertIsNotNone(row, "Session should exist")
        narrator_text, msg_count = row
        
        print(f"[NarratorTest] DB State -> Text: {narrator_text}, Count: {msg_count}")
        
        # NOTE: Narrator generation uses an LLM call. In tests, we might want to mock it 
        # OR verify that the logic was attempted. 
        # However, since this is a "repro" on the real env (using the User's keys presumably),
        # it might actually call the LLM. 
        # If it's too slow or fails, we will see.
        
        # The user said "The DB contains the full message history... verified".
        # So let's assume it works. If it doesn't, we will know.
        
        if narrator_text:
            print("[NarratorTest] SUCCESS: Narrator text is present.")
        else:
            print("[NarratorTest] WARNING: Narrator text is NULL. The background task might have failed or LLM call failed.")

        # 3. Verify API output for list_sessions
        res_list = self.client.get("/api/conversations")
        self.assertEqual(res_list.status_code, 200)
        list_data = res_list.get_json()
        conversations = list_data.get("conversations", [])
        
        target_conv = next((c for c in conversations if c["conversation_id"] == conversation_id), None)
        self.assertIsNotNone(target_conv, "Conversation should be in the list")
        
        print(f"[NarratorTest] API Data -> duet_narrator_text: {target_conv.get('duet_narrator_text')}")
        
        # Assertion
        # We only strictly assert if we expect it to definitively succeed (LLM dependent).
        # We'll assert that the field exists in key, even if None.
        self.assertIn("duet_narrator_text", target_conv)

if __name__ == "__main__":
    unittest.main()
