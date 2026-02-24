import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function TeacherDashboard() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);

  const loadTests = async () => {
    try {
      const res = await API.get("/tests");
      setTests(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTests();
  }, []);

  // 🔥 Evaluate Function
  const handleEvaluate = async (testId, mode) => {
    try {
      await API.post(`/evaluate-test/${testId}?mode=${mode}`);
      alert(`Evaluation completed using ${mode.toUpperCase()} pipeline`);
      loadTests();
    } catch (err) {
      console.error(err);
      alert("Evaluation failed");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Teacher Dashboard</h2>

      <div className="mb-4">
        <button
          className="btn btn-primary me-2"
          onClick={() => navigate("/teacher/questions")}
        >
          Manage Questions
        </button>

        <button
          className="btn btn-success"
          onClick={() => navigate("/teacher/create-test")}
        >
          Create Test
        </button>
      </div>

      <h4>Your Tests</h4>

      {tests.length === 0 ? (
        <p>No tests created yet.</p>
      ) : (
        <ul className="list-group">
          {tests.map((test) => (
            <li
              key={test.id}
              className="list-group-item"
            >
              <div className="d-flex justify-content-between align-items-center">
                <strong>{test.title}</strong>

                <div>
                  {/* 🔵 MiniLM */}
                  <button
                    className="btn btn-outline-primary btn-sm me-2"
                    onClick={() =>
                      handleEvaluate(test.id, "minilm")
                    }
                  >
                    Evaluate (MiniLM)
                  </button>

                  {/* 🔴 Hybrid */}
                  <button
                    className="btn btn-outline-danger btn-sm me-2"
                    onClick={() =>
                      handleEvaluate(test.id, "hybrid")
                    }
                  >
                    Evaluate (MiniLM + NLI)
                  </button>

                  {/* Analytics */}
                  <button
                    className="btn btn-info btn-sm me-2"
                    onClick={() =>
                      navigate(`/teacher/analytics-detailed/${test.id}`)
                    }
                  >
                    Detailed Analytics
                  </button>

                  {/* Reports */}
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() =>
                      navigate(`/teacher/reports/${test.id}`)
                    }
                  >
                    Reports
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default TeacherDashboard;