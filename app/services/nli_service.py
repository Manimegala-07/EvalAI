from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class NLIService:

    _model = None
    _tokenizer = None
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def load(cls):
        if cls._model is None:
            model_name = "cross-encoder/nli-deberta-v3-small"

            cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._model = AutoModelForSequenceClassification.from_pretrained(model_name)

            cls._model.to(cls._device)
            cls._model.eval()

            print("✅ NLI model loaded successfully")
            print("Label mapping:", cls._model.config.id2label)

    @classmethod
    def score(cls, premise, hypothesis):
        """
        Returns a soft entailment score between 0 and 1
        """

        cls.load()

        inputs = cls._tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        inputs = {k: v.to(cls._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = cls._model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0]

        id2label = cls._model.config.id2label

        entailment_score = 0.0
        neutral_score = 0.0
        contradiction_score = 0.0

        # 🔥 DO NOT ASSUME LABEL ORDER
        for idx, label in id2label.items():
            label_lower = label.lower()

            if "entail" in label_lower:
                entailment_score = probs[idx].item()

            elif "neutral" in label_lower:
                neutral_score = probs[idx].item()

            elif "contradiction" in label_lower:
                contradiction_score = probs[idx].item()

        # Soft logical score
        # Strong entailment + partial credit for neutral
        final_score = entailment_score + 0.5 * neutral_score

        return float(final_score)

    @classmethod
    def bidirectional_score(cls, reference, student):
        """
        Forward: reference entails student
        Backward: student entails reference
        """

        forward = cls.score(reference, student)
        backward = cls.score(student, reference)

        return forward, backward