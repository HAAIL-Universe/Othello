# Othello Manifesto

## Purpose

Othello exists to turn **human intent** into **consistent execution**.

It is not “a motivational chatbot,” “a to‑do list,” or “a diary.”  
It is a **personal operations system**: a planner + routine engine + behavioural insight loop that turns fuzzy goals into repeatable action.

Othello’s north star is simple:

- If you tell Othello what matters, Othello helps you **do the next right thing today**
- Othello records what actually happened
- Othello learns what works for you, and adapts tomorrow

## Identity

Othello is the **tactical executor** in your wider ecosystem:

- **Magistus** (brain/orchestrator) can reason across contexts and modules.
- **Othello** (execution spine) produces plans, collects outcomes, and generates behavioural insights.
- Othello must remain **contract-first** and **debuggable**, so other systems can safely rely on it.

Othello must be:

- **Deterministic where it counts** (truth, state, projections)
- **Adaptive where it helps** (plan suggestions, task phrasing, coaching tone)
- **Traceable always** (you can answer “why did it do that?” from stored evidence)

## Principles

### 1) Contract before cleverness
Before adding features, define:

- the **data contract** (schema)
- the **events** emitted
- the **read models** derived
- the **UI states** that consume those read models

Anything that cannot be represented in the contract does not exist.

### 2) Truth is append-only
Othello’s source of truth is an **event ledger**:

- Every meaningful user action becomes an event.
- Events are not edited in place. Corrections are new events.
- Read models are derived from events (or maintained as projections).

This makes Othello replayable, auditable, and scalable.

### 3) UI is a lens, not a brain
The UI does not compute truth.

- The UI may format, sort, filter, and render.
- The UI may cache read models.
- The UI must not invent state that the backend cannot justify.

### 4) Plans are promises; outcomes are reality
A “plan” is not the same as “progress.”

- Plans are hypotheses.
- Outcomes are facts.
- Insight comes from comparing them.

### 5) Behaviour beats vibes
Othello optimizes for **behavioural change**, not “good feelings.”

The tone may be encouraging, but the system is measured by:

- adherence and follow-through
- reduced friction
- improved consistency
- improved next-action clarity

### 6) Minimalism, but not fragility
Othello should be small and fast, but never brittle.

- fewer moving parts, but strong boundaries
- simple auth now, but expandable later
- Render cold starts handled as first-class UX

### 7) Everything is explainable
Othello must be able to answer:

- “What is my plan today?”
- “Why is this task recommended?”
- “What evidence supports this insight?”
- “What changed since last week?”

No hidden magic. No silent state loss.

## The Othello Loop

1. **Capture intent**
   - Goal, routine, constraint, mood, time window, context.
2. **Normalize into a structured update**
   - Always ends as a canonical internal schema.
3. **Generate a Today Plan**
   - Few tasks, right size, ordered, time-aware.
4. **Execute and record reality**
   - done / partial / skipped / blocked + reason
5. **Reflect and learn**
   - insights + adjustments
6. **Repeat**
   - tomorrow’s plan incorporates what was learned

## What Othello is NOT (Non-goals)

- A generic life coach or therapist
- An unstructured “chat log” with no durable meaning
- A place where the frontend calculates canonical truth
- A system that stores opaque LLM blobs as its primary memory
- A multi-tenant SaaS (yet). Start as single-user, expand cleanly later.
- A “perfect planner” that requires perfect behaviour

## Product Guardrails

- **No silent data loss**: if something fails, it must be visible (UI + logs).
- **No unversioned contracts**: schema drift is a bug.
- **No hidden state**: every derived state must be reproducible from the ledger + config.
- **No dependency on “LLM availability” for core truth**: the system still runs if AI is off.

## Measures of Success

Short-term:

- Othello reliably boots on Render, shows a waking state, and responds.
- You can create goals, get a Today Plan, log outcomes, and see insights.

Mid-term:

- Planning becomes fast and consistent: “I always know what to do next.”
- Insights lead to real plan adjustments: fewer repeated failures.

Long-term:

- Othello becomes a trustworthy execution layer Magistus can call into.
- Your history becomes a replayable dataset that explains your behaviour and growth.

