import "./styles/globalStyles.js";
import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LanguageProvider } from "./context/LangContext";
import AuthPage from "./pages/auth/AuthPage";
import TeacherShell from "./pages/teacher/TeacherShell";
import StudentShell from "./pages/student/StudentShell";

function Router() {
  const { user } = useAuth();
  const [page, setPage] = useState("dashboard");
  if (!user) return <AuthPage />;
  if (user.role === "teacher") return <TeacherShell page={page} setPage={setPage} />;
  return <StudentShell page={page} setPage={setPage} />;
}

export default function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router />
      </LanguageProvider>
    </AuthProvider>
  );
}
