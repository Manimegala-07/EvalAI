import re
import math
import numpy as np
import joblib
import os
from collections import Counter

from sentence_transformers.util import cos_sim
from app.services.model_service import ModelService
from app.services.nli_service import NLIService


STOPWORDS = {
    'a','an','the','is','are','was','were','be','been','being',
    'have','has','had','do','does','did','will','would','could',
    'should','may','might','shall','can','need','dare','ought',
    'it','its','this','that','these','those','i','we','you',
    'he','she','they','what','which','who','when','where','why',
    'how','all','both','each','few','more','most','other','some',
    'such','no','nor','not','only','own','same','so','than','too',
    'very','just','but','and','or','in','on','at','to','for','of',
    'with','by','from','as','into','through','about','against',
    'between','during','without','before','after','above','below',
    'up','down','out','off','over','under','then','once','also',
    'per','used','while','where','their','there','here','its'
}

_MIN_NLI_TOKENS = 5

# ─────────────────────────────────────────────────────────────
# DEBUG HELPER  – neat separator lines in terminal
# ─────────────────────────────────────────────────────────────
def _sep(title=""):
    line = "─" * 60
    if title:
        print(f"\n┌{line}┐")
        print(f"│  🔍 {title:<55}│")
        print(f"└{line}┘")
    else:
        print(f"{'─'*62}")


class ScoringService:

    _calibrator = None

    def __init__(self):
        self.model = ModelService.get_model()
        self.calibrator = self._load_calibrator()

    @classmethod
    def _load_calibrator(cls):
        if cls._calibrator is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_path = os.path.join(base_dir, "models", "score_calibrator.pkl")
            if os.path.exists(model_path):
                cls._calibrator = joblib.load(model_path)
                print(f"✅ Calibrator loaded from: {model_path}")
            else:
                print(f"⚠️  Calibrator NOT found at: {model_path}  (fallback formula will be used)")
        return cls._calibrator

    # ─────────────────────────────────────────────────────────
    # TEXT UTILITIES
    # ─────────────────────────────────────────────────────────

    def tokenize(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        result = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
        return result

    def extract_sentences(self, text):
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip('"\'')
        text = re.sub(r'"([^"]{1,20})"', lambda m: m.group(1), text)
        text = re.sub(r"'([^']{1,20})'", lambda m: m.group(1), text)
        text = re.sub(r'(?<=[^\s\(])"(?=[\s\.]|$)', '', text)
        text = re.sub(r'^"+|"+$', '', text)
        text = re.sub(
            r'\b(e\.g|i\.e|etc|vs|fig|dr|mr|ms|prof|no|st|avg|approx)\.',
            lambda m: m.group().replace('.', '\x00'),
            text, flags=re.IGNORECASE
        )
        text = re.sub(r'(\d+)\.(\d+)',
                      lambda m: m.group().replace('.', '\x00'), text)
        for _ in range(3):
            text = re.sub(r'([A-Za-z_]\w*)\.([A-Za-z_]\w*)',
                          lambda m: m.group().replace('.', '\x01'), text)

        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z("])|(?<=[.!?])\s*$', text)
        secondary = []
        for part in parts:
            sub = re.split(r'(?<=[\)])\. +(?=[a-z])|(?<=[a-z])\. +(?=[a-z])', part)
            if len(sub) > 1 and all(len(s.split()) >= 3 for s in sub if s.strip()):
                secondary.extend(sub)
            else:
                secondary.append(part)

        refined = []
        for part in secondary:
            sub = re.split(r';\s*(?=[A-Za-z])', part)
            if all(len(s.split()) >= 4 for s in sub if s.strip()):
                refined.extend(sub)
            else:
                refined.append(part)

        sentences = []
        seen = set()
        for s in refined:
            s = s.replace('\x00', '.').replace('\x01', '.')
            s = s.strip().strip('"\'').strip()
            s = re.sub(r'\s+', ' ', s)
            if len(s.split()) < 4:
                continue
            key = re.sub(r'[^a-z0-9]', '', s.lower())
            if key in seen:
                continue
            seen.add(key)
            sentences.append(s)
        return sentences

    def build_idf(self, reference):
        sentences = self.extract_sentences(reference)

        # ── DEBUG ──────────────────────────────────────────
        _sep("IDF TABLE CONSTRUCTION")
        print(f"  📄 Total concept sentences found : {len(sentences)}")
        for i, s in enumerate(sentences):
            print(f"     Sentence [{i+1}]: {s[:90]}{'...' if len(s)>90 else ''}")
        # ───────────────────────────────────────────────────

        if len(sentences) < 2:
            tokens = self.tokenize(reference)
            freq = Counter(tokens)
            total = max(len(tokens), 1)
            idf = {t: math.log(total / f + 1) + 1 for t, f in freq.items()}
            print(f"  ⚠️  Fewer than 2 sentences → using token-freq fallback IDF")
            print(f"  📊 IDF table (top 10): { {k: round(v,3) for k,v in list(idf.items())[:10]} }")
            return idf

        N = len(sentences)
        df = Counter()
        for sent in sentences:
            for token in set(self.tokenize(sent)):
                df[token] += 1

        idf = {
            term: math.log((N + 1) / (freq + 1)) + 1
            for term, freq in df.items()
        }

        # ── DEBUG ──────────────────────────────────────────
        sorted_idf = sorted(idf.items(), key=lambda x: -x[1])
        print(f"\n  📊 IDF weights (top 15 highest → most domain-specific):")
        for term, weight in sorted_idf[:15]:
            bar = "█" * int(weight * 6)
            print(f"     {term:<20} {round(weight,4):.4f}  {bar}")
        print(f"\n  📊 IDF weights (bottom 5 lowest → most common terms):")
        for term, weight in sorted_idf[-5:]:
            print(f"     {term:<20} {round(weight,4):.4f}")
        # ───────────────────────────────────────────────────

        return idf

    # ─────────────────────────────────────────────────────────
    # CONCEPT ANALYSIS
    # ─────────────────────────────────────────────────────────

    def concept_analysis(self, reference, student):

        # ── DEBUG ──────────────────────────────────────────
        _sep("CONCEPT ANALYSIS — START")
        print(f"  📝 Reference answer  ({len(reference.split())} words):")
        print(f"     {reference[:200]}{'...' if len(reference)>200 else ''}")
        print(f"\n  ✍️  Student answer ({len(student.split())} words):")
        print(f"     {student[:200]}{'...' if len(student)>200 else ''}")
        # ───────────────────────────────────────────────────

        ref_concepts = self.extract_sentences(reference)
        if not ref_concepts:
            print("  ❌ No concept sentences extracted from reference — returning empty")
            return [], 0.0, 0.0

        ref_idf = self.build_idf(reference)
        student_tokens = list(set(self.tokenize(student)))

        # ── DEBUG ──────────────────────────────────────────
        _sep("STUDENT TOKENIZATION")
        print(f"  🔤 Student unique tokens ({len(student_tokens)}): {student_tokens}")
        # ───────────────────────────────────────────────────

        if not student_tokens:
            print("  ❌ Student answer produced zero tokens — marking all concepts as missing")
            missing = [{"concept": c, "status": "missing",
                        "coverage": 0.0, "covered_kws": [], "missing_kws": []}
                       for c in ref_concepts]
            return missing, 0.0, 0.0

        # ── DEBUG ──────────────────────────────────────────
        _sep("SENTENCE TRANSFORMER — STUDENT TOKEN ENCODING")
        print(f"  🧠 Encoding {len(student_tokens)} student tokens into 384-dim vectors...")
        # ───────────────────────────────────────────────────

        stu_tok_embeddings = self.model.encode(
            student_tokens, convert_to_tensor=True
        )

        # ── DEBUG ──────────────────────────────────────────
        print(f"  ✅ Student token embedding shape : {stu_tok_embeddings.shape}")
        # ───────────────────────────────────────────────────

        stu_sentences = self.extract_sentences(student)
        stu_has_sentences = len(stu_sentences) > 0 and len(student_tokens) >= _MIN_NLI_TOKENS

        # ── DEBUG ──────────────────────────────────────────
        _sep("STUDENT SENTENCE EXTRACTION")
        print(f"  📋 Student sentences extracted : {len(stu_sentences)}")
        for i, s in enumerate(stu_sentences):
            print(f"     [{i+1}] {s[:100]}{'...' if len(s)>100 else ''}")
        print(f"  ✅ NLI eligible (has sentences + enough tokens): {stu_has_sentences}")
        # ───────────────────────────────────────────────────

        stu_sent_embeddings = None
        if stu_has_sentences:
            print(f"  🧠 Encoding {len(stu_sentences)} student sentences...")
            stu_sent_embeddings = self.model.encode(
                stu_sentences, convert_to_tensor=True
            )
            print(f"  ✅ Student sentence embedding shape: {stu_sent_embeddings.shape}")

        concept_results = []
        total_coverage = 0.0
        wrong_count = 0

        # ── Per-concept loop ──────────────────────────────
        for c_idx, concept in enumerate(ref_concepts):

            # ── DEBUG ──────────────────────────────────────
            _sep(f"CONCEPT [{c_idx+1}/{len(ref_concepts)}]")
            print(f"  📌 Concept sentence: {concept}")
            # ───────────────────────────────────────────────

            keywords = list(set(self.tokenize(concept)))
            if not keywords:
                print("  ⚠️  No keywords extracted from concept — skipping")
                continue

            kw_weights = [(kw, ref_idf.get(kw, 1.0)) for kw in keywords]
            total_weight = sum(w for _, w in kw_weights)

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  🔑 Keywords & IDF weights ({len(keywords)}):")
            for kw, w in sorted(kw_weights, key=lambda x: -x[1]):
                print(f"     {kw:<22} IDF={round(w,4):.4f}")
            print(f"  ∑  Total IDF weight : {round(total_weight, 4)}")
            # ───────────────────────────────────────────────

            kw_list = [kw for kw, _ in kw_weights]
            kw_embeddings = self.model.encode(kw_list, convert_to_tensor=True)
            sim_matrix = cos_sim(kw_embeddings, stu_tok_embeddings).cpu().numpy()

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  📐 Similarity matrix shape: {sim_matrix.shape}  "
                  f"(keywords × student_tokens)")
            # ───────────────────────────────────────────────

            covered_weight = 0.0
            covered_kws = []
            missing_kws = []

            print(f"\n  🔎 Keyword matching (threshold θ=0.65):")
            for i, (kw, weight) in enumerate(kw_weights):
                best_sim = float(sim_matrix[i].max())
                best_tok = student_tokens[int(sim_matrix[i].argmax())]
                matched = best_sim >= 0.65

                if matched:
                    covered_weight += weight
                    covered_kws.append({
                        "keyword": kw,
                        "matched_by": best_tok,
                        "similarity": round(best_sim, 3),
                    })
                    status_icon = "✅ COVERED"
                else:
                    missing_kws.append({
                        "keyword": kw,
                        "best_sim": round(best_sim, 3),
                    })
                    status_icon = "❌ MISSING"

                print(f"     {status_icon}  '{kw}' → best match '{best_tok}'  "
                      f"sim={round(best_sim,3):.3f}  weight={round(weight,3):.3f}")

            keyword_coverage = covered_weight / max(total_weight, 1e-9)

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  📊 Covered weight  : {round(covered_weight,4)}")
            print(f"  📊 Total weight    : {round(total_weight,4)}")
            print(f"  📊 Keyword coverage: {round(keyword_coverage,4):.4f}  "
                  f"({round(keyword_coverage*100,1)}%)")
            # ───────────────────────────────────────────────

            # ── NLI contradiction check ────────────────────
            is_wrong = False
            if keyword_coverage > 0.3 and stu_has_sentences and stu_sent_embeddings is not None:

                concept_emb = self.model.encode(concept, convert_to_tensor=True)
                sent_sims   = cos_sim(concept_emb, stu_sent_embeddings)[0]
                best_sent_idx = int(sent_sims.argmax())
                best_sent = stu_sentences[best_sent_idx]
                best_sent_sim = float(sent_sims[best_sent_idx])

                # ── DEBUG ──────────────────────────────────
                _sep(f"  NLI CHECK — Concept [{c_idx+1}]")
                print(f"  🔗 Best matching student sentence (sim={round(best_sent_sim,3):.3f}):")
                print(f"     \"{best_sent}\"")
                print(f"\n  ⚡ Running DeBERTa NLI (forward + backward)...")
                # ───────────────────────────────────────────

                nli = NLIService.bidirectional_full(concept, best_sent)

                # ── DEBUG ──────────────────────────────────
                print(f"\n  📋 NLI Results:")
                print(f"     FORWARD  (premise=concept   | hyp=student)")
                print(f"       Entailment   : {round(nli['forward_ent'],4):.4f}")
                print(f"       Neutral      : {round(nli['forward_neu'],4):.4f}")
                print(f"       Contradiction: {round(nli['forward_con'],4):.4f}  "
                      f"{'⚠️  > 0.55 → WRONG FLAG!' if nli['forward_con']>0.55 else '✅ OK'}")
                print(f"\n     BACKWARD (premise=student   | hyp=concept)")
                print(f"       Entailment   : {round(nli['backward_ent'],4):.4f}")
                print(f"       Neutral      : {round(nli['backward_neu'],4):.4f}")
                print(f"       Contradiction: {round(nli['backward_con'],4):.4f}")
                # ───────────────────────────────────────────

                if nli["forward_con"] > 0.55:
                    is_wrong = True
                    wrong_count += 1
                    print(f"  🚨 Concept [{c_idx+1}] flagged as WRONG (contradiction > 0.55)")

            # ── Status assignment ──────────────────────────
            if is_wrong:
                status = "wrong"
            elif keyword_coverage >= 0.65:
                status = "matched"
            elif keyword_coverage >= 0.35:
                status = "partial"
            else:
                status = "missing"

            STATUS_ICON = {"matched":"✅","partial":"🟡","missing":"❌","wrong":"🚨"}
            print(f"\n  {STATUS_ICON.get(status,'?')} Final concept status : {status.upper()}  "
                  f"(coverage={round(keyword_coverage,4):.4f})")

            concept_results.append({
                "concept":      concept,
                "status":       status,
                "coverage":     round(keyword_coverage, 4),
                "covered_kws":  covered_kws,
                "missing_kws":  missing_kws,
            })

            if status == "matched":
                total_coverage += 1.0
            elif status == "partial":
                total_coverage += 0.5

        n = max(len(ref_concepts), 1)
        avg_coverage = round(total_coverage / n, 4)
        wrong_ratio  = round(wrong_count / n, 4)

        # ── DEBUG ──────────────────────────────────────────
        _sep("CONCEPT ANALYSIS — SUMMARY")
        print(f"  Total concepts   : {len(ref_concepts)}")
        matched  = sum(1 for r in concept_results if r['status']=='matched')
        partial  = sum(1 for r in concept_results if r['status']=='partial')
        missing  = sum(1 for r in concept_results if r['status']=='missing')
        wrong    = sum(1 for r in concept_results if r['status']=='wrong')
        print(f"  ✅ Matched  : {matched}")
        print(f"  🟡 Partial  : {partial}")
        print(f"  ❌ Missing  : {missing}")
        print(f"  🚨 Wrong    : {wrong}")
        print(f"  📊 Avg coverage : {avg_coverage}")
        print(f"  📊 Wrong ratio  : {wrong_ratio}")
        # ───────────────────────────────────────────────────

        return concept_results, avg_coverage, wrong_ratio

    # ─────────────────────────────────────────────────────────
    # SENTENCE HEATMAP
    # ─────────────────────────────────────────────────────────

    def sentence_heatmap(self, reference, student):
        ref_sentences = self.extract_sentences(reference)
        stu_sentences = self.extract_sentences(student)

        # ── DEBUG ──────────────────────────────────────────
        _sep("SENTENCE HEATMAP GENERATION")
        print(f"  📄 Reference sentences : {len(ref_sentences)}")
        print(f"  ✍️  Student sentences  : {len(stu_sentences)}")
        # ───────────────────────────────────────────────────

        if not stu_sentences or not ref_sentences:
            print("  ⚠️  Empty sentences — returning empty heatmap")
            return []

        ref_embeddings = self.model.encode(ref_sentences, convert_to_tensor=True)
        stu_embeddings = self.model.encode(stu_sentences, convert_to_tensor=True)

        heatmap = []
        for i, stu_sent in enumerate(stu_sentences):

            sims = cos_sim(stu_embeddings[i], ref_embeddings)[0]
            best_idx = int(sims.argmax())
            best_sim = float(sims[best_idx])
            best_ref = ref_sentences[best_idx]

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  🔷 Student sentence [{i+1}]: \"{stu_sent[:80]}...\"")
            print(f"     Best matching ref  [{best_idx+1}]: \"{best_ref[:80]}...\"")
            print(f"     Cosine similarity  : {round(best_sim,4):.4f}")
            # ───────────────────────────────────────────────

            nli = NLIService.bidirectional_full(best_ref, stu_sent)
            forward_ent = nli["forward_ent"]
            forward_con = nli["forward_con"]

            # ── DEBUG ──────────────────────────────────────
            print(f"     NLI forward_ent    : {round(forward_ent,4):.4f}")
            print(f"     NLI forward_con    : {round(forward_con,4):.4f}")
            # ───────────────────────────────────────────────

            if forward_con > 0.5:
                status = "wrong"
            elif best_sim > 0.60 and forward_ent > 0.35:
                status = "matched"
            elif best_sim > 0.45:
                status = "partial"
            else:
                status = "irrelevant"

            STATUS_ICON = {"matched":"✅","partial":"🟡","irrelevant":"⬜","wrong":"🚨"}
            print(f"     Status             : {STATUS_ICON.get(status,'?')} {status.upper()}")

            heatmap.append({
                "sentence":   stu_sent,
                "status":     status,
                "similarity": round(best_sim, 4),
                "entailment": round(forward_ent, 4),
            })

        # ── DEBUG ──────────────────────────────────────────
        _sep("SENTENCE HEATMAP — SUMMARY")
        for r in heatmap:
            icon = STATUS_ICON.get(r['status'], '?')
            print(f"  {icon} [{r['status']:<10}] sim={r['similarity']:.3f}  "
                  f"ent={r['entailment']:.3f}  \"{r['sentence'][:60]}...\"")
        # ───────────────────────────────────────────────────

        return heatmap

    # ─────────────────────────────────────────────────────────
    # CONFIDENCE SCORE
    # ─────────────────────────────────────────────────────────

    def compute_confidence(self, similarity, forward_ent, backward_ent,
                           coverage, wrong_ratio, length_ratio, lexical_overlap):

        # ── DEBUG ──────────────────────────────────────────
        _sep("CONFIDENCE SCORE COMPUTATION")
        print(f"  Input features to Random Forest:")
        print(f"    similarity      : {round(similarity,4):.4f}")
        print(f"    forward_ent     : {round(forward_ent,4):.4f}")
        print(f"    backward_ent    : {round(backward_ent,4):.4f}")
        print(f"    direction_gap   : {round(abs(backward_ent-forward_ent),4):.4f}")
        print(f"    coverage        : {round(coverage,4):.4f}")
        print(f"    wrong_ratio     : {round(wrong_ratio,4):.4f}")
        print(f"    length_ratio    : {round(length_ratio,4):.4f}")
        print(f"    lexical_overlap : {round(lexical_overlap,4):.4f}")
        # ───────────────────────────────────────────────────

        if self.calibrator is None:
            confidence = round((similarity + forward_ent + coverage) / 3, 4)
            print(f"  ⚠️  No calibrator → fallback formula: (sim+ent+cov)/3 = {confidence}")
            return confidence

        direction_gap = backward_ent - forward_ent
        features = np.array([[
            similarity, forward_ent, backward_ent, direction_gap,
            coverage, wrong_ratio, length_ratio, lexical_overlap
        ]])
        confidence = float(self.calibrator.predict(features)[0])
        confidence = round(min(max(confidence, 0.0), 1.0), 4)
        print(f"  ✅ Random Forest predicted confidence : {confidence}")
        return confidence

    # ─────────────────────────────────────────────────────────
    # GRADE SINGLE — MAIN PIPELINE ENTRY POINT
    # ─────────────────────────────────────────────────────────

    def grade_single(self, reference, student, max_score=10):

        # ═════════════════════════════════════════════════════
        _sep("▶▶▶  grade_single() — FULL PIPELINE START")
        print(f"  max_score = {max_score}")
        # ═════════════════════════════════════════════════════

        # ── STEP 1: Semantic Similarity ───────────────────
        _sep("STEP 1 — SEMANTIC SIMILARITY (Sentence Transformer)")
        print(f"  🧠 Encoding full reference and student answers...")

        ref_emb = self.model.encode([reference], convert_to_tensor=True)
        stu_emb = self.model.encode([student], convert_to_tensor=True)
        similarity = float(cos_sim(ref_emb, stu_emb)[0][0])

        print(f"  📐 Reference embedding shape : {ref_emb.shape}")
        print(f"  📐 Student  embedding shape  : {stu_emb.shape}")
        print(f"  ✅ Cosine similarity (S_sim)  : {round(similarity,4):.4f}  "
              f"({round(similarity*100,1)}%)")

        # ── STEP 2: Global NLI ────────────────────────────
        _sep("STEP 2 — GLOBAL BIDIRECTIONAL NLI")
        print(f"  ⚡ Running DeBERTa NLI on full answer pair...")

        global_nli   = NLIService.bidirectional_full(reference, student)
        forward_ent  = global_nli["forward_ent"]
        backward_ent = global_nli["backward_ent"]
        nli_score    = forward_ent * 0.6 + backward_ent * 0.4

        print(f"\n  📋 Global NLI Results:")
        print(f"     FORWARD  (premise=reference | hypothesis=student)")
        print(f"       Entailment   : {round(global_nli['forward_ent'],4):.4f}")
        print(f"       Neutral      : {round(global_nli['forward_neu'],4):.4f}")
        print(f"       Contradiction: {round(global_nli['forward_con'],4):.4f}")
        print(f"\n     BACKWARD (premise=student   | hypothesis=reference)")
        print(f"       Entailment   : {round(global_nli['backward_ent'],4):.4f}")
        print(f"       Neutral      : {round(global_nli['backward_neu'],4):.4f}")
        print(f"       Contradiction: {round(global_nli['backward_con'],4):.4f}")
        print(f"\n  ✅ Combined NLI score (S_nli)")
        print(f"     = 0.60×{round(forward_ent,4)} + 0.40×{round(backward_ent,4)}")
        print(f"     = {round(nli_score,4):.4f}  ({round(nli_score*100,1)}%)")

        # ── STEP 3: Concept Analysis ──────────────────────
        _sep("STEP 3 — IDF-WEIGHTED CONCEPT ANALYSIS")
        concept_results, coverage, wrong_ratio = self.concept_analysis(
            reference, student
        )
        print(f"\n  ✅ Returned from concept_analysis:")
        print(f"     avg_coverage : {coverage}")
        print(f"     wrong_ratio  : {wrong_ratio}")

        # ── STEP 4: Length + Penalties ────────────────────
        _sep("STEP 4 — LENGTH RATIO & PENALTIES")
        ref_len       = max(len(reference.split()), 1)
        stu_len       = len(student.split())
        length_ratio  = min(stu_len / ref_len, 1.0)

        length_penalty = 0.0
        if length_ratio < 0.20:
            length_penalty = 0.15 * (0.20 - length_ratio) / 0.20

        wrong_penalty = min(wrong_ratio * 0.20, 0.20)

        print(f"  📏 Reference word count : {ref_len}")
        print(f"  📏 Student  word count  : {stu_len}")
        print(f"  📏 Length ratio         : {round(length_ratio,4):.4f}")
        print(f"  ⚠️  Length penalty       : {round(length_penalty,4):.4f}  "
              f"{'(applied — answer too short!)' if length_penalty>0 else '(none)'}")
        print(f"  ⚠️  Wrong penalty        : {round(wrong_penalty,4):.4f}  "
              f"{'(applied — wrong concepts found!)' if wrong_penalty>0 else '(none)'}")

        # ── STEP 5: Lexical Overlap ───────────────────────
        _sep("STEP 5 — LEXICAL OVERLAP (Jaccard)")
        ref_words       = set(reference.lower().split())
        stu_words       = set(student.lower().split())
        lexical_overlap = len(ref_words & stu_words) / max(len(ref_words), 1)
        print(f"  📝 Reference unique words : {len(ref_words)}")
        print(f"  📝 Student  unique words  : {len(stu_words)}")
        print(f"  📝 Common words           : {len(ref_words & stu_words)}")
        print(f"  ✅ Lexical overlap (Jaccard): {round(lexical_overlap,4):.4f}")

        # ── STEP 6: Weighted Score Formula ───────────────
        _sep("STEP 6 — WEIGHTED SCORING FORMULA")
        base_ratio      = 0.47*similarity + 0.37*nli_score + 0.16*coverage
        penalized_ratio = base_ratio * (1 - wrong_penalty) * (1 - length_penalty)
        final_ratio     = max(0.0, min(penalized_ratio, 1.0))
        final_score     = round(final_ratio * max_score, 2)

        print(f"  📐 Formula: R = 0.47×S_sim + 0.37×S_nli + 0.16×S_cov")
        print(f"     = 0.47×{round(similarity,4)} + 0.37×{round(nli_score,4)} + 0.16×{round(coverage,4)}")
        print(f"     base_ratio      = {round(base_ratio,4):.4f}")
        print(f"\n  📐 Applying penalties:")
        print(f"     × (1 - wrong_penalty)  = × (1 - {round(wrong_penalty,4)}) = × {round(1-wrong_penalty,4)}")
        print(f"     × (1 - length_penalty) = × (1 - {round(length_penalty,4)}) = × {round(1-length_penalty,4)}")
        print(f"     penalized_ratio = {round(penalized_ratio,4):.4f}")
        print(f"     final_ratio     = {round(final_ratio,4):.4f}  (clamped 0–1)")
        print(f"\n  🏆 FINAL SCORE = {round(final_ratio,4)} × {max_score} = {final_score}")

        # ── STEP 7: Confidence ────────────────────────────
        confidence = self.compute_confidence(
            similarity, forward_ent, backward_ent,
            coverage, wrong_ratio, length_ratio, lexical_overlap
        )

        # ── STEP 8: Sentence Heatmap ──────────────────────
        sent_heatmap = self.sentence_heatmap(reference, student)

        # ── FINAL SUMMARY ─────────────────────────────────
        _sep("▶▶▶  grade_single() — PIPELINE COMPLETE")
        print(f"  ┌─────────────────────────────────────────┐")
        print(f"  │  S_sim     (similarity)  = {round(similarity,4):.4f}         │")
        print(f"  │  S_nli     (NLI score)   = {round(nli_score,4):.4f}         │")
        print(f"  │  S_cov     (coverage)    = {round(coverage,4):.4f}         │")
        print(f"  │  wrong_ratio             = {round(wrong_ratio,4):.4f}         │")
        print(f"  │  length_ratio            = {round(length_ratio,4):.4f}         │")
        print(f"  │  confidence              = {round(confidence,4):.4f}         │")
        print(f"  │  ─────────────────────────────────────  │")
        print(f"  │  🏆 FINAL SCORE  = {final_score} / {max_score}              │")
        print(f"  └─────────────────────────────────────────┘")

        return {
            "score":            final_score,
            "similarity":       round(similarity, 4),
            "entailment":       round(forward_ent, 4),
            "coverage":         round(coverage, 4),
            "length_ratio":     round(length_ratio, 4),
            "wrong_ratio":      round(wrong_ratio, 4),
            "confidence":       confidence,
            "concept_results":  concept_results,
            "sentence_heatmap": sent_heatmap,
        }

    def grade_batch(self, refs, students, max_score=10):
        print(f"\n{'═'*62}")
        print(f"  📦 grade_batch() called — {len(refs)} answer pair(s)")
        print(f"{'═'*62}")
        return [
            self.grade_single(ref, stu, max_score)
            for ref, stu in zip(refs, students)
        ]