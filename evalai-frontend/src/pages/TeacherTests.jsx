import { useEffect, useState } from "react"
import API from "../services/api"

function TeacherTests() {
  const [tests, setTests] = useState([])

  useEffect(() => {
    API.get("/dashboard/summary") // we reuse summary for now
      .then((res) => {
        // We need real test list later
        setTests(res.data.recent_tests || [])
      })
      .catch(() => alert("Failed to load tests"))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">My Tests</h1>

      {tests.length === 0 && <p>No tests available</p>}

      {tests.map((test) => (
        <TestCard key={test.id} test={test} />
      ))}
    </div>
  )
}

function TestCard({ test }) {

  const handleEvaluate = async () => {
    try {
      await API.post(`/evaluate/${test.id}`)
      alert("Batch evaluation completed")
    } catch {
      alert("Evaluation failed")
    }
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow mb-4">
      <h2 className="text-lg font-semibold">{test.title}</h2>

      <button
        onClick={handleEvaluate}
        className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded"
      >
        Evaluate Test
      </button>
    </div>
  )
}

export default TeacherTests