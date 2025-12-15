# db/database.py
"""
Database helper module for Othello.

Provides a PostgreSQL connection pool and query execution utilities
using psycopg2. Reads DATABASE_URL from environment variables.

Usage:
    from db.database import execute_query, fetch_one, fetch_all
    
    # Insert/Update/Delete
    execute_query("INSERT INTO goals (title, user_id) VALUES (%s, %s)", ("My Goal", 1))
    
    # Fetch single row
    goal = fetch_one("SELECT * FROM goals WHERE id = %s", (goal_id,))
    
    # Fetch multiple rows
    goals = fetch_all("SELECT * FROM goals WHERE user_id = %s", (user_id,))
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


# Initialize connection pool
_connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


def init_pool(min_conn: int = 1, max_conn: int = 10) -> None:
    """
    Initialize the PostgreSQL connection pool.
    Reads DATABASE_URL from environment variables.
    """
    global _connection_pool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    try:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            min_conn,
            max_conn,
            database_url
        )
        print(f"[Database] Connection pool initialized (min={min_conn}, max={max_conn})")
    except Exception as e:
        print(f"[Database] Failed to initialize connection pool: {e}")
        raise


def get_pool() -> psycopg2.pool.SimpleConnectionPool:
    """Get the connection pool, initializing it if necessary."""
    global _connection_pool
    if _connection_pool is None:
        init_pool()
    return _connection_pool


@contextmanager
def get_connection():
    """
    Context manager for getting a connection from the pool.
    Automatically returns the connection to the pool when done.
    """
    pool = get_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            pool.putconn(conn)


def execute_query(query: str, params: Optional[Tuple] = None) -> None:
    """
    Execute an INSERT, UPDATE, or DELETE query.
    
    Args:
        query: SQL query with %s placeholders
        params: Tuple of parameters to bind to the query
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()


def fetch_one(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row as a dictionary.
    
    Args:
        query: SQL query with %s placeholders
        params: Tuple of parameters to bind to the query
    
    Returns:
        Dictionary representing the row, or None if no results
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return dict(result) if result else None


def fetch_all(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Fetch all rows as a list of dictionaries.
    
    Args:
        query: SQL query with %s placeholders
        params: Tuple of parameters to bind to the query
    
    Returns:
        List of dictionaries, each representing a row
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]


def execute_and_fetch_one(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    """
    Execute an INSERT/UPDATE query and return the affected row (using RETURNING clause).
    
    Args:
        query: SQL query with RETURNING clause
        params: Tuple of parameters to bind to the query
    
    Returns:
        Dictionary representing the returned row, or None
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            result = cursor.fetchone()
            return dict(result) if result else None


def ensure_core_schema() -> None:
    """Ensure required core tables exist (goals, plan_steps, plans, plan_items)."""
    ddl_statements = [
        # Goals table (unchanged)
        """
        CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            priority INTEGER DEFAULT 3,
            category TEXT DEFAULT '',
            plan TEXT DEFAULT '',
            checklist JSONB DEFAULT '[]'::jsonb,
            last_conversation_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);",
        "CREATE INDEX IF NOT EXISTS idx_goals_created_at ON goals(created_at DESC);",

        # Existing goal plan steps table (legacy multi-step goals)
        """
        CREATE TABLE IF NOT EXISTS plan_steps (
            id SERIAL PRIMARY KEY,
            goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
            step_index INTEGER NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            due_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(goal_id, step_index)
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_id ON plan_steps(goal_id);",
        "CREATE INDEX IF NOT EXISTS idx_plan_steps_status ON plan_steps(status);",
        "CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_step ON plan_steps(goal_id, step_index);",

        # Daily plans header
        """
        CREATE TABLE IF NOT EXISTS plans (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_date DATE NOT NULL,
            generation_context JSONB DEFAULT '{}'::jsonb,
            behavior_snapshot JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, plan_date)
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_plans_plan_date ON plans(plan_date);",
        "CREATE INDEX IF NOT EXISTS idx_plans_user_date ON plans(user_id, plan_date);",

        # Daily plan items
        """
        CREATE TABLE IF NOT EXISTS plan_items (
            id SERIAL PRIMARY KEY,
            plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
            item_id TEXT NOT NULL,
            type TEXT NOT NULL,
            section TEXT,
            status TEXT DEFAULT 'planned',
            reschedule_to DATE,
            skip_reason TEXT,
            priority INTEGER,
            effort TEXT,
            energy TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(plan_id, item_id)
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON plan_items(plan_id);",
        "CREATE INDEX IF NOT EXISTS idx_plan_items_status ON plan_items(status);",
        "CREATE INDEX IF NOT EXISTS idx_plan_items_type ON plan_items(type);",

        # Insights table
        """
        CREATE TABLE IF NOT EXISTS insights (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            status TEXT NOT NULL DEFAULT 'pending',
            type TEXT NOT NULL,
            source_mode TEXT,
            summary TEXT NOT NULL,
            payload JSONB DEFAULT '{}'::jsonb
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_insights_status ON insights(status);",
        "CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type);",
        "CREATE INDEX IF NOT EXISTS idx_insights_created_at ON insights(created_at DESC);",
        "ALTER TABLE insights ADD COLUMN IF NOT EXISTS user_id TEXT NOT NULL DEFAULT '1';",
        "ALTER TABLE insights ALTER COLUMN user_id DROP DEFAULT;",
        "ALTER TABLE insights ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at::timestamptz;",
        "ALTER TABLE insights ALTER COLUMN created_at SET DEFAULT NOW();",

        # Goal task history (applied insights)
        """
        CREATE TABLE IF NOT EXISTS goal_task_history (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_date DATE NOT NULL,
            item_id TEXT NOT NULL,
            label TEXT NOT NULL,
            status TEXT DEFAULT 'planned',
            effort TEXT,
            section_hint TEXT,
            source_insight_id INTEGER,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id, plan_date, item_id)
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_goal_task_history_user_date ON goal_task_history(user_id, plan_date);",
        "CREATE INDEX IF NOT EXISTS idx_goal_task_history_insight ON goal_task_history(source_insight_id);",
        "CREATE INDEX IF NOT EXISTS idx_goal_task_history_status ON goal_task_history(status);",
    ]

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for ddl in ddl_statements:
                cursor.execute(ddl)
            conn.commit()


def close_pool() -> None:
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        print("[Database] Connection pool closed")
