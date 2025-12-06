import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getCimMetrics = async (path) => {
  const response = await api.post('/files/metrics-cim', { path });
  return response.data;
};

export const transformCimToPim = async (path) => {
  const response = await api.post('/files/transform-cim-pim', {
    path,
  });
  return response.data;
};

export const transformPimToPsm = async (path) => {
  const response = await api.post('/files/transform-pim-psm', {
    path,
  });
  return response.data;
};

export default api;