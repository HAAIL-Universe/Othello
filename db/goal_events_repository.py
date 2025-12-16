"""Repository helpers for goal_events (append-only event ledger for goals)."""
from typing import Any, Dict, List, Optional
from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one

def append_goal_event(user_id: str, goal_id: int, step_id: Optional[int], event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO goal_events (user_id, goal_id, step_id, event_type, payload, occurred_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id, user_id, goal_id, step_id, event_type, payload, occurred_at
    """
    return execute_and_fetch_one(query, (user_id, goal_id, step_id, event_type, payload)) or {}

def list_goal_events(user_id: str, goal_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, goal_id, step_id, event_type, payload, occurred_at
        FROM goal_events
        WHERE user_id = %s AND goal_id = %s
        ORDER BY occurred_at DESC
        LIMIT %s
    """
    return fetch_all(query, (user_id, goal_id, limit))
