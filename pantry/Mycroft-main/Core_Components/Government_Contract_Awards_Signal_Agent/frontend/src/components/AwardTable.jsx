import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import ScoreBadge from './ScoreBadge'

function formatAmount(value) {
  if (!value && value !== 0) return '—'
  return '$' + Number(value).toLocaleString('en-US')
}

function agencyBadge(type) {
  switch ((type || '').toLowerCase()) {
    case 'dod':
      return <span className="badge badge-dod">{type}</span>
    case 'intel':
      return <span className="badge badge-intel">{type}</span>
    case 'civilian':
      return <span className="badge badge-civilian">{type}</span>
    default:
      return <span className="badge badge-unknown">{type || 'Unknown'}</span>
  }
}

function truncate(str, len = 40) {
  if (!str) return '—'
  return str.length > len ? str.slice(0, len) + '…' : str
}

const COLUMNS = [
  { key: 'signal_score', label: 'Score', sortable: true },
  { key: 'recipient_name', label: 'Recipient', sortable: true },
  { key: 'awarding_agency', label: 'Agency', sortable: true },
  { key: 'award_amount', label: 'Amount', sortable: true },
  { key: 'award_date', label: 'Date', sortable: true },
  { key: 'agency_type', label: 'Type', sortable: true },
  { key: 'description', label: 'Description', sortable: false },
]

export default function AwardTable({ awards }) {
  const navigate = useNavigate()
  const [sortKey, setSortKey] = useState('signal_score')
  const [sortDir, setSortDir] = useState('desc')

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const sorted = useMemo(() => {
    if (!awards || awards.length === 0) return []
    return [...awards].sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      if (av == null && bv == null) return 0
      if (av == null) return 1
      if (bv == null) return -1
      let cmp
      if (typeof av === 'number' && typeof bv === 'number') {
        cmp = av - bv
      } else {
        cmp = String(av).localeCompare(String(bv))
      }
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [awards, sortKey, sortDir])

  if (!awards || awards.length === 0) {
    return (
      <div className="empty-state">
        <h3>No awards found</h3>
        <p>Try fetching with different filters or a different keyword.</p>
      </div>
    )
  }

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                onClick={() => col.sortable && handleSort(col.key)}
                style={{ cursor: col.sortable ? 'pointer' : 'default' }}
              >
                {col.label}
                {col.sortable && (
                  <span className="sort-icon">
                    {sortKey === col.key
                      ? sortDir === 'asc'
                        ? ' ▲'
                        : ' ▼'
                      : ' ↕'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((award) => (
            <tr
              key={award.award_id}
              onClick={() =>
                navigate(`/awards/${award.award_id}`, { state: { award } })
              }
            >
              <td>
                <ScoreBadge score={award.signal_score} />
              </td>
              <td style={{ fontWeight: 500, maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {award.recipient_name || '—'}
              </td>
              <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                {award.awarding_agency
                  ? award.awarding_agency.split('.')[0]
                  : '—'}
              </td>
              <td style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
                {formatAmount(award.award_amount)}
              </td>
              <td style={{ whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                {award.award_date || '—'}
              </td>
              <td>{agencyBadge(award.agency_type)}</td>
              <td
                className="col-desc"
                title={award.description || ''}
                style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}
              >
                {truncate(award.description, 40)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
