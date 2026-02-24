from app.db.models import *


# ---------------- TEST ----------------
def create_test(db, title, teacher_id, questions):

    test = Test(title=title, teacher_id=teacher_id)
    db.add(test)
    db.flush()
    

    for item in questions:
        db.add(
            TestQuestion(
                test_id=test.id,
                question_id=item["question_id"],
                max_score=item["max_score"]
            )
        )

    db.commit()
    db.refresh(test)
    
    return test.id


# ---------------- SUBMISSION ----------------
def create_submission(db, student_id, test_id):

    submission = Submission(
        student_id=student_id,
        test_id=test_id,
        total_minilm=0,
        total_hybrid=0,
        status="pending"
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission.id


# ---------------- ANSWERS ----------------
def save_answer(db, submission_id, question_id, answer, score, feedback):

    db.add(Answer(
        submission_id=submission_id,
        question_id=question_id,
        student_answer=answer,
        score=score,
        feedback=feedback
    ))


# ---------------- RESULTS ----------------
def get_test_results(db, test_id):

    return db.query(Answer).join(Submission)\
        .filter(Submission.test_id == test_id).all()


# ---------------- ANALYTICS ----------------
def get_test_analytics(db, test_id):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .all()

    student_totals = {}
    question_scores = {}

    for sub in submissions:

        answers = db.query(Answer)\
            .filter(Answer.submission_id == sub.id)\
            .all()

        total = 0

        for ans in answers:
            total += ans.score
            question_scores.setdefault(ans.question_id, []).append(ans.score)

        student_totals[sub.student_id] = total

    if not student_totals:
        return {}

    scores = list(student_totals.values())

    return {
        "average_score": round(sum(scores) / len(scores), 2),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "student_ranking": sorted(student_totals.items(), key=lambda x: x[1], reverse=True),
        "question_performance": {
            qid: round(sum(vals) / len(vals), 2)
            for qid, vals in question_scores.items()
        }
    }