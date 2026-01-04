Cycle Status: COMPLETE
Todo Ledger:
Planned: Fix missing '?? Goal' intent marker on first bot reply; Adjust 'Is this a goal?' UX to use '?' icon for weak intents; Stop false goal-candidate suggestions for 'I want to ask a question'; Remove duplicate 'Goal suggestion' entries.
Completed: Updated detectUserGoalHint with strict regex; Added detectGoalCandidateStatement for weak intents; Updated updateSecondaryBadge to show '?' icon; Added hard negative guard in sendMessage for question intents; Added deduplication logic in addSecondarySuggestion.
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that 'I want to ask a question' does NOT show a goal suggestion, and 'I want to lose 10kg' shows a '?' icon.

diff --git a/othello_ui.html b/othello_ui.html
index 7bf87f8b..747e3bd6 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6068,7 +6068,8 @@

     function updateSecondaryBadge(entry) {
       if (!entry || !entry.clientMessageId || !entry.bubbleEl) return;
-      const count = getSecondarySuggestions(entry.clientMessageId).length;
+      const suggestions = getSecondarySuggestions(entry.clientMessageId);
+      const count = suggestions.length;
       const meta = entry.bubbleEl.querySelector('.meta');
       if (!meta) return;
       if (!count) {
@@ -6090,7 +6091,12 @@
         entry.secondaryBadgeEl = badge;
         meta.appendChild(badge);
       }
-      badge.textContent = \•\\;
+      
+      const hasGoal = suggestions.some(s => s.type === 'goal_intent');
+      badge.textContent = hasGoal ? '?' : \•\\;
+      badge.style.fontWeight = hasGoal ? 'bold' : 'normal';
+      badge.style.color = hasGoal ? 'var(--accent)' : 'inherit';
+
       if (entry.secondaryPanelEl && entry.secondaryPanelEl.style.display === 'flex') {
         renderSecondarySuggestionPanel(entry);
       }
@@ -6110,7 +6116,11 @@
       const suggestionId = suggestion.suggestion_id || suggestion.id || null;
       const key = suggestionId != null ? \\:\\ : \\:\\;
       const list = othelloState.secondarySuggestionsByClientId[clientMessageId] || [];
+      
       if (list.some((item) => item.key === key)) return false;
+      // Enforce one candidate per type per message
+      if (list.some((item) => item.type === normalizedType)) return false;
+
       list.push({ key, type: normalizedType, suggestionId, suggestion });
       othelloState.secondarySuggestionsByClientId[clientMessageId] = list;
       const entry = othelloState.messagesByClientId[clientMessageId];
@@ -6621,10 +6631,18 @@
       const raw = String(userText || '').trim();
       if (!raw) return false;
       const text = raw.toLowerCase();
+
+      // Hard negative guard: question intent must never trigger goal candidates
+      if (text.includes('question') || text.includes('?') || 
+          text.startsWith('i want to ask') || text.startsWith('i have a question') ||
+          text.startsWith('can i ask') || text.startsWith('could i ask')) {
+        return false;
+      }
+
       const tokens = text.split(/\\s+/).filter(Boolean);
       const explicitGoal = /(goal:|my goal is|i want to|i'm going to|im going to|i am going to|i will|new goal|i need to achieve|i'm working towards|im working towards)/.test(text);
       if (tokens.length <= 4 && !explicitGoal) return false;
-      if (raw.includes('?') || /^(what|why|how|when|where|who|can|should|do|is|are)\\b/.test(text)) {
+      if (/^(what|why|how|when|where|who|can|should|do|is|are)\\b/.test(text)) {
         return false;
       }
       const routineSignals = /\\b(every day|each day|daily|weekly|remind me|alarm|routine|habit|meet at)\\b/.test(text);
@@ -6649,18 +6667,9 @@
       const entryText = entry && typeof entry.text === 'string' ? entry.text : '';
       if (!shouldSuggestGoalDraft(entryText, normalizedSuggestion, othelloState)) return;
       if (isSuggestionDismissed(normalizedSuggestion.type, clientMessageId)) return;
-      const focusKind = getActiveFocusKind(othelloState);
-      if (focusKind && focusKind !== 'goal') {
-        addSecondarySuggestion(clientMessageId, normalizedSuggestion);
-        return;
-      }
-      othelloState.goalIntentSuggestions[clientMessageId] = normalizedSuggestion;
-      if (!entry || !entry.bubbleEl || !entry.rowEl) return;
-      if (entry.panelEl) return;
-      entry.bubbleEl.classList.add('ux-goal-intent');
-      const panel = buildGoalIntentPanel(normalizedSuggestion, entry);
-      entry.panelEl = panel;
-      entry.rowEl.appendChild(panel);
+      
+      // Always use secondary suggestion for goal intents (candidate flow)
+      addSecondarySuggestion(clientMessageId, normalizedSuggestion);
     }
 
     function applySuggestionMeta(meta) {
@@ -7213,7 +7222,10 @@
       const qWords = ['what', 'how', 'why', 'when', 'where', 'who', 'can', 'should', 'do', 'is', 'are'];
       if (qWords.some(w => t.startsWith(w + ' ') || t === w)) return false;
       
-      const signals = ['goal:', 'my goal is', 'new goal', 'i want to', 'i'm going to', 'i will', 'working towards'];
+      const signals = [
+        'goal', 'i have a goal', 'i need to create a goal', 'create a goal', 
+        'set a goal', 'new goal', 'my goal is', 'working towards'
+      ];
       return signals.some(s => t.includes(s));
     }
