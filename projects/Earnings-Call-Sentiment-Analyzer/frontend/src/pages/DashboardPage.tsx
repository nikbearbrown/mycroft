import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, BarChart3, ChevronRight, FileClock, Gauge, MessageSquareQuote, Search, ShieldAlert, Telescope, UsersRound } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getChunks, getSections, getSpeakers, getSummary, getTranscript } from '../api'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { SentimentPill, StatusPill } from '../components/StatusPill'
import { apiErrorMessage, formatDate, formatNetTone, readableName } from '../lib'
import type { SentimentAggregate, SentimentChunk, SentimentLabel, SentimentSummary } from '../types'

const sentimentColors: Record<SentimentLabel, string> = {
  POSITIVE: '#238168',
  NEUTRAL: '#8c9a94',
  NEGATIVE: '#d75b4b',
}

export function DashboardPage() {
  const transcriptId = Number(useParams().transcriptId)
  const transcriptQuery = useQuery({
    queryKey: ['transcript', transcriptId],
    queryFn: () => getTranscript(transcriptId),
    enabled: Number.isFinite(transcriptId),
    refetchInterval: (context) => context.state.data?.status === 'COMPLETED' ? false : 5000,
  })
  const completed = transcriptQuery.data?.status === 'COMPLETED'
  const summaryQuery = useQuery({ queryKey: ['summary', transcriptId], queryFn: () => getSummary(transcriptId), enabled: completed })
  const chunksQuery = useQuery({ queryKey: ['chunks', transcriptId], queryFn: () => getChunks(transcriptId), enabled: completed })
  const sectionsQuery = useQuery({ queryKey: ['sections', transcriptId], queryFn: () => getSections(transcriptId), enabled: completed })
  const speakersQuery = useQuery({ queryKey: ['speakers', transcriptId], queryFn: () => getSpeakers(transcriptId), enabled: completed })

  if (transcriptQuery.isLoading) return <LoadingState label="Loading transcript" />
  if (transcriptQuery.isError || !transcriptQuery.data) return <div className="panel p-6 text-sm text-red-700">{apiErrorMessage(transcriptQuery.error, 'Transcript not found')}</div>
  if (!completed) return <PendingAnalysis status={transcriptQuery.data.status} />
  if (summaryQuery.isLoading || chunksQuery.isLoading || sectionsQuery.isLoading || speakersQuery.isLoading) return <LoadingState />

  const failedQuery = [summaryQuery, chunksQuery, sectionsQuery, speakersQuery].find((query) => query.isError)
  if (failedQuery || !summaryQuery.data || !chunksQuery.data || !sectionsQuery.data || !speakersQuery.data) {
    return <div className="panel p-6 text-sm text-red-700">{apiErrorMessage(failedQuery?.error, 'Could not load the analysis')}</div>
  }

  const transcript = transcriptQuery.data
  const summary = summaryQuery.data
  const chunks = chunksQuery.data
  const counts = [
    { name: 'Positive', value: summary.positiveChunkCount, color: sentimentColors.POSITIVE },
    { name: 'Neutral', value: summary.neutralChunkCount, color: sentimentColors.NEUTRAL },
    { name: 'Negative', value: summary.negativeChunkCount, color: sentimentColors.NEGATIVE },
  ]
  const sectionData = sectionsQuery.data.map((item) => ({ ...item, displayName: readableName(item.name), fill: item.score >= 0.05 ? sentimentColors.POSITIVE : item.score <= -0.05 ? sentimentColors.NEGATIVE : sentimentColors.NEUTRAL }))
  const speakerData = speakersQuery.data.slice(0, 8).map((item) => ({ ...item, displayName: item.name.length > 18 ? `${item.name.slice(0, 18)}…` : item.name, fill: item.score >= 0.05 ? sentimentColors.POSITIVE : item.score <= -0.05 ? sentimentColors.NEGATIVE : sentimentColors.NEUTRAL }))
  const positive = chunks.filter((chunk) => chunk.label === 'POSITIVE').sort((a, b) => b.finalScore - a.finalScore).slice(0, 5)
  const negative = chunks.filter((chunk) => chunk.label === 'NEGATIVE').sort((a, b) => a.finalScore - b.finalScore).slice(0, 5)

  return (
    <div className="mx-auto max-w-[1480px]">
      <PageHeader
        eyebrow={`${transcript.ticker} · ${transcript.quarter} FY${transcript.fiscalYear}`}
        title={transcript.companyName}
        description={`Analyzed with ProsusAI/finbert · ${chunks.length} evidence chunks · completed ${formatDate(summary.createdAt)}`}
        actions={<Link to="/transcripts" className="secondary-button"><ArrowLeft size={16} />All transcripts</Link>}
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <div className="relative overflow-hidden rounded-2xl bg-ink p-5 text-white shadow-card sm:col-span-2 xl:col-span-1">
          <div className="absolute -right-5 -top-5 h-24 w-24 rounded-full bg-mint/10" />
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/45">Overall label</p>
          <p className="mt-7 text-2xl font-bold tracking-tight">{readableName(summary.overallLabel)}</p>
          <p className="mt-3 text-xs leading-5 text-white/50">Derived from overall net tone</p>
        </div>
        <ScoreCard label="Overall net tone" value={summary.overallScore} description={`Mean across all ${chunks.length} chunks`} emphasized />
        <ScoreCard label="Prepared tone" value={summary.preparedRemarksScore} description="Prepared-remarks chunks only" />
        <ScoreCard label="Q&A tone" value={summary.qaScore} description="Question-and-answer chunks only" />
        <ScoreCard label="Management tone" value={summary.managementScore} description="CEO and CFO chunks only" />
        <ScoreCard label="Analyst tone" value={summary.analystScore} description="Analyst chunks only" />
      </section>

      <MetricDefinition overallScore={summary.overallScore} />

      <ResearchSignals summary={summary} sections={sectionsQuery.data} chunks={chunks} />

      <section className="mt-6 grid gap-6 xl:grid-cols-3">
        <ChartPanel title="Evidence distribution" subtitle="FinBERT label by chunk" icon={<BarChart3 size={18} />}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={counts} margin={{ top: 15, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#14221f12" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#61706b' }} />
              <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#83908b' }} />
              <Tooltip cursor={{ fill: '#f5f7f2' }} contentStyle={tooltipStyle} />
              <Bar dataKey="value" radius={[8, 8, 2, 2]} maxBarSize={50}>{counts.map((item) => <Cell key={item.name} fill={item.color} />)}</Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="By call section" subtitle="Mean net tone from −100% to +100%" icon={<MessageSquareQuote size={18} />}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={sectionData} layout="vertical" margin={{ top: 8, right: 20, left: 20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" horizontal={false} stroke="#14221f12" />
              <XAxis type="number" domain={[-1, 1]} tickFormatter={(value) => `${Math.round(Number(value) * 100)}%`} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#83908b' }} />
              <YAxis type="category" dataKey="displayName" width={115} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#61706b' }} />
              <Tooltip formatter={(value) => formatNetTone(Number(value))} cursor={{ fill: '#f5f7f2' }} contentStyle={tooltipStyle} />
              <Bar dataKey="score" radius={[0, 6, 6, 0]} maxBarSize={24}>{sectionData.map((item) => <Cell key={item.name} fill={item.fill} />)}</Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="By speaker" subtitle="Mean net tone for the most active voices" icon={<UsersRound size={18} />}>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={speakerData} layout="vertical" margin={{ top: 8, right: 20, left: 20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" horizontal={false} stroke="#14221f12" />
              <XAxis type="number" domain={[-1, 1]} tickFormatter={(value) => `${Math.round(Number(value) * 100)}%`} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#83908b' }} />
              <YAxis type="category" dataKey="displayName" width={115} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#61706b' }} />
              <Tooltip formatter={(value) => formatNetTone(Number(value))} cursor={{ fill: '#f5f7f2' }} contentStyle={tooltipStyle} />
              <Bar dataKey="score" radius={[0, 6, 6, 0]} maxBarSize={20}>{speakerData.map((item) => <Cell key={`${item.name}-${item.role}`} fill={item.fill} />)}</Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <EvidenceList title="Strongest positive evidence" items={positive} label="POSITIVE" />
        <EvidenceList title="Strongest negative evidence" items={negative} label="NEGATIVE" />
      </section>

      <EvidenceTable chunks={chunks} />
    </div>
  )
}

const riskLanguage = /\b(risk|headwind|pressure|declin|weak|uncertain|challenge|inflation|tariff|delay|lower|soft|volatil|restructur|constraint)\w*/i

function ResearchSignals({ summary, sections, chunks }: { summary: SentimentSummary; sections: SentimentAggregate[]; chunks: SentimentChunk[] }) {
  const guidanceSection = sections.find((section) => section.name === 'GUIDANCE')
  const guidanceScore = guidanceSection?.score ?? summary.preparedRemarksScore
  const guidanceTone = guidanceScore == null ? 'Unavailable' : guidanceScore >= 0.15 ? 'Supportive' : guidanceScore <= -0.05 ? 'Cautious' : 'Balanced'
  const guidanceMeaning = guidanceScore == null
    ? 'No guidance or prepared-remarks signal was available.'
    : guidanceTone === 'Supportive'
      ? 'Forward-looking language leans positive, which supports an improving outlook but does not confirm future results.'
      : guidanceTone === 'Cautious'
        ? 'Forward-looking language leans negative, suggesting management is emphasizing constraints or downside.'
        : 'Forward-looking language is mixed or neutral, so the call offers limited directional conviction.'

  const riskEvidence = chunks
    .filter((chunk) => chunk.label === 'NEGATIVE' && riskLanguage.test(chunk.chunkText))
    .sort((a, b) => a.finalScore - b.finalScore)
  const riskShare = chunks.length ? riskEvidence.length / chunks.length : 0
  const riskLevel = riskShare >= 0.05 ? 'Elevated' : riskEvidence.length ? 'Present' : 'Limited'
  const riskMeaning = riskLevel === 'Elevated'
    ? 'Negative risk terms recur across the call; review the cited passages for the specific operational or financial exposure.'
    : riskLevel === 'Present'
      ? 'Some downside language is present, but it is not dominant across the transcript.'
      : 'The model found little explicitly negative risk language; this is not evidence that the business has no risks.'

  const qaDelta = summary.qaScore != null && summary.preparedRemarksScore != null
    ? summary.qaScore - summary.preparedRemarksScore
    : null
  const confidence = summary.managementScore == null ? 'Unavailable' : summary.managementScore >= 0.2 ? 'Strong' : summary.managementScore <= 0 ? 'Guarded' : 'Measured'
  const confidenceMeaning = summary.managementScore == null
    ? 'No CEO or CFO signal was available.'
    : `${confidence === 'Strong' ? 'CEO/CFO language is consistently constructive.' : confidence === 'Guarded' ? 'CEO/CFO language is neutral to negative.' : 'CEO/CFO language is mildly constructive.'}${qaDelta == null ? '' : qaDelta <= -0.1 ? ' Tone softens materially in Q&A versus prepared remarks.' : qaDelta >= 0.1 ? ' Tone strengthens in Q&A versus prepared remarks.' : ' Tone remains broadly consistent when questioning begins.'}`

  return (
    <section className="panel mt-6 p-5 sm:p-6">
      <div className="max-w-3xl">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-moss">Research interpretation</p>
        <h2 className="mt-1 text-xl font-bold">What these sentiment outputs may signal</h2>
        <p className="mt-2 text-sm leading-6 text-ink/55">Signals are transparent interpretations of FinBERT scores and transcript text—not forecasts or investment recommendations.</p>
      </div>
      <div className="mt-5 grid gap-4 xl:grid-cols-3">
        <SignalCard icon={<Telescope size={18} />} title="Guidance tone" value={guidanceTone} metric={formatNetTone(guidanceScore)} meaning={guidanceMeaning} basis={guidanceSection ? 'Dedicated guidance section' : 'Prepared remarks proxy; no separate guidance section detected'} />
        <SignalCard icon={<ShieldAlert size={18} />} title="Risk language" value={riskLevel} metric={`${(riskShare * 100).toFixed(1)}%`} meaning={riskMeaning} basis={`${riskEvidence.length} of ${chunks.length} chunks combine a negative label with risk terms`} evidence={riskEvidence[0]?.chunkText} />
        <SignalCard icon={<Gauge size={18} />} title="Management confidence" value={confidence} metric={formatNetTone(summary.managementScore)} meaning={confidenceMeaning} basis={qaDelta == null ? 'CEO/CFO mean net tone' : `Q&A minus prepared net tone: ${formatNetTone(qaDelta)}`} />
      </div>
      <div className="mt-4 rounded-xl border border-ink/10 bg-sand/45 p-4 text-xs leading-5 text-ink/60">
        <strong className="text-ink">How to compare:</strong> overall net tone is the mean across every evidence chunk, so longer sections influence it more. Section-aware metrics calculate each group separately—prepared vs. Q&A and management vs. analysts—to expose tone gaps that the transcript-level average can hide. Use the gaps as research prompts, then validate them against the evidence below.
      </div>
    </section>
  )
}

function SignalCard({ icon, title, value, metric, meaning, basis, evidence }: { icon: React.ReactNode; title: string; value: string; metric: string; meaning: string; basis: string; evidence?: string }) {
  return (
    <article className="rounded-xl border border-ink/10 bg-white p-4">
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-mint text-moss">{icon}</span>
        <div className="min-w-0"><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-ink/40">{title}</p><p className="text-lg font-bold">{value}</p></div>
        <span className="ml-auto text-sm font-bold tabular-nums">{metric}</span>
      </div>
      <p className="mt-3 text-sm leading-6 text-ink/65">{meaning}</p>
      {evidence && <p className="mt-3 line-clamp-2 border-l-2 border-moss/35 pl-3 text-xs italic leading-5 text-ink/50">“{evidence}”</p>}
      <p className="mt-3 text-[10px] font-semibold uppercase tracking-wide text-ink/35">Basis: {basis}</p>
    </article>
  )
}

const tooltipStyle = { borderRadius: 12, border: '1px solid rgba(20,34,31,.1)', boxShadow: '0 12px 30px rgba(20,34,31,.12)', fontSize: 12 }

function MetricDefinition({ overallScore }: { overallScore: number }) {
  return (
    <div className="panel mt-4 grid gap-3 p-4 text-xs leading-5 text-ink/60 lg:grid-cols-[220px_1fr] lg:items-center">
      <div><p className="font-bold text-ink">What “net tone” means</p><p>Range: −100% to +100%</p></div>
      <p><strong className="text-ink">Formula:</strong> for each chunk, FinBERT positive probability minus negative probability; the displayed metric is the mean for the named group. Here, <strong className="text-ink">{formatNetTone(overallScore)}</strong> is an average net difference of {Math.abs(Math.round(overallScore * 100))} percentage points; a negative value means negative probability is higher. It does not mean {Math.abs(Math.round(overallScore * 100))}% of sentences were positive. Aggregate labels and chart colors use net-tone bands: Positive above +5%, Neutral from −5% to +5%, and Negative below −5%. Individual evidence labels are FinBERT&apos;s highest-probability class, so a chunk&apos;s class can differ from its net-tone band.</p>
    </div>
  )
}

function ScoreCard({ label, value, description, emphasized = false }: { label: string; value: number | null; description: string; emphasized?: boolean }) {
  const color = value == null ? 'bg-slate-300' : value >= 0.05 ? 'bg-emerald-500' : value <= -0.05 ? 'bg-red-500' : 'bg-slate-400'
  const width = value == null ? 0 : Math.abs(value) * 50
  return (
    <div className={`panel p-5 ${emphasized ? 'ring-1 ring-moss/20' : ''}`}>
      <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-ink/45">{label}</p>
      <p className="mt-5 text-2xl font-bold tabular-nums tracking-tight">{formatNetTone(value)}</p>
      <p className="mt-1 min-h-8 text-[10px] leading-4 text-ink/40">{description}</p>
      <div className="relative mt-4 h-1.5 overflow-hidden rounded-full bg-ink/8">
        <span className="absolute left-1/2 top-0 h-full w-px bg-ink/20" />
        {value != null && <span className={`absolute top-0 h-full rounded-full ${color}`} style={value >= 0 ? { left: '50%', width: `${width}%` } : { right: '50%', width: `${width}%` }} />}
      </div>
    </div>
  )
}

function ChartPanel({ title, subtitle, icon, children }: { title: string; subtitle: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="panel min-w-0 p-5">
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-mint text-moss">{icon}</span>
        <div><h2 className="text-sm font-bold">{title}</h2><p className="mt-0.5 text-xs text-ink/40">{subtitle}</p></div>
      </div>
      <div className="mt-4">{children}</div>
    </div>
  )
}

function EvidenceList({ title, items, label }: { title: string; items: SentimentChunk[]; label: SentimentLabel }) {
  return (
    <div className="panel p-5 sm:p-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-base font-bold">{title}</h2><SentimentPill label={label} />
      </div>
      <div className="mt-4 divide-y divide-ink/10">
        {items.map((chunk, index) => (
          <div key={chunk.chunkId} className="py-4 first:pt-1 last:pb-0">
            <div className="flex gap-4">
              <span className="text-xs font-bold text-ink/20">0{index + 1}</span>
              <div className="min-w-0 flex-1">
                <p className="line-clamp-3 text-sm leading-6 text-ink/75">“{chunk.chunkText}”</p>
                <div className="mt-2 flex flex-wrap items-center gap-x-2 text-[10px] font-semibold uppercase tracking-wide text-ink/40">
                  <span>{chunk.speakerName || 'Unknown speaker'}</span><span>·</span><span>{readableName(chunk.sectionName)}</span><span className="ml-auto text-xs font-bold text-ink">Net {formatNetTone(chunk.finalScore)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {!items.length && <p className="py-8 text-center text-sm text-ink/45">No {label.toLowerCase()} chunks were detected.</p>}
      </div>
    </div>
  )
}

function EvidenceTable({ chunks }: { chunks: SentimentChunk[] }) {
  const [query, setQuery] = useState('')
  const [label, setLabel] = useState<'ALL' | SentimentLabel>('ALL')
  const filtered = useMemo(() => chunks.filter((chunk) => {
    const matchesLabel = label === 'ALL' || chunk.label === label
    const needle = query.toLowerCase()
    const matchesQuery = !needle || chunk.chunkText.toLowerCase().includes(needle) || chunk.speakerName?.toLowerCase().includes(needle)
    return matchesLabel && Boolean(matchesQuery)
  }), [chunks, label, query])

  return (
    <section className="panel mt-6 overflow-hidden">
      <div className="flex flex-col gap-4 border-b border-ink/10 p-5 sm:flex-row sm:items-end sm:justify-between sm:p-6">
        <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-moss">Source of truth</p><h2 className="mt-1 text-xl font-bold">Transcript evidence</h2><p className="mt-1 text-xs text-ink/45">All class probabilities are stored for auditability.</p></div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <label className="relative"><Search className="absolute left-3 top-3 text-ink/35" size={16} /><input className="field h-10 pl-9 sm:w-56" placeholder="Search evidence" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          <select className="field h-10 sm:w-36" value={label} onChange={(event) => setLabel(event.target.value as 'ALL' | SentimentLabel)}><option value="ALL">All labels</option><option>POSITIVE</option><option>NEUTRAL</option><option>NEGATIVE</option></select>
        </div>
      </div>
      <div className="divide-y divide-ink/10">
        {filtered.map((chunk) => (
          <article key={chunk.chunkId} className="grid gap-3 p-5 sm:grid-cols-[140px_1fr_110px] sm:p-6">
            <div>
              <p className="truncate text-xs font-bold">{chunk.speakerName || 'Unknown speaker'}</p>
              <p className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-ink/40">{readableName(chunk.speakerRole)}</p>
              <p className="mt-2 text-[10px] text-ink/40">{readableName(chunk.sectionName)}</p>
            </div>
            <p className="text-sm leading-6 text-ink/70">{chunk.chunkText}</p>
            <div className="sm:text-right">
              <SentimentPill label={chunk.label} />
              <p className="mt-2 text-lg font-bold tabular-nums">{formatNetTone(chunk.finalScore)}</p>
              <p className="text-[9px] font-semibold uppercase tracking-wide text-ink/35">Net tone</p>
              <p className="mt-1 text-[9px] leading-4 text-ink/35">P {(chunk.positiveScore * 100).toFixed(0)}% · N {(chunk.neutralScore * 100).toFixed(0)}% · Neg {(chunk.negativeScore * 100).toFixed(0)}%</p>
            </div>
          </article>
        ))}
        {!filtered.length && <div className="p-10 text-center text-sm text-ink/45">No evidence matches these filters.</div>}
      </div>
    </section>
  )
}

function PendingAnalysis({ status }: { status: 'QUEUED' | 'PROCESSING' | 'FAILED' | 'COMPLETED' }) {
  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader eyebrow="Analysis unavailable" title="This call is not ready yet." description="The dashboard will become available after the background worker completes the analysis." />
      <div className="panel grid min-h-72 place-items-center p-8 text-center">
        <div>
          <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-sand text-ink/55"><FileClock size={26} /></span>
          <div className="mt-5"><StatusPill status={status} /></div>
          <p className="mt-4 max-w-md text-sm leading-6 text-ink/50">{status === 'FAILED' ? 'The worker could not complete this transcript. Upload it again after checking the worker logs.' : 'This page checks the transcript status every five seconds.'}</p>
          <Link to="/transcripts" className="secondary-button mt-5">Back to library <ChevronRight size={16} /></Link>
        </div>
      </div>
    </div>
  )
}
