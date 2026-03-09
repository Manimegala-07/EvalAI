import torch
from sentence_transformers import SentenceTransformer
import app.config as config


class ModelService:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # ── DEBUG ──────────────────────────────────────
            print(f"\n{'═'*62}")
            print(f"  🧠 ModelService — Loading Sentence Transformer")
            print(f"  💻 Device      : {device}")
            print(f"  📦 Model path  : {config.MODEL_PATH}")
            print(f"{'═'*62}")
            # ───────────────────────────────────────────────

            cls._model = SentenceTransformer(
                config.MODEL_PATH,
                device=device
            )

            # ── DEBUG ──────────────────────────────────────
            print(f"  ✅ Model loaded successfully!")
            print(f"  📐 Embedding dimension : {cls._model.get_sentence_embedding_dimension()}")
            print(f"  📊 Max sequence length : {cls._model.max_seq_length}")
            print(f"{'═'*62}\n")
            # ───────────────────────────────────────────────

        else:
            # ── DEBUG ──────────────────────────────────────
            print(f"  ♻️  ModelService — reusing cached model (already loaded)")
            # ───────────────────────────────────────────────

        return cls._model