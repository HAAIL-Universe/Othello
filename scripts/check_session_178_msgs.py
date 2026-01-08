import os
import sys

# Mock env
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_2LT5BvRPkjFY@ep-crimson-dream-abaxd3hk-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Project root
sys.path.append(os.getcwd())

from db.messages_repository import list_all_session_messages_for_summary

USER_ID = "1"
SESSION_ID = 178

print(f"Listing Messages for Session {SESSION_ID}")
try:
    msgs = list_all_session_messages_for_summary(USER_ID, SESSION_ID)
    print(msgs)
except Exception as e:
    print(f"Error: {e}")
