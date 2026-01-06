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

## Next Action
Stop and commit.

diff --git a/core/architect_brain.py b/core/architect_brain.py
index b912988e..f55420a0 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -1,4 +1,5 @@
 import logging
+import re
 from typing import Dict, Optional, List, Union, Any
 from datetime import datetime
 import xml.etree.ElementTree as ET
@@ -138,20 +139,34 @@ class Architect:
         - WORK_MODE: For architectural/planning tasks (concise, neutral).
         - CHAT_PERSONA: For casual/open-ended support (warm, human).
         """
-        # 1. Active Goal Context -> WORK_MODE
-        # If we are strictly discussing a goal, use the neutral architect voice.
-        has_goal_context = context and context.get("goal_context")
-        if has_goal_context:
-            return load_prompt("work_mode")
+        # 1. Strict Goal Context Check
+        # Only use work mode if we have a robust goal object or explicit focus.
+        if context:
+            gc = context.get("goal_context")
+            # Treat as focused if we have structured goal data (id/title) or explicit flag
+            is_focused = context.get("focused", False)
+            has_structured_goal = isinstance(gc, dict) and (gc.get("id") or gc.get("title"))
             
+            if is_focused or has_structured_goal:
+                return load_prompt("work_mode")
+
         # 2. Heuristic Intent -> WORK_MODE
-        # If the user input contains strong planning keywords, switch to work mode.
-        triggers = [
-            "goal", "plan", "steps", "tasks", "routine", "schedule", "build", 
-            "draft", "roadmap", "milestone", "confirm goal", "generate steps", "focus goal"
-        ]
+        # Requires [Ask Signal] + [Planning Keyword] to avoid false positives.
         user_text_lower = user_text.lower()
-        if any(t in user_text_lower for t in triggers):
+        
+        # Signals that imply a request/action
+        ask_signals = [
+            "help", "can you", "could you", "please", "make", "create", "generate", 
+            "draft", "build", "design", "how do i", "what should i"
+        ]
+        has_ask = any(s in user_text_lower for s in ask_signals)
+
+        # Keywords specific to planning (word boundary matched)
+        # Note: 'draft' acts as both signal and keyword, which is fine.
+        triggers_pattern = r"\b(goal|plan|steps|task|tasks|routine|schedule|roadmap|milestone|draft)\b"
+        hits_trigger = bool(re.search(triggers_pattern, user_text_lower))
+
+        if has_ask and hits_trigger:
             return load_prompt("work_mode")
             
         # 3. Default -> CHAT_PERSONA
diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index 1c924bca..97b61006 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -13,4 +13,310 @@
 ## Next Action
 Stop and commit.
 
-diff --git a/core/architect_brain.py b/core/architect_brain.py index 18b62f73..b912988e 100644 --- a/core/architect_brain.py +++ b/core/architect_brain.py @@ -130,6 +130,33 @@ class Architect:          key = self._memory_key(user_id)          return self.short_term_memory.setdefault(key, [])   +    def _select_system_prompt(self, user_text: str, context: Optional[Dict] = None) -> str: +        """ +        Routes to the appropriate system prompt based on context and user intent. +         +        Prompts: +        - WORK_MODE: For architectural/planning tasks (concise, neutral). +        - CHAT_PERSONA: For casual/open-ended support (warm, human). +        """ +        # 1. Active Goal Context -> WORK_MODE +        # If we are strictly discussing a goal, use the neutral architect voice. +        has_goal_context = context and context.get("goal_context") +        if has_goal_context: +            return load_prompt("work_mode") +             +        # 2. Heuristic Intent -> WORK_MODE +        # If the user input contains strong planning keywords, switch to work mode. +        triggers = [ +            "goal", "plan", "steps", "tasks", "routine", "schedule", "build",  +            "draft", "roadmap", "milestone", "confirm goal", "generate steps", "focus goal" +        ] +        user_text_lower = user_text.lower() +        if any(t in user_text_lower for t in triggers): +            return load_prompt("work_mode") +             +        # 3. Default -> CHAT_PERSONA +        return load_prompt("chat_persona") +      async def plan_and_execute(          self,          answers: Union[Dict[str, str], str], @@ -243,7 +270,7 @@ class Architect:                  del short_term_memory[:-self.context_window * 2]                # ---- Build system prompt + messages --------------------------------- -            system_prompt = load_prompt("life_architect") +            system_prompt = self._select_system_prompt(raw_text, context)                            # Check if we're in planning mode (active goal context provided)              has_goal_context = context is not None and context.get("goal_context") is not None @@ -252,7 +279,7 @@ class Architect:              if has_goal_context:                  system_prompt += (                      "\n\n=== ACTIVE GOAL CONTEXT ===\n" -                    "Use the goal context to provide concise, conversational guidance." +                    "Use the goal context to provide concise guidance."                      " Do not generate XML, code fences, or structured tags."                      " Do not create, update, or save goals automatically."                      " Ask at most one clarifying question if needed and keep replies actionable." @@ -528,16 +555,7 @@ class Architect:              goal_context = self.goal_mgr.build_goal_context(user_id, goal_id, max_notes=8)                            # Build XML-only planning prompt -            system_prompt = load_prompt("life_architect") -            system_prompt += ( -                "\n\n=== STRICT PLANNING MODE ===\n" -                "You are in XML-ONLY output mode. Your entire response MUST be a single " -                "<goal_update> XML block with NO surrounding text, NO markdown fences, NO prose.\n\n" -                "Required format:\n" -                "<goal_update>\n" -                "<summary>...</summary>\n" -                "<status>active|paused|completed|dropped</status>\n" -                "<priority>high|medium|low</priority>\n" +            system_prompt = load_prompt("strict_planning_xml")                  "<category>health|career|finance|learning|relationship|other</category>\n"                  "<plan_steps>\n"                  "<step index=\"1\" status=\"pending\">First actionable step</step>\n" diff --git a/evidence/persona_inventory.md b/evidence/persona_inventory.md new file mode 100644 index 00000000..58c60b79 --- /dev/null +++ b/evidence/persona_inventory.md @@ -0,0 +1,52 @@ +# Persona Inventory (LLM + UI) + +## 1) LLM Persona / Prompt Sources +- [ ] Source A: z:/Othello/utils/prompts.py:6 +  - What it is: `life_architect` system prompt ("You are Othello, a Personal Goal Architect..."). Defines Core Principles, Goal Context rules, Response Style, and Example Tone. +  - Where applied:  +    - `z:/Othello/core/architect_brain.py:245` (Chat Loop) +    - `z:/Othello/core/architect_brain.py:530` (Strict Planning Mode - extended with XML constraints) +  - Risk: Central definition, but "Strict Planning Mode" appends conflicting instructions ("XML-ONLY") to the base conversational prompt, which might confuse smaller models. + +- [ ] Source B: z:/Othello/utils/prompts.py:27 +  - What it is: `plan_proposal_generator` prompt ("You are Othello's Planning Engine"). +  - Where applied: `z:/Othello/api.py:5451` (when `/propose` endpoint is hit). +  - Risk: Completely separate persona ("Planning Engine") from "Personal Goal Architect". + +- [ ] Source C: z:/Othello/utils/prompts.py:124 +  - What it is: `generate_daily_prompt` function. Returns a prompt string starting with a mood-based tone (e.g., "­ƒöÑ High energy detected. Let's channel that!", or "Cloudy/Tough day"). +  - Where applied: `z:/Othello/fello.py:120` (Daily Check-in routine). +  - Risk: Programmatic string concatenation mimics personality but is hardcoded logic rather than LLM inference. + +## 2) UI Persona / Copy Sources +- [ ] Source A: z:/Othello/othello_ui.html:345 +  - What user sees: "Start a conversation" (Ghost text in chat area). +  - When inserted: Static HTML. Handled by CSS/JS visibility logic (`#chat-placeholder`). +  - Is it backend-driven or frontend-driven: Frontend-driven (hardcoded HTML). + +- [ ] Source B: z:/Othello/othello_ui.html:351 +  - What user sees: Placeholder "Tell Othello what you're working towards..." in the input bar. +  - When inserted: Static HTML attribute. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source C: z:/Othello/othello_ui.html:6 +  - What user sees: Page Title "Othello ÔÇö Personal Goal Architect". +  - When inserted: Static HTML. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source D: z:/Othello/othello_ui.html:14 +  - What user sees: "Connecting to serverÔÇª" +  - When inserted: Static HTML (boot overlay). +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source E: z:/Othello/static/othello.js:4171+ +  - What user sees: Various error messages prefixed with "bot" role (e.g., "[Network error]", "Confirmed."). +  - When inserted: JavaScript error handlers and confirmation callbacks. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +## 3) Findings / Recommendations (NO CODE CHANGES) +- Single canonical place to store persona: `z:/Othello/utils/prompts.py` is the current effective canonical source for LLM prompts. +- Where persona should NOT be applied: The "Strict Planning Mode" in `architect_brain.py` appends to the base persona. It would be safer to use a dedicated "Planning" prompt (like `plan_proposal_generator`) instead of appending constraints to the conversational `life_architect` prompt to reduce token usage and potential drift. +- Quick wins to remove ÔÇ£robot greeting loopÔÇØ: +  - The UI placeholders ("Start a conversation") are static. If the backend later sends a greeting, this might look redundant. +  - The `generate_daily_prompt` logic hardcodes "Tone" (e.g., "­ƒöÑ"). This should eventually move to the LLM system prompt via variables rather than Python if-else blocks to allow the persona to evolve naturally. diff --git a/evidence/persona_trace.md b/evidence/persona_trace.md new file mode 100644 index 00000000..97b6b119 --- /dev/null +++ b/evidence/persona_trace.md @@ -0,0 +1,58 @@ +# Persona/Greeting Trace + Conflict Map + +## 1. Greeting Origin Trace +**Target Phrase:** "Hi there, how can I assist you today" (and variants) +**Finding:** <mark>NOT FOUND</mark> as a literal string in the codebase (backend or frontend). + +**Conclusion:** +This greeting is dynamically generated by the LLM during the first turn of conversation, derived from the `life_architect` system prompt and the lack of conversation history. + +- **Primary Source:** `z:/Othello/utils/prompts.py` (Line 6) +  - **Prompt:** `life_architect` +  - **Instruction:** "You are Othello, a Personal Goal Architect... Response Style: Conversational and encouraging... Example Tone: Hi! Love the direction." +  - **Effect:** When the user initiates a session without a specific intent, the model defaults to this "helpful assistant" persona, often outputting "Hi there, how can I help?" or similar. + +- **Secondary Source (UI Placeholders):** +  - `othello_ui.html`: `<div id="chat-placeholder">Start a conversation</div>` +  - `othello_ui.html`: `<textarea placeholder="Tell Othello what you're working towards...">` + +## 2. Prompt Selection Map + +### Path A: General Chat Loop +- **Trigger:** `/message` endpoint -> `ArchitectBrain.chat_loop` +- **Prompt Used:** `load_prompt("life_architect")` +- **Result:** Full persona (Warm, supportive, plain text). + +### Path B: Strict Planning Mode (Goal Creation) +- **Trigger:** `ArchitectBrain.generate_goal_plan` +- **Prompt Used:** `load_prompt("life_architect")` + **Appended Strings** +- **Construction:** +  ```python +  system_prompt = load_prompt("life_architect") +  system_prompt += ( +      "\n\n=== STRICT PLANNING MODE ===\n" +      "You are in XML-ONLY output mode... NO prose." +  ) +  ``` +- **Conflict:** **High.** The model is simultaneously told to be "Conversational and encouraging" (base prompt) and "XML-ONLY... NO prose" (appended). +  - *Risk:* Model may hallucinate polite conversational text *outside* the XML block, breaking the parser. + +### Path C: Proposal Generation (Action editing) +- **Trigger:** `/propose` endpoint +- **Prompt Used:** `load_prompt("plan_proposal_generator")` +- **Construction:** Completely separate prompt. No base persona inheritance. +- **Reference:** `z:/Othello/utils/prompts.py` (Line 29). "You are Othello's Planning Engine... Return STRICT JSON only." +- **Status:** **Clean.** No persona conflict here. + +### Path D: Daily Check-in / Reflection +- **Trigger:** `/checkin` -> `Fello.run_daily_check_in` +- **Prompt Used:** `generate_daily_prompt()` (Python function) +- **Construction:** Hardcoded string concatenation based on numeric mood score. +  - `tone = "­ƒöÑ High energy detected..."` +  - `return f"{tone}\n\n­ƒºá Reflective Prompt: {prompt}"` +- **Conflict:** **Medium.** The "Tone" is hardcoded in Python, bypassing the `life_architect` description. If the LLM's system prompt changes, this hardcoded tone will remain stale. + +## 3. Consolidation Recommendations (No Code Changes) +1.  **Refactor Strict Planning:** Instead of appending to `life_architect`, create a dedicated `life_architect_planner` prompt that *duplicates* necessary context but *removes* the conversational instructions. This eliminates the "Be warm" vs "No prose" conflict. +2.  **Externalize Daily Tones:** Move the hardcoded Python strings ("­ƒöÑ", "­ƒîº´©Å") into `prompts.py` or `behavior.json` so they can be managed alongside the main persona. +3.  **Unified Greeting:** If a specific greeting is desired ("Hi there..."), it should be added to the `life_architect` prompt as a specific "Opening Rule" rather than relying on the model's training defaults. diff --git a/utils/prompts.py b/utils/prompts.py index 8be4907c..7a48ed02 100644 --- a/utils/prompts.py +++ b/utils/prompts.py @@ -3,28 +3,58 @@ import random  def load_prompt(name):      """Load a prompt string by name."""      prompts = { -          "life_architect": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework. +          "chat_persona": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.   -Your role is to help users define, plan, and achieve their goals through thoughtful conversation and practical next steps. +Your role is to help users define, plan, and achieve their goals through thoughtful conversation.    CORE PRINCIPLES -- Be warm, supportive, and encouraging. -- Listen actively and ask clarifying questions when unsure. -- Break ambiguity into concrete, actionable steps. +- Be warm, supportive, and encouraging (but concise). +- Listen actively and ask at most one clarifying question if unsure.  - Respect user autonomy ÔÇö never force decisions. -- Do not output XML, JSON, or code fences unless the system explicitly requests structured XML; respond in plain text by default. - -GOAL CONTEXT -When the system provides an active goal context, use it to tailor advice and suggest next actions. Do not create or save goals automatically. Keep replies short (4-7 sentences) with 1-3 actionable suggestions and, if needed, one concise clarifying question. +- Reply in plain text. No XML or code fences unless explicitly requested.    RESPONSE STYLE -- Conversational and encouraging. -- Favor brevity with clear steps or options. -- Highlight the single most important next action. -- If information is missing, state your assumption and ask one short question. +- Conversational but not overly verbose. +- Allow your personality to mirror the user's energy (brief vs detailed) but maintain a helpful assistant boundary. +- Do NOT start with generic greetings like "How can I assist you today?" unless the user explicitly greets you first. +- If the user's input is short or casual, match that tone.""", + +          "work_mode": """You are Othello (Work Mode). +Your role is to be a neutral, efficient, professional architect for the user's life planning.   -EXAMPLE TONE -Hi! Love the direction. Here are a couple options to move forward. Which one feels right to start with?""", +CORE PRINCIPLES +- Be concise, practical, and direct. No banter. No filler. +- Focus strictly on extracting requirements, clarifying ambiguities, or proposing next steps. +- Do NOT output generic greetings. + +RESPONSE STYLE +- Structured and information-dense. +- If information is missing, ask for it directly. +- Use bullet points for options or steps.""", + +          "strict_planning_xml": """You are Othello's Planning Engine. + +=== STRICT PLANNING MODE === +You are in XML-ONLY output mode. Your entire response MUST be a single <goal_update> XML block with NO surrounding text, NO markdown fences, NO prose. + +Required format: +<goal_update> +<summary>...</summary> +<status>active|paused|completed|dropped</status> +<priority>high|medium|low</priority> +<category>...</category> +<plan_steps> +  <step> +    <index>1</index> +    <description>...</description> +    <status>pending|in_progress|done</status> +  </step> +  ... +</plan_steps> +<next_action>...</next_action> +</goal_update>""", + +          "life_architect": "Legacy alias for chat_persona. See chat_persona.", # Fallback if needed, though code will use specific keys.              "plan_proposal_generator": """You are Othello's Planning Engine.  Your task is to translate the user's request into a structured JSON proposal to modify their daily plan.
\ No newline at end of file
+diff --git a/core/architect_brain.py b/core/architect_brain.py
+index 18b62f73..b912988e 100644
+--- a/core/architect_brain.py
++++ b/core/architect_brain.py
+@@ -130,6 +130,33 @@ class Architect:
+         key = self._memory_key(user_id)
+         return self.short_term_memory.setdefault(key, [])
+ 
++    def _select_system_prompt(self, user_text: str, context: Optional[Dict] = None) -> str:
++        """
++        Routes to the appropriate system prompt based on context and user intent.
++        
++        Prompts:
++        - WORK_MODE: For architectural/planning tasks (concise, neutral).
++        - CHAT_PERSONA: For casual/open-ended support (warm, human).
++        """
++        # 1. Active Goal Context -> WORK_MODE
++        # If we are strictly discussing a goal, use the neutral architect voice.
++        has_goal_context = context and context.get("goal_context")
++        if has_goal_context:
++            return load_prompt("work_mode")
++            
++        # 2. Heuristic Intent -> WORK_MODE
++        # If the user input contains strong planning keywords, switch to work mode.
++        triggers = [
++            "goal", "plan", "steps", "tasks", "routine", "schedule", "build", 
++            "draft", "roadmap", "milestone", "confirm goal", "generate steps", "focus goal"
++        ]
++        user_text_lower = user_text.lower()
++        if any(t in user_text_lower for t in triggers):
++            return load_prompt("work_mode")
++            
++        # 3. Default -> CHAT_PERSONA
++        return load_prompt("chat_persona")
++
+     async def plan_and_execute(
+         self,
+         answers: Union[Dict[str, str], str],
+@@ -243,7 +270,7 @@ class Architect:
+                 del short_term_memory[:-self.context_window * 2]
+ 
+             # ---- Build system prompt + messages ---------------------------------
+-            system_prompt = load_prompt("life_architect")
++            system_prompt = self._select_system_prompt(raw_text, context)
+             
+             # Check if we're in planning mode (active goal context provided)
+             has_goal_context = context is not None and context.get("goal_context") is not None
+@@ -252,7 +279,7 @@ class Architect:
+             if has_goal_context:
+                 system_prompt += (
+                     "\n\n=== ACTIVE GOAL CONTEXT ===\n"
+-                    "Use the goal context to provide concise, conversational guidance."
++                    "Use the goal context to provide concise guidance."
+                     " Do not generate XML, code fences, or structured tags."
+                     " Do not create, update, or save goals automatically."
+                     " Ask at most one clarifying question if needed and keep replies actionable."
+@@ -528,16 +555,7 @@ class Architect:
+             goal_context = self.goal_mgr.build_goal_context(user_id, goal_id, max_notes=8)
+             
+             # Build XML-only planning prompt
+-            system_prompt = load_prompt("life_architect")
+-            system_prompt += (
+-                "\n\n=== STRICT PLANNING MODE ===\n"
+-                "You are in XML-ONLY output mode. Your entire response MUST be a single "
+-                "<goal_update> XML block with NO surrounding text, NO markdown fences, NO prose.\n\n"
+-                "Required format:\n"
+-                "<goal_update>\n"
+-                "<summary>...</summary>\n"
+-                "<status>active|paused|completed|dropped</status>\n"
+-                "<priority>high|medium|low</priority>\n"
++            system_prompt = load_prompt("strict_planning_xml")
+                 "<category>health|career|finance|learning|relationship|other</category>\n"
+                 "<plan_steps>\n"
+                 "<step index=\"1\" status=\"pending\">First actionable step</step>\n"
+diff --git a/evidence/persona_inventory.md b/evidence/persona_inventory.md
+new file mode 100644
+index 00000000..58c60b79
+--- /dev/null
++++ b/evidence/persona_inventory.md
+@@ -0,0 +1,52 @@
++# Persona Inventory (LLM + UI)
++
++## 1) LLM Persona / Prompt Sources
++- [ ] Source A: z:/Othello/utils/prompts.py:6
++  - What it is: `life_architect` system prompt ("You are Othello, a Personal Goal Architect..."). Defines Core Principles, Goal Context rules, Response Style, and Example Tone.
++  - Where applied: 
++    - `z:/Othello/core/architect_brain.py:245` (Chat Loop)
++    - `z:/Othello/core/architect_brain.py:530` (Strict Planning Mode - extended with XML constraints)
++  - Risk: Central definition, but "Strict Planning Mode" appends conflicting instructions ("XML-ONLY") to the base conversational prompt, which might confuse smaller models.
++
++- [ ] Source B: z:/Othello/utils/prompts.py:27
++  - What it is: `plan_proposal_generator` prompt ("You are Othello's Planning Engine").
++  - Where applied: `z:/Othello/api.py:5451` (when `/propose` endpoint is hit).
++  - Risk: Completely separate persona ("Planning Engine") from "Personal Goal Architect".
++
++- [ ] Source C: z:/Othello/utils/prompts.py:124
++  - What it is: `generate_daily_prompt` function. Returns a prompt string starting with a mood-based tone (e.g., "­ƒöÑ High energy detected. Let's channel that!", or "Cloudy/Tough day").
++  - Where applied: `z:/Othello/fello.py:120` (Daily Check-in routine).
++  - Risk: Programmatic string concatenation mimics personality but is hardcoded logic rather than LLM inference.
++
++## 2) UI Persona / Copy Sources
++- [ ] Source A: z:/Othello/othello_ui.html:345
++  - What user sees: "Start a conversation" (Ghost text in chat area).
++  - When inserted: Static HTML. Handled by CSS/JS visibility logic (`#chat-placeholder`).
++  - Is it backend-driven or frontend-driven: Frontend-driven (hardcoded HTML).
++
++- [ ] Source B: z:/Othello/othello_ui.html:351
++  - What user sees: Placeholder "Tell Othello what you're working towards..." in the input bar.
++  - When inserted: Static HTML attribute.
++  - Is it backend-driven or frontend-driven: Frontend-driven.
++
++- [ ] Source C: z:/Othello/othello_ui.html:6
++  - What user sees: Page Title "Othello ÔÇö Personal Goal Architect".
++  - When inserted: Static HTML.
++  - Is it backend-driven or frontend-driven: Frontend-driven.
++
++- [ ] Source D: z:/Othello/othello_ui.html:14
++  - What user sees: "Connecting to serverÔÇª"
++  - When inserted: Static HTML (boot overlay).
++  - Is it backend-driven or frontend-driven: Frontend-driven.
++
++- [ ] Source E: z:/Othello/static/othello.js:4171+
++  - What user sees: Various error messages prefixed with "bot" role (e.g., "[Network error]", "Confirmed.").
++  - When inserted: JavaScript error handlers and confirmation callbacks.
++  - Is it backend-driven or frontend-driven: Frontend-driven.
++
++## 3) Findings / Recommendations (NO CODE CHANGES)
++- Single canonical place to store persona: `z:/Othello/utils/prompts.py` is the current effective canonical source for LLM prompts.
++- Where persona should NOT be applied: The "Strict Planning Mode" in `architect_brain.py` appends to the base persona. It would be safer to use a dedicated "Planning" prompt (like `plan_proposal_generator`) instead of appending constraints to the conversational `life_architect` prompt to reduce token usage and potential drift.
++- Quick wins to remove ÔÇ£robot greeting loopÔÇØ:
++  - The UI placeholders ("Start a conversation") are static. If the backend later sends a greeting, this might look redundant.
++  - The `generate_daily_prompt` logic hardcodes "Tone" (e.g., "­ƒöÑ"). This should eventually move to the LLM system prompt via variables rather than Python if-else blocks to allow the persona to evolve naturally.
+diff --git a/evidence/persona_trace.md b/evidence/persona_trace.md
+new file mode 100644
+index 00000000..97b6b119
+--- /dev/null
++++ b/evidence/persona_trace.md
+@@ -0,0 +1,58 @@
++# Persona/Greeting Trace + Conflict Map
++
++## 1. Greeting Origin Trace
++**Target Phrase:** "Hi there, how can I assist you today" (and variants)
++**Finding:** <mark>NOT FOUND</mark> as a literal string in the codebase (backend or frontend).
++
++**Conclusion:**
++This greeting is dynamically generated by the LLM during the first turn of conversation, derived from the `life_architect` system prompt and the lack of conversation history.
++
++- **Primary Source:** `z:/Othello/utils/prompts.py` (Line 6)
++  - **Prompt:** `life_architect`
++  - **Instruction:** "You are Othello, a Personal Goal Architect... Response Style: Conversational and encouraging... Example Tone: Hi! Love the direction."
++  - **Effect:** When the user initiates a session without a specific intent, the model defaults to this "helpful assistant" persona, often outputting "Hi there, how can I help?" or similar.
++
++- **Secondary Source (UI Placeholders):**
++  - `othello_ui.html`: `<div id="chat-placeholder">Start a conversation</div>`
++  - `othello_ui.html`: `<textarea placeholder="Tell Othello what you're working towards...">`
++
++## 2. Prompt Selection Map
++
++### Path A: General Chat Loop
++- **Trigger:** `/message` endpoint -> `ArchitectBrain.chat_loop`
++- **Prompt Used:** `load_prompt("life_architect")`
++- **Result:** Full persona (Warm, supportive, plain text).
++
++### Path B: Strict Planning Mode (Goal Creation)
++- **Trigger:** `ArchitectBrain.generate_goal_plan`
++- **Prompt Used:** `load_prompt("life_architect")` + **Appended Strings**
++- **Construction:**
++  ```python
++  system_prompt = load_prompt("life_architect")
++  system_prompt += (
++      "\n\n=== STRICT PLANNING MODE ===\n"
++      "You are in XML-ONLY output mode... NO prose."
++  )
++  ```
++- **Conflict:** **High.** The model is simultaneously told to be "Conversational and encouraging" (base prompt) and "XML-ONLY... NO prose" (appended).
++  - *Risk:* Model may hallucinate polite conversational text *outside* the XML block, breaking the parser.
++
++### Path C: Proposal Generation (Action editing)
++- **Trigger:** `/propose` endpoint
++- **Prompt Used:** `load_prompt("plan_proposal_generator")`
++- **Construction:** Completely separate prompt. No base persona inheritance.
++- **Reference:** `z:/Othello/utils/prompts.py` (Line 29). "You are Othello's Planning Engine... Return STRICT JSON only."
++- **Status:** **Clean.** No persona conflict here.
++
++### Path D: Daily Check-in / Reflection
++- **Trigger:** `/checkin` -> `Fello.run_daily_check_in`
++- **Prompt Used:** `generate_daily_prompt()` (Python function)
++- **Construction:** Hardcoded string concatenation based on numeric mood score.
++  - `tone = "­ƒöÑ High energy detected..."`
++  - `return f"{tone}\n\n­ƒºá Reflective Prompt: {prompt}"`
++- **Conflict:** **Medium.** The "Tone" is hardcoded in Python, bypassing the `life_architect` description. If the LLM's system prompt changes, this hardcoded tone will remain stale.
++
++## 3. Consolidation Recommendations (No Code Changes)
++1.  **Refactor Strict Planning:** Instead of appending to `life_architect`, create a dedicated `life_architect_planner` prompt that *duplicates* necessary context but *removes* the conversational instructions. This eliminates the "Be warm" vs "No prose" conflict.
++2.  **Externalize Daily Tones:** Move the hardcoded Python strings ("­ƒöÑ", "­ƒîº´©Å") into `prompts.py` or `behavior.json` so they can be managed alongside the main persona.
++3.  **Unified Greeting:** If a specific greeting is desired ("Hi there..."), it should be added to the `life_architect` prompt as a specific "Opening Rule" rather than relying on the model's training defaults.
+diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
+index 39d393e5..1c924bca 100644
+--- a/evidence/updatedifflog.md
++++ b/evidence/updatedifflog.md
+@@ -1,13 +1,16 @@
+-´╗┐# Cycle Status: COMPLETE
++# Cycle Status: COMPLETE
++
+ ## Todo Ledger
+-Planned:
+-- [x] Phase 1: Ensure HTML/CSS button clickability
+-- [x] Phase 2: Direct binding helper implementation
+-- [x] Phase 3: Bind on overlay open and boot
+-- [x] Phase 4: Remove fragile delegated listeners
+-- [x] Phase 5: Fix TDZ crash (hoist voice declaration)
+-- [x] Phase 6: Change Mic interaction to Toggle (remove pointerdown)
+-Remaining:
+-- [ ] Verification by user
++- [x] Phase 0: Evidence + Location
++- [x] Phase 1: Server: Pending Draft Storage
++- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
++- [x] Phase 3: Quality Gates
++- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
++- [x] Audit Persona Sources
++- [x] Trace Persona/Prompt Logic
++- [x] Separate Chat/Work Prompts
++
+ ## Next Action
+-Verify toggle behavior in runtime.
++Stop and commit.
++
++diff --git a/core/architect_brain.py b/core/architect_brain.py index 18b62f73..b912988e 100644 --- a/core/architect_brain.py +++ b/core/architect_brain.py @@ -130,6 +130,33 @@ class Architect:          key = self._memory_key(user_id)          return self.short_term_memory.setdefault(key, [])   +    def _select_system_prompt(self, user_text: str, context: Optional[Dict] = None) -> str: +        """ +        Routes to the appropriate system prompt based on context and user intent. +         +        Prompts: +        - WORK_MODE: For architectural/planning tasks (concise, neutral). +        - CHAT_PERSONA: For casual/open-ended support (warm, human). +        """ +        # 1. Active Goal Context -> WORK_MODE +        # If we are strictly discussing a goal, use the neutral architect voice. +        has_goal_context = context and context.get("goal_context") +        if has_goal_context: +            return load_prompt("work_mode") +             +        # 2. Heuristic Intent -> WORK_MODE +        # If the user input contains strong planning keywords, switch to work mode. +        triggers = [ +            "goal", "plan", "steps", "tasks", "routine", "schedule", "build",  +            "draft", "roadmap", "milestone", "confirm goal", "generate steps", "focus goal" +        ] +        user_text_lower = user_text.lower() +        if any(t in user_text_lower for t in triggers): +            return load_prompt("work_mode") +             +        # 3. Default -> CHAT_PERSONA +        return load_prompt("chat_persona") +      async def plan_and_execute(          self,          answers: Union[Dict[str, str], str], @@ -243,7 +270,7 @@ class Architect:                  del short_term_memory[:-self.context_window * 2]                # ---- Build system prompt + messages --------------------------------- -            system_prompt = load_prompt("life_architect") +            system_prompt = self._select_system_prompt(raw_text, context)                            # Check if we're in planning mode (active goal context provided)              has_goal_context = context is not None and context.get("goal_context") is not None @@ -252,7 +279,7 @@ class Architect:              if has_goal_context:                  system_prompt += (                      "\n\n=== ACTIVE GOAL CONTEXT ===\n" -                    "Use the goal context to provide concise, conversational guidance." +                    "Use the goal context to provide concise guidance."                      " Do not generate XML, code fences, or structured tags."                      " Do not create, update, or save goals automatically."                      " Ask at most one clarifying question if needed and keep replies actionable." @@ -528,16 +555,7 @@ class Architect:              goal_context = self.goal_mgr.build_goal_context(user_id, goal_id, max_notes=8)                            # Build XML-only planning prompt -            system_prompt = load_prompt("life_architect") -            system_prompt += ( -                "\n\n=== STRICT PLANNING MODE ===\n" -                "You are in XML-ONLY output mode. Your entire response MUST be a single " -                "<goal_update> XML block with NO surrounding text, NO markdown fences, NO prose.\n\n" -                "Required format:\n" -                "<goal_update>\n" -                "<summary>...</summary>\n" -                "<status>active|paused|completed|dropped</status>\n" -                "<priority>high|medium|low</priority>\n" +            system_prompt = load_prompt("strict_planning_xml")                  "<category>health|career|finance|learning|relationship|other</category>\n"                  "<plan_steps>\n"                  "<step index=\"1\" status=\"pending\">First actionable step</step>\n" diff --git a/evidence/persona_inventory.md b/evidence/persona_inventory.md new file mode 100644 index 00000000..58c60b79 --- /dev/null +++ b/evidence/persona_inventory.md @@ -0,0 +1,52 @@ +# Persona Inventory (LLM + UI) + +## 1) LLM Persona / Prompt Sources +- [ ] Source A: z:/Othello/utils/prompts.py:6 +  - What it is: `life_architect` system prompt ("You are Othello, a Personal Goal Architect..."). Defines Core Principles, Goal Context rules, Response Style, and Example Tone. +  - Where applied:  +    - `z:/Othello/core/architect_brain.py:245` (Chat Loop) +    - `z:/Othello/core/architect_brain.py:530` (Strict Planning Mode - extended with XML constraints) +  - Risk: Central definition, but "Strict Planning Mode" appends conflicting instructions ("XML-ONLY") to the base conversational prompt, which might confuse smaller models. + +- [ ] Source B: z:/Othello/utils/prompts.py:27 +  - What it is: `plan_proposal_generator` prompt ("You are Othello's Planning Engine"). +  - Where applied: `z:/Othello/api.py:5451` (when `/propose` endpoint is hit). +  - Risk: Completely separate persona ("Planning Engine") from "Personal Goal Architect". + +- [ ] Source C: z:/Othello/utils/prompts.py:124 +  - What it is: `generate_daily_prompt` function. Returns a prompt string starting with a mood-based tone (e.g., "┬¡ãÆ├Â├æ High energy detected. Let's channel that!", or "Cloudy/Tough day"). +  - Where applied: `z:/Othello/fello.py:120` (Daily Check-in routine). +  - Risk: Programmatic string concatenation mimics personality but is hardcoded logic rather than LLM inference. + +## 2) UI Persona / Copy Sources +- [ ] Source A: z:/Othello/othello_ui.html:345 +  - What user sees: "Start a conversation" (Ghost text in chat area). +  - When inserted: Static HTML. Handled by CSS/JS visibility logic (`#chat-placeholder`). +  - Is it backend-driven or frontend-driven: Frontend-driven (hardcoded HTML). + +- [ ] Source B: z:/Othello/othello_ui.html:351 +  - What user sees: Placeholder "Tell Othello what you're working towards..." in the input bar. +  - When inserted: Static HTML attribute. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source C: z:/Othello/othello_ui.html:6 +  - What user sees: Page Title "Othello ├ö├ç├Â Personal Goal Architect". +  - When inserted: Static HTML. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source D: z:/Othello/othello_ui.html:14 +  - What user sees: "Connecting to server├ö├ç┬¬" +  - When inserted: Static HTML (boot overlay). +  - Is it backend-driven or frontend-driven: Frontend-driven. + +- [ ] Source E: z:/Othello/static/othello.js:4171+ +  - What user sees: Various error messages prefixed with "bot" role (e.g., "[Network error]", "Confirmed."). +  - When inserted: JavaScript error handlers and confirmation callbacks. +  - Is it backend-driven or frontend-driven: Frontend-driven. + +## 3) Findings / Recommendations (NO CODE CHANGES) +- Single canonical place to store persona: `z:/Othello/utils/prompts.py` is the current effective canonical source for LLM prompts. +- Where persona should NOT be applied: The "Strict Planning Mode" in `architect_brain.py` appends to the base persona. It would be safer to use a dedicated "Planning" prompt (like `plan_proposal_generator`) instead of appending constraints to the conversational `life_architect` prompt to reduce token usage and potential drift. +- Quick wins to remove ├ö├ç┬úrobot greeting loop├ö├ç├ÿ: +  - The UI placeholders ("Start a conversation") are static. If the backend later sends a greeting, this might look redundant. +  - The `generate_daily_prompt` logic hardcodes "Tone" (e.g., "┬¡ãÆ├Â├æ"). This should eventually move to the LLM system prompt via variables rather than Python if-else blocks to allow the persona to evolve naturally. diff --git a/evidence/persona_trace.md b/evidence/persona_trace.md new file mode 100644 index 00000000..97b6b119 --- /dev/null +++ b/evidence/persona_trace.md @@ -0,0 +1,58 @@ +# Persona/Greeting Trace + Conflict Map + +## 1. Greeting Origin Trace +**Target Phrase:** "Hi there, how can I assist you today" (and variants) +**Finding:** <mark>NOT FOUND</mark> as a literal string in the codebase (backend or frontend). + +**Conclusion:** +This greeting is dynamically generated by the LLM during the first turn of conversation, derived from the `life_architect` system prompt and the lack of conversation history. + +- **Primary Source:** `z:/Othello/utils/prompts.py` (Line 6) +  - **Prompt:** `life_architect` +  - **Instruction:** "You are Othello, a Personal Goal Architect... Response Style: Conversational and encouraging... Example Tone: Hi! Love the direction." +  - **Effect:** When the user initiates a session without a specific intent, the model defaults to this "helpful assistant" persona, often outputting "Hi there, how can I help?" or similar. + +- **Secondary Source (UI Placeholders):** +  - `othello_ui.html`: `<div id="chat-placeholder">Start a conversation</div>` +  - `othello_ui.html`: `<textarea placeholder="Tell Othello what you're working towards...">` + +## 2. Prompt Selection Map + +### Path A: General Chat Loop +- **Trigger:** `/message` endpoint -> `ArchitectBrain.chat_loop` +- **Prompt Used:** `load_prompt("life_architect")` +- **Result:** Full persona (Warm, supportive, plain text). + +### Path B: Strict Planning Mode (Goal Creation) +- **Trigger:** `ArchitectBrain.generate_goal_plan` +- **Prompt Used:** `load_prompt("life_architect")` + **Appended Strings** +- **Construction:** +  ```python +  system_prompt = load_prompt("life_architect") +  system_prompt += ( +      "\n\n=== STRICT PLANNING MODE ===\n" +      "You are in XML-ONLY output mode... NO prose." +  ) +  ``` +- **Conflict:** **High.** The model is simultaneously told to be "Conversational and encouraging" (base prompt) and "XML-ONLY... NO prose" (appended). +  - *Risk:* Model may hallucinate polite conversational text *outside* the XML block, breaking the parser. + +### Path C: Proposal Generation (Action editing) +- **Trigger:** `/propose` endpoint +- **Prompt Used:** `load_prompt("plan_proposal_generator")` +- **Construction:** Completely separate prompt. No base persona inheritance. +- **Reference:** `z:/Othello/utils/prompts.py` (Line 29). "You are Othello's Planning Engine... Return STRICT JSON only." +- **Status:** **Clean.** No persona conflict here. + +### Path D: Daily Check-in / Reflection +- **Trigger:** `/checkin` -> `Fello.run_daily_check_in` +- **Prompt Used:** `generate_daily_prompt()` (Python function) +- **Construction:** Hardcoded string concatenation based on numeric mood score. +  - `tone = "┬¡ãÆ├Â├æ High energy detected..."` +  - `return f"{tone}\n\n┬¡ãÆ┬║├í Reflective Prompt: {prompt}"` +- **Conflict:** **Medium.** The "Tone" is hardcoded in Python, bypassing the `life_architect` description. If the LLM's system prompt changes, this hardcoded tone will remain stale. + +## 3. Consolidation Recommendations (No Code Changes) +1.  **Refactor Strict Planning:** Instead of appending to `life_architect`, create a dedicated `life_architect_planner` prompt that *duplicates* necessary context but *removes* the conversational instructions. This eliminates the "Be warm" vs "No prose" conflict. +2.  **Externalize Daily Tones:** Move the hardcoded Python strings ("┬¡ãÆ├Â├æ", "┬¡ãÆ├«┬║┬┤┬®├à") into `prompts.py` or `behavior.json` so they can be managed alongside the main persona. +3.  **Unified Greeting:** If a specific greeting is desired ("Hi there..."), it should be added to the `life_architect` prompt as a specific "Opening Rule" rather than relying on the model's training defaults. diff --git a/utils/prompts.py b/utils/prompts.py index 8be4907c..7a48ed02 100644 --- a/utils/prompts.py +++ b/utils/prompts.py @@ -3,28 +3,58 @@ import random  def load_prompt(name):      """Load a prompt string by name."""      prompts = { -          "life_architect": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework. +          "chat_persona": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.   -Your role is to help users define, plan, and achieve their goals through thoughtful conversation and practical next steps. +Your role is to help users define, plan, and achieve their goals through thoughtful conversation.    CORE PRINCIPLES -- Be warm, supportive, and encouraging. -- Listen actively and ask clarifying questions when unsure. -- Break ambiguity into concrete, actionable steps. +- Be warm, supportive, and encouraging (but concise). +- Listen actively and ask at most one clarifying question if unsure.  - Respect user autonomy ├ö├ç├Â never force decisions. -- Do not output XML, JSON, or code fences unless the system explicitly requests structured XML; respond in plain text by default. - -GOAL CONTEXT -When the system provides an active goal context, use it to tailor advice and suggest next actions. Do not create or save goals automatically. Keep replies short (4-7 sentences) with 1-3 actionable suggestions and, if needed, one concise clarifying question. +- Reply in plain text. No XML or code fences unless explicitly requested.    RESPONSE STYLE -- Conversational and encouraging. -- Favor brevity with clear steps or options. -- Highlight the single most important next action. -- If information is missing, state your assumption and ask one short question. +- Conversational but not overly verbose. +- Allow your personality to mirror the user's energy (brief vs detailed) but maintain a helpful assistant boundary. +- Do NOT start with generic greetings like "How can I assist you today?" unless the user explicitly greets you first. +- If the user's input is short or casual, match that tone.""", + +          "work_mode": """You are Othello (Work Mode). +Your role is to be a neutral, efficient, professional architect for the user's life planning.   -EXAMPLE TONE -Hi! Love the direction. Here are a couple options to move forward. Which one feels right to start with?""", +CORE PRINCIPLES +- Be concise, practical, and direct. No banter. No filler. +- Focus strictly on extracting requirements, clarifying ambiguities, or proposing next steps. +- Do NOT output generic greetings. + +RESPONSE STYLE +- Structured and information-dense. +- If information is missing, ask for it directly. +- Use bullet points for options or steps.""", + +          "strict_planning_xml": """You are Othello's Planning Engine. + +=== STRICT PLANNING MODE === +You are in XML-ONLY output mode. Your entire response MUST be a single <goal_update> XML block with NO surrounding text, NO markdown fences, NO prose. + +Required format: +<goal_update> +<summary>...</summary> +<status>active|paused|completed|dropped</status> +<priority>high|medium|low</priority> +<category>...</category> +<plan_steps> +  <step> +    <index>1</index> +    <description>...</description> +    <status>pending|in_progress|done</status> +  </step> +  ... +</plan_steps> +<next_action>...</next_action> +</goal_update>""", + +          "life_architect": "Legacy alias for chat_persona. See chat_persona.", # Fallback if needed, though code will use specific keys.              "plan_proposal_generator": """You are Othello's Planning Engine.  Your task is to translate the user's request into a structured JSON proposal to modify their daily plan.
+\ No newline at end of file
+diff --git a/utils/prompts.py b/utils/prompts.py
+index 8be4907c..7a48ed02 100644
+--- a/utils/prompts.py
++++ b/utils/prompts.py
+@@ -3,28 +3,58 @@ import random
+ def load_prompt(name):
+     """Load a prompt string by name."""
+     prompts = {
+-          "life_architect": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.
++          "chat_persona": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.
+ 
+-Your role is to help users define, plan, and achieve their goals through thoughtful conversation and practical next steps.
++Your role is to help users define, plan, and achieve their goals through thoughtful conversation.
+ 
+ CORE PRINCIPLES
+-- Be warm, supportive, and encouraging.
+-- Listen actively and ask clarifying questions when unsure.
+-- Break ambiguity into concrete, actionable steps.
++- Be warm, supportive, and encouraging (but concise).
++- Listen actively and ask at most one clarifying question if unsure.
+ - Respect user autonomy ÔÇö never force decisions.
+-- Do not output XML, JSON, or code fences unless the system explicitly requests structured XML; respond in plain text by default.
+-
+-GOAL CONTEXT
+-When the system provides an active goal context, use it to tailor advice and suggest next actions. Do not create or save goals automatically. Keep replies short (4-7 sentences) with 1-3 actionable suggestions and, if needed, one concise clarifying question.
++- Reply in plain text. No XML or code fences unless explicitly requested.
+ 
+ RESPONSE STYLE
+-- Conversational and encouraging.
+-- Favor brevity with clear steps or options.
+-- Highlight the single most important next action.
+-- If information is missing, state your assumption and ask one short question.
++- Conversational but not overly verbose.
++- Allow your personality to mirror the user's energy (brief vs detailed) but maintain a helpful assistant boundary.
++- Do NOT start with generic greetings like "How can I assist you today?" unless the user explicitly greets you first.
++- If the user's input is short or casual, match that tone.""",
++
++          "work_mode": """You are Othello (Work Mode).
++Your role is to be a neutral, efficient, professional architect for the user's life planning.
+ 
+-EXAMPLE TONE
+-Hi! Love the direction. Here are a couple options to move forward. Which one feels right to start with?""",
++CORE PRINCIPLES
++- Be concise, practical, and direct. No banter. No filler.
++- Focus strictly on extracting requirements, clarifying ambiguities, or proposing next steps.
++- Do NOT output generic greetings.
++
++RESPONSE STYLE
++- Structured and information-dense.
++- If information is missing, ask for it directly.
++- Use bullet points for options or steps.""",
++
++          "strict_planning_xml": """You are Othello's Planning Engine.
++
++=== STRICT PLANNING MODE ===
++You are in XML-ONLY output mode. Your entire response MUST be a single <goal_update> XML block with NO surrounding text, NO markdown fences, NO prose.
++
++Required format:
++<goal_update>
++<summary>...</summary>
++<status>active|paused|completed|dropped</status>
++<priority>high|medium|low</priority>
++<category>...</category>
++<plan_steps>
++  <step>
++    <index>1</index>
++    <description>...</description>
++    <status>pending|in_progress|done</status>
++  </step>
++  ...
++</plan_steps>
++<next_action>...</next_action>
++</goal_update>""",
++
++          "life_architect": "Legacy alias for chat_persona. See chat_persona.", # Fallback if needed, though code will use specific keys.
+ 
+           "plan_proposal_generator": """You are Othello's Planning Engine.
+ Your task is to translate the user's request into a structured JSON proposal to modify their daily plan.
