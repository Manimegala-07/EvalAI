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

scorer = ScoringService(training=True)


def train():

    df = pd.read_csv(DATA_PATH)

    X = []
    y = []

    for _, row in df.iterrows():

        reference = str(row["question"]) + " " + str(row["model_answer"])
        student = str(row["student_answer"])

        result = scorer.grade_batch([reference], [student], 10)[0]

        X.append([
            result["similarity"],
            result["entailment"],
            result["coverage"],
            result["length_ratio"]
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