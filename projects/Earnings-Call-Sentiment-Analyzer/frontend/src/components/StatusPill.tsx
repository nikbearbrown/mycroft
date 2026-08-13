import type { JobStatus, SentimentLabel } from '../types'

const statusStyles: Record<JobStatus, string> = {
  QUEUED: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  PROCESSING: 'bg-blue-50 text-blue-700 ring-blue-600/15',
  COMPLETED: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  FAILED: 'bg-red-50 text-red-700 ring-red-600/15',
}

const sentimentStyles: Record<SentimentLabel, string> = {
  POSITIVE: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  NEUTRAL: 'bg-slate-100 text-slate-600 ring-slate-500/15',
  NEGATIVE: 'bg-red-50 text-red-700 ring-red-600/15',
}

export function StatusPill({ status }: { status: JobStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide ring-1 ring-inset ${statusStyles[status]}`}>
      {status}
    </span>
  )
}

export function SentimentPill({ label }: { label: SentimentLabel }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-bold tracking-wide ring-1 ring-inset ${sentimentStyles[label]}`}>
      {label}
    </span>
  )
}
