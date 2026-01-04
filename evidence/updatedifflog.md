Cycle Status: COMPLETE
Todo Ledger:
Planned: Locate time ambiguity parsing + ambiguity generation; add cue guard for bare hours; add regression tests; update evidence log; run py_compile
Completed: Added time cue guard for bare hours; added regression tests for numeric counts/cued time/colon ambiguity; ran py_compile; runtime PASS
Remaining: None
Next Action: None

Paths Read: build_docs/theexecutor.md; build_docs/othello_blueprint.md; build_docs/othello_manifesto.md; build_docs/othello_directive.md; core/conversation_parser.py; tests/test_conversation_parser.py
Anchors:
- time cue guard + bare hour match: core/conversation_parser.py:196
- ambiguity generation for bare hours: core/conversation_parser.py:281
- tests for numeric count/cued hour/colon ambiguity: tests/test_conversation_parser.py:20
Verification:
- Static: python -m py_compile core/conversation_parser.py (PASS)
- Runtime: PASS
  1) "each day I log 3 priorities" -> no 3am/3pm clarification.
  2) "at 3" -> time ambiguity still present.
  3) "7:00" -> ambiguity preserved.
diff --git a/core/conversation_parser.py b/core/conversation_parser.py
index b229fa43..3d94b8e6 100644
--- a/core/conversation_parser.py
+++ b/core/conversation_parser.py
@@ -199,6 +199,15 @@ class ConversationParser:
         ambiguous_fields: List[str] = []
         time_text: Optional[str] = None
         time_local: Optional[str] = None
+        time_cues = {"at", "@", "around", "by"}
+        dayparts = ("morning", "afternoon", "evening", "tonight")
+
+        def _has_time_cue(prefix: str) -> bool:
+            tokens = re.findall(r"[@\\w]+", prefix)
+            for token in tokens[-2:]:
+                if token in time_cues:
+                    return True
+            return False
 
         match = re.search(
             r"\b([01]?\d|2[0-3]):([0-5]\d)\s*(a\.?m\.?|p\.?m\.?)?\b",
@@ -270,11 +279,15 @@ class ConversationParser:
             time_local = "19:00"
 
         if time_local is None:
-            match = re.search(r"\b([1-9]|1[0-2])\s*(?:o\W?clock)?\b", lower)
+            match = re.search(r"\b([1-9]|1[0-2])\s*(o\W?clock)?\b", lower)
             if match:
-                time_text = match.group(0).strip()
-                missing_fields.append("time_ampm")
-                ambiguous_fields.append("time_local")
+                has_oclock = match.group(2) is not None
+                has_daypart = any(daypart in lower for daypart in dayparts)
+                has_cue = _has_time_cue(lower[:match.start()])
+                if has_oclock or has_daypart or has_cue:
+                    time_text = match.group(0).strip()
+                    missing_fields.append("time_ampm")
+                    ambiguous_fields.append("time_local")
 
         return {
             "time_text": time_text,
diff --git a/tests/test_conversation_parser.py b/tests/test_conversation_parser.py
index 7d64ad19..67668862 100644
--- a/tests/test_conversation_parser.py
+++ b/tests/test_conversation_parser.py
@@ -21,6 +21,24 @@ class TestConversationParser(unittest.TestCase):
         routines = self.parser.extract_routines(text)
         self.assertTrue(any("wake up" in r["question"].lower() for r in routines))
 
+    def test_parse_time_ignores_numeric_counts(self):
+        info = self.parser._parse_time_from_text("each day I log 3 priorities.")
+        self.assertIsNone(info.get("time_text"))
+        self.assertIsNone(info.get("time_local"))
+        self.assertFalse(info.get("ambiguous_fields"))
+
+    def test_parse_time_accepts_cued_hour(self):
+        info = self.parser._parse_time_from_text("at 3")
+        self.assertEqual(info.get("time_text"), "3")
+        self.assertIn("time_ampm", info.get("missing_fields") or [])
+        self.assertIn("time_local", info.get("ambiguous_fields") or [])
+
+    def test_parse_time_keeps_colon_ambiguity(self):
+        info = self.parser._parse_time_from_text("meet at 7:00")
+        self.assertEqual(info.get("time_text"), "7:00")
+        self.assertIsNone(info.get("time_local"))
+        self.assertIn("time_local", info.get("ambiguous_fields") or [])
+
     def test_extract_traits_detects_trait(self):
         text = "I am compassionate and kind."
         traits = self.parser.extract_traits(text)
