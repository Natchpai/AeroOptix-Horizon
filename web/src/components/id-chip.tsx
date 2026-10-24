import { ids, idTitle, sourceUrl } from '@/data'
import { cn } from '@/lib/utils'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'

/** A spec ID (IF-010, DEC-014, OPEN-017) linked to its row on GitHub. */
export function IdChip({ id, className }: { id: string; className?: string }) {
  const s = ids[id]
  const isOpen = s?.kind === 'OPEN' && !s.closed
  const chip = (
    <a
      href={s ? sourceUrl(s.file, s.line) : undefined}
      target='_blank'
      rel='noreferrer'
      className={cn(
        'inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[11px] leading-none whitespace-nowrap transition-colors',
        isOpen
          ? 'border-status-open/50 text-status-open hover:bg-status-open/10'
          : 'border-primary/40 text-primary hover:bg-primary/10',
        s?.closed && 'line-through opacity-60',
        !s && 'border-dashed text-muted-foreground',
        className
      )}
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
