Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Find goal plan UI placeholder + plan persistence infra; reuse goal_plan suggestion accept for append; wire UI confirm flow; add idempotence guard; update evidence log
Completed: Located Current Plan placeholder + plan_steps storage; confirmed plan_from_text/intents return pending_suggestion_id; implemented UI auto-confirm for plan suggestions; added accept idempotence guard; ran static compile
Remaining: Runtime verification pending deploy; report PASS/FAIL + screenshot/console
Next Action: Deploy and run runtime checklist; report PASS/FAIL + screenshot/console.
Commit: 833cd092 (branch ux/routine-clarify-panel-pending)

Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; othello_ui.html; api.py; db/db_goal_manager.py; db/goals_repository.py; db/database.py
Root-Cause Classification: UI not confirming goal plan suggestions (pending_suggestion_id never accepted)
Schema Choice: Reuse existing plan_steps table + goal_plan suggestion accept flow (no new tables/migrations; confirm-gated).
Root-Cause Anchors:
- othello_ui.html:7799 (Current Plan placeholder shows when plan_steps empty)
- othello_ui.html:7139 (Add to Current Plan calls plan_from_text_append without confirm)
- api.py:4924 (plan_from_text_append returns pending_suggestion_id)
- api.py:2211 (goal_plan accept path persists steps)
Anchors:
- api.py:2109 (idempotence guard for already-decided suggestions)
- othello_ui.html:7140 (confirmGoalPlanSuggestion)
- othello_ui.html:7164 (postPlanFromText auto-confirm)
- othello_ui.html:7208 (postPlanFromIntent auto-confirm + reply tweak)
Verification:
- Static: python -m py_compile api.py core/conversation_parser.py db/*.py (PASS)
- Runtime: PENDING (deploy-required)
  1) Focus a goal, receive step list, click Add to Current Plan -> steps persisted; goal detail shows plan steps.
  2) Use intent plan button -> steps appended; chat reply ends with Saved to Current Plan.
  3) Reload page -> Current Plan still shows steps.
  4) Re-click Add to Current Plan on same suggestion -> no duplicate steps (idempotent accept).
  5) No console errors in goal detail view.

diff --git a/api.py b/api.py
index 4269bc7e..21b2eceb 100644
--- a/api.py
+++ b/api.py
@@ -2109,6 +2109,15 @@ def _apply_suggestion_decisions(
 
         kind = suggestion.get("kind")
         payload = suggestion.get("payload") or {}
+        status = (suggestion.get("status") or "").strip().lower()
+        if action == "accept" and status and status != "pending":
+            results.append({
+                "ok": True,
+                "action": "noop",
+                "suggestion": suggestion,
+                "reason": "already_decided",
+            })
+            continue
 
         if action == "reject":
             updated = update_suggestion_status(user_id, suggestion_id, "rejected", decided_reason=reason)
             if kind == "goal_plan":
                 goal_id = payload.get("goal_id")
diff --git a/othello_ui.html b/othello_ui.html
index 11b0a710..0590cb20 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -7137,6 +7137,30 @@
       return fallback ? [{ index: 1, text: fallback }] : [];
     }
 
+    async function confirmGoalPlanSuggestion(suggestionId) {
+      if (!suggestionId) return null;
+      const payload = await v1Request(
+        `/v1/suggestions/${suggestionId}/accept`,
+        {
+          method: "POST",
+          headers: { "Content-Type": "application/json" },
+          credentials: "include",
+          body: JSON.stringify({ reason: "confirm" })
+        },
+        "Confirm goal plan"
+      );
+      const results = payload && payload.data && Array.isArray(payload.data.results)
+        ? payload.data.results
+        : [];
+      const result = results[0] || null;
+      if (result && result.ok === false) {
+        const err = new Error(result.error || "Failed to confirm plan.");
+        err.requestId = payload && payload.request_id ? payload.request_id : null;
+        throw err;
+      }
+      return result;
+    }
+
     async function postPlanFromText(planText) {
       const goalId = othelloState.activeGoalId;
       if (goalId == null) throw new Error("No focused goal.");
       const res = await fetch(API, {
@@ -7170,7 +7194,15 @@
         }
         throw new Error(errMsg);
       }
-      return res.json();
+      const data = await res.json();
+      const pendingId = data && data.meta ? data.meta.pending_suggestion_id : null;
+      if (pendingId) {
+        await confirmGoalPlanSuggestion(pendingId);
+        data.meta = data.meta || {};
+        data.meta.intent = "plan_steps_added";
+        data.meta.confirmed_suggestion_id = pendingId;
+      }
+      return data;
     }
 
     async function postPlanFromIntent(goalId, intentIndex, intentText) {
@@ -7207,7 +7239,19 @@
         }
         throw new Error(errMsg);
       }
-      return res.json();
+      const data = await res.json();
+      const pendingId = data && data.meta ? data.meta.pending_suggestion_id : null;
+      if (pendingId) {
+        await confirmGoalPlanSuggestion(pendingId);
+        data.meta = data.meta || {};
+        data.meta.intent = "plan_steps_added";
+        data.meta.confirmed_suggestion_id = pendingId;
+        if (typeof data.reply === "string") {
+          const cleaned = data.reply.replace(/\n?\s*Confirm to apply these steps\.?\s*$/i, "").trim();
+          data.reply = cleaned ? `${cleaned}\n\nSaved to Current Plan.` : "Saved to Current Plan.";
+        }
+      }
+      return data;
     }
 
     function formatStepStatus(status) {
