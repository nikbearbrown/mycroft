import { useEffect } from 'react'
import { useStore } from '../store'
import MetricCard from '../components/MetricCard'
import AllocationBar from '../components/charts/AllocationBar'

const RISK_COLOR = {
  aggressive: 'text-red',
  'moderate-aggressive': 'text-amber',
  moderate: 'text-accent',
  conservative: 'text-green',
}

export default function StrategyPage() {
  const { strategy, loading, errors, fetchStrategy, computeStrategy } = useStore()

  useEffect(() => { fetchStrategy() }, [])

  const handleCompute = async () => {
    try { await computeStrategy() }
    catch (e) { /* error shown via store */ }
  }

  const m = strategy?.metrics_snapshot || {}

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-text">Strategy Profile</h1>
          {strategy && (
            <div className="text-xs text-muted mt-0.5">
              v{strategy.version} · computed {new Date(strategy.computed_at).toLocaleString()}
            </div>
          )}
        </div>
        <button
          onClick={handleCompute}
          disabled={loading.compute}
          className="btn-primary disabled:opacity-40"
        >
          {loading.compute ? 'Computing...' : '⟳ Run Pipeline'}
        </button>
      </div>

      {errors.compute && (
        <div className="text-red text-sm border border-red/20 bg-red/5 px-3 py-2 rounded">
          {errors.compute}
        </div>
      )}

      {!strategy && !loading.strategy && (
        <div className="card text-muted text-sm">
          No strategy computed yet. Ingest events then click <strong className="text-text">Run Pipeline</strong>.
        </div>
      )}

      {strategy && (
        <>
          {/* Core metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard
              label="Risk Posture"
              value={strategy.risk_posture}
              color={RISK_COLOR[strategy.risk_posture]}
            />
            <MetricCard
              label="Liquidity Pref."
              value={strategy.liquidity_preference}
            />
            <MetricCard
              label="Concentration"
              value={strategy.concentration_tendency}
            />
            <MetricCard
              label="Drift Score"
              value={m.drift_score != null ? m.drift_score.toFixed(3) : '—'}
              sub={m.drift_score > 0.25 ? 'significant' : m.drift_score > 0.1 ? 'minor' : 'stable'}
              color={m.drift_score > 0.25 ? 'text-red' : m.drift_score > 0.1 ? 'text-amber' : 'text-green'}
            />
          </div>

          {/* Quantitative metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard label="HHI" value={m.hhi?.toFixed(4)} sub="1.0 = fully concentrated" />
            <MetricCard label="Entropy" value={m.entropy?.toFixed(4)} sub="higher = more diverse" />
            <MetricCard label="Turnover Rate" value={m.turnover_rate ? (m.turnover_rate * 100).toFixed(1) + '%' : '—'} />
            <MetricCard label="Idle Capital" value={m.idle_capital_ratio ? (m.idle_capital_ratio * 100).toFixed(1) + '%' : '—'} />
          </div>

          {/* Narrative */}
          <div className="card space-y-2">
            <div className="metric-label">inferred strategy narrative</div>
            <p className="text-sm text-text leading-relaxed">{strategy.profile_text}</p>
          </div>

          {/* Allocation chart */}
          <div className="card space-y-3">
            <div className="metric-label">allocation weights</div>
            <AllocationBar weights={strategy.baseline_weights} />
          </div>
        </>
      )}
    </div>
  )
}