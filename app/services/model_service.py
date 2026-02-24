import torch
from sentence_transformers import SentenceTransformer
import app.config as config


class ModelService:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:

            device = "cuda" if torch.cuda.is_available() else "cpu"

            print(f"Loading model on {device}...")
            
            cls._model = SentenceTransformer(
                config.MODEL_PATH,
                device=device
            )

        return cls._model
