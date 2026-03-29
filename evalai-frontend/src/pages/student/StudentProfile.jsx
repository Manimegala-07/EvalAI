import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/apiClient";

export default function StudentProfile() {
  const { user, token, login } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ name: user?.name || "", institution: user?.institution || "", email: user?.email || "" });
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try { await api.put("/users/me", form, token); } catch { /* fallback */ }
    login({ ...user, ...form }, token);
    setSaved(true); setEditing(false);
    setTimeout(() => setSaved(false), 3000);
  };

  const initials = (form.name || "S").slice(0, 2).toUpperCase();

  return (
    <>
      <div className="page-header"><h1>My Profile</h1><p>Your student account & settings</p></div>
      <div className="page-body">
        <div className="page-inner">
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
                  {[{ key: "name", label: "Full Name" }, { key: "institution", label: "Institution" }].map(f => (
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
                  {[{ label: "Full Name", value: form.name }, { label: "Email", value: form.email }, { label: "Institution", value: form.institution || "—" }, { label: "Role", value: "Student" }].map((f, i) => (
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
      </div>
    </>
  );
}
