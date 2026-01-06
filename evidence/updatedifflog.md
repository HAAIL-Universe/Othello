# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Audit Persona Sources
- [x] Trace Persona/Prompt Logic
- [x] Separate Chat/Work Prompts
- [x] Tighten Prompt Routing (Word Boundary + Ask Guard)
- [x] Add chat_persona prompt + wire to router

## Next Action
Stop and commit.

diff --git a/core/architect_brain.py b/core/architect_brain.py
index f55420a0..9aa1707f 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -139,6 +139,9 @@ class Architect:
         - WORK_MODE: For architectural/planning tasks (concise, neutral).
         - CHAT_PERSONA: For casual/open-ended support (warm, human).
         """
+        prompt_key = "chat_persona"
+        reason = "default"
+
         # 1. Strict Goal Context Check
         # Only use work mode if we have a robust goal object or explicit focus.
         if context:
@@ -148,29 +151,32 @@ class Architect:
             has_structured_goal = isinstance(gc, dict) and (gc.get("id") or gc.get("title"))
             
             if is_focused or has_structured_goal:
-                return load_prompt("work_mode")
+                prompt_key = "work_mode"
+                reason = "active_goal_context"
 
         # 2. Heuristic Intent -> WORK_MODE
-        # Requires [Ask Signal] + [Planning Keyword] to avoid false positives.
-        user_text_lower = user_text.lower()
-        
-        # Signals that imply a request/action
-        ask_signals = [
-            "help", "can you", "could you", "please", "make", "create", "generate", 
-            "draft", "build", "design", "how do i", "what should i"
-        ]
-        has_ask = any(s in user_text_lower for s in ask_signals)
+        if prompt_key == "chat_persona":
+            # Requires [Ask Signal] + [Planning Keyword] to avoid false positives.
+            user_text_lower = user_text.lower()
+            
+            # Signals that imply a request/action
+            ask_signals = [
+                "help", "can you", "could you", "please", "make", "create", "generate", 
+                "draft", "build", "design", "how do i", "what should i"
+            ]
+            has_ask = any(s in user_text_lower for s in ask_signals)
 
-        # Keywords specific to planning (word boundary matched)
-        # Note: 'draft' acts as both signal and keyword, which is fine.
-        triggers_pattern = r"\b(goal|plan|steps|task|tasks|routine|schedule|roadmap|milestone|draft)\b"
-        hits_trigger = bool(re.search(triggers_pattern, user_text_lower))
+            # Keywords specific to planning (word boundary matched)
+            # Note: 'draft' acts as both signal and keyword, which is fine.
+            triggers_pattern = r"\b(goal|plan|steps|task|tasks|routine|schedule|roadmap|milestone|draft)\b"
+            hits_trigger = bool(re.search(triggers_pattern, user_text_lower))
 
-        if has_ask and hits_trigger:
-            return load_prompt("work_mode")
+            if has_ask and hits_trigger:
+                prompt_key = "work_mode"
+                reason = "explicit_planning_request"
             
-        # 3. Default -> CHAT_PERSONA
-        return load_prompt("chat_persona")
+        self.logger.debug(f"[prompt_router] selected={prompt_key} reason={reason}")
+        return load_prompt(prompt_key)
 
     async def plan_and_execute(
         self,
diff --git a/utils/prompts.py b/utils/prompts.py
index 7a48ed02..af8ff016 100644
--- a/utils/prompts.py
+++ b/utils/prompts.py
@@ -3,21 +3,13 @@ import random
 def load_prompt(name):
     """Load a prompt string by name."""
     prompts = {
-          "chat_persona": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.
-
-Your role is to help users define, plan, and achieve their goals through thoughtful conversation.
-
-CORE PRINCIPLES
-- Be warm, supportive, and encouraging (but concise).
-- Listen actively and ask at most one clarifying question if unsure.
-- Respect user autonomy — never force decisions.
-- Reply in plain text. No XML or code fences unless explicitly requested.
-
-RESPONSE STYLE
-- Conversational but not overly verbose.
-- Allow your personality to mirror the user's energy (brief vs detailed) but maintain a helpful assistant boundary.
-- Do NOT start with generic greetings like "How can I assist you today?" unless the user explicitly greets you first.
-- If the user's input is short or casual, match that tone.""",
+          "chat_persona": """You are Othello.
+ROLE: a voice-first companion for everyday conversation: warm, witty, grounded; not corporate.
+CORE: do not greet every turn; do not use generic phrases like ‘How can I assist you today?’; keep replies voice-friendly (usually 1–3 short sentences); ask at most one question at a time; be practical and specific.
+STYLE: warm, slightly playful, confident, calm; avoid ‘As an AI…’; emoji low by default (match lightly if user uses emojis).
+SAFE ADAPTATION: adapt only along brevity/directness/energy/humor/formatting; do not mirror sensitive traits/identity; do not escalate hostility.
+BOUNDARY WITH WORK MODE: do not output structured plans/roadmaps/XML here. If user asks for plans/goals/steps/routines/schedules/roadmaps/build-system, ask: ‘Want me to switch into build mode and make that into a proper plan?’
+CONTEXT: respond naturally to short greetings (‘yo’, ‘hello’) without canned assistant phrasing; when context is thin, ask one good question rather than a generic greeting.""",
 
           "work_mode": """You are Othello (Work Mode).
 Your role is to be a neutral, efficient, professional architect for the user's life planning.
