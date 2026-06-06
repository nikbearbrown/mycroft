const AGENT_LABELS = {
  behavior:      'Behavior',
  timing:        'Timing',
  regime:        'Regime',
  sector:        'Sector / Market Cap',
  hold_duration: 'Hold Duration',
  luck_vs_skill: 'Recipe vs Luck',
}

function fmt(n) {
  if (n == null) return '—'
  if (Math.abs(n) >= 1000) return `$${(n / 1000).toFixed(1)}k`
  return `$${Number(n).toFixed(0)}`
}

function scoreLabel(s) {
  if (s >= 0.5)  return 'Strong edge'
  if (s >= 0.2)  return 'Developing'
  if (s >= 0)    return 'Marginal'
  if (s >= -0.2) return 'Slight drag'
  return 'Significant drag'
}

function scoreColor(s) {
  if (s >= 0.2)  return '#3ecf8e'
  if (s >= 0)    return '#fbbf24'
  return '#f87171'
}

function renderMarkdown(text) {
  return text
    .split('\n')
    .map(line => {
      if (line.startsWith('## ') || line.startsWith('### ')) {
        return `<h3>${line.replace(/^#{2,3} /, '')}</h3>`
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        const content = line.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        return `<li>${content}</li>`
      }
      if (line.trim() === '') return '<br/>'
      return `<p>${line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}</p>`
    })
    .join('\n')
}

export function exportReport(report) {
  const { trade_stats: s, agent_findings, narrative, edge_profile, generated_at } = report
  const scores = edge_profile?.edge_scores_by_dimension ?? {}
  const date   = generated_at
    ? new Date(generated_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    : ''

  const scoresHTML = Object.entries(scores).map(([name, score]) => {
    const pct   = Math.round(((score + 1) / 2) * 100)
    const color = scoreColor(score)
    const label = scoreLabel(score)
    return `
      <div class="score-row">
        <div class="score-header">
          <span class="score-name">${AGENT_LABELS[name] ?? name}</span>
          <span class="score-badge" style="color:${color}">${label}</span>
        </div>
        <div class="score-track">
          <div class="score-fill" style="width:${pct}%;background:${color}"></div>
        </div>
        <div class="score-value" style="color:${color}">${score >= 0 ? '+' : ''}${score.toFixed(2)}</div>
      </div>`
  }).join('')

  const insightsHTML = agent_findings.map(f => {
    if (!f.insights.length) return ''
    return `
      <div class="insight-group">
        <div class="insight-label">${AGENT_LABELS[f.agent_name] ?? f.agent_name}</div>
        <ul>${f.insights.map(i => `<li>${i}</li>`).join('')}</ul>
      </div>`
  }).join('')

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Behavioral Alpha — Edge Report</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Helvetica Neue',Arial,sans-serif;font-size:14px;color:#1a1a1a;background:#fff;padding:48px;max-width:800px;margin:0 auto}
  @media print{
    body{padding:0}
    @page{margin:32px;size:A4}
    .score-track{-webkit-print-color-adjust:exact;print-color-adjust:exact}
    .stat{-webkit-print-color-adjust:exact;print-color-adjust:exact;break-inside:avoid}
    .insight-group{break-inside:avoid}
    .section{break-inside:avoid}
  }

  .header{border-bottom:2px solid #1a1a1a;padding-bottom:16px;margin-bottom:32px}
  .header h1{font-size:22px;font-weight:700;letter-spacing:-0.3px}
  .header .meta{font-size:12px;color:#888;margin-top:4px}
  .header .tagline{font-size:13px;color:#555;margin-top:8px}

  .section{margin-bottom:36px}
  .section-title{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#888;margin-bottom:14px;padding-bottom:6px;border-bottom:1px solid #e5e5e5}

  .stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  .stat{background:#f7f7f7;border-radius:8px;padding:14px}
  .stat-label{font-size:11px;color:#888;margin-bottom:4px}
  .stat-value{font-size:20px;font-weight:700;font-family:monospace}
  .stat-sub{font-size:11px;color:#aaa;margin-top:2px}
  .green{color:#16a34a}.red{color:#dc2626}.amber{color:#d97706}

  .score-row{margin-bottom:14px}
  .score-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
  .score-name{font-size:13px;font-weight:500}
  .score-badge{font-size:11px;font-weight:600}
  .score-track{background:#e5e5e5;border-radius:4px;height:6px;margin-bottom:3px}
  .score-fill{height:6px;border-radius:4px}
  .score-value{font-size:11px;font-family:monospace;text-align:right}

  .narrative h3{font-size:13px;font-weight:700;margin:16px 0 6px}
  .narrative p{font-size:13px;color:#333;line-height:1.7;margin-bottom:6px}
  .narrative li{font-size:13px;color:#333;line-height:1.7;margin-left:18px;margin-bottom:3px}
  .narrative br{display:block;margin:4px 0}
  .narrative strong{font-weight:600;color:#1a1a1a}

  .insight-group{margin-bottom:20px}
  .insight-label{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#7c6dfa;margin-bottom:8px}
  .insight-group ul{padding-left:16px}
  .insight-group li{font-size:13px;color:#333;line-height:1.7;margin-bottom:4px}

  .footer{margin-top:40px;padding-top:16px;border-top:1px solid #e5e5e5;display:flex;justify-content:space-between;font-size:11px;color:#aaa}
</style>
</head>
<body>

<div class="header">
  <h1>Behavioral Alpha — Edge Report</h1>
  <div class="meta">Generated ${date}</div>
  <div class="tagline">A behavioral analysis of your personal trading history.</div>
</div>

<div class="section">
  <div class="section-title">Overview</div>
  <div class="stats-grid">
    <div class="stat">
      <div class="stat-label">Total P&amp;L</div>
      <div class="stat-value ${s.total_realized_pnl >= 0 ? 'green' : 'red'}">${fmt(s.total_realized_pnl)}</div>
    </div>
    <div class="stat">
      <div class="stat-label">Win rate</div>
      <div class="stat-value ${s.win_rate >= 55 ? 'green' : s.win_rate >= 45 ? 'amber' : 'red'}">${s.win_rate}%</div>
    </div>
    <div class="stat">
      <div class="stat-label">Avg hold</div>
      <div class="stat-value">${s.avg_hold_days}d</div>
    </div>
    <div class="stat">
      <div class="stat-label">Total trades</div>
      <div class="stat-value">${s.total_trades}</div>
      <div class="stat-sub">${s.unique_tickers} tickers</div>
    </div>
    <div class="stat">
      <div class="stat-label">Closed positions</div>
      <div class="stat-value">${s.total_sells}</div>
    </div>
    <div class="stat">
      <div class="stat-label">Overall edge score</div>
      <div class="stat-value ${edge_profile?.overall_edge_score >= 0.2 ? 'green' : edge_profile?.overall_edge_score >= 0 ? 'amber' : 'red'}">
        ${edge_profile?.overall_edge_score != null ? (edge_profile.overall_edge_score >= 0 ? '+' : '') + edge_profile.overall_edge_score.toFixed(2) : '—'}
      </div>
      <div class="stat-sub">−1 noise → +1 edge</div>
    </div>
  </div>
</div>

<div class="section">
  <div class="section-title">Edge by dimension</div>
  ${scoresHTML}
</div>

<div class="section">
  <div class="section-title">Analysis</div>
  <div class="narrative">${renderMarkdown(narrative)}</div>
</div>

<div class="section">
  <div class="section-title">Detailed insights</div>
  ${insightsHTML}
</div>

<div class="footer">
  <span>Behavioral Alpha</span>
  <span>Date range: ${s.date_range_start} → ${s.date_range_end}</span>
</div>

</body>
</html>`

  const win = window.open('', '_blank')
  win.document.write(html)
  win.document.close()
  win.addEventListener('load', () => {
    win.focus()
    win.print()
    // Close the tab after the print dialog is dismissed
    win.addEventListener('afterprint', () => win.close())
  })
}