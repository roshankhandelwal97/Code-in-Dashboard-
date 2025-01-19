/* DashboardDetailPage.jsx */
import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";
import Block from "../components/Block";
import "../styles/DashboardDetailPage.css";


function DashboardDetailPage() {
  const { id } = useParams();
  const [dashboard, setDashboard] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchDashboard();
    // eslint-disable-next-line
  }, [id]);

  const fetchDashboard = async () => {
    try {
      const response = await api.get(`/dashboard/${id}/`);
      setDashboard(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const uploadCSV = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    try {
      await api.post(`/dashboard/${id}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("File uploaded successfully");
      setSelectedFile(null);
    } catch (err) {
      console.error(err);
      alert("File upload error");
    }
  };

  return (
    <div className="dashboard-detail">
      <h2 className="dashboard-detail__title">
        Dashboard: {dashboard?.title}
      </h2>

      {/* CSV Upload Section */}
      <div className="dashboard-detail__upload">
        <label className="dashboard-detail__upload-label">
          Upload CSV:
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="dashboard-detail__upload-input"
          />
        </label>
        <button
          className="dashboard-detail__upload-btn"
          onClick={uploadCSV}
          disabled={!selectedFile}
        >
          Upload
        </button>
      </div>

      {/* Blocks Section */}
      <div className="dashboard-detail__blocks">
        {dashboard?.blocks?.map((block) => (
          <Block
            key={block.id}
            block={block}
            onBlockChange={fetchDashboard}
          />
        ))}
      </div>
    </div>
  );
}

export default DashboardDetailPage;
