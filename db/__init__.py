# db/__init__.py
"""
Database module for Othello.

Provides PostgreSQL database connectivity and repository functions.
"""

from db.database import init_pool, get_connection, execute_query, fetch_one, fetch_all
from db.goals_repository import (
    list_goals,
    get_goal,
    create_goal,
    update_goal_meta,
    update_goal_from_conversation,
    delete_goal
)

__all__ = [
    "init_pool",
    "get_connection",
    "execute_query",
    "fetch_one",
    "fetch_all",
    "list_goals",
    "get_goal",
    "create_goal",
    "update_goal_meta",
    "update_goal_from_conversation",
    "delete_goal",
]
