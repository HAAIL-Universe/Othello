# Persona Inventory (LLM + UI)

## 1) LLM Persona / Prompt Sources
- [ ] Source A: z:/Othello/utils/prompts.py:6
  - What it is: `life_architect` system prompt ("You are Othello, a Personal Goal Architect..."). Defines Core Principles, Goal Context rules, Response Style, and Example Tone.
  - Where applied: 
    - `z:/Othello/core/architect_brain.py:245` (Chat Loop)
    - `z:/Othello/core/architect_brain.py:530` (Strict Planning Mode - extended with XML constraints)
  - Risk: Central definition, but "Strict Planning Mode" appends conflicting instructions ("XML-ONLY") to the base conversational prompt, which might confuse smaller models.

- [ ] Source B: z:/Othello/utils/prompts.py:27
  - What it is: `plan_proposal_generator` prompt ("You are Othello's Planning Engine").
  - Where applied: `z:/Othello/api.py:5451` (when `/propose` endpoint is hit).
  - Risk: Completely separate persona ("Planning Engine") from "Personal Goal Architect".

- [ ] Source C: z:/Othello/utils/prompts.py:124
  - What it is: `generate_daily_prompt` function. Returns a prompt string starting with a mood-based tone (e.g., "🔥 High energy detected. Let's channel that!", or "Cloudy/Tough day").
  - Where applied: `z:/Othello/fello.py:120` (Daily Check-in routine).
  - Risk: Programmatic string concatenation mimics personality but is hardcoded logic rather than LLM inference.

## 2) UI Persona / Copy Sources
- [ ] Source A: z:/Othello/othello_ui.html:345
  - What user sees: "Start a conversation" (Ghost text in chat area).
  - When inserted: Static HTML. Handled by CSS/JS visibility logic (`#chat-placeholder`).
  - Is it backend-driven or frontend-driven: Frontend-driven (hardcoded HTML).

- [ ] Source B: z:/Othello/othello_ui.html:351
  - What user sees: Placeholder "Tell Othello what you're working towards..." in the input bar.
  - When inserted: Static HTML attribute.
  - Is it backend-driven or frontend-driven: Frontend-driven.

- [ ] Source C: z:/Othello/othello_ui.html:6
  - What user sees: Page Title "Othello — Personal Goal Architect".
  - When inserted: Static HTML.
  - Is it backend-driven or frontend-driven: Frontend-driven.

- [ ] Source D: z:/Othello/othello_ui.html:14
  - What user sees: "Connecting to server…"
  - When inserted: Static HTML (boot overlay).
  - Is it backend-driven or frontend-driven: Frontend-driven.

- [ ] Source E: z:/Othello/static/othello.js:4171+
  - What user sees: Various error messages prefixed with "bot" role (e.g., "[Network error]", "Confirmed.").
  - When inserted: JavaScript error handlers and confirmation callbacks.
  - Is it backend-driven or frontend-driven: Frontend-driven.

## 3) Findings / Recommendations (NO CODE CHANGES)
- Single canonical place to store persona: `z:/Othello/utils/prompts.py` is the current effective canonical source for LLM prompts.
- Where persona should NOT be applied: The "Strict Planning Mode" in `architect_brain.py` appends to the base persona. It would be safer to use a dedicated "Planning" prompt (like `plan_proposal_generator`) instead of appending constraints to the conversational `life_architect` prompt to reduce token usage and potential drift.
- Quick wins to remove “robot greeting loop”:
  - The UI placeholders ("Start a conversation") are static. If the backend later sends a greeting, this might look redundant.
  - The `generate_daily_prompt` logic hardcodes "Tone" (e.g., "🔥"). This should eventually move to the LLM system prompt via variables rather than Python if-else blocks to allow the persona to evolve naturally.
