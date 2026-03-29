import { useState } from "react";
import Sidebar from "../../components/Sidebar";
import StudentDashboard from "./StudentDashboard";
import AvailableTests from "./AvailableTests";
import TakeTest from "./TakeTest";
import MySubmissions from "./MySubmissions";
import StudentProfile from "./StudentProfile";
import SubmissionDetail from "../shared/SubmissionDetail";

export default function StudentShell({ page, setPage }) {
  const [selectedTest, setSelectedTest] = useState(null);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

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
