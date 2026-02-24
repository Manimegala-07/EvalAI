import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip
);

function StudentDashboard() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const testsRes = await API.get("/tests/student");
      const subRes = await API.get("/student/submissions");

      setTests(testsRes.data);
      setSubmissions(subRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getSubmission = (testId) => {
    return submissions.find((s) => s.test_id === testId);
  };

  return (
    <div className="container mt-5">
      <h2>Student Dashboard</h2>

      {/* 📈 Performance Trend */}
      {submissions.length > 0 && (
        <div className="card p-4 mb-4 shadow-sm">
          <h5>Performance Trend</h5>

          <Line
            data={{
              labels: submissions.map((s) => `Test ${s.test_id}`),
              datasets: [
                {
                  label: "MiniLM",
                  data: submissions.map((s) => s.total_minilm),
                  borderColor: "blue",
                },
                {
                  label: "Hybrid",
                  data: submissions.map((s) => s.total_hybrid),
                  borderColor: "green",
                },
              ],
            }}
          />
        </div>
      )}

      {/* Test Cards */}
      {tests.map((test) => {
        const submission = getSubmission(test.id);

        return (
          <div key={test.id} className="card p-3 mb-3 shadow-sm">
            <h5>{test.title}</h5>

            {submission ? (
              <>
                <p className="text-success">✅ Attempted</p>

                <p>
                  <strong>MiniLM:</strong> {submission.total_minilm}
                  {" | "}
                  <strong>Hybrid:</strong> {submission.total_hybrid}
                </p>

                <button
                  className="btn btn-info btn-sm"
                  onClick={() =>
                    navigate(`/student/report/${submission.submission_id}`)
                  }
                >
                  View Learning Report
                </button>
              </>
            ) : (
              <>
                <p className="text-danger">❌ Not Attempted</p>

                <button
                  className="btn btn-primary btn-sm"
                  onClick={() =>
                    navigate(`/student/take-test/${test.id}`)
                  }
                >
                  Take Test
                </button>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default StudentDashboard;