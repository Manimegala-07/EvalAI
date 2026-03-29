import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLang } from "../../context/LangContext";
import api from "../../services/apiClient";

const LANGUAGES = [
  { code: "en", label: "English", flag: "🇬🇧" },
  { code: "ta", label: "தமிழ்",  flag: "🇮🇳" },
  { code: "hi", label: "हिंदी",  flag: "🇮🇳" },
];

export default function TakeTest({ test, setPage, setSelectedSubmission }) {
  const { token } = useAuth();
  const { t, lang, setLanguage } = useLang();
  const [testDetail, setTestDetail]           = useState(null);
  const [answers, setAnswers]                 = useState({});
  const [submitting, setSubmitting]           = useState(false);
  const [error, setError]                     = useState("");
  const [loading, setLoading]                 = useState(true);
  const [translatedQuestions, setTranslatedQuestions] = useState({});
  const [translating, setTranslating]         = useState(false);

  useEffect(() => {
    if (!test) { setPage("tests"); return; }
    api.get(`/tests/${test.id}`, token)
      .then(d => { setTestDetail(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [test]);

  // When global lang changes, translate questions
  useEffect(() => {
    if (!testDetail) return;
    if (lang === "en") { setTranslatedQuestions({}); return; }
    translateAllQuestions(lang);
  }, [lang, testDetail]);

  const translateAllQuestions = async (targetLang) => {
    if (!testDetail?.questions) return;
    setTranslating(true);
    const translated = {};
    for (const q of testDetail.questions) {
      try {
        const res = await api.post("/translate/question", { text: q.text, target_lang: targetLang });
        translated[q.id] = res.translated;
      } catch { translated[q.id] = q.text; }
    }
    setTranslatedQuestions(translated);
    setTranslating(false);
  };

  const getQuestionText = (q) => lang === "en" ? q.text : (translatedQuestions[q.id] || q.text);

  const submit = async () => {
    const unanswered = testDetail?.questions?.filter(q => !answers[q.id]?.trim());
    if (unanswered?.length > 0) { setError(t("answer_all")); return; }
    setSubmitting(true); setError("");
    try {
      const payload = {
        test_id: test.id,
        answers: Object.entries(answers).map(([qid, ans]) => ({ question_id: parseInt(qid), student_answer: ans })),
      };
      const res = await api.post("/submissions/submit-test", payload, token);
      setSelectedSubmission({ submission_id: res.submission_id, id: res.submission_id });
      setPage("submission_detail");
    } catch (e) { setError(e.message); }
    setSubmitting(false);
  };

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;
  if (!testDetail) return <div style={{ padding: 40 }}>{t("no_data")}</div>;

  const answered = Object.values(answers).filter(a => a?.trim()).length;
  const total    = testDetail.questions?.length || 0;

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>{testDetail.title}</h1>
            <p>{answered}/{total} {t("questions_answered")}</p>
          </div>
          <div className="flex gap-3 items-center">
            {/* Language toggle — synced with global LangContext */}
            <div style={{ display: "flex", gap: 4, background: "var(--border)", borderRadius: 10, padding: 4 }}>
              {LANGUAGES.map(l => (
                <button key={l.code} onClick={() => setLanguage(l.code)}
                  style={{
                    padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer",
                    fontSize: 13, fontWeight: 600,
                    background: lang === l.code ? "var(--accent)" : "transparent",
                    color: lang === l.code ? "white" : "var(--ink-muted)",
                    transition: "all 0.2s", display: "flex", alignItems: "center", gap: 4,
                  }}>
                  {l.flag} {l.label}
                </button>
              ))}
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setPage("tests")}>{t("back")}</button>
          </div>
        </div>
      </div>

      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}

        {lang !== "en" && (
          <div className="alert alert-info" style={{ marginBottom: 16 }}>
            {t("lang_notice", { lang: LANGUAGES.find(l => l.code === lang)?.label })}
          </div>
        )}

        {translating && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 16px", background: "var(--accent-light)", borderRadius: 8, marginBottom: 16 }}>
            <div className="spinner" />
            <span style={{ fontSize: 13, color: "var(--accent)" }}>{t("translating")}</span>
          </div>
        )}

        {/* Progress bar */}
        <div className="mb-4">
          <div style={{ height: 6, background: "var(--border)", borderRadius: 99 }}>
            <div style={{ height: "100%", borderRadius: 99, background: "var(--accent)", width: `${total ? (answered / total) * 100 : 0}%`, transition: "width 0.3s ease" }} />
          </div>
        </div>

        {testDetail.questions?.map((q, i) => (
          <div className="answer-block" key={q.id}>
            <div className="q-num">
              {t("question")} {i + 1} {t("of")} {total} · {t("max")} {q.max_score} {t("pts")}
              {lang !== "en" && (
                <span style={{ marginLeft: 8, fontSize: 11, color: "var(--accent)", background: "var(--accent-light)", padding: "2px 8px", borderRadius: 20, fontWeight: 600 }}>
                  {LANGUAGES.find(l => l.code === lang)?.label}
                </span>
              )}
            </div>
            <div className="q-text" style={{ marginBottom: 8 }}>{getQuestionText(q)}</div>
            {lang !== "en" && translatedQuestions[q.id] && (
              <div style={{ fontSize: 12, color: "var(--ink-muted)", marginBottom: 10, fontStyle: "italic" }}>
                {t("original")} {q.text}
              </div>
            )}
            <textarea className="form-textarea"
              placeholder={t("write_answer")}
              value={answers[q.id] || ""}
              onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })}
              style={{ minHeight: 120 }} />
            <div style={{ fontSize: 11, color: "var(--ink-muted)", marginTop: 4, textAlign: "right" }}>
              {(answers[q.id] || "").length} {t("characters")}
            </div>
          </div>
        ))}

        <div className="flex justify-end gap-3 mt-4">
          <button className="btn btn-secondary" onClick={() => setPage("tests")}>{t("cancel")}</button>
          <button className="btn btn-primary btn-lg" onClick={submit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> {t("submitting")}</> : t("submit_test")}
          </button>
        </div>
      </div>
    </>
  );
}
