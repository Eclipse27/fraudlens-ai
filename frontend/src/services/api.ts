import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getModelInfo = async () => {
  const response = await api.get('/model-info');
  return response.data;
};

export const analyzeClaim = async (data: any) => {
  const response = await api.post('/analyze-claim', data);
  return response.data;
};

export const analyzeProvider = async (data: any) => {
  const response = await api.post('/analyze-provider', data);
  return response.data;
};

export const analyzeAnomaly = async (data: any) => {
  const response = await api.post('/analyze-anomaly', data);
  return response.data;
};

export default api;
