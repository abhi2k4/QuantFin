import axios from 'axios';

// Get API URL from environment variables
// For development: uses localhost:8000
// For production: uses the Vercel environment variable VITE_API_URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('API Base URL:', API_BASE_URL);

// Create axios instance with base URL
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include credentials for CORS requests
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      console.error('Unauthorized - please login');
    } else if (error.response?.status === 403) {
      console.error('Forbidden - access denied');
    } else if (error.response?.status === 404) {
      console.error('Not found');
    } else if (error.response?.status === 500) {
      console.error('Server error');
    } else if (error.code === 'ERR_NETWORK') {
      console.error('Network error - backend may be unavailable');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
