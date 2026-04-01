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
            question_perf.setdefault(ans.question_id, []).append({
                "score":      ans.score,
                "confidence": ans.confidence,
                "rf_score":   ans.rf_score,
            })

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

        scores_list = [v["score"] for v in vals]
        avg = sum(scores_list) / len(scores_list)
        difficulty = round(1 - (avg / max_score), 2)

        conf_vals = [v["confidence"] for v in vals if v["confidence"] is not None]
        rf_vals   = [v["rf_score"]   for v in vals if v["rf_score"]   is not None]

        question_analysis[qid] = {
            "average_score":    round(avg, 2),
            "difficulty_index": difficulty,
            "avg_confidence":   round(sum(conf_vals) / len(conf_vals), 3) if conf_vals else None,
            "avg_rf_score":     round(sum(rf_vals)   / len(rf_vals),   2) if rf_vals   else None,
            "low_confidence_count": sum(1 for c in conf_vals if c < 0.75),
        }

    all_conf = [
        v["confidence"]
        for vals in question_perf.values()
        for v in vals if v["confidence"] is not None
    ]

    return {
        "average_score": average,
        "highest_score": highest,
        "lowest_score": lowest,
        "ranking": ranking,
        "question_analysis": question_analysis,
        "confidence_summary": {
            "avg_confidence":       round(sum(all_conf) / len(all_conf), 3) if all_conf else None,
            "low_confidence_count": sum(1 for c in all_conf if c < 0.75),
            "total_answers":        len(all_conf),
        },
    }