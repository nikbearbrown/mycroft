import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = ['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316','#ec4899']

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div className="bg-surface border border-border px-3 py-2 text-xs font-mono">
      <div className="text-text">{d.payload.name}</div>
      <div className="text-accent">{(d.value * 100).toFixed(1)}%</div>
    </div>
  )
}

export default function AllocationBar({ weights }) {
  if (!weights || !Object.keys(weights).length) return null

  const data = Object.entries(weights)
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) => ({ name: k, value: v }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 24, left: 0 }}>
        <XAxis
          dataKey="name"
          tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }}
          angle={-25}
          textAnchor="end"
          interval={0}
        />
        <YAxis
          tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
          tick={{ fontSize: 10, fill: '#6b7280', fontFamily: 'JetBrains Mono' }}
          width={38}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
        <Bar dataKey="value" radius={[2, 2, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}