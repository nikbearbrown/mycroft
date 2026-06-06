const BASE = '/api'

async function req(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Events
  ingestEvent: (payload) => req('POST', '/event', payload),
  listEvents: (limit = 200) => req('GET', `/event?limit=${limit}`),
  deleteEvent: (id) => req('DELETE', `/event/${id}`),

  // Strategy
  computeStrategy: () => req('POST', '/strategy/compute'),
  getCurrentStrategy: () => req('GET', '/strategy/current'),
  getStrategyHistory: () => req('GET', '/strategy/history'),
  getDrift: () => req('GET', '/strategy/drift'),

  // Capital
  getCapitalFlow: () => req('GET', '/capital-flow'),
  simulate: (payload) => req('POST', '/simulate-allocation', payload),

  // Metrics
  getMetrics: (limit = 50) => req('GET', `/metrics?limit=${limit}`),
}