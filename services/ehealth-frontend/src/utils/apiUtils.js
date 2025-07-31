import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Utility to check if the backend API is available
 * @returns {Promise<boolean>} True if the API is available, false otherwise
 */
export const checkApiAvailability = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/v1/health`, { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.error('API availability check failed:', error);
    return false;
  }
};

export default {
  checkApiAvailability
};