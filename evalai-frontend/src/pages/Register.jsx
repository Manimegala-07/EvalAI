import { useState } from "react"
import { useNavigate } from "react-router-dom"
import API from "../services/api"

function Register() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "teacher",
    institution: ""
  })

  const handleRegister = async () => {
    try {
      await API.post("/register", form)
      alert("Registration successful")
      navigate("/")
    } catch {
      alert("Registration failed")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-blue-100">
      <div className="bg-white p-10 rounded-2xl shadow-lg w-[420px]">
        <h1 className="text-2xl font-bold text-center mb-8">
          Create Account
        </h1>

        <input
          className="w-full border p-3 rounded mb-4"
          placeholder="Full Name"
          onChange={(e) =>
            setForm({ ...form, name: e.target.value })
          }
        />

        <input
          className="w-full border p-3 rounded mb-4"
          placeholder="Institution"
          onChange={(e) =>
            setForm({ ...form, institution: e.target.value })
          }
        />

        <input
          className="w-full border p-3 rounded mb-4"
          placeholder="Email"
          onChange={(e) =>
            setForm({ ...form, email: e.target.value })
          }
        />

        <input
          type="password"
          className="w-full border p-3 rounded mb-4"
          placeholder="Password"
          onChange={(e) =>
            setForm({ ...form, password: e.target.value })
          }
        />

        <select
          className="w-full border p-3 rounded mb-6"
          onChange={(e) =>
            setForm({ ...form, role: e.target.value })
          }
        >
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
        </select>

        <button
          onClick={handleRegister}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition"
        >
          Register
        </button>
      </div>
    </div>
  )
}

export default Register