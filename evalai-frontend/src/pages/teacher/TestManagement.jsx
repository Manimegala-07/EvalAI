import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

function CreateTestModal({ onClose }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    if (!title) { setError("Enter a title"); return; }
    setSaving(true);
    try { await api.post("/tests", { title }, token); onClose(); }
    catch (e) { setError(e.message); }
    setSaving(false);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header"><h3>Create New Test</h3><button className="modal-close" onClick={onClose}>×</button></div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Test Title</label>
            <input className="form-input" placeholder="e.g. Unit 3 - Data Structures"
              value={title} onChange={e => setTitle(e.target.value)} onKeyDown={e => e.key === "Enter" && save()} />
          </div>
          <div className="flex gap-3 justify-end">
            <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={save} disabled={saving}>
              {saving ? <span className="spinner" /> : "Create Test"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function TestQuestionsModal({ test, onClose }) {
  const { token } = useAuth();
  const [testDetail, setTestDetail] = useState(null);
  const [allQuestions, setAllQuestions] = useState([]);
  const [search, setSearch] = useState("");
  const [maxScore, setMaxScore] = useState(10);
  const [tab, setTab] = useState("existing");
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    const [detailRes, qsRes] = await Promise.allSettled([
      api.get(`/tests/${test.id}`, token),
      api.get(`/questions?search=${encodeURIComponent(search)}`, token),
    ]);
    setTestDetail(detailRes.status === "fulfilled" ? detailRes.value : { questions: [] });
    setAllQuestions(qsRes.status === "fulfilled" ? (qsRes.value.items || []) : []);
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);
  useEffect(() => { const t = setTimeout(() => fetchData(), 400); return () => clearTimeout(t); }, [search]);

  const addQ    = async (qId) => { await api.post(`/tests/${test.id}/questions`, { question_id: qId, max_score: maxScore }, token); fetchData(); };
  const removeQ = async (qId) => { await api.delete(`/tests/${test.id}/questions/${qId}`, token); fetchData(); };
  const inTest  = new Set(testDetail?.questions?.map(q => q.id) || []);

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 680 }}>
        <div className="modal-header"><h3>{test.title} — Questions</h3><button className="modal-close" onClick={onClose}>×</button></div>
        <div className="modal-body">
          <div className="tabs">
            <button className={`tab-btn ${tab === "existing" ? "active" : ""}`} onClick={() => setTab("existing")}>Add from Bank</button>
            <button className={`tab-btn ${tab === "current" ? "active" : ""}`} onClick={() => setTab("current")}>
              Current Questions ({testDetail?.questions?.length || 0})
            </button>
          </div>
          {tab === "existing" && (
            <>
              <div className="flex gap-3 mb-4">
                <div className="search-bar" style={{ flex: 1 }}>
                  <span className="search-icon">🔍</span>
                  <input className="form-input" placeholder="Search question bank..."
                    value={search} onChange={e => setSearch(e.target.value)} />
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <label className="form-label" style={{ margin: 0, whiteSpace: "nowrap" }}>Max Score:</label>
                  <input className="form-input" type="number" style={{ width: 70 }}
                    value={maxScore} onChange={e => setMaxScore(Number(e.target.value))} />
                </div>
              </div>
              {loading ? <div className="spinner" style={{ margin: "20px auto" }} /> : (
                allQuestions.map(q => (
                  <div className={`q-card ${inTest.has(q.id) ? "selected" : ""}`} key={q.id}>
                    <div className="flex justify-between items-start">
                      <div style={{ flex: 1 }}><div className="q-text">{q.text}</div><div className="q-answer">{q.model_answer}</div></div>
                      <div style={{ marginLeft: 12 }}>
                        {inTest.has(q.id)
                          ? <button className="btn btn-danger btn-sm" onClick={() => removeQ(q.id)}>Remove</button>
                          : <button className="btn btn-primary btn-sm" onClick={() => addQ(q.id)}>Add</button>}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </>
          )}
          {tab === "current" && (
            testDetail?.questions?.length === 0
              ? <div className="empty-state" style={{ padding: "30px 0" }}><p>No questions in this test yet.</p></div>
              : testDetail?.questions?.map(q => (
                <div className="q-card" key={q.id}>
                  <div className="flex justify-between items-start">
                    <div style={{ flex: 1 }}><div className="q-text">{q.text}</div><span className="badge badge-amber">Max: {q.max_score} pts</span></div>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: 12 }} onClick={() => removeQ(q.id)}>Remove</button>
                  </div>
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  );
}

export default function TestManagement({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTestModal, setSelectedTestModal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(null);
  const [evalMsg, setEvalMsg] = useState("");

  const fetchTests = async () => {
    setLoading(true);
    const data = await api.get("/tests", token).catch(() => []);
    setTests(data); setLoading(false);
  };

  useEffect(() => { fetchTests(); }, []);

  const evaluate = async (testId) => {
    setEvaluating(testId);
    try {
      const res = await api.post(`/submissions/evaluate/${testId}`, {}, token);
      setEvalMsg(`✅ ${res.evaluated_count} submissions evaluated`);
      fetchTests();
      setTimeout(() => setEvalMsg(""), 4000);
    } catch (e) { setEvalMsg("❌ " + e.message); }
    setEvaluating(null);
  };

  return (
    <>
      <div className="page-header"><h1>Tests</h1><p>Create and manage your tests</p></div>
      <div className="page-body">
        <div className="page-inner">
        {evalMsg && <div className={`alert ${evalMsg.startsWith("✅") ? "alert-success" : "alert-error"}`}>{evalMsg}</div>}
        <div className="flex justify-end mb-4">
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Test</button>
        </div>
        {loading ? (
          <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
        ) : tests.length === 0 ? (
          <div className="empty-state"><div className="icon">📋</div><p>No tests yet. Create your first test!</p></div>
        ) : (
          <div className="card table-wrap">
            <table>
              <thead><tr><th>Title</th><th>Questions</th><th>Submissions</th><th>Evaluated</th><th>Actions</th></tr></thead>
              <tbody>
                {tests.map(t => (
                  <tr key={t.id}>
                    <td className="font-600">{t.title}</td>
                    <td>{t.question_count ?? "—"}</td>
                    <td>{t.submission_count ?? "—"}</td>
                    <td>{t.evaluated_count ?? "—"}</td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn btn-secondary btn-sm" onClick={() => setSelectedTestModal(t)}>Manage Questions</button>
                        <button className="btn btn-success btn-sm" onClick={() => evaluate(t.id)} disabled={evaluating === t.id}>
                          {evaluating === t.id ? <span className="spinner" /> : "⚡ Evaluate"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        </div>
      </div>
      {showCreate && <CreateTestModal onClose={() => { setShowCreate(false); fetchTests(); }} />}
      {selectedTestModal && <TestQuestionsModal test={selectedTestModal} onClose={() => { setSelectedTestModal(null); fetchTests(); }} />}
    </>
  );
}
