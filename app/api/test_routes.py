from fastapi import APIRouter,Depends
from app.db.crud import create_test
from app.auth.dependencies import require_teacher
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Test,TestQuestion,Question

router = APIRouter()


@router.post("/tests")
def create_test_api(
    data: dict,
    user=Depends(require_teacher),
    db: Session = Depends(get_db)   # ← THIS WAS MISSING
):

    test_id = create_test(
        db=db,                       # ← PASS DB
        title=data["title"],
        teacher_id=user.id,
        questions=data["questions"]
    )

    return {"test_id": test_id}

@router.get("/tests")
def list_tests(
    user=Depends(require_teacher),
    db: Session = Depends(get_db)
):
    tests = db.query(Test).filter(Test.teacher_id == user.id).all()

    return [
        {
            "id": t.id,
            "title": t.title
        }
        for t in tests
    ]

@router.get("/tests/student")
def list_tests_for_students(db: Session = Depends(get_db)):
    tests = db.query(Test).all()

    return [
        {
            "id": t.id,
            "title": t.title
        }
        for t in tests
    ]

@router.get("/tests/{test_id}")
def get_test(test_id: int, db: Session = Depends(get_db)):

    test = db.query(Test).filter(Test.id == test_id).first()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    mappings = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).all()

    questions = []

    for m in mappings:
        q = db.query(Question).filter(
            Question.id == m.question_id
        ).first()

        if q:
            questions.append({
                "id": q.id,
                "text": q.text,
                "max_score": m.max_score
            })

    return {
        "test_id": test.id,
        "title": test.title,
        "questions": questions
    }