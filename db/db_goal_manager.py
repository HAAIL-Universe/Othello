# db/db_goal_manager.py
"""
Database-backed GoalManager wrapper for Othello.

This class provides the same interface as modules/goal_manager.py but uses
PostgreSQL database for storage instead of JSON files.

It bridges the existing GoalManager API with the new goals_repository functions,
maintaining backward compatibility with existing Flask routes.

Key differences from file-based GoalManager:
- Goals stored in PostgreSQL 'goals' table instead of data/goals.json
- Conversation logs stored in goal_events (DB truth)
- All goal operations require an explicit user_id
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging

from db import goals_repository
from db.database import execute_and_fetch_one


class DbGoalManager:
    """
    Database-backed GoalManager that mimics the interface of the file-based GoalManager.
    
    Maps between the old GoalEntry format (id, text, deadline, created_at)
    and the new database schema (id, title, description, status, etc.).
    """
    
    def __init__(self) -> None:
        self.active_goal_id: Dict[str, Optional[int]] = {}
        self.logger = logging.getLogger("GoalManager")

    def _require_user_id(self, user_id: str) -> str:
        uid = str(user_id or "").strip()
        if not uid:
            raise ValueError("user_id is required")
        return uid
    
    # ------------------------------------------------------------------
    # Helpers for per-goal log events (DB-backed)
    # ------------------------------------------------------------------
    def add_note_to_goal(
        self,
        user_id: str,
        goal_id: int,
        role: str,
        content: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Append a note to this goal's log (DB goal_events).
        """
        from db.goal_events_repository import safe_append_goal_event
        uid = self._require_user_id(user_id)
        if role not in ("user", "othello", "system"):
            role = "system"
        
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            return {"ok": False, "reason": "goal_not_found"}
        
        note = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "role": role,
            "content": content,
        }
        result = safe_append_goal_event(
            uid,
            goal_id,
            None,
            "note",
            note,
            request_id=request_id,
        )
        if not result.get("ok", False):
            self.logger.warning(
                "DbGoalManager: goal_events append skipped for goal %s reason=%s",
                goal_id,
                result.get("reason", "unknown"),
            )
        return result
    
    def get_recent_notes(self, user_id: str, goal_id: int, max_notes: int = 10) -> List[Dict[str, Any]]:
        """
        Load up to `max_notes` most recent notes from goal_events.
        """
        from db.goal_events_repository import safe_list_goal_events
        uid = self._require_user_id(user_id)
        events = safe_list_goal_events(uid, goal_id, limit=max_notes)
        notes: List[Dict[str, Any]] = []
        for event in events:
            if event.get("event_type") != "note":
                continue
            payload = event.get("payload")
            if not isinstance(payload, dict):
                continue
            role = payload.get("role")
            content = payload.get("content") or payload.get("message")
            if not role or not content:
                continue
            if not isinstance(role, str) or not isinstance(content, str):
                continue
            occurred_at = event.get("occurred_at")
            if occurred_at is not None and hasattr(occurred_at, "isoformat"):
                occurred_at = occurred_at.isoformat()
            elif occurred_at is not None:
                occurred_at = str(occurred_at)
            note = {
                "timestamp": payload.get("timestamp") or occurred_at or "",
                "role": role,
                "content": content,
            }
            notes.append(note)
        notes.reverse()
        return notes[:max_notes]
    
    def build_goal_context(self, user_id: str, goal_id: int, max_notes: int = 10) -> str:
        """
        Construct a text block summarising the goal + recent notes for LLM context.
        """
        uid = self._require_user_id(user_id)
        goal = self.get_goal(uid, goal_id, include_conversation=False)
        if goal is None:
            return ""
        
        lines = [
            f"Active Goal #{goal['id']}: {goal['text']}",
        ]
        if goal.get("deadline"):
            lines.append(f"Deadline: {goal['deadline']}")
        lines.append("")
        
        notes = self.get_recent_notes(uid, goal_id, max_notes=max_notes)
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
    # Database-backed goal operations (mapping to repository)
    # ------------------------------------------------------------------
    
    def _db_to_legacy_format(
        self,
        user_id: str,
        db_goal: Dict[str, Any],
        *,
        include_conversation: bool = False,
        max_notes: int = 25,
    ) -> Dict[str, Any]:
        """
        Convert database goal format to legacy GoalEntry format.
        
        Database: {id, user_id, title, description, status, priority, ...}
        Legacy: {id, text, deadline, created_at, conversation}
        """
        # Extract conversation from JSONL file
        uid = self._require_user_id(user_id)
        conversation = []
        if include_conversation:
            conversation = self.get_recent_notes(uid, db_goal["id"], max_notes=max_notes)
        
        return {
            "id": db_goal["id"],
            "text": db_goal["title"],
            "deadline": None,  # Not in current DB schema, can be added later
            "created_at": db_goal["created_at"].isoformat() if hasattr(db_goal["created_at"], "isoformat") else str(db_goal["created_at"]),
            "conversation": conversation,  # Include for UI
            "description": db_goal.get("description", ""),
            "status": db_goal.get("status", "active"),
            "priority": db_goal.get("priority", "medium"),
            "plan": db_goal.get("plan", ""),
            "checklist": db_goal.get("checklist", []),
        }
    
    def add_goal(self, user_id: str, text: str, deadline: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new goal to the database and set it as active.
        """
        data = {
            "title": text,
            "description": "",
            "status": "active",
        }
        uid = self._require_user_id(user_id)
        db_goal = goals_repository.create_goal(data, uid)
        goal_dict = self._db_to_legacy_format(uid, db_goal, include_conversation=False)
        
        # Automatically set newly created goal as active
        goal_id = goal_dict.get("id")
        if goal_id:
            self.set_active_goal(uid, goal_id)
            self.logger.info(
                f"GoalManager: created goal #{goal_id} and set it as active for user {uid}"
            )
        
        return goal_dict
    
    def list_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Return all goals for the default user in legacy format.
        """
        uid = self._require_user_id(user_id)
        db_goals = goals_repository.list_goals(uid, include_archived=False)
        return [
            self._db_to_legacy_format(uid, g, include_conversation=False)
            for g in db_goals
        ]
    
    def get_goal(
        self,
        user_id: str,
        goal_id: int,
        *,
        include_conversation: bool = True,
        max_notes: int = 25,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a single goal by ID in legacy format.
        """
        uid = self._require_user_id(user_id)
        db_goal = goals_repository.get_goal(goal_id, uid)
        if db_goal is None:
            return None
        return self._db_to_legacy_format(
            uid,
            db_goal,
            include_conversation=include_conversation,
            max_notes=max_notes,
        )
    
    def update_goal(
        self,
        user_id: str,
        goal_id: int,
        *,
        text: Optional[str] = None,
        deadline: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing goal's title.
        """
        fields = {}
        if text is not None:
            fields["title"] = text
        
        uid = self._require_user_id(user_id)
        if not fields:
            return self.get_goal(uid, goal_id)
        
        db_goal = goals_repository.update_goal_meta(goal_id, fields, user_id=uid)
        if db_goal is None:
            return None

        self.logger.info("DbGoalManager: Updated goal %s", goal_id)
        return self._db_to_legacy_format(uid, db_goal, include_conversation=False)

    def _update_goal_description(
        self,
        user_id: str,
        goal_id: int,
        new_description: str,
    ) -> Optional[Dict[str, Any]]:
        uid = self._require_user_id(user_id)
        query = """
            UPDATE goals
            SET description = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, title, description, status, priority, category,
                      plan, checklist, last_conversation_summary, created_at, updated_at
        """
        db_goal = execute_and_fetch_one(query, (new_description, goal_id, uid))
        if db_goal is None:
            return None
        return self._db_to_legacy_format(uid, db_goal)

    def replace_goal_description(
        self,
        user_id: str,
        goal_id: int,
        new_description: str,
        request_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Replace the goal description in full for this user/goal.
        """
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id) is None:
            return None
        updated_goal = self._update_goal_description(uid, goal_id, new_description)
        if updated_goal is None:
            self.logger.warning("DbGoalManager: goal description replace failed for goal %s", goal_id)
        return updated_goal

    def append_goal_description(
        self,
        user_id: str,
        goal_id: int,
        extra_text: str,
        request_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Append extra text to the goal description.
        """
        uid = self._require_user_id(user_id)
        goal = self.get_goal(uid, goal_id, include_conversation=True, max_notes=25)
        if goal is None:
            return None
        base_description = (goal.get("description") or "").rstrip()
        extra = (extra_text or "").strip()
        if base_description:
            new_description = f"{base_description}\n\n{extra}"
        else:
            new_description = extra
        updated_goal = self._update_goal_description(uid, goal_id, new_description)
        if updated_goal is None:
            self.logger.warning("DbGoalManager: goal description append failed for goal %s", goal_id)
        return updated_goal
    
    def update_goal_plan(
        self,
        user_id: str,
        goal_id: int,
        plan: Optional[str] = None,
        checklist: Optional[List[Dict[str, Any]]] = None,
        summary: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a goal's plan, checklist, and conversation summary.
        This is called after the user confirms a structured plan from the LLM.
        
        Args:
            goal_id: The goal ID to update
            plan: New plan text (optional)
            checklist: New checklist as list of dicts with 'text' and 'done' keys (optional)
            summary: Conversation summary for this update (optional)
        
        Returns:
            Updated goal in legacy format, or None if failed
        """
        uid = self._require_user_id(user_id)
        db_goal = goals_repository.update_goal_from_conversation(
            goal_id=goal_id,
            new_plan=plan,
            new_checklist=checklist,
            new_summary=summary,
        )
        
        if db_goal is None:
            return None
        
        self.logger.info("DbGoalManager: Updated goal plan for #%s", goal_id)
        return self._db_to_legacy_format(uid, db_goal, include_conversation=False)
    
    def delete_goal(self, user_id: str, goal_id: int) -> bool:
        """
        Remove a goal by ID.
        """
        uid = self._require_user_id(user_id)
        success = goals_repository.delete_goal(goal_id, uid)
        if success:
            print(f"[DbGoalManager] Deleted goal {goal_id}")
        return success

    def archive_goal(self, user_id: str, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Archive a goal by ID (soft delete).
        """
        uid = self._require_user_id(user_id)
        db_goal = goals_repository.archive_goal(goal_id, uid)
        if db_goal is None:
            return None
        self.logger.info("DbGoalManager: Archived goal %s", goal_id)
        return self._db_to_legacy_format(uid, db_goal)
    
    # ------------------------------------------------------------------
    # Active goal handling
    # ------------------------------------------------------------------
    
    def set_active_goal(self, user_id: str, goal_id: int) -> bool:
        """
        Mark a goal as active for the current session.
        """
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            return False
        self.active_goal_id[uid] = goal_id
        self.logger.info(f"GoalManager: Active goal set to #{goal_id} for user {uid}")
        return True

    def clear_active_goal(self, user_id: str) -> None:
        uid = self._require_user_id(user_id)
        if uid in self.active_goal_id:
            self.active_goal_id.pop(uid, None)
    
    def get_active_goal(self, user_id: str) -> Optional[Dict[str, Any]]:
        uid = self._require_user_id(user_id)
        goal_id = self.active_goal_id.get(uid)
        if goal_id is None:
            return None
        return self.get_goal(uid, goal_id)
    
    # ------------------------------------------------------------------
    # Lookup by name
    # ------------------------------------------------------------------
    
    def find_goal_by_name(self, user_id: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Find a goal whose title matches the query (case-insensitive substring).
        """
        q = query.strip().lower()
        if not q:
            return None
        
        uid = self._require_user_id(user_id)
        all_goals = self.list_goals(uid)
        
        starts_with = []
        contains = []
        
        for g in all_goals:
            title = g["text"].strip().lower()
            if title.startswith(q):
                starts_with.append(g)
            elif q in title:
                contains.append(g)
        
        if starts_with:
            return starts_with[-1]
        if contains:
            return contains[-1]
        return None
    
    def find_goal_by_id_or_name(self, user_id: str, identifier: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Try interpreting the identifier as an ID first, then as a name query.
        """
        try:
            if isinstance(identifier, str):
                num = int(identifier)
            else:
                num = int(identifier)
            uid = self._require_user_id(user_id)
            goal = self.get_goal(uid, num)
            if goal is not None:
                return goal
        except (ValueError, TypeError):
            pass
        
        if isinstance(identifier, str):
            return self.find_goal_by_name(user_id, identifier)
        return None

    # ------------------------------------------------------------------
    # Plan step management (multi-step goal planning)
    # ------------------------------------------------------------------
    
    def save_goal_plan(self, user_id: str, goal_id: int, plan_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Save a multi-step plan for a goal.
        
        This replaces any existing plan steps for the goal with the new list.
        Each step dict should include:
        - step_index (int): order of execution
        - description (str): the actual step text
        - status (str, optional): defaults to 'pending'
        - due_date (str or None, optional): ISO format deadline
        
        Args:
            goal_id: The goal ID to save the plan for
            plan_steps: List of step dictionaries
        
        Returns:
            List of created step dictionaries from the database
        """
        # Validate that the goal exists
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            self.logger.error(f"DbGoalManager: Cannot save plan for non-existent goal {goal_id}")
            return []
        try:
            goals_repository.delete_plan_steps_for_goal(goal_id)
            created_steps = goals_repository.create_plan_steps(goal_id, plan_steps)
            self.logger.info(f"DbGoalManager: Saved {len(created_steps)} plan steps for goal {goal_id}")
            return created_steps
        except Exception as exc:
            # In environments without the plan_steps table, gracefully degrade to no-op
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, skipping DB save for goal {goal_id}: {exc}"
            )
            return []
    
    def get_goal_with_plan(self, user_id: str, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a goal with its associated plan steps.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            Goal dictionary with an additional 'plan_steps' key containing the ordered list of steps,
            or None if the goal doesn't exist
        """
        uid = self._require_user_id(user_id)
        goal = self.get_goal(uid, goal_id)
        if goal is None:
            return None

        try:
            plan_steps = goals_repository.get_plan_steps_for_goal(goal_id)
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, returning goal {goal_id} with no steps: {exc}"
            )
            plan_steps = []

        goal["plan_steps"] = plan_steps
        return goal
    
    def update_plan_step_status(self, user_id: str, goal_id: int, step_id: int, status: str) -> Optional[Dict[str, Any]]:
        """
        Update the status of a specific plan step.
        
        Validates that the step belongs to the given goal before updating.
        
        Args:
            goal_id: The goal ID (for validation)
            step_id: The step ID to update
            status: New status ('pending', 'in_progress', 'done')
        
        Returns:
            Updated step dictionary if successful, None otherwise
        """
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            self.logger.error(f"DbGoalManager: Cannot update step for non-existent goal {goal_id}")
            return None

        try:
            plan_steps = goals_repository.get_plan_steps_for_goal(goal_id)
            step_ids = [step["id"] for step in plan_steps]

            if step_id not in step_ids:
                self.logger.error(f"DbGoalManager: Step {step_id} does not belong to goal {goal_id}")
                return None

            updated_step = goals_repository.update_plan_step_status(step_id, status)
            if updated_step:
                self.logger.info(f"DbGoalManager: Updated step {step_id} status to '{status}'")

            return updated_step
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, cannot update step {step_id} for goal {goal_id}: {exc}"
            )
            return None
    
    def get_next_action_for_goal(self, user_id: str, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next incomplete step for a goal.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            Next incomplete step dictionary, or None if all steps are done or goal doesn't exist
        """
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            return None

        try:
            return goals_repository.get_next_incomplete_step(goal_id)
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, no next action for goal {goal_id}: {exc}"
            )
            return None
    
    def get_all_plan_steps(self, user_id: str, goal_id: int) -> List[Dict[str, Any]]:
        """
        Get all plan steps for a goal, ordered by step_index.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            List of step dictionaries
        """
        uid = self._require_user_id(user_id)
        if self.get_goal(uid, goal_id, include_conversation=False) is None:
            return []

        try:
            return goals_repository.get_plan_steps_for_goal(goal_id)
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, returning no steps for goal {goal_id}: {exc}"
            )
            return []

