import { useState, useEffect, createContext, useContext } from "react";
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, Legend
} from "recharts";

// ─────────────────────────────────────────────
// STYLES
// ─────────────────────────────────────────────
const style = document.createElement("style");
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --cream: #FAF8F4;
    --white: #FFFFFF;
    --ink: #1A1A2E;
    --ink-light: #4A4A6A;
    --ink-muted: #8888AA;
    --accent: #2D5BE3;
    --accent-light: #EEF2FF;
    --accent-soft: #C7D4FA;
    --green: #16A34A;
    --green-light: #DCFCE7;
    --red: #DC2626;
    --red-light: #FEE2E2;
    --amber: #D97706;
    --amber-light: #FEF3C7;
    --border: #E8E6F0;
    --shadow-sm: 0 1px 3px rgba(26,26,46,0.08);
    --shadow-md: 0 4px 16px rgba(26,26,46,0.10);
    --shadow-lg: 0 8px 32px rgba(26,26,46,0.13);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-lg: 20px;
  }

  html, body, #root { height: 100%; font-family: 'DM Sans', sans-serif; background: var(--cream); color: var(--ink); font-size: 15px; line-height: 1.6; }
  h1, h2, h3, h4 { font-family: 'DM Serif Display', serif; letter-spacing: -0.02em; }

  .app-shell { display: flex; min-height: 100vh; }
  .sidebar { width: 260px; min-height: 100vh; background: var(--white); border-right: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; top: 0; left: 0; z-index: 100; box-shadow: var(--shadow-sm); }
  .sidebar-logo { padding: 28px 24px 20px; border-bottom: 1px solid var(--border); }
  .sidebar-logo h2 { font-size: 20px; color: var(--accent); }
  .sidebar-logo p { font-size: 12px; color: var(--ink-muted); font-weight: 300; margin-top: 2px; }
  .sidebar-nav { flex: 1; padding: 16px 12px; }
  .nav-section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-muted); padding: 8px 12px 4px; }
  .nav-item { display: flex; align-items: center; gap: 10px; padding: 11px 14px; border-radius: var(--radius-sm); cursor: pointer; font-size: 14px; font-weight: 400; color: var(--ink-light); margin-bottom: 2px; transition: all 0.15s ease; border: none; background: none; width: 100%; text-align: left; }
  .nav-item:hover { background: var(--accent-light); color: var(--accent); }
  .nav-item.active { background: var(--accent-light); color: var(--accent); font-weight: 600; }
  .nav-item .nav-icon { font-size: 16px; width: 20px; text-align: center; }
  .sidebar-footer { padding: 16px; border-top: 1px solid var(--border); }
  .user-chip { display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: var(--cream); border-radius: var(--radius-sm); }
  .user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; flex-shrink: 0; overflow: hidden; }
  .user-info { flex: 1; min-width: 0; }
  .user-info .name { font-size: 14px; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .user-info .role { font-size: 12px; color: var(--ink-muted); text-transform: capitalize; }
  .logout-btn { background: none; border: none; cursor: pointer; color: var(--ink-muted); font-size: 18px; padding: 4px; border-radius: 4px; transition: color 0.15s; }
  .logout-btn:hover { color: var(--red); }

  .main-content { margin-left: 260px; flex: 1; min-height: 100vh; background: var(--cream); }
  .page-header { padding: 40px 48px 24px; display: flex; flex-direction: column; gap: 8px; }
  .page-header h1 { font-size: 32px; color: var(--ink); margin: 0; }
  .page-header p { color: var(--ink-muted); margin: 4px 0 0; font-size: 14.5px; }

  .page-body { padding: 28px 48px 64px; }
  .card { background: var(--white); border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
  .card-pad { padding: 28px 32px; }

  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
  .stat-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px 28px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; justify-content: center; min-height: 140px; }
  .stat-card .stat-label { font-size: 12px; color: var(--ink-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card .stat-value { font-size: 36px; font-family: 'DM Serif Display', serif; color: var(--ink); margin: 8px 0 6px; line-height: 1; }
  .stat-card .stat-sub { font-size: 12px; color: var(--ink-muted); }
  .stat-card.accent { background: var(--accent); border-color: var(--accent); }
  .stat-card.accent .stat-label, .stat-card.accent .stat-value, .stat-card.accent .stat-sub { color: white; }

  .btn {
    display: inline-flex; align-items: center; justify-content: center;
    gap: 8px; padding: 10px 20px; border-radius: var(--radius-sm);
    font-size: 14px; font-weight: 500; cursor: pointer; border: none;
    transition: all 0.15s ease; font-family: 'DM Sans', sans-serif;
    min-width: 120px; text-align: center; white-space: nowrap;
  }
  .btn-primary { background: var(--accent); color: white; }
  .btn-primary:hover { background: #2449C0; box-shadow: var(--shadow-md); }
  .btn-secondary { background: var(--white); color: var(--ink); border: 1px solid var(--border); }
  .btn-secondary:hover { background: var(--cream); border-color: var(--accent-soft); }
  .btn-danger { background: var(--red); color: white; }
  .btn-success { background: var(--green); color: white; }
  .btn-lg { padding: 12px 32px; font-size: 15px; min-width: 160px; }
  .btn-sm { padding: 7px 14px; font-size: 13px; min-width: 90px; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .form-group { margin-bottom: 20px; }
  .form-label { display: block; font-size: 13.5px; font-weight: 500; color: var(--ink); margin-bottom: 8px; }
  .form-input, .form-select, .form-textarea {
    width: 100%; padding: 11px 16px; border: 1px solid var(--border);
    border-radius: var(--radius-sm); font-size: 14px; font-family: 'DM Sans', sans-serif;
    color: var(--ink); background: var(--white); transition: border-color 0.18s, box-shadow 0.18s;
    line-height: 1.5;
  }
  .form-input:focus, .form-select:focus, .form-textarea:focus {
    border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-light); outline: none;
  }
  .form-textarea { min-height: 120px; resize: vertical; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 2px solid var(--border); background: #f8f9fc; }
  tbody tr { border-bottom: 1px solid var(--border); transition: background 0.14s; }
  tbody tr:hover { background: var(--accent-light); }
  th { font-size: 12px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.05em; padding: 14px 20px; text-align: left; }
  td { padding: 14px 20px; font-size: 14px; color: var(--ink); }

  .badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
  .badge-green { background: var(--green-light); color: var(--green); }
  .badge-red { background: var(--red-light); color: var(--red); }
  .badge-amber { background: var(--amber-light); color: var(--amber); }
  .badge-blue { background: var(--accent-light); color: var(--accent); }
  .badge-gray { background: #F3F4F6; color: #6B7280; }

  .auth-shell { min-height: 100vh; display: flex; background: var(--cream); }
  .auth-left { width: 420px; background: var(--accent); display: flex; flex-direction: column; justify-content: center; padding: 60px 48px; color: white; }
  .auth-left h1 { font-size: 42px; color: white; line-height: 1.1; }
  .auth-left p { font-size: 15px; opacity: 0.8; margin-top: 16px; line-height: 1.7; }
  .auth-feature { display: flex; align-items: flex-start; gap: 12px; margin-top: 32px; }
  .auth-feature-icon { font-size: 20px; margin-top: 2px; }
  .auth-feature-text { font-size: 14px; opacity: 0.85; }
  .auth-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px; }
  .auth-card { width: 100%; max-width: 440px; background: var(--white); border-radius: var(--radius-lg); padding: 40px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); }
  .auth-card h2 { font-size: 26px; margin-bottom: 6px; }
  .auth-card .subtitle { color: var(--ink-muted); font-size: 14px; margin-bottom: 28px; }
  .auth-switch { text-align: center; margin-top: 20px; font-size: 14px; color: var(--ink-muted); }
  .auth-switch button { background: none; border: none; color: var(--accent); cursor: pointer; font-weight: 600; font-size: 14px; }

  .role-toggle { display: flex; gap: 8px; margin-bottom: 24px; }
  .role-btn { flex: 1; padding: 12px; border-radius: var(--radius-sm); border: 2px solid var(--border); background: var(--white); cursor: pointer; font-size: 14px; font-weight: 500; color: var(--ink-light); transition: all 0.15s; text-align: center; }
  .role-btn.active { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }

  .profile-banner { background: linear-gradient(135deg, var(--accent) 0%, #1A3A9E 100%); border-radius: var(--radius) var(--radius) 0 0; padding: 40px 40px 72px; color: white; position: relative; }
  .profile-institution { font-size: 12px; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
  .profile-name { font-size: 32px; color: white; }
  .profile-email { opacity: 0.8; font-size: 14px; margin-top: 6px; }
  .profile-avatar-lg { width: 90px; height: 90px; border-radius: 50%; background: rgba(255,255,255,0.25); border: 3px solid rgba(255,255,255,0.5); display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: 700; color: white; margin-bottom: 20px; overflow: hidden; }
  .profile-body { margin-top: -48px; padding: 0 40px 40px; }

  .heatmap-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .heatmap-label { font-size: 13px; font-weight: 500; width: 120px; color: var(--ink); }
  .heatmap-bar-track { flex: 1; height: 10px; background: var(--border); border-radius: 99px; overflow: hidden; }
  .heatmap-bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
  .heatmap-pct { font-size: 12px; color: var(--ink-muted); width: 40px; text-align: right; }

  .tabs { display: flex; gap: 4px; border-bottom: 2px solid var(--border); margin-bottom: 24px; }
  .tab-btn { padding: 10px 20px; font-size: 14px; font-weight: 500; background: none; border: none; cursor: pointer; color: var(--ink-muted); border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.15s; }
  .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

  .modal-overlay { position: fixed; inset: 0; background: rgba(26,26,46,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; padding: 20px; }
  .modal { background: var(--white); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); width: 100%; max-width: 620px; max-height: 90vh; overflow-y: auto; }
  .modal-header { padding: 24px 32px 16px; display: flex; align-items: center; justify-content: space-between; }
  .modal-header h3 { font-size: 20px; margin: 0; }
  .modal-close { background: none; border: none; cursor: pointer; font-size: 24px; color: var(--ink-muted); padding: 4px; }
  .modal-body { padding: 0 32px 32px; }

  .alert { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 14px; margin-bottom: 16px; }
  .alert-error { background: var(--red-light); color: var(--red); }
  .alert-success { background: var(--green-light); color: var(--green); }
  .alert-info { background: var(--accent-light); color: var(--accent); }

  .search-bar { position: relative; display: flex; align-items: center; flex: 1; max-width: 360px; }
  .search-bar input { padding-left: 40px !important; }
  .search-icon { position: absolute; left: 14px; font-size: 15px; color: var(--ink-muted); pointer-events: none; }

  .q-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 12px; transition: box-shadow 0.15s, border-color 0.15s; }
  .q-card:hover { box-shadow: var(--shadow-md); border-color: var(--accent-soft); }
  .q-card.selected { border-color: var(--accent); background: var(--accent-light); }
  .q-text { font-size: 14.5px; color: var(--ink); margin-bottom: 8px; font-weight: 500; }
  .q-answer { font-size: 13px; color: var(--ink-muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

  .answer-block { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 20px; }
  .answer-block .q-num { font-size: 11.5px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 8px; }
  .answer-block .q-text { font-size: 15.5px; font-weight: 600; margin-bottom: 14px; }

  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { width: 20px; height: 20px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; }

  .feedback-card { background: linear-gradient(135deg, #EEF2FF 0%, #F8F0FF 100%); border: 1px solid var(--accent-soft); border-radius: var(--radius); padding: 20px 24px; }
  .feedback-card h4 { font-size: 14px; color: var(--accent); margin-bottom: 10px; }
  .feedback-card p { font-size: 14px; color: var(--ink); line-height: 1.7; }

  .empty-state { text-align: center; padding: 64px 24px; color: var(--ink-muted); }
  .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
  .empty-state p { font-size: 15px; }

  .validation-panel { background: var(--cream); border-radius: var(--radius-sm); padding: 16px 20px; margin-top: 16px; border-left: 4px solid var(--accent); }

  .flex { display: flex; }
  .flex-col { flex-direction: column; }
  .items-center { align-items: center; }
  .items-start { align-items: flex-start; }
  .justify-between { justify-content: space-between; }
  .justify-end { justify-content: flex-end; }
  .gap-2 { gap: 8px; }
  .gap-3 { gap: 12px; }
  .gap-4 { gap: 16px; }
  .gap-6 { gap: 24px; }
  .mt-1 { margin-top: 4px; }
  .mt-2 { margin-top: 8px; }
  .mt-3 { margin-top: 12px; }
  .mt-4 { margin-top: 16px; }
  .mt-6 { margin-top: 24px; }
  .mb-2 { margin-bottom: 8px; }
  .mb-4 { margin-bottom: 16px; }
  .mb-6 { margin-bottom: 24px; }
  .w-full { width: 100%; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
  .text-sm { font-size: 13px; }
  .text-xs { font-size: 12px; }
  .text-muted { color: var(--ink-muted); }
  .font-600 { font-weight: 600; }
  .section-title { font-size: 18px; margin-bottom: 16px; }
  .divider { height: 1px; background: var(--border); margin: 24px 0; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--cream); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
`;
document.head.appendChild(style);

// ─────────────────────────────────────────────
// API
// ─────────────────────────────────────────────
const BASE = "http://localhost:8000";

const api = {
  async req(method, path, body, token) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Request failed");
    }
    return res.json();
  },
  get:    (path, token)        => api.req("GET",    path, null, token),
  post:   (path, body, token)  => api.req("POST",   path, body, token),
  put:    (path, body, token)  => api.req("PUT",    path, body, token),
  delete: (path, token)        => api.req("DELETE", path, null, token),
};

// ─────────────────────────────────────────────
// AUTH CONTEXT
// FIX: decode name/institution/email from token
// ─────────────────────────────────────────────
const AuthContext = createContext(null);
function useAuth() { return useContext(AuthContext); }

function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
  });
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);

  const login = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);
    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("token", accessToken);
  };

  const logout = () => {
    setUser(null); setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─────────────────────────────────────────────
// ROUTER
// ─────────────────────────────────────────────
function Router() {
  const { user } = useAuth();
  const [page, setPage] = useState("dashboard");
  if (!user) return <AuthPage />;
  if (user.role === "teacher") return <TeacherShell page={page} setPage={setPage} />;
  return <StudentShell page={page} setPage={setPage} />;
}

// ─────────────────────────────────────────────
// AUTH PAGE
// ─────────────────────────────────────────────
function AuthPage() {
  const [mode, setMode] = useState("login");
  return (
    <div className="auth-shell">
      <div className="auth-left">
        <h1>EvalAI<br />Platform</h1>
        <p>AI-powered exam evaluation with intelligent feedback, heatmaps, and deep analytics.</p>
        {[
          { icon: "🧠", text: "Hybrid NLI + semantic scoring engine" },
          { icon: "📊", text: "Real-time analytics & visualizations" },
          { icon: "✨", text: "Gemini-powered feedback reports" },
        ].map((f, i) => (
          <div className="auth-feature" key={i}>
            <span className="auth-feature-icon">{f.icon}</span>
            <span className="auth-feature-text">{f.text}</span>
          </div>
        ))}
      </div>
      <div className="auth-right">
        {mode === "login"
          ? <LoginForm onSwitch={() => setMode("register")} />
          : <RegisterForm onSwitch={() => setMode("login")} />}
      </div>
    </div>
  );
}

function LoginForm({ onSwitch }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true); setError("");
    try {
      const res = await api.post("/login", form);
      // FIX: token now contains name, institution, email — no undefined user.name
      const payload = JSON.parse(atob(res.access_token.split(".")[1]));
      login({
        id:          payload.user_id,
        role:        payload.role,
        name:        payload.name || form.email,
        email:       payload.email || form.email,
        institution: payload.institution || "",
      }, res.access_token);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div className="auth-card">
      <h2>Welcome back</h2>
      <p className="subtitle">Sign in to your account</p>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="form-group">
        <label className="form-label">Email</label>
        <input className="form-input" type="email" placeholder="you@university.edu"
          value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
          onKeyDown={e => e.key === "Enter" && handleSubmit()} />
      </div>
      <div className="form-group">
        <label className="form-label">Password</label>
        <input className="form-input" type="password" placeholder="••••••••"
          value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
          onKeyDown={e => e.key === "Enter" && handleSubmit()} />
      </div>
      <button className="btn btn-primary w-full btn-lg" onClick={handleSubmit} disabled={loading}>
        {loading ? <span className="spinner" /> : "Sign In"}
      </button>
      <div className="auth-switch">
        Don't have an account? <button onClick={onSwitch}>Register</button>
      </div>
    </div>
  );
}

function RegisterForm({ onSwitch }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "student", institution: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!form.name || !form.email || !form.password) { setError("Please fill all required fields"); return; }
    setLoading(true); setError("");
    try {
      await api.post("/register", form);
      const res = await api.post("/login", { email: form.email, password: form.password });
      const payload = JSON.parse(atob(res.access_token.split(".")[1]));
      login({
        id:          payload.user_id,
        role:        payload.role,
        name:        payload.name || form.name,
        email:       payload.email || form.email,
        institution: payload.institution || form.institution,
      }, res.access_token);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div className="auth-card">
      <h2>Create account</h2>
      <p className="subtitle">Join the platform</p>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="role-toggle">
        {["student", "teacher"].map(r => (
          <button key={r} className={`role-btn ${form.role === r ? "active" : ""}`}
            onClick={() => setForm({ ...form, role: r })}>
            {r === "student" ? "🎓 Student" : "👨‍🏫 Teacher"}
          </button>
        ))}
      </div>
      {[
        { key: "name", label: "Full Name", type: "text", placeholder: "Dr. Jane Smith" },
        { key: "email", label: "Email", type: "email", placeholder: "you@university.edu" },
        { key: "password", label: "Password", type: "password", placeholder: "••••••••" },
        { key: "institution", label: "Institution (optional)", type: "text", placeholder: "University of..." },
      ].map(f => (
        <div className="form-group" key={f.key}>
          <label className="form-label">{f.label}</label>
          <input className="form-input" type={f.type} placeholder={f.placeholder}
            value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
        </div>
      ))}
      <button className="btn btn-primary w-full btn-lg" onClick={handleSubmit} disabled={loading}>
        {loading ? <span className="spinner" /> : "Create Account"}
      </button>
      <div className="auth-switch">
        Already have an account? <button onClick={onSwitch}>Sign in</button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// SIDEBAR
// ─────────────────────────────────────────────
function Sidebar({ navItems, page, setPage }) {
  const { user, logout } = useAuth();
  const initials = (user?.name || user?.email || "U").slice(0, 2).toUpperCase();

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <h2>EvalAI</h2>
        <p>Academic Evaluation Platform</p>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((section, si) => (
          <div key={si}>
            {section.label && <div className="nav-section-label">{section.label}</div>}
            {section.items.map(item => (
              <button key={item.id} className={`nav-item ${page === item.id ? "active" : ""}`}
                onClick={() => setPage(item.id)}>
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="user-chip">
          <div className="user-avatar">{initials}</div>
          <div className="user-info">
            <div className="name">{user?.name || user?.email}</div>
            <div className="role">{user?.role}</div>
          </div>
          <button className="logout-btn" onClick={logout} title="Logout">⏻</button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// TEACHER SHELL
// ─────────────────────────────────────────────
function TeacherShell({ page, setPage }) {
  const [selectedTest, setSelectedTest] = useState(null);

  const nav = [
    { items: [
      { id: "dashboard", icon: "⬡", label: "Dashboard" },
      { id: "profile",   icon: "👤", label: "My Profile" },
    ]},
    { label: "Content", items: [
      { id: "questions", icon: "❓", label: "Question Bank" },
      { id: "tests",     icon: "📋", label: "Tests" },
    ]},
    { label: "Insights", items: [
      { id: "analytics",    icon: "📊", label: "Analytics" },
      { id: "submissions",  icon: "📝", label: "Student Submissions" },
    ]},
  ];

  const pages = {
    dashboard:   <TeacherDashboard setPage={setPage} />,
    profile:     <TeacherProfile />,
    questions:   <QuestionBank />,
    tests:       <TestManagement setPage={setPage} setSelectedTest={setSelectedTest} />,
    analytics:   <AnalyticsDashboard />,
    submissions: <TeacherSubmissions selectedTest={selectedTest} />,
  };

  return (
    <div className="app-shell">
      <Sidebar navItems={nav} page={page} setPage={setPage} />
      <main className="main-content">{pages[page] || pages.dashboard}</main>
    </div>
  );
}

// ─────────────────────────────────────────────
// STUDENT SHELL
// ─────────────────────────────────────────────
function StudentShell({ page, setPage }) {
  const nav = [
    { items: [
      { id: "dashboard", icon: "⬡", label: "Dashboard" },
      { id: "tests",     icon: "📝", label: "Available Tests" },
      { id: "profile",   icon: "👤", label: "My Profile" },
    ]},
    { label: "My Results", items: [
      { id: "results", icon: "📈", label: "My Submissions" },
    ]},
  ];

  const [selectedTest, setSelectedTest] = useState(null);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  const pages = {
    dashboard:         <StudentDashboard setPage={setPage} setSelectedTest={setSelectedTest} />,
    tests:             <AvailableTests setPage={setPage} setSelectedTest={setSelectedTest} />,
    take_test:         <TakeTest test={selectedTest} setPage={setPage} setSelectedSubmission={setSelectedSubmission} />,
    results:           <MySubmissions setPage={setPage} setSelectedSubmission={setSelectedSubmission} />,
    submission_detail: <SubmissionDetail submission={selectedSubmission} setPage={setPage} />,
    profile:           <StudentProfile />,
  };

  return (
    <div className="app-shell">
      <Sidebar navItems={nav} page={page} setPage={setPage} />
      <main className="main-content">{pages[page] || pages.dashboard}</main>
    </div>
  );
}

// ─────────────────────────────────────────────
// TEACHER DASHBOARD
// ─────────────────────────────────────────────
function TeacherDashboard({ setPage }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [questions, setQuestions] = useState({ total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/tests", token),
      api.get("/questions", token),
    ]).then(([t, q]) => {
      setTests(t);
      // FIX: questions endpoint now returns { total, items }
      setQuestions(q);
      setLoading(false);
    }).catch(() => setLoading(false));
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

  const totalSubs = tests.reduce((a, t) => a + (t.submission_count || 0), 0);
  const pendingEval = tests.reduce((a, t) => a + ((t.submission_count || 0) - (t.evaluated_count || 0)), 0);

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your evaluation activity</p>
      </div>
      <div className="page-body">
        <div className="stat-grid mb-6">
          {[
            { label: "Total Tests",    value: tests.length,        sub: "created by you",       accent: true },
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
              <thead>
                <tr><th>Title</th><th>Questions</th><th>Submissions</th><th>Evaluated</th><th>Status</th></tr>
              </thead>
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
    </>
  );
}

// ─────────────────────────────────────────────
// TEACHER PROFILE
// ─────────────────────────────────────────────
function TeacherProfile() {
  const { user, token, login } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    name: user?.name || "",
    institution: user?.institution || "",
    email: user?.email || "",
  });
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try {
      await api.put("/users/me", form, token);
      login({ ...user, ...form }, token);
      setSaved(true); setEditing(false);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      login({ ...user, ...form }, token);
      setSaved(true); setEditing(false);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  const initials = (form.name || "T").slice(0, 2).toUpperCase();

  return (
    <>
      <div className="page-header"><h1>My Profile</h1><p>Faculty information & account settings</p></div>
      <div className="page-body">
        {saved && <div className="alert alert-success">Profile updated successfully!</div>}
        <div className="card mb-6" style={{ overflow: "hidden" }}>
          <div className="profile-banner">
            <div className="profile-avatar-lg">{initials}</div>
            <div className="profile-institution">{form.institution || "Institution not set"}</div>
            <div className="profile-name">{form.name || "Faculty Member"}</div>
            <div className="profile-email">{form.email}</div>
          </div>
          <div className="profile-body">
            <div className="card card-pad" style={{ marginTop: 0 }}>
              <div className="flex items-center justify-between mb-4">
                <h3 style={{ fontSize: 18 }}>Personal Information</h3>
                {!editing && <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}>✏️ Edit Profile</button>}
              </div>
              {editing ? (
                <>
                  {[
                    { key: "name", label: "Full Name" },
                    { key: "institution", label: "Institution" },
                    { key: "email", label: "Email", type: "email" },
                  ].map(f => (
                    <div className="form-group" key={f.key}>
                      <label className="form-label">{f.label}</label>
                      <input className="form-input" type={f.type || "text"}
                        value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                    </div>
                  ))}
                  <div className="flex gap-3 justify-end">
                    <button className="btn btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave}>Save Changes</button>
                  </div>
                </>
              ) : (
                <div className="grid-2">
                  {[
                    { label: "Full Name", value: form.name },
                    { label: "Email", value: form.email },
                    { label: "Institution", value: form.institution || "—" },
                    { label: "Role", value: "Teacher" },
                  ].map((f, i) => (
                    <div key={i}>
                      <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 4 }}>{f.label}</div>
                      <div className="text-sm font-600">{f.value}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// STUDENT PROFILE (was missing entirely)
// ─────────────────────────────────────────────
function StudentProfile() {
  const { user, token, login } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    name: user?.name || "",
    institution: user?.institution || "",
    email: user?.email || "",
  });
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try {
      await api.put("/users/me", form, token);
      login({ ...user, ...form }, token);
      setSaved(true); setEditing(false);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      login({ ...user, ...form }, token);
      setSaved(true); setEditing(false);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  const initials = (form.name || "S").slice(0, 2).toUpperCase();

  return (
    <>
      <div className="page-header"><h1>My Profile</h1><p>Your student account & settings</p></div>
      <div className="page-body">
        {saved && <div className="alert alert-success">Profile updated!</div>}
        <div className="card mb-6" style={{ overflow: "hidden" }}>
          <div className="profile-banner">
            <div className="profile-avatar-lg">{initials}</div>
            <div className="profile-institution">{form.institution || "Institution not set"}</div>
            <div className="profile-name">{form.name || "Student"}</div>
            <div className="profile-email">{form.email}</div>
          </div>
          <div className="profile-body">
            <div className="card card-pad" style={{ marginTop: 0 }}>
              <div className="flex items-center justify-between mb-4">
                <h3 style={{ fontSize: 18 }}>Personal Information</h3>
                {!editing && <button className="btn btn-secondary btn-sm" onClick={() => setEditing(true)}>✏️ Edit Profile</button>}
              </div>
              {editing ? (
                <>
                  {[
                    { key: "name", label: "Full Name" },
                    { key: "institution", label: "Institution" },
                  ].map(f => (
                    <div className="form-group" key={f.key}>
                      <label className="form-label">{f.label}</label>
                      <input className="form-input" type="text"
                        value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                    </div>
                  ))}
                  <div className="flex gap-3 justify-end">
                    <button className="btn btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave}>Save Changes</button>
                  </div>
                </>
              ) : (
                <div className="grid-2">
                  {[
                    { label: "Full Name",    value: form.name },
                    { label: "Email",        value: form.email },
                    { label: "Institution",  value: form.institution || "—" },
                    { label: "Role",         value: "Student" },
                  ].map((f, i) => (
                    <div key={i}>
                      <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 4 }}>{f.label}</div>
                      <div className="text-sm font-600">{f.value}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// QUESTION BANK
// FIX: reads items from paginated response
// ─────────────────────────────────────────────
function QuestionBank() {
  const { token } = useAuth();
  const [data, setData] = useState({ total: 0, items: [] });
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchQuestions = async (q = "") => {
    setLoading(true);
    const res = await api.get(`/questions?search=${encodeURIComponent(q)}`, token).catch(() => ({ total: 0, items: [] }));
    setData(res);
    setLoading(false);
  };

  useEffect(() => { fetchQuestions(); }, []);
  useEffect(() => {
    const t = setTimeout(() => fetchQuestions(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  return (
    <>
      <div className="page-header">
        <h1>Question Bank</h1>
        <p>{data.total} questions in your bank</p>
      </div>
      <div className="page-body">
        <div className="flex items-center justify-between mb-4">
          <div className="search-bar" style={{ width: 320 }}>
            <span className="search-icon">🔍</span>
            <input className="form-input" placeholder="Search questions..."
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Question</button>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
        ) : data.items.length === 0 ? (
          <div className="empty-state"><div className="icon">❓</div><p>No questions found. Add your first question!</p></div>
        ) : (
          data.items.map(q => (
            <div className="q-card" key={q.id}>
              <div className="flex justify-between items-start">
                <div style={{ flex: 1 }}>
                  <div className="q-text">{q.text}</div>
                  <div className="q-answer">{q.model_answer}</div>
                </div>
                <span className="badge badge-blue" style={{ marginLeft: 12, flexShrink: 0 }}>Q#{q.id}</span>
              </div>
            </div>
          ))
        )}
      </div>
      {showCreate && <CreateQuestionModal onClose={() => { setShowCreate(false); fetchQuestions(search); }} />}
    </>
  );
}

function CreateQuestionModal({ onClose }) {
  const { token } = useAuth();
  const [form, setForm] = useState({ text: "", model_answer: "" });
  const [validation, setValidation] = useState(null);
  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const validate = async () => {
    if (!form.text || !form.model_answer) { setError("Fill both fields first"); return; }
    setValidating(true); setError("");
    try {
      const res = await api.post("/questions/validate", form, token);
      setValidation(res);
    } catch (e) { setError(e.message); }
    setValidating(false);
  };

  const save = async () => {
    if (!form.text || !form.model_answer) { setError("Fill both fields"); return; }
    setSaving(true);
    try {
      await api.post("/questions", form, token);
      onClose();
    } catch (e) { setError(e.message); }
    setSaving(false);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3>Add New Question</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Question Text</label>
            <textarea className="form-textarea" placeholder="Enter your question..."
              value={form.text} onChange={e => setForm({ ...form, text: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Reference Answer</label>
            <textarea className="form-textarea" placeholder="Enter the model/reference answer..."
              value={form.model_answer} onChange={e => setForm({ ...form, model_answer: e.target.value })} />
          </div>
          <div className="flex gap-3 mb-4">
            <button className="btn btn-secondary" onClick={validate} disabled={validating}>
              {validating ? <><span className="spinner" /> Validating...</> : "✨ Validate with AI"}
            </button>
          </div>
          {validation && (
            <div className="validation-panel mb-4">
              <div className="text-sm font-600 mb-2">AI Validation Result</div>
              <div className="flex gap-3 mb-2">
                <span className={`badge ${validation.analysis?.grammar_ok ? "badge-green" : "badge-red"}`}>
                  {validation.analysis?.grammar_ok ? "✓ Grammar OK" : "✗ Grammar Issues"}
                </span>
                <span className={`badge ${validation.analysis?.answers_question ? "badge-green" : "badge-amber"}`}>
                  {validation.analysis?.answers_question ? "✓ Answers Question" : "⚠ Unclear"}
                </span>
              </div>
              {validation.analysis?.comments && (
                <div className="text-sm text-muted">{validation.analysis.comments}</div>
              )}
              {validation.analysis?.corrected_answer && validation.analysis.corrected_answer !== form.model_answer && (
                <div className="mt-2">
                  <div className="text-xs font-600 text-muted mb-1">Suggested correction:</div>
                  <div className="text-sm">{validation.analysis.corrected_answer}</div>
                  <button className="btn btn-secondary btn-sm mt-2"
                    onClick={() => setForm({ ...form, model_answer: validation.analysis.corrected_answer })}>
                    Use suggested answer
                  </button>
                </div>
              )}
            </div>
          )}
          <div className="flex gap-3 justify-end">
            <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button className="btn btn-primary" onClick={save} disabled={saving}>
              {saving ? <span className="spinner" /> : "Save Question"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// TEST MANAGEMENT
// FIX: shows question_count and submission_count from API
// ─────────────────────────────────────────────
function TestManagement({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTestModal, setSelectedTestModal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(null);
  const [evalMsg, setEvalMsg] = useState("");

  const fetchTests = async () => {
    setLoading(true);
    const data = await api.get("/tests", token).catch(() => []);
    setTests(data);
    setLoading(false);
  };

  useEffect(() => { fetchTests(); }, []);

  const evaluate = async (testId) => {
    setEvaluating(testId);
    try {
      const res = await api.post(`/submissions/evaluate/${testId}`, {}, token);
      setEvalMsg(`✅ ${res.evaluated_count} submissions evaluated`);
      fetchTests();
      setTimeout(() => setEvalMsg(""), 4000);
    } catch (e) { setEvalMsg("❌ " + e.message); }
    setEvaluating(null);
  };

  return (
    <>
      <div className="page-header"><h1>Tests</h1><p>Create and manage your tests</p></div>
      <div className="page-body">
        {evalMsg && <div className={`alert ${evalMsg.startsWith("✅") ? "alert-success" : "alert-error"}`}>{evalMsg}</div>}
        <div className="flex justify-end mb-4">
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Test</button>
        </div>
        {loading ? (
          <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
        ) : tests.length === 0 ? (
          <div className="empty-state"><div className="icon">📋</div><p>No tests yet. Create your first test!</p></div>
        ) : (
          <div className="card table-wrap">
            <table>
              <thead>
                <tr><th>Title</th><th>Questions</th><th>Submissions</th><th>Evaluated</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {tests.map(t => (
                  <tr key={t.id}>
                    <td className="font-600">{t.title}</td>
                    <td>{t.question_count ?? "—"}</td>
                    <td>{t.submission_count ?? "—"}</td>
                    <td>{t.evaluated_count ?? "—"}</td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn btn-secondary btn-sm" onClick={() => setSelectedTestModal(t)}>
                          Manage Questions
                        </button>
                        <button className="btn btn-success btn-sm"
                          onClick={() => evaluate(t.id)} disabled={evaluating === t.id}>
                          {evaluating === t.id ? <span className="spinner" /> : "⚡ Evaluate"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showCreate && <CreateTestModal onClose={() => { setShowCreate(false); fetchTests(); }} />}
      {selectedTestModal && <TestQuestionsModal test={selectedTestModal} onClose={() => { setSelectedTestModal(null); fetchTests(); }} />}
    </>
  );
}

function CreateTestModal({ onClose }) {
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    if (!title) { setError("Enter a title"); return; }
    setSaving(true);
    try {
      await api.post("/tests", { title }, token);
      onClose();
    } catch (e) { setError(e.message); }
    setSaving(false);
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3>Create New Test</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label">Test Title</label>
            <input className="form-input" placeholder="e.g. Unit 3 - Data Structures"
              value={title} onChange={e => setTitle(e.target.value)}
              onKeyDown={e => e.key === "Enter" && save()} />
          </div>
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
  const [tab, setTab] = useState("existing");
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    // FIX: use Promise.allSettled so one failure doesn't kill both
    const [detailRes, qsRes] = await Promise.allSettled([
      api.get(`/tests/${test.id}`, token),
      api.get(`/questions?search=${encodeURIComponent(search)}`, token),
    ]);
    const detail = detailRes.status === "fulfilled" ? detailRes.value : { questions: [] };
    const qs     = qsRes.status     === "fulfilled" ? qsRes.value     : { total: 0, items: [] };
    setTestDetail(detail);
    setAllQuestions(qs.items || []);
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);
  useEffect(() => {
    const t = setTimeout(() => fetchData(), 400);
    return () => clearTimeout(t);
  }, [search]);

  const addQ = async (qId) => {
    await api.post(`/tests/${test.id}/questions`, { question_id: qId, max_score: maxScore }, token);
    fetchData();
  };

  const removeQ = async (qId) => {
    await api.delete(`/tests/${test.id}/questions/${qId}`, token);
    fetchData();
  };

  const inTest = new Set(testDetail?.questions?.map(q => q.id) || []);

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 680 }}>
        <div className="modal-header">
          <h3>{test.title} — Questions</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="tabs">
            <button className={`tab-btn ${tab === "existing" ? "active" : ""}`} onClick={() => setTab("existing")}>
              Add from Bank
            </button>
            <button className={`tab-btn ${tab === "current" ? "active" : ""}`} onClick={() => setTab("current")}>
              Current Questions ({testDetail?.questions?.length || 0})
            </button>
          </div>

          {tab === "existing" && (
            <>
              <div className="flex gap-3 mb-4">
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
              </div>
              {loading ? <div className="spinner" style={{ margin: "20px auto" }} /> : (
                allQuestions.map(q => (
                  <div className={`q-card ${inTest.has(q.id) ? "selected" : ""}`} key={q.id}>
                    <div className="flex justify-between items-start">
                      <div style={{ flex: 1 }}>
                        <div className="q-text">{q.text}</div>
                        <div className="q-answer">{q.model_answer}</div>
                      </div>
                      <div style={{ marginLeft: 12 }}>
                        {inTest.has(q.id) ? (
                          <button className="btn btn-danger btn-sm" onClick={() => removeQ(q.id)}>Remove</button>
                        ) : (
                          <button className="btn btn-primary btn-sm" onClick={() => addQ(q.id)}>Add</button>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </>
          )}

          {tab === "current" && (
            testDetail?.questions?.length === 0 ? (
              <div className="empty-state" style={{ padding: "30px 0" }}><p>No questions in this test yet.</p></div>
            ) : (
              testDetail?.questions?.map(q => (
                <div className="q-card" key={q.id}>
                  <div className="flex justify-between items-start">
                    <div style={{ flex: 1 }}>
                      <div className="q-text">{q.text}</div>
                      <span className="badge badge-amber">Max: {q.max_score} pts</span>
                    </div>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: 12 }} onClick={() => removeQ(q.id)}>Remove</button>
                  </div>
                </div>
              ))
            )
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// TEACHER: STUDENT SUBMISSIONS VIEW (new page)
// ─────────────────────────────────────────────
function TeacherSubmissions({ selectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [testId, setTestId] = useState(selectedTest?.id || "");
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSub, setSelectedSub] = useState(null);

  useEffect(() => {
    api.get("/tests", token).then(setTests).catch(() => {});
  }, []);

  const loadSubs = async (id) => {
    setTestId(id);
    if (!id) { setSubmissions([]); return; }
    setLoading(true);
    const data = await api.get(`/submissions/test/${id}`, token).catch(() => []);
    setSubmissions(data);
    setLoading(false);
  };

  if (selectedSub) {
    return <SubmissionDetail submission={selectedSub} setPage={() => setSelectedSub(null)} backLabel="← Back to Submissions" />;
  }

  return (
    <>
      <div className="page-header"><h1>Student Submissions</h1><p>Review individual student answers and scores</p></div>
      <div className="page-body">
        <div className="form-group" style={{ maxWidth: 320 }}>
          <label className="form-label">Select Test</label>
          <select className="form-select" value={testId} onChange={e => loadSubs(e.target.value)}>
            <option value="">— Choose a test —</option>
            {tests.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>
        </div>

        {loading && <div className="spinner" style={{ margin: "40px auto", display: "block" }} />}

        {!loading && submissions.length > 0 && (
          <div className="card table-wrap">
            <table>
              <thead>
                <tr><th>Student</th><th>Email</th><th>Score</th><th>Status</th><th>Submitted</th><th>Action</th></tr>
              </thead>
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
                      {s.status === "evaluated" && (
                        <button className="btn btn-primary btn-sm" onClick={() => setSelectedSub(s)}>View</button>
                      )}
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

        {!testId && (
          <div className="empty-state"><div className="icon">📝</div><p>Select a test to view submissions</p></div>
        )}
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// ANALYTICS DASHBOARD
// ─────────────────────────────────────────────
function AnalyticsDashboard() {
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
    setAnalytics(data);
    setLoading(false);
  };

  const rankingData = analytics?.ranking?.slice(0, 8).map((r, i) => ({
    name: `S${r.student_id}`, score: r.score, rank: i + 1
  })) || [];

  const qData = analytics?.question_analysis
    ? Object.entries(analytics.question_analysis).map(([qid, v]) => ({
      name: `Q${qid}`,
      avg: v.average_score,
      difficulty: Math.round(v.difficulty_index * 100),
    }))
    : [];

  const diffPie = analytics ? [
    { name: "Easy (≤30%)",  value: qData.filter(q => q.difficulty <= 30).length, color: "#16A34A" },
    { name: "Medium",       value: qData.filter(q => q.difficulty > 30 && q.difficulty <= 60).length, color: "#D97706" },
    { name: "Hard (>60%)",  value: qData.filter(q => q.difficulty > 60).length, color: "#DC2626" },
  ] : [];

  return (
    <>
      <div className="page-header"><h1>Analytics</h1><p>Deep insights into test and student performance</p></div>
      <div className="page-body">
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
                { label: "Average Score", value: analytics.average_score, accent: true },
                { label: "Highest Score", value: analytics.highest_score },
                { label: "Lowest Score",  value: analytics.lowest_score },
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
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
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
                    </Pie>
                    <Tooltip />
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
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="avg" name="Avg Score" fill="#2D5BE3" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="difficulty" name="Difficulty %" fill="#F87171" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            <div className="card">
              <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
                <h3 style={{ fontSize: 18 }}>Student Ranking</h3>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Rank</th><th>Student ID</th><th>Score</th><th>Performance</th></tr>
                  </thead>
                  <tbody>
                    {analytics.ranking?.map((r, i) => (
                      <tr key={i}>
                        <td><span className="badge badge-blue">#{i + 1}</span></td>
                        <td className="font-600">Student {r.student_id}</td>
                        <td>{r.score}</td>
                        <td>
                          <span className={`badge ${i === 0 ? "badge-green" : i < 3 ? "badge-blue" : "badge-gray"}`}>
                            {i === 0 ? "🥇 Top" : i < 3 ? "Above Avg" : "Avg"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {!analytics && !loading && selectedTestId && (
          <div className="empty-state"><div className="icon">📊</div><p>No evaluated submissions yet for this test.</p></div>
        )}
        {!selectedTestId && (
          <div className="empty-state"><div className="icon">📊</div><p>Select a test above to view analytics</p></div>
        )}
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// STUDENT DASHBOARD
// ─────────────────────────────────────────────
function StudentDashboard({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [tests, setTests] = useState([]);

  useEffect(() => {
    Promise.all([
      api.get("/submissions/student", token),
      api.get("/tests/student", token),
    ]).then(([s, t]) => { setSubmissions(s); setTests(t); }).catch(() => {});
  }, []);

  const evaluated = submissions.filter(s => s.status === "evaluated");
  const avgScore = evaluated.length
    ? Math.round(evaluated.reduce((a, s) => a + s.total_score, 0) / evaluated.length)
    : 0;

  const scoreData = evaluated.slice(-6).map((s, i) => ({
    name: `Test ${i + 1}`, score: s.total_score,
  }));

  return (
    <>
      <div className="page-header"><h1>My Dashboard</h1><p>Track your progress and performance</p></div>
      <div className="page-body">
        <div className="stat-grid mb-6">
          {[
            { label: "Tests Taken",      value: submissions.length, accent: true },
            { label: "Evaluated",        value: evaluated.length },
            { label: "Avg Score",        value: avgScore },
            { label: "Available Tests",  value: tests.length },
          ].map((s, i) => (
            <div className={`stat-card ${i === 0 ? "accent" : ""}`} key={i}>
              <div className="stat-label">{s.label}</div>
              <div className="stat-value">{s.value}</div>
            </div>
          ))}
        </div>

        {scoreData.length > 0 && (
          <div className="card card-pad mb-6">
            <h3 className="section-title">My Score History</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="card">
          <div className="card-pad" style={{ borderBottom: "1px solid var(--border)" }}>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: 18 }}>Available Tests</h3>
              <button className="btn btn-primary btn-sm" onClick={() => setPage("tests")}>View All</button>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Test</th><th>Status</th><th>Action</th></tr></thead>
              <tbody>
                {tests.slice(0, 5).map(t => {
                  const done = submissions.find(s => s.test_id === t.id);
                  return (
                    <tr key={t.id}>
                      <td className="font-600">{t.title}</td>
                      <td>
                        <span className={`badge ${done ? (done.status === "evaluated" ? "badge-green" : "badge-amber") : "badge-blue"}`}>
                          {done ? (done.status === "evaluated" ? "Evaluated" : "Pending") : "Available"}
                        </span>
                      </td>
                      <td>
                        {!done && (
                          <button className="btn btn-primary btn-sm"
                            onClick={() => { setSelectedTest(t); setPage("take_test"); }}>
                            Start Test
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {tests.length === 0 && (
                  <tr><td colSpan={3} style={{ textAlign: "center", color: "var(--ink-muted)", padding: 24 }}>No tests available</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// AVAILABLE TESTS
// ─────────────────────────────────────────────
function AvailableTests({ setPage, setSelectedTest }) {
  const { token } = useAuth();
  const [tests, setTests] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/tests/student", token),
      api.get("/submissions/student", token),
    ]).then(([t, s]) => { setTests(t); setSubmissions(s); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;

  return (
    <>
      <div className="page-header"><h1>Available Tests</h1><p>Browse and take your assigned tests</p></div>
      <div className="page-body">
        {tests.length === 0 ? (
          <div className="empty-state"><div className="icon">📝</div><p>No tests available yet.</p></div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
            {tests.map(t => {
              const done = submissions.find(s => s.test_id === t.id);
              return (
                <div className="card card-pad" key={t.id}>
                  <div className="flex items-start justify-between mb-3">
                    <div style={{ fontSize: 32 }}>📝</div>
                    <span className={`badge ${done ? (done.status === "evaluated" ? "badge-green" : "badge-amber") : "badge-blue"}`}>
                      {done ? (done.status === "evaluated" ? "Evaluated" : "Submitted") : "Available"}
                    </span>
                  </div>
                  <div className="font-600" style={{ fontSize: 16, marginBottom: 4 }}>{t.title}</div>
                  <div className="text-sm text-muted mb-4">Test #{t.id}</div>
                  {!done ? (
                    <button className="btn btn-primary w-full"
                      onClick={() => { setSelectedTest(t); setPage("take_test"); }}>
                      Start Test →
                    </button>
                  ) : (
                    <div className="text-sm text-muted" style={{ textAlign: "center", padding: "8px 0" }}>
                      {done.status === "evaluated" ? `Score: ${done.total_score}` : "Awaiting evaluation"}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// TAKE TEST
// ─────────────────────────────────────────────
function TakeTest({ test, setPage, setSelectedSubmission }) {
  const { token } = useAuth();
  const [testDetail, setTestDetail] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!test) { setPage("tests"); return; }
    api.get(`/tests/${test.id}`, token)
      .then(d => { setTestDetail(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [test]);

  const submit = async () => {
    const unanswered = testDetail?.questions?.filter(q => !answers[q.id]?.trim());
    if (unanswered?.length > 0) { setError(`Please answer all ${unanswered.length} remaining question(s)`); return; }
    setSubmitting(true); setError("");
    try {
      const payload = {
        test_id: test.id,
        answers: Object.entries(answers).map(([qid, ans]) => ({
          question_id: parseInt(qid),
          student_answer: ans,
        })),
      };
      const res = await api.post("/submissions/submit-test", payload, token);
      setSelectedSubmission({ submission_id: res.submission_id, id: res.submission_id });
      setPage("submission_detail");
    } catch (e) { setError(e.message); }
    setSubmitting(false);
  };

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;
  if (!testDetail) return <div style={{ padding: 40 }}>Test not found.</div>;

  const answered = Object.values(answers).filter(a => a?.trim()).length;
  const total = testDetail.questions?.length || 0;

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>{testDetail.title}</h1>
            <p>{answered}/{total} questions answered</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setPage("tests")}>← Back</button>
        </div>
      </div>
      <div className="page-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="mb-4">
          <div style={{ height: 6, background: "var(--border)", borderRadius: 99 }}>
            <div style={{
              height: "100%", borderRadius: 99, background: "var(--accent)",
              width: `${total ? (answered / total) * 100 : 0}%`,
              transition: "width 0.3s ease",
            }} />
          </div>
        </div>

        {testDetail.questions?.map((q, i) => (
          <div className="answer-block" key={q.id}>
            <div className="q-num">Question {i + 1} of {total} · Max {q.max_score} pts</div>
            <div className="q-text">{q.text}</div>
            <textarea className="form-textarea" placeholder="Write your answer here..."
              value={answers[q.id] || ""}
              onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })}
              style={{ minHeight: 120 }}
            />
          </div>
        ))}

        <div className="flex justify-end gap-3 mt-4">
          <button className="btn btn-secondary" onClick={() => setPage("tests")}>Cancel</button>
          <button className="btn btn-primary btn-lg" onClick={submit} disabled={submitting}>
            {submitting ? <><span className="spinner" /> Submitting...</> : "Submit Test →"}
          </button>
        </div>
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// MY SUBMISSIONS
// ─────────────────────────────────────────────
function MySubmissions({ setPage, setSelectedSubmission }) {
  const { token } = useAuth();
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
      <div className="page-header"><h1>My Submissions</h1><p>View your test results and feedback</p></div>
      <div className="page-body">
        {submissions.length === 0 ? (
          <div className="empty-state"><div className="icon">📈</div><p>No submissions yet. Take a test first!</p></div>
        ) : (
          <div className="card table-wrap">
            <table>
              <thead>
                <tr><th>Test</th><th>Score</th><th>Status</th><th>Submitted</th><th>Action</th></tr>
              </thead>
              <tbody>
                {submissions.map(s => (
                  <tr key={s.submission_id}>
                    <td className="font-600">Test #{s.test_id}</td>
                    <td>{s.status === "evaluated" ? <strong>{s.total_score}</strong> : "—"}</td>
                    <td>
                      <span className={`badge ${s.status === "evaluated" ? "badge-green" : "badge-amber"}`}>
                        {s.status === "evaluated" ? "✓ Evaluated" : "⏳ Pending"}
                      </span>
                    </td>
                    <td className="text-sm text-muted">{s.submitted_at ? new Date(s.submitted_at).toLocaleDateString() : "—"}</td>
                    <td>
                      {s.status === "evaluated" && (
                        <button className="btn btn-primary btn-sm"
                          onClick={() => { setSelectedSubmission(s); setPage("submission_detail"); }}>
                          View Results
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
    </>
  );
}

// ─────────────────────────────────────────────
// SUBMISSION DETAIL
// FIX: calls /reports/submission/{id} which now returns all fields
// FIX: consistent concept_data field usage
// ─────────────────────────────────────────────
function SubmissionDetail({ submission, setPage, backLabel }) {
  const { token } = useAuth();
  const [detail, setDetail] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  const subId = submission?.submission_id || submission?.id;

  useEffect(() => {
    if (!subId) { setPage("results"); return; }
    // FIX: single unified endpoint that returns all fields
    api.get(`/reports/submission/${subId}`, token)
      .then(d => { setDetail(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [subId]);

  const downloadPDF = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${BASE}/reports/submission/${subId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `EvalAI_Report_${subId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) { alert("Could not download report: " + e.message); }
    setDownloading(false);
  };

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;
  if (!detail) return <div style={{ padding: 40 }}>Results not available yet. The teacher may not have evaluated this submission.</div>;

  const heatmapColors = (val) => {
    if (val >= 0.75) return "#16A34A";
    if (val >= 0.4)  return "#D97706";
    return "#DC2626";
  };

  const radarData = detail.answers?.map((a, i) => ({
    question:  `Q${i + 1}`,
    score:     Math.round(((a.score || 0) / (a.max_score || 1)) * 100),
    coverage:  Math.round((a.concept_data?.coverage || a.coverage || 0) * 100),
  })) || [];

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>Submission Results</h1>
            <p>Detailed breakdown of your performance</p>
          </div>
          <div className="flex gap-2">
            <button className="btn btn-secondary btn-sm" onClick={() => setPage("results")}>{backLabel || "← Back"}</button>
            <button className="btn btn-primary btn-sm" onClick={downloadPDF} disabled={downloading}>
              {downloading ? <span className="spinner" /> : "⬇ Download PDF"}
            </button>
          </div>
        </div>
      </div>
      <div className="page-body">
        {/* Score Header */}
        <div className="card mb-6" style={{ overflow: "hidden" }}>
          <div style={{
            background: "linear-gradient(135deg, var(--accent) 0%, #1A3A9E 100%)",
            padding: "32px 40px", color: "white",
            display: "flex", alignItems: "center", gap: 40
          }}>
            <div>
              <div style={{ fontSize: 13, opacity: 0.7, textTransform: "uppercase", letterSpacing: "0.08em" }}>Total Score</div>
              <div style={{ fontSize: 60, fontFamily: "DM Serif Display", lineHeight: 1 }}>{detail.total_score}</div>
            </div>
            <div style={{ width: 1, height: 80, background: "rgba(255,255,255,0.2)" }} />
            <div>
              <div style={{ fontSize: 13, opacity: 0.7, textTransform: "uppercase", letterSpacing: "0.08em" }}>Percentage</div>
              <div style={{ fontSize: 60, fontFamily: "DM Serif Display", lineHeight: 1 }}>{detail.percentage}%</div>
            </div>
            <div style={{ marginLeft: "auto" }}>
              <span style={{
                padding: "8px 20px", borderRadius: 999,
                background: detail.percentage >= 60 ? "#16A34A" : "#DC2626",
                fontSize: 14, fontWeight: 600,
              }}>
                {detail.percentage >= 75 ? "Distinction" : detail.percentage >= 60 ? "Pass" : "Needs Improvement"}
              </span>
            </div>
          </div>
        </div>

        <div className="tabs">
          {["overview", "heatmap", "breakdown"].map(t => (
            <button key={t} className={`tab-btn ${activeTab === t ? "active" : ""}`}
              onClick={() => setActiveTab(t)}>
              {t === "overview" ? "Overview" : t === "heatmap" ? "Concept Heatmap" : "Answer Breakdown"}
            </button>
          ))}
        </div>

        {activeTab === "overview" && (
          <>
            <div className="grid-2 mb-6">
              <div className="card card-pad">
                <h3 className="section-title">Performance Radar</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="question" tick={{ fontSize: 12 }} />
                    <Radar name="Score %" dataKey="score" stroke="#2D5BE3" fill="#2D5BE3" fillOpacity={0.3} />
                    <Radar name="Coverage %" dataKey="coverage" stroke="#16A34A" fill="#16A34A" fillOpacity={0.2} />
                    <Legend />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
              <div className="card card-pad">
                <h3 className="section-title">Score per Question</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={detail.answers?.map((a, i) => ({ name: `Q${i+1}`, score: a.score || 0, max: a.max_score }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8E6F0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="score" name="Your Score" fill="#2D5BE3" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="max" name="Max Score" fill="#E8E6F0" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Feedback */}
            <div className="card card-pad">
              <h3 style={{ fontSize: 18, marginBottom: 16 }}>AI Feedback</h3>
              {detail.answers?.filter(a => a.feedback && a.feedback !== "Pending evaluation").length > 0 ? (
                detail.answers.map((a, i) => a.feedback && a.feedback !== "Pending evaluation" && (
                  <div className="feedback-card mb-4" key={i}>
                    <h4>Q{i + 1} Feedback</h4>
                    <p>{a.feedback}</p>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ padding: "20px 0" }}>
                  <p>Feedback will appear here after the teacher evaluates your submission.</p>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === "heatmap" && (
          <div className="card card-pad">
            <h3 className="section-title">Concept Coverage Heatmap</h3>
            <p className="text-sm text-muted mb-6">Shows which key concepts you covered, partially covered, or missed</p>
            {detail.answers?.map((a, i) => {
              // FIX: consistent — always read from concept_data
              const cd = a.concept_data || {};
              const covered = cd.covered || [];
              const partial = cd.partial || [];
              const missing = cd.missing || [];
              const wrong   = cd.wrong   || [];
              const details = cd.concept_details || [];
              const coverage = cd.coverage || a.coverage || 0;
              const status   = cd.status || (coverage >= 0.65 ? "strong" : coverage >= 0.35 ? "partial" : "weak");
              const hasData  = covered.length || partial.length || missing.length || wrong.length || details.length;

              return (
                <div key={i} style={{ marginBottom: 28 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                    <div className="font-600" style={{ fontSize: 14 }}>Q{i + 1}: {(a.question_text || a.question || "").slice(0, 65)}...</div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span className="text-xs text-muted">Coverage:</span>
                      <span className="font-600" style={{ fontSize: 13, color: heatmapColors(coverage) }}>{Math.round(coverage * 100)}%</span>
                      <span className={`badge ${status === "strong" ? "badge-green" : status === "partial" ? "badge-amber" : "badge-red"}`}>{status}</span>
                    </div>
                  </div>

                  <div className="heatmap-row" style={{ marginBottom: 12 }}>
                    <div className="heatmap-label">Coverage</div>
                    <div className="heatmap-bar-track">
                      <div className="heatmap-bar-fill" style={{ width: `${coverage * 100}%`, background: heatmapColors(coverage) }} />
                    </div>
                    <div className="heatmap-pct">{Math.round(coverage * 100)}%</div>
                  </div>

                  {hasData ? (
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {details.length > 0 ? details.map((c, j) => (
                        <div key={j} style={{
                          background: c.status === "matched" ? "var(--green-light)" : c.status === "partial" ? "var(--amber-light)" : "var(--red-light)",
                          borderRadius: 8, padding: "8px 12px",
                          borderLeft: `3px solid ${c.status === "matched" ? "var(--green)" : c.status === "partial" ? "var(--amber)" : "var(--red)"}`,
                        }}>
                          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
                            <div className="text-sm" style={{ flex: 1 }}>
                              <span style={{ marginRight: 6 }}>
                                {c.status === "matched" ? "✓" : c.status === "partial" ? "~" : c.status === "wrong" ? "⚠" : "✗"}
                              </span>
                              {c.concept}
                            </div>
                            <span className={`badge ${c.status === "matched" ? "badge-green" : c.status === "partial" ? "badge-amber" : "badge-red"}`} style={{ flexShrink: 0 }}>
                              {c.status} · {Math.round((c.coverage || 0) * 100)}%
                            </span>
                          </div>
                          {(c.covered_kws?.length > 0 || c.missing_kws?.length > 0) && (
                            <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 4 }}>
                              {c.covered_kws?.slice(0, 5).map((kw, k) => (
                                <span key={k} style={{ fontSize: 11, background: "rgba(22,163,74,0.15)", color: "var(--green)", borderRadius: 4, padding: "1px 6px" }}>
                                  ✓ {kw.keyword}
                                </span>
                              ))}
                              {c.missing_kws?.slice(0, 5).map((kw, k) => (
                                <span key={k} style={{ fontSize: 11, background: "rgba(220,38,38,0.10)", color: "var(--red)", borderRadius: 4, padding: "1px 6px" }}>
                                  ✗ {kw.keyword}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )) : (
                        <>
                          {covered.map((c, j) => (
                            <div key={`cov-${j}`} style={{ background: "var(--green-light)", borderRadius: 8, padding: "7px 12px", borderLeft: "3px solid var(--green)", fontSize: 13 }}>✓ {c}</div>
                          ))}
                          {partial.map((c, j) => (
                            <div key={`par-${j}`} style={{ background: "var(--amber-light)", borderRadius: 8, padding: "7px 12px", borderLeft: "3px solid var(--amber)", fontSize: 13 }}>~ {c}</div>
                          ))}
                          {missing.map((c, j) => (
                            <div key={`mis-${j}`} style={{ background: "var(--red-light)", borderRadius: 8, padding: "7px 12px", borderLeft: "3px solid var(--red)", fontSize: 13 }}>✗ {c}</div>
                          ))}
                          {wrong.map((c, j) => (
                            <div key={`wrg-${j}`} style={{ background: "var(--amber-light)", borderRadius: 8, padding: "7px 12px", borderLeft: "3px solid var(--amber)", fontSize: 13 }}>⚠ {c}</div>
                          ))}
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted" style={{ padding: "8px 0" }}>
                      No concept data available — re-evaluate to generate heatmap.
                    </div>
                  )}
                  <div className="divider" style={{ marginTop: 16 }} />
                </div>
              );
            })}
          </div>
        )}

        {activeTab === "breakdown" && (
          <div>
            {detail.answers?.map((a, i) => (
              <div className="card card-pad mb-4" key={i}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>Question {i + 1}</div>
                    <div className="font-600" style={{ fontSize: 15, marginTop: 4 }}>{a.question}</div>
                  </div>
                  <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
                    <div style={{ fontSize: 24, fontFamily: "DM Serif Display", color: "var(--accent)" }}>{a.score}</div>
                    <div className="text-xs text-muted">/ {a.max_score}</div>
                  </div>
                </div>

                <div style={{ background: "var(--cream)", borderRadius: "var(--radius-sm)", padding: "12px 14px", marginBottom: 12 }}>
                  <div className="text-xs text-muted font-600 mb-1">Your Answer</div>
                  <div className="text-sm">{a.student_answer}</div>
                </div>

                <div className="flex gap-2 flex-wrap mb-3">
                  {[
                    { label: "Similarity",  val: a.similarity },
                    { label: "Entailment",  val: a.entailment },
                    { label: "Coverage",    val: a.coverage },
                    { label: "Confidence",  val: a.confidence },
                  ].filter(m => m.val != null).map(m => (
                    <div key={m.label} style={{ background: "var(--accent-light)", borderRadius: 8, padding: "4px 10px" }}>
                      <span className="text-xs text-muted">{m.label}: </span>
                      <span className="text-xs font-600" style={{ color: "var(--accent)" }}>{(m.val * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>

                {a.feedback && a.feedback !== "Pending evaluation" && (
                  <div className="feedback-card">
                    <h4>AI Feedback</h4>
                    <p>{a.feedback}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

// ─────────────────────────────────────────────
// APP
// ─────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}