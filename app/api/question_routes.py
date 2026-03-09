from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Question
from app.auth.dependencies import require_teacher
from app.services.llm_service import LLMService
import json

router = APIRouter(prefix="/questions", tags=["Questions"])


# ======================================================
# LIST QUESTIONS (teacher-owned only)
# ======================================================

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
                "id": qu.id,
                "text": qu.text,
                "model_answer": qu.model_answer,
                "created_at": qu.created_at,
            }
            for qu in questions
        ],
    }


# ======================================================
# CREATE QUESTION
# ======================================================

@router.post("")
def create_question(
    data: dict,
    user=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    if not data.get("text") or not data.get("model_answer"):
        raise HTTPException(status_code=400, detail="text and model_answer are required")

    question = Question(
        text=data["text"],
        model_answer=data["model_answer"],
        teacher_id=user.id,   # FIX: track ownership
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {"id": question.id, "message": "Question created"}


# ======================================================
# VALIDATE QUESTION WITH AI  (was missing entirely)
# ======================================================

@router.post("/validate")
def validate_question(
    data: dict,
    user=Depends(require_teacher),
):
    """
    Uses Gemini to validate that:
    - The model answer actually answers the question
    - Grammar is acceptable
    - Returns a corrected answer if needed
    """
    text = data.get("text", "").strip()
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
        # Strip markdown fences if present
        raw = raw.strip().strip("```json").strip("```").strip()
        analysis = json.loads(raw)
    except Exception as e:
        analysis = {
            "grammar_ok": True,
            "answers_question": True,
            "comments": "Validation service unavailable.",
            "corrected_answer": model_answer,
        }

    return {"analysis": analysis}


# ======================================================
# DELETE QUESTION
# ======================================================

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