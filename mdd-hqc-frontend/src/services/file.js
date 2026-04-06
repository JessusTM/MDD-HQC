/**
 * File upload services used by the frontend to persist CIM XML artifacts.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Axios client used by upload-related requests from the CIM panel.
 */
export const fileApi = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Uploads the selected XML file to the backend and returns the saved file metadata.
 *
 * This service is used by the CIM component so file persistence stays outside the UI
 * component and can be reused from one request layer.
 */
export const uploadFile = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fileApi.post('/files/upload', formData, {
    signal: options.signal,
  });
  return response.data;
};
