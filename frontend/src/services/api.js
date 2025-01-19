import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api"; // Adjust for your backend

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Optional: If you store the token in localStorage, attach it to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
