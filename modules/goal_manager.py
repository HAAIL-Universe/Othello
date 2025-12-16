# modules/goal_manager.py

from typing import List, Optional, TypedDict, Literal
from datetime import datetime
from pathlib import Path
import json


class GoalEntry(TypedDict):
    """
    Typed representation of a single goal in Othello.
    """
    id: int
    text: str
    deadline: Optional[str]
    created_at: str


class GoalNote(TypedDict):
    """
    A single note attached to a goal's conversation log.
    """
    timestamp: str
    role: Literal["user", "othello", "system"]
    content: str


class GoalManager:
    """
    GoalManager for Othello.

    - Stores goals in memory AND on disk (data/goals.json).
    - Maintains an 'active_goal_id' so the API can route messages.
    - For each goal, keeps a JSONL log in data/goal_logs/goal_<id>.jsonl
      containing the conversation notes/updates for that goal.
    """

    def __init__(self, user_id: str = "1") -> None:
        self.user_id = user_id
        self.active_goal_id: Optional[int] = None

    # ------------------------------------------------------------------
    # Persistence: goals list
    # ------------------------------------------------------------------
    # All persistence is now DB-backed; no-op legacy disk methods.

    # ------------------------------------------------------------------
    # Helpers for per-goal log "folders"
    # ------------------------------------------------------------------
    # No-op: logs are now in DB goal_events.

    def add_note_to_goal(self, goal_id: int, role: str, content: str) -> None:
        """
        Append a note to this goal's log (now DB-backed).
        """
        from db.goal_events_repository import append_goal_event
        if role not in ("user", "othello", "system"):
            role = "system"
        if self.get_goal(goal_id) is None:
            return
        note = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "role": role,
            "content": content,
        }
        append_goal_event(self.user_id, goal_id, None, "note", note)

    def get_recent_notes(self, goal_id: int, max_notes: int = 10) -> List[GoalNote]:
        """
        Load up to `max_notes` most recent notes from the goal's log (DB-backed).
        """
        from db.goal_events_repository import list_goal_events
        events = list_goal_events(self.user_id, goal_id, limit=max_notes)
        notes = [e["payload"] for e in events if e["event_type"] == "note"]
        return notes[:max_notes]

    def build_goal_context(self, goal_id: int, max_notes: int = 10) -> str:
        """
        Construct a text block summarising the goal + recent notes (DB-backed).
        """
        goal = self.get_goal(goal_id)
        if goal is None:
            return ""
        lines = [
            f"Active Goal #{goal['id']}: {goal.get('title', goal.get('text', ''))}",
        ]
        if goal.get("deadline"):
            lines.append(f"Deadline: {goal['deadline']}")
        lines.append("")
        notes = self.get_recent_notes(goal_id, max_notes=max_notes)
        if notes:
            lines.append("Recent updates and conversation about this goal:")
            for n in notes:
                ts = n.get("timestamp", "")
                role = n.get("role", "system")
                content = n.get("content", "")
                lines.append(f"- [{role} @ {ts}]: {content}")
        else:
            lines.append("No prior notes for this goal yet.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    # No longer needed: IDs are DB-assigned.

    # ------------------------------------------------------------------
    # Public API: goals
    # ------------------------------------------------------------------
    def add_goal(self, text: str, deadline: Optional[str] = None) -> GoalEntry:
        """
        Add a new goal and return the stored entry (DB-backed).
        """
        from db.goals_repository import create_goal
        data = {"title": text, "deadline": deadline}
        entry = create_goal(data, self.user_id)
        print(f"[GoalManager] Added goal: {entry}")
        return entry

    def list_goals(self) -> List[GoalEntry]:
        """Return all goals recorded so far (DB-backed)."""
        from db.goals_repository import list_goals
        return list_goals(self.user_id)

    def get_goal(self, goal_id: int) -> Optional[GoalEntry]:
        """Return a single goal by ID, or None if not found (DB-backed)."""
        from db.goals_repository import get_goal
        return get_goal(goal_id, self.user_id)

    def update_goal(
        self,
        goal_id: int,
        *,
        text: Optional[str] = None,
        deadline: Optional[str] = None,
    ) -> Optional[GoalEntry]:
        """
        Update an existing goal in-place. Returns the updated goal, or None if the ID doesn't exist (DB-backed).
        """
        from db.goals_repository import update_goal_meta
        fields = {}
        if text is not None:
            fields["title"] = text
        if deadline is not None:
            fields["deadline"] = deadline
        updated = update_goal_meta(goal_id, fields)
        print(f"[GoalManager] Updated goal {goal_id}: {updated}")
        return updated

    def delete_goal(self, goal_id: int) -> bool:
        """
        Remove a goal by ID. Returns True if deleted, False if not found (DB-backed).
        """
        from db.goals_repository import delete_goal
        result = delete_goal(goal_id, self.user_id)
        print(f"[GoalManager] Deleted goal {goal_id}: {result}")
        return result

    # ------------------------------------------------------------------
    # Active goal handling
    # ------------------------------------------------------------------
    def set_active_goal(self, goal_id: int) -> bool:
        """
        Mark a goal as active for the current session.
        """
        if self.get_goal(goal_id) is None:
            return False
        self.active_goal_id = goal_id
        print(f"[GoalManager] Active goal set to #{goal_id}")
        return True

    def get_active_goal(self) -> Optional[GoalEntry]:
        if self.active_goal_id is None:
            return None
        return self.get_goal(self.active_goal_id)

    # ------------------------------------------------------------------
    # Lookup by name (for "talk about <goal name>")
    # ------------------------------------------------------------------
    def find_goal_by_name(self, query: str) -> Optional[GoalEntry]:
        """
        Find a goal whose text matches the query (case-insensitive substring).
        This lets the user refer to a goal by its title instead of ID.
        """
        q = query.strip().lower()
        if not q:
            return None

        # Simple heuristic: prefer goals where the title starts with the query,
        # then fall back to any substring match.
        starts_with = []
        contains = []

        for g in self.goals:
            title = g["text"].strip().lower()
            if title.startswith(q):
                starts_with.append(g)
            elif q in title:
                contains.append(g)

        if starts_with:
            return starts_with[-1]  # latest that starts with query
        if contains:
            return contains[-1]     # latest that contains query
        return None

    def find_goal_by_id_or_name(self, identifier: str | int) -> Optional[GoalEntry]:
        """
        Convenience helper: try interpreting the identifier as an ID first,
        then as a name query.
        """
        # Try numeric ID first
        try:
            if isinstance(identifier, str):
                num = int(identifier)
            else:
                num = int(identifier)
            goal = self.get_goal(num)
            if goal is not None:
                return goal
        except (ValueError, TypeError):
            pass

        # Fallback: use as name query
        if isinstance(identifier, str):
            return self.find_goal_by_name(identifier)
        return None

    # ------------------------------------------------------------------
    # Hard reset (clear stack + logs)
    # ------------------------------------------------------------------
    def clear_all(self, delete_logs: bool = True, reset_ids: bool = True) -> None:
        """
        Clear all goals and logs (DB-backed).
        """
        from db.goals_repository import clear_all_goals
        clear_all_goals(self.user_id)
        self.active_goal_id = None
        print("[GoalManager] All goals and logs cleared.")
