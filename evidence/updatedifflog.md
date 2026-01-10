Cycle Status: COMPLETE

Evidence:
- Phase 1: Confirmed 'duet-mode' class does not exist (grep failed). Confirmed Duet uses #duet-top/#duet-bottom via applyDuetPins.
- Phase 2: Replaced invalid CSS selector .duet-mode with #duet-top/#duet-bottom overrides.
- Phase 3: Verified backend wiring remains intact (ui_action returns draft_id 363). CSS syntax is correct.

Commit: Fix: show secondary ? badge in duet view (Case A)
