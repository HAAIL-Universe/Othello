import logging
import os
import re
import time
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, send_file, session, send_from_directory, g, Blueprint
from flask_cors import CORS
import asyncio
from typing import Any, Dict, Optional, List, Tuple
from functools import wraps
from passlib.hash import bcrypt
import mimetypes
from utils.llm_config import is_openai_configured, get_openai_api_key
from core.capabilities_registry import (
    format_capabilities_for_chat,
    get_capabilities_payload,
    get_help_capabilities,
)
import openai
import httpx
import uuid
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from db import routines_repository
from db import suggestions_repository
from db import goals_repository
from db.database import get_connection
import hashlib
import json

# NOTE: Keep import-time work minimal! Do not import LLM/agent modules or connect to DB at module scope unless required for health endpoints.
from dotenv import load_dotenv

# Preserve any runtime-provided OPENAI_API_KEY (e.g., Render env var) when loading local .env for dev.
_preexisting_openai_key = os.environ.get("OPENAI_API_KEY")
load_dotenv(override=False)
if _preexisting_openai_key and _preexisting_openai_key.strip():
    os.environ["OPENAI_API_KEY"] = _preexisting_openai_key

def _is_truthy_env(value: Optional[str]) -> bool:
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized in ("1", "true", "yes", "on")

def _is_phase1_enabled() -> bool:
    phase = (os.environ.get("OTHELLO_PHASE") or "").strip().lower()
    if phase == "phase1":
        return True
    return _is_truthy_env(os.environ.get("OTHELLO_PHASE1"))

def _parse_env_csv(name: str) -> List[str]:
    raw = os.environ.get(name)
    if not raw:
        return []
    return [entry.strip() for entry in str(raw).split(",") if entry.strip()]

def _get_beta_allowlist() -> set:
    return set(_parse_env_csv("BETA_ALLOWLIST"))

def _get_beta_user_cap() -> int:
    raw = os.environ.get("BETA_USER_CAP")
    if raw is None:
        return 0
    raw_text = str(raw).strip()
    if not raw_text:
        return 0
    try:
        cap = int(raw_text)
    except ValueError:
        logging.getLogger("API.Auth").warning("Invalid BETA_USER_CAP value '%s'; ignoring.", raw_text)
        return 0
    return max(cap, 0)

_PHASE1_ENABLED = _is_phase1_enabled()
if _PHASE1_ENABLED:
    os.environ["OTHELLO_PHASE1_DB_ONLY"] = "1"

# Configure logging to show DEBUG messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
if _PHASE1_ENABLED:
    logging.getLogger("API.Startup").info("[Phase-1] DB-only + confirm-gated mode enabled")

# Constants
MAX_ERROR_MSG_LENGTH = 200  # Maximum length for error message logging
REQUEST_ID_HEADER = "X-Request-ID"
CHAT_CONTEXT_TURNS = 12
CHAT_CONTEXT_MAX_CHARS = 6000
CLARIFICATION_TTL_SECONDS = 600
AI2_BATCH_TTL_SECONDS = 600

# Simple in-memory cache for clarification candidates: { user_id: { candidates, request, created_at, plan_date } }
CLARIFICATION_CACHE = {}
# Simple in-memory cache for AI2 batches: { user_id: { option_a_id, option_b_id, created_at, plan_date } }
AI2_BATCH_CACHE = {}

def _get_valid_clarification_cache(user_id: str, local_today: date) -> Optional[Dict]:
    """
    Retrieves clarification cache if valid (not expired, same day).
    Returns None if invalid or missing, and cleans up.
    """
    entry = CLARIFICATION_CACHE.get(user_id)
    if not entry:
        return None
        
    # Check Day Scope
    if entry.get("plan_date") != local_today.isoformat():
        CLARIFICATION_CACHE.pop(user_id, None)
        return None
        
    # Check TTL
    created_at = entry.get("created_at", 0)
    now_ts = datetime.now(timezone.utc).timestamp()
    if (now_ts - created_at) > CLARIFICATION_TTL_SECONDS:
        CLARIFICATION_CACHE.pop(user_id, None)
        return None
        
    return entry

def _get_last_ai2_batch_from_db(user_id: str, local_today: date) -> Optional[Dict]:
    """
    Authoritative fallback: fetches the most recent AI2 batch from DB.
    Returns a dict structure compatible with AI2_BATCH_CACHE.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Find the latest batch_id for this user and day
                cursor.execute(
                    """
                    SELECT provenance->>'ai2_batch_id' as batch_id, MAX(created_at) as last_created
                    FROM suggestions
                    WHERE user_id = %s 
                      AND kind = 'plan_proposal'
                      AND provenance->>'ai2_batch_id' IS NOT NULL
                      AND provenance->>'plan_date' = %s
                    GROUP BY batch_id
                    ORDER BY last_created DESC
                    LIMIT 1
                    """,
                    (user_id, local_today.isoformat())
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                batch_id = row[0]
                created_at_dt = row[1]
                
                # TTL Check
                if created_at_dt.tzinfo is None:
                    created_at_dt = created_at_dt.replace(tzinfo=timezone.utc)
                
                age = (datetime.now(timezone.utc) - created_at_dt).total_seconds()
                if age > AI2_BATCH_TTL_SECONDS:
                    return None
                
                # Now fetch the suggestions for this batch
                cursor.execute(
                    """
                    SELECT id, provenance->>'option_label' as label
                    FROM suggestions
                    WHERE user_id = %s 
                      AND provenance->>'ai2_batch_id' = %s
                    """,
                    (user_id, batch_id)
                )
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                    
                entry = {
                    "created_at": created_at_dt.timestamp(),
                    "plan_date": local_today.isoformat(),
                    "batch_id": batch_id
                }
                
                for r in rows:
                    s_id = r[0]
                    label = r[1] # "A" or "B"
                    if label == "A":
                        entry["option_a"] = s_id
                    elif label == "B":
                        entry["option_b"] = s_id
                
                return entry
    except Exception as e:
        logger.error(f"DB fallback for AI2 batch failed: {e}")
        return None

def _get_valid_ai2_batch_cache(user_id: str, local_today: date) -> Optional[Dict]:
    """
    Retrieves AI2 batch cache if valid (not expired, same day).
    Returns None if invalid or missing, and cleans up.
    """
    entry = AI2_BATCH_CACHE.get(user_id)
    
    # Fallback to DB if cache miss
    if not entry:
        entry = _get_last_ai2_batch_from_db(user_id, local_today)
        
    if not entry:
        return None
        
    # Check Day Scope
    if entry.get("plan_date") != local_today.isoformat():
        AI2_BATCH_CACHE.pop(user_id, None)
        return None
        
    # Check TTL
    created_at = entry.get("created_at", 0)
    now_ts = datetime.now(timezone.utc).timestamp()
    if (now_ts - created_at) > AI2_BATCH_TTL_SECONDS:
        AI2_BATCH_CACHE.pop(user_id, None)
        return None
        
    return entry



def _get_request_id() -> str:
    request_id = getattr(g, "request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())
        g.request_id = request_id
    return request_id


def _is_api_request() -> bool:
    try:
        return request.path.startswith("/api/")
    except Exception:
        return False


def api_error(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Any] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    payload = {
        "error_code": error_code,
        "message": message,
        "request_id": _get_request_id(),
    }
    if details is not None:
        payload["details"] = details
    if extra:
        payload.update(extra)
    response = jsonify(payload)
    response.status_code = status_code
    return response

# Helper function to classify OpenAI errors and return appropriate JSON responses
def handle_llm_error(e: Exception, logger: logging.Logger):
    """
    Classify LLM/OpenAI errors and return structured JSON response with appropriate status code.
    
    Args:
        e: The exception that was raised
        logger: Logger instance for logging the error
        
    Returns:
        Tuple of (json_dict, status_code)
    """
    # Log the exception class and message (sanitized - no API keys)
    error_class = type(e).__name__
    error_msg = str(e)
    request_id = _get_request_id()
    logger.error(
        "LLM error: %s: %s request_id=%s",
        error_class,
        error_msg[:MAX_ERROR_MSG_LENGTH],
        request_id,
        exc_info=False,
    )
    
    # Timeout errors
    if isinstance(e, (openai.APITimeoutError, httpx.TimeoutException)):
        return api_error("LLM_TIMEOUT", "LLM timeout", 504, details="LLM request timed out")

    # Authentication errors
    if isinstance(e, openai.AuthenticationError):
        return api_error(
            "LLM_AUTH_FAILED",
            "LLM auth failed",
            503,
            details="Invalid API key or auth failure",
        )
    
    # Rate limit errors  
    if isinstance(e, openai.RateLimitError):
        return api_error(
            "LLM_RATE_LIMIT",
            "LLM rate limit reached",
            429,
            details="API rate limit exceeded. Please try again later.",
        )
    
    # Connection errors
    if isinstance(e, openai.APIConnectionError):
        return api_error(
            "LLM_CONNECTION_ERROR",
            "LLM connection error",
            502,
            details="Could not connect to LLM service",
        )
    
    # Other OpenAI API errors
    if isinstance(e, openai.OpenAIError):
        return api_error(
            "LLM_UPSTREAM_ERROR",
            "LLM upstream error",
            502,
            details=f"LLM service error: {error_class}",
        )
    
    # Generic error for non-OpenAI exceptions
    return api_error(
        "LLM_INTERNAL_ERROR",
        "Internal error",
        500,
        details=f"An unexpected error occurred: {error_class}",
    )


def _unwrap_llm_exception(exc: Exception) -> Optional[Exception]:
    if isinstance(exc, (openai.OpenAIError, httpx.TimeoutException, asyncio.TimeoutError)):
        return exc
    cause = getattr(exc, "__cause__", None)
    if isinstance(cause, (openai.OpenAIError, httpx.TimeoutException, asyncio.TimeoutError)):
        return cause
    return None

# --- Flask App Setup (must be before any route decorators) ---
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)  # Allow requests from frontend

# Harden SECRET_KEY handling for production (support OTHELLO_SECRET_KEY alias)
_secret_env = (os.getenv("OTHELLO_SECRET_KEY") or os.getenv("SECRET_KEY") or "").strip()
if not _secret_env:
    if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
        logging.warning("[API] WARNING: SECRET_KEY/OTHELLO_SECRET_KEY is not set in environment! Using insecure default. Set SECRET_KEY or OTHELLO_SECRET_KEY in Render environment variables.")
    _secret_env = "dev-secret-key"
app.config["SECRET_KEY"] = _secret_env
_is_render = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(_is_render)
if _is_render:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def _log_auth_config():
    """Log presence booleans for auth-related env; never log values."""
    logger = logging.getLogger("API.Auth")
    secret_present = bool(_secret_env)
    pin_present = bool((os.getenv("OTHELLO_PIN_HASH") or "").strip())
    login_key_present = bool((os.getenv("OTHELLO_LOGIN_KEY") or "").strip())
    legacy_pwd_present = bool((os.getenv("OTHELLO_PASSWORD") or "").strip())
    auth_mode = "pin_hash" if pin_present else ("login_key" if login_key_present else ("plaintext_password" if legacy_pwd_present else "none"))
    logger.info(
        "AuthConfig: secret_present=%s pin_hash_present=%s login_key_present=%s legacy_pwd_present=%s auth_mode=%s",
        secret_present,
        pin_present,
        login_key_present,
        legacy_pwd_present,
        auth_mode,
    )

_log_auth_config()

# Minimal auth config (compat bridge)
OTHELLO_PASSWORD = os.environ.get("OTHELLO_PASSWORD")
OTHELLO_PIN_HASH = os.environ.get("OTHELLO_PIN_HASH")

def get_runtime_config_snapshot():
    """
    Returns a dict with booleans for env presence, selected auth/secret/model/db modes, and build info.
    Never includes or logs secret values.
    """
    env = os.environ
    def present(key):
        val = env.get(key)
        return bool(val and str(val).strip())

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


# Debug config endpoint registration (to avoid import-order issues)
def register_debug_routes(app):
    def _debug_config_allowed():
        # Only allow if authed session AND DEBUG_CONFIG=1
        if not session.get("authed"):
            return False
        return os.environ.get("DEBUG_CONFIG") == "1"

    @app.route("/api/debug/config", methods=["GET"])
    def debug_config():
        if not _debug_config_allowed():
            return api_error("NOT_FOUND", "Not found", 404)
        return jsonify(get_runtime_config_snapshot())

# Asset route registration (after app exists)
def register_asset_routes(app):
    @app.get('/scripts/<path:filename>')
    def serve_scripts(filename):
        return send_from_directory(os.path.join(os.getcwd(), 'scripts'), filename)

    @app.get('/interface/<path:filename>')
    def serve_interface(filename):
        return send_from_directory(os.path.join(os.getcwd(), 'interface'), filename)

# Register debug and asset routes after app/session setup
v1 = Blueprint("v1", __name__, url_prefix="/v1")

register_debug_routes(app)
register_asset_routes(app)


@app.before_request
def assign_request_id():
    g.request_id = str(uuid.uuid4())
    if _is_api_request():
        logging.getLogger("API").info(
            "API: request start request_id=%s method=%s path=%s",
            g.request_id,
            request.method,
            request.path,
        )


@app.after_request
def attach_request_id(response):
    request_id = getattr(g, "request_id", None)
    if request_id:
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(exc: HTTPException):
    if not _is_api_request():
        return exc
    logger = logging.getLogger("API")
    logger.warning(
        "API: HTTPException status=%s name=%s request_id=%s",
        exc.code,
        exc.name,
        _get_request_id(),
    )
    return api_error(
        f"HTTP_{exc.code}",
        exc.description or "Request failed",
        exc.code or 500,
        details={"name": exc.name},
    )


@app.errorhandler(Exception)
def handle_unhandled_exception(exc: Exception):
    if not _is_api_request():
        raise exc
    logging.getLogger("API").error(
        "API: unhandled exception request_id=%s", _get_request_id(), exc_info=True
    )
    return api_error("INTERNAL_ERROR", "Internal server error", 500)

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

# Initialize database connection pool
db_initialized = False
try:
    from db.database import init_pool, ensure_core_schema, fetch_one, execute_query
    init_pool()
    ensure_core_schema()

    # Migration: Ensure draft_text column exists
    try:
        execute_query("ALTER TABLE goals ADD COLUMN IF NOT EXISTS draft_text TEXT")
        print("[API] [OK] Ensured goals.draft_text column exists")
    except Exception as e:
        print(f"[API] [ERR] Failed to ensure goals.draft_text column: {e}")

    db_initialized = True
    print("[API] [OK] Database connection pool initialized successfully")
    print("[API] [OK] Connected to Neon PostgreSQL database")
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
    print(f"[API] [ERR] Warning: Failed to initialize database: {e}")
    print("[API] [ERR] The app will run but goal persistence may not work correctly")
    print("[API] [ERR] Check that DATABASE_URL is set in .env and the database is accessible")

# Lazy initialization of agent components (runtime only)
_agent_components = None
_agent_init_error = None
_agent_init_error_message = None


def _openai_key_present() -> bool:
    """Check for a non-empty OPENAI_API_KEY without logging secrets."""
    key = os.getenv("OPENAI_API_KEY")
    return bool(key and key.strip())


def log_llm_startup_status():
    logger = logging.getLogger("API.Startup")
    model = (
        (os.getenv("OTHELLO_MODEL") or "").strip()
        or (os.getenv("FELLO_MODEL") or "").strip()
        or (os.getenv("OPENAI_MODEL") or "").strip()
        or "gpt-4o-mini"
    )
    key_present = _openai_key_present()
    logger.info("[Startup] OPENAI_API_KEY_present=%s model=%s", key_present, model)


def log_library_versions():
    """Log library versions for diagnostics (no secrets)."""
    logger = logging.getLogger("API.Startup")
    try:
        logger.info(
            "LibraryVersions: openai=%s httpx=%s",
            getattr(openai, "__version__", "?"),
            getattr(httpx, "__version__", "?"),
        )
    except Exception as exc:
        logger.warning("LibraryVersions: failed to log versions: %s", exc)


def get_agent_components():
    global _agent_components, _agent_init_error, _agent_init_error_message
    if _agent_components is not None:
        return _agent_components

    logger = logging.getLogger("API.AgentInit")
    try:
        if not is_openai_configured():
            raise ValueError("Missing OPENAI_API_KEY")

        from core.architect_brain import Architect
        from core.llm_wrapper import AsyncLLMWrapper
        from core.input_router import InputRouter
        from core.othello_engine import OthelloEngine
        from utils.postprocessor import postprocess_and_save
        from db import plan_repository
        from db import goal_task_history_repository
        from db.db_goal_manager import DbGoalManager
        from core.memory_manager import MemoryManager
        from db import insights_repository
        from insights_service import extract_insights_from_exchange
        from db.goal_events_repository import ensure_goal_events_table

        model = (
            (os.getenv("OTHELLO_MODEL") or "").strip()
            or (os.getenv("FELLO_MODEL") or "").strip()
            or (os.getenv("OPENAI_MODEL") or "").strip()
            or "gpt-4o-mini"
        )

        openai_model = AsyncLLMWrapper(model=model)
        architect_agent = Architect(model=openai_model)
        architect_agent.goal_mgr = DbGoalManager()
        architect_agent.memory_mgr = MemoryManager()
        othello_engine = OthelloEngine(
            goal_manager=architect_agent.goal_mgr,
            memory_manager=architect_agent.memory_mgr,
        )
        _agent_components = {
            'architect_agent': architect_agent,
            'othello_engine': othello_engine,
            'insights_repository': insights_repository,
            'plan_repository': plan_repository,
            'goal_task_history_repository': goal_task_history_repository,
            'postprocess_and_save': postprocess_and_save,
            'extract_insights_from_exchange': extract_insights_from_exchange,
            'model': model,
        }
        try:
            ensure_goal_events_table()
        except Exception as exc:
            logger.warning("Goal events table ensure failed: %s", exc, exc_info=True)
        globals().update(
            architect_agent=architect_agent,
            othello_engine=othello_engine,
            insights_repository=insights_repository,
            plan_repository=plan_repository,
            goal_task_history_repository=goal_task_history_repository,
            postprocess_and_save=postprocess_and_save,
            extract_insights_from_exchange=extract_insights_from_exchange,
        )
        _agent_init_error = None
        _agent_init_error_message = None
        logger.info("[AgentInit] OPENAI_API_KEY_present=%s model=%s", _openai_key_present(), model)
        return _agent_components
    except Exception as e:
        _agent_components = None
        _agent_init_error = e
        _agent_init_error_message = str(e)
        logger.error("Agent initialization failed", exc_info=True)
        raise


log_llm_startup_status()
log_library_versions()

architect_agent = None
othello_engine = None
insights_repository = None
plan_repository = None
goal_task_history_repository = None
_suggestion_dismissals: Dict[str, set] = {}
postprocess_and_save = None
extract_insights_from_exchange = None


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
        "goal list",
        "goals list",
        "show goal list",
        "show goals list",
        "show goals",
        "view goals",
        "view my goals",
        "see my goals",
        "what goals do i have",
        "what goals have i",
    ]
    
    # Check if any explicit phrase is present
    return any(phrase in t for phrase in goal_list_phrases)


def is_help_request(text: str) -> bool:
    if not text:
        return False
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    normalized = normalized.rstrip(" ?")
    help_phrases = {
        "help",
        "/help",
        "capabilities",
        "what can you do",
        "what can you do for me",
    }
    return normalized in help_phrases


def is_today_plan_request(text: str) -> bool:
    if not text:
        return False
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    normalized = normalized.replace("?", "").replace("!", "").replace(".", "")
    phrases = [
        "whats todays plan",
        "what is todays plan",
        "what's todays plan",
        "what is today's plan",
        "what's today's plan",
        "what is the plan today",
        "what's the plan today",
        "show today plan",
        "show today's plan",
        "show me today's plan",
        "show me the plan today",
        "do i have any plans",
        "do i have any plan",
        "do i have a plan",
        "do i have plans",
        "any plans today",
        "what am i doing today",
        "what am i doing",
        "plan for today",
        "today plan",
        "my plan today",
    ]
    if any(phrase in normalized for phrase in phrases):
        return True
    if "plan" in normalized and "today" in normalized:
        return normalized.startswith(("what", "do i", "show", "any", "is there"))
    if normalized.startswith("do i have") and "plan" in normalized:
        return True
    return False


def _extract_weekday_plan_query(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    normalized = re.sub(r"\s+", " ", str(text).strip().lower())
    normalized = normalized.replace("?", "").replace("!", "").replace(".", "")
    if "routine" in normalized or "habit" in normalized:
        return None
    plan_cues = (
        "plan",
        "schedule",
        "agenda",
        "what am i doing",
        "what's on",
        "whats on",
        "what is on",
        "what's my plan",
        "what is my plan",
    )
    if not any(cue in normalized for cue in plan_cues):
        return None
    match = re.search(
        r"\b(mon(day)?|tue(sday)?|wed(nesday)?|thu(rsday)?|fri(day)?|sat(urday)?|sun(day)?)\b",
        normalized,
    )
    if not match:
        return None
    token = match.group(1).lower()
    weekday_map = {
        "mon": "mon",
        "monday": "mon",
        "tue": "tue",
        "tues": "tue",
        "tuesday": "tue",
        "wed": "wed",
        "weds": "wed",
        "wednesday": "wed",
        "thu": "thu",
        "thur": "thu",
        "thurs": "thu",
        "thursday": "thu",
        "fri": "fri",
        "friday": "fri",
        "sat": "sat",
        "saturday": "sat",
        "sun": "sun",
        "sunday": "sun",
    }
    return weekday_map.get(token)


def _resolve_weekday_to_ymd(
    *,
    weekday_key: str,
    timezone_name: Optional[str],
    logger: logging.Logger,
) -> str:
    weekday_indexes = {
        "mon": 0,
        "tue": 1,
        "wed": 2,
        "thu": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6,
    }
    target_idx = weekday_indexes.get(weekday_key)
    if target_idx is None:
        return datetime.now(timezone.utc).date().isoformat()
    resolved_timezone = _normalize_timezone(timezone_name, logger)
    local_today = datetime.now(ZoneInfo(resolved_timezone)).date()
    days_ahead = (target_idx - local_today.weekday()) % 7
    target_date = local_today + timedelta(days=days_ahead)
    return target_date.isoformat()


def _weekday_label(weekday_key: str) -> str:
    labels = {
        "mon": "Monday",
        "tue": "Tuesday",
        "wed": "Wednesday",
        "thu": "Thursday",
        "fri": "Friday",
        "sat": "Saturday",
        "sun": "Sunday",
    }
    return labels.get(weekday_key, weekday_key.title())


def _load_plan_for_date_peek(
    *,
    user_id: str,
    plan_date: date,
    comps: Dict[str, Any],
) -> Dict[str, Any]:
    plan_repo = comps["plan_repository"]
    plan_row = plan_repo.get_plan_by_date(user_id, plan_date)
    if not plan_row:
        return {
            "date": plan_date.isoformat(),
            "sections": {"routines": [], "goal_tasks": [], "optional": []},
            "_plan_source": "empty_stub",
        }
    items = plan_repo.get_plan_items(plan_row["id"])
    sections = {"routines": [], "goal_tasks": [], "optional": []}
    for item in items:
        kind = item.get("type")
        source_kind = item.get("source_kind")
        if kind in ("routine", "routine_step") or source_kind == "routine":
            sections["routines"].append(item)
        elif kind == "goal_task" or source_kind == "goal_task":
            sections["goal_tasks"].append(item)
        else:
            sections["optional"].append(item)
    return {
        "date": plan_date.isoformat(),
        "sections": sections,
        "_plan_source": "peek",
    }


def _format_day_plan_reply(plan: Dict[str, Any], plan_date: date, weekday_label: str) -> str:
    sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
    items: List[str] = []
    for section_key in ("routines", "goal_tasks", "optional"):
        for item in sections.get(section_key, []) or []:
            label = (
                item.get("label")
                or item.get("name")
                or item.get("title")
                or (item.get("metadata") or {}).get("label")
            )
            if label:
                items.append(str(label))
    if not items:
        return f"No plan items for {weekday_label} yet."
    headline = f"Plan for {weekday_label} ({plan_date.isoformat()}):"
    lines = [headline]
    for label in items[:6]:
        lines.append(f"- {label}")
    if len(items) > 6:
        lines.append(f"...and {len(items) - 6} more.")
    return "\n".join(lines)


def _format_today_plan_reply(plan: Dict[str, Any], brief: Optional[Dict[str, Any]], plan_date: date) -> str:
    sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
    items: List[str] = []
    for section_key in ("routines", "goal_tasks", "optional"):
        for item in sections.get(section_key, []) or []:
            label = (
                item.get("label")
                or item.get("name")
                or item.get("title")
                or (item.get("metadata") or {}).get("label")
            )
            if label:
                items.append(str(label))
    if not items:
        return "No plan items for today yet. If you want, I can build a plan."
    headline = ""
    if isinstance(brief, dict):
        headline = (brief.get("headline") or "").strip()
    if not headline:
        headline = f"Plan for {plan_date.isoformat()}"
    lines = [headline, "", "Top items:"]
    for label in items[:6]:
        lines.append(f"- {label}")
    if len(items) > 6:
        lines.append(f"...and {len(items) - 6} more.")
    return "\n".join(lines)


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


def _parse_date_local(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def _serialize_datetime(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _normalize_timezone(value: Optional[str], logger: logging.Logger) -> str:
    timezone_name = (value or "UTC").strip() or "UTC"
    try:
        ZoneInfo(timezone_name)
        return timezone_name
    except Exception:
        logger.warning("API: invalid timezone '%s', defaulting to UTC", timezone_name)
        return "UTC"


def _resolve_plan_date_and_timezone(
    *,
    user_id: str,
    date_local: Optional[Any],
    timezone_name: Optional[str],
    logger: logging.Logger,
) -> tuple[date, str]:
    from db.plan_repository import get_user_timezone

    fallback_timezone = get_user_timezone(user_id)
    resolved_timezone = _normalize_timezone(timezone_name or fallback_timezone, logger)
    parsed_date = _parse_date_local(date_local)
    if parsed_date:
        return parsed_date, resolved_timezone
    local_now = datetime.now(ZoneInfo(resolved_timezone))
    return local_now.date(), resolved_timezone


def _suggestion_key(suggestion_type: str, source_client_message_id: str) -> str:
    return f"{suggestion_type}:{source_client_message_id}"


def _is_suggestion_dismissed(
    user_id: Optional[str],
    suggestion_type: str,
    source_client_message_id: str,
) -> bool:
    if not user_id or not suggestion_type or not source_client_message_id:
        return False
    key = _suggestion_key(suggestion_type, source_client_message_id)
    dismissed = _suggestion_dismissals.get(str(user_id), set())
    return key in dismissed


def _record_suggestion_dismissal(
    user_id: Optional[str],
    suggestion_type: str,
    source_client_message_id: str,
) -> bool:
    if not user_id or not suggestion_type or not source_client_message_id:
        return False
    key = _suggestion_key(suggestion_type, source_client_message_id)
    user_key = str(user_id)
    dismissed = _suggestion_dismissals.setdefault(user_key, set())
    dismissed.add(key)
    return True


def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
    from core.llm_wrapper import LLMWrapper
    
    system_prompt = (
        "You are a goal extraction engine. Extract goal details from the user's request into a JSON object.\n"
        "Required keys:\n"
        "- title: string (concise goal title)\n"
        "- target_days: integer or null (number of days to achieve)\n"
        "- steps: array of strings (actionable steps)\n"
        "- body: string or null (additional context/description)\n"
        "Return ONLY valid JSON."
    )
    
    try:
        llm = LLMWrapper()
        response = llm.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logging.error(f"Failed to generate goal draft payload: {e}")
        # Fallback
        return {
            "title": _extract_goal_title_suggestion(user_input) or "New Goal",
            "target_days": 7,
            "steps": [],
            "body": user_input
        }


def _apply_goal_draft_deterministic_edit(current_payload: Dict[str, Any], user_instruction: str) -> Tuple[Dict[str, Any], bool, str]:
    """
    Attempts to apply deterministic edits to the draft payload based on user instruction.
    Returns (updated_payload, handled, reply_suffix)
    """
    updated_payload = current_payload.copy()
    handled = False
    reply_suffix = ""
    
    # A) Title Change
    # "change title to X", "update title to X", "set title to X"
    title_match = re.search(r"\b(change|update|set)\b.*\btitle\b.*\bto\b\s+(.+)", user_instruction, re.IGNORECASE)
    if title_match:
        new_title = title_match.group(2).strip()
        # Remove quotes if present
        if (new_title.startswith('"') and new_title.endswith('"')) or (new_title.startswith("'") and new_title.endswith("'")):
            new_title = new_title[1:-1]
            
        updated_payload["title"] = new_title
        return updated_payload, True, f"Updated title to '{new_title}'."

    # B) Target Days Change
    # "change target to 10 days", "set target days to 10", "make it 14 days"
    target_match = re.search(r"\b(change|update|set|make)\b.*\b(target|days)\b.*?\b(\d+)\b", user_instruction, re.IGNORECASE)
    if target_match:
        days = int(target_match.group(3))
        updated_payload["target_days"] = days
        return updated_payload, True, f"Updated target to {days} days."

    # C) Step Change
    # "change step 2 to X", "update step 3 to X", "set step 1 to X"
    step_match = re.search(r"\b(change|update|set)\b.*\bstep\b\s+(\d+)\b.*\bto\b\s+(.+)", user_instruction, re.IGNORECASE)
    if step_match:
        step_idx = int(step_match.group(2)) - 1 # 0-based
        new_step_text = step_match.group(3).strip()
        # Remove quotes
        if (new_step_text.startswith('"') and new_step_text.endswith('"')) or (new_step_text.startswith("'") and new_step_text.endswith("'")):
            new_step_text = new_step_text[1:-1]
            
        steps = updated_payload.get("steps", [])
        if not isinstance(steps, list):
            steps = []
            
        # Sanitize existing steps (remove blanks)
        steps = [str(s).strip() for s in steps if str(s).strip()]
        
        # Logic:
        # 1. If steps empty, allow only step 1.
        # 2. If steps exist, allow 1..len(steps) (edit) OR len(steps)+1 (append).
        # 3. Reject gaps.
        
        current_count = len(steps)
        target_idx = step_idx
        
        if current_count == 0:
            if target_idx == 0:
                # Set first step
                steps = [new_step_text]
                updated_payload["steps"] = steps
                return updated_payload, True, "Added step 1."
            else:
                return current_payload, True, "No steps exist yet. Generate steps first, or set step 1 before step 2."
        else:
            if target_idx < current_count:
                # Edit existing
                steps[target_idx] = new_step_text
                updated_payload["steps"] = steps
                return updated_payload, True, f"Updated step {target_idx + 1}."
            elif target_idx == current_count:
                # Append next
                steps.append(new_step_text)
                updated_payload["steps"] = steps
                return updated_payload, True, f"Added step {target_idx + 1}."
            else:
                # Gap
                return current_payload, True, f"You currently have {current_count} steps. Add step {current_count + 1} next (or generate steps)."

    return current_payload, False, ""


def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction: str) -> Dict[str, Any]:
    from core.llm_wrapper import LLMWrapper
    
    system_prompt = (
        "You are a goal editing engine. Update the existing goal draft JSON based on the user's instruction.\n"
        "Return the FULL updated JSON object with keys: title, target_days, steps, body.\n"
        "Do not lose existing information unless instructed to change it.\n"
        "Crucial: If the user provides details, answers, or context (e.g., 'It is for my health'), update the 'body' string with this intent info.\n"
        "Do NOT set step 1 unless explicitly asked to add a step.\n"
        "Return ONLY valid JSON."
    )
    
    try:
        llm = LLMWrapper()
        response = llm.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Current Payload: {json.dumps(current_payload)}\nInstruction: {user_instruction}"}
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        updated_payload = json.loads(content)
        
        # Hardening: Prevent regressions
        norm_input = user_instruction.lower()
        
        # If title not mentioned, restore original
        if "title" not in norm_input and current_payload.get("title"):
            updated_payload["title"] = current_payload["title"]
            
        # If target/days not mentioned, restore original
        if "target" not in norm_input and "days" not in norm_input and current_payload.get("target_days"):
            updated_payload["target_days"] = current_payload["target_days"]
            
        # If steps not mentioned, restore original steps if new ones are empty/missing
        if "step" not in norm_input:
             new_steps = updated_payload.get("steps")
             if not new_steps or not isinstance(new_steps, list):
                 updated_payload["steps"] = current_payload.get("steps", [])

        return updated_payload
    except Exception as e:
        logging.error(f"Failed to patch goal draft payload: {e}")
        return current_payload


def _generate_draft_steps_payload(current_payload: Dict[str, Any]) -> Dict[str, Any]:
    from core.llm_wrapper import LLMWrapper
    
    system_prompt = (
        "You are a goal planning engine. Generate a list of concrete, actionable steps for the user's goal.\n"
        "Return the FULL updated JSON object with keys: title, target_days, steps, body.\n"
        "The 'steps' key should be a list of strings.\n"
        "Keep the existing title, target_days, and body unless they are missing.\n"
        "Return ONLY valid JSON."
    )
    
    try:
        llm = LLMWrapper()
        response = llm.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Current Payload: {json.dumps(current_payload)}\nTask: Generate 3-5 actionable steps for this goal."}
            ],
            temperature=0.2,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logging.error(f"Failed to generate draft steps: {e}")
        return current_payload


def _extract_goal_title_suggestion(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    cleaned = re.sub(
        r"^(my goal is|my goal|next goal|goal)\s*[:\-]?\s*",
        "",
        raw,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^(i want to|i'm going to|im going to|we need to|i will|we will)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    if not cleaned:
        cleaned = raw
    cleaned = cleaned.strip()
    if len(cleaned) > 60:
        cleaned = cleaned[:60].strip()
    return cleaned


def _detect_goal_intent_suggestion(
    text: str,
    client_message_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not text or not client_message_id:
        return None
    raw = str(text).strip()
    if not raw or raw.startswith("__"):
        return None
    if is_goal_list_request(raw):
        return None
    if parse_goal_selection_request(raw) is not None:
        return None

    t = raw.lower()
    starts = (
        "next goal",
        "my goal",
        "i want to",
        "i'm going to",
        "im going to",
        "we need to",
        "i will",
        "we will",
    )
    intent_phrases = (
        "want to",
        "going to",
        "plan to",
        "need to",
        "aim to",
    )
    action_verbs = (
        "build",
        "create",
        "implement",
        "launch",
        "learn",
        "become",
    )

    score = 0.0
    if any(t.startswith(prefix) for prefix in starts):
        score += 0.6
    if any(phrase in t for phrase in intent_phrases):
        score += 0.25
    if any(re.search(rf"\\b{verb}\\b", t) for verb in action_verbs):
        score += 0.25
    if "goal" in t:
        score += 0.2
    score = min(score, 1.0)

    if score < 0.55:
        return None

    title_suggestion = _extract_goal_title_suggestion(raw)
    return {
        "type": "goal_intent",
        "source_client_message_id": client_message_id,
        "confidence": round(score, 2),
        "title_suggestion": title_suggestion,
        "body_suggestion": raw,
    }


def _has_schedule_cues(text: Optional[str]) -> bool:
    if not text:
        return False
    lower = str(text).lower()
    day_match = re.search(
        r"\b(mon(day)?|tue(sday)?|wed(nesday)?|thu(rsday)?|fri(day)?|sat(urday)?|sun(day)?)\b",
        lower,
    )
    if not day_match:
        return False
    time_match = re.search(
        r"\b([01]?\d|2[0-3]):[0-5]\d\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(o\W?clock)\b|\bmorning\b|\bevening\b",
        lower,
    )
    return bool(time_match)


def _get_goal_intent_suggestion(
    user_input: str,
    client_message_id: Optional[str],
    user_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    if _has_schedule_cues(user_input):
        return None
    if _extract_weekday_plan_query(user_input):
        return None
    suggestion = _detect_goal_intent_suggestion(user_input, client_message_id)
    if not suggestion:
        return None
    if _is_suggestion_dismissed(user_id, suggestion["type"], client_message_id or ""):
        return None
    return suggestion


def _build_goal_intent_fallback(
    user_input: str,
    client_message_id: Optional[str],
    user_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not user_input or not client_message_id:
        return None
    raw = str(user_input).strip()
    if not raw:
        return None
    if _is_suggestion_dismissed(user_id, "goal_intent", client_message_id):
        return None
    title_suggestion = _extract_goal_title_suggestion(raw)
    return {
        "type": "goal_intent",
        "source_client_message_id": client_message_id,
        "confidence": 0.45,
        "title_suggestion": title_suggestion,
        "body_suggestion": raw,
    }


def _normalize_reply_text(text: str) -> str:
    raw = (text or "").strip().lower()
    normalized = re.sub(r"\s+", " ", raw)
    return re.sub(r"[.!?]+$", "", normalized).strip()


def _is_placeholder_reply(text: str) -> bool:
    normalized = _normalize_reply_text(text)
    if normalized in {
        "it isn't saved yet",
        "it isnt saved yet",
        "it is not saved yet",
        "not saved yet",
    }:
        return True
    return any(
        phrase in normalized
        for phrase in (
            "isn't saved yet",
            "isnt saved yet",
            "not saved yet",
        )
    )


def _clear_day_plan_cache(user_id: Optional[str], logger: logging.Logger) -> int:
    uid = str(user_id or "").strip()
    if not uid:
        return 0
    safe_uid = re.sub(r"[^A-Za-z0-9_.-]+", "_", uid)
    plan_dir = Path(__file__).resolve().parent / "data" / "day_plans"
    if not plan_dir.exists():
        return 0
    removed = 0
    pattern = f"plan_{safe_uid}_*.json"
    for path in plan_dir.glob(pattern):
        try:
            path.unlink()
            removed += 1
        except Exception as exc:
            logger.warning(
                "API: failed to remove plan cache file=%s error=%s",
                path,
                type(exc).__name__,
            )
    return removed


def _load_companion_context(
    user_id: Optional[str],
    logger: logging.Logger,
    *,
    channel: str = "companion",
    max_turns: int = CHAT_CONTEXT_TURNS,
    max_chars: int = CHAT_CONTEXT_MAX_CHARS,
    conversation_id: Optional[int] = None,
) -> List[Dict[str, str]]:
    uid = str(user_id or "").strip()
    if not uid:
        return []
    channel_name = str(channel or "companion").strip().lower()
    if channel_name not in {"companion", "planner"}:
        channel_name = "companion"
    limit = max(0, int(max_turns) * 2)
    if limit <= 0:
        return []
    try:
        from db.messages_repository import list_recent_messages, list_messages_for_session
        if conversation_id:
            rows = list_messages_for_session(uid, conversation_id, limit=limit, channel=channel_name)
        else:
            rows = list_recent_messages(uid, limit=limit, channel=channel_name)
    except Exception as exc:
        logger.warning(
            "API: failed to load companion history user_id=%s error=%s",
            uid,
            type(exc).__name__,
            exc_info=True,
        )
        return []
    if not rows:
        return []
    messages: List[Dict[str, str]] = []
    total_chars = 0
    for row in reversed(rows):
        content = (row.get("transcript") or "").strip()
        if not content:
            continue
        source = (row.get("source") or "").strip().lower()
        role = "assistant" if source == "assistant" else "user"
        if total_chars and total_chars + len(content) > max_chars:
            break
        if len(content) > max_chars:
            content = content[:max_chars]
        messages.append({"role": role, "content": content})
        total_chars += len(content)
        if len(messages) >= limit:
            break
    messages.reverse()
    if messages:
        logger.debug(
            "API: loaded history messages=%s chars=%s channel=%s",
            len(messages),
            total_chars,
            channel_name,
        )
    return messages


def should_offer_goal_intent(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    if not t:
        return False

    # Question check
    if "?" in t:
        return False
    question_words = ("what", "why", "how", "when", "where", "who", "can", "should", "do", "is", "are")
    if any(t.startswith(w + " ") or t == w for w in question_words):
        return False

    # Routine signals
    routine_signals = (
        "every day", "each day", "daily", "weekly", "remind me", "alarm",
        "routine", "habit", "meet at"
    )
    if any(s in t for s in routine_signals):
        return False

    # Time signals
    if re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", t):
        return False
    if re.search(r"\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b", t):
        return False
    if re.search(r"\b(at|around|by)\s+([1-9]|1[0-2])\b", t):
        return False

    # Explicit goal phrasing
    explicit_phrases = (
        "goal:", "my goal is", "i want to", "i am going to", "i'm going to",
        "i will", "new goal", "working towards", "need to achieve"
    )
    has_explicit = any(p in t for p in explicit_phrases)

    # Return True only when explicit goal phrasing is present AND none of the disqualifiers matched.
    return has_explicit


def _goal_intent_prompt(active_goal_id: Optional[int]) -> str:
    if active_goal_id is not None:
        return "Want this saved as a goal, added to your focused goal, or broken into steps?"
    return "Want this saved as a goal or broken into steps?"


def _llm_unavailable_prompt(active_goal_id: Optional[int]) -> str:
    return (
        "I'm having trouble reaching the assistant right now. "
        + _goal_intent_prompt(active_goal_id)
    )

def _find_goal_text_in_context(companion_context: List[Dict[str, Any]]) -> Optional[str]:
    if not companion_context:
        return None
    goal_text = None
    for msg in reversed(companion_context):
        if msg.get("role") != "assistant":
            continue
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        match = re.search(r"goal:\s*(.+)", content, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if candidate:
                goal_text = candidate
                break
    fallback_text = None
    if not goal_text:
        for msg in reversed(companion_context):
            if msg.get("role") != "user":
                continue
            text = (msg.get("content") or "").strip()
            if not text:
                continue
            norm = re.sub(r"\s+", " ", text.lower()).strip()
            if re.match(r"^(hi|hey|hello)\b", norm) and not re.search(
                r"\b(goal|want|build|start|today)\b",
                norm,
            ):
                continue
            if re.search(r"\bstep(s)?\b", norm) or "break" in norm:
                continue
            if "save" in norm:
                continue
            goal_language = re.search(r"\bgoal(s)?\b", norm) is not None
            goal_like = False
            if norm.startswith(("i want to", "my goal is", "today", "build", "start")):
                goal_like = True
            if goal_language and len(norm) > 12:
                goal_like = True
            if goal_language and not goal_like:
                continue
            if len(text) <= 12:
                continue
            if goal_like:
                goal_text = text
                break
            if fallback_text is None:
                fallback_text = text
        if not goal_text:
            goal_text = fallback_text
    return goal_text

def _format_goal_questions_reply(goal_text: str, questions: Optional[List[str]] = None) -> str:
    lines = [
        f"Ok - goal: {goal_text}",
        "Before I draft steps, a few quick questions:",
    ]
    if questions:
        for idx, q_text in enumerate(questions, start=1):
            q_text = (q_text or "").strip()
            if q_text:
                lines.append(f"{idx}) {q_text}")
        return "\n".join(lines)
    lines.extend(["1) What time window or cadence should this fit?",
                  "2) What does success look like for you?",
                  "3) Any constraints or must-avoid items?",
                  "4) What's the hardest part?"])
    return "\n".join(lines)

def _generate_goal_intake_questions(
    *,
    goal_text: Optional[str],
    goal_title: Optional[str],
    goal_description: Optional[str],
    user_message: str,
    recent_messages: Optional[List[Dict[str, Any]]],
    user_id: Optional[str],
    request_id: str,
    logger: logging.Logger,
) -> Optional[Dict[str, Any]]:
    fallback_context = (
        "Share one line of context about your goal (tools, constraints, or timeline), "
        "and I'll tailor the questions."
    )
    if not (goal_text or goal_title or goal_description):
        return {"need_more_context": True, "context_request": fallback_context, "questions": []}
    if not is_openai_configured():
        return None
    recent_context = "\n".join(
        f"{msg.get('role')}: {msg.get('content')}"
        for msg in (recent_messages or [])[-6:]
        if msg.get("role") and msg.get("content")
    )
    prompt = (
        "Generate goal-specific intake questions. Return JSON only with "
        '{"need_more_context":bool,"context_request":string|null,'
        '"questions":[{"q":string,"why":string,"answer_type":"one_line"|"time_window"|"choice"|"yes_no"|"number"}]}. '
        "If context is insufficient, set need_more_context=true and provide a single-line context_request. "
        "Otherwise ask 4-6 questions tied to the goal details and avoid repeating recent questions.\n"
        f"Goal title: {goal_title or ''}\n"
        f"Goal description: {goal_description or ''}\n"
        f"Goal text: {goal_text or ''}\n"
        f"User request: {user_message or ''}\n"
        f"Recent context:\n{recent_context}\n"
    )
    loop = None
    try:
        comps = get_agent_components()
        architect = comps["architect_agent"]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply_text, _agent_status = loop.run_until_complete(
            asyncio.wait_for(
                architect.plan_and_execute(
                    prompt,
                    user_id=user_id,
                    recent_messages=recent_messages,
                ),
                timeout=30.0
            )
        )
    except Exception as exc:
        logger.error(
            "API: goal intake questions failed request_id=%s",
            request_id,
            exc_info=True,
        )
        return None
    finally:
        if loop is not None:
            try:
                loop.close()
            except Exception:
                logger.debug("API: event loop close failed but continuing")
    raw_reply = (reply_text or "").strip()
    payload = None
    if raw_reply:
        try:
            payload = json.loads(raw_reply)
        except Exception:
            start = raw_reply.find("{")
            end = raw_reply.rfind("}")
            if start != -1 and end > start:
                try:
                    payload = json.loads(raw_reply[start:end + 1])
                except Exception:
                    payload = None
    if not isinstance(payload, dict):
        return None
    need_more_context = bool(payload.get("need_more_context"))
    if need_more_context:
        context_request = (payload.get("context_request") or "").strip()
        if not context_request:
            context_request = fallback_context
        elif "question" not in context_request.lower():
            context_request = f"{context_request.rstrip('.')} I'll tailor the questions."
        return {"need_more_context": True, "context_request": context_request, "questions": []}
    raw_questions = payload.get("questions") if isinstance(payload.get("questions"), list) else []
    questions = []
    for entry in raw_questions:
        if not isinstance(entry, dict):
            continue
        q_text = (entry.get("q") or "").strip()
        if len(q_text) >= 6:
            questions.append(q_text)
    if len(questions) < 4:
        return None
    recent_assistant = " ".join(
        (msg.get("content") or "") for msg in (recent_messages or []) if msg.get("role") == "assistant"
    )
    if recent_assistant:
        recent_norm = recent_assistant.lower()
        if recent_norm and all(q.lower() in recent_norm for q in questions):
            return {"need_more_context": True, "context_request": fallback_context, "questions": []}
    return {"need_more_context": False, "context_request": None, "questions": questions[:6]}

def _attach_goal_intent_suggestion(
    response: Dict[str, Any],
    *,
    user_input: str,
    client_message_id: Optional[str],
    user_id: Optional[str],
    request_id: str,
    logger: logging.Logger,
    active_goal_id: Optional[int] = None,
    suggestion: Optional[Dict[str, Any]] = None,
) -> bool:
    if suggestion is None:
        suggestion = _get_goal_intent_suggestion(user_input, client_message_id, user_id)
    if not suggestion:
        return False
    suggestion_id = suggestion.get("suggestion_id") or suggestion.get("id")
    if suggestion_id is None and user_id:
        title = suggestion.get("title_suggestion") or _extract_goal_title_suggestion(user_input)
        body = suggestion.get("body_suggestion") or (user_input or "").strip()
        payload = {
            "title": title,
            "body": body,
            "description": body,
            "confidence": suggestion.get("confidence"),
        }
        provenance = {
            "source": "api_message_goal_intent",
            "request_id": request_id,
            "client_message_id": client_message_id,
        }
        try:
            created = suggestions_repository.create_suggestion(
                user_id=user_id,
                kind="goal",
                payload=payload,
                provenance=provenance,
            )
            if isinstance(created, dict):
                suggestion_id = created.get("id")
        except Exception:
            logger.warning(
                "API: goal suggestion create failed request_id=%s client_message_id=%s",
                request_id,
                client_message_id,
                exc_info=True,
            )
    if suggestion_id is not None:
        suggestion = dict(suggestion)
        suggestion["suggestion_id"] = suggestion_id
        suggestion.setdefault("kind", "goal")

        # Draft Focus: Return draft context and payload
        # Payload normalization
        raw_payload = suggestion.get("payload", {})
        if isinstance(raw_payload, str):
            try:
                import json
                raw_payload = json.loads(raw_payload)
            except Exception:
                raw_payload = {}
        if not isinstance(raw_payload, dict):
            raw_payload = {}

        response["draft_context"] = {
            "draft_id": suggestion_id,
            "draft_type": "goal",
            "source_message_id": suggestion_id  # Use stable ID for UI highlight
        }
        response["draft_payload"] = {
            "title": suggestion.get("title_suggestion") or raw_payload.get("title"),
            "target_days": raw_payload.get("target_days"),
            "steps": raw_payload.get("steps"),
            "body": suggestion.get("body_suggestion") or raw_payload.get("body")
        }

    meta = response.setdefault("meta", {})
    suggestions = meta.setdefault("suggestions", [])
    suggestions.append(suggestion)
    actions = ["save_goal", "edit", "dismiss"]
    if active_goal_id is not None:
        actions.append("add_to_focused_goal")
    meta["goal_intent_suggestion"] = {
        "message_id": client_message_id,
        "suggested_goal_text": suggestion.get("body_suggestion") or (user_input or "").strip(),
        "confidence": suggestion.get("confidence"),
        "actions": actions,
    }
    logger.info(
        "API: suggestion goal_intent request_id=%s client_message_id=%s confidence=%s",
        request_id,
        client_message_id,
        suggestion.get("confidence"),
    )
    return True


def _extract_hour_hint(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"\b([1-9]|1[0-2])\b", str(text))
    if not match:
        return None
    try:
        return int(match.group(1))
    except (TypeError, ValueError):
        return None


def _routine_status_from_fields(
    draft: Dict[str, Any],
    missing_fields: List[str],
    ambiguous_fields: List[str],
) -> str:
    if missing_fields or ambiguous_fields:
        return "incomplete"
    if not draft.get("title"):
        return "incomplete"
    if not draft.get("time_local"):
        return "incomplete"
    return "complete"


def _build_routine_clarifying_question(
    draft: Dict[str, Any],
    missing_fields: List[str],
    ambiguous_fields: List[str],
) -> Optional[str]:
    if "time_ampm" in missing_fields or "time_local" in ambiguous_fields:
        time_text = draft.get("time_text") or "that time"
        hour = _extract_hour_hint(time_text)
        if hour is None:
            return f"For {time_text}, do you mean am or pm?"
        return f"For {time_text} - do you mean {hour}am or {hour}pm?"
    return None


def _build_routine_suggestion_payload(
    draft: Dict[str, Any],
    missing_fields: List[str],
    ambiguous_fields: List[str],
) -> Dict[str, Any]:
    status = _routine_status_from_fields(draft, missing_fields, ambiguous_fields)
    clarifying_question = None
    if status == "incomplete":
        clarifying_question = _build_routine_clarifying_question(draft, missing_fields, ambiguous_fields)
    return {
        "draft": draft,
        "missing_fields": missing_fields,
        "ambiguous_fields": ambiguous_fields,
        "clarifying_question": clarifying_question,
        "status": status,
    }


def _parse_routine_time_answer(text: str, draft: Dict[str, Any]) -> Optional[str]:
    lower = (text or "").lower()
    match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return f"{hour:02d}:{minute:02d}"
    match = re.search(r"\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b", lower)
    if match:
        hour = int(match.group(1))
        ampm_raw = match.group(2).replace(".", "")
        is_pm = ampm_raw.startswith("p")
        if is_pm and hour != 12:
            hour += 12
        if not is_pm and hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    hour_hint = _extract_hour_hint(draft.get("time_text"))
    if "morning" in lower:
        hour = hour_hint or 7
        if hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    if "evening" in lower:
        hour = hour_hint or 7
        if hour != 12:
            hour += 12
        return f"{hour:02d}:00"
    if "am" in lower or "pm" in lower:
        hour = _extract_hour_hint(lower) or hour_hint
        if hour is None:
            return None
        is_pm = "pm" in lower or "p.m" in lower
        if is_pm and hour != 12:
            hour += 12
        if not is_pm and hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    return None


def _build_routine_patch_payload(text: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not text or not isinstance(payload, dict):
        return None
    lower = text.lower()
    draft = dict(payload.get("draft") or {})
    if not isinstance(draft, dict):
        return None
    missing_fields = list(payload.get("missing_fields") or [])
    ambiguous_fields = list(payload.get("ambiguous_fields") or [])
    updates: Dict[str, Any] = {}
    time_local = _parse_routine_time_answer(text, draft)
    if time_local:
        updates["time_local"] = time_local
        missing_fields = [f for f in missing_fields if f != "time_ampm"]
        ambiguous_fields = [f for f in ambiguous_fields if f != "time_local"]
    days = _extract_days_of_week(text)
    if not days and re.search(r"\bmon(day)?s?\s*-\s*fri(day)?s?\b", lower):
        days = ["mon", "tue", "wed", "thu", "fri"]
    if days:
        updates["days_of_week"] = days

    duration_minutes = _parse_duration_minutes(text)
    if duration_minutes is not None:
        updates["duration_minutes"] = duration_minutes

    if not updates:
        return None
    draft.update(updates)
    return _build_routine_suggestion_payload(draft, missing_fields, ambiguous_fields)


def _format_routine_summary(draft: Dict[str, Any]) -> str:
    title = draft.get("title") or "Routine"
    days = draft.get("days_of_week") or []
    day_labels = {
        "mon": "Mon",
        "tue": "Tue",
        "wed": "Wed",
        "thu": "Thu",
        "fri": "Fri",
        "sat": "Sat",
        "sun": "Sun",
    }
    day_text = ", ".join(day_labels.get(day, day) for day in days) if days else "days TBD"
    time_text = draft.get("time_local") or draft.get("time_text") or "unspecified time"
    return f"Routine draft ready: {title} on {day_text} at {time_text}. Confirm to save."


def _normalize_goal_title(title: str) -> str:
    if not isinstance(title, str):
        title = str(title or "")
    return " ".join(title.strip().split()).lower()


def parse_goal_selection_request(text: str) -> Optional[int]:
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


def _parse_focused_goal_edit_command(text: str) -> Optional[Dict[str, str]]:
    raw = (text or "").strip()
    if not raw:
        return None
    match = re.match(
        r"^(append(?:\s+to)?\s+goal|update\s+goal):\s*(.*)$",
        raw,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    command = match.group(1).lower()
    mode = "append" if command.startswith("append") else "update"
    payload = (match.group(2) or "").strip()
    return {"mode": mode, "payload": payload}


def _detect_goal_edit_arm(data: Dict[str, Any], text: str) -> Optional[str]:
    key_candidates = (
        "goal_action",
        "goalAction",
        "action",
        "intent",
        "ui_action",
        "uiAction",
    )
    for key in key_candidates:
        value = data.get(key)
        if not isinstance(value, str):
            continue
        normalized = value.strip().lower()
        if key in ("goal_action", "goalAction"):
            if "append" in normalized:
                return "append"
            if "update" in normalized or "edit" in normalized:
                return "update"
        if "goal" in normalized:
            if "append" in normalized:
                return "append"
            if "update" in normalized or "edit" in normalized:
                return "update"
    normalized_text = (text or "").strip().lower()
    if normalized_text in ("update goal", "update goal with that info", "update goal with that info."):
        return "update"
    if normalized_text in ("append to goal", "append to goal.", "append goal", "append goal."):
        return "append"
    return None


_PLAN_ACTION_VERBS = (
    "build",
    "create",
    "implement",
    "design",
    "draft",
    "write",
    "review",
    "test",
    "deploy",
    "launch",
    "set up",
    "setup",
    "configure",
    "add",
    "update",
    "fix",
    "refactor",
    "research",
    "analyze",
    "document",
    "plan",
    "prepare",
    "define",
    "outline",
    "ship",
    "integrate",
    "install",
    "migrate",
    "monitor",
    "measure",
    "improve",
    "optimize",
    "schedule",
    "notify",
    "clean",
    "merge",
    "decide",
    "collect",
    "run",
)
_PLAN_ACTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(verb) for verb in _PLAN_ACTION_VERBS) + r")\b",
    re.IGNORECASE,
)


def _strip_outer_bold(text: str) -> Dict[str, Any]:
    trimmed = (text or "").strip()
    if len(trimmed) >= 4:
        if trimmed.startswith("**") and trimmed.endswith("**"):
            inner = trimmed[2:-2].strip()
            if inner:
                return {"text": inner, "bold": True}
        if trimmed.startswith("__") and trimmed.endswith("__"):
            inner = trimmed[2:-2].strip()
            if inner:
                return {"text": inner, "bold": True}
    return {"text": trimmed, "bold": False}


def _normalize_section_label(text: str) -> str:
    trimmed = (text or "").strip()
    if trimmed.endswith(":"):
        trimmed = trimmed[:-1].strip()
    return trimmed


def _looks_actionable(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower().strip()
    if lowered.startswith("to "):
        return True
    return bool(_PLAN_ACTION_RE.search(lowered))


def parse_structured_plan(plan_text: str) -> List[Dict[str, Any]]:
    """
    Parse markdown-ish plan text into structured steps.
    Returns a list of {"section": str|None, "text": str} in stable order.
    """
    items: List[Dict[str, Any]] = []
    if not isinstance(plan_text, str):
        return items
    current_section: Optional[str] = None

    def _extract_section_heading(line: str) -> Optional[str]:
        if not line:
            return None
        if re.match(r"^#{1,3}\s+\S", line):
            heading = re.sub(r"^#{1,3}\s+", "", line).strip()
            heading = _strip_outer_bold(heading)["text"]
            heading = _normalize_section_label(heading)
            return heading or None
        bold_info = _strip_outer_bold(line)
        if bold_info["bold"]:
            heading = _normalize_section_label(bold_info["text"])
            return heading or None
        numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if numbered:
            remainder = numbered.group(1).strip()
            bold_remainder = _strip_outer_bold(remainder)
            if bold_remainder["bold"]:
                heading = _normalize_section_label(bold_remainder["text"])
                return heading or None
            if not _looks_actionable(remainder):
                heading = _normalize_section_label(remainder)
                return heading or None
        if line.endswith(":") and len(line) <= 120:
            heading = _normalize_section_label(line)
            return heading or None
        return None

    def _extract_step_text(line: str) -> Optional[str]:
        if not line:
            return None
        bullet = re.match(r"^(?:[-*]|\u2022)\s+(.+)$", line)
        if bullet:
            text = (bullet.group(1) or "").strip()
            return text or None
        numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if numbered:
            remainder = (numbered.group(1) or "").strip()
            if _strip_outer_bold(remainder)["bold"]:
                return None
            if _looks_actionable(remainder):
                return remainder
            return None
        return None

    for raw_line in plan_text.splitlines():
        line = (raw_line or "").strip()
        if not line:
            continue
        if re.match(r"^[-*_]{3,}$", line):
            continue
        header = _extract_section_heading(line)
        if header:
            current_section = header
            continue
        step_text = _extract_step_text(line)
        if not step_text:
            continue
        items.append({"section": current_section, "text": step_text})

    return items


def _structured_steps_to_plan_steps(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    for idx, item in enumerate(items):
        text = (item.get("text") or "").strip()
        if not text:
            continue
        step = {
            "step_index": idx + 1,
            "description": text,
            "status": "pending",
        }
        section = (item.get("section") or "").strip()
        if section:
            step["section"] = section
        steps.append(step)
    return steps


def _parse_plan_text_to_steps(plan_text: str) -> List[Dict[str, Any]]:
    return _structured_steps_to_plan_steps(parse_structured_plan(plan_text))


def _parse_plan_text_with_log(plan_text: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    structured = parse_structured_plan(plan_text)
    steps = _structured_steps_to_plan_steps(structured)
    section_count = len({item.get("section") for item in structured if item.get("section")})
    logger.info(
        "API: plan parse summary sections=%s steps=%s",
        section_count,
        len(steps),
    )
    return steps


def _fallback_steps_from_text(source_text: str) -> List[Dict[str, Any]]:
    if not isinstance(source_text, str):
        return []
    text = source_text.strip()
    if not text:
        return []
    raw_steps: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^[-*•]\s+(.*)$", stripped)
        if match is None:
            match = re.match(r"^\d+[\).]\s+(.*)$", stripped)
        if match:
            candidate = match.group(1).strip()
            if candidate:
                raw_steps.append(candidate)
    if not raw_steps:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            candidate = sentence.strip()
            if candidate:
                raw_steps.append(candidate)
            if len(raw_steps) >= 5:
                break
    if not raw_steps and text:
        raw_steps = [text]
    return [
        {"step_index": idx, "description": candidate, "status": "pending"}
        for idx, candidate in enumerate(raw_steps[:5], start=1)
    ]


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow unauthenticated for health, login, me, and root
        if request.path in ["/api/health", "/api/auth/login", "/api/auth/me", "/"]:
            return f(*args, **kwargs)
        if not session.get("authed"):
            return api_error("AUTH_REQUIRED", "Authentication required", 401)
        if not session.get("user_id"):
            session.clear()
            return api_error(
                "AUTH_USER_MISSING",
                "Authenticated session missing user_id",
                401,
            )
        g.user_id = session.get("user_id")
        return f(*args, **kwargs)
    return decorated


def get_current_user_id() -> str:
    if not session.get("authed"):
        raise PermissionError("Authentication required")
    user_id = getattr(g, "user_id", None) or session.get("user_id")
    if not user_id:
        raise RuntimeError("Authenticated session missing user_id")
    return str(user_id)


def _ensure_users_table_exists() -> None:
    from db.database import execute_query
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            timezone TEXT NOT NULL DEFAULT 'Europe/London',
            night_prompt_time TIME DEFAULT '20:00',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def _beta_gate_check(user_id: str) -> Optional[Any]:
    user_id = str(user_id or "").strip()
    if not user_id:
        return api_error("BETA_GATE_FAILED", "Missing user identifier", 500)
    allowlist = _get_beta_allowlist()
    cap = _get_beta_user_cap()
    if allowlist and user_id not in allowlist:
        return api_error("BETA_ALLOWLIST_BLOCKED", "Beta access denied", 403)
    if cap > 0:
        logger = logging.getLogger("API.Auth")
        try:
            _ensure_users_table_exists()
            from db.database import fetch_one
            existing = fetch_one("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
            if existing:
                return None
            count_row = fetch_one("SELECT COUNT(*) AS count FROM users")
            count = int((count_row or {}).get("count") or 0)
            # Only block new users when cap is reached.
            if count >= cap:
                return api_error("BETA_USER_CAP_REACHED", "Beta user cap reached", 403)
        except Exception as exc:
            logger.error("Beta gate check failed: %s", exc, exc_info=True)
            return api_error(
                "BETA_GATE_FAILED",
                "Failed to validate beta access",
                500,
                details=type(exc).__name__,
            )
    return None


def ensure_user_exists(user_id: str) -> None:
    user_id = str(user_id or "").strip()
    if not user_id:
        raise ValueError("user_id is required")
    from db.database import execute_query
    _ensure_users_table_exists()
    execute_query(
        """
        INSERT INTO users (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,),
    )


def _get_user_id_or_error():
    try:
        return get_current_user_id(), None
    except PermissionError:
        return None, api_error("AUTH_REQUIRED", "Authentication required", 401)
    except RuntimeError as exc:
        return None, api_error(
            "AUTH_USER_MISSING",
            "Authenticated session missing user_id",
            500,
            details=str(exc),
        )


def _ready_state() -> dict:
    """Return readiness info without exposing secrets."""
    key_present = _openai_key_present()
    agent_error = _agent_init_error
    agent_error_message = _agent_init_error_message
    ready = key_present and agent_error is None
    reason = None
    if not key_present:
        reason = "OPENAI_API_KEY missing or empty"
    elif agent_error is not None:
        reason = f"agent_init_error:{type(agent_error).__name__}"

    return {
        "ready": ready,
        "openai_key_present": key_present,
        "agent_init_error": type(agent_error).__name__ if agent_error else None,
        "agent_init_error_message": agent_error_message if agent_error_message else None,
        "reason": reason,
    }


# Always-on health endpoint for connection checks (does not check DB)
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"ok": True})


@app.route("/ready", methods=["GET"])
def ready_check():
    """Lightweight readiness probe focused on critical runtime config."""
    try:
        state = _ready_state()
        status = 200 if state["ready"] else 503
        body = {k: v for k, v in state.items() if v is not None}
        body["ok"] = bool(state["ready"])
        body["request_id"] = _get_request_id()
        if not state["ready"]:
            body["error_code"] = "NOT_READY"
            body["message"] = "Service not ready"
            body["details"] = state.get("reason")
        return jsonify(body), status
    except Exception as exc:
        logging.getLogger("API").error("ready_check failed: %s", exc, exc_info=True)
        return jsonify({
            "ok": False,
            "ready": False,
            "request_id": _get_request_id(),
            "error_code": "NOT_READY",
            "message": "Service not ready",
            "details": "ready_check_exception",
        }), 503


@app.route("/api/capabilities", methods=["GET"])
def api_capabilities():
    allowlist_enabled = bool(_get_beta_allowlist())
    cap_enabled = _get_beta_user_cap() > 0
    return jsonify({
        "beta_gate_enabled": allowlist_enabled or cap_enabled,
        "allowlist_enabled": allowlist_enabled,
        "cap_enabled": cap_enabled,
    })


def _v1_envelope(*, data: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None, status: int = 200):
    payload = {
        "ok": error is None,
        "request_id": _get_request_id(),
        "data": data,
        "error": error,
    }
    response = jsonify(payload)
    response.status_code = status
    return response


def _v1_error(code: str, message: str, status: int, details: Optional[Any] = None):
    return _v1_envelope(
        error={"code": code, "message": message, "details": details},
        status=status,
    )


def _v1_from_api_response(resp):
    status = getattr(resp, "status_code", 200)
    payload = resp.get_json(silent=True) if hasattr(resp, "get_json") else None
    if status >= 400:
        code = "ERROR"
        message = "Request failed"
        details = None
        if isinstance(payload, dict):
            code = payload.get("error_code") or code
            message = payload.get("message") or message
            details = payload.get("details")
        return _v1_error(code, message, status, details=details)
    return _v1_envelope(data=payload, status=status)


def _v1_get_user_id():
    try:
        return get_current_user_id(), None
    except PermissionError:
        return None, _v1_error("AUTH_REQUIRED", "Authentication required", 401)
    except RuntimeError as exc:
        return None, _v1_error(
            "AUTH_USER_MISSING",
            "Authenticated session missing user_id",
            500,
            details=str(exc),
        )


def _create_goal_plan_suggestion(
    *,
    user_id: str,
    payload: Dict[str, Any],
    provenance: Dict[str, Any],
) -> Dict[str, Any]:
    from db.suggestions_repository import create_suggestion
    return create_suggestion(
        user_id=user_id,
        kind="goal_plan",
        payload=payload,
        provenance=provenance,
    )


def _apply_suggestion_decisions(
    user_id: str,
    decisions: List[Dict[str, Any]],
    *,
    event_source: str = "confirm",
) -> List[Dict[str, Any]]:
    from db.suggestions_repository import get_suggestion, update_suggestion_status
    from db.goals_repository import create_goal, update_goal_meta
    from db.goal_events_repository import safe_append_goal_event
    from db.db_goal_manager import DbGoalManager
    from db.routines_repository import create_routine_from_draft
    from db.plan_repository import (
        get_next_plan_item_order_index,
        insert_plan_item_from_payload,
        upsert_plan_header,
    )

    results: List[Dict[str, Any]] = []
    goal_mgr = DbGoalManager()
    logger = logging.getLogger("API.Confirm")
    request_id = _get_request_id()
    for entry in decisions:
        if not isinstance(entry, dict):
            results.append({"ok": False, "error": "invalid_decision"})
            continue
        suggestion_id = entry.get("suggestion_id")
        action = (entry.get("action") or entry.get("decision") or "").strip().lower()
        reason = entry.get("reason")
        try:
            suggestion_id = int(suggestion_id)
        except (TypeError, ValueError):
            results.append({"ok": False, "error": "invalid_suggestion_id"})
            continue
        if action not in ("accept", "reject"):
            results.append({"ok": False, "error": "invalid_action", "suggestion_id": suggestion_id})
            continue

        suggestion = get_suggestion(user_id, suggestion_id)
        if not suggestion:
            results.append({"ok": False, "error": "suggestion_not_found", "suggestion_id": suggestion_id})
            continue

        kind = suggestion.get("kind")
        payload = suggestion.get("payload") or {}
        status = (suggestion.get("status") or "").strip().lower()
        if action == "accept" and status and status != "pending":
            results.append({
                "ok": True,
                "action": "noop",
                "suggestion": suggestion,
                "reason": "already_decided",
            })
            continue

        if action == "reject":
            updated = update_suggestion_status(user_id, suggestion_id, "rejected", decided_reason=reason)
            if kind == "goal_plan":
                goal_id = payload.get("goal_id")
                if goal_id:
                    safe_append_goal_event(
                        user_id,
                        goal_id,
                        None,
                        "goal_plan_rejected",
                        {"suggestion_id": suggestion_id, "reason": reason, "source": event_source},
                    )
            if kind == "plan_item":
                logger.info(
                    "API: plan_item rejected request_id=%s user_id=%s suggestion_id=%s",
                    request_id,
                    user_id,
                    suggestion_id,
                )
            results.append({"ok": True, "suggestion": updated, "action": "rejected"})
            continue

        if kind == "goal":
            title = payload.get("title") or payload.get("body") or "Untitled Goal"
            description = payload.get("description") or payload.get("body") or ""
            steps = payload.get("steps") or []
            goal = create_goal({"title": title, "description": description, "checklist": steps}, user_id)
            if not goal:
                results.append({"ok": False, "error": "goal_create_failed", "suggestion_id": suggestion_id})
                continue
            safe_append_goal_event(
                user_id,
                goal.get("id"),
                None,
                "goal_created",
                {"source": event_source, "suggestion_id": suggestion_id, "title": title},
            )
            updated = update_suggestion_status(user_id, suggestion_id, "accepted", decided_reason=reason)
            results.append({"ok": True, "action": "accepted", "goal": goal, "suggestion": updated})
            continue

        if kind == "plan_item":
            plan_date_local, timezone_name = _resolve_plan_date_and_timezone(
                user_id=user_id,
                date_local=payload.get("plan_date_local") or payload.get("date_local"),
                timezone_name=payload.get("timezone"),
                logger=logger,
            )
            plan = upsert_plan_header(
                user_id=user_id,
                plan_date_local=plan_date_local,
                timezone=timezone_name,
                status="confirmed",
                confirmed_at_utc=datetime.now(timezone.utc),
            )
            if not plan:
                results.append({"ok": False, "error": "plan_create_failed", "suggestion_id": suggestion_id})
                continue
            plan_id = plan.get("id")
            try:
                order_index = int(payload.get("order_index"))
            except (TypeError, ValueError):
                order_index = None
            if order_index is None:
                order_index = get_next_plan_item_order_index(plan_id)
            
            # Force status to planned for accepted suggestions
            payload["status"] = "planned"
            payload["suggestion_id"] = suggestion_id
            
            item = insert_plan_item_from_payload(
                plan_id=plan_id,
                user_id=user_id,
                payload=payload,
                order_index=order_index,
            )
            if not item:
                results.append({"ok": False, "error": "plan_item_create_failed", "suggestion_id": suggestion_id})
                continue
            updated = update_suggestion_status(user_id, suggestion_id, "accepted", decided_reason=reason)
            logger.info(
                "API: plan_item accepted request_id=%s user_id=%s suggestion_id=%s plan_id=%s item_id=%s",
                request_id,
                user_id,
                suggestion_id,
                plan_id,
                item.get("item_id"),
            )
            results.append(
                {
                    "ok": True,
                    "action": "accepted",
                    "plan_id": plan_id,
                    "plan_item": item,
                    "suggestion": updated,
                }
            )
            continue

        if kind == "goal_plan":
            goal_id = payload.get("goal_id")
            try:
                goal_id = int(goal_id)
            except (TypeError, ValueError):
                results.append({"ok": False, "error": "invalid_goal_id", "suggestion_id": suggestion_id})
                continue
            steps = payload.get("steps") or payload.get("plan_steps") or []
            if not isinstance(steps, list) or not steps:
                results.append({"ok": False, "error": "no_steps", "suggestion_id": suggestion_id})
                continue
            mode = (payload.get("mode") or "replace").strip().lower()
            section_label = payload.get("section_label")
            section_prefix = payload.get("section_prefix")
            plan_text = payload.get("plan_text")
            summary = payload.get("summary")
            meta_updates = payload.get("meta_updates") or {}
            try:
                if mode == "append" and hasattr(goal_mgr, "append_goal_plan"):
                    goal_mgr.append_goal_plan(
                        user_id,
                        goal_id,
                        steps,
                        default_section=section_label,
                    )
                elif hasattr(goal_mgr, "save_goal_plan_section") and section_label:
                    goal_mgr.save_goal_plan_section(
                        user_id,
                        goal_id,
                        steps,
                        section_label,
                        section_prefix=section_prefix,
                    )
                else:
                    goal_mgr.save_goal_plan(user_id, goal_id, steps)
            except Exception:
                results.append({"ok": False, "error": "plan_save_failed", "suggestion_id": suggestion_id})
                continue
            if plan_text or summary:
                try:
                    goal_mgr.update_goal_plan(user_id, goal_id, plan=plan_text, summary=summary)
                except Exception:
                    pass
            if meta_updates:
                try:
                    update_goal_meta(goal_id, meta_updates, user_id=user_id)
                except Exception:
                    pass
            safe_append_goal_event(
                user_id,
                goal_id,
                None,
                "goal_plan_confirmed",
                {
                    "suggestion_id": suggestion_id,
                    "step_count": len(steps),
                    "mode": mode,
                    "source": event_source,
                },
            )
            updated = update_suggestion_status(user_id, suggestion_id, "accepted", decided_reason=reason)
            results.append({
                "ok": True,
                "action": "accepted",
                "goal_id": goal_id,
                "step_count": len(steps),
                "suggestion": updated,
            })
            continue

        if kind == "routine":
            status = payload.get("status")
            draft = payload.get("draft") or {}
            if status != "complete":
                results.append({"ok": False, "error": "routine_incomplete", "suggestion_id": suggestion_id})
                continue
            routine = create_routine_from_draft(user_id, draft)
            if not routine:
                results.append({"ok": False, "error": "routine_create_failed", "suggestion_id": suggestion_id})
                continue
            updated = update_suggestion_status(user_id, suggestion_id, "accepted", decided_reason=reason)
            results.append({"ok": True, "action": "accepted", "routine": routine, "suggestion": updated})
            continue

        results.append({"ok": False, "error": "unsupported_kind", "suggestion_id": suggestion_id})

    return results


@v1.route("/health", methods=["GET"])
def v1_health_check():
    return _v1_envelope(data={"ok": True})


@v1.route("/ready", methods=["GET"])
def v1_ready_check():
    state = _ready_state()
    status = 200 if state["ready"] else 503
    return _v1_envelope(data=state, status=status)


@v1.route("/read/today", methods=["GET"])
@require_auth
def v1_read_today():
    logger = logging.getLogger("API.V1")
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    date_local_param = request.args.get("date_local")
    timezone_param = request.args.get("timezone")
    plan_date_local, timezone_name = _resolve_plan_date_and_timezone(
        user_id=user_id,
        date_local=date_local_param,
        timezone_name=timezone_param,
        logger=logger,
    )
    from db.plan_repository import get_plan_with_items_by_local_date
    plan = get_plan_with_items_by_local_date(user_id, plan_date_local)
    if plan:
        items = []
        for item in plan.get("items") or []:
            item_payload = dict(item)
            item_payload["created_at_utc"] = _serialize_datetime(item.get("created_at_utc"))
            item_payload["updated_at_utc"] = _serialize_datetime(item.get("updated_at_utc"))
            items.append(item_payload)
        plan_payload = {
            "plan_id": plan.get("id"),
            "plan_date_local": (
                plan.get("plan_date_local").isoformat()
                if hasattr(plan.get("plan_date_local"), "isoformat")
                else plan.get("plan_date_local")
            ),
            "timezone": plan.get("timezone") or timezone_name,
            "status": plan.get("status") or "draft",
            "created_at_utc": _serialize_datetime(plan.get("created_at_utc")),
            "confirmed_at_utc": _serialize_datetime(plan.get("confirmed_at_utc")),
            "items": items,
        }
    else:
        plan_payload = {
            "plan_id": None,
            "plan_date_local": plan_date_local.isoformat(),
            "timezone": timezone_name,
            "status": "none",
            "items": [],
        }
    logger.info(
        "API: v1 read today request_id=%s route=%s status=%s user_id=%s plan_date_local=%s plan_status=%s",
        request_id,
        request.path,
        200,
        user_id,
        plan_payload.get("plan_date_local"),
        plan_payload.get("status"),
    )
    return _v1_envelope(data={"plan": plan_payload}, status=200)


@v1.route("/plan/draft", methods=["POST"])
@require_auth
def v1_plan_draft():
    logger = logging.getLogger("API.V1")
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if not request.is_json:
        return api_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)
    message_ids = data.get("message_ids") or []
    include_rollover = bool(data.get("include_rollover"))
    date_local_param = data.get("date_local")
    timezone_param = data.get("timezone")
    if message_ids and not isinstance(message_ids, list):
        return api_error("VALIDATION_ERROR", "message_ids must be a list", 400)
    if not message_ids and not include_rollover:
        return api_error("VALIDATION_ERROR", "message_ids or include_rollover required", 400)
    plan_date_local, timezone_name = _resolve_plan_date_and_timezone(
        user_id=user_id,
        date_local=date_local_param,
        timezone_name=timezone_param,
        logger=logger,
    )
    suggestion_ids: List[int] = []
    from db.suggestions_repository import create_suggestion
    if message_ids:
        normalized_ids: List[int] = []
        for value in message_ids:
            try:
                normalized_ids.append(int(value))
            except (TypeError, ValueError):
                return api_error("VALIDATION_ERROR", "message_ids must be integers", 400)
        from db.messages_repository import list_messages_by_ids
        rows = list_messages_by_ids(user_id, normalized_ids)
        if not rows:
            return api_error("NOT_FOUND", "No messages found", 404, details={"message_ids": normalized_ids})
        for row in rows:
            transcript = (row.get("transcript") or "").strip()
            if not transcript:
                continue
            title = transcript[:120].strip()
            payload = {
                "title": title,
                "notes": transcript,
                "source_kind": "message",
                "source_id": str(row.get("id")),
                "plan_date_local": plan_date_local.isoformat(),
                "timezone": timezone_name,
            }
            provenance = {
                "source": "v1_plan_draft",
                "message_id": row.get("id"),
                "request_id": request_id,
            }
            suggestion = create_suggestion(
                user_id=user_id,
                kind="plan_item",
                payload=payload,
                provenance=provenance,
            )
            suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
            if suggestion_id:
                suggestion_ids.append(int(suggestion_id))

    if include_rollover:
        from db.plan_repository import get_plan_with_items_by_local_date
        rollover_date = plan_date_local - timedelta(days=1)
        rollover_plan = get_plan_with_items_by_local_date(user_id, rollover_date)
        rollover_items = (rollover_plan or {}).get("items") or []
        for item in rollover_items:
            status = (item.get("status") or "planned").strip().lower()
            if status in ("done", "completed", "skipped", "canceled", "dropped"):
                continue
            title = item.get("title") or item.get("notes") or item.get("item_id") or "Rollover item"
            payload = {
                "title": str(title).strip()[:120] or "Rollover item",
                "notes": item.get("notes"),
                "source_kind": "rollover",
                "source_id": str(item.get("item_id") or item.get("id") or ""),
                "plan_date_local": plan_date_local.isoformat(),
                "timezone": timezone_name,
            }
            if item.get("order_index") is not None:
                payload["order_index"] = item.get("order_index")
            provenance = {
                "source": "v1_plan_draft_rollover",
                "rollover_plan_date": rollover_date.isoformat(),
                "request_id": request_id,
            }
            suggestion = create_suggestion(
                user_id=user_id,
                kind="plan_item",
                payload=payload,
                provenance=provenance,
            )
            suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
            if suggestion_id:
                suggestion_ids.append(int(suggestion_id))

    logger.info(
        "API: v1 plan draft request_id=%s route=%s status=%s user_id=%s plan_date_local=%s suggestions=%s",
        request_id,
        request.path,
        200,
        user_id,
        plan_date_local.isoformat(),
        len(suggestion_ids),
    )
    return _v1_envelope(data={"suggestion_ids": suggestion_ids}, status=200)


@v1.route("/suggestions/<int:suggestion_id>/accept", methods=["POST"])
@require_auth
def v1_accept_suggestion(suggestion_id: int):
    logger = logging.getLogger("API.V1")
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    reason = None
    payload_override = None
    if request.is_json:
        payload = request.get_json(silent=True)
        if isinstance(payload, dict):
            reason = payload.get("reason")
            payload_override = payload.get("payload")
    if payload_override and isinstance(payload_override, dict):
        try:
            existing = suggestions_repository.get_suggestion(user_id, suggestion_id)
            if isinstance(existing, dict):
                merged = dict(existing.get("payload") or {})
                merged.update(payload_override)
                suggestions_repository.update_suggestion_payload(user_id, suggestion_id, merged)
        except Exception:
            logger.warning(
                "API: suggestion payload update failed request_id=%s suggestion_id=%s",
                request_id,
                suggestion_id,
                exc_info=True,
            )
    results = _apply_suggestion_decisions(
        user_id,
        [{"suggestion_id": suggestion_id, "action": "accept", "reason": reason}],
        event_source="v1_accept",
    )
    logger.info(
        "API: v1 suggestion accept request_id=%s route=%s status=%s user_id=%s suggestion_id=%s",
        request_id,
        request.path,
        200,
        user_id,
        suggestion_id,
    )
    return _v1_envelope(data={"results": results}, status=200)


@v1.route("/suggestions/<int:suggestion_id>/patch", methods=["POST"])
@require_auth
def v1_patch_suggestion(suggestion_id: int):
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return _v1_error("VALIDATION_ERROR", "text is required", 400)
    suggestion = suggestions_repository.get_suggestion(user_id, suggestion_id)
    if not suggestion:
        return _v1_error("NOT_FOUND", "Suggestion not found", 404, details={"suggestion_id": suggestion_id})
    if suggestion.get("kind") != "routine":
        return _v1_error("INVALID_KIND", "Only routine suggestions can be patched", 400)
    status = (suggestion.get("status") or "").strip().lower()
    if status != "pending":
        return _v1_error("INVALID_STATUS", "Suggestion is not pending", 400)
    payload = suggestion.get("payload") or {}
    patched_payload = _build_routine_patch_payload(text, payload)
    if not patched_payload:
        return _v1_error("NO_PATCH_FIELDS", "No routine fields detected in edit text", 400)
    updated = suggestions_repository.update_suggestion_payload(user_id, suggestion_id, patched_payload)
    return _v1_envelope(
        data={"suggestion_id": suggestion_id, "suggestion": updated or suggestion},
        status=200,
    )


@v1.route("/capabilities", methods=["GET"])
def v1_capabilities():
    return jsonify(get_capabilities_payload())


@v1.route("/auth/login", methods=["POST"])
def v1_auth_login():
    return _v1_from_api_response(auth_login())


@v1.route("/auth/me", methods=["GET"])
def v1_auth_me():
    return _v1_from_api_response(auth_me())


@v1.route("/auth/logout", methods=["POST"])
def v1_auth_logout():
    return _v1_from_api_response(auth_logout())


@v1.route("/sessions", methods=["POST"])
@require_auth
def v1_create_session():
    user_id, error = _v1_get_user_id()
    if error:
        return error
    from db.messages_repository import create_session
    session = create_session(user_id)
    session_id = session.get("id") if isinstance(session, dict) else None
    if not session_id:
        return _v1_error("SESSION_CREATE_FAILED", "Failed to create session", 500)
    return _v1_envelope(data={"session_id": session_id}, status=201)


@require_auth
@v1.route("/messages", methods=["GET", "POST"])
def v1_messages():
    if request.method == "GET":
        user_id, error = _get_user_id_or_error()
        if error:
            return error
        channel = request.args.get("channel") or "companion"
        channel = str(channel).strip().lower()
        if channel not in {"companion", "planner", "system"}:
            return _v1_error("VALIDATION_ERROR", "channel is invalid", 400)
        limit = request.args.get("limit")
        try:
            limit_value = int(limit) if limit is not None else 50
        except (TypeError, ValueError):
            return _v1_error("VALIDATION_ERROR", "limit must be an integer", 400)
        if limit_value <= 0:
            return _v1_error("VALIDATION_ERROR", "limit must be positive", 400)
        if limit_value > 200:
            limit_value = 200
        from db.messages_repository import list_recent_messages
        include_legacy_raw = request.args.get("include_legacy_planner")
        if include_legacy_raw is None:
            include_legacy_raw = request.args.get("include_legacy")
        if include_legacy_raw is None:
            include_legacy_raw = "1"
        include_legacy = str(include_legacy_raw).strip().lower() in ("1", "true", "yes", "on")
        rows = list_recent_messages(user_id, limit=limit_value, channel=channel)
        companion_count = len(rows) if channel == "companion" else 0
        legacy_rows = []
        legacy_used = False
        if channel == "companion" and include_legacy:
            legacy_rows = list_recent_messages(user_id, limit=limit_value, channel="planner")
            if legacy_rows:
                legacy_used = True
            merged = []
            seen_ids = set()
            for row in rows + legacy_rows:
                msg_id = row.get("id")
                if msg_id in seen_ids:
                    continue
                seen_ids.add(msg_id)
                merged.append(row)
            merged.sort(
                key=lambda r: (
                    r.get("created_at") or datetime.min.replace(tzinfo=timezone.utc),
                    r.get("id") or 0,
                ),
                reverse=True,
            )
            merged = merged[:limit_value]
            merged.sort(
                key=lambda r: (
                    r.get("created_at") or datetime.min.replace(tzinfo=timezone.utc),
                    r.get("id") or 0,
                )
            )
            rows = merged
        logging.getLogger("API.Messages").info(
            "v1_messages requested_channel=%s include_legacy_planner=%s counts={companion:%s,planner:%s} legacy_used=%s final_count=%s",
            channel,
            include_legacy,
            companion_count,
            len(legacy_rows),
            legacy_used,
            len(rows),
        )
        provenance = {
            "requested_channel": channel,
            "include_legacy_planner": include_legacy,
            "legacy_used": legacy_used,
            "count_companion": companion_count,
            "count_planner": len(legacy_rows),
        }
        return _v1_envelope(data={"messages": rows, "provenance": provenance}, status=200)

    user_id, error = _v1_get_user_id()
    if error:
        return error
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)

    transcript = data.get("transcript")
    if transcript is None:
        transcript = data.get("text")
    if not isinstance(transcript, str) or not transcript.strip():
        return _v1_error("VALIDATION_ERROR", "transcript is required", 400)

    source = data.get("source") or "text"
    if not isinstance(source, str) or not source.strip():
        source = "text"
    channel = data.get("channel") or "companion"
    if not isinstance(channel, str) or not channel.strip():
        channel = "companion"
    channel = channel.strip().lower()
    if channel not in {"companion", "planner", "system"}:
        return _v1_error("VALIDATION_ERROR", "channel is invalid", 400)

    session_id = data.get("session_id")
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return _v1_error("VALIDATION_ERROR", "session_id must be an integer", 400)

    from db.messages_repository import create_message
    # Canonical transcript lives on messages.transcript; transcripts table stores snapshots for audit.
    record = create_message(
        user_id=user_id,
        transcript=transcript.strip(),
        source=source.strip(),
        channel=channel,
        session_id=session_id,
        status="final",
        create_session_if_missing=True,
    )
    return _v1_envelope(data={"message": record}, status=201)


@v1.route("/data/clear", methods=["POST"])
@require_auth
def v1_clear_data():
    logger = logging.getLogger("API")
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if not request.is_json:
        return api_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)
    confirm = data.get("confirm")
    if confirm != "DELETE":
        return api_error("CONFIRM_REQUIRED", "Type DELETE to confirm", 400)
    scopes = data.get("scopes")
    if not isinstance(scopes, list) or not scopes:
        return api_error("VALIDATION_ERROR", "scopes must be a non-empty list", 400)
    normalized_scopes = []
    invalid_scopes = []
    for scope in scopes:
        if not isinstance(scope, str):
            invalid_scopes.append(scope)
            continue
        cleaned = scope.strip().lower()
        if cleaned in ("goals", "plans", "insights", "history", "routines"):
            normalized_scopes.append(cleaned)
        else:
            invalid_scopes.append(scope)
    if invalid_scopes:
        return api_error(
            "VALIDATION_ERROR",
            "Invalid scopes provided",
            400,
            details={"invalid_scopes": invalid_scopes},
        )

    deleted: Dict[str, int] = {}
    from db.database import get_connection
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if "plans" in normalized_scopes:
                cursor.execute(
                    "DELETE FROM plan_items WHERE plan_id IN (SELECT id FROM plans WHERE user_id = %s)",
                    (user_id,),
                )
                deleted["plan_items"] = cursor.rowcount
                cursor.execute("DELETE FROM plans WHERE user_id = %s", (user_id,))
                deleted["plans"] = cursor.rowcount
                cursor.execute("DELETE FROM goal_task_history WHERE user_id = %s", (user_id,))
                deleted["goal_task_history"] = cursor.rowcount
            if "routines" in normalized_scopes:
                cursor.execute(
                    "DELETE FROM routine_steps WHERE routine_id IN (SELECT id FROM routines WHERE user_id = %s)",
                    (user_id,),
                )
                deleted["routine_steps"] = cursor.rowcount
                cursor.execute("DELETE FROM routines WHERE user_id = %s", (user_id,))
                deleted["routines"] = cursor.rowcount
                
                # SAFE DELETION: Only delete routine items from today onwards to preserve history
                # Use local_today to match plan generation semantics
                local_today = _get_local_today(user_id)
                
                # Backfill legacy items (scoped to today+) so we can rely on source_kind
                cursor.execute(
                    """
                    UPDATE plan_items 
                    SET source_kind = 'routine' 
                    WHERE user_id = %s 
                    AND source_kind IS NULL 
                    AND type IN ('routine', 'routine_step')
                    AND plan_id IN (
                        SELECT id FROM plans 
                        WHERE user_id = %s AND plan_date >= %s
                    )
                    """,
                    (user_id, user_id, local_today),
                )
                
                # Delete strictly by source_kind='routine'
                cursor.execute(
                    """
                    DELETE FROM plan_items 
                    WHERE user_id = %s 
                    AND source_kind = 'routine'
                    AND plan_id IN (
                        SELECT id FROM plans 
                        WHERE user_id = %s AND plan_date >= %s
                    )
                    """,
                    (user_id, user_id, local_today),
                )
                deleted["routine_plan_items"] = cursor.rowcount
            if "goals" in normalized_scopes:
                if "plans" not in normalized_scopes:
                    cursor.execute(
                        "DELETE FROM plan_items WHERE user_id = %s AND (LOWER(type) = 'goal_task' OR section = 'goal_tasks')",
                        (user_id,),
                    )
                    deleted["goal_task_plan_items"] = cursor.rowcount
                    cursor.execute("DELETE FROM goal_task_history WHERE user_id = %s", (user_id,))
                    deleted["goal_task_history"] = cursor.rowcount
                cursor.execute(
                    "DELETE FROM plan_steps WHERE goal_id IN (SELECT id FROM goals WHERE user_id = %s)",
                    (user_id,),
                )
                deleted["goal_steps"] = cursor.rowcount
                cursor.execute("DELETE FROM goal_events WHERE user_id = %s", (user_id,))
                deleted["goal_events"] = cursor.rowcount
                cursor.execute("DELETE FROM goals WHERE user_id = %s", (user_id,))
                deleted["goals"] = cursor.rowcount
            if "insights" in normalized_scopes:
                cursor.execute("DELETE FROM insights WHERE user_id = %s", (user_id,))
                deleted["insights"] = cursor.rowcount
            if "history" in normalized_scopes:
                cursor.execute("DELETE FROM suggestions WHERE user_id = %s", (user_id,))
                deleted["suggestions"] = cursor.rowcount
                cursor.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
                deleted["messages"] = cursor.rowcount
                cursor.execute("DELETE FROM sessions WHERE user_id = %s", (user_id,))
                deleted["sessions"] = cursor.rowcount
        conn.commit()

    if "plans" in normalized_scopes or "goals" in normalized_scopes:
        removed = _clear_day_plan_cache(user_id, logger)
        deleted["plan_cache_files"] = removed

    return jsonify(
        {
            "ok": True,
            "request_id": _get_request_id(),
            "scopes": normalized_scopes,
            "deleted": deleted,
        }
    )


@require_auth
@v1.route("/sessions/<int:session_id>/messages", methods=["GET"])
def v1_list_session_messages(session_id: int):
    user_id, error = _v1_get_user_id()
    if error:
        return error
    from db.messages_repository import list_messages_for_session
    rows = list_messages_for_session(user_id, session_id)
    return _v1_envelope(data={"session_id": session_id, "messages": rows}, status=200)


@require_auth
@v1.route("/messages/<int:message_id>", methods=["GET"])
def v1_get_message(message_id: int):
    user_id, error = _v1_get_user_id()
    if error:
        return error
    from db.messages_repository import get_message
    record = get_message(user_id, message_id)
    if not record:
        return _v1_error("NOT_FOUND", "Message not found", 404, details={"message_id": message_id})
    return _v1_envelope(data={"message": record}, status=200)


def _v1_update_message_payload(message_id: int, data: Dict[str, Any]):
    user_id, error = _v1_get_user_id()
    if error:
        return error
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)
    status = data.get("status")
    transcript = data.get("transcript")
    if transcript is None:
        transcript = data.get("text")
    if status is None and transcript is None:
        return _v1_error("VALIDATION_ERROR", "status or transcript required", 400)
    if transcript is not None and not isinstance(transcript, str):
        return _v1_error("VALIDATION_ERROR", "transcript must be a string", 400)
    if transcript is not None and status is None:
        status = "final"

    allowed_statuses = {"uploading", "transcribing", "ready", "failed", "final"}
    if status is not None:
        if not isinstance(status, str):
            return _v1_error("VALIDATION_ERROR", "status must be a string", 400)
        status = status.strip().lower()
        if status not in allowed_statuses:
            return _v1_error("VALIDATION_ERROR", "status is invalid", 400)

    from db.messages_repository import get_message, update_message
    current = get_message(user_id, message_id)
    if not current:
        return _v1_error("NOT_FOUND", "Message not found", 404, details={"message_id": message_id})
    current_status = (current.get("status") or "").strip().lower()
    transitions = {
        "uploading": {"transcribing", "ready", "failed", "final"},
        "transcribing": {"ready", "failed", "final"},
        "ready": {"final", "failed"},
        "failed": {"transcribing", "final"},
        "final": {"final"},
    }
    if status is not None:
        allowed_next = transitions.get(current_status, set())
        if status != current_status and status not in allowed_next:
            return _v1_error(
                "INVALID_STATUS_TRANSITION",
                "Invalid status transition",
                409,
                details={"from": current_status, "to": status},
            )

    # Canonical transcript lives on messages.transcript; transcripts table stores snapshots for audit.
    record = update_message(
        user_id=user_id,
        message_id=message_id,
        status=status,
        transcript=transcript.strip() if isinstance(transcript, str) else None,
    )
    if not record:
        return _v1_error("UPDATE_FAILED", "Failed to update message", 500)
    return _v1_envelope(data={"message": record}, status=200)


@v1.route("/messages/<int:message_id>", methods=["PATCH"])
@require_auth
def v1_update_message(message_id: int):
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    return _v1_update_message_payload(message_id, data)


@require_auth
@v1.route("/messages/<int:message_id>/finalize", methods=["POST"])
def v1_finalize_message(message_id: int):
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)
    transcript = data.get("transcript")
    if transcript is None:
        transcript = data.get("text")
    if not isinstance(transcript, str) or not transcript.strip():
        return _v1_error("VALIDATION_ERROR", "transcript is required", 400)
    payload = {"status": "final", "transcript": transcript}
    return _v1_update_message_payload(message_id, payload)


@require_auth
@v1.route("/analyze", methods=["POST"])
def v1_analyze():
    user_id, error = _v1_get_user_id()
    if error:
        return error
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)

    message_ids = data.get("message_ids") or []
    if not isinstance(message_ids, list) or not message_ids:
        return _v1_error("VALIDATION_ERROR", "message_ids must be a non-empty list", 400)
    normalized_ids = []
    for value in message_ids:
        try:
            normalized_ids.append(int(value))
        except (TypeError, ValueError):
            return _v1_error("VALIDATION_ERROR", "message_ids must be integers", 400)

    from db.messages_repository import list_messages_by_ids
    from db.suggestions_repository import create_suggestion

    rows = list_messages_by_ids(user_id, normalized_ids)
    if not rows:
        return _v1_error("NOT_FOUND", "No messages found", 404, details={"message_ids": normalized_ids})

    llm_error_code = None
    raw_llm_error = data.get("llm_error_code")
    if isinstance(raw_llm_error, str) and raw_llm_error.strip():
        llm_error_code = raw_llm_error.strip()
    elif not is_openai_configured():
        llm_error_code = "missing_api_key"

    def _fallback_goal_payload(text: str) -> Optional[Dict[str, Any]]:
        raw = str(text or "").strip()
        if not raw:
            return None
        if is_goal_list_request(raw):
            return None
        if parse_goal_selection_request(raw) is not None:
            return None
        patterns = (
            r"^my goal is\b",
            r"^my goal\b",
            r"^i want to\b",
            r"^i'd like to\b",
            r"^help me\b",
            r"^can you help me\b",
            r"^please help me\b",
        )
        if not any(re.search(pattern, raw, flags=re.IGNORECASE) for pattern in patterns):
            return None
        title_suggestion = _extract_goal_title_suggestion(raw)
        return {
            "title": title_suggestion,
            "body": raw,
            "confidence": 0.6,
        }

    created = []
    routine_parser = None
    routine_timezone = None
    try:
        from core.conversation_parser import ConversationParser
        from db.plan_repository import get_user_timezone
        routine_parser = ConversationParser()
        routine_timezone = get_user_timezone(user_id)
    except Exception as exc:
        logging.getLogger("API").warning(
            "API: routine parser unavailable: %s",
            exc,
            exc_info=True,
        )
    for row in rows:
        transcript = (row.get("transcript") or "").strip()
        if not transcript:
            continue
        if routine_parser is not None:
            try:
                routine_candidates = routine_parser.extract_routines(transcript) or []
            except Exception as exc:
                logging.getLogger("API").warning(
                    "API: routine extraction failed: %s",
                    exc,
                    exc_info=True,
                )
                routine_candidates = []
            routine_drafts = [
                routine for routine in routine_candidates
                if isinstance(routine, dict) and routine.get("draft_type") == "schedule"
            ]
            if routine_drafts:
                for routine_draft in routine_drafts:
                    draft = dict(routine_draft)
                    draft["timezone"] = routine_timezone
                    missing_fields = list(draft.get("missing_fields") or [])
                    ambiguous_fields = list(draft.get("ambiguous_fields") or [])
                    payload = _build_routine_suggestion_payload(draft, missing_fields, ambiguous_fields)
                    provenance = {
                        "message_ids": [row.get("id")],
                        "source": "v1_analyze_routine",
                        "detector": "routine_schedule_parser",
                    }
                    created.append(
                        create_suggestion(
                            user_id=user_id,
                            kind="routine",
                            payload=payload,
                            provenance=provenance,
                        )
                    )
        suggestion = _detect_goal_intent_suggestion(transcript, str(row.get("id")))
        if suggestion:
            payload = {
                "title": suggestion.get("title_suggestion"),
                "body": suggestion.get("body_suggestion"),
                "confidence": suggestion.get("confidence"),
            }
            provenance = {
                "message_ids": [row.get("id")],
                "source": "v1_analyze_llm",
                "detector": "goal_intent_heuristic",
            }
            created.append(
                create_suggestion(
                    user_id=user_id,
                    kind="goal",
                    payload=payload,
                    provenance=provenance,
                )
            )
            continue

        fallback_payload = _fallback_goal_payload(transcript)
        if not fallback_payload:
            continue
        fallback_reason = "llm_unavailable" if not is_openai_configured() else "heuristic"
        provenance = {
            "message_ids": [row.get("id")],
            "source": "v1_analyze_fallback",
            "detector": "fallback_pattern",
            "fallback_reason": fallback_reason,
        }
        if llm_error_code:
            provenance["llm_error_code"] = llm_error_code
        created.append(
            create_suggestion(
                user_id=user_id,
                kind="goal",
                payload=fallback_payload,
                provenance=provenance,
            )
        )

    return _v1_envelope(
        data={"suggestions": created, "analyzed_message_ids": normalized_ids},
        status=200,
    )

@require_auth

@v1.route("/suggestions", methods=["GET"])
def v1_list_suggestions():
    user_id, error = _v1_get_user_id()
    if error:
        return error
    status = (request.args.get("status") or "pending").strip().lower()
    if not status:
        return _v1_error("VALIDATION_ERROR", "status is required", 400)
    kind = request.args.get("kind")
    if kind is not None:
        kind = str(kind).strip()
        if not kind:
            kind = None
    limit = request.args.get("limit")
    try:
        limit_value = int(limit) if limit is not None else 50
    except (TypeError, ValueError):
        return _v1_error("VALIDATION_ERROR", "limit must be an integer", 400)
    if limit_value <= 0:
        return _v1_error("VALIDATION_ERROR", "limit must be positive", 400)
    from db.suggestions_repository import list_suggestions
    rows = list_suggestions(user_id=user_id, status=status, kind=kind, limit=limit_value)
    return _v1_envelope(data={"suggestions": rows}, status=200)


@v1.route("/confirm", methods=["POST"])
def v1_confirm():
    user_id, error = _v1_get_user_id()
    if error:
        return error
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)

    decisions = data.get("decisions")
    if decisions is None:
        decisions = [data]
    if not isinstance(decisions, list) or not decisions:
        return _v1_error("VALIDATION_ERROR", "decisions must be a non-empty list", 400)

    results = _apply_suggestion_decisions(user_id, decisions, event_source="v1_confirm")
    return _v1_envelope(data={"results": results}, status=200)


@v1.route("/read/history", methods=["GET"])
def v1_read_history():
    user_id, error = _v1_get_user_id()
    if error:
        return error
    limit = request.args.get("limit")
    try:
        limit_value = int(limit) if limit is not None else 100
    except (TypeError, ValueError):
        return _v1_error("VALIDATION_ERROR", "limit must be an integer", 400)
    from db.goal_events_repository import safe_list_user_goal_events
    events = safe_list_user_goal_events(user_id, limit=limit_value)
    return _v1_envelope(data={"events": events}, status=200)


app.register_blueprint(v1)

# Serve static assets (JS, CSS, etc.) if referenced as /static/...
@app.route('/static/<path:filename>')
def static_files(filename):
    # Guess mimetype for correct Content-Type
    mimetype, _ = mimetypes.guess_type(filename)
    return send_file(os.path.join(app.static_folder, filename), mimetype=mimetype)

# Minimal auth endpoints
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    logger = logging.getLogger("API.Auth")

    if not request.is_json:
        return api_error("VALIDATION_ERROR", "JSON body required", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)

    # Accept multiple field names for the access code
    raw_code = (
        data.get("password")
        or data.get("access_code")
        or data.get("code")
        or data.get("pin")
        or ""
    )
    password = str(raw_code).strip()

    def _env_trim(key: str) -> Optional[str]:
        val = os.environ.get(key)
        if val is None:
            return None
        stripped = str(val).strip()
        return stripped or None

    login_keys_raw = _env_trim("OTHELLO_LOGIN_KEYS")
    pin_hash = _env_trim("OTHELLO_PIN_HASH")
    login_key = _env_trim("OTHELLO_LOGIN_KEY")
    plain_pwd = _env_trim("OTHELLO_PASSWORD")  # legacy fallback
    default_user_id = _env_trim("OTHELLO_USER_ID") or "1"
    auth_mode = "pin_hash" if pin_hash else ("login_key" if login_key else ("plaintext_password" if plain_pwd else "none"))

    def _login_success(user_id: str, mode: str):
        session["authed"] = True
        session["user_id"] = user_id
        try:
            ensure_user_exists(user_id)
        except Exception as exc:
            session.clear()
            logger.error("ensure_user_exists failed: %s", exc, exc_info=True)
            return api_error(
                "USER_INIT_FAILED",
                "Failed to initialize user",
                500,
                details=type(exc).__name__,
            )
        return jsonify({"ok": True, "auth_mode": mode, "user_id": user_id})

    if login_keys_raw:
        entries = []
        for entry in login_keys_raw.split(";"):
            entry = entry.strip()
            if not entry or "=" not in entry:
                continue
            user_id_part, code_part = entry.split("=", 1)
            user_id_part = user_id_part.strip()
            code_part = code_part.strip()
            if user_id_part and code_part:
                entries.append((user_id_part, code_part))
        if not entries:
            return api_error(
                "AUTH_MISCONFIGURED",
                "Authentication misconfigured",
                503,
                details="invalid_login_keys",
                extra={"auth_mode": "login_keys"},
            )
        import hmac
        matched_user_id = None
        for user_id_part, code_part in entries:
            if hmac.compare_digest(password, code_part):
                matched_user_id = user_id_part
                break
        if not matched_user_id:
            return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": "login_keys"})
        gate_error = _beta_gate_check(matched_user_id)
        if gate_error:
            return gate_error
        return _login_success(matched_user_id, "login_keys")

    if not pin_hash and not login_key and not plain_pwd:
        return api_error(
            "AUTH_NOT_CONFIGURED",
            "Authentication not configured",
            503,
            details="no_login_configured",
            extra={"auth_mode": auth_mode},
        )

    if not password:
        return api_error(
            "VALIDATION_ERROR",
            "Access code required",
            400,
            extra={"auth_mode": auth_mode},
        )

    # Verify session secret exists
    secret_key = (_env_trim("OTHELLO_SECRET_KEY") or _env_trim("SECRET_KEY"))
    if not secret_key:
        return api_error(
            "AUTH_MISCONFIGURED",
            "Authentication misconfigured",
            503,
            details="missing_secret_key",
            extra={"auth_mode": auth_mode},
        )

    if pin_hash:
        try:
            if bcrypt.verify(password, pin_hash):
                gate_error = _beta_gate_check(default_user_id)
                if gate_error:
                    return gate_error
                return _login_success(default_user_id, auth_mode)
            return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": auth_mode})
        except Exception:
            logger.error("bcrypt verification error", exc_info=True)
            return api_error(
                "AUTH_MISCONFIGURED",
                "Authentication misconfigured",
                503,
                details="invalid_pin_hash",
                extra={"auth_mode": auth_mode},
            )

    if login_key:
        import hmac
        if hmac.compare_digest(password, login_key):
            gate_error = _beta_gate_check(default_user_id)
            if gate_error:
                return gate_error
            return _login_success(default_user_id, auth_mode)
        return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": auth_mode})

    # Legacy plaintext password
    logger.warning("plaintext password mode enabled; set OTHELLO_PIN_HASH or OTHELLO_LOGIN_KEY to harden")
    if password == plain_pwd:
        gate_error = _beta_gate_check(default_user_id)
        if gate_error:
            return gate_error
        return _login_success(default_user_id, auth_mode)
    return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": auth_mode})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    authed = bool(session.get("authed"))
    user_id = session.get("user_id")
    if authed and not user_id:
        session.clear()
        authed = False
        user_id = None
    return jsonify({
        "ok": True,
        "authed": authed,
        "user_id": user_id,
    })

@app.route("/api/whoami", methods=["GET"])
@require_auth
def whoami():
    return jsonify({
        "ok": True,
        "user_id": g.user_id,
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "request_id": _get_request_id()
    })

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    response = jsonify({"ok": True})
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    response.delete_cookie(cookie_name)
    return response


def _dev_reset_enabled() -> bool:
    return (os.getenv("OTHELLO_ENABLE_DEV_RESET") or "").strip().lower() == "true"


def _wipe_database() -> list[str]:
    from db.database import get_connection

    tables = [
        "goal_events",
        "plan_steps",
        "goals",
        "plans",
        "plan_items",
        "insights",
        "goal_task_history",
        "suggestions",
        "reflection_entries",
        "memory_entries",
        "profile_snapshots",
        "audit_events",
    ]
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE';
                    """
                )
                rows = cursor.fetchall() or []
                existing = set()
                for row in rows:
                    if isinstance(row, dict):
                        table_name = row.get("table_name")
                    else:
                        table_name = row[0] if row else None
                    if table_name:
                        existing.add(table_name)
                to_truncate = [name for name in tables if name in existing]
                if to_truncate:
                    cursor.execute(
                        f"TRUNCATE {', '.join(to_truncate)} RESTART IDENTITY CASCADE;"
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return to_truncate


@app.route("/api/admin/capabilities", methods=["GET"])
@require_auth
def admin_capabilities():
    return jsonify({"dev_reset_enabled": _dev_reset_enabled()})


@app.route("/api/admin/reset", methods=["POST"])
@require_auth
def admin_reset():
    logger = logging.getLogger("API.Admin")
    if not _dev_reset_enabled():
        return api_error("DEV_RESET_DISABLED", "Dev reset disabled", 403)

    if not request.is_json:
        return api_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)
    if data.get("confirm") != "RESET":
        return api_error(
            "VALIDATION_ERROR",
            "Confirmation required",
            400,
            details="confirm must be RESET",
        )

    try:
        tables = _wipe_database()
        logger.warning(
            "API: dev reset completed request_id=%s tables=%s",
            _get_request_id(),
            tables,
        )
        return jsonify({"ok": True, "request_id": _get_request_id(), "tables": tables})
    except Exception as exc:
        logger.error(
            "API: dev reset failed request_id=%s",
            _get_request_id(),
            exc_info=True,
        )
        return api_error(
            "DEV_RESET_FAILED",
            "Dev reset failed",
            500,
            details=type(exc).__name__,
        )


def log_pending_insights_on_startup():
    logger = logging.getLogger("API.Insights")
    logger.info("API: startup pending insights summary skipped (no user context)")


def _normalize_insights_meta(meta: Any) -> Dict[str, Any]:
    if not isinstance(meta, dict):
        return {"created": 0, "pending_counts": {}}
    pending_counts = meta.get("pending_counts")
    if not isinstance(pending_counts, dict):
        meta["pending_counts"] = {}
    created = meta.get("created")
    if not isinstance(created, int):
        try:
            meta["created"] = int(created)
        except Exception:
            meta["created"] = 0
    return meta


def _coerce_goal_id(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    try:
        text = str(value).strip()
        if not text:
            return None
        parsed = int(text)
        return parsed if parsed > 0 else None
    except Exception:
        return None


def _process_insights_pipeline(*, user_text: str, assistant_text: str, user_id: str):
    """Extract and persist insights, shielding chat flow from failures."""
    logger = logging.getLogger("API.Insights")
    meta: Dict[str, Any] = {"created": 0, "pending_counts": {}}

    try:
        comps = get_agent_components()
        created = comps["extract_insights_from_exchange"](
            user_message=user_text,
            assistant_message=assistant_text,
            user_id=user_id,
        ) or []
        meta["created"] = len(created) if isinstance(created, (list, tuple)) else 0
        logger.info("API: insight extraction persisted %s candidates", meta["created"])
    except Exception as exc:
        logger.warning("API: insight extraction failed: %s", exc, exc_info=True)
        return meta

    try:
        meta["pending_counts"] = comps["insights_repository"].count_pending_by_type(user_id) or {}
    except Exception as exc:
        logger.warning("API: failed to fetch pending insight counts: %s", exc, exc_info=True)

    return meta


@app.route("/api/conversations", methods=["POST"])
@require_auth
def create_conversation():
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    from db.messages_repository import create_session
    session = create_session(user_id)
    return jsonify({"conversation_id": session.get("id")})


@app.route("/api/conversations", methods=["GET"])
@require_auth
def list_conversations():
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    from db.messages_repository import list_sessions
    sessions = list_sessions(user_id, limit=50)
    return jsonify({"conversations": sessions})


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["GET"])
@require_auth
def list_conversation_messages(conversation_id: int):
    user_id, error = _get_user_id_or_error()
    if error:
        return error

    channel = request.args.get("channel") or "companion"
    channel = str(channel).strip().lower()

    limit = request.args.get("limit")
    try:
        limit_value = int(limit) if limit is not None else 50
    except (TypeError, ValueError):
        return _v1_error("VALIDATION_ERROR", "limit must be an integer", 400)

    from db.messages_repository import list_messages_for_session
    rows = list_messages_for_session(user_id, conversation_id, limit=limit_value, channel=channel)
    
    provenance = {
        "requested_channel": channel,
        "conversation_id": conversation_id
    }
    return _v1_envelope(data={"messages": rows, "provenance": provenance, "conversation_id": conversation_id}, status=200)


@app.route("/api/message", methods=["POST"])
@require_auth
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
    request_id = _get_request_id()
    start_time = time.monotonic()
    payload_bytes = request.content_length or 0
    log_started = False
    event_storage_ok: Optional[bool] = None
    phase1_skipped: List[str] = []
    if _PHASE1_ENABLED:
        phase1_skipped = ["postprocess", "insights"]

    def _log_request_start(goal_value: Optional[Any]) -> None:
        nonlocal log_started
        if log_started:
            return
        logger.info(
            "API: handle_message start request_id=%s payload_bytes=%s goal_id=%s",
            request_id,
            payload_bytes,
            goal_value,
        )
        log_started = True

    def _log_request_end() -> None:
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        logger.info(
            "API: handle_message done request_id=%s elapsed_ms=%s goal_events_ok=%s",
            request_id,
            elapsed_ms,
            event_storage_ok,
        )
    try:
        if not request.is_json:
            _log_request_start(None)
            return api_error("VALIDATION_ERROR", "JSON body required", 400)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            _log_request_start(None)
            return api_error("VALIDATION_ERROR", "JSON object required", 400)
        raw_user_input = data.get("message")
        if raw_user_input is None:
            raw_user_input = ""
        if not isinstance(raw_user_input, str):
            raw_user_input = str(raw_user_input)
        user_input = raw_user_input.strip()
        raw_goal_id = data.get("goal_id")
        goal_id_source = "goal_id"
        if raw_goal_id is None:
            raw_goal_id = data.get("active_goal_id")
            goal_id_source = "active_goal_id"
        raw_ui_action = data.get("ui_action")
        if raw_ui_action is None:
            raw_ui_action = data.get("uiAction")
        ui_action = raw_ui_action.strip().lower() if isinstance(raw_ui_action, str) else ""
        current_mode = (data.get("current_mode") or "companion").strip().lower()
        current_view = data.get("current_view")
        raw_channel = data.get("channel")
        view_label = str(current_view or "chat")
        is_chat_view = view_label.strip().lower() == "chat"
        incoming_channel = str(raw_channel or "").strip().lower() or None
        effective_channel = "companion" if is_chat_view else (incoming_channel or "companion")
        if effective_channel not in {"companion", "planner"}:
            effective_channel = "companion"
        raw_client_message_id = data.get("client_message_id")
        if raw_client_message_id is None:
            raw_client_message_id = data.get("clientMessageId")
        client_message_id = None
        if raw_client_message_id is not None:
            client_message_id = str(raw_client_message_id).strip() or None

        raw_conversation_id = data.get("conversation_id")
        conversation_id = None
        if raw_conversation_id is not None:
            try:
                conversation_id = int(raw_conversation_id)
            except (ValueError, TypeError):
                pass

        logger.info(
            "API: message meta request_id=%s current_view=%s current_mode=%s keys=%s goal_id=%s active_goal_id=%s conversation_id=%s",
            request_id,
            current_view,
            current_mode,
            list(data.keys()),
            data.get("goal_id"),
            data.get("active_goal_id"),
            conversation_id,
        )

        _log_request_start(raw_goal_id)

        # Allow empty message if ui_action is present (e.g. confirm_draft, dismiss_draft)
        if not user_input and not ui_action:
            return api_error("VALIDATION_ERROR", "message is required", 400)

        logger.info("API: Received message: %s request_id=%s", user_input[:100], request_id)

        user_id, user_error = _get_user_id_or_error()
        if user_error:
            if session.get("authed"):
                return user_error
            user_id = None

        # Draft Focus: Confirm Goal Intent
        # Tightened routing:
        # A) data.ui_action == "confirm_draft"
        # B) user_input == "confirm goal" (exact)
        # C) user_input == "confirm" ONLY if draft_id is present
        is_confirm_action = data.get("ui_action") == "confirm_draft"
        is_confirm_goal_text = user_input.strip().lower() == "confirm goal"
        is_confirm_text_with_id = user_input.strip().lower() == "confirm" and data.get("draft_id")

        if user_id and (is_confirm_action or is_confirm_goal_text or is_confirm_text_with_id):
            draft_id = data.get("draft_id")
            
            if draft_id:
                # Verify it exists and is pending
                try:
                    draft_id = int(draft_id)
                    draft = suggestions_repository.get_suggestion(user_id, draft_id)
                    if not draft or draft.get("status") != "pending":
                        draft = None # Invalid draft_id provided
                except (ValueError, TypeError):
                    draft = None
            elif is_confirm_goal_text:
                # Find latest pending goal draft ONLY if explicit "confirm goal"
                pending_drafts = suggestions_repository.list_suggestions(
                    user_id=user_id,
                    status="pending",
                    kind="goal",
                    limit=1
                )
                # list_suggestions orders by created_at DESC
                draft = pending_drafts[0] if pending_drafts else None
            else:
                draft = None
            
            if draft:
                draft_id = draft["id"]
                
                # --- PHASE 13: Sanitize Payload ---
                current_payload = draft.get("payload") or {}
                
                # 1. Title
                title = str(current_payload.get("title", "")).strip()
                if not title:
                    title = "New Goal"
                
                # 2. Target Days
                try:
                    target_days = int(current_payload.get("target_days", 7))
                except:
                    target_days = 7
                
                # 3. Steps
                raw_steps = current_payload.get("steps", [])
                if not isinstance(raw_steps, list):
                    raw_steps = []
                
                # Filter blanks & Dedupe
                steps = []
                seen = set()
                for s in raw_steps:
                    s_str = str(s).strip()
                    if s_str:
                        k = s_str.lower()
                        if k not in seen:
                            seen.add(k)
                            steps.append(s_str)
                
                # 4. Body
                body = str(current_payload.get("body", "")).strip()
                
                # Update Payload
                sanitized_payload = {
                    "title": title,
                    "target_days": target_days,
                    "steps": steps,
                    "body": body
                }
                
                # Persist sanitized payload before confirming
                suggestions_repository.update_suggestion_payload(user_id, draft_id, sanitized_payload)

                # Apply decision (Accept)
                results = _apply_suggestion_decisions(
                    user_id, 
                    [{"suggestion_id": draft_id, "action": "accept", "reason": "user_confirmed_via_chat"}],
                    event_source="api_message_confirm"
                )
                
                if results and results[0].get("ok"):
                    res = results[0]
                    saved_goal = res.get("goal")
                    goal_id = saved_goal.get("id") if saved_goal else None
                    
                    meta = {}
                    if not steps:
                        meta["steps_empty"] = True

                    return jsonify({
                        "reply": f"Goal confirmed! I've saved '{saved_goal.get('title')}' and set it as your active focus.",
                        "saved_goal": {
                            "goal_id": goal_id, 
                            "title": saved_goal.get("title"),
                            "target_days": target_days,
                            "steps_count": len(steps)
                        },
                        "draft_cleared": True,
                        "active_goal_id": goal_id,
                        "agent_status": {"planner_active": True},
                        "request_id": request_id,
                        "meta": meta
                    })
            
            # If no draft found or confirm failed
            return jsonify({
                "reply": "PENDING_GOAL_DRAFT_MISSING. I couldn't find a pending goal draft to confirm. Try describing your goal again.",
                "agent_status": {},
                "request_id": request_id
            })

        # Draft Focus: Dismiss Draft
        if user_id and data.get("ui_action") == "dismiss_draft":
            draft_id = data.get("draft_id")
            if draft_id:
                try:
                    draft_id = int(draft_id)
                    suggestions_repository.update_suggestion_status(
                        user_id, 
                        draft_id, 
                        "dismissed", 
                        decided_reason="user_dismissed_via_ui"
                    )
                    return jsonify({
                        "reply": "Draft dismissed.",
                        "dismissed_draft_id": draft_id,
                        "request_id": request_id
                    })
                except (ValueError, TypeError):
                    pass
            return jsonify({
                "reply": "Could not dismiss draft.",
                "request_id": request_id
            })

        # Draft Focus: Create Draft (Voice-First)
        # Trigger: "create a goal draft", "start a goal draft", etc.
        is_create_draft = False
        if user_id and user_input:
            norm_input = user_input.strip().lower()
            if "create a goal draft" in norm_input or "start a goal draft" in norm_input:
                is_create_draft = True
            elif re.search(r"\b(create|make|start)\b.*\bgoal\b.*\bdraft\b", norm_input):
                is_create_draft = True
        
        if is_create_draft:
            payload = _generate_goal_draft_payload(user_input)
            suggestion = suggestions_repository.create_suggestion(
                user_id=user_id,
                kind="goal",
                payload=payload,
                provenance={"source": "api_message_create_goal_draft", "original_text": user_input},
                status="pending"
            )
            
            draft_id = suggestion["id"]
            
            # Construct response with draft context
            response = {
                "reply": "I've drafted that goal for you. What would you like to change first?",
                "draft_context": {
                    "draft_id": draft_id,
                    "draft_type": "goal",
                    "source_message_id": client_message_id
                },
                "draft_payload": payload,
                "request_id": request_id
            }
            
            # Add to meta.suggestions for completeness
            meta = response.setdefault("meta", {})
            suggestions = meta.setdefault("suggestions", [])
            suggestion_out = dict(suggestion)
            suggestion_out["suggestion_id"] = draft_id
            suggestions.append(suggestion_out)
            
            return jsonify(response)

        # Draft Focus: Edit Draft (While Pending)
        # Trigger: draft_id present + draft_type="goal" + NO ui_action
        if user_id and data.get("draft_id") and data.get("draft_type") == "goal" and not ui_action:
            draft_id = data.get("draft_id")
            logger.info("Draft edit lane draft_id=%s", draft_id)
            try:
                draft_id = int(draft_id)
                draft = suggestions_repository.get_suggestion(user_id, draft_id)
                
                if draft and draft.get("status") == "pending":
                    # This is an edit instruction
                    current_payload = draft.get("payload", {})
                    
                    # 1. Try deterministic edit
                    updated_payload, handled, reply_suffix = _apply_goal_draft_deterministic_edit(current_payload, user_input)
                    
                    # 2. Fallback to LLM if not handled (Semantic Edit)
                    if not handled:
                        updated_payload = _patch_goal_draft_payload(current_payload, user_input)
                        reply_suffix = "Updated the draft."
                        
                        # Auto-Generate Logic (Voice Flow) - Tightened
                        # Only auto-generate if we previously flagged this draft as needing seed steps (via clarification)
                        # OR if it's very clearly an initial elaboration.
                        needs_seed_steps = updated_payload.get("needs_seed_steps")
                        if not updated_payload.get("steps"):
                             new_body = updated_payload.get("body") or ""
                             # Explicitly check the flag set by clarify_goal_intent
                             if needs_seed_steps and len(new_body) > 5:
                                 updated_payload = _generate_draft_steps_payload(updated_payload)
                                 # Clear the flag
                                 updated_payload.pop("needs_seed_steps", None)
                                 steps_count = len(updated_payload.get("steps", []))
                                 if steps_count > 0:
                                     reply_suffix += f" I've also auto-generated {steps_count} starting steps for you."
                             elif needs_seed_steps:
                                 # Keep the flag if body is too short
                                 pass

                    # Diff Logic (Step Diff) - Computed AFTER all updates
                    diff_meta = {}
                    before_steps = current_payload.get("steps", []) or []
                    after_steps = updated_payload.get("steps", []) or []
                    
                    if len(before_steps) != len(after_steps) or before_steps != after_steps:
                        # Simple diff detection
                        diff_meta["goal_title"] = updated_payload.get("title", "Goal")
                        diff_meta["steps_changed"] = True
                        
                        # Try to find specific index change
                        if len(before_steps) == len(after_steps):
                            for i, (b, a) in enumerate(zip(before_steps, after_steps)):
                                if b != a:
                                    diff_meta["step_index"] = i + 1
                                    diff_meta["before_text"] = b
                                    diff_meta["after_text"] = a
                                    break
                    
                    # Update DB
                    updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                    
                    title = updated_payload.get("title", "Goal")
                    steps_count = len(updated_payload.get("steps", []))
                    
                    # Format Response with Diff - Safe
                    reply_msg = f"{reply_suffix}"
                    if diff_meta.get("steps_changed"):
                        if diff_meta.get("step_index") and diff_meta.get("before_text") and diff_meta.get("after_text"):
                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated step {diff_meta['step_index']}\nBefore: {diff_meta['before_text']}\nAfter: {diff_meta['after_text']}"
                        else:
                            # Steps added/removed or multiple changes
                            # Limit to first 3 steps in summary to keep it concise? Or just count.
                            step_list_str = ", ".join([f"{i+1}. {s}" for i, s in enumerate(after_steps[:3])])
                            if len(after_steps) > 3: step_list_str += "..."
                            reply_msg = f"{diff_meta.get('goal_title', 'Goal')}\nUpdated steps.\nNow: {step_list_str}"
                    elif not reply_msg.strip():
                         reply_msg = f"Draft: '{title}' ({steps_count} steps)."
                    else:
                         # Append summary if not a diff
                         reply_msg += f" Draft: '{title}' ({steps_count} steps)."

                    response = {
                        "reply": reply_msg,
                        "draft_context": {
                            "draft_id": draft_id,
                            "draft_type": "goal",
                            "source_message_id": client_message_id
                        },
                        "draft_payload": updated_payload,
                        "request_id": request_id
                    }
                    return jsonify(response)
                    
            except (ValueError, TypeError):
                pass

        # Draft Focus: Generate Steps
        # Trigger: ui_action="generate_draft_steps" OR voice command "generate steps" with active draft
        is_generate_steps = (ui_action == "generate_draft_steps")
        is_regenerate_steps = (ui_action == "regenerate_draft_steps")
        
        if not (is_generate_steps or is_regenerate_steps) and user_id and data.get("draft_id") and data.get("draft_type") == "goal":
             norm_input = user_input.strip().lower()
             if "generate steps" in norm_input or "suggest steps" in norm_input:
                 is_generate_steps = True
             elif "regenerate steps" in norm_input:
                 is_regenerate_steps = True

        if (is_generate_steps or is_regenerate_steps) and user_id and data.get("draft_id"):
            draft_id = data.get("draft_id")
            try:
                draft_id = int(draft_id)
                draft = suggestions_repository.get_suggestion(user_id, draft_id)
                
                if draft and draft.get("status") == "pending":
                    current_payload = draft.get("payload", {})
                    if isinstance(current_payload, str):
                        try:
                            current_payload = json.loads(current_payload)
                        except:
                            current_payload = {}

                    # Normalize existing steps
                    existing_steps = current_payload.get("steps", [])
                    if not isinstance(existing_steps, list):
                        existing_steps = []
                    existing_steps = [str(s).strip() for s in existing_steps if str(s).strip()]
                    
                    # Idempotency check (only for generate, not regenerate)
                    if is_generate_steps and len(existing_steps) >= 5:
                        response = {
                            "reply": f"Steps already generated ({len(existing_steps)}). Say 'regenerate steps' to replace them.",
                            "draft_context": {
                                "draft_id": draft_id,
                                "draft_type": "goal",
                                "source_message_id": client_message_id
                            },
                            "draft_payload": current_payload, # Return normalized? No, keep as is but maybe update DB if we normalized? 
                            # Actually let's update DB with normalized steps just in case
                            "request_id": request_id
                        }
                        # Update DB with normalized steps to be safe
                        current_payload["steps"] = existing_steps
                        suggestions_repository.update_suggestion_payload(user_id, draft_id, current_payload)
                        response["draft_payload"] = current_payload
                        return jsonify(response)

                    # Call LLM
                    # If regenerating, we might want to clear steps or pass them as context to replace?
                    # The prompt says "Keep existing... unless missing".
                    # For regenerate, we probably want fresh ideas, but let's stick to the requested logic:
                    # "Fill to 5, preserving existing steps" for generate.
                    # For regenerate, maybe we clear them first?
                    # The user requirement says: "Regenerate... This is the explicit 'replace' path".
                    
                    payload_to_process = current_payload.copy()
                    payload_to_process["steps"] = existing_steps # Use normalized
                    
                    if is_regenerate_steps:
                        # Clear steps for regeneration so LLM generates fresh ones
                        payload_to_process["steps"] = []
                    
                    updated_payload = _generate_draft_steps_payload(payload_to_process)
                    
                    # Fallback Logic & Post-processing
                    steps = updated_payload.get("steps", [])
                    if not isinstance(steps, list):
                        steps = []
                    
                    # Sanitize steps
                    steps = [str(s).strip() for s in steps if str(s).strip()]
                    
                    # Deduplicate (case-insensitive)
                    seen = set()
                    deduped_steps = []
                    for s in steps:
                        k = s.lower()
                        if k not in seen:
                            seen.add(k)
                            deduped_steps.append(s)
                    steps = deduped_steps
                    
                    used_fallback = False
                    if not steps:
                        used_fallback = True
                        steps = [
                            "Define success criteria",
                            "Break down into sub-tasks",
                            f"Schedule daily work for {updated_payload.get('target_days', 7)} days",
                            "Execute and track progress",
                            "Review and adjust"
                        ]
                        logging.warning(f"Used fallback steps for draft {draft_id}")
                    
                    # Ensure at least 5 steps if we have fewer (pad with generics if needed, but avoid dupes)
                    # Only if we are in generate/regenerate mode which implies we want a full plan.
                    if len(steps) < 5:
                        defaults = [
                            "Define success criteria",
                            "Break down into sub-tasks",
                            "Identify resources needed",
                            "Set milestones",
                            "Execute and track progress",
                            "Review and adjust",
                            "Celebrate completion"
                        ]
                        for d in defaults:
                            if len(steps) >= 5:
                                break
                            if d.lower() not in seen:
                                steps.append(d)
                                seen.add(d.lower())

                    updated_payload["steps"] = steps

                    # Update DB
                    updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                    
                    steps_count = len(steps)
                    reply_text = f"I've generated {steps_count} steps for your goal:"
                    for i, s in enumerate(steps, 1):
                        reply_text += f"\n{i}) {s}"
                    
                    response = {
                        "reply": reply_text,
                        "draft_context": {
                            "draft_id": draft_id,
                            "draft_type": "goal",
                            "source_message_id": client_message_id
                        },
                        "draft_payload": updated_payload,
                        "request_id": request_id
                    }
                    
                    meta = response.setdefault("meta", {})
                    meta["used_fallback_steps"] = used_fallback
                    
                    return jsonify(response)
            except (ValueError, TypeError):
                pass

        # Phase 18: Show Seed Steps
        # Trigger: ui_action="show_seed_steps" or text command "show seed steps"
        is_show_steps = (ui_action == "show_seed_steps")
        if not is_show_steps and user_input:
             if re.search(r"^(show|list)\s+((me|the)\s+)?(seed\s+)?steps", user_input.strip().lower()):
                 is_show_steps = True

        if is_show_steps and user_id:
            target_goal_id = data.get("goal_id") or data.get("active_goal_id")
            if target_goal_id:
                try:
                    target_goal_id = int(target_goal_id)
                    goal = goals_repository.get_goal(target_goal_id, user_id)
                    if goal:
                        checklist = goal.get("checklist", [])
                        if not checklist:
                             reply = f"Goal '{goal.get('title')}' has no seed steps recorded."
                        else:
                             reply = f"Seed Steps for '{goal.get('title')}':\n"
                             for i, step in enumerate(checklist, 1):
                                 txt = step if isinstance(step, str) else step.get('text', str(step))
                                 reply += f"\n{i}. {txt}"
                        
                        return jsonify({
                            "reply": reply,
                            "agent_status": {"planner_active": False},
                            "request_id": request_id
                        })
                except Exception as e:
                    logger.error(f"Error fetching seed steps: {e}")
                    pass
            elif is_show_steps and ui_action == "show_seed_steps":
                 return jsonify({
                    "reply": "Please select a goal first.",
                    "request_id": request_id
                 })

        # Phase 18: Intent Clarification
        if user_id and ui_action == "clarify_goal_intent":
             # Phase 20: If confirming a draft, flag it for auto-seed steps
             if data.get("draft_id"):
                 try:
                     did = int(data.get("draft_id"))
                     d = suggestions_repository.get_suggestion(user_id, did)
                     if d and d.get("status") == "pending":
                         p = d.get("payload", {})
                         p["needs_seed_steps"] = True
                         suggestions_repository.update_suggestion_payload(user_id, did, p)
                 except (ValueError, TypeError):
                     pass

             # Force the agent to ask clarifying questions
             user_input = "Please ask me 1-3 targeted clarifying questions to help me refine the intent of this goal. Be concise."

        # --- Phase 3.2: Chat Command Router ---
        if user_id:
            cmd_text = user_input.strip().lower()
            
            # 1. Generate Proposals
            if cmd_text in ("/suggest", "/proposals", "suggest plan", "suggest changes"):
                try:
                    local_today = _get_local_today(user_id)
                    proposals = _generate_proposals_core(user_id, local_today)
                    count = len(proposals)
                    
                    if count > 0:
                        reply = f"Generated {count} proposal{'s' if count != 1 else ''}:\n\n"
                        for p in proposals:
                            reply += f"ID {p['proposal_id']}: {p['title']} - {p['summary']}\n"
                        reply += "\nUse '/accept <id>' or '/reject <id>'."
                    else:
                        # Check if duplicates were skipped by listing pending
                        pending = _get_last_pending_proposals(user_id, local_today.isoformat(), limit=5)
                        if pending:
                            reply = "No new proposals (duplicates skipped). Pending:\n\n"
                            for p in pending:
                                reply += f"ID {p['proposal_id']}: {p['title']} - {p['summary']}\n"
                            reply += "\nUse '/accept <id>' or '/reject <id>'."
                        else:
                            reply = "No new proposals found."
                    
                    return jsonify({
                        "reply": reply,
                        "agent_status": {"planner_active": False},
                        "request_id": request_id
                    })
                except Exception as e:
                    logger.error(f"Command /suggest failed: {e}")
                    return jsonify({
                        "reply": "Failed to generate proposals.",
                        "agent_status": {},
                        "request_id": request_id
                    })

            # 2. List Proposals / Last
            if cmd_text in ("/suggestions", "/proposals list", "/pending", "/last"):
                try:
                    local_today = _get_local_today(user_id)
                    limit = 3 if cmd_text == "/last" else 100
                    proposals = _get_last_pending_proposals(user_id, local_today.isoformat(), limit=limit)
                    
                    if not proposals:
                        reply = "No pending proposals for today."
                    else:
                        reply = f"{'Most recent' if cmd_text == '/last' else 'Pending'} proposals:\n\n"
                        for p in proposals:
                            reply += f"ID {p['proposal_id']}: {p['title']} - {p['summary']}\n"
                        reply += "\nUse '/accept <id>' or '/reject <id>'."
                    
                    return jsonify({
                        "reply": reply,
                        "agent_status": {},
                        "request_id": request_id
                    })
                except Exception as e:
                    logger.error(f"Command /list failed: {e}")
                    return jsonify({
                        "reply": "Failed to list proposals.",
                        "agent_status": {},
                        "request_id": request_id
                    })

            # 3. Accept/Reject (Specific or Last or A/B)
            accept_match = re.match(r"^/accept\s+(a|b|last|\d+)$", cmd_text, re.IGNORECASE)
            reject_match = re.match(r"^/reject\s+(a|b|last|\d+)$", cmd_text, re.IGNORECASE)
            
            if accept_match:
                target = accept_match.group(1).lower()
                p_id = None
                is_batch_selection = False
                
                if target in ("a", "b"):
                    local_today = _get_local_today(user_id)
                    cached = _get_valid_ai2_batch_cache(user_id, local_today)
                    if cached:
                        if target == "a": p_id = cached.get("option_a")
                        elif target == "b": p_id = cached.get("option_b")
                        is_batch_selection = True
                    
                    if not p_id:
                        return jsonify({"reply": f"Option '{target.upper()}' not found in active batch (expired or invalid).", "agent_status": {}, "request_id": request_id})

                elif target == "last":
                    local_today = _get_local_today(user_id)
                    last_props = _get_last_pending_proposals(user_id, local_today.isoformat(), limit=1)
                    if last_props:
                        p_id = last_props[0]["proposal_id"]
                    else:
                        return jsonify({"reply": "No pending proposals for today.", "agent_status": {}, "request_id": request_id})
                else:
                    p_id = int(target)

                ok, status, detail = _apply_proposal_core(user_id, p_id)
                if ok:
                    if is_batch_selection:
                        AI2_BATCH_CACHE.pop(user_id, None)
                    reply = f"Accepted proposal {p_id}. Plan updated."
                else:
                    reply = f"Failed to accept proposal {p_id}: {status} ({detail})"
                return jsonify({
                    "reply": reply,
                    "agent_status": {},
                    "request_id": request_id
                })
            
            if reject_match:
                target = reject_match.group(1).lower()
                p_id = None
                
                if target in ("a", "b"):
                    local_today = _get_local_today(user_id)
                    cached = _get_valid_ai2_batch_cache(user_id, local_today)
                    if cached:
                        if target == "a": p_id = cached.get("option_a")
                        elif target == "b": p_id = cached.get("option_b")
                    
                    if not p_id:
                        return jsonify({"reply": f"Option '{target.upper()}' not found in active batch.", "agent_status": {}, "request_id": request_id})

                elif target == "last":
                    local_today = _get_local_today(user_id)
                    last_props = _get_last_pending_proposals(user_id, local_today.isoformat(), limit=1)
                    if last_props:
                        p_id = last_props[0]["proposal_id"]
                    else:
                        return jsonify({"reply": "No pending proposals for today.", "agent_status": {}, "request_id": request_id})
                else:
                    p_id = int(target)

                ok, status, detail = _reject_proposal_core(user_id, p_id)
                if ok:
                    reply = f"Rejected proposal {p_id}."
                else:
                    reply = f"Failed to reject proposal {p_id}: {status} ({detail})"
                return jsonify({
                    "reply": reply,
                    "agent_status": {},
                    "request_id": request_id
                })

            # 4. Preview
            preview_match = re.match(r"^/preview\s+(a|b|last|\d+)$", cmd_text, re.IGNORECASE)
            if preview_match:
                target = preview_match.group(1).lower()
                p_id = None
                local_today = _get_local_today(user_id)
                
                if target in ("a", "b"):
                    cached = _get_valid_ai2_batch_cache(user_id, local_today)
                    if cached:
                        if target == "a": p_id = cached.get("option_a")
                        elif target == "b": p_id = cached.get("option_b")
                    
                    if not p_id:
                        return jsonify({"reply": f"Option '{target.upper()}' not found in active batch.", "agent_status": {}, "request_id": request_id})

                elif target == "last":
                    last_props = _get_last_pending_proposals(user_id, local_today.isoformat(), limit=1)
                    if last_props:
                        p_id = last_props[0]["proposal_id"]
                    else:
                        return jsonify({"reply": "No pending proposals for today.", "agent_status": {}, "request_id": request_id})
                else:
                    p_id = int(target)
                
                # Fetch proposal payload
                proposal_data = None
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT payload, status FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal'",
                            (p_id, user_id)
                        )
                        row = cursor.fetchone()
                        if row:
                            proposal_data = row[0]
                            p_status = row[1]
                
                if not proposal_data:
                    return jsonify({"reply": f"Proposal {p_id} not found.", "agent_status": {}, "request_id": request_id})
                
                # Load plan for context
                comps = get_agent_components()
                othello_engine = comps["othello_engine"]
                plan = othello_engine.day_planner.get_today_plan(user_id, force_regen=False, plan_date=local_today)
                
                preview_text = _format_proposal_preview(plan, proposal_data)

                reply = f"Preview proposal {p_id}: {proposal_data.get('title', 'Untitled')}\n"
                if p_status != "pending":
                    reply += f"(Status: {p_status})\n"
                reply += "\n" + preview_text
                
                return jsonify({
                    "reply": reply,
                    "agent_status": {},
                    "request_id": request_id
                })

            # 5. Cleanup
            cleanup_match = re.match(r"^/cleanup(?:\s+(\d+))?$", cmd_text)
            if cleanup_match:
                days_str = cleanup_match.group(1)
                days = int(days_str) if days_str else 14
                # Clamp to [1, 90]
                days = max(1, min(90, days))
                
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                
                accepted_count = 0
                rejected_count = 0
                total_count = 0
                
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            DELETE FROM suggestions 
                            WHERE user_id = %s 
                              AND kind = 'plan_proposal' 
                              AND status IN ('accepted', 'rejected') 
                              AND created_at < %s
                            RETURNING status
                            """,
                            (user_id, cutoff)
                        )
                        rows = cursor.fetchall()
                        total_count = len(rows)
                        for r in rows:
                            if r[0] == 'accepted':
                                accepted_count += 1
                            elif r[0] == 'rejected':
                                rejected_count += 1
                        conn.commit()
                
                return jsonify({
                    "reply": f"Cleanup complete: {total_count} removed (accepted={accepted_count}, rejected={rejected_count}) older than {days}d.",
                    "agent_status": {},
                    "request_id": request_id
                })

            # 6. Cancel Applying
            cancel_match = re.match(r"^/cancel\s+applying(?:\s+(last|\d+))?$", cmd_text)
            if cancel_match:
                target = cancel_match.group(1) or "last"
                p_id = None
                created_at = None
                
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        if target == "last":
                            cursor.execute(
                                """
                                SELECT id, created_at FROM suggestions 
                                WHERE user_id = %s 
                                  AND kind = 'plan_proposal' 
                                  AND status = 'applying'
                                ORDER BY created_at DESC LIMIT 1
                                """,
                                (user_id,)
                            )
                            row = cursor.fetchone()
                            if row:
                                p_id = row[0]
                                created_at = row[1]
                            else:
                                return jsonify({"reply": "No applying proposal found.", "agent_status": {}, "request_id": request_id})
                        else:
                            p_id = int(target)
                            cursor.execute(
                                "SELECT created_at FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal' AND status = 'applying'",
                                (p_id, user_id)
                            )
                            row = cursor.fetchone()
                            if row:
                                created_at = row[0]
                            else:
                                return jsonify({"reply": f"Proposal {p_id} is not in 'applying' state or not found.", "agent_status": {}, "request_id": request_id})

                        # Check staleness
                        if created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                        
                        stale_threshold = datetime.now(timezone.utc) - timedelta(minutes=10)
                        
                        if created_at > stale_threshold:
                             return jsonify({"reply": "Cannot cancel yet (not stale). Try again later.", "agent_status": {}, "request_id": request_id})
                        
                        cursor.execute(
                            "UPDATE suggestions SET status = 'pending' WHERE id = %s",
                            (p_id,)
                        )
                        conn.commit()
                        
                        return jsonify({
                            "reply": f"Cancelled applying; proposal reset to pending: {p_id}.",
                            "agent_status": {},
                            "request_id": request_id
                        })

            # 6.4 Pick (AI2 Selection - Read Only)
            if cmd_text.startswith("/ai2") or cmd_text.startswith("/pick "):
                is_pick = cmd_text.startswith("/pick ")
                pick_target = cmd_text[6:].strip().lower() if is_pick else None
                
                local_today = _get_local_today(user_id)
                cached = _get_valid_ai2_batch_cache(user_id, local_today)
                
                if not cached:
                    return jsonify({"reply": "No active AI2 batch found (expired or lost). Please rerun: /propose ai2 <request>", "agent_status": {}, "request_id": request_id})
                
                # /ai2 (Inspect)
                if not is_pick:
                    created_at = cached.get("created_at", 0)
                    age = int(datetime.now(timezone.utc).timestamp() - created_at)
                    ttl_rem = max(0, AI2_BATCH_TTL_SECONDS - age)
                    
                    lines = [f"Active AI2 Batch (expires in {ttl_rem}s):"]
                    if cached.get("option_a"): lines.append(f"Option A: ID {cached['option_a']}")
                    if cached.get("option_b"): lines.append(f"Option B: ID {cached['option_b']}")
                    lines.append("\nUse '/preview a' or '/preview b' to see details.")
                    lines.append("Use '/accept a' or '/accept b' to apply.")
                    
                    return jsonify({"reply": "\n".join(lines), "agent_status": {}, "request_id": request_id})

                # /pick (Preview + Guidance)
                target_id = None
                if pick_target == "a":
                    target_id = cached.get("option_a")
                elif pick_target == "b":
                    target_id = cached.get("option_b")
                
                if not target_id:
                    return jsonify({"reply": f"Option '{pick_target}' not available in this batch.", "agent_status": {}, "request_id": request_id})
                
                # Fetch proposal payload for preview
                proposal_data = None
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT payload, status FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal'",
                            (target_id, user_id)
                        )
                        row = cursor.fetchone()
                        if row:
                            proposal_data = row[0]
                            p_status = row[1]
                
                if not proposal_data:
                    return jsonify({"reply": f"Proposal {target_id} not found.", "agent_status": {}, "request_id": request_id})

                # Load plan for context
                comps = get_agent_components()
                othello_engine = comps["othello_engine"]
                plan = othello_engine.day_planner.get_today_plan(user_id, force_regen=False, plan_date=local_today)
                
                preview_text = _format_proposal_preview(plan, proposal_data)
                
                reply = (
                    f"Selected Option {pick_target.upper()} (ID {target_id}).\n"
                    f"Run: /accept {pick_target} (or /accept {target_id}) to confirm.\n\n"
                    f"{preview_text}"
                )
                
                return jsonify({
                    "reply": reply,
                    "agent_status": {},
                    "request_id": request_id
                })

            # 6.5 Use (Clarification Response)
            if cmd_text.startswith("/use "):
                try:
                    idx_str = cmd_text[5:].strip()
                    idx = int(idx_str)
                    
                    local_today = _get_local_today(user_id)
                    cached = _get_valid_clarification_cache(user_id, local_today)
                    
                    if not cached:
                        return jsonify({"reply": "No active clarification found (expired or lost). Please rerun: /propose ai <your request>", "agent_status": {}, "request_id": request_id})
                    
                    candidates = cached["candidates"]
                    if idx < 1 or idx > len(candidates):
                        return jsonify({"reply": f"Invalid selection. Choose 1-{len(candidates)}.", "agent_status": {}, "request_id": request_id})
                        
                    selected = candidates[idx-1]
                    item_id = selected["item_id"]
                    orig_req = cached.get("request", "...")
                    
                    # Clear cache to prevent replay
                    CLARIFICATION_CACHE.pop(user_id, None)
                    
                    reply = (
                        f"Selected: {selected['label']} (ID {item_id}).\n"
                        f"Please run:\n"
                        f"/propose ai {orig_req} item {item_id}"
                    )
                    return jsonify({"reply": reply, "agent_status": {}, "request_id": request_id})
                except ValueError:
                    return jsonify({"reply": "Usage: /use <number>", "agent_status": {}, "request_id": request_id})

            # 7. Propose (Deterministic Intent or AI)
            if cmd_text.startswith("/propose "):
                propose_text = cmd_text[9:].strip()
                
                # AI2 Branch (Alternatives)
                if propose_text.startswith("ai2 "):
                    user_request = propose_text[4:].strip()
                    if not user_request:
                        return jsonify({"reply": "Usage: /propose ai2 <request>", "agent_status": {}, "request_id": request_id})
                    
                    try:
                        comps = get_agent_components()
                        othello_engine = comps["othello_engine"]
                        local_today = _get_local_today(user_id)
                        plan = othello_engine.day_planner.get_today_plan(user_id, force_regen=False, plan_date=local_today)
                        if not plan: return jsonify({"reply": "No active plan.", "agent_status": {}, "request_id": request_id})
                        
                        plan_context, valid_ids = _build_plan_context_for_llm(plan)
                        from core.llm_wrapper import LLMWrapper
                        from utils.prompts import load_prompt
                        
                        llm = LLMWrapper()
                        system_prompt = load_prompt("plan_proposal_generator_alternatives")
                        user_prompt = f"User Request: {user_request}\n\nCurrent Plan:\n{plan_context}"
                        
                        raw_response, attempts = _generate_llm_proposal_with_retry(llm, user_prompt, system_prompt)
                        result_data, error_code = _validate_and_parse_alternatives(raw_response, valid_ids)
                        
                        if not result_data:
                            return jsonify({"reply": f"Failed to generate alternatives: {error_code}", "agent_status": {}, "request_id": request_id})
                            
                        # Handle Clarification
                        if result_data.get("need_clarification"):
                            candidates = result_data.get("candidates", [])
                            CLARIFICATION_CACHE[user_id] = {
                                "candidates": candidates,
                                "request": user_request,
                                "created_at": datetime.now(timezone.utc).timestamp(),
                                "plan_date": local_today.isoformat(),
                                "request_id": request_id
                            }
                            lines = ["Which item did you mean?"]
                            for i, c in enumerate(candidates, 1):
                                lines.append(f"{i}) [{c['item_id']}] {c['label']}")
                            lines.append("\nReply: '/use <number>' or '/propose ai ... item <id>'")
                            return jsonify({"reply": "\n".join(lines), "agent_status": {}, "request_id": request_id})
                            
                        # Handle Alternatives
                        alts = result_data.get("alternatives", [])
                        reply_parts = []
                        labels = ["Option A", "Option B"]
                        
                        # Track IDs for caching
                        generated_ids = []
                        
                        # Generate Batch ID for persistence
                        batch_id = str(uuid.uuid4())

                        for i, alt in enumerate(alts):
                            if i >= 2: break
                            # Server-side cap
                            if len(alt.get("ops", [])) > 5: continue
                            
                            # Prefix title
                            alt["title"] = f"{labels[i]}: {alt.get('title')}"
                            alt["plan_date"] = local_today.isoformat()
                            
                            # Persist with batch info
                            provenance = {
                                "ai2_batch_id": batch_id,
                                "option_label": "A" if i == 0 else "B",
                                "plan_date": local_today.isoformat()
                            }
                            res = _save_proposal(user_id, alt, provenance_data=provenance)
                            
                            if res["status"] == "created":
                                pid = res['proposal_id']
                                generated_ids.append(pid)
                                preview = _format_proposal_preview(plan, alt)
                                reply_parts.append(
                                    f"{labels[i]} created: {pid} — {alt['title']}\n"
                                    f"{alt['summary']}\n"
                                    f"{preview}\n"
                                )
                        
                        if not reply_parts:
                            return jsonify({"reply": "Could not generate valid safe alternatives.", "agent_status": {}, "request_id": request_id})
                        
                        # Cache for /pick command
                        if len(generated_ids) > 0:
                            cache_entry = {
                                "created_at": datetime.now(timezone.utc).timestamp(),
                                "plan_date": local_today.isoformat(),
                                "request_id": request_id
                            }
                            if len(generated_ids) >= 1: cache_entry["option_a"] = generated_ids[0]
                            if len(generated_ids) >= 2: cache_entry["option_b"] = generated_ids[1]
                            AI2_BATCH_CACHE[user_id] = cache_entry

                        reply_parts.append("Use '/pick a' or '/pick b' (or '/accept <id>') to apply one option.")
                        return jsonify({"reply": "\n".join(reply_parts), "agent_status": {}, "request_id": request_id})
                        
                    except Exception as e:
                        logger.error(f"Command /propose ai2 failed: {e}", exc_info=True)
                        return jsonify({"reply": "Error generating alternatives.", "agent_status": {}, "request_id": request_id})

                # AI Branch
                if propose_text.startswith("ai "):
                    user_request = propose_text[3:].strip()
                    if not user_request:
                        return jsonify({"reply": "Usage: /propose ai <request>\nExample: /propose ai move gym to tomorrow", "agent_status": {}, "request_id": request_id})
                    
                    try:
                        # Load Plan Context
                        comps = get_agent_components()
                        othello_engine = comps["othello_engine"]
                        local_today = _get_local_today(user_id)
                        plan = othello_engine.day_planner.get_today_plan(user_id, force_regen=False, plan_date=local_today)
                        
                        if not plan:
                             return jsonify({"reply": "No active plan found for today. Cannot generate proposal.", "agent_status": {}, "request_id": request_id})

                        plan_context, valid_ids = _build_plan_context_for_llm(plan)
                        
                        # Call LLM
                        from core.llm_wrapper import LLMWrapper
                        from utils.prompts import load_prompt
                        
                        llm = LLMWrapper() # Uses env config
                        system_prompt = load_prompt("plan_proposal_generator")
                        user_prompt = f"User Request: {user_request}\n\nCurrent Plan:\n{plan_context}"
                        
                        # Retry Logic
                        raw_response, attempts = _generate_llm_proposal_with_retry(llm, user_prompt, system_prompt)
                        
                        # Validate
                        proposal, error_code = _validate_and_parse_llm_proposal(raw_response, valid_ids)
                        
                        if not proposal:
                             # Transparent Failure
                             reason = error_code or "UNKNOWN"
                             reply = (
                                 f"Couldn't form a safe proposal (reason: {reason}).\n"
                                 f"Attempts: {attempts}\n\n"
                                 "Try rephrasing, e.g.:\n"
                                 "- 'move item 123 to tomorrow'\n"
                                 "- 'snooze item 123 20'"
                             )
                             return jsonify({"reply": reply, "agent_status": {}, "request_id": request_id})

                        # Handle Clarification
                        if proposal.get("need_clarification"):
                            candidates = proposal.get("candidates", [])
                            CLARIFICATION_CACHE[user_id] = {
                                "candidates": candidates,
                                "request": user_request,
                                "created_at": datetime.now(timezone.utc).timestamp(),
                                "plan_date": local_today.isoformat(),
                                "request_id": request_id
                            }
                            lines = ["Which item did you mean?"]
                            for i, c in enumerate(candidates, 1):
                                lines.append(f"{i}) [{c['item_id']}] {c['label']}")
                            lines.append("\nReply: '/use <number>' or '/propose ai ... item <id>'")
                            return jsonify({"reply": "\n".join(lines), "agent_status": {}, "request_id": request_id})
                        
                        # Server-side Cap for AI Proposals
                        ops = proposal.get("ops", [])
                        if len(ops) > 5:
                            return jsonify({"reply": f"Too many steps for one AI proposal ({len(ops)}). Please break it into smaller requests.", "agent_status": {}, "request_id": request_id})
                             
                        # Save
                        result = _save_proposal(user_id, proposal)
                        if result["status"] == "created":
                            # Auto-preview
                            preview_text = _format_proposal_preview(plan, proposal)
                            reply = (
                                f"Created AI proposal {result['proposal_id']}: {proposal['title']}\n"
                                f"{proposal['summary']}\n\n"
                                f"{preview_text}\n\n"
                                f"Use '/accept {result['proposal_id']}' to apply, or '/reject {result['proposal_id']}' to discard."
                            )
                        elif result["status"] == "duplicate":
                            reply = f"Proposal already pending: {proposal['summary']}"
                        else:
                            reply = "Failed to save proposal."
                            
                        return jsonify({"reply": reply, "agent_status": {}, "request_id": request_id})

                    except Exception as e:
                        logger.error(f"Command /propose ai failed: {e}", exc_info=True)
                        return jsonify({"reply": "An error occurred while generating the proposal.", "agent_status": {}, "request_id": request_id})

                # Deterministic Branch (Existing)
                try:
                    proposal = _parse_propose_text_to_ops(user_id, propose_text)
                    if not proposal:
                        reply = f"Could not parse intent '{propose_text}'. Try 'start next', 'snooze', 'move <item>', or 'complete <item>'."
                    else:
                        result = _save_proposal(user_id, proposal)
                        if result["status"] == "created":
                            reply = f"Created proposal {result['proposal_id']}: {proposal['summary']}\nUse '/accept {result['proposal_id']}' to apply."
                        elif result["status"] == "duplicate":
                            reply = f"Proposal already pending: {proposal['summary']}"
                        else:
                            reply = "Failed to create proposal."
                    
                    return jsonify({
                        "reply": reply,
                        "agent_status": {},
                        "request_id": request_id
                    })
                except Exception as e:
                    logger.error(f"Command /propose failed: {e}")
                    return jsonify({
                        "reply": "Failed to process proposal.",
                        "agent_status": {},
                        "request_id": request_id
                    })

        def _should_persist_chat() -> bool:
            if not user_id:
                return False
            if not is_chat_view:
                return False
            if ui_action:
                return False
            if user_input.startswith("__"):
                return False
            return True

        companion_context = None
        persist_enabled = _should_persist_chat()
        if persist_enabled:
            companion_context = _load_companion_context(user_id, logger, channel=effective_channel, conversation_id=conversation_id)

        def _persist_chat_exchange(reply_text: Optional[str]) -> None:
            if not reply_text or not _should_persist_chat():
                return
            cleaned_reply = str(reply_text).strip()
            if not cleaned_reply:
                return
            try:
                from db.messages_repository import create_message

                create_message(
                    user_id=user_id,
                    transcript=user_input,
                    source="text",
                    channel=effective_channel,
                    status="final",
                    session_id=conversation_id,
                )
                create_message(
                    user_id=user_id,
                    transcript=cleaned_reply,
                    source="assistant",
                    channel=effective_channel,
                    status="final",
                    session_id=conversation_id,
                )
            except Exception as exc:
                logger.warning(
                    "API: chat persistence failed request_id=%s error=%s",
                    request_id,
                    type(exc).__name__,
                    exc_info=True,
                )

        def _respond(payload: Dict[str, Any]):
            reply_text = payload.get("reply") if isinstance(payload, dict) else None
            _persist_chat_exchange(reply_text)
            if isinstance(payload, dict) and conversation_id:
                payload["conversation_id"] = conversation_id
            return jsonify(payload)

        logger.info(
            "API: routing request_id=%s mode=%s view=%s incoming_channel=%s effective_channel=%s persist_chat=%s ctx_len=%s",
            request_id,
            current_mode,
            current_view,
            incoming_channel,
            effective_channel,
            persist_enabled,
            len(companion_context or []),
        )

        # Helper to detect positive routine intent
        def _has_positive_routine_intent(text: str) -> bool:
            t = (text or "").lower()
            if "no routine" in t or "do not create a routine" in t or "goal draft only" in t or "goal only" in t:
                return False
            # Explicit creation requests
            if "create a routine" in t or "make a routine" in t or "schedule this" in t or "set up a routine" in t:
                return True
            # Explicit schedule patterns
            if "every day" in t or "daily" in t or "weekly" in t:
                return True
            return False

        routine_response = None
        # If goal focus is active, suppress routine suggestions unless explicitly requested
        goal_focus_active = bool(raw_goal_id)
        should_check_routines = True
        if goal_focus_active and not _has_positive_routine_intent(user_input):
            should_check_routines = False

        if user_id and should_check_routines:
            try:
                from db.suggestions_repository import (
                    create_suggestion,
                    list_suggestions,
                    update_suggestion_payload,
                )
                pending = list_suggestions(user_id=user_id, status="pending", kind="routine", limit=1)
                if pending:
                    suggestion = pending[0]
                    payload = suggestion.get("payload") or {}
                    if payload.get("status") == "incomplete":
                        draft = payload.get("draft") or {}
                        missing_fields = list(payload.get("missing_fields") or [])
                        ambiguous_fields = list(payload.get("ambiguous_fields") or [])
                        time_local = _parse_routine_time_answer(user_input, draft)
                        if time_local:
                            draft["time_local"] = time_local
                            missing_fields = [f for f in missing_fields if f != "time_ampm"]
                            ambiguous_fields = [f for f in ambiguous_fields if f != "time_local"]
                            payload = _build_routine_suggestion_payload(draft, missing_fields, ambiguous_fields)
                            update_suggestion_payload(user_id, suggestion.get("id"), payload)
                        if payload.get("status") == "incomplete":
                            question = payload.get("clarifying_question") or "Do you mean am or pm?"
                            routine_response = {
                                "reply": question,
                                "request_id": request_id,
                                "meta": {
                                    "intent": "routine_clarify",
                                    "routine_suggestion_id": suggestion.get("id"),
                                },
                            }
                        else:
                            routine_response = {
                                "reply": _format_routine_summary(payload.get("draft") or {}),
                                "request_id": request_id,
                                "meta": {
                                "intent": "routine_ready",
                                "routine_suggestion_id": suggestion.get("id"),
                            },
                        }
                if not routine_response:
                    from core.conversation_parser import ConversationParser
                    from db.plan_repository import get_user_timezone
                    routine_parser = ConversationParser()
                    routine_candidates = routine_parser.extract_routines(user_input) or []
                    routine_drafts = [
                        routine for routine in routine_candidates
                        if isinstance(routine, dict) and routine.get("draft_type") == "schedule"
                    ]
                    if routine_drafts:
                        draft = dict(routine_drafts[0])
                        draft["timezone"] = get_user_timezone(user_id)
                        missing_fields = list(draft.get("missing_fields") or [])
                        ambiguous_fields = list(draft.get("ambiguous_fields") or [])
                        payload = _build_routine_suggestion_payload(draft, missing_fields, ambiguous_fields)
                        provenance = {
                            "source": "api_message_routine",
                            "detector": "routine_schedule_parser",
                            "request_id": request_id,
                        }
                        created = create_suggestion(
                            user_id=user_id,
                            kind="routine",
                            payload=payload,
                            provenance=provenance,
                        )
                        if created:
                            if payload.get("status") == "incomplete":
                                question = payload.get("clarifying_question") or "Do you mean am or pm?"
                                routine_response = {
                                    "reply": question,
                                    "request_id": request_id,
                                    "meta": {
                                        "intent": "routine_clarify",
                                        "routine_suggestion_id": created.get("id"),
                                    },
                                }
                            else:
                                routine_response = {
                                    "reply": _format_routine_summary(payload.get("draft") or {}),
                                    "request_id": request_id,
                                    "meta": {
                                        "intent": "routine_ready",
                                        "routine_suggestion_id": created.get("id"),
                                    },
                                }
            except Exception as exc:
                logger.warning("API: routine clarification failed: %s", exc, exc_info=True)

        if routine_response:
            return _respond(routine_response)

        if effective_channel == "companion" and companion_context:
            last_assistant = next(
                (msg for msg in reversed(companion_context) if msg.get("role") == "assistant"),
                None,
            )
            gate_prompt = False
            questions_prompt = False
            context_prompt = False
            if last_assistant:
                last_text = (last_assistant.get("content") or "").lower()
                gate_prompt = (
                    ("saved as a goal" in last_text and "broken into steps" in last_text) or
                    "saved that as a pending goal suggestion" in last_text
                )
                questions_prompt = "before i draft steps" in last_text and "quick questions" in last_text
                context_prompt = "tailor the questions" in last_text or "one line of context" in last_text
            if context_prompt:
                goal_text = _find_goal_text_in_context(companion_context)
                if not goal_text:
                    response = {
                        "reply": "What's the goal you want to break into steps?",
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_steps_questions"},
                    }
                    return _respond(response)
                questions_payload = _generate_goal_intake_questions(
                    goal_text=goal_text,
                    goal_title=None,
                    goal_description=None,
                    user_message=user_input,
                    recent_messages=companion_context,
                    user_id=user_id,
                    request_id=request_id,
                    logger=logger,
                )
                if questions_payload and questions_payload.get("need_more_context"):
                    reply_text = questions_payload.get("context_request") or ""
                elif questions_payload and questions_payload.get("questions"):
                    reply_text = _format_goal_questions_reply(goal_text, questions_payload.get("questions"))
                else:
                    reply_text = _format_goal_questions_reply(goal_text)
                response = {
                    "reply": reply_text,
                    "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                    "request_id": request_id,
                    "meta": {"intent": "goal_steps_questions"},
                }
                return _respond(response)
            if questions_prompt:
                goal_text = _find_goal_text_in_context(companion_context)
                if not goal_text:
                    response = {
                        "reply": "What's the goal you want to break into steps?",
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_steps_questions"},
                    }
                    return _respond(response)
                if not is_openai_configured():
                    steps = _fallback_steps_from_text(f"{goal_text}\n{user_input}")
                    lines = [
                        f"{step.get('step_index', idx)}. {step.get('description', '').strip()}"
                        for idx, step in enumerate(steps, start=1)
                        if step.get("description")
                    ]
                    reply_text = "Draft steps:\n" + "\n".join(lines)
                    response = {
                        "reply": reply_text,
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_steps_draft"},
                    }
                    return _respond(response)
                loop = None
                try:
                    comps = get_agent_components()
                    architect = comps["architect_agent"]
                    prompt = (
                        "Draft a concise numbered list of steps for the goal below.\n"
                        f"Goal: {goal_text}\n"
                        f"User answers: {user_input}\n"
                        "Return only the numbered list."
                    )
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    reply_text, _agent_status = loop.run_until_complete(
                        asyncio.wait_for(
                            architect.plan_and_execute(
                                prompt,
                                user_id=user_id,
                                recent_messages=companion_context,
                            ),
                            timeout=30.0
                        )
                    )
                except Exception as exc:
                    logger.error(
                        "API: steps question draft failed request_id=%s",
                        request_id,
                        exc_info=True,
                    )
                    llm_exc = _unwrap_llm_exception(exc)
                    if llm_exc:
                        return handle_llm_error(llm_exc, logger)
                    return api_error("STEP_DRAFT_FAILED", "Failed to draft steps", 500)
                finally:
                    if loop is not None:
                        try:
                            loop.close()
                        except Exception:
                            logger.debug("API: event loop close failed but continuing")
                cleaned_reply = (reply_text or "").strip()
                if not cleaned_reply:
                    response = {
                        "reply": "I couldn't draft steps from that yet. Could you add a bit more detail?",
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_steps_questions"},
                    }
                    return _respond(response)
                response = {
                    "reply": cleaned_reply,
                    "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                    "request_id": request_id,
                    "meta": {"intent": "goal_steps_draft"},
                }
                return _respond(response)
            t = (user_input or "").strip().lower()
            if gate_prompt and t in {"yes", "yeah", "yep"}:
                response = {
                    "reply": "Goal or steps?",
                    "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                    "request_id": request_id,
                    "meta": {"intent": "goal_intent_continuation_clarify"},
                }
                return _respond(response)
            has_steps_word = re.search(r"\bstep(s)?\b", t) is not None
            has_goal_word = re.search(r"\bgoal(s)?\b", t) is not None
            has_save_word = re.search(r"\bsave\b", t) is not None
            steps_choice = has_steps_word and not (has_goal_word or has_save_word)
            goal_choice = has_goal_word or has_save_word
            asks_questions = "question" in t and ("ask" in t or "relevant" in t or "before" in t)
            if has_steps_word and has_goal_word and not has_save_word:
                steps_choice = True
                goal_choice = False
            if has_steps_word and has_save_word:
                steps_choice = False
                goal_choice = True
            if asks_questions and not goal_choice:
                steps_choice = True
            if gate_prompt and (steps_choice or goal_choice):
                goal_text = _find_goal_text_in_context(companion_context)
                normalized_log_text = t[:60]
                logger.info(
                    "API: continuation resolver request_id=%s gate_prompt=%s steps_choice=%s goal_choice=%s text=%s found_goal_text=%s",
                    request_id,
                    gate_prompt,
                    steps_choice,
                    goal_choice,
                    normalized_log_text,
                    bool(goal_text),
                )
                if not goal_text:
                    response = {
                        "reply": "What's the goal you want to save or break into steps?",
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_intent_continuation_missing_goal"},
                    }
                    return _respond(response)
                if steps_choice:
                    questions_payload = _generate_goal_intake_questions(
                        goal_text=goal_text,
                        goal_title=None,
                        goal_description=None,
                        user_message=user_input,
                        recent_messages=companion_context,
                        user_id=user_id,
                        request_id=request_id,
                        logger=logger,
                    )
                    if questions_payload and questions_payload.get("need_more_context"):
                        reply_text = questions_payload.get("context_request") or ""
                    elif questions_payload and questions_payload.get("questions"):
                        reply_text = _format_goal_questions_reply(goal_text, questions_payload.get("questions"))
                    else:
                        reply_text = _format_goal_questions_reply(goal_text)
                    response = {
                        "reply": reply_text,
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {"intent": "goal_steps_questions"},
                    }
                    return _respond(response)
                if goal_choice:
                    if user_id is None:
                        return user_error
                    from db.suggestions_repository import create_suggestion
                    title = _extract_goal_title_suggestion(goal_text) or goal_text.strip()[:120]
                    provenance = {
                        "source": "goal_intent_continuation",
                        "request_id": request_id,
                        "client_message_id": client_message_id,
                    }
                    suggestion = create_suggestion(
                        user_id=user_id,
                        kind="goal",
                        payload={"title": title, "body": goal_text},
                        provenance=provenance,
                    )
                    suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
                    if not suggestion_id:
                        return api_error(
                            "SUGGESTION_CREATE_FAILED",
                            "Failed to create pending goal suggestion",
                            500,
                        )
                    response = {
                        "reply": "Got it. I saved that as a pending goal suggestion. Confirm to apply it.",
                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                        "request_id": request_id,
                        "meta": {
                            "intent": "goal_suggestion_pending",
                            "suggestion_id": suggestion_id,
                        },
                    }
                    return _respond(response)


        if user_id and is_chat_view:
            weekday_key = _extract_weekday_plan_query(user_input)
            if weekday_key:
                try:
                    from db.plan_repository import get_user_timezone

                    timezone_name = get_user_timezone(user_id)
                    ymd = _resolve_weekday_to_ymd(
                        weekday_key=weekday_key,
                        timezone_name=timezone_name,
                        logger=logger,
                    )
                    plan_date = date.fromisoformat(ymd)
                    comps = get_agent_components()
                    plan = _load_plan_for_date_peek(
                        user_id=user_id,
                        plan_date=plan_date,
                        comps=comps,
                    )
                    sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
                    item_count = sum(
                        len(sections.get(key, []) or [])
                        for key in ("routines", "goal_tasks", "optional")
                    )
                    response = {
                        "reply": _format_day_plan_reply(
                            plan,
                            plan_date,
                            _weekday_label(weekday_key),
                        ),
                        "agent_status": {"planner_active": False},
                        "request_id": request_id,
                        "meta": {
                            "intent": "day_plan_query",
                            "ymd": plan_date.isoformat(),
                            "weekday": weekday_key,
                            "item_count": item_count,
                        },
                    }
                    return _respond(response)
                except Exception as exc:
                    logger.error(
                        "API: weekday plan query failed request_id=%s error=%s",
                        request_id,
                        type(exc).__name__,
                        exc_info=True,
                    )
                    response = {
                        "reply": (
                            f"I couldn't load the plan for {_weekday_label(weekday_key)} right now. "
                            "Please try again in a moment."
                        ),
                        "agent_status": {"planner_active": False},
                        "request_id": request_id,
                        "meta": {"intent": "day_plan_query_failed", "weekday": weekday_key},
                    }
                    return _respond(response)

        if user_id and is_chat_view and is_today_plan_request(user_input):
            try:
                local_today = _get_local_today(user_id)
                comps = get_agent_components()
                othello_engine = comps["othello_engine"]
                plan = othello_engine.day_planner.get_today_plan(
                    user_id,
                    force_regen=False,
                    plan_date=local_today,
                )
                brief = othello_engine.summarise_today_plan(plan) if isinstance(plan, dict) else {}
                sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
                item_count = sum(
                    len(sections.get(key, []) or [])
                    for key in ("routines", "goal_tasks", "optional")
                )
                logger.info(
                    "API: today-plan chat gate request_id=%s user_id=%s local_date=%s item_count=%s",
                    request_id,
                    user_id,
                    local_today.isoformat(),
                    item_count,
                )
                response = {
                    "reply": _format_today_plan_reply(plan, brief, local_today),
                    "agent_status": {"planner_active": False},
                    "request_id": request_id,
                    "meta": {
                        "intent": "today_plan_brief",
                        "plan_date": local_today.isoformat(),
                        "item_count": item_count,
                    },
                }
                return _respond(response)
            except Exception as exc:
                logger.error(
                    "API: today-plan chat gate failed request_id=%s error=%s",
                    request_id,
                    type(exc).__name__,
                    exc_info=True,
                )
                response = {
                    "reply": "I couldn't load today's plan right now. Please try again in a moment.",
                    "agent_status": {"planner_active": False},
                    "request_id": request_id,
                    "meta": {"intent": "today_plan_brief_failed"},
                }
                return _respond(response)

        if is_help_request(user_input):
            help_caps = get_help_capabilities(phase1_only=_PHASE1_ENABLED)
            response = {
                "reply": format_capabilities_for_chat(phase1_only=_PHASE1_ENABLED),
                "capabilities": help_caps,
                "meta": {"intent": "capabilities_help"},
            }
            if _PHASE1_ENABLED:
                response["meta"]["phase1_skipped"] = phase1_skipped
            return _respond(response)

        def _log_goal_intent_status(goal_intent_detected: bool, reply_source: str) -> None:
            logger.info(
                "API: goal_intent status request_id=%s user_id=%s message_id=%s goal_intent_detected=%s reply_source=%s",
                request_id,
                user_id,
                client_message_id,
                goal_intent_detected,
                reply_source,
            )

        try:
            comps = get_agent_components()
            architect_agent = comps["architect_agent"]
            othello_engine = comps["othello_engine"]
            logger.debug(
                "API: handle_message agent_initialized=True request_id=%s", request_id
            )
        except Exception:
            logger.error(
                "API: handle_message agent init failed request_id=%s",
                request_id,
                exc_info=True,
            )
            detail = "Missing or invalid OPENAI_API_KEY"
            if _agent_init_error:
                if isinstance(_agent_init_error, ValueError) and "OPENAI_API_KEY" in str(_agent_init_error):
                    detail = "Missing or invalid OPENAI_API_KEY"
                else:
                    detail = f"Agent init failed ({type(_agent_init_error).__name__})"
            if effective_channel == "companion":
                fallback_reply = _llm_unavailable_prompt(None)
            else:
                fallback_reply = (
                    "I'm having trouble reaching the assistant right now. "
                    "Could you share a bit more detail so I can help you plan?"
                )
            response = {
                "reply": fallback_reply,
                "agent_status": {"planner_active": False, "had_goal_update_xml": False},
                "request_id": request_id,
                "meta": {"intent": "llm_unavailable", "details": detail},
            }
            suggestion = _get_goal_intent_suggestion(
                user_input,
                client_message_id,
                user_id,
            )
            if not suggestion and effective_channel == "companion":
                suggestion = _build_goal_intent_fallback(
                    user_input,
                    client_message_id,
                    user_id,
                )
            goal_intent_detected = _attach_goal_intent_suggestion(
                response,
                user_input=user_input,
                client_message_id=client_message_id,
                user_id=user_id,
                request_id=request_id,
                logger=logger,
                active_goal_id=None,
                suggestion=suggestion,
            )
            _log_goal_intent_status(goal_intent_detected, "fallback")
            return _respond(response)
        requested_goal_id = _coerce_goal_id(raw_goal_id) if raw_goal_id is not None else None
        if raw_goal_id is not None and requested_goal_id is None:
            return api_error(
                "VALIDATION_ERROR",
                f"{goal_id_source} must be a positive integer",
                400,
                details={"goal_id": raw_goal_id},
            )

        requested_goal = None
        if requested_goal_id is not None:
            if user_id is None:
                return user_error
            try:
                requested_goal = architect_agent.goal_mgr.get_goal(user_id, requested_goal_id)
            except Exception as exc:
                logger.error("API: Goal lookup failed request_id=%s", request_id, exc_info=True)
                return api_error(
                    "GOAL_STORAGE_UNAVAILABLE",
                    "Goal storage unavailable",
                    503,
                    details=type(exc).__name__,
                )
            if requested_goal is None:
                return api_error(
                    "GOAL_NOT_FOUND",
                    "Goal not found",
                    404,
                    details={"goal_id": requested_goal_id},
                )
            status = (requested_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": requested_goal_id},
                )

        active_goal = requested_goal
        goal_resolution_path = "explicit_id" if requested_goal is not None else "none"
        if raw_goal_id is None and user_id is not None and active_goal is None:
            try:
                server_active_goal = architect_agent.goal_mgr.get_active_goal(user_id)
            except Exception as exc:
                logger.warning(
                    "API: server active goal lookup failed request_id=%s error=%s",
                    request_id,
                    type(exc).__name__,
                )
                server_active_goal = None
            if isinstance(server_active_goal, dict):
                status = (server_active_goal.get("status") or "").strip().lower()
                if status != "archived":
                    active_goal = server_active_goal
                    goal_resolution_path = "server_active"

        logger.info(
            "API: resolved active_goal path=%s request_id=%s goal_id=%s",
            goal_resolution_path,
            request_id,
            active_goal.get("id") if isinstance(active_goal, dict) else None,
        )

        if ui_action == "plan_from_text_append":
            if user_id is None:
                return user_error
            plan_text = data.get("plan_text")
            if not isinstance(plan_text, str) or not plan_text.strip():
                return api_error("VALIDATION_ERROR", "plan_text is required", 400)
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                return api_error("VALIDATION_ERROR", "Please focus a goal first.", 400)
            status = (active_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": active_goal.get("id")},
                )
            steps = _parse_plan_text_with_log(plan_text, logger)
            if not steps:
                return api_error(
                    "PLAN_PARSE_EMPTY",
                    "No actionable steps found; provide bullets or numbered tasks.",
                    400,
                )
            section_label = data.get("section_label")
            if not isinstance(section_label, str) or not section_label.strip():
                section_label = f"Chat Plan: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            payload = {
                "goal_id": active_goal["id"],
                "steps": steps,
                "plan_text": plan_text,
                "mode": "append",
                "section_label": section_label,
            }
            provenance = {
                "source": "api_message",
                "ui_action": ui_action,
                "request_id": request_id,
                "client_message_id": client_message_id,
                "goal_id": active_goal["id"],
            }
            try:
                suggestion = _create_goal_plan_suggestion(
                    user_id=user_id,
                    payload=payload,
                    provenance=provenance,
                )
            except Exception:
                logger.error(
                    "API: plan_from_text_append suggestion failed request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                    exc_info=True,
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
            if not suggestion_id:
                logger.error(
                    "API: plan_from_text_append suggestion missing id request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            response = {
                "reply": f"Prepared {len(steps)} steps for confirmation.",
                "meta": {
                    "intent": "plan_steps_proposed",
                    "pending_suggestion_id": suggestion_id,
                    "requires_confirmation": True,
                },
                "goal_id": active_goal["id"],
                "section_label": section_label,
            }
            if _PHASE1_ENABLED:
                response["meta"]["phase1_skipped"] = phase1_skipped
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        if ui_action == "plan_from_text":
            if user_id is None:
                return user_error
            plan_text = data.get("plan_text")
            if not isinstance(plan_text, str) or not plan_text.strip():
                return api_error("VALIDATION_ERROR", "plan_text is required", 400)
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                return api_error("VALIDATION_ERROR", "Please focus a goal first.", 400)
            status = (active_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": active_goal.get("id")},
                )
            steps = _parse_plan_text_with_log(plan_text, logger)
            if not steps:
                return api_error(
                    "PLAN_PARSE_EMPTY",
                    "No actionable steps found; provide bullets or numbered tasks.",
                    400,
                )
            payload = {
                "goal_id": active_goal["id"],
                "steps": steps,
                "plan_text": plan_text,
                "mode": "replace",
            }
            provenance = {
                "source": "api_message",
                "ui_action": ui_action,
                "request_id": request_id,
                "client_message_id": client_message_id,
                "goal_id": active_goal["id"],
            }
            try:
                suggestion = _create_goal_plan_suggestion(
                    user_id=user_id,
                    payload=payload,
                    provenance=provenance,
                )
            except Exception:
                logger.error(
                    "API: plan_from_text suggestion failed request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                    exc_info=True,
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
            if not suggestion_id:
                logger.error(
                    "API: plan_from_text suggestion missing id request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            response = {
                "reply": f"Prepared {len(steps)} steps for confirmation.",
                "meta": {
                    "intent": "plan_steps_proposed",
                    "pending_suggestion_id": suggestion_id,
                    "requires_confirmation": True,
                },
                "goal_id": active_goal["id"],
            }
            if _PHASE1_ENABLED:
                response["meta"]["phase1_skipped"] = phase1_skipped
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        if ui_action == "plan_from_intent":
            if user_id is None:
                return user_error
            raw_intent_index = data.get("intent_index")
            if raw_intent_index is None:
                raw_intent_index = data.get("intentIndex")
            try:
                intent_index = int(raw_intent_index)
            except (TypeError, ValueError):
                return api_error("VALIDATION_ERROR", "intent_index must be a number", 400)
            if intent_index <= 0:
                return api_error("VALIDATION_ERROR", "intent_index must be positive", 400)
            intent_text = data.get("intent_text") or data.get("intentText") or ""
            if not isinstance(intent_text, str) or not intent_text.strip():
                return api_error("VALIDATION_ERROR", "intent_text is required", 400)
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                return api_error("VALIDATION_ERROR", "Please focus a goal first.", 400)
            status = (active_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": active_goal.get("id")},
                )
            instruction = (
                f"Create a plan for Intent #{intent_index}: {intent_text}.\n"
                f"Output format: start with a markdown header like "
                f"\"### Intent {intent_index} Plan: <short title>\" then a numbered list of actionable steps.\n"
                f"No prose outside the list."
            )
            goal_context = ""
            try:
                goal_context = architect_agent.goal_mgr.build_goal_context(
                    user_id, active_goal["id"], max_notes=5
                ) or ""
            except Exception:
                goal_context = ""
            llm_error_code = None
            fallback_on_llm_error = False
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                plan_reply, _agent_status = loop.run_until_complete(
                    asyncio.wait_for(
                        architect_agent.plan_and_execute(
                            instruction,
                            context={
                                "goal_context": goal_context,
                                "active_goal": active_goal,
                            } if goal_context else None,
                            user_id=user_id,
                            recent_messages=companion_context,
                        ),
                        timeout=30.0
                    )
                )
            except Exception as exc:
                logger.error(
                    "API: plan_from_intent failed request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                    exc_info=True,
                )
                llm_exc = _unwrap_llm_exception(exc)
                if llm_exc and isinstance(llm_exc, openai.AuthenticationError):
                    fallback_on_llm_error = True
                    llm_error_code = getattr(llm_exc, "code", None) or "authentication_error"
                if isinstance(exc, ValueError) and "OpenAI chat completion failed" in str(exc):
                    fallback_on_llm_error = True
                    if llm_error_code is None:
                        llm_error_code = "llm_wrapper_error"
                if not fallback_on_llm_error:
                    if llm_exc:
                        return handle_llm_error(llm_exc, logger)
                    return api_error("PLAN_FROM_INTENT_FAILED", "Failed to build plan", 500)
                plan_reply = ""
                _agent_status = {}
            finally:
                if loop is not None:
                    try:
                        loop.close()
                    except Exception:
                        logger.debug("API: event loop close failed but continuing")
            plan_text = plan_reply or ""
            steps = _parse_plan_text_with_log(plan_text, logger)
            if not steps and isinstance(_agent_status, dict) and _agent_status.get("planner_active") is False:
                fallback_on_llm_error = True
                if llm_error_code is None:
                    llm_error_code = "llm_wrapper_error"
            if not steps and (plan_text or "").strip().lower().startswith("sorry, something went wrong"):
                fallback_on_llm_error = True
                if llm_error_code is None:
                    llm_error_code = "llm_wrapper_error"
            if fallback_on_llm_error and not steps:
                fallback_steps = _fallback_steps_from_text(intent_text or user_input)
                if not fallback_steps:
                    return api_error(
                        "PLAN_PARSE_EMPTY",
                        "No actionable steps found; provide bullets or numbered tasks.",
                        400,
                    )
                payload = {
                    "goal_id": active_goal["id"],
                    "steps": fallback_steps,
                    "mode": "replace",
                    "intent_index": intent_index,
                    "intent_text": intent_text,
                }
                provenance = {
                    "source": "fallback_parser",
                    "llm_error_code": llm_error_code,
                    "ui_action": ui_action,
                    "request_id": request_id,
                    "client_message_id": client_message_id,
                    "goal_id": active_goal["id"],
                    "intent_index": intent_index,
                }
                try:
                    suggestion = _create_goal_plan_suggestion(
                        user_id=user_id,
                        payload=payload,
                        provenance=provenance,
                    )
                except Exception:
                    logger.error(
                        "API: plan_from_intent fallback suggestion failed request_id=%s goal_id=%s",
                        request_id,
                        active_goal.get("id"),
                        exc_info=True,
                    )
                    return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
                suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
                if not suggestion_id:
                    logger.error(
                        "API: plan_from_intent fallback suggestion missing id request_id=%s goal_id=%s",
                        request_id,
                        active_goal.get("id"),
                    )
                    return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
                response = {
                    "reply": f"Prepared {len(fallback_steps)} steps from your intent for confirmation.",
                    "meta": {
                        "intent": "plan_steps_proposed",
                        "intent_index": intent_index,
                        "pending_suggestion_id": suggestion_id,
                        "requires_confirmation": True,
                    },
                    "goal_id": active_goal["id"],
                }
                if _PHASE1_ENABLED:
                    response["meta"]["phase1_skipped"] = phase1_skipped
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            if not steps:
                return api_error(
                    "PLAN_PARSE_EMPTY",
                    "No actionable steps found; provide bullets or numbered tasks.",
                    400,
                )
            section_label = None
            for step in steps:
                section_label = step.get("section")
                if section_label:
                    break
            section_prefix = f"Intent {intent_index}"
            if not section_label:
                section_label = section_prefix
            elif not section_label.lower().startswith(section_prefix.lower()):
                section_label = f"{section_prefix}: {section_label}"
            for step in steps:
                step["section"] = section_label
            payload = {
                "goal_id": active_goal["id"],
                "steps": steps,
                "plan_text": plan_text,
                "mode": "replace",
                "section_label": section_label,
                "section_prefix": section_prefix,
                "intent_index": intent_index,
            }
            provenance = {
                "source": "api_message",
                "ui_action": ui_action,
                "request_id": request_id,
                "client_message_id": client_message_id,
                "goal_id": active_goal["id"],
                "intent_index": intent_index,
            }
            try:
                suggestion = _create_goal_plan_suggestion(
                    user_id=user_id,
                    payload=payload,
                    provenance=provenance,
                )
            except Exception:
                logger.error(
                    "API: plan_from_intent suggestion failed request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                    exc_info=True,
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
            if not suggestion_id:
                logger.error(
                    "API: plan_from_intent suggestion missing id request_id=%s goal_id=%s",
                    request_id,
                    active_goal.get("id"),
                )
                return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
            reply_with_confirm = plan_text
            if reply_with_confirm:
                reply_with_confirm = reply_with_confirm.rstrip()
            reply_with_confirm = f"{reply_with_confirm}\n\nConfirm to apply these steps.".strip()
            response = {
                "reply": reply_with_confirm,
                "meta": {
                    "intent": "plan_steps_proposed",
                    "intent_index": intent_index,
                    "pending_suggestion_id": suggestion_id,
                    "requires_confirmation": True,
                },
                "goal_id": active_goal["id"],
            }
            if _PHASE1_ENABLED:
                response["meta"]["phase1_skipped"] = phase1_skipped
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        focused_goal_edit = _parse_focused_goal_edit_command(user_input)
        if focused_goal_edit:
            if user_id is None:
                return user_error
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                reply_text = "Please focus a goal first (for example, 'goal 1')."
                response = {
                    "reply": reply_text,
                    "meta": {"intent": "focused_goal_edit_missing_focus"},
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            payload = focused_goal_edit.get("payload", "")
            if not payload:
                reply_text = "Please include text after 'append to goal:' or 'update goal:'."
                response = {
                    "reply": reply_text,
                    "meta": {"intent": "focused_goal_edit_missing_text"},
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            try:
                if focused_goal_edit["mode"] == "append":
                    updated_goal = architect_agent.goal_mgr.append_goal_draft(
                        user_id,
                        active_goal["id"],
                        payload,
                        request_id=request_id,
                    )
                    intent = "append_goal_draft"
                else:
                    updated_goal = architect_agent.goal_mgr.replace_goal_draft(
                        user_id,
                        active_goal["id"],
                        payload,
                        request_id=request_id,
                    )
                    intent = "update_goal_draft"
            except Exception:
                logger.error(
                    "API: focused goal edit failed request_id=%s goal_id=%s mode=%s",
                    request_id,
                    active_goal.get("id"),
                    focused_goal_edit["mode"],
                    exc_info=True,
                )
                updated_goal = None
                intent = "focused_goal_edit_failed"
            if not updated_goal:
                reply_text = "I couldn't update that goal right now."
                response = {
                    "reply": reply_text,
                    "meta": {"intent": "focused_goal_edit_failed"},
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            try:
                note_label = (
                    "[Goal Draft Append] Appended text (len=%s)" % len(payload)
                    if focused_goal_edit["mode"] == "append"
                    else "[Goal Draft Update] Replaced draft (len=%s)" % len(payload)
                )
                architect_agent.goal_mgr.add_note_to_goal(
                    user_id,
                    active_goal["id"],
                    "system",
                    note_label,
                    request_id=request_id,
                )
            except Exception:
                pass
            fresh_goal = architect_agent.goal_mgr.get_goal(user_id, active_goal["id"])
            if fresh_goal is None:
                reply_text = "I updated the goal, but couldn't reload it."
                response = {
                    "reply": reply_text,
                    "meta": {"intent": "focused_goal_edit_reload_failed"},
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            reply_text = (
                "Appended to the focused goal draft." if focused_goal_edit["mode"] == "append"
                else "Updated the focused goal draft."
            )
            response = {
                "reply": reply_text,
                "meta": {
                    "intent": intent,
                    "goal_updated": True,
                    "goal_id": active_goal["id"],
                    "goal_field_updated": "draft_text"
                },
                "goal": fresh_goal,
            }
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        pending_edit = session.get("pending_goal_edit")
        if isinstance(pending_edit, dict):
            pending_mode = pending_edit.get("mode")
            pending_goal_id = pending_edit.get("goal_id")
            session.pop("pending_goal_edit", None)
            logger.info(
                "pending_goal_edit cleared goal_id=%s request_id=%s",
                pending_goal_id,
                request_id,
            )
            if pending_goal_id is None:
                return api_error(
                    "VALIDATION_ERROR",
                    "Please focus a goal again before updating.",
                    400,
                )
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                return api_error(
                    "VALIDATION_ERROR",
                    "Please focus a goal again before updating.",
                    400,
                )
            if pending_goal_id is not None and active_goal.get("id") != pending_goal_id:
                return api_error(
                    "VALIDATION_ERROR",
                    "The focused goal changed. Please focus the goal again before updating.",
                    400,
                )
            status = (active_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": active_goal.get("id")},
                )
            updated_goal = None
            try:
                if pending_mode == "update":
                    updated_goal = architect_agent.goal_mgr.replace_goal_description(
                        user_id,
                        pending_goal_id,
                        user_input,
                        request_id=request_id,
                    )
                elif pending_mode == "append":
                    updated_goal = architect_agent.goal_mgr.append_goal_description(
                        user_id,
                        pending_goal_id,
                        user_input,
                        request_id=request_id,
                    )
            except Exception:
                logger.error(
                    "API: pending_goal_edit failed request_id=%s goal_id=%s mode=%s",
                    request_id,
                    active_goal.get("id"),
                    pending_mode,
                    exc_info=True,
                )
            ok = bool(updated_goal)
            logger.info(
                "pending_goal_edit apply mode=%s goal_id=%s ok=%s request_id=%s user_id=%s payload_len=%s",
                pending_mode,
                pending_goal_id,
                ok,
                request_id,
                user_id,
                len(user_input),
            )
            if ok and pending_goal_id is not None:
                try:
                    note_label = (
                        "[Goal Append] Appended text (len=%s)" % len(user_input)
                        if pending_mode == "append"
                        else "[Goal Update] Replaced description (len=%s)" % len(user_input)
                    )
                    architect_agent.goal_mgr.add_note_to_goal(
                        user_id,
                        pending_goal_id,
                        "system",
                        note_label,
                        request_id=request_id,
                    )
                except Exception:
                    pass
            fresh_goal = architect_agent.goal_mgr.get_goal(user_id, pending_goal_id)
            reply_text = (
                "Updated the focused goal."
                if pending_mode == "update"
                else "Appended to the focused goal."
            )
            if not ok:
                reply_text = "I couldn't update that goal right now."
            response = {
                "reply": reply_text,
                "meta": {
                    "intent": "pending_goal_edit_applied",
                    "mode": pending_mode,
                    "ok": ok,
                },
                "goal": fresh_goal,
            }
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        pending_mode = _detect_goal_edit_arm(data, user_input)
        if pending_mode in ("update", "append"):
            if user_id is None:
                return user_error
            if not isinstance(active_goal, dict) or active_goal.get("id") is None:
                reply_text = "Please focus a goal first (for example, 'goal 1')."
                response = {
                    "reply": reply_text,
                    "meta": {"intent": "pending_goal_edit_missing_focus"},
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)
            status = (active_goal.get("status") or "").strip().lower()
            if status == "archived":
                return api_error(
                    "GOAL_ARCHIVED",
                    "Goal is archived",
                    409,
                    details={"goal_id": active_goal.get("id")},
                )
            session["pending_goal_edit"] = {
                "mode": pending_mode,
                "goal_id": active_goal["id"],
                "set_at_utc": datetime.utcnow().isoformat() + "Z",
            }
            logger.info(
                "pending_goal_edit set mode=%s goal_id=%s request_id=%s user_id=%s",
                pending_mode,
                active_goal.get("id"),
                request_id,
                user_id,
            )
            reply_text = (
                "Got it. Paste the updated goal text you'd like saved."
                if pending_mode == "update"
                else "Got it. Paste the text you'd like to append to the goal."
            )
            response = {
                "reply": reply_text,
                "meta": {"intent": "pending_goal_edit_set", "mode": pending_mode},
            }
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        # --- Shortcut 1: user is asking for their goals; answer directly -----
        if is_goal_list_request(user_input):
            if user_id is None:
                return user_error
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
                "goal list",
                "goals list",
                "show goal list",
                "show goals list",
                "show goals",
                "view goals",
                "view my goals",
                "see my goals",
                "what goals do i have",
                "what goals have i",
            ]
            matched_phrase = next((p for p in goal_list_phrases if p in t), None)
            logger.info(f"API: Routing to goal list (shortcut branch) due to phrase: {matched_phrase!r}")
        
            goals = architect_agent.goal_mgr.list_goals(user_id) or []
            reply_text = format_goal_list(goals)
            logger.info(f"API: Returning goal list with {len(goals)} goals")
            response = {
                "reply": reply_text,
                "goals": goals,
                "meta": {
                    "source": "goal_manager",
                    "intent": "list_goals",
                },
            }
            _log_goal_intent_status(False, "fallback")
            return _respond(response)

        # --- Shortcut 2: user wants to focus on a specific goal -------------
        goal_id = parse_goal_selection_request(user_input)
        if goal_id is not None:
            if user_id is None:
                return user_error
            logger.info(f"API: User explicitly selecting goal #{goal_id} via goal-selection command")
            goal = architect_agent.goal_mgr.get_goal(user_id, goal_id)
            if goal is None:
                logger.warning(f"API: Goal #{goal_id} not found")
                reply_text = (
                    f"I couldn't find a goal #{goal_id}. "
                    "Ask me to list your goals first if you're not sure of the number."
                )
                response = {
                    "reply": reply_text,
                    "meta": {
                        "source": "goal_manager",
                        "intent": "select_goal_failed",
                        "requested_goal_id": goal_id,
                    },
                }
                _log_goal_intent_status(False, "fallback")
                return _respond(response)

            architect_agent.goal_mgr.set_active_goal(user_id, goal_id)
            ctx = architect_agent.goal_mgr.build_goal_context(user_id, goal_id, max_notes=5)
            logger.info(f"API: Set active goal to #{goal_id}: {goal['text'][:50]}...")
            reply_text = (
                f"Okay, we'll focus on Goal #{goal_id}: {goal['text']}.\n\n"
                "I'll attach our next messages to this goal. "
                "Tell me updates, questions, or ask me to help you plan steps."
            )
            response = {
                "reply": reply_text,
                "active_goal_id": goal_id,
                "goal_context": ctx,
                "meta": {
                    "source": "goal_manager",
                    "intent": "select_goal_success",
                    "selected_goal_id": goal_id,
                },
            }
            _log_goal_intent_status(False, "fallback")
            return _respond(response)
        # ---------------------------------------------------------------------

        goal_intent_suggestion = _get_goal_intent_suggestion(
            user_input,
            client_message_id,
            user_id,
        )
        goal_intent_detected = bool(goal_intent_suggestion)

        # === Post-processing (analysis only - no persistence here) ===========
        if _PHASE1_ENABLED:
            logger.info("API: Phase-1 DB-only mode - skipping postprocess")
            summary = None
        else:
            summary = postprocess_and_save(user_input)
            print("[DEBUG] Postprocess summary:", summary)  # Comment/remove in prod

        # === Build goal_context for Architect (if an active goal exists) =====
        goal_context = None
        if isinstance(active_goal, dict) and active_goal.get("id") is not None:
            goal_context = architect_agent.goal_mgr.build_goal_context(
                user_id, active_goal["id"], max_notes=8
            ) or ""
            logger.info(f"API: Active goal #{active_goal['id']}: {active_goal.get('text', '')[:50]}...")
            logger.info(f"API: Built goal context ({len(goal_context) if goal_context else 0} chars)")
            logger.info(f"API: Routing message to Architect planning engine for goal_id={active_goal['id']}")
        else:
            active_goal = None
            logger.info("API: No active goal - casual chat mode")
        # ---------------------------------------------------------------------

        # === Route to Architect planning if active goal exists ===============
        if active_goal is not None:
            # Active goal detected - check if this is an explicit plan generation request
            reply_source = "fallback"
            try:
                from core.input_router import InputRouter
                router = InputRouter()
                is_plan_request = router.is_plan_request(user_input)
            except Exception as exc:
                logger.warning("API: InputRouter unavailable, skipping plan routing: %s", exc, exc_info=True)
                is_plan_request = False
        
            if is_plan_request:
                # Explicit plan generation request - use XML-only planning mode
                logger.info(f"API: PLAN REQUEST detected for goal #{active_goal['id']}")
                logger.info(f"API: Routing to generate_goal_plan (XML-only mode)")
            
                try:
                    loop = asyncio.new_event_loop()
                    try:
                        asyncio.set_event_loop(loop)
                        plan_result = loop.run_until_complete(
                            architect_agent.generate_goal_plan(
                                user_id,
                                goal_id=active_goal['id'],
                                instruction=user_input,
                                persist=False,
                            )
                        )
                    finally:
                        loop.close()
                
                    if plan_result:
                        # Successfully generated plan - build natural language summary
                        plan_steps = plan_result.get("plan_steps") or []
                        step_count = len(plan_steps)
                        next_action = plan_result.get('next_action', 'Begin with the first step')
                        priority = plan_result.get('priority', 'medium')
                        status = plan_result.get('status', 'active')
                        payload = {
                            "goal_id": active_goal["id"],
                            "plan_steps": plan_steps,
                            "summary": plan_result.get("summary"),
                            "next_action": next_action,
                            "mode": "replace",
                        }
                        provenance = {
                            "source": "api_message",
                            "ui_action": "plan_request",
                            "request_id": request_id,
                            "client_message_id": client_message_id,
                            "goal_id": active_goal["id"],
                        }
                        try:
                            suggestion = _create_goal_plan_suggestion(
                                user_id=user_id,
                                payload=payload,
                                provenance=provenance,
                            )
                        except Exception:
                            logger.error(
                                "API: plan_request suggestion failed request_id=%s goal_id=%s",
                                request_id,
                                active_goal.get("id"),
                                exc_info=True,
                            )
                            return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
                        suggestion_id = suggestion.get("id") if isinstance(suggestion, dict) else None
                        if not suggestion_id:
                            logger.error(
                                "API: plan_request suggestion missing id request_id=%s goal_id=%s",
                                request_id,
                                active_goal.get("id"),
                            )
                            return api_error("PLAN_SUGGESTION_FAILED", "Failed to create pending suggestion", 500)
                    
                        agentic_reply = (
                            f"I've prepared a {step_count}-step plan for this goal.\n\n"
                            f"Status: {status}\n"
                            f"Priority: {priority}\n\n"
                            f"Your next action: {next_action}\n\n"
                            "Confirm to apply these steps."
                        )
                    
                        agent_status = {
                            "planner_active": True,
                            "had_goal_update_xml": True,
                            "plan_generated": True,
                            "step_count": step_count,
                            "pending_suggestion_id": suggestion_id,
                            "requires_confirmation": True,
                        }
                        reply_source = "llm"
                    
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
                        reply_source = "fallback"
                    
                except Exception as e:
                    logger.error(f"API: generate_goal_plan failed: {e}", exc_info=True)
                
                    # Check if it's an LLM error - return structured error
                    llm_exc = _unwrap_llm_exception(e)
                    if llm_exc:
                        if effective_channel == "companion":
                            agentic_reply = _llm_unavailable_prompt(active_goal.get("id"))
                        else:
                            agentic_reply = (
                                "I'm having trouble reaching the assistant right now. "
                                "Could you share a bit more detail so I can help you plan?"
                            )
                        agent_status = {
                            "planner_active": False,
                            "had_goal_update_xml": False,
                            "plan_generated": False,
                        }
                        reply_source = "fallback"
                    else:
                        # Otherwise provide generic error message in response
                        agentic_reply = (
                            "I encountered an error while generating the plan. "
                            "Please try again or rephrase your request."
                        )
                        agent_status = {
                            "planner_active": False,
                            "had_goal_update_xml": False,
                            "plan_generated": False
                        }
                        reply_source = "fallback"
        
            else:
                # Normal conversational planning mode
                logger.info(f"API: Planning with active goal #{active_goal['id']}: {active_goal.get('text', '')[:80]}")
            
                loop = None
                try:
                    logger.debug(f"API: Calling architect_agent.plan_and_execute with context={goal_context is not None}")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    agentic_reply, agent_status = loop.run_until_complete(
                        asyncio.wait_for(
                            architect_agent.plan_and_execute(
                                user_input,
                                context={
                                    "goal_context": goal_context,
                                    "active_goal": active_goal,
                                } if goal_context else None,
                                user_id=user_id,
                                recent_messages=companion_context,
                            ),
                            timeout=30.0
                        )
                    )
                
                    logger.info(f"API: Architect planning completed successfully for goal_id={active_goal['id']}")
                    logger.debug(f"API: Agent status: {agent_status}")
                    logger.debug(f"API: Reply preview: {agentic_reply[:150]}...")
                    reply_source = "llm"
                
                    # Ensure planner_active is True since we routed through Architect
                    if agent_status.get("planner_active") is None:
                        agent_status["planner_active"] = True
                    
                    # --- PHASE 15: Apply Goal Update to Draft ---
                    # If Architect returned a parsed goal update and we have an active draft, apply it.
                    goal_update = agent_status.get("goal_update")
                    if goal_update and draft_id:
                        logger.info(f"API: Applying goal update to draft {draft_id}: {goal_update.keys()}")
                        
                        # Load current draft
                        current_draft = suggestions_repository.get_suggestion(user_id, draft_id)
                        if current_draft and current_draft.get("status") == "pending":
                            current_payload = current_draft.get("payload") or {}
                            
                            # Update fields if present in goal_update
                            if "title" in goal_update:
                                current_payload["title"] = str(goal_update["title"]).strip()
                            if "target_days" in goal_update:
                                try:
                                    current_payload["target_days"] = int(goal_update["target_days"])
                                except:
                                    pass
                            if "steps" in goal_update:
                                raw_steps = goal_update["steps"]
                                if isinstance(raw_steps, list):
                                    # Sanitize steps (same logic as confirm)
                                    steps = []
                                    seen = set()
                                    for s in raw_steps:
                                        s_str = str(s).strip()
                                        if s_str:
                                            k = s_str.lower()
                                            if k not in seen:
                                                seen.add(k)
                                                steps.append(s_str)
                                    current_payload["steps"] = steps
                            
                            # Persist updated payload
                            suggestions_repository.update_suggestion_payload(user_id, draft_id, current_payload)
                            
                            # Add updated payload to response so UI updates immediately
                            response_data = {
                                "reply": agentic_reply,
                                "agent_status": agent_status,
                                "request_id": request_id,
                                "draft_context": {
                                    "draft_id": draft_id,
                                    "draft_type": "goal",
                                    "source_message_id": client_message_id
                                },
                                "draft_payload": current_payload
                            }
                            
                            # Log success
                            logger.info(f"API: Updated draft {draft_id} payload with {len(current_payload.get('steps', []))} steps")
                            
                            # Return early with the updated payload
                            return jsonify(response_data)

                except Exception as e:
                    logger.error(f"API: Architect planning failed with exception for goal_id={active_goal['id']}: {e}", exc_info=True)
                
                    # Check if it's an LLM error - return structured error
                    llm_exc = _unwrap_llm_exception(e)
                    if llm_exc:
                        if effective_channel == "companion":
                            agentic_reply = _llm_unavailable_prompt(active_goal.get("id"))
                        else:
                            agentic_reply = (
                                "I'm having trouble reaching the assistant right now. "
                                "Could you share a bit more detail so I can help you plan?"
                            )
                        agent_status = {"planner_active": False, "had_goal_update_xml": False}
                        reply_source = "fallback"
                    else:
                        # Otherwise provide generic error message in response
                        agentic_reply = (
                            "I ran into an internal error while updating your goal plan. "
                            "Please try again or rephrase your message."
                        )
                        agent_status = {"planner_active": False, "had_goal_update_xml": False}
                        reply_source = "fallback"
                
                finally:
                    if loop is not None:
                        try:
                            loop.close()
                        except Exception:
                            logger.debug("API: event loop close failed but continuing")

            if not isinstance(agent_status, dict):
                agent_status = {}

            if not (agentic_reply or "").strip():
                if effective_channel == "companion":
                    agentic_reply = "Noted."
                else:
                    agentic_reply = "Please share a bit more detail so I can help you plan."
                reply_source = "fallback"

            if should_offer_goal_intent(user_input):
                if not goal_intent_suggestion:
                    goal_intent_suggestion = _build_goal_intent_fallback(
                        user_input,
                        client_message_id,
                        user_id,
                    )
                goal_intent_detected = bool(goal_intent_suggestion)
            else:
                goal_intent_suggestion = None
                goal_intent_detected = False

        if active_goal is None:
            logger.info("API: No active goal for this message; falling back to casual mode")
            reply_source = "fallback"
            try:
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    agentic_reply, agent_status = loop.run_until_complete(
                        asyncio.wait_for(
                            architect_agent.plan_and_execute(
                                user_input,
                                context=None,
                                user_id=user_id,
                                recent_messages=companion_context,
                            ),
                            timeout=30.0
                        )
                    )
                finally:
                    loop.close()

                logger.info("API: Casual chat completed successfully")
                logger.debug("API: Reply preview: %s...", agentic_reply[:150])
                reply_source = "llm"

            except Exception as e:
                logger.error("API: Casual chat failed with exception: %s", e, exc_info=True)

                # Check if it's an LLM error - return structured error
                llm_exc = _unwrap_llm_exception(e)
                if llm_exc:
                    if effective_channel == "companion":
                        agentic_reply = _llm_unavailable_prompt(None)
                    else:
                        agentic_reply = (
                            "I'm having trouble reaching the assistant right now. "
                            "Could you share a bit more detail so I can help you plan?"
                        )
                    agent_status = {"planner_active": False, "had_goal_update_xml": False}
                    reply_source = "fallback"
                else:
                    # Otherwise provide generic error message in response
                    agentic_reply = "I'm having trouble processing that right now. Could you try again?"
                    agent_status = {"planner_active": False, "had_goal_update_xml": False}
                    reply_source = "fallback"

            if not isinstance(agent_status, dict):
                agent_status = {}

            if not (agentic_reply or "").strip():
                if effective_channel == "companion":
                    agentic_reply = "Noted."
                else:
                    agentic_reply = "Please share a bit more detail so I can help you plan."
                reply_source = "fallback"

            if should_offer_goal_intent(user_input):
                if not goal_intent_suggestion:
                    goal_intent_suggestion = _build_goal_intent_fallback(
                        user_input,
                        client_message_id,
                        user_id,
                    )
                goal_intent_detected = bool(goal_intent_suggestion)
            else:
                goal_intent_suggestion = None
                goal_intent_detected = False

            response = {
                "reply": agentic_reply,
                "agent_status": agent_status,
                "request_id": request_id,
            }
            try:
                if user_id and not _PHASE1_ENABLED:
                    logger.info("API: running insight extraction for message (casual mode)")
                    response["insights_meta"] = _normalize_insights_meta(
                        _process_insights_pipeline(
                            user_text=raw_user_input,
                            assistant_text=agentic_reply,
                            user_id=user_id,
                        )
                    )
                    logger.info(
                        "API: insight extraction completed (created=%s)",
                        response["insights_meta"].get("created", "?"),
                    )
                elif user_id and _PHASE1_ENABLED:
                    logger.info("API: Phase-1 DB-only mode - skipping insight extraction")
            except Exception as exc:
                logger.warning("API: insight extraction skipped due to error: %s", exc, exc_info=True)
            if _PHASE1_ENABLED:
                response.setdefault("meta", {})["phase1_skipped"] = phase1_skipped
            goal_intent_attached = _attach_goal_intent_suggestion(
                response,
                user_input=user_input,
                client_message_id=client_message_id,
                user_id=user_id,
                request_id=request_id,
                logger=logger,
                active_goal_id=None,
                suggestion=goal_intent_suggestion,
            )
            _log_goal_intent_status(goal_intent_attached, reply_source)
            return _respond(response)

        # --- Log conversation into active goal -------------------------------
        def _event_ok(result):
            if isinstance(result, dict):
                return bool(result.get("ok", False)), result.get("reason")
            return False, "unknown"

        event_storage_ok = True
        event_emitted = True
        try:
            user_event = architect_agent.goal_mgr.add_note_to_goal(
                user_id,
                active_goal["id"],
                "user",
                user_input,
                request_id=request_id,
            )
            assistant_event = architect_agent.goal_mgr.add_note_to_goal(
                user_id,
                active_goal["id"],
                "othello",
                agentic_reply,
                request_id=request_id,
            )
            user_ok, user_reason = _event_ok(user_event)
            assistant_ok, assistant_reason = _event_ok(assistant_event)
            if not user_ok or not assistant_ok:
                event_storage_ok = False
                event_emitted = False
                details = {
                    "user_event_ok": user_ok,
                    "assistant_event_ok": assistant_ok,
                    "goal_id": active_goal.get("id"),
                }
                if user_reason:
                    details["user_reason"] = user_reason
                if assistant_reason:
                    details["assistant_reason"] = assistant_reason
                logger.warning(
                    "API: goal event storage unavailable request_id=%s details=%s",
                    request_id,
                    details,
                )
        except Exception as e:
            event_storage_ok = False
            event_emitted = False
            logger.exception(
                "API: goal event append failed request_id=%s goal_id=%s",
                request_id,
                active_goal.get("id"),
                extra={"request_id": request_id},
            )

        if event_storage_ok:
            logger.debug(f"API: Logged conversation to goal #{active_goal['id']}")
        # ---------------------------------------------------------------------

        # Log final response details
        logger.info(f"API: Returning response - planner_active={agent_status.get('planner_active', False)}, had_xml={agent_status.get('had_goal_update_xml', False)}")

        agent_status["event_storage_ok"] = event_storage_ok
        agent_status["event_emitted"] = event_emitted

        response = {
            "reply": agentic_reply,
            "agent_status": agent_status,
            "request_id": request_id,
        }
        try:
            if user_id and not _PHASE1_ENABLED:
                logger.info("API: running insight extraction for message (goal mode)")
                response["insights_meta"] = _normalize_insights_meta(
                    _process_insights_pipeline(
                        user_text=raw_user_input,
                        assistant_text=agentic_reply,
                        user_id=user_id,
                    )
                )
                logger.info(
                    "API: insight extraction completed (created=%s)",
                    response["insights_meta"].get("created", "?"),
                )
            elif user_id and _PHASE1_ENABLED:
                logger.info("API: Phase-1 DB-only mode - skipping insight extraction")
        except Exception as exc:
            logger.warning("API: insight extraction skipped due to error: %s", exc, exc_info=True)
        if _PHASE1_ENABLED:
            response.setdefault("meta", {})["phase1_skipped"] = phase1_skipped
        goal_intent_attached = _attach_goal_intent_suggestion(
            response,
            user_input=user_input,
            client_message_id=client_message_id,
            user_id=user_id,
            request_id=request_id,
            logger=logger,
            active_goal_id=active_goal.get("id") if isinstance(active_goal, dict) else None,
            suggestion=goal_intent_suggestion,
        )
        _log_goal_intent_status(goal_intent_attached, reply_source)
        return _respond(response)

    except Exception as exc:
        logger.exception(
            "API: handle_message failed request_id=%s error_type=%s",
            request_id,
            type(exc).__name__,
            extra={"request_id": request_id},
        )
        return api_error("INTERNAL_ERROR", "Internal server error", 500)
    finally:
        _log_request_end()


@app.route("/api/confirm", methods=["POST"])
@require_auth
def api_confirm():
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if not request.is_json:
        return _v1_error("VALIDATION_ERROR", "JSON body required", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _v1_error("VALIDATION_ERROR", "JSON object required", 400)

    decisions = data.get("decisions")
    if decisions is None:
        decisions = [data]
    if not isinstance(decisions, list) or not decisions:
        return _v1_error("VALIDATION_ERROR", "decisions must be a non-empty list", 400)

    results = _apply_suggestion_decisions(user_id, decisions, event_source="api_confirm")
    return _v1_envelope(data={"results": results}, status=200)


@app.route("/api/suggestions/dismiss", methods=["POST"])
@require_auth
def dismiss_suggestion():
    logger = logging.getLogger("API")
    request_id = _get_request_id()
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)
    suggestion_type = str(data.get("type") or "").strip()
    source_client_message_id = str(data.get("source_client_message_id") or "").strip()
    if not suggestion_type or not source_client_message_id:
        return api_error(
            "VALIDATION_ERROR",
            "type and source_client_message_id are required",
            400,
        )
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if not _record_suggestion_dismissal(user_id, suggestion_type, source_client_message_id):
        return api_error("SUGGESTION_DISMISS_FAILED", "Failed to dismiss suggestion", 400)
    logger.info(
        "API: suggestion dismiss request_id=%s type=%s client_message_id=%s",
        request_id,
        suggestion_type,
        source_client_message_id,
    )
    return jsonify({"ok": True})


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
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    args = request.args or {}
    mood_context = {
        "mood": args.get("mood"),
        "fatigue": args.get("fatigue"),
        "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
    }

    # Peek mode: Read-only, no generation, no merging, no persistence
    peek_mode = args.get("peek") == "1"
    plan_date = None
    if peek_mode:
        plan_date_str = args.get("plan_date")
        if not plan_date_str:
            return api_error("VALIDATION_ERROR", "peek_requires_plan_date", 400)
        try:
            plan_date = date.fromisoformat(plan_date_str)
        except ValueError:
            return api_error("VALIDATION_ERROR", "invalid_plan_date", 400)
    else:
        if args.get("plan_date"):
            try:
                plan_date = date.fromisoformat(args.get("plan_date"))
            except ValueError:
                return api_error(
                    "VALIDATION_ERROR",
                    "Invalid plan_date format (expected YYYY-MM-DD)",
                    400,
                )
        else:
            plan_date = _get_local_today(user_id)
            logger.info("API: today-plan using local_today=%s", plan_date)

    if peek_mode:
        # Try to load existing plan row
        plan_repo = comps["plan_repository"]
        plan_row = plan_repo.get_plan_by_date(user_id, plan_date)
        
        if not plan_row:
            # Return empty stub
            return jsonify({
                "plan": {
                    "date": plan_date.isoformat(),
                    "sections": {"routines": [], "goal_tasks": [], "optional": []},
                    "mood_context": {},
                    "_plan_source": "empty_stub"
                }
            })
            
        # Load full plan with items
        # Reuse day_planner logic but bypass generation/merging
        # We can use get_today_plan with force_regen=False, but we must ensure it doesn't generate if missing.
        # However, get_today_plan WILL generate if missing.
        # So we manually construct the response from the row + items.
        
        # Re-fetch with items using repository helper if available, or manual construction
        # Since we don't have a clean "load full plan" repo method exposed here easily without duplicating logic,
        # we will use a lightweight reconstruction similar to what DayPlanner does, but strictly read-only.
        
        items = plan_repo.get_plan_items(plan_row["id"])
        # Group items
        sections = {"routines": [], "goal_tasks": [], "optional": []}
        for item in items:
            sec = item.get("section_hint") or "routines"
            # Map 'any' to routines for legacy compat, or keep as is? 
            # DayPlanner logic: routines go to 'routines', goal_tasks to 'goal_tasks'
            # We'll just map by type/source_kind for safety
            kind = item.get("type")
            source_kind = item.get("source_kind")
            
            # Simple mapping matching DayPlanner.get_today_plan logic roughly
            if kind == "routine" or kind == "routine_step" or source_kind == "routine":
                sections["routines"].append(item)
            elif kind == "goal_task" or source_kind == "goal_task":
                sections["goal_tasks"].append(item)
            else:
                sections["optional"].append(item)
                
        plan_data = {
            "id": plan_row["id"],
            "date": plan_row["plan_date"].isoformat(),
            "sections": sections,
            "mood_context": plan_row.get("mood_context") or {},
            "_plan_source": "db_peek"
        }
        return jsonify({"plan": plan_data})

    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            mood_context=mood_context,
            force_regen=False,
            plan_date=plan_date,
        )
        sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
        goal_tasks_count = len(sections.get("goal_tasks", []) or [])
        plan_source = plan.get("_plan_source") if isinstance(plan, dict) else None
        logger.info("API: Served today plan goal_tasks_count=%s source=%s", goal_tasks_count, plan_source or "unknown")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to build today plan: {exc}", exc_info=True)
        return api_error(
            "TODAY_PLAN_FAILED",
            "Failed to build today plan",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/today-brief", methods=["GET"])
@require_auth
def get_today_brief():
    """Return a terse tactical brief for voice/read-out."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    args = request.args or {}
    mood_context = {
        "mood": args.get("mood"),
        "fatigue": args.get("fatigue"),
        "time_pressure": args.get("time_pressure") in ("1", "true", "True", "yes"),
    }

    plan_date = _get_local_today(user_id)
    if args.get("plan_date"):
        try:
            plan_date = date.fromisoformat(args.get("plan_date"))
        except ValueError:
            pass

    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            mood_context=mood_context,
            force_regen=False,
            plan_date=plan_date,
        )
        brief = othello_engine.summarise_today_plan(plan)
        logger.info("API: Served today brief")
        return jsonify({"brief": brief})
    except Exception as exc:
        logger.error(f"API: Failed to build today brief: {exc}", exc_info=True)
        return api_error(
            "TODAY_BRIEF_FAILED",
            "Failed to build today brief",
            500,
            details=type(exc).__name__,
        )


# ---------------------------------------------------------------------------
# PROPOSALS (Confirm-gated suggestions)
# ---------------------------------------------------------------------------

def _recover_stale_proposals(user_id: str):
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE suggestions 
                    SET status = 'pending' 
                    WHERE user_id = %s 
                      AND kind = 'plan_proposal' 
                      AND status = 'applying' 
                      AND created_at < NOW() - INTERVAL '10 minutes'
                    """,
                    (user_id,)
                )
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.getLogger("API").warning(f"Recovered {cursor.rowcount} stale applying proposals for user {user_id}")
        except Exception as e:
            logging.getLogger("API").error(f"Failed to recover stale proposals: {e}")

def _list_proposals_core(user_id: str, plan_date_str: str) -> List[Dict]:
    _recover_stale_proposals(user_id)
    suggestions = suggestions_repository.list_suggestions(
        user_id=user_id,
        status="pending",
        kind="plan_proposal",
        limit=100
    )
    filtered = []
    for s in suggestions:
        payload = s.get("payload") or {}
        if payload.get("plan_date") == plan_date_str:
            filtered.append({
                "proposal_id": s["id"],
                "created_at": s["created_at"],
                "title": payload.get("title"),
                "summary": payload.get("summary"),
                "ops": payload.get("ops", []),
                "plan_date": payload.get("plan_date")
            })
    return filtered

def _get_last_pending_proposals(user_id: str, plan_date_str: str, limit: int = 3) -> List[Dict]:
    """
    Retrieve the most recent pending proposals for the given plan date.
    Ordered by ID descending (proxy for creation time).
    """
    _recover_stale_proposals(user_id)
    suggestions = suggestions_repository.list_suggestions(
        user_id=user_id,
        status="pending",
        kind="plan_proposal",
        limit=100 # Fetch enough to filter by date
    )
    
    # Filter by plan_date and sort by ID desc
    filtered = []
    for s in suggestions:
        payload = s.get("payload") or {}
        if payload.get("plan_date") == plan_date_str:
            filtered.append({
                "proposal_id": s["id"],
                "title": payload.get("title"),
                "summary": payload.get("summary"),
                "created_at": s["created_at"]
            })
            
    # Sort by ID descending (newest first)
    filtered.sort(key=lambda x: x["proposal_id"], reverse=True)
    return filtered[:limit]

@app.route("/api/proposals", methods=["GET"])
@require_auth
def list_proposals():
    user_id, error = _get_user_id_or_error()
    if error: return error
    
    plan_date_str = request.args.get("plan_date")
    if not plan_date_str:
        return api_error("VALIDATION_ERROR", "plan_date is required", 400)

    proposals = _list_proposals_core(user_id, plan_date_str)
    return jsonify({"proposals": proposals})


def _get_local_today(user_id: str) -> date:
    """
    Get the local date for the user.
    Defaults to Europe/London if no timezone is configured.
    """
    # TODO: Fetch user timezone from DB or profile
    tz = ZoneInfo("Europe/London")
    return datetime.now(tz).date()

def _format_proposal_preview(plan: Dict, proposal_payload: Dict) -> str:
    """
    Generates a read-only preview string for a proposal payload against a plan.
    """
    # Flatten items for lookup
    all_items = {}
    if plan and "sections" in plan:
        for items in plan["sections"].values():
            if isinstance(items, list):
                for it in items:
                    all_items[it["id"]] = it

    ops = proposal_payload.get("ops", [])
    preview_lines = [f"Ops: {len(ops)}"]
    
    for op in ops:
        item_id = op.get("item_id")
        item = all_items.get(item_id)
        item_label = item.get("label", item_id) if item else item_id
        op_type = op.get("op")
        
        if not item:
            preview_lines.append(f"- [WARN] Item {item_id} not found in today's plan.")
            continue

        if op_type == "set_status":
            old_status = item.get("status", "unknown")
            new_status = op.get("status")
            preview_lines.append(f"- {item_label}: status {old_status} -> {new_status}")
        elif op_type == "snooze":
            minutes = op.get("minutes", 60)
            preview_lines.append(f"- {item_label}: snooze +{minutes}m")
        elif op_type == "reschedule":
            preview_lines.append(f"- {item_label}: reschedule to tomorrow")
        else:
            preview_lines.append(f"- {item_label}: {op_type} (unknown op)")
            
    return "\n".join(preview_lines)

def _validate_and_parse_alternatives(raw_json: str, plan_item_ids: List[str]) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Wrapper to parse alternatives or clarification.
    Returns ({ "alternatives": [...], "need_clarification": ... }, error).
    """
    try:
        cleaned = raw_json.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].startswith("```"): lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        
        if not cleaned.startswith("{"): return None, "NON_JSON"
        data = json.loads(cleaned)
        
        # Clarification check
        if data.get("need_clarification"):
            # Reuse existing validator logic by passing raw json
            return _validate_and_parse_llm_proposal(raw_json, plan_item_ids)
            
        # Alternatives check
        alts = data.get("alternatives")
        if not isinstance(alts, list) or not (1 <= len(alts) <= 2):
            return None, "VALIDATION_ERROR: alternatives must be list of 1-2 items"
            
        valid_alts = []
        for i, alt in enumerate(alts):
            # Validate each as a standalone proposal
            # We re-serialize to reuse the strict validator (inefficient but safe/DRY)
            alt_json = json.dumps(alt)
            prop, err = _validate_and_parse_llm_proposal(alt_json, plan_item_ids)
            if prop:
                valid_alts.append(prop)
            else:
                # If one fails, we skip it. If all fail, we return error.
                pass
                
        if not valid_alts:
            return None, "VALIDATION_ERROR: No valid alternatives found"
            
        return { "alternatives": valid_alts }, None
        
    except Exception as e:
        return None, f"EXCEPTION: {str(e)}"

def _build_plan_context_for_llm(plan: Dict) -> Tuple[str, List[str]]:
    """
    Constructs a compact text representation of the current plan for the LLM.
    Returns (context_string, list_of_valid_ids).
    Truncates to N=40 items to save tokens.
    """
    lines = []
    valid_ids = []
    count = 0
    if "sections" in plan:
        for section_name, items in plan["sections"].items():
            if isinstance(items, list):
                for item in items:
                    if count >= 40:
                        break
                    status = item.get("status", "planned")
                    label = item.get("label", "Untitled")
                    item_id = item.get("id")
                    if item_id:
                        valid_ids.append(str(item_id))
                        lines.append(f"- [{item_id}] {label} ({status}, {section_name})")
                        count += 1
            if count >= 40:
                break
    if not lines:
        return "Plan is empty.", []
    return "\n".join(lines), valid_ids

def _validate_and_parse_llm_proposal(raw_json: str, plan_item_ids: List[str]) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Parses LLM JSON output and validates against strict safety rules.
    Returns (valid_proposal_dict, error_code_string).
    If success, error_code is None.
    If failure, proposal is None and error_code describes why (NON_JSON, JSON_PARSE_ERROR, VALIDATION_ERROR:...).
    """
    try:
        # 1. Clean and Parse
        cleaned = raw_json.strip()
        # Remove markdown fences if present
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        
        # Deterministic non-JSON reject
        if not cleaned.startswith("{"):
            return None, "NON_JSON"
            
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None, "JSON_PARSE_ERROR"
        
        # 2. Structure Check
        if not isinstance(data, dict): return None, "VALIDATION_ERROR: Root must be object"

        # Clarification Branch
        if data.get("need_clarification") is True:
            candidates = data.get("candidates")
            if not isinstance(candidates, list): return None, "VALIDATION_ERROR: candidates must be list"
            
            valid_candidates = []
            for c in candidates:
                if isinstance(c, dict) and str(c.get("item_id")) in plan_item_ids:
                    valid_candidates.append({
                        "item_id": c.get("item_id"),
                        "label": str(c.get("label", ""))[:60]
                    })
            
            if not valid_candidates:
                return None, "VALIDATION_ERROR: No valid candidates provided"
                
            return {
                "need_clarification": True,
                "candidates": valid_candidates[:5],
                "title": "Clarification Needed",
                "summary": str(data.get("summary", "Please clarify item")),
                "ops": []
            }, None

        title = str(data.get("title", "")).strip()
        summary = str(data.get("summary", "")).strip()
        ops = data.get("ops")
        
        if not title or len(title) > 80: return None, "VALIDATION_ERROR: Title missing or too long (>80)"
        if not summary or len(summary) > 240: return None, "VALIDATION_ERROR: Summary missing or too long (>240)"
        if not isinstance(ops, list) or not (1 <= len(ops) <= 10): return None, "VALIDATION_ERROR: Ops must be list of 1-10 items"
        
        # 3. Op Validation
        valid_ops = []
        allowed_ops = {"set_status", "snooze", "reschedule"}
        allowed_statuses = {"planned", "in_progress", "complete", "skipped"}
        
        for i, op in enumerate(ops):
            if not isinstance(op, dict): return None, f"VALIDATION_ERROR: Op {i} is not an object"
            op_type = op.get("op")
            item_id = op.get("item_id")
            
            if op_type not in allowed_ops: return None, f"VALIDATION_ERROR: Op {i} type '{op_type}' invalid"
            
            # Normalize ID for check
            str_id = str(item_id)
            if str_id not in plan_item_ids: return None, f"VALIDATION_ERROR: Op {i} item_id '{item_id}' not in today's plan"
            
            # Prefer int if it looks like one (for downstream compatibility)
            if str_id.isdigit():
                op["item_id"] = int(str_id)
            
            # Strict Schema Enforcement
            keys = set(op.keys())
            if op_type == "set_status":
                if keys != {"op", "item_id", "status"}: return None, f"VALIDATION_ERROR: Op {i} (set_status) has invalid keys {keys}"
                if op.get("status") not in allowed_statuses: return None, f"VALIDATION_ERROR: Op {i} status '{op.get('status')}' invalid"
            elif op_type == "snooze":
                if keys != {"op", "item_id", "minutes"}: return None, f"VALIDATION_ERROR: Op {i} (snooze) has invalid keys {keys}"
                mins = op.get("minutes")
                if not isinstance(mins, int) or not (5 <= mins <= 240): return None, f"VALIDATION_ERROR: Op {i} snooze minutes invalid (5-240)"
            elif op_type == "reschedule":
                if keys != {"op", "item_id", "to"}: return None, f"VALIDATION_ERROR: Op {i} (reschedule) has invalid keys {keys}"
                target = op.get("to")
                if target not in {"tomorrow", "later_today"}: return None, f"VALIDATION_ERROR: Op {i} reschedule.to must be 'tomorrow' or 'later_today'"
                
            valid_ops.append(op)
            
        return {
            "title": title,
            "summary": summary,
            "ops": valid_ops
        }, None
        
    except Exception as e:
        return None, f"UNKNOWN_ERROR: {str(e)}"

def _generate_llm_proposal_with_retry(llm, user_prompt: str, system_prompt: str) -> Tuple[str, int]:
    """
    Generates proposal with a single deterministic retry for JSON failures.
    Returns (raw_response, attempt_count).
    """
    # Attempt 1: Standard
    raw = llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=1000)
    
    # Quick check for obvious JSON failure (heuristic)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        
    is_json_like = cleaned.startswith("{")
    can_parse = False
    if is_json_like:
        try:
            json.loads(cleaned)
            can_parse = True
        except:
            pass
            
    if is_json_like and can_parse:
        return raw, 1
        
    # Attempt 2: Strict Retry
    retry_prompt = system_prompt + "\n\nCRITICAL: Your previous response was invalid JSON. Return a single valid JSON object only. No markdown. No prose."
    raw_retry = llm.generate(user_prompt, system_prompt=retry_prompt, temperature=0.0, max_tokens=1000)
    return raw_retry, 2

def _parse_propose_text_to_ops(user_id: str, text: str) -> Optional[Dict]:
    """
    Parses natural language intent into a structured proposal.
    Supported intents:
    - "start next": Start the first planned item.
    - "complete <item>": Complete an item.
    - "snooze <item>": Snooze an item (default 60 mins if not specified).
    - "move <item>": Reschedule an item (to tomorrow if not specified).
    """
    text = text.strip().lower()
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    
    # Ensure we work on the user's local today
    local_today = _get_local_today(user_id)
    
    # We need the plan to resolve items
    plan = othello_engine.day_planner.get_today_plan(
        user_id, 
        force_regen=False,
        plan_date=local_today
    )
    if not plan:
        return None
        
    # Flatten items for searching
    all_items = []
    if "sections" in plan:
        for items in plan["sections"].values():
            if isinstance(items, list):
                all_items.extend(items)
    
    # Helper to find item by fuzzy match
    def find_item(query):
        # 1. Exact ID match
        for item in all_items:
            if item["id"] == query:
                return item
        # 2. Label contains query
        for item in all_items:
            if query in item.get("label", "").lower():
                return item
        return None

    ops = []
    title = ""
    summary = ""
    
    # Intent: Start Next
    if text == "start next":
        next_action = None
        for item in all_items:
            if item.get("status") == "planned":
                next_action = item
                break
        if next_action:
            title = "Start Next Action"
            summary = f"Mark '{next_action.get('label')}' as in progress"
            ops.append({
                "op": "set_status",
                "item_id": next_action["id"],
                "status": "in_progress"
            })
        else:
            return None # No next action found

    # Intent: Complete
    elif text.startswith("complete "):
        query = text[9:].strip()
        target = find_item(query)
        if target:
            title = "Complete Item"
            summary = f"Mark '{target.get('label')}' as complete"
            ops.append({
                "op": "set_status",
                "item_id": target["id"],
                "status": "complete"
            })
        else:
            return None # Item not found

    # Intent: Snooze
    elif text.startswith("snooze"):
        query = text[6:].strip()
        target = None
        if not query:
            # Find in_progress
            for item in all_items:
                if item.get("status") == "in_progress":
                    target = item
                    break
            # If no in_progress, find next planned
            if not target:
                for item in all_items:
                    if item.get("status") == "planned":
                        target = item
                        break
        else:
            target = find_item(query)
            
        if target:
            title = "Snooze Item"
            summary = f"Snooze '{target.get('label')}' for 60m"
            ops.append({
                "op": "snooze",
                "item_id": target["id"],
                "minutes": 60 # Default
            })
        else:
            return None

    # Intent: Move (Reschedule)
    elif text.startswith("move "):
        query = text[5:].strip()
        target = find_item(query)
        if target:
            title = "Move Item"
            summary = f"Move '{target.get('label')}' to tomorrow"
            ops.append({
                "op": "reschedule",
                "item_id": target["id"],
                "status": "rescheduled",
            })
        else:
            return None
            
    else:
        return None

    if not ops:
        return None
        
    return {
        "plan_date": local_today.isoformat(),
        "title": title,
        "summary": summary,
        "ops": ops
    }

def _save_proposal(user_id: str, proposal: Dict, provenance_data: Optional[Dict] = None) -> Dict:
    """Persists a single proposal if not already pending."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Check for identical pending proposal
            cursor.execute(
                "SELECT payload FROM suggestions WHERE user_id = %s AND status = 'pending' AND kind = 'plan_proposal'",
                (user_id,)
            )
            existing_rows = cursor.fetchall()
            
            def _compute_hash(p_payload):
                canonical = {
                    "plan_date": p_payload.get("plan_date"),
                    "ops": p_payload.get("ops", [])
                }
                s = json.dumps(canonical, sort_keys=True)
                return hashlib.sha256(s.encode("utf-8")).hexdigest()

            new_hash = _compute_hash(proposal)
            for row in existing_rows:
                if _compute_hash(row[0] or {}) == new_hash:
                    return {"status": "duplicate", "message": "Identical proposal already pending."}

            final_provenance = {"generated_by": "user_command"}
            if provenance_data:
                final_provenance.update(provenance_data)

            cursor.execute(
                """
                INSERT INTO suggestions (user_id, kind, status, payload, provenance, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (user_id, "plan_proposal", "pending", json.dumps(proposal), json.dumps(final_provenance))
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return {"status": "created", "proposal_id": new_id}

def _generate_proposals_core(user_id: str, plan_date: date) -> List[Dict]:
    local_today = _get_local_today(user_id)
    if plan_date != local_today:
        raise ValueError("READ_ONLY_MODE: Cannot generate proposals for past/future dates")

    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    
    plan = othello_engine.day_planner.get_today_plan(
        user_id,
        plan_date=plan_date,
        force_regen=False
    )
    if not plan:
        return []
        
    new_proposals = []
    
    sections = plan.get("sections", {})
    all_items = []
    for k, items in sections.items():
        if isinstance(items, list):
            all_items.extend(items)
            
    next_action = None
    for item in all_items:
        if item.get("status") == "planned":
            next_action = item
            break
            
    if next_action:
        new_proposals.append({
            "plan_date": plan_date.isoformat(),
            "title": "Start Next Action",
            "summary": f"Mark '{next_action.get('title') or 'Next Item'}' as in progress",
            "ops": [
                {"op": "set_status", "item_id": next_action["id"], "status": "in_progress"}
            ]
        })

    overdue_ops = []
    plan_date_str = plan_date.isoformat()
    for item in all_items:
        reschedule_to = item.get("reschedule_to")
        if reschedule_to and reschedule_to < plan_date_str and item.get("status") == "planned":
            overdue_ops.append({
                "op": "reschedule", 
                "item_id": item["id"], 
                "reschedule_to": None, 
                "status": "planned"
            })
            if len(overdue_ops) >= 3: break
            
    if overdue_ops:
        new_proposals.append({
            "plan_date": plan_date_str,
            "title": "Normalize Overdue",
            "summary": f"Clear overdue flags for {len(overdue_ops)} items",
            "ops": overdue_ops
        })

    created = []
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT payload FROM suggestions WHERE user_id = %s AND status = 'pending' AND kind = 'plan_proposal' FOR UPDATE",
                    (user_id,)
                )
                existing_rows = cursor.fetchall()
                
                def _compute_hash(p_payload):
                    canonical = {
                        "plan_date": p_payload.get("plan_date"),
                        "ops": p_payload.get("ops", [])
                    }
                    s = json.dumps(canonical, sort_keys=True)
                    return hashlib.sha256(s.encode("utf-8")).hexdigest()

                existing_hashes = set()
                for row in existing_rows:
                    existing_hashes.add(_compute_hash(row[0] or {}))

                for p in new_proposals:
                    p_hash = _compute_hash(p)
                    if p_hash in existing_hashes:
                        continue
                        
                    cursor.execute(
                        """
                        INSERT INTO suggestions (user_id, kind, status, payload, provenance, created_at)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        RETURNING id, created_at
                        """,
                        (user_id, "plan_proposal", "pending", json.dumps(p), json.dumps({"generated_by": "rule_engine"}))
                    )
                    new_row = cursor.fetchone()
                    created.append({
                        "proposal_id": new_row[0],
                        "created_at": new_row[1],
                        "title": p["title"],
                        "summary": p["summary"],
                        "ops": p["ops"],
                        "plan_date": p["plan_date"]
                    })
                conn.commit()
        except Exception as e:
            conn.rollback()
            logging.getLogger("API").error(f"Failed to generate proposals: {e}", exc_info=True)
            raise e
        
    return created

@app.route("/api/proposals/generate", methods=["POST"])
@require_auth
def generate_proposals():
    user_id, error = _get_user_id_or_error()
    if error: return error
    
    data = request.json or {}
    plan_date_str = data.get("plan_date")
    
    local_today = _get_local_today(user_id)
    
    if plan_date_str:
        try:
            plan_date = date.fromisoformat(plan_date_str)
        except ValueError:
            return api_error("VALIDATION_ERROR", "Invalid plan_date format (expected YYYY-MM-DD)", 400)
    else:
        plan_date = local_today

    try:
        created = _generate_proposals_core(user_id, plan_date)
        return jsonify({"proposals": created})
    except ValueError as ve:
        if "READ_ONLY_MODE" in str(ve):
            return api_error("READ_ONLY_MODE", str(ve), 403)
        return api_error("VALIDATION_ERROR", str(ve), 400)
    except Exception as e:
        return api_error("GENERATE_FAILED", str(e), 500)


def _apply_proposal_core(user_id: str, proposal_id: int) -> tuple[bool, str, Optional[str]]:
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    local_today = _get_local_today(user_id)

    ops_to_apply = []
    plan_date_str = None
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                # 1. Lock & Check
                cursor.execute(
                    "SELECT id, status, payload FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal' FOR UPDATE",
                    (proposal_id, user_id)
                )
                row = cursor.fetchone()
                if not row:
                    return False, "NOT_FOUND", "Proposal not found"
                
                s_id, status, payload = row
                if status == "applying":
                    return False, "CONFLICT", "Proposal is currently being applied"
                
                if status != "pending":
                    return True, status, "Already decided"
                
                # 2. Read-only Guard
                plan_date_str = payload.get("plan_date")
                if not plan_date_str:
                     return False, "VALIDATION_ERROR", "Proposal missing plan_date"
                
                try:
                    plan_date = date.fromisoformat(plan_date_str)
                except ValueError:
                    return False, "VALIDATION_ERROR", "Invalid plan_date format"

                if plan_date != local_today:
                    return False, "READ_ONLY_MODE", "Cannot apply proposals for past/future dates"

                # 3. Validate Ops (Allowlist + Required Fields)
                ops = payload.get("ops", [])
                allowed_ops = {"set_status", "reschedule", "snooze"}
                allowed_statuses = {"planned", "in_progress", "complete", "skipped", "rescheduled"}
                
                # Pre-fetch plan items to validate existence
                plan = othello_engine.day_planner.get_today_plan(user_id, force_regen=False, plan_date=local_today)
                plan_item_ids = set()
                if plan and "sections" in plan:
                    for items in plan["sections"].values():
                        if isinstance(items, list):
                            for it in items:
                                plan_item_ids.add(it.get("id"))

                for op in ops:
                    op_type = op.get("op")
                    if not op_type or op_type not in allowed_ops:
                        return False, "INVALID_OP", f"Unknown or missing op type: {op_type}"
                    
                    item_id = op.get("item_id")
                    if not item_id:
                        return False, "INVALID_OP", "Missing item_id"
                    if item_id not in plan_item_ids:
                        return False, "INVALID_OP", f"Item {item_id} not found in today's plan"
                        
                    target_status = op.get("status")
                    if op_type == "set_status":
                        if not target_status or target_status not in allowed_statuses:
                            return False, "INVALID_OP", f"Invalid status: {target_status}"
                    elif op_type == "reschedule":
                        if target_status and target_status not in allowed_statuses:
                             return False, "INVALID_OP", f"Invalid status: {target_status}"
                    elif op_type == "snooze":
                        minutes = op.get("minutes")
                        if minutes is not None and not isinstance(minutes, int):
                             return False, "INVALID_OP", "Snooze minutes must be an integer"

                ops_to_apply = ops
                
                # 4. Mark Applying (Commit Phase 1)
                cursor.execute(
                    "UPDATE suggestions SET status = 'applying' WHERE id = %s",
                    (s_id,)
                )
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logging.getLogger("API").error(f"Failed to validate/lock proposal {proposal_id}: {e}", exc_info=True)
            return False, "APPLY_FAILED", str(e)

    # Phase 2: Execute Ops (External Commits)
    apply_error = None
    try:
        for op in ops_to_apply:
            op_type = op.get("op")
            item_id = op.get("item_id")
            if op_type == "set_status":
                othello_engine.day_planner.update_plan_item_status(
                    user_id, 
                    item_id, 
                    op["status"], 
                    plan_date=plan_date_str
                )
            elif op_type == "reschedule":
                othello_engine.day_planner.update_plan_item_status(
                    user_id,
                    item_id,
                    op.get("status", "rescheduled"),
                    plan_date=plan_date_str,
                    reschedule_to=op.get("reschedule_to")
                )
            elif op_type == "snooze":
                othello_engine.day_planner.snooze_plan_item(
                    user_id,
                    item_id,
                    op.get("minutes", 60),
                    plan_date=plan_date_str
                )
    except Exception as e:
        apply_error = e
        logging.getLogger("API").error(f"Failed to execute ops for proposal {proposal_id}: {e}", exc_info=True)

    # Phase 3: Finalize Status
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, status FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal' FOR UPDATE",
                    (proposal_id, user_id)
                )
                row = cursor.fetchone()
                if row:
                    s_id, status = row
                    if status == "applying":
                        if apply_error:
                            cursor.execute(
                                "UPDATE suggestions SET status = 'pending' WHERE id = %s",
                                (s_id,)
                            )
                        else:
                            cursor.execute(
                                "UPDATE suggestions SET status = 'accepted', decided_at = NOW() WHERE id = %s",
                                (s_id,)
                            )
                        conn.commit()
        except Exception as e:
            conn.rollback()
            logging.getLogger("API").error(f"Failed to finalize proposal {proposal_id}: {e}", exc_info=True)
            return False, "APPLY_FINALIZE_FAILED", str(e)

    if apply_error:
        return False, "APPLY_EXECUTION_FAILED", str(apply_error)
    
    return True, "accepted", plan_date_str

@app.route("/api/proposals/apply", methods=["POST"])
@require_auth
def apply_proposal():
    user_id, error = _get_user_id_or_error()
    if error: return error
    
    data = request.json or {}
    proposal_id = data.get("proposal_id")
    if not proposal_id:
        return api_error("VALIDATION_ERROR", "proposal_id required", 400)

    ok, status, detail = _apply_proposal_core(user_id, proposal_id)
    if not ok:
        code = 500
        if status in ("NOT_FOUND",): code = 404
        elif status in ("CONFLICT",): code = 409
        elif status in ("VALIDATION_ERROR", "INVALID_OP"): code = 400
        elif status in ("READ_ONLY_MODE",): code = 403
        return api_error(status, detail, code)
        
    return jsonify({"ok": True, "proposal_id": proposal_id, "status": status, "plan_date": detail})


def _reject_proposal_core(user_id: str, proposal_id: int) -> tuple[bool, str, Optional[str]]:
    local_today = _get_local_today(user_id)
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, status, payload FROM suggestions WHERE id = %s AND user_id = %s AND kind = 'plan_proposal' FOR UPDATE",
                    (proposal_id, user_id)
                )
                row = cursor.fetchone()
                if not row:
                    return False, "NOT_FOUND", "Proposal not found"
                
                s_id, status, payload = row
                if status == "applying":
                    return False, "CONFLICT", "Proposal is currently being applied"
                    
                if status != "pending":
                    return True, status, "Already decided"
                
                plan_date_str = payload.get("plan_date")
                if not plan_date_str:
                     return False, "VALIDATION_ERROR", "Proposal missing plan_date"
                
                try:
                    plan_date = date.fromisoformat(plan_date_str)
                except ValueError:
                    return False, "VALIDATION_ERROR", "Invalid plan_date format"

                if plan_date != local_today:
                    return False, "READ_ONLY_MODE", "Cannot reject proposals for past/future dates"

                cursor.execute(
                    "UPDATE suggestions SET status = 'rejected', decided_at = NOW() WHERE id = %s",
                    (s_id,)
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            logging.getLogger("API").error(f"Failed to reject proposal {proposal_id}: {e}", exc_info=True)
            return False, "REJECT_FAILED", str(e)

    return True, "rejected", None

@app.route("/api/proposals/reject", methods=["POST"])
@require_auth
def reject_proposal():
    user_id, error = _get_user_id_or_error()
    if error: return error
    
    data = request.json or {}
    proposal_id = data.get("proposal_id")
    if not proposal_id:
        return api_error("VALIDATION_ERROR", "proposal_id required", 400)

    ok, status, detail = _reject_proposal_core(user_id, proposal_id)
    if not ok:
        code = 500
        if status in ("NOT_FOUND",): code = 404
        elif status in ("CONFLICT",): code = 409
        elif status in ("VALIDATION_ERROR",): code = 400
        elif status in ("READ_ONLY_MODE",): code = 403
        return api_error(status, detail, code)

    return jsonify({"ok": True, "proposal_id": proposal_id, "status": status})


# ---------------------------------------------------------------------------
# Routines CRUD
# ---------------------------------------------------------------------------

@app.route("/api/routines", methods=["GET"])
@require_auth
def list_routines():
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        routines = routines_repository.list_routines_with_steps(user_id)
        return jsonify({"ok": True, "routines": routines})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to list routines: {e}", exc_info=True)
        return api_error("ROUTINE_LIST_FAILED", str(e), 500)

@app.route("/api/routines", methods=["POST"])
@require_auth
def create_routine():
    user_id, error = _get_user_id_or_error()
    if error: return error
    data = request.json or {}
    title = data.get("title")
    if not title:
        return api_error("INVALID_INPUT", "Title is required", 400)
    
    try:
        schedule_rule = data.get("schedule_rule", {})
        # Default to all days if days is missing/null (but respect empty list)
        if "days" not in schedule_rule or schedule_rule["days"] is None:
            schedule_rule["days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        
        if isinstance(schedule_rule.get("days"), list):
            valid = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
            schedule_rule["days"] = [d.strip().lower()[:3] for d in schedule_rule["days"] if str(d).strip().lower()[:3] in valid]

        routine = routines_repository.create_routine(
            user_id, 
            title, 
            schedule_rule, 
            data.get("enabled", True)
        )
        return jsonify({"ok": True, "routine": routine})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to create routine: {e}", exc_info=True)
        return api_error("ROUTINE_CREATE_FAILED", str(e), 500)

@app.route("/api/routines/<routine_id>", methods=["PATCH"])
@require_auth
def update_routine(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        patch = request.json or {}
        if "schedule_rule" in patch:
            schedule_rule = patch["schedule_rule"]
            # If days is explicitly None or missing in a replacement object, default to all
            if "days" not in schedule_rule or schedule_rule["days"] is None:
                 schedule_rule["days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

            if isinstance(schedule_rule.get("days"), list):
                valid = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
                schedule_rule["days"] = [d.strip().lower()[:3] for d in schedule_rule["days"] if str(d).strip().lower()[:3] in valid]
            patch["schedule_rule"] = schedule_rule

        routine = routines_repository.update_routine(user_id, routine_id, patch)
        if not routine:
            return api_error("NOT_FOUND", "Routine not found", 404)
        return jsonify({"ok": True, "routine": routine})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to update routine: {e}", exc_info=True)
        return api_error("ROUTINE_UPDATE_FAILED", str(e), 500)

@app.route("/api/routines/<routine_id>", methods=["DELETE"])
@require_auth
def delete_routine(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        success = routines_repository.delete_routine(user_id, routine_id)
        if not success:
            return api_error("NOT_FOUND", "Routine not found", 404)
        return jsonify({"ok": True})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to delete routine: {e}", exc_info=True)
        return api_error("ROUTINE_DELETE_FAILED", str(e), 500)

@app.route("/api/routines/<routine_id>/steps", methods=["POST"])
@require_auth
def create_routine_step(routine_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    data = request.json or {}
    title = data.get("title")
    if not title:
        return api_error("INVALID_INPUT", "Title is required", 400)
        
    try:
        step = routines_repository.create_step(
            user_id,
            routine_id,
            title,
            est_minutes=data.get("est_minutes"),
            energy=data.get("energy"),
            tags=data.get("tags"),
            order_index=data.get("order_index")
        )
        return jsonify({"ok": True, "step": step})
    except ValueError as ve:
        return api_error("INVALID_INPUT", str(ve), 400)
    except Exception as e:
        logging.getLogger("API").error(f"Failed to create step: {e}", exc_info=True)
        return api_error("STEP_CREATE_FAILED", str(e), 500)

@app.route("/api/steps/<step_id>", methods=["PATCH"])
@require_auth
def update_routine_step(step_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        step = routines_repository.update_step(user_id, step_id, request.json or {})
        if not step:
            return api_error("NOT_FOUND", "Step not found", 404)
        return jsonify({"ok": True, "step": step})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to update step: {e}", exc_info=True)
        return api_error("STEP_UPDATE_FAILED", str(e), 500)

@app.route("/api/steps/<step_id>", methods=["DELETE"])
@require_auth
def delete_routine_step(step_id):
    user_id, error = _get_user_id_or_error()
    if error: return error
    try:
        success = routines_repository.delete_step(user_id, step_id)
        if not success:
            return api_error("NOT_FOUND", "Step not found", 404)
        return jsonify({"ok": True})
    except Exception as e:
        logging.getLogger("API").error(f"Failed to delete step: {e}", exc_info=True)
        return api_error("STEP_DELETE_FAILED", str(e), 500)


@app.route("/api/plan/update", methods=["POST"])
@require_auth
def update_plan_item():
    """Update lifecycle status for a plan item (complete/skip/reschedule)."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    status = data.get("status")
    plan_date = data.get("plan_date")
    reason = data.get("reason")
    reschedule_to = data.get("reschedule_to")
    snooze_minutes = data.get("snooze_minutes")

    if not item_id:
        return api_error("VALIDATION_ERROR", "item_id is required", 400)

    if snooze_minutes is not None:
        try:
            plan = othello_engine.day_planner.snooze_plan_item(
                user_id,
                item_id=item_id,
                snooze_minutes=int(snooze_minutes),
                plan_date=plan_date
            )
            return jsonify({"plan": plan})
        except Exception as exc:
            logger.error(f"API: Failed to snooze item {item_id}: {exc}", exc_info=True)
            return api_error("PLAN_SNOOZE_FAILED", str(exc), 500)

    if not status:
        return api_error("VALIDATION_ERROR", "status is required", 400)

    try:
        plan = othello_engine.day_planner.update_plan_item_status(
            user_id,
            item_id=item_id,
            status=status,
            plan_date=plan_date,
            reason=reason,
            reschedule_to=reschedule_to,
        )
        logger.info(f"API: Updated plan item {item_id} -> {status}")
        return jsonify({"plan": plan})
    except ValueError as ve:
        return api_error("INVALID_STATUS", str(ve), 400)
    except Exception as exc:
        logger.error(f"API: Failed to update plan item {item_id}: {exc}", exc_info=True)
        return api_error(
            "PLAN_UPDATE_FAILED",
            "Failed to update plan item",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/plan/rebuild", methods=["POST"])
@require_auth
def rebuild_today_plan():
    """Force regeneration of today's plan (used when context shifts)."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    data = request.get_json() or {}
    mood_context = data.get("mood_context") or data
    local_today = _get_local_today(user_id)
    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            mood_context=mood_context,
            force_regen=True,
            plan_date=local_today,
        )
        logger.info("API: Rebuilt today plan on demand for %s", local_today)
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to rebuild plan: {exc}", exc_info=True)
        return api_error(
            "PLAN_REBUILD_FAILED",
            "Failed to rebuild plan",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/goals", methods=["GET", "POST"])
@require_auth
def goals():
    """
    GET: list goals for the current user.
    POST: create a new goal.

    POST body:
        { "title": "My long-term goal" }
    """
    logger = logging.getLogger("API")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]

    if request.method == "GET":
        user_id, error = _get_user_id_or_error()
        if error:
            return error
        logger.debug(
            "API: get_goals session_user=%s authed=%s",
            session.get("user_id"),
            bool(session.get("authed")),
        )
        try:
            goals = architect_agent.goal_mgr.list_goals(user_id)
            return jsonify({"goals": goals})
        except Exception as e:
            logging.getLogger("ARCHITECT").error(f"Failed to fetch goals: {e}")
            return api_error(
                "GOALS_FETCH_FAILED",
                "Failed to fetch goals",
                500,
                details=type(e).__name__,
            )

    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api goal creation; use /v1 confirm flow",
            409,
        )

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)

    raw_title = data.get("title")
    if raw_title is None:
        return api_error("VALIDATION_ERROR", "title is required", 400)

    title = str(raw_title).strip()
    if len(title) < 3:
        return api_error("VALIDATION_ERROR", "title is too short", 400)

    raw_description = data.get("description")
    description = ""
    if raw_description is not None:
        description = str(raw_description).strip()

    source_client_message_id = data.get("source_client_message_id")

    normalized_title = _normalize_goal_title(title)
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error

    try:
        from db import goals_repository

        existing = goals_repository.list_goals(user_id, include_archived=False) or []
        for goal in existing:
            existing_title = _normalize_goal_title(goal.get("title") or goal.get("text") or "")
            if existing_title and existing_title == normalized_title:
                goal_id = goal.get("id")
                goal_payload = architect_agent.goal_mgr.get_goal(user_id, goal_id) if goal_id else None
                if goal_payload is None:
                    goal_payload = {"id": goal_id, "text": goal.get("title") or ""}
                logger.debug(
                    "API: create_goal request_id=%s user_id=%s normalized_title=%s created=%s",
                    request_id,
                    user_id,
                    normalized_title,
                    False,
                )
                return jsonify(
                    {
                        "ok": True,
                        "created": False,
                        "goal": goal_payload,
                        "goal_id": goal_payload.get("id"),
                        "meta": {"intent": "goal_exists"},
                    }
                )

        created = goals_repository.create_goal(
            {"title": title, "description": description, "status": "active"},
            user_id,
        )
        goal_id = created.get("id") if isinstance(created, dict) else None
        if not goal_id:
            logger.error("API: create_goal failed to return a goal id")
            return api_error("GOAL_CREATE_FAILED", "Failed to create goal", 500)

        goal_payload = architect_agent.goal_mgr.get_goal(user_id, goal_id)
        if goal_payload is None:
            goal_payload = {"id": goal_id, "text": title}
        logger.debug(
            "API: create_goal request_id=%s user_id=%s normalized_title=%s created=%s",
            request_id,
            user_id,
            normalized_title,
            True,
        )
        logger.info(
            "API: commit create_goal request_id=%s source_client_message_id=%s goal_id=%s",
            request_id,
            source_client_message_id,
            goal_id,
        )
        return jsonify(
            {
                "ok": True,
                "created": True,
                "goal": goal_payload,
                "goal_id": goal_id,
                "meta": {"intent": "goal_created"},
            }
        )
    except Exception as exc:
        logger.error("API: create_goal failed: %s", exc, exc_info=True)
        return api_error(
            "GOAL_CREATE_FAILED",
            "Failed to create goal",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/goals/<int:goal_id>/notes", methods=["POST"])
@require_auth
def add_goal_note(goal_id: int):
    logger = logging.getLogger("API")
    request_id = _get_request_id()
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api goal notes; use /v1 confirm flow",
            409,
        )

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("VALIDATION_ERROR", "JSON object required", 400)

    raw_text = data.get("text")
    if raw_text is None:
        return api_error("VALIDATION_ERROR", "text is required", 400)
    text = str(raw_text).strip()
    if not text:
        return api_error("VALIDATION_ERROR", "text is required", 400)

    source_client_message_id = data.get("source_client_message_id")

    try:
        goal = architect_agent.goal_mgr.get_goal(user_id, goal_id)
    except Exception as exc:
        logger.error(
            "API: add_goal_note lookup failed request_id=%s goal_id=%s",
            request_id,
            goal_id,
            exc_info=True,
        )
        return api_error(
            "GOAL_STORAGE_UNAVAILABLE",
            "Goal storage unavailable",
            503,
            details=type(exc).__name__,
        )

    if goal is None:
        return api_error("GOAL_NOT_FOUND", "Goal not found", 404, details={"goal_id": goal_id})

    status = (goal.get("status") or "").strip().lower()
    if status == "archived":
        return api_error("GOAL_ARCHIVED", "Goal is archived", 409, details={"goal_id": goal_id})

    result = architect_agent.goal_mgr.add_note_to_goal(
        user_id,
        goal_id,
        "user",
        text,
        request_id=request_id,
    )
    ok = isinstance(result, dict) and result.get("ok")
    if not ok:
        reason = result.get("reason") if isinstance(result, dict) else "unknown"
        return api_error(
            "GOAL_NOTE_FAILED",
            "Failed to add note",
            500,
            details={"reason": reason},
        )

    logger.info(
        "API: commit add_goal_note request_id=%s goal_id=%s source_client_message_id=%s",
        request_id,
        goal_id,
        source_client_message_id,
    )
    return jsonify({"ok": True, "goal_id": goal_id, "meta": {"intent": "goal_note_added"}})


@app.route("/api/goals/unfocus", methods=["POST"])
@require_auth
def unfocus_goal():
    logger = logging.getLogger("API")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    try:
        if hasattr(architect_agent.goal_mgr, "clear_active_goal"):
            architect_agent.goal_mgr.clear_active_goal(user_id)
            logger.info("API: Cleared active goal request_id=%s user_id=%s", request_id, user_id)
            return jsonify({"ok": True, "request_id": request_id})
        return api_error(
            "GOAL_FOCUS_UNAVAILABLE",
            "Goal focus unavailable",
            503,
            details="active_goal_id not supported",
        )
    except Exception as exc:
        logger.exception(
            "API: Failed to clear active goal request_id=%s",
            request_id,
            extra={"request_id": request_id},
        )
        return api_error(
            "GOAL_UNFOCUS_FAILED",
            "Failed to clear active goal",
            500,
            details=type(exc).__name__,
        )


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
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    try:
        goal = architect_agent.goal_mgr.get_goal_with_plan(user_id, goal_id)
        
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found")
            return api_error(
                "GOAL_NOT_FOUND",
                "Goal not found",
                404,
                extra={"goal_id": goal_id},
            )
        
        logger.info(f"API: Retrieved goal #{goal_id} with {len(goal.get('plan_steps', []))} steps")
        return jsonify({"goal": goal})

    except ValueError as exc:
        reason = str(exc)
        if reason == "INVALID_GOAL_ID":
            return api_error("VALIDATION_ERROR", f"Invalid goal ID format: {goal_id}", 400)

        logger.error(f"API: get_goal_with_plan ValueError for {goal_id}: {reason}", exc_info=True)
        return api_error("INTERNAL_ERROR", "Failed to retrieve goal", 500)

    except Exception as e:
        logger.error(f"API: Failed to fetch goal #{goal_id}: {e}", exc_info=True)
        return api_error(
            "GOAL_FETCH_FAILED",
            "Failed to fetch goal",
            500,
            details=type(e).__name__,
            extra={"goal_id": goal_id},
        )


@app.route("/api/goals/<int:goal_id>/archive", methods=["POST"])
@require_auth
def archive_goal(goal_id):
    """Archive (soft delete) a goal and emit a goal_event if available."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api goal archive; use /v1 confirm flow",
            409,
        )

    try:
        goal = architect_agent.goal_mgr.get_goal(user_id, goal_id)
    except Exception as exc:
        logger.error("API: Failed to load goal for archive: %s", exc, exc_info=True)
        return api_error(
            "GOAL_STORAGE_UNAVAILABLE",
            "Goal storage unavailable",
            503,
            details=type(exc).__name__,
            extra={"goal_id": goal_id},
        )

    if goal is None:
        return api_error(
            "GOAL_NOT_FOUND",
            "Goal not found",
            404,
            extra={"goal_id": goal_id},
        )

    status = (goal.get("status") or "").strip().lower()
    if status == "archived":
        return api_error(
            "GOAL_ARCHIVED",
            "Goal already archived",
            409,
            extra={"goal_id": goal_id},
        )

    try:
        archived_goal = architect_agent.goal_mgr.archive_goal(user_id, goal_id)
    except Exception as exc:
        logger.error("API: Failed to archive goal %s: %s", goal_id, exc, exc_info=True)
        return api_error(
            "GOAL_ARCHIVE_FAILED",
            "Failed to archive goal",
            500,
            details=type(exc).__name__,
            extra={"goal_id": goal_id},
        )

    if archived_goal is None:
        return api_error(
            "GOAL_NOT_FOUND",
            "Goal not found",
            404,
            extra={"goal_id": goal_id},
        )

    event_emitted = False
    try:
        from db.goal_events_repository import safe_append_goal_event
        payload = {"previous_status": status, "new_status": "archived"}
        result = safe_append_goal_event(
            user_id,
            goal_id,
            None,
            "goal_archived",
            payload,
            request_id=request_id,
        )
        event_emitted = bool(result.get("ok"))
    except Exception as exc:
        logger.warning("API: Goal archive event skipped: %s", exc, exc_info=True)
        event_emitted = False

    return jsonify(
        {
            "ok": True,
            "goal_id": goal_id,
            "status": "archived",
            "event_emitted": event_emitted,
            "request_id": request_id,
        }
    )


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
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    try:
        all_goals = architect_agent.goal_mgr.list_goals(user_id)
        
        # Filter for active goals
        active_goals = [g for g in all_goals if g.get("status") == "active"]
        
        results = []
        for goal in active_goals:
            goal_id = goal.get("id")
            if goal_id is None:
                continue
            
            # Get next action for this goal
            next_step = architect_agent.goal_mgr.get_next_action_for_goal(user_id, goal_id)
            
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
        return api_error(
            "GOALS_FETCH_FAILED",
            "Failed to fetch active goals with next actions",
            500,
            details=type(e).__name__,
        )


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
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api step updates; use /v1 confirm flow",
            409,
        )
    data = request.get_json() or {}
    new_status = data.get("status")
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "done"]
    if not new_status or new_status not in valid_statuses:
        return api_error(
            "VALIDATION_ERROR",
            "Invalid status. Must be one of: pending, in_progress, done",
            400,
            extra={"valid_statuses": valid_statuses},
        )
    
    try:
        updated_step = architect_agent.goal_mgr.update_plan_step_status(
            user_id, goal_id, step_id, new_status
        )
        
        if updated_step is None:
            logger.warning(f"API: Failed to update step #{step_id} for goal #{goal_id}")
            return api_error(
                "STEP_NOT_FOUND",
                "Step not found or does not belong to this goal",
                404,
                extra={"goal_id": goal_id, "step_id": step_id},
            )
        
        logger.info(f"API: Updated step #{step_id} status to '{new_status}'")
        return jsonify({"step": updated_step})
        
    except Exception as e:
        logger.error(f"API: Failed to update step status: {e}", exc_info=True)
        return api_error(
            "STEP_UPDATE_FAILED",
            "Failed to update step status",
            500,
            details=type(e).__name__,
            extra={"goal_id": goal_id, "step_id": step_id},
        )


@app.route("/api/goals/<int:goal_id>/steps/<int:step_id>/detail", methods=["POST"])
@require_auth
def update_step_detail(goal_id, step_id):
    """
    Update the detail field for a specific plan step.

    Request body:
        {
            "detail": "Optional elaboration"
        }

    Returns:
        {
            "step": {
                "goal_id": 1,
                "step_id": 2,
                "detail": "Optional elaboration"
            }
        }
    """
    logger = logging.getLogger("API")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    request_id = _get_request_id()
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api step detail updates; use /v1 confirm flow",
            409,
        )
    data = request.get_json() or {}
    detail = data.get("detail")
    raw_step_index = data.get("step_index")
    if raw_step_index is None:
        raw_step_index = data.get("stepIndex")
    raw_body_step_id = data.get("step_id")
    if raw_body_step_id is None:
        raw_body_step_id = data.get("stepId")

    logger.info(
        "API: step detail types goal_id=%s(%s) step_id=%s(%s) raw_step_index=%s(%s) raw_body_step_id=%s(%s)",
        goal_id,
        type(goal_id).__name__,
        step_id,
        type(step_id).__name__,
        raw_step_index,
        type(raw_step_index).__name__,
        raw_body_step_id,
        type(raw_body_step_id).__name__,
    )

    if detail is None or not isinstance(detail, str):
        return api_error("VALIDATION_ERROR", "detail is required", 400)

    step_index = None
    if raw_step_index is not None:
        try:
            step_index = int(raw_step_index)
        except (TypeError, ValueError):
            step_index = None

    body_step_id = None
    if raw_body_step_id is not None:
        try:
            body_step_id = int(raw_body_step_id)
        except (TypeError, ValueError):
            body_step_id = None

    try:
        updated = architect_agent.goal_mgr.update_plan_step_detail(
            user_id,
            goal_id,
            step_id,
            detail,
            step_index=step_index,
            request_id=request_id,
        )
        resolved_step_id = updated.get("step_id") if isinstance(updated, dict) else None
        matched = bool(updated)
        logger.info(
            "API: step detail update request_id=%s user_id=%s goal_id=%s step_id=%s body_step_id=%s step_index=%s matched=%s resolved_step_id=%s",
            request_id,
            user_id,
            goal_id,
            step_id,
            body_step_id,
            step_index,
            matched,
            resolved_step_id,
        )
        if matched and step_index is not None and resolved_step_id and resolved_step_id != step_id:
            logger.warning(
                "API: step detail update used step_index fallback request_id=%s user_id=%s goal_id=%s step_id=%s resolved_step_id=%s step_index=%s",
                request_id,
                user_id,
                goal_id,
                step_id,
                resolved_step_id,
                step_index,
            )
        if updated is None:
            logger.warning(f"API: Failed to update step detail #{step_id} for goal #{goal_id}")
            return api_error(
                "STEP_NOT_FOUND",
                "Step not found or does not belong to this goal",
                404,
                extra={"goal_id": goal_id, "step_id": step_id},
            )

        logger.info(f"API: Updated step detail #{step_id} for goal #{goal_id}")
        return jsonify({"step": updated})
    except ValueError as exc:
        reason = str(exc)
        logger.error(
            "API: Step detail id normalization failed goal_id=%s step_id=%s reason=%s",
            goal_id,
            step_id,
            reason,
        )
        if reason == "INVALID_PLAN_STEP_ID":
            return api_error("PLAN_STEP_ID_INVALID", "Plan step id must be an integer", 500)
        if reason == "STEP_ID_STALE":
            logger.info(
                "API: step detail stale goal_id=%s step_id=%s step_index=%s",
                goal_id,
                step_id,
                step_index,
            )
            return api_error(
                "STEP_ID_STALE",
                "Step id is stale; refresh and try again.",
                409,
                extra={"goal_id": goal_id, "step_id": step_id, "step_index": step_index},
            )
        return api_error("STEP_DETAIL_ID_INVALID", "Step detail id normalization failed", 500)
    except Exception as e:
        logger.error(f"API: Failed to update step detail: {e}", exc_info=True)
        return api_error(
            "STEP_DETAIL_UPDATE_FAILED",
            "Failed to update step detail",
            500,
            details=type(e).__name__,
            extra={"goal_id": goal_id, "step_id": step_id},
        )


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
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    othello_engine = comps["othello_engine"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    if _PHASE1_ENABLED:
        return api_error(
            "PHASE1_WRITE_BLOCKED",
            "Phase-1 blocks legacy /api goal planning; use /v1 analyze + confirm",
            409,
        )
    data = request.get_json() or {}
    instruction = data.get("instruction", "").strip()
    
    if not instruction:
        instruction = "Create a detailed step-by-step plan for achieving this goal."
    
    try:
        # Get the goal
        goal = architect_agent.goal_mgr.get_goal(user_id, goal_id)
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found for planning")
            return api_error(
                "GOAL_NOT_FOUND",
                "Goal not found",
                404,
                extra={"goal_id": goal_id},
            )
        
        # Set as active goal
        architect_agent.goal_mgr.set_active_goal(user_id, goal_id)
        
        # Build goal context
        goal_context = architect_agent.goal_mgr.build_goal_context(user_id, goal_id, max_notes=10)
        
        logger.info(f"API: Triggering planning for goal #{goal_id}: {goal.get('text', '')[:50]}...")
        
        # Call architect in planning mode
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
        
            context = {
                "goal_context": goal_context,
                "active_goal": goal
            }
        
            agentic_reply, agent_status = loop.run_until_complete(
                asyncio.wait_for(
                    architect_agent.plan_and_execute(
                        instruction,
                        context=context,
                        user_id=user_id,
                    ),
                    timeout=30.0
                )
            )
        finally:
            loop.close()
        
        # Get updated goal with plan
        updated_goal = architect_agent.goal_mgr.get_goal_with_plan(user_id, goal_id)
        
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
        return api_error(
            "GOAL_PLAN_FAILED",
            "Failed to trigger goal planning",
            500,
            details=type(e).__name__,
            extra={"goal_id": goal_id},
        )


def _ensure_today_plan_id(user_id: str) -> Optional[int]:
    logger = logging.getLogger("API.Insights")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    plan_repository = comps["plan_repository"]
    local_today = _get_local_today(user_id)

    def _fetch_plan_row() -> Optional[Dict[str, Any]]:
        return plan_repository.get_plan_by_date(user_id, local_today)

    # Try existing row
    today_row = _fetch_plan_row()
    if not today_row:
        # Generate (or rebuild) and persist a plan row for today
        try:
            othello_engine.day_planner.get_today_plan(user_id, force_regen=True, plan_date=local_today)
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
    logger.debug("API: ensure today plan id resolved %s", {"plan_id": plan_id, "user": user_id})
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


def _append_goal_task_to_plan(user_id: str, plan_item: dict) -> bool:
    """Append a goal_task into today's plan sections and persist.

    Returns True if appended, False if skipped (e.g., duplicate).
    """
    logger = logging.getLogger("API.Insights")
    local_today = _get_local_today(user_id)
    try:
        plan = othello_engine.day_planner.get_today_plan(
            user_id,
            force_regen=False,
            plan_date=local_today,
        )
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
        othello_engine.day_planner._persist_plan(user_id, local_today, plan)  # type: ignore[attr-defined]
    except Exception as exc:
        logger.warning("API: failed to persist plan after appending insight task: %s", exc, exc_info=True)
        return False

    try:
        meta = plan_item.get("metadata") or {}
        label = meta.get("label") or plan_item.get("label") or item_id
        goal_task_history_repository.upsert_goal_task(
            user_id=str(user_id),
            plan_date=local_today,
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


def _apply_plan_insight(user_id: str, insight: dict) -> int:
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
        if _append_goal_task_to_plan(user_id, item):
            created += 1
    return created


def _apply_simple_plan_item_from_insight(user_id: str, insight: dict) -> int:
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
    if _append_goal_task_to_plan(user_id, item):
        logger.info("API: appended simple plan item from insight id=%s label='%s'", insight.get("id"), labels[0])
        return 1
    return 0


def _apply_goal_insight(user_id: str, insight: dict) -> Dict[str, Any]:
    payload = insight.get("payload") or {}
    items = payload.get("items") or []
    title = payload.get("title") or (items[0] if items else insight.get("summary"))
    if not title:
        raise ValueError("Goal insight missing title")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    return architect_agent.goal_mgr.add_goal(user_id, title)


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
    comps = get_agent_components()
    insights_repository = comps["insights_repository"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    try:
        counts = insights_repository.count_pending_by_type(user_id)
        logger.info("API: insights summary pending_counts=%s", counts)
        return jsonify({"pending_counts": counts})
    except Exception as exc:
        logger.warning("API: insights summary failed: %s", exc, exc_info=True)
        return api_error(
            "INSIGHTS_SUMMARY_FAILED",
            "Insights summary unavailable",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/insights/list", methods=["GET"])
@require_auth
def insights_list():
    logger = logging.getLogger("API.Insights")
    comps = get_agent_components()
    insights_repository = comps["insights_repository"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    status = (request.args.get("status") or "pending").strip().lower()

    logger.info("API: /api/insights/list status=%s", status or "any")

    try:
        insights = insights_repository.list_insights(
            user_id=user_id,
            status=status,
        )
        items = [serialize_insight(i) for i in insights]
        logger.info("API: /api/insights/list returning %s insights", len(items))
        return jsonify({"insights": items})
    except Exception as exc:
        logger.warning("API: insights list failed: %s", exc, exc_info=True)
        return api_error(
            "INSIGHTS_LIST_FAILED",
            "Insights list unavailable",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/insights/apply", methods=["POST"])
@require_auth
def insights_apply():
    comps = get_agent_components()
    insights_repository = comps["insights_repository"]
    othello_engine = comps.get("othello_engine")
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return api_error("VALIDATION_ERROR", "id is required", 400)
    insight = insights_repository.get_insight_by_id(user_id, insight_id)
    if not insight:
        return api_error("INSIGHT_NOT_FOUND", "Insight not found", 404)

    try:
        created_count = 0
        if insight.get("type") == "plan":
            created_count += _apply_plan_insight(user_id, insight)
        elif insight.get("type") == "goal":
            created_goal = _apply_goal_insight(user_id, insight)
            if not created_goal:
                return api_error(
                    "GOAL_CREATE_FAILED",
                    "Failed to create goal",
                    500,
                )
            created_count += _apply_simple_plan_item_from_insight(user_id, insight)
        elif insight.get("type") == "routine":
            _apply_routine_insight(insight)
            created_count += _apply_simple_plan_item_from_insight(user_id, insight)
        else:
            _apply_idea_insight(insight)
            created_count += _apply_simple_plan_item_from_insight(user_id, insight)

        try:
            updated = insights_repository.update_insight_status(
                insight_id, "applied", user_id=user_id
            )
            if not updated:
                return api_error(
                    "INSIGHT_STATUS_UPDATE_FAILED",
                    "Failed to update insight status",
                    500,
                )
        except Exception as exc:
            logging.getLogger("API.Insights").warning(
                "API: failed to update insight status for id=%s: %s", insight_id, exc
            )
            return api_error(
                "INSIGHT_STATUS_UPDATE_FAILED",
                "Failed to update insight status",
                500,
                details=type(exc).__name__,
            )

        counts = {}
        try:
            counts = insights_repository.count_pending_by_type(user_id)
        except Exception as exc:
            logging.getLogger("API.Insights").warning("API: failed to refresh pending counts after apply: %s", exc)

        return jsonify({
            "ok": True,
            "applied_count": created_count,
            "insights_meta": {"pending_counts": counts},
        })
    except ValueError as exc:
        logging.getLogger("API").warning(
            "API: invalid goal insight id=%s error=%s", insight_id, exc
        )
        return api_error(
            "INSIGHT_INVALID",
            "Goal insight missing title",
            400,
            details=str(exc),
        )
    except Exception as exc:
        logging.getLogger("API").error(f"API: failed to apply insight {insight_id}: {exc}", exc_info=True)
        return api_error(
            "INSIGHT_APPLY_FAILED",
            "Failed to apply insight",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/goal-tasks/history", methods=["GET"])
@require_auth
def goal_task_history():
    logger = logging.getLogger("API.GoalTasks")
    comps = get_agent_components()
    goal_task_history_repository = comps["goal_task_history_repository"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
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
            user_id,
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
        return api_error(
            "GOAL_TASK_HISTORY_FAILED",
            "History unavailable",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/insights/dismiss", methods=["POST"])
@require_auth
def insights_dismiss():
    comps = get_agent_components()
    insights_repository = comps["insights_repository"]
    user_id, error = _get_user_id_or_error()
    if error:
        return error
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return api_error("VALIDATION_ERROR", "id is required", 400)
    insight = insights_repository.get_insight_by_id(user_id, insight_id)
    if not insight:
        return api_error("INSIGHT_NOT_FOUND", "Insight not found", 404)

    try:
        insights_repository.update_insight_status(insight_id, "dismissed", user_id=user_id)
        counts = insights_repository.count_pending_by_type(user_id)
        return jsonify({"ok": True, "insights_meta": {"pending_counts": counts}})
    except Exception as exc:
        return api_error(
            "INSIGHT_DISMISS_FAILED",
            "Failed to dismiss insight",
            500,
            details=type(exc).__name__,
        )


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
            return api_error(
                "DB_HEALTH_FAILED",
                "Database health check failed",
                500,
                details="unexpected_result",
                extra={"status": "error"},
            )
            
    except Exception as e:
        return api_error(
            "DB_HEALTH_FAILED",
            "Database connection failed",
            503,
            details=type(e).__name__,
            extra={"status": "error"},
        )


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
