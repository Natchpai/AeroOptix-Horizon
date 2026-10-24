import { Link as RouterLink } from '@tanstack/react-router'
import {
  type Block,
  type Link,
  type Mcu,
  type PinRow,
  blockById,
  busInfo,
  linkSignals,
  mcuInfo,
} from '@/data'
import { cn } from '@/lib/utils'
import { kindInfo } from './kinds'

type End = { mcu: Mcu; row: PinRow } | undefined
type Row = { key: string; name: string; left: End; right: End }

function rowsFor(link: Link, right: Block): Row[] {
  return linkSignals(link).map((s) => {
    if (s.b) return { key: s.key, name: s.name, left: s.a, right: s.b }
    const onRight = !!s.a && right.mcu === s.a.mcu
    return {
      key: s.key,
      name: s.name,
      left: onRight ? undefined : s.a,
      right: onRight ? s.a : undefined,
    }
  })
}

/**
 * Level 2: one line per signal between the two ends of a link, with the
 * MCU pin name, package pin and signal at each end. Ends the docs don't
 * give stay TBD.
 */
export function InterfaceView({ link }: { link: Link }) {
  const from = blockById.get(link.from)!
  const to = blockById.get(link.to)!
  const rows = rowsFor(link, to)
  const color = busInfo[link.bus].color

  return (
    <div className='h-full overflow-auto p-4 sm:p-6 md:pe-[25rem]'>
      <div className='mx-auto max-w-5xl'>
        <div className='mb-4 flex flex-wrap items-center gap-2'>
          <span
            className='rounded-md border px-2 py-0.5 font-mono text-xs font-semibold'
            style={{
              color,
              borderColor: `color-mix(in oklab, ${color} 50%, transparent)`,
              background: `color-mix(in oklab, ${color} 12%, transparent)`,
            }}
          >
            {busInfo[link.bus].label}
          </span>
          <h2 className='text-lg font-semibold tracking-tight'>{link.label}</h2>
          <span className='text-sm text-muted-foreground'>
            {from.label} → {to.label}
          </span>
        </div>

        {rows.length === 0 ? (
          <div className='rounded-lg border border-dashed p-6 text-sm text-muted-foreground'>
            No MCU pins on this link. Net names, connector pins and wiring are
            not in the design records yet (TBD). See the source IDs in the
            panel.
          </div>
        ) : (
          <div className='grid grid-cols-[minmax(0,1fr)_minmax(5rem,1.1fr)_minmax(0,1fr)] overflow-hidden rounded-xl border bg-card'>
            <EndHeader block={from} side='left' />
            <div className='border-b bg-muted/30' />
            <EndHeader block={to} side='right' />
            {rows.map((r, i) => (
              <RowView
                key={r.key}
                row={r}
                color={color}
                last={i === rows.length - 1}
              />
            ))}
          </div>
        )}

        <p className='mt-3 text-xs text-muted-foreground'>
          MCU pins come from the pin allocation record. Far-end pins (sensor,
          connector) are not in the records, so they show TBD. Click a pin to
          open it in the pinout.
        </p>
      </div>
    </div>
  )
}

function EndHeader({ block, side }: { block: Block; side: 'left' | 'right' }) {
  const k = kindInfo[block.kind]
  return (
    <div
      className={cn(
        'flex items-center gap-2 border-b px-3 py-2.5',
        side === 'right' && 'flex-row-reverse text-end'
      )}
      style={{ background: `color-mix(in oklab, ${k.color} 10%, var(--card))` }}
    >
      <k.icon className='size-4 shrink-0' style={{ color: k.color }} />
      <div className='min-w-0 leading-tight'>
        <div className='truncate text-sm font-semibold'>{block.label}</div>
        {block.sub && (
          <div className='truncate font-mono text-[11px] text-muted-foreground'>
            {block.sub}
          </div>
        )}
      </div>
    </div>
  )
}

function RowView({
  row,
  color,
  last,
}: {
  row: Row
  color: string
  last: boolean
}) {
  return (
    <>
      <PinCell end={row.left} side='left' last={last} />
      <div
        className={cn(
          'relative flex items-center px-1',
          !last && 'border-b border-border/50'
        )}
      >
        <div
          className='h-0.5 w-full rounded-full'
          style={{ background: color }}
        />
        <span
          className='absolute inset-x-0 top-1/2 mx-auto w-fit max-w-[95%] -translate-y-1/2 truncate rounded border px-1.5 py-px font-mono text-[10.5px] font-semibold'
          style={{
            color,
            borderColor: `color-mix(in oklab, ${color} 45%, transparent)`,
            background: `color-mix(in oklab, ${color} 10%, var(--card))`,
          }}
          title={row.name}
        >
          {row.name}
        </span>
        <span
          className='absolute top-1/2 -left-1 size-2 -translate-y-1/2 rounded-full'
          style={{ background: color }}
        />
        <span
          className='absolute top-1/2 -right-1 size-2 -translate-y-1/2 rounded-full'
          style={{ background: color }}
        />
      </div>
      <PinCell end={row.right} side='right' last={last} />
    </>
  )
}

function PinCell({
  end,
  side,
  last,
}: {
  end: End
  side: 'left' | 'right'
  last: boolean
}) {
  const base = cn(
    'flex min-h-12 flex-col justify-center px-3 py-1.5',
    side === 'left' ? 'items-end text-end' : 'items-start text-start',
    !last && 'border-b border-border/50'
  )
  if (!end)
    return (
      <div className={base}>
        <span className='rounded border border-dashed border-status-candidate/60 px-1.5 font-mono text-xs text-status-candidate'>
          TBD
        </span>
      </div>
    )
  const { mcu, row } = end
  return (
    <RouterLink
      to='/pinout'
      search={{ mcu, pin: row.pin }}
      className={cn(base, 'transition-colors hover:bg-accent/50')}
    >
      <span className='flex items-baseline gap-1.5'>
        <span className='text-[10px] text-muted-foreground'>
          {mcuInfo[mcu].label}
        </span>
        <span className='font-mono text-sm font-bold'>{row.pin}</span>
        {row.number !== null && (
          <span className='font-mono text-[10px] text-muted-foreground'>
            #{row.number}
          </span>
        )}
      </span>
      <span className='truncate font-mono text-[11px] text-muted-foreground'>
        {row.signal}
      </span>
    </RouterLink>
  )
}
