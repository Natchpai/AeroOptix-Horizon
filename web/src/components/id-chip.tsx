import { Link } from '@tanstack/react-router'
import { ids, idTitle, sourceUrl } from '@/data'
import { REQ_KINDS } from '@/lib/spec-ids'
import { cn } from '@/lib/utils'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'

/**
 * A spec ID (IF-010, DEC-014, OPEN-017) linked to its row on the site:
 * decisions on the Decisions page, open items on the Open items page,
 * requirements on the Traceability page. Other kinds (REF ...) open their
 * spec row on GitHub. Each site page links the spec line in its detail row.
 */
export function IdChip({
  id,
  className,
  plain,
}: {
  id: string
  className?: string
  /** No link: for the ID column of the ID's own page, where the row opens. */
  plain?: boolean
}) {
  const s = ids[id]
  const isOpen = s?.kind === 'OPEN' && !s.closed
  const cls = cn(
    'inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[11px] leading-none whitespace-nowrap transition-colors',
    isOpen
      ? 'border-status-open/50 text-status-open hover:bg-status-open/10'
      : 'border-primary/40 text-primary hover:bg-primary/10',
    s?.closed && 'line-through opacity-60',
    !s && 'border-dashed text-muted-foreground',
    className
  )
  const chip =
    !s || plain ? (
      <span className={cls}>{id}</span>
    ) : s.kind === 'DEC' ? (
      <Link to='/decisions' search={{ id }} className={cls}>
        {id}
      </Link>
    ) : s.kind === 'OPEN' ? (
      <Link to='/open' search={{ id }} className={cls}>
        {id}
      </Link>
    ) : REQ_KINDS.includes(s.kind) ? (
      <Link to='/trace' search={{ id }} className={cls}>
        {id}
      </Link>
    ) : (
      <a
        href={sourceUrl(s.file, s.line)}
        target='_blank'
        rel='noreferrer'
        className={cls}
      >
        {id}
      </a>
    )
  if (!s) return chip
  return (
    <Tooltip>
      <TooltipTrigger asChild>{chip}</TooltipTrigger>
      <TooltipContent className='max-w-80 text-xs'>
        <div className='font-semibold'>{idTitle(id)}</div>
        <div className='opacity-80'>{s.section}</div>
      </TooltipContent>
    </Tooltip>
  )
}

export function IdList({ list }: { list: string[] }) {
  return (
    <div className='flex flex-wrap gap-1'>
      {list.map((id) => (
        <IdChip key={id} id={id} />
      ))}
    </div>
  )
}
