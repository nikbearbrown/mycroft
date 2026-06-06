import React from 'react'

const barStyle = {
  background: '#fff',
  border: '1px solid var(--border)',
  borderRadius: '10px',
  padding: '18px 20px',
  marginBottom: '24px',
  boxShadow: '0 1px 3px rgba(0,0,0,.06)',
}

const rowStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  alignItems: 'flex-end',
  gap: '16px',
}

const fieldStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '5px',
}

const labelStyle = {
  fontSize: '0.72rem',
  fontWeight: 600,
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
}

const sliderValueStyle = {
  fontSize: '0.78rem',
  fontWeight: 600,
  color: 'var(--accent)',
  minWidth: '30px',
  textAlign: 'right',
}

export default function FilterBar({ filters, onChange, onFetch, onMockFetch, loading }) {
  const handleChange = (field, value) => {
    onChange({ ...filters, [field]: value })
  }

  return (
    <div style={barStyle}>
      <div style={rowStyle}>
        {/* Keyword */}
        <div style={{ ...fieldStyle, flex: '1 1 240px' }}>
          <label style={labelStyle}>Keyword</label>
          <input
            type="text"
            className="form-input"
            style={{ width: '100%' }}
            placeholder="e.g. artificial intelligence"
            value={filters.keyword}
            onChange={(e) => handleChange('keyword', e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onFetch()}
          />
        </div>

        {/* Agency Type */}
        <div style={fieldStyle}>
          <label style={labelStyle}>Agency Type</label>
          <select
            className="form-select"
            value={filters.agency_type}
            onChange={(e) => handleChange('agency_type', e.target.value)}
          >
            <option value="All">All</option>
            <option value="DoD">DoD</option>
            <option value="Intel">Intel</option>
            <option value="Civilian">Civilian</option>
            <option value="Unknown">Unknown</option>
          </select>
        </div>

        {/* Limit */}
        <div style={fieldStyle}>
          <label style={labelStyle}>Limit</label>
          <input
            type="number"
            className="form-input"
            min={10}
            max={1000}
            value={filters.limit}
            onChange={(e) =>
              handleChange('limit', Math.max(10, Math.min(1000, Number(e.target.value))))
            }
          />
        </div>

        {/* Min Score slider */}
        <div style={fieldStyle}>
          <label style={labelStyle}>Min Score</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={filters.minScore}
              onChange={(e) => handleChange('minScore', parseFloat(e.target.value))}
            />
            <span style={sliderValueStyle}>{filters.minScore.toFixed(2)}</span>
          </div>
        </div>

        {/* Fetch buttons */}
        <div style={{ ...fieldStyle, justifyContent: 'flex-end', gap: '8px', flexDirection: 'row', alignItems: 'flex-end' }}>
          <button
            className="btn-primary"
            onClick={onFetch}
            disabled={loading}
            style={{ height: '38px' }}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Fetching…
              </>
            ) : (
              <>
                <span>⬇</span>
                Fetch Awards
              </>
            )}
          </button>
          <button
            className="btn-secondary"
            onClick={onMockFetch}
            disabled={loading}
            style={{ height: '38px', fontSize: '0.8rem' }}
            title="Load sample data with AI briefs (use when SAM.gov quota is reached)"
          >
            🧪 Mock Data
          </button>
        </div>
      </div>
    </div>
  )
}
