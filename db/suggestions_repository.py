# db/suggestions_repository.py
"""
Repository helpers for confirm-gated suggestions.
"""
from typing import Optional, Dict, Any

from psycopg2.extras import Json

from db.database import execute_and_fetch_one, fetch_one
from db.database import fetch_all


def create_suggestion(
    *,
    user_id: str,
    kind: str,
    payload: Dict[str, Any],
    provenance: Dict[str, Any],
    status: str = "pending",
) -> Dict[str, Any]:
    query = """
        INSERT INTO suggestions (user_id, kind, status, payload, provenance, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
    """
    return execute_and_fetch_one(
        query,
        (user_id, kind, status, Json(payload), Json(provenance)),
    ) or {}


def get_suggestion(user_id: str, suggestion_id: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
        FROM suggestions
        WHERE id = %s AND user_id = %s
    """
    return fetch_one(query, (suggestion_id, user_id))


def update_suggestion_status(
    user_id: str,
    suggestion_id: int,
    status: str,
    decided_reason: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE suggestions
        SET status = %s,
            decided_at = NOW(),
            decided_reason = %s
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
    """
    return execute_and_fetch_one(query, (status, decided_reason, suggestion_id, user_id))


def update_suggestion_payload(
    user_id: str,
    suggestion_id: int,
    payload: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE suggestions
        SET payload = %s
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, kind, status, payload, provenance, created_at, decided_at, decided_reason
    """
    return execute_and_fetch_one(query, (Json(payload), suggestion_id, user_id))


def list_suggestions(
    *,
    user_id: str,
    status: str = "pending",
    kind: Optional[str] = None,
    limit: int = 50,
) -> list[Dict[str, Any]]:
    params = [user_id, status]
    clauses = ["user_id = %s", "status = %s"]
    if kind:
        clauses.append("kind = %s")
        params.append(kind)
    params.append(limit)
    query = f"""
        SELECT id, kind, status, payload, provenance, created_at, decided_at
        FROM suggestions
        WHERE {" AND ".join(clauses)}
        ORDER BY created_at DESC
        LIMIT %s
    """
    return fetch_all(query, tuple(params))
