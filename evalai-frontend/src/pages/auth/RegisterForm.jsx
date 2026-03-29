import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

export default function RegisterForm({ onSwitch }) {
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
        id: payload.user_id, role: payload.role,
        name: payload.name || form.name,
        email: payload.email || form.email,
        institution: payload.institution || form.institution,
      }, res.access_token);
    } catch (e) { setError(e.message); }
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
            {r === "student" ? "🎓 Student" : "👨🏫 Teacher"}
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
