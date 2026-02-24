import { useState, useEffect } from "react";
import API from "../services/api";

function QuestionBank() {
  const [questions, setQuestions] = useState([]);
  const [form, setForm] = useState({
    text: "",
    model_answer: ""
  });

  const loadQuestions = async () => {
    const res = await API.get("/questions");
    setQuestions(res.data);
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const addQuestion = async () => {
    await API.post("/questions", form);
    setForm({ text: "", model_answer: "" });
    loadQuestions();
  };

  return (
    <div className="container mt-4">
      <h2>Question Bank</h2>

      <div className="card p-3 mb-4">
        <h5>Add New Question</h5>

        <textarea
          className="form-control mb-2"
          placeholder="Question text"
          value={form.text}
          onChange={(e) =>
            setForm({ ...form, text: e.target.value })
          }
        />

        <textarea
          className="form-control mb-2"
          placeholder="Model answer"
          value={form.model_answer}
          onChange={(e) =>
            setForm({ ...form, model_answer: e.target.value })
          }
        />

        <button className="btn btn-success" onClick={addQuestion}>
          Add Question
        </button>
      </div>

      <h5>Existing Questions</h5>
      <ul className="list-group">
        {questions.map((q) => (
          <li key={q.id} className="list-group-item">
            <strong>{q.text}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default QuestionBank;
