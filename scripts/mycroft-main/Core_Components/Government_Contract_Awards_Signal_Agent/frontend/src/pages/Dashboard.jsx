import React, { useState, useEffect, useCallback } from 'react'
import Navbar from '../components/Navbar'
import SummaryStats from '../components/SummaryStats'
import FilterBar from '../components/FilterBar'
import AwardTable from '../components/AwardTable'
import { fetchAwards, fetchMockAwards } from '../services/api'

const DEFAULT_FILTERS = {
  keyword: 'artificial intelligence',
  agency_type: 'All',
  minScore: 0,
  limit: 100,
}

function applyClientFilters(awards, filters) {
  return awards.filter((a) => {
    if (
      filters.agency_type !== 'All' &&
      (a.agency_type || '').toLowerCase() !== filters.agency_type.toLowerCase()
    ) {
      return false
    }
    if ((a.signal_score || 0) < filters.minScore) {
      return false
    }
    return true
  })
}

export default function Dashboard() {
  const [awards, setAwards] = useState([])
  const [filtered, setFiltered] = useState([])
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const doFetch = useCallback(async (currentFilters, useMock = false) => {
    setLoading(true)
    setError(null)
    try {
      const res = useMock
        ? await fetchMockAwards()
        : await fetchAwards(currentFilters.keyword, currentFilters.limit)
      const data = Array.isArray(res.data) ? res.data : res.data?.awards || []
      setAwards(data)
      setFiltered(applyClientFilters(data, currentFilters))
      setLastUpdated(new Date())
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Failed to fetch awards. Is the backend running?'

      if (detail.includes('RATE_LIMITED:')) {
        const nextAccess = detail.split('RATE_LIMITED:')[1]?.trim()
        setError(`⚠️ SAM.gov daily quota reached. API resets at: ${nextAccess}. Your last fetched data is still shown below.`)
      } else {
        setError(detail)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  // Auto-fetch on mount
  useEffect(() => {
    doFetch(DEFAULT_FILTERS)
  }, [doFetch])

  // Re-apply client-side filters whenever filter params change (but only after
  // we have data — a new keyword/limit triggers a real fetch via the button)
  useEffect(() => {
    setFiltered(applyClientFilters(awards, filters))
  }, [awards, filters])

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  const handleFetch = () => {
    doFetch(filters)
  }

  const handleMockFetch = () => {
    doFetch(filters, true)
  }

  return (
    <>
      <Navbar />
      <main className="page-main">
        {/* Header */}
        <div style={{ marginBottom: '24px' }}>
          <h1
            style={{
              fontSize: '1.6rem',
              fontWeight: 800,
              color: 'var(--text)',
              marginBottom: '4px',
              letterSpacing: '-0.02em',
            }}
          >
            Contract Awards Signal Dashboard
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            {lastUpdated
              ? `Last updated: ${lastUpdated.toLocaleString()}`
              : 'Fetching data…'}
            {filtered.length > 0 && !loading && (
              <span
                style={{
                  marginLeft: '16px',
                  background: 'var(--gray-bg)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  padding: '2px 10px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--text-muted)',
                }}
              >
                {filtered.length} of {awards.length} awards shown
              </span>
            )}
          </p>
        </div>

        {/* Filter bar */}
        <FilterBar
          filters={filters}
          onChange={handleFilterChange}
          onFetch={handleFetch}
          onMockFetch={handleMockFetch}
          loading={loading}
        />

        {/* Error / Warning */}
        {error && (
          <div className={error.startsWith('⚠️') ? 'warn-banner' : 'error-banner'}>
            {error.startsWith('⚠️') ? error : <><strong>Error:</strong> {error}</>}
          </div>
        )}

        {/* Stats */}
        {awards.length > 0 && <SummaryStats awards={filtered} />}

        {/* Table */}
        {loading ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '12px',
              padding: '56px 0',
              color: 'var(--text-muted)',
            }}
          >
            <span className="spinner spinner-dark" />
            <span>Loading awards…</span>
          </div>
        ) : (
          <AwardTable awards={filtered} />
        )}
      </main>
    </>
  )
}
