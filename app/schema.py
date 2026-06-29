from pydantic import BaseModel, Field
from typing import List


class KeyMoment(BaseModel):
    timestamp: str = Field(description="MM:SS or HH:MM:SS into the clip")
    description: str


class ObservedStats(BaseModel):
    """All values are estimates observed from the footage, not official stats."""
    passes_observed: int = 0
    pass_completion_pct_observed: float = 0.0
    shots_observed: int = 0
    shots_on_target_observed: int = 0
    tackles_observed: int = 0
    duels_won_observed: int = 0
    interceptions_observed: int = 0
    distance_covered_observed_km: float = 0.0
    sprints_observed: int = 0


class MatchReport(BaseModel):
    player_name: str
    player_position: str
    jersey: str
    team_home: str
    team_away: str
    match_date: str
    competition: str

    summary: str
    overall_rating_observed: float = Field(ge=0, le=10, description="0-10, observed estimate")
    strengths: List[str]
    weaknesses: List[str]
    key_moments: List[KeyMoment]
    observed_stats: ObservedStats
    recommendations: List[str]
