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
  idTitle,
  links,
  meta,
  sourceUrl,
} from '@/data'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { detailLabel, useScrollToRow } from '@/lib/record-rows'
import { Button } from '@/components/ui/button'
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
import { MentionedIn } from '@/components/mentioned-in'
import {
  DiagramItemList,
  RecordTable,
  SiteRowList,
  TaskRowList,
} from '@/components/record-table'
import { UnknownIdNotice } from '@/components/unknown-id-notice'
import { tasksNaming } from './cites'

const route = getRouteApi('/_site/open')

const byId = (a: SpecId, b: SpecId) => a.id.localeCompare(b.id)

/** Every OPEN row of the spec: open rows first, then closed ones. */
const all = Object.values(ids).filter((s) => s.kind === 'OPEN')
const openRows = all.filter((s) => !s.closed).sort(byId)
const closedRows = all.filter((s) => s.closed).sort(byId)
const openIds = new Set(all.map((s) => s.id))

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

/** The filter searches the whole row (description, impact, owner). */
const rowText: FilterFn<SpecId> = (row, _col, value: string) => {
  const q = value.trim().toLowerCase()
  const s = row.original
  return (
    !q ||
    `${s.id} ${Object.values(s.fields).join(' ')}`.toLowerCase().includes(q)
  )
}

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
            {/* its own page: the row click opens it, so no link */}
            <IdChip id={row.original.id} plain />
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

  useScrollToRow(search.id)

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
                aria-label='Filter open items'
                placeholder='Filter: UBEC, P3-007, OPEN-023…'
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className='h-8 min-w-0 flex-1 sm:w-72 sm:flex-none'
              />
            </div>
          </CardHeader>
          <CardContent className='px-0'>
            <UnknownIdNotice id={search.id} known={openIds}>
              is not in the spec.
            </UnknownIdNotice>
            <RecordTable
              table={table}
              openId={search.id}
              getId={(s) => s.id}
              onToggle={toggle}
              detail={(s) => <OpenDetail row={s} />}
              rowClassName={(s) => s.closed && 'text-muted-foreground'}
              empty={
                <>
                  No items match.
                  {!search.closed && ' Closed items are hidden.'}
                </>
              }
            />
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function OpenDetail({ row }: { row: SpecId }) {
  const cited = citedBy.get(row.id) ?? []
  const rest = cited.filter((s) => s.kind !== 'DEC')
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_18rem]'>
      <div className='min-w-0 space-y-2'>
        <div className={detailLabel}>Description</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={row.fields['Description'] || '-'} />
        </p>
        <div className={detailLabel}>Owner / next action</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={row.fields['Owner / next action'] || '-'} />
        </p>
        <div className={detailLabel}>Impact</div>
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
          <div className={detailLabel}>Checklist tasks</div>
          <TaskRowList tasks={tasksNaming(row)} />
        </div>
        <div className='space-y-2'>
          <div className={detailLabel}>On the diagram</div>
          <DiagramItemList items={usedOn.get(row.id) ?? []} />
        </div>
        <div className='space-y-2'>
          <div className={detailLabel}>Decisions that name it</div>
          <SiteRowList
            rows={cited.filter((s) => s.kind === 'DEC')}
            text={(d) => idTitle(d.id)}
          />
        </div>
        {rest.length > 0 && (
          <div className='space-y-2'>
            <div className={detailLabel}>Other spec rows</div>
            <div className='flex flex-wrap gap-1'>
              {rest.map((s) => (
                <IdChip key={s.id} id={s.id} />
              ))}
            </div>
          </div>
        )}
        <MentionedIn id={row.id} />
      </div>
    </div>
  )
}
