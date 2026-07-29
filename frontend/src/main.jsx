import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import AdminDashboard from "./AdminDashboard.jsx";

const isAdminRoute =
  window.location.pathname.startsWith("/admin");

createRoot(
  document.getElementById("root")
).render(
  <StrictMode>
    {isAdminRoute ? (
      <AdminDashboard />
    ) : (
      <App />
    )}
  </StrictMode>
);