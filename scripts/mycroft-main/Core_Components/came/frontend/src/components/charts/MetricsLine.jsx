import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-border px-3 py-2 text-xs font-mono space-y-1">
      <div className="text-muted">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(3) : p.value}
        </div>
      ))}
    </div>
  )
}

export default function MetricsLineChart({ data }) {
  if (!data?.length) return (
    <div className="flex items-center justify-center h-40 text-muted text-sm">
      No metric history yet.
    </div>
  )

  const chartData = [...data].reverse().map((m) => ({
    date: format(new Date(m.window_end), 'MM/dd'),
    HHI: m.hhi,
    Entropy: m.entropy,
    Turnover: m.turnover_rate,
    'Idle Ratio': m.idle_capital_ratio,
  }))

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
        <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }} />
        <YAxis tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }} width={38} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 10, fontFamily: 'JetBrains Mono', color: '#6b7280' }} />
        <Line type="monotone" dataKey="HHI"        stroke="#3b82f6" dot={false} strokeWidth={1.5} />
        <Line type="monotone" dataKey="Entropy"    stroke="#22c55e" dot={false} strokeWidth={1.5} />
        <Line type="monotone" dataKey="Turnover"   stroke="#f59e0b" dot={false} strokeWidth={1.5} />
        <Line type="monotone" dataKey="Idle Ratio" stroke="#ef4444" dot={false} strokeWidth={1.5} />
      </LineChart>
    </ResponsiveContainer>
  )
}