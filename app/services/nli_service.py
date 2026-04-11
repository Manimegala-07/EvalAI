from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class NLIService:

    _model     = None
    _tokenizer = None
    _device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MAX_TOKENS = 512

    @classmethod
    def load(cls):
        if cls._model is None:
            model_name = "cross-encoder/nli-deberta-v3-small"
            print(f"\n  🔄 Loading NLI model: {model_name} | Device: {cls._device}")
            cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._model     = AutoModelForSequenceClassification.from_pretrained(model_name)
            cls._model.to(cls._device)
            cls._model.eval()
            print(f"  ✅ NLI model loaded successfully")

    @classmethod
    def _smart_truncate(cls, premise, hypothesis, max_tokens=480):
        p_tokens = cls._tokenizer.encode(premise,    add_special_tokens=False)
        h_tokens = cls._tokenizer.encode(hypothesis, add_special_tokens=False)
        total = len(p_tokens) + len(h_tokens)
        if total <= max_tokens:
            return premise, hypothesis
        p_budget = int(max_tokens * 0.60)
        h_budget = max_tokens - p_budget
        if len(p_tokens) > p_budget:
            p_tokens   = p_tokens[:p_budget]
            premise    = cls._tokenizer.decode(p_tokens, skip_special_tokens=True)
        if len(h_tokens) > h_budget:
            h_tokens   = h_tokens[:h_budget]
            hypothesis = cls._tokenizer.decode(h_tokens, skip_special_tokens=True)
        return premise, hypothesis

    @classmethod
    def full_scores(cls, premise, hypothesis):
        cls.load()
        premise, hypothesis = cls._smart_truncate(premise, hypothesis)
        inputs = cls._tokenizer(premise, hypothesis, return_tensors="pt",
                                truncation=True, max_length=cls.MAX_TOKENS, padding=True)
        inputs = {k: v.to(cls._device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = cls._model(**inputs)
            logits  = outputs.logits
            probs   = torch.softmax(logits, dim=1)[0]

        print(f"        Raw logits   : {[round(x,4) for x in logits[0].tolist()]}")
        print(f"        Softmax probs: {[round(x,4) for x in probs.tolist()]}")

        id2label = cls._model.config.id2label
        entailment = neutral = contradiction = 0.0
        for idx, label in id2label.items():
            ll = label.lower()
            if "entail" in ll:       entailment    = probs[idx].item()
            elif "neutral" in ll:    neutral       = probs[idx].item()
            elif "contradict" in ll: contradiction = probs[idx].item()

        print(f"        → entailment={round(entailment,4):.4f}  neutral={round(neutral,4):.4f}  contradiction={round(contradiction,4):.4f}")
        return entailment, neutral, contradiction

    @classmethod
    def bidirectional_full(cls, reference, student):
        print(f"\n     ➡️  Forward pass  (premise=reference | hypothesis=student)")
        print(f"        Premise   : {reference[:80]}{'...' if len(reference)>80 else ''}")
        print(f"        Hypothesis: {student[:80]}{'...' if len(student)>80 else ''}")
        f_ent, f_neu, f_con = cls.full_scores(reference, student)

        print(f"\n     ⬅️  Backward pass (premise=student | hypothesis=reference)")
        print(f"        Premise   : {student[:80]}{'...' if len(student)>80 else ''}")
        print(f"        Hypothesis: {reference[:80]}{'...' if len(reference)>80 else ''}")
        b_ent, b_neu, b_con = cls.full_scores(student, reference)

        print(f"\n     📊 NLI Summary:")
        print(f"        Forward  → ent={round(f_ent,4):.4f}  con={round(f_con,4):.4f}")
        print(f"        Backward → ent={round(b_ent,4):.4f}  con={round(b_con,4):.4f}")

        return {
            "forward_ent":  f_ent, "forward_neu":  f_neu, "forward_con":  f_con,
            "backward_ent": b_ent, "backward_neu": b_neu, "backward_con": b_con,
        }
