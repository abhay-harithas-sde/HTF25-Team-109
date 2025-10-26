// API utility functions for FoodVision AI

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Use relative URLs in production (same domain)
  : 'http://localhost:5000'; // Use localhost in development

// Helper function to make API requests
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add authorization header if token exists
  const token = localStorage.getItem('token');
  if (token) {
    defaultOptions.headers.Authorization = `Bearer ${token}`;
  }

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    console.log(`Making API request to: ${url}`, config);
    const response = await fetch(url, config);
    const data = await response.json();
    
    console.log(`API response from ${endpoint}:`, { status: response.status, data });
    
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    
    return { success: true, data, status: response.status };
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    return { 
      success: false, 
      error: error.message || 'Network error occurred',
      status: error.status || 500
    };
  }
};

// Authentication API functions
export const authAPI = {
  login: async (credentials) => {
    return apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  signup: async (userData) => {
    return apiRequest('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  verifyToken: async (token) => {
    return apiRequest('/api/auth/verify-token', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  getProfile: async () => {
    return apiRequest('/api/auth/profile');
  },

  updateProfile: async (profileData) => {
    return apiRequest('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },
};

// Health check function
export const healthCheck = async () => {
  return apiRequest('/api/health');
};

export default apiRequest;