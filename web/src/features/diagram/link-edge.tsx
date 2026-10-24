import { memo } from 'react'
import { type Link, busInfo, statusOf } from '@/data'
import {
  EdgeLabelRenderer,
  getSmoothStepPath,
  type Edge,
  type EdgeProps,
} from '@xyflow/react'
import { cn } from '@/lib/utils'
import { draw } from './style'

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
  const { color, power } = busInfo[link.bus]
  const status = statusOf(link)
  // power lines are thick and never dashed; a candidate one is faded
  const faded = power && status === 'candidate'
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
  // beside the line (a small gap clear) or centered on it
  const gap = draw.label.gap
  const anchor =
    labelSide === 'left'
      ? `translate(-100%, -50%) translate(${lx - gap}px, ${ly}px)`
      : labelSide === 'right'
        ? `translate(0, -50%) translate(${lx + gap}px, ${ly}px)`
        : `translate(-50%, -50%) translate(${lx}px, ${ly}px)`
  const strong = selected || hot
  const kind = power ? 'power' : 'signal'
  return (
    <>
      {/* wide invisible path makes the edge easy to click */}
      <path
        d={d}
        fill='none'
        stroke='transparent'
        strokeWidth={draw.hit[kind]}
        className='react-flow__edge-interaction'
      />
      <path
        id={id}
        d={d}
        fill='none'
        stroke={color}
        strokeWidth={(strong ? draw.lineStrong : draw.line)[kind]}
        strokeDasharray={
          !power && status === 'candidate' ? draw.dash.signal : undefined
        }
        strokeOpacity={dim ? 0.15 : faded ? draw.candidatePower : 1}
        className={cn(
          'transition-[stroke-width,stroke-opacity]',
          strong && 'drop-shadow-[0_0_6px_currentColor]'
        )}
        style={{ color }}
      />
      <EdgeLabelRenderer>
        <div
          className={cn(
            'nodrag nopan pointer-events-auto absolute flex cursor-pointer items-center rounded border font-mono whitespace-nowrap shadow-sm transition-opacity',
            status === 'open' && 'ring-1 ring-status-open/50',
            dim && 'opacity-20'
          )}
          style={{
            transform: anchor,
            height: draw.label.height,
            paddingInline: draw.label.padX,
            fontSize: draw.label.font,
            lineHeight: 1,
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
