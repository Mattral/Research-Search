import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/auth/me', data),
  changePassword: (data) => api.post('/api/auth/change-password', data),
};

// User endpoints
export const userAPI = {
  getInterests: () => api.get('/api/users/interests'),
  updateInterests: (interest_ids) => api.post('/api/users/interests', { interest_ids }),
  getMyInterests: () => api.get('/api/users/me/interests'),
};

// Paper endpoints
export const paperAPI = {
  search: (params) => api.get('/api/papers/search', { params }),
  browse: (limit = 50) => api.get('/api/papers/browse', { params: { limit } }),
  getById: (paperId) => api.get(`/api/papers/${encodeURIComponent(paperId)}`),
  viewPaper: (paperId) => api.post(`/api/papers/${encodeURIComponent(paperId)}/view`),
  likePaper: (paperId) => api.post(`/api/papers/${encodeURIComponent(paperId)}/like`),
  unlikePaper: (paperId) => api.delete(`/api/papers/${encodeURIComponent(paperId)}/like`),
  getRecommendations: (limit = 10) => api.get('/api/papers/recommendations', { params: { limit } }),
  getFavorites: () => api.get('/api/papers/me/favorites'),
  getRecentViews: () => api.get('/api/papers/me/recent-views'),
};

export default api;
