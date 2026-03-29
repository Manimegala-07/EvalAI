import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLang } from "../../context/LangContext";
import api from "../../services/apiClient";

export default function MySubmissions({ setPage, setSelectedSubmission }) {
  const { token } = useAuth();
  const { t } = useLang();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/submissions/student", token)
      .then(s => { setSubmissions(s); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;

  return (
    <>
      <div className="page-header"><h1>{t("my_submissions_title")}</h1><p>{t("my_submissions_title")}</p></div>
      <div className="page-body">
        <div className="page-inner">
        {submissions.length === 0 ? (
          <div className="empty-state"><div className="icon">📈</div><p>{t("no_submissions")}</p></div>
        ) : (
          <div className="card table-wrap">
            <table>
              <thead>
                <tr><th>{t("test")}</th><th>{t("score")}</th><th>{t("status")}</th><th>{t("submitted")}</th><th>{t("action")}</th></tr>
              </thead>
              <tbody>
                {submissions.map(s => (
                  <tr key={s.submission_id}>
                    <td className="font-600">{t("test")} #{s.test_id}</td>
                    <td>{s.status === "evaluated" ? <strong>{s.total_score}</strong> : "—"}</td>
                    <td>
                      <span className={`badge ${s.status === "evaluated" ? "badge-green" : "badge-amber"}`}>
                        {s.status === "evaluated" ? `✓ ${t("evaluated")}` : t("pending")}
                      </span>
                    </td>
                    <td className="text-sm text-muted">{s.submitted_at ? new Date(s.submitted_at).toLocaleDateString() : "—"}</td>
                    <td>
                      {s.status === "evaluated" && (
                        <button className="btn btn-primary btn-sm"
                          onClick={() => { setSelectedSubmission(s); setPage("submission_detail"); }}>
                          {t("view_results")}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        </div>
      </div>
    </>
  );
}
