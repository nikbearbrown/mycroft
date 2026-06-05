// Displays a single edge dimension score as a labeled bar
// score: -1 to 1

function scoreColor(s) {
  if (s >= 0.3)  return 'bg-green'
  if (s >= 0)    return 'bg-amber'
  return 'bg-red'
}

function scoreLabel(s) {
  if (s >= 0.5)  return 'Strong edge'
  if (s >= 0.2)  return 'Developing'
  if (s >= 0)    return 'Marginal'
  if (s >= -0.2) return 'Slight drag'
  return 'Significant drag'
}

const LABELS = {
  behavior:       'Behavior',
  timing:         'Timing',
  regime:         'Regime',
  sector:         'Sector',
  hold_duration:  'Hold duration',
  luck_vs_skill:  'Skill vs luck',
}

export default function EdgeScoreCard({ name, score }) {
  const pct    = Math.round(((score + 1) / 2) * 100)  // map [-1,1] → [0,100]
  const color  = scoreColor(score)
  const label  = scoreLabel(score)

  return (
    <div className="bg-surface border border-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-primary">{LABELS[name] ?? name}</span>
        <span className={`text-xs font-mono px-2 py-0.5 rounded
          ${score >= 0.2 ? 'bg-green/10 text-green' : score >= 0 ? 'bg-amber/10 text-amber' : 'bg-red/10 text-red'}`}>
          {label}
        </span>
      </div>
      <div className="w-full bg-border rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-1.5 text-right">
        <span className="text-dim text-xs font-mono">{score >= 0 ? '+' : ''}{score.toFixed(2)}</span>
      </div>
    </div>
  )
}