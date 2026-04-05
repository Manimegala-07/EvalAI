from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Question
from app.auth.dependencies import require_teacher
from app.services.llm_service import LLMService
from app.services.translation_service import translate_to_language
import json

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("")
def list_questions(
    search: str = Query("", alias="search"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(
        (Question.teacher_id == user.id) | (Question.teacher_id == None)
    )
    if search:
        q = q.filter(Question.text.ilike(f"%{search}%"))

    total = q.count()
    questions = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id":             qu.id,
                "text":           qu.text,
                "model_answer":    qu.model_answer,
                "model_answer_ta": qu.model_answer_ta,
                "model_answer_hi": qu.model_answer_hi,
                "difficulty":      qu.difficulty,
                "blooms_level":    qu.blooms_level,
                "co_mapping":      qu.co_mapping,
                "created_at":     qu.created_at,
            }
            for qu in questions
        ],
    }


@router.post("")
def create_question(
    data: dict,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    if not data.get("text") or not data.get("model_answer"):
        raise HTTPException(status_code=400, detail="text and model_answer are required")

    english_answer = data["model_answer"]

    # ── Auto-translate reference answer to Tamil and Hindi ──
    print(f"  🌐 Auto-translating reference answer...")
    tamil_answer = data.get("model_answer_ta") or translate_to_language(english_answer, "ta")
    hindi_answer = data.get("model_answer_hi") or translate_to_language(english_answer, "hi")
    print(f"  ✅ Tamil reference: {tamil_answer[:60]}...")
    print(f"  ✅ Hindi reference: {hindi_answer[:60]}...")

    question = Question(
        text           = data["text"],
        model_answer   = english_answer,
        model_answer_ta = tamil_answer,
        model_answer_hi = hindi_answer,
        teacher_id     = user.id,
        difficulty     = data.get("difficulty"),
        blooms_level   = data.get("blooms_level"),
        co_mapping     = data.get("co_mapping"),
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "id":             question.id,
        "model_answer_ta": question.model_answer_ta,
        "model_answer_hi": question.model_answer_hi,
        "message":        "Question created with multilingual references",
    }


@router.put("/{question_id}")
def update_question(
    question_id: int,
    data: dict,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.teacher_id == user.id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if "text"           in data: question.text            = data["text"]
    if "model_answer"   in data: question.model_answer    = data["model_answer"]
    if "model_answer_ta" in data: question.model_answer_ta = data["model_answer_ta"]
    if "model_answer_hi" in data: question.model_answer_hi = data["model_answer_hi"]
    if "difficulty"     in data: question.difficulty      = data["difficulty"]
    if "blooms_level"   in data: question.blooms_level    = data["blooms_level"]
    if "co_mapping"     in data: question.co_mapping      = data["co_mapping"]

    db.commit()
    return {"message": "Question updated successfully"}


@router.put("/{question_id}/translations")
def update_translations(
    question_id: int,
    data: dict,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Teacher can manually correct auto-translated references."""
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.teacher_id == user.id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if "model_answer_ta" in data:
        question.model_answer_ta = data["model_answer_ta"]
    if "model_answer_hi" in data:
        question.model_answer_hi = data["model_answer_hi"]

    db.commit()
    return {"message": "Translations updated successfully"}


@router.post("/validate")
def validate_question(
    data: dict,
    user=Depends(require_teacher),
):
    text         = data.get("text", "").strip()
    model_answer = data.get("model_answer", "").strip()

    if not text or not model_answer:
        raise HTTPException(status_code=400, detail="text and model_answer are required")

    llm = LLMService()
    prompt = f"""
You are an academic question validator. Analyse this question and its model answer.
Question: {text}
Model Answer: {model_answer}
Return STRICT JSON only, no markdown fences, no extra text:
{{
  "grammar_ok": true or false,
  "answers_question": true or false,
  "comments": "brief comment about quality",
  "corrected_answer": "improved version of the answer, or same if already good"
}}
"""
    try:
        raw = llm.model.generate_content(prompt).text
        raw = raw.strip().strip("```json").strip("```").strip()
        analysis = json.loads(raw)
    except Exception:
        analysis = {
            "grammar_ok": True,
            "answers_question": True,
            "comments": "Validation service unavailable.",
            "corrected_answer": model_answer,
        }

    return {"analysis": analysis}


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(
        Question.id == question_id,
    ).filter(
        (Question.teacher_id == user.id) | (Question.teacher_id == None)
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found or not yours")

    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}