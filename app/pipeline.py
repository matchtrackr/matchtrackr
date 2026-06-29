import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Callable, Optional

from app.analyzers.base import get_analyzer
from app.video import download_video, compress_video
from app.pdf_report import build_pdf
from app.email_sender import send_report_email


@dataclass
class Submission:
    player_name: str
    player_email: str
    position: str
    jersey: str
    video_link: str
    team_home: str
    team_away: str
    match_date: str
    competition: str


def _noop(_msg: str) -> None:
    return None


def process(submission: Submission, progress: Optional[Callable[[str], None]] = None) -> None:
    """Run the full pipeline for one submission.

    Steps: download video -> compress -> analyze -> generate PDF -> email -> delete temp files.
    Temp files are always removed in the finally block, even if an earlier step raises.
    """
    progress = progress or _noop
    workdir = tempfile.mkdtemp(prefix="matchtrackr_")
    try:
        analyzer = get_analyzer()

        video_path = None
        if analyzer.needs_video:
            progress("Downloading video...")
            raw = download_video(submission.video_link, workdir)
            progress("Compressing video...")
            video_path = compress_video(raw, os.path.join(workdir, "compressed.mp4"))
        else:
            progress("Skipping video download (mock analyzer).")

        progress("Analyzing footage...")
        report = analyzer.analyze(submission, video_path)

        progress("Generating PDF...")
        pdf_path = os.path.join(workdir, "matchtrackr_report.pdf")
        build_pdf(report, pdf_path)

        progress("Emailing report...")
        send_report_email(submission, report, pdf_path)

        progress(f"Done — report sent to {submission.player_email}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
