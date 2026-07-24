import { BarChart3, FileUp, Files, Menu, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/transcripts', label: 'Transcripts', icon: Files },
  { to: '/upload', label: 'New analysis', icon: FileUp },
]

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/10 bg-ink px-5 text-white lg:hidden">
        <Brand />
        <button aria-label="Toggle navigation" onClick={() => setOpen((value) => !value)}>
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </header>

      <aside className={`${open ? 'block' : 'hidden'} fixed inset-x-0 top-16 z-20 bg-ink p-5 text-white lg:sticky lg:top-0 lg:block lg:h-screen lg:p-7`}>
        <Brand />
        <p className="mt-8 text-[11px] font-semibold uppercase tracking-[0.2em] text-white/40">Workspace</p>
        <nav className="mt-3 space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive ? 'bg-white text-ink' : 'text-white/65 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-10 rounded-2xl border border-white/10 bg-white/[0.06] p-4 lg:absolute lg:bottom-7 lg:left-7 lg:right-7">
          <div className="flex items-center gap-2 text-xs font-semibold text-mint">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            FinBERT pipeline
          </div>
          <p className="mt-2 text-xs leading-5 text-white/45">Explainable sentiment, from call to claim.</p>
        </div>
      </aside>

      <main className="min-w-0 p-5 sm:p-8 xl:p-11">{children}</main>
    </div>
  )
}

function Brand() {
  return (
    <NavLink to="/transcripts" className="flex items-center gap-3">
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-mint text-moss">
        <BarChart3 size={20} strokeWidth={2.5} />
      </span>
      <span>
        <span className="block text-sm font-bold tracking-tight">SignalCall</span>
        <span className="block text-[10px] uppercase tracking-[0.17em] text-white/40">Earnings intelligence</span>
      </span>
    </NavLink>
  )
}
