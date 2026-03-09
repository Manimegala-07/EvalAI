from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Question, Submission, TestQuestion, Answer, Test
from app.auth.dependencies import require_student, require_teacher, get_current_user
from app.services.scoring_service import ScoringService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/submissions", tags=["Submissions"])


# ======================================================
# STUDENT: SUBMIT TEST
# ======================================================

@router.post("/submit-test")
def submit_test(
    data: dict,
    user=Depends(require_student),
    db: Session = Depends(get_db),
):
    test = db.query(Test).filter(Test.id == data["test_id"]).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    existing = db.query(Submission).filter(
        Submission.student_id == user.id,
        Submission.test_id == data["test_id"],
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted this test")

    submission = Submission(
        student_id=user.id,
        test_id=data["test_id"],
        status="pending",
    )
    db.add(submission)
    db.flush()

    for item in data["answers"]:
        answer = Answer(
            submission_id=submission.id,
            question_id=item["question_id"],
            student_answer=item["student_answer"],
            score=0.0,
            feedback="Pending evaluation",
        )
        db.add(answer)

    db.commit()
    return {
        "message": "Test submitted successfully",
        "submission_id": submission.id,
        "status": "pending",
    }


# ======================================================
# STUDENT: VIEW OWN SUBMISSIONS
# ======================================================

@router.get("/student")
def student_submissions(
    user=Depends(require_student),
    db: Session = Depends(get_db),
):
    submissions = db.query(Submission).filter(
        Submission.student_id == user.id
    ).order_by(Submission.created_at.desc()).all()

    return [
        {
            "submission_id": s.id,
            "test_id": s.test_id,
            "total_score": s.total_score,
            "status": s.status,
            "submitted_at": s.created_at,
        }
        for s in submissions
    ]


# ======================================================
# TEACHER: VIEW ALL SUBMISSIONS FOR A TEST
# ======================================================

@router.get("/test/{test_id}")
def teacher_view_submissions(
    test_id: int,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    from app.db.models import Test as TestModel, User
    test = db.query(TestModel).filter(
        TestModel.id == test_id,
        TestModel.teacher_id == user.id,
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not yours")

    submissions = db.query(Submission).filter(
        Submission.test_id == test_id
    ).all()

    result = []
    for s in submissions:
        student = db.query(User).filter(User.id == s.student_id).first()
        result.append({
            "submission_id": s.id,
            "student_id": s.student_id,
            "student_name": student.name if student else f"Student #{s.student_id}",
            "student_email": student.email if student else "",
            "total_score": s.total_score,
            "status": s.status,
            "submitted_at": s.created_at,
        })

    return result


# ======================================================
# SUBMISSION DETAIL  (used by both student & teacher)
# ======================================================

@router.get("/{submission_id}/detail")
def submission_detail(
    submission_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if user.role == "student" and submission.student_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    answers = db.query(Answer).filter(
        Answer.submission_id == submission_id
    ).all()

    total_max = 0
    result = []

    for ans in answers:
        question = db.query(Question).filter(
            Question.id == ans.question_id
        ).first()
        mapping = db.query(TestQuestion).filter(
            TestQuestion.test_id == submission.test_id,
            TestQuestion.question_id == ans.question_id,
        ).first()

        max_score = mapping.max_score if mapping else 10
        total_max += max_score

        concept_data = ans.concept_data or {}

        result.append({
            "question_id":      ans.question_id,
            "question":         question.text if question else "",
            "question_text":    question.text if question else "",
            "student_answer":   ans.student_answer,
            "score":            ans.score or 0,
            "max_score":        max_score,
            "similarity":       ans.similarity or 0,
            "entailment":       ans.entailment or 0,
            "coverage":         ans.coverage or 0,
            "length_ratio":     ans.length_ratio or 0,
            "confidence":       ans.confidence or 0,
            "feedback":         ans.feedback,
            "concept_data":     concept_data,
            "concept_heatmap":  concept_data,
            "sentence_heatmap": ans.sentence_heatmap or [],
        })

    percentage = round(
        (submission.total_score / total_max) * 100, 2
    ) if total_max else 0

    return {
        "submission_id": submission.id,
        "student_id":    submission.student_id,
        "test_id":       submission.test_id,
        "total_score":   submission.total_score,
        "total_max":     total_max,
        "percentage":    percentage,
        "status":        submission.status,
        "answers":       result,
    }


# ======================================================
# BATCH EVALUATION
# ======================================================

@router.post("/evaluate/{test_id}")
def evaluate_test(
    test_id: int,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    from app.db.models import Test as TestModel
    test = db.query(TestModel).filter(
        TestModel.id == test_id,
        TestModel.teacher_id == user.id,
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not yours")

    submissions = db.query(Submission).filter(
        Submission.test_id == test_id,
        Submission.status == "pending",
    ).all()

    if not submissions:
        return {"message": "No pending submissions", "evaluated_count": 0}

    scorer = ScoringService()
    llm = LLMService()

    for sub in submissions:
        answers = db.query(Answer).filter(
            Answer.submission_id == sub.id
        ).all()

        total_score = 0.0

        for ans in answers:
            question = db.query(Question).filter(
                Question.id == ans.question_id
            ).first()
            if not question:
                continue

            mapping = db.query(TestQuestion).filter(
                TestQuestion.test_id == test_id,
                TestQuestion.question_id == ans.question_id,
            ).first()
            max_score = mapping.max_score if mapping else 10

            # Guard against empty answers
            student_text = (ans.student_answer or "").strip()
            if not student_text or len(student_text.split()) < 3:
                ans.score    = 0.0
                ans.feedback = "No meaningful answer provided."
                ans.concept_data = {
                    "covered": [], "partial": [], "missing": [], "wrong": [],
                    "concept_details": [], "coverage": 0.0, "wrong_ratio": 0.0,
                    "status": "weak",
                }
                continue

            # ── Run hybrid pipeline ───────────────────────────
            result = scorer.grade_single(
                question.model_answer,
                student_text,
                max_score=max_score,
            )

            score           = result["score"]
            concept_results = result["concept_results"]
            total_score    += score

            # ── Categorise concepts ───────────────────────────
            covered = [c["concept"] for c in concept_results if c["status"] == "matched"]
            partial = [c["concept"] for c in concept_results if c["status"] == "partial"]
            missing = [c["concept"] for c in concept_results if c["status"] == "missing"]
            wrong   = [c["concept"] for c in concept_results if c["status"] == "wrong"]

            concept_details = [
                {
                    "concept":     c["concept"],
                    "status":      c["status"],
                    "coverage":    c["coverage"],
                    "covered_kws": c.get("covered_kws", []),
                    "missing_kws": c.get("missing_kws", []),
                }
                for c in concept_results
            ]

            # ── Gemini feedback ───────────────────────────────
            prompt = f"""
You are an academic evaluator giving feedback to a student.

Question: {question.text}
Student Answer: {student_text}
Score: {score} / {max_score}

Concepts correctly covered:
{chr(10).join(f'- {c}' for c in covered) or '- None'}

Concepts partially covered:
{chr(10).join(f'- {c}' for c in partial) or '- None'}

Concepts missing:
{chr(10).join(f'- {c}' for c in missing) or '- None'}

Concepts answered incorrectly:
{chr(10).join(f'- {c}' for c in wrong) or '- None'}

Write 3-5 sentences of constructive feedback. Tell the student what they got
right, what concepts they missed, and specifically how to improve.
Be encouraging but honest.
"""
            try:
                feedback = llm.model.generate_content(prompt).text

            except Exception:
                # ── Meaningful fallback using actual concept data ──
                parts = [f"Score: {score}/{max_score}."]
                if covered:
                    parts.append(
                        f"Well done on correctly covering: "
                        f"{'; '.join(c[:80] for c in covered[:3])}."
                    )
                if wrong:
                    parts.append(
                        f"Incorrect information detected in: "
                        f"{'; '.join(c[:80] for c in wrong[:2])}. "
                        f"Please review these carefully."
                    )
                if missing:
                    parts.append(
                        f"Key concepts not addressed: "
                        f"{'; '.join(c[:80] for c in missing[:3])}."
                    )
                if partial:
                    parts.append(
                        f"Needs more detail: "
                        f"{'; '.join(c[:80] for c in partial[:2])}."
                    )
                if not any([covered, missing, partial, wrong]):
                    parts.append(
                        "Re-evaluate this submission to generate detailed concept feedback."
                    )
                feedback = " ".join(parts)

            # ── Save all results ──────────────────────────────
            ans.score         = score
            ans.similarity    = result["similarity"]
            ans.entailment    = result["entailment"]
            ans.coverage      = result["coverage"]
            ans.length_ratio  = result["length_ratio"]
            ans.confidence    = result["confidence"]
            ans.feedback      = feedback

            ans.concept_data = {
                "covered":         covered,
                "partial":         partial,
                "missing":         missing,
                "wrong":           wrong,
                "concept_details": concept_details,
                "coverage":        result["coverage"],
                "wrong_ratio":     result["wrong_ratio"],
                "status": (
                    "strong"  if result["coverage"] > 0.65 else
                    "partial" if result["coverage"] > 0.35 else
                    "weak"
                ),
            }
            ans.sentence_heatmap = result["sentence_heatmap"]

        sub.total_score = round(total_score, 2)
        sub.status      = "evaluated"

    db.commit()

    return {
        "message":         "Batch evaluation completed",
        "evaluated_count": len(submissions),
    }