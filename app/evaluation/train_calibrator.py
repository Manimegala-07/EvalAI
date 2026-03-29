import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from app.services.scoring_service import ScoringService


# 🔹 project root (E:\12Feb)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# 🔹 correct paths
DATA_PATH = os.path.join(BASE_DIR, "data", "clean_training_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "score_calibrator.pkl")

scorer = ScoringService()


def train():

    df = pd.read_csv(DATA_PATH)

    X = []
    y = []

    for _, row in df.iterrows():

        reference = str(row["question"]) + " " + str(row["model_answer"])
        student   = str(row["student_answer"])

        result = scorer.grade_batch([reference], [student], 10)[0]

        ref_words     = set(reference.lower().split())
        stu_words     = set(student.lower().split())
        lex_overlap   = len(ref_words & stu_words) / max(len(ref_words), 1)
        forward_ent   = result["entailment"]
        # grade_single stores forward_ent; approximate backward from nli_score
        backward_ent  = result.get("backward_ent", forward_ent)
        direction_gap = backward_ent - forward_ent

        X.append([
            result["similarity"],
            forward_ent,
            backward_ent,
            direction_gap,
            result["coverage"],
            result["wrong_ratio"],
            result["length_ratio"],
            lex_overlap,
        ])

        y.append(float(row["human_score"]))

    reg = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
    )
    reg.fit(X, y)

    # ⭐ create models folder if missing
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    joblib.dump(reg, MODEL_PATH)

    print("Calibration model saved at:", MODEL_PATH)


if __name__ == "__main__":
    train()