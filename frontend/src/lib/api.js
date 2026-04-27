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

// arXiv API endpoints
export const arxivAPI = {
  search: (params) => api.get('/api/arxiv/search', { params }),
  categories: () => api.get('/api/arxiv/categories'),
  latest: (params) => api.get('/api/arxiv/latest', { params }),
  getPaper: (arxivId) => api.get(`/api/arxiv/paper/${arxivId}`),
  summarize: (data) => api.post('/api/arxiv/summarize', data),
  save: (data) => api.post('/api/arxiv/save', data),
  unsave: (arxivId) => api.delete(`/api/arxiv/save/${arxivId}`),
  readingList: () => api.get('/api/arxiv/reading-list'),
};

// Multi-source discover API
export const discoverAPI = {
  search: (params) => api.get('/api/discover/search', { params }),
  compare: (papers) => api.post('/api/discover/compare', { papers }),
  trends: (params) => api.get('/api/discover/trends', { params }),
  // Workspaces
  listWorkspaces: () => api.get('/api/discover/workspaces'),
  createWorkspace: (data) => api.post('/api/discover/workspaces', data),
  getWorkspace: (id) => api.get(`/api/discover/workspaces/${id}`),
  updateWorkspace: (id, data) => api.put(`/api/discover/workspaces/${id}`, data),
  deleteWorkspace: (id) => api.delete(`/api/discover/workspaces/${id}`),
  addPaper: (wsId, data) => api.post(`/api/discover/workspaces/${wsId}/papers`, data),
  removePaper: (wsId, paperId) => api.delete(`/api/discover/workspaces/${wsId}/papers/${paperId}`),
  annotatePaper: (wsId, paperId, data) => api.put(`/api/discover/workspaces/${wsId}/papers/${paperId}/annotate`, data),
  exportPapers: (data) => api.post('/api/discover/export', data),
};

export default api;
