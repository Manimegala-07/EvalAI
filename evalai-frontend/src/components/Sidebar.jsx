import { useAuth } from "../context/AuthContext";
import { useLang } from "../context/LangContext";
import LanguageSelector from "./LanguageSelector";

export default function Sidebar({ navItems, page, setPage }) {
  const { user, logout } = useAuth();
  const { t } = useLang();
  const initials = (user?.name || user?.email || "U").slice(0, 2).toUpperCase();

  const translateLabel = (id) => {
    const map = {
      dashboard: t("dashboard"), profile: t("my_profile"),
      questions: t("question_bank"), tests: t("tests"),
      analytics: t("analytics"), submissions: t("student_submissions"),
      results: t("my_submissions"),
    };
    return map[id] || id;
  };

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <h2>EvalAI</h2>
        <p>Academic Evaluation Platform</p>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((section, si) => (
          <div key={si}>
            {section.label && (
              <div className="nav-section-label">
                {section.label === "Content"    ? t("content")    :
                 section.label === "Insights"   ? t("insights")   :
                 section.label === "My Results" ? t("my_results") : section.label}
              </div>
            )}
            {section.items.map(item => (
              <button key={item.id} className={`nav-item ${page === item.id ? "active" : ""}`}
                onClick={() => setPage(item.id)}>
                <span className="nav-icon">{item.icon}</span>
                {translateLabel(item.id)}
              </button>
            ))}
          </div>
        ))}
      </nav>
      <LanguageSelector />
      <div className="sidebar-footer">
        <div className="user-chip">
          <div className="user-avatar">{initials}</div>
          <div className="user-info">
            <div className="name">{user?.name || user?.email}</div>
            <div className="role">{user?.role === "student" ? t("student") : t("teacher")}</div>
          </div>
          <button className="logout-btn" onClick={logout} title="Logout">⏻</button>
        </div>
      </div>
    </div>
  );
}
