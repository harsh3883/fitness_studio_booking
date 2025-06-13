// utils/api.js - API Helper with Authentication
export const API_BASE_URL = "http://localhost:8002";

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Generic API request function
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: getAuthHeaders(),
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
};

// API methods
export const api = {
  // GET request
  get: (endpoint) => apiRequest(endpoint),
  
  // POST request
  post: (endpoint, data) => apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // PUT request
  put: (endpoint, data) => apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  // DELETE request
  delete: (endpoint) => apiRequest(endpoint, {
    method: 'DELETE',
  }),
};

// Specific API calls for your app
export const classesAPI = {
  getAll: () => api.get('/api/classes/'),
  getById: (id) => api.get(`/api/classes/${id}/`),
  create: (classData) => api.post('/api/classes/', classData),
  update: (id, classData) => api.put(`/api/classes/${id}/`, classData),
  delete: (id) => api.delete(`/api/classes/${id}/`),
};

export const bookingsAPI = {
  getAll: () => api.get('/api/bookings/'),
  create: (bookingData) => api.post('/api/bookings/', bookingData),
  cancel: (id) => api.delete(`/api/bookings/${id}/`),
};

export default api;