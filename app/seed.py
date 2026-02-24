from app.db.database import SessionLocal
from app.db.models import User, Question

db = SessionLocal()

teacher = User(name="Teacher A", role="teacher")
student = User(name="Student A", role="student")

q1 = Question(
    text="What is photosynthesis?",
    model_answer="Photosynthesis is the process by which plants make food using sunlight."
)

db.add_all([teacher, student, q1])
db.commit()

print("Seed data inserted!")
db.close()
