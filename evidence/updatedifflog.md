# Cycle Status: COMPLETE (Phase 19)

## Todo Ledger
Planned:
- [x] Phase 19: Fix LLMWrapper mismatch & bundle voice/UI improvements.
Completed:
- [x] Fix: Added `chat_completion` adapter to `LLMWrapper`.
- [x] Feat: Auto-generate steps after clarification/intent update.
- [x] Feat: Map intent to `body` in LLM prompts.
- [x] Feat: Show pending drafts in GOALS tab (API & UI).
- [x] Feat: Step edit diff formatting.
Remaining:
- [ ] Next phase tasks...

## Next Action
Stop and commit.

## Full Unified Diff
```diff
diff --git a/api.py b/api.py
index 48ec1058..0428e013 100644
--- a/api.py
+++ b/api.py
@@ -1208,6 +1208,8 @@ def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction:
         "You are a goal editing engine. Update the existing goal draft JSON based on the user's instruction.\n"
         "Return the FULL updated JSON object with keys: title, target_days, steps, body.\n"
         "Do not lose existing information unless instructed to change it.\n"
+        "Crucial: If the user provides details, answers, or context (e.g., 'It is for my health'), update the 'body' string with this intent info.\n"
+        "Do NOT set step 1 unless explicitly asked to add a step.\n"
         "Return ONLY valid JSON."
     )
 
@@ -4395,19 +4397,61 @@ def handle_message():
                     # 1. Try deterministic edit
                     updated_payload, handled, reply_suffix = _apply_goal_draft_deterministic_edit(current_payload, user_input)
                     
-                    # 2. Fallback to LLM if not handled
+                    # Diff Logic (Step Diff)
+                    diff_meta = {}
+                    before_steps = current_payload.get("steps", []) or []
+                    after_steps = updated_payload.get("steps", []) or []
+                    
+                    if len(before_steps) != len(after_steps) or before_steps != after_steps:
+                        # Simple diff detection
+                        diff_meta["goal_title"] = updated_payload.get("title", "Goal")
+                        # Try to find specific index change
+                        if len(before_steps) == len(after_steps):
+                            for i, (b, a) in enumerate(zip(before_steps, after_steps)):
+                                if b != a:
+                                    diff_meta["step_index"] = i + 1
+                                    diff_meta["before_text"] = b
+                                    diff_meta["after_text"] = a
+                                    break
+
+                    # 2. Fallback to LLM if not handled (Semantic Edit)
                     if not handled:
                         updated_payload = _patch_goal_draft_payload(current_payload, user_input)
                         reply_suffix = "Updated the draft."
+                        
+                        # Auto-Generate Logic (Voice Flow)
+                        # If description likely changed (not just steps), and steps are empty, auto-generate.
+                        # Heuristic: If we are here, user said something that wasn't a command.
+                        # If steps are empty, assuming it's an elaboration/answer.
+                        if not updated_payload.get("steps"):
+                             # Check if body changed, or just safe assumption: if 0 steps, generate.
+                             # But avoid generating if user just said "No".
+                             # Let's assume meaningful update if body length > 5
+                             new_body = updated_payload.get("body") or ""
+                             if len(new_body) > 5:
+                                 updated_payload = _generate_draft_steps_payload(updated_payload)
+                                 steps_count = len(updated_payload.get("steps", []))
+                                 if steps_count > 0:
+                                     reply_suffix += f" I've also auto-generated {steps_count} starting steps for you."
                     
                     # Update DB
                     updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                     
                     title = updated_payload.get("title", "Goal")
                     steps_count = len(updated_payload.get("steps", []))
                     
+                    # Format Response with Diff
+                    reply_msg = f"{reply_suffix}"
+                    if diff_meta:
+                        reply_msg = f"{diff_meta['goal_title']}\nUpdated step {diff_meta['step_index']}\nBefore: {diff_meta['before_text']}\nAfter: {diff_meta['after_text']}"
+                    elif not reply_msg.strip():
+                         reply_msg = f"Draft: '{title}' ({steps_count} steps)."
+                    else:
+                         # Append summary if not a diff
+                         reply_msg += f" Draft: '{title}' ({steps_count} steps)."
+
                     response = {
-                        "reply": f"{reply_suffix} Draft: '{title}' ({steps_count} steps).",
+                        "reply": reply_msg,
                         "draft_context": {
                             "draft_id": draft_id,
                             "draft_type": "goal",
diff --git a/core/llm_wrapper.py b/core/llm_wrapper.py
index 244ddf58..1be10da6 100644
--- a/core/llm_wrapper.py
+++ b/core/llm_wrapper.py
@@ -60,6 +60,13 @@ class LLMWrapper:
             with open(model_cache_path, "w") as f:
                 f.write(self.model)
 
+    def chat_completion(self, *args, **kwargs):
+        """
+        Adapter method to call current OpenAI client chat completions directly.
+        Fixes compatibility issues where code uses .chat_completion instead of .client.chat.completions.create.
+        """
+        return self.client.chat.completions.create(*args, **kwargs)
+
     def generate(
         self,
         prompt: str,
diff --git a/db/db_goal_manager.py b/db/db_goal_manager.py
index 15fc7863..356f2463 100644
--- a/db/db_goal_manager.py
+++ b/db/db_goal_manager.py
@@ -18,7 +18,7 @@ from typing import List, Optional, Dict, Any, Union
 from datetime import datetime
 import logging
 
-from db import goals_repository
+from db import goals_repository, suggestions_repository
 from db.database import execute_and_fetch_one
 
 
@@ -237,14 +237,39 @@ class DbGoalManager:
 
     def list_goals(self, user_id: str) -> List[Dict[str, Any]]:
         """
-        Return all goals for the default user in legacy format.
+        Return all goals for the default user in legacy format, PLUS pending drafts.
         """
         uid = self._require_user_id(user_id)
+        
+        # 1. Fetch real goals
         db_goals = goals_repository.list_goals(uid, include_archived=False)
-        return [
+        goals = [
             self._db_to_legacy_format(uid, g, include_conversation=False)
             for g in db_goals
         ]
+        
+        # 2. Fetch pending goal drafts
+        drafts = suggestions_repository.list_suggestions(
+            user_id=uid, status="pending", kind="goal"
+        )
+        
+        draft_entries = []
+        for d in drafts:
+            payload = d.get("payload") or {}
+            # Ensure it looks like a goal so the UI renders it
+            # We prefix ID with 'draft:' so UI can distinguish action clicks
+            draft_entries.append({
+                "id": f"draft:{d['id']}",
+                "text": payload.get("title") or "New Draft",
+                "deadline": f"{payload.get('target_days', 7)} days",
+                "created_at": d.get("created_at").isoformat(),
+                "draft_text": payload.get("body"), # Show body as draft text
+                "checklist": payload.get("steps", []),
+                "is_draft": True,
+                "real_draft_id": d["id"]
+            })
+            
+        return draft_entries + goals
 
     def get_goal(
         self,
diff --git a/evidence/updatedifflog.md b/evidence/updatedifflog.md
index a8790477..c21fd2bd 100644
--- a/evidence/updatedifflog.md
+++ b/evidence/updatedifflog.md
@@ -1,22 +1,19 @@
-# Cycle Status: COMPLETE (Phase 18)
+# Cycle Status: COMPLETE (Phase 19)
 
 ## Todo Ledger
 Planned:
-- [x] Phase 18: Intent clarification + focus context + show seed steps bundle
+- [x] Phase 19: Fix LLMWrapper mismatch & bundle voice/UI improvements.
 Completed:
-- [x] Phase 18: Implemented 'Show Seed Steps' API lane.
-- [x] Phase 18: Injected Seed Steps into LLM Context (build_goal_context).
-- [x] Phase 18: Added 'Clarify Intent' button (static/othello.js).
+- [x] Fix: Added chat_completion adapter to LLMWrapper.
+- [x] Feat: Auto-generate steps after clarification/intent update.
+- [x] Feat: Map intent to body in LLM prompts.
+- [x] Feat: Show pending drafts in GOALS tab (API & UI).
+- [x] Feat: Step edit diff formatting.
 Remaining:
 - [ ] Next phase tasks...
 
 ## Next Action
-Stop and commit refactor/ui-consolidation.
+Stop and commit.
 
-## Phase 18 Summary
-Features delivered:
-1. **Show Seed Steps**: Direct API access to goal checklist without LLM latency.
-2. **Focus Context**: Active goals now expose their seed steps to the planner LLM automatically.
-3. **Intent Clarification**: One-click prompt injection to ask clarifying questions.
-
-Files modified: api.py, db/db_goal_manager.py, static/othello.js.
+## Full Unified Diff
+(See git show for details)
diff --git a/static/othello.js b/static/othello.js
index 4b6ec131..8d150d5b 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -6477,24 +6477,41 @@
       othelloState.goals.forEach(goal => {
         const card = document.createElement("div");
         card.className = "goal-card";
+        if (goal.is_draft) {
+             card.classList.add("goal-card--draft");
+        }
         
         const isActive = goal.id === othelloState.activeGoalId;
         const updateCount = othelloState.goalUpdateCounts[goal.id] || 0;
 
+        let badge = "";
+        if (goal.is_draft) {
+             badge = '<div class="goal-card__badge" style="background:var(--accent-color);color:#000;">Draft</div>';
+        } else if (isActive) {
+             badge = '<div class="goal-card__badge">Active</div>';
+        }
+
         card.innerHTML = \`
           <div class="goal-card__header">
             <div>
-              <div class="goal-card__id">Goal #${goal.id}</div>
-              <div class="goal-card__title">${formatMessageText(goal.text || "Untitled Goal")}</div>
+              <div class="goal-card__id">${goal.is_draft ? 'Draft' : 'Goal #' + goal.id}</div>
+              <div class="goal-card__title">${formatMessageText(goal.text || "Untitled")}</div>
             </div>
-            ${isActive ? '<div class="goal-card__badge">Active</div>' : ''}
+            ${badge}
           </div>
-          ${goal.deadline ? \`<div class="goal-card__meta">Deadline: ${formatMessageText(goal.deadline)}</div>\` : ''}
+          ${goal.deadline ? \`<div class="goal-card__meta">Target: ${formatMessageText(goal.deadline)}</div>\` : ''}
+          ${goal.is_draft ? \`<div class="goal-card__meta">Seed Steps: ${(goal.checklist||[]).length}</div>\` : ''}
           ${updateCount > 0 ? \`<div class="goal-card__meta">${updateCount} update${updateCount !== 1 ? 's' : ''} this session</div>\` : ''}
         \`;
 
         card.addEventListener("click", () => {
-          showGoalDetail(goal.id);
+          if (goal.is_draft) {
+              // Open draft ribbon context directly? 
+              // Better: Show detail panel with draft info.
+              showGoalDetail(goal.id); 
+          } else {
+              showGoalDetail(goal.id);
+          }
         });
 
         goalsList.appendChild(card);
@@ -6820,7 +6837,57 @@
       othelloState.currentDetailGoalId = goalId;
 
       if (goal) {
-        renderGoalDetail(goal);
+        if (goal.is_draft) {
+             // Render Draft Detail
+             detailGoalId.textContent = "Draft";
+             detailGoalTitle.innerHTML = formatMessageText(goal.text || "New Draft");
+             let contentHtml = "";
+
+             // Intent/Body
+             if (goal.draft_text) {
+                contentHtml += \`
+                  <div class="detail-section">
+                    <div class="detail-section__title">Description / Intent</div>
+                    <div class="detail-section__body" style="white-space: pre-wrap;">${formatMessageText(goal.draft_text)}</div>
+                  </div>
+                  <div class="detail-actions" style="padding: 0 16px 16px 16px;">
+                    <button class="action-btn clarify-intent-btn" data-goal-id="${goal.id}" style="font-size: 0.9em; padding: 6px 12px; border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
+                       <span class="codicon codicon-question"></span> Clarify Intent
+                    </button>
+                  </div>
+                \`;
+             }
+
+             // Steps
+             if (goal.checklist && goal.checklist.length > 0) {
+                 const stepsHtml = goal.checklist.map((step, idx) => {
+                    return \`<div class="intent-item"><div class="intent-item__text">${idx + 1}. ${formatMessageText(step)}</div></div>\`;
+                 }).join("");
+                  contentHtml += \`
+                  <div class="detail-section">
+                    <div class="detail-section__title">Draft Steps</div>
+                    <div class="intent-list">${stepsHtml}</div>
+                  </div>\`;
+             } else {
+                 contentHtml += \`<div class="detail-section"><div class="detail-section__body" style="font-style:italic; opacity:0.7;">No steps generated yet. Use chat to "generate steps".</div></div>\`;
+             }
+             
+             // Actions (Confirm/Dismiss wrappers handled by chat usually, but we can add buttons here if needed)
+             // Using data-draft-id for actions
+             const realId = goal.real_draft_id;
+             contentHtml += \`
+               <div class="detail-section" style="margin-top:20px; border-top:1px solid var(--border-color); padding-top:10px;">
+                  <div style="display:flex; gap:10px;">
+                      <button onclick="sendMessage('', {ui_action:'confirm_draft', draft_id:${realId}})" class="commitment-btn">Confirm Goal</button>
+                      <button onclick="sendMessage('', {ui_action:'dismiss_draft', draft_id:${realId}})" style="background:var(--bg-secondary); border:1px solid var(--border-color); color:var(--text-color); padding:8px 16px; border-radius:4px; cursor:pointer;">Dismiss</button>
+                  </div>
+               </div>
+             \`;
+
+             detailContent.innerHTML = contentHtml;
+        } else {
+             renderGoalDetail(goal);
+        }
       } else {
         detailGoalId.textContent = \`Goal #${goalId}\`;
         detailGoalTitle.textContent = "Loading...";
@@ -6832,7 +6899,10 @@
       }
 
       goalDetail.classList.add("visible");
-      fetchGoalDetail(goalId);
+      // Only fetch if it's a real goal, otherwise we have data in memory
+      if (!goal || !goal.is_draft) {
+          fetchGoalDetail(goalId);
+      }
     }
 
     async function archiveGoal(goalId) {
@@ -6970,9 +7040,21 @@
 
         const clarifyBtn = e.target.closest(".clarify-intent-btn");
         if (clarifyBtn) {
-            const goalId = clarifyBtn.getAttribute("data-goal-id");
+            let goalId = clarifyBtn.getAttribute("data-goal-id");
             if (!goalId) return;
             
+            // Handle draft IDs (e.g. "draft:123")
+            if (goalId.startsWith("draft:")) {
+                 // For drafts, we want to simply trigger the clarification intent without a goal_id context?
+                 // Or pass the draft_id.
+                 // ui_action "clarify_goal_intent" in api.py just sets prompt text.
+                 // It relies on current context.
+                 // If we are looking at a draft, we should probably just send the text.
+                 hideGoalDetail();
+                 sendMessage("", { ui_action: "clarify_goal_intent" }); 
+                 return;
+            }
+
             // Phase 18: Clarify Intent Action
             hideGoalDetail(); // Close detail to show chat
             sendMessage("", { ui_action: "clarify_goal_intent", goal_id: goalId });
```
