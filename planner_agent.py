import copy
import json
import logging
import re
from typing import Any, Dict, Optional, Tuple


_FILLER_RE = re.compile(r"\b(uh|um|like|please|kind of|sort of|you know)\b", re.IGNORECASE)


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    lowered = text.lower()
    lowered = _FILLER_RE.sub(" ", lowered)
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def determine_build_kind(text: str) -> Optional[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return None

    patterns = [
        ("plan", [r"\bproject\s+plan\b", r"\bplan\b", r"\bplanning\b"]),
        ("goal", [r"\bgoal\b", r"\btarget\b", r"\baim\b"]),
        ("routine", [r"\broutine\b", r"\bhabit\b", r"\bdaily\b"]),
        ("task", [r"\btask\b", r"\btodo\b", r"\bto\s+do\b"]),
    ]
    for kind, kind_patterns in patterns:
        for pattern in kind_patterns:
            if re.search(pattern, normalized):
                return kind
    return None


def init_build_draft_payload() -> Dict[str, Any]:
    return {
        "build_kind": None,
        "missing_fields": ["build_kind"],
        "next_question": "What are we building: a plan, a goal, a routine, or a task?",
    }


def init_plan_draft_payload() -> Dict[str, Any]:
    return {
        "objective": None,
        "tasks": [],
        "timeline": None,
        "resources": [],
        "checklist": [],
        "missing_fields": ["objective", "tasks", "timeline"],
        "next_question": "What is the objective of the plan?",
    }


def _clean_fragment(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" .")


def _trim_at_keywords(value: str) -> str:
    if not value:
        return value
    splitter = re.compile(
        r"\b(main tasks|tasks are|tasks include|timeline is|deadline is|resources are|checklist)\b",
        re.IGNORECASE,
    )
    parts = splitter.split(value)
    return parts[0].strip() if parts else value


def _split_tasks(value: str) -> list[str]:
    if not value:
        return []
    cleaned = value.strip()
    cleaned = re.sub(r"\band then\b", ",", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\band\b", ",", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    parts = [p.strip(" .") for p in cleaned.split(",")]
    return [p for p in parts if p]


def _dedupe_tasks(tasks: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for task in tasks:
        key = task.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(task)
    return deduped


def _coerce_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {}
    return {}


def recompute_plan_missing_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _coerce_payload(payload)
    missing = []

    objective = data.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        missing.append("objective")

    tasks_value = data.get("tasks")
    tasks_list = tasks_value if isinstance(tasks_value, list) else []
    cleaned_tasks = [str(task).strip() for task in tasks_list if str(task).strip()]
    if cleaned_tasks:
        data["tasks"] = cleaned_tasks
    else:
        missing.append("tasks")

    timeline = data.get("timeline")
    if not isinstance(timeline, str) or not timeline.strip():
        missing.append("timeline")

    data["missing_fields"] = missing

    if missing:
        prompt_map = {
            "objective": "What is the objective of the plan?",
            "tasks": "What are the tasks?",
            "timeline": "What is the timeline?",
        }
        data["next_question"] = prompt_map.get(
            missing[0], "What is the objective of the plan?"
        )
    else:
        data["next_question"] = (
            "If that looks right, say 'confirm plan'. "
            "Or tell me what to change (add/remove tasks, change timeline, tweak objective)."
        )

    return data


def patch_plan_draft_payload_deterministic(
    text: str, payload: Dict[str, Any]
) -> Tuple[Dict[str, Any], bool]:
    source_payload = _coerce_payload(payload)
    updated_payload = copy.deepcopy(source_payload)
    changed = False

    objective = None
    objective_patterns = [
        r"\bobjective\s+is\s+(?P<value>[^.]+)",
        r"\bgoal\s+is\s+(?P<value>[^.]+)",
        r"\bi want to\s+(?P<value>[^.]+)",
    ]
    for pattern in objective_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            objective = _clean_fragment(_trim_at_keywords(match.group("value")))
            break

    if objective and objective != updated_payload.get("objective"):
        updated_payload["objective"] = objective
        changed = True

    timeline = None
    timeline_patterns = [
        r"\btimeline\s+is\s+(?P<value>[^.]+)",
        r"\bdeadline\s+is\s+(?P<value>[^.]+)",
    ]
    for pattern in timeline_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            timeline = _clean_fragment(_trim_at_keywords(match.group("value")))
            break

    if timeline is None:
        match = re.search(r"\bby\s+(?P<value>[^.]+)", text, flags=re.IGNORECASE)
        if match:
            timeline = f"by {_clean_fragment(_trim_at_keywords(match.group('value')))}"

    if timeline is None:
        match = re.search(r"\bin\s+(?P<value>\d+\s+\w+)", text, flags=re.IGNORECASE)
        if match:
            timeline = f"in {_clean_fragment(match.group('value'))}"

    if timeline is None and re.search(
        r"\b(timeline|deadline|slip|push|extend)\b",
        text,
        flags=re.IGNORECASE,
    ):
        match = re.search(
            r"\b(?:(?:about|around|maybe|approximately)\s+)?(?P<value>(?:\d+|[a-z]+)\s+weeks?)\b",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            timeline = _clean_fragment(match.group("value"))

    if timeline and timeline != updated_payload.get("timeline"):
        updated_payload["timeline"] = timeline
        changed = True

    tasks_text = None
    tasks_patterns = [
        r"\bmain\s+tasks?\s+(?:are|include)\s+(?P<value>[^.]+)",
        r"\btasks?\s+(?:are|include)\s+(?P<value>[^.]+)",
    ]
    for pattern in tasks_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            tasks_text = _trim_at_keywords(match.group("value"))
            break

    add_tasks_text = None
    match = re.search(
        r"\b(?:can\s+you\s+)?add\s+(?:another\s+|a\s+|an\s+|new\s+)?task(?:\s+to)?\s+(?P<value>[^.]+)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        add_tasks_text = _trim_at_keywords(match.group("value"))

    if tasks_text:
        parsed = _split_tasks(tasks_text)
        parsed = _dedupe_tasks(parsed)
        if parsed and parsed != (updated_payload.get("tasks") or []):
            updated_payload["tasks"] = parsed
            changed = True

    if add_tasks_text:
        task = _clean_fragment(add_tasks_text)
        task = task.strip(" .!?")
        existing = updated_payload.get("tasks")
        existing = existing if isinstance(existing, list) else []
        merged = _dedupe_tasks(existing + ([task] if task else []))
        if merged != existing:
            updated_payload["tasks"] = merged
            changed = True

    updated_payload = recompute_plan_missing_fields(updated_payload)
    return updated_payload, changed


def patch_plan_draft_payload_llm(
    text: str,
    payload: Dict[str, Any],
    llm=None,
) -> Dict[str, Any]:
    from core.llm_wrapper import LLMWrapper

    system_prompt = (
        "You are a plan editing engine. Update the existing plan draft JSON based on the user's instruction (STT).\n"
        "Return the FULL updated JSON object with keys: objective, tasks, timeline, notes.\n"
        " - objective: The main goal/focus of the plan (string).\n"
        " - tasks: A list of task strings.\n"
        " - timeline: When to do it (string or null).\n"
        " - notes: Any extra details (string or null).\n"
        "Do not lose existing information unless instructed to change it.\n"
        "Return ONLY valid JSON."
    )

    try:
        llm = llm or LLMWrapper()
        response = llm.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Current Payload: {json.dumps(payload)}\nInstruction: {text}"},
            ],
            temperature=0.1,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        updated_payload = json.loads(content)
        return recompute_plan_missing_fields(updated_payload)
    except Exception as exc:
        logging.error("Failed to patch plan draft payload: %s", exc)
        return recompute_plan_missing_fields(payload)


def _stringify_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items = []
    for entry in value:
        text = str(entry).strip()
        if text:
            items.append(text)
    return items


def _format_missing_line(payload: Dict[str, Any]) -> Optional[str]:
    missing = payload.get("missing_fields") or []
    if isinstance(missing, str):
        missing = [missing]
    if not isinstance(missing, list):
        return None
    cleaned = [str(item).strip() for item in missing if str(item).strip()]
    if not cleaned:
        return None
    return f"**Missing:** {', '.join(cleaned)}"


def _format_next_line(payload: Dict[str, Any]) -> Optional[str]:
    next_question = payload.get("next_question")
    if next_question:
        return f"**Next:** {str(next_question).strip()}"
    return None


def format_build_mode_reply(draft_payload: Dict[str, Any]) -> str:
    payload = _coerce_payload(draft_payload)
    next_question = payload.get("next_question") or "What are we building: a plan, a goal, a routine, or a task?"
    lines = ["**Build Mode**", str(next_question).strip()]
    missing_line = _format_missing_line(payload)
    if missing_line:
        lines.append(missing_line)
    return "\n\n".join(lines)


def format_plan_draft_reply(draft_payload: Dict[str, Any]) -> str:
    payload = _coerce_payload(draft_payload)
    objective = payload.get("objective") or "(missing)"
    timeline = payload.get("timeline") or "(missing)"
    tasks = _stringify_list(payload.get("tasks"))

    lines = [
        "**Plan Draft**",
        "",
        f"**Objective:** {objective}",
        f"**Timeline:** {timeline}",
        "**Tasks:**",
    ]
    if tasks:
        for task in tasks:
            lines.append(f"- {task}")
    else:
        lines.append("(missing)")

    missing_line = _format_missing_line(payload)
    if missing_line:
        lines.append(missing_line)

    next_line = _format_next_line(payload)
    if next_line:
        lines.append(next_line)

    return "\n".join(lines)


def format_goal_draft_reply(draft_payload: Dict[str, Any]) -> str:
    payload = _coerce_payload(draft_payload)
    title = payload.get("title") or "(missing)"
    steps = _stringify_list(payload.get("steps"))
    if not steps:
        steps = _stringify_list(payload.get("objectives"))

    lines = [
        "**Goal Draft**",
        "",
        f"**Title:** {title}",
        "**Steps:**",
    ]
    if steps:
        lines.append(f"{len(steps)} total")
        for step in steps[:3]:
            lines.append(f"- {step}")
    else:
        lines.append("(missing)")

    missing_line = _format_missing_line(payload)
    if missing_line:
        lines.append(missing_line)

    next_line = _format_next_line(payload)
    if next_line:
        lines.append(next_line)

    return "\n".join(lines)
