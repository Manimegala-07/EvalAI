from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Submission, Answer, TestQuestion
from app.db.models import Question

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/tests/{test_id}")
def test_analytics(test_id: int, mode: str = "hybrid", db: Session = Depends(get_db)):

    submissions = db.query(Submission).filter(
        Submission.test_id == test_id
    ).all()

    if not submissions:
        return {"message": "No submissions yet"}

    student_scores = []
    question_perf = {}

    for sub in submissions:

        # choose total based on mode
        if mode == "minilm":
            total = sub.total_minilm
        else:
            total = sub.total_hybrid

        student_scores.append({
            "student_id": sub.student_id,
            "score": total
        })

        answers = db.query(Answer).filter(
            Answer.submission_id == sub.id
        ).all()

        for ans in answers:

            # choose question score based on mode
            if mode == "minilm":
                score = ans.score_minilm
            else:
                score = ans.score_hybrid

            question_perf.setdefault(ans.question_id, []).append(score)

@router.get("/tests/{test_id}/detailed")
def detailed_analytics(test_id: int, db: Session = Depends(get_db)):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .all()

    if not submissions:
        return {"message": "No submissions found"}

    result = []

    for sub in submissions:

        answers = db.query(Answer)\
            .filter(Answer.submission_id == sub.id)\
            .all()

        answer_list = []

        for ans in answers:

            question = db.query(Question)\
                .filter(Question.id == ans.question_id)\
                .first()

            answer_list.append({
                "question": question.text,
                "student_answer": ans.student_answer,
                "minilm_score": ans.score_minilm,
                "hybrid_score": ans.score_hybrid,
                "concept_data": ans.concept_data
            })

        result.append({
            "student_id": sub.student_id,
            "total_minilm": sub.total_minilm,
            "total_hybrid": sub.total_hybrid,
            "answers": answer_list
        })

    return {"students": result}
    # =============================
    # CLASS STATS
    # =============================

    scores = [s["score"] for s in student_scores]

    average = round(sum(scores) / len(scores), 2)
    highest = max(scores)
    lowest = min(scores)

    ranking = sorted(student_scores, key=lambda x: x["score"], reverse=True)

    # =============================
    # QUESTION DIFFICULTY
    # =============================

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
        "mode": mode,
        "average_score": average,
        "highest_score": highest,
        "lowest_score": lowest,
        "ranking": ranking,
        "question_analysis": question_analysis
    }