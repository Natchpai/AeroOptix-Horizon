import { Fragment, type ReactNode } from 'react'
import { Link as RouterLink } from '@tanstack/react-router'
import { type Table as TanTable, flexRender } from '@tanstack/react-table'
import { type Block, type Link, type SpecId, type Task } from '@/data'
import { levelName } from '@/lib/record-rows'
import { cn } from '@/lib/utils'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { MdText } from '@/components/md-text'
import { TaskChip } from '@/components/task-status'

/**
 * Shared components of the record table pages (Decisions, Open items,
 * Checklist, Spec history, Traceability): the table with a detail row and
 * the lists in a detail row. Helpers are in `src/lib/record-rows.ts`.
 */

/**
 * A TanStack table whose rows open a detail row below them on click. The
 * column `meta.className` hides a column on small screens; `thClassName`
 * sets a header width.
 */
export function RecordTable<T>({
  table,
  openId,
  getId,
  onToggle,
  detail,
  rowClassName,
  empty,
}: {
  table: TanTable<T>
  openId: string | undefined
  getId: (row: T) => string
  onToggle: (id: string) => void
  detail: (row: T) => ReactNode
  rowClassName?: (row: T) => string | false | undefined
  /** Text for an empty result; none shows nothing. */
  empty?: ReactNode
}) {
  const rows = table.getRowModel().rows
  const span = table.getVisibleLeafColumns().length
  return (
    <div className='overflow-x-auto'>
      <Table className='sm:table-fixed'>
        <TableHeader>
          {table.getHeaderGroups().map((hg) => (
            <TableRow key={hg.id}>
              {hg.headers.map((h) => (
                <TableHead
                  key={h.id}
                  className={cn(
                    'first:ps-6',
                    h.column.columnDef.meta?.className,
                    h.column.columnDef.meta?.thClassName
                  )}
                >
                  {flexRender(h.column.columnDef.header, h.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {rows.map((r) => {
            const id = getId(r.original)
            const open = id === openId
            return (
              <Fragment key={r.id}>
                <TableRow
                  id={`row-${id}`}
                  onClick={() => onToggle(id)}
                  data-state={open ? 'selected' : undefined}
                  className={cn(
                    'cursor-pointer scroll-mt-20 align-top data-[state=selected]:bg-primary/10',
                    rowClassName?.(r.original)
                  )}
                >
                  {r.getVisibleCells().map((c) => (
                    <TableCell
                      key={c.id}
                      className={cn(
                        'py-2 align-top whitespace-normal first:ps-6',
                        c.column.columnDef.meta?.className
                      )}
                    >
                      {flexRender(c.column.columnDef.cell, c.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
                {open && (
                  <TableRow className='bg-primary/5 hover:bg-primary/5'>
                    <TableCell
                      colSpan={span}
                      className='px-6 py-3 whitespace-normal'
                    >
                      {detail(r.original)}
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            )
          })}
          {!rows.length && empty && (
            <TableRow>
              <TableCell
                colSpan={span}
                className='px-6 py-6 text-center text-sm text-muted-foreground'
              >
                {empty}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}

/** Diagram blocks and links, each opening its view with the item selected. */
export function DiagramItemList({
  items,
  none = 'Not drawn on any diagram view.',
}: {
  items: (Block | Link)[]
  none?: string
}) {
  if (!items.length)
    return <p className='text-xs text-muted-foreground'>{none}</p>
  return (
    <ul className='space-y-1'>
      {items.map((item) => {
        const isLink = 'from' in item
        return (
          <li key={item.id} className='flex items-baseline gap-1.5'>
            <span className='w-16 shrink-0 text-xs text-muted-foreground'>
              {levelName[item.level]}
            </span>
            <RouterLink
              to='/diagram'
              search={
                isLink
                  ? { level: item.level, link: item.id }
                  : { level: item.level, block: item.id }
              }
              className='min-w-0 [overflow-wrap:anywhere] text-primary hover:underline'
            >
              {isLink ? `${item.label} (link)` : item.label}
            </RouterLink>
          </li>
        )
      })}
    </ul>
  )
}

/** Checklist tasks as status-coloured chips with the start of the task. */
export function TaskRowList({
  tasks,
  none = 'None.',
}: {
  tasks: Task[]
  none?: string
}) {
  if (!tasks.length)
    return <p className='text-xs text-muted-foreground'>{none}</p>
  return (
    <ul className='space-y-1'>
      {tasks.map((t) => (
        <li key={t.id} className='flex items-baseline gap-1.5'>
          <span className='w-16 shrink-0'>
            <TaskChip id={t.id} />
          </span>
          <span className='min-w-0 truncate text-xs text-muted-foreground'>
            <MdText text={t.task} />
          </span>
        </li>
      ))}
    </ul>
  )
}

/**
 * DEC or OPEN rows, each linking to its row on the site page, with a short
 * text. A removed decision or closed item is struck through.
 */
export function SiteRowList({
  rows,
  text,
  none = 'None.',
}: {
  rows: SpecId[]
  text: (row: SpecId) => string
  none?: string
}) {
  if (!rows.length)
    return <p className='text-xs text-muted-foreground'>{none}</p>
  return (
    <ul className='space-y-1'>
      {rows.map((s) => (
        <li key={s.id} className='flex items-baseline gap-1.5'>
          {s.kind === 'DEC' ? (
            <RouterLink
              to='/decisions'
              search={{ id: s.id }}
              className={cn(
                'w-20 shrink-0 font-mono text-xs text-primary hover:underline',
                s.removed && 'line-through opacity-60'
              )}
            >
              {s.id}
            </RouterLink>
          ) : (
            <RouterLink
              to='/open'
              search={{ id: s.id }}
              className={cn(
                'w-20 shrink-0 font-mono text-xs text-primary hover:underline',
                s.closed && 'line-through opacity-60'
              )}
            >
              {s.id}
            </RouterLink>
          )}
          <span className='min-w-0 truncate text-xs text-muted-foreground'>
            <MdText text={text(s)} />
          </span>
        </li>
      ))}
    </ul>
  )
}
