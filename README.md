
# Othello — Personal Goal Architect

Othello is an AI-powered personal goal architect that helps you set, track, and achieve your goals through natural conversation.

## Status

Othello is under active development. Features, structure, and APIs may change as the project evolves.

**Always-on instance:** Othello runs on a paid Render instance—no cold starts or waking delays. The UI includes robust reconnect handling if the API is temporarily unavailable.

## Features

- 🎯 **Conversational Goal Setting**: Tell Othello your goals naturally through chat
- 📊 **Goal Tracking**: Track progress, deadlines, and plans for multiple goals
- 📆 **Day Planner with Routines**: Generate a realistic Today Plan blending routines and a handful of priority goal tasks
- 💾 **PostgreSQL Storage**: Persistent goal storage using Neon database
- 🤖 **AI-Powered Insights**: Uses OpenAI models to help organize and refine your goals
- 📱 **Mobile-First UI**: Clean, responsive interface optimized for mobile devices

## Architecture

- **Backend**: Flask API with PostgreSQL (Neon) database
- **Frontend**: Single-page HTML/CSS/JS application
- **AI**: OpenAI GPT models for conversation and goal analysis
- **Storage**: Goals in PostgreSQL, conversation logs in JSONL files

## Local Setup

Follow these steps to set up Othello on your local machine:

### 1. Prerequisites

- Python 3.9 or higher
- A Neon PostgreSQL account (free tier available at https://neon.tech)
- OpenAI API key

### 2. Create Neon Database

1. Go to https://neon.tech and create a free account
2. Create a new project (e.g., "Othello")
3. In the Neon dashboard, open the **SQL Editor**
4. Copy the contents of `db/schema.sql` and paste into the SQL Editor
5. Click **Run** to create the `goals` table
6. Copy your connection string (it looks like `postgresql://user:password@host/database?sslmode=require`)

### 3. Clone and Configure

```bash
# Clone or download this project
cd Othello

# Create a .env file with your credentials
# Copy .env.example if it exists, or create new .env file
```

Add the following to your `.env` file:

```env
# OpenAI API Key (required for AI features)
OPENAI_API_KEY=sk-proj-your-key-here

# Neon Database URL (required for goal persistence)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

Never commit `.env`; use Render environment variables for production secrets.

### 4. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run the Application

```bash
# Start the Flask server
python api.py
```

You should see output like:
```
[API] ✓ Database connection pool initialized successfully
[API] ✓ Connected to Neon PostgreSQL database
Which model would you like FELLO to use this session?
1: gpt-3.5-turbo
2: gpt-4
3: gpt-4-turbo
4: gpt-4o
Enter 1-4 [default=4]: 
```

Select your preferred model (press Enter for default GPT-4o).

### 6. Test the Setup

Once the server is running, test the following endpoints:

**1. Test Database Connection:**
```bash
curl http://127.0.0.1:8000/api/health/db
```
Expected response:
```json
{
  "status": "ok",
  "message": "Database connection healthy",
  "database": "PostgreSQL (Neon)"
}
```

**2. Test Goals API:**
```bash
curl http://127.0.0.1:8000/api/goals
```
Expected response:
```json
{
  "goals": []
}
```

**3. Open the UI:**
Open your browser and go to: http://127.0.0.1:8000/

You should see the Othello interface. Try chatting to set your first goal!

## How to Run and Test Locally (Windows)

### 1. Start the backend

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_local.ps1
```

- This will activate the virtual environment (if present), set the default port (5000), and start the Flask server on http://127.0.0.1:5000/.
- The health endpoint will be available at http://127.0.0.1:5000/api/health/db

### 2. Open the UI

- Visit: [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser (do NOT use file://).

### 3. Test the health endpoint

```powershell
curl.exe -i http://127.0.0.1:5000/api/health/db
```
Expected response:
```json
{
  "status": "ok",
  "message": "Database connection healthy",
  "database": "PostgreSQL (Neon)"
}
```


### 4. Connection/Retry UX Verification Checklist

1. Stop the backend if running, then start it using the command above.
2. Open the UI in your browser. The app should attempt to connect immediately—no "waking server" overlay.
3. If the backend is unreachable, a "Connecting to server…" banner with a Retry button will appear. The app will retry automatically with backoff.
4. Once the backend is available, the banner disappears and the app loads.
5. Confirm the health endpoint returns JSON as above at http://127.0.0.1:5000/api/health/db

## Render Deploy Sanity

- Othello runs as Flask WSGI (`app = Flask(__name__)` in `api.py`).
- Start command (Render): `gunicorn api:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120`
- Ensure `Flask>=2.3` is present in `requirements.txt`.

---

## Project Structure

```
Othello/
├── api.py                      # Flask application entry point
├── othello_ui.html            # Frontend single-page application
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── core/                      # Core application logic
│   ├── architect_brain.py    # Main AI agent orchestration
│   ├── llm_wrapper.py        # OpenAI API wrapper
│   └── ...
├── db/                        # Database layer
│   ├── database.py           # PostgreSQL connection pool & helpers
│   ├── goals_repository.py   # Goal CRUD operations
│   ├── db_goal_manager.py    # Database-backed GoalManager
│   ├── schema.sql            # Database schema definition
│   └── README.md             # Database documentation
├── modules/                   # Application modules
│   └── goal_manager.py       # Original file-based GoalManager
├── data/                      # Local data storage
│   ├── goals.json            # (Legacy) File-based goal storage
│   └── goal_logs/            # JSONL conversation logs
└── utils/                     # Utility functions
```

## API Endpoints

### Core Endpoints

- `GET /` - Serve the Othello UI
- `POST /api/message` - Send a message to Othello
- `GET /api/goals` - List all goals
- `GET /api/today-plan` - Fetch the blended Today Plan (routines + selected goal tasks)
- `POST /api/plan/update` - Mark a plan item complete/skipped/rescheduled
- `POST /api/plan/rebuild` - Force regeneration of Today Plan with new context

### Health Check Endpoints

- `GET /api/health/db` - Check database connectivity

## Development

### Database Schema

Goals are stored in PostgreSQL with the following schema:

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

### Running Tests

```bash
# Run unit tests
python run_tests.py
```

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DATABASE_URL` - PostgreSQL connection string (required)

## Troubleshooting

### Database Connection Issues

If you see `"status": "error"` when checking `/api/health/db`:

1. Verify `DATABASE_URL` is set correctly in `.env`
2. Check that your Neon database is running (not paused)
3. Ensure the `goals` table exists (run `db/schema.sql`)
4. Test the connection string directly using `psql` or a database client

### Missing Dependencies

If you get import errors:

```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

If port 8000 is already in use, modify `api.py`:

```python
if __name__ == "__main__":
    app.run(port=8001, debug=False)  # Change port here
```

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## License

MIT License - Feel free to use and modify for your own goals!

---

**Built with ❤️ to help you achieve your goals**

## Render Deploy Checklist

- **Build command:** (leave blank or use default)
- **Start command:**
  ```
  python -m gunicorn api:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120
  ```
- **Required env vars:**
  - `OPENAI_API_KEY` (for AI features)
  - `DATABASE_URL` (for goal persistence)
- **Notes:**
  - `gunicorn` is now installed via `requirements.txt`.
  - The start command uses `python -m gunicorn` to avoid PATH issues on Render.
  - The app is served at `/` and health at `/api/health/db`.

To redeploy:
1. Push to the main branch on GitHub.
2. Trigger a manual deploy in the Render dashboard if needed.
3. Watch logs for `Booting worker with pid` and `Listening at: http://0.0.0.0:$PORT`.
4. Visit your Render URL and confirm the app loads and the connection overlay only appears if the backend is unavailable.

---
