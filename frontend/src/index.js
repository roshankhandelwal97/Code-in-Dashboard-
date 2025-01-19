// index.js
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router } from "react-router-dom"; // Imported Router
import App from "./App";
import './styles/variables.css';
import './styles/global.css';

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Router> 
      <App />
    </Router>
  </React.StrictMode>,
);
