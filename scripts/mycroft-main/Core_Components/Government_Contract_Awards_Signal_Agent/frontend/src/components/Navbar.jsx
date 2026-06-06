import React, { useState, useEffect } from 'react'
import { getHealth } from '../services/api'

const navStyle = {
  background: 'var(--navy)',
  color: '#fff',
  padding: '0 24px',
  height: '60px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
  position: 'sticky',
  top: 0,
  zIndex: 100,
}

const logoStyle = {
  fontSize: '1.15rem',
  fontWeight: 700,
  letterSpacing: '-0.01em',
  color: '#fff',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
}

const subtitleStyle = {
  fontSize: '0.7rem',
  fontWeight: 400,
  color: 'rgba(255,255,255,0.55)',
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  marginLeft: '4px',
}

const statusBoxStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  background: 'rgba(255,255,255,0.07)',
  border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: '20px',
  padding: '5px 14px',
  fontSize: '0.8rem',
  fontWeight: 500,
  color: 'rgba(255,255,255,0.9)',
}

export default function Navbar() {
  const [status, setStatus] = useState('checking') // 'checking' | 'live' | 'offline'

  useEffect(() => {
    const check = () => {
      getHealth()
        .then(() => setStatus('live'))
        .catch(() => setStatus('offline'))
    }
    check()
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <nav style={navStyle}>
      {/* Left: Brand */}
      <div style={logoStyle}>
        <span style={{ fontSize: '1.35rem' }}>🏛</span>
        <span>GovSignal</span>
        <span style={subtitleStyle}>Contract Intelligence</span>
      </div>

      {/* Right: API Status */}
      <div style={statusBoxStyle}>
        {status === 'checking' ? (
          <>
            <span
              style={{
                display: 'inline-block',
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: '#94a3b8',
              }}
            />
            <span>Checking…</span>
          </>
        ) : status === 'live' ? (
          <>
            <span className="status-dot live" />
            <span>API Live</span>
          </>
        ) : (
          <>
            <span className="status-dot offline" />
            <span>API Offline</span>
          </>
        )}
      </div>
    </nav>
  )
}
