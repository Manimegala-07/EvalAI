import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../services/api";

function TakeTest() {
  const { testId } = useParams();
  const navigate = useNavigate();

  const [testTitle, setTestTitle] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    loadTest();
  }, []);

  const loadTest = async () => {
    try {
      const res = await API.get(`/tests/${testId}`);
      console.log("Test data:", res.data);

      setTestTitle(res.data.title);
      setQuestions(res.data.questions || []);
    } catch (err) {
      console.error("Error loading test:", err);
    }
  };

  const handleAnswerChange = (qid, value) => {
    setAnswers((prev) => ({
      ...prev,
      [qid]: value,
    }));
  };

  const handleSubmit = async () => {
    if (questions.length === 0) {
      alert("No questions loaded.");
      return;
    }

    if (Object.keys(answers).length === 0) {
      alert("Please write answers before submitting.");
      return;
    }

    const formattedAnswers = questions.map((q) => ({
      question_id: q.id,
      student_answer: answers[q.id] || ""
    }));

    try {
      const res = await API.post("/submit-test", {
        test_id: parseInt(testId),
        answers: formattedAnswers
      });

      alert("Test submitted successfully!");
      navigate(`/student/report/${res.data.submission_id}`);
    } catch (err) {
      console.error("Submit error:", err.response?.data || err);
      alert("Submission failed.");
    }
  };

  return (
    <div className="container mt-5">
      <h2>{testTitle}</h2>

      {/* 🔥 SCORING ENGINE LABEL ADDED HERE */}
      <div className="alert alert-info mt-3">
        ⚙️ Scoring Engine: <strong>MiniLM + NLI Hybrid Model</strong>
      </div>
      
      {questions.length === 0 ? (
        <p>Loading questions...</p>
      ) : (
        questions.map((q, index) => (
          <div key={q.id} className="card p-3 mb-4 shadow-sm">
            <h5>
              Q{index + 1}. {q.text}
              <span className="text-muted">
                {" "}({q.max_score} marks)
              </span>
            </h5>

            <textarea
              className="form-control mt-2"
              rows="5"
              placeholder="Write your answer here..."
              onChange={(e) =>
                handleAnswerChange(q.id, e.target.value)
              }
            />
          </div>
        ))
      )}

      {questions.length > 0 && (
        <button
          className="btn btn-success btn-lg"
          onClick={handleSubmit}
        >
          Submit Test
        </button>
      )}
    </div>
  );
}

export default TakeTest;
