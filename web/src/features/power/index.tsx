import { Link as RouterLink } from '@tanstack/react-router'
import {
  type Block,
  type Power,
  type RailSummary,
  type RecordTable,
  blocksAt,
  sourceUrl,
} from '@/data'
import powerJson from '@/data/generated/power.json'
import { TriangleAlert } from 'lucide-react'
import { idsIn } from '@/lib/spec-ids'
import { cn } from '@/lib/utils'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { SpecText } from '@/components/spec-text'

const power = powerJson as Power
const powerBlocks = blocksAt('power')

/**
 * Presentation only: which rail colour and which Power view block (the part
 * that sets the limit) belong to each summary row, by the record's rail name.
 */
const railStyle = (rail: string) =>
  /IMU/.test(rail)
    ? { color: 'var(--rail-3v3a)', block: 'pw-ldo' }
    : /^3\.3 V/.test(rail)
      ? { color: 'var(--rail-3v3)', block: 'pw-buck' }
      : /^5 V/.test(rail)
        ? { color: 'var(--rail-5v)', block: 'pw-pmux' }
        : /^6 V/.test(rail)
          ? { color: 'var(--rail-6v)', block: 'pw-ubec' }
          : { color: 'var(--muted-foreground)', block: undefined }

/**
 * The Power view block a load row belongs to: one whose part number is in
 * the load name, or whose refs share a spec ID with the row.
 */
function blockFor(cells: string[], headers: string[]): Block | undefined {
  const load = cells[0] ?? ''
  const refCol = headers.indexOf('Ref')
  const refs = refCol >= 0 ? idsIn(cells[refCol] ?? '') : new Set<string>()
  return powerBlocks.find(
    (b) =>
      (b.sub ?? '')
        .split(/,\s*/)
        .map((p) => p.split(' ')[0])
        // a part number: 4+ characters with a letter and a digit
        .some(
          (mpn) =>
            mpn.length >= 4 &&
            /[A-Z]/i.test(mpn) &&
            /\d/.test(mpn) &&
            load.includes(mpn)
        ) || b.refs.some((r) => refs.has(r))
  )
}

const fmt = (n: number) => `${n.toLocaleString('en-US')} mA`

function SectionTitle({
  title,
  line,
  children,
}: {
  title: string
  line: number
  children?: React.ReactNode
}) {
  return (
    <CardHeader>
      <CardTitle className='text-base'>{title}</CardTitle>
      <CardDescription>
        {children}{' '}
        <a
          href={sourceUrl(power.file, line)}
          target='_blank'
          rel='noreferrer'
          className='text-primary hover:underline'
        >
          Record line {line}
        </a>
      </CardDescription>
    </CardHeader>
  )
}

export function PowerPage() {
  return (
    <>
      <SiteHeader title='Power budget' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Power budget</h1>
          <p className='text-sm text-muted-foreground'>
            From the{' '}
            <a
              href={sourceUrl(power.file)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              power budget record
            </a>{' '}
            (rev {power.revision} · {power.updated}), as written there with its
            evidence labels. The site draws the record's numbers and does not
            recompute them. A draft record, not a verification result.
          </p>
        </div>

        <RailBars />

        <Card className='gap-3'>
          <SectionTitle title='Loads per rail' line={power.loadsLine}>
            Section 3: typical or average current per load. A load name links to
            its Power view block where one matches.
          </SectionTitle>
          <CardContent className='space-y-6 px-0'>
            {power.loads.map((t) => (
              <div key={t.heading} className='space-y-2'>
                <div className='px-6 text-sm font-semibold'>{t.heading}</div>
                <RecordTableView table={t} linkLoads />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className='gap-3'>
          <SectionTitle title='Totals' line={power.totalsLine}>
            Section 4. The record says the subtotals are far from complete and
            not for sizing a regulator.
          </SectionTitle>
          <CardContent className='px-0'>
            <RecordTableView table={power.totals} />
          </CardContent>
        </Card>

        <Card className='gap-3'>
          <SectionTitle title='Rail tolerances' line={power.tolerancesLine}>
            Section 5 (PWR-013).
          </SectionTitle>
          <CardContent className='px-0'>
            <RecordTableView table={power.tolerances} />
          </CardContent>
        </Card>

        <Card className='gap-3'>
          <SectionTitle title='Thermal margin' line={power.thermalLine}>
            Section 11: junction temperature from the JEDEC RθJA of each
            datasheet.
          </SectionTitle>
          <CardContent className='px-0'>
            <RecordTableView table={power.thermal} />
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

/** One bullet bar per rail, each on its own scale (small multiples). */
function RailBars() {
  return (
    <Card className='gap-3'>
      <CardHeader>
        <CardTitle className='text-base'>Rail load against limit</CardTitle>
        <CardDescription>
          From the record's Rail summary table. Each rail has its own scale.
          Hover a bar for its values.
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-5'>
        <ul className='space-y-5'>
          {power.summary.map((r) => (
            <RailBar key={r.rail} row={r} />
          ))}
        </ul>
        <div className='flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted-foreground'>
          <span className='flex items-center gap-1.5'>
            <span className='h-2.5 w-4 rounded-sm bg-foreground/70' />
            Typical load
          </span>
          <span className='flex items-center gap-1.5'>
            <span className='h-2.5 w-4 rounded-sm bg-foreground/25' />
            Worst-case load
          </span>
          <span className='flex items-center gap-1.5'>
            <span className='h-3.5 w-0.5 bg-foreground' />
            Limit
          </span>
        </div>
        <SummaryTable />
      </CardContent>
    </Card>
  )
}

function RailBar({ row }: { row: RailSummary }) {
  const { color, block } = railStyle(row.rail)
  const top = Math.max(row.limit, row.worst ?? 0, row.typical ?? 0) * 1.1
  const pct = (n: number) => `${(n / top) * 100}%`
  const over = row.worst !== null && row.worst > row.limit
  const tip = (what: string, n: number) => (
    <TooltipContent className='text-xs'>
      <div className='font-semibold'>
        {row.rail}: {what}
      </div>
      <div>{fmt(n)}</div>
    </TooltipContent>
  )
  return (
    <li className='grid gap-x-6 gap-y-2 sm:grid-cols-[13rem_minmax(0,1fr)]'>
      <div className='min-w-0 space-y-1'>
        <div className='flex flex-wrap items-center gap-2'>
          <span
            className='size-2.5 shrink-0 rounded-full'
            style={{ background: color }}
          />
          {block ? (
            <RouterLink
              to='/diagram'
              search={{ level: 'power', block }}
              className='font-medium hover:text-primary hover:underline'
            >
              {row.rail}
            </RouterLink>
          ) : (
            <span className='font-medium'>{row.rail}</span>
          )}
        </div>
        <div className='text-xs text-muted-foreground'>
          <SpecText text={row.limitFrom} />
        </div>
      </div>
      <div className='min-w-0 space-y-1.5'>
        {/* the track; marks are absolutely placed on the rail's own scale */}
        <div
          className='relative h-5 rounded-md bg-muted'
          data-rail-bar={row.rail}
          role='img'
          aria-label={`${row.rail}: typical ${row.typical === null ? 'TBD' : fmt(row.typical)}, worst case ${row.worst === null ? 'TBD' : fmt(row.worst)}, limit ${fmt(row.limit)}`}
        >
          {row.worst !== null && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  className='absolute inset-y-0 left-0 rounded-e-[4px]'
                  style={{
                    width: pct(row.worst),
                    background: `color-mix(in oklab, ${color} 35%, var(--card))`,
                  }}
                />
              </TooltipTrigger>
              {tip('worst case', row.worst)}
            </Tooltip>
          )}
          {row.typical !== null && (
            <Tooltip>
              <TooltipTrigger asChild>
                {/* a 2px card-coloured gap keeps typical apart from worst */}
                <span
                  className='absolute inset-y-0 left-0 rounded-e-[4px] border-e-2 border-card'
                  style={{ width: pct(row.typical), background: color }}
                />
              </TooltipTrigger>
              {tip('typical', row.typical)}
            </Tooltip>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <span
                className='absolute -inset-y-1 w-0.5 -translate-x-1/2 bg-foreground'
                style={{ left: pct(row.limit) }}
              />
            </TooltipTrigger>
            {tip('limit', row.limit)}
          </Tooltip>
        </div>
        <div className='flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground'>
          <span>
            Typical{' '}
            <span className='font-mono text-foreground'>
              {row.typical === null ? 'TBD' : fmt(row.typical)}
            </span>
          </span>
          <span>
            Worst case{' '}
            <span className='font-mono text-foreground'>
              {row.worst === null ? 'TBD' : fmt(row.worst)}
            </span>
          </span>
          <span>
            Limit{' '}
            <span className='font-mono text-foreground'>{fmt(row.limit)}</span>
          </span>
          <SpecText text={row.label} labels />
          {over && (
            <span className='flex items-center gap-1 text-status-open'>
              <TriangleAlert className='size-3.5' />
              Worst case above the limit
            </span>
          )}
        </div>
      </div>
    </li>
  )
}

/** The Rail summary as a table: the bars' numbers in text. */
function SummaryTable() {
  return (
    <details className='text-sm'>
      <summary className='cursor-pointer text-xs text-primary'>
        Table view
      </summary>
      <div className='mt-2 overflow-x-auto'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rail</TableHead>
              <TableHead className='text-end'>Typical</TableHead>
              <TableHead className='text-end'>Worst case</TableHead>
              <TableHead className='text-end'>Limit</TableHead>
              <TableHead>Limit from</TableHead>
              <TableHead>Label</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {power.summary.map((r) => (
              <TableRow key={r.rail}>
                <TableCell>{r.rail}</TableCell>
                <TableCell className='text-end font-mono'>
                  {r.typical === null ? 'TBD' : fmt(r.typical)}
                </TableCell>
                <TableCell className='text-end font-mono'>
                  {r.worst === null ? 'TBD' : fmt(r.worst)}
                </TableCell>
                <TableCell className='text-end font-mono'>
                  {fmt(r.limit)}
                </TableCell>
                <TableCell className='whitespace-normal'>
                  <SpecText text={r.limitFrom} />
                </TableCell>
                <TableCell className='whitespace-normal'>
                  <SpecText text={r.label} labels />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </details>
  )
}

/** A record table as written; wide tables scroll inside their card. */
function RecordTableView({
  table,
  linkLoads,
}: {
  table: RecordTable
  linkLoads?: boolean
}) {
  return (
    <div className='overflow-x-auto'>
      <Table className='min-w-[48rem]'>
        <TableHeader>
          <TableRow>
            {table.headers.map((h, k) => (
              <TableHead
                key={h}
                className={cn('first:ps-6 last:pe-6', k === 0 && 'w-[22%]')}
              >
                {h}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {table.rows.map((r) => {
            const block = linkLoads
              ? blockFor(r.cells, table.headers)
              : undefined
            return (
              <TableRow key={r.line} className='align-top'>
                {table.headers.map((h, k) => (
                  <TableCell
                    key={h}
                    className={cn(
                      'py-2 align-top text-xs leading-relaxed [overflow-wrap:anywhere] whitespace-normal first:ps-6 last:pe-6',
                      k === 0 && 'text-sm font-medium'
                    )}
                  >
                    <SpecText text={r.cells[k] ?? ''} labels />
                    {k === 0 && block && (
                      <RouterLink
                        to='/diagram'
                        search={{ level: 'power', block: block.id }}
                        className='mt-1 block text-xs font-normal text-primary hover:underline'
                      >
                        Power view: {block.label}
                      </RouterLink>
                    )}
                  </TableCell>
                ))}
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}
