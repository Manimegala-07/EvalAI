from sentence_transformers.util import cos_sim
from app.services.model_service import ModelService
from app.services.nli_service import NLIService
import joblib
import os


class ScoringService:

    _calibrator = None

    def __init__(self, training=False):
        self.model = ModelService.get_model()
        self.calibrator = None if training else self.get_calibrator()

    @classmethod
    def get_calibrator(cls):
        if cls._calibrator is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_path = os.path.join(base_dir, "models", "score_calibrator.pkl")

            if os.path.exists(model_path):
                cls._calibrator = joblib.load(model_path)
            else:
                cls._calibrator = None

        return cls._calibrator

    def grade_batch(self, refs, students, max_score=10, mode="hybrid"):

        ref_emb = self.model.encode(refs, convert_to_tensor=True)
        stu_emb = self.model.encode(students, convert_to_tensor=True)

        sims = cos_sim(ref_emb, stu_emb).diagonal().cpu().numpy()

        results = []

        for reference, student, sim in zip(refs, students, sims):

            similarity = float(sim)

            ref_words = set(reference.lower().split())
            stu_words = set(student.lower().split())

            common_words = list(ref_words & stu_words)
            missing_words = list(ref_words - stu_words)
            extra_words = list(stu_words - ref_words)

            coverage = len(common_words) / max(len(ref_words), 1)

            length_ratio = min(
                len(student.split()) / max(len(reference.split()), 1),
                1
            )

            # ================================
            # MINI LM ONLY MODE
            # ================================
            if mode == "minilm":

                final_ratio = (
                    0.6 * similarity +
                    0.3 * coverage +
                    0.1 * length_ratio
                )

                raw_score = final_ratio * max_score
                entailment = 0
                contradiction_flag = False

            # ================================
            # HYBRID MODE (Stable Version)
            # ================================
            else:

                forward = NLIService.score(reference, student)
                backward = NLIService.score(student, reference)

                contradiction_penalty = max(0, backward - forward)
                entailment = max(forward - 0.7 * contradiction_penalty, 0)

                final_ratio = (
                    0.2 * similarity +
                    0.6 * entailment +
                    0.2 * coverage
                )

                raw_score = final_ratio * max_score

                contradiction_flag = backward > forward + 0.2

                # 🔥 SOFT GATES ONLY (no hard zeroing)

                if entailment < 0.3:
                    raw_score *= 0.7

                if coverage < 0.3:
                    raw_score *= 0.8

                if length_ratio < 0.4:
                    raw_score *= 0.8

                # If strong contradiction → big penalty
                if contradiction_flag:
                    raw_score *= 0.2    

            # ================================
            # OPTIONAL CALIBRATION
            # ================================
            if self.calibrator is not None and mode == "hybrid":
                predicted = self.calibrator.predict(
                    [[similarity, entailment, coverage, length_ratio]]
                )[0]
                raw_score = 0.7 * raw_score + 0.3 * predicted

            score = round(max(0, min(raw_score, max_score)), 2)

            results.append({
                "score": score,
                "similarity": round(similarity, 4),
                "entailment": round(entailment, 4),
                "coverage": round(coverage, 4),
                "length_ratio": round(length_ratio, 4),

                "concept_data": {
                    "correct": common_words[:10],
                    "missing": missing_words[:10],
                    "extra": extra_words[:10],
                    "contradiction": contradiction_flag
                }
            })

        return results