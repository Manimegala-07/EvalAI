import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Answer, Question, TestQuestion, Submission, Test, User
from app.auth.dependencies import get_current_user

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

router = APIRouter(prefix="/reports", tags=["Reports"])

# ─────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────
INK        = colors.HexColor("#1A1A2E")
INK_LIGHT  = colors.HexColor("#4A4A6A")
INK_MUTED  = colors.HexColor("#8888AA")
ACCENT     = colors.HexColor("#2D5BE3")
ACCENT_BG  = colors.HexColor("#EEF2FF")
GREEN      = colors.HexColor("#16A34A")
GREEN_BG   = colors.HexColor("#DCFCE7")
RED        = colors.HexColor("#DC2626")
RED_BG     = colors.HexColor("#FEE2E2")
AMBER      = colors.HexColor("#D97706")
AMBER_BG   = colors.HexColor("#FEF3C7")
BORDER     = colors.HexColor("#E8E6F0")
CREAM      = colors.HexColor("#FAF8F4")
WHITE      = colors.white


def build_styles():
    styles = {
        "title": ParagraphStyle("ReportTitle", fontName="Helvetica-Bold",
            fontSize=22, textColor=WHITE, spaceAfter=4, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("ReportSubtitle", fontName="Helvetica",
            fontSize=11, textColor=colors.HexColor("#C7D4FA"), spaceAfter=2, alignment=TA_LEFT),
        "section": ParagraphStyle("Section", fontName="Helvetica-Bold",
            fontSize=13, textColor=INK, spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("Body", fontName="Helvetica",
            fontSize=10, textColor=INK, leading=15, spaceAfter=4),
        "body_muted": ParagraphStyle("BodyMuted", fontName="Helvetica",
            fontSize=9, textColor=INK_MUTED, leading=13, spaceAfter=3),
        "label": ParagraphStyle("Label", fontName="Helvetica-Bold",
            fontSize=8, textColor=INK_MUTED, spaceAfter=2),
        "answer_text": ParagraphStyle("AnswerText", fontName="Helvetica",
            fontSize=10, textColor=INK, leading=14, leftIndent=8, spaceAfter=4),
        "feedback": ParagraphStyle("Feedback", fontName="Helvetica",
            fontSize=10, textColor=colors.HexColor("#1e3a8a"), leading=15,
            leftIndent=8, spaceAfter=4),
        "q_title": ParagraphStyle("QTitle", fontName="Helvetica-Bold",
            fontSize=11, textColor=INK, spaceBefore=4, spaceAfter=6, leading=16),
        "concept_matched": ParagraphStyle("ConceptMatched", fontName="Helvetica",
            fontSize=9, textColor=GREEN, leftIndent=12, spaceAfter=2),
        "concept_missing": ParagraphStyle("ConceptMissing", fontName="Helvetica",
            fontSize=9, textColor=RED, leftIndent=12, spaceAfter=2),
        "concept_wrong": ParagraphStyle("ConceptWrong", fontName="Helvetica",
            fontSize=9, textColor=AMBER, leftIndent=12, spaceAfter=2),
        "concept_partial": ParagraphStyle("ConceptPartial", fontName="Helvetica",
            fontSize=9, textColor=AMBER, leftIndent=12, spaceAfter=2),
    }
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(ACCENT)
    canvas.rect(0, h - 6, w, 6, fill=1, stroke=0)
    canvas.setFillColor(BORDER)
    canvas.rect(0, 0, w, 28, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(40, 10, "EvalAI Academic Evaluation Platform")
    canvas.drawRightString(w - 40, 10, f"Page {doc.page}")
    canvas.restoreState()


def score_to_color(score, max_score):
    pct = score / max_score if max_score else 0
    if pct >= 0.75:
        return GREEN, GREEN_BG
    elif pct >= 0.5:
        return AMBER, AMBER_BG
    return RED, RED_BG


# ─────────────────────────────────────────────────────────────
# HELPER: fetch and assemble submission data
# ─────────────────────────────────────────────────────────────

def _get_submission_data(submission_id: int, db: Session):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    answers = db.query(Answer).filter(Answer.submission_id == submission_id).all()

    total_max = 0
    answer_data = []

    for ans in answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        mapping = db.query(TestQuestion).filter(
            TestQuestion.test_id == submission.test_id,
            TestQuestion.question_id == ans.question_id,
        ).first()

        max_score = mapping.max_score if mapping else 10
        total_max += max_score

        concept_data = ans.concept_data or {}

        answer_data.append({
            "question":          question.text if question else "",
            "question_text":     question.text if question else "",
            "student_answer":    ans.student_answer or "",
            "score":             ans.score or 0,
            "max_score":         max_score,
            "similarity":        ans.similarity or 0,
            "entailment":        ans.entailment or 0,
            "coverage":          ans.coverage or 0,
            "length_ratio":      ans.length_ratio or 0,
            "confidence":        ans.confidence or 0,
            "feedback":          ans.feedback or "",
            "concept_data":      concept_data,
            "concept_heatmap":   concept_data,
            "sentence_heatmap":  ans.sentence_heatmap or [],
        })

    percentage = round((submission.total_score / total_max) * 100, 2) if total_max else 0

    return submission, answer_data, total_max, percentage


# ─────────────────────────────────────────────────────────────
# VIEW REPORT (JSON)
# FIX: Now returns ALL fields the frontend needs (heatmap, metrics etc.)
# ─────────────────────────────────────────────────────────────

@router.get("/submission/{submission_id}")
def student_report(
    submission_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission, answer_data, total_max, percentage = _get_submission_data(
        submission_id, db
    )

    # Auth check
    if user.role == "student" and submission.student_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "submission_id": submission_id,
        "total_score":   submission.total_score,
        "total_max":     total_max,
        "percentage":    percentage,
        "status":        submission.status,
        "answers":       answer_data,
    }


# ─────────────────────────────────────────────────────────────
# DOWNLOAD PDF REPORT
# FIX: temp file is cleaned up after response
# ─────────────────────────────────────────────────────────────

@router.get("/submission/{submission_id}/download")
def download_report(
    submission_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission, answer_data, total_max, percentage = _get_submission_data(
        submission_id, db
    )

    if user.role == "student" and submission.student_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    student = db.query(User).filter(User.id == submission.student_id).first()
    test = db.query(Test).filter(Test.id == submission.test_id).first()

    grade = (
        "Distinction" if percentage >= 75 else
        "Pass"        if percentage >= 50 else
        "Needs Improvement"
    )

    # ── Build PDF ────────────────────────────────────────────
    # FIX: use delete=True so OS cleans up; we copy to named path first
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_path = tmp.name
    tmp.close()

    doc = SimpleDocTemplate(
        tmp_path, pagesize=A4,
        leftMargin=40, rightMargin=40,
        topMargin=50, bottomMargin=50,
    )

    S = build_styles()
    story = []
    W = A4[0] - 80

    student_name  = student.name if student else f"Student #{submission.student_id}"
    student_email = student.email if student else ""
    institution   = student.institution if student and student.institution else "—"
    test_title    = test.title if test else f"Test #{submission.test_id}"

    # ── Cover header ─────────────────────────────────────────
    header_rows = [
        Paragraph("EvalAI Evaluation Report", S["title"]),
        Paragraph(test_title, S["subtitle"]),
        Spacer(1, 8),
        Paragraph(f"Student: {student_name}  |  {student_email}", S["subtitle"]),
        Paragraph(f"Institution: {institution}", S["subtitle"]),
    ]
    header_table = Table([[r] for r in header_rows], colWidths=[W])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))

    # ── Stat cards ───────────────────────────────────────────
    sc, sc_bg = score_to_color(submission.total_score, total_max)

    def stat_cell(val, lbl, fg, bg):
        t = Table([
            [Paragraph(str(val), ParagraphStyle("sv", fontName="Helvetica-Bold",
                fontSize=24, textColor=fg, alignment=TA_CENTER))],
            [Paragraph(lbl, ParagraphStyle("sl", fontName="Helvetica",
                fontSize=8, textColor=INK_MUTED, alignment=TA_CENTER))],
        ], colWidths=[120])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), bg),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("BOX",           (0, 0), (-1, -1), 1, BORDER),
        ]))
        return t

    stats = Table([[
        stat_cell(f"{submission.total_score}", "Total Score", sc, sc_bg),
        stat_cell(f"{percentage}%",            "Percentage",  sc, sc_bg),
        stat_cell(str(len(answer_data)),        "Questions",   ACCENT, ACCENT_BG),
        stat_cell(grade,                        "Grade",       sc, sc_bg),
    ]], colWidths=[120, 120, 120, 120], hAlign="CENTER")
    stats.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(stats)
    story.append(Spacer(1, 20))

    # ── Score overview table ─────────────────────────────────
    story.append(Paragraph("Score Overview", S["section"]))
    story.append(HRFlowable(width=W, thickness=1, color=BORDER, spaceAfter=8))

    ov_data = [["#", "Question", "Score", "Max", "Coverage", "Confidence"]]
    for i, ans in enumerate(answer_data, 1):
        qshort = ans["question"][:55] + "..." if len(ans["question"]) > 55 else ans["question"]
        asc, _ = score_to_color(ans["score"], ans["max_score"])
        ov_data.append([
            str(i),
            Paragraph(qshort, S["body_muted"]),
            Paragraph(f"<b>{ans['score']}</b>", ParagraphStyle(
                "sc", fontName="Helvetica-Bold", fontSize=10,
                textColor=asc, alignment=TA_CENTER)),
            str(int(ans["max_score"])),
            f"{int(ans['coverage'] * 100)}%",
            f"{int(ans['confidence'] * 100)}%",
        ])

    ov_table = Table(ov_data, colWidths=[25, 240, 50, 40, 65, 65])
    ov_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",        (1, 0), (1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
        ("GRID",         (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(ov_table)
    story.append(Spacer(1, 24))

    # ── Per-question breakdown ───────────────────────────────
    story.append(Paragraph("Detailed Answer Breakdown", S["section"]))
    story.append(HRFlowable(width=W, thickness=1, color=BORDER, spaceAfter=12))

    for i, ans in enumerate(answer_data, 1):
        sc2, sc2_bg = score_to_color(ans["score"], ans["max_score"])
        q_block = []

        q_hdr = Table([[
            Paragraph(f"Question {i}", ParagraphStyle("qn",
                fontName="Helvetica-Bold", fontSize=9, textColor=ACCENT)),
            Paragraph(f"<b>{ans['score']}</b> / {int(ans['max_score'])}",
                ParagraphStyle("qs", fontName="Helvetica-Bold", fontSize=14,
                    textColor=sc2, alignment=TA_RIGHT)),
        ]], colWidths=[W - 80, 80])
        q_hdr.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND",    (0, 0), (-1, -1), ACCENT_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))
        q_block.append(q_hdr)

        for label, text, bg in [
            ("QUESTION",     ans["question"],       WHITE),
            ("YOUR ANSWER",  ans["student_answer"], WHITE),
        ]:
            lbl_t = Table([[Paragraph(label, S["label"])]], colWidths=[W])
            lbl_t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), CREAM),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            body_t = Table([[Paragraph(text, S["answer_text"])]], colWidths=[W])
            body_t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), bg),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            q_block.append(lbl_t)
            q_block.append(body_t)

        # Metrics
        metrics = [
            ("Similarity", ans["similarity"]),
            ("Entailment", ans["entailment"]),
            ("Coverage",   ans["coverage"]),
            ("Confidence", ans["confidence"]),
        ]
        col_w = (W - 30) / 4
        m_cells = []
        for m_label, m_val in metrics:
            mc = GREEN if m_val >= 0.7 else AMBER if m_val >= 0.4 else RED
            m_cells.append(Table([
                [Paragraph(f"{int(m_val*100)}%", ParagraphStyle("mv",
                    fontName="Helvetica-Bold", fontSize=11,
                    textColor=mc, alignment=TA_CENTER))],
                [Paragraph(m_label, ParagraphStyle("ml", fontName="Helvetica",
                    fontSize=7, textColor=INK_MUTED, alignment=TA_CENTER))],
            ], colWidths=[col_w]))
        m_row = Table([m_cells], colWidths=[col_w] * 4)
        m_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), CREAM),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ("LINEAFTER",     (0, 0), (2, 0), 0.5, BORDER),
        ]))
        q_block.append(m_row)

        # Concept heatmap
        cd = ans.get("concept_data", {})
        if cd:
            covered = cd.get("covered", [])
            partial = cd.get("partial", [])
            missing = cd.get("missing", [])
            wrong   = cd.get("wrong", [])

            heatmap_rows = [
                Table([[Paragraph("CONCEPT HEATMAP", S["label"])]], colWidths=[W])
            ]
            for section_label, items, style_key, symbol in [
                ("✓ Covered",  covered, "concept_matched", "•"),
                ("~ Partial",  partial, "concept_partial", "•"),
                ("✗ Missing",  missing, "concept_missing", "•"),
                ("⚠ Incorrect",wrong,   "concept_wrong",   "•"),
            ]:
                if items:
                    heatmap_rows.append(Paragraph(section_label, ParagraphStyle(
                        "hh", fontName="Helvetica-Bold", fontSize=9,
                        textColor=S[style_key].textColor, leftIndent=12, spaceAfter=3)))
                    for c in items:
                        heatmap_rows.append(Paragraph(f"  {symbol} {c}", S[style_key]))

            ht = Table([[r] for r in heatmap_rows], colWidths=[W])
            ht.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
                ("BACKGROUND",    (0, 0), (0, 0), CREAM),
            ]))
            q_block.append(ht)

        # Feedback
        if ans.get("feedback"):
            fb_lbl = Table([[Paragraph("AI FEEDBACK", S["label"])]], colWidths=[W])
            fb_lbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), ACCENT_BG),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D4FA")),
            ]))
            fb_body = Table([[Paragraph(ans["feedback"], S["feedback"])]], colWidths=[W])
            fb_body.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F0FF")),
                ("TOPPADDING",    (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D4FA")),
            ]))
            q_block.append(fb_lbl)
            q_block.append(fb_body)

        story.append(KeepTogether(q_block))
        story.append(Spacer(1, 20))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    filename = f"EvalAI_{student_name.replace(' ', '_')}_{submission_id}.pdf"

    # FIX: Use BackgroundTask to delete temp file after response is sent
    from starlette.background import BackgroundTask

    def cleanup():
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return FileResponse(
        tmp_path,
        media_type="application/pdf",
        filename=filename,
        background=BackgroundTask(cleanup),
    )