import { useState } from "react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";

export default function AuthPage() {
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
