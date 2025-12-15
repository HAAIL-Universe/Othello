def get_runtime_config_snapshot():
    """
    Returns a dict with booleans for env presence, selected auth/secret/model/db modes, and build info.
    Never includes or logs secret values.
    """
    env = os.environ
    def present(key):
        return bool(env.get(key))

    # Auth mode
    if present("OTHELLO_PIN_HASH"):
        auth_mode = "pin_hash"
    elif present("OTHELLO_PASSWORD"):
        auth_mode = "plaintext_password"
    else:
        auth_mode = "none"

    # Secret key source
    if present("SECRET_KEY"):
        secret_key_source = "SECRET_KEY"
    elif present("OTHELLO_SECRET_KEY"):
        secret_key_source = "OTHELLO_SECRET_KEY"
    elif (os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID")):
        secret_key_source = "missing"
    else:
        secret_key_source = "default_dev"

    # Model
    model = env.get("OTHELLO_MODEL")
    if not model:
        # Try to read from .llm_model_cache if present (safe)
        try:
            with open(".llm_model_cache", "r") as f:
                model = f.read().strip()
        except Exception:
            model = None
    model_selected = model or "unknown"

    # DB
    db_mode = "configured" if present("DATABASE_URL") else "missing"

    # Build info
    build = env.get("RENDER_GIT_COMMIT") or "unknown"

    # Compose snapshot
    snapshot = {
        "env_present": {
            "DATABASE_URL_present": present("DATABASE_URL"),
            "OPENAI_API_KEY_present": present("OPENAI_API_KEY"),
            "OTHELLO_PIN_HASH_present": present("OTHELLO_PIN_HASH"),
            "OTHELLO_PASSWORD_present": present("OTHELLO_PASSWORD"),
            "SECRET_KEY_present": present("SECRET_KEY"),
            "OTHELLO_SECRET_KEY_present": present("OTHELLO_SECRET_KEY"),
            "OTHELLO_MODEL_present": present("OTHELLO_MODEL"),
            "OTHELLO_LOGIN_KEY_present": present("OTHELLO_LOGIN_KEY"),
        },
        "auth_mode_selected": auth_mode,
        "secret_key_source": secret_key_source,
        "model_selected": model_selected,
        "db_mode": db_mode,
        "build": build,
    }
    return snapshot

# Minimal auth endpoints
def _debug_config_allowed():
    # Only allow if authed session AND DEBUG_CONFIG=1
    if not session.get("authed"):
        return False
    return os.environ.get("DEBUG_CONFIG") == "1"


# --- Debug config endpoint ---
@app.route("/api/debug/config", methods=["GET"])
def debug_config():
    if not _debug_config_allowed():
        return ("Not found", 404)
    return jsonify(get_runtime_config_snapshot())

import logging
import os
import re
from datetime import date, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
from typing import Any, Dict, Optional


# NOTE: Keep import-time work minimal! Do not import LLM/agent modules or connect to DB at module scope unless required for health endpoints.
from dotenv import load_dotenv
load_dotenv()


def serialize_insight(insight: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a repository row into a JSON-safe dict for the UI."""
    if not insight:
        return {}

    created_at = insight.get("created_at")
    created_iso = None
    if created_at is not None:
        created_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)

    insight_type = insight.get("insight_type") or insight.get("type")
    content = insight.get("content") or insight.get("summary")

    return {
        "id": insight.get("id"),
        "user_id": insight.get("user_id"),
        "created_at": created_iso,
        "status": insight.get("status"),
        "type": insight_type,
        "insight_type": insight_type,
        "summary": content,
        "content": content,
        "payload": insight.get("payload"),
    }


def serialize_goal_task_history(row: Dict[str, Any]) -> Dict[str, Any]:
    created_at = row.get("created_at")
    updated_at = row.get("updated_at")
    plan_date = row.get("plan_date")
    return {
        "id": row.get("id"),
        "user_id": row.get("user_id"),
        "plan_date": plan_date.isoformat() if hasattr(plan_date, "isoformat") else plan_date,
        "item_id": row.get("item_id"),
        "label": row.get("label"),
        "status": row.get("status"),
        "effort": row.get("effort"),
        "section_hint": row.get("section_hint"),
        "source_insight_id": row.get("source_insight_id"),
        "metadata": row.get("metadata"),
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
        "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
    }

# Configure logging to show DEBUG messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize database connection pool
db_initialized = False
try:
    init_pool()
    ensure_core_schema()
    db_initialized = True
    print("[API] ✓ Database connection pool initialized successfully")
    print("[API] ✓ Connected to Neon PostgreSQL database")
    try:
        _insight_check = fetch_one("SELECT COUNT(*) AS count FROM insights;")
        logging.getLogger("API").info(
            "[API] Insights table check: count=%s",
            (_insight_check or {}).get("count"),
        )
    except Exception as log_exc:
        logging.getLogger("API").warning(
            "[API] Insights table check failed: %s", log_exc, exc_info=True
        )
except Exception as e:
    print(f"[API] ✗ Warning: Failed to initialize database: {e}")
    print("[API] ✗ The app will run but goal persistence may not work correctly")
    print("[API] ✗ Check that DATABASE_URL is set in .env and the database is accessible")


def is_goal_list_request(text: str) -> bool:
    """
    Heuristic: treat certain phrases as 'list my goals' instead of a new goal.
    Only triggers on explicit requests to view/list goals.
    """
    t = text.lower()
    
    # Explicit phrases that clearly mean "show me my goals"
    goal_list_phrases = [
        "what are my goals",
        "what's my goals",
        "what are the goals",
        "show my goals",
        "show me my goals",
        "list my goals",
        "list the goals",
        "list goals",
        "show goals",
        "view goals",
        "view my goals",
        "see my goals",
        "what goals do i have",
        "what goals have i",
    ]
    
    # Check if any explicit phrase is present
    return any(phrase in t for phrase in goal_list_phrases)


def format_goal_list(goals) -> str:
    """
    Turn the GoalManager list into a human-friendly reply string.
    """
    if not goals:
        return (
            "You don't have any goals stored yet. "
            "You can set one by saying something like: "
            "'My goal today is improvement.'"
        )

    lines = ["Here are your current goals:"]
    for g in goals:
        goal_id = g.get("id", "?")
        text = g.get("text", "").strip() or "(empty goal text)"
        deadline = g.get("deadline")
        if deadline:
            lines.append(f"- Goal #{goal_id}: {text} (deadline: {deadline})")
        else:
            lines.append(f"- Goal #{goal_id}: {text}")

    return "\n".join(lines)


def parse_goal_selection_request(text: str) -> Optional[int]:

    # === Model selector and agent/LLM/DB lazy loader ===
    import os
    SELECTED_MODEL = os.getenv("FELLO_MODEL", "gpt-4o-mini")

    # Canonical lazy loader for agent/LLM/DB modules and model selection
    def get_agent_components():
        # Import only when needed (not for health endpoints)
        from core.architect_brain import Architect
        from core.llm_wrapper import AsyncLLMWrapper
        from core.input_router import InputRouter
        from core.othello_engine import OthelloEngine
        from utils.postprocessor import postprocess_and_save
        from db.database import ensure_core_schema, fetch_one
        from db import plan_repository
        from db import goal_task_history_repository
        from db.db_goal_manager import DbGoalManager
        from core.memory_manager import MemoryManager
        from db import insights_repository
        from insights_service import extract_insights_from_exchange
        # Model selection: try pick_model if available, else fallback
        try:
            from core.llm_wrapper import pick_model
            model = pick_model(default=os.getenv("FELLO_MODEL", "gpt-4o-mini"))
        except Exception:
            model = os.getenv("FELLO_MODEL", "gpt-4o-mini")
        openai_model = AsyncLLMWrapper(model=model)
        architect_agent = Architect(model=openai_model)
        architect_agent.goal_mgr = DbGoalManager()
        architect_agent.memory_mgr = MemoryManager()
        othello_engine = OthelloEngine(goal_manager=architect_agent.goal_mgr, memory_manager=architect_agent.memory_mgr)
        DEFAULT_USER_ID = DbGoalManager.DEFAULT_USER_ID
        return locals()
    """
    Try to parse EXPLICIT goal selection commands like:
    - "goal 1"
    - "goal #2"
    - "select goal 3"
    - "switch to goal 1"
    
    Does NOT match casual mentions of "goal" with numbers nearby.
    """
    t = text.lower().strip()
    
    # Strict patterns that require explicit goal selection intent
    goal_select_patterns = [
        r'^goal\s+#?(\d+)$',                    # "goal 1" or "goal #1"
        r'^select\s+goal\s+#?(\d+)$',           # "select goal 1"
        r'^switch\s+to\s+goal\s+#?(\d+)$',      # "switch to goal 1"
        r'^focus\s+on\s+goal\s+#?(\d+)$',       # "focus on goal 1"
        r'^work\s+on\s+goal\s+#?(\d+)$',        # "work on goal 1"
        r'^talk\s+about\s+goal\s+#?(\d+)$',     # "talk about goal 1"
        r'^go\s+to\s+goal\s+#?(\d+)$',          # "go to goal 1"
        r'^use\s+goal\s+#?(\d+)$',              # "use goal 1"
    ]
    
    for pattern in goal_select_patterns:
        m = re.match(pattern, t)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
    
    return None





app = Flask(__name__)
CORS(app)  # Allow requests from frontend
# Harden SECRET_KEY handling for production
secret = os.getenv("SECRET_KEY")
if not secret:
    if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
        logging.warning("[API] WARNING: SECRET_KEY is not set in environment! Using insecure default. Set SECRET_KEY in Render environment variables.")
    secret = "dev-secret-key"
app.config["SECRET_KEY"] = secret


# Minimal auth config (compat bridge)
from flask import session, abort
from functools import wraps
from passlib.hash import bcrypt

OTHELLO_PASSWORD = os.environ.get("OTHELLO_PASSWORD")
OTHELLO_PIN_HASH = os.environ.get("OTHELLO_PIN_HASH")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow unauthenticated for health, login, me, and root
        if request.path in ["/api/health", "/api/auth/login", "/api/auth/me", "/"]:
            return f(*args, **kwargs)
        if not session.get("authed"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

# Fast, LLM-free health endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Minimal auth endpoints
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    password = data.get("password")
    # Auth precedence: OTHELLO_PIN_HASH > OTHELLO_PASSWORD > misconfig
    auth_mode = get_runtime_config_snapshot()["auth_mode_selected"]
    if OTHELLO_PIN_HASH:
        if not password:
            return jsonify({"error": "missing_password", "detail": "Password required", "auth_mode": auth_mode}), 400
        try:
            if bcrypt.verify(password, OTHELLO_PIN_HASH):
                session["authed"] = True
                return jsonify({"ok": True})
            else:
                return jsonify({"error": "Invalid password", "auth_mode": auth_mode}), 401
        except Exception as e:
            logging.getLogger("API").error(f"bcrypt verification error: {e}")
            return jsonify({"error": "server_error", "detail": "bcrypt verification failed", "auth_mode": auth_mode}), 500
    elif OTHELLO_PASSWORD:
        logging.getLogger("API").warning("plaintext password mode enabled; set OTHELLO_PIN_HASH to harden")
        if not password:
            return jsonify({"error": "missing_password", "detail": "Password required", "auth_mode": auth_mode}), 400
        if password == OTHELLO_PASSWORD:
            session["authed"] = True
            return jsonify({"ok": True})
        return jsonify({"error": "Invalid password", "auth_mode": auth_mode}), 401
    else:
        return (
            jsonify({
                "error": "server_misconfigured",
                "detail": "OTHELLO_PASSWORD not set",
                "auth_mode": auth_mode
            }),
            503
        )

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    return jsonify({"authenticated": bool(session.get("authed"))})


def log_pending_insights_on_startup():
    logger = logging.getLogger("API.Insights")
    try:
        counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
        logger.info("API: startup pending insights summary: %s", counts)
    except Exception as exc:
        logger.warning("API: insights summary unavailable at startup: %s", exc)


# Run once at import time to avoid Flask 3.x before_first_request removal
try:
    log_pending_insights_on_startup()
except Exception:
    logging.getLogger("API.Insights").warning("API: startup insights check failed during import", exc_info=True)


def _process_insights_pipeline(*, user_text: str, assistant_text: str, user_id: str):
    """Extract and persist insights, shielding chat flow from failures."""
    logger = logging.getLogger("API.Insights")
    meta: Dict[str, Any] = {"created": 0, "pending_counts": {}}

    try:
        created = extract_insights_from_exchange(
            user_message=user_text,
            assistant_message=assistant_text,
            user_id=user_id,
        )
        meta["created"] = len(created)
        logger.info("API: insight extraction persisted %s candidates", meta["created"])
    except Exception as exc:
        logger.warning("API: insight extraction failed: %s", exc, exc_info=True)
        return meta

    try:
        meta["pending_counts"] = insights_repository.count_pending_by_type(user_id)
    except Exception as exc:
        logger.warning("API: failed to fetch pending insight counts: %s", exc, exc_info=True)

    return meta


@app.route("/api/message", methods=["POST"])
def handle_message():
    """
    Main endpoint for user interaction:
    1. Optionally intercept 'list my goals' and answer from GoalManager.
    2. Optionally intercept 'talk about goal X' and set active_goal_id.
    3. Runs postprocessor to extract goals/traits/routines from input (analysis only).
    4. Builds goal context (if an active goal exists) and calls agent planner.
    5. Logs this exchange into the active goal's conversation log.
    6. Returns reply to frontend.
    """
    logger = logging.getLogger("API")
    data = request.get_json() or {}
    raw_user_input = data.get("message") or ""
    user_input = raw_user_input.strip()
    active_goal_id = data.get("active_goal_id")
    current_mode = (data.get("current_mode") or "companion").strip().lower()
    current_view = data.get("current_view")
    
    logger.info(f"API: Received message: {user_input[:100]}...")
    
    # Set active goal from client focus if provided
    if active_goal_id:
        try:
            architect_agent.goal_mgr.set_active_goal(active_goal_id)
            logger.info(f"API: Active goal set from client focus: #{active_goal_id}")
        except Exception as e:
            logger.warning(f"API: Failed to set active goal from client focus: {e}", exc_info=True)

    # --- Shortcut 1: user is asking for their goals; answer directly -----
    if is_goal_list_request(user_input):
        # Log which phrase triggered the goal list route
        t = user_input.lower()
        goal_list_phrases = [
            "what are my goals",
            "what's my goals",
            "what are the goals",
            "show my goals",
            "show me my goals",
            "list my goals",
            "list the goals",
            "list goals",
            "show goals",
            "view goals",
            "view my goals",
            "see my goals",
            "what goals do i have",
            "what goals have i",
        ]
        matched_phrase = next((p for p in goal_list_phrases if p in t), None)
        logger.info(f"API: Routing to goal list (shortcut branch) due to phrase: {matched_phrase!r}")
        
        goals = architect_agent.goal_mgr.list_goals()
        reply_text = format_goal_list(goals)
        logger.info(f"API: Returning goal list with {len(goals)} goals")
        return jsonify(
            {
                "reply": reply_text,
                "goals": goals,
                "meta": {
                    "source": "goal_manager",
                    "intent": "list_goals",
                },
            }
        )

    # --- Shortcut 2: user wants to focus on a specific goal -------------
    goal_id = parse_goal_selection_request(user_input)
    if goal_id is not None:
        logger.info(f"API: User explicitly selecting goal #{goal_id} via goal-selection command")
        goal = architect_agent.goal_mgr.get_goal(goal_id)
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found")
            reply_text = (
                f"I couldn't find a goal #{goal_id}. "
                "Ask me to list your goals first if you're not sure of the number."
            )
            return jsonify(
                {
                    "reply": reply_text,
                    "meta": {
                        "source": "goal_manager",
                        "intent": "select_goal_failed",
                        "requested_goal_id": goal_id,
                    },
                }
            )

        architect_agent.goal_mgr.set_active_goal(goal_id)
        ctx = architect_agent.goal_mgr.build_goal_context(goal_id, max_notes=5)
        logger.info(f"API: Set active goal to #{goal_id}: {goal['text'][:50]}...")
        reply_text = (
            f"Okay, we'll focus on Goal #{goal_id}: {goal['text']}.\n\n"
            "I'll attach our next messages to this goal. "
            "Tell me updates, questions, or ask me to help you plan steps."
        )

        return jsonify(
            {
                "reply": reply_text,
                "active_goal_id": goal_id,
                "goal_context": ctx,
                "meta": {
                    "source": "goal_manager",
                    "intent": "select_goal_success",
                    "selected_goal_id": goal_id,
                },
            }
        )
    # ---------------------------------------------------------------------

    # === Post-processing (analysis only – no persistence here) ===========
    summary = postprocess_and_save(user_input)
    print("[DEBUG] Postprocess summary:", summary)  # Comment/remove in prod

    # === Determine active goal with fallback logic =======================
    active_goal = architect_agent.goal_mgr.get_active_goal()
    
    # Fallback: if no active goal but exactly one goal exists, use it as default
    if active_goal is None:
        goals = architect_agent.goal_mgr.list_goals()
        if goals and len(goals) == 1:
            single_goal = goals[0]
            logger.info(
                f"API: No explicit active goal, but 1 goal exists (#{single_goal.get('id')}). "
                "Defaulting to this as active planning goal."
            )
            try:
                architect_agent.goal_mgr.set_active_goal(single_goal["id"])
                active_goal = single_goal
                logger.info(f"API: Successfully set active goal to #{single_goal.get('id')}")
            except Exception as e:
                logger.warning(f"API: Failed to persist active goal default: {e}")
                # Still use it for this request even if persistence failed
                active_goal = single_goal
    
    # === Build goal_context for Architect (if an active goal exists) =====
    goal_context = None
    if active_goal is not None:
        goal_context = architect_agent.goal_mgr.build_goal_context(
            active_goal["id"], max_notes=8
        )
        logger.info(f"API: Active goal #{active_goal['id']}: {active_goal.get('text', '')[:50]}...")
        logger.info(f"API: Built goal context ({len(goal_context) if goal_context else 0} chars)")
        logger.info(f"API: Routing message to Architect planning engine for goal_id={active_goal['id']}")
    else:
        logger.info("API: No active goal - casual chat mode")
    # ---------------------------------------------------------------------

    # === Route to Architect planning if active goal exists ===============
    if active_goal is not None:
        # Active goal detected - check if this is an explicit plan generation request
        router = InputRouter()
        is_plan_request = router.is_plan_request(user_input)
        
        if is_plan_request:
            # Explicit plan generation request - use XML-only planning mode
            logger.info(f"API: PLAN REQUEST detected for goal #{active_goal['id']}")
            logger.info(f"API: Routing to generate_goal_plan (XML-only mode)")
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                plan_result = loop.run_until_complete(
                    architect_agent.generate_goal_plan(
                        goal_id=active_goal['id'],
                        instruction=user_input
                    )
                )
                loop.close()
                
                if plan_result:
                    # Successfully generated plan - build natural language summary
                    step_count = len(plan_result.get('plan_steps', []))
                    next_action = plan_result.get('next_action', 'Begin with the first step')
                    priority = plan_result.get('priority', 'medium')
                    status = plan_result.get('status', 'active')
                    
                    agentic_reply = (
                        f"I've created a {step_count}-step plan for this goal.\n\n"
                        f"Status: {status}\n"
                        f"Priority: {priority}\n\n"
                        f"Your next action: {next_action}\n\n"
                        f"You can review all steps in the GOALS tab."
                    )
                    
                    agent_status = {
                        "planner_active": True,
                        "had_goal_update_xml": True,
                        "plan_generated": True,
                        "step_count": step_count
                    }
                    
                    logger.info(f"API: Plan generation successful - {step_count} steps created")
                    
                else:
                    # Plan generation failed
                    logger.error(f"API: Plan generation returned None for goal #{active_goal['id']}")
                    agentic_reply = (
                        "I had trouble generating a structured plan. "
                        "Let me try in conversational mode instead."
                    )
                    agent_status = {
                        "planner_active": False,
                        "had_goal_update_xml": False,
                        "plan_generated": False
                    }
                    
            except Exception as e:
                logger.error(f"API: generate_goal_plan failed: {e}", exc_info=True)
                agentic_reply = (
                    "I encountered an error while generating the plan. "
                    "Please try again or rephrase your request."
                )
                agent_status = {
                    "planner_active": False,
                    "had_goal_update_xml": False,
                    "plan_generated": False
                }
        
        else:
            # Normal conversational planning mode
            logger.info(f"API: Planning with active goal #{active_goal['id']}: {active_goal.get('text', '')[:80]}")
            
            loop = None
            try:
                logger.debug(f"API: Calling architect_agent.plan_and_execute with context={goal_context is not None}")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                agentic_reply, agent_status = loop.run_until_complete(
                    architect_agent.plan_and_execute(
                        user_input,
                        context={
                            "goal_context": goal_context,
                            "active_goal": active_goal,
                        } if goal_context else None,
                    )
                )
                
                logger.info(f"API: Architect planning completed successfully for goal_id={active_goal['id']}")
                logger.debug(f"API: Agent status: {agent_status}")
                logger.debug(f"API: Reply preview: {agentic_reply[:150]}...")
                
                # Ensure planner_active is True since we routed through Architect
                if agent_status.get("planner_active") is None:
                    agent_status["planner_active"] = True
            except Exception as e:
                logger.error(f"API: Architect planning failed with exception for goal_id={active_goal['id']}: {e}", exc_info=True)
                agentic_reply = (
                    "I ran into an internal error while updating your goal plan. "
                    "Please try again or rephrase your message."
                )
                agent_status = {"planner_active": False, "had_goal_update_xml": False}
            finally:
                if loop is not None:
                    try:
                        loop.close()
                    except Exception:
                        logger.debug("API: event loop close failed but continuing")

        # --- Log conversation into active goal -------------------------------
        try:
            architect_agent.goal_mgr.add_note_to_goal(active_goal["id"], "user", user_input)
            architect_agent.goal_mgr.add_note_to_goal(active_goal["id"], "othello", agentic_reply)
            logger.debug(f"API: Logged conversation to goal #{active_goal['id']}")
        except Exception as e:
            logger.warning(f"API: Failed to log exchange for goal #{active_goal['id']}: {e}")
        # ---------------------------------------------------------------------

        # Log final response details
        logger.info(f"API: Returning response - planner_active={agent_status.get('planner_active', False)}, had_xml={agent_status.get('had_goal_update_xml', False)}")

        response = {
            "reply": agentic_reply,
            "agent_status": agent_status
        }
        try:
            logger.info("API: running insight extraction for message (goal mode)")
            response["insights_meta"] = _process_insights_pipeline(
                user_text=raw_user_input,
                assistant_text=agentic_reply,
                user_id=DEFAULT_USER_ID,
            )
            logger.info(
                "API: insight extraction completed (created=%s)",
                response["insights_meta"].get("created", "?"),
            )
        except Exception as exc:
            logger.warning("API: insight extraction skipped due to error: %s", exc, exc_info=True)
        return jsonify(response)
    
    # === Fallback: Casual chat mode (no active goal) ====================
    else:
        logger.info("API: No active goal for this message; falling back to casual mode")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            agentic_reply, agent_status = loop.run_until_complete(
                architect_agent.plan_and_execute(
                    user_input,
                    context=None,
                )
            )
            loop.close()
            
            logger.info(f"API: Casual chat completed successfully")
            logger.debug(f"API: Reply preview: {agentic_reply[:150]}...")
            
        except Exception as e:
            logger.error(f"API: Casual chat failed with exception: {e}", exc_info=True)
            agentic_reply = "I'm having trouble processing that right now. Could you try again?"
            agent_status = {"planner_active": False, "had_goal_update_xml": False}

        response = {
            "reply": agentic_reply,
            "agent_status": agent_status
        }
        try:
            logger.info("API: running insight extraction for message (casual mode)")
            response["insights_meta"] = _process_insights_pipeline(
                user_text=raw_user_input,
                assistant_text=agentic_reply,
                user_id=DEFAULT_USER_ID,
            )
            logger.info(
                "API: insight extraction completed (created=%s)",
                response["insights_meta"].get("created", "?"),
            )
        except Exception as exc:
            logger.warning("API: insight extraction skipped due to error: %s", exc, exc_info=True)
        return jsonify(response)


@app.route("/api/today-plan", methods=["GET"])
@require_auth
def get_today_plan():
    """Return today's blended plan of routines + focused goal tasks.

    Query params (optional):
        mood: int 1-10 (energy)
        fatigue: low|medium|high
        time_pressure: truthy flag
    """
    logger = logging.getLogger("API")
    args = request.args or {}
    mood_context = {
        "mood": args.get("mood"),
        "fatigue": args.get("fatigue"),
        "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
    }
    try:
        plan = othello_engine.generate_today_plan(mood_context=mood_context)
        sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
        goal_tasks_count = len(sections.get("goal_tasks", []) or [])
        plan_source = plan.get("_plan_source") if isinstance(plan, dict) else None
        logger.info("API: Served today plan goal_tasks_count=%s source=%s", goal_tasks_count, plan_source or "unknown")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to build today plan: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/today-brief", methods=["GET"])
@require_auth
def get_today_brief():
    """Return a terse tactical brief for voice/read-out."""
    logger = logging.getLogger("API")
    args = request.args or {}
    mood_context = {
        "mood": args.get("mood"),
        "fatigue": args.get("fatigue"),
        "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
    }
    try:
        brief = othello_engine.get_today_brief(mood_context=mood_context)
        logger.info("API: Served today brief")
        return jsonify({"brief": brief})
    except Exception as exc:
        logger.error(f"API: Failed to build today brief: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/plan/update", methods=["POST"])
@require_auth
def update_plan_item():
    """Update lifecycle status for a plan item (complete/skip/reschedule)."""
    logger = logging.getLogger("API")
    data = request.get_json() or {}
    item_id = data.get("item_id")
    status = data.get("status")
    plan_date = data.get("plan_date")
    reason = data.get("reason")
    reschedule_to = data.get("reschedule_to")

    if not item_id or not status:
        return jsonify({"error": "item_id and status are required"}), 400

    try:
        plan = othello_engine.update_plan_item(
            item_id=item_id,
            status=status,
            plan_date=plan_date,
            reason=reason,
            reschedule_to=reschedule_to,
        )
        logger.info(f"API: Updated plan item {item_id} -> {status}")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to update plan item {item_id}: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 400


@app.route("/api/plan/rebuild", methods=["POST"])
@require_auth
def rebuild_today_plan():
    """Force regeneration of today's plan (used when context shifts)."""
    logger = logging.getLogger("API")
    data = request.get_json() or {}
    mood_context = data.get("mood_context") or data
    try:
        plan = othello_engine.rebuild_today_plan(mood_context=mood_context)
        logger.info("API: Rebuilt today plan on demand")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to rebuild plan: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/goals", methods=["GET"])
@require_auth
def get_goals():
    """
    Simple read-only endpoint so the UI can see what goals
    the Architect/GoalManager have captured so far.
    """
    try:
        goals = architect_agent.goal_mgr.list_goals()
        return jsonify({"goals": goals})
    except Exception as e:
        logging.getLogger("ARCHITECT").error(f"Failed to fetch goals: {e}")
        return jsonify({"goals": [], "error": str(e)}), 500


@app.route("/api/goals/<int:goal_id>", methods=["GET"])
@require_auth
def get_goal_with_plan(goal_id):
    """
    Get a single goal with its associated plan steps.
    
    Returns:
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
                        "status": "pending",
                        "due_date": null
                    },
                    ...
                ]
            }
        }
    """
    logger = logging.getLogger("API")
    try:
        goal = architect_agent.goal_mgr.get_goal_with_plan(goal_id)
        
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found")
            return jsonify({
                "error": "Goal not found",
                "goal_id": goal_id
            }), 404
        
        logger.info(f"API: Retrieved goal #{goal_id} with {len(goal.get('plan_steps', []))} steps")
        return jsonify({"goal": goal})
        
    except Exception as e:
        logger.error(f"API: Failed to fetch goal #{goal_id}: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "goal_id": goal_id
        }), 500


@app.route("/api/goals/active-with-next-actions", methods=["GET"])
@require_auth
def get_active_goals_with_next_actions():
    """
    Get all active goals with their next incomplete step.
    
    Returns:
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
                        "status": "pending"
                    }
                },
                ...
            ]
        }
    """
    logger = logging.getLogger("API")
    try:
        all_goals = architect_agent.goal_mgr.list_goals()
        
        # Filter for active goals
        active_goals = [g for g in all_goals if g.get("status") == "active"]
        
        results = []
        for goal in active_goals:
            goal_id = goal.get("id")
            if goal_id is None:
                continue
            
            # Get next action for this goal
            next_step = architect_agent.goal_mgr.get_next_action_for_goal(goal_id)
            
            results.append({
                "goal_id": goal_id,
                "title": goal.get("text", ""),
                "status": goal.get("status", ""),
                "next_step": next_step  # Will be None if all steps are done
            })
        
        logger.info(f"API: Retrieved {len(results)} active goals with next actions")
        return jsonify({"goals": results})
        
    except Exception as e:
        logger.error(f"API: Failed to fetch active goals with next actions: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "goals": []
        }), 500


@app.route("/api/goals/<int:goal_id>/steps/<int:step_id>/status", methods=["POST"])
@require_auth
def update_step_status(goal_id, step_id):
    """
    Update the status of a specific plan step.
    
    Request body:
        {
            "status": "pending" | "in_progress" | "done"
        }
    
    Returns:
        {
            "step": {
                "id": 2,
                "goal_id": 1,
                "step_index": 2,
                "description": "Build a small project",
                "status": "done",
                ...
            }
        }
    """
    logger = logging.getLogger("API")
    data = request.get_json() or {}
    new_status = data.get("status")
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "done"]
    if not new_status or new_status not in valid_statuses:
        return jsonify({
            "error": "Invalid status. Must be one of: pending, in_progress, done",
            "valid_statuses": valid_statuses
        }), 400
    
    try:
        updated_step = architect_agent.goal_mgr.update_plan_step_status(
            goal_id, step_id, new_status
        )
        
        if updated_step is None:
            logger.warning(f"API: Failed to update step #{step_id} for goal #{goal_id}")
            return jsonify({
                "error": "Step not found or does not belong to this goal",
                "goal_id": goal_id,
                "step_id": step_id
            }), 404
        
        logger.info(f"API: Updated step #{step_id} status to '{new_status}'")
        return jsonify({"step": updated_step})
        
    except Exception as e:
        logger.error(f"API: Failed to update step status: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "goal_id": goal_id,
            "step_id": step_id
        }), 500


@app.route("/api/goals/<int:goal_id>/plan", methods=["POST"])
@require_auth
def trigger_goal_planning(goal_id):
    """
    Trigger architect planning for a specific goal.
    
    Request body:
        {
            "instruction": "Plan out how to achieve this goal step by step"
        }
    
    This endpoint:
    - Fetches the goal details
    - Collects relevant memories
    - Calls the architect brain with goal context
    - Returns the updated goal with plan steps
    """
    logger = logging.getLogger("API")
    data = request.get_json() or {}
    instruction = data.get("instruction", "").strip()
    
    if not instruction:
        instruction = "Create a detailed step-by-step plan for achieving this goal."
    
    try:
        # Get the goal
        goal = architect_agent.goal_mgr.get_goal(goal_id)
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found for planning")
            return jsonify({
                "error": "Goal not found",
                "goal_id": goal_id
            }), 404
        
        # Set as active goal
        architect_agent.goal_mgr.set_active_goal(goal_id)
        
        # Build goal context
        goal_context = architect_agent.goal_mgr.build_goal_context(goal_id, max_notes=10)
        
        logger.info(f"API: Triggering planning for goal #{goal_id}: {goal.get('text', '')[:50]}...")
        
        # Call architect in planning mode
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        context = {
            "goal_context": goal_context,
            "active_goal": goal
        }
        
        agentic_reply, agent_status = loop.run_until_complete(
            architect_agent.plan_and_execute(
                instruction,
                context=context
            )
        )
        loop.close()
        
        # Get updated goal with plan
        updated_goal = architect_agent.goal_mgr.get_goal_with_plan(goal_id)
        
        logger.info(
            f"API: Planning completed for goal #{goal_id}. "
            f"XML: {agent_status.get('had_goal_update_xml', False)}, "
            f"Steps: {len(updated_goal.get('plan_steps', []))}"
        )
        
        return jsonify({
            "reply": agentic_reply,
            "goal": updated_goal,
            "agent_status": agent_status
        })
        
    except Exception as e:
        logger.error(f"API: Failed to trigger planning for goal #{goal_id}: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "goal_id": goal_id
        }), 500


def _ensure_today_plan_id() -> Optional[int]:
    logger = logging.getLogger("API.Insights")
    planner_user = getattr(othello_engine.day_planner, "user_id", "default")

    def _fetch_plan_row() -> Optional[Dict[str, Any]]:
        return plan_repository.get_plan_by_date(planner_user, date.today())

    # Try existing row
    today_row = _fetch_plan_row()
    if not today_row:
        # Generate (or rebuild) and persist a plan row for today
        try:
            othello_engine.rebuild_today_plan()
        except Exception as exc:
            logger.warning("API: failed to rebuild plan before applying insight: %s", exc)
        today_row = _fetch_plan_row()

    if not today_row:
        logger.warning("API: no today plan row found while applying insight")
        return None
    plan_id = today_row.get("id")
    if not plan_id:
        logger.warning("API: today plan row missing id while applying insight")
        return None
    logger.debug("API: ensure today plan id resolved %s", {"plan_id": plan_id, "user": planner_user})
    return plan_id


def _extract_insight_labels(insight: dict) -> list:
    labels = []
    payload_items = (insight.get("payload") or {}).get("items") or []
    for entry in payload_items:
        if isinstance(entry, dict):
            label = entry.get("label") or entry.get("title") or entry.get("text") or entry.get("description")
        else:
            label = str(entry).strip()
        if label:
            label = label.strip()
            labels.append(label)
    if not labels:
        fallback_label = insight.get("summary") or insight.get("content")
        if fallback_label:
            labels.append(fallback_label)
    return labels


def _build_insight_plan_item(insight: dict, label: str, idx: int) -> dict:
    item_id = f"insight-{insight.get('id')}-task-{idx}"
    section_hint = "deep-work"
    priority_value = "priority"
    metadata = {
        "id": item_id,
        "type": "goal_task",
        "label": label,
        "status": "planned",
        "priority": priority_value,
        "effort": "light",
        "section_hint": section_hint,
        "energy_cost": "low",
        "source": "insight",
        "insight_id": insight.get("id"),
    }
    return {
        "id": item_id,
        "type": "goal_task",
        "section": "goal_tasks",
        "section_hint": section_hint,
        "status": "planned",
        "priority": priority_value,
        "effort": "light",
        "energy": "low",
        "metadata": metadata,
    }


def _append_goal_task_to_plan(plan_item: dict) -> bool:
    """Append a goal_task into today's plan sections and persist.

    Returns True if appended, False if skipped (e.g., duplicate).
    """
    logger = logging.getLogger("API.Insights")
    try:
        plan = othello_engine.day_planner.get_today_plan(force_regen=False)
    except Exception as exc:
        logger.warning("API: failed to load plan before appending insight task: %s", exc, exc_info=True)
        return False

    sections = plan.setdefault("sections", {})
    goal_tasks = sections.setdefault("goal_tasks", [])
    existing_ids = {str(item.get("id")) for item in goal_tasks if item.get("id")}

    item_id = str(plan_item.get("id") or plan_item.get("item_id") or "").strip()
    if not item_id:
        logger.warning("API: insight task missing id; skipping append")
        return False
    if item_id in existing_ids:
        logger.info("API: insight task already present in plan; skipping duplicate id=%s", item_id)
        return False

    goal_tasks.append(plan_item)
    try:
        othello_engine.day_planner._persist_plan(date.today(), plan)  # type: ignore[attr-defined]
    except Exception as exc:
        logger.warning("API: failed to persist plan after appending insight task: %s", exc, exc_info=True)
        return False

    try:
        planner_user = getattr(othello_engine.day_planner, "user_id", DEFAULT_USER_ID)
        meta = plan_item.get("metadata") or {}
        label = meta.get("label") or plan_item.get("label") or item_id
        goal_task_history_repository.upsert_goal_task(
            user_id=str(planner_user),
            plan_date=date.today(),
            item_id=item_id,
            label=label,
            status=plan_item.get("status") or meta.get("status"),
            effort=plan_item.get("effort") or meta.get("effort"),
            section_hint=plan_item.get("section_hint") or plan_item.get("section"),
            source_insight_id=meta.get("insight_id") or plan_item.get("insight_id"),
            metadata={**meta, "label": label},
        )
    except Exception as exc:
        logger.warning(
            "API: failed to persist goal_task_history id=%s label=%s: %s",
            item_id,
            (plan_item.get("metadata") or {}).get("label") or plan_item.get("label"),
            exc,
            exc_info=True,
        )

    logger.info(
        "API: appended insight task to plan id=%s label=%s goal_tasks_count=%s",
        item_id,
        (plan_item.get("metadata") or {}).get("label") or plan_item.get("label"),
        len(goal_tasks),
    )
    return True


def _apply_plan_insight(insight: dict) -> int:
    logger = logging.getLogger("API.Insights")
    labels = _extract_insight_labels(insight)
    if not labels:
        logger.warning("API: cannot apply plan insight; labels missing %s", {"labels": labels})
        return 0
    created = 0
    for idx, label in enumerate(labels, 1):
        item = _build_insight_plan_item(insight, label, idx)
        logger.debug("API: appending plan item from insight %s", {
            "label": label,
            "item_id": item.get("id"),
            "type": item.get("type"),
            "section": item.get("section"),
        })
        if _append_goal_task_to_plan(item):
            created += 1
    return created


def _apply_simple_plan_item_from_insight(insight: dict) -> int:
    logger = logging.getLogger("API.Insights")
    labels = _extract_insight_labels(insight)
    if not labels:
        return 0
    item = _build_insight_plan_item(insight, labels[0], 1)
    logger.debug("API: appending simple plan item from insight %s", {
        "label": labels[0],
        "item_id": item.get("id"),
        "type": item.get("type"),
        "section": item.get("section"),
    })
    if _append_goal_task_to_plan(item):
        logger.info("API: appended simple plan item from insight id=%s label='%s'", insight.get("id"), labels[0])
        return 1
    return 0


def _apply_goal_insight(insight: dict) -> None:
    payload = insight.get("payload") or {}
    items = payload.get("items") or []
    title = payload.get("title") or (items[0] if items else insight.get("summary"))
    if not title:
        return
    try:
        architect_agent.goal_mgr.add_goal(title)
    except Exception as exc:
        logging.getLogger("API").warning(f"API: failed to apply goal insight: {exc}")


def _apply_routine_insight(insight: dict) -> None:
    # Placeholder: routines persistence not fully wired yet.
    # We keep the insight payload as the source of truth.
    return


def _apply_idea_insight(insight: dict) -> None:
    # Placeholder: no dedicated ideas inbox yet; marking applied keeps payload accessible.
    return


@app.route("/api/insights/summary", methods=["GET"])
@require_auth
def insights_summary():
    logger = logging.getLogger("API.Insights")
    try:
        counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
        logger.info("API: insights summary pending_counts=%s", counts)
        return jsonify({"pending_counts": counts})
    except Exception as exc:
        logger.warning("API: insights summary failed: %s", exc, exc_info=True)
        return jsonify({"pending_counts": {}, "error": "insights summary unavailable"})


@app.route("/api/insights/list", methods=["GET"])
@require_auth
def insights_list():
    logger = logging.getLogger("API.Insights")
    status = (request.args.get("status") or "pending").strip().lower()

    logger.info("API: /api/insights/list status=%s", status or "any")

    try:
        insights = insights_repository.list_insights(
            user_id=DEFAULT_USER_ID,
            status=status,
        )
        items = [serialize_insight(i) for i in insights]
        logger.info("API: /api/insights/list returning %s insights", len(items))
        return jsonify({"insights": items})
    except Exception as exc:
        logger.warning("API: insights list failed: %s", exc, exc_info=True)
        return jsonify({"insights": [], "error": "insights list unavailable"})


@app.route("/api/insights/apply", methods=["POST"])
@require_auth
def insights_apply():
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return jsonify({"error": "id is required"}), 400
    insight = insights_repository.get_insight_by_id(DEFAULT_USER_ID, insight_id)
    if not insight:
        return jsonify({"error": "insight not found"}), 404

    try:
        created_count = 0
        if insight.get("type") == "plan":
            created_count += _apply_plan_insight(insight)
        elif insight.get("type") == "goal":
            _apply_goal_insight(insight)
            created_count += _apply_simple_plan_item_from_insight(insight)
        elif insight.get("type") == "routine":
            _apply_routine_insight(insight)
            created_count += _apply_simple_plan_item_from_insight(insight)
        else:
            _apply_idea_insight(insight)
            created_count += _apply_simple_plan_item_from_insight(insight)

        try:
            insights_repository.update_insight_status(insight_id, "applied", user_id=DEFAULT_USER_ID)
        except Exception as exc:
            logging.getLogger("API.Insights").warning(
                "API: failed to update insight status for id=%s: %s", insight_id, exc
            )

        counts = {}
        try:
            counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
        except Exception as exc:
            logging.getLogger("API.Insights").warning("API: failed to refresh pending counts after apply: %s", exc)

        return jsonify({
            "ok": True,
            "applied_count": created_count,
            "insights_meta": {"pending_counts": counts},
        })
    except Exception as exc:
        logging.getLogger("API").error(f"API: failed to apply insight {insight_id}: {exc}", exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/goal-tasks/history", methods=["GET"])
@require_auth
def goal_task_history():
    logger = logging.getLogger("API.GoalTasks")
    args = request.args or {}
    status = (args.get("status") or "").strip() or None
    start_date_param = args.get("start_date")
    end_date_param = args.get("end_date")
    days_param = args.get("days")

    today = date.today()
    try:
        if start_date_param:
            start_date = date.fromisoformat(start_date_param)
        elif days_param:
            try:
                days = int(days_param)
            except Exception:
                days = 1
            days = max(1, min(days, 30))
            start_date = today - timedelta(days=days - 1)
        else:
            start_date = today

        if end_date_param:
            end_date = date.fromisoformat(end_date_param)
        else:
            end_date = today if not start_date_param else start_date

        rows = goal_task_history_repository.list_goal_tasks(
            DEFAULT_USER_ID,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=300,
        )
        payload = [serialize_goal_task_history(r) for r in rows]
        return jsonify({
            "goal_tasks": payload,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        })
    except Exception as exc:
        logger.warning("API: goal task history fetch failed: %s", exc, exc_info=True)
        return jsonify({"goal_tasks": [], "error": "history unavailable"}), 500


@app.route("/api/insights/dismiss", methods=["POST"])
@require_auth
def insights_dismiss():
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return jsonify({"error": "id is required"}), 400
    insight = insights_repository.get_insight_by_id(DEFAULT_USER_ID, insight_id)
    if not insight:
        return jsonify({"error": "insight not found"}), 404

    try:
        insights_repository.update_insight_status(insight_id, "dismissed", user_id=DEFAULT_USER_ID)
        counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
        return jsonify({"ok": True, "insights_meta": {"pending_counts": counts}})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/health/db", methods=["GET"])
def health_check_db():
    """
    Database health check endpoint.
    
    Tests the database connection by executing a simple query.
    Returns JSON with status 'ok' or 'error'.
    """
    try:
        from db.database import fetch_one
        
        # Try a simple query to verify database connectivity
        result = fetch_one("SELECT 1 as health_check")
        
        if result and result.get("health_check") == 1:
            return jsonify({
                "status": "ok",
                "message": "Database connection healthy",
                "database": "PostgreSQL (Neon)"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "details": "Query returned unexpected result"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "details": str(e),
            "message": "Database connection failed"
        }), 503


@app.route("/", methods=["GET"])
def serve_ui():
    """
    Serve the Othello UI at the root path.
    """
    return send_file("othello_ui.html")



# Log config snapshot at startup (safe, no secrets)
try:
    snap = get_runtime_config_snapshot()
    logging.info(
        f"[CONFIG] auth_mode={snap['auth_mode_selected']}, secret_key_source={snap['secret_key_source']}, db_configured={snap['db_mode']}, model={snap['model_selected']}, build={snap['build']}"
    )
except Exception as e:
    logging.warning(f"[CONFIG] Could not log config snapshot: {e}")

if __name__ == "__main__":
    app.run(port=8000, debug=False)


# ============================================================================
# BASIC FLOW AFTER UPGRADE - How to use the enhanced planning engine
# ============================================================================
#
# 1. CREATE A NEW GOAL
#    Send a message to /api/message with goal declaration:
#    POST /api/message
#    {"message": "My goal is to learn Python"}
#    
#    Response will include goal_id and optionally prompt for planning.
#
# 2. TRIGGER PLANNING FOR THE GOAL
#    Use the new planning endpoint:
#    POST /api/goals/{goal_id}/plan
#    {"instruction": "Create a detailed step-by-step plan"}
#    
#    This will:
#    - Call architect brain with goal context
#    - Extract XML with plan steps
#    - Save steps to plan_steps table
#    - Write memory entry
#    - Return updated goal with plan_steps array
#
# 3. FETCH THE GOAL AND ITS PLAN
#    GET /api/goals/{goal_id}
#    
#    Returns goal with plan_steps array ordered by step_index.
#
# 4. MARK A STEP AS DONE
#    POST /api/goals/{goal_id}/steps/{step_id}/status
#    {"status": "done"}
#    
#    Updates the step status in the database.
#
# 5. GET ACTIVE GOALS WITH NEXT ACTIONS
#    GET /api/goals/active-with-next-actions
#    
#    Returns all active goals with their next incomplete step.
#
# All of this works without manual DB edits. The XML-driven planning engine
# handles extraction, persistence, and memory writing automatically.
#
# Expected XML schema from LLM in planning mode:
# <goal_update>
#   <summary>Goal summary</summary>
#   <status>active|completed|paused</status>
#   <priority>1-5 or low|medium|high</priority>
#   <category>work|personal|health|learning</category>
#   <plan_steps>
#     <step index="1" status="pending" due_date="2025-12-15">First step</step>
#     <step index="2" status="pending">Second step</step>
#   </plan_steps>
#   <metadata>
#     <tags>tag1,tag2</tags>
#     <notes>Additional notes</notes>
#   </metadata>
# </goal_update>
# ============================================================================
