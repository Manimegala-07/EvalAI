import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

function CreateQuestionModal({ onClose }) {
  const { token } = useAuth();
  const [form, setForm] = useState({ text: "", model_answer: "", model_answer_ta: "", model_answer_hi: "" });
  const [validation, setValidation] = useState(null);
  const [validating, setValidating] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("english");

  const autoTranslate = async () => {
    if (!form.model_answer.trim()) return;
    setTranslating(true);
    try {
      const [ta, hi] = await Promise.all([
        api.post("/translate/question", { text: form.model_answer, target_lang: "ta" }),
        api.post("/translate/question", { text: form.model_answer, target_lang: "hi" }),
      ]);
      setForm(f => ({ ...f, model_answer_ta: ta.translated, model_answer_hi: hi.translated }));
    } catch (e) { console.error("Auto-translate failed:", e); }
    setTranslating(false);
  };

  const validate = async () => {
    if (!form.text || !form.model_answer) { setError("Fill both fields first"); return; }
    setValidating(true); setError("");
    try {
      const res = await api.post("/questions/validate", { text: form.text, model_answer: form.model_answer }, token);
      setValidation(res);
    } catch (e) { setError(e.message); }
    setValidating(false);
  };

  const save = async () => {
    if (!form.text || !form.model_answer) { setError("Fill both fields"); return; }
    setSaving(true);
    try { await api.post("/questions", form, token); onClose(); }
    catch (e) { setError(e.message); }
    setSaving(false);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 660 }}>
        <div className="modal-header">
          <h3>Add New Question</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Question Text</label>
            <textarea className="form-textarea" placeholder="Enter your question..."
              value={form.text} onChange={e => setForm({ ...form, text: e.target.value })} />
          </div>
          <div className="tabs">
            {[{ id: "english", label: "🇬🇧 English Reference" }, { id: "tamil", label: "🇮🇳 Tamil Reference" }, { id: "hindi", label: "🇮🇳 Hindi Reference" }].map(t => (
              <button key={t.id} className={`tab-btn ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>{t.label}</button>
            ))}
          </div>
          {tab === "english" && (
            <div className="form-group">
              <label className="form-label">English Reference Answer</label>
              <textarea className="form-textarea" placeholder="Enter the model/reference answer in English..."
                value={form.model_answer} onChange={e => setForm({ ...form, model_answer: e.target.value })} onBlur={autoTranslate} />
              <div className="text-xs text-muted mt-1">Tamil and Hindi references will be auto-generated when you click away</div>
            </div>
          )}
          {tab === "tamil" && (
            <div className="form-group">
              <div className="flex items-center justify-between mb-2">
                <label className="form-label" style={{ margin: 0 }}>Tamil Reference Answer</label>
                {translating ? <div className="flex items-center gap-2"><div className="spinner" /><span className="text-xs text-muted">Translating...</span></div>
                  : <button className="btn btn-secondary btn-sm" onClick={autoTranslate}>🔄 Re-translate</button>}
              </div>
              <textarea className="form-textarea" placeholder="Tamil reference will be auto-generated..."
                value={form.model_answer_ta} onChange={e => setForm({ ...form, model_answer_ta: e.target.value })} />
            </div>
          )}
          {tab === "hindi" && (
            <div className="form-group">
              <div className="flex items-center justify-between mb-2">
                <label className="form-label" style={{ margin: 0 }}>Hindi Reference Answer</label>
                {translating ? <div className="flex items-center gap-2"><div className="spinner" /><span className="text-xs text-muted">Translating...</span></div>
                  : <button className="btn btn-secondary btn-sm" onClick={autoTranslate}>🔄 Re-translate</button>}
              </div>
              <textarea className="form-textarea" placeholder="Hindi reference will be auto-generated..."
                value={form.model_answer_hi} onChange={e => setForm({ ...form, model_answer_hi: e.target.value })} />
            </div>
          )}
          <div className="flex gap-3 mb-4">
            <button className="btn btn-secondary" onClick={validate} disabled={validating}>
              {validating ? <><span className="spinner" /> Validating...</> : "✨ Validate with AI"}
            </button>
          </div>
          {validation && (
            <div className="validation-panel mb-4">
              <div className="text-sm font-600 mb-2">AI Validation Result</div>
              <div className="flex gap-3 mb-2">
                <span className={`badge ${validation.analysis?.grammar_ok ? "badge-green" : "badge-red"}`}>
                  {validation.analysis?.grammar_ok ? "✓ Grammar OK" : "✗ Grammar Issues"}
                </span>
                <span className={`badge ${validation.analysis?.answers_question ? "badge-green" : "badge-amber"}`}>
                  {validation.analysis?.answers_question ? "✓ Answers Question" : "⚠ Unclear"}
                </span>
              </div>
              {validation.analysis?.comments && <div className="text-sm text-muted">{validation.analysis.comments}</div>}
            </div>
          )}
          <div className="flex gap-3 justify-end">
            <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={save} disabled={saving}>
              {saving ? <span className="spinner" /> : "Save Question"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function QuestionBank() {
  const { token } = useAuth();
  const [data, setData] = useState({ total: 0, items: [] });
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchQuestions = async (q = "") => {
    setLoading(true);
    const res = await api.get(`/questions?search=${encodeURIComponent(q)}`, token).catch(() => ({ total: 0, items: [] }));
    setData(res);
    setLoading(false);
  };

  useEffect(() => { fetchQuestions(); }, []);
  useEffect(() => {
    const t = setTimeout(() => fetchQuestions(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  return (
    <>
      <div className="page-header"><h1>Question Bank</h1><p>{data.total} questions in your bank</p></div>
      <div className="page-body">
        <div className="page-inner">
        <div className="flex items-center justify-between mb-4">
          <div className="search-bar" style={{ width: 320 }}>
            <span className="search-icon">🔍</span>
            <input className="form-input" placeholder="Search questions..."
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Question</button>
        </div>
        {loading ? (
          <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
        ) : data.items.length === 0 ? (
          <div className="empty-state"><div className="icon">❓</div><p>No questions found. Add your first question!</p></div>
        ) : (
          data.items.map(q => (
            <div className="q-card" key={q.id}>
              <div className="flex justify-between items-start">
                <div style={{ flex: 1 }}>
                  <div className="q-text">{q.text}</div>
                  <div className="q-answer">{q.model_answer}</div>
                </div>
                <span className="badge badge-blue" style={{ marginLeft: 12, flexShrink: 0 }}>Q#{q.id}</span>
              </div>
            </div>
          ))
        )}
        </div>
      </div>
      {showCreate && <CreateQuestionModal onClose={() => { setShowCreate(false); fetchQuestions(search); }} />}
    </>
  );
}
