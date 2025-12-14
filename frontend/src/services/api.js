import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1', // Proxy configured in vite.config.js
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
