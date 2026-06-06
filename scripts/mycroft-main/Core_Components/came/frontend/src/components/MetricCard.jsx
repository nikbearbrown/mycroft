import clsx from 'clsx'

export default function MetricCard({ label, value, sub, color }) {
  return (
    <div className="card flex flex-col gap-1">
      <div className="metric-label">{label}</div>
      <div className={clsx('metric-value', color || 'text-text')}>{value ?? '—'}</div>
      {sub && <div className="text-xs text-muted">{sub}</div>}
    </div>
  )
}