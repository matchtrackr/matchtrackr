from typing import Optional
from app.schema import MatchReport
from app.config import settings


class Analyzer:
    """Base class for analyzers. Subclasses must implement analyze()."""

    needs_video: bool = True

    def analyze(self, submission, video_path: Optional[str]) -> MatchReport:
        raise NotImplementedError


def get_analyzer() -> Analyzer:
    name = (settings.analyzer or "mock").lower()
    if name == "gemini":
        from app.analyzers.gemini import GeminiAnalyzer
        return GeminiAnalyzer()
    if name == "mock":
        from app.analyzers.mock import MockAnalyzer
        return MockAnalyzer()
    raise ValueError(f"Unknown ANALYZER value: {name!r}. Use 'mock' or 'gemini'.")
