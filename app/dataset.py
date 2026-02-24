import pandas as pd
from sentence_transformers import InputExample



def build_examples(df):
    examples = []
    print(df.columns)
    for _, row in df.iterrows():
        ref = str(row["question"]) + " " + str(row["model_answer"])
        stu = str(row["student_answer"])
        score = float(row["human_score"]) / 10.0

        examples.append(InputExample(
            texts=[ref, stu],
            label=score
        ))

    return examples


def load_dataset(path):
    df = pd.read_csv(path)

    train = df[df["dataset_split"] == "train"]
    val = df[df["dataset_split"] == "validation"]

    return build_examples(train), build_examples(val)
