"""Repository helpers for goal_events (append-only event ledger for goals)."""
from typing import Any, Dict, List, Optional
import logging
from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one

logger = logging.getLogger("GoalEventsRepository")


def ensure_goal_events_table() -> None:
    query = """
        CREATE TABLE IF NOT EXISTS goal_events (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
            step_id INTEGER REFERENCES plan_steps(id) ON DELETE SET NULL,
            event_type TEXT NOT NULL,
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """
    execute_query(query)

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


def safe_append_goal_event(user_id: str, goal_id: int, step_id: Optional[int], event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Append a goal event but never raise; returns ok=false payload on failure."""
    try:
        event = append_goal_event(user_id, goal_id, step_id, event_type, payload)
        if event:
            return {"ok": True, "event": event}
        return {"ok": False, "reason": "empty_result"}
    except Exception as exc:
        logger.warning("Goal events append failed: %s", exc, exc_info=True)
        return {"ok": False, "reason": type(exc).__name__}


def safe_list_goal_events(user_id: str, goal_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """List goal events but never raise; returns [] on failure."""
    try:
        events = list_goal_events(user_id, goal_id, limit=limit)
        return events if isinstance(events, list) else []
    except Exception as exc:
        logger.warning("Goal events list failed: %s", exc, exc_info=True)
        return []
