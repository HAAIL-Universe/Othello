# EVIDENCE REPORT: Fix markdown bold rendering in Goals UI

## Cycle Status
STOPPED:ENVIRONMENT_LIMITATION

## Todo Ledger
- [x] Phase 1: Single-source markdown formatter (Reused formatMessageText)
- [x] Phase 2: Apply formatting to Goals UI (Goals List, Detail Header, Intent, Activity Log)
- [x] Phase 3: Toast helper verification (Verified showToast exists)
- [ ] Phase 4: Runtime Verification (Visual check of bold rendering) - BLOCKED

## Next Action
Run manual verification checklist.

## Manual Verification Checklist
1. Chat: send a message containing `**bold**` and confirm it renders bold (no asterisks).
2. Goals list: open Goals tab and confirm entries like `**Deadline:**` render as bold “Deadline:” (no asterisks).
3. Goal detail: open a goal; in “INTENT” section confirm lines render bold correctly.
4. Save command sanity: type “save as long-term goal” and confirm:
   - no chat bubble is added for the command phrase
   - toast shows feedback
   - no console errors (especially showToast undefined)

## FULL unified diff patch
```diff
diff --git a/static/othello.js b/static/othello.js
index 85088ed6..xxxxxx 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -6030,11 +6030,11 @@
         card.innerHTML = `
           <div class="goal-card__header">
             <div>
               <div class="goal-card__id">Goal #${goal.id}</div>
-              <div class="goal-card__title">${goal.text || "Untitled Goal"}</div>
+              <div class="goal-card__title">${formatMessageText(goal.text || "Untitled Goal")}</div>
             </div>
             ${isActive ? '<div class="goal-card__badge">Active</div>' : ''}
           </div>
-          ${goal.deadline ? `<div class="goal-card__meta">Deadline: ${goal.deadline}</div>` : ''}
+          ${goal.deadline ? `<div class="goal-card__meta">Deadline: ${formatMessageText(goal.deadline)}</div>` : ''}
           ${updateCount > 0 ? `<div class="goal-card__meta">${updateCount} update${updateCount !== 1 ? 's' : ''} this session</div>` : ''}
         `;
 
@@ -6075,7 +6075,7 @@
     function renderGoalDetail(goal) {
       if (!goal) return;
       detailGoalId.textContent = `Goal #${goal.id}`;
-      detailGoalTitle.textContent = goal.text || "Untitled Goal";
+      detailGoalTitle.innerHTML = formatMessageText(goal.text || "Untitled Goal");
 
       // Build detail content
       let contentHtml = "";
@@ -6103,7 +6103,7 @@
         const itemsHtml = intentItems.map((item, idx) => {
           const itemIndex = Number.isFinite(item.index) ? item.index : (idx + 1);
           const itemText = item.text || "";
-          const safeText = escapeHtml(itemText);
+          const safeText = formatMessageText(itemText);
           const planBtn = `
             <button class="commitment-btn intent-plan-btn" data-intent-index="${itemIndex}" data-intent-text="${encodeURIComponent(itemText)}" data-goal-id="${goalIdNum || ""}">
               Build plan
@@ -6121,7 +6121,7 @@
         contentHtml += `
           <div class="detail-section">
             <div class="detail-section__title">Intent</div>
-            <div class="detail-section__body">${escapeHtml(intentText)}</div>
+            <div class="detail-section__body">${formatMessageText(intentText)}</div>
           </div>
         `;
       }
@@ -6156,8 +6156,8 @@
             : "";
           contentHtml += `
             <div class="activity-item">
               <div class="activity-item__role">${escapeHtml(role)}</div>
-              <div class="activity-item__text">${escapeHtml(entry.content || "")}</div>
+              <div class="activity-item__text">${formatMessageText(entry.content || "")}</div>
               ${planBtn}
             </div>
           `;
```
