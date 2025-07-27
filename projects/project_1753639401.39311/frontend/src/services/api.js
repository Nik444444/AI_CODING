import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Создать экземпляр axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцепторы для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API методы
export const api = {
  // Health check
  healthCheck: () => apiClient.get('/health'),
  
  // Items CRUD
  getItems: () => apiClient.get('/items'),
  createItem: (data) => apiClient.post('/items', data),
  getItem: (id) => apiClient.get(`/items/${id}`),
  deleteItem: (id) => apiClient.delete(`/items/${id}`),
  
  // Root endpoint
  getRoot: () => apiClient.get('/'),
};

export default api;
