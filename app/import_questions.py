import os
import pandas as pd
from app.db.database import SessionLocal
from app.db.models import Question

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "question_model.xlsx")


def import_questions():
    df = pd.read_excel(FILE_PATH)

    # 🔥 Clean column names automatically
    df.columns = df.columns.str.strip().str.lower()

    db = SessionLocal()

    try:
        for _, row in df.iterrows():
            q = Question(
                text=row["question"],   # now safe
                model_answer=row["model_answer"]
            )
            db.add(q)

        db.commit()
        print("Questions imported successfully!")

    except Exception as e:
        db.rollback()
        print("Error importing questions:", e)

    finally:
        db.close()


if __name__ == "__main__":
    import_questions()