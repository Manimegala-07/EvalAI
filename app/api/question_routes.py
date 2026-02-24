from fastapi import APIRouter
from app.db.database import SessionLocal
from app.db.models import Question

router = APIRouter()


@router.post("/questions")
def add_question(data: dict):

    db = SessionLocal()

    q = Question(
        text=data["text"],
        model_answer=data["model_answer"]
    )

    db.add(q)
    db.commit()
    db.refresh(q)

    question_id = q.id

    db.close()

    return {"question_id": question_id}


@router.get("/questions")
def list_questions():

    db = SessionLocal()

    questions = db.query(Question).all()

    db.close()

    return [
        {
            "id": q.id,
            "text": q.text,
            "model_answer": q.model_answer
        }
        for q in questions
    ]
