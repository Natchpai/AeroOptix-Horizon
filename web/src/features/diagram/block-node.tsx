import { memo } from 'react'
import { type Block, openItems, statusOf } from '@/data'
import { Handle, Position, type Node, type NodeProps } from '@xyflow/react'
import { ChevronsRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { kindInfo } from './kinds'
import type { HandleSpec, Side } from './layout'

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

function BlockNodeImpl({ data, selected }: NodeProps<BlockNodeType>) {
  const { block, w, h, handles, dim } = data
  const k = kindInfo[block.kind]
  const status = statusOf(block)
  const open = openItems(block).length
  // MCUs and the board are large: icon and text centered, bigger type
  const big = block.kind === 'mcu' || block.kind === 'board'
  return (
    <div
      style={{ width: w, height: h, ['--k' as string]: k.color }}
      className={cn(
        'group relative flex items-center rounded-lg border bg-card px-3 text-card-foreground shadow-sm transition-[opacity,box-shadow,border-color]',
        big ? 'flex-col justify-center gap-3 text-center' : 'gap-2.5',
        'border-[color-mix(in_oklab,var(--k)_45%,var(--border))]',
        'hover:border-[var(--k)] hover:shadow-[0_0_0_1px_var(--k),0_8px_24px_-8px_color-mix(in_oklab,var(--k)_55%,transparent)]',
        status === 'candidate' && 'border-dashed',
        block.kind === 'board' &&
          'bg-[linear-gradient(135deg,color-mix(in_oklab,var(--brand)_22%,var(--card)),var(--card))]',
        selected && 'shadow-[0_0_0_2px_var(--k)]',
        dim && 'opacity-30'
      )}
    >
      {handles ? (
        handles.map((hd) => (
          <Handle
            key={hd.id}
            id={hd.id}
            type={hd.type}
            position={position[hd.side]}
            className='!size-1.5 !min-h-0 !min-w-0 !border-0'
            style={{
              background: 'var(--k)',
              ...(hd.side === 'left' || hd.side === 'right'
                ? { top: `${hd.pos * 100}%` }
                : { left: `${hd.pos * 100}%` }),
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
          color: k.color,
          background: `color-mix(in oklab, ${k.color} 16%, transparent)`,
        }}
      >
        <k.icon className={big ? 'size-6' : 'size-4'} />
      </span>
      <div className={cn('min-w-0 leading-tight', big ? 'w-full' : 'flex-1')}>
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
            big ? 'absolute top-1/2 right-3 size-5 -translate-y-1/2' : 'size-4'
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
