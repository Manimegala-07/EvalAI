from fastapi import APIRouter, BackgroundTasks
from app.services.scoring_service import ScoringService
from app.services.feedback_service import FeedbackService

router = APIRouter()
scorer = ScoringService()
feedback_service = FeedbackService()


@router.post("/grade")
def grade(data: dict, bg: BackgroundTasks):

    refs = data["references"]
    students = data["students"]

    scores = scorer.grade_batch(refs, students)

    # Background feedback generation
    bg.add_task(
        generate_feedback_batch,
        refs,
        students,
        scores
    )

    return {"scores": scores}


def generate_feedback_batch(refs, students, scores):

    for r, s, sc in zip(refs, students, scores):

        feedback_service.generate(
            r,
            s,
            sc["score"]
        )
