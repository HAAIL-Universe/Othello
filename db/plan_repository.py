from datetime import date
from typing import Any, Dict, List, Optional

import logging

from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one


logger = logging.getLogger("PlanRepository")


# ---------------------------------------------------------------------------
# Plans (header)
# ---------------------------------------------------------------------------

def upsert_plan(
    user_id: str,
    plan_date: date,
    generation_context: Optional[Dict[str, Any]] = None,
    behavior_snapshot: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        INSERT INTO plans (user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (user_id, plan_date)
        DO UPDATE SET
            generation_context = EXCLUDED.generation_context,
            behavior_snapshot = EXCLUDED.behavior_snapshot,
            updated_at = NOW()
        RETURNING id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (user_id, plan_date, generation_context or {}, behavior_snapshot or {}))


def get_plan_by_date(user_id: str, plan_date: date) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at
        FROM plans
        WHERE user_id = %s AND plan_date = %s
        LIMIT 1;
    """
    return fetch_one(query, (user_id, plan_date))


def get_plan_with_items(user_id: str, plan_date: date) -> Optional[Dict[str, Any]]:
    plan = get_plan_by_date(user_id, plan_date)
    if not plan:
        return None
    items = get_plan_items(plan["id"])
    plan["items"] = items
    return plan


def update_behavior_snapshot(plan_id: int, behavior_snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE plans
        SET behavior_snapshot = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (behavior_snapshot, plan_id))


def get_plans_since(user_id: str, earliest_date: date) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, plan_date, generation_context, behavior_snapshot, created_at, updated_at
        FROM plans
        WHERE user_id = %s AND plan_date >= %s
        ORDER BY plan_date DESC;
    """
    return fetch_all(query, (user_id, earliest_date))


# ---------------------------------------------------------------------------
# Plan items
# ---------------------------------------------------------------------------

def delete_plan_items(plan_id: int) -> None:
    execute_query("DELETE FROM plan_items WHERE plan_id = %s", (plan_id,))


def insert_plan_item(plan_id: int, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    logger.debug(
        "PlanRepository: insert plan_item plan_id=%s id=%s type=%s section=%s status=%s label=%s",
        plan_id,
        item.get("id") or item.get("item_id"),
        item.get("type"),
        item.get("section") or item.get("section_hint"),
        item.get("status"),
        (item.get("metadata") or {}).get("label"),
    )
    query = """
        INSERT INTO plan_items (
            plan_id, item_id, type, section, status, reschedule_to, skip_reason,
            priority, effort, energy, metadata, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
                  priority, effort, energy, metadata, created_at, updated_at;
    """
    return execute_and_fetch_one(
        query,
        (
            plan_id,
            item.get("id") or item.get("item_id"),
            item.get("type"),
            item.get("section") or item.get("section_hint"),
            item.get("status", "planned"),
            item.get("reschedule_to"),
            item.get("reason") or item.get("skip_reason"),
            item.get("priority"),
            item.get("effort"),
            item.get("energy_profile") or item.get("energy"),
            item.get("metadata") or item,
        ),
    )


def replace_plan_items(plan_id: int, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    delete_plan_items(plan_id)
    created: List[Dict[str, Any]] = []
    for item in items:
        created_item = insert_plan_item(plan_id, item)
        if created_item:
            created.append(created_item)
    return created


def get_plan_items(plan_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
               priority, effort, energy, metadata, created_at, updated_at
        FROM plan_items
        WHERE plan_id = %s
        ORDER BY id ASC;
    """
    rows = fetch_all(query, (plan_id,))
    goal_rows = [
        {
            "id": r.get("item_id") or r.get("id"),
            "section": r.get("section"),
            "status": r.get("status"),
            "label": (r.get("metadata") or {}).get("label"),
        }
        for r in rows
        if (r.get("type") or "").lower() == "goal_task"
    ]
    logger.debug(
        "PlanRepository: fetched plan_items plan_id=%s total=%s goal_tasks=%s preview=%s",
        plan_id,
        len(rows),
        len(goal_rows),
        goal_rows[:3],
    )
    return rows


def update_plan_item_status(
    plan_id: int,
    item_id: str,
    status: str,
    skip_reason: Optional[str] = None,
    reschedule_to: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE plan_items
        SET status = %s,
            skip_reason = COALESCE(%s, skip_reason),
            reschedule_to = COALESCE(%s, reschedule_to),
            metadata = COALESCE(%s, metadata),
            updated_at = NOW()
        WHERE plan_id = %s AND item_id = %s
        RETURNING id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
                  priority, effort, energy, metadata, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (status, skip_reason, reschedule_to, metadata, plan_id, item_id))


def get_plan_item(plan_id: int, item_id: str) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, plan_id, item_id, type, section, status, reschedule_to, skip_reason,
               priority, effort, energy, metadata, created_at, updated_at
        FROM plan_items
        WHERE plan_id = %s AND item_id = %s
        LIMIT 1;
    """
    return fetch_one(query, (plan_id, item_id))
