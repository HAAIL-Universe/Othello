Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Locate generic questions prompt + context sources; add LLM-backed question generator with repetition guard; wire into questions flow; update evidence log; run static compile
Completed: Added goal-text extraction helper; added LLM-backed goal intake questions with fallback + repetition guard; wired context_prompt and steps_choice to dynamic questions; added ask-questions detection; ran py_compile
Remaining: Runtime verification pending deploy (tailored questions + context request)
Next Action: Deploy and run runtime checklist; report PASS/FAIL + sample outputs.

Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; api.py
Anchors:
- _find_goal_text_in_context: api.py:1340
- _format_goal_questions_reply: api.py:1393
- _generate_goal_intake_questions: api.py:1410
- questions_prompt/context_prompt detection: api.py:4600
- steps_choice ask-questions handling: api.py:4738
- dynamic question reply: api.py:4758
Verification:
- Static: python -m py_compile api.py (PASS)
- Runtime: PENDING (deploy-required)
  1) Concrete goal -> "Ask me the relevant questions" returns tailored questions.
  2) Vague goal -> one-line context request, then tailored questions after reply.
diff --git a/api.py b/api.py
index 21b2eceb..b1eaae0e 100644
--- a/api.py
+++ b/api.py
@@ -1337,6 +1337,182 @@ def _llm_unavailable_prompt(active_goal_id: Optional[int]) -> str:
         + _goal_intent_prompt(active_goal_id)
     )
 
+def _find_goal_text_in_context(companion_context: List[Dict[str, Any]]) -> Optional[str]:
+    if not companion_context:
+        return None
+    goal_text = None
+    for msg in reversed(companion_context):
+        if msg.get("role") != "assistant":
+            continue
+        content = (msg.get("content") or "").strip()
+        if not content:
+            continue
+        match = re.search(r"goal:\s*(.+)", content, flags=re.IGNORECASE)
+        if match:
+            candidate = match.group(1).strip()
+            if candidate:
+                goal_text = candidate
+                break
+    fallback_text = None
+    if not goal_text:
+        for msg in reversed(companion_context):
+            if msg.get("role") != "user":
+                continue
+            text = (msg.get("content") or "").strip()
+            if not text:
+                continue
+            norm = re.sub(r"\s+", " ", text.lower()).strip()
+            if re.match(r"^(hi|hey|hello)\b", norm) and not re.search(
+                r"\b(goal|want|build|start|today)\b",
+                norm,
+            ):
+                continue
+            if re.search(r"\bstep(s)?\b", norm) or "break" in norm:
+                continue
+            if "save" in norm:
+                continue
+            goal_language = re.search(r"\bgoal(s)?\b", norm) is not None
+            goal_like = False
+            if norm.startswith(("i want to", "my goal is", "today", "build", "start")):
+                goal_like = True
+            if goal_language and len(norm) > 12:
+                goal_like = True
+            if goal_language and not goal_like:
+                continue
+            if len(text) <= 12:
+                continue
+            if goal_like:
+                goal_text = text
+                break
+            if fallback_text is None:
+                fallback_text = text
+        if not goal_text:
+            goal_text = fallback_text
+    return goal_text
+
+def _format_goal_questions_reply(goal_text: str, questions: Optional[List[str]] = None) -> str:
+    lines = [
+        f"Ok - goal: {goal_text}",
+        "Before I draft steps, a few quick questions:",
+    ]
+    if questions:
+        for idx, q_text in enumerate(questions, start=1):
+            q_text = (q_text or "").strip()
+            if q_text:
+                lines.append(f"{idx}) {q_text}")
+        return "\n".join(lines)
+    lines.extend(["1) What time window or cadence should this fit?",
+                  "2) What does success look like for you?",
+                  "3) Any constraints or must-avoid items?",
+                  "4) What's the hardest part?"])
+    return "\n".join(lines)
+
+def _generate_goal_intake_questions(
+    *,
+    goal_text: Optional[str],
+    goal_title: Optional[str],
+    goal_description: Optional[str],
+    user_message: str,
+    recent_messages: Optional[List[Dict[str, Any]]],
+    user_id: Optional[str],
+    request_id: str,
+    logger: logging.Logger,
+) -> Optional[Dict[str, Any]]:
+    fallback_context = (
+        "Share one line of context about your goal (tools, constraints, or timeline), "
+        "and I'll tailor the questions."
+    )
+    if not (goal_text or goal_title or goal_description):
+        return {"need_more_context": True, "context_request": fallback_context, "questions": []}
+    if not is_openai_configured():
+        return None
+    recent_context = "\n".join(
+        f"{msg.get('role')}: {msg.get('content')}"
+        for msg in (recent_messages or [])[-6:]
+        if msg.get("role") and msg.get("content")
+    )
+    prompt = (
+        "Generate goal-specific intake questions. Return JSON only with "
+        '{"need_more_context":bool,"context_request":string|null,'
+        '"questions":[{"q":string,"why":string,"answer_type":"one_line"|"time_window"|"choice"|"yes_no"|"number"}]}. '
+        "If context is insufficient, set need_more_context=true and provide a single-line context_request. "
+        "Otherwise ask 4-6 questions tied to the goal details and avoid repeating recent questions.\n"
+        f"Goal title: {goal_title or ''}\n"
+        f"Goal description: {goal_description or ''}\n"
+        f"Goal text: {goal_text or ''}\n"
+        f"User request: {user_message or ''}\n"
+        f"Recent context:\n{recent_context}\n"
+    )
+    loop = None
+    try:
+        comps = get_agent_components()
+        architect = comps["architect_agent"]
+        loop = asyncio.new_event_loop()
+        asyncio.set_event_loop(loop)
+        reply_text, _agent_status = loop.run_until_complete(
+            asyncio.wait_for(
+                architect.plan_and_execute(
+                    prompt,
+                    user_id=user_id,
+                    recent_messages=recent_messages,
+                ),
+                timeout=30.0
+            )
+        )
+    except Exception as exc:
+        logger.error(
+            "API: goal intake questions failed request_id=%s",
+            request_id,
+            exc_info=True,
+        )
+        return None
+    finally:
+        if loop is not None:
+            try:
+                loop.close()
+            except Exception:
+                logger.debug("API: event loop close failed but continuing")
+    raw_reply = (reply_text or "").strip()
+    payload = None
+    if raw_reply:
+        try:
+            payload = json.loads(raw_reply)
+        except Exception:
+            start = raw_reply.find("{")
+            end = raw_reply.rfind("}")
+            if start != -1 and end > start:
+                try:
+                    payload = json.loads(raw_reply[start:end + 1])
+                except Exception:
+                    payload = None
+    if not isinstance(payload, dict):
+        return None
+    need_more_context = bool(payload.get("need_more_context"))
+    if need_more_context:
+        context_request = (payload.get("context_request") or "").strip()
+        if not context_request:
+            context_request = fallback_context
+        elif "question" not in context_request.lower():
+            context_request = f"{context_request.rstrip('.')} I'll tailor the questions."
+        return {"need_more_context": True, "context_request": context_request, "questions": []}
+    raw_questions = payload.get("questions") if isinstance(payload.get("questions"), list) else []
+    questions = []
+    for entry in raw_questions:
+        if not isinstance(entry, dict):
+            continue
+        q_text = (entry.get("q") or "").strip()
+        if len(q_text) >= 6:
+            questions.append(q_text)
+    if len(questions) < 4:
+        return None
+    recent_assistant = " ".join(
+        (msg.get("content") or "") for msg in (recent_messages or []) if msg.get("role") == "assistant"
+    )
+    if recent_assistant:
+        recent_norm = recent_assistant.lower()
+        if recent_norm and all(q.lower() in recent_norm for q in questions):
+            return {"need_more_context": True, "context_request": fallback_context, "questions": []}
+    return {"need_more_context": False, "context_request": None, "questions": questions[:6]}
 
 def _attach_goal_intent_suggestion(
     response: Dict[str, Any],
@@ -4414,6 +4590,7 @@ def handle_message():
             )
             gate_prompt = False
             questions_prompt = False
+            context_prompt = False
             if last_assistant:
                 last_text = (last_assistant.get("content") or "").lower()
                 gate_prompt = (
@@ -4421,55 +4598,42 @@ def handle_message():
                     "saved that as a pending goal suggestion" in last_text
                 )
                 questions_prompt = "before i draft steps" in last_text and "quick questions" in last_text
-            if questions_prompt:
-                goal_text = None
-                for msg in reversed(companion_context):
-                    if msg.get("role") != "assistant":
-                        continue
-                    content = (msg.get("content") or "").strip()
-                    if not content:
-                        continue
-                    match = re.search(r"goal:\s*(.+)", content, flags=re.IGNORECASE)
-                    if match:
-                        candidate = match.group(1).strip()
-                        if candidate:
-                            goal_text = candidate
-                            break
-                fallback_text = None
+                context_prompt = "tailor the questions" in last_text or "one line of context" in last_text
+            if context_prompt:
+                goal_text = _find_goal_text_in_context(companion_context)
                 if not goal_text:
-                    for msg in reversed(companion_context):
-                        if msg.get("role") != "user":
-                            continue
-                        text = (msg.get("content") or "").strip()
-                        if not text:
-                            continue
-                        norm = re.sub(r"\s+", " ", text.lower()).strip()
-                        if re.match(r"^(hi|hey|hello)\b", norm) and not re.search(
-                            r"\b(goal|want|build|start|today)\b",
-                            norm,
-                        ):
-                            continue
-                        if re.search(r"\bstep(s)?\b", norm) or "break" in norm:
-                            continue
-                        if "save" in norm:
-                            continue
-                        goal_language = re.search(r"\bgoal(s)?\b", norm) is not None
-                        goal_like = False
-                        if norm.startswith(("i want to", "my goal is", "today", "build", "start")):
-                            goal_like = True
-                        if goal_language and len(norm) > 12:
-                            goal_like = True
-                        if goal_language and not goal_like:
-                            continue
-                        if len(text) <= 12:
-                            continue
-                        if goal_like:
-                            goal_text = text
-                            break
-                        if fallback_text is None:
-                            fallback_text = text
-                    if not goal_text:
-                        goal_text = fallback_text
+                    response = {
+                        "reply": "What's the goal you want to break into steps?",
+                        "agent_status": {"planner_active": False, "had_goal_update_xml": False},
+                        "request_id": request_id,
+                        "meta": {"intent": "goal_steps_questions"},
+                    }
+                    return _respond(response)
+                questions_payload = _generate_goal_intake_questions(
+                    goal_text=goal_text,
+                    goal_title=None,
+                    goal_description=None,
+                    user_message=user_input,
+                    recent_messages=companion_context,
+                    user_id=user_id,
+                    request_id=request_id,
+                    logger=logger,
+                )
+                if questions_payload and questions_payload.get("need_more_context"):
+                    reply_text = questions_payload.get("context_request") or ""
+                elif questions_payload and questions_payload.get("questions"):
+                    reply_text = _format_goal_questions_reply(goal_text, questions_payload.get("questions"))
+                else:
+                    reply_text = _format_goal_questions_reply(goal_text)
+                response = {
+                    "reply": reply_text,
+                    "agent_status": {"planner_active": False, "had_goal_update_xml": False},
+                    "request_id": request_id,
+                    "meta": {"intent": "goal_steps_questions"},
+                }
+                return _respond(response)
+            if questions_prompt:
+                goal_text = _find_goal_text_in_context(companion_context)
                 if not goal_text:
                     response = {
                         "reply": "What's the goal you want to break into steps?",
@@ -4561,48 +4725,17 @@ def handle_message():
             has_save_word = re.search(r"\bsave\b", t) is not None
             steps_choice = has_steps_word and not (has_goal_word or has_save_word)
             goal_choice = has_goal_word or has_save_word
+            asks_questions = "question" in t and ("ask" in t or "relevant" in t or "before" in t)
             if has_steps_word and has_goal_word and not has_save_word:
                 steps_choice = True
                 goal_choice = False
             if has_steps_word and has_save_word:
                 steps_choice = False
                 goal_choice = True
+            if asks_questions and not goal_choice:
+                steps_choice = True
             if gate_prompt and (steps_choice or goal_choice):
-                goal_text = None
-                fallback_text = None
-                for msg in reversed(companion_context):
-                    if msg.get("role") != "user":
-                        continue
-                    text = (msg.get("content") or "").strip()
-                    if not text:
-                        continue
-                    norm = re.sub(r"\s+", " ", text.lower()).strip()
-                    if re.match(r"^(hi|hey|hello)\b", norm) and not re.search(
-                        r"\b(goal|want|build|start|today)\b",
-                        norm,
-                    ):
-                        continue
-                    if re.search(r"\bstep(s)?\b", norm) or "break" in norm:
-                        continue
-                    if "save" in norm:
-                        continue
-                    goal_language = re.search(r"\bgoal(s)?\b", norm) is not None
-                    goal_like = False
-                    if norm.startswith(("i want to", "my goal is", "today", "build", "start")):
-                        goal_like = True
-                    if goal_language and len(norm) > 12:
-                        goal_like = True
-                    if goal_language and not goal_like:
-                        continue
-                    if len(text) <= 12:
-                        continue
-                    if goal_like:
-                        goal_text = text
-                        break
-                    if fallback_text is None:
-                        fallback_text = text
-                if not goal_text:
-                    goal_text = fallback_text
+                goal_text = _find_goal_text_in_context(companion_context)
                 normalized_log_text = t[:60]
                 logger.info(
                     "API: continuation resolver request_id=%s gate_prompt=%s steps_choice=%s goal_choice=%s text=%s found_goal_text=%s",
@@ -4622,16 +4755,22 @@ def handle_message():
                     }
                     return _respond(response)
                 if steps_choice:
-                    reply_text = "\n".join(
-                        [
-                            f"Ok - goal: {goal_text}",
-                            "Before I draft steps, a few quick questions:",
-                            "1) What time window or cadence should this fit?",
-                            "2) What does success look like for you?",
-                            "3) Any constraints or must-avoid items?",
-                            "4) What's the hardest part?",
-                        ]
+                    questions_payload = _generate_goal_intake_questions(
+                        goal_text=goal_text,
+                        goal_title=None,
+                        goal_description=None,
+                        user_message=user_input,
+                        recent_messages=companion_context,
+                        user_id=user_id,
+                        request_id=request_id,
+                        logger=logger,
                     )
+                    if questions_payload and questions_payload.get("need_more_context"):
+                        reply_text = questions_payload.get("context_request") or ""
+                    elif questions_payload and questions_payload.get("questions"):
+                        reply_text = _format_goal_questions_reply(goal_text, questions_payload.get("questions"))
+                    else:
+                        reply_text = _format_goal_questions_reply(goal_text)
                     response = {
                         "reply": reply_text,
                         "agent_status": {"planner_active": False, "had_goal_update_xml": False},
