-- ============================================================================
-- OTHELLO DATABASE SCHEMA (FULL REPLACEMENT)
-- ============================================================================
--
-- Name: Othello (Goals + Planning + Reflections + Memory + Suggestions)
-- Engine: Neon PostgreSQL (Postgres)
-- Schema Version: 1.1
--
-- This file is intended as a FULL replacement schema for a fresh database.
-- If you already have a live DB with data, apply only the delta portions
-- (CREATE TABLE IF NOT EXISTS...) or use migrations instead.
--
-- Principles:
-- - DB is authoritative truth (no JSON/JSONL truth in runtime)
-- - Append-only event tables for history/audit where appropriate
-- - All timestamps stored as TIMESTAMPTZ (UTC)
--
-- Usage:
-- 1) In Neon SQL editor, paste and Run.
-- 2) Put DATABASE_URL in .env
--
-- ============================================================================

-- ----------------------------------------------------------------------------
-- USERS (minimal, multi-user-capable even if single-user today)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    timezone TEXT NOT NULL DEFAULT 'Europe/London',
    night_prompt_time TIME DEFAULT '20:00',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_timezone ON users(timezone);

-- ----------------------------------------------------------------------------
-- GOALS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'active',  -- 'active', 'completed', 'paused', 'archived'
    priority INTEGER DEFAULT 3,     -- 1..5 (or your own scale)
    category TEXT DEFAULT '',
    plan TEXT DEFAULT '',
    checklist JSONB DEFAULT '[]'::jsonb, -- [{"task": "...", "done": false}, ...]
    last_conversation_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_goals_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_goals_created_at ON goals(created_at DESC);

-- ----------------------------------------------------------------------------
-- PLAN STEPS (canonical goal step list)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plan_steps (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,      -- execution order
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',    -- 'pending', 'in_progress', 'done', 'dropped'
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(goal_id, step_index)
);

CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_id ON plan_steps(goal_id);
CREATE INDEX IF NOT EXISTS idx_plan_steps_status ON plan_steps(status);
CREATE INDEX IF NOT EXISTS idx_plan_steps_goal_step ON plan_steps(goal_id, step_index);

-- ----------------------------------------------------------------------------
-- GOAL EVENTS (replaces file-based goal_logs/*.jsonl as truth)
-- Append-only ledger: created/updated/step_done/completed/notes/etc.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goal_events (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES plan_steps(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,     -- 'goal_created'|'step_added'|'step_done'|'goal_completed'|'note'...
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_goal_events_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_goal_events_goal_time ON goal_events(goal_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_goal_events_user_time ON goal_events(user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_goal_events_type ON goal_events(event_type);

-- ----------------------------------------------------------------------------
-- SUGGESTIONS (replaces pending_goals.json; confirm-gated inference)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suggestions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    kind TEXT NOT NULL,                  -- 'goal'|'step'|'insight'|'constraint'|'plan_item'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending'|'accepted'|'rejected'
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    decided_reason TEXT,
    CONSTRAINT fk_suggestions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_suggestions_user_status ON suggestions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_suggestions_user_kind ON suggestions(user_id, kind);

-- ----------------------------------------------------------------------------
-- DAILY PLANS (present in your schema; not required for Phase 1 but supported)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan_date DATE NOT NULL,
    generation_context JSONB DEFAULT '{}'::jsonb,
    behavior_snapshot JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, plan_date),
    CONSTRAINT fk_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

ALTER TABLE plans ADD COLUMN IF NOT EXISTS plan_id INTEGER GENERATED ALWAYS AS (id) STORED;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS plan_date_local DATE;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC';
ALTER TABLE plans ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft';
ALTER TABLE plans ADD COLUMN IF NOT EXISTS created_at_utc TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE plans ADD COLUMN IF NOT EXISTS confirmed_at_utc TIMESTAMPTZ;
UPDATE plans SET plan_date_local = plan_date WHERE plan_date_local IS NULL;
UPDATE plans SET created_at_utc = created_at WHERE created_at_utc IS NULL;

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
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(plan_id, item_id)
);

ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS user_id TEXT;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS source_kind TEXT;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS source_id TEXT;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS order_index INTEGER;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS created_at_utc TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE plan_items ADD COLUMN IF NOT EXISTS updated_at_utc TIMESTAMPTZ DEFAULT NOW();
UPDATE plan_items SET created_at_utc = created_at WHERE created_at_utc IS NULL;
UPDATE plan_items SET updated_at_utc = updated_at WHERE updated_at_utc IS NULL;
UPDATE plan_items SET user_id = plans.user_id
FROM plans
WHERE plan_items.plan_id = plans.id AND plan_items.user_id IS NULL;

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
    UNIQUE(user_id, plan_date, item_id),
    CONSTRAINT fk_goal_task_history_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_goal_task_history_user_date ON goal_task_history(user_id, plan_date);
CREATE INDEX IF NOT EXISTS idx_goal_task_history_insight ON goal_task_history(source_insight_id);
CREATE INDEX IF NOT EXISTS idx_goal_task_history_status ON goal_task_history(status);

-- ----------------------------------------------------------------------------
-- REFLECTION ENTRIES (replaces self_reflection_log.json)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reflection_entries (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_reflections_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reflections_user_time ON reflection_entries(user_id, created_at DESC);

-- ----------------------------------------------------------------------------
-- MEMORY ENTRIES + PROFILE SNAPSHOT (replaces agentic_memory.json truth)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS memory_entries (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    kind TEXT NOT NULL,          -- 'note'|'preference'|'insight'|'constraint' etc.
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_memory_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_memory_user_time ON memory_entries(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_user_kind ON memory_entries(user_id, kind);

CREATE TABLE IF NOT EXISTS profile_snapshots (
    user_id TEXT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- AUDIT EVENTS (optional, but recommended; replaces privacy/system file logs as truth)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_events (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    area TEXT NOT NULL,          -- 'privacy'|'system'|'security'|'consent' etc.
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_area_time ON audit_events(area, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON audit_events(user_id, occurred_at DESC);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- SELECT COUNT(*) FROM goals;
-- SELECT COUNT(*) FROM plan_steps;
-- SELECT COUNT(*) FROM suggestions;
-- SELECT COUNT(*) FROM goal_events;
-- SELECT COUNT(*) FROM memory_entries;
-- SELECT COUNT(*) FROM reflection_entries;
-- ============================================================================
