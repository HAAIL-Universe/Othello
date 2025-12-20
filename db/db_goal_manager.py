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
- All goals belong to a default user_id (can be extended for multi-user support)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from db import goals_repository


class DbGoalManager:
    """
    Database-backed GoalManager that mimics the interface of the file-based GoalManager.
    
    Maps between the old GoalEntry format (id, text, deadline, created_at)
    and the new database schema (id, title, description, status, etc.).
    """
    
    DEFAULT_USER_ID = "1"  # For single-user mode; extend later for multi-user
    
    def __init__(self) -> None:
        self.active_goal_id: Optional[int] = None
        self.logger = logging.getLogger("GoalManager")
    
    # ------------------------------------------------------------------
    # Helpers for per-goal log events (DB-backed)
    # ------------------------------------------------------------------
    def add_note_to_goal(self, goal_id: int, role: str, content: str) -> None:
        """
        Append a note to this goal's log (DB goal_events).
        """
        from db.goal_events_repository import safe_append_goal_event
        if role not in ("user", "othello", "system"):
            role = "system"
        
        if self.get_goal(goal_id) is None:
            return
        
        note = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "role": role,
            "content": content,
        }
        event = safe_append_goal_event(self.DEFAULT_USER_ID, goal_id, None, "note", note)
        if not event:
            self.logger.warning("DbGoalManager: goal_events append skipped for goal %s", goal_id)
    
    def get_recent_notes(self, goal_id: int, max_notes: int = 10) -> List[Dict[str, Any]]:
        """
        Load up to `max_notes` most recent notes from goal_events.
        """
        from db.goal_events_repository import safe_list_goal_events
        events = safe_list_goal_events(self.DEFAULT_USER_ID, goal_id, limit=max_notes)
        notes = [
            event.get("payload")
            for event in events
            if event.get("event_type") == "note" and isinstance(event.get("payload"), dict)
        ]
        notes.reverse()
        return notes[:max_notes]
    
    def build_goal_context(self, goal_id: int, max_notes: int = 10) -> str:
        """
        Construct a text block summarising the goal + recent notes for LLM context.
        """
        goal = self.get_goal(goal_id)
        if goal is None:
            return ""
        
        lines = [
            f"Active Goal #{goal['id']}: {goal['text']}",
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
    # Database-backed goal operations (mapping to repository)
    # ------------------------------------------------------------------
    
    def _db_to_legacy_format(self, db_goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert database goal format to legacy GoalEntry format.
        
        Database: {id, user_id, title, description, status, priority, ...}
        Legacy: {id, text, deadline, created_at, conversation}
        """
        # Extract conversation from JSONL file
        conversation = self.get_recent_notes(db_goal["id"], max_notes=100)
        
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
    
    def add_goal(self, text: str, deadline: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new goal to the database and set it as active.
        """
        data = {
            "title": text,
            "description": "",
            "status": "active",
        }
        db_goal = goals_repository.create_goal(data, self.DEFAULT_USER_ID)
        goal_dict = self._db_to_legacy_format(db_goal)
        
        # Automatically set newly created goal as active
        goal_id = goal_dict.get("id")
        if goal_id:
            self.set_active_goal(goal_id)
            self.logger.info(
                f"GoalManager: created goal #{goal_id} and set it as active for user {self.DEFAULT_USER_ID}"
            )
        
        return goal_dict
    
    def list_goals(self) -> List[Dict[str, Any]]:
        """
        Return all goals for the default user in legacy format.
        """
        db_goals = goals_repository.list_goals(self.DEFAULT_USER_ID, include_archived=False)
        return [self._db_to_legacy_format(g) for g in db_goals]
    
    def get_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Return a single goal by ID in legacy format.
        """
        db_goal = goals_repository.get_goal(goal_id, self.DEFAULT_USER_ID)
        if db_goal is None:
            return None
        return self._db_to_legacy_format(db_goal)
    
    def update_goal(
        self,
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
        
        if not fields:
            return self.get_goal(goal_id)
        
        db_goal = goals_repository.update_goal_meta(goal_id, fields)
        if db_goal is None:
            return None
        
        print(f"[DbGoalManager] Updated goal {goal_id}: {db_goal}")
        return self._db_to_legacy_format(db_goal)
    
    def update_goal_plan(
        self,
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
        db_goal = goals_repository.update_goal_from_conversation(
            goal_id=goal_id,
            new_plan=plan,
            new_checklist=checklist,
            new_summary=summary,
        )
        
        if db_goal is None:
            return None
        
        print(f"[DbGoalManager] Updated goal plan for #{goal_id}")
        return self._db_to_legacy_format(db_goal)
    
    def delete_goal(self, goal_id: int) -> bool:
        """
        Remove a goal by ID.
        """
        success = goals_repository.delete_goal(goal_id, self.DEFAULT_USER_ID)
        if success:
            print(f"[DbGoalManager] Deleted goal {goal_id}")
        return success

    def archive_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Archive a goal by ID (soft delete).
        """
        db_goal = goals_repository.archive_goal(goal_id, self.DEFAULT_USER_ID)
        if db_goal is None:
            return None
        self.logger.info("DbGoalManager: Archived goal %s", goal_id)
        return self._db_to_legacy_format(db_goal)
    
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
        self.logger.info(f"GoalManager: Active goal set to #{goal_id}")
        return True
    
    def get_active_goal(self) -> Optional[Dict[str, Any]]:
        if self.active_goal_id is None:
            return None
        return self.get_goal(self.active_goal_id)
    
    # ------------------------------------------------------------------
    # Lookup by name
    # ------------------------------------------------------------------
    
    def find_goal_by_name(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Find a goal whose title matches the query (case-insensitive substring).
        """
        q = query.strip().lower()
        if not q:
            return None
        
        all_goals = self.list_goals()
        
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
    
    def find_goal_by_id_or_name(self, identifier: str | int) -> Optional[Dict[str, Any]]:
        """
        Try interpreting the identifier as an ID first, then as a name query.
        """
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
        
        if isinstance(identifier, str):
            return self.find_goal_by_name(identifier)
        return None

    # ------------------------------------------------------------------
    # Plan step management (multi-step goal planning)
    # ------------------------------------------------------------------
    
    def save_goal_plan(self, goal_id: int, plan_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        if self.get_goal(goal_id) is None:
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
    
    def get_goal_with_plan(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a goal with its associated plan steps.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            Goal dictionary with an additional 'plan_steps' key containing the ordered list of steps,
            or None if the goal doesn't exist
        """
        goal = self.get_goal(goal_id)
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
    
    def update_plan_step_status(self, goal_id: int, step_id: int, status: str) -> Optional[Dict[str, Any]]:
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
        if self.get_goal(goal_id) is None:
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
    
    def get_next_action_for_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next incomplete step for a goal.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            Next incomplete step dictionary, or None if all steps are done or goal doesn't exist
        """
        if self.get_goal(goal_id) is None:
            return None

        try:
            return goals_repository.get_next_incomplete_step(goal_id)
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, no next action for goal {goal_id}: {exc}"
            )
            return None
    
    def get_all_plan_steps(self, goal_id: int) -> List[Dict[str, Any]]:
        """
        Get all plan steps for a goal, ordered by step_index.
        
        Args:
            goal_id: The goal ID
        
        Returns:
            List of step dictionaries
        """
        if self.get_goal(goal_id) is None:
            return []

        try:
            return goals_repository.get_plan_steps_for_goal(goal_id)
        except Exception as exc:
            self.logger.warning(
                f"DbGoalManager: plan_steps storage unavailable, returning no steps for goal {goal_id}: {exc}"
            )
            return []

