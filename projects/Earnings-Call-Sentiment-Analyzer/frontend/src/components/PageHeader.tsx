import type { ReactNode } from 'react'

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-moss">{eyebrow}</p>
        <h1 className="mt-2 text-3xl font-bold tracking-[-0.04em] text-ink sm:text-4xl">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-ink/55">{description}</p>
      </div>
      {actions}
    </div>
  )
}
