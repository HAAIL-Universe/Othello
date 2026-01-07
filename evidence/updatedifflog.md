Cycle Status: COMPLETE (AUDIT)
Todo Ledger:
Planned: [Fix Focus user-bubble obstruction, Reflow bot padding]
Completed: [Impl "Peek" logic in othello.js, Add debugDuetDOM helper, CSS transforms for .duet-user-peek, Fix #duet-top padding]
Remaining: []
Next Action: Manual Verify of "Transform Peek" behavior.

# UI Forensic Audit: Focus View "Peek" & Padding

## 1. Problem Statement
The "Focus View" (Duet Mode) had two issues:
1. Long bot messages touched the top edge (clipping/no padding).
2. Long user messages obscured the bot text.
**Requirement:** 
- Slide user bubble out of the way ("Peek") when bot text is long.
- Use `transform` only, no new UI widgets.
- Fix top padding for bot messages.

## 2. DOM Proof Strategy
**Anchor Points:**
- Bot Container: `#duet-top`
- User Container: `#duet-bottom`
- Peek State Class: `.duet-user-peek`

**Verification Tool:**
`window.DEBUG_DUET = true` enables console logging of computed styles and DOM paths for the active bubbles to verify selectors before applying fixes.

## 3. Implementation Details

### A. Bot Padding Fix
**File:** [static/othello.css](static/othello.css)
Moved padding from individual bubbles to the scroll container to ensure consistent scroll-top behavior.
```css
#duet-top {
  padding-top: 1rem;
  padding-bottom: 2rem;
  overflow-y: auto;
}
#duet-top .bubble:first-child {
  margin-top: 0; /* Reset bubble margins to respect container padding */
}
```

### B. User "Peek" Transform
**File:** [static/othello.css](static/othello.css)
Configured the `#duet-bottom` container to slide right, leaving a 22px "handle" visible.
Key fix involved `width: fit-content` and `max-width` to ensure `translateX(100%)` calculated based on the bubble size, not the full screen width.
```css
#duet-bottom.duet-user-peek {
  max-width: 80% !important;
  width: fit-content;
  transform: translateX(calc(100% - 22px));
  position: absolute;
  bottom: 80px;
  right: 0;
  cursor: pointer;
}
```

### C. Trigger Logic
**File:** [static/othello.js](static/othello.js)
Updated `updateFocusPeekBehavior` to detect if bot content exceeds 45% of the viewport.
```javascript
const threshold = sheetHeight * 0.45;
if (botHeight > threshold) {
  duetBottom.classList.add("duet-user-peek");
}
```

## 4. Verification Check
**Status:** Ready to Verify
**Procedure:**
1. Open Focus View.
2. Send a long message to generate a long bot response.
3. Observe User bubble sliding right (leaving sliver).
4. Verify Bot text has top padding.
5. Click User sliver -> Check it slides back.
