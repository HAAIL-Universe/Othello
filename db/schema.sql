-- ============================================================================
-- Othello Goals Database Schema
-- ============================================================================
-- 
-- This file defines the database schema for the Othello personal goal 
-- architect application. It should be run manually in your Neon PostgreSQL
-- database when setting up a new environment.
--
-- HOW TO USE:
-- 1. Create a new Neon project at https://neon.tech
-- 2. Open the SQL Editor in your Neon dashboard
-- 3. Copy and paste this entire file into the SQL Editor
-- 4. Click "Run" to execute the schema creation
-- 5. Copy the connection string and add it to your .env file as DATABASE_URL
--
-- SCHEMA VERSION: 1.0
-- REQUIRED FOR: db/goals_repository.py, db/db_goal_manager.py
-- ============================================================================

-- Goals table stores all user goals with metadata and conversation-derived fields
CREATE TABLE IF NOT EXISTS goals (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'active',  -- e.g., 'active', 'completed', 'paused', 'archived'
    priority INTEGER DEFAULT 3,  -- Numeric priority: 1=low, 3=medium, 5=high (or custom values)
    category TEXT DEFAULT '',  -- e.g., 'work', 'personal', 'health', 'learning'
    plan TEXT DEFAULT '',  -- Current plan/strategy for achieving the goal
    checklist JSONB DEFAULT '[]'::jsonb,  -- Array of checklist items [{"task": "...", "done": false}, ...]
    last_conversation_summary TEXT,  -- Summary of recent conversation about this goal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_goals_created_at ON goals(created_at DESC);

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- After running this schema, verify it was created successfully:
-- SELECT COUNT(*) FROM goals;
-- 
-- This should return 0 if the table is empty (expected on first run).
-- ============================================================================

-- ============================================================================
-- Plan Steps table (multi-step goal planning)
-- ============================================================================
-- Stores individual steps/actions for each goal, enabling multi-step planning
-- and tracking progress through complex goals.
-- ============================================================================

CREATE TABLE IF NOT EXISTS plan_steps (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,  -- Order of execution in the plan (0-based or 1-based)
    description TEXT NOT NULL,  -- The actual step text/instruction
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'done'
    due_date TIMESTAMP,  -- Optional deadline for this step
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure each goal has unique step indices
    UNIQUE(goal_id, step_index)
);

-- Indexes for faster queries on plan steps
CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_id ON plan_steps(goal_id);
CREATE INDEX IF NOT EXISTS idx_plan_steps_status ON plan_steps(status);
CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_step ON plan_steps(goal_id, step_index);

-- ============================================================================
-- Daily Plans (plans + plan_items)
-- ============================================================================
-- Primary storage for Today Plans; plan headers are keyed by (user_id, plan_date)
-- and plan_items hold each routine/task/backlog entry with stable item_ids.
-- ============================================================================

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

CREATE INDEX IF NOT EXISTS idx_plans_plan_date ON plans(plan_date);
CREATE INDEX IF NOT EXISTS idx_plans_user_date ON plans(user_id, plan_date);

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

CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON plan_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_plan_items_status ON plan_items(status);
CREATE INDEX IF NOT EXISTS idx_plan_items_type ON plan_items(type);

-- Applied insights / goal task history (recallable across days)
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

CREATE INDEX IF NOT EXISTS idx_goal_task_history_user_date ON goal_task_history(user_id, plan_date);
CREATE INDEX IF NOT EXISTS idx_goal_task_history_insight ON goal_task_history(source_insight_id);
CREATE INDEX IF NOT EXISTS idx_goal_task_history_status ON goal_task_history(status);

-- ============================================================================
-- OPTIONAL: Conversation history table (future enhancement)
-- ============================================================================
-- Currently conversation logs are stored in JSONL files in data/goal_logs/
-- This table could replace the file-based approach in a future version:
--
-- CREATE TABLE IF NOT EXISTS goal_conversations (
--     id SERIAL PRIMARY KEY,
--     goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
--     role TEXT NOT NULL,  -- 'user', 'othello', 'system'
--     content TEXT NOT NULL,
--     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
--
-- CREATE INDEX IF NOT EXISTS idx_goal_conversations_goal_id ON goal_conversations(goal_id);
-- CREATE INDEX IF NOT EXISTS idx_goal_conversations_timestamp ON goal_conversations(timestamp DESC);
-- ============================================================================
