import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Check, Clock3, LoaderCircle, RotateCcw, TriangleAlert } from 'lucide-react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { getJob } from '../api'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { apiErrorMessage } from '../lib'
import type { JobStatus } from '../types'

const stateCopy: Record<JobStatus, { title: string; description: string }> = {
  QUEUED: { title: 'Your analysis is queued', description: 'The transcript is safe. A worker will pick it up as soon as it is available.' },
  PROCESSING: { title: 'FinBERT is reading the call', description: 'We are detecting structure, scoring evidence chunks, and assembling your summary.' },
  COMPLETED: { title: 'Your signal is ready', description: 'The complete analysis, charts, and source evidence are ready to explore.' },
  FAILED: { title: 'The analysis hit a snag', description: 'The job stopped safely. Review the worker message below for the cause.' },
}

export function JobStatusPage() {
  const jobId = Number(useParams().jobId)
  const [params] = useSearchParams()
  const fallbackTranscriptId = Number(params.get('transcriptId'))
  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJob(jobId),
    enabled: Number.isFinite(jobId),
    refetchInterval: (context) => ['COMPLETED', 'FAILED'].includes(context.state.data?.status ?? '') ? false : 2000,
  })

  if (query.isLoading) return <div className="mx-auto max-w-4xl"><LoadingState label="Finding your analysis job" /></div>
  if (query.isError || !query.data) return <div className="mx-auto max-w-4xl panel p-6 text-sm text-red-700">{apiErrorMessage(query.error, 'Job not found')}</div>

  const job = query.data
  const copy = stateCopy[job.status]
  const transcriptId = job.transcriptId || fallbackTranscriptId
  const isActive = job.status === 'QUEUED' || job.status === 'PROCESSING'

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader eyebrow={`Analysis job #${job.id}`} title="From transcript to evidence." description="This page updates automatically while the asynchronous worker processes your call." />
      <div className="panel overflow-hidden">
        <div className="p-7 sm:p-10">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
            <StatusIcon status={job.status} />
            <div className="flex-1">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.16em] text-moss">{job.status}</p>
                  <h1 className="mt-2 text-2xl font-bold tracking-tight">{copy.title}</h1>
                </div>
                <span className="text-3xl font-bold tabular-nums text-ink/20">{job.progress}%</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-ink/50">{copy.description}</p>
              <div className="mt-7 h-2 overflow-hidden rounded-full bg-ink/8">
                <div className={`h-full rounded-full transition-all duration-700 ${job.status === 'FAILED' ? 'bg-red-500' : 'bg-moss'}`} style={{ width: `${Math.max(job.progress, 3)}%` }} />
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs font-medium text-ink/50">
                {isActive && <LoaderCircle className="animate-spin text-moss" size={15} />}
                {job.message || 'Waiting for status'}
              </div>
            </div>
          </div>

          {job.status === 'FAILED' && (
            <div className="mt-7 rounded-xl border border-red-200 bg-red-50 p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-red-700">Worker error</p>
              <p className="mt-2 break-words font-mono text-xs leading-5 text-red-700/80">{job.errorMessage || 'No additional detail was provided.'}</p>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-3 border-t border-ink/10 bg-paper/55 px-7 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-10">
          <div className="flex items-center gap-2 text-xs text-ink/45"><Clock3 size={15} />{isActive ? 'Checking again in 2 seconds' : 'Processing has finished'}</div>
          {job.status === 'COMPLETED' && <Link to={`/transcripts/${transcriptId}`} className="primary-button">Open dashboard <ArrowRight size={17} /></Link>}
          {job.status === 'FAILED' && <Link to="/upload" className="secondary-button"><RotateCcw size={16} />Try another transcript</Link>}
        </div>
      </div>
    </div>
  )
}

function StatusIcon({ status }: { status: JobStatus }) {
  const styles: Record<JobStatus, string> = {
    QUEUED: 'bg-amber-100 text-amber-700', PROCESSING: 'bg-blue-100 text-blue-700', COMPLETED: 'bg-emerald-100 text-emerald-700', FAILED: 'bg-red-100 text-red-700',
  }
  const icon = status === 'QUEUED' ? <Clock3 /> : status === 'PROCESSING' ? <LoaderCircle className="animate-spin" /> : status === 'COMPLETED' ? <Check /> : <TriangleAlert />
  return <span className={`grid h-14 w-14 shrink-0 place-items-center rounded-2xl ${styles[status]}`}>{icon}</span>
}
