import json
import time
from typing import Optional

from app.analyzers.base import Analyzer
from app.config import settings
from app.schema import MatchReport


PROMPT_TEMPLATE = """You are an experienced soccer scout. You are watching a clip from a real match.

Player to focus on:
- Name: {player_name}
- Position: {position}
- Jersey number: {jersey}
- Team: {team_home} (home) vs {team_away} (away)
- Match: {competition} on {match_date}

Watch the player wearing jersey {jersey}. Produce a structured performance report.
All numbers MUST be honest estimates observed from this clip only — label them as observed.
Do not invent stats from outside the clip. If you cannot tell from the footage, give 0.

Return ONLY a JSON object that matches this schema (no markdown fences, no commentary):

{schema}
"""


class GeminiAnalyzer(Analyzer):
    needs_video = True

    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is empty. Set it in .env or switch ANALYZER=mock."
            )
        from google import genai  # imported lazily so mock mode never needs the SDK
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def analyze(self, submission, video_path: Optional[str]) -> MatchReport:
        if not video_path:
            raise RuntimeError("GeminiAnalyzer requires a video file path.")

        uploaded = self._client.files.upload(file=video_path)

        # Wait until the upload finishes server-side processing.
        deadline = time.time() + 600
        while getattr(uploaded, "state", None) and str(uploaded.state).endswith("PROCESSING"):
            if time.time() > deadline:
                raise TimeoutError("Gemini took too long to process the uploaded video.")
            time.sleep(2)
            uploaded = self._client.files.get(name=uploaded.name)

        prompt = PROMPT_TEMPLATE.format(
            player_name=submission.player_name,
            position=submission.position or "unspecified",
            jersey=submission.jersey or "unspecified",
            team_home=submission.team_home or "Home",
            team_away=submission.team_away or "Away",
            competition=submission.competition or "match",
            match_date=submission.match_date or "unspecified",
            schema=json.dumps(MatchReport.model_json_schema(), indent=2),
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=[uploaded, prompt],
            config={"response_mime_type": "application/json"},
        )

        raw = response.text or ""
        data = json.loads(raw)

        # Fill in submission fields if the model omitted them.
        data.setdefault("player_name", submission.player_name)
        data.setdefault("player_position", submission.position)
        data.setdefault("jersey", submission.jersey)
        data.setdefault("team_home", submission.team_home)
        data.setdefault("team_away", submission.team_away)
        data.setdefault("match_date", submission.match_date)
        data.setdefault("competition", submission.competition)

        return MatchReport.model_validate(data)
