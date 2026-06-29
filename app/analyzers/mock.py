import random
from typing import Optional
from app.analyzers.base import Analyzer
from app.schema import MatchReport, KeyMoment, ObservedStats


class MockAnalyzer(Analyzer):
    """Returns a realistic-looking MatchReport without touching any external API or video file."""

    needs_video = False

    def analyze(self, submission, video_path: Optional[str]) -> MatchReport:
        rng = random.Random(f"{submission.player_name}-{submission.match_date}")

        strengths = rng.sample(
            [
                "Strong off-the-ball movement and intelligent positioning",
                "Composed in possession under pressure",
                "Good first touch and ball control in tight spaces",
                "Effective use of body to shield the ball",
                "Sharp acceleration over the first 5 metres",
                "Reads the second ball well in transitions",
                "Active in pressing triggers and counter-pressing",
            ],
            k=3,
        )
        weaknesses = rng.sample(
            [
                "Decision-making in the final third can be rushed",
                "Defensive recovery runs sometimes lack urgency",
                "Weaker foot under-used in build-up",
                "Tends to drift out of central pockets when team is in possession",
                "Aerial duel timing inconsistent",
            ],
            k=2,
        )
        recommendations = rng.sample(
            [
                "Practice 1v1 finishing drills emphasising weaker-foot strikes",
                "Add small-sided pressing games to sharpen counter-press triggers",
                "Video review focused on positioning between the lines",
                "Strength + plyometric block to improve aerial duel timing",
                "Pattern-of-play sessions to stay central in build-up",
            ],
            k=3,
        )

        moments = [
            KeyMoment(timestamp="03:12", description="Switched play with an outside-foot pass to release the right-back."),
            KeyMoment(timestamp="17:48", description="Lost possession in midfield, recovered the ball within 3 seconds via counter-press."),
            KeyMoment(timestamp="34:05", description="Half-chance: shot from the edge of the box, deflected wide."),
            KeyMoment(timestamp="58:22", description="Drove into the half-space and drew a foul in a dangerous area."),
            KeyMoment(timestamp="72:40", description="Defensive header cleared a corner under pressure."),
        ]

        stats = ObservedStats(
            passes_observed=rng.randint(38, 72),
            pass_completion_pct_observed=round(rng.uniform(74.0, 91.0), 1),
            shots_observed=rng.randint(1, 5),
            shots_on_target_observed=rng.randint(0, 3),
            tackles_observed=rng.randint(2, 7),
            duels_won_observed=rng.randint(4, 14),
            interceptions_observed=rng.randint(1, 6),
            distance_covered_observed_km=round(rng.uniform(7.8, 11.4), 2),
            sprints_observed=rng.randint(12, 28),
        )

        summary = (
            f"{submission.player_name} put in a competitive shift at "
            f"{submission.position.lower() or 'their position'} for "
            f"{submission.team_home} against {submission.team_away} in the "
            f"{submission.competition}. The footage shows a player comfortable on the ball, "
            f"willing to take up advanced positions, and active in transitions. "
            f"There are still clear development areas — particularly in final-third "
            f"decision-making and defensive recovery — but the overall body of work is positive."
        )

        return MatchReport(
            player_name=submission.player_name,
            player_position=submission.position,
            jersey=submission.jersey,
            team_home=submission.team_home,
            team_away=submission.team_away,
            match_date=submission.match_date,
            competition=submission.competition,
            summary=summary,
            overall_rating_observed=round(rng.uniform(6.4, 8.2), 1),
            strengths=strengths,
            weaknesses=weaknesses,
            key_moments=moments,
            observed_stats=stats,
            recommendations=recommendations,
        )
