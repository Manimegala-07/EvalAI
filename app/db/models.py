from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # teacher or student


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    model_answer = Column(Text)


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    max_score = Column(Float)  # NEW FIELD

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    total_minilm = Column(Float, default=0)
    total_hybrid = Column(Float, default=0)
    status = Column(String, default="pending")
    

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    student_answer = Column(Text)     
    score_minilm = Column(Float, default=0)
    score_hybrid = Column(Float, default=0)

    feedback_minilm = Column(Text)
    feedback_hybrid = Column(Text)
    
    # 🔥 NEW — concept level heatmap data
    concept_data = Column(JSON)

