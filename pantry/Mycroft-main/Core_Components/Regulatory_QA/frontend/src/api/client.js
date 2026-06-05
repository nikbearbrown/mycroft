import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const feedsAPI = {
  // List feeds with filters
  listFeeds: async (params = {}) => {
    const response = await api.get('/api/feeds/list', { params });
    return response.data;
  },

  // Get single feed
  getFeed: async (id) => {
    const response = await api.get(`/api/feeds/${id}`);
    return response.data;
  },

  // Get recent feeds
  getRecent: async (days = 7, limit = 20) => {
    const response = await api.get('/api/feeds/recent', {
      params: { days, limit }
    });
    return response.data;
  },

  // Get stats
  getStats: async () => {
    const response = await api.get('/api/feeds/stats');
    return response.data;
  },

  // Trigger feed fetch
  triggerFetch: async () => {
    const response = await api.post('/api/feeds/fetch');
    return response.data;
  },
};

export const chatAPI = {
  // Ask question
  ask: async (question, feedIds) => {
    const response = await api.post('/api/chat', {
      question,
      feed_ids: feedIds,
    });
    return response.data;
  },
};

export default api;