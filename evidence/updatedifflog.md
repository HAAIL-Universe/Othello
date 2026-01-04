Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Deploy + runtime verification; mark COMPLETE if PASS
Completed: Weekday plan-query intent + static py_compile
Remaining: Runtime verification on deployed env + any hotfix if FAIL
Next Action: Deploy this commit and test 'What's the plan for Monday?' then paste PASS/FAIL + screenshot/console; only then we'll update log to COMPLETE.
Verification:
- Static: python -m py_compile api.py (pass)
- Runtime: Not run (pending deploy)

diff --git a/api.py b/api.py
index 9c9904d0..32f7b08a 100644
--- a/api.py
+++ b/api.py
@@ -802,6 +802,150 @@ def is_today_plan_request(text: str) -> bool:
     return False
 
 
+def _extract_weekday_plan_query(text: Optional[str]) -> Optional[str]:
+    if not text:
+        return None
+    normalized = re.sub(r"\s+", " ", str(text).strip().lower())
+    normalized = normalized.replace("?", "").replace("!", "").replace(".", "")
+    if "routine" in normalized or "habit" in normalized:
+        return None
+    plan_cues = (
+        "plan",
+        "schedule",
+        "agenda",
+        "what am i doing",
+        "what's on",
+        "whats on",
+        "what is on",
+        "what's my plan",
+        "what is my plan",
+    )
+    if not any(cue in normalized for cue in plan_cues):
+        return None
+    match = re.search(
+        r"\b(mon(day)?|tue(sday)?|wed(nesday)?|thu(rsday)?|fri(day)?|sat(urday)?|sun(day)?)\b",
+        normalized,
+    )
+    if not match:
+        return None
+    token = match.group(1).lower()
+    weekday_map = {
+        "mon": "mon",
+        "monday": "mon",
+        "tue": "tue",
+        "tues": "tue",
+        "tuesday": "tue",
+        "wed": "wed",
+        "weds": "wed",
+        "wednesday": "wed",
+        "thu": "thu",
+        "thur": "thu",
+        "thurs": "thu",
+        "thursday": "thu",
+        "fri": "fri",
+        "friday": "fri",
+        "sat": "sat",
+        "saturday": "sat",
+        "sun": "sun",
+        "sunday": "sun",
+    }
+    return weekday_map.get(token)
+
+
+def _resolve_weekday_to_ymd(
+    *,
+    weekday_key: str,
+    timezone_name: Optional[str],
+    logger: logging.Logger,
+) -> str:
+    weekday_indexes = {
+        "mon": 0,
+        "tue": 1,
+        "wed": 2,
+        "thu": 3,
+        "fri": 4,
+        "sat": 5,
+        "sun": 6,
+    }
+    target_idx = weekday_indexes.get(weekday_key)
+    if target_idx is None:
+        return datetime.now(timezone.utc).date().isoformat()
+    resolved_timezone = _normalize_timezone(timezone_name, logger)
+    local_today = datetime.now(ZoneInfo(resolved_timezone)).date()
+    days_ahead = (target_idx - local_today.weekday()) % 7
+    target_date = local_today + timedelta(days=days_ahead)
+    return target_date.isoformat()
+
+
+def _weekday_label(weekday_key: str) -> str:
+    labels = {
+        "mon": "Monday",
+        "tue": "Tuesday",
+        "wed": "Wednesday",
+        "thu": "Thursday",
+        "fri": "Friday",
+        "sat": "Saturday",
+        "sun": "Sunday",
+    }
+    return labels.get(weekday_key, weekday_key.title())
+
+
+def _load_plan_for_date_peek(
+    *,
+    user_id: str,
+    plan_date: date,
+    comps: Dict[str, Any],
+) -> Dict[str, Any]:
+    plan_repo = comps["plan_repository"]
+    plan_row = plan_repo.get_plan_by_date(user_id, plan_date)
+    if not plan_row:
+        return {
+            "date": plan_date.isoformat(),
+            "sections": {"routines": [], "goal_tasks": [], "optional": []},
+            "_plan_source": "empty_stub",
+        }
+    items = plan_repo.get_plan_items(plan_row["id"])
+    sections = {"routines": [], "goal_tasks": [], "optional": []}
+    for item in items:
+        kind = item.get("type")
+        source_kind = item.get("source_kind")
+        if kind in ("routine", "routine_step") or source_kind == "routine":
+            sections["routines"].append(item)
+        elif kind == "goal_task" or source_kind == "goal_task":
+            sections["goal_tasks"].append(item)
+        else:
+            sections["optional"].append(item)
+    return {
+        "date": plan_date.isoformat(),
+        "sections": sections,
+        "_plan_source": "peek",
+    }
+
+
+def _format_day_plan_reply(plan: Dict[str, Any], plan_date: date, weekday_label: str) -> str:
+    sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
+    items: List[str] = []
+    for section_key in ("routines", "goal_tasks", "optional"):
+        for item in sections.get(section_key, []) or []:
+            label = (
+                item.get("label")
+                or item.get("name")
+                or item.get("title")
+                or (item.get("metadata") or {}).get("label")
+            )
+            if label:
+                items.append(str(label))
+    if not items:
+        return f"No plan items for {weekday_label} yet."
+    headline = f"Plan for {weekday_label} ({plan_date.isoformat()}):"
+    lines = [headline]
+    for label in items[:6]:
+        lines.append(f"- {label}")
+    if len(items) > 6:
+        lines.append(f"...and {len(items) - 6} more.")
+    return "\n".join(lines)
+
+
 def _format_today_plan_reply(plan: Dict[str, Any], brief: Optional[Dict[str, Any]], plan_date: date) -> str:
     sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
     items: List[str] = []
@@ -1044,6 +1188,8 @@ def _get_goal_intent_suggestion(
 ) -> Optional[Dict[str, Any]]:
     if _has_schedule_cues(user_input):
         return None
+    if _extract_weekday_plan_query(user_input):
+        return None
     suggestion = _detect_goal_intent_suggestion(user_input, client_message_id)
     if not suggestion:
         return None
@@ -4445,6 +4591,64 @@ def handle_message():
                     return _respond(response)
 
 
+        if user_id and is_chat_view:
+            weekday_key = _extract_weekday_plan_query(user_input)
+            if weekday_key:
+                try:
+                    from db.plan_repository import get_user_timezone
+
+                    timezone_name = get_user_timezone(user_id)
+                    ymd = _resolve_weekday_to_ymd(
+                        weekday_key=weekday_key,
+                        timezone_name=timezone_name,
+                        logger=logger,
+                    )
+                    plan_date = date.fromisoformat(ymd)
+                    comps = get_agent_components()
+                    plan = _load_plan_for_date_peek(
+                        user_id=user_id,
+                        plan_date=plan_date,
+                        comps=comps,
+                    )
+                    sections = plan.get("sections", {}) if isinstance(plan, dict) else {}
+                    item_count = sum(
+                        len(sections.get(key, []) or [])
+                        for key in ("routines", "goal_tasks", "optional")
+                    )
+                    response = {
+                        "reply": _format_day_plan_reply(
+                            plan,
+                            plan_date,
+                            _weekday_label(weekday_key),
+                        ),
+                        "agent_status": {"planner_active": False},
+                        "request_id": request_id,
+                        "meta": {
+                            "intent": "day_plan_query",
+                            "ymd": plan_date.isoformat(),
+                            "weekday": weekday_key,
+                            "item_count": item_count,
+                        },
+                    }
+                    return _respond(response)
+                except Exception as exc:
+                    logger.error(
+                        "API: weekday plan query failed request_id=%s error=%s",
+                        request_id,
+                        type(exc).__name__,
+                        exc_info=True,
+                    )
+                    response = {
+                        "reply": (
+                            f"I couldn't load the plan for {_weekday_label(weekday_key)} right now. "
+                            "Please try again in a moment."
+                        ),
+                        "agent_status": {"planner_active": False},
+                        "request_id": request_id,
+                        "meta": {"intent": "day_plan_query_failed", "weekday": weekday_key},
+                    }
+                    return _respond(response)
+
         if user_id and is_chat_view and is_today_plan_request(user_input):
             try:
                 local_today = _get_local_today(user_id)

