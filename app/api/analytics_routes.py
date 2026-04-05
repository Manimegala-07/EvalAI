from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Submission, Answer, TestQuestion, Question, User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/tests/{test_id}")
def test_analytics(test_id: int, db: Session = Depends(get_db)):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .filter(Submission.status == "evaluated")\
        .all()

    if not submissions:
        return {"message": "No evaluated submissions yet"}

    # ── Per student scores ─────────────────────────────────────
    student_scores = []
    for sub in submissions:
        student = db.query(User).filter(User.id == sub.student_id).first()
        student_scores.append({
            "student_id":   sub.student_id,
            "student_name": student.name if student else f"Student #{sub.student_id}",
            "score":        sub.total_score,
        })

    scores   = [s["score"] for s in student_scores]
    average  = round(sum(scores) / len(scores), 2)
    highest  = max(scores)
    lowest   = min(scores)
    ranking  = sorted(student_scores, key=lambda x: x["score"], reverse=True)

    # ── Total max score for this test ──────────────────────────
    tqs = db.query(TestQuestion).filter(TestQuestion.test_id == test_id).all()
    total_max = sum(tq.max_score for tq in tqs) if tqs else 100

    # ── Pass rate ──────────────────────────────────────────────
    pass_count = sum(1 for s in scores if (s / total_max) * 100 >= 50)
    pass_rate  = round((pass_count / len(scores)) * 100, 1) if scores else 0

    # ── Score distribution bands ───────────────────────────────
    bands = {"Excellent (80-100)": 0, "Good (60-80)": 0, "Pass (40-60)": 0, "Fail (<40)": 0}
    for s in scores:
        pct = (s / total_max) * 100
        if pct >= 80:   bands["Excellent (80-100)"] += 1
        elif pct >= 60: bands["Good (60-80)"] += 1
        elif pct >= 40: bands["Pass (40-60)"] += 1
        else:           bands["Fail (<40)"] += 1

    score_distribution = [
        {"name": k, "value": v, "color": c}
        for (k, v), c in zip(bands.items(), ["#16A34A", "#2D5BE3", "#D97706", "#DC2626"])
    ]

    # ── Per question analysis ──────────────────────────────────
    question_perf = {}
    for sub in submissions:
        answers = db.query(Answer).filter(Answer.submission_id == sub.id).all()
        for ans in answers:
            question_perf.setdefault(ans.question_id, []).append({
                "score": ans.score, "confidence": ans.confidence, "rf_score": ans.rf_score,
            })

    question_analysis = {}
    for qid, vals in question_perf.items():
        mapping   = db.query(TestQuestion).filter(TestQuestion.test_id == test_id, TestQuestion.question_id == qid).first()
        max_score = mapping.max_score if mapping else 1
        scores_list = [v["score"] for v in vals]
        avg         = sum(scores_list) / len(scores_list)
        diff_index  = round(1 - (avg / max_score), 2)
        question_analysis[qid] = {
            "average_score":    round(avg, 2),
            "difficulty_index": diff_index,
        }

    # ── Difficulty level analytics ─────────────────────────────
    difficulty_perf = {}
    co_perf         = {}
    blooms_perf     = {}
    student_co_perf = {}  # { student_id: { CO1: [pct], CO2: [pct] } }

    for sub in submissions:
        answers = db.query(Answer).filter(Answer.submission_id == sub.id).all()
        for ans in answers:
            question = db.query(Question).filter(Question.id == ans.question_id).first()
            if not question: continue
            mapping   = db.query(TestQuestion).filter(TestQuestion.test_id == test_id, TestQuestion.question_id == ans.question_id).first()
            max_score = mapping.max_score if mapping else 1
            pct       = round((ans.score / max_score) * 100, 2) if max_score else 0

            if question.difficulty:
                difficulty_perf.setdefault(question.difficulty, []).append(pct)
            if mapping and mapping.co_mapping:
                co_perf.setdefault(mapping.co_mapping, []).append(pct)
                student_co_perf.setdefault(sub.student_id, {}).setdefault(mapping.co_mapping, []).append(pct)
            if question.blooms_level:
                blooms_perf.setdefault(question.blooms_level, []).append(pct)

    DIFF_LABELS = {1: "Very Easy", 2: "Easy", 3: "Average", 4: "Hard", 5: "Very Hard"}
    difficulty_analytics = [
        {"level": k, "label": DIFF_LABELS.get(k, f"Level {k}"), "avg_score": round(sum(v) / len(v), 2), "count": len(v)}
        for k, v in sorted(difficulty_perf.items())
    ]

    co_analytics = [
        {"co": k, "avg_score": round(sum(v) / len(v), 2), "count": len(v)}
        for k, v in sorted(co_perf.items())
    ]

    blooms_analytics = [
        {"level": k, "avg_score": round(sum(v) / len(v), 2), "count": len(v)}
        for k, v in sorted(blooms_perf.items())
    ]

    # ── Students needing attention (below 50%) ─────────────────
    needs_attention = []
    for s in ranking:
        pct = round((s["score"] / total_max) * 100, 1)
        if pct < 50:
            # Find weakest CO for this student
            s_co = student_co_perf.get(s["student_id"], {})
            weakest_co = min(s_co, key=lambda co: sum(s_co[co]) / len(s_co[co])) if s_co else None
            needs_attention.append({
                "student_name": s["student_name"],
                "student_id":   s["student_id"],
                "score":        s["score"],
                "percentage":   pct,
                "weakest_co":   weakest_co,
            })

    return {
        "average_score":        average,
        "highest_score":        highest,
        "lowest_score":         lowest,
        "pass_rate":            pass_rate,
        "total_max":            total_max,
        "total_students":       len(scores),
        "ranking":              ranking,
        "score_distribution":   score_distribution,
        "question_analysis":    question_analysis,
        "difficulty_analytics": difficulty_analytics,
        "co_analytics":         co_analytics,
        "blooms_analytics":     blooms_analytics,
        "needs_attention":      needs_attention,
    }
