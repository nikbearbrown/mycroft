import { useEffect, useState } from 'react'
import { useStore } from '../store'
import { format } from 'date-fns'

const EVENT_TYPES = ['INVESTMENT', 'DIVESTMENT', 'CASH_ALLOCATION', 'HOLD_DECISION', 'INACTION_MARKER']
const ASSET_CLASSES = ['equities', 'bonds', 'cash', 'crypto', 'real_estate', 'commodities', 'money_market', 'alternatives']

const TYPE_COLOR = {
  INVESTMENT: 'text-green',
  DIVESTMENT: 'text-red',
  CASH_ALLOCATION: 'text-accent',
  HOLD_DECISION: 'text-amber',
  INACTION_MARKER: 'text-muted',
}

const defaultForm = {
  event_type: 'INVESTMENT',
  asset_class: 'equities',
  ticker: '',
  amount: '',
  timestamp: new Date().toISOString().slice(0, 16),
  notes: '',
}

export default function EventsPage() {
  const { events, loading, fetchEvents, ingestEvent, deleteEvent } = useStore()
  const [form, setForm] = useState(defaultForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => { fetchEvents() }, [])

  const handleSubmit = async () => {
    if (!form.amount || isNaN(parseFloat(form.amount))) {
      setError('Amount is required and must be a number.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await ingestEvent({
        ...form,
        amount: parseFloat(form.amount),
        timestamp: new Date(form.timestamp).toISOString(),
        ticker: form.ticker || null,
      })
      setForm(defaultForm)
      setShowForm(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="p-6 space-y-5 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-text">Event Timeline</h1>
          <div className="text-xs text-muted mt-0.5">{events.length} events</div>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-xs">
          {showForm ? '✕ Cancel' : '+ New Event'}
        </button>
      </div>

      {/* Ingest form */}
      {showForm && (
        <div className="card space-y-3">
          <div className="metric-label">ingest event</div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted block mb-1">Event Type</label>
              <select
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                value={form.event_type}
                onChange={(e) => setForm({ ...form, event_type: e.target.value })}
              >
                {EVENT_TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Asset Class</label>
              <select
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                value={form.asset_class}
                onChange={(e) => setForm({ ...form, asset_class: e.target.value })}
              >
                {ASSET_CLASSES.map((a) => <option key={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Amount (USD)</label>
              <input
                type="number"
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                placeholder="10000"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
              />
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Ticker (optional)</label>
              <input
                type="text"
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                placeholder="AAPL"
                value={form.ticker}
                onChange={(e) => setForm({ ...form, ticker: e.target.value.toUpperCase() })}
              />
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Timestamp</label>
              <input
                type="datetime-local"
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                value={form.timestamp}
                onChange={(e) => setForm({ ...form, timestamp: e.target.value })}
              />
            </div>
            <div>
              <label className="text-xs text-muted block mb-1">Notes (optional)</label>
              <input
                type="text"
                className="w-full bg-bg border border-border text-text text-sm px-2 py-1.5 rounded font-mono"
                placeholder="e.g. rebalancing quarterly"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
            </div>
          </div>

          {error && <div className="text-red text-xs">{error}</div>}

          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="btn-primary disabled:opacity-40"
          >
            {submitting ? 'Ingesting...' : 'Ingest Event'}
          </button>
        </div>
      )}

      {/* Timeline */}
      {loading.events ? (
        <div className="text-muted text-sm">Loading...</div>
      ) : events.length === 0 ? (
        <div className="card text-muted text-sm">No events yet.</div>
      ) : (
        <div className="space-y-2">
          {events.map((e) => (
            <div key={e.id} className="card flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className={`text-xs font-mono pt-0.5 w-28 shrink-0 ${TYPE_COLOR[e.event_type] || 'text-muted'}`}>
                  {e.event_type}
                </div>
                <div>
                  <div className="text-sm text-text">
                    <span className="font-semibold">{e.asset_class}</span>
                    {e.ticker && <span className="text-accent ml-2">{e.ticker}</span>}
                    <span className="text-muted ml-2">${e.amount.toLocaleString()}</span>
                  </div>
                  <div className="text-xs text-muted mt-0.5">
                    {format(new Date(e.timestamp), 'MMM d, yyyy HH:mm')}
                    {e.notes && <span className="ml-2 text-text-dim">· {e.notes}</span>}
                  </div>
                </div>
              </div>
              <button
                onClick={() => deleteEvent(e.id)}
                className="text-muted hover:text-red text-xs shrink-0"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}