import { useMemo, useState } from 'react'
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

const route = getRouteApi('/_site/pinout')

export function PinoutPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const mcu: Mcu = search.mcu ?? 'h743'
  const info = mcuInfo[mcu]
  const selected = search.pin
    ? pins[mcu].find((p) => p.pin === search.pin)
    : undefined
  const pick = (pin?: string) =>
    navigate({ search: { mcu, pin: pin === search.pin ? undefined : pin } })

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
                search={{ mcu: m }}
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

          <div className='min-w-0 space-y-4'>
            {selected && (
              <PinDetail mcu={mcu} row={selected} onClose={() => pick()} />
            )}
            <PinTable mcu={mcu} selected={search.pin} onPick={pick} />
            {mcu === 'f100' && <ReservedTable />}
          </div>
        </div>
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
      className='gap-3 border-[color-mix(in_oklab,var(--c)_50%,var(--border))]'
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
}: {
  mcu: Mcu
  selected?: string
  onPick: (pin: string) => void
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
          <span className='font-mono text-xs'>{row.original.signal}</span>
        ),
      },
      {
        accessorKey: 'function',
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Function' />
        ),
      },
      {
        id: 'refs',
        accessorFn: (r) => r.refs.join(' '),
        header: 'Ref',
        enableSorting: false,
        cell: ({ row }) => (
          <div className='flex flex-wrap gap-1'>
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
          <span className='text-xs text-muted-foreground'>
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

  return (
    <Card className='gap-3'>
      <CardHeader className='flex flex-row flex-wrap items-center justify-between gap-2'>
        <div>
          <CardTitle className='text-base'>Allocated pins</CardTitle>
          <CardDescription>
            {table.getRowModel().rows.length} of {pins[mcu].length} rows
          </CardDescription>
        </div>
        <Input
          placeholder='Filter: PA5, SPI1, IF-010…'
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className='h-8 w-full sm:w-64'
        />
      </CardHeader>
      <CardContent className='px-0'>
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
      </CardContent>
    </Card>
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
