import MetricsGrid     from '../components/MetricsGrid'
import EdgeScoreCard   from '../components/EdgeScoreCard'
import InsightsList    from '../components/InsightsList'
import NarrativeReport from '../components/NarrativeReport'
import { exportReport } from '../utils/exportReport'

function Section({ title, children }) {
  return (
    <section className="mb-10">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xs font-mono text-accent uppercase tracking-wider">{title}</span>
        <div className="flex-1 h-px bg-border" />
      </div>
      {children}
    </section>
  )
}

export default function Results({ report, onReset }) {
  const { trade_stats, agent_findings, narrative, edge_profile, generated_at } = report

  const edgeScores = edge_profile?.edge_scores_by_dimension ?? {}
  const dateStr    = generated_at
    ? new Date(generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : null

  return (
    <div className="min-h-screen px-4 py-12 max-w-2xl mx-auto">

      {/* Header */}
      <div className="mb-10 flex items-start justify-between">
        <div>
          <div className="inline-flex items-center gap-2 text-accent text-xs font-mono tracking-widest uppercase mb-3 opacity-70">
            <span className="w-4 h-px bg-accent" /> behavioral analysis system
          </div>
          <h1 className="text-2xl font-semibold text-primary tracking-tight">Your edge report</h1>
          {dateStr && <p className="text-dim text-xs mt-1">Generated {dateStr}</p>}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => exportReport(report)}
            className="text-xs text-dim hover:text-primary transition-colors font-mono border border-border rounded-lg px-3 py-1.5"
          >
            ↓ export
          </button>
          <button
            onClick={onReset}
            className="text-xs text-dim hover:text-primary transition-colors font-mono border border-border rounded-lg px-3 py-1.5"
          >
            ← new file
          </button>
        </div>
      </div>

      {/* Overview stats */}
      <Section title="Overview">
        <MetricsGrid stats={trade_stats} edgeProfile={edge_profile} />
      </Section>

      {/* Edge scores by dimension */}
      {Object.keys(edgeScores).length > 0 && (
        <Section title="Edge by dimension">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.entries(edgeScores).map(([name, score]) => (
              <EdgeScoreCard key={name} name={name} score={score} />
            ))}
          </div>
        </Section>
      )}

      {/* All insights */}
      <Section title="Detailed insights">
        <InsightsList findings={agent_findings} />
      </Section>

      {/* Narrative */}
      <Section title="Analysis">
        <NarrativeReport narrative={narrative} />
      </Section>

      

      {/* Footer */}
      <div className="mt-12 pt-6 border-t border-border flex items-center justify-between">
        <span className="text-dim text-xs font-mono">behavioral alpha</span>
        <button
          onClick={onReset}
          className="text-xs text-accent hover:text-accent/80 transition-colors font-mono"
        >
          analyze another file →
        </button>
      </div>
    </div>
  )
}