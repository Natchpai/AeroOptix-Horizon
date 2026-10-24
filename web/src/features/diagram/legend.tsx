import { useState } from 'react'
import { type Bus, type Level, busInfo, linksAt } from '@/data'
import { ChevronDown, ChevronUp } from 'lucide-react'

/** Colour key for the buses on the current level, plus line styles. */
export function Legend({ level }: { level: Level }) {
  const [open, setOpen] = useState(false)
  const used = new Set(linksAt(level).map((l) => l.bus))
  const buses = (Object.keys(busInfo) as Bus[]).filter((b) => used.has(b))
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
          <div className='grid grid-cols-2 gap-x-4 gap-y-1'>
            {buses.map((b) => (
              <span key={b} className='flex items-center gap-1.5'>
                <span
                  className='h-0.5 w-4 rounded-full'
                  style={{ background: busInfo[b].color }}
                />
                {busInfo[b].label}
              </span>
            ))}
          </div>
          <div className='space-y-1 border-t pt-2 text-muted-foreground'>
            <span className='flex items-center gap-1.5'>
              <svg width='16' height='4'>
                <line
                  x1='0'
                  y1='2'
                  x2='16'
                  y2='2'
                  stroke='currentColor'
                  strokeWidth='2'
                  strokeDasharray='4 3'
                />
              </svg>
              Dashed: candidate, TBD
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
