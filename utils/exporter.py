from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


# ── Color palette ────────────────────────────────────────────────────────────
PURPLE      = colors.HexColor("#6366f1")
GREEN       = colors.HexColor("#10b981")
AMBER       = colors.HexColor("#f59e0b")
RED         = colors.HexColor("#ef4444")
LIGHT_GRAY  = colors.HexColor("#f3f4f6")
DARK_GRAY   = colors.HexColor("#374151")
MID_GRAY    = colors.HexColor("#6b7280")


def _score_color(score: int):
    if score >= 70: return GREEN
    if score >= 50: return AMBER
    return RED


def _status_label(status: str) -> str:
    return {"good": "✓ Kuat", "warn": "⚠ Perlu Ditingkatkan", "bad": "✗ Lemah"}.get(status, "-")


def _priority_label(p: str) -> str:
    return {"high": "🔴 Tinggi", "medium": "🟡 Sedang", "low": "🟢 Rendah"}.get(p, p)


def export_to_pdf(result: dict, jd_preview: str = "") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Title ────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle("title", fontSize=22, textColor=PURPLE,
                                 fontName="Helvetica-Bold", spaceAfter=4)
    sub_style   = ParagraphStyle("sub", fontSize=10, textColor=MID_GRAY,
                                 fontName="Helvetica", spaceAfter=16)
    h2_style    = ParagraphStyle("h2", fontSize=14, textColor=DARK_GRAY,
                                 fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=8)
    body_style  = ParagraphStyle("body", fontSize=10, textColor=DARK_GRAY,
                                 fontName="Helvetica", leading=14, spaceAfter=6)
    note_style  = ParagraphStyle("note", fontSize=9, textColor=MID_GRAY,
                                 fontName="Helvetica-Oblique", leading=13)

    story.append(Paragraph("🎯 SmartCV Analyzer Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')} &nbsp;|&nbsp; JD Preview: {jd_preview[:80]}...",
        sub_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=16))

    # ── Match Score ──────────────────────────────────────────────────────────
    score = result.get("match_score", 0)
    score_color = _score_color(score)
    score_label = "Sangat Cocok" if score >= 70 else "Cukup Cocok" if score >= 50 else "Perlu Peningkatan"

    score_table = Table(
        [[
            Paragraph(f"<font size=36 color='{score_color.hexval()}'><b>{score}%</b></font>", styles["Normal"]),
            Paragraph(f"<b>Match Score</b><br/>{score_label}", body_style)
        ]],
        colWidths=[5*cm, None]
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("ROWPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [8]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    # ── Gap Analysis ─────────────────────────────────────────────────────────
    story.append(Paragraph("Gap Analysis per Section", h2_style))

    gap_data = [["Section", "Score", "Status", "Catatan"]]
    for section, data in result.get("gap_analysis", {}).items():
        sec_score = data.get("score", 0)
        gap_data.append([
            Paragraph(section, body_style),
            Paragraph(f"<b>{sec_score}/100</b>", body_style),
            Paragraph(_status_label(data.get("status", "warn")), body_style),
            Paragraph(data.get("note", "-"), note_style),
        ])

    gap_table = Table(gap_data, colWidths=[4*cm, 2*cm, 4*cm, None])
    gap_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(gap_table)
    story.append(Spacer(1, 16))

    # ── Suggestions ──────────────────────────────────────────────────────────
    story.append(Paragraph("Saran Perbaikan", h2_style))

    for i, sug in enumerate(result.get("suggestions", []), 1):
        priority = sug.get("priority", "medium")
        p_color = RED if priority == "high" else AMBER if priority == "medium" else GREEN
        sug_table = Table([[
            Paragraph(f"<font color='{p_color.hexval()}'><b>{_priority_label(priority)}</b></font>", body_style),
            Paragraph(f"<b>{sug.get('title','')}</b><br/>{sug.get('detail','')}", body_style)
        ]], colWidths=[3.5*cm, None])
        sug_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWPADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(sug_table)
        story.append(Spacer(1, 6))

    # ── Keywords ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Keyword Match", h2_style))

    matched = ", ".join(result.get("matched_keywords", [])) or "-"
    missing = ", ".join(result.get("missing_keywords", [])) or "-"

    kw_table = Table([
        [
            Paragraph(f"<b>✅ Keyword Ada di CV</b><br/>{matched}", body_style),
            Paragraph(f"<b>❌ Keyword Hilang</b><br/>{missing}", body_style)
        ]
    ], colWidths=["50%", "50%"])
    kw_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#d1fae5")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fee2e2")),
        ("ROWPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    story.append(kw_table)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Paragraph("Generated by SmartCV Analyzer — Powered by Groq + LLaMA 3.3", note_style))

    doc.build(story)
    return buffer.getvalue()
