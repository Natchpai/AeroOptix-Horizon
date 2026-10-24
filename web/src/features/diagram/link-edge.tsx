import { memo } from 'react'
import { type Link, busInfo, statusOf } from '@/data'
import {
  EdgeLabelRenderer,
  getSmoothStepPath,
  type Edge,
  type EdgeProps,
} from '@xyflow/react'
import { cn } from '@/lib/utils'

export type LinkEdgeType = Edge<
  {
    link: Link
    labelAt: number
    labelSide?: 'left' | 'right'
    dim?: boolean
    hot?: boolean
    onPick?: (linkId: string) => void
  },
  'link'
>

/**
 * One link. The placed layout lines both ends up, so the step path is a
 * straight line; it only bends if a block is moved out of line.
 */
function LinkEdgeImpl({
  id,
  data,
  selected,
  sourceX,
  sourceY,
  sourcePosition,
  targetX,
  targetY,
  targetPosition,
}: EdgeProps<LinkEdgeType>) {
  if (!data) return null
  const { link, labelAt, labelSide, dim, hot, onPick } = data
  const color = busInfo[link.bus].color
  const status = statusOf(link)
  const [d] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    borderRadius: 8,
    offset: 18,
  })
  // the line is straight, so the label sits at a fraction along it
  const lx = sourceX + (targetX - sourceX) * labelAt
  const ly = sourceY + (targetY - sourceY) * labelAt
  // beside the line (6 px clear) or centered on it
  const anchor =
    labelSide === 'left'
      ? `translate(-100%, -50%) translate(${lx - 6}px, ${ly}px)`
      : labelSide === 'right'
        ? `translate(0, -50%) translate(${lx + 6}px, ${ly}px)`
        : `translate(-50%, -50%) translate(${lx}px, ${ly}px)`
  const strong = selected || hot
  return (
    <>
      {/* wide invisible path makes the edge easy to click */}
      <path
        d={d}
        fill='none'
        stroke='transparent'
        strokeWidth={14}
        className='react-flow__edge-interaction'
      />
      <path
        id={id}
        d={d}
        fill='none'
        stroke={color}
        strokeWidth={strong ? 3 : 1.75}
        strokeDasharray={status === 'candidate' ? '6 5' : undefined}
        strokeOpacity={dim ? 0.15 : 1}
        className={cn(
          'transition-[stroke-width,stroke-opacity]',
          strong && 'drop-shadow-[0_0_6px_currentColor]'
        )}
        style={{ color }}
      />
      <EdgeLabelRenderer>
        <div
          className={cn(
            'nodrag nopan pointer-events-auto absolute cursor-pointer rounded border px-1.5 py-px font-mono text-[12px] leading-4 whitespace-nowrap shadow-sm transition-opacity',
            status === 'open' && 'ring-1 ring-status-open/50',
            dim && 'opacity-20'
          )}
          style={{
            transform: anchor,
            color,
            borderColor: `color-mix(in oklab, ${color} 45%, transparent)`,
            background: `color-mix(in oklab, ${color} 12%, var(--card))`,
            fontWeight: strong ? 700 : 500,
          }}
          onClick={() => onPick?.(link.id)}
        >
          {link.label}
        </div>
      </EdgeLabelRenderer>
    </>
  )
}

export const LinkEdge = memo(LinkEdgeImpl)
