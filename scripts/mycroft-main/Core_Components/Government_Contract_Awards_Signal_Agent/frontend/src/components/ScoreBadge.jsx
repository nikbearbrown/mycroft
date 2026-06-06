import React from 'react'

/**
 * Colored pill badge for signal scores.
 * score >= 0.7  → HIGH  (red)
 * score >= 0.4  → MEDIUM (yellow)
 * score >= 0.15 → LOW   (blue)
 * else          → NONE  (gray)
 */
export default function ScoreBadge({ score }) {
  const s = typeof score === 'number' ? score : parseFloat(score) || 0

  let cls, label
  if (s >= 0.7) {
    cls = 'badge badge-high'
    label = 'HIGH'
  } else if (s >= 0.4) {
    cls = 'badge badge-medium'
    label = 'MEDIUM'
  } else if (s >= 0.15) {
    cls = 'badge badge-low'
    label = 'LOW'
  } else {
    cls = 'badge badge-none'
    label = 'NONE'
  }

  return (
    <span className={cls} title={`Signal score: ${s}`}>
      {label}&nbsp;{s.toFixed(2)}
    </span>
  )
}
