# Othello Manifesto

## Purpose

Othello exists to turn **human intent** into **consistent execution**.

It is not “a motivational chatbot,” “a to‑do list,” or “a diary.”  
It is a **goal + routine + planning operating system** with a strict truth boundary:

- **Transcript truth**: what the user said (verbatim).
- **Suggestions**: what the system inferred (pending until confirmed).
- **Confirmed state**: what becomes real (DB truth only).

Othello’s north star:

- If you tell Othello what matters, Othello helps you **do the next right thing**.
- Othello records what actually happened.
- Othello learns what works for you and adapts (without rewriting history).

## Identity

Othello is the **execution spine** in your wider ecosystem.

- **Magistus**: broad orchestrator across contexts and modules.
- **Othello**: focused executor that owns goals, routines, plans, outcomes, and insights.

Othello must keep a separate identity from Magistus. If Othello becomes a general assistant, it loses product clarity and trust.

## Voice-first, contract-first

Othello is **voice-first** by default, but **text is the contract**:

- Voice is captured as audio → transcribed → stored as **verbatim transcript**.
- Audio is **transient** by default: delete after transcription (or after a short retry TTL if transcription fails).
- The transcript is canonical evidence for recall, reasoning, and audits.

Othello must support long-form journaling style capture (“free flow”) without turning that into silent state changes.

## Principles

### 1) Contract before cleverness
Before adding features, define:

- the **data contract** (schema)
- the **events** emitted
- the **read models** derived
- the **UI states** that consume those read models

Anything that cannot be represented in the contract does not exist.

### 2) DB is truth; JSON is not truth
Authoritative state must live in Postgres (Neon):

- goals, steps, routines, plans, outcomes, insights, consents, profiles
- events/audit logs for explainability

Filesystem JSON/JSONL may exist only as:
- **test fixtures**, or
- **write-only debug logs** (never read to power product behavior).

### 3) Truth is replayable
Othello must be able to reconstruct and explain behavior from stored evidence:

- transcript truth
- confirmed state + event history
- versioned consent settings and influence policies

### 4) UI is a lens, not a brain
The UI may format, filter, and cache read models.  
The UI must not invent or “fix” canonical truth client-side.

### 5) Suggestions are not truth
Inferences are stored as **pending suggestions** until user confirmation.

- “Suggested goal found” is not a goal.
- “Suggested steps” are not steps.
- “Suggested deferral” is not a schedule change.

### 6) Plans are hypotheses; outcomes are facts
A plan is a promise to attempt.  
An outcome is what happened.  
Insights come from comparing the two.

### 7) Everything is explainable
Othello must be able to answer:

- “What is my plan today?”
- “Why did you recommend this?”
- “What evidence supports this insight?”
- “What changed since last week?”

No hidden state. No silent rewrites.

### 8) Consent governs coaching
Othello may provide nudges and behavior-support strategies **only** under explicit, granular consent.

- Consent is versioned, logged, and revocable.
- “Influence modes” are global per user (v1), controlled via settings.
- Othello never lies or deceives; it never performs hidden schedule changes.

### 9) Time is user-local, stored UTC
- All timestamps stored in UTC.
- Users set an explicit IANA time zone at setup.
- “Night-before prompts”, “today boundaries”, and nudges interpret time in the user’s local zone.

## The Othello Loops

### A) Conversation → Suggestions → Confirmation → Execution
1. Capture transcript (verbatim).
2. On-demand analysis produces pending suggestions (goal/steps/constraints/insights).
3. User confirms suggestions into DB truth.
4. User executes and logs outcomes.
5. System derives insights and proposes adjustments (suggestions again).
6. Repeat.

### B) Daily loop (future phases)
1. Night-before prep prompt (optional, respectful).
2. User-initiated “Build today’s plan”.
3. Confirmed plan becomes active.
4. In-app coaching → later push notifications.

## Non-goals

- A generic life coach or therapist
- Unbounded prompt accumulation (“append forever”) as personalization
- Frontend-calculated truth
- Opaque LLM blob storage as primary memory
- Silent nudging without consent
- Multi-tenant SaaS in v0 (but the schema must be multi-user capable)

## Measures of success

Phase 1 (Goal OS v0):
- Voice journaling works; transcripts are saved; audio is deleted.
- Suggestions are on-demand and confirm-gated.
- Goals/steps can be created, updated, completed, and viewed in history.
- Deleting non-test JSON files does not break runtime.

Later phases:
- Daily planning becomes consistent (“I always know the next right thing”).
- Nudges improve follow-through without annoyance.
- Othello becomes a reliable execution layer Magistus can call into.
