import { useEffect } from 'react'
import { useStore } from '../store'
import MetricCard from '../components/MetricCard'
import MetricsLineChart from '../components/charts/MetricsLine'

export default function MetricsPage() {
  const { metrics, strategy, loading, fetchMetrics, fetchStrategy } = useStore()

  useEffect(() => {
    fetchMetrics()
    fetchStrategy()
  }, [])

  const latest = metrics[0]
  const m = strategy?.metrics_snapshot || {}

  return (
    <div className="p-6 space-y-5 max-w-5xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text">Behavioral Metrics</h1>
        <button onClick={fetchMetrics} className="btn-ghost text-xs">⟳ Refresh</button>
      </div>

      {/* Current snapshot */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="HHI"
          value={m.hhi?.toFixed(4) ?? '—'}
          sub="Herfindahl-Hirschman Index"
        />
        <MetricCard
          label="Entropy"
          value={m.entropy?.toFixed(4) ?? '—'}
          sub="Shannon entropy (nats)"
        />
        <MetricCard
          label="Turnover Rate"
          value={m.turnover_rate != null ? (m.turnover_rate * 100).toFixed(1) + '%' : '—'}
          sub="reallocation / AUM"
        />
        <MetricCard
          label="Idle Capital"
          value={m.idle_capital_ratio != null ? (m.idle_capital_ratio * 100).toFixed(1) + '%' : '—'}
          sub="cash / total capital"
        />
      </div>

      {/* History chart */}
      <div className="card space-y-3">
        <div className="metric-label">metric history across pipeline runs</div>
        {loading.metrics ? (
          <div className="text-muted text-sm py-6 text-center">Loading...</div>
        ) : (
          <MetricsLineChart data={metrics} />
        )}
      </div>

      {/* Table */}
      {metrics.length > 0 && (
        <div className="card overflow-x-auto">
          <div className="metric-label mb-3">run log</div>
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-muted border-b border-border">
                <th className="text-left pb-2 pr-4">window</th>
                <th className="text-right pb-2 pr-4">HHI</th>
                <th className="text-right pb-2 pr-4">Entropy</th>
                <th className="text-right pb-2 pr-4">Turnover</th>
                <th className="text-right pb-2 pr-4">Idle</th>
                <th className="text-left pb-2">Dominant Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {metrics.map((m) => (
                <tr key={m.id} className="text-text-dim hover:text-text">
                  <td className="py-1.5 pr-4">
                    {new Date(m.window_end).toLocaleDateString()}
                  </td>
                  <td className="py-1.5 pr-4 text-right">{m.hhi?.toFixed(4)}</td>
                  <td className="py-1.5 pr-4 text-right">{m.entropy?.toFixed(4)}</td>
                  <td className="py-1.5 pr-4 text-right">
                    {m.turnover_rate ? (m.turnover_rate * 100).toFixed(1) + '%' : '—'}
                  </td>
                  <td className="py-1.5 pr-4 text-right">
                    {m.idle_capital_ratio ? (m.idle_capital_ratio * 100).toFixed(1) + '%' : '—'}
                  </td>
                  <td className="py-1.5">{m.dominant_action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}