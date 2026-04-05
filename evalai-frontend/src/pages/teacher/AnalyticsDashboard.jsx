import { useState, useEffect } from "react";
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from "recharts";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

const DIFF_COLORS  = { 1: "#16A34A", 2: "#65A30D", 3: "#D97706", 4: "#EA580C", 5: "#DC2626" };
const CO_COLORS    = ["#2D5BE3", "#7C3AED", "#0891B2", "#059669", "#D97706", "#DC2626"];
const BLOOMS_COLORS = { L1: "#6B7280", L2: "#2D5BE3", L3: "#0891B2", L4: "#7C3AED", L5: "#D97706", L6: "#16A34A" };

function ScoreBar({ label, value, max = 100, color }) {
  const pct = Math.round((value / max) * 100);
  const barColor = color || (pct >= 75 ? "var(--green)" : pct >= 50 ? "var(--amber)" : "var(--red)");
  return (
    <div style={{ marginBottom: 10 }}>
      <div className="flex justify-between mb-1">
        <span className="text-sm">{label}</span>
        <span className="text-sm font-600" style={{ color: barColor }}>{value}%</span>
      </div>
      <div style={{ height: 8, background: "var(--border)", borderRadius: 99, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: barColor, borderRadius: 99, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

export default function AnalyticsDashboard() {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [selectedTestId, setSelectedTestId] = useState("");
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.get("/tests", token).then(setTests).catch(() => {}); }, []);

  const loadAnalytics = async (testId) => {
    setSelectedTestId(testId);
    if (!testId) { setAnalytics(null); return; }
    setLoading(true);
    const data = await api.get(`/analytics/tests/${testId}`, token).catch(() => null);
    setAnalytics(data); setLoading(false);
  };

  const rankingData = analytics?.ranking?.slice(0, 10).map(r => ({
    name: r.student_name?.split(" ")[0] || `S${r.student_id}`,
    score: r.score,
  })) || [];

  const qData = analytics?.question_analysis
    ? Object.entries(analytics.question_analysis).map(([qid, v]) => ({
        name: `Q${qid}`,
        avg: v.average_score,
        difficulty: Math.round(v.difficulty_index * 100),
      }))
    : [];

  const diffLevelData  = analytics?.difficulty_analytics || [];
  const coData         = analytics?.co_analytics || [];
  const bloomsData     = analytics?.blooms_analytics || [];
  const scoreDist      = analytics?.score_distribution || [];
  const needsAttention = analytics?.needs_attention || [];

  return (
    <>
      <div className="page-header"><h1>Analytics</h1><p>Deep insights into test and student performance</p></div>
      <div className="page-body">
        <div className="page-inner">

          {/* ── Test Selector ── */}
          <div className="form-group" style={{ maxWidth: 320 }}>
            <label className="form-label">Select Test</label>
            <select className="form-select" value={selectedTestId} onChange={e => loadAnalytics(e.target.value)}>
              <option value="">— Choose a test —</option>
              {tests.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
            </select>
          </div>

          {loading && <div className="spinner" style={{ margin: "40px auto", display: "block" }} />}

          {!selectedTestId && (
            <div className="empty-state"><div className="icon">📊</div><p>Select a test above to view analytics</p></div>
          )}

          {analytics && !loading && (
            <>
              {/* ══ ROW 1 — Stat Cards ══ */}
              <div className="stat-grid mb-6">
                {[
                  { label: "Total Students", value: analytics.total_students,          accent: true },
                  { label: "Average Score",  value: `${analytics.average_score}`,      sub: `out of ${analytics.total_max}` },
                  { label: "Pass Rate",      value: `${analytics.pass_rate}%`,         sub: "scored ≥ 50%" },
                  { label: "Highest Score",  value: analytics.highest_score },
                  { label: "Lowest Score",   value: analytics.lowest_score },
                ].map((s, i) => (
                  <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
                    <div className="stat-label">{s.label}</div>
                    <div className="stat-value">{s.value}</div>
                    {s.sub && <div className="stat-sub">{s.sub}</div>}
                  </div>
                ))}
              </div>

              {/* ══ ROW 2 — Score Distribution + Student Ranking ══ */}
              <div className="grid-2 mb-6">
                <div className="card card-pad">
                  <h3 className="section-title">📊 Score Distribution</h3>
                  <p className="text-sm text-muted mb-4">How many students fall in each performance band</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={scoreDist} cx="50%" cy="50%" outerRadius={80} dataKey="value"
                        label={({ name, value }) => value > 0 ? `${name} (${value})` : ""}>
                        {scoreDist.map((d, i) => <Cell key={i} fill={d.color} />)}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="card card-pad">
                  <h3 className="section-title">🏆 Student Score Ranking</h3>
                  <p className="text-sm text-muted mb-4">Top students by score</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={rankingData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 12 }} domain={[0, analytics.total_max]} />
                      <Tooltip />
                      <Bar dataKey="score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* ══ ROW 3 — Question Performance ══ */}
              {qData.length > 0 && (
                <div className="card card-pad mb-6">
                  <h3 className="section-title">📝 Question-wise Performance</h3>
                  <p className="text-sm text-muted mb-4">Average score per question — helps identify which questions students struggled with</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={qData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip /><Legend />
                      <Bar dataKey="avg" name="Avg Score" fill="#2D5BE3" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="difficulty" name="Difficulty %" fill="#F87171" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* ══ ROW 4 — CO Performance ══ */}
              {coData.length > 0 && (
                <div className="card card-pad mb-6">
                  <h3 className="section-title">🎯 Course Outcome (CO) Performance</h3>
                  <p className="text-sm text-muted mb-4">Shows which learning objectives students have achieved — low CO score means that topic needs to be retaught</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={coData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                      <XAxis dataKey="co" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} unit="%" />
                      <Tooltip formatter={v => `${v}%`} />
                      <Bar dataKey="avg_score" name="Avg Score %" radius={[4, 4, 0, 0]}>
                        {coData.map((d, i) => <Cell key={i} fill={CO_COLORS[i % CO_COLORS.length]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  {/* CO score bars for quick reading */}
                  <div className="mt-4">
                    {coData.map((d, i) => (
                      <ScoreBar key={i} label={d.co} value={d.avg_score} color={CO_COLORS[i % CO_COLORS.length]} />
                    ))}
                  </div>
                </div>
              )}

              {/* ══ ROW 5 — Difficulty Performance ══ */}
              {diffLevelData.length > 0 && (
                <div className="card card-pad mb-6">
                  <h3 className="section-title">📈 Performance by Difficulty Level</h3>
                  <p className="text-sm text-muted mb-4">Shows how students performed on Easy vs Hard questions — if Easy questions score low, foundational concepts are weak</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={diffLevelData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} unit="%" />
                      <Tooltip formatter={v => `${v}%`} />
                      <Bar dataKey="avg_score" name="Avg Score %" radius={[4, 4, 0, 0]}>
                        {diffLevelData.map((d, i) => <Cell key={i} fill={DIFF_COLORS[d.level] || "#2D5BE3"} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* ══ ROW 6 — Bloom's Level Performance ══ */}
              {bloomsData.length > 0 && (
                <div className="card card-pad mb-6">
                  <h3 className="section-title">🧠 Performance by Bloom&apos;s Taxonomy Level</h3>
                  <p className="text-sm text-muted mb-4">L1=Remember, L2=Understand, L3=Apply, L4=Analyze, L5=Evaluate, L6=Create — low scores at L3+ means students can recall but cannot apply</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={bloomsData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                      <XAxis dataKey="level" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} unit="%" />
                      <Tooltip formatter={v => `${v}%`} />
                      <Bar dataKey="avg_score" name="Avg Score %" radius={[4, 4, 0, 0]}>
                        {bloomsData.map((d, i) => <Cell key={i} fill={BLOOMS_COLORS[d.level] || "#2D5BE3"} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* ══ ROW 7 — Students Needing Attention ══ */}
              {needsAttention.length > 0 && (
                <div className="card mb-6">
                  <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
                    <h3 style={{ fontSize: 18, color: "var(--red)" }}>⚠️ Students Needing Attention</h3>
                    <p className="text-sm text-muted mt-1">Students who scored below 50% — may need extra support</p>
                  </div>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Student</th>
                          <th>Score</th>
                          <th>Percentage</th>
                          <th>Weakest CO</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {needsAttention.map((s, i) => (
                          <tr key={i}>
                            <td className="font-600">{s.student_name}</td>
                            <td>{s.score}</td>
                            <td>
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{ flex: 1, height: 6, background: "var(--border)", borderRadius: 99, overflow: "hidden", maxWidth: 80 }}>
                                  <div style={{ width: `${s.percentage}%`, height: "100%", background: "var(--red)", borderRadius: 99 }} />
                                </div>
                                <span className="text-sm" style={{ color: "var(--red)" }}>{s.percentage}%</span>
                              </div>
                            </td>
                            <td>{s.weakest_co ? <span className="badge badge-red">{s.weakest_co}</span> : "—"}</td>
                            <td><span className="badge badge-red">Needs Support</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* ══ ROW 8 — Full Student Ranking Table ══ */}
              <div className="card">
                <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
                  <h3 style={{ fontSize: 18 }}>📋 Full Student Ranking</h3>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr><th>Rank</th><th>Student</th><th>Score</th><th>Percentage</th><th>Performance</th></tr>
                    </thead>
                    <tbody>
                      {analytics.ranking?.map((r, i) => {
                        const pct = Math.round((r.score / analytics.total_max) * 100);
                        return (
                          <tr key={i}>
                            <td><span className="badge badge-blue">#{i + 1}</span></td>
                            <td className="font-600">{r.student_name}</td>
                            <td>{r.score} / {analytics.total_max}</td>
                            <td>
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{ flex: 1, height: 6, background: "var(--border)", borderRadius: 99, overflow: "hidden", maxWidth: 80 }}>
                                  <div style={{ width: `${pct}%`, height: "100%", background: pct >= 75 ? "var(--green)" : pct >= 50 ? "var(--amber)" : "var(--red)", borderRadius: 99 }} />
                                </div>
                                <span className="text-sm">{pct}%</span>
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${pct >= 80 ? "badge-green" : pct >= 60 ? "badge-blue" : pct >= 40 ? "badge-amber" : "badge-red"}`}>
                                {pct >= 80 ? "🌟 Excellent" : pct >= 60 ? "✓ Good" : pct >= 40 ? "~ Pass" : "✗ Fail"}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

            </>
          )}

          {!analytics && !loading && selectedTestId && (
            <div className="empty-state"><div className="icon">📊</div><p>No evaluated submissions yet for this test.</p></div>
          )}

        </div>
      </div>
    </>
  );
}
