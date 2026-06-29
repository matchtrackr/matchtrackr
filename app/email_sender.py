import os
import smtplib
import ssl
from email.message import EmailMessage

from app.config import settings


_HTML_TEMPLATE = """\
<html><body style="font-family:Helvetica,Arial,sans-serif;color:#1F2937;">
<p>Hi {player_name},</p>
<p>Your <strong>MatchTrackr</strong> performance report for
<strong>{team_home} vs {team_away}</strong> ({competition}, {match_date}) is attached as a PDF.</p>
<p>All numbers in the report are <em>observed estimates</em> based on the clip you provided
&mdash; not official match stats.</p>
<p>Good luck with the next one.<br>&mdash; MatchTrackr</p>
</body></html>
"""


def send_report_email(submission, report, pdf_path: str) -> None:
    if not settings.gmail_user or not settings.gmail_app_password:
        raise RuntimeError(
            "GMAIL_USER or GMAIL_APP_PASSWORD is not set in .env — cannot send email."
        )

    msg = EmailMessage()
    msg["From"] = f"{settings.from_name} <{settings.gmail_user}>"
    msg["To"] = submission.player_email
    msg["Subject"] = (
        f"Your MatchTrackr report — {submission.team_home} vs {submission.team_away} "
        f"({submission.match_date})"
    )

    plain = (
        f"Hi {submission.player_name},\n\n"
        f"Your MatchTrackr performance report for {submission.team_home} vs "
        f"{submission.team_away} ({submission.competition}, {submission.match_date}) "
        f"is attached as a PDF.\n\n"
        f"All numbers in the report are observed estimates based on the clip you "
        f"provided — not official match stats.\n\n"
        f"— MatchTrackr\n"
    )
    msg.set_content(plain)
    msg.add_alternative(
        _HTML_TEMPLATE.format(
            player_name=submission.player_name,
            team_home=submission.team_home,
            team_away=submission.team_away,
            competition=submission.competition,
            match_date=submission.match_date,
        ),
        subtype="html",
    )

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_name = os.path.basename(pdf_path) or "matchtrackr_report.pdf"
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=pdf_name)

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=60) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(settings.gmail_user, settings.gmail_app_password)
        smtp.send_message(msg)
