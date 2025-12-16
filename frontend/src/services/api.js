import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1', // Proxy configured in vite.config.js
  // Don't set default Content-Type header - let Axios handle it automatically
  // For FormData, browser will set multipart/form-data with boundary
  // For JSON, Axios will set application/json
});

export default api;
