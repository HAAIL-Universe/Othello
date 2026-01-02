import uuid
from typing import Any, Dict, List, Optional
import logging
from psycopg2.extras import Json
from db.database import execute_query, fetch_one, fetch_all, execute_and_fetch_one

logger = logging.getLogger("RoutinesRepository")

# ---------------------------------------------------------------------------
# Routines (Header)
# ---------------------------------------------------------------------------

def list_routines(user_id: str) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, title, schedule_rule, enabled, created_at, updated_at
        FROM routines
        WHERE user_id = %s
        ORDER BY updated_at DESC;
    """
    return fetch_all(query, (user_id,))

def get_routine(user_id: str, routine_id: str) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, title, schedule_rule, enabled, created_at, updated_at
        FROM routines
        WHERE user_id = %s AND id = %s;
    """
    return fetch_one(query, (user_id, routine_id))

def create_routine(user_id: str, title: str, schedule_rule: Dict, enabled: bool) -> Dict[str, Any]:
    routine_id = str(uuid.uuid4())
    query = """
        INSERT INTO routines (id, user_id, title, schedule_rule, enabled, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, title, schedule_rule, enabled, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (routine_id, user_id, title, Json(schedule_rule), enabled))

def update_routine(user_id: str, routine_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    fields = []
    values = []
    
    if "title" in patch:
        fields.append("title = %s")
        values.append(patch["title"])
    if "schedule_rule" in patch:
        fields.append("schedule_rule = %s")
        values.append(Json(patch["schedule_rule"]))
    if "enabled" in patch:
        fields.append("enabled = %s")
        values.append(patch["enabled"])
        
    if not fields:
        return get_routine(user_id, routine_id)
        
    fields.append("updated_at = NOW()")
    values.append(user_id)
    values.append(routine_id)
    
    query = f"""
        UPDATE routines
        SET {", ".join(fields)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, title, schedule_rule, enabled, created_at, updated_at;
    """
    return execute_and_fetch_one(query, tuple(values))

def delete_routine(user_id: str, routine_id: str) -> bool:
    query = "DELETE FROM routines WHERE user_id = %s AND id = %s"
    # execute_query doesn't return rowcount, so we check existence first or just assume success
    # But to return bool, let's check if it existed. 
    # Actually, execute_query is void. Let's just run it.
    # If we really need bool, we can select first.
    # For now, let's assume if no exception, it's fine.
    # But the spec says return bool.
    # Let's use execute_and_fetch_one with RETURNING id to check.
    query = "DELETE FROM routines WHERE user_id = %s AND id = %s RETURNING id"
    result = execute_and_fetch_one(query, (user_id, routine_id))
    return result is not None

# ---------------------------------------------------------------------------
# Routine Steps
# ---------------------------------------------------------------------------

def list_steps(user_id: str, routine_id: str) -> List[Dict[str, Any]]:
    # Verify ownership of routine implicitly by joining or checking routine first?
    # The schema has routine_id. We should probably check if routine belongs to user.
    # But for simplicity/perf, we can just trust the routine_id if we also filter by user_id on the join?
    # Or just check routine ownership.
    # Let's just query steps where routine_id matches AND routine belongs to user.
    query = """
        SELECT s.id, s.user_id, s.routine_id, s.order_index, s.title, s.est_minutes, s.energy, s.tags, s.created_at, s.updated_at
        FROM routine_steps s
        JOIN routines r ON s.routine_id = r.id
        WHERE s.user_id = %s AND s.routine_id = %s AND r.user_id = %s
        ORDER BY s.order_index ASC, s.created_at ASC;
    """
    return fetch_all(query, (user_id, routine_id, user_id))

def create_step(
    user_id: str, 
    routine_id: str, 
    title: str, 
    est_minutes: Optional[int] = None, 
    energy: Optional[str] = None, 
    tags: Optional[List[str]] = None, 
    order_index: Optional[int] = None
) -> Dict[str, Any]:
    # Ensure routine belongs to user
    routine = get_routine(user_id, routine_id)
    if not routine:
        raise ValueError("Routine not found or access denied")

    if order_index is None:
        # Get max order_index
        q_max = "SELECT MAX(order_index) as m FROM routine_steps WHERE routine_id = %s"
        res = fetch_one(q_max, (routine_id,))
        current_max = res["m"] if res and res["m"] is not None else -1
        order_index = current_max + 1

    step_id = str(uuid.uuid4())
    query = """
        INSERT INTO routine_steps (id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at;
    """
    return execute_and_fetch_one(query, (step_id, user_id, routine_id, order_index, title, est_minutes, energy, Json(tags or [])))

def update_step(user_id: str, step_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    fields = []
    values = []
    
    if "title" in patch:
        fields.append("title = %s")
        values.append(patch["title"])
    if "est_minutes" in patch:
        fields.append("est_minutes = %s")
        values.append(patch["est_minutes"])
    if "energy" in patch:
        fields.append("energy = %s")
        values.append(patch["energy"])
    if "tags" in patch:
        fields.append("tags = %s")
        values.append(Json(patch["tags"]))
    if "order_index" in patch:
        fields.append("order_index = %s")
        values.append(patch["order_index"])
        
    if not fields:
        # Just fetch
        query = "SELECT * FROM routine_steps WHERE user_id = %s AND id = %s"
        return fetch_one(query, (user_id, step_id))
        
    fields.append("updated_at = NOW()")
    values.append(user_id)
    values.append(step_id)
    
    query = f"""
        UPDATE routine_steps
        SET {", ".join(fields)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at;
    """
    return execute_and_fetch_one(query, tuple(values))

def delete_step(user_id: str, step_id: str) -> bool:
    query = "DELETE FROM routine_steps WHERE user_id = %s AND id = %s RETURNING id"
    result = execute_and_fetch_one(query, (user_id, step_id))
    return result is not None

def list_routines_with_steps(user_id: str) -> List[Dict[str, Any]]:
    routines = list_routines(user_id)
    if not routines:
        return []
        
    # Fetch all steps for user (optimization: could filter by routine_ids if list is huge, but per-user is fine)
    query = """
        SELECT id, user_id, routine_id, order_index, title, est_minutes, energy, tags, created_at, updated_at
        FROM routine_steps
        WHERE user_id = %s
        ORDER BY order_index ASC, created_at ASC;
    """
    all_steps = fetch_all(query, (user_id,))
    
    # Group steps by routine_id
    steps_by_routine = {}
    for step in all_steps:
        rid = step["routine_id"]
        if rid not in steps_by_routine:
            steps_by_routine[rid] = []
        steps_by_routine[rid].append(step)
        
    for r in routines:
        r["steps"] = steps_by_routine.get(r["id"], [])
        
    return routines
