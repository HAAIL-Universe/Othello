
import os
import sys

# Mock env
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_2LT5BvRPkjFY@ep-crimson-dream-abaxd3hk-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Project root
sys.path.append(os.getcwd())

from db.messages_repository import create_message, count_session_messages
from db.database import init_pool

init_pool()

USER_ID = "1"
SESSION_ID = 178

print(f"Attempting to insert message into Session {SESSION_ID}")
try:
    record = create_message(
        user_id=USER_ID,
        transcript="Manual Injection Test",
        source="script",
        channel="companion",
        session_id=SESSION_ID,
        create_session_if_missing=False 
    )
    print(f"Inserted Message ID: {record.get('id')}")
    
    count = count_session_messages(USER_ID, SESSION_ID)
    print(f"New Message Count: {count}")

except Exception as e:
    print(f"Error: {e}")
