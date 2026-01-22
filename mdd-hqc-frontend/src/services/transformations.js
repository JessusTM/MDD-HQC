import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const transformationsApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const transformCimToPim = async (path) => {
  const response = await transformationsApi.post('/transformations/cim-to-pim', {
    path,
  });
  return response.data;
};

export const transformPimToPsm = async (path) => {
  const response = await transformationsApi.post('/transformations/pim-to-psm', {
    path,
  });
  return response.data;
};
