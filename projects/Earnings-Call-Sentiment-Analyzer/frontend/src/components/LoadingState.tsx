export function LoadingState({ label = 'Loading analysis' }: { label?: string }) {
  return (
    <div className="panel grid min-h-72 place-items-center p-8 text-center">
      <div>
        <span className="mx-auto block h-9 w-9 animate-spin rounded-full border-[3px] border-moss/20 border-t-moss" />
        <p className="mt-4 text-sm font-medium text-ink/55">{label}</p>
      </div>
    </div>
  )
}
