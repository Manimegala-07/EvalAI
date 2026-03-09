import { useState } from "react"
import { useNavigate } from "react-router-dom"
import API from "../services/api"

function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleLogin = async () => {
    try {
      const res = await API.post("/login", { email, password })
      localStorage.setItem("token", res.data.access_token)

      const payload = JSON.parse(atob(res.data.access_token.split(".")[1]))

      if (payload.role === "teacher") {
        navigate("/teacher/dashboard")
      } else {
        navigate("/student/dashboard")
      }
    } catch {
      alert("Invalid credentials")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow w-96">
        <h1 className="text-xl font-semibold mb-6">Login</h1>

        <input
          className="w-full border p-2 rounded mb-3"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          className="w-full border p-2 rounded mb-4"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700"
        >
          Login
        </button>

        <p className="text-sm mt-4 text-center">
          No account?{" "}
          <span
            className="text-indigo-600 cursor-pointer"
            onClick={() => navigate("/register")}
          >
            Register
          </span>
        </p>
      </div>
    </div>
  )
}

export default Login