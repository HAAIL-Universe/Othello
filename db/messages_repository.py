# db/messages_repository.py
"""
Repository helpers for sessions/messages/transcripts (Phase 1 transcript spine).
"""
from typing import Optional, List, Dict, Any

from db.database import execute_and_fetch_one, fetch_all, fetch_one


def create_session(user_id: str) -> Dict[str, Any]:
    query = """
        INSERT INTO sessions (user_id, created_at)
        VALUES (%s, NOW())
        RETURNING id, user_id, created_at
    """
    return execute_and_fetch_one(query, (user_id,)) or {}


def create_message(
    *,
    user_id: str,
    transcript: str,
    source: str = "text",
    channel: str = "companion",
    session_id: Optional[int] = None,
    status: str = "ready",
    stt_provider: Optional[str] = None,
    stt_model: Optional[str] = None,
    audio_duration_ms: Optional[int] = None,
    error: Optional[str] = None,
    create_session_if_missing: bool = False,
) -> Dict[str, Any]:
    if session_id is None and create_session_if_missing:
        session = create_session(user_id)
        session_id = session.get("id")

    query = """
        INSERT INTO messages (
            user_id,
            session_id,
            source,
            channel,
            transcript,
            status,
            stt_provider,
            stt_model,
            audio_duration_ms,
            error,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id, user_id, session_id, source, channel, transcript, status,
                  stt_provider, stt_model, audio_duration_ms, error, created_at
    """
    record = execute_and_fetch_one(
        query,
        (
            user_id,
            session_id,
            source,
            channel,
            transcript,
            status,
            stt_provider,
            stt_model,
            audio_duration_ms,
            error,
        ),
    ) or {}

    if record and transcript:
        transcript_query = """
            INSERT INTO transcripts (message_id, transcript, created_at)
            VALUES (%s, %s, NOW())
            RETURNING id, message_id, transcript, created_at
        """
        execute_and_fetch_one(transcript_query, (record.get("id"), transcript))

    return record


def list_messages_by_ids(user_id: str, message_ids: List[int]) -> List[Dict[str, Any]]:
    if not message_ids:
        return []
    query = """
        SELECT id, user_id, session_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND id = ANY(%s)
        ORDER BY id ASC
    """
    return fetch_all(query, (user_id, message_ids))


def list_messages_for_session(user_id: str, session_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, session_id, source, transcript, status, created_at
        FROM messages
        WHERE user_id = %s AND session_id = %s
        ORDER BY id ASC
    """
    return fetch_all(query, (user_id, session_id))


def list_recent_messages(user_id: str, limit: int = 50, channel: str = "companion") -> List[Dict[str, Any]]:
    query = """
        SELECT id, user_id, session_id, source, channel, transcript, status, error, created_at
        FROM (
            SELECT id, user_id, session_id, source, channel, transcript, status, error, created_at
            FROM messages
            WHERE user_id = %s AND channel = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
        ) recent
        ORDER BY created_at ASC, id ASC
    """
    return fetch_all(query, (user_id, channel, limit))


def get_message(user_id: str, message_id: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, session_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND id = %s
    """
    return fetch_one(query, (user_id, message_id))


def update_message(
    *,
    user_id: str,
    message_id: int,
    status: Optional[str] = None,
    transcript: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    current_transcript = None
    if transcript is not None:
        current = get_message(user_id, message_id)
        if current:
            current_transcript = current.get("transcript")
    set_clauses = []
    params: List[Any] = []

    if status is not None:
        set_clauses.append("status = %s")
        params.append(status)
    if transcript is not None:
        set_clauses.append("transcript = %s")
        params.append(transcript)

    if not set_clauses:
        return get_message(user_id, message_id)

    query = f"""
        UPDATE messages
        SET {", ".join(set_clauses)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, session_id, source, transcript, status, error, created_at
    """
    params.extend([user_id, message_id])
    record = execute_and_fetch_one(query, tuple(params))

    transcript_changed = transcript is not None and transcript != current_transcript
    if record and transcript_changed:
        transcript_query = """
            INSERT INTO transcripts (message_id, transcript, created_at)
            VALUES (%s, %s, NOW())
            RETURNING id, message_id, transcript, created_at
        """
        execute_and_fetch_one(transcript_query, (message_id, transcript))

    return record
