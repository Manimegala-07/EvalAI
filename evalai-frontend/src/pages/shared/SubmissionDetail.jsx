import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLang } from "../../context/LangContext";
import api from "../../services/apiClient";
import { BASE } from "../../services/apiClient";
import HeatmapBar from "../../components/HeatmapBar";

// ── Concept heatmap pill ─────────────────────────────────────
function ConceptPill({ concept, status }) {
  const colors = {
    matched: { bg: "var(--green-light)",  color: "var(--green)",  icon: "✓" },
    partial: { bg: "var(--amber-light)",  color: "var(--amber)",  icon: "~" },
    missing: { bg: "var(--red-light)",    color: "var(--red)",    icon: "✗" },
    wrong:   { bg: "var(--amber-light)",  color: "var(--amber)",  icon: "⚠" },
  };
  const s = colors[status] || colors.missing;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      background: s.bg, color: s.color, borderRadius: 20,
      padding: "3px 10px", fontSize: 12, fontWeight: 500, margin: "3px 4px 3px 0",
    }}>
      {s.icon} {concept}
    </span>
  );
}

// ── Sentence heatmap row ─────────────────────────────────────
function SentenceRow({ sentence, status, similarity, entailment, t }) {
  const styles = {
    matched:   { border: "var(--green)",  bg: "#F0FDF4", labelKey: "covered",    labelColor: "var(--green)" },
    partial:   { border: "var(--amber)",  bg: "#FFFBEB", labelKey: "partial",    labelColor: "var(--amber)" },
    wrong:     { border: "var(--red)",    bg: "#FEF2F2", labelKey: "incorrect",  labelColor: "var(--red)"   },
    irrelevant:{ border: "var(--border)", bg: "var(--cream)", labelKey: "no_data", labelColor: "var(--ink-muted)" },
  };
  const s = styles[status] || styles.irrelevant;
  return (
    <div style={{ borderLeft: `3px solid ${s.border}`, background: s.bg, borderRadius: "0 8px 8px 0", padding: "10px 14px", marginBottom: 8 }}>
      <div style={{ fontSize: 13.5, color: "var(--ink)", lineHeight: 1.6, marginBottom: 6 }}>{sentence}</div>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: s.labelColor }}>{t(s.labelKey)}</span>
        <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>sim {Math.round(similarity * 100)}%</span>
        <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>ent {Math.round(entailment * 100)}%</span>
      </div>
    </div>
  );
}

// ── Override panel (teacher only) ───────────────────────────
function OverridePanel({ answers, submissionId, token, t, onSaved }) {
  const [overrides, setOverrides] = useState({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  const set = (id, field, val) =>
    setOverrides(prev => ({ ...prev, [id]: { ...prev[id], [field]: val } }));

  const save = async () => {
    setSaving(true);
    try {
      const res = await api.post(`/submissions/${submissionId}/override`, { overrides }, token);
      setMsg(`✅ Saved — new total: ${res.total_score} / ${res.total_max} (${res.percentage}%)`);
      onSaved();
    } catch (e) { setMsg("❌ " + e.message); }
    setSaving(false);
    setTimeout(() => setMsg(""), 4000);
  };

  return (
    <div className="card card-pad mt-4">
      <h3 className="section-title">{t("override")}</h3>
      <div className="alert alert-info mb-4" style={{ fontSize: 13 }}>{t("override_info")}</div>
      {answers.map((a, i) => (
        <div key={a.question_id} style={{ borderBottom: "1px solid var(--border)", paddingBottom: 16, marginBottom: 16 }}>
                    <div className="text-sm font-600 mb-2">Q{i + 1}: {getQ(a)?.slice(0, 80)}...</div>
          <div className="flex items-center gap-3" style={{ flexWrap: "wrap" }}>
            <span className="badge badge-blue">{t("ai_score")}: {a.score} / {a.max_score}</span>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <label className="form-label" style={{ margin: 0, fontSize: 13 }}>{t("override_score")}:</label>
              <input type="number" className="form-input" style={{ width: 80 }}
                min={0} max={a.max_score} step={0.5}
                placeholder={a.score}
                onChange={e => set(a.question_id, "score", e.target.value)} />
            </div>
            <input className="form-input" style={{ flex: 1, minWidth: 180 }}
              placeholder={t("reason_placeholder")}
              onChange={e => set(a.question_id, "reason", e.target.value)} />
          </div>
        </div>
      ))}
      {msg && <div className={`alert ${msg.startsWith("✅") ? "alert-success" : "alert-error"} mb-3`}>{msg}</div>}
      <div className="flex justify-end gap-3">
        <button className="btn btn-secondary btn-sm" onClick={() => setOverrides({})}>
          {t("clear_overrides")}
        </button>
        <button className="btn btn-primary" onClick={save} disabled={saving}>
          {saving ? <><span className="spinner" style={{ width: 14, height: 14 }} /> {t("saving")}</> : t("save_update")}
        </button>
      </div>
    </div>
  );
}

// ── Main component ───────────────────────────────────────────
export default function SubmissionDetail({ submission, setPage, backLabel, onBack, isTeacher = false }) {
  const { token, user } = useAuth();
  const { t, lang } = useLang();
  const [detail, setDetail]         = useState(null);
  const [loading, setLoading]       = useState(true);
  const [tab, setTab]               = useState("overview");
  const [translated, setTranslated] = useState({});  // { [qid]: { question, feedback } }
  const [translating, setTranslating] = useState(false);

  const handleBack = onBack || (() => setPage("results"));
  const resolvedBackLabel = backLabel || t("back");

  const fetchDetail = () => {
    const id = submission?.submission_id || submission?.id;
    if (!id) { handleBack(); return; }
    api.get(`/submissions/${id}/detail`, token)
      .then(d => { setDetail(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  // Translate question_text and feedback when lang changes
  useEffect(() => {
    if (!detail || lang === "en") { setTranslated({}); return; }
    const translateContent = async () => {
      setTranslating(true);
      const result = {};
      for (const a of detail.answers || []) {
        try {
          const [qRes, fRes] = await Promise.all([
            api.post("/translate/question", { text: a.question_text, target_lang: lang }),
            a.feedback
              ? api.post("/translate/question", { text: a.feedback, target_lang: lang })
              : Promise.resolve({ translated: "" }),
          ]);
          result[a.question_id] = {
            question: qRes.translated || a.question_text,
            feedback: fRes.translated || a.feedback,
          };
        } catch {
          result[a.question_id] = { question: a.question_text, feedback: a.feedback };
        }
      }
      setTranslated(result);
      setTranslating(false);
    };
    translateContent();
  }, [lang, detail]);

  const getQ = (a) => translated[a.question_id]?.question || a.question_text;
  const getF = (a) => translated[a.question_id]?.feedback  || a.feedback;

  const downloadPdf = async () => {
    const id = submission?.submission_id || submission?.id;
    try {
      const res = await fetch(`${BASE}/reports/submission/${id}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href = url; a.download = `EvalAI_Report_${id}.pdf`;
      a.click(); URL.revokeObjectURL(url);
    } catch { /* silent */ }
  };

  useEffect(() => { fetchDetail(); }, [submission]);

  if (loading) return <div style={{ padding: 60, textAlign: "center" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;
  if (!detail) return <div style={{ padding: 40 }}>Submission not found.</div>;

  const pct       = detail.total_max ? Math.round((detail.total_score / detail.total_max) * 100) : 0;
  const grade     = pct >= 75 ? t("distinction") : pct >= 50 ? t("pass") : t("needs_work");
  const gradeBadge= pct >= 75 ? "badge-green"   : pct >= 50 ? "badge-blue" : "badge-red";
  const showOverride = isTeacher || user?.role === "teacher";
  const submissionId = submission?.submission_id || submission?.id;

  const tabs = [
    { id: "overview",  label: t("overview") },
    { id: "answers",   label: t("answer_breakdown") },
    { id: "concepts",  label: t("concept_map") },
    ...(showOverride ? [{ id: "override", label: t("override") }] : []),
  ];

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>{t("submission_results")}</h1>
            <p>{t("detailed_breakdown")}</p>
          </div>
          <div className="flex gap-2">
            <button className="btn btn-secondary btn-sm" onClick={downloadPdf}>
              {t("download_pdf")}
            </button>
            <button className="btn btn-secondary btn-sm" onClick={handleBack}>{resolvedBackLabel}</button>
          </div>
        </div>
      </div>

      <div className="page-body">
        <div className="page-inner">

          {translating && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 16px", background: "var(--accent-light)", borderRadius: 8, marginBottom: 16 }}>
              <div className="spinner" />
              <span style={{ fontSize: 13, color: "var(--accent)" }}>{t("translating")}</span>
            </div>
          )}

          {/* ── Score summary cards ── */}
          <div className="stat-grid mb-4">
            {[
              { label: t("total_score"), value: `${detail.total_score} / ${detail.total_max}`, accent: true },
              { label: t("percentage"),  value: `${pct}%` },
              { label: t("distinction").includes(grade) ? t("distinction") : "Grade", value: <span className={`badge ${gradeBadge}`}>{grade}</span> },
              { label: t("question"),    value: detail.answers?.length || 0 },
            ].map((s, i) => (
              <div className={`stat-card ${s.accent ? "accent" : ""}`} key={i}>
                <div className="stat-label">{s.label}</div>
                <div className="stat-value">{s.value}</div>
              </div>
            ))}
          </div>

          {/* ── Tabs ── */}
          <div className="tabs">
            {tabs.map(tb => (
              <button key={tb.id} className={`tab-btn ${tab === tb.id ? "active" : ""}`} onClick={() => setTab(tb.id)}>
                {tb.label}
              </button>
            ))}
          </div>

          {/* ══ OVERVIEW TAB ══ */}
          {tab === "overview" && (
            <div className="card card-pad">
              <h3 className="section-title">{t("score_per_question")}</h3>
              {detail.answers?.map((a, i) => {
                const qPct = a.max_score ? Math.round((a.score / a.max_score) * 100) : 0;
                const qColor = qPct >= 75 ? "var(--green)" : qPct >= 50 ? "var(--amber)" : "var(--red)";
                return (
                  <div key={a.question_id} style={{ marginBottom: 16 }}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-600">Q{i + 1}: {getQ(a)?.slice(0, 70)}{getQ(a)?.length > 70 ? "…" : ""}</span>
                      <span className="text-sm font-600" style={{ color: qColor }}>{a.score} / {a.max_score}</span>
                    </div>
                    <div style={{ height: 8, background: "var(--border)", borderRadius: 99, overflow: "hidden" }}>
                      <div style={{ width: `${qPct}%`, height: "100%", background: qColor, borderRadius: 99, transition: "width 0.6s ease" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ══ ANSWER BREAKDOWN TAB ══ */}
          {tab === "answers" && detail.answers?.map((a, i) => (
            <div className="answer-block" key={a.question_id} style={{ marginBottom: 20 }}>
              {/* Question header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                <div>
                  <div className="q-num">{t("question")} {i + 1} · {t("max")} {a.max_score} {t("pts")}</div>
                  <div className="q-text">{getQ(a)}</div>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: a.score / a.max_score >= 0.75 ? "var(--green)" : a.score / a.max_score >= 0.5 ? "var(--amber)" : "var(--red)" }}>
                    {a.score} <span style={{ fontSize: 14, color: "var(--ink-muted)", fontWeight: 400 }}>/ {a.max_score}</span>
                  </div>
                </div>
              </div>

              {/* Student answer */}
              <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>{t("your_answer")}</div>
              <div style={{ fontSize: 14, color: "var(--ink)", lineHeight: 1.75, background: "var(--cream)", padding: "12px 16px", borderRadius: 8, marginBottom: 14 }}>
                {a.student_answer || <em style={{ color: "var(--ink-muted)" }}>{t("no_data")}</em>}
              </div>

              {/* AI scoring signals */}
              <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>{t("ai_scoring")}</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 24px", marginBottom: 14 }}>
                <HeatmapBar label={t("similarity")}  value={a.similarity} />
                <HeatmapBar label={t("entailment")}  value={a.entailment} />
                <HeatmapBar label={t("coverage")}    value={a.coverage}   />
              </div>

              {/* Sentence heatmap */}
              {a.sentence_heatmap?.length > 0 && (
                <>
                  <div className="text-xs text-muted font-600" style={{ textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
                    {t("answer_breakdown")}
                  </div>
                  {a.sentence_heatmap.map((row, si) => (
                    <SentenceRow key={si} {...row} t={t} />
                  ))}
                  <div style={{ marginBottom: 14 }} />
                </>
              )}

              {/* AI Feedback */}
              {a.feedback && (
                <div className="feedback-card">
                  <h4>{t("ai_feedback")}</h4>
                  <p>{getF(a)}</p>
                </div>
              )}
            </div>
          ))}

          {/* ══ CONCEPT MAP TAB ══ */}
          {tab === "concepts" && (
            <div className="card card-pad">
              <h3 className="section-title">{t("concept_coverage")}</h3>
              <p className="text-sm text-muted mb-4">{t("shows_concepts")}</p>

              {/* Legend */}
              <div className="flex gap-3 mb-6" style={{ flexWrap: "wrap" }}>
                {[
                  { status: "matched", label: t("covered")   },
                  { status: "partial", label: t("partial")   },
                  { status: "missing", label: t("missing")   },
                  { status: "wrong",   label: t("incorrect") },
                ].map(l => <ConceptPill key={l.status} concept={l.label} status={l.status} />)}
              </div>

              {detail.answers?.map((a, i) => {
                const cd = a.concept_data || {};
                const covered = cd.covered || [];
                const partial = cd.partial || [];
                const missing = cd.missing || [];
                const wrong   = cd.wrong   || [];
                const total   = covered.length + partial.length + missing.length + wrong.length;
                if (total === 0) return null;

                return (
                  <div key={a.question_id} style={{ marginBottom: 24 }}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-600">Q{i + 1}: {getQ(a)?.slice(0, 80)}{getQ(a)?.length > 80 ? "…" : ""}</div>
                      <span className="badge badge-blue">{t("coverage")}: {Math.round((a.coverage || 0) * 100)}%</span>
                    </div>
                    <div style={{ marginBottom: 8 }}>
                      {covered.map(c => <ConceptPill key={c} concept={c} status="matched" />)}
                      {partial.map(c => <ConceptPill key={c} concept={c} status="partial" />)}
                      {missing.map(c => <ConceptPill key={c} concept={c} status="missing" />)}
                      {wrong.map(c   => <ConceptPill key={c} concept={c} status="wrong"   />)}
                    </div>
                    <div style={{ height: 1, background: "var(--border)", marginTop: 12 }} />
                  </div>
                );
              })}
            </div>
          )}

          {/* ══ OVERRIDE TAB (teacher only) ══ */}
          {tab === "override" && showOverride && (
            <OverridePanel
              answers={detail.answers || []}
              submissionId={submissionId}
              token={token}
              t={t}
              onSaved={fetchDetail}
            />
          )}

        </div>
      </div>
    </>
  );
}
