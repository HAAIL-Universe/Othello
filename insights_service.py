"""Lightweight extraction of conversational insights.

This module stays independent from Flask and database layers.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List

from db import insights_repository


_LIST_PATTERN = re.compile(r"^(?:[-*\u2022]\s+|\d+[\.\)]\s+)(.+)$")


def _extract_list_lines(text: str) -> List[str]:
    lines: List[str] = []
    for raw in (text or "").splitlines():
        candidate = raw.strip()
        match = _LIST_PATTERN.match(candidate)
        if match:
            item = match.group(1).strip()
            if item:
                lines.append(item)
    return lines


def _infer_type(user_text: str) -> str:
    text = (user_text or "").lower()
    if any(keyword in text for keyword in ("goal", "goals", "plan", "planning")):
        return "goal"
    return "generic"


def extract_insights_from_exchange(
    user_message: str,
    assistant_message: str,
    user_id: str,
) -> List[Dict[str, object]]:
    """Persist simple bullet-style insights from a chat exchange.

    Extracts bullet/numbered lines from the assistant reply and stores each as a
    pending insight. Failures are logged but never raised.
    """

    logger = logging.getLogger("InsightsExtractor")
    created: List[Dict[str, object]] = []

    preview_user = (user_message or "")[:120]
    preview_assistant = (assistant_message or "")[:120]
    logger.info(
        "Insights: start extraction user='%s' assistant_preview='%s' len=%s",
        preview_user,
        preview_assistant,
        len(assistant_message or ""),
    )

    items = _extract_list_lines(assistant_message)
    if not items:
        logger.info("Insights: no bullet/numbered lines detected in assistant reply")
        return []

    insight_type = _infer_type(user_message)

    for line in items:
        try:
            insight = insights_repository.create_insight(
                user_id=user_id,
                insight_type=insight_type,
                summary=line,
                status="pending",
            )
            if insight:
                created.append(insight)
                logger.info(
                    "Insights: created insight id=%s, type=%s",
                    insight.get("id"),
                    insight.get("type"),
                )
        except Exception:
            logger.warning("insights: failed to persist candidate", exc_info=True)

    logger.info(
        "insights: persisted %s insight candidate(s) type=%s",
        len(created),
        insight_type,
    )
    return created
