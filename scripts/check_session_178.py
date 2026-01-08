import os
import sys

# Mock env
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_2LT5BvRPkjFY@ep-crimson-dream-abaxd3hk-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Project root
sys.path.append(os.getcwd())

from db.messages_repository import count_session_messages, get_session_narrator_state

USER_ID = "1"
SESSION_ID = 178

print(f"Checking Session {SESSION_ID} for User {USER_ID}")
try:
    count = count_session_messages(USER_ID, SESSION_ID)
    print(f"Message Count: {count}")
    
    state = get_session_narrator_state(USER_ID, SESSION_ID)
    print(f"Narrator State: {state}")
except Exception as e:
    print(f"Error: {e}")
