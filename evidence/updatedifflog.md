Cycle Status: PHASE_3A_EVIDENCE_COMPLETE (STOP+COMMIT A)

Todo Ledger:
- Done: Phase 3A evidence bundle (duet rendering path, state maps, badge visibility)
- Next: Phase 3B minimal fix to register messages/enable badge in duet mode
- Next: Phase 3C verify badge visibility + click path

Evidence Bundle:

A1) Duet vs normal render path
- addMessage appends to getChatContainer (chat-log/history-log) and then updates duet view: static/othello.js:5312, static/othello.js:5393, static/othello.js:5400
- getChatContainer chooses #history-log if history panel open, else #chat-log: static/othello.js:4744
- updateDuetView defers to applyDuetPins: static/othello.js:4732
- applyDuetPins collects rows from duet-top/bottom/chat-log and moves last bot -> #duet-top, last user -> #duet-bottom, rest -> #chat-log: static/othello.js:4637, static/othello.js:4670, static/othello.js:4701

A2) Why state maps can be empty
- messagesByClientId initialized on othelloState: static/othello.js:862
- clearChatState wipes messagesByClientId and goalIntentSuggestions: static/othello.js:5033, static/othello.js:5070
- loadChatHistory clears state and renders history via addMessage with no clientMessageId: static/othello.js:5168, static/othello.js:5175, static/othello.js:5178
- addMessage only registers messagesByClientId for role="user" when clientMessageId provided: static/othello.js:5407
- updateSecondaryBadge attaches badge into .meta element: static/othello.js:5464
- addSecondarySuggestion only updates badge if entry exists in messagesByClientId: static/othello.js:5504, static/othello.js:5521
- build-mode suggestions mapped to bot entry when client_message_id == "current_bot_response": static/othello.js:7144, static/othello.js:7153

A3) Why badge has rectCount=0 (hidden by CSS)
- Badge is appended inside .meta; .meta is hidden in duet/chat contexts:
  - #duet-top .meta, #duet-bottom .meta, #chat-log .meta { display: none !important; }: static/othello.css:8132
  - #history-log .meta { display: block !important; }: static/othello.css:8144
- #chat-log is forced hidden in duet mode (so only duet panes show rows): static/othello.css:7022

Root-Cause Anchors:
- Badge inserted in .meta but .meta hidden in duet panes: static/othello.js:5464 + static/othello.css:8132
- Duet mode pins messages into #duet-top/#duet-bottom (chat-log hidden): static/othello.js:4637 + static/othello.css:7022

Minimal Diff Summary:
- No code changes in Phase 3A (evidence only).


Phase 3B Fix Implementation:
- Modified msg-row class handling in static/othello.js:updateSecondaryBadge to toggle 'has-secondary-badge' based on suggestion count.
- Added CSS override in static/othello.css to display .meta for rows with 'has-secondary-badge' in duet mode.
- Expected Result: The '?' badge should now be visible (non-zero rect) and clickable in duet mode.
