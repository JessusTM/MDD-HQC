/**
 * Interaction services used by the frontend guided-question flow.
 */

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const API_BASE = `${API_BASE_URL}/interactions`;

/**
 * Requests the guided questions generated for the current uploaded model path.
 *
 * This service is used by the main application flow before the CIM-to-PIM step when the
 * AI-assisted interaction mode needs clarification questions from the backend.
 */
export const fetchQuestions = async (path, options = {}) => {
    try {
        const response = await axios.post(`${API_BASE}/report`, { path }, { signal: options.signal });
        return response.data.questions || [];
    } catch (error) {
        console.error("Error fetching questions:", error);
        throw error;
    }
};

/**
 * Sends the user answers collected during the guided interaction flow.
 *
 * This service exists so question-answer submission can stay reusable and separate from
 * the modal components that collect the answers.
 */
export const sendAnswers = async (answers) => {
  try {
    const response = await axios.post(`${API_BASE}/answers`, { answers });
    return response.data;
  } catch (error) {
    console.error("Error sending answers:", error);
    throw error;
  }
};

/**
 * Confirms the current UVL artifact after the interaction step is completed.
 *
 * This service supports flows that need the backend to persist or acknowledge the
 * validated UVL state outside the UI layer.
 */
export const confirmUvl = async (path) => {
  try {
    const response = await axios.post(`${API_BASE}/confirm`, { path });
    return response.data;
  } catch (error) {
    console.error("Error confirming UVL:", error);
    throw error;
  }
};
