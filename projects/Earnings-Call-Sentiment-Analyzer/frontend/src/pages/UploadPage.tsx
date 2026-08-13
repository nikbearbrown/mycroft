import { useMutation } from '@tanstack/react-query'
import { FileText, ShieldCheck, Sparkles, UploadCloud, X } from 'lucide-react'
import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadTranscript } from '../api'
import { PageHeader } from '../components/PageHeader'
import { apiErrorMessage } from '../lib'

const currentYear = new Date().getFullYear()

export function UploadPage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [dragging, setDragging] = useState(false)
  const [form, setForm] = useState({ companyName: '', ticker: '', quarter: 'Q1', fiscalYear: currentYear })

  const mutation = useMutation({
    mutationFn: uploadTranscript,
    onSuccess: (result) => navigate(`/jobs/${result.jobId}?transcriptId=${result.transcriptId}`),
  })

  function chooseFile(nextFile?: File) {
    if (nextFile && ['.txt', '.pdf'].some((extension) => nextFile.name.toLowerCase().endsWith(extension))) {
      setFile(nextFile)
      mutation.reset()
    }
  }

  function onFileInput(event: ChangeEvent<HTMLInputElement>) {
    chooseFile(event.target.files?.[0])
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!file) return
    const payload = new FormData()
    payload.append('file', file)
    payload.append('companyName', form.companyName)
    payload.append('ticker', form.ticker)
    payload.append('quarter', form.quarter)
    payload.append('fiscalYear', String(form.fiscalYear))
    mutation.mutate(payload)
  }

  return (
    <div className="mx-auto max-w-6xl">
      <PageHeader
        eyebrow="New analysis"
        title="Turn the call into a signal."
        description="Upload a TXT or text-based PDF earnings transcript. We’ll detect speakers and sections, score every evidence chunk with FinBERT, and assemble the result in the background."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <form onSubmit={submit} className="panel p-5 sm:p-7">
          <div className="grid gap-5 sm:grid-cols-2">
            <label>
              <span className="label">Company name</span>
              <input className="field" required maxLength={200} placeholder="e.g. Microsoft" value={form.companyName} onChange={(event) => setForm({ ...form, companyName: event.target.value })} />
            </label>
            <label>
              <span className="label">Ticker</span>
              <input className="field uppercase" required maxLength={20} placeholder="MSFT" value={form.ticker} onChange={(event) => setForm({ ...form, ticker: event.target.value.toUpperCase() })} />
            </label>
            <label>
              <span className="label">Quarter</span>
              <select className="field" value={form.quarter} onChange={(event) => setForm({ ...form, quarter: event.target.value })}>
                {['Q1', 'Q2', 'Q3', 'Q4'].map((quarter) => <option key={quarter}>{quarter}</option>)}
              </select>
            </label>
            <label>
              <span className="label">Fiscal year</span>
              <input className="field" required type="number" min={1990} max={currentYear + 2} value={form.fiscalYear} onChange={(event) => setForm({ ...form, fiscalYear: Number(event.target.value) })} />
            </label>
          </div>

          <div className="mt-6">
            <span className="label">Transcript file</span>
            <input ref={inputRef} className="hidden" type="file" accept=".txt,.pdf,text/plain,application/pdf" onChange={onFileInput} />
            {file ? (
              <div className="flex min-h-36 items-center justify-between gap-4 rounded-2xl border border-moss/25 bg-mint/35 p-5">
                <div className="flex min-w-0 items-center gap-4">
                  <span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-white text-moss shadow-sm"><FileText size={23} /></span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-ink">{file.name}</p>
                    <p className="mt-1 text-xs text-ink/45">{(file.size / 1024).toFixed(1)} KB · {file.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'Plain text'}</p>
                  </div>
                </div>
                <button type="button" aria-label="Remove file" className="rounded-lg p-2 text-ink/40 hover:bg-white hover:text-ink" onClick={() => setFile(null)}><X size={19} /></button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                onDragOver={(event) => { event.preventDefault(); setDragging(true) }}
                onDragLeave={() => setDragging(false)}
                onDrop={(event) => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]) }}
                className={`grid min-h-44 w-full place-items-center rounded-2xl border border-dashed p-6 text-center transition ${dragging ? 'border-moss bg-mint/50' : 'border-ink/20 bg-paper/60 hover:border-moss/60 hover:bg-mint/25'}`}
              >
                <span>
                  <UploadCloud className="mx-auto text-moss" size={30} />
                  <span className="mt-3 block text-sm font-semibold">Drop a .txt or .pdf file here, or browse</span>
                  <span className="mt-1 block text-xs text-ink/40">Maximum file size: 10 MB</span>
                </span>
              </button>
            )}
          </div>

          {mutation.isError && <p className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{apiErrorMessage(mutation.error, 'Could not submit transcript')}</p>}

          <div className="mt-6 flex items-center justify-between gap-4 border-t border-ink/10 pt-6">
            <p className="hidden text-xs leading-5 text-ink/40 sm:block">Analysis runs asynchronously.<br />You can leave the status screen safely.</p>
            <button className="primary-button ml-auto" disabled={!file || mutation.isPending}>
              <Sparkles size={17} />
              {mutation.isPending ? 'Creating job…' : 'Analyze transcript'}
            </button>
          </div>
        </form>

        <aside className="space-y-4">
          <div className="rounded-2xl bg-ink p-6 text-white shadow-card">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-mint/65">What happens next</p>
            <ol className="mt-5 space-y-5">
              {[
                ['01', 'Parse', 'Sections, speakers, and roles are detected.'],
                ['02', 'Score', 'Small text chunks run through FinBERT in batches.'],
                ['03', 'Explain', 'Aggregates stay linked to the source evidence.'],
              ].map(([number, title, copy]) => (
                <li key={number} className="flex gap-3">
                  <span className="text-xs font-bold text-mint/55">{number}</span>
                  <span><strong className="block text-sm">{title}</strong><span className="mt-1 block text-xs leading-5 text-white/45">{copy}</span></span>
                </li>
              ))}
            </ol>
          </div>
          <div className="panel flex gap-3 p-5">
            <ShieldCheck className="shrink-0 text-moss" size={22} />
            <div>
              <p className="text-sm font-semibold">No black-box final score</p>
              <p className="mt-1 text-xs leading-5 text-ink/50">Every result includes all three class probabilities and the exact text behind it.</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
