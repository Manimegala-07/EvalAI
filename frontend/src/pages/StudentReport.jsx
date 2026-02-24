import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../services/api";

function StudentReport() {
  const { submissionId } = useParams();
  const navigate = useNavigate();

  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      const res = await API.get(`/submission/${submissionId}/report`);
      setReport(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load report.");
    }
  };

  const handleDownload = async () => {
    try {
      const response = await API.get(
        `/submission/${submissionId}/download`,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${submissionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  if (error) {
    return (
      <div className="container mt-5">
        <h4 className="text-danger">{error}</h4>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mt-5">
        <h4>Generating AI feedback... Please wait.</h4>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Learning Report</h2>

      <div className="alert alert-info">
        ⚙️ MiniLM + NLI Concept Evaluation
      </div>

      {/* ===== TOTAL SECTION ===== */}
      <div className="card p-4 mb-4 shadow-sm">
        <h4>MiniLM Total: {report.total_minilm}</h4>
        <h4>Hybrid Total: {report.total_hybrid}</h4>

        <h5>
          MiniLM %: {report.percentage_minilm}% | Hybrid %: {report.percentage_hybrid}%
        </h5>
      </div>

      {/* ===== PER QUESTION ===== */}
      {report.answers.map((ans, index) => (
        <div key={index} className="card p-4 mb-4 shadow-sm">

          <h5>Q{index + 1}: {ans.question}</h5>

          <p>
            <strong>Your Answer:</strong>
            <br />
            {ans.student_answer}
          </p>

          <div className="mb-2">
            <strong>MiniLM:</strong> {ans.score_minilm} / {ans.max_score}
            {" | "}
            <strong>Hybrid:</strong> {ans.score_hybrid} / {ans.max_score}
          </div>

          <hr />

          {/* 🔥 Concept Heatmap */}
          <div className="mb-3">

            <div className="mb-2">
              <span className="badge bg-success me-2">
                Matched Concepts
              </span>
              {ans.concept_data?.correct?.length > 0
                ? ans.concept_data.correct.join(", ")
                : "None"}
            </div>

            <div className="mb-2">
              <span className="badge bg-warning text-dark me-2">
                Missing Concepts
              </span>
              {ans.concept_data?.missing?.length > 0
                ? ans.concept_data.missing.join(", ")
                : "None"}
            </div>

            <div className="mb-2">
              <span className="badge bg-danger me-2">
                Incorrect Concepts
              </span>
              {ans.concept_data?.extra?.length > 0
                ? ans.concept_data.extra.join(", ")
                : "None"}
            </div>

            {ans.concept_data?.contradiction && (
              <div className="mt-2">
                <span className="badge bg-dark">
                  Logical Contradiction Detected
                </span>
              </div>
            )}

          </div>

          {/* 🔥 AI FEEDBACK SECTION */}
          <div className="alert alert-secondary">
            <strong>AI Feedback:</strong>
            <br />
            {ans.feedback_hybrid || ans.feedback_minilm || "Generating..."}
          </div>

        </div>
      ))}

      <button className="btn btn-primary me-3" onClick={handleDownload}>
        Download PDF
      </button>

      <button
        className="btn btn-secondary"
        onClick={() => navigate("/student")}
      >
        Back to Dashboard
      </button>
    </div>
  );
}

export default StudentReport;