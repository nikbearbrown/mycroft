import { useEffect } from 'react'
import { useStore } from '../store'
import clsx from 'clsx'

function DeltaBar({ value }) {
  const pct = Math.abs(value) * 100
  const positive = value >= 0
  return (
    <div className="flex items-center gap-2">
      <div className="w-32 h-1.5 bg-border rounded overflow-hidden">
        <div
          className={clsx('h-full rounded', positive ? 'bg-green' : 'bg-red')}
          style={{ width: `${Math.min(100, pct * 4)}%` }}
        />
      </div>
      <span className={clsx('text-xs font-mono', positive ? 'text-green' : 'text-red')}>
        {positive ? '+' : ''}{(value * 100).toFixed(1)}%
      </span>
    </div>
  )
}

export default function DriftPage() {
  const { drift, loading, fetchDrift } = useStore()

  useEffect(() => { fetchDrift() }, [])

  const scoreColor =
    !drift ? '' :
    drift.drift_score > 0.25 ? 'text-red' :
    drift.drift_score > 0.1 ? 'text-amber' : 'text-green'

  return (
    <div className="p-6 space-y-5 max-w-4xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text">Drift Monitor</h1>
        <button onClick={fetchDrift} className="btn-ghost text-xs">⟳ Refresh</button>
      </div>

      {!drift && !loading.drift && (
        <div className="card text-muted text-sm">
          Run the pipeline at least twice to detect drift.
        </div>
      )}

      {drift && (
        <>
          <div className="grid grid-cols-3 gap-3">
            <div className="card">
              <div className="metric-label">drift score</div>
              <div className={clsx('metric-value', scoreColor)}>
                {drift.drift_score.toFixed(4)}
              </div>
              <div className="text-xs text-muted mt-1">
                {drift.drift_score > 0.25 ? 'significant' : drift.drift_score > 0.1 ? 'minor' : 'stable'}
              </div>
            </div>
            <div className="card">
              <div className="metric-label">dominant shift</div>
              <div className="metric-value text-accent">{drift.dominant_shift || '—'}</div>
            </div>
            <div className="card">
              <div className="metric-label">baseline available</div>
              <div className={clsx('metric-value', drift.has_baseline ? 'text-green' : 'text-muted')}>
                {drift.has_baseline ? 'yes' : 'no'}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="metric-label mb-2">narrative</div>
            <p className="text-sm text-text">{drift.drift_narrative}</p>
          </div>

          {Object.keys(drift.weight_deltas).length > 0 && (
            <div className="card space-y-3">
              <div className="metric-label">weight deltas vs baseline</div>
              <div className="space-y-2">
                {Object.entries(drift.weight_deltas)
                  .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                  .map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between gap-4">
                      <span className="text-sm text-muted w-28 truncate">{k}</span>
                      <DeltaBar value={v} />
                    </div>
                  ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="card space-y-2">
              <div className="metric-label">current weights</div>
              {Object.entries(drift.current_weights)
                .sort((a, b) => b[1] - a[1])
                .map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm">
                    <span className="text-muted">{k}</span>
                    <span className="text-text font-mono">{(v * 100).toFixed(1)}%</span>
                  </div>
                ))}
            </div>
            <div className="card space-y-2">
              <div className="metric-label">baseline weights</div>
              {Object.keys(drift.baseline_weights).length === 0 ? (
                <div className="text-muted text-sm">No baseline yet</div>
              ) : (
                Object.entries(drift.baseline_weights)
                  .sort((a, b) => b[1] - a[1])
                  .map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm">
                      <span className="text-muted">{k}</span>
                      <span className="text-text font-mono">{(v * 100).toFixed(1)}%</span>
                    </div>
                  ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}