import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../services/api";

function TeacherDetailedAnalytics() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await API.get(`/analytics/tests/${testId}/detailed`);
      setData(res.data.students);
    } catch (err) {
      console.error(err);
    }
  };

  if (!data) {
    return <div className="container mt-5">Loading...</div>;
  }

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Detailed Concept Analytics</h2>

      {data.map((student, index) => (
        <div key={index} className="card p-4 mb-5 shadow-sm">

          <h4 className="mb-3">Student ID: {student.student_id}</h4>

          <div className="mb-3">
            <strong>Total MiniLM:</strong> {student.total_minilm} <br />
            <strong>Total Hybrid:</strong> {student.total_hybrid}
          </div>

          <hr />

          {student.answers.map((ans, i) => {

            const diff = ans.minilm_score - ans.hybrid_score;

            let scoreColor = "";
            if (Math.abs(diff) < 0.5) scoreColor = "#d4edda";
            else if (diff > 0) scoreColor = "#cce5ff";
            else scoreColor = "#f8d7da";

            return (
              <div key={i} className="mb-4 p-3 border rounded">

                <h6>Q{i + 1}: {ans.question}</h6>

                <p><strong>Student Answer:</strong> {ans.student_answer}</p>

                {/* Score Comparison */}
                <div
                  className="p-2 mb-2"
                  style={{ backgroundColor: scoreColor }}
                >
                  <strong>MiniLM:</strong> {ans.minilm_score}
                  {" | "}
                  <strong>Hybrid:</strong> {ans.hybrid_score}
                  {" | "}
                  <strong>Difference:</strong> {diff.toFixed(2)}
                </div>

                {/* 🔥 Concept Heatmap */}
                <div className="mt-3">

                  <div className="mb-1">
                    <span className="badge bg-success me-2">Correct Concepts</span>
                    {ans.concept_data?.correct?.length > 0
                      ? ans.concept_data.correct.join(", ")
                      : "None"}
                  </div>

                  <div className="mb-1">
                    <span className="badge bg-warning text-dark me-2">Missing Concepts</span>
                    {ans.concept_data?.missing?.length > 0
                      ? ans.concept_data.missing.join(", ")
                      : "None"}
                  </div>

                  <div className="mb-1">
                    <span className="badge bg-danger me-2">Extra / Incorrect Concepts</span>
                    {ans.concept_data?.extra?.length > 0
                      ? ans.concept_data.extra.join(", ")
                      : "None"}
                  </div>

                  {ans.concept_data?.contradiction && (
                    <div className="mt-2">
                      <span className="badge bg-dark">
                        Logical Contradiction Detected (NLI)
                      </span>
                    </div>
                  )}

                </div>

              </div>
            );
          })}

        </div>
      ))}

      <button
        className="btn btn-secondary"
        onClick={() => navigate("/teacher")}
      >
        Back
      </button>
    </div>
  );
}

export default TeacherDetailedAnalytics;