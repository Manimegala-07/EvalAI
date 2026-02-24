import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
from app.services.scoring_service import ScoringService

scorer = ScoringService()


# ------------------------------
# Convert score into grade band
# ------------------------------
def band(score):
    """
    Convert numeric marks into grading category
    0–2   -> incorrect
    3–5   -> partially correct
    6–10  -> correct
    """
    if score <= 2:
        return 0
    elif score <= 5:
        return 1
    else:
        return 2


def evaluate():

    print("\n📂 Loading dataset...")
    df = pd.read_csv("data/clean_training_data.csv")

    human_scores = []
    predicted_scores = []

    print("🚀 Running grading on dataset...\n")

    for i, row in df.iterrows():

        reference = str(row["question"]) + " " + str(row["model_answer"])
        student = str(row["student_answer"])

        result = scorer.grade_batch([reference], [student], 10)[0]

        human = float(row["human_score"])
        pred = float(result["score"])

        human_scores.append(human)
        predicted_scores.append(pred)

        if i % 50 == 0:
            print(f"Sample {i}: Human={human:.2f} | AI={pred:.2f}")

    # ------------------------------
    # Spearman correlation
    # ------------------------------
    print("\n📊 Calculating Spearman correlation...")
    spearman_corr, _ = spearmanr(human_scores, predicted_scores)

    # ------------------------------
    # Quadratic Weighted Kappa
    # ------------------------------
    print("📊 Calculating Quadratic Weighted Kappa...")

    human_band = [band(x) for x in human_scores]
    pred_band = [band(x) for x in predicted_scores]

    kappa = cohen_kappa_score(human_band, pred_band, weights="quadratic")

    # ------------------------------
    # Report
    # ------------------------------
    print("\n==============================")
    print("   MODEL EVALUATION REPORT")
    print("==============================")

    print(f"Total Samples: {len(human_scores)}")
    print(f"Spearman Correlation : {round(spearman_corr,4)}")
    print(f"Quadratic Weighted Kappa : {round(kappa,4)}\n")

    # Interpretation
    if kappa > 0.8:
        print("Result: Excellent agreement with human grading 🎯")
    elif kappa > 0.65:
        print("Result: Strong agreement 👍")
    elif kappa > 0.5:
        print("Result: Moderate agreement 🙂")
    else:
        print("Result: Weak agreement — needs tuning ⚠️")


if __name__ == "__main__":
    evaluate()