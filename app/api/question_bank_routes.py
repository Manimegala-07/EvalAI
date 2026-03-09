from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from statistics import variance
from app.db.database import get_db
from app.db.models import Question, Answer, TestQuestion, Submission

router = APIRouter(prefix="/question-bank", tags=["Question Bank"])


@router.get("/full-analytics")
def question_bank_full_analytics(db: Session = Depends(get_db)):

    questions = db.query(Question).all()

    result = []
    concept_failures = {}
    contradiction_count = {}

    for q in questions:

        answers = db.query(Answer)\
            .filter(Answer.question_id == q.id)\
            .all()

        if not answers:
            continue

        total_attempts = len(answers)
        hybrid_scores = [a.score_hybrid for a in answers]

        avg_score = sum(hybrid_scores) / total_attempts

        mapping = db.query(TestQuestion)\
            .filter(TestQuestion.question_id == q.id)\
            .first()

        max_score = mapping.max_score if mapping else 10

        difficulty_index = round(1 - (avg_score / max_score), 2)

        success_rate = sum(
            1 for s in hybrid_scores if s >= 0.5 * max_score
        ) / total_attempts

        score_variance = variance(hybrid_scores) if len(hybrid_scores) > 1 else 0

        # 🔥 Concept analytics
        for ans in answers:
            if ans.concept_data:

                for m in ans.concept_data.get("missing", []):
                    concept_failures[m] = concept_failures.get(m, 0) + 1

                if ans.concept_data.get("contradiction"):
                    contradiction_count[q.id] = contradiction_count.get(q.id, 0) + 1

        result.append({
            "question_id": q.id,
            "question_text": q.text,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 2),
            "difficulty_index": difficulty_index,
            "success_rate": round(success_rate * 100, 2),
            "score_variance": round(score_variance, 2),
            "contradictions": contradiction_count.get(q.id, 0)
        })

    # Top analytics
    hardest = sorted(result, key=lambda x: x["difficulty_index"], reverse=True)[:5]
    easiest = sorted(result, key=lambda x: x["success_rate"], reverse=True)[:5]
    most_variable = sorted(result, key=lambda x: x["score_variance"], reverse=True)[:5]

    top_failed_concepts = sorted(concept_failures.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "questions": result,
        "top_hardest": hardest,
        "top_easiest": easiest,
        "most_variable_questions": most_variable,
        "most_failed_concepts": top_failed_concepts
    }