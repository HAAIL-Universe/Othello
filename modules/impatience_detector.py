import re
from typing import Literal

ImpatienceLevel = Literal["low", "medium", "high"]


class ImpatienceDetector:
    """Lightweight heuristic detector for short-term impatience signals."""

    def __init__(self) -> None:
        self.default_level: ImpatienceLevel = "low"

    def analyze(self, text: str) -> ImpatienceLevel:
        if not text:
            return self.default_level
        lower = text.lower()
        exclamations = text.count("!")
        all_caps = sum(1 for token in text.split() if len(token) > 2 and token.isupper())
        harsh_terms = len(re.findall(r"\b(damn|frustrating|annoying|stupid|hate|angry|now)\b", lower))

        score = 0
        score += min(exclamations, 3)
        score += min(all_caps, 3)
        score += harsh_terms * 2

        if score >= 5:
            return "high"
        if score >= 2:
            return "medium"
        return "low"
