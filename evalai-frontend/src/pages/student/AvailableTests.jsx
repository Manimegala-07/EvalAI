import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLang } from "../../context/LangContext";
import api from "../../services/apiClient";

export default function AvailableTests({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const { t } = useLang();
  const [tests, setTests]             = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading]         = useState(true);

  useEffect(() => {
    Promise.all([api.get("/tests/student", token), api.get("/submissions/student", token)])
      .then(([ts, s]) => { setTests(ts); setSubmissions(s); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;

  return (
    <>
      <div className="page-header">
        <h1>{t("available_tests")}</h1>
        <p>{t("track_progress")}</p>
      </div>
      <div className="page-body">
        <div className="page-inner">
          {tests.length === 0 ? (
            <div className="empty-state"><div className="icon">📝</div><p>{t("no_data")}</p></div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
              {tests.map(test => {
                const done = submissions.find(s => s.test_id === test.id);
                const badgeClass = done ? (done.status === "evaluated" ? "badge-green" : "badge-amber") : "badge-blue";
                const badgeLabel = done ? (done.status === "evaluated" ? t("evaluated") : t("pending")) : t("available");
                return (
                  <div className="card card-pad" key={test.id}>
                    <div className="flex items-start justify-between mb-3">
                      <div style={{ fontSize: 32 }}>📝</div>
                      <span className={`badge ${badgeClass}`}>{badgeLabel}</span>
                    </div>
                    <div className="font-600" style={{ fontSize: 16, marginBottom: 4 }}>{test.title}</div>
                    <div className="text-sm text-muted mb-4">{t("test")} #{test.id}</div>
                    {!done ? (
                      <button className="btn btn-primary w-full"
                        onClick={() => { setSelectedTest(test); setPage("take_test"); }}>
                        {t("start_test")}
                      </button>
                    ) : (
                      <div className="text-sm text-muted" style={{ textAlign: "center", padding: "8px 0" }}>
                        {done.status === "evaluated" ? `${t("score")}: ${done.total_score}` : t("pending")}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
