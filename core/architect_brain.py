import logging
import re
from typing import Dict, Optional, List, Union, Any
from datetime import datetime
import xml.etree.ElementTree as ET

from utils.prompts import load_prompt
from utils.utilities import async_retry

# === Persona Engines ===
from modules.goal_manager import GoalManager
from modules.trait_manager import TraitManager
from modules.routine_tracker import RoutineTracker
from modules.conversation_parser import ConversationParser
from core.conversation_parser import ConversationParser as CoreConversationParser
from core.memory_manager import MemoryManager
# (Future: from modules.behaviouralist import BehaviouralistModule)


class Architect:
    """
    Main agentic orchestrator for H.A.A.I.L. FELLO™ / Othello.

    - Handles LLM prompt assembly, context window, and persona engine (manager) updates.
    - All *long-term* memory is handled by modular managers (GoalManager, etc.).
    - Only *short-term* conversation context (N most recent turns) is kept in RAM.
    """

    def __init__(self, model, memory_window: int = 20) -> None:
        self.model = model
        self.logger = logging.getLogger("ARCHITECT")
        self.framework = "H.A.A.I.L. FELLO™"
        self.context_window = memory_window

        # === Persona engines ===
        self.goal_mgr = GoalManager()
        self.trait_mgr = TraitManager()
        self.routine_tracker = RoutineTracker()
        self.parser = ConversationParser()
        self.xml_parser = CoreConversationParser()  # For XML parsing
        self.memory_mgr = MemoryManager()  # Memory manager for agentic_memory.json
        # self.behaviouralist = BehaviouralistModule()  # (Future stub)

        # Simple rolling buffer of recent turns per user: {"user_id": [{"role": "...", "content": "..."}]}
        self.short_term_memory: Dict[str, List[Dict[str, str]]] = {}
        
        # Startup confirmation
        self.logger.info("✓ ARCHITECT: XML planning prompt loaded (life_architect)")
        self.logger.info("✓ ARCHITECT: Memory manager initialized")

    # ------------------------------------------------------------------
    # Small helper: detect if a sentence is a real goal declaration
    # ------------------------------------------------------------------
    def _is_goal_declaration(self, text: str) -> bool:
        """
        Heuristic: only auto-create goals when the user clearly states one,
        not every time they casually mention the word 'goal'.
        """
        t = text.lower()

        phrases = [
            "my goal is",
            "the goal is",
            "the goal today is",
            "today the goal is",
            "goal today is",
            "today's goal is",
            "todays goal is",
            "i have a goal",
            "i've got a goal",
            "i want to",
            "i'm aiming to",
            "i am aiming to",
            "i'm planning to",
            "i am planning to",
        ]

        if any(p in t for p in phrases):
            return True

        # Slightly more general: "... goal is to <verb> ..."
        if "goal" in t and "goal is" in t and " to " in t:
            return True

        return False

    def _strip_markdown_fences(self, text: str) -> str:
        """
        Remove markdown code fences (```xml or ```) from LLM responses.
        
        This ensures the XML parser receives clean XML without markdown formatting.
        
        Args:
            text: Raw LLM response that may contain markdown fences
        
        Returns:
            Cleaned text with fences removed
        """
        stripped = text.strip()
        
        # Remove leading fence (```xml, ```XML, or just ```)
        if stripped.startswith("```"):
            # Find the end of the first line (fence declaration)
            first_newline = stripped.find("\n")
            if first_newline != -1:
                stripped = stripped[first_newline + 1:]
            else:
                # No newline after ```, just remove the backticks
                stripped = stripped[3:]
        
        # Remove trailing fence (```)
        if stripped.endswith("```"):
            # Find the start of the last line
            last_newline = stripped.rfind("\n")
            if last_newline != -1:
                stripped = stripped[:last_newline]
            else:
                # No newline before ```, just remove the backticks
                stripped = stripped[:-3]
        
        return stripped.strip()

    def design_agent(self) -> str:
        return f"Designing agent based on {self.framework}"

    def _memory_key(self, user_id: Optional[str]) -> str:
        uid = str(user_id or "").strip()
        return uid or "anonymous"

    def _get_short_term_memory(self, user_id: Optional[str]) -> List[Dict[str, str]]:
        key = self._memory_key(user_id)
        return self.short_term_memory.setdefault(key, [])

    def _select_system_prompt(self, user_text: str, context: Optional[Dict] = None) -> str:
        """
        Routes to the appropriate system prompt based on context and user intent.
        
        Prompts:
        - WORK_MODE: For architectural/planning tasks (concise, neutral).
        - CHAT_PERSONA: For casual/open-ended support (warm, human).
        """
        prompt_key = "chat_persona"
        reason = "default"

        # 1. Strict Goal Context Check
        # Only use work mode if we have a robust goal object or explicit focus.
        if context:
            gc = context.get("goal_context")
            # Treat as focused if we have structured goal data (id/title) or explicit flag
            is_focused = context.get("focused", False)
            has_structured_goal = isinstance(gc, dict) and (gc.get("id") or gc.get("title"))
            
            if is_focused or has_structured_goal:
                prompt_key = "work_mode"
                reason = "active_goal_context"

        # 2. Heuristic Intent -> WORK_MODE
        if prompt_key == "chat_persona":
            # Requires [Ask Signal] + [Planning Keyword] to avoid false positives.
            user_text_lower = user_text.lower()
            
            # Signals that imply a request/action
            ask_signals = [
                "help", "can you", "could you", "please", "make", "create", "generate", 
                "draft", "build", "design", "how do i", "what should i"
            ]
            has_ask = any(s in user_text_lower for s in ask_signals)

            # Keywords specific to planning (word boundary matched)
            # Note: 'draft' acts as both signal and keyword, which is fine.
            triggers_pattern = r"\b(goal|plan|steps|task|tasks|routine|schedule|roadmap|milestone|draft)\b"
            hits_trigger = bool(re.search(triggers_pattern, user_text_lower))

            if has_ask and hits_trigger:
                prompt_key = "work_mode"
                reason = "explicit_planning_request"
            
        self.logger.debug(f"[prompt_router] selected={prompt_key} reason={reason}")
        return load_prompt(prompt_key)

    async def plan_and_execute(
        self,
        answers: Union[Dict[str, str], str],
        context: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None,
        recent_messages: Optional[List[Dict[str, str]]] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """
        Main planning entrypoint.

        `answers` can be:
        - a dict from the old multi-question check-in (keys: goal/trait/routine/etc.), or
        - a plain string from the chat frontend.

        We normalise both cases into:
        - `answers_dict`: a dict view
        - `raw_text`: the main user utterance for this turn

        `context` can optionally include:
        - "goal_context": a text block describing the active goal + recent notes,
          which will be injected as an extra system message.
        
        Returns:
            tuple: (response_text, agent_status_dict)
        """
        try:
            # ---- Normalise input -------------------------------------------------
            if isinstance(answers, str):
                raw_text = answers.strip()
                answers_dict: Dict[str, str] = {
                    "goal": raw_text,
                    "trait": "",
                    "routine": "",
                    "freeform": raw_text,
                }
            elif isinstance(answers, dict):
                answers_dict = answers
                raw_text = (
                    answers_dict.get("freeform")
                    or answers_dict.get("message")
                    or answers_dict.get("goal")
                    or answers_dict.get("trait")
                    or answers_dict.get("routine")
                    or " ".join(
                        v for v in answers_dict.values() if isinstance(v, str)
                    )
                ).strip()
            else:
                # Fallback: best-effort string representation
                raw_text = str(answers)
                answers_dict = {
                    "goal": raw_text,
                    "trait": "",
                    "routine": "",
                    "freeform": raw_text,
                }
            memory_user_id = user_id
            if memory_user_id is None and isinstance(context, dict):
                memory_user_id = context.get("user_id")
            if recent_messages is not None:
                short_term_memory = [
                    {"role": msg.get("role"), "content": msg.get("content")}
                    for msg in recent_messages
                    if isinstance(msg, dict)
                    and msg.get("role") in ("user", "assistant")
                    and isinstance(msg.get("content"), str)
                    and msg.get("content").strip()
                ]
            else:
                short_term_memory = self._get_short_term_memory(memory_user_id)

            self.logger.info(f"🧭 Planning response to user input: {raw_text}")

            # ---- Persona engine updates via parser ------------------------------
            goal_text = answers_dict.get("goal", raw_text)
            trait_text = answers_dict.get("trait", raw_text)
            routine_text = answers_dict.get("routine", raw_text)

            # Traits
            traits = self.parser.extract_traits(trait_text)
            if traits:
                self.trait_mgr.record_traits(traits, context=trait_text)

            # Routines
            routines = self.parser.extract_routines(routine_text)
            if routines:
                for routine in routines:
                    self.routine_tracker.log_routine_detected(
                        routine, context=routine_text
                    )

            # Goals (awareness only; no auto-save)
            goals = self.parser.extract_goals(goal_text) or []
            if goals:
                self.logger.debug(
                    f"Detected potential goals in conversation; not auto-saving. goals={goals!r}"
                )

            # ---- Build user message summary for context -------------------------
            if isinstance(answers, dict):
                full_user_msg = "\n".join(
                    [f"{k.capitalize()} Q: {q}" for k, q in answers_dict.items() if q]
                )
            else:
                full_user_msg = raw_text

            short_term_memory.append(
                {"role": "user", "content": full_user_msg}
            )
            if len(short_term_memory) > self.context_window * 2:
                del short_term_memory[:-self.context_window * 2]

            # ---- Build system prompt + messages ---------------------------------
            system_prompt = self._select_system_prompt(raw_text, context)
            
            # Check if we're in planning mode (active goal context provided)
            has_goal_context = context is not None and context.get("goal_context") is not None
            
            # Add PLANNING MODE instructions when active goal exists
            if has_goal_context:
                system_prompt += (
                    "\n\n=== ACTIVE GOAL CONTEXT ===\n"
                    "Use the goal context to provide concise guidance."
                    " Do not generate XML, code fences, or structured tags."
                    " Do not create, update, or save goals automatically."
                    " Ask at most one clarifying question if needed and keep replies actionable."
                )
            
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
            ]

            if has_goal_context:
                messages.append({
                    "role": "system",
                    "content": "Use ONLY the injected goal context for any claims about the active goal. Do not invent details."
                })
            else:
                messages.append({
                    "role": "system",
                    "content": (
                        "MEMORY & CONTEXT: You have full access to the conversation history provided in this thread. "
                        "You MUST use this history to answer questions about previous messages (e.g. 'What did I ask?', 'What is my favorite fruit?'). "
                        "Active Goal Status: NONE (Casual Chat). "
                        "If (and only if) the user explicitly asks to view/modify a Goal, explain that there is no active Goal context "
                        "and suggest creating or focusing one. "
                        "For all other topics, chat normally and context-aware using the provided history."
                    )
                })

            # Inject active goal context (if provided by API)
            if has_goal_context:
                # Build comprehensive active goal context message
                active_goal = context.get("active_goal")
                goal_context_msg = None
                
                if active_goal:
                    goal_text = active_goal.get("text", "").strip()
                    goal_id = active_goal.get("id")
                    last_summary = (active_goal.get("summary") or "").strip()
                    last_plan = (active_goal.get("plan") or "").strip()
                    
                    parts = [
                        f"Active goal context (for planning mode):",
                        f"Goal ID: {goal_id}",
                        "",
                        "Goal description:",
                        goal_text or "(no description provided)",
                    ]
                    if last_summary:
                        parts.extend(["", "Last saved summary:", last_summary])
                    if last_plan:
                        parts.extend(["", "Last saved plan:", last_plan])
                    
                    goal_context_msg = "\n".join(parts)
                    
                    messages.append({
                        "role": "system",
                        "content": goal_context_msg,
                    })
                    
                    self.logger.debug(f"ARCHITECT active goal context message:\n{goal_context_msg}")
                    self.logger.info(
                        f"→ Injected active goal context (ID: {goal_id}, {len(goal_context_msg)} chars)"
                    )
                else:
                    # Fallback to old goal_context string if active_goal not provided
                    goal_ctx = context.get("goal_context")
                    if goal_ctx:
                        messages.append(
                            {
                                "role": "system",
                                "content": (
                                    "Active goal context (for planning mode):\n\n"
                                    f"{goal_ctx}"
                                ),
                            }
                        )
                        self.logger.info(
                            f"→ Injected goal context into system messages ({len(goal_ctx)} chars)"
                        )

            # Then append short-term dialogue history
            messages += short_term_memory
            
            self.logger.info(
                f"→ Sending to LLM: {len(messages)} messages "
                f"(system={sum(1 for m in messages if m['role']=='system')}, "
                f"history={len(short_term_memory)})"
            )
            
            # Log all system messages for debugging
            for msg in messages:
                if msg.get('role') == 'system':
                    content = msg.get('content', '')
                    self.logger.debug(f"ARCHITECT system message: {content}")
            
            # Log the final combined system prompt for debugging
            if has_goal_context and messages:
                final_system_prompt = messages[0].get('content', '')
                self.logger.debug(f"ARCHITECT FINAL SYSTEM MESSAGE:\n{final_system_prompt}")

            # --- DEBUG STEP B: Pre-LLM Log ---
            _debug_msg_count = len(messages)
            _debug_roles_seq = ",".join(m.get('role', '?') for m in messages)
            
            # Find oldest and newest user messages for preview
            _user_msgs = [m for m in messages if m.get('role') == 'user']
            _oldest_preview = "N/A"
            _newest_preview = "N/A"
            if _user_msgs:
                _oldest_c = str(_user_msgs[0].get('content', ''))
                _newest_c = str(_user_msgs[-1].get('content', ''))
                _oldest_preview = (_oldest_c[:77] + "...") if len(_oldest_c) > 80 else _oldest_c
                _newest_preview = (_newest_c[:77] + "...") if len(_newest_c) > 80 else _newest_c

            self.logger.info(
                "DEBUG_LLM_PREFLIGHT: request_id=? msg_count=%d roles=%s oldest_user='%s' newest_user='%s'",
                _debug_msg_count,
                _debug_roles_seq,
                _oldest_preview,
                _newest_preview
            )
            # ---------------------------------

            # ---- Call LLM -------------------------------------------------------
            raw_response = await async_retry(self.model.chat, messages, max_tokens=1000)

            # Ensure we always end up with a string for type safety / Pylance
            if isinstance(raw_response, str):
                raw_text: str = raw_response
            elif raw_response is None:
                raw_text = ""
            else:
                raw_text = str(raw_response)
            
            # Log full raw response for debugging
            self.logger.debug(f"ARCHITECT raw LLM response: {raw_text}")

            # Parse any goal update XML before stripping it
            parsed_goal_update = self._parse_goal_update_xml(raw_text)
            
            # Remove stray markdown fences for a cleaner reply
            user_facing_response = self._strip_markdown_fences(raw_text).strip() or raw_text

            # Drop any unexpected XML goal update blocks from the user-facing reply
            if "<goal_update>" in user_facing_response and "</goal_update>" in user_facing_response:
                self.logger.info("  → Detected <goal_update> XML in response; removing and ignoring.")
                start = user_facing_response.find("<goal_update>")
                end = user_facing_response.rfind("</goal_update>")
                if start != -1 and end != -1:
                    end += len("</goal_update>")
                    user_facing_response = (
                        user_facing_response[:start] + user_facing_response[end:]
                    ).strip()

            # Log response preview for debugging
            preview = user_facing_response[:200].replace('\n', ' ')
            self.logger.info(f"← LLM response preview: {preview}...")

            agent_status = {
                "planner_active": bool(has_goal_context),
                "had_goal_update_xml": bool(parsed_goal_update),
                "goal_update": parsed_goal_update
            }

            # Append assistant turn to memory
            short_term_memory.append(
                {"role": "assistant", "content": user_facing_response}
            )

            # Debug Sink (Issue 1 Requirement A)
            agent_status["_debug"] = {
                "llm_msg_count": len(messages),
                "llm_roles_sequence": ",".join(m.get('role','?') for m in messages),
                "system_prompt_flags": {
                    "has_cant_recall": "can't recall" in system_prompt.lower() or "no access to chat history" in system_prompt.lower()
                }
            }

            # ---- Optional self-reflection hook ---------------------------------
            try:
                from core.self_reflection import SelfReflectionEngine

                sref = SelfReflectionEngine()
                summary = sref.run_reflection()
                self.logger.info(f"🪞 Self-reflection summary: {summary}")
            except ImportError:
                # Module not present - this is expected if shadow_linker isn't installed
                self.logger.debug("Self-reflection skipped: core.shadow_linker extension not available")
            except Exception as e:
                # Actual error during reflection - log as warning
                self.logger.warning(f"Self-reflection error: {e}")

            return user_facing_response, agent_status

        except Exception as e:
            self.logger.error(f"❌ Architect failed: {e}")
            # Return error message with default agent_status
            return "Sorry, something went wrong planning that.", {
                "planner_active": False,
                "had_goal_update_xml": False,
            }

    def _parse_goal_update_xml(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse the <goal_update>...</goal_update> block from the LLM
        response using the robust XML parsing from conversation_parser.
        
        This function implements safe fallback behavior:
        - If no valid <goal_update> is found, logs a warning and returns None
        - Treats parsing failure as "no plan update this turn" (not an error)
        - Never raises exceptions - gracefully handles all error conditions
        
        Returns:
            Parsed goal update dict with fields, or None if no valid XML found
        """
        try:
            # Use the XML parser from conversation_parser for robust extraction
            xml_block = self.xml_parser.extract_goal_update_xml(text)
            
            if not xml_block:
                # No XML found - this is normal for casual conversation turns
                self.logger.debug("_parse_goal_update_xml: No <goal_update> tag found in response")
                return None
            
            # Parse the XML block (handles legacy schema normalization internally)
            parsed_data = self.xml_parser.parse_goal_update_xml(xml_block)
            
            if not parsed_data:
                # XML was found but couldn't be parsed - log warning but don't crash
                self.logger.warning(
                    "_parse_goal_update_xml: XML extraction succeeded but parsing failed. "
                    "Treating as 'no plan update' turn."
                )
                self.logger.debug(f"Unparseable XML block:\n{xml_block[:500]}")
                return None
            
            # Add the raw XML to the result for debugging/logging
            parsed_data["raw_xml"] = xml_block
            
            # Log successful parsing with key metrics
            plan_step_count = len(parsed_data.get('plan_steps', []))
            has_summary = bool(parsed_data.get('summary'))
            status = parsed_data.get('status', 'unknown')
            
            self.logger.info(
                f"_parse_goal_update_xml: Successfully parsed XML "
                f"(steps={plan_step_count}, has_summary={has_summary}, status={status})"
            )
            
            return parsed_data
            
        except Exception as e:
            # Catch-all safety net: log error but never raise
            # This ensures the system continues functioning even with unexpected XML issues
            self.logger.warning(
                f"ARCHITECT: Unexpected error in _parse_goal_update_xml: {e}. "
                "Treating as normal conversational reply (no plan update)."
            )
            self.logger.debug(f"Failed XML parsing traceback:", exc_info=True)
            return None

    async def generate_goal_plan(
        self,
        user_id: str,
        goal_id: int,
        instruction: str = None,
        *,
        persist: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate or update a structured plan for the given goal using the canonical
        <goal_update> XML schema.
        
        This is a dedicated entrypoint for explicit plan generation requests from chat.
        It bypasses conversational mode and instructs the LLM to return XML-only.
        
        Args:
            user_id: The user ID (required).
            goal_id: The ID of the goal to plan for.
            instruction: Optional user instruction/context (e.g. "focus on health").
        
        Returns:
            Dict with parsed plan fields:
            {
                "goal_id": int,
                "summary": str,
                "status": str,
                "priority": str,
                "category": str,
                "plan_steps": [{"index": int, "description": str, "status": str}, ...],
                "next_action": str
            }
            
            Returns None if plan generation fails (logs error internally).
        """
        try:
            # Fetch goal from database
            goal = self.goal_mgr.get_goal(user_id, goal_id)
            if not goal:
                self.logger.error(f"generate_goal_plan: Goal #{goal_id} not found")
                return None
            
            goal_text = goal.get("text", "")
            self.logger.info(f"🎯 Generating plan for goal #{goal_id}: {goal_text[:60]}...")
            
            # Build goal context
            goal_context = self.goal_mgr.build_goal_context(user_id, goal_id, max_notes=8)
            
            # Build XML-only planning prompt
            system_prompt = load_prompt("strict_planning_xml")
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "system",
                    "content": (
                        f"Goal to plan:\n"
                        f"ID: {goal_id}\n"
                        f"Description: {goal_text}\n\n"
                        f"Context:\n{goal_context or 'No prior context.'}"
                    )
                },
            ]
            
            # Add user instruction if provided
            if instruction:
                messages.append({
                    "role": "user",
                    "content": instruction
                })
            else:
                messages.append({
                    "role": "user",
                    "content": "Generate a complete, structured plan for this goal."
                })
            
            self.logger.debug(f"generate_goal_plan: Calling LLM with {len(messages)} messages")
            
            # Call LLM
            raw_response = await async_retry(self.model.chat, messages)
            
            if isinstance(raw_response, str):
                raw_text = raw_response
            else:
                raw_text = str(raw_response) if raw_response else ""
            
            self.logger.debug(f"generate_goal_plan: Raw LLM response:\n{raw_text}")
            
            # Strip markdown fences
            clean_response = self._strip_markdown_fences(raw_text)
            
            if clean_response != raw_text:
                self.logger.info("  → Stripped markdown fences from plan generation response")
            
            # Parse the XML
            goal_update_data = self._parse_goal_update_xml(clean_response)
            
            if not goal_update_data:
                self.logger.error(
                    f"generate_goal_plan: Failed to parse XML from LLM response for goal #{goal_id}"
                )
                self.logger.debug(f"Unparseable response:\n{clean_response[:500]}")
                return None
            
            # Extract parsed fields
            summary = goal_update_data.get("summary", "")
            status = goal_update_data.get("status")
            priority = goal_update_data.get("priority")
            category = goal_update_data.get("category")
            plan_steps = goal_update_data.get("plan_steps", [])
            next_action = goal_update_data.get("next_action", "")
            
            self.logger.info(
                f"✅ Successfully parsed plan: {len(plan_steps)} steps, "
                f"status={status}, priority={priority}"
            )
            
            if not persist:
                return {
                    "goal_id": goal_id,
                    "summary": summary,
                    "status": status or "active",
                    "priority": priority or "medium",
                    "category": category or "other",
                    "plan_steps": plan_steps,
                    "next_action": next_action
                }

            # Save to database
            # Update goal metadata
            meta_updates = {}
            if status:
                meta_updates["status"] = status
            if priority:
                meta_updates["priority"] = priority
            if category:
                meta_updates["category"] = category
            
            if meta_updates:
                try:
                    from db import goals_repository
                    goals_repository.update_goal_meta(goal_id, meta_updates, user_id=user_id)
                    self.logger.info(f"  → Updated goal metadata: {meta_updates}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update goal metadata: {e}")
            
            # Save plan steps
            if plan_steps:
                try:
                    saved_steps = self.goal_mgr.save_goal_plan(user_id, goal_id, plan_steps)
                    self.logger.info(f"  → Saved {len(saved_steps)} plan steps to database")
                except Exception as e:
                    self.logger.error(f"⚠️ Failed to save plan steps: {e}", exc_info=True)
                    # Continue anyway - we still have the parsed data to return
            
            # Update conversation summary
            if summary:
                try:
                    from db import goals_repository
                    goals_repository.update_goal_from_conversation(
                        goal_id=goal_id,
                        new_summary=summary,
                        user_id=user_id
                    )
                    self.logger.info(f"  → Updated conversation summary")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update summary: {e}")
            
            # Write memory entry
            try:
                memory_entry = {
                    "type": "goal_plan_generated",
                    "goal_id": goal_id,
                    "content": f"Generated {len(plan_steps)}-step plan for '{goal_text[:50]}...'" if plan_steps else f"Updated plan for '{goal_text[:50]}...'",
                    "plan_step_count": len(plan_steps),
                    "metadata": {
                        "status": status,
                        "priority": priority,
                        "category": category
                    }
                }
                self.memory_mgr.append_memory(memory_entry)
                self.logger.info("  → Saved memory entry for plan generation")
            except Exception as e:
                self.logger.error(f"⚠️ Failed to save memory entry: {e}", exc_info=True)
            
            # Return structured result
            return {
                "goal_id": goal_id,
                "summary": summary,
                "status": status or "active",
                "priority": priority or "medium",
                "category": category or "other",
                "plan_steps": plan_steps,
                "next_action": next_action
            }
            
        except Exception as e:
            self.logger.error(
                f"❌ generate_goal_plan failed for goal #{goal_id}: {e}",
                exc_info=True
            )
            return None

    def set_memory_window(self, window_size: int) -> None:
        self.context_window = window_size

    def clear_short_term_memory(self, user_id: Optional[str] = None) -> None:
        if user_id is None:
            self.short_term_memory = {}
            return
        key = self._memory_key(user_id)
        self.short_term_memory.pop(key, None)
