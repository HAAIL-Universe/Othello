Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Phase 2 manual UI verification (DEPLOYED); Phase 3 commit checkpoint finalization
Completed: Phase 0 contract gate + workspace proof; Phase 1 collapse clarify panel on tap
Remaining: Phase 2 manual UI verification (DEPLOYED); Phase 3 commit checkpoint finalization
Next Action: Deploy this commit and run manual UI verification on deployed environment; report PASS/FAIL
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; othello_ui.html
Verification:
- Not run yet (deploy-based verification pending)

diff --git a/othello_ui.html b/othello_ui.html
index e48b2e3b..b00079e0 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6435,22 +6435,40 @@
       const actions = document.createElement("div");
       actions.className = "ux-goal-intent-panel__actions";
 
+      const collapseRoutineClarifyPanel = (chosenLabel) => {
+        if (!actions) return;
+        const status = document.createElement("div");
+        status.className = "ux-goal-intent-status";
+        status.textContent = `Sent: ${chosenLabel} - updating...`;
+        actions.innerHTML = "";
+        actions.appendChild(status);
+        window.setTimeout(() => {
+          if (panel && panel.parentNode) {
+            panel.style.display = "none";
+          }
+        }, 600);
+      };
+
       const amBtn = document.createElement("button");
       amBtn.className = "ux-goal-intent-btn secondary";
       amBtn.textContent = "7am";
       amBtn.addEventListener("click", () => {
+        const replyText = amBtn.dataset.reply || amBtn.textContent;
         amBtn.disabled = true;
         pmBtn.disabled = true;
-        sendQuickReply(amBtn.dataset.reply || amBtn.textContent);
+        collapseRoutineClarifyPanel(replyText);
+        sendQuickReply(replyText);
       });
 
       const pmBtn = document.createElement("button");
       pmBtn.className = "ux-goal-intent-btn secondary";
       pmBtn.textContent = "7pm";
       pmBtn.addEventListener("click", () => {
+        const replyText = pmBtn.dataset.reply || pmBtn.textContent;
         amBtn.disabled = true;
         pmBtn.disabled = true;
-        sendQuickReply(pmBtn.dataset.reply || pmBtn.textContent);
+        collapseRoutineClarifyPanel(replyText);
+        sendQuickReply(replyText);
       });
 
       const applyHourHint = (hour) => {
@@ -6735,9 +6753,20 @@
         }
 
         const data = await res.json();
-        const botEntry = addMessage("bot", data.reply || "[no reply]", { sourceClientMessageId: clientMessageId });
+        const meta = data && data.meta ? data.meta : null;
+        const isRoutineReady = !!(meta && meta.intent === "routine_ready" && meta.routine_suggestion_id);
+        let replyText = data.reply || "[no reply]";
+        if (isRoutineReady) {
+          replyText = " ";
+        }
+        const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId });
+        if (isRoutineReady && botEntry && botEntry.bubble && botEntry.bubble.firstChild) {
+          if (botEntry.bubble.firstChild.nodeType === 3) {
+            botEntry.bubble.firstChild.textContent = "";
+          }
+        }
         try {
-          await applyRoutineMeta(data.meta, botEntry);
+          await applyRoutineMeta(meta, botEntry);
         } catch (err) {
           console.warn("[Othello UI] routine meta render failed:", err);
         }
