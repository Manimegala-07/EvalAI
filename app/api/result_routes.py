from fastapi import APIRouter
from app.db.crud import get_test_results

router = APIRouter()


@router.get("/test-results/{test_id}")
def get_results(test_id: int):

    results = get_test_results(test_id)

    return [
        {
            "question_id": r.question_id,
            "score": r.score,
            "feedback": r.feedback
        }
        for r in results
    ]
