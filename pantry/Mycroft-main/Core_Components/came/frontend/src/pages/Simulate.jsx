import { useState } from 'react'
import { api } from '../api/client'
import AllocationBar from '../components/charts/AllocationBar'

const EVENT_TYPES = ['INVESTMENT', 'DIVESTMENT', 'CASH_ALLOCATION', 'HOLD_DECISION', 'INACTION_MARKER']
const ASSET_CLASSES = ['equities', 'bonds', 'cash', 'crypto', 'real_estate', 'commodities', 'money_market', 'alternatives']

const emptyEvent = () => ({
  event_type: 'INVESTMENT',
  asset_class: 'equities',
  ticker: '',
  amount: '',
  timestamp: new Date().toISOString().slice(0, 16),
})

export default function SimulatePage() {
  const [proposed, setProposed] = useState([emptyEvent()])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const addRow = () => setProposed([...proposed, emptyEvent()])
  const removeRow = (i) => setProposed(proposed.filter((_, idx) => idx !== i))
  const updateRow = (i, field, val) =>
    setProposed(proposed.map((r, idx) => (idx === i ? { ...r, [field]: val } : r)))

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const payload = {
        proposed_events: proposed.map((e) => ({
          ...e,
          amount: parseFloat(e.amount) || 0,
          timestamp: new Date(e.timestamp).toISOString(),
          ticker: e.ticker || null,
        })),
        horizon_days: 30,
      }
      const res = await api.simulate(payload)
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const RISK_COLOR = {
    aggressive: 'text-red', 'moderate-aggressive': 'text-amber',
    moderate: 'text-accent', conservative: 'text-green',
  }

  return (
    <div className="p-6 space-y-5 max-w-4xl">
      <h1 className="text-lg font-semibold text-text">Simulate Allocation</h1>
      <p className="text-sm text-muted">
        Propose hypothetical events and preview their effect on your strategy profile before committing.
      </p>

      {/* Proposed events */}
      <div className="card space-y-3">
        <div className="metric-label">proposed events</div>
        {proposed.map((row, i) => (
          <div key={i} className="grid grid-cols-5 gap-2 items-end">
            <select
              className="bg-bg border border-border text-text text-xs px-2 py-1.5 rounded font-mono"
              value={row.event_type}
              onChange={(e) => updateRow(i, 'event_type', e.target.value)}
            >
              {EVENT_TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
            <select
              className="bg-bg border border-border text-text text-xs px-2 py-1.5 rounded font-mono"
              value={row.asset_class}
              onChange={(e) => updateRow(i, 'asset_class', e.target.value)}
            >
              {ASSET_CLASSES.map((a) => <option key={a}>{a}</option>)}
            </select>
            <input
              type="number"
              placeholder="Amount"
              className="bg-bg border border-border text-text text-xs px-2 py-1.5 rounded font-mono"
              value={row.amount}
              onChange={(e) => updateRow(i, 'amount', e.target.value)}
            />
            <input
              type="datetime-local"
              className="bg-bg border border-border text-text text-xs px-2 py-1.5 rounded font-mono"
              value={row.timestamp}
              onChange={(e) => updateRow(i, 'timestamp', e.target.value)}
            />
            <button
              onClick={() => removeRow(i)}
              className="text-muted hover:text-red text-xs text-right"
            >
              ✕
            </button>
          </div>
        ))}
        <div className="flex gap-2 pt-1">
          <button onClick={addRow} className="btn-ghost text-xs">+ Add Row</button>
          <button onClick={handleSimulate} disabled={loading} className="btn-primary text-xs disabled:opacity-40">
            {loading ? 'Simulating...' : '⟳ Run Simulation'}
          </button>
        </div>
      </div>

      {error && <div className="text-red text-sm border border-red/20 bg-red/5 px-3 py-2 rounded">{error}</div>}

      {result && (
        <>
          <div className="grid grid-cols-3 gap-3">
            <div className="card">
              <div className="metric-label">projected risk posture</div>
              <div className={`metric-value ${RISK_COLOR[result.projected_risk_posture] || 'text-text'}`}>
                {result.projected_risk_posture}
              </div>
            </div>
            <div className="card">
              <div className="metric-label">projected HHI</div>
              <div className="metric-value">{result.projected_hhi.toFixed(4)}</div>
            </div>
            <div className="card">
              <div className="metric-label">projected entropy</div>
              <div className="metric-value">{result.projected_entropy.toFixed(4)}</div>
            </div>
          </div>

          <div className="card">
            <div className="metric-label mb-2">simulation narrative</div>
            <p className="text-sm text-text">{result.narrative}</p>
          </div>

          <div className="card">
            <div className="metric-label mb-3">projected allocation</div>
            <AllocationBar weights={result.projected_weights} />
          </div>
        </>
      )}
    </div>
  )
}