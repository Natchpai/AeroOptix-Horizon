import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import {
  type ColumnDef,
  type SortingState,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { type Bom, type BomRow, sourceUrl } from '@/data'
import bomJson from '@/data/generated/bom.json'
import { ChevronDown, ChevronRight, TriangleAlert } from 'lucide-react'
import { detailLabel, useScrollToRow } from '@/lib/record-rows'
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
import { DataTableColumnHeader } from '@/components/data-table'
import { IdChip } from '@/components/id-chip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { MdText } from '@/components/md-text'
import { DiagramItemList, RecordTable } from '@/components/record-table'
import { UnknownIdNotice } from '@/components/unknown-id-notice'
import { blocksFor, decisionsFor, missingOf } from './links'

const route = getRouteApi('/_site/bom')

/** The BOM export as the extractor read it; a lazy chunk with this page. */
const bom = bomJson as Bom
/** A row's key: its first reference (each reference is in one row only). */
const keyOf = (r: BomRow) => r.refs[0]
/** The row that holds each reference, so R1 never matches R10. */
const rowOfRef = new Map(bom.rows.flatMap((r) => r.refs.map((x) => [x, r])))
const knownRefs = new Set(rowOfRef.keys())
const flagged = bom.rows.filter((r) => missingOf(r).length)
/** A committed file links to GitHub; an uncommitted one is not there yet. */
const committed = bom.meta.date !== 'uncommitted'

const rowText = (r: BomRow) =>
  [
    r.refs.join(' '),
    r.value,
    r.mfr,
    r.mpn,
    r.lcsc,
    r.footprint ?? '',
    r.status ?? '',
    r.dnp ? 'DNP' : '',
  ]
    .join(' ')
    .toLowerCase()

function DnpBadge() {
  return (
    <span
      data-bom-dnp
      title='Do not place'
      className='inline-flex items-center rounded-md border border-dashed border-status-candidate/50 bg-status-candidate/10 px-1.5 py-0.5 text-[11px] font-medium whitespace-nowrap text-status-candidate'
    >
      DNP
    </span>
  )
}

function Flag({ row }: { row: BomRow }) {
  const missing = missingOf(row)
  if (!missing.length) return null
  return (
    <span
      data-bom-flag
      className='mt-0.5 flex items-center gap-1 text-xs text-status-open'
    >
      <TriangleAlert className='size-3.5 shrink-0' />
      No {missing.join(' or ')}
    </span>
  )
}

export function BomPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const [sorting, setSorting] = useState<SortingState>([])
  const filter = search.q ?? ''
  const set = (s: Partial<typeof search>, replace = true) =>
    navigate({ search: { ...search, ...s }, replace })
  const linked = search.id ? rowOfRef.get(search.id) : undefined
  const openKey = linked && keyOf(linked)
  const toggle = (key: string) =>
    set({ id: key === openKey ? undefined : key }, false)

  // A linked row shows even when the filters would hide it.
  const data = useMemo(() => {
    const q = filter.trim().toLowerCase()
    return bom.rows.filter(
      (r) =>
        r === linked ||
        ((!search.dnp || (search.dnp === 'dnp') === r.dnp) &&
          (!q || rowText(r).includes(q)))
    )
  }, [filter, search.dnp, linked])

  const columns = useMemo<ColumnDef<BomRow>[]>(
    () => [
      {
        id: 'refs',
        meta: { thClassName: 'sm:w-[22%]' },
        accessorFn: (r) => r.refs[0],
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Refs' />
        ),
        cell: ({ row }) => {
          const refs = row.original.refs
          const shown = refs.length > 3 ? refs.slice(0, 2) : refs
          return (
            <span className='flex items-start gap-1'>
              {keyOf(row.original) === openKey ? (
                <ChevronDown className='mt-0.5 size-3.5 shrink-0 text-muted-foreground' />
              ) : (
                <ChevronRight className='mt-0.5 size-3.5 shrink-0 text-muted-foreground' />
              )}
              <span className='min-w-0 font-mono text-xs'>
                {shown.join(', ')}
                {refs.length > shown.length && (
                  <span className='text-muted-foreground'>
                    {' '}
                    +{refs.length - shown.length}
                  </span>
                )}
                {refs.length > 1 && (
                  <span className='block text-[11px] text-muted-foreground'>
                    {refs.length} refs
                  </span>
                )}
              </span>
            </span>
          )
        },
      },
      {
        accessorKey: 'qty',
        // on a phone the Refs cell carries the count
        meta: { className: 'hidden sm:table-cell', thClassName: 'w-14' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Qty' />
        ),
        cell: ({ row }) => (
          <span className='font-mono text-xs'>{row.original.qty}</span>
        ),
      },
      {
        accessorKey: 'value',
        meta: { thClassName: 'sm:w-[16%]' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Value' />
        ),
        cell: ({ row }) => (
          <span className='block min-w-0 [overflow-wrap:anywhere]'>
            <span className='font-medium'>{row.original.value || '-'}</span>
            <Flag row={row.original} />
          </span>
        ),
      },
      {
        accessorKey: 'mfr',
        meta: { className: 'hidden lg:table-cell', thClassName: 'w-36' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='MFR' />
        ),
        cell: ({ row }) => (
          <span className='text-muted-foreground'>
            {row.original.mfr || '-'}
          </span>
        ),
      },
      {
        accessorKey: 'mpn',
        meta: { className: 'hidden sm:table-cell' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='MFR.P/N' />
        ),
        cell: ({ row }) => (
          <span className='font-mono text-xs [overflow-wrap:anywhere]'>
            {row.original.mpn || '-'}
          </span>
        ),
      },
      {
        accessorKey: 'lcsc',
        meta: { className: 'hidden md:table-cell', thClassName: 'w-28' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='LCSC' />
        ),
        cell: ({ row }) => (
          <span className='font-mono text-xs text-muted-foreground'>
            {row.original.lcsc || '-'}
          </span>
        ),
      },
      ...(bom.meta.columns.footprint
        ? [
            {
              id: 'footprint',
              meta: { className: 'hidden xl:table-cell' },
              accessorFn: (r: BomRow) => r.footprint ?? '',
              header: 'Footprint',
              enableSorting: false,
              cell: ({ row }: { row: { original: BomRow } }) => (
                <span className='font-mono text-xs [overflow-wrap:anywhere] text-muted-foreground'>
                  {row.original.footprint || '-'}
                </span>
              ),
            } satisfies ColumnDef<BomRow>,
          ]
        : []),
      {
        id: 'dnp',
        // plain header: the DNP chips filter, and a sort button does not fit
        meta: { thClassName: 'w-16 pe-6' },
        header: 'DNP',
        enableSorting: false,
        cell: ({ row }) => (row.original.dnp ? <DnpBadge /> : null),
      },
    ],
    [openKey]
  )

  // The React Compiler skips this component, as on every table page; the
  // rule is off here so a new page does not add one more warning
  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  useScrollToRow(openKey, 'row-', 'center')

  const chip = (on: boolean) =>
    cn('h-7 px-2.5 text-xs', on && 'border-primary/60 bg-primary/10')
  const dnpRows = bom.rows.filter((r) => r.dnp).length

  return (
    <>
      <SiteHeader title='BOM' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>BOM</h1>
          <p className='text-sm text-muted-foreground'>
            Every row of the bill of materials the engineer exported from KiCad,
            as written there. Click a row for all its references, the diagram
            blocks and the decisions that name its part number. Stock and price
            are not shown.
          </p>
        </div>

        <Card className='gap-3'>
          <CardHeader className='space-y-3'>
            <div className='flex flex-row flex-wrap items-center justify-between gap-2'>
              <div>
                <CardTitle className='text-base'>Parts</CardTitle>
                <CardDescription data-bom-summary>
                  {committed ? (
                    <a
                      href={sourceUrl(bom.meta.file)}
                      target='_blank'
                      rel='noreferrer'
                      className='font-mono text-primary hover:underline'
                    >
                      {bom.meta.name}
                    </a>
                  ) : (
                    <span className='font-mono'>{bom.meta.name}</span>
                  )}{' '}
                  ({bom.meta.date}) · {data.length} of {bom.meta.rows} rows ·{' '}
                  {bom.meta.parts} parts · {bom.meta.dnpParts} DNP parts
                  {flagged.length > 0 && (
                    <span className='text-status-open'>
                      {' '}
                      · {flagged.length} fitted without MFR.P/N or LCSC
                    </span>
                  )}
                </CardDescription>
              </div>
              <Input
                aria-label='Filter parts'
                placeholder='Filter: 100n, YAGEO, R306, C85858…'
                value={filter}
                onChange={(e) => set({ q: e.target.value || undefined })}
                className='h-8 w-full sm:w-72'
              />
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='DNP'>
              {(
                [
                  [undefined, 'All rows', bom.meta.rows],
                  ['fitted', 'Fitted', bom.meta.rows - dnpRows],
                  ['dnp', 'DNP', dnpRows],
                ] as const
              ).map(([value, label, n]) => (
                <Button
                  key={label}
                  variant='outline'
                  size='sm'
                  aria-pressed={search.dnp === value}
                  className={chip(search.dnp === value)}
                  onClick={() => set({ dnp: value })}
                >
                  {label}
                  <span className='text-muted-foreground'>{n}</span>
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent className='px-0'>
            <UnknownIdNotice id={search.id} known={knownRefs}>
              is not in the BOM.
            </UnknownIdNotice>
            <RecordTable
              table={table}
              openId={openKey}
              getId={keyOf}
              onToggle={toggle}
              detail={(r) => <BomDetail row={r} linkedRef={search.id} />}
              rowClassName={(r) => r.dnp && 'text-muted-foreground'}
              empty='No rows match.'
            />
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function BomDetail({ row, linkedRef }: { row: BomRow; linkedRef?: string }) {
  const used = blocksFor(row)
  const decs = decisionsFor(row)
  const fields: [string, string | undefined][] = [
    ['MFR', row.mfr],
    ['MFR.P/N', row.mpn],
    ['LCSC', row.lcsc],
    ['Footprint', row.footprint],
    ['Status', row.status],
    ['Exclude from BOM', row.exclude],
  ]
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_18rem]'>
      <div className='min-w-0 space-y-3'>
        <div className='space-y-1'>
          <div className={detailLabel}>
            References ({row.refs.length}){row.dnp && ' · DNP'}
          </div>
          <p className='font-mono text-xs leading-relaxed [overflow-wrap:anywhere]'>
            {row.refs.map((r, i) => (
              <span key={r}>
                {i > 0 && ', '}
                <span
                  className={cn(
                    r === linkedRef && 'rounded bg-primary/15 px-1 text-primary'
                  )}
                >
                  {r}
                </span>
              </span>
            ))}
          </p>
        </div>
        <dl className='grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-1 text-xs'>
          {fields
            .filter(([, v]) => v !== undefined)
            .map(([k, v]) => (
              <div key={k} className='contents'>
                <dt className='text-muted-foreground'>{k}</dt>
                <dd className='font-mono [overflow-wrap:anywhere]'>
                  {v || '-'}
                </dd>
              </div>
            ))}
        </dl>
        <Flag row={row} />
        {committed ? (
          <a
            href={sourceUrl(bom.meta.file, row.line)}
            target='_blank'
            rel='noreferrer'
            className='inline-block text-xs text-primary hover:underline'
          >
            CSV line {row.line}
          </a>
        ) : (
          <p className='text-xs text-muted-foreground'>CSV line {row.line}</p>
        )}
      </div>
      <div className='min-w-0 space-y-4'>
        <div className='space-y-2'>
          <div className={detailLabel}>On the diagram</div>
          <DiagramItemList
            items={used}
            none='No diagram block names this part number.'
          />
        </div>
        <div className='space-y-2'>
          <div className={detailLabel}>Decisions naming it</div>
          {decs.length ? (
            <ul className='space-y-1' data-bom-decisions>
              {decs.map((d) => (
                <li key={d.id} className='flex items-baseline gap-1.5'>
                  <IdChip
                    id={d.id}
                    className={cn(d.removed && 'line-through opacity-60')}
                  />
                  <span className='min-w-0 truncate text-xs text-muted-foreground'>
                    <MdText text={d.fields['Topic'] ?? ''} />
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className='text-xs text-muted-foreground'>
              No DEC row names this part number.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
