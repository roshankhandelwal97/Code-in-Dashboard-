/* DashboardListPage.jsx */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "../styles/DashboardListPage.css";

function DashboardListPage() {
  const navigate = useNavigate();
  const [dashboards, setDashboards] = useState([]);
  const [title, setTitle] = useState("");

  useEffect(() => {
    fetchDashboards();
  }, []);

  const fetchDashboards = async () => {
    try {
      const response = await api.get("/dashboard/");
      setDashboards(response.data);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        navigate("/login");
      }
    }
  };

  const createDashboard = async () => {
    if (!title.trim()) return;
    try {
      await api.post("/dashboard/", { title });
      setTitle("");
      fetchDashboards();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="dashboard-list">
      <h2 className="dashboard-list__title">My Dashboards</h2>
      <ul className="dashboard-list__items">
        {dashboards.map((db) => (
          <li
            key={db.id}
            className="dashboard-list__item"
            onClick={() => navigate(`/dashboard/${db.id}`)}
          >
            {db.title}
          </li>
        ))}
      </ul>

      <div className="dashboard-list__create">
        <input
          className="dashboard-list__input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New Dashboard Title"
        />
        <button className="dashboard-list__button" onClick={createDashboard}>
          Create Dashboard
        </button>
      </div>
    </div>
  );
}

export default DashboardListPage;
