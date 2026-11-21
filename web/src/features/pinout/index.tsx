import { useEffect, useMemo, useState } from 'react'
import { getRouteApi, Link as RouterLink } from '@tanstack/react-router'
import {
  type ColumnDef,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import {
  type Bus,
  type Mcu,
  type PinRow,
  busInfo,
  busOfSignal,
  linkForPin,
  mcuInfo,
  meta,
  pins,
  sourceUrl,
} from '@/data'
import { Download, Network, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardAction,
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
import { PackageView } from './package-view'
import { type PeripheralGroup, peripheralGroups } from './peripherals'

const route = getRouteApi('/_site/pinout')

export function PinoutPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const mcu: Mcu = search.mcu ?? 'h743'
  const info = mcuInfo[mcu]
  const selected = search.pin
    ? pins[mcu].find((p) => p.pin === search.pin)
    : undefined
  const view = search.view
  const pick = (pin?: string) =>
    navigate({
      search: { mcu, pin: pin === search.pin ? undefined : pin, view },
    })

  // A pin picked in the table or a peripheral group (below the package)
  // brings its details into view.
  useEffect(() => {
    if (search.pin)
      document
        .getElementById('pin-detail')
        ?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [search.pin])

  return (
    <>
      <SiteHeader title={`Pinout · ${info.part}`} />
      <Main className='space-y-4'>
        <div className='flex flex-wrap items-end justify-between gap-3'>
          <div>
            <h1 className='text-2xl font-bold tracking-tight'>Pinout</h1>
            <p className='text-sm text-muted-foreground'>
              From the{' '}
              <a
                href={sourceUrl(meta.sources.pins)}
                target='_blank'
                rel='noreferrer'
                className='text-primary hover:underline'
              >
                pin allocation record
              </a>
              . Click a pin for details and its link in the block diagram.
            </p>
          </div>
          <div className='inline-flex rounded-lg border bg-muted/40 p-0.5'>
            {(Object.keys(mcuInfo) as Mcu[]).map((m) => (
              <RouterLink
                key={m}
                to='/pinout'
                search={{ mcu: m, view }}
                className={cn(
                  'rounded-md px-3 py-1 text-sm font-medium transition-colors',
                  m === mcu
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {mcuInfo[m].part}
              </RouterLink>
            ))}
          </div>
        </div>

        <div className='grid gap-4 xl:grid-cols-[minmax(0,42rem)_minmax(0,1fr)]'>
          <Card className='gap-2'>
            <CardHeader>
              <CardTitle className='text-base'>{info.pkg} top view</CardTitle>
              <CardDescription>
                Pin 1 top left, numbers counter-clockwise. Coloured pins are
                allocated.
              </CardDescription>
              <CardAction>
                <Button
                  variant='outline'
                  size='sm'
                  onClick={() =>
                    import('./export-svg').then((m) => m.exportPackage(mcu))
                  }
                >
                  <Download /> SVG
                </Button>
              </CardAction>
            </CardHeader>
            <CardContent className='px-2 sm:px-6'>
              <PackageView mcu={mcu} selected={search.pin} onPick={pick} />
              <BusKey mcu={mcu} />
            </CardContent>
          </Card>

          <div className='min-w-0'>
            {selected ? (
              <PinDetail mcu={mcu} row={selected} onClose={() => pick()} />
            ) : (
              <PinHint mcu={mcu} />
            )}
          </div>
        </div>

        {/* full width, so every column fits without tall wrapped rows */}
        <PinTable
          mcu={mcu}
          selected={search.pin}
          onPick={pick}
          view={view}
          onView={(v) =>
            navigate({ search: { ...search, view: v }, replace: true })
          }
        />
        {mcu === 'f100' && <ReservedTable />}
      </Main>
    </>
  )
}

function BusKey({ mcu }: { mcu: Mcu }) {
  const used = [...new Set(pins[mcu].map((p) => busOfSignal(p.signal)))]
  return (
    <div className='mt-2 flex flex-wrap justify-center gap-x-3 gap-y-1 text-xs text-muted-foreground'>
      {used.map((b) => (
        <span key={b} className='flex items-center gap-1.5'>
          <span
            className='size-2.5 rounded-sm'
            style={{ background: busInfo[b].color }}
          />
          {busInfo[b].label}
        </span>
      ))}
    </div>
  )
}

/** Wide screens: what the empty space beside the package is for. */
function PinHint({ mcu }: { mcu: Mcu }) {
  const counts = new Map<Bus, number>()
  for (const p of pins[mcu]) {
    const b = busOfSignal(p.signal)
    counts.set(b, (counts.get(b) ?? 0) + 1)
  }
  return (
    <Card className='hidden gap-3 xl:flex'>
      <CardHeader>
        <CardTitle className='text-base'>Pin details</CardTitle>
        <CardDescription>
          Click a pin in the package or a row in the table for its function,
          source IDs, datasheet check and diagram link.
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-2 text-sm'>
        <p>
          {pins[mcu].length} of {mcuInfo[mcu].pinCount} pins allocated:
        </p>
        <ul className='space-y-1'>
          {[...counts].map(([b, n]) => (
            <li key={b} className='flex items-center gap-2'>
              <span
                className='size-2.5 rounded-sm'
                style={{ background: busInfo[b].color }}
              />
              <span>{busInfo[b].label}</span>
              <span className='ms-auto font-mono text-xs text-muted-foreground'>
                {n}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

function PinDetail({
  mcu,
  row,
  onClose,
}: {
  mcu: Mcu
  row: PinRow
  onClose: () => void
}) {
  const link = linkForPin(mcu, row.pin)
  const color = busInfo[busOfSignal(row.signal)].color
  return (
    <Card
      id='pin-detail'
      className='scroll-mt-20 gap-3 border-[color-mix(in_oklab,var(--c)_50%,var(--border))]'
      style={{ ['--c' as string]: color }}
    >
      <CardHeader className='flex flex-row items-start justify-between gap-2'>
        <div>
          <CardTitle className='flex items-baseline gap-2 font-mono'>
            <span style={{ color }}>{row.pin}</span>
            <span className='text-sm text-muted-foreground'>
              pin {row.number ?? '-'}
            </span>
          </CardTitle>
          <CardDescription className='font-mono'>{row.signal}</CardDescription>
        </div>
        <Button
          size='icon'
          variant='ghost'
          className='size-7'
          onClick={onClose}
          aria-label='Clear selection'
        >
          <X className='size-4' />
        </Button>
      </CardHeader>
      <CardContent className='space-y-3 text-sm'>
        <div>{row.function}</div>
        <div className='flex flex-wrap items-center gap-1'>
          {row.refs.map((r) => (
            <IdChip key={r} id={r} />
          ))}
          <span className='ms-2 text-xs text-muted-foreground'>
            DS check: {row.ds || '-'}
          </span>
        </div>
        <div className='flex flex-wrap gap-2'>
          {link && (
            <Button asChild size='sm'>
              <RouterLink
                to='/diagram'
                search={{ level: 'board', link: link.id }}
              >
                <Network className='size-4' /> Open {link.label} in the diagram
              </RouterLink>
            </Button>
          )}
          <Button asChild size='sm' variant='outline'>
            <a
              href={sourceUrl(meta.sources.pins, row.line)}
              target='_blank'
              rel='noreferrer'
            >
              Source row (line {row.line})
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function PinTable({
  mcu,
  selected,
  onPick,
  view,
  onView,
}: {
  mcu: Mcu
  selected?: string
  onPick: (pin: string) => void
  view?: 'peripheral'
  onView: (view?: 'peripheral') => void
}) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'number', desc: false },
  ])
  const [filter, setFilter] = useState('')

  const columns = useMemo<ColumnDef<PinRow>[]>(
    () => [
      {
        id: 'number',
        accessorFn: (r) => r.number ?? 999,
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='#' />
        ),
        cell: ({ row }) => (
          <span className='font-mono text-muted-foreground'>
            {row.original.number ?? '-'}
          </span>
        ),
      },
      {
        accessorKey: 'pin',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Pin' />
        ),
        cell: ({ row }) => {
          const color = busInfo[busOfSignal(row.original.signal)].color
          return (
            <span className='flex items-center gap-1.5 font-mono font-semibold'>
              <span
                className='size-2 rounded-sm'
                style={{ background: color }}
              />
              {row.original.pin}
            </span>
          )
        },
      },
      {
        accessorKey: 'signal',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Signal' />
        ),
        cell: ({ row }) => (
          <span className='block min-w-40 font-mono text-xs whitespace-normal'>
            {row.original.signal}
          </span>
        ),
      },
      {
        accessorKey: 'function',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Function' />
        ),
        cell: ({ row }) => (
          <span className='block min-w-48 whitespace-normal'>
            {row.original.function}
          </span>
        ),
      },
      {
        id: 'refs',
        accessorFn: (r) => r.refs.join(' '),
        header: 'Ref',
        enableSorting: false,
        cell: ({ row }) => (
          <div className='flex min-w-40 flex-wrap gap-1'>
            {row.original.refs.map((r) => (
              <IdChip key={r} id={r} />
            ))}
          </div>
        ),
      },
      {
        accessorKey: 'ds',
        header: 'DS',
        enableSorting: false,
        cell: ({ row }) => (
          <span className='block min-w-32 text-xs whitespace-normal text-muted-foreground'>
            {row.original.ds}
          </span>
        ),
      },
    ],
    []
  )

  const table = useReactTable({
    data: pins[mcu],
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setFilter,
    globalFilterFn: 'includesString',
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  const groups = useMemo(() => {
    const q = filter.trim().toLowerCase()
    return peripheralGroups(pins[mcu])
      .map((g) => ({
        ...g,
        rows: g.rows.filter(
          ({ row }) =>
            !q ||
            [g.name, row.pin, row.signal, row.function, ...row.refs].some((t) =>
              t.toLowerCase().includes(q)
            )
        ),
      }))
      .filter((g) => g.rows.length)
  }, [mcu, filter])
  const shown = groups.reduce((n, g) => n + g.rows.length, 0)

  return (
    <Card className='gap-3'>
      <CardHeader className='flex flex-row flex-wrap items-center justify-between gap-2'>
        <div>
          <CardTitle className='text-base'>Allocated pins</CardTitle>
          <CardDescription>
            {view === 'peripheral'
              ? `${shown} of ${pins[mcu].length} pins in ${groups.length} groups`
              : `${table.getRowModel().rows.length} of ${pins[mcu].length} rows`}
          </CardDescription>
        </div>
        <div className='flex w-full flex-wrap items-center gap-2 sm:w-auto'>
          <div
            role='group'
            aria-label='Pin view'
            className='inline-flex rounded-lg border bg-muted/40 p-0.5'
          >
            {(
              [
                [undefined, 'Table'],
                ['peripheral', 'By peripheral'],
              ] as const
            ).map(([v, label]) => (
              <button
                key={label}
                type='button'
                aria-pressed={view === v}
                onClick={() => onView(v)}
                className={cn(
                  'rounded-md px-3 py-1 text-sm font-medium transition-colors',
                  view === v
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {label}
              </button>
            ))}
          </div>
          <Input
            aria-label='Filter pins'
            placeholder='Filter: PA5, SPI1, IF-010…'
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className='h-8 w-full sm:w-64'
          />
        </div>
      </CardHeader>
      <CardContent className='px-0'>
        {view === 'peripheral' ? (
          <PeripheralList groups={groups} selected={selected} onPick={onPick} />
        ) : (
          <div className='overflow-x-auto'>
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((hg) => (
                  <TableRow key={hg.id}>
                    {hg.headers.map((h) => (
                      <TableHead key={h.id} className='first:ps-6'>
                        {flexRender(h.column.columnDef.header, h.getContext())}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows.map((r) => (
                  <TableRow
                    key={r.id}
                    onClick={() => onPick(r.original.pin)}
                    data-state={
                      r.original.pin === selected ? 'selected' : undefined
                    }
                    className='cursor-pointer data-[state=selected]:bg-primary/10'
                  >
                    {r.getVisibleCells().map((c) => (
                      <TableCell key={c.id} className='py-1.5 first:ps-6'>
                        {flexRender(c.column.columnDef.cell, c.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

/** Pins grouped by peripheral instance, one small box per group. */
function PeripheralList({
  groups,
  selected,
  onPick,
}: {
  groups: PeripheralGroup[]
  selected?: string
  onPick: (pin: string) => void
}) {
  if (!groups.length)
    return <p className='px-6 text-sm text-muted-foreground'>No pin matches.</p>
  return (
    <div className='gap-3 px-6 sm:columns-2 lg:columns-3 2xl:columns-4'>
      {groups.map((g) => {
        const color = busInfo[busOfSignal(g.rows[0].row.signal)].color
        return (
          <section
            key={g.name}
            data-peripheral={g.name}
            className='mb-3 break-inside-avoid rounded-lg border'
          >
            <h3 className='flex items-center gap-2 border-b px-3 py-1.5 text-sm font-semibold'>
              <span
                className='size-2.5 shrink-0 rounded-sm'
                style={{ background: color }}
              />
              <span className='font-mono'>{g.name}</span>
              <span className='ms-auto font-mono text-xs font-normal text-muted-foreground'>
                {g.rows.length} {g.rows.length === 1 ? 'pin' : 'pins'}
              </span>
            </h3>
            <ul className='py-1'>
              {g.rows.map(({ row, label }) => (
                <li key={row.pin}>
                  <button
                    type='button'
                    data-pin={row.pin}
                    data-state={row.pin === selected ? 'selected' : undefined}
                    onClick={() => onPick(row.pin)}
                    className='flex w-full gap-2 px-3 py-1 text-start text-sm hover:bg-muted/50 data-[state=selected]:bg-primary/10'
                  >
                    <span className='w-12 shrink-0 font-mono font-semibold'>
                      {row.pin}
                    </span>
                    <span className='min-w-0 break-words'>
                      <span className='font-mono text-xs'>{label}</span>
                      <span className='text-muted-foreground'>
                        {' · '}
                        {row.function}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )
      })}
    </div>
  )
}

function ReservedTable() {
  return (
    <Card className='gap-3'>
      <CardHeader>
        <CardTitle className='text-base'>Reserved for px4io-v2</CardTitle>
        <CardDescription>
          Pins that stock px4io drives or reads. Not used for anything else (pin
          allocation record F-13). Package pin numbers are not in the record.
        </CardDescription>
      </CardHeader>
      <CardContent className='px-0'>
        <div className='overflow-x-auto'>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className='ps-6'>Pins</TableHead>
                <TableHead>px4io-v2 function</TableHead>
                <TableHead>Plan</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pins.f100Reserved.map((r) => (
                <TableRow key={r.line}>
                  <TableCell className='ps-6 font-mono font-semibold'>
                    {r.pins.join(', ')}
                  </TableCell>
                  <TableCell>{r.function}</TableCell>
                  <TableCell className='text-muted-foreground'>
                    {r.plan}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
