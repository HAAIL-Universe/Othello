"""Repository helpers for memory_entries (agentic memory log) and profile_snapshots."""
from typing import Any, Dict, List, Optional
from psycopg2.extras import Json
from db.database import execute_and_fetch_one, fetch_all

def append_memory_entry(user_id: str, kind: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO memory_entries (user_id, kind, content, metadata, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id, user_id, kind, content, metadata, created_at
    """
    return execute_and_fetch_one(query, (user_id, kind, content, Json(metadata))) or {}

def list_memory_entries(user_id: str, kind: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    if kind:
        query = """
            SELECT id, user_id, kind, content, metadata, created_at
            FROM memory_entries
            WHERE user_id = %s AND kind = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, kind, limit))
    else:
        query = """
            SELECT id, user_id, kind, content, metadata, created_at
            FROM memory_entries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, limit))

def list_memories_by_goal(user_id: str, goal_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, kind, content, metadata, created_at
        FROM memory_entries
        WHERE user_id = %s AND (metadata->>'goal_id')::int = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    return fetch_all(query, (user_id, goal_id, limit))

def upsert_profile_snapshot(user_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO profile_snapshots (user_id, snapshot, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET snapshot = EXCLUDED.snapshot, updated_at = NOW()
        RETURNING user_id, snapshot, updated_at
    """
    return execute_and_fetch_one(query, (user_id, Json(snapshot))) or {}
