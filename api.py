import logging
import os
import re
from datetime import date, timedelta
from flask import Flask, request, jsonify, send_file, session, send_from_directory, g
from flask_cors import CORS
import asyncio
from typing import Any, Dict, Optional
from functools import wraps
from passlib.hash import bcrypt
import mimetypes
from utils.llm_config import is_openai_configured, get_openai_api_key
import openai
import httpx
import uuid
from werkzeug.exceptions import HTTPException

# NOTE: Keep import-time work minimal! Do not import LLM/agent modules or connect to DB at module scope unless required for health endpoints.
from dotenv import load_dotenv

# Preserve any runtime-provided OPENAI_API_KEY (e.g., Render env var) when loading local .env for dev.
_preexisting_openai_key = os.environ.get("OPENAI_API_KEY")
load_dotenv(override=False)
if _preexisting_openai_key and _preexisting_openai_key.strip():
    os.environ["OPENAI_API_KEY"] = _preexisting_openai_key

# Configure logging to show DEBUG messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
MAX_ERROR_MSG_LENGTH = 200  # Maximum length for error message logging
REQUEST_ID_HEADER = "X-Request-ID"


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
def handle_llm_error(e: Exception, logger: logging.Logger) -> tuple[dict, int]:
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
    
    # Authentication errors
    if isinstance(e, openai.AuthenticationError):
        return {
            "error_code": "LLM_AUTH_FAILED",
            "message": "LLM auth failed",
            "details": "Invalid API key or auth failure",
            "request_id": request_id,
        }, 503
    
    # Rate limit errors  
    if isinstance(e, openai.RateLimitError):
        return {
            "error_code": "LLM_RATE_LIMIT",
            "message": "LLM rate limit reached",
            "details": "API rate limit exceeded. Please try again later.",
            "request_id": request_id,
        }, 429
    
    # Connection/timeout errors
    if isinstance(e, (openai.APIConnectionError, openai.APITimeoutError)):
        return {
            "error_code": "LLM_CONNECTION_ERROR",
            "message": "LLM connection error",
            "details": "Could not connect to LLM service",
            "request_id": request_id,
        }, 502
    
    # Other OpenAI API errors
    if isinstance(e, openai.OpenAIError):
        return {
            "error_code": "LLM_UPSTREAM_ERROR",
            "message": "LLM upstream error",
            "details": f"LLM service error: {error_class}",
            "request_id": request_id,
        }, 502
    
    # Generic error for non-OpenAI exceptions
    return {
        "error_code": "LLM_INTERNAL_ERROR",
        "message": "Internal error",
        "details": f"An unexpected error occurred: {error_class}",
        "request_id": request_id,
    }, 500

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
    from db.database import init_pool, ensure_core_schema, fetch_one
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
        DEFAULT_USER_ID = DbGoalManager.DEFAULT_USER_ID

        _agent_components = {
            'architect_agent': architect_agent,
            'othello_engine': othello_engine,
            'DEFAULT_USER_ID': DEFAULT_USER_ID,
            'insights_repository': insights_repository,
            'plan_repository': plan_repository,
            'goal_task_history_repository': goal_task_history_repository,
            'postprocess_and_save': postprocess_and_save,
            'extract_insights_from_exchange': extract_insights_from_exchange,
            'model': model,
        }
        globals().update(
            architect_agent=architect_agent,
            othello_engine=othello_engine,
            DEFAULT_USER_ID=DEFAULT_USER_ID,
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
DEFAULT_USER_ID = "default"
insights_repository = None
plan_repository = None
goal_task_history_repository = None
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



def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow unauthenticated for health, login, me, and root
        if request.path in ["/api/health", "/api/auth/login", "/api/auth/me", "/"]:
            return f(*args, **kwargs)
        if not session.get("authed"):
            return api_error("AUTH_REQUIRED", "Authentication required", 401)
        return f(*args, **kwargs)
    return decorated


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

    pin_hash = _env_trim("OTHELLO_PIN_HASH")
    login_key = _env_trim("OTHELLO_LOGIN_KEY")
    plain_pwd = _env_trim("OTHELLO_PASSWORD")  # legacy fallback
    auth_mode = "pin_hash" if pin_hash else ("login_key" if login_key else ("plaintext_password" if plain_pwd else "none"))

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
                session["authed"] = True
                return jsonify({"ok": True, "auth_mode": auth_mode})
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
            session["authed"] = True
            return jsonify({"ok": True, "auth_mode": auth_mode})
        return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": auth_mode})

    # Legacy plaintext password
    logger.warning("plaintext password mode enabled; set OTHELLO_PIN_HASH or OTHELLO_LOGIN_KEY to harden")
    if password == plain_pwd:
        session["authed"] = True
        return jsonify({"ok": True, "auth_mode": auth_mode})
    return api_error("AUTH_INVALID", "Invalid access code", 401, extra={"auth_mode": auth_mode})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    return jsonify({"authenticated": bool(session.get("authed"))})

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"ok": True})


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
    try:
        comps = get_agent_components()
        counts = comps["insights_repository"].count_pending_by_type(comps["DEFAULT_USER_ID"])
        logger.info("API: startup pending insights summary: %s", counts)
    except Exception as exc:
        logger.warning("API: insights summary unavailable at startup: %s", exc)


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
    request_id = _get_request_id()
    try:
        if not request.is_json:
            return api_error("VALIDATION_ERROR", "JSON body required", 400)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
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
        current_mode = (data.get("current_mode") or "companion").strip().lower()
        current_view = data.get("current_view")

        if not user_input:
            return api_error("VALIDATION_ERROR", "message is required", 400)

        logger.info("API: Received message: %s request_id=%s", user_input[:100], request_id)

        try:
            comps = get_agent_components()
            architect_agent = comps["architect_agent"]
            othello_engine = comps["othello_engine"]
            DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
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
            return api_error("LLM_INIT_FAILED", "LLM unavailable", 503, details=detail)

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
        try:
            requested_goal = architect_agent.goal_mgr.get_goal(requested_goal_id)
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
        
        goals = architect_agent.goal_mgr.list_goals() or []
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
    active_goal = requested_goal
    if active_goal is None:
        try:
            active_goal = architect_agent.goal_mgr.get_active_goal()
        except Exception as exc:
            logger.error("API: Failed to load active goal: %s", exc, exc_info=True)
            active_goal = None
    
    # Fallback: if no active goal but exactly one goal exists, use it as default
    if active_goal is None:
        try:
            goals = architect_agent.goal_mgr.list_goals() or []
        except Exception as exc:
            logger.error("API: Failed to list goals for fallback: %s", exc, exc_info=True)
            goals = []
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
    if isinstance(active_goal, dict) and active_goal.get("id") is not None:
        goal_context = architect_agent.goal_mgr.build_goal_context(
            active_goal["id"], max_notes=8
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
                
                # Check if it's an OpenAI error - return structured error
                if isinstance(e, openai.OpenAIError):
                    error_response, status_code = handle_llm_error(e, logger)
                    return jsonify(error_response), status_code
                
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
                
                # Check if it's an OpenAI error - return structured error
                if isinstance(e, openai.OpenAIError):
                    error_response, status_code = handle_llm_error(e, logger)
                    return jsonify(error_response), status_code
                
                # Otherwise provide generic error message in response
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

        if not isinstance(agent_status, dict):
            agent_status = {}

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
            "agent_status": agent_status,
            "request_id": request_id,
        }
        try:
            logger.info("API: running insight extraction for message (goal mode)")
            response["insights_meta"] = _normalize_insights_meta(
                _process_insights_pipeline(
                    user_text=raw_user_input,
                    assistant_text=agentic_reply,
                    user_id=DEFAULT_USER_ID,
                )
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
            
            # Check if it's an OpenAI error - return structured error
            if isinstance(e, openai.OpenAIError):
                error_response, status_code = handle_llm_error(e, logger)
                return jsonify(error_response), status_code
            
            # Otherwise provide generic error message in response
            agentic_reply = "I'm having trouble processing that right now. Could you try again?"
            agent_status = {"planner_active": False, "had_goal_update_xml": False}

        if not isinstance(agent_status, dict):
            agent_status = {}

        response = {
            "reply": agentic_reply,
            "agent_status": agent_status,
            "request_id": request_id,
        }
        try:
            logger.info("API: running insight extraction for message (casual mode)")
            response["insights_meta"] = _normalize_insights_meta(
                _process_insights_pipeline(
                    user_text=raw_user_input,
                    assistant_text=agentic_reply,
                    user_id=DEFAULT_USER_ID,
                )
            )
            logger.info(
                "API: insight extraction completed (created=%s)",
                response["insights_meta"].get("created", "?"),
            )
        except Exception as exc:
            logger.warning("API: insight extraction skipped due to error: %s", exc, exc_info=True)
        return jsonify(response)

    except Exception as exc:
        logger.exception(
            "API: handle_message failed request_id=%s error_type=%s",
            request_id,
            type(exc).__name__,
        )
        return api_error("INTERNAL_ERROR", "Internal server error", 500)


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
        return api_error(
            "TODAY_BRIEF_FAILED",
            "Failed to build today brief",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/plan/update", methods=["POST"])
@require_auth
def update_plan_item():
    """Update lifecycle status for a plan item (complete/skip/reschedule)."""
    logger = logging.getLogger("API")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    data = request.get_json() or {}
    item_id = data.get("item_id")
    status = data.get("status")
    plan_date = data.get("plan_date")
    reason = data.get("reason")
    reschedule_to = data.get("reschedule_to")

    if not item_id or not status:
        return api_error("VALIDATION_ERROR", "item_id and status are required", 400)

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
    data = request.get_json() or {}
    mood_context = data.get("mood_context") or data
    try:
        plan = othello_engine.rebuild_today_plan(mood_context=mood_context)
        logger.info("API: Rebuilt today plan on demand")
        return jsonify({"plan": plan})
    except Exception as exc:
        logger.error(f"API: Failed to rebuild plan: {exc}", exc_info=True)
        return api_error(
            "PLAN_REBUILD_FAILED",
            "Failed to rebuild plan",
            500,
            details=type(exc).__name__,
        )


@app.route("/api/goals", methods=["GET"])
@require_auth
def get_goals():
    """
    Simple read-only endpoint so the UI can see what goals
    the Architect/GoalManager have captured so far.
    """
    logger = logging.getLogger("API")
    comps = get_agent_components()
    architect_agent = comps["architect_agent"]
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    logger.debug(
        "API: get_goals session_user=%s authed=%s",
        session.get("user_id"),
        bool(session.get("authed")),
    )
    try:
        goals = architect_agent.goal_mgr.list_goals()
        return jsonify({"goals": goals})
    except Exception as e:
        logging.getLogger("ARCHITECT").error(f"Failed to fetch goals: {e}")
        return api_error(
            "GOALS_FETCH_FAILED",
            "Failed to fetch goals",
            500,
            details=type(e).__name__,
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
    try:
        goal = architect_agent.goal_mgr.get_goal_with_plan(goal_id)
        
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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    request_id = _get_request_id()

    try:
        goal = architect_agent.goal_mgr.get_goal(goal_id)
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
        archived_goal = architect_agent.goal_mgr.archive_goal(goal_id)
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
        result = safe_append_goal_event(DEFAULT_USER_ID, goal_id, None, "goal_archived", payload)
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
            goal_id, step_id, new_status
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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    data = request.get_json() or {}
    instruction = data.get("instruction", "").strip()
    
    if not instruction:
        instruction = "Create a detailed step-by-step plan for achieving this goal."
    
    try:
        # Get the goal
        goal = architect_agent.goal_mgr.get_goal(goal_id)
        if goal is None:
            logger.warning(f"API: Goal #{goal_id} not found for planning")
            return api_error(
                "GOAL_NOT_FOUND",
                "Goal not found",
                404,
                extra={"goal_id": goal_id},
            )
        
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
        return api_error(
            "GOAL_PLAN_FAILED",
            "Failed to trigger goal planning",
            500,
            details=type(e).__name__,
            extra={"goal_id": goal_id},
        )


def _ensure_today_plan_id() -> Optional[int]:
    logger = logging.getLogger("API.Insights")
    comps = get_agent_components()
    othello_engine = comps["othello_engine"]
    plan_repository = comps["plan_repository"]
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
    comps = get_agent_components()
    insights_repository = comps["insights_repository"]
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    try:
        counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return api_error("VALIDATION_ERROR", "id is required", 400)
    insight = insights_repository.get_insight_by_id(DEFAULT_USER_ID, insight_id)
    if not insight:
        return api_error("INSIGHT_NOT_FOUND", "Insight not found", 404)

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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
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
    DEFAULT_USER_ID = comps["DEFAULT_USER_ID"]
    data = request.get_json() or {}
    insight_id = data.get("id")
    if not insight_id:
        return api_error("VALIDATION_ERROR", "id is required", 400)
    insight = insights_repository.get_insight_by_id(DEFAULT_USER_ID, insight_id)
    if not insight:
        return api_error("INSIGHT_NOT_FOUND", "Insight not found", 404)

    try:
        insights_repository.update_insight_status(insight_id, "dismissed", user_id=DEFAULT_USER_ID)
        counts = insights_repository.count_pending_by_type(DEFAULT_USER_ID)
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
