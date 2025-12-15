"""Repository helpers for insights persistence."""
from typing import Any, Dict, List, Optional
import logging

from psycopg2.extras import RealDictCursor

from db.database import get_pool

VALID_TYPES = {"goal", "plan", "routine", "idea", "generic"}
VALID_STATUSES = {"pending", "applied", "dismissed"}


def _coerce_type(value: Optional[str]) -> str:
    t = (value or "").strip().lower()
    return t if t in VALID_TYPES else "generic"


def _coerce_status(value: Optional[str]) -> str:
    s = (value or "").strip().lower()
    return s if s in VALID_STATUSES else "pending"


def _row_to_insight(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not row:
        return None

    created_at = row.get("created_at")
    created_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else created_at
    insight_type = row.get("insight_type") or row.get("type")
    content = row.get("content") or row.get("summary")

    return {
        "id": row.get("id"),
        "user_id": row.get("user_id"),
        "insight_type": insight_type,
        "type": insight_type,
        "content": content,
        "summary": content,
        "status": row.get("status"),
        "created_at": created_iso,
    }


def create_insight(
    user_id: str,
    insight_type: str,
    summary: str,
    status: str = "pending",
) -> Optional[Dict[str, Any]]:
    """Insert a new insight row and return the created record."""
    logger = logging.getLogger("InsightsRepository")
    pool = get_pool()
    conn = None

    query = """
        INSERT INTO insights (user_id, type, status, summary)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, type, summary, status, created_at;
    """

    params = (
        user_id,
        _coerce_type(insight_type),
        _coerce_status(status),
        (summary or "").strip(),
    )

    try:
        conn = pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.commit()
            logger.info("[insights] created insight id=%s type=%s", row.get("id") if row else None, params[1])
            return _row_to_insight(row)
    except Exception:
        logger.warning("[insights] failed to create insight", exc_info=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return None
    finally:
        if conn:
            pool.putconn(conn)


def list_insights(
    user_id: str,
    status: Optional[str] = "pending",
) -> List[Dict[str, Any]]:
    logger = logging.getLogger("InsightsRepository")
    pool = get_pool()
    conn = None
    filters = ["user_id = %s"]
    params: List[Any] = [user_id]

    if status:
        filters.append("status = %s")
        params.append(_coerce_status(status))

    where_clause = " AND ".join(filters)
    query = f"""
        SELECT id, user_id, type, summary, status, created_at
        FROM insights
        WHERE {where_clause}
        ORDER BY created_at DESC;
    """

    try:
        conn = pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall() or []
            results = [_row_to_insight(r) for r in rows if r]
            logger.info(
                "[insights] list_insights returned %s rows for user_id=%s status=%s",
                len(results),
                user_id,
                status or "any",
            )
            return results
    except Exception:
        logger.warning("[insights] failed to list insights", exc_info=True)
        return []
    finally:
        if conn:
            pool.putconn(conn)


def count_pending_by_type(user_id: str) -> Dict[str, int]:
    logger = logging.getLogger("InsightsRepository")
    pool = get_pool()
    conn = None
    query = """
        SELECT type, COUNT(*) AS count
        FROM insights
        WHERE user_id = %s AND status = 'pending'
        GROUP BY type;
    """

    counts = {key: 0 for key in VALID_TYPES}

    try:
        conn = pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall() or []
            for row in rows:
                key = (row.get("type") or "").strip().lower()
                if not key:
                    key = "generic"
                counts[key] = int(row.get("count") or 0)
    except Exception:
        logger.warning("[insights] failed to count pending insights", exc_info=True)
    finally:
        if conn:
            pool.putconn(conn)
    logger.info("[insights] count_pending_by_type for user_id=%s -> %s", user_id, counts)
    return counts


def update_insight_status(
    insight_id: int,
    status: str,
    user_id: Optional[str] = None,
) -> bool:
    logger = logging.getLogger("InsightsRepository")
    pool = get_pool()
    conn = None
    status_value = _coerce_status(status)

    if user_id:
        query = "UPDATE insights SET status = %s WHERE id = %s AND user_id = %s"
        params = (status_value, insight_id, user_id)
    else:
        query = "UPDATE insights SET status = %s WHERE id = %s"
        params = (status_value, insight_id)

    try:
        conn = pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    except Exception:
        logger.warning("[insights] failed to update status", exc_info=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn:
            pool.putconn(conn)


def get_insight_by_id(user_id: str, insight_id: int) -> Optional[Dict[str, Any]]:
    logger = logging.getLogger("InsightsRepository")
    pool = get_pool()
    conn = None
    query = """
        SELECT id, user_id, type, summary, status, created_at
        FROM insights
        WHERE user_id = %s AND id = %s
        LIMIT 1;
    """

    try:
        conn = pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (user_id, insight_id))
            row = cursor.fetchone()
            return _row_to_insight(row)
    except Exception:
        logger.warning("[insights] failed to fetch insight", exc_info=True)
        return None
    finally:
        if conn:
            pool.putconn(conn)
