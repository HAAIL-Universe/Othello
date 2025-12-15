# Othello Database Module

This module provides PostgreSQL database integration for the Othello goal architect application.

## Files

- **`database.py`**: Core database helper with connection pooling and query utilities
- **`goals_repository.py`**: Repository functions for CRUD operations on goals
- **`db_goal_manager.py`**: Database-backed wrapper that mimics the file-based GoalManager interface
- **`schema.sql`**: Database schema definition for the goals table
- **`__init__.py`**: Module exports

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This will install `psycopg2-binary` for PostgreSQL connectivity.

2. **Configure database URL**:
   Add your Neon PostgreSQL connection string to `.env`:
   ```
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require
   ```

3. **Create the database schema**:
   The `goals` table must exist in your Neon database. Run the SQL from `schema.sql` or use a migration tool.

## Usage in Flask Routes

The `api.py` file has been updated to use the database-backed `DbGoalManager` instead of the file-based `GoalManager`:

```python
from db.database import init_pool
from db.db_goal_manager import DbGoalManager

# Initialize database connection pool at startup
init_pool()

# Replace file-based GoalManager with database version
architect_agent.goal_mgr = DbGoalManager()
```

## Database Schema

The `goals` table contains:

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `user_id` | INTEGER | User who owns this goal |
| `title` | TEXT | Goal title/description |
| `description` | TEXT | Extended description |
| `status` | TEXT | Status: 'active', 'completed', 'paused', etc. |
| `priority` | TEXT | Priority: 'low', 'medium', 'high' |
| `category` | TEXT | Category: 'work', 'personal', 'health', etc. |
| `plan` | TEXT | Current plan/strategy |
| `checklist` | JSONB | Array of checklist items |
| `last_conversation_summary` | TEXT | Summary of recent conversation |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

## Repository Functions

### `list_goals(user_id)`
Retrieve all goals for a specific user.

### `get_goal(goal_id, user_id)`
Retrieve a single goal by ID.

### `create_goal(data, user_id)`
Create a new goal. The `data` dict can contain:
- `title` or `text`: Goal title (required)
- `description`: Extended description
- `status`: Goal status (default: 'active')
- `priority`: Priority level (default: 'medium')
- `category`: Goal category
- `plan`: Current plan
- `checklist`: List of checklist items

### `update_goal_meta(goal_id, fields_to_change)`
Update metadata fields (title, description, status, priority, category).

### `update_goal_from_conversation(goal_id, new_plan, new_checklist, new_summary)`
Update fields derived from conversation analysis (plan, checklist, summary).

### `delete_goal(goal_id, user_id)`
Delete a goal.

## Backward Compatibility

The `DbGoalManager` class maintains the same interface as the original file-based `GoalManager`:

- Goals are automatically mapped between database format and legacy format
- Conversation logs still use JSONL files in `data/goal_logs/` for now
- All existing Flask route code continues to work without changes

## Future Enhancements

- Move conversation logs from JSONL files to a `goal_conversations` database table
- Add multi-user support with proper authentication
- Implement database migrations
- Add indexes for better query performance
- Add full-text search on goal titles and descriptions
