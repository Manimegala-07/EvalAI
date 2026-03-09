from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, DateTime
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # teacher or student

    profile_photo = Column(String, nullable=True)
    institution = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Optional: deadline support
    due_date = Column(DateTime, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("TestQuestion", backref="test", lazy="dynamic")
    submissions = relationship("Submission", backref="test", lazy="dynamic")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    model_answer = Column(Text, nullable=False)

    # FIX: Track ownership so teachers only see their own questions
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    max_score = Column(Float, nullable=False, default=10.0)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)

    total_score = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending / evaluated

    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answer", backref="submission", lazy="dynamic")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    student_answer = Column(Text)

    # Scoring transparency
    score = Column(Float, default=0.0)
    similarity = Column(Float, nullable=True)
    entailment = Column(Float, nullable=True)
    coverage = Column(Float, nullable=True)
    length_ratio = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)

    # Gemini feedback
    feedback = Column(Text, nullable=True)

    # Heatmap data
    concept_data = Column(JSON, nullable=True)
    sentence_heatmap = Column(JSON, nullable=True)