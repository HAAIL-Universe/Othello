"""Repository helpers for reflection_entries (self-reflection log)."""
from typing import Any, Dict, List
from db.database import execute_and_fetch_one, fetch_all

def append_reflection(user_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO reflection_entries (user_id, content, metadata, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING id, user_id, content, metadata, created_at
    """
    return execute_and_fetch_one(query, (user_id, content, metadata)) or {}

def list_reflections(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, content, metadata, created_at
        FROM reflection_entries
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    return fetch_all(query, (user_id, limit))
