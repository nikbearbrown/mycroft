import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000,
})

/**
 * Fetch contract awards from the backend.
 * @param {string} keyword  - Search keyword (e.g. "artificial intelligence")
 * @param {number} limit    - Max number of results (default 100)
 */
export const fetchAwards = (keyword = 'artificial intelligence', limit = 100) =>
  api.get('/api/awards/fetch', { params: { keyword, limit } })

export const fetchMockAwards = () =>
  api.get('/api/awards/mock')

/**
 * Health check endpoint.
 */
export const getHealth = () => api.get('/health')

export default api
