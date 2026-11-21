import { Fragment, useEffect, useMemo, useState } from 'react'
import { getRouteApi, Link as RouterLink } from '@tanstack/react-router'
import {
  type ColumnDef,
  type FilterFn,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import {
  type Block,
  type Link,
  type SpecId,
  blocks,
  ids,
  idTitle,
  links,
  meta,
  sourceUrl,
} from '@/data'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { DataTableColumnHeader } from '@/components/data-table'
import { IdChip } from '@/components/id-chip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { MdText } from '@/components/md-text'
import { TaskChip } from '@/components/task-status'
import { tasksNaming } from './cites'

const route = getRouteApi('/_site/open')

const byId = (a: SpecId, b: SpecId) => a.id.localeCompare(b.id)

/** Every OPEN row of the spec: open rows first, then closed ones. */
const all = Object.values(ids).filter((s) => s.kind === 'OPEN')
const openRows = all.filter((s) => !s.closed).sort(byId)
const closedRows = all.filter((s) => s.closed).sort(byId)

/** Diagram blocks and links that cite each item (refs or open). */
const usedOn = new Map<string, (Block | Link)[]>()
for (const item of [...blocks, ...links])
  for (const r of new Set([...item.refs, ...(item.open ?? [])]))
    if (r.startsWith('OPEN-')) usedOn.set(r, [...(usedOn.get(r) ?? []), item])

/** Other spec rows whose text names each item: decisions, then the rest. */
const citedBy = new Map<string, SpecId[]>()
const others = Object.values(ids)
  .filter((s) => s.kind !== 'OPEN')
  .sort((a, b) => Number(b.kind === 'DEC') - Number(a.kind === 'DEC'))
for (const s of others)
  for (const id of new Set(s.text.match(/\bOPEN-\d{3}\b/g) ?? []))
    citedBy.set(id, [...(citedBy.get(id) ?? []), s])

const levelName = { system: 'Overview', board: 'System', power: 'Power' }

/** The filter searches the whole row (description, impact, owner). */
const rowText: FilterFn<SpecId> = (row, _col, value: string) => {
  const q = value.trim().toLowerCase()
  const s = row.original
  return (
    !q ||
    `${s.id} ${Object.values(s.fields).join(' ')}`.toLowerCase().includes(q)
  )
}

const label =
  'text-xs font-semibold tracking-wide text-muted-foreground uppercase'

export function OpenItemsPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const [sorting, setSorting] = useState<SortingState>([])
  const filter = search.q ?? ''
  const setFilter = (q: string) =>
    navigate({ search: { ...search, q: q || undefined }, replace: true })
  const toggle = (id: string) =>
    navigate({ search: { ...search, id: id === search.id ? undefined : id } })
  const toggleClosed = () =>
    navigate({
      search: { ...search, closed: search.closed ? undefined : true },
      replace: true,
    })

  // A link to a closed item shows that item even with closed rows hidden.
  const data = useMemo(
    () =>
      search.closed
        ? [...openRows, ...closedRows]
        : [...openRows, ...closedRows.filter((s) => s.id === search.id)],
    [search.closed, search.id]
  )

  const columns = useMemo<ColumnDef<SpecId>[]>(
    () => [
      {
        accessorKey: 'id',
        meta: { thClassName: 'w-32' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='ID' />
        ),
        cell: ({ row }) => (
          <span className='flex items-center gap-1'>
            {row.original.id === search.id ? (
              <ChevronDown className='size-3.5 text-muted-foreground' />
            ) : (
              <ChevronRight className='size-3.5 text-muted-foreground' />
            )}
            {/* the chip opens GitHub; it should not also toggle the row */}
            <span onClick={(e) => e.stopPropagation()}>
              <IdChip id={row.original.id} />
            </span>
          </span>
        ),
      },
      {
        id: 'description',
        accessorFn: (r) => r.fields['Description'] ?? '',
        header: 'Description',
        enableSorting: false,
        cell: ({ row }) => (
          <span className='line-clamp-2 [overflow-wrap:anywhere]'>
            <MdText text={row.original.fields['Description'] ?? ''} />
          </span>
        ),
      },
      {
        id: 'owner',
        meta: { className: 'hidden sm:table-cell', thClassName: 'w-[28%]' },
        accessorFn: (r) => r.fields['Owner / next action'] ?? '',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Owner / next action' />
        ),
        cell: ({ row }) => (
          <span className='line-clamp-2 [overflow-wrap:anywhere] text-muted-foreground'>
            <MdText text={row.original.fields['Owner / next action'] ?? ''} />
          </span>
        ),
      },
      {
        id: 'used',
        meta: { className: 'hidden md:table-cell', thClassName: 'w-28' },
        accessorFn: (r) => usedOn.get(r.id)?.length ?? 0,
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='On diagram' />
        ),
        cell: ({ row }) => {
          const n = usedOn.get(row.original.id)?.length ?? 0
          return (
            <span className='text-xs text-muted-foreground'>
              {n ? `${n} item${n > 1 ? 's' : ''}` : '-'}
            </span>
          )
        },
      },
    ],
    [search.id]
  )

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    globalFilterFn: rowText,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  // A link such as ?id=OPEN-023 scrolls its row into view once.
  useEffect(() => {
    if (!search.id) return
    const t = setTimeout(
      () =>
        document
          .getElementById(`row-${search.id}`)
          ?.scrollIntoView({ block: 'start' }),
      50
    )
    return () => clearTimeout(t)
  }, [search.id])

  const rows = table.getRowModel().rows

  return (
    <>
      <SiteHeader title='Open items' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Open items</h1>
          <p className='text-sm text-muted-foreground'>
            Every <span className='font-mono'>OPEN-xxx</span> row of the{' '}
            <a
              href={sourceUrl(meta.sources.spec)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              specification
            </a>{' '}
            (rev {meta.specRevision}, section {meta.openSection}), as written
            there. Click a row for the full text and what cites it.
          </p>
        </div>

        <Card className='gap-3'>
          <CardHeader className='flex flex-row flex-wrap items-center justify-between gap-2'>
            <div>
              <CardTitle className='text-base'>Open questions</CardTitle>
              <CardDescription>
                {rows.length} shown · {openRows.length} open,{' '}
                {closedRows.length} closed
              </CardDescription>
            </div>
            <div className='flex w-full flex-wrap gap-2 sm:w-auto'>
              <Button
                variant={search.closed ? 'secondary' : 'outline'}
                size='sm'
                aria-pressed={!!search.closed}
                onClick={toggleClosed}
                className='h-8'
              >
                {search.closed ? 'Hide closed' : 'Show closed'}
              </Button>
              <Input
                placeholder='Filter: UBEC, P3-007, OPEN-023…'
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className='h-8 min-w-0 flex-1 sm:w-72 sm:flex-none'
              />
            </div>
          </CardHeader>
          <CardContent className='px-0'>
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
                          {flexRender(
                            h.column.columnDef.header,
                            h.getContext()
                          )}
                        </TableHead>
                      ))}
                    </TableRow>
                  ))}
                </TableHeader>
                <TableBody>
                  {rows.map((r) => {
                    const open = r.original.id === search.id
                    return (
                      <Fragment key={r.id}>
                        <TableRow
                          id={`row-${r.original.id}`}
                          onClick={() => toggle(r.original.id)}
                          data-state={open ? 'selected' : undefined}
                          className={cn(
                            'cursor-pointer scroll-mt-20 align-top data-[state=selected]:bg-primary/10',
                            r.original.closed && 'text-muted-foreground'
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
                              {flexRender(
                                c.column.columnDef.cell,
                                c.getContext()
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                        {open && (
                          <TableRow className='bg-primary/5 hover:bg-primary/5'>
                            <TableCell
                              colSpan={columns.length}
                              className='px-6 py-3 whitespace-normal'
                            >
                              <OpenDetail row={r.original} />
                            </TableCell>
                          </TableRow>
                        )}
                      </Fragment>
                    )
                  })}
                  {!rows.length && (
                    <TableRow>
                      <TableCell
                        colSpan={columns.length}
                        className='px-6 py-6 text-center text-sm text-muted-foreground'
                      >
                        No items match.
                        {!search.closed && ' Closed items are hidden.'}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function OpenDetail({ row }: { row: SpecId }) {
  const used = usedOn.get(row.id) ?? []
  const cited = citedBy.get(row.id) ?? []
  const decs = cited.filter((s) => s.kind === 'DEC')
  const rest = cited.filter((s) => s.kind !== 'DEC')
  const tasks = tasksNaming(row)
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_18rem]'>
      <div className='min-w-0 space-y-2'>
        <div className={label}>Description</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={row.fields['Description'] || '-'} />
        </p>
        <div className={label}>Owner / next action</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={row.fields['Owner / next action'] || '-'} />
        </p>
        <div className={label}>Impact</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={row.fields['Impact'] || '-'} />
        </p>
        <a
          href={sourceUrl(row.file, row.line)}
          target='_blank'
          rel='noreferrer'
          className='inline-block text-xs text-primary hover:underline'
        >
          Spec line {row.line}
        </a>
      </div>
      <div className='min-w-0 space-y-4'>
        <div className='space-y-2'>
          <div className={label}>Checklist tasks</div>
          {tasks.length ? (
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
          ) : (
            <p className='text-xs text-muted-foreground'>None.</p>
          )}
        </div>
        <div className='space-y-2'>
          <div className={label}>On the diagram</div>
          {used.length ? (
            <ul className='space-y-1'>
              {used.map((item) => {
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
          ) : (
            <p className='text-xs text-muted-foreground'>
              Not drawn on any diagram view.
            </p>
          )}
        </div>
        <div className='space-y-2'>
          <div className={label}>Decisions that name it</div>
          {decs.length ? (
            <ul className='space-y-1'>
              {decs.map((d) => (
                <li key={d.id} className='flex items-baseline gap-1.5'>
                  <RouterLink
                    to='/decisions'
                    search={{ id: d.id }}
                    className='w-16 shrink-0 font-mono text-xs text-primary hover:underline'
                  >
                    {d.id}
                  </RouterLink>
                  <span className='min-w-0 truncate text-xs text-muted-foreground'>
                    {idTitle(d.id)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className='text-xs text-muted-foreground'>None.</p>
          )}
        </div>
        {rest.length > 0 && (
          <div className='space-y-2'>
            <div className={label}>Other spec rows</div>
            <div className='flex flex-wrap gap-1'>
              {rest.map((s) => (
                <IdChip key={s.id} id={s.id} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
