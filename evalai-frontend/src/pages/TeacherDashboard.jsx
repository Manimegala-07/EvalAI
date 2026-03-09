import { useEffect, useState } from "react"
import API from "../services/api"

function TeacherDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    API.get("/dashboard/summary")
      .then((res) => setData(res.data))
      .catch(() => alert("Failed to load dashboard"))
  }, [])

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading Dashboard...
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8">
        Teacher Dashboard
      </h1>

      <div className="grid grid-cols-3 gap-6">

        <StatCard title="Total Tests" value={data.total_tests} />
        <StatCard title="Total Questions" value={data.total_questions} />
        <StatCard title="Total Students" value={data.total_students} />
        <StatCard title="Total Submissions" value={data.total_submissions} />
        <StatCard title="Pending Evaluations" value={data.pending_evaluations} />
        <StatCard title="Average Score" value={data.average_score} />

      </div>
    </div>
  )
}

function StatCard({ title, value }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition">
      <p className="text-gray-500 text-sm">{title}</p>
      <h2 className="text-2xl font-bold mt-2">{value}</h2>
    </div>
  )
}

export default TeacherDashboard