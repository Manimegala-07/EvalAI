from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from app.dataset import load_dataset
import app.config as config


def freeze_backbone(model, freeze_ratio=0.8):
    """
    Freeze bottom 80% of transformer layers.
    Keep top layers trainable.
    """

    auto_model = model._first_module().auto_model

    layers = auto_model.encoder.layer
    freeze_until = int(len(layers) * freeze_ratio)

    for layer in layers[:freeze_until]:
        for param in layer.parameters():
            param.requires_grad = False


def train():

    train_examples, val_examples = load_dataset(
        "data/clean_training_data.csv"
    )

    loader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=config.BATCH_SIZE
    )

    model = SentenceTransformer(config.MODEL_NAME)

    freeze_backbone(model)

    loss = losses.CosineSimilarityLoss(model)

    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
        val_examples
    )

    model.fit(
        train_objectives=[(loader, loss)],
        evaluator=evaluator,
        epochs=config.EPOCHS,
        output_path=config.MODEL_PATH
    )


if __name__ == "__main__":
    train()
