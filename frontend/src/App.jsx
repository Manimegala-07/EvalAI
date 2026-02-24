import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import TeacherDashboard from "./pages/TeacherDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import QuestionBank from "./pages/QuestionBank";
import CreateTest from "./pages/CreateTest";
import TakeTest from "./pages/TakeTest";
import AnalyticsPage from "./pages/AnalyticsPage";
import StudentReport from "./pages/StudentReport";
import TeacherDetailedAnalytics from "./pages/TeacherDetailedAnalytics";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/teacher"
          element={
            <ProtectedRoute role="teacher">
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student"
          element={
            <ProtectedRoute role="student">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        <Route
            path="/teacher/questions"
            element={
                <ProtectedRoute role="teacher">
                <QuestionBank />
                </ProtectedRoute>
            }
        />

        <Route
            path="/teacher/create-test"
            element={
                <ProtectedRoute role="teacher">
                <CreateTest />
                </ProtectedRoute>
            }
        />

        <Route
            path="/student/take-test/:testId"
            element={
                <ProtectedRoute role="student">
                <TakeTest />
                </ProtectedRoute>
            }
        />

        <Route
        path="/teacher/analytics/:testId"
        element={
            <ProtectedRoute role="teacher">
            <AnalyticsPage />
            </ProtectedRoute>
        }
        />

        <Route
          path="/student/report/:submissionId"
          element={
            <ProtectedRoute role="student">
              <StudentReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/teacher/analytics-detailed/:testId"
          element={<TeacherDetailedAnalytics />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
