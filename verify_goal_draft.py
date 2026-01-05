import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from db.database import init_pool, execute_query, fetch_one, execute_and_fetch_one
from db.goals_repository import create_goal, get_goal, update_goal_draft
from db.db_goal_manager import DbGoalManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_goal_draft")

def verify():
    print("Initializing DB pool...")
    init_pool()

    # 1. Check column existence
    print("Checking for draft_text column...")
    try:
        execute_query("ALTER TABLE goals ADD COLUMN IF NOT EXISTS draft_text TEXT")
        print("Column check passed (idempotent ALTER).")
    except Exception as e:
        print(f"Column check failed: {e}")
        return

    # 2. Create test goal
    user_id = "test_user_verify"
    print(f"Creating test goal for user {user_id}...")
    goal_data = {
        "title": "Test Goal for Draft Verification",
        "description": "Initial description",
        "status": "active"
    }
    created = create_goal(goal_data, user_id)
    goal_id = created["id"]
    print(f"Created goal {goal_id}")

    # 3. Test append_goal_draft via Manager
    mgr = DbGoalManager()
    print("Testing append_goal_draft...")
    updated = mgr.append_goal_draft(user_id, goal_id, "First draft line.")
    if updated and updated.get("draft_text") == "First draft line.":
        print("Append 1 passed.")
    else:
        print(f"Append 1 failed: {updated.get('draft_text')}")

    updated = mgr.append_goal_draft(user_id, goal_id, "Second draft line.")
    expected = "First draft line.\n\nSecond draft line."
    if updated and updated.get("draft_text") == expected:
        print("Append 2 passed.")
    else:
        print(f"Append 2 failed: {updated.get('draft_text')}")

    # 4. Test replace_goal_draft via Manager
    print("Testing replace_goal_draft...")
    updated = mgr.replace_goal_draft(user_id, goal_id, "Replaced draft.")
    if updated and updated.get("draft_text") == "Replaced draft.":
        print("Replace passed.")
    else:
        print(f"Replace failed: {updated.get('draft_text')}")

    # 5. Verify get_goal returns draft_text
    print("Verifying get_goal...")
    fetched = get_goal(goal_id, user_id)
    if fetched and fetched.get("draft_text") == "Replaced draft.":
        print("get_goal passed.")
    else:
        print(f"get_goal failed: {fetched.get('draft_text')}")

    print("Verification complete.")

if __name__ == "__main__":
    verify()
