
import os
import sys
import json
import logging
from unittest.mock import MagicMock

# Setup dummy environment
os.environ["DATABASE_URL"] = "postgres://othello:othello_dev_secret@localhost:5432/othello"
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Mock core modules to avoid heavy imports
sys.modules["core.llm_wrapper"] = MagicMock()
sys.modules["core.architect_brain"] = MagicMock()

# Import repo directly
from db.database import execute_query
from db import suggestions_repository

def run_test():
    # 1. Clean slate
    user_id = "debug_user_123"
    print(f"Cleaning suggestions for {user_id}...")
    execute_query("DELETE FROM suggestions WHERE user_id = %s", (user_id,))

    # 2. Create Draft (Simulate api.py logic)
    print("Creating draft...")
    payload = {
        "title": "Debug Goal",
        "steps": ["Step 1", "Step 2"],
        "target_days": 7,
        "body": "Test body"
    }
    provenance = {"source": "debug_script"}
    suggestion = suggestions_repository.create_suggestion(
        user_id=user_id,
        kind="goal",
        payload=payload,
        provenance=provenance,
        status="pending"
    )
    draft_id = suggestion["id"]
    print(f"Draft created: ID={draft_id}, Status={suggestion['status']}")

    # 3. Simulate 'Edit' (Update payload)
    print("Updating draft...")
    updated_payload = payload.copy()
    updated_payload["body"] = "Updated body"
    updated = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
    
    # Verify status didn't change
    check = suggestions_repository.get_suggestion(user_id, draft_id)
    print(f"Draft after update: Status={check['status']}, Body={check['payload'].get('body')}")
    if check['status'] != 'pending':
        print("FAIL: Status changed after update!")
        return

    # 4. Simulate 'Confirm' Check
    print("Simulating Confirm Check...")
    # This matches api.py lines 4530+
    
    # A. With explicit ID
    fetched = suggestions_repository.get_suggestion(user_id, draft_id)
    if not fetched or fetched.get("status") != "pending":
        print("FAIL: Explicit fetch failed")
    else:
        print("PASS: Explicit fetch success")

    # B. With 'list_suggestions' (No ID)
    pending_drafts = suggestions_repository.list_suggestions(
        user_id=user_id,
        status="pending",
        kind="goal",
        limit=1
    )
    if not pending_drafts:
        print("FAIL: list_suggestions failed")
        print(f"Got: {pending_drafts}")
    elif pending_drafts[0]["id"] != draft_id:
        print(f"FAIL: list_suggestions returned wrong ID: {pending_drafts[0]['id']} vs {draft_id}")
    else:
        print("PASS: list_suggestions success")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error: {e}")
