# Draft Handling & Cleanup Report

## Changes Implemented

### 1. Data Hygiene (Danger Zone)
- **Updated `api.py` (`v1_clear_data`):**
  - When "goals" are cleared via the Settings > Data > Clear Data menu, **pending goal drafts** are now also deleted.
  - This ensures that a "fresh start" actually removes stuck drafts.

### 2. Deterministic Dismissal
- **New Endpoint:** `POST /v1/suggestions/<id>/dismiss`
- **Behavior:** Explicitly marks a suggestion as `status='rejected'` (matches schema).
- This provides a reliable API surface for the frontend to clear drafts without relying on chat side-effects.

### 3. Duplicate Prevention
- **Updated `api.py` (Draft Creation):**
  - Before creating a new goal suggestion from chat intent, the system now checks for **existing pending suggestions** with the same title (case-insensitive).
  - If a duplicate is found, it reuses the existing draft ID instead of creating a new one.
  - This prevents the "piling up" of identical drafts when the user repeats a request.

### 4. Frontend UI
- **Updated `static/othello.js`:**
  - The Goals tab now renders a **Dismiss (×)** button on draft cards.
  - Clicking this button triggers the new `/dismiss` endpoint.
  - UI automatically refreshes to remove the card immediately.

## Verification
- **Clear Data:** Verified logic addresses `kind='goal'` in `active_steps` cleanup.
- **Dismiss:** Verified new route definition in `api.py`.
- **Dedupe:** Verified check-before-create logic in intent handler.
