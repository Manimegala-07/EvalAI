import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useAuth } from "../../context/AuthContext";
import { useLang } from "../../context/LangContext";
import api from "../../services/apiClient";

export default function StudentDashboard({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const { t } = useLang();
  const [submissions, setSubmissions] = useState([]);
  const [tests, setTests] = useState([]);

  useEffect(() => {
    Promise.all([api.get("/submissions/student", token), api.get("/tests/student", token)])
      .then(([s, t]) => { setSubmissions(s); setTests(t); }).catch(() => {});
  }, []);

  const evaluated = submissions.filter(s => s.status === "evaluated");
  const avgScore  = evaluated.length ? Math.round(evaluated.reduce((a, s) => a + s.total_score, 0) / evaluated.length) : 0;
  const scoreData = evaluated.slice(-6).map((s, i) => ({ name: `${t("test")} ${i + 1}`, score: s.total_score }));

  return (
    <>
      <div className="page-header"><h1>{t("my_dashboard")}</h1><p>{t("track_progress")}</p></div>
      <div className="page-body">
        <div className="page-inner">
        <div className="stat-grid mb-6">
          {[
            { label: t("tests_taken"), value: submissions.length, accent: true },
            { label: t("evaluated"),   value: evaluated.length },
            { label: t("avg_score"),   value: avgScore },
            { label: t("available"),   value: tests.length },
          ].map((s, i) => (
            <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
              <div className="stat-label">{s.label}</div>
              <div className="stat-value">{s.value}</div>
            </div>
          ))}
        </div>
        {scoreData.length > 0 && (
          <div className="card card-pad mb-6">
            <h3 className="section-title">{t("score_history")}</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} /><YAxis tick={{ fontSize: 12 }} />
                <Tooltip /><Bar dataKey="score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="card">
          <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: 18 }}>{t("available_tests")}</h3>
              <button className="btn btn-primary btn-sm" onClick={() => setPage("tests")}>{t("view_all")}</button>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>{t("test")}</th><th>{t("status")}</th><th>{t("action")}</th></tr></thead>
              <tbody>
                {tests.slice(0, 5).map(test => {
                  const done = submissions.find(s => s.test_id === test.id);
                  return (
                    <tr key={test.id}>
                      <td className="font-600">{test.title}</td>
                      <td>
                        <span className={`badge ${done ? (done.status === "evaluated" ? "badge-green" : "badge-amber") : "badge-blue"}`}>
                          {done ? (done.status === "evaluated" ? t("evaluated") : t("pending")) : t("available")}
                        </span>
                      </td>
                      <td>
                        {!done && (
                          <button className="btn btn-primary btn-sm"
                            onClick={() => { setSelectedTest(test); setPage("take_test"); }}>
                            {t("start_test")}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {tests.length === 0 && (
                  <tr><td colSpan={3} style={{ textAlign: "center", color: "var(--ink-muted)", padding: 24 }}>{t("no_data")}</td></tr>
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
