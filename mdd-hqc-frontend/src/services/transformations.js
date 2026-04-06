/**
 * Transformation services used by the frontend to run backend model conversions.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Axios client used by frontend requests that trigger backend transformations.
 */
export const transformationsApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Requests the backend CIM-to-PIM transformation for the uploaded file path.
 *
 * This service is used by the main application flow so transformation requests stay out
 * of the UI components and remain reusable from one request layer.
 */
export const transformCimToPim = async (path, options = {}) => {
  const response = await transformationsApi.post('/transformations/cim-to-pim', {
    path,
  }, {
    signal: options.signal,
  });
  return response.data;
};

/**
 * Requests the backend PIM-to-PSM transformation for the uploaded file path.
 *
 * This service is used by the filter and application flow when the frontend needs the
 * generated PlantUML artifact and the related transformation metrics.
 */
export const transformPimToPsm = async (path, options = {}) => {
  const response = await transformationsApi.post('/transformations/pim-to-psm', {
    path,
  }, {
    signal: options.signal,
  });
  return response.data;
};
