import { Link } from '@tanstack/react-router'
import { progress } from '@/data'
import { cn } from '@/lib/utils'
import { MdText } from '@/components/md-text'

/** Checklist task states, in bar order. N/A tasks are left out of bars. */
export const taskStates = [
  { key: 'DONE', label: 'Done', color: 'var(--status-decided)' },
  { key: 'IN_PROGRESS', label: 'In progress', color: 'var(--brand)' },
  { key: 'BLOCKED', label: 'Blocked', color: 'var(--destructive)' },
  { key: 'OPEN', label: 'Open', color: 'var(--status-open)' },
  { key: 'DEFERRED', label: 'Deferred', color: 'var(--status-candidate)' },
]

const NA = { key: 'N/A', label: 'N/A', color: 'var(--muted-foreground)' }

/** Every state a task can have, for filters: the bar states, then N/A. */
export const allTaskStates = [...taskStates, NA]

export function taskState(status: string) {
  return (
    allTaskStates.find((s) => s.key === status) ?? {
      key: status,
      label: status,
      color: 'var(--muted-foreground)',
    }
  )
}

/** Stacked bar of task counts per state for one gate. */
export function GateBar({
  counts,
  className,
}: {
  counts: Record<string, number>
  className?: string
}) {
  const parts = taskStates.map((s) => ({ ...s, n: counts[s.key] ?? 0 }))
  const total = parts.reduce((t, p) => t + p.n, 0)
  return (
    <div
      className={cn(
        'flex h-2.5 overflow-hidden rounded-full bg-muted',
        className
      )}
      role='img'
      aria-label={parts
        .filter((p) => p.n)
        .map((p) => `${p.n} ${p.label.toLowerCase()}`)
        .join(', ')}
    >
      {parts.map(
        (p) =>
          p.n > 0 && (
            <span
              key={p.key}
              title={`${p.label}: ${p.n}`}
              style={{
                width: `${(p.n / total) * 100}%`,
                background: p.color,
              }}
            />
          )
      )}
    </div>
  )
}

/** Colour key for the gate bars. */
export function TaskLegend() {
  return (
    <div className='flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground'>
      {taskStates.map((s) => (
        <span key={s.key} className='flex items-center gap-1.5'>
          <span
            className='size-2.5 rounded-sm'
            style={{ background: s.color }}
          />
          {s.label}
        </span>
      ))}
    </div>
  )
}

/** A task status as a small coloured badge. */
export function StatusBadge({ status }: { status: string }) {
  const s = taskState(status)
  return (
    <span
      className='inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[11px] leading-none whitespace-nowrap'
      style={{
        color: s.color,
        borderColor: `color-mix(in oklab, ${s.color} 50%, transparent)`,
      }}
    >
      {s.key}
    </span>
  )
}

/** A checklist task ID (P2-017) as a chip that opens its Checklist row. */
export function TaskChip({ id }: { id: string }) {
  const task = progress.tasks[id]
  const s = task ? taskState(task.status) : undefined
  const color = s?.color ?? 'var(--muted-foreground)'
  if (!task) return <MdText text={id} />
  return (
    <Link
      to='/checklist'
      search={{ id }}
      title={`${id}: ${s?.label ?? task.status}`}
      className='inline-flex items-center rounded border px-1 py-px align-baseline font-mono text-[11px] leading-none whitespace-nowrap hover:opacity-80'
      style={{
        color,
        borderColor: `color-mix(in oklab, ${color} 50%, transparent)`,
      }}
    >
      {id}
    </Link>
  )
}

/** Record text with each checklist task ID (P2-017) as a chip. */
export function TaskText({ text }: { text: string }) {
  return text
    .split(/\b(P\d-\d{3})\b/)
    .map((part, i) =>
      i % 2 ? (
        <TaskChip key={i} id={part} />
      ) : (
        part && <MdText key={i} text={part} />
      )
    )
}
