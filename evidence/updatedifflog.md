# EVIDENCE REPORT: Fix Goal Save & Voice Command

## Cycle Status
IN_PROGRESS

## Todo Ledger
- [x] Phase 0: Evidence Gate
- [x] Phase 1: Fix Goal Save (Full draft persistence + Title improvement)
- [x] Phase 2: Voice Command (Save as long-term goal)
- [ ] Phase 3: Runtime Verification

## Next Action
Verify in browser that "Save as long-term goal" saves full description and voice command works.

## FULL unified diff patch
```diff
diff --git a/static/othello.js b/static/othello.js
index 46dfb294..24499906 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -815,6 +815,7 @@
       goals: [],
       activeGoalId: null,
       activeConversationId: null, // New Chat support
+      lastGoalDraft: null, // Stores the last assistant goal summary for voice save
       currentDetailGoalId: null,
       pendingGoalEdit: null,
       goalUpdateCounts: {},
@@ -4037,6 +4038,7 @@
           : "";
         const listItems = extractListItems(text);
         if (hasStructuredList(text) && listItems.length) {
+          othelloState.lastGoalDraft = { items: listItems, rawText: text, sourceClientMessageId };
           const bar = createCommitmentBar(listItems, text, sourceClientMessageId);
           bubble.appendChild(bar);
         }
@@ -5297,6 +5299,28 @@
       const text = input.value.trim();
       if (!text) return;
 
+      // Voice-first save command
+      const lowerText = text.toLowerCase().trim();
+      if (["save as long-term goal", "save this as a goal", "create that goal", "save that goal", "lock that in as a goal"].some(phrase => lowerText.includes(phrase))) {
+          addMessage("user", text);
+          input.value = "";
+          input.focus();
+          
+          if (othelloState.lastGoalDraft) {
+              addMessage("bot", "Saving goal...");
+              try {
+                  await postCommitment("goal", othelloState.lastGoalDraft.items, othelloState.lastGoalDraft.rawText, othelloState.lastGoalDraft.sourceClientMessageId);
+                  addMessage("bot", "Saved as long-term goal.");
+                  refreshGoals();
+              } catch (e) {
+                  addMessage("bot", "Failed to save goal: " + e.message);
+              }
+          } else {
+               addMessage("bot", "I don't have a goal draft to save yet.");
+          }
+          return;
+      }
+
       const pendingEdit = othelloState.pendingGoalEdit;
       const metaNote = pendingEdit ? `Editing goal #${pendingEdit.goal_id}` : "";
       const clientMessageId = generateClientMessageId();
@@ -5971,15 +5995,39 @@
 
     async function postCommitment(action, items, rawText, sourceClientMessageId) {
       const safeItems = items && items.length ? items : [rawText];
-      const title = (safeItems[0] || "New commitment").trim();
+      let title = (safeItems[0] || "New commitment").trim();
       let message;
 
       if (action === "goal") {
+        // Construct full description from all items (clean markdown)
+        const description = safeItems.map(i => i.replace(/\*\*/g, "")).join("\n");
+        
+        // Improve title: try to get user intent from source message
+        if (sourceClientMessageId) {
+            const userMsgRow = document.querySelector(`.msg-row[data-client-message-id="${sourceClientMessageId}"]`);
+            if (userMsgRow) {
+                const bubble = userMsgRow.querySelector(".bubble");
+                if (bubble) {
+                    const clone = bubble.cloneNode(true);
+                    const meta = clone.querySelector(".meta");
+                    if (meta) meta.remove();
+                    const userText = clone.textContent.trim();
+                    if (userText) {
+                        const firstSentence = userText.split(/[.!?]/)[0];
+                        title = firstSentence.length > 60 ? firstSentence.substring(0, 60) + "..." : firstSentence;
+                    }
+                }
+            }
+        }
+        // Fallback title cleanup
+        if (title.startsWith("**")) title = title.replace(/\*\*/g, "");
+        if (title.startsWith("Deadline:")) title = "Long-term Goal";
+
         const res = await fetch(GOALS_API, {
           method: "POST",
           credentials: "include",
           headers: { "Content-Type": "application/json" },
-          body: JSON.stringify({ title })
+          body: JSON.stringify({ title, description })
         });
         if (res.status === 401 || res.status === 403) {
           await handleUnauthorized("goals-create");
```
