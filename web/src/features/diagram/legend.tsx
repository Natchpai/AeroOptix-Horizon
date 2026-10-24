import { useState } from 'react'
import { type Bus, type Level, blocksAt, busInfo, linksAt } from '@/data'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { draw } from './style'

/** Colour key for the rails and buses on the current level, plus line styles. */
export function Legend({ level }: { level: Level }) {
  const [open, setOpen] = useState(false)
  const used = new Set<Bus | undefined>([
    ...linksAt(level).map((l) => l.bus),
    ...blocksAt(level).map((b) => b.rail),
  ])
  const all = (Object.keys(busInfo) as Bus[]).filter((b) => used.has(b))
  const groups = [
    { title: 'Power rails', buses: all.filter((b) => busInfo[b].power) },
    { title: 'Signals', buses: all.filter((b) => !busInfo[b].power) },
  ]
  return (
    <div className='absolute bottom-3 left-3 z-10 hidden max-w-xs rounded-lg border bg-popover/90 text-xs shadow-lg backdrop-blur md:block'>
      <button
        onClick={() => setOpen(!open)}
        className='flex w-full items-center justify-between gap-4 px-3 py-1.5 font-semibold'
      >
        Legend
        {open ? (
          <ChevronDown className='size-3.5' />
        ) : (
          <ChevronUp className='size-3.5' />
        )}
      </button>
      {open && (
        <div className='space-y-2 border-t px-3 py-2'>
          {groups.map(
            (g) =>
              g.buses.length > 0 && (
                <div key={g.title}>
                  <div className='mb-1 text-[10px] font-semibold tracking-wide text-muted-foreground uppercase'>
                    {g.title}
                  </div>
                  <div className='grid grid-cols-2 gap-x-4 gap-y-1'>
                    {g.buses.map((b) => (
                      <span key={b} className='flex items-center gap-1.5'>
                        <LineSample
                          color={busInfo[b].color}
                          power={busInfo[b].power}
                        />
                        {busInfo[b].label}
                      </span>
                    ))}
                  </div>
                </div>
              )
          )}
          <div className='space-y-1 border-t pt-2 text-muted-foreground'>
            <span className='flex items-center gap-1.5'>
              <LineSample color='currentColor' candidate />
              <LineSample color='currentColor' power candidate />
              Dashed signal or faded power line: candidate, TBD
            </span>
            <span className='flex items-center gap-1.5'>
              <svg width='20' height='12' className='shrink-0'>
                <rect
                  x={draw.border / 2}
                  y={draw.border / 2}
                  width={20 - draw.border}
                  height={12 - draw.border}
                  rx='3'
                  fill='none'
                  stroke='currentColor'
                  strokeWidth={draw.border}
                  strokeDasharray={draw.dash.block}
                />
              </svg>
              Dashed block border: candidate part
            </span>
            <span className='flex items-center gap-1.5'>
              <span className='flex size-4 items-center justify-center rounded-full border border-status-open/60 text-[9px] font-bold text-status-open'>
                n
              </span>
              Open items on a block
            </span>
            <span>Click a block for details, a link for its pins.</span>
          </div>
        </div>
      )}
    </div>
  )
}

/** A short line drawn as on the canvas: width, dash and fade from style.ts. */
function LineSample({
  color,
  power = false,
  candidate = false,
}: {
  color: string
  power?: boolean
  candidate?: boolean
}) {
  const kind = power ? 'power' : 'signal'
  const w = power ? 20 : 16
  const h = Math.ceil(draw.line[kind])
  return (
    <svg width={w} height={h} className='shrink-0'>
      <line
        x1='0'
        y1={h / 2}
        x2={w}
        y2={h / 2}
        stroke={color}
        strokeWidth={draw.line[kind]}
        strokeDasharray={candidate && !power ? draw.dash.signal : undefined}
        strokeOpacity={candidate && power ? draw.candidatePower : undefined}
      />
    </svg>
  )
}
