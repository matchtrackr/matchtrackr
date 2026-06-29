"""MatchTrackr CLI — your self-run replacement for Tally + Make.com.

Example:
    python run.py --name "Alex" --email "you@gmail.com" --link "https://..."

Any required argument you omit will be asked interactively. Optional fields fall
back to sensible defaults when you press Enter.
"""

import argparse
import sys
from datetime import date

from app.pipeline import Submission, process


def _ask(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val or default


def _resolve(args) -> Submission:
    today = date.today().isoformat()

    name = args.name or _ask("Player name")
    while not name:
        print("  (player name is required)")
        name = _ask("Player name")

    email = args.email or _ask("Player email")
    while not email or "@" not in email:
        print("  (a valid email is required)")
        email = _ask("Player email")

    link = args.link or _ask("Video link (Google Drive / YouTube / direct URL)")
    while not link:
        print("  (video link is required)")
        link = _ask("Video link")

    position = args.position or _ask("Position", "Central Midfielder")
    jersey = args.jersey or _ask("Jersey number", "10")
    home = args.home or _ask("Home team", "Home FC")
    away = args.away or _ask("Away team", "Away United")
    match_date = args.date or _ask("Match date (YYYY-MM-DD)", today)
    competition = args.competition or _ask("Competition", "League Match")

    return Submission(
        player_name=name,
        player_email=email,
        position=position,
        jersey=jersey,
        video_link=link,
        team_home=home,
        team_away=away,
        match_date=match_date,
        competition=competition,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="MatchTrackr — generate a match performance report.")
    p.add_argument("--name", help="Player name")
    p.add_argument("--email", help="Player email (where the report PDF will be sent)")
    p.add_argument("--link", help="Video link: Google Drive share link, YouTube URL, or direct MP4 URL")
    p.add_argument("--position", help="Player position (e.g. 'Central Midfielder')")
    p.add_argument("--jersey", help="Jersey number")
    p.add_argument("--home", help="Home team name")
    p.add_argument("--away", help="Away team name")
    p.add_argument("--date", help="Match date (YYYY-MM-DD)")
    p.add_argument("--competition", help="Competition name (e.g. 'U17 League')")
    args = p.parse_args()

    try:
        submission = _resolve(args)
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return 130

    def progress(msg: str) -> None:
        print(f"[matchtrackr] {msg}")

    print()
    print(f"Submitting report for {submission.player_name} <{submission.player_email}>")
    print(f"  {submission.team_home} vs {submission.team_away} — {submission.competition} ({submission.match_date})")
    print()

    try:
        process(submission, progress=progress)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    except Exception as exc:  # noqa: BLE001 — we want a friendly summary for any failure
        print()
        print(f"[matchtrackr] FAILED: {type(exc).__name__}: {exc}")
        print()
        print("If you want the full traceback, re-run with: python -X faulthandler run.py ...")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
