import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";
import SubmissionDetail from "../shared/SubmissionDetail";

export default function TeacherSubmissions({ selectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [testId, setTestId] = useState(selectedTest?.id || "");
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSub, setSelectedSub] = useState(null);
  const [evaluating, setEvaluating] = useState(null);
  const [evalMsg, setEvalMsg] = useState("");

  useEffect(() => { api.get("/tests", token).then(setTests).catch(() => {}); }, []);

  const loadSubs = async (id) => {
    setTestId(id);
    if (!id) { setSubmissions([]); return; }
    setLoading(true);
    const data = await api.get(`/submissions/test/${id}`, token).catch(() => []);
    setSubmissions(data); setLoading(false);
  };

  const evaluateSingle = async (submissionId) => {
    setEvaluating(submissionId);
    try {
      await api.post(`/submissions/evaluate-single/${submissionId}`, {}, token);
      setEvalMsg("✅ Evaluated successfully!");
      loadSubs(testId);
      setTimeout(() => setEvalMsg(""), 3000);
    } catch (e) { setEvalMsg("❌ " + e.message); }
    setEvaluating(null);
  };

  if (selectedSub) {
    return <SubmissionDetail submission={selectedSub} setPage={() => setSelectedSub(null)} backLabel="← Back to Submissions" />;
  }

  return (
    <>
      <div className="page-header"><h1>Student Submissions</h1><p>Review individual student answers and scores</p></div>
      <div className="page-body">
        <div className="page-inner">
          <div className="form-group" style={{ maxWidth: 320 }}>
            <label className="form-label">Select Test</label>
            <select className="form-select" value={testId} onChange={e => loadSubs(e.target.value)}>
              <option value="">— Choose a test —</option>
              {tests.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
            </select>
          </div>
          {evalMsg && <div className={`alert ${evalMsg.startsWith("✅") ? "alert-success" : "alert-error"}`}>{evalMsg}</div>}
          {loading && <div className="spinner" style={{ margin: "40px auto", display: "block" }} />}
          {!loading && submissions.length > 0 && (
            <div className="card table-wrap">
              <table>
                <thead><tr><th>Student</th><th>Email</th><th>Score</th><th>Status</th><th>Submitted</th><th>Action</th></tr></thead>
                <tbody>
                  {submissions.map(s => (
                    <tr key={s.submission_id}>
                      <td className="font-600">{s.student_name}</td>
                      <td className="text-muted text-sm">{s.student_email}</td>
                      <td>{s.status === "evaluated" ? <strong>{s.total_score}</strong> : "—"}</td>
                      <td>
                        <span className={`badge ${s.status === "evaluated" ? "badge-green" : "badge-amber"}`}>
                          {s.status === "evaluated" ? "✓ Evaluated" : "⏳ Pending"}
                        </span>
                      </td>
                      <td className="text-sm text-muted">{s.submitted_at ? new Date(s.submitted_at).toLocaleDateString() : "—"}</td>
                      <td>
                        <div className="flex gap-2">
                          {s.status === "pending" && (
                            <button className="btn btn-success btn-sm" onClick={() => evaluateSingle(s.submission_id)} disabled={evaluating === s.submission_id}>
                              {evaluating === s.submission_id ? <span className="spinner" /> : "⚡ Evaluate"}
                            </button>
                          )}
                          {s.status === "evaluated" && (
                            <button className="btn btn-primary btn-sm" onClick={() => setSelectedSub(s)}>View</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!loading && testId && submissions.length === 0 && (
            <div className="empty-state"><div className="icon">📝</div><p>No submissions for this test yet.</p></div>
          )}
          {!testId && <div className="empty-state"><div className="icon">📝</div><p>Select a test to view submissions</p></div>}
        </div>
      </div>
    </>
  );
}
