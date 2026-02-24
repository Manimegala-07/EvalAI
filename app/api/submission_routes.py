from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.db.models import Question, Submission, TestQuestion, Answer
from app.db.crud import create_submission
from app.auth.dependencies import require_student
from app.services.scoring_service import ScoringService

router = APIRouter()


# ======================================================
# STUDENT SUBMIT (FAST - NO SCORING)
# ======================================================

@router.post("/submit-test")
def submit_test(
    data: dict,
    user=Depends(require_student),
):

    db = SessionLocal()

    # Check duplicate
    existing = db.query(Submission)\
        .filter(Submission.student_id == user.id)\
        .filter(Submission.test_id == data["test_id"])\
        .first()

    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Test already submitted")

    # Create submission
    submission_id = create_submission(db, user.id, data["test_id"])

    for item in data["answers"]:

        mapping = db.query(TestQuestion)\
            .filter(TestQuestion.test_id == data["test_id"])\
            .filter(TestQuestion.question_id == item["question_id"])\
            .first()

        if not mapping:
            db.close()
            raise HTTPException(status_code=400, detail="Invalid question")

        answer = Answer(
            submission_id=submission_id,
            question_id=item["question_id"],
            student_answer=item["student_answer"],
            score_minilm=0,
            score_hybrid=0,
            feedback_minilm="Pending",
            feedback_hybrid="Pending"
        )

        db.add(answer)

    submission = db.query(Submission)\
        .filter(Submission.id == submission_id)\
        .first()

    submission.total_minilm = 0
    submission.total_hybrid = 0
    submission.status = "pending"

    db.commit()
    db.close()

    return {
        "submission_id": submission_id,
        "message": "Submitted successfully. Awaiting evaluation."
    }


# ======================================================
# TEACHER EVALUATE
# ======================================================

@router.post("/evaluate-test/{test_id}")
def evaluate_test(test_id: int, mode: str, db: Session = Depends(get_db)):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .all()

    if not submissions:
        return {"message": "No submissions found"}

    scorer = ScoringService()

    for sub in submissions:

        answers = db.query(Answer)\
            .filter(Answer.submission_id == sub.id)\
            .all()

        total_score = 0

        for ans in answers:

            question = db.query(Question)\
                .filter(Question.id == ans.question_id)\
                .first()

            mapping = db.query(TestQuestion)\
                .filter(TestQuestion.test_id == test_id)\
                .filter(TestQuestion.question_id == ans.question_id)\
                .first()

            max_score = mapping.max_score

            result = scorer.grade_batch(
                [question.model_answer],
                [ans.student_answer],
                max_score,
                mode=mode
            )[0]

            if mode == "minilm":
                ans.score_minilm = result["score"]
                ans.feedback_minilm = "Pending"
            else:
                ans.score_hybrid = result["score"]
                ans.feedback_hybrid = "Pending"
            # 🔥 store concept heatmap    
            ans.concept_data = result["concept_data"]

            total_score += result["score"]

        if mode == "minilm":
            sub.total_minilm = round(total_score, 2)
        else:
            sub.total_hybrid = round(total_score, 2)

        sub.status = "evaluated"

    db.commit()

    return {
        "message": f"Evaluation completed using {mode.upper()} pipeline"
    }


# ======================================================
# STUDENT VIEW SUBMISSIONS
# ======================================================

@router.get("/student/submissions")
def student_submissions(
    user=Depends(require_student),
    db: Session = Depends(get_db)
):

    submissions = db.query(Submission)\
        .filter(Submission.student_id == user.id)\
        .all()

    return [
        {
            "test_id": s.test_id,
            "submission_id": s.id,
            "total_minilm": s.total_minilm,
            "total_hybrid": s.total_hybrid,
            "status": s.status
        }
        for s in submissions
    ]