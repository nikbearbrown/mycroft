const AGENT_LABELS = {
  behavior:      'Behavior',
  timing:        'Timing',
  regime:        'Regime',
  sector:        'Sector / market cap',
  hold_duration: 'Hold duration',
  luck_vs_skill: 'Recipe vs luck',
}

// Simple heuristic: classify each insight as positive, negative, or neutral
function classifyInsight(text) {
  const t = text.toLowerCase()
  if (/good|best|strong|outperform|helped|let winners|added value|optimal/.test(t)) return 'positive'
  if (/worst|hurt|drag|panic|high churn|loss|warning|outsized|dependency|passive.*outperform/.test(t)) return 'negative'
  return 'neutral'
}

function InsightDot({ type }) {
  const cls = {
    positive: 'bg-green',
    negative: 'bg-red',
    neutral:  'bg-dim',
  }[type]
  return <span className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${cls}`} />
}

export default function InsightsList({ findings }) {
  // Flatten all insights, grouped by agent
  return (
    <div className="space-y-6">
      {findings.map(f => f.insights.length > 0 && (
        <div key={f.agent_name}>
          <div className="text-xs font-mono text-accent uppercase tracking-wider mb-3">
            {AGENT_LABELS[f.agent_name] ?? f.agent_name}
          </div>
          <ul className="space-y-2">
            {f.insights.map((insight, i) => {
              const type = classifyInsight(insight)
              return (
                <li key={i} className="flex items-start gap-2.5 text-sm text-primary leading-relaxed">
                  <InsightDot type={type} />
                  {insight}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}