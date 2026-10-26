import { memo } from 'react'
import { type Block, openItems, statusOf } from '@/data'
import { Handle, Position, type Node, type NodeProps } from '@xyflow/react'
import { ChevronsRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { blockColor, kindInfo } from './kinds'
import { type HandleSpec, type Side, TALL, cableSide } from './layout'
import { draw } from './style'

export type BlockNodeType = Node<
  { block: Block; w: number; h: number; handles?: HandleSpec[]; dim?: boolean },
  'block'
>

const position: Record<Side, Position> = {
  left: Position.Left,
  right: Position.Right,
  top: Position.Top,
  bottom: Position.Bottom,
}

/**
 * Handle offset so it lands at `pos` of the outer box, as layout.ts assumes.
 * A handle is placed in the padding box, inside the border.
 */
const handleAt = (pos: number) =>
  `calc(${pos * 100}% + ${(2 * pos - 1) * draw.border}px)`

function BlockNodeImpl({ data, selected }: NodeProps<BlockNodeType>) {
  const { block, w, h, handles, dim } = data
  const k = kindInfo[block.kind]
  const color = blockColor(block)
  const status = statusOf(block)
  const open = openItems(block).length
  // MCUs and the board are large: icon and text centered, bigger type
  const big = block.kind === 'mcu' || block.kind === 'board'
  // tall small blocks (servo headers, PDB) stack icon and text, centred, so
  // the name gets the full width
  const tall = !big && h >= TALL
  // connectors: square corners and a solid tab where the cable plugs in
  const port = block.kind === 'connector'
  const tab = port ? cableSide(handles ?? []) : null
  return (
    <div
      style={{
        width: w,
        height: h,
        borderWidth: draw.border,
        borderRadius: port ? draw.port.radius : draw.radius,
        ['--k' as string]: color,
      }}
      className={cn(
        'group relative flex items-center bg-card px-3 text-card-foreground shadow-sm transition-[opacity,box-shadow,border-color]',
        big
          ? 'flex-col justify-center gap-3 text-center'
          : tall
            ? 'flex-col justify-center gap-2 text-center'
            : 'gap-2.5',
        'border-[color-mix(in_oklab,var(--k)_45%,var(--border))]',
        'hover:border-[var(--k)] hover:shadow-[0_0_0_1px_var(--k),0_8px_24px_-8px_color-mix(in_oklab,var(--k)_55%,transparent)]',
        status === 'candidate' && 'border-dashed',
        block.kind === 'board' &&
          'bg-[linear-gradient(135deg,color-mix(in_oklab,var(--brand)_22%,var(--card)),var(--card))]',
        selected && 'shadow-[0_0_0_2px_var(--k)]',
        dim && 'opacity-30'
      )}
    >
      {tab && (
        <span
          aria-hidden
          className='absolute bg-[var(--k)]'
          style={
            tab === 'left' || tab === 'right'
              ? { [tab]: 0, top: 0, bottom: 0, width: draw.port.tab }
              : { [tab]: 0, left: 0, right: 0, height: draw.port.tab }
          }
        />
      )}
      {handles ? (
        handles.map((hd) => (
          <Handle
            key={hd.id}
            id={hd.id}
            type={hd.type}
            position={position[hd.side]}
            className='!min-h-0 !min-w-0 !border-0'
            style={{
              width: draw.dot,
              height: draw.dot,
              background: 'var(--k)',
              ...(hd.side === 'left' || hd.side === 'right'
                ? { top: handleAt(hd.pos) }
                : { left: handleAt(hd.pos) }),
            }}
          />
        ))
      ) : (
        <Handle type='target' position={Position.Left} className='!opacity-0' />
      )}
      <span
        className={cn(
          'flex shrink-0 items-center justify-center rounded-md',
          big ? 'size-12' : 'size-8'
        )}
        style={{
          color,
          background: `color-mix(in oklab, ${color} 16%, transparent)`,
        }}
      >
        <k.icon className={big ? 'size-6' : 'size-4'} />
      </span>
      <div
        className={cn(
          'min-w-0 leading-tight',
          big || tall ? 'w-full' : 'flex-1'
        )}
      >
        <div
          className={cn(
            'truncate font-semibold',
            big ? 'text-2xl' : 'text-[15px]'
          )}
        >
          {block.label}
        </div>
        {block.sub && (
          <div
            className={cn(
              'truncate font-mono text-muted-foreground',
              big ? 'mt-1 text-base' : 'text-[12px]'
            )}
          >
            {block.sub}
          </div>
        )}
      </div>
      {open > 0 && (
        <span
          title={`${open} open item(s)`}
          className='absolute -top-2 -right-2 flex size-5 items-center justify-center rounded-full border border-status-open/60 bg-background text-[10px] font-bold text-status-open'
        >
          {open}
        </span>
      )}
      {block.drill && (
        <ChevronsRight
          className={cn(
            'shrink-0 text-primary',
            big
              ? 'absolute top-1/2 right-3 size-5 -translate-y-1/2'
              : tall
                ? 'absolute top-1/2 right-2 size-4 -translate-y-1/2'
                : 'size-4'
          )}
        />
      )}
      {!handles && (
        <Handle
          type='source'
          position={Position.Right}
          className='!opacity-0'
        />
      )}
    </div>
  )
}

export const BlockNode = memo(BlockNodeImpl)
