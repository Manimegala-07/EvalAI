from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.db.database import get_db
from app.db.models import Answer, Question, TestQuestion, Submission
from app.services.feedback_service import FeedbackService

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

import os

router = APIRouter()


# ======================================================
# STUDENT REPORT (Lazy Ollama Generation)
# ======================================================

@router.get("/submission/{submission_id}/report")
def student_report(submission_id: int, db: Session = Depends(get_db)):

    submission = db.query(Submission)\
        .filter(Submission.id == submission_id)\
        .first()

    if not submission:
        return {"error": "Submission not found"}

    answers = db.query(Answer)\
        .filter(Answer.submission_id == submission_id)\
        .all()

    feedback_service = FeedbackService()

    total_max = 0
    response_answers = []

    for ans in answers:

        question = db.query(Question)\
            .filter(Question.id == ans.question_id)\
            .first()

        mapping = db.query(TestQuestion)\
            .filter(TestQuestion.test_id == submission.test_id)\
            .filter(TestQuestion.question_id == ans.question_id)\
            .first()

        max_score = mapping.max_score if mapping else 1
        total_max += max_score

        # 🔥 Generate Ollama feedback only if pending
        if ans.feedback_hybrid == "Pending" and ans.concept_data:

            concept = ans.concept_data

            feedback_text = feedback_service.generate(
                concept.get("correct", []),
                concept.get("missing", []),
                concept.get("extra", []),
                ans.score_hybrid
            )

            ans.feedback_hybrid = feedback_text
            db.commit()

        response_answers.append({
            "question": question.text,
            "student_answer": ans.student_answer,
            "score_minilm": ans.score_minilm,
            "score_hybrid": ans.score_hybrid,
            "max_score": max_score,
            "feedback_minilm": ans.feedback_minilm,
            "feedback_hybrid": ans.feedback_hybrid,
            "concept_data": ans.concept_data
        })

    return {
        "total_minilm": submission.total_minilm,
        "total_hybrid": submission.total_hybrid,
        "percentage_minilm": round((submission.total_minilm / total_max) * 100, 2) if total_max else 0,
        "percentage_hybrid": round((submission.total_hybrid / total_max) * 100, 2) if total_max else 0,
        "answers": response_answers
    }


# ======================================================
# DOWNLOAD PDF REPORT (Styled + Concept Aware)
# ======================================================

@router.get("/submission/{submission_id}/download")
def download_report(submission_id: int, db: Session = Depends(get_db)):

    submission = db.query(Submission)\
        .filter(Submission.id == submission_id)\
        .first()

    if not submission:
        return {"error": "Submission not found"}

    answers = db.query(Answer)\
        .filter(Answer.submission_id == submission_id)\
        .all()

    file_path = f"report_{submission_id}.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    # Custom colored styles
    green_style = ParagraphStyle(
        'GreenStyle',
        parent=styles['Normal'],
        textColor=colors.green
    )

    red_style = ParagraphStyle(
        'RedStyle',
        parent=styles['Normal'],
        textColor=colors.red
    )

    blue_style = ParagraphStyle(
        'BlueStyle',
        parent=styles['Normal'],
        textColor=colors.blue
    )

    elements = []

    elements.append(Paragraph("<b>AI Learning Evaluation Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        f"MiniLM Total: {submission.total_minilm}",
        blue_style
    ))

    elements.append(Paragraph(
        f"Hybrid Total: {submission.total_hybrid}",
        green_style
    ))

    elements.append(Spacer(1, 0.4 * inch))

    for ans in answers:

        question = db.query(Question)\
            .filter(Question.id == ans.question_id)\
            .first()

        elements.append(Paragraph(
            f"<b>Question:</b> {question.text}",
            styles["Heading3"]
        ))
        elements.append(Spacer(1, 0.1 * inch))

        elements.append(Paragraph(
            f"<b>Your Answer:</b> {ans.student_answer}",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 0.1 * inch))

        elements.append(Paragraph(
            f"MiniLM Score: {ans.score_minilm}",
            blue_style
        ))

        elements.append(Paragraph(
            f"Hybrid Score: {ans.score_hybrid}",
            green_style
        ))

        elements.append(Spacer(1, 0.2 * inch))

        # 🔥 Concept breakdown
        concept = ans.concept_data or {}

        elements.append(Paragraph(
            f"Matched Concepts: {', '.join(concept.get('correct', []))}",
            green_style
        ))

        elements.append(Paragraph(
            f"Missing Concepts: {', '.join(concept.get('missing', []))}",
            red_style
        ))

        elements.append(Paragraph(
            f"Incorrect Concepts: {', '.join(concept.get('extra', []))}",
            red_style
        ))

        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph(
            "<b>AI Feedback:</b>",
            styles["Heading4"]
        ))

        elements.append(Paragraph(
            ans.feedback_hybrid or "No feedback generated",
            styles["Normal"]
        ))

        elements.append(Spacer(1, 0.4 * inch))

    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=file_path
    )