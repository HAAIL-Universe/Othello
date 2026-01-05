# Phase 8: Draft Visibility + Step Generation

## Changes

### Backend (`api.py`)
- Added `_generate_draft_steps_payload` helper function using LLM JSON mode.
- Updated `handle_message` to handle `ui_action="generate_draft_steps"` and voice commands ("generate steps").
- Updated draft edit response to return `draft_payload` and a descriptive reply.

### Frontend (`othello_ui.html`, `othello.css`, `othello.js`)
- Added `#draft-preview` container to the chat view.
- Added CSS for `.draft-preview`.
- Updated `othelloState` to track `activeDraftPayload`.
- Updated `handleServerResponse` to store `draft_payload`.
- Implemented `renderDraftPreview` to show draft details (Title, Target, Steps).
- Updated `updateFocusRibbon` to include "Generate Steps" button and call `renderDraftPreview`.
- Updated `loadDraftState` to restore payload from localStorage.

## Verification
- "Generate Steps" button should appear in the ribbon when a draft is active.
- Clicking "Generate Steps" should trigger the backend to generate steps and update the draft.
- The draft preview should appear in the chat view showing the title, target days, and steps.
- Voice commands "generate steps" should also work.
