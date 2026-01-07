# Othello Planning Engine - Quick Reference

## Database Setup

Before using the upgraded system, ensure your database schema is up to date:

1. Connect to your Neon PostgreSQL database
2. Run the updated `db/schema.sql` file to create the `plan_steps` table
3. The table will be created automatically with proper foreign keys and indexes

## API Endpoints

### Goal Management

#### List All Goals
```http
GET /api/goals
```

Response:
```json
{
  "goals": [
    {
      "id": 1,
      "text": "Learn Python",
      "status": "active",
      "priority": "high",
      ...
    }
  ]
}
```

#### Get Goal with Plan
```http
GET /api/goals/{goal_id}
```

Response:
```json
{
  "goal": {
    "id": 1,
    "text": "Learn Python",
    "status": "active",
    "plan_steps": [
      {
        "id": 1,
        "step_index": 1,
        "description": "Complete beginner tutorial",
        "status": "done",
        "due_date": null
      },
      {
        "id": 2,
        "step_index": 2,
        "description": "Build a small project",
        "status": "in_progress",
        "due_date": "2025-12-15"
      }
    ]
  }
}
```

#### Get Active Goals with Next Actions
```http
GET /api/goals/active-with-next-actions
```

Response:
```json
{
  "goals": [
    {
      "goal_id": 1,
      "title": "Learn Python",
      "status": "active",
      "next_step": {
        "id": 2,
        "step_index": 2,
        "description": "Build a small project",
        "status": "in_progress"
      }
    }
  ]
}
```

### Planning

#### Trigger Planning for a Goal
```http
POST /api/goals/{goal_id}/plan
Content-Type: application/json

{
  "instruction": "Create a detailed step-by-step plan for achieving this goal"
}
```

Response:
```json
{
  "reply": "I've created a comprehensive plan...",
  "goal": {
    "id": 1,
    "text": "Learn Python",
    "plan_steps": [...]
  },
  "agent_status": {
    "planner_active": true,
    "had_goal_update_xml": true
  }
}
```

### Step Management

#### Update Step Status
```http
POST /api/goals/{goal_id}/steps/{step_id}/status
Content-Type: application/json

{
  "status": "done"
}
```

Valid statuses: `"pending"`, `"in_progress"`, `"done"`

Response:
```json
{
  "step": {
    "id": 2,
    "goal_id": 1,
    "step_index": 2,
    "description": "Build a small project",
    "status": "done",
    "updated_at": "2025-12-08T10:30:00Z"
  }
}
```

## Memory System

### Using Memory Manager in Code

```python
from core.memory_manager import MemoryManager

memory = MemoryManager()

# Add a memory entry
memory.append_memory({
    "type": "goal_update",
    "goal_id": 5,
    "content": "Created a 3-step plan to learn Python"
})

# Get recent memories
recent = memory.get_recent_memories(limit=10)

# Get goal-specific memories
goal_memories = memory.get_relevant_memories(goal_id=5, limit=5)
```

### Memory Entry Structure

```json
{
  "timestamp": "2025-12-08T10:30:00Z",
  "type": "goal_update",
  "goal_id": 5,
  "content": "Created a 3-step plan to learn Python",
  "plan_step_count": 3,
  "metadata": {
    "tags": "python,learning",
    "notes": "User is motivated"
  }
}
```

## XML Schema for LLM Responses

When the architect brain is in planning mode, it expects this XML structure:

```xml
<goal_update>
  <summary>A 2-3 sentence summary of this conversation update</summary>
  <status>active</status>
  <priority>high</priority>
  <category>learning</category>
  <plan_steps>
    <step index="1" status="pending">First actionable step</step>
    <step index="2" status="pending" due_date="2025-12-15">Second step with deadline</step>
    <step index="3" status="pending">Third step</step>
  </plan_steps>
  <metadata>
    <tags>python,learning,project-based</tags>
    <notes>User is motivated and ready to start</notes>
    <next_action>Choose a project idea</next_action>
  </metadata>
</goal_update>
```

### XML Parsing Rules

- The parser looks for `<goal_update>` and `</goal_update>` tags
- If either tag is missing, parsing returns `None` (with logged warning)
- Each `<step>` must have an `index` attribute
- Optional attributes: `status`, `due_date`
- Step description is the text content of the `<step>` element

## Code Integration

### In Architect Brain

The architect brain automatically:
1. Extracts XML from LLM response
2. Parses plan_steps
3. Saves steps to database
4. Updates goal metadata
5. Writes memory entry
6. Strips XML from user-facing response

### In Input Router

For goal-related inputs:
```python
context = {'goal_id': 5}
result = router.route_input(user_input, context=context)

# result includes:
# - input: cleaned input text
# - tags: detected tags
# - routing_target: where to route
# - memories: relevant memory entries
```

## Database Queries

### Get Plan Steps for a Goal
```python
from db import goals_repository

steps = goals_repository.get_plan_steps_for_goal(goal_id=1)
# Returns list of step dicts ordered by step_index
```

### Create Plan Steps
```python
from db.db_goal_manager import DbGoalManager

goal_mgr = DbGoalManager()
steps = [
    {"step_index": 1, "description": "First step", "status": "pending"},
    {"step_index": 2, "description": "Second step", "status": "pending", "due_date": "2025-12-15"}
]
saved_steps = goal_mgr.save_goal_plan(goal_id=1, plan_steps=steps)
```

### Update Step Status
```python
goal_mgr.update_plan_step_status(
    goal_id=1,
    step_id=2,
    status="done"
)
```

### Get Next Action
```python
next_step = goal_mgr.get_next_action_for_goal(goal_id=1)
# Returns next incomplete step or None
```

## Error Handling

All components handle errors gracefully:

- **XML extraction fails**: Returns None, logs warning, continues without DB update
- **Memory write fails**: Logs error, doesn't crash main flow
- **Step update for wrong goal**: Returns None, logs error
- **Missing goal**: Returns 404 with error message

## Logging

All operations log at appropriate levels:

- `INFO`: Successful operations, major steps
- `DEBUG`: Detailed data, XML content
- `WARNING`: Missing XML, failed updates
- `ERROR`: Exceptions, critical failures

Check logs for:
- `"ARCHITECT: XML detected"` - XML found and parsing started
- `"Saved N plan steps"` - Steps successfully persisted
- `"Saved memory entry"` - Memory write succeeded
- `"No <goal_update> XML found"` - Missing XML (expected in casual chat)

## Best Practices

1. **Always check for active goals** before entering planning mode
2. **Use the planning endpoint** for structured goal decomposition
3. **Monitor XML generation** in logs to debug LLM responses
4. **Keep step descriptions actionable** and specific
5. **Use due_dates** for time-sensitive steps
6. **Check next actions** to guide user workflow
7. **Review memory entries** for context in conversations

## Troubleshooting

### LLM Not Generating XML
- Check if goal context is present in architect brain call
- Review system prompt in `utils/prompts.py`
- Look for "planning mode" indicators in logs

### Plan Steps Not Saving
- Check database connection (`/api/health/db`)
- Verify XML parsing succeeded (check logs)
- Ensure goal exists before saving plan

### Memory Not Loading
- Verify `agentic_memory.json` exists and is valid JSON
- Check file permissions
- Review memory manager logs

### Step Status Not Updating
- Ensure step belongs to the goal
- Check valid status values
- Verify database connectivity
