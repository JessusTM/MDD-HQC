import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const fileApi = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadFile = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fileApi.post('/files/upload', formData, {
    signal: options.signal,
  });
  return response.data;
};
