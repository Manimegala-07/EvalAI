from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Test, TestQuestion, Question, Submission
from app.auth.dependencies import require_teacher, require_student, get_current_user

router = APIRouter(prefix="/tests", tags=["Tests"])

DEFAULT_CO_OUTCOMES = {
    "CO1": "Knowledge & Recall — Student can recall and state facts, definitions, and basic concepts",
    "CO2": "Comprehension — Student can explain and describe concepts in their own words",
    "CO3": "Application — Student can apply concepts to solve problems or real situations",
    "CO4": "Analysis — Student can break down, compare, and examine relationships",
    "CO5": "Evaluation — Student can justify, assess, and make judgments",
    "CO6": "Creation — Student can design, construct, or produce something new",
}


@router.get("")
def list_tests(user=Depends(require_teacher), db: Session = Depends(get_db)):
    tests = db.query(Test).filter(Test.teacher_id == user.id).all()
    result = []
    for t in tests:
        q_count    = db.query(TestQuestion).filter(TestQuestion.test_id == t.id).count()
        s_count    = db.query(Submission).filter(Submission.test_id == t.id).count()
        s_evaluated = db.query(Submission).filter(Submission.test_id == t.id, Submission.status == "evaluated").count()
        result.append({
            "id": t.id, "title": t.title, "teacher_id": t.teacher_id,
            "question_count": q_count, "submission_count": s_count, "evaluated_count": s_evaluated,
            "due_date": t.due_date, "time_limit_minutes": t.time_limit_minutes,
            "co_outcomes": t.co_outcomes or DEFAULT_CO_OUTCOMES,
            "created_at": t.created_at,
        })
    return result


@router.get("/student")
def list_tests_for_student(user=Depends(require_student), db: Session = Depends(get_db)):
    tests = db.query(Test).all()
    return [{"id": t.id, "title": t.title, "due_date": t.due_date, "time_limit_minutes": t.time_limit_minutes, "created_at": t.created_at} for t in tests]


@router.post("")
def create_test(data: dict, user=Depends(require_teacher), db: Session = Depends(get_db)):
    if not data.get("title"):
        raise HTTPException(status_code=400, detail="title is required")

    # Use custom CO outcomes if provided, else use defaults
    co_outcomes = data.get("co_outcomes") or DEFAULT_CO_OUTCOMES

    test = Test(
        title=data["title"],
        teacher_id=user.id,
        due_date=data.get("due_date"),
        time_limit_minutes=data.get("time_limit_minutes"),
        co_outcomes=co_outcomes,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"id": test.id, "title": test.title, "co_outcomes": test.co_outcomes}


@router.put("/{test_id}/co-outcomes")
def update_co_outcomes(test_id: int, data: dict, user=Depends(require_teacher), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    test.co_outcomes = data.get("co_outcomes", DEFAULT_CO_OUTCOMES)
    db.commit()
    return {"message": "CO outcomes updated", "co_outcomes": test.co_outcomes}


@router.get("/{test_id}")
def get_test(test_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    tqs = db.query(TestQuestion).filter(TestQuestion.test_id == test_id).all()
    questions = []
    for tq in tqs:
        q = db.query(Question).filter(Question.id == tq.question_id).first()
        if q:
            questions.append({
                "id": q.id, "text": q.text, "max_score": tq.max_score,
                "co_mapping": tq.co_mapping,
                "difficulty": q.difficulty, "blooms_level": q.blooms_level,
            })

    return {
        "id": test.id, "title": test.title,
        "due_date": test.due_date, "time_limit_minutes": test.time_limit_minutes,
        "co_outcomes": test.co_outcomes or DEFAULT_CO_OUTCOMES,
        "questions": questions,
    }


@router.post("/{test_id}/questions")
def add_question_to_test(test_id: int, data: dict, user=Depends(require_teacher), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not yours")

    existing = db.query(TestQuestion).filter(TestQuestion.test_id == test_id, TestQuestion.question_id == data["question_id"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question already in test")

    tq = TestQuestion(
        test_id=test_id,
        question_id=data["question_id"],
        max_score=data.get("max_score", 10),
        co_mapping=data.get("co_mapping"),
    )
    db.add(tq)
    db.commit()
    return {"message": "Question added"}


@router.delete("/{test_id}/questions/{question_id}")
def remove_question_from_test(test_id: int, question_id: int, user=Depends(require_teacher), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not yours")

    tq = db.query(TestQuestion).filter(TestQuestion.test_id == test_id, TestQuestion.question_id == question_id).first()
    if not tq:
        raise HTTPException(status_code=404, detail="Question not in test")

    db.delete(tq)
    db.commit()
    return {"message": "Question removed"}


@router.delete("/{test_id}")
def delete_test(test_id: int, user=Depends(require_teacher), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found or not yours")
    db.delete(test)
    db.commit()
    return {"message": "Test deleted"}
