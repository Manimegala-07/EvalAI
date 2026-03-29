import { useState } from "react";
import Sidebar from "../../components/Sidebar";
import TeacherDashboard from "./TeacherDashboard";
import TeacherProfile from "./TeacherProfile";
import QuestionBank from "./QuestionBank";
import TestManagement from "./TestManagement";
import AnalyticsDashboard from "./AnalyticsDashboard";
import TeacherSubmissions from "./TeacherSubmissions";

export default function TeacherShell({ page, setPage }) {
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
      { id: "analytics",   icon: "📊", label: "Analytics" },
      { id: "submissions", icon: "📝", label: "Student Submissions" },
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
