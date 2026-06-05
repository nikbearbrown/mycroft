function Stat({ label, value, sub, highlight }) {
  const color = highlight === 'green' ? 'text-green'
    : highlight === 'red' ? 'text-red'
    : highlight === 'amber' ? 'text-amber'
    : 'text-primary'

  return (
    <div className="bg-surface border border-border rounded-xl p-4">
      <div className="text-dim text-xs mb-1">{label}</div>
      <div className={`text-xl font-mono font-medium ${color}`}>{value}</div>
      {sub && <div className="text-dim text-xs mt-0.5">{sub}</div>}
    </div>
  )
}

function fmt(n) {
  if (n == null) return '—'
  if (Math.abs(n) >= 1000) return `$${(n / 1000).toFixed(1)}k`
  return `$${n.toFixed(0)}`
}

export default function MetricsGrid({ stats, edgeProfile }) {
  const pnl   = stats.total_realized_pnl
  const alpha = edgeProfile?.edge_profile?.estimated_alpha

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <Stat
        label="Total P&L"
        value={fmt(pnl)}
        highlight={pnl >= 0 ? 'green' : 'red'}
      />
      <Stat
        label="Win rate"
        value={`${stats.win_rate}%`}
        highlight={stats.win_rate >= 55 ? 'green' : stats.win_rate >= 45 ? 'amber' : 'red'}
      />
      <Stat
        label="Avg hold"
        value={`${stats.avg_hold_days}d`}
      />
      <Stat
        label="Trades analyzed"
        value={stats.total_trades}
        sub={`${stats.unique_tickers} tickers`}
      />
      <Stat
        label="Closed positions"
        value={stats.total_sells}
      />
      <Stat
        label="Overall edge score"
        value={edgeProfile?.overall_edge_score != null
          ? (edgeProfile.overall_edge_score >= 0 ? '+' : '') + edgeProfile.overall_edge_score.toFixed(2)
          : '—'}
        highlight={
          edgeProfile?.overall_edge_score >= 0.2 ? 'green'
          : edgeProfile?.overall_edge_score >= 0 ? 'amber'
          : 'red'
        }
        sub="−1 noise → +1 edge"
      />
    </div>
  )
}