"""
translation_service.py — EvalAI Language Support
=================================================
Handles:
  - Auto-detect language of student answer
  - Translate Tamil/Hindi/any language → English for grading
  - Translate English question → Tamil/Hindi for display
"""

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Make langdetect deterministic
DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "தமிழ்",
    "hi": "हिंदी",
}

# Human-readable names for detected codes
LANG_NAMES = {
    "en": "English", "ta": "Tamil", "hi": "Hindi",
    "fr": "French",  "de": "German", "es": "Spanish",
    "zh": "Chinese", "ar": "Arabic", "ja": "Japanese",
}


def detect_language(text: str) -> dict:
    """Detect language of given text using langdetect."""
    try:
        lang_code = detect(text)
        lang_name = LANG_NAMES.get(lang_code, lang_code).title()
        return {
            "lang_code":  lang_code,
            "lang_name":  lang_name,
            "confidence": None,          # langdetect doesn't expose a simple confidence float
            "is_english": lang_code == "en",
        }
    except LangDetectException as e:
        print(f"[WARN] Language detection failed: {e}")
        return {"lang_code": "en", "lang_name": "English", "confidence": None, "is_english": True}


def translate_to_english(text: str) -> dict:
    """
    Translate any language text to English.
    Returns original text unchanged if already English.
    """
    try:
        lang_code = detect(text)
    except LangDetectException:
        lang_code = "en"

    if lang_code == "en":
        return {
            "translated":      text,
            "original":        text,
            "source_language": "English",
            "source_code":     "en",
            "was_translated":  False,
        }

    try:
        translated = GoogleTranslator(source=lang_code, target="en").translate(text)
        lang_name  = LANG_NAMES.get(lang_code, lang_code).title()

        return {
            "translated":      translated,
            "original":        text,
            "source_language": lang_name,
            "source_code":     lang_code,
            "was_translated":  True,
        }
    except Exception as e:
        print(f"[WARN] Translation failed: {e} -- using original text")
        return {
            "translated":      text,
            "original":        text,
            "source_language": "Unknown",
            "source_code":     "unknown",
            "was_translated":  False,
        }


def translate_to_language(text: str, target_lang: str = "ta") -> str:
    """
    Translate English text to target language.
    Used for auto-generating Tamil/Hindi reference answers.
    """
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception as e:
        print(f"[WARN] Translation to {target_lang} failed: {e}")
        return text
