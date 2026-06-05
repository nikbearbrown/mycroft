const BASE = '/api'

export async function previewCSV(file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${BASE}/parse-preview`, { method: 'POST', body: fd })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Preview failed')
  }
  return res.json()
}

export async function analyzeCSV(file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${BASE}/analyze`, { method: 'POST', body: fd })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Analysis failed')
  }
  return res.json()
}