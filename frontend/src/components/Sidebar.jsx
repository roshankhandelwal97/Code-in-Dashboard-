import React from "react";
import { Link } from "react-router-dom";
import "../styles/Sidebar.css";


const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>MyBrand</h2>
      </div>
      <nav className="sidebar-nav">
        <Link to="/">Home</Link>
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
        {/* Additional links */}
      </nav>
    </aside>
  );
};

export default Sidebar;
