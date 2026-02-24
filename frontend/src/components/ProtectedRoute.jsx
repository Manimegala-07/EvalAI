import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

function ProtectedRoute({ children, role }) {
  const token = localStorage.getItem("token");

  if (!token) return <Navigate to="/" />;

  const decoded = jwtDecode(token);

  if (decoded.role !== role) return <Navigate to="/" />;

  return children;
}

export default ProtectedRoute;
