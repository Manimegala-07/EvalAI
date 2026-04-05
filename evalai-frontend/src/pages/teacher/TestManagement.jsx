import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";
import SubmissionDetail from "../shared/SubmissionDetail";

const DEFAULT_CO_OUTCOMES = {
  CO1: "Knowledge & Recall — Recall facts, definitions, and basic concepts",
  CO2: "Comprehension — Explain and describe concepts in own words",
  CO3: "Application — Apply concepts to solve problems",
  CO4: "Analysis — Break down, compare, and examine relationships",
  CO5: "Evaluation — Justify, assess, and make judgments",
  CO6: "Creation — Design, construct, or produce something new",
};

function CreateTestModal({ onClose }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [coOutcomes, setCoOutcomes] = useState({ ...DEFAULT_CO_OUTCOMES });
  const [showCO, setShowCO] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    if (!title) { setError("Enter a title"); return; }
    setSaving(true);
    try {
      await api.post("/tests", { title, co_outcomes: coOutcomes }, token);
      onClose();
    } catch (e) { setError(e.message); }
    setSaving(false);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 620 }}>
        <div className="modal-header"><h3>Create New Test</h3><button className="modal-close" onClick={onClose}>×</button></div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Test Title</label>
            <input className="form-input" placeholder="e.g. Unit 3 - Data Structures"
              value={title} onChange={e => setTitle(e.target.value)} onKeyDown={e => e.key === "Enter" && save()} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowCO(!showCO)}>
              {showCO ? "▲ Hide" : "▼ Customize"} Course Outcomes (CO1–CO6)
            </button>
          </div>
          {showCO && (
            <div style={{ background: "var(--cream)", borderRadius: 8, padding: 16, marginBottom: 16 }}>
              <div className="text-xs text-muted font-600 mb-3" style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Course Outcomes — Edit descriptions for this test
              </div>
              {Object.keys(coOutcomes).map(co => (
                <div className="form-group" key={co} style={{ marginBottom: 10 }}>
                  <label className="form-label" style={{ fontSize: 12 }}>{co}</label>
                  <input className="form-input" style={{ fontSize: 13 }}
                    value={coOutcomes[co]}
                    onChange={e => setCoOutcomes(prev => ({ ...prev, [co]: e.target.value }))} />
                </div>
              ))}
            </div>
          )}
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
  const [selectedCO, setSelectedCO] = useState("");
  const [tab, setTab] = useState("existing");
  const [loading, setLoading] = useState(true);

  const coOutcomes = test.co_outcomes || DEFAULT_CO_OUTCOMES;

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

  const addQ    = async (qId) => { await api.post(`/tests/${test.id}/questions`, { question_id: qId, max_score: maxScore, co_mapping: selectedCO || null }, token); fetchData(); };
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
            <button className={`tab-btn ${tab === "co" ? "active" : ""}`} onClick={() => setTab("co")}>CO Outcomes</button>
          </div>

          {tab === "existing" && (
            <>
              <div className="flex gap-3 mb-4" style={{ flexWrap: "wrap" }}>
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
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <label className="form-label" style={{ margin: 0, whiteSpace: "nowrap" }}>Map to CO:</label>
                  <select className="form-select" style={{ width: 90 }} value={selectedCO} onChange={e => setSelectedCO(e.target.value)}>
                    <option value="">-- None --</option>
                    {Object.keys(coOutcomes).map(co => <option key={co} value={co}>{co}</option>)}
                  </select>
                </div>
              </div>
              {loading ? <div className="spinner" style={{ margin: "20px auto" }} /> : (
                allQuestions.map(q => (
                  <div className={`q-card ${inTest.has(q.id) ? "selected" : ""}`} key={q.id}>
                    <div className="flex justify-between items-start">
                      <div style={{ flex: 1 }}>
                        <div className="q-text">{q.text}</div>
                        <div className="q-answer">{q.model_answer}</div>
                        <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                          {q.difficulty && <span className="badge badge-amber">D{q.difficulty}</span>}
                          {q.blooms_level && <span className="badge badge-blue">{q.blooms_level}</span>}
                        </div>
                      </div>
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
                    <div style={{ flex: 1 }}>
                      <div className="q-text">{q.text}</div>
                      <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                        <span className="badge badge-amber">Max: {q.max_score} pts</span>
                        {q.co_mapping && <span className="badge badge-green">{q.co_mapping}</span>}
                        {q.difficulty && <span className="badge badge-amber">D{q.difficulty}</span>}
                        {q.blooms_level && <span className="badge badge-blue">{q.blooms_level}</span>}
                      </div>
                    </div>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: 12 }} onClick={() => removeQ(q.id)}>Remove</button>
                  </div>
                </div>
              ))
          )}

          {tab === "co" && (
            <div>
              <p className="text-sm text-muted mb-4">Course Outcomes defined for this test:</p>
              {Object.entries(coOutcomes).map(([co, desc]) => (
                <div key={co} style={{ padding: "12px 16px", background: "var(--accent-light)", borderRadius: 8, marginBottom: 8, borderLeft: "4px solid var(--accent)" }}>
                  <div className="font-600 text-sm" style={{ color: "var(--accent)", marginBottom: 4 }}>{co}</div>
                  <div className="text-sm">{desc}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Submissions panel shown inline below each test row ──
function SubmissionsPanel({ test, token, onViewDetail }) {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(null);
  const [evaluatingAll, setEvaluatingAll] = useState(false);
  const [msg, setMsg] = useState("");

  const load = async () => {
    setLoading(true);
    const data = await api.get(`/submissions/test/${test.id}`, token).catch(() => []);
    setSubmissions(data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const evaluateSingle = async (submissionId) => {
    setEvaluating(submissionId);
    try {
      await api.post(`/submissions/evaluate-single/${submissionId}`, {}, token);
      setMsg("✅ Evaluated!");
      load();
      setTimeout(() => setMsg(""), 3000);
    } catch (e) { setMsg("❌ " + e.message); }
    setEvaluating(null);
  };

  const evaluateAll = async () => {
    setEvaluatingAll(true);
    try {
      const res = await api.post(`/submissions/evaluate/${test.id}`, {}, token);
      setMsg(`✅ ${res.evaluated_count} submissions evaluated!`);
      load();
      setTimeout(() => setMsg(""), 3000);
    } catch (e) { setMsg("❌ " + e.message); }
    setEvaluatingAll(false);
  };

  const pending = submissions.filter(s => s.status === "pending").length;

  return (
    <div style={{ background: "var(--cream)", borderTop: "1px solid var(--border)", padding: "16px 24px" }}>
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-600" style={{ color: "var(--ink)" }}>
          Student Submissions — {submissions.length} total, {pending} pending
        </div>
        {pending > 0 && (
          <button className="btn btn-success btn-sm" onClick={evaluateAll} disabled={evaluatingAll}>
            {evaluatingAll ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Evaluating...</> : `⚡ Evaluate All (${pending})`}
          </button>
        )}
      </div>

      {msg && <div className={`alert ${msg.startsWith("✅") ? "alert-success" : "alert-error"} mb-3`} style={{ padding: "8px 12px", fontSize: 13 }}>{msg}</div>}

      {loading ? (
        <div className="spinner" style={{ margin: "20px auto", display: "block" }} />
      ) : submissions.length === 0 ? (
        <div style={{ textAlign: "center", color: "var(--ink-muted)", padding: "16px 0", fontSize: 13 }}>No submissions yet</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              {["Student", "Score", "Status", "Submitted", "Action"].map(h => (
                <th key={h} style={{ fontSize: 11, fontWeight: 600, color: "var(--ink-muted)", textTransform: "uppercase", padding: "8px 12px", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {submissions.map(s => (
              <tr key={s.submission_id} style={{ borderBottom: "1px solid var(--border)" }}>
                <td style={{ padding: "10px 12px", fontSize: 13, fontWeight: 600 }}>{s.student_name}</td>
                <td style={{ padding: "10px 12px", fontSize: 13 }}>{s.status === "evaluated" ? <strong>{s.total_score}</strong> : "—"}</td>
                <td style={{ padding: "10px 12px" }}>
                  <span className={`badge ${s.status === "evaluated" ? "badge-green" : "badge-amber"}`} style={{ fontSize: 11 }}>
                    {s.status === "evaluated" ? "✓ Evaluated" : "⏳ Pending"}
                  </span>
                </td>
                <td style={{ padding: "10px 12px", fontSize: 12, color: "var(--ink-muted)" }}>
                  {s.submitted_at ? new Date(s.submitted_at).toLocaleDateString() : "—"}
                </td>
                <td style={{ padding: "10px 12px" }}>
                  <div className="flex gap-2">
                    {s.status === "pending" && (
                      <button className="btn btn-success btn-sm" onClick={() => evaluateSingle(s.submission_id)} disabled={evaluating === s.submission_id}>
                        {evaluating === s.submission_id ? <span className="spinner" style={{ width: 12, height: 12 }} /> : "⚡ Evaluate"}
                      </button>
                    )}
                    {s.status === "evaluated" && (
                      <button className="btn btn-primary btn-sm" onClick={() => onViewDetail(s)}>View</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function TestManagement({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTestModal, setSelectedTestModal] = useState(null);
  const [expandedTestId, setExpandedTestId] = useState(null);
  const [selectedSub, setSelectedSub] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTests = async () => {
    setLoading(true);
    const data = await api.get("/tests", token).catch(() => []);
    setTests(data); setLoading(false);
  };

  useEffect(() => { fetchTests(); }, []);

  if (selectedSub) {
    return <SubmissionDetail submission={selectedSub} setPage={() => setSelectedSub(null)} backLabel="← Back to Tests" isTeacher={true} />;
  }

  return (
    <>
      <div className="page-header"><h1>Tests</h1><p>Create and manage your tests</p></div>
      <div className="page-body">
        <div className="page-inner">
          <div className="flex justify-end mb-4">
            <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Test</button>
          </div>
          {loading ? (
            <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
          ) : tests.length === 0 ? (
            <div className="empty-state"><div className="icon">📋</div><p>No tests yet. Create your first test!</p></div>
          ) : (
            <div className="card">
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid var(--border)", background: "#f8f9fc" }}>
                    {["Title", "Questions", "Submissions", "Evaluated", "Actions"].map(h => (
                      <th key={h} style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-muted)", textTransform: "uppercase", padding: "14px 20px", textAlign: "left" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tests.map(t => (
                    <>
                      <tr key={t.id} style={{ borderBottom: expandedTestId === t.id ? "none" : "1px solid var(--border)", background: expandedTestId === t.id ? "var(--accent-light)" : "white" }}>
                        <td style={{ padding: "14px 20px", fontWeight: 600 }}>{t.title}</td>
                        <td style={{ padding: "14px 20px" }}>{t.question_count ?? "—"}</td>
                        <td style={{ padding: "14px 20px" }}>{t.submission_count ?? "—"}</td>
                        <td style={{ padding: "14px 20px" }}>{t.evaluated_count ?? "—"}</td>
                        <td style={{ padding: "14px 20px" }}>
                          <div className="flex gap-2">
                            <button className="btn btn-secondary btn-sm" onClick={() => setSelectedTestModal(t)}>
                              Manage Questions
                            </button>
                            <button
                              className={`btn btn-sm ${expandedTestId === t.id ? "btn-primary" : "btn-secondary"}`}
                              onClick={() => setExpandedTestId(expandedTestId === t.id ? null : t.id)}>
                              {expandedTestId === t.id ? "▲ Hide" : "▼ Submissions"}
                            </button>
                          </div>
                        </td>
                      </tr>
                      {expandedTestId === t.id && (
                        <tr key={`${t.id}-panel`}>
                          <td colSpan={5} style={{ padding: 0 }}>
                            <SubmissionsPanel
                              test={t}
                              token={token}
                              onViewDetail={(sub) => setSelectedSub(sub)}
                            />
                          </td>
                        </tr>
                      )}
                    </>
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
