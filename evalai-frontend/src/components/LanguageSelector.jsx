import { useLang } from "../context/LangContext";

const LANGS = [
  { code: "en", label: "EN",     full: "English", flag: "🇬🇧" },
  { code: "ta", label: "தமிழ்", full: "Tamil",   flag: "🇮🇳" },
  { code: "hi", label: "हिंदी", full: "Hindi",   flag: "🇮🇳" },
];

export default function LanguageSelector() {
  const { lang, setLanguage } = useLang();
  return (
    <div style={{ padding: "12px 16px", borderTop: "1px solid var(--border)" }}>
      <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--ink-muted)", marginBottom: 8 }}>
        🌐 Language
      </div>
      <div style={{ display: "flex", gap: 4 }}>
        {LANGS.map(l => (
          <button key={l.code} onClick={() => setLanguage(l.code)} title={l.full}
            style={{
              flex: 1, padding: "6px 4px", borderRadius: 6,
              border: lang === l.code ? "2px solid var(--accent)" : "1px solid var(--border)",
              background: lang === l.code ? "var(--accent-light)" : "var(--white)",
              color: lang === l.code ? "var(--accent)" : "var(--ink-muted)",
              cursor: "pointer", fontSize: 11, fontWeight: 600, transition: "all 0.15s",
            }}>
            {l.flag} {l.label}
          </button>
        ))}
      </div>
    </div>
  );
}
