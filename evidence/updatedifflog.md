# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Phase 6: Draft Focus Polish (Fix 400 error, Unfocus behavior, Bubble cleanup)

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
--- a/api.py
+++ b/api.py
@@ -3986,8 +3986,9 @@
         _log_request_start(raw_goal_id)
 
-        if not user_input:
+        # Allow empty message if ui_action is present (e.g. confirm_draft, dismiss_draft)
+        if not user_input and not ui_action:
             return api_error("VALIDATION_ERROR", "message is required", 400)
 
         logger.info("API: Received message: %s request_id=%s", user_input[:100], request_id)
 
         user_id, user_error = _get_user_id_or_error()

diff --git a/static/othello.js b/static/othello.js
--- a/static/othello.js
+++ b/static/othello.js
@@ -3854,6 +3854,17 @@
     async function unfocusGoal() {
+      // If we have an active draft, treat Unfocus as Dismiss Draft
+      if (othelloState.activeDraft) {
+          console.log("[Othello UI] Unfocus clicked while drafting -> Dismissing draft");
+          // Optimistic clear
+          othelloState.activeDraft = null;
+          localStorage.removeItem("othello_active_draft");
+          updateFocusRibbon();
+          
+          // Tell backend
+          await sendMessage("", { ui_action: "dismiss_draft" });
+          return;
+      }
+
       const hadFocus = othelloState.activeGoalId !== null;
       if (!hadFocus) return;
 
@@ -3902,6 +3913,11 @@
       othelloState.messagesByClientId = {};
       othelloState.goalIntentSuggestions = {};
+      
+      // Clear draft state on new chat/reset
+      othelloState.activeDraft = null;
+      localStorage.removeItem("othello_active_draft");
+      updateFocusRibbon();
     }
 
     function resetAuthBoundary(reason) {
@@ -5418,7 +5434,12 @@
 
       const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim(), isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
-      addMessage("user", text || (extraData.ui_action ? `[Action: ${extraData.ui_action}]` : ""), { metaNote, clientMessageId });
+      
+      // Only add user bubble if there is actual text
+      if (text) {
+          addMessage("user", text, { metaNote, clientMessageId });
+      } else if (extraData.ui_action) {
+          // No bubble for pure UI actions
+      }
+
       if (overrideText === null) {
           input.value = "";
           input.focus();
```

## Verification Results
- [x] Click Send with normal typed text containing capitals/punctuation → NO console error.
- [x] Press Enter to send (if supported) → NO console error.
- [x] Click Draft ribbon Confirm / Dismiss → works and NO console error.
- [x] Confirm that `/api/message` payload still includes draft fields and ui_action when used.
- [x] Confirm no regression: user can send multiple messages back-to-back.
- [x] Draft Focus: Click Dismiss → ribbon disappears, backend 200 (no 400), draft cleared.
- [x] Draft Focus: Click Unfocus → acts as Dismiss (clears draft).
- [x] Draft Focus: Click Confirm → backend 200, goal created, draft cleared.
- [x] UI Actions (Confirm/Dismiss) do NOT create fake user bubbles.
- [x] New Chat clears any stuck draft state.
