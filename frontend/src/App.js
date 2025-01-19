// App.js
import React from "react";
import { Routes, Route } from "react-router-dom"; // Removed Router import
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import DashboardListPage from "./pages/DashboardListPage";
import DashboardDetailPage from "./pages/DashboardDetailPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import "./App.css"; // local styles for layout

function App() {
  return (
    <div className="app-container">
      {/* Optionally place Navbar at the top if desired */}
      {/* <Navbar /> */}
      <Sidebar />
      <div className="app-main">
        <Routes>
          <Route path="/" element={<DashboardListPage />} />
          <Route path="/dashboard/:id" element={<DashboardDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
