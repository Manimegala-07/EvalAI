"""
moodle_routes.py — EvalAI ↔ Moodle Integration
================================================
Endpoints:
  POST /moodle/grade        ← Moodle sends question + student answer → EvalAI grades it
  POST /moodle/pushgrade    ← EvalAI pushes score back to Moodle gradebook
  GET  /moodle/result/{id}  ← Fetch a previously graded result
"""

import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/moodle", tags=["Moodle Integration"])

scoring_service = ScoringService()

# ─── In-memory store for graded results (keyed by submission_id) ───────────
_results_store: dict = {}

# ─── Moodle connection config (set via environment variables) ───────────────
MOODLE_URL   = os.getenv("MOODLE_URL",   "http://localhost:8080")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "")


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class MoodleGradeRequest(BaseModel):
    submission_id:  str           # Moodle submission ID
    student_name:   str           # Student's full name
    question:       str           # Question text
    reference:      str           # Model answer (reference)
    student_answer: str           # Student's answer
    max_score:      float = 10.0  # Maximum marks for this question


class MoodlePushRequest(BaseModel):
    submission_id:  str    # same ID used in /moodle/grade
    moodle_user_id: int    # Moodle user ID of student
    course_id:      int    # Moodle course ID
    assign_id:      int    # Moodle assignment ID


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 1 — GRADE (Moodle → EvalAI)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/grade")
async def moodle_grade(req: MoodleGradeRequest):
    """
    Moodle calls this endpoint when a student submits an answer.
    EvalAI runs the full hybrid pipeline and returns the score.
    """
    print(f"\n{'═'*60}")
    print(f"  📥 Moodle Grade Request Received")
    print(f"     submission_id : {req.submission_id}")
    print(f"     student       : {req.student_name}")
    print(f"     max_score     : {req.max_score}")
    print(f"{'═'*60}")

    try:
        # Run full hybrid grading pipeline
        result = scoring_service.grade_single(
            reference=req.reference,
            student=req.student_answer,
            max_score=req.max_score
        )

        # Store result for later fetch
        _results_store[req.submission_id] = {
            "submission_id":  req.submission_id,
            "student_name":   req.student_name,
            "question":       req.question,
            "student_answer": req.student_answer,
            "max_score":      req.max_score,
            **result
        }

        print(f"\n  ✅ Graded: {result['score']} / {req.max_score}")

        return {
            "success":       True,
            "submission_id": req.submission_id,
            "student_name":  req.student_name,
            "score":         result["score"],
            "max_score":     req.max_score,
            "similarity":    result["similarity"],
            "entailment":    result["entailment"],
            "coverage":      result["coverage"],
            "confidence":    result["confidence"],
            "wrong_ratio":   result["wrong_ratio"],
            "message":       f"Score: {result['score']} / {req.max_score}"
        }

    except Exception as e:
        print(f"  ❌ Grading failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 2 — FETCH RESULT (GET)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/result/{submission_id}")
async def get_result(submission_id: str):
    """
    Fetch a previously graded result by submission ID.
    """
    result = _results_store.get(submission_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No result found for submission_id: {submission_id}"
        )
    return result


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 3 — PUSH GRADE BACK TO MOODLE GRADEBOOK
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/pushgrade")
async def push_grade_to_moodle(req: MoodlePushRequest):
    """
    Push the EvalAI score back to Moodle gradebook via Moodle Web Services API.
    """
    result = _results_store.get(req.submission_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No graded result found for submission_id: {req.submission_id}"
        )

    score = result["score"]

    # Moodle Web Services API call
    moodle_api_url = f"{MOODLE_URL}/webservice/rest/server.php"

    params = {
        "wstoken":                    MOODLE_TOKEN,
        "wsfunction":                 "core_grades_update_grades",
        "moodlewsrestformat":         "json",
        "source":                     "evalai",
        "courseid":                   req.course_id,
        "component":                  "mod_assign",
        "activityid":                 req.assign_id,
        "itemnumber":                 0,
        "grades[0][studentid]":       req.moodle_user_id,
        "grades[0][grade]":           score,
        "grades[0][str_feedback]":    f"EvalAI Score: {score}/{result['max_score']} | Similarity: {result['similarity']*100:.1f}% | Coverage: {result['coverage']*100:.1f}%",
    }

    print(f"\n  📤 Pushing grade to Moodle...")
    print(f"     user_id   : {req.moodle_user_id}")
    print(f"     assign_id : {req.assign_id}")
    print(f"     score     : {score}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(moodle_api_url, data=params)
        moodle_response = response.json()

    if isinstance(moodle_response, dict) and moodle_response.get("exception"):
        raise HTTPException(
            status_code=400,
            detail=f"Moodle API error: {moodle_response.get('message')}"
        )

    print(f"  ✅ Grade pushed to Moodle gradebook!")

    return {
        "success":       True,
        "submission_id": req.submission_id,
        "score":         score,
        "moodle_response": moodle_response,
        "message":       f"Score {score}/{result['max_score']} pushed to Moodle gradebook!"
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 4 — HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/health")
async def moodle_health():
    """Check if Moodle integration is working."""
    return {
        "status":      "ok",
        "moodle_url":  MOODLE_URL,
        "evalai_ready": True,
        "message":     "EvalAI-Moodle integration is active!"
    }