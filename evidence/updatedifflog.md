Cycle Status: COMPLETE (AUDIT)
Todo Ledger:
Planned: [Identify off-screen expansion cause]
Completed: [Audit DOM structure in othello_ui.html, Audit CSS positioning in othello.css, Check runtime toggles in othello.js]
Remaining: []
Next Action: Provide fix directive based on identified anchors

# UI Forensic Audit: Mobile PWA Keyboard Shift

## 1. Viewport Sizing Usage
**File:** [static/othello.css](static/othello.css#L64)
The root containers rely on `height: 100%`, which falls back to the **layout viewport** (covering the area under the keyboard on some devices) rather than the **visual viewport**.
```css
html {
  height: 100%;
  overflow: hidden; /* Root scroll lock */
}
body {
  height: 100%;
  overflow: hidden;
  position: fixed; /* Fixes body to viewport */
  top: 0; left: 0;
}
.shell {
  height: 100%; /* Inherits fixed height */
}
```

## 2. Scroll Ownership
**File:** [static/othello.css](static/othello.css#L960)
Scrolling is correctly delegated to internal views, not the body.
```css
.view {
  overflow-y: auto; /* Internal scroll */
  -webkit-overflow-scrolling: touch;
}
```
However, because `body` is `position: fixed` without `visualViewport` management, the browser pan-scrolls the entire fixed layer to keep the focused input visible when the keyboard creates an inset.

## 3. Fixed/Sticky Elements
**File:** [static/othello.js](static/othello.js) (Logic Check)
The `nav.tab-bar` and `header` are flex children of `.shell`. They are **not** sticky. They only stay at the top because `.shell` fills the screen. When the browser shifts the viewport, they shift with it.
The input bar (in the chat sheet) is relative to the sheet.

## 4. Keyboard Handling Check
**File:** [static/othello.js](static/othello.js)
- **visualViewport:** `0` matches found. The app is unaware of the keyboard geometry.
- **Input Blur:** `0` matches for explicit `blur()` calls on the chat input. The keyboard likely stays open after send, compounding layout issues.

## 5. Root Cause Analysis
**PRIMARY CAUSE:** The app relies on CSS `height: 100%` and `position: fixed` on the body without listening to the `visualViewport` API; thus, when the keyboard opens, the browser scrolls the entire fixed `body` upwards to ensure the input is visible, pushing the top bar off-screen.

## 6. Fix Direction
To stabilize the layout:
1.  **Dynamic Sizing:** Bind `window.visualViewport` events to set a CSS variable `--app-height`.
2.  **Constraint:** Set `body` (or `.shell`) height to `var(--app-height)` so it resizes *instead* of shifting.
3.  **Keyboard Inset:** Calculate `--keyboard-inset` to translate bottom bars up if needed (though resizing the shell usually suffices for flex layouts).
4.  **UX Polish:** Blur the input on send (optional, but requested behavior is usually to keep keyboard for rapid fire, but stable layout is the priority).

