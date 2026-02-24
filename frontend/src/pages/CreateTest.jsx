import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function CreateTest() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState({});

  // Load question bank
  const loadQuestions = async () => {
    try {
      const res = await API.get("/questions");
      setQuestions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const handleCheckbox = (qid) => {
    setSelected((prev) => {
      const updated = { ...prev };
      if (updated[qid]) {
        delete updated[qid];
      } else {
        updated[qid] = 10; // default max score
      }
      return updated;
    });
  };

  const handleScoreChange = (qid, value) => {
    setSelected((prev) => ({
      ...prev,
      [qid]: parseFloat(value),
    }));
  };

  const handleCreateTest = async () => {
    const questionList = Object.entries(selected).map(
      ([qid, max_score]) => ({
        question_id: parseInt(qid),
        max_score: max_score,
      })
    );

    if (!title || questionList.length === 0) {
      alert("Please enter title and select questions");
      return;
    }

    try {
      await API.post("/tests", {
        title: title,
        questions: questionList,
      });

      alert("Test created successfully!");
      navigate("/teacher");
    } catch (err) {
      console.error(err);
      alert("Failed to create test");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Create Test</h2>

      <div className="mb-4">
        <input
          className="form-control"
          placeholder="Test Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <h4>Select Questions</h4>

      <div className="list-group">
        {questions.map((q) => (
          <div
            key={q.id}
            className="list-group-item"
          >
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <input
                  type="checkbox"
                  onChange={() => handleCheckbox(q.id)}
                />{" "}
                {q.text}
              </div>

              {selected[q.id] !== undefined && (
                <input
                  type="number"
                  className="form-control"
                  style={{ width: "100px" }}
                  value={selected[q.id]}
                  onChange={(e) =>
                    handleScoreChange(q.id, e.target.value)
                  }
                />
              )}
            </div>
          </div>
        ))}
      </div>

      <button
        className="btn btn-success mt-4"
        onClick={handleCreateTest}
      >
        Create Test
      </button>
    </div>
  );
}

export default CreateTest;
