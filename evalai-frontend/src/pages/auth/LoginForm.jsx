import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

export default function LoginForm({ onSwitch }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true); setError("");
    try {
      const res = await api.post("/login", form);
      const payload = JSON.parse(atob(res.access_token.split(".")[1]));
      login({
        id: payload.user_id, role: payload.role,
        name: payload.name || form.email,
        email: payload.email || form.email,
        institution: payload.institution || "",
      }, res.access_token);
    } catch (e) { setError(e.message); }
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
        Don&apos;t have an account? <button onClick={onSwitch}>Register</button>
      </div>
    </div>
  );
}
