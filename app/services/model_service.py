import torch
from sentence_transformers import SentenceTransformer
import app.config as config


class ModelService:

    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"\n{'═'*62}")
            print(f"  🧠 Loading Sentence Transformer — {config.MODEL_PATH}")
            print(f"  💻 Device: {device}")
            print(f"{'═'*62}")
            cls._model = SentenceTransformer(config.MODEL_PATH, device=device)
            print(f"  ✅ Model loaded | Embedding dim: {cls._model.get_sentence_embedding_dimension()} | Max seq: {cls._model.max_seq_length}")
            print(f"{'═'*62}\n")
        else:
            print(f"  ♻️  Sentence Transformer — reusing cached model")
        return cls._model
