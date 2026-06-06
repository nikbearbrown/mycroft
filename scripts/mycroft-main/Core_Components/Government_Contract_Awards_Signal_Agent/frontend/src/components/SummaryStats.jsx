import React from 'react'

function formatCurrency(value) {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`
  return `$${value}`
}

const gridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px',
  marginBottom: '24px',
}

const cardStyle = {
  background: '#fff',
  border: '1px solid var(--border)',
  borderRadius: '10px',
  padding: '22px 24px',
  boxShadow: '0 1px 3px rgba(0,0,0,.06)',
}

const valueStyle = (color) => ({
  fontSize: '2rem',
  fontWeight: 800,
  lineHeight: 1.1,
  color: color || 'var(--text)',
  marginBottom: '6px',
})

const labelStyle = {
  fontSize: '0.8rem',
  fontWeight: 600,
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
}

const iconStyle = {
  fontSize: '1.4rem',
  marginBottom: '8px',
  display: 'block',
}

export default function SummaryStats({ awards }) {
  if (!awards || awards.length === 0) return null

  const totalCount = awards.length

  const flaggedCount = awards.filter((a) => a.signal_score >= 0.7).length

  const totalValue = awards.reduce((sum, a) => sum + (a.award_amount || 0), 0)

  const avgScore =
    awards.reduce((sum, a) => sum + (a.signal_score || 0), 0) / totalCount

  const stats = [
    {
      icon: '📋',
      value: totalCount.toLocaleString(),
      label: 'Total Awards',
      color: 'var(--text)',
    },
    {
      icon: '🚨',
      value: flaggedCount.toLocaleString(),
      label: 'Flagged Signals',
      color: flaggedCount > 0 ? 'var(--red)' : 'var(--text)',
    },
    {
      icon: '💰',
      value: formatCurrency(totalValue),
      label: 'Total Contract Value',
      color: 'var(--green)',
    },
    {
      icon: '📊',
      value: avgScore.toFixed(2),
      label: 'Avg Signal Score',
      color:
        avgScore >= 0.7
          ? 'var(--red)'
          : avgScore >= 0.4
          ? 'var(--yellow)'
          : 'var(--accent)',
    },
  ]

  return (
    <div style={gridStyle}>
      {stats.map((s) => (
        <div key={s.label} style={cardStyle}>
          <span style={iconStyle}>{s.icon}</span>
          <div style={valueStyle(s.color)}>{s.value}</div>
          <div style={labelStyle}>{s.label}</div>
        </div>
      ))}
    </div>
  )
}
