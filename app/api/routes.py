from fastapi import APIRouter, BackgroundTasks
from app.services.scoring_service import ScoringService
from app.workers.background_tasks import generate_feedback_task

router = APIRouter()
scorer = ScoringService()


@router.post("/grade")
def grade(request: dict, background_tasks: BackgroundTasks):

    refs = request["references"]
    students = request["students"]

    scores = scorer.grade_batch(refs, students)

    background_tasks.add_task(
        generate_feedback_task,
        refs,
        students,
        scores
    )

    return {"scores": scores}
