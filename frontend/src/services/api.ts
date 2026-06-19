import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export const auth = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, password: string, role: string, full_name: string) =>
    api.post('/auth/register', { email, password, role, full_name }),
};

export const predictions = {
  success: (data: Record<string, unknown>) =>
    api.post('/predict/success', data),
  growth: (data: Record<string, unknown>) =>
    api.post('/predict/growth', data),
  risk: (data: Record<string, unknown>) =>
    api.post('/predict/risk', data),
};

export const startups = {
  create: (data: Record<string, unknown>) =>
    api.post('/startup', data),
  get: (id: number) =>
    api.get(`/startup/${id}`),
};

export const reports = {
  generate: (startup_id: number) =>
    api.post('/report/generate', { startup_id }),
};

export const health = () => api.get('/health');

export default api;
