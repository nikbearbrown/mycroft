import { create } from 'zustand'
import { api } from '../api/client'

export const useStore = create((set, get) => ({
  // State
  events: [],
  strategy: null,
  drift: null,
  capitalFlow: null,
  metrics: [],
  loading: {},
  errors: {},

  setLoading: (key, val) => set((s) => ({ loading: { ...s.loading, [key]: val } })),
  setError: (key, val) => set((s) => ({ errors: { ...s.errors, [key]: val } })),

  fetchEvents: async () => {
    get().setLoading('events', true)
    try {
      const events = await api.listEvents()
      set({ events })
    } catch (e) {
      get().setError('events', e.message)
    } finally {
      get().setLoading('events', false)
    }
  },

  fetchStrategy: async () => {
    get().setLoading('strategy', true)
    try {
      const strategy = await api.getCurrentStrategy()
      set({ strategy })
    } catch (e) {
      // 404 is expected if not computed yet
      if (!e.message.includes('404')) get().setError('strategy', e.message)
    } finally {
      get().setLoading('strategy', false)
    }
  },

  computeStrategy: async () => {
    get().setLoading('compute', true)
    get().setError('compute', null)
    try {
      const strategy = await api.computeStrategy()
      set({ strategy })
      // Refresh drift after compute
      get().fetchDrift()
      return strategy
    } catch (e) {
      get().setError('compute', e.message)
      throw e
    } finally {
      get().setLoading('compute', false)
    }
  },

  fetchDrift: async () => {
    get().setLoading('drift', true)
    try {
      const drift = await api.getDrift()
      set({ drift })
    } catch (e) {
      if (!e.message.includes('404')) get().setError('drift', e.message)
    } finally {
      get().setLoading('drift', false)
    }
  },

  fetchCapitalFlow: async () => {
    get().setLoading('flow', true)
    try {
      const capitalFlow = await api.getCapitalFlow()
      set({ capitalFlow })
    } catch (e) {
      get().setError('flow', e.message)
    } finally {
      get().setLoading('flow', false)
    }
  },

  fetchMetrics: async () => {
    get().setLoading('metrics', true)
    try {
      const metrics = await api.getMetrics()
      set({ metrics })
    } catch (e) {
      get().setError('metrics', e.message)
    } finally {
      get().setLoading('metrics', false)
    }
  },

  ingestEvent: async (payload) => {
    const event = await api.ingestEvent(payload)
    set((s) => ({ events: [event, ...s.events] }))
    return event
  },

  deleteEvent: async (id) => {
    await api.deleteEvent(id)
    set((s) => ({ events: s.events.filter((e) => e.id !== id) }))
  },
}))