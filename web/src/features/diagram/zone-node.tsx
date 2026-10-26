import { memo } from 'react'
import type { Node, NodeProps } from '@xyflow/react'
import { draw } from './style'

export type ZoneNodeType = Node<
  { label: string; w: number; h: number; center?: boolean },
  'zone'
>

/** A titled box behind a group of blocks; it takes no clicks. */
function ZoneNodeImpl({ data }: NodeProps<ZoneNodeType>) {
  return (
    <div
      style={{
        width: data.w,
        height: data.h,
        borderRadius: draw.zone.radius,
        paddingLeft: draw.zone.pad,
        paddingRight: draw.zone.pad,
        textAlign: data.center ? 'center' : 'left',
        lineHeight: `${draw.zone.head + draw.zone.pad / 2}px`,
        fontSize: draw.zone.font,
      }}
      className='pointer-events-none border border-[color-mix(in_oklab,var(--brand)_30%,var(--border))] bg-[color-mix(in_oklab,var(--brand)_6%,transparent)] font-semibold tracking-wider text-muted-foreground uppercase'
    >
      {data.label}
    </div>
  )
}

export const ZoneNode = memo(ZoneNodeImpl)
