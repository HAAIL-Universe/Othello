Cycle Status: COMPLETE
Todo Ledger:
Planned: Fix plural weekday parsing; prevent weekday-only title; replace blank routine_ready bubble; verification; commit checkpoint
Completed: Added plural weekday detection; added weekday-only action fallback; updated routine_ready prompt; static + parser sanity verification
Remaining: None
Next Action: None
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; core/conversation_parser.py; othello_ui.html
Anchors:
- _extract_days_of_week: core/conversation_parser.py:166
- _extract_routine_action: core/conversation_parser.py:296
- _extract_scheduled_routine: core/conversation_parser.py:367
- routine_ready reply handling: othello_ui.html:6757
Verification:
- Static: python -m py_compile core/conversation_parser.py (pass)
- Runtime:
  - python - <<'PY' (extract_routines) -> title "Feed the cat", days ['fri'], time_local '18:00'
  - python - <<'PY' (_parse_time_from_text) -> missing_fields ['time_ampm'], ambiguous_fields ['time_local']

diff --git a/core/conversation_parser.py b/core/conversation_parser.py
index e4ae01be..b229fa43 100644
--- a/core/conversation_parser.py
+++ b/core/conversation_parser.py
@@ -173,13 +173,13 @@ class ConversationParser:
         if "weekend" in lower:
             days.extend(["sat", "sun"])
         day_patterns = [
-            ("mon", r"\bmon(day)?\b"),
-            ("tue", r"\btue(sday)?\b"),
-            ("wed", r"\bwed(nesday)?\b"),
-            ("thu", r"\bthu(rsday)?\b"),
-            ("fri", r"\bfri(day)?\b"),
-            ("sat", r"\bsat(urday)?\b"),
-            ("sun", r"\bsun(day)?\b"),
+            ("mon", r"\bmon(day)?s?\b"),
+            ("tue", r"\btue(sday)?s?\b"),
+            ("wed", r"\bwed(nesday)?s?\b"),
+            ("thu", r"\bthu(rsday)?s?\b"),
+            ("fri", r"\bfri(day)?s?\b"),
+            ("sat", r"\bsat(urday)?s?\b"),
+            ("sun", r"\bsun(day)?s?\b"),
         ]
         for day_key, pattern in day_patterns:
             if re.search(pattern, lower):
@@ -321,7 +321,48 @@ class ConversationParser:
                 if cue_match:
                     candidate = candidate[:cue_match.start()].strip()
                 action = candidate.strip()
-        return action.rstrip(".").strip()
+        action = action.rstrip(".").strip()
+        if action:
+            weekday_only = re.fullmatch(
+                r"(mon(day)?|tue(sday)?|wed(nesday)?|thu(rsday)?|fri(day)?|sat(urday)?|sun(day)?)(s)?",
+                action.lower(),
+            ) is not None
+            if weekday_only:
+                fallback = None
+                sentences = re.split(r"[.!?]+", cleaned)
+                for sentence in sentences:
+                    candidate = sentence.strip()
+                    if not candidate:
+                        continue
+                    if "routine" in candidate.lower():
+                        continue
+                    need_match = re.search(
+                        r"\bneed to\b\s+([^.;\n]+)",
+                        candidate,
+                        flags=re.IGNORECASE,
+                    )
+                    if need_match:
+                        fallback = need_match.group(1).strip()
+                    else:
+                        to_match = re.search(
+                            r"\bto\b\s+([^.;\n]+)",
+                            candidate,
+                            flags=re.IGNORECASE,
+                        )
+                        if to_match:
+                            fallback = to_match.group(1).strip()
+                    if fallback:
+                        break
+                if fallback:
+                    fallback = re.sub(
+                        r"\s+at\s+\d{1,2}(?::\d{2})?\s*(a\.?m\.?|p\.?m\.?)?$",
+                        "",
+                        fallback,
+                        flags=re.IGNORECASE,
+                    ).strip()
+                    if fallback:
+                        action = fallback
+        return action
 
     def _extract_scheduled_routine(self, text: str) -> Optional[Dict[str, Any]]:
         lower = (text or "").lower()
diff --git a/othello_ui.html b/othello_ui.html
index b00079e0..a7c88e21 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -6757,14 +6757,9 @@
         const isRoutineReady = !!(meta && meta.intent === "routine_ready" && meta.routine_suggestion_id);
         let replyText = data.reply || "[no reply]";
         if (isRoutineReady) {
-          replyText = " ";
+          replyText = "Confirm this routine?";
         }
         const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId });
-        if (isRoutineReady && botEntry && botEntry.bubble && botEntry.bubble.firstChild) {
-          if (botEntry.bubble.firstChild.nodeType === 3) {
-            botEntry.bubble.firstChild.textContent = "";
-          }
-        }
         try {
           await applyRoutineMeta(meta, botEntry);
         } catch (err) {

--- EOF Phase 5 ---
