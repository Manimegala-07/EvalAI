import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../services/api";
import {
  Bar
} from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function AnalyticsPage() {
  const { testId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const res = await API.get(`/analytics/tests/${testId}`);
      setData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (!data) return <div className="container mt-5">Loading analytics...</div>;

  const chartData = {
    labels: data.ranking.map(r => `Student ${r.student_id}`),
    datasets: [
      {
        label: "Scores",
        data: data.ranking.map(r => r.score),
        backgroundColor: "rgba(54, 162, 235, 0.6)",
      },
    ],
  };

  return (
    <div className="container mt-5">
      <h2>Test Analytics</h2>

      <div className="card p-3 mb-4">
        <h5>Average: {data.average_score}</h5>
        <h5>Highest: {data.highest_score}</h5>
        <h5>Lowest: {data.lowest_score}</h5>
      </div>

      <div className="card p-3">
        <Bar data={chartData} />
      </div>
    </div>
  );
}

export default AnalyticsPage;
