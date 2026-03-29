import { useState, useEffect } from "react";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

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

  const rankingData = analytics?.ranking?.slice(0, 8).map((r, i) => ({ name: `S${r.student_id}`, score: r.score, rank: i + 1 })) || [];
  const qData = analytics?.question_analysis
    ? Object.entries(analytics.question_analysis).map(([qid, v]) => ({ name: `Q${qid}`, avg: v.average_score, difficulty: Math.round(v.difficulty_index * 100) }))
    : [];
  const diffPie = analytics ? [
    { name: "Easy (≤30%)",  value: qData.filter(q => q.difficulty <= 30).length,                          color: "#16A34A" },
    { name: "Medium",       value: qData.filter(q => q.difficulty > 30 && q.difficulty <= 60).length,     color: "#D97706" },
    { name: "Hard (>60%)",  value: qData.filter(q => q.difficulty > 60).length,                           color: "#DC2626" },
  ] : [];

  return (
    <>
      <div className="page-header"><h1>Analytics</h1><p>Deep insights into test and student performance</p></div>
      <div className="page-body">
        <div className="page-inner">
        <div className="form-group" style={{ maxWidth: 320 }}>
          <label className="form-label">Select Test</label>
          <select className="form-select" value={selectedTestId} onChange={e => loadAnalytics(e.target.value)}>
            <option value="">— Choose a test —</option>
            {tests.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>
        </div>
        {loading && <div className="spinner" style={{ margin: "40px auto", display: "block" }} />}
        {analytics && !loading && (
          <>
            <div className="stat-grid mb-6">
              {[
                { label: "Average Score",  value: analytics.average_score, accent: true },
                { label: "Highest Score",  value: analytics.highest_score },
                { label: "Lowest Score",   value: analytics.lowest_score },
                { label: "Total Students", value: analytics.ranking?.length || 0 },
              ].map((s, i) => (
                <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
                  <div className="stat-label">{s.label}</div>
                  <div className="stat-value">{s.value}</div>
                </div>
              ))}
            </div>
            <div className="grid-2 mb-6">
              <div className="card card-pad">
                <h3 className="section-title">Student Score Ranking</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={rankingData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} /><YAxis tick={{ fontSize: 12 }} />
                    <Tooltip /><Bar dataKey="score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="card card-pad">
                <h3 className="section-title">Difficulty Distribution</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={diffPie} cx="50%" cy="50%" outerRadius={80} dataKey="value"
                      label={({ name, value }) => value > 0 ? `${name} (${value})` : ""}>
                      {diffPie.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie><Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            {qData.length > 0 && (
              <div className="card card-pad mb-6">
                <h3 className="section-title">Question Performance</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={qData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} /><YAxis tick={{ fontSize: 12 }} />
                    <Tooltip /><Legend />
                    <Bar dataKey="avg" name="Avg Score" fill="#2D5BE3" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="difficulty" name="Difficulty %" fill="#F87171" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            <div className="card">
              <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}><h3 style={{ fontSize: 18 }}>Student Ranking</h3></div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Rank</th><th>Student ID</th><th>Score</th><th>Performance</th></tr></thead>
                  <tbody>
                    {analytics.ranking?.map((r, i) => (
                      <tr key={i}>
                        <td><span className="badge badge-blue">#{i + 1}</span></td>
                        <td className="font-600">Student {r.student_id}</td>
                        <td>{r.score}</td>
                        <td><span className={`badge ${i === 0 ? "badge-green" : i < 3 ? "badge-blue" : "badge-gray"}`}>{i === 0 ? "🥇 Top" : i < 3 ? "Above Avg" : "Avg"}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
        {!analytics && !loading && selectedTestId && <div className="empty-state"><div className="icon">📊</div><p>No evaluated submissions yet for this test.</p></div>}
        {!selectedTestId && <div className="empty-state"><div className="icon">📊</div><p>Select a test above to view analytics</p></div>}
        </div>
      </div>
    </>
  );
}
