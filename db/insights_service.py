"""Minimal, formatting-driven insight extraction."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional


def extract_insights_from_exchange(
    *,
    user_text: str,
    assistant_text: Optional[str],
    current_mode: Optional[str] = None,
    source_message_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Extract a single pending insight from bullet/numbered assistant replies."""

    logger = logging.getLogger("Insights")

    assistant = assistant_text or ""
    lines = assistant.splitlines()
    items: List[str] = []

    for raw_line in lines:
        line = (raw_line or "").strip()
        if not line:
            continue

        if line.startswith("-"):
            content = line[1:].lstrip()
        elif line.startswith("*"):
            content = line[1:].lstrip()
        elif line.startswith("•"):
            content = line[1:].lstrip()
        else:
            numbered = re.match(r"^(\d+)\.\s+(.*)$", line)
            content = numbered.group(2).strip() if numbered else None

        if content:
            items.append(content)

    if not items:
        logger.info("Insights: no list-formatted candidates found; skipping")
        return []

    mode = (current_mode or "unknown").strip().lower() or "unknown"
    user_lower = (user_text or "").lower()

    if mode == "today":
        insight_type = "plan"
    elif mode == "routine":
        insight_type = "routine"
    else:
        insight_type = "goal" if ("goal" in user_lower or "goals" in user_lower) else "idea"

    summary = items[0][:120] if len(items[0]) <= 120 else items[0][:117] + "..."

    insight = {
        "type": insight_type,
        "status": "pending",
        "summary": summary,
        "payload": {
            "items": items,
            "raw_assistant": assistant,
            "raw_user": user_text,
        },
        "source_mode": mode,
        "source_message_id": source_message_id,
    }

    logger.info("Insights: emitting %s insight from %s items", insight_type, len(items))
    return [insight]
