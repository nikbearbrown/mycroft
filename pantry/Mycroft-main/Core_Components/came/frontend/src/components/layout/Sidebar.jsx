import { NavLink } from 'react-router-dom'
import clsx from 'clsx'

const NAV = [
  { path: '/',          label: 'Strategy',    icon: '◈' },
  { path: '/flow',      label: 'Capital Flow', icon: '⟶' },
  { path: '/drift',     label: 'Drift',        icon: '△' },
  { path: '/metrics',   label: 'Metrics',      icon: '▦' },
  { path: '/events',    label: 'Events',       icon: '⊞' },
  { path: '/simulate',  label: 'Simulate',     icon: '⟳' },
]

export default function Sidebar() {
  return (
    <aside className="w-52 shrink-0 bg-surface border-r border-border flex flex-col h-screen sticky top-0">
      <div className="px-4 py-5 border-b border-border">
        <div className="text-accent text-xs tracking-widest uppercase font-semibold">CAME</div>
        <div className="text-muted text-xs mt-0.5">Capital Allocation</div>
        <div className="text-muted text-xs">Memory Engine</div>
      </div>
      <nav className="flex-1 py-3">
        {NAV.map(({ path, label, icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-2.5 text-sm transition-colors',
                isActive
                  ? 'text-accent bg-accent/5 border-r-2 border-accent'
                  : 'text-muted hover:text-text hover:bg-white/[0.02]'
              )
            }
          >
            <span className="text-base leading-none">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-3 border-t border-border">
        <div className="text-muted text-xs">v1.0.0</div>
      </div>
    </aside>
  )
}