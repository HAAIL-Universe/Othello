# Build Mode Refactor Audit & Verification

## 1. Trigger Changes Inventory

| Trigger Source | Phrase / Condition | Old Behavior | New Behavior | Analysis |
| :--- | :--- | :--- | :--- | :--- |
| **Backend Handler** | `if "build mode" in input` | **Hard Intercept** (Started draft immediately) | **Soft Offer** (via Router) | Decoupled. Now just suggests the mode. |
| **Backend Handler** | `turn/make this (into) a goal` | **Hard Intercept** (Started draft immediately) | **Soft Offer** (via Router) | Decoupled. Prevents accidents. |
| **Backend Handler** | `(create\|make\|start).*goal.*draft` | **Hard Intercept** (Started draft) | **Removed** | Too broad/dangerous. Removed entirely. |
| **Backend Handler** | `create a goal draft` | **Hard Intercept** | **Hard Intercept** | Kept as explicit Power Command. |
| **Backend Handler** | `start a goal draft` | **Hard Intercept** | **Hard Intercept** | Kept as explicit Power Command. |
| **Backend Handler** | `ui_action: "enter_build_mode..."` | **Hard Intercept** | **Hard Intercept** | Required for Button Functionality. |
| **Router** | `_should_offer_build_mode_router` | Checked specific list | **Expanded** | Now includes "turn into goal", "make this a goal". |
| **Response Logic** | `_get_goal_intent_suggestion` | Returned `goal_intent` Type | **Mapped to `build_mode`** | Unified UI pathway. Added `bias_type="goal"`. |

## 2. Minimal Diff Strategy

We modified `z:\Othello\api.py` to:
1.  **Strictly Gate Hard Interceptions**: Removed the `elif` blocks for natural language in the "Draft Focus: Create Draft" section (~Line 4769).
2.  **Unify Soft Suggestions**: Updated `_respond` (~Line 6228) to define a single `offer_type = "build_mode"` pipeline. It checks the dedicated router first, then falls back to legacy goal intent heuristics, remapping them to `build_mode` with a payload bias.
3.  **Global Safety**: Added definition of `_build_mode_cooldowns` to prevent potential NameErrors.

## 3. Verification Plan

| User Message | Expected Outcome |
| :--- | :--- |
| **"Build mode"** | **Soft Offer**: "Enter Build Mode" badge/button appears. No immediate mode switch. |
| **"Turn this into a goal"** | **Soft Offer**: "Enter Build Mode" (Bias: Goal). Badge appears. |
| **"Create a goal draft"** | **Hard Action**: Immediate mode switch (Agent: "Draft: New Goal..."). |
| **"Help me plan"** | **Soft Offer**: "Enter Build Mode" badge appears. |
| **"I want to run a marathon"** | **Soft Offer**: "Enter Build Mode" (Bias: Goal). Badge appears. |
| **[Click 'Enter build mode']** | **Hard Action**: Immediate mode switch. |
| **"Make this a goal"** | **Soft Offer**: "Enter Build Mode" badge appears. |
| **"Show me my goals"** | **No Offer**: Disqualifier "show" prevents build mode offer. |
