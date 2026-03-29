# app/services/nli_service.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class NLIService:

    _model     = None
    _tokenizer = None
    _device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MAX_TOKENS = 512   # DeBERTa-v3-small hard limit

    @classmethod
    def load(cls):
        if cls._model is None:
            model_name = "cross-encoder/nli-deberta-v3-small"
            print(f"\n  🔄 Loading NLI model: {model_name}")
            print(f"  💻 Device: {cls._device}")
            cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._model     = AutoModelForSequenceClassification.from_pretrained(model_name)
            cls._model.to(cls._device)
            cls._model.eval()
            print(f"  ✅ NLI model loaded successfully")
            print(f"  🏷️  Label mapping: {cls._model.config.id2label}")

    # ─────────────────────────────────────────────────────────────────
    # HELPER: truncate long texts before passing to NLI
    # Strategy: keep first 60% of premise + first 40% of hypothesis
    # so neither text dominates the token budget
    # ─────────────────────────────────────────────────────────────────
    @classmethod
    def _smart_truncate(cls, premise, hypothesis, max_tokens=480):
        """
        Truncate premise and hypothesis so their combined token count
        fits within max_tokens. Preserves the start of each text.
        """
        p_tokens = cls._tokenizer.encode(premise,    add_special_tokens=False)
        h_tokens = cls._tokenizer.encode(hypothesis, add_special_tokens=False)

        # 3 special tokens: [CLS] premise [SEP] hypothesis [SEP]
        total = len(p_tokens) + len(h_tokens)

        if total <= max_tokens:
            return premise, hypothesis  # already fits — no truncation needed

        # Budget: give 60% to premise, 40% to hypothesis
        p_budget = int(max_tokens * 0.60)
        h_budget = max_tokens - p_budget

        if len(p_tokens) > p_budget:
            p_tokens = p_tokens[:p_budget]
            premise  = cls._tokenizer.decode(p_tokens, skip_special_tokens=True)

        if len(h_tokens) > h_budget:
            h_tokens = h_tokens[:h_budget]
            hypothesis = cls._tokenizer.decode(h_tokens, skip_special_tokens=True)

        print(f"        ✂️  Truncated: premise={len(p_tokens)}tok  hypothesis={len(h_tokens)}tok")
        return premise, hypothesis

    @classmethod
    def full_scores(cls, premise, hypothesis):
        cls.load()

        print(f"\n     ⚡ NLI.full_scores()")
        print(f"        Premise    [{len(premise.split()):>3}w]: {premise[:80]}{'...' if len(premise)>80 else ''}")
        print(f"        Hypothesis [{len(hypothesis.split()):>3}w]: {hypothesis[:80]}{'...' if len(hypothesis)>80 else ''}")

        # ── FIX: smart truncate before tokenizing ────────────────────
        premise, hypothesis = cls._smart_truncate(premise, hypothesis)

        inputs = cls._tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=cls.MAX_TOKENS,  # ← explicit max_length added
            padding=True,
        )

        token_count = inputs["input_ids"].shape[1]
        print(f"        Tokenized input length: {token_count} tokens")

        inputs = {k: v.to(cls._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = cls._model(**inputs)
            logits  = outputs.logits
            probs   = torch.softmax(logits, dim=1)[0]

        print(f"        Raw logits : {[round(x,4) for x in logits[0].tolist()]}")
        print(f"        Softmax probs: {[round(x,4) for x in probs.tolist()]}")

        id2label      = cls._model.config.id2label
        entailment    = 0.0
        neutral       = 0.0
        contradiction = 0.0

        for idx, label in id2label.items():
            label_lower = label.lower()
            if "entail" in label_lower:
                entailment    = probs[idx].item()
            elif "neutral" in label_lower:
                neutral       = probs[idx].item()
            elif "contradiction" in label_lower:
                contradiction = probs[idx].item()

        print(f"        → entailment={round(entailment,4):.4f}  "
              f"neutral={round(neutral,4):.4f}  "
              f"contradiction={round(contradiction,4):.4f}")

        return entailment, neutral, contradiction

    @classmethod
    def bidirectional_full(cls, reference, student):
        print(f"\n     🔄 bidirectional_full()")
        print(f"        Reference : {reference[:70]}{'...' if len(reference)>70 else ''}")
        print(f"        Student   : {student[:70]}{'...' if len(student)>70 else ''}")

        print(f"\n     ➡️  Forward pass  (premise=reference, hyp=student):")
        f_ent, f_neu, f_con = cls.full_scores(reference, student)

        print(f"\n     ⬅️  Backward pass (premise=student,    hyp=reference):")
        b_ent, b_neu, b_con = cls.full_scores(student, reference)

        result = {
            "forward_ent":  f_ent,
            "forward_neu":  f_neu,
            "forward_con":  f_con,
            "backward_ent": b_ent,
            "backward_neu": b_neu,
            "backward_con": b_con,
        }

        print(f"\n     📊 bidirectional_full result:")
        print(f"        forward  → ent={round(f_ent,4):.4f}  neu={round(f_neu,4):.4f}  con={round(f_con,4):.4f}")
        print(f"        backward → ent={round(b_ent,4):.4f}  neu={round(b_neu,4):.4f}  con={round(b_con,4):.4f}")

        return result