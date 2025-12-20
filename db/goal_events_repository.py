"""Repository helpers for goal_events (append-only event ledger for goals)."""
from typing import Any, Dict, List, Optional
import logging
import time
import psycopg2
from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one

logger = logging.getLogger("GoalEventsRepository")
_goal_events_ensure_ok = False
_goal_events_last_attempt_ts = 0.0
_goal_events_backoff_sec = 60.0


def ensure_goal_events_table() -> None:
    global _goal_events_ensure_ok, _goal_events_last_attempt_ts
    if _goal_events_ensure_ok:
        return
    now = time.monotonic()
    if now - _goal_events_last_attempt_ts < _goal_events_backoff_sec:
        return
    _goal_events_last_attempt_ts = now
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
    try:
        execute_query(query)
        _goal_events_ensure_ok = True
    except psycopg2.Error as exc:
        logger.warning("Goal events table ensure failed: %s", exc, exc_info=True)

def append_goal_event(
    user_id: str,
    goal_id: int,
    step_id: Optional[int],
    event_type: str,
    payload: Dict[str, Any],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    query = """
        INSERT INTO goal_events (user_id, goal_id, step_id, event_type, payload, occurred_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id, user_id, goal_id, step_id, event_type, payload, occurred_at
    """
    try:
        return execute_and_fetch_one(query, (user_id, goal_id, step_id, event_type, payload)) or {}
    except psycopg2.Error as exc:
        logger.warning(
            "Goal events insert failed request_id=%s reason=%s",
            request_id,
            type(exc).__name__,
        )
        return {}

def list_goal_events(user_id: str, goal_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, goal_id, step_id, event_type, payload, occurred_at
        FROM goal_events
        WHERE user_id = %s AND goal_id = %s
        ORDER BY occurred_at DESC
        LIMIT %s
    """
    return fetch_all(query, (user_id, goal_id, limit))


def safe_append_goal_event(
    user_id: str,
    goal_id: int,
    step_id: Optional[int],
    event_type: str,
    payload: Dict[str, Any],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Append a goal event but never raise; returns ok=false payload on failure."""
    ensure_goal_events_table()
    try:
        event = append_goal_event(user_id, goal_id, step_id, event_type, payload, request_id=request_id)
        if event:
            return {"ok": True, "event": event}
        logger.warning(
            "Goal events append failed request_id=%s reason=%s",
            request_id,
            "empty_result",
        )
        return {"ok": False, "reason": "empty_result"}
    except Exception as exc:
        reason = type(exc).__name__
        logger.warning(
            "Goal events append failed request_id=%s reason=%s",
            request_id,
            reason,
        )
        return {"ok": False, "reason": reason}


def safe_list_goal_events(user_id: str, goal_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """List goal events but never raise; returns [] on failure."""
    try:
        events = list_goal_events(user_id, goal_id, limit=limit)
        return events if isinstance(events, list) else []
    except Exception as exc:
        logger.warning("Goal events list failed: %s", exc, exc_info=True)
        return []
