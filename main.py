"""Optional FastAPI surface for MatchTrackr.

For Phase 1-3 you can ignore this entirely and just use `run.py` from the CLI.
Phase 4(b) adds the proper HTML submission form here.
"""

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from app.pipeline import Submission, process

app = FastAPI(title="MatchTrackr")


class SubmissionIn(BaseModel):
    player_name: str
    player_email: EmailStr
    position: str = ""
    jersey: str = ""
    video_link: str
    team_home: str = ""
    team_away: str = ""
    match_date: str = ""
    competition: str = ""


@app.get("/")
def root():
    return {"app": "MatchTrackr", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
def submit(payload: SubmissionIn, background_tasks: BackgroundTasks):
    """Kick off the pipeline asynchronously so the HTTP request returns immediately."""
    if not payload.video_link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="video_link must be an http(s) URL")
    sub = Submission(**payload.model_dump())
    background_tasks.add_task(process, sub)
    return {"status": "accepted", "player_email": payload.player_email}


@app.post("/test")
def test_pipeline(background_tasks: BackgroundTasks):
    """Run the pipeline against a hard-coded sample submission. Useful for smoke tests."""
    sub = Submission(
        player_name="Test Player",
        player_email="",  # filled at runtime from env or query? Keep empty -> caller must override.
        position="Central Midfielder",
        jersey="8",
        video_link="https://example.com/sample.mp4",
        team_home="Home FC",
        team_away="Away United",
        match_date="2025-01-01",
        competition="Friendly",
    )
    if not sub.player_email:
        raise HTTPException(
            status_code=400,
            detail="No player_email set on the sample submission. Use POST /submit instead.",
        )
    background_tasks.add_task(process, sub)
    return {"status": "accepted"}
