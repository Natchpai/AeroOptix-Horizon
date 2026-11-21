import { Link } from '@tanstack/react-router'
import { ids, meta, sourceUrl, statusInfo } from '@/data'
import { Keyboard } from 'lucide-react'
import { REQ_KINDS } from '@/lib/spec-ids'
import { cn } from '@/lib/utils'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'

const ext = { target: '_blank', rel: 'noreferrer' } as const
const linkCls = 'text-primary underline-offset-2 hover:underline'

/** From the project workflow rule; the engineer declares each phase. */
const phases = [
  {
    id: 'DRAFT',
    text: 'Schematic capture is in progress. PCB work is not yet part of the scope.',
  },
  {
    id: 'PRELIMINARY',
    text: 'The schematic is nearly complete and PCB work has started. ERC and DRC are not phase gates yet.',
  },
  {
    id: 'CHECK',
    text: 'Schematic and PCB are mostly final. The engineer runs ERC and DRC on a saved baseline and reviews the results.',
  },
  {
    id: 'RELEASE',
    text: 'An approved CHECK baseline is published as a release, from the same checked source.',
  },
]

/** From the project engineering rule. */
const labels = [
  {
    id: 'VERIFIED',
    text: 'Backed by named evidence: CAD data, a calculation or an official source.',
  },
  { id: 'ASSUMED', text: 'Taken as given; the record states the assumption.' },
  {
    id: 'ESTIMATED',
    text: 'Calculated or approximated; the record states the method and margin.',
  },
  {
    id: 'NOT_VERIFIED',
    text: 'Evidence is missing or the check was not run. This is the default for a value on this site.',
  },
]

/** What each spec ID prefix holds, named after its spec section. */
const kindNames: Record<string, string> = {
  SYS: 'System scope',
  MCU: 'MCU choice',
  FUN: 'Functional requirements',
  IF: 'External interfaces',
  SEN: 'Sensors',
  PWR: 'Power',
  SAF: 'Protection and fault behavior',
  ENV: 'Environment and reliability',
  CMP: 'Component selection constraints',
  MEC: 'Mechanical envelope',
  PCB: 'PCB fabrication and stackup',
  MFG: 'Manufacturing and assembly',
  TST: 'Debug and testability',
  DEC: 'Design decisions',
  OPEN: 'Open questions and assumptions',
  REF: 'References',
}

const kindPage = (kind: string) =>
  kind === 'DEC'
    ? { to: '/decisions' as const, name: 'Decisions' }
    : kind === 'OPEN'
      ? { to: '/open' as const, name: 'Open items' }
      : REQ_KINDS.includes(kind)
        ? { to: '/trace' as const, name: 'Traceability' }
        : undefined

const kinds = Object.keys(kindNames).map((kind) => {
  const rows = Object.values(ids).filter((s) => s.kind === kind && !s.removed)
  return { kind, count: rows.length, first: rows[0]?.id }
})

const pages: { name: string; to: string; reads: string; source: string }[] = [
  {
    name: 'Overview',
    to: '/',
    reads: 'Phase, revisions, key features, progress and next action',
    source: 'readme',
  },
  {
    name: 'Block diagram',
    to: '/diagram',
    reads:
      'Hand-drawn blocks and links that cite spec IDs; pins from the pin allocation',
    source: 'spec',
  },
  {
    name: 'Pinout',
    to: '/pinout',
    reads: 'H743, F100 and F100 reserved pin tables',
    source: 'pins',
  },
  {
    name: 'Decisions',
    to: '/decisions',
    reads: 'DEC rows, section 8.1',
    source: 'spec',
  },
  {
    name: 'Open items',
    to: '/open',
    reads: 'OPEN rows, section 8.2',
    source: 'spec',
  },
  {
    name: 'Checklist',
    to: '/checklist',
    reads: 'Gate summary and every task row',
    source: 'checklist',
  },
  {
    name: 'Spec history',
    to: '/history',
    reads: 'Change notes, section 9',
    source: 'spec',
  },
  {
    name: 'Traceability',
    to: '/trace',
    reads:
      'Requirement rows against checklist Req cells, DEC rows and diagram items',
    source: 'spec',
  },
  {
    name: 'Power budget',
    to: '/power',
    reads: 'Rail summary, load tables and margins',
    source: 'power',
  },
]

const sourceName: Record<string, string> = {
  spec: 'Specification',
  pins: 'Pin allocation',
  readme: 'README',
  checklist: 'Execution checklist',
  power: 'Power budget',
}

export function AboutPage() {
  return (
    <>
      <SiteHeader title='About this site' />
      <Main className='space-y-6'>
        <div className='space-y-2'>
          <h1 className='text-2xl font-bold tracking-tight'>
            How to read this site
          </h1>
          <p className='max-w-3xl text-sm text-muted-foreground'>
            The site shows what the design records in the repository say. It
            reads the saved Markdown records at build time and never changes
            them. A design change goes into the specification first, through the
            engineer; the site follows on the next build. A value the records do
            not give shows as <Code>TBD</Code>.
          </p>
        </div>

        <div className='grid gap-4 lg:grid-cols-2'>
          <Card>
            <CardHeader>
              <CardTitle>Project phase</CardTitle>
              <CardDescription>
                The engineer declares the phase; the site only shows it. Now:{' '}
                <span className='font-semibold text-status-open'>
                  {meta.phase}
                </span>
                .
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='space-y-3 text-sm'>
                {phases.map((p) => (
                  <li key={p.id} className='flex gap-3'>
                    <span
                      className={cn(
                        'h-fit w-28 shrink-0 rounded border px-1.5 py-0.5 text-center font-mono text-[11px]',
                        p.id === meta.phase
                          ? 'border-status-open/60 bg-status-open/10 text-status-open'
                          : 'text-muted-foreground'
                      )}
                    >
                      {p.id}
                    </span>
                    <span>{p.text}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Evidence labels</CardTitle>
              <CardDescription>
                Records label each significant value. A pass in ERC or DRC does
                not prove a design correct.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='space-y-3 text-sm'>
                {labels.map((l) => (
                  <li key={l.id} className='flex gap-3'>
                    <span className='h-fit w-28 shrink-0'>
                      <Code>{l.id}</Code>
                    </span>
                    <span>{l.text}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Spec IDs</CardTitle>
            <CardDescription>
              Every row of the{' '}
              <a
                className={linkCls}
                href={sourceUrl(meta.sources.spec)}
                {...ext}
              >
                specification
              </a>{' '}
              has a stable ID that is never reused. Click an ID chip anywhere on
              the site to open its row. Removed rows are not counted.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className='grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-3'>
              {kinds.map(({ kind, count, first }) => {
                const page = kindPage(kind)
                return (
                  <li key={kind} className='flex items-baseline gap-2'>
                    <span className='w-12 shrink-0 font-mono text-xs font-semibold text-primary'>
                      {kind}
                    </span>
                    <span className='min-w-0'>
                      {kindNames[kind]}{' '}
                      <span className='text-xs text-muted-foreground'>
                        {count} rows
                        {page && first && (
                          <>
                            {' · '}
                            <Link
                              to={page.to}
                              search={{ id: first }}
                              className={linkCls}
                            >
                              {page.name}
                            </Link>
                          </>
                        )}
                      </span>
                    </span>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Where each page comes from</CardTitle>
            <CardDescription>
              A missing heading, table or column in a record fails the build,
              and the old site stays up.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className='divide-y divide-border text-sm'>
              {pages.map((p) => (
                <li
                  key={p.name}
                  className='flex flex-col gap-1 py-2 first:pt-0 sm:flex-row sm:gap-3'
                >
                  <Link
                    to={p.to}
                    className='w-32 shrink-0 font-medium hover:text-primary'
                  >
                    {p.name}
                  </Link>
                  <span className='min-w-0 flex-1 text-muted-foreground'>
                    {p.reads}
                  </span>
                  <a
                    className={cn(linkCls, 'shrink-0 text-xs')}
                    href={sourceUrl(
                      meta.sources[p.source as keyof typeof meta.sources]
                    )}
                    {...ext}
                  >
                    {sourceName[p.source]}
                  </a>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <div className='grid gap-4 lg:grid-cols-2'>
          <Card>
            <CardHeader>
              <CardTitle>Reading the diagram</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className='space-y-2 text-sm'>
                {Object.values(statusInfo).map((s) => (
                  <li key={s.label}>
                    <span className='font-medium'>{s.label}:</span>{' '}
                    <span className='text-muted-foreground'>{s.hint}.</span>
                  </li>
                ))}
                <li>
                  <span className='font-medium'>Lines:</span>{' '}
                  <span className='text-muted-foreground'>
                    power rails are thick, one colour per rail; a dashed signal
                    or faded power line is a candidate. Click a block or line
                    for its notes, source IDs and pins.
                  </span>
                </li>
                <li>
                  <span className='font-medium'>
                    <Code>TBD</Code>:
                  </span>{' '}
                  <span className='text-muted-foreground'>
                    the records do not give the value yet, for example
                    sensor-side pins and connector pinouts.
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className='flex items-center gap-2'>
                <Keyboard className='size-4 text-primary' />
                <CardTitle>Finding things</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <ul className='space-y-2 text-sm text-muted-foreground'>
                <li>
                  <Kbd>Ctrl</Kbd> <Kbd>K</Kbd> searches pins, signals, blocks,
                  spec IDs, checklist tasks and revisions.
                </li>
                <li>
                  An opened row puts its ID in the address bar (
                  <Code>?id=DEC-050</Code>), so the link opens the same row for
                  a teammate. On Decisions, Open items and Traceability it also
                  lists the spec revisions whose change note names the ID.
                </li>
                <li>
                  The table pages (Decisions, Open items, Checklist, Spec
                  history, Traceability, Pinout) have a text filter. A linked
                  row always shows, even when a filter would hide it. The
                  Checklist also filters by gate, state and owner, and under
                  each open gate lists the open items that name its tasks. The
                  Pinout can also list its pins by peripheral (SPI1, USART6
                  ...).
                </li>
                <li>
                  The footer of the Overview names the commit and date the site
                  was built from.
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </Main>
    </>
  )
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code className='rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]'>
      {children}
    </code>
  )
}

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className='rounded border bg-muted px-1.5 py-0.5 font-mono text-[11px] text-foreground'>
      {children}
    </kbd>
  )
}
