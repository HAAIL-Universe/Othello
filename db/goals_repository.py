# db/goals_repository.py
"""
Goals repository module for Othello.

Provides database operations for managing goals in the PostgreSQL database.
Maps to the 'goals' table schema with columns:
- id (serial primary key)
- user_id (text)
- title (text)
- description (text)
- status (text)
- priority (integer) - stored as INT, normalized from string values
- category (text)
- plan (text)
- checklist (jsonb)
- last_conversation_summary (text)
- created_at (timestamp)
- updated_at (timestamp)

Used by Flask API routes to replace JSON file-based storage.

Usage:
    from db.goals_repository import list_goals, create_goal, update_goal_meta
    
    goals = list_goals(user_id="1")
    new_goal = create_goal({"title": "Learn Python", "description": "..."}, user_id="1")
    update_goal_meta(goal_id=5, {"status": "in_progress", "priority": "high"})
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one


def normalize_priority(value: Any) -> int:
    """
    Normalize priority values to integers for database storage.
    
    The database stores priority as INT, but the application may receive
    string values like "low", "medium", "high" from user input or legacy code.
    
    Mapping:
        - "low" → 1
        - "medium" → 3 (default)
        - "high" → 5
        - Numeric values (int or string) → converted to int
        - None or invalid → 3 (medium, default)
    
    Args:
        value: Priority value as string, int, or None
    
    Returns:
        Integer priority value (1, 3, or 5, or custom numeric value)
    """
    # Default to medium priority
    if value is None:
        return 3
    
    # If already an integer, return it
    if isinstance(value, int):
        return value
    
    # Handle string values
    if isinstance(value, str):
        value_lower = value.lower().strip()
        
        # Map common string priorities
        priority_map = {
            "low": 1,
            "medium": 3,
            "high": 5
        }
        
        if value_lower in priority_map:
            return priority_map[value_lower]
        
        # Try to parse as numeric string
        try:
            return int(value)
        except ValueError:
            # Invalid string, return default
            return 3
    
    # Fallback for any other type
    return 3


def list_goals(user_id: str, *, include_archived: bool = False) -> List[Dict[str, Any]]:
    """
    Retrieve all goals for a specific user.
    
    Args:
        user_id: The user ID to filter goals (as string)
        include_archived: Include archived goals when True
    
    Returns:
        List of goal dictionaries with all fields
    """
    if include_archived:
        query = """
            SELECT id, user_id, title, description, status, priority, category,
                   plan, checklist, last_conversation_summary, created_at, updated_at
            FROM goals
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (user_id,))

    query = """
        SELECT id, user_id, title, description, status, priority, category,
               plan, checklist, last_conversation_summary, created_at, updated_at
        FROM goals
        WHERE user_id = %s AND (status IS NULL OR status != 'archived')
        ORDER BY created_at DESC
    """
    return fetch_all(query, (user_id,))


def get_goal(goal_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single goal by ID and user ID.
    
    Args:
        goal_id: The goal ID
        user_id: The user ID (for authorization, as string)
    
    Returns:
        Goal dictionary if found, None otherwise
    """
    query = """
        SELECT id, user_id, title, description, status, priority, category,
               plan, checklist, last_conversation_summary, created_at, updated_at
        FROM goals
        WHERE id = %s AND user_id = %s
    """
    return fetch_one(query, (goal_id, user_id))


def create_goal(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Create a new goal in the database.
    
    Args:
        data: Dictionary containing goal fields (title, description, etc.)
        user_id: The user ID who owns this goal (as string)
    
    Returns:
        The created goal with all fields including the new ID
    """
    title = data.get("title") or data.get("text") or "Untitled Goal"
    description = data.get("description") or ""
    status = data.get("status") or "active"
    priority = normalize_priority(data.get("priority", "medium"))
    category = data.get("category") or ""
    plan = data.get("plan") or ""
    checklist = data.get("checklist", [])
    
    # Ensure checklist is JSON serializable
    if isinstance(checklist, str):
        try:
            checklist = json.loads(checklist)
        except:
            checklist = []
    
    query = """
        INSERT INTO goals 
        (user_id, title, description, status, priority, category, plan, checklist, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, title, description, status, priority, category,
                  plan, checklist, last_conversation_summary, created_at, updated_at
    """
    
    result = execute_and_fetch_one(
        query,
        (user_id, title, description, status, priority, category, plan, json.dumps(checklist))
    )
    
    return result or {}


def update_goal_meta(goal_id: int, fields_to_change: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update metadata fields of a goal (title, status, priority, etc.).
    
    Args:
        goal_id: The goal ID to update
        fields_to_change: Dictionary of field names and new values
    
    Returns:
        Updated goal dictionary if successful, None otherwise
    """
    allowed_fields = ["title", "description", "status", "priority", "category"]
    
    # Build dynamic SET clause
    set_clauses = []
    params = []
    
    for field, value in fields_to_change.items():
        if field in allowed_fields:
            # Normalize priority values before inserting
            if field == "priority":
                value = normalize_priority(value)
            set_clauses.append(f"{field} = %s")
            params.append(value)
    
    if not set_clauses:
        # No valid fields to update, return None
        return None
    
    # Always update updated_at
    set_clauses.append("updated_at = NOW()")
    
    query = f"""
        UPDATE goals
        SET {', '.join(set_clauses)}
        WHERE id = %s
        RETURNING id, user_id, title, description, status, priority, category,
                  plan, checklist, last_conversation_summary, created_at, updated_at
    """
    
    params.append(goal_id)
    
    return execute_and_fetch_one(query, tuple(params))


def update_goal_from_conversation(
    goal_id: int,
    new_plan: Optional[str] = None,
    new_checklist: Optional[List[Dict[str, Any]]] = None,
    new_summary: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update goal fields that are derived from conversation analysis
    (plan, checklist, last_conversation_summary).
    
    Args:
        goal_id: The goal ID to update
        new_plan: Updated plan text (optional)
        new_checklist: Updated checklist as list of dicts (optional)
        new_summary: Updated conversation summary (optional)
    
    Returns:
        Updated goal dictionary if successful, None otherwise
    """
    set_clauses = []
    params = []
    
    if new_plan is not None:
        set_clauses.append("plan = %s")
        params.append(new_plan)
    
    if new_checklist is not None:
        set_clauses.append("checklist = %s")
        params.append(json.dumps(new_checklist))
    
    if new_summary is not None:
        set_clauses.append("last_conversation_summary = %s")
        params.append(new_summary)
    
    if not set_clauses:
        # Nothing to update
        return None
    
    # Always update updated_at
    set_clauses.append("updated_at = NOW()")
    
    query = f"""
        UPDATE goals
        SET {', '.join(set_clauses)}
        WHERE id = %s
        RETURNING id, user_id, title, description, status, priority, category,
                  plan, checklist, last_conversation_summary, created_at, updated_at
    """
    
    params.append(goal_id)
    
    return execute_and_fetch_one(query, tuple(params))


def delete_goal(goal_id: int, user_id: str) -> bool:
    """
    Delete a goal from the database.
    
    Args:
        goal_id: The goal ID to delete
        user_id: The user ID (for authorization, as string)
    
    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM goals WHERE id = %s AND user_id = %s"
    try:
        execute_query(query, (goal_id, user_id))
        return True
    except Exception as e:
        print(f"[GoalsRepository] Failed to delete goal {goal_id}: {e}")
        return False


def archive_goal(goal_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Archive a goal (soft delete) by setting status to 'archived'.
    
    Args:
        goal_id: The goal ID to archive
        user_id: The user ID (for authorization, as string)
    
    Returns:
        Archived goal dictionary if successful, None otherwise
    """
    query = """
        UPDATE goals
        SET status = 'archived', updated_at = NOW()
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, title, description, status, priority, category,
                  plan, checklist, last_conversation_summary, created_at, updated_at
    """
    return execute_and_fetch_one(query, (goal_id, user_id))


def add_conversation_note(goal_id: int, role: str, content: str) -> None:
    """
    Append a conversation note to the goal's conversation log.
    This could be stored in a separate 'goal_conversations' table,
    or appended to a JSONB field in the goals table.
    
    For now, this is a placeholder until a DB-backed conversation table
    (or goal_events usage) is fully wired with user_id context.
    
    Args:
        goal_id: The goal ID
        role: The role (user, othello, system)
        content: The message content
    """
    # TODO: Implement conversation storage in database
    pass


# ============================================================================
# PLAN STEPS - Multi-step goal planning
# ============================================================================

def create_plan_step(
    goal_id: int,
    step_index: int,
    description: str,
    status: str = "pending",
    due_date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a single plan step for a goal.
    
    Args:
        goal_id: The goal ID this step belongs to
        step_index: Order of execution in the plan (0-based or 1-based)
        description: The actual step text/instruction
        status: Step status ('pending', 'in_progress', 'done')
        due_date: Optional deadline for this step (ISO format string or None)
    
    Returns:
        Created step dictionary with all fields including the new ID
    """
    query = """
        INSERT INTO plan_steps 
        (goal_id, step_index, description, status, due_date, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, goal_id, step_index, description, status, due_date, created_at, updated_at
    """
    
    return execute_and_fetch_one(query, (goal_id, step_index, description, status, due_date))


def create_plan_steps(goal_id: int, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Bulk insert a list of plan steps for a goal.
    
    Args:
        goal_id: The goal ID these steps belong to
        steps: List of dicts, each containing at least:
               - step_index (int)
               - description (str)
               Optionally:
               - status (str, defaults to 'pending')
               - due_date (str or None)
    
    Returns:
        List of created step dictionaries
    """
    if not steps:
        return []
    
    created_steps = []
    for step in steps:
        step_index = step.get("step_index")
        description = step.get("description")
        status = step.get("status", "pending")
        due_date = step.get("due_date")
        
        if step_index is None or not description:
            print(f"[GoalsRepository] Skipping invalid step: {step}")
            continue
        
        created_step = create_plan_step(goal_id, step_index, description, status, due_date)
        if created_step:
            created_steps.append(created_step)
    
    return created_steps


def get_plan_steps_for_goal(goal_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all plan steps for a goal, ordered by step_index.
    
    Args:
        goal_id: The goal ID
    
    Returns:
        List of step dictionaries ordered by step_index
    """
    query = """
        SELECT id, goal_id, step_index, description, status, due_date, created_at, updated_at
        FROM plan_steps
        WHERE goal_id = %s
        ORDER BY step_index ASC
    """
    return fetch_all(query, (goal_id,))


def update_plan_step_status(step_id: int, status: str) -> Optional[Dict[str, Any]]:
    """
    Update the status of a plan step.
    
    Args:
        step_id: The step ID to update
        status: New status ('pending', 'in_progress', 'done')
    
    Returns:
        Updated step dictionary if successful, None otherwise
    """
    query = """
        UPDATE plan_steps
        SET status = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, goal_id, step_index, description, status, due_date, created_at, updated_at
    """
    return execute_and_fetch_one(query, (status, step_id))


def get_next_incomplete_step(goal_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the next step with status != 'done' for a goal, ordered by step_index.
    
    Args:
        goal_id: The goal ID
    
    Returns:
        Next incomplete step dictionary, or None if all steps are done
    """
    query = """
        SELECT id, goal_id, step_index, description, status, due_date, created_at, updated_at
        FROM plan_steps
        WHERE goal_id = %s AND status != 'done'
        ORDER BY step_index ASC
        LIMIT 1
    """
    return fetch_one(query, (goal_id,))


def delete_plan_steps_for_goal(goal_id: int) -> None:
    """
    Delete all plan steps for a goal.
    Useful when regenerating a plan from scratch.
    
    Args:
        goal_id: The goal ID
    """
    query = "DELETE FROM plan_steps WHERE goal_id = %s"
    try:
        execute_query(query, (goal_id,))
    except Exception as e:
        print(f"[GoalsRepository] Failed to delete plan steps for goal {goal_id}: {e}")

