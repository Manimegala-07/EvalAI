from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Test, Submission, User, Question

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):

    total_tests = db.query(Test).count()
    total_questions = db.query(Question).count()
    total_submissions = db.query(Submission).count()
    total_students = db.query(User)\
        .filter(User.role == "student")\
        .count()

    pending_count = db.query(Submission)\
        .filter(Submission.status == "pending")\
        .count()

    scores = db.query(Submission.total_score)\
        .filter(Submission.status == "evaluated")\
        .all()

    scores = [s[0] for s in scores if s[0] is not None]

    average_score = round(sum(scores)/len(scores), 2) if scores else 0

    return {
        "total_tests": total_tests,
        "total_questions": total_questions,
        "total_submissions": total_submissions,
        "total_students": total_students,
        "pending_evaluations": pending_count,
        "average_score": average_score
    }

@router.get("/tests")
def get_tests(db: Session = Depends(get_db)):

    tests = db.query(Test).all()

    return [
        {
            "id": t.id,
            "title": t.title
        }
        for t in tests
    ]