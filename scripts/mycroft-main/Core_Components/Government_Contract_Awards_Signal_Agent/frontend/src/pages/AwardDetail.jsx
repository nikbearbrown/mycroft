import React, { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import ScoreBadge from '../components/ScoreBadge'
import { fetchAwards } from '../services/api'

function formatAmount(value) {
  if (!value && value !== 0) return '—'
  return '$' + Number(value).toLocaleString('en-US')
}

/* ------------------------------------------------------------------ */
/*  Signal Breakdown — explains which factors pushed the score up/down  */
/* ------------------------------------------------------------------ */
function SignalBreakdown({ award }) {
  const score = award.signal_score || 0

  const factors = [
    {
      label: 'Award Amount',
      active: (award.award_amount || 0) > 10_000_000,
      description:
        (award.award_amount || 0) > 10_000_000
          ? 'Large contract value (>$10M) signals significant investment.'
          : 'Contract value below $10M — lower financial significance.',
      weight: 0.25,
    },
    {
      label: 'DoD / Intel Affiliation',
      active: ['dod', 'intel'].includes((award.agency_type || '').toLowerCase()),
      description:
        ['dod', 'intel'].includes((award.agency_type || '').toLowerCase())
          ? 'Award issued by a defense or intelligence agency.'
          : 'Civilian agency — lower strategic sensitivity.',
      weight: 0.3,
    },
    {
      label: 'AI / Technology Keywords',
      active: /artificial intelligence|machine learning|autonomous|cyber|quantum/i.test(
        award.description || ''
      ),
      description:
        /artificial intelligence|machine learning|autonomous|cyber|quantum/i.test(
          award.description || ''
        )
          ? 'Description contains high-signal technology keywords.'
          : 'No high-signal technology terms detected in description.',
      weight: 0.25,
    },
    {
      label: 'Recency',
      active: !!award.award_date && new Date(award.award_date) >= new Date('2025-01-01'),
      description:
        !!award.award_date && new Date(award.award_date) >= new Date('2025-01-01')
          ? 'Award date is recent (2025 or later).'
          : 'Older award — reduced recency weight.',
      weight: 0.2,
    },
  ]

  const barColor = score >= 0.7 ? 'var(--red)' : score >= 0.4 ? 'var(--yellow)' : 'var(--accent)'

  return (
    <div className="card" style={{ marginTop: '24px' }}>
      <h2
        style={{
          fontSize: '1rem',
          fontWeight: 700,
          marginBottom: '16px',
          color: 'var(--text)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        📡 Signal Breakdown
      </h2>

      {/* Overall score bar */}
      <div style={{ marginBottom: '20px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '6px',
          }}
        >
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            Overall Signal Score
          </span>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: barColor }}>
            {score.toFixed(2)} / 1.00
          </span>
        </div>
        <div
          style={{
            height: '8px',
            background: 'var(--border)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${Math.min(score * 100, 100)}%`,
              background: barColor,
              borderRadius: '4px',
              transition: 'width 0.5s ease',
            }}
          />
        </div>
      </div>

      {/* Factor list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {factors.map((f) => (
          <div
            key={f.label}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              padding: '12px 14px',
              borderRadius: '8px',
              background: f.active ? '#f0fdf4' : '#f8fafc',
              border: `1px solid ${f.active ? '#bbf7d0' : 'var(--border)'}`,
            }}
          >
            <span style={{ fontSize: '1rem', marginTop: '1px' }}>
              {f.active ? '✅' : '⬜'}
            </span>
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  color: f.active ? '#14532d' : 'var(--text)',
                  marginBottom: '2px',
                }}
              >
                {f.label}
                <span
                  style={{
                    marginLeft: '8px',
                    fontSize: '0.72rem',
                    fontWeight: 500,
                    color: 'var(--text-muted)',
                  }}
                >
                  weight {f.weight.toFixed(2)}
                </span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {f.description}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Field helper                                                         */
/* ------------------------------------------------------------------ */
function Field({ label, value }) {
  return (
    <div>
      <div
        style={{
          fontSize: '0.72rem',
          fontWeight: 600,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '4px',
        }}
      >
        {label}
      </div>
      <div style={{ fontSize: '0.925rem', color: 'var(--text)', fontWeight: 500 }}>
        {value || '—'}
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Main page                                                            */
/* ------------------------------------------------------------------ */
export default function AwardDetail() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()

  const [award, setAward] = useState(location.state?.award || null)
  const [loading, setLoading] = useState(!award)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (award) return
    // If we don't have state, re-fetch (search for matching award_id)
    setLoading(true)
    fetchAwards('', 1000)
      .then((res) => {
        const data = Array.isArray(res.data) ? res.data : res.data?.awards || []
        const found = data.find((a) => a.award_id === id)
        if (found) {
          setAward(found)
        } else {
          setError('Award not found. It may have expired from the cache.')
        }
      })
      .catch(() => setError('Failed to load award details.'))
      .finally(() => setLoading(false))
  }, [id, award])

  return (
    <>
      {/* Mini navbar strip */}
      <div
        style={{
          background: 'var(--navy)',
          height: '60px',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
        }}
      >
        <button
          className="btn-secondary"
          onClick={() => navigate(-1)}
          style={{
            color: '#fff',
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
          }}
        >
          ← Back to Dashboard
        </button>
        <span
          style={{
            marginLeft: '20px',
            color: 'rgba(255,255,255,0.6)',
            fontSize: '0.875rem',
          }}
        >
          🏛 GovSignal / Award Detail
        </span>
      </div>

      <main className="page-main">
        {loading && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '12px',
              padding: '80px 0',
              color: 'var(--text-muted)',
            }}
          >
            <span className="spinner spinner-dark" />
            <span>Loading award details…</span>
          </div>
        )}

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {!loading && !error && award && (
          <>
            {/* Header card */}
            <div className="card" style={{ marginBottom: '20px' }}>
              {/* Award ID pill */}
              <div style={{ marginBottom: '10px' }}>
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    background: 'var(--gray-bg)',
                    border: '1px solid var(--border)',
                    borderRadius: '4px',
                    padding: '2px 8px',
                  }}
                >
                  Award ID: {award.award_id}
                </span>
              </div>

              {/* Recipient name + score */}
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  alignItems: 'center',
                  gap: '14px',
                  marginBottom: '6px',
                }}
              >
                <h1
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 800,
                    color: 'var(--text)',
                    letterSpacing: '-0.02em',
                    lineHeight: 1.2,
                  }}
                >
                  {award.recipient_name || 'Unknown Recipient'}
                </h1>
                <span style={{ transform: 'scale(1.15)', transformOrigin: 'left center' }}>
                  <ScoreBadge score={award.signal_score} />
                </span>
              </div>

              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {award.awarding_agency || 'Agency unknown'}
              </p>
            </div>

            {/* Details grid */}
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2
                style={{
                  fontSize: '1rem',
                  fontWeight: 700,
                  marginBottom: '20px',
                  color: 'var(--text)',
                }}
              >
                Contract Details
              </h2>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '20px 32px',
                }}
              >
                <Field label="Awarding Agency" value={award.awarding_agency} />
                <Field label="Award Amount" value={formatAmount(award.award_amount)} />
                <Field label="Award Date" value={award.award_date} />
                <Field label="NAICS Code" value={award.naics_code} />
                <Field
                  label="Place of Performance"
                  value={award.place_of_performance || 'Not specified'}
                />
                <Field label="Agency Type" value={award.agency_type} />
              </div>
            </div>

            {/* Description */}
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2
                style={{
                  fontSize: '1rem',
                  fontWeight: 700,
                  marginBottom: '12px',
                  color: 'var(--text)',
                }}
              >
                Description
              </h2>
              <p
                style={{
                  color: 'var(--text)',
                  fontSize: '0.925rem',
                  lineHeight: 1.7,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {award.description || 'No description available.'}
              </p>
            </div>

            {/* AI Analyst Brief */}
            {award.ai_brief && (
              <div className="card" style={{ marginBottom: '20px', borderLeft: '4px solid var(--accent)' }}>
                <h2
                  style={{
                    fontSize: '1rem',
                    fontWeight: 700,
                    marginBottom: '12px',
                    color: 'var(--text)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  🤖 AI Analyst Brief
                  <span
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: '#dbeafe',
                      color: '#1e40af',
                      borderRadius: '999px',
                      padding: '2px 8px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                    }}
                  >
                    Claude
                  </span>
                </h2>
                <p
                  style={{
                    color: 'var(--text)',
                    fontSize: '0.95rem',
                    lineHeight: 1.75,
                    fontStyle: 'italic',
                  }}
                >
                  {award.ai_brief}
                </p>
              </div>
            )}

            {/* Signal Breakdown */}
            <SignalBreakdown award={award} />
          </>
        )}
      </main>
    </>
  )
}
