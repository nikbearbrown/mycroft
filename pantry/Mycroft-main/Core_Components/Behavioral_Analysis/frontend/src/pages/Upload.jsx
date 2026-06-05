import { useState, useRef } from 'react'
import { previewCSV, analyzeCSV } from '../api/client'

const BROKERS = ['Robinhood', 'IBKR', 'Schwab', 'Fidelity']

const STEPS = [
  'Parsing trades...',
  'Fetching market data...',
  'Loading macro context...',
  'Running behavior analysis...',
  'Analyzing timing patterns...',
  'Checking regime sensitivity...',
  'Decomposing sector edge...',
  'Scoring luck vs skill...',
  'Writing edge report...',
]

export default function Upload({ onReport }) {
  const [file, setFile]       = useState(null)
  const [preview, setPreview] = useState(null)
  const [step, setStep]       = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  async function handleFile(f) {
    if (!f || !f.name.endsWith('.csv')) {
      setError('Please upload a .csv file.')
      return
    }
    setFile(f)
    setError(null)
    setPreview(null)
    try {
      const p = await previewCSV(f)
      setPreview(p)
    } catch (e) {
      setError(e.message)
      setFile(null)
    }
  }

  async function handleAnalyze() {
    setLoading(true)
    setError(null)
    setStep(0)

    // Cycle through loading steps for UX
    const iv = setInterval(() => setStep(s => Math.min(s + 1, STEPS.length - 1)), 4000)

    try {
      const report = await analyzeCSV(file)
      clearInterval(iv)
      onReport(report)
    } catch (e) {
      clearInterval(iv)
      setError(e.message)
      setLoading(false)
    }
  }

  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16">

      {/* Header */}
      <div className="mb-12 text-center">
        <div className="inline-flex items-center gap-2 text-accent text-xs font-mono tracking-widest uppercase mb-4 opacity-70">
          <span className="w-4 h-px bg-accent" /> behavioral analysis system <span className="w-4 h-px bg-accent" />
        </div>
        <h1 className="text-3xl font-semibold text-primary tracking-tight">
          Where's your edge?
        </h1>
        <p className="mt-3 text-dim text-sm max-w-sm mx-auto text-balance">
          Upload your brokerage CSV and get a brutally honest report on where you actually make money — and where you don't.
        </p>
      </div>

      {/* Drop zone */}
      {!loading && (
        <div
          className={`w-full max-w-md border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
            ${dragging ? 'border-accent bg-accent/5' : 'border-border hover:border-muted'}`}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={e => handleFile(e.target.files[0])}
          />
          {file ? (
            <div>
              <div className="text-green text-sm font-mono mb-1">{file.name}</div>
              <div className="text-dim text-xs">{(file.size / 1024).toFixed(1)} KB</div>
            </div>
          ) : (
            <div>
              <div className="text-dim text-2xl mb-3">↑</div>
              <div className="text-primary text-sm">Drop your CSV here or click to browse</div>
              <div className="text-dim text-xs mt-1">Supported: {BROKERS.join(', ')}</div>
            </div>
          )}
        </div>
      )}

      {/* Preview card */}
      {preview && !loading && (
        <div className="w-full max-w-md mt-4 bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono text-accent uppercase tracking-wider">Preview</span>
            <span className="text-xs bg-muted text-primary px-2 py-0.5 rounded capitalize">{preview.broker}</span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              ['Total trades',    preview.total_trades],
              ['Closed trades',   preview.closed_trades],
              ['Unique tickers',  preview.unique_tickers],
              ['Date range',      `${preview.date_range.start} → ${preview.date_range.end}`],
            ].map(([label, val]) => (
              <div key={label}>
                <div className="text-dim text-xs mb-0.5">{label}</div>
                <div className="text-primary font-mono">{val}</div>
              </div>
            ))}
          </div>
          {preview.sample_tickers?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border">
              <div className="text-dim text-xs mb-2">Top tickers</div>
              <div className="flex gap-2 flex-wrap">
                {preview.sample_tickers.map(t => (
                  <span key={t} className="text-xs font-mono bg-muted px-2 py-0.5 rounded text-primary">{t}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="w-full max-w-md mt-4 bg-red/10 border border-red/30 rounded-xl px-4 py-3 text-red text-sm">
          {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="w-full max-w-md text-center">
          <div className="flex justify-center mb-6">
            <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          </div>
          <div className="text-primary text-sm font-mono">{STEPS[step]}</div>
          <div className="mt-4 w-full bg-border rounded-full h-0.5">
            <div
              className="bg-accent h-0.5 rounded-full transition-all duration-[3500ms]"
              style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
            />
          </div>
          <div className="text-dim text-xs mt-2">This takes 30–60s on first run</div>
        </div>
      )}

      {/* CTA */}
      {preview && !loading && (
        <button
          onClick={handleAnalyze}
          className="mt-6 w-full max-w-md bg-accent hover:bg-accent/90 text-white font-medium py-3 rounded-xl transition-colors text-sm"
        >
          Run analysis →
        </button>
      )}

      {/* Footer note */}
      {!loading && (
        <p className="mt-10 text-dim text-xs text-center max-w-xs">
          Your data never leaves your machine — analysis runs locally against your own API keys.
        </p>
      )}
    </div>
  )
}