"""
translation_routes.py — EvalAI Language API
============================================
Endpoints:
  POST /translate/question   → Translate question to target language
  POST /translate/detect     → Detect language of text
  GET  /translate/languages  → Get supported languages
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.translation_service import (
    translate_to_language,
    translate_to_english,
    detect_language,
    SUPPORTED_LANGUAGES,
)

router = APIRouter(prefix="/translate", tags=["Translation"])


class TranslateQuestionRequest(BaseModel):
    text:        str
    target_lang: str = "ta"  # default Tamil


class DetectLanguageRequest(BaseModel):
    text: str


# ═══════════════════════════════════════════════════════════
# ENDPOINT 1 — Translate question to target language
# ═══════════════════════════════════════════════════════════

@router.post("/question")
async def translate_question(req: TranslateQuestionRequest):
    """
    Translate a question from English to target language.
    Frontend calls this when student switches language!
    """
    translated = translate_to_language(req.text, req.target_lang)
    return {
        "original":    req.text,
        "translated":  translated,
        "target_lang": req.target_lang,
        "target_name": SUPPORTED_LANGUAGES.get(req.target_lang, req.target_lang),
    }


# ═══════════════════════════════════════════════════════════
# ENDPOINT 2 — Detect language of text
# ═══════════════════════════════════════════════════════════

@router.post("/detect")
async def detect_text_language(req: DetectLanguageRequest):
    """Detect what language the text is written in."""
    return detect_language(req.text)


# ═══════════════════════════════════════════════════════════
# ENDPOINT 3 — Get supported languages
# ═══════════════════════════════════════════════════════════

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for UI toggle."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }