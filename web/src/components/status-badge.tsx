import { type Status, statusInfo } from '@/data'
import { cn } from '@/lib/utils'

const tone: Record<Status, string> = {
  decided: 'border-status-decided/50 bg-status-decided/10 text-status-decided',
  open: 'border-status-open/50 bg-status-open/10 text-status-open',
  candidate:
    'border-status-candidate/50 bg-status-candidate/10 text-status-candidate border-dashed',
}

export function StatusBadge({
  status,
  className,
}: {
  status: Status
  className?: string
}) {
  return (
    <span
      title={statusInfo[status].hint}
      className={cn(
        'inline-flex items-center rounded-md border px-1.5 py-0.5 text-[11px] font-medium whitespace-nowrap',
        tone[status],
        className
      )}
    >
      {statusInfo[status].label}
    </span>
  )
}
