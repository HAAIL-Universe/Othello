import unittest
from core.conversation_parser import ConversationParser

class TestConversationParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConversationParser()

    def test_extract_goals_detects_strong_goal(self):
        text = "I want to finish my project by Friday."
        goals = self.parser.extract_goals(text)
        self.assertTrue(any("want to" in g["source_phrase"] for g in goals))
        self.assertTrue(any("by friday" in (g["deadline"] or "").lower() for g in goals))

    def test_extract_goals_detects_progress_pattern(self):
        text = "I made progress on my goal of learning Python."
        goals = self.parser.extract_goals(text)
        self.assertTrue(any("progress-pattern" == g["source_phrase"] for g in goals))

    def test_extract_routines_detects_wake_up(self):
        text = "I woke up at 7 today."
        routines = self.parser.extract_routines(text)
        self.assertTrue(any("wake up" in r["question"].lower() for r in routines))

    def test_parse_time_ignores_numeric_counts(self):
        info = self.parser._parse_time_from_text("each day I log 3 priorities.")
        self.assertIsNone(info.get("time_text"))
        self.assertIsNone(info.get("time_local"))
        self.assertFalse(info.get("ambiguous_fields"))

    def test_parse_time_accepts_cued_hour(self):
        info = self.parser._parse_time_from_text("at 3")
        self.assertEqual(info.get("time_text"), "3")
        self.assertIn("time_ampm", info.get("missing_fields") or [])
        self.assertIn("time_local", info.get("ambiguous_fields") or [])

    def test_parse_time_keeps_colon_ambiguity(self):
        info = self.parser._parse_time_from_text("meet at 7:00")
        self.assertEqual(info.get("time_text"), "7:00")
        self.assertIsNone(info.get("time_local"))
        self.assertIn("time_local", info.get("ambiguous_fields") or [])

    def test_extract_traits_detects_trait(self):
        text = "I am compassionate and kind."
        traits = self.parser.extract_traits(text)
        self.assertIn("compassionate", traits)

    def test_extract_behaviors_detects_behavior(self):
        text = "I tend to avoid difficult tasks."
        behaviors = self.parser.extract_behaviors(text)
        self.assertIn("avoidant", behaviors)

    def test_detect_mood_positive(self):
        text = "I feel so happy and excited!"
        mood = self.parser.detect_mood(text)
        self.assertEqual(mood, "positive")

    def test_detect_mood_negative(self):
        text = "I am feeling tired and frustrated."
        mood = self.parser.detect_mood(text)
        self.assertEqual(mood, "negative")

    def test_extract_decisions_combines_data(self):
        text = "I want to exercise more. I am organized."
        decisions = self.parser.extract_decisions(text)
        self.assertTrue(any(d["type"] == "goal" for d in decisions))
        self.assertTrue(any(d["type"] == "trait" for d in decisions))

if __name__ == "__main__":
    unittest.main()
