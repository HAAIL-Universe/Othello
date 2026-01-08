import os
import sys

# Mock env
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_2LT5BvRPkjFY@ep-crimson-dream-abaxd3hk-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Project root
sys.path.append(os.getcwd())

from db.database import fetch_one, init_pool

init_pool()

def find_user_for_session(sid):
    row = fetch_one("SELECT user_id FROM sessions WHERE id = %s", (sid,))
    return row['user_id'] if row else None

target_session = 178
user_id = find_user_for_session(target_session)

if user_id:
    print(f"User for Session {target_session} is: {user_id}")
    from db.messages_repository import count_session_messages, get_session_narrator_state
    count = count_session_messages(user_id, target_session)
    state = get_session_narrator_state(user_id, target_session)
    print(f"Message Count: {count}")
    print(f"Narrator State: {state}")
else:
    print(f"Session {target_session} not found.")

