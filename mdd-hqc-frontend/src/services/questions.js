import axios from "axios";

const API_BASE = "http://localhost:8000/interactions";

export const fetchQuestions = async (path, options = {}) => {
    try {
        const response = await axios.post(`${API_BASE}/report`, { path }, { signal: options.signal });
        return response.data.questions || [];
    } catch (error) {
        console.error("Error fetching questions:", error);
        throw error;
    }
};

export const sendAnswers = async (answers) => {
  try {
    const response = await axios.post(`${API_BASE}/answers`, { answers });
    return response.data;
  } catch (error) {
    console.error("Error sending answers:", error);
    throw error;
  }
};

export const confirmUvl = async (path) => {
  try {
    const response = await axios.post(`${API_BASE}/confirm`, { path });
    return response.data;
  } catch (error) {
    console.error("Error confirming UVL:", error);
    throw error;
  }
};
