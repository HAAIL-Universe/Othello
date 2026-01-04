import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import dateparser
import xml.etree.ElementTree as ET
from core.llm_wrapper import LLMWrapper
import logging

logging.basicConfig(level=logging.DEBUG)

class ConversationParser:
    """
    Main parsing engine for extracting goals, routines, traits, deadlines, and moods from user freeform text.
    Extendable for richer pattern mining, intent ambiguity/confidence, phrase tracking, and agentic RL upgrades.
    """
    def __init__(self, hub=None):
        self.hub = hub

    # === Helper Functions ===

    def _detect_keywords(self, text: str, keywords: List[str]) -> bool:
        """Helper function to detect keywords in the text."""
        return any(keyword in text.lower() for keyword in keywords)

    def parse(self, user_input: str) -> dict:
        logging.debug(f"ConversationAgent: Passing user input to ConversationParser: {user_input}")
        
        # Corrected: Using user_input (raw text) to extract the parsed data
        parsed_data = {
            "behaviors": self.extract_behaviors(user_input),
            "traits": self.extract_traits(user_input),
            "goals": self.extract_goals(user_input),
            "routines": self.extract_routines(user_input),
            "impatience_data": self.extract_impatience_data(user_input),
            "psychological_data": self.extract_psychological_data(user_input),
        }
        
        logging.debug(f"ConversationAgent: Parsed data received from ConversationParser: {parsed_data}")
        
        # Pass parsed data to CentralHub instead of raw user input
        if self.hub:
            logging.debug("ConversationAgent: Passing parsed data to CentralHub")
            self.hub.receive_user_input(parsed_data)  # Pass parsed data to the hub instead of raw text
            
        logging.debug("ConversationAgent: Data passed to CentralHub")
        return parsed_data
    
    def _extract_with_pattern(self, text: str, pattern: str):
        """Extracts data based on a regex pattern."""
        return re.findall(pattern, text.lower())

    # === Goal Extraction ===

    def extract_goals(self, text):
        """
        Scan user input for potential goals or tasks, including deadlines and timelines.
        Detects both strong and soft cue phrases.
        Also catches common 'progress' and 'completed' patterns.
        Returns:
            list of dict: [{"text": goal_text, "deadline": deadline_str, "soft": True/False, "confidence": float}]
        """
        possible_goals = []
        lines = text.split("\n")

        # Strong intention cues
        goal_keywords = [
            # Direct/strong
            "want to", "need to", "plan to", "hope to", "try to", "aim to", "set a goal",
            "intend to", "working on", "wish to", "target is", "goal is", "I aspire", "I wish",
            "ambition", "would love to", "long-term goal", "bucket list", "dream is", "life’s work",
            "calling", "purpose is", "objective is", "mission is", "going for", "looking to", "yearn to",
            "my dream", "I crave", "yearning for", "I'm pursuing"
        ]

        # Soft cue patterns for passive capture
        soft_cue_keywords = [
            "should", "remind me to", "meant to", "i wish i", "i ought to", "i must", "i've been meaning to",
            "supposed to", "would like to", "i could", "i might try", "could do with", "it'd be good to",
            "I was thinking of", "maybe someday", "eventually", "some point", "might get to", "when I have time"
        ]

        # Deadline/timeframe patterns
        deadline_patterns = [
            r'by\s+\w+\s*\d*',
            r'before\s+\w+\s*\d*',
            r'in\s+\d+\s+(day|days|week|weeks|month|months)',
            r'on\s+\w+\s*\d*',
            r'\b(deadline|due|finish by|complete by)\b',
        ]

        # Progress-patterns (explicit "I made progress on..." or "completed my..." lines)
        progress_patterns = [
            r"progress on my goal of ([^.,;]+)",
            r"made progress on ([^.,;]+)",
            r"completed my ([^.,;]+)",
            r"finished my ([^.,;]+)",
            r"achieved my ([^.,;]+)",
            r"did not (?:finish|complete|achieve) my ([^.,;]+)",
            r"accomplished ([^.,;]+)",
            r"smashed ([^.,;]+)",
            r"nailed ([^.,;]+)"
        ]

        # Loop over the text lines
        for line in lines:
            l = line.lower()
            soft = False
            confidence = 1.0
            matched_kw = None
            # 1. Strong/soft keyword
            for kw in goal_keywords:
                if kw in l:
                    matched_kw = kw
                    soft = False
                    confidence = 0.95
                    break
            if not matched_kw:
                for kw in soft_cue_keywords:
                    if kw in l:
                        matched_kw = kw
                        soft = True
                        confidence = 0.7
                        break

            if matched_kw:
                deadline = None
                for pattern in deadline_patterns:
                    match = re.search(pattern, l)
                    if match:
                        deadline = match.group()
                        break
                possible_goals.append({
                    "text": line.strip(),
                    "deadline": deadline,
                    "soft": soft,
                    "confidence": confidence,
                    "source_phrase": matched_kw,
                    "timestamp": datetime.now().isoformat(),
                })

            # 2. Progress-patterns (runs even if no matched_kw)
            for pattern in progress_patterns:
                match = re.search(pattern, l)
                if match:
                    goal_text = match.group(1)
                    possible_goals.append({
                        "text": goal_text.strip(),
                        "deadline": None,
                        "soft": False,
                        "confidence": 0.9,
                        "source_phrase": "progress-pattern",
                        "timestamp": datetime.now().isoformat(),
                    })
                    break

        return possible_goals

    # === Routine Extraction ===

    def _normalize_title(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        if not cleaned:
            return ""
        return cleaned[0].upper() + cleaned[1:]

    def _extract_days_of_week(self, text: str) -> List[str]:
        lower = (text or "").lower()
        days: List[str] = []
        if "every day" in lower or "each day" in lower or "daily" in lower:
            return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        if "weekday" in lower:
            days.extend(["mon", "tue", "wed", "thu", "fri"])
        if "weekend" in lower:
            days.extend(["sat", "sun"])
        day_patterns = [
            ("mon", r"\bmon(day)?\b"),
            ("tue", r"\btue(sday)?\b"),
            ("wed", r"\bwed(nesday)?\b"),
            ("thu", r"\bthu(rsday)?\b"),
            ("fri", r"\bfri(day)?\b"),
            ("sat", r"\bsat(urday)?\b"),
            ("sun", r"\bsun(day)?\b"),
        ]
        for day_key, pattern in day_patterns:
            if re.search(pattern, lower):
                days.append(day_key)
        seen = set()
        ordered: List[str] = []
        for day in days:
            if day in seen:
                continue
            seen.add(day)
            ordered.append(day)
        return ordered

    def _parse_time_from_text(self, text: str) -> Dict[str, Any]:
        lower = (text or "").lower()
        missing_fields: List[str] = []
        ambiguous_fields: List[str] = []
        time_text: Optional[str] = None
        time_local: Optional[str] = None

        match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lower)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            time_local = f"{hour:02d}:{minute:02d}"
            time_text = match.group(0)
            return {
                "time_text": time_text,
                "time_local": time_local,
                "missing_fields": missing_fields,
                "ambiguous_fields": ambiguous_fields,
            }

        match = re.search(r"\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b", lower)
        if match:
            hour = int(match.group(1))
            ampm_raw = match.group(2).replace(".", "")
            is_pm = ampm_raw.startswith("p")
            if is_pm and hour != 12:
                hour += 12
            if not is_pm and hour == 12:
                hour = 0
            time_local = f"{hour:02d}:00"
            time_text = match.group(0).replace(" ", "")
            return {
                "time_text": time_text,
                "time_local": time_local,
                "missing_fields": missing_fields,
                "ambiguous_fields": ambiguous_fields,
            }

        if "morning" in lower:
            time_text = "morning"
            time_local = "07:00"
        elif "evening" in lower:
            time_text = "evening"
            time_local = "19:00"

        if time_local is None:
            match = re.search(r"\b([1-9]|1[0-2])\s*(?:o\W?clock)?\b", lower)
            if match:
                time_text = match.group(0).strip()
                missing_fields.append("time_ampm")
                ambiguous_fields.append("time_local")

        return {
            "time_text": time_text,
            "time_local": time_local,
            "missing_fields": missing_fields,
            "ambiguous_fields": ambiguous_fields,
        }

    def _parse_duration_minutes(self, text: str) -> Optional[int]:
        lower = (text or "").lower()
        match = re.search(r"\b(\d{1,3})\s*(?:-?\s*)?(?:minutes?|mins?|min)\b", lower)
        if not match:
            return None
        try:
            return int(match.group(1))
        except (TypeError, ValueError):
            return None

    def _extract_routine_action(self, text: str) -> str:
        cleaned = (text or "").strip()
        if not cleaned:
            return ""
        # Only treat ":" as a delimiter when followed by whitespace to avoid splitting time tokens like "7:00".
        delimiter = re.search(r":\s+", cleaned)
        if delimiter:
            action = cleaned[delimiter.end():].strip()
        else:
            match = re.search(r"\broutine\b.*?\b(?:to|for)\b\s+([^.;\n]+)", cleaned, flags=re.IGNORECASE)
            action = match.group(1).strip() if match else ""
            if not action:
                candidate = re.sub(
                    r"^(hey othello|hey|hi|hello|ok|okay|please)\s*,?\s*",
                    "",
                    cleaned,
                    flags=re.IGNORECASE,
                )
                candidate = re.sub(
                    r"^(i want to|i'm going to|im going to|i am going to|i will|we will|let's|lets)\s+",
                    "",
                    candidate,
                    flags=re.IGNORECASE,
                )
                cue_match = re.search(r"\b(on|at)\b", candidate, flags=re.IGNORECASE)
                if cue_match:
                    candidate = candidate[:cue_match.start()].strip()
                action = candidate.strip()
        return action.rstrip(".").strip()

    def _extract_scheduled_routine(self, text: str) -> Optional[Dict[str, Any]]:
        lower = (text or "").lower()
        if "routine" not in lower and "every" not in lower and "daily" not in lower:
            return None
        action = self._extract_routine_action(text)
        if not action:
            return None
        time_info = self._parse_time_from_text(text)
        if not time_info.get("time_text") and not time_info.get("time_local"):
            return None
        days = self._extract_days_of_week(text)
        duration_minutes = self._parse_duration_minutes(text)
        return {
            "draft_type": "schedule",
            "title": self._normalize_title(action),
            "days_of_week": days,
            "time_text": time_info.get("time_text"),
            "time_local": time_info.get("time_local"),
            "duration_minutes": duration_minutes,
            "timezone": None,
            "missing_fields": time_info.get("missing_fields") or [],
            "ambiguous_fields": time_info.get("ambiguous_fields") or [],
        }

    def extract_routines(self, text: str) -> list:
        routines = []
        draft = self._extract_scheduled_routine(text)
        if draft:
            routines.append(draft)
        # Wake up
        if self._detect_keywords(text, [
            "wake", "woke", "got up", "morning", "rise", "out of bed", "slept in", "alarm", "up early", "late night"
        ]):
            routines.append({"question": "What time did you wake up today?", "answer": "7 AM"})
        # Meals
        if self._detect_keywords(text, [
            "coffee", "breakfast", "brunch", "ate this morning", "meal", "had lunch", "skipped lunch", "dinner",
            "grabbed food", "ordered in", "fasted"
        ]):
            routines.append({"question": "Did you have any meals or coffee today?", "answer": "Yes"})
        # Work/focus
        if self._detect_keywords(text, [
            "work", "clocked in", "started my shift", "focused", "didn't focus", "worked on", "finished my tasks",
            "task", "productive", "procrastinated work", "late to work", "started late", "burnt out"
        ]):
            routines.append({"question": "When did you start your main work/task?", "answer": "9 AM"})
        # Physical activity
        if self._detect_keywords(text, [
            "gym", "walk", "ran", "run", "jog", "lifted weights", "yoga", "moved my body", "stretch", "physical",
            "played sports", "went swimming", "active", "cardio", "exercise", "hiked"
        ]):
            routines.append({"question": "Did you do any physical activity today?", "answer": "Yes"})
        # Wind down/sleep
        if self._detect_keywords(text, [
            "wind down", "bed", "sleep", "fell asleep", "read before bed", "wound down", "insomnia",
            "late night", "early night", "night routine", "meditated at night"
        ]):
            routines.append({"question": "What time did you wind down/go to sleep?", "answer": "10 PM"})
        return routines

    # === Trait Extraction ===

    def extract_traits(self, text: str) -> list:
        trait_keywords = {
            "perfectionist": [
                "perfect", "perfectionist", "never good enough", "overachiever", "strive for perfection"
            ],
            "procrastinator": [
                "keep putting things off", "procrastinate", "delay", "put off", "postpone", "I'll do it later"
            ],
            "overthinker": [
                "overthink", "think too much", "spiral", "can't stop thinking", "get stuck in my head"
            ],
            "disciplined": [
                "routine", "habit", "consistent", "disciplined", "never skip", "stick to my plan", "on schedule"
            ],
            "avoidant": [
                "avoid", "ignore", "put it off", "numb it", "distract myself", "not dealing with", "let it slide"
            ],
            "resilient": [
                "bounce back", "resilient", "tough", "persevere", "didn't give up", "kept going", "push through"
            ],
            "impulsive": [
                "impulsive", "reckless", "act without thinking", "jumped in", "spur of the moment", "couldn't resist"
            ],
            "compassionate": [
                "compassionate", "kind", "helpful", "generous", "empathetic", "caring", "helped someone",
                "supported", "volunteered", "forgave", "listened", "showed kindness"
            ],
            "creative": [
                "creative", "innovative", "imaginative", "original", "came up with", "designed", "brainstormed"
            ],
            "confident": [
                "confident", "self-assured", "bold", "fearless", "stood up for", "asserted", "took the lead"
            ],
            "organized": [
                "organized", "orderly", "systematic", "planned ahead", "kept things tidy"
            ]
            # Add more as you expand trait logging
        }
        detected = set()
        lowered_text = text.lower()
        # Direct "I am"/"I'm"/"I tend to be"
        direct_trait_patterns = [
            r"\bi am ([a-z ,\-&]+)", r"\bi'm ([a-z ,\-&]+)", r"\bi tend to be ([a-z ,\-&]+)"
        ]
        for pat in direct_trait_patterns:
            matches = self._extract_with_pattern(lowered_text, pat)
            for match in matches:
                traits = re.split(r"[,&]|\band\b", match)
                detected.update([t.strip() for t in traits if len(t.strip()) > 2])
        for trait, phrases in trait_keywords.items():
            for phrase in phrases:
                if phrase in lowered_text:
                    detected.add(trait)
        return list(detected)
    
     # === Psychological Data Extraction ===

    def extract_psychological_data(self, text: str) -> dict:
        psychological_data = {
            "emotional_state": self.detect_mood(text),
            "traits": self.extract_traits(text),
            "mood": self.detect_mood(text),
        }
        psychological_data["psychological_cues"] = self._extract_psychological_cues(text)
        return psychological_data

    def extract_psychological_cues(self, text: str):
        cues = {
            "anxiety": ["nervous", "anxious", "worry", "uneasy", "stress"],
            "optimism": ["hopeful", "positive", "excited", "enthusiastic", "bright"],
            "pessimism": ["negative", "worried", "doubtful", "hopeless", "fearful"],
            "neuroticism": ["moody", "irritable", "tense", "easily frustrated"],
        }
        psychological_cues = {}
        for cue, keywords in cues.items():
            for keyword in keywords:
                if keyword in text.lower():
                    psychological_cues[cue] = True
                    break
            else:
                psychological_cues[cue] = False
        return psychological_cues

    def _extract_psychological_cues(self, text: str):
        """Extract psychological cues that indicate certain psychological traits (e.g., anxiety, stress)."""
        cues = {
            "anxiety": ["nervous", "anxious", "worry", "uneasy", "stress"],
            "optimism": ["hopeful", "positive", "excited", "enthusiastic", "bright"],
            "pessimism": ["negative", "worried", "doubtful", "hopeless", "fearful"],
            "neuroticism": ["moody", "irritable", "tense", "easily frustrated"],
        }

        psychological_cues = {}

        # Check for keywords that suggest a particular trait
        for cue, keywords in cues.items():
            for keyword in keywords:
                if keyword in text.lower():
                    psychological_cues[cue] = True
                    break
            else:
                psychological_cues[cue] = False

        return psychological_cues

    # === Mood and Emotional Detection ===

    def detect_mood(self, text):
        positive = ["excited", "happy", "hopeful", "motivated", "grateful", "optimistic", "energetic", "inspired", "confident"]
        negative = [
            "tired", "anxious", "frustrated", "angry", "sad", "drained", "overwhelmed", "fed up",
            "hopeless", "worried", "burnt out", "stressed"
        ]
        text_lower = text.lower()
        for word in positive:
            if word in text_lower:
                return "positive"
        for word in negative:
            if word in text_lower:
                return "negative"
        return "neutral"

    def detect_mood_trend(self, texts: List[str]) -> str:
        mood_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for text in texts:
            mood = self.detect_mood(text)
            mood_counts[mood] += 1
        if abs(mood_counts["positive"] - mood_counts["negative"]) <= 2:
            return "fluctuating"
        return max(mood_counts.items(), key=lambda x: x[1])[0]
    
    def extract_deadline_date(self, text: str):
        parsed_date = dateparser.parse(text)
        if parsed_date:
            return parsed_date.strftime("%Y-%m-%d")
        return None
    
    def detect_timeline(self, text: str):
        """
        Try to extract rough timeframes (days/weeks/months) from the text.
        Returns:
            tuple: ("in 2 days", 2, "days") or None
        """
        match = re.search(r"in (\d+) (day|days|week|weeks|month|months)", text.lower())
        if match:
            count = int(match.group(1))
            unit = match.group(2)
            return (match.group(0), count, unit)
        return None

    # === Long-Term Goals and Behavior Analysis ===

    def extract_long_term_goals(self, text: str):
        long_term_goal_keywords = [
            "dream of", "hope to", "aim to", "vision of", "my life goal is", "goal for the future",
            "bucket list", "purpose in life", "eventually want to", "ultimate aim"
        ]
        long_term_goals = []
        for line in text.split("\n"):
            for keyword in long_term_goal_keywords:
                if keyword in line.lower():
                    goal = {"text": line.strip(), "confidence": 0.8}
                    deadline = self.extract_deadline_date(line)
                    if deadline:
                        goal["deadline"] = deadline
                    long_term_goals.append(goal)
        return long_term_goals

    def extract_behaviors(self, text: str) -> list:
        behavior_keywords = {
            "avoidant": [
                "avoid", "procrastinate", "delay", "distract", "put off", "postpone", "escape",
                "dodge", "shirk", "skip", "ignore", "abandon", "withdraw", "evade", "not dealing",
                "let it slide", "left unfinished"
            ],
            "empathetic": [
                "compassionate", "understanding", "care", "feel for", "sympathetic", "supportive",
                "listened", "comforted", "stood up for", "forgave", "showed compassion", "cared for"
            ],
            "aggressive": [
                "angry", "rage", "attack", "hostile", "snapped", "lost my temper", "lashed out", "got mad",
                "exploded", "argued", "shouted", "yelled", "criticized", "blamed", "got into a fight"
            ],
            "indecisive": [
                "can't decide", "unsure", "indecisive", "torn", "on the fence", "couldn't choose", "hesitated",
                "waffled", "debated with myself", "second guessed", "doubted", "sat on it", "delayed deciding"
            ],
            "persistent": [
                "kept at it", "didn't give up", "followed through", "kept trying", "stayed committed", "persisted"
            ],
            "proactive": [
                "took initiative", "jumped in", "got started", "made a plan", "set up", "prepped ahead"
            ],
            "optimistic": [
                "looked on the bright side", "felt positive", "expected the best", "was hopeful"
            ]
            # Add further behavior types as your agent suite expands
        }
        detected_behaviors = []
        text_lower = text.lower()
        for behavior, phrases in behavior_keywords.items():
            for phrase in phrases:
                if phrase in text_lower:
                    detected_behaviors.append(behavior)
        return detected_behaviors

    # === Utility Functions ===

    def extract_impatience_data(self, text: str) -> dict:
        emotional_state = "neutral"
        impatience_keywords = [
            "hurry", "quick", "now", "can't", "annoyed", "frustrated", "fed up", "losing patience",
            "rushed", "need it now", "waiting forever", "why is this taking so long", "getting anxious",
            "too slow", "can’t stand it", "over it", "irritated", "stressed", "ready to snap"
        ]
        impatience_found = any(word in text.lower() for word in impatience_keywords)
        if impatience_found:
            emotional_state = "impatient"
        elif "calm" in text.lower() or "relaxed" in text.lower():
            emotional_state = "calm"
        return {"user_input": text, "emotional_state": emotional_state}

    def generate_suggestions(self, text: str):
        suggestions = []
        if "too much on my plate" in text.lower():
            suggestions.append("Consider breaking down larger goals into smaller tasks.")
        if "can't focus" in text.lower():
            suggestions.append("Try a short break or focus technique.")
        return suggestions

    def extract_decisions(self, text: str) -> list:
        decisions = []
        goals = self.extract_goals(text)
        for goal in goals:
            decisions.append({"type": "goal", "details": goal})
        traits = self.extract_traits(text)
        for trait in traits:
            decisions.append({"type": "trait", "details": {"description": trait}})
        routines = self.extract_routines(text)
        for routine in routines:
            decisions.append({"type": "routine", "details": routine})
        decision_cues = self.extract_decision_cues(text)
        for cue in decision_cues:
            decisions.append({"type": "decision_cue", "details": {"cue": cue}})
        behaviors = self.extract_behaviors(text)
        for behavior in behaviors:
            decisions.append({"type": "behavior", "details": {"description": behavior}})
        return decisions

    def extract_decision_cues(self, text: str) -> list:
        decision_keywords = [
            "can't decide", "undecided", "not sure", "what should I do", "conflicted", "struggling with",
            "don't know which", "can't make up my mind", "torn between", "I need to make a decision", 
            "should I", "decide between", "dilemma", "split decision", "debate with myself"
        ]
        decision_cues = []
        text_lower = text.lower()
        for keyword in decision_keywords:
            if keyword in text_lower:
                decision_cues.append(keyword)
        return decision_cues

    def parse_and_analyze_decisions(self, text: str):
        decisions = []
        decision_cues = self.extract_decision_cues(text)
        goals = self.extract_goals(text)
        traits = self.extract_traits(text)
        for cue in decision_cues:
            decisions.append({
                "type": "decision_cue",
                "details": {"cue": cue},
            })
        for goal in goals:
            decisions.append({
                "type": "goal",
                "details": goal,
            })
        for trait in traits:
            decisions.append({
                "type": "trait",
                "details": {"description": trait},
            })
        return decisions

    
    def extract_habits_and_events(self, text: str) -> dict:
        # BehavioralAgent hooks for logging habit/event triggers
        habit_phrases = [
            "every day", "each morning", "daily", "routinely", "after breakfast", "before bed",
            "always", "never skip", "as usual", "my habit", "trying to build a habit"
        ]
        event_phrases = [
            "today I", "this morning", "last night", "this week", "yesterday", "on Monday", "recently",
            "I started", "I finished", "I changed", "I tried", "I failed", "I succeeded", "missed"
        ]
        detected = {
            "habits": [],
            "events": []
        }
        for phrase in habit_phrases:
            if phrase in text.lower():
                detected["habits"].append(phrase)
        for phrase in event_phrases:
            if phrase in text.lower():
                detected["events"].append(phrase)
        return detected

    # === XML Parsing for Goal Updates (Multi-step Planning) ===

    def _normalize_legacy_schema(self, xml_string: str) -> str:
        """
        Normalize legacy <goal> schemas to the canonical <goal_update> schema.
        
        This provides backward compatibility for older XML formats that may use:
        - <goal> instead of <goal_update>
        - <plan_step> instead of <step>
        - <description> instead of <summary>
        - <action_plan> instead of <plan_steps>
        
        Args:
            xml_string: The raw XML string
        
        Returns:
            Normalized XML string with <goal_update> schema
        """
        # Quick check: if already using <goal_update>, return as-is
        if "<goal_update>" in xml_string:
            return xml_string
        
        # Check if this is a legacy <goal> schema
        if "<goal>" not in xml_string:
            return xml_string
        
        logging.info("ConversationParser: Detected legacy <goal> schema, normalizing to <goal_update>")
        
        try:
            # Parse the legacy XML
            root = ET.fromstring(xml_string)
            
            if root.tag != "goal":
                return xml_string  # Not a legacy schema we recognize
            
            # Build a new <goal_update> structure
            goal_update = ET.Element("goal_update")
            
            # Map <description> → <summary>
            description_elem = root.find("description")
            if description_elem is not None and description_elem.text:
                summary = ET.SubElement(goal_update, "summary")
                summary.text = description_elem.text.strip()
            else:
                # Default summary
                summary = ET.SubElement(goal_update, "summary")
                summary.text = "Goal update from legacy schema"
            
            # Add default status, priority, category
            status = ET.SubElement(goal_update, "status")
            status.text = "active"
            
            priority = ET.SubElement(goal_update, "priority")
            priority.text = "medium"
            
            category_elem = root.find("category")
            if category_elem is not None and category_elem.text:
                category = ET.SubElement(goal_update, "category")
                category.text = category_elem.text.strip()
            else:
                category = ET.SubElement(goal_update, "category")
                category.text = "other"
            
            # Map <action_plan><plan_step> → <plan_steps><step>
            plan_steps = ET.SubElement(goal_update, "plan_steps")
            
            action_plan = root.find("action_plan")
            if action_plan is not None:
                step_index = 1
                for plan_step in action_plan.findall("plan_step"):
                    # Create new <step> element
                    step = ET.SubElement(plan_steps, "step")
                    
                    # Get step_number or use sequential index
                    step_num = plan_step.get("step_number")
                    if step_num:
                        try:
                            step_index = int(step_num)
                        except ValueError:
                            pass
                    
                    step.set("index", str(step_index))
                    step.set("status", "pending")
                    
                    # Get description
                    desc_elem = plan_step.find("description")
                    if desc_elem is not None and desc_elem.text:
                        step.text = desc_elem.text.strip()
                    else:
                        step.text = f"Step {step_index}"
                    
                    # Optional: map duration to due_date (skip for now)
                    
                    step_index += 1
            
            # If no action_plan found, create minimal steps
            if len(plan_steps) == 0:
                for i in range(1, 4):
                    step = ET.SubElement(plan_steps, "step")
                    step.set("index", str(i))
                    step.set("status", "pending")
                    step.text = f"Action step {i}"
            
            # Add <next_action>
            next_action = ET.SubElement(goal_update, "next_action")
            first_step = plan_steps.find("step")
            if first_step is not None and first_step.text:
                next_action.text = first_step.text
            else:
                next_action.text = "Begin working on the first step"
            
            # Convert back to string
            normalized_xml = ET.tostring(goal_update, encoding="unicode")
            logging.debug(f"ConversationParser: Normalized legacy schema:\n{normalized_xml}")
            
            return normalized_xml
            
        except ET.ParseError as e:
            logging.error(f"ConversationParser: Failed to parse legacy schema: {e}")
            return xml_string  # Return original if normalization fails
        except Exception as e:
            logging.error(f"ConversationParser: Error normalizing legacy schema: {e}")
            return xml_string

    def parse_goal_update_xml(self, xml_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse goal update XML from LLM responses into structured data.
        
        Expected XML schema:
        <goal_update>
            <summary>Overall goal description</summary>
            <status>active|completed|paused</status>
            <priority>1-5 or low|medium|high</priority>
            <category>work|personal|health|learning</category>
            <plan_steps>
                <step index="1" status="pending" due_date="2025-12-15">First step description</step>
                <step index="2" status="pending">Second step description</step>
                ...
            </plan_steps>
            <metadata>
                <tags>tag1,tag2,tag3</tags>
                <notes>Additional notes about the goal</notes>
            </metadata>
        </goal_update>
        
        Args:
            xml_string: The XML string to parse
        
        Returns:
            Dictionary with parsed data:
            {
                "summary": str,
                "status": str,
                "priority": str or int,
                "category": str,
                "plan_steps": [
                    {"step_index": int, "description": str, "status": str, "due_date": str or None},
                    ...
                ],
                "metadata": {"tags": str, "notes": str, ...}
            }
            Returns None if parsing fails.
        """
        if not xml_string or not xml_string.strip():
            logging.warning("ConversationParser: Empty XML string provided to parse_goal_update_xml")
            return None
        
        try:
            # Normalize legacy schemas before parsing
            xml_string = self._normalize_legacy_schema(xml_string)
            
            # Parse the XML
            root = ET.fromstring(xml_string)
            
            # Validate root tag
            if root.tag != "goal_update":
                logging.error(f"ConversationParser: Expected <goal_update> root tag, got <{root.tag}>")
                return None
            
            # Extract core fields
            result: Dict[str, Any] = {
                "summary": None,
                "status": None,
                "priority": None,
                "category": None,
                "plan_steps": [],
                "metadata": {}
            }
            
            # Extract summary
            summary_elem = root.find("summary")
            if summary_elem is not None and summary_elem.text:
                result["summary"] = summary_elem.text.strip()
            
            # Extract status
            status_elem = root.find("status")
            if status_elem is not None and status_elem.text:
                result["status"] = status_elem.text.strip()
            
            # Extract priority
            priority_elem = root.find("priority")
            if priority_elem is not None and priority_elem.text:
                priority_text = priority_elem.text.strip()
                # Try to convert to int if it's numeric
                try:
                    result["priority"] = int(priority_text)
                except ValueError:
                    result["priority"] = priority_text
            
            # Extract category
            category_elem = root.find("category")
            if category_elem is not None and category_elem.text:
                result["category"] = category_elem.text.strip()
            
            # Extract plan steps
            plan_steps_elem = root.find("plan_steps")
            if plan_steps_elem is not None:
                for step_elem in plan_steps_elem.findall("step"):
                    try:
                        # Get step index
                        index_attr = step_elem.get("index")
                        if index_attr is None:
                            logging.warning("ConversationParser: Step element missing 'index' attribute, skipping")
                            continue
                        
                        step_index = int(index_attr)
                        
                        # Get step description from text content
                        description = step_elem.text.strip() if step_elem.text else ""
                        if not description:
                            logging.warning(f"ConversationParser: Step {step_index} has no description, skipping")
                            continue
                        
                        # Get optional status attribute (default to 'pending')
                        status = step_elem.get("status", "pending")
                        
                        # Get optional due_date attribute
                        due_date = step_elem.get("due_date")
                        
                        result["plan_steps"].append({
                            "step_index": step_index,
                            "description": description,
                            "status": status,
                            "due_date": due_date
                        })
                    except (ValueError, AttributeError) as e:
                        logging.error(f"ConversationParser: Error parsing step element: {e}")
                        continue
            
            # Extract metadata
            metadata_elem = root.find("metadata")
            if metadata_elem is not None:
                for child in metadata_elem:
                    if child.text:
                        result["metadata"][child.tag] = child.text.strip()
            
            logging.info(f"ConversationParser: Successfully parsed goal update XML with {len(result['plan_steps'])} steps")
            return result
            
        except ET.ParseError as e:
            logging.error(f"ConversationParser: XML parse error: {e}")
            return None
        except Exception as e:
            logging.error(f"ConversationParser: Unexpected error parsing goal update XML: {e}")
            return None
    
    def extract_goal_update_xml(self, text: str) -> Optional[str]:
        """
        Extract the <goal_update>...</goal_update> block from LLM response text.
        
        This searches for the opening and closing tags and returns the XML block if found.
        
        Args:
            text: The full LLM response text
        
        Returns:
            The extracted XML string (including tags), or None if not found
        """
        if not text:
            return None
        
        # Search for opening and closing tags
        start_tag = "<goal_update>"
        end_tag = "</goal_update>"
        
        start_idx = text.find(start_tag)
        if start_idx == -1:
            logging.debug("ConversationParser: No <goal_update> opening tag found in text")
            return None
        
        end_idx = text.find(end_tag, start_idx)
        if end_idx == -1:
            logging.warning("ConversationParser: Found <goal_update> opening tag but no closing tag")
            return None
        
        # Extract the XML block (including tags)
        xml_block = text[start_idx:end_idx + len(end_tag)]
        
        logging.debug(f"ConversationParser: Extracted goal_update XML block ({len(xml_block)} chars)")
        return xml_block

