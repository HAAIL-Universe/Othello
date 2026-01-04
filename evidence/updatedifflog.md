Cycle Status: IN_PROGRESS
Todo Ledger:
Planned: Deploy + runtime verification; mark COMPLETE if PASS
Completed: Fix HH:MM AM/PM parsing; guard ordinal one-offs; static py_compile
Remaining: Runtime verification on deployed env + any hotfix if FAIL
Next Action: Deploy this commit and test AM/PM (6:00 PM -> 18:00) and ordinal one-off guard; report PASS/FAIL + screenshot/console.
Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; core/conversation_parser.py
Anchors:
- _parse_time_from_text: core/conversation_parser.py:196
- _extract_scheduled_routine: core/conversation_parser.py:307
- extract_routines: core/conversation_parser.py:331
Verification:
- Static: python -m py_compile core/conversation_parser.py api.py (pass)
- Runtime: Not run (pending deploy)

diff --git a/core/conversation_parser.py b/core/conversation_parser.py
index 801bafb3..e4ae01be 100644
--- a/core/conversation_parser.py
+++ b/core/conversation_parser.py
@@ -200,13 +200,32 @@ class ConversationParser:
         time_text: Optional[str] = None
         time_local: Optional[str] = None
 
-        match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lower)
+        match = re.search(
+            r"\b([01]?\d|2[0-3]):([0-5]\d)\s*(a\.?m\.?|p\.?m\.?)?\b",
+            lower,
+        )
         if match:
             hour = int(match.group(1))
             minute = int(match.group(2))
             time_text = match.group(0)
-            has_ampm = re.search(r"\b(a\.?m\.?|p\.?m\.?)\b", lower) is not None
+            ampm_raw = match.group(3)
+            has_ampm = ampm_raw is not None
             has_daypart = "morning" in lower or "evening" in lower
+            if has_ampm and 1 <= hour <= 12:
+                ampm_clean = ampm_raw.replace(".", "")
+                is_pm = ampm_clean.startswith("p")
+                if is_pm and hour != 12:
+                    hour += 12
+                if not is_pm and hour == 12:
+                    hour = 0
+                time_local = f"{hour:02d}:{minute:02d}"
+                time_text = time_text.replace(" ", "")
+                return {
+                    "time_text": time_text,
+                    "time_local": time_local,
+                    "missing_fields": missing_fields,
+                    "ambiguous_fields": ambiguous_fields,
+                }
             if 1 <= hour <= 11 and not has_ampm and not has_daypart:
                 # Prefer ambiguity for bare 7:00-style times so we don't persist until clarified.
                 missing_fields.append("time_ampm")
@@ -315,6 +334,13 @@ class ConversationParser:
         if not time_info.get("time_text") and not time_info.get("time_local"):
             return None
         days = self._extract_days_of_week(text)
+        has_ordinal_date = re.search(r"\b([1-9]|[12]\d|3[01])(st|nd|rd|th)\b", lower)
+        has_recurrence = bool(days) or re.search(
+            r"\b(every|daily|weekly|weekday|weekend|each|monthly|yearly|annually)\b",
+            lower,
+        ) is not None
+        if has_ordinal_date and not has_recurrence:
+            return None
         duration_minutes = self._parse_duration_minutes(text)
         return {
             "draft_type": "schedule",

