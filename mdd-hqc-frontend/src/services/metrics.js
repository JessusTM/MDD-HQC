/**
 * Metrics services used by the frontend to request CIM summaries from the backend.
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

/**
 * Axios client used by metric requests triggered from the frontend flow.
 */
export const metricsApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Requests the backend CIM metrics for the uploaded XML file path.
 *
 * This service is used by the CIM component after upload so the metrics request stays
 * isolated from the UI state management logic.
 */
export const getCimMetrics = async (path, options = {}) => {
  const response = await metricsApi.post('/metrics/cim', { path }, {
    signal: options.signal,
  });
  return response.data;
};
