import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "student"
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async () => {
    try {
      await API.post("/register", form);

      alert("Registration successful! Please login.");
      navigate("/");
    } catch (error) {
      console.error(error);
      alert("Registration failed.");
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "500px" }}>
      <div className="card shadow p-4">
        <h2 className="text-center mb-4">Register</h2>

        <input
          className="form-control mb-3"
          name="name"
          placeholder="Full Name"
          onChange={handleChange}
        />

        <input
          className="form-control mb-3"
          name="email"
          placeholder="Email"
          onChange={handleChange}
        />

        <input
          type="password"
          className="form-control mb-3"
          name="password"
          placeholder="Password"
          onChange={handleChange}
        />

        <select
          className="form-select mb-3"
          name="role"
          onChange={handleChange}
          value={form.role}
        >
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
        </select>

        <button
          className="btn btn-success w-100"
          onClick={handleRegister}
        >
          Register
        </button>

        <p className="text-center mt-3">
          Already have an account?{" "}
          <span
            style={{ color: "blue", cursor: "pointer" }}
            onClick={() => navigate("/")}
          >
            Login
          </span>
        </p>
      </div>
    </div>
  );
}

export default Register;
