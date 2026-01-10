# db/messages_repository.py
"""
Repository helpers for sessions/messages/transcripts (Phase 1 transcript spine).
"""
from typing import Optional, List, Dict, Any

from db.database import execute_and_fetch_one, fetch_all, fetch_one, execute_query, get_connection


def create_session(user_id: str) -> Dict[str, Any]:
    query = """
        INSERT INTO sessions (user_id, created_at)
        VALUES (%s, NOW())
        RETURNING id, user_id, created_at
    """
    return execute_and_fetch_one(query, (user_id,)) or {}


def list_sessions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List sessions for a user, ordered by most recent activity.
    Computes updated_at from max message time if needed.
    """
    query = """
        SELECT s.id as conversation_id, s.created_at,
               s.duet_narrator_text, s.duet_narrator_updated_at, s.duet_narrator_msg_count,
               COALESCE(MAX(m.created_at), s.created_at) as updated_at
        FROM sessions s
        LEFT JOIN messages m ON s.id = m.session_id
        WHERE s.user_id = %s
        GROUP BY s.id, s.created_at, s.duet_narrator_text, s.duet_narrator_updated_at, s.duet_narrator_msg_count
        ORDER BY updated_at DESC
        LIMIT %s
    """
    return fetch_all(query, (user_id, limit))


def create_message(
    *,
    user_id: str,
    transcript: str,
    source: str = "text",
    channel: str = "companion",
    session_id: Optional[int] = None,
    checkpoint_id: Optional[int] = None,
    client_message_id: Optional[str] = None,
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
            checkpoint_id,
            client_message_id,
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status,
                  stt_provider, stt_model, audio_duration_ms, error, created_at
    """
    record = execute_and_fetch_one(
        query,
        (
            user_id,
            session_id,
            checkpoint_id,
            client_message_id,
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
        SELECT id, user_id, session_id, checkpoint_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND id = ANY(%s)
        ORDER BY id ASC
    """
    return fetch_all(query, (user_id, message_ids))


def list_messages_for_session(user_id: str, session_id: int, limit: int = 50, channel: Optional[str] = "companion") -> List[Dict[str, Any]]:
    if channel:
        if channel == "companion":
             query = """
                SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
                FROM (
                    SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
                    FROM messages
                    WHERE user_id = %s AND session_id = %s AND (channel = 'companion' OR channel = 'duet' OR channel = 'auto')
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s
                ) recent
                ORDER BY created_at ASC, id ASC
            """
             return fetch_all(query, (user_id, session_id, limit))

        query = """
            SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
            FROM (
                SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
                FROM messages
                WHERE user_id = %s AND session_id = %s AND channel = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
            ) recent
            ORDER BY created_at ASC, id ASC
        """
        return fetch_all(query, (user_id, session_id, channel, limit))
    else:
        # Fetch all messages in session regardless of channel
        query = """
            SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
            FROM (
                SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
                FROM messages
                WHERE user_id = %s AND session_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
            ) recent
            ORDER BY created_at ASC, id ASC
        """
        return fetch_all(query, (user_id, session_id, limit))


def list_recent_messages(user_id: str, limit: int = 50, channel: str = "companion") -> List[Dict[str, Any]]:
    # If channel is 'duet', we still query 'companion' underlying but theoretically could differ.
    # Actually, Duet UI might pass 'duet' as channel param to API, which then saves as 'duet'.
    # But filtering by it might be strict.
    # Phase 23 Compatibility: If channel is 'companion', we also include 'duet' to show history in main chat?
    # Or strict separation?
    # For now, let's allow "companion" to fetch both "companion" and "auto" and "duet" if we want unified history.
    
    if channel == "companion":
         query = """
            SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
            FROM (
                SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
                FROM messages
                WHERE user_id = %s AND (channel = 'companion' OR channel = 'duet' OR channel = 'auto')
                ORDER BY created_at DESC, id DESC
                LIMIT %s
            ) recent
            ORDER BY created_at ASC, id ASC
        """
         return fetch_all(query, (user_id, limit))
    
    query = """
        SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
        FROM (
            SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, channel, transcript, status, error, created_at
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
        SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND id = %s
    """
    return fetch_one(query, (user_id, message_id))


def get_message_by_client_id(user_id: str, client_message_id: str) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND client_message_id = %s
    """
    return fetch_one(query, (user_id, client_message_id))


def update_message(
    *,
    user_id: str,
    message_id: int,
    status: Optional[str] = None,
    transcript: Optional[str] = None,
    checkpoint_id: Optional[int] = None,
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
    if checkpoint_id is not None:
        set_clauses.append("checkpoint_id = %s")
        params.append(checkpoint_id)

    if not set_clauses:
        return get_message(user_id, message_id)

    query = f"""
        UPDATE messages
        SET {", ".join(set_clauses)}
        WHERE user_id = %s AND id = %s
        RETURNING id, user_id, session_id, checkpoint_id, source, transcript, status, error, created_at
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

def get_active_checkpoint(user_id: str, channel: str = "companion") -> Optional[int]:
    """
    Get the most recent checkpoint_id from the user's message stream.
    Used to propagate context linkage to new messages.
    """
    query = """
        SELECT checkpoint_id
        FROM messages
        WHERE user_id = %s AND channel = %s AND checkpoint_id IS NOT NULL
        ORDER BY created_at DESC, id DESC
        LIMIT 1
    """
    res = fetch_one(query, (user_id, channel))
    return res.get("checkpoint_id") if res else None

def get_linked_messages_from_checkpoint(user_id: str, checkpoint_id: int) -> List[Dict[str, Any]]:
    """
    Reconstruct context window from a checkpoint.
    Includes the checkpoint message itself (if it self-references) and all subsequent linked messages.
    """
    query = """
        SELECT id, user_id, session_id, checkpoint_id, client_message_id, source, transcript, status, error, created_at
        FROM messages
        WHERE user_id = %s AND (id = %s OR checkpoint_id = %s)
        ORDER BY created_at ASC, id ASC
    """
    return fetch_all(query, (user_id, checkpoint_id, checkpoint_id))


def count_session_messages(user_id: str, session_id: int) -> int:
    query = "SELECT COUNT(*) as count FROM messages WHERE user_id=%s AND session_id=%s"
    result = fetch_one(query, (user_id, session_id))
    return int(result.get("count", 0)) if result else 0


def create_draft_context(user_id: str, session_id: int, start_message_id: int, intent_kind: str, status: str = "active") -> Dict[str, Any]:
    """
    Populate the draft_contexts table when an intent is detected.
    """
    query = """
        INSERT INTO draft_contexts (user_id, session_id, start_message_id, intent_kind, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, user_id, session_id, start_message_id, intent_kind, status, created_at
    """
    return execute_and_fetch_one(query, (user_id, session_id, start_message_id, intent_kind, status)) or {}


def get_latest_active_draft_context(user_id: str, session_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent active draft context for a session (or user).
    """
    if session_id:
        query = """
            SELECT id, user_id, session_id, start_message_id, intent_kind, status, created_at
            FROM draft_contexts
            WHERE user_id = %s AND session_id = %s AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """
        return fetch_one(query, (user_id, session_id))
    else:
        query = """
            SELECT id, user_id, session_id, start_message_id, intent_kind, status, created_at
            FROM draft_contexts
            WHERE user_id = %s AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """
        return fetch_one(query, (user_id,))


def get_session_narrator_state(user_id: str, session_id: int) -> Dict[str, Any]:
    query = """
        SELECT duet_narrator_text, duet_narrator_msg_count, duet_narrator_updated_at, duet_narrator_carryover_due
        FROM sessions 
        WHERE user_id=%s AND id=%s
    """
    return fetch_one(query, (user_id, session_id)) or {}


def update_session_narrator_state(
    user_id: str, 
    session_id: int, 
    text: str, 
    msg_count: int, 
    carryover_due: Optional[bool] = None
) -> int:
    # Build query dynamically to handle optional updates (or just update all if stable)
    # Simpler: just update all. "carryover_due" defaults to False in DB, pass it explicitly if needed.
    # However, to avoid drift if we pass None, we should fetch-modify-write or just handle it logic side.
    # For Minimal Diff, let's just make it explicit param.
    
    if carryover_due is not None:
        query = """
            UPDATE sessions 
            SET duet_narrator_text=%s, duet_narrator_msg_count=%s, duet_narrator_carryover_due=%s, duet_narrator_updated_at=NOW() 
            WHERE id=%s
        """
        params = (text, msg_count, carryover_due, session_id)
    else:
        # Compatibility override: don't touch carryover if not specified? 
        # Actually safer to keep it consistent. Let's assume most callers won't pass it.
        # But we need to preserve it if not passed.
        # Minimal diff: use COALESCE? No, we need python logic.
        query = """
            UPDATE sessions 
            SET duet_narrator_text=%s, duet_narrator_msg_count=%s, duet_narrator_updated_at=NOW() 
            WHERE id=%s
        """
        params = (text, msg_count, session_id)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount


def list_all_session_messages_for_summary(user_id: str, session_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT source, transcript, created_at 
        FROM messages 
        WHERE user_id=%s AND session_id=%s 
        ORDER BY created_at ASC, id ASC
    """
    return fetch_all(query, (user_id, session_id))


def get_next_narrator_block_index(user_id: str, session_id: int) -> int:
    query = """
        SELECT COALESCE(MAX(block_index), 0) + 1 as next_idx 
        FROM session_narrator_blocks 
        WHERE user_id=%s AND session_id=%s
    """
    res = fetch_one(query, (user_id, session_id))
    return int(res.get("next_idx", 1)) if res else 1


def insert_session_narrator_block(user_id: str, session_id: int, block_index: int, raw_text: str, summary_text: str) -> int:
    query = """
        INSERT INTO session_narrator_blocks (user_id, session_id, block_index, raw_text, summary_text, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id
    """
    res = execute_and_fetch_one(query, (user_id, session_id, block_index, raw_text, summary_text))
    return res.get("id") if res else 0


def list_session_narrator_block_summaries(user_id: str, session_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    limit_clause = "LIMIT %s" if limit else ""
    params = [user_id, session_id]
    if limit:
        params.append(limit)
    
    query = f"""
        SELECT block_index, summary_text, created_at
        FROM session_narrator_blocks
        WHERE user_id=%s AND session_id=%s
        ORDER BY block_index ASC
        {limit_clause}
    """
    return fetch_all(query, tuple(params)) 
