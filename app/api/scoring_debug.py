# app/routers/scoring_debug.py
# Add this router to main.py:  app.include_router(scoring_debug.router)

from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.scoring_service import ScoringService
from app.services.nli_service import NLIService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/scoring", tags=["Debug"])


class DebugRequest(BaseModel):
    reference: str
    student_answer: str
    max_score: float = 10.0


@router.post("/debug")
def debug_score(req: DebugRequest):
    """
    Returns ALL intermediate outputs of the scoring pipeline
    for the EvalAI Pipeline Visualizer demo.
    """
    scorer = ScoringService()
    llm    = LLMService()

    # ── Run full scoring ──────────────────────────────────────
    result = scorer.grade_single(req.reference, req.student_answer, req.max_score)

    # ── Get raw NLI scores (bidirectional) ────────────────────
    nli_raw = NLIService.bidirectional_full(req.reference, req.student_answer)

    # ── Tokenization intermediate ─────────────────────────────
    ref_tokens = scorer.tokenize(req.reference)
    stu_tokens = scorer.tokenize(req.student_answer)

    # ── Sentence extraction intermediate ──────────────────────
    ref_sentences = scorer.extract_sentences(req.reference)
    stu_sentences = scorer.extract_sentences(req.student_answer)

    # ── IDF table ─────────────────────────────────────────────
    idf = scorer.build_idf(req.reference)
    idf_sorted = sorted(idf.items(), key=lambda x: -x[1])[:25]

    # ── LLM Feedback ─────────────────────────────────────────
    concept_results = result["concept_results"]
    covered = [c["concept"] for c in concept_results if c["status"] == "matched"]
    partial = [c["concept"] for c in concept_results if c["status"] == "partial"]
    missing = [c["concept"] for c in concept_results if c["status"] == "missing"]
    wrong   = [c["concept"] for c in concept_results if c["status"] == "wrong"]

    try:
        prompt = f"""
You are an academic evaluator giving feedback to a student.
Student Answer: {req.student_answer}
Score: {result['score']} / {req.max_score}
Covered concepts: {', '.join(covered) or 'none'}
Partially covered: {', '.join(partial) or 'none'}
Missing concepts: {', '.join(missing) or 'none'}
Wrong concepts: {', '.join(wrong) or 'none'}
Write 3-5 sentences of constructive feedback.
"""
        feedback = llm.model.generate_content(prompt).text
    except Exception:
        feedback = f"Score: {result['score']}/{req.max_score}. Covered: {', '.join(covered) or 'none'}. Missing: {', '.join(missing) or 'none'}."

    return {
        # ── Core scores ───────────────────────────────────────
        "score":            result["score"],
        "similarity":       result["similarity"],
        "entailment":       result["entailment"],
        "coverage":         result["coverage"],
        "length_ratio":     result["length_ratio"],
        "wrong_ratio":      result["wrong_ratio"],
        "confidence":       result["confidence"],

        # ── Concept heatmap ───────────────────────────────────
        "concept_results":  result["concept_results"],

        # ── Sentence heatmap ──────────────────────────────────
        "sentence_heatmap": result["sentence_heatmap"],

        # ── NLI raw ───────────────────────────────────────────
        "nli": nli_raw,

        # ── Intermediate outputs ──────────────────────────────
        "ref_tokens":       ref_tokens,
        "stu_tokens":       stu_tokens,
        "ref_sentences":    ref_sentences,
        "stu_sentences":    stu_sentences,
        "idf_table":        [{"term": t, "idf": round(v, 4)} for t, v in idf_sorted],

        # ── Feedback ──────────────────────────────────────────
        "feedback":         feedback,
    }