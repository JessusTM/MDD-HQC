import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const metricsApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getCimMetrics = async (path) => {
  const response = await metricsApi.post('/metrics/cim', { path });
  return response.data;
};
