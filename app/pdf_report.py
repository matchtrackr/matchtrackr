from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)

from app.schema import MatchReport


_BRAND = colors.HexColor("#0E7C66")
_INK = colors.HexColor("#1F2937")
_MUTED = colors.HexColor("#6B7280")


def _styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=22, leading=26, textColor=_BRAND, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=14, leading=18, textColor=_BRAND, spaceBefore=14, spaceAfter=6),
        "meta": ParagraphStyle("meta", parent=base["BodyText"], fontSize=10, leading=14, textColor=_MUTED),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=11, leading=15, textColor=_INK),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=11, leading=15, textColor=_INK, leftIndent=14, bulletIndent=2),
        "footer": ParagraphStyle("footer", parent=base["BodyText"], fontSize=8, leading=10, textColor=_MUTED, alignment=1),
    }


def _bullets(items, style):
    return [Paragraph(f"&bull; {item}", style) for item in items]


def _stats_table(stats):
    rows = [
        ["Metric", "Observed"],
        ["Passes", str(stats.passes_observed)],
        ["Pass completion", f"{stats.pass_completion_pct_observed:.1f}%"],
        ["Shots", str(stats.shots_observed)],
        ["Shots on target", str(stats.shots_on_target_observed)],
        ["Tackles", str(stats.tackles_observed)],
        ["Duels won", str(stats.duels_won_observed)],
        ["Interceptions", str(stats.interceptions_observed)],
        ["Distance covered", f"{stats.distance_covered_observed_km:.2f} km"],
        ["Sprints", str(stats.sprints_observed)],
    ]
    table = Table(rows, colWidths=[2.6 * inch, 1.8 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _moments_table(moments):
    rows = [["Time", "What happened"]]
    for m in moments:
        rows.append([m.timestamp, m.description])
    table = Table(rows, colWidths=[0.9 * inch, 5.3 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(
        LETTER[0] / 2.0, 0.4 * inch,
        "MatchTrackr  |  All numbers are observed estimates from the provided clip, not official stats.",
    )
    canvas.drawRightString(LETTER[0] - 0.5 * inch, 0.4 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(report: MatchReport, output_path: str) -> str:
    styles = _styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.6 * inch, bottomMargin=0.7 * inch,
        title=f"MatchTrackr report — {report.player_name}",
    )

    story = []

    # ---------- Page 1: Cover & summary ----------
    story.append(Paragraph(f"{report.player_name}", styles["h1"]))
    meta = (
        f"#{report.jersey} &middot; {report.player_position} &middot; "
        f"{report.team_home} vs {report.team_away} &middot; {report.competition} &middot; {report.match_date}"
    )
    story.append(Paragraph(meta, styles["meta"]))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Overall (observed)", styles["h2"]))
    story.append(Paragraph(
        f"<font size=28 color='#0E7C66'><b>{report.overall_rating_observed:.1f}</b></font> "
        f"<font color='#6B7280'>/ 10 observed</font>",
        styles["body"],
    ))

    story.append(Paragraph("Summary", styles["h2"]))
    story.append(Paragraph(report.summary, styles["body"]))

    story.append(PageBreak())

    # ---------- Page 2: Qualitative ----------
    story.append(Paragraph("Strengths", styles["h2"]))
    story.extend(_bullets(report.strengths, styles["bullet"]))

    story.append(Paragraph("Areas to improve", styles["h2"]))
    story.extend(_bullets(report.weaknesses, styles["bullet"]))

    story.append(Paragraph("Key moments", styles["h2"]))
    story.append(_moments_table(report.key_moments))

    story.append(PageBreak())

    # ---------- Page 3: Quantitative + Recommendations ----------
    story.append(Paragraph("Observed stats", styles["h2"]))
    story.append(Paragraph(
        "These are estimates observed from the footage, not official match data.",
        styles["meta"],
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(_stats_table(report.observed_stats))

    story.append(Paragraph("Recommendations", styles["h2"]))
    story.extend(_bullets(report.recommendations, styles["bullet"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path
