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

  const weekData = [
    { day: "Mon", submissions: 4 }, { day: "Tue", submissions: 7 },
    { day: "Wed", submissions: 3 }, { day: "Thu", submissions: 9 },
    { day: "Fri", submissions: 12 }, { day: "Sat", submissions: 2 }, { day: "Sun", submissions: 1 },
  ];
  const diffData = [
    { name: "Easy", value: 34, color: "#16A34A" },
    { name: "Medium", value: 41, color: "#D97706" },
    { name: "Hard", value: 25, color: "#DC2626" },
  ];

  if (loading) return <div style={{ padding: 40 }}><div className="spinner" /></div>;

  const totalSubs  = tests.reduce((a, t) => a + (t.submission_count || 0), 0);
  const pendingEval = tests.reduce((a, t) => a + ((t.submission_count || 0) - (t.evaluated_count || 0)), 0);

  return (
    <>
      <div className="page-header"><h1>Dashboard</h1><p>Overview of your evaluation activity</p></div>
      <div className="page-body">
        <div className="page-inner">
        <div className="stat-grid mb-6">
          {[
            { label: "Total Tests",  value: tests.length,         sub: "created by you",       accent: true },
            { label: "Questions",    value: questions.total || 0, sub: "in your question bank" },
            { label: "Submissions",  value: totalSubs,            sub: "across all tests" },
            { label: "Pending Eval", value: pendingEval,          sub: "submissions waiting" },
          ].map((s, i) => (
            <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
              <div className="stat-label">{s.label}</div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-sub">{s.sub}</div>
            </div>
          ))}
        </div>

        <div className="grid-2 mb-6">
          <div className="card card-pad">
            <h3 className="section-title">Weekly Submissions</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={weekData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="submissions" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card card-pad">
            <h3 className="section-title">Question Difficulty</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={diffData} cx="50%" cy="50%" outerRadius={75} dataKey="value"
                  label={({ name, value }) => `${name} ${value}%`}>
                  {diffData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: 18 }}>Recent Tests</h3>
              <button className="btn btn-primary btn-sm" onClick={() => setPage("tests")}>View All</button>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Title</th><th>Questions</th><th>Submissions</th><th>Evaluated</th><th>Status</th></tr></thead>
              <tbody>
                {tests.slice(0, 5).map(t => (
                  <tr key={t.id}>
                    <td className="font-600">{t.title}</td>
                    <td>{t.question_count ?? "—"}</td>
                    <td>{t.submission_count ?? "—"}</td>
                    <td>{t.evaluated_count ?? "—"}</td>
                    <td><span className="badge badge-green">Active</span></td>
                  </tr>
                ))}
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
