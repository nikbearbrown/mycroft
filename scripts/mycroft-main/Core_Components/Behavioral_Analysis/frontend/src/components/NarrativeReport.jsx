import { useState } from 'react'

export default function NarrativeReport({ narrative }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(narrative)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Render markdown-lite: bold (**text**), headers (##), bullet (-)
  function renderLine(line, i) {
    if (line.startsWith('## ') || line.startsWith('### ')) {
      const text = line.replace(/^#{2,3} /, '')
      return (
        <h3 key={i} className="text-primary font-medium text-sm mt-5 mb-2 first:mt-0">
          {text}
        </h3>
      )
    }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      const text = line.slice(2)
      return (
        <li key={i} className="text-dim text-sm leading-relaxed ml-3 list-disc">
          <span dangerouslySetInnerHTML={{ __html: boldify(text) }} />
        </li>
      )
    }
    if (line.trim() === '') return <div key={i} className="h-2" />
    return (
      <p key={i} className="text-dim text-sm leading-relaxed">
        <span dangerouslySetInnerHTML={{ __html: boldify(line) }} />
      </p>
    )
  }

  function boldify(str) {
    return str.replace(/\*\*(.+?)\*\*/g, '<span class="text-primary font-medium">$1</span>')
  }

  const lines = narrative.split('\n')

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-mono text-accent uppercase tracking-wider">Edge report</span>
        <button
          onClick={copy}
          className="text-xs text-dim hover:text-primary transition-colors font-mono"
        >
          {copied ? 'copied ✓' : 'copy'}
        </button>
      </div>
      <div className="space-y-1">
        {lines.map((line, i) => renderLine(line, i))}
      </div>
    </div>
  )
}