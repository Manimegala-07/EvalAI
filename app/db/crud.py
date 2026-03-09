from app.db.models import Test, TestQuestion, Submission, Answer


# ---------------- TEST ----------------
def create_test(db, title, teacher_id, questions):

    test = Test(title=title, teacher_id=teacher_id)
    db.add(test)
    db.flush()  # get test.id before commit

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
        total_score=0,
        status="evaluated"   # auto evaluation system
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission.id


# ---------------- ANSWERS ----------------
def save_answer(
    db,
    submission_id,
    question_id,
    student_answer,
    score,
    similarity,
    entailment,
    coverage,
    length_ratio,
    confidence,
    feedback,
    concept_data
):

    answer = Answer(
        submission_id=submission_id,
        question_id=question_id,
        student_answer=student_answer,
        score=score,
        similarity=similarity,
        entailment=entailment,
        coverage=coverage,
        length_ratio=length_ratio,
        confidence=confidence,
        feedback=feedback,
        concept_data=concept_data
    )

    db.add(answer)


# ---------------- RESULTS ----------------
def get_test_results(db, test_id):

    return db.query(Answer).join(Submission)\
        .filter(Submission.test_id == test_id)\
        .all()


# ---------------- ANALYTICS ----------------
def get_test_analytics(db, test_id):

    submissions = db.query(Submission)\
        .filter(Submission.test_id == test_id)\
        .all()

    if not submissions:
        return {}

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

    scores = list(student_totals.values())

    return {
        "average_score": round(sum(scores) / len(scores), 2),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "student_ranking": sorted(
            student_totals.items(),
            key=lambda x: x[1],
            reverse=True
        ),
        "question_performance": {
            qid: round(sum(vals) / len(vals), 2)
            for qid, vals in question_scores.items()
        }
    }