"""Repository helpers for goal_task_history (applied insight tasks)."""
from datetime import date
from typing import Any, Dict, List, Optional
import logging

from db.database import execute_and_fetch_one, fetch_all

logger = logging.getLogger("GoalTaskHistoryRepository")


ALLOWED_STATUSES = {
    "planned",
    "complete",
    "completed",
    "done",
    "cancelled",
    "skipped",
    "rescheduled",
    "in_progress",
    "in-progress",
}


def _coerce_status(status: Optional[str]) -> str:
    value = (status or "planned").strip().lower()
    return value if value in ALLOWED_STATUSES else "planned"


def upsert_goal_task(
    *,
    user_id: str,
    plan_date: date,
    item_id: str,
    label: str,
    status: Optional[str] = None,
    effort: Optional[str] = None,
    section_hint: Optional[str] = None,
    source_insight_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        INSERT INTO goal_task_history (
            user_id, plan_date, item_id, label, status, effort, section_hint, source_insight_id, metadata, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (user_id, plan_date, item_id)
        DO UPDATE SET
            label = EXCLUDED.label,
            status = EXCLUDED.status,
            effort = EXCLUDED.effort,
            section_hint = EXCLUDED.section_hint,
            source_insight_id = COALESCE(EXCLUDED.source_insight_id, goal_task_history.source_insight_id),
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        RETURNING id, user_id, plan_date, item_id, label, status, effort, section_hint, source_insight_id, metadata, created_at, updated_at;
    """
    status_value = _coerce_status(status)
    section_value = (section_hint or "").strip() or None
    metadata_value = metadata or {}

    return execute_and_fetch_one(
        query,
        (
            user_id,
            plan_date,
            item_id,
            label or item_id,
            status_value,
            effort,
            section_value,
            source_insight_id,
            metadata_value,
        ),
    )


def list_goal_tasks(
    user_id: str,
    *,
    start_date: date,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    filters = ["user_id = %s", "plan_date BETWEEN %s AND %s"]
    params: List[Any] = [user_id, start_date, end_date or start_date]

    if status:
        filters.append("status = %s")
        params.append(_coerce_status(status))

    where_clause = " AND ".join(filters)
    query = f"""
        SELECT id, user_id, plan_date, item_id, label, status, effort, section_hint, source_insight_id, metadata, created_at, updated_at
        FROM goal_task_history
        WHERE {where_clause}
        ORDER BY plan_date DESC, updated_at DESC
        LIMIT %s;
    """
    params.append(max(1, limit))

    return fetch_all(query, tuple(params))


def get_for_date(user_id: str, *, target_date: date, status: Optional[str] = None) -> List[Dict[str, Any]]:
    return list_goal_tasks(user_id, start_date=target_date, end_date=target_date, status=status, limit=100)
