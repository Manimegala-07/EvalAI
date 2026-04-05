import { useState, useEffect } from "react";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

export default function TeacherDashboard({ setPage }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [questions, setQuestions] = useState({ total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get("/tests", token), api.get("/questions", token)])
      .then(([t, q]) => { setTests(t); setQuestions(q); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 40 }}><div className="spinner" /></div>;

  const totalSubs   = tests.reduce((a, t) => a + (t.submission_count || 0), 0);
  const totalEval   = tests.reduce((a, t) => a + (t.evaluated_count || 0), 0);
  const pendingEval = totalSubs - totalEval;

  // Real submission status pie data
  const submissionStatusData = [
    { name: "Evaluated", value: totalEval,   color: "#16A34A" },
    { name: "Pending",   value: pendingEval, color: "#D97706" },
  ].filter(d => d.value > 0);

  // Real test performance bar data
  const testPerfData = tests.slice(0, 6).map(t => ({
    name: t.title.length > 15 ? t.title.slice(0, 15) + "…" : t.title,
    submissions: t.submission_count || 0,
    evaluated:   t.evaluated_count  || 0,
  }));

  return (
    <>
      <div className="page-header"><h1>Dashboard</h1><p>Overview of your evaluation activity</p></div>
      <div className="page-body">
        <div className="page-inner">

          {/* ── Stat Cards ── */}
          <div className="stat-grid mb-6">
            {[
              { label: "Total Tests",    value: tests.length,         sub: "created by you",        accent: true },
              { label: "Questions",      value: questions.total || 0, sub: "in your question bank" },
              { label: "Submissions",    value: totalSubs,            sub: "across all tests" },
              { label: "Pending Eval",   value: pendingEval,          sub: "submissions waiting" },
            ].map((s, i) => (
              <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
                <div className="stat-label">{s.label}</div>
                <div className="stat-value">{s.value}</div>
                <div className="stat-sub">{s.sub}</div>
              </div>
            ))}
          </div>

          {/* ── Charts ── */}
          <div className="grid-2 mb-6">

            {/* Submission Status Pie — real data */}
            <div className="card card-pad">
              <h3 className="section-title">Submission Status</h3>
              <p className="text-sm text-muted mb-3">Evaluated vs Pending across all tests</p>
              {totalSubs === 0 ? (
                <div className="empty-state" style={{ padding: "30px 0" }}>
                  <div className="icon" style={{ fontSize: 32 }}>📭</div>
                  <p>No submissions yet</p>
                </div>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie data={submissionStatusData} cx="50%" cy="50%" outerRadius={70} dataKey="value"
                        label={({ name, value }) => `${name} (${value})`}>
                        {submissionStatusData.map((d, i) => <Cell key={i} fill={d.color} />)}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex gap-4 justify-center mt-2">
                    {submissionStatusData.map(d => (
                      <div key={d.name} className="flex items-center gap-2">
                        <div style={{ width: 10, height: 10, borderRadius: "50%", background: d.color }} />
                        <span className="text-sm">{d.name}: <strong>{d.value}</strong></span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* Test Submissions Bar — real data */}
            <div className="card card-pad">
              <h3 className="section-title">Submissions per Test</h3>
              <p className="text-sm text-muted mb-3">Total vs evaluated per test</p>
              {tests.length === 0 ? (
                <div className="empty-state" style={{ padding: "30px 0" }}>
                  <div className="icon" style={{ fontSize: 32 }}>📋</div>
                  <p>No tests yet</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={testPerfData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                    <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="submissions" name="Total"     fill="#C7D4FA" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="evaluated"   name="Evaluated" fill="#2D5BE3" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* ── Recent Tests Table ── */}
          <div className="card">
            <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
              <div className="flex items-center justify-between">
                <h3 style={{ fontSize: 18 }}>Recent Tests</h3>
                <button className="btn btn-primary btn-sm" onClick={() => setPage("tests")}>View All</button>
              </div>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Title</th><th>Questions</th><th>Submissions</th><th>Evaluated</th><th>Pending</th></tr></thead>
                <tbody>
                  {tests.slice(0, 5).map(t => {
                    const pending = (t.submission_count || 0) - (t.evaluated_count || 0);
                    return (
                      <tr key={t.id}>
                        <td className="font-600">{t.title}</td>
                        <td>{t.question_count ?? "—"}</td>
                        <td>{t.submission_count ?? "—"}</td>
                        <td><span className="badge badge-green">{t.evaluated_count ?? 0}</span></td>
                        <td>{pending > 0 ? <span className="badge badge-amber">{pending} pending</span> : <span className="badge badge-green">All done</span>}</td>
                      </tr>
                    );
                  })}
                  {tests.length === 0 && (
                    <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--ink-muted)", padding: 24 }}>No tests yet</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
