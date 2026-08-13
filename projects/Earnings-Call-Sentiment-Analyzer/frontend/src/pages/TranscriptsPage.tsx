import { useQuery } from '@tanstack/react-query'
import { ArrowRight, FilePlus2, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getTranscripts } from '../api'
import { LoadingState } from '../components/LoadingState'
import { PageHeader } from '../components/PageHeader'
import { StatusPill } from '../components/StatusPill'
import { apiErrorMessage, formatDate } from '../lib'

export function TranscriptsPage() {
  const query = useQuery({ queryKey: ['transcripts'], queryFn: getTranscripts, refetchInterval: 10_000 })

  return (
    <div className="mx-auto max-w-7xl">
      <PageHeader
        eyebrow="Research library"
        title="Earnings calls, decoded."
        description="Track uploaded transcripts and open completed analyses. Processing status refreshes automatically."
        actions={<Link to="/upload" className="primary-button"><FilePlus2 size={17} />New analysis</Link>}
      />

      {query.isLoading ? <LoadingState label="Loading transcripts" /> : query.isError ? (
        <div className="panel p-6 text-sm text-red-700">{apiErrorMessage(query.error, 'Could not load transcripts')}</div>
      ) : !query.data?.length ? (
        <div className="panel grid min-h-80 place-items-center p-8 text-center">
          <div>
            <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-mint text-moss"><FileText size={26} /></span>
            <h2 className="mt-5 text-xl font-bold">Your research shelf is empty</h2>
            <p className="mt-2 text-sm text-ink/50">Upload an earnings call transcript to create your first analysis.</p>
            <Link to="/upload" className="primary-button mt-5">Start an analysis <ArrowRight size={17} /></Link>
          </div>
        </div>
      ) : (
        <div className="panel overflow-hidden">
          <div className="hidden grid-cols-[1.5fr_.7fr_.6fr_.7fr_.8fr_40px] border-b border-ink/10 bg-paper/50 px-6 py-3 text-[10px] font-bold uppercase tracking-[0.16em] text-ink/45 md:grid">
            <span>Company</span><span>Period</span><span>Year</span><span>Status</span><span>Uploaded</span><span />
          </div>
          <div className="divide-y divide-ink/10">
            {query.data.map((transcript) => (
              <Link key={transcript.id} to={`/transcripts/${transcript.id}`} className="grid gap-3 p-5 transition hover:bg-mint/20 md:grid-cols-[1.5fr_.7fr_.6fr_.7fr_.8fr_40px] md:items-center md:px-6">
                <span className="flex min-w-0 items-center gap-3">
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-sand/65 text-ink/55"><FileText size={18} /></span>
                  <span className="min-w-0"><strong className="block truncate text-sm">{transcript.companyName}</strong><span className="mt-0.5 block text-xs font-semibold text-moss">{transcript.ticker}</span></span>
                </span>
                <span className="text-sm font-medium">{transcript.quarter}</span>
                <span className="text-sm text-ink/55">FY {transcript.fiscalYear}</span>
                <span><StatusPill status={transcript.status} /></span>
                <span className="text-xs text-ink/45">{formatDate(transcript.createdAt)}</span>
                <ArrowRight className="hidden text-ink/25 md:block" size={18} />
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
