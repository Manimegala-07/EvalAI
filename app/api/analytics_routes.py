from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Submission, Answer, TestQuestion, Question

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ======================================================
# CLASS LEVEL ANALYTICS
# ======================================================

@router.get("/tests/{test_id}")
def test_analytics(test_id: int, db: Session = Depends(get_db)):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .filter(Submission.status == "evaluated")\
        .all()

    if not submissions:
        return {"message": "No evaluated submissions yet"}

    student_scores = []
    question_perf = {}

    for sub in submissions:

        student_scores.append({
            "student_id": sub.student_id,
            "score": sub.total_score
        })

        answers = db.query(Answer)\
            .filter(Answer.submission_id == sub.id)\
            .all()

        for ans in answers:
            question_perf.setdefault(ans.question_id, []).append(ans.score)

    scores = [s["score"] for s in student_scores]

    average = round(sum(scores) / len(scores), 2)
    highest = max(scores)
    lowest = min(scores)

    ranking = sorted(student_scores, key=lambda x: x["score"], reverse=True)

    question_analysis = {}

    for qid, vals in question_perf.items():

        mapping = db.query(TestQuestion)\
            .filter(TestQuestion.test_id == test_id)\
            .filter(TestQuestion.question_id == qid)\
            .first()

        max_score = mapping.max_score if mapping else 1

        avg = sum(vals) / len(vals)
        difficulty = round(1 - (avg / max_score), 2)

        question_analysis[qid] = {
            "average_score": round(avg, 2),
            "difficulty_index": difficulty
        }

    return {
        "average_score": average,
        "highest_score": highest,
        "lowest_score": lowest,
        "ranking": ranking,
        "question_analysis": question_analysis
    }