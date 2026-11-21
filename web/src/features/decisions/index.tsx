import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import {
  type ColumnDef,
  type FilterFn,
  type SortingState,
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
  links,
  meta,
  sourceUrl,
} from '@/data'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { detailLabel, useScrollToRow } from '@/lib/record-rows'
import { cn } from '@/lib/utils'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { DataTableColumnHeader } from '@/components/data-table'
import { IdChip } from '@/components/id-chip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { MdText } from '@/components/md-text'
import { DiagramItemList, RecordTable } from '@/components/record-table'

const route = getRouteApi('/_site/decisions')

/** Every DEC row of the spec, as the extractor read it. */
const decisions = Object.values(ids).filter((s) => s.kind === 'DEC')

/** Diagram blocks and links that cite each decision (refs or open). */
const usedOn = new Map<string, (Block | Link)[]>()
for (const item of [...blocks, ...links])
  for (const r of new Set([...item.refs, ...(item.open ?? [])]))
    if (r.startsWith('DEC-')) usedOn.set(r, [...(usedOn.get(r) ?? []), item])

/** The filter searches the whole row (topic, decision, notes, date). */
const rowText: FilterFn<SpecId> = (row, _col, value: string) => {
  const q = value.trim().toLowerCase()
  return (
    !q || `${row.original.id} ${row.original.text}`.toLowerCase().includes(q)
  )
}

export function DecisionsPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'id', desc: false },
  ])
  const filter = search.q ?? ''
  const setFilter = (q: string) =>
    navigate({ search: { ...search, q: q || undefined }, replace: true })
  const toggle = (id: string) =>
    navigate({ search: { ...search, id: id === search.id ? undefined : id } })

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
            {/* its own page: the row click opens it, so no link */}
            <IdChip id={row.original.id} plain />
          </span>
        ),
      },
      {
        id: 'topic',
        meta: { thClassName: 'sm:w-[28%]' },
        accessorFn: (r) => r.fields['Topic'] ?? '',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Topic' />
        ),
        cell: ({ row }) => (
          <span className='font-medium'>
            <MdText text={row.original.fields['Topic'] ?? ''} />
          </span>
        ),
      },
      {
        id: 'decision',
        meta: { className: 'hidden sm:table-cell' },
        accessorFn: (r) => r.fields['Selected option'] ?? '',
        header: 'Decision',
        enableSorting: false,
        cell: ({ row }) => (
          <span
            className={cn(
              'text-muted-foreground',
              row.original.id !== search.id && 'line-clamp-2'
            )}
          >
            <MdText text={row.original.fields['Selected option'] ?? ''} />
          </span>
        ),
      },
      {
        id: 'date',
        meta: { className: 'hidden sm:table-cell', thClassName: 'w-28' },
        accessorFn: (r) => r.fields['Date'] ?? '',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Date' />
        ),
        cell: ({ row }) => (
          <span className='font-mono text-xs whitespace-nowrap text-muted-foreground'>
            {row.original.fields['Date']}
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
    data: decisions,
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    globalFilterFn: rowText,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  useScrollToRow(search.id, 'row-', 'center')

  const rows = table.getRowModel().rows

  return (
    <>
      <SiteHeader title='Decisions' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Decisions</h1>
          <p className='text-sm text-muted-foreground'>
            Every <span className='font-mono'>DEC-xxx</span> row of the{' '}
            <a
              href={sourceUrl(meta.sources.spec)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              specification
            </a>{' '}
            (rev {meta.specRevision}), as written there. Click a row for the
            full decision, its notes and where the diagram uses it.
          </p>
        </div>

        <Card className='gap-3'>
          <CardHeader className='flex flex-row flex-wrap items-center justify-between gap-2'>
            <div>
              <CardTitle className='text-base'>Decision log</CardTitle>
              <CardDescription>
                {rows.length} of {decisions.length} decisions
              </CardDescription>
            </div>
            <Input
              placeholder='Filter: USB, TPS2121, DEC-050…'
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className='h-8 w-full sm:w-72'
            />
          </CardHeader>
          <CardContent className='px-0'>
            <RecordTable
              table={table}
              openId={search.id}
              getId={(s) => s.id}
              onToggle={toggle}
              detail={(s) => <DecisionDetail row={s} />}
              rowClassName={(s) => s.removed && 'line-through opacity-60'}
            />
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function DecisionDetail({ row }: { row: SpecId }) {
  const used = usedOn.get(row.id) ?? []
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_16rem]'>
      <div className='min-w-0 space-y-2'>
        <div className='space-y-2 sm:hidden'>
          <div className={detailLabel}>Decision · {row.fields['Date']}</div>
          <p className='leading-relaxed'>
            <MdText text={row.fields['Selected option'] ?? ''} />
          </p>
        </div>
        <div className={detailLabel}>Notes</div>
        <p className='leading-relaxed'>
          <MdText text={row.fields['Notes'] || '-'} />
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
      <div className='space-y-2'>
        <div className={detailLabel}>On the diagram</div>
        <DiagramItemList items={used} />
      </div>
    </div>
  )
}
