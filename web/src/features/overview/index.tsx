import { Link } from '@tanstack/react-router'
import {
  blocksAt,
  commitUrl,
  ids,
  meta,
  pins,
  progress,
  sourceUrl,
} from '@/data'
import {
  ArrowRight,
  BatteryCharging,
  CircleAlert,
  Cpu,
  FileClock,
  Gauge,
  History,
  Info,
  ListChecks,
  Microchip,
  Network,
  ScrollText,
  Waypoints,
  Workflow,
  Zap,
} from 'lucide-react'
import { REQ_KINDS } from '@/lib/spec-ids'
import { cn } from '@/lib/utils'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { BrandLogo } from '@/components/brand-logo'
import { IdChip } from '@/components/id-chip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { MdText } from '@/components/md-text'
import { GateBar, TaskLegend, TaskText } from '@/components/task-status'

const openList = Object.values(ids).filter(
  (s) => s.kind === 'OPEN' && !s.closed
)
const sensors = blocksAt('board').filter((b) => b.kind === 'sensor')
const taskList = Object.values(progress.tasks)
const tasksDone = taskList.filter((t) => t.status === 'DONE').length
const liveReqs = Object.values(ids).filter(
  (s) => REQ_KINDS.includes(s.kind) && !s.removed
).length

const stats = [
  {
    title: 'Main MCU',
    value: meta.mainMcu,
    hint: `${pins.h743.length} pins allocated, LQFP100`,
    icon: Cpu,
    color: 'var(--bus-spi)',
  },
  {
    title: 'IO MCU',
    value: meta.ioMcu,
    hint: `${pins.f100.length} pins allocated, px4io`,
    icon: Microchip,
    color: 'var(--bus-uart)',
  },
  {
    title: 'Sensors',
    value: `${sensors.length} on board`,
    hint: sensors.map((s) => s.sub?.split(' @')[0]).join(', '),
    icon: Gauge,
    color: 'var(--bus-i2c)',
  },
  {
    title: 'Open items',
    value: `${openList.length} open`,
    hint: 'OPEN-xxx rows in the spec',
    icon: CircleAlert,
    color: 'var(--status-open)',
    to: '/open',
  },
] as const

const explore = [
  {
    // display names swapped against the level ids, as on the diagram page
    title: 'Overview diagram',
    text: 'The board and everything it connects to on the aircraft.',
    to: '/diagram',
    search: { level: 'system' },
    icon: Workflow,
    color: 'var(--bus-usb)',
  },
  {
    title: 'System view',
    text: 'How the MCUs, sensors and connectors connect. Click a link for signals and pins.',
    to: '/diagram',
    search: { level: 'board' },
    icon: Network,
    color: 'var(--bus-spi)',
  },
  {
    title: 'Power view',
    text: 'Power from the battery and USB to every load, left to right.',
    to: '/diagram',
    search: { level: 'power' },
    icon: Zap,
    color: 'var(--rail-5v)',
  },
  {
    title: 'H743 pinout',
    text: 'LQFP100 package view and the full pin table.',
    to: '/pinout',
    search: { mcu: 'h743' },
    icon: Cpu,
    color: 'var(--bus-pwm)',
  },
  {
    title: 'F100 pinout',
    text: 'LQFP48 package view, px4io pins and reserved pins.',
    to: '/pinout',
    search: { mcu: 'f100' },
    icon: Microchip,
    color: 'var(--bus-uart)',
  },
  {
    title: 'Decisions',
    text: `All ${Object.values(ids).filter((s) => s.kind === 'DEC').length} DEC rows of the spec, searchable, with where the diagram uses them.`,
    to: '/decisions',
    search: {},
    icon: ScrollText,
    color: 'var(--status-decided)',
  },
  {
    title: 'Open items',
    text: `The ${openList.length} open OPEN rows, with owner and next action. Closed ones on request.`,
    to: '/open',
    search: {},
    icon: CircleAlert,
    color: 'var(--status-open)',
  },
  {
    title: 'Checklist',
    text: `${tasksDone} of ${taskList.length} tasks done. Every task by gate, owner and status.`,
    to: '/checklist',
    search: {},
    icon: ListChecks,
    color: 'var(--bus-i2c)',
  },
  {
    title: 'Spec history',
    text: `All ${meta.specRevisions.length} change notes of the spec, newest first.`,
    to: '/history',
    search: {},
    icon: History,
    color: 'var(--bus-sdmmc)',
  },
  {
    title: 'Traceability',
    text: `${liveReqs} requirements against the tasks, decisions and diagram items that cite them.`,
    to: '/trace',
    search: {},
    icon: Waypoints,
    color: 'var(--bus-usb)',
  },
  {
    title: 'Power budget',
    text: 'Load per rail against its limit, from the power budget record.',
    to: '/power',
    search: {},
    icon: BatteryCharging,
    color: 'var(--rail-6v)',
  },
  {
    title: 'About this site',
    text: 'Phases, evidence labels, spec ID kinds and the record behind each page.',
    to: '/about',
    search: {},
    icon: Info,
    color: 'var(--brand)',
  },
] as const

const ext = { target: '_blank', rel: 'noreferrer' } as const
const linkCls = 'text-primary underline-offset-2 hover:underline'

export function Overview() {
  return (
    <>
      <SiteHeader title='Overview' />
      <Main className='space-y-6'>
        {/* Hero */}
        <Card className='relative overflow-hidden border-primary/30'>
          <div className='pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_85%_20%,color-mix(in_oklab,var(--brand)_28%,transparent),transparent_55%),linear-gradient(135deg,color-mix(in_oklab,var(--navy)_35%,transparent),transparent_60%)]' />
          <CardContent className='relative flex flex-col gap-6 sm:flex-row sm:items-center'>
            <BrandLogo className='size-20 shrink-0' />
            <div className='space-y-3'>
              <div>
                <h1 className='text-2xl font-bold tracking-tight sm:text-3xl'>
                  AeroOptix-Horizon
                </h1>
                <p className='text-muted-foreground'>{meta.tagline}</p>
              </div>
              <div className='flex flex-wrap gap-2 text-xs'>
                <Pill className='border-status-open/50 bg-status-open/10 text-status-open'>
                  Phase {meta.phase}
                </Pill>
                <Pill>Board {meta.boardRevision}</Pill>
                <Pill>
                  Spec rev {meta.specRevision} · {meta.specUpdated}
                </Pill>
                <Pill>KiCad {meta.kicad}</Pill>
                <Pill>Baseline {meta.baseline}</Pill>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          {stats.map((s) => (
            <StatLink key={s.title} to={'to' in s ? s.to : undefined}>
              <Card
                className={cn(
                  'h-full gap-2',
                  'to' in s && 'transition-colors group-hover:border-primary/60'
                )}
              >
                <CardHeader className='flex flex-row items-center justify-between pb-0'>
                  <CardTitle className='text-sm font-medium text-muted-foreground'>
                    {s.title}
                  </CardTitle>
                  <span
                    className='flex size-8 items-center justify-center rounded-lg'
                    style={{
                      color: s.color,
                      background: `color-mix(in oklab, ${s.color} 15%, transparent)`,
                    }}
                  >
                    <s.icon className='size-4' />
                  </span>
                </CardHeader>
                <CardContent>
                  <div className='text-lg font-bold tracking-tight'>
                    {s.value}
                  </div>
                  <p className='text-xs text-muted-foreground'>{s.hint}</p>
                </CardContent>
              </Card>
            </StatLink>
          ))}
        </div>

        {/* Explore */}
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
          {explore.map((e) => (
            <Link key={e.title} to={e.to} search={e.search} className='group'>
              <Card className='h-full gap-3 transition-colors group-hover:border-primary/60'>
                <CardHeader className='pb-0'>
                  <div className='flex items-center gap-2'>
                    <e.icon className='size-4' style={{ color: e.color }} />
                    <CardTitle className='text-base'>{e.title}</CardTitle>
                    <ArrowRight className='ms-auto size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary' />
                  </div>
                </CardHeader>
                <CardContent className='text-sm text-muted-foreground'>
                  {e.text}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className='grid gap-4 lg:grid-cols-2'>
          <ProgressCard />
          <ChangesCard />
        </div>

        <NextActionCard />

        <div className='grid gap-4 lg:grid-cols-7'>
          <Card className='lg:col-span-3'>
            <CardHeader>
              <CardTitle>Key features</CardTitle>
              <CardDescription>
                From <code className='font-mono text-xs'>README.md</code>.
                Design targets, not verified results.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='space-y-2 text-sm'>
                {meta.keyFeatures.map((f) => (
                  <li key={f} className='flex gap-2'>
                    <span className='mt-1.5 size-1.5 shrink-0 rounded-full bg-primary' />
                    <span>
                      <MdText text={f} />
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className='lg:col-span-4'>
            <CardHeader>
              <div className='flex items-center gap-2'>
                <CardTitle>Open items</CardTitle>
                <Link
                  to='/open'
                  className='group ms-auto flex items-center gap-1 text-xs text-primary hover:underline'
                >
                  All open items
                  <ArrowRight className='size-3.5 transition-transform group-hover:translate-x-0.5' />
                </Link>
              </div>
              <CardDescription>
                Still open in the{' '}
                <a
                  className={linkCls}
                  href={sourceUrl(meta.sources.spec)}
                  {...ext}
                >
                  specification
                </a>{' '}
                (section {meta.openSection}).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='divide-y divide-border text-sm'>
                {openList.map((o) => (
                  <li key={o.id} className='flex gap-3 py-2 first:pt-0'>
                    <IdChip id={o.id} className='mt-0.5 h-fit' />
                    <div className='min-w-0'>
                      <Link
                        to='/open'
                        search={{ id: o.id }}
                        className='line-clamp-2 hover:text-primary'
                      >
                        <MdText text={o.fields['Description'] ?? ''} />
                      </Link>
                      <p className='text-xs text-muted-foreground'>
                        {o.fields['Owner / next action']}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        <p className='text-xs text-muted-foreground'>
          Read at build time from the saved Markdown records in the repository.
          Every value is a design target from the draft specification and is{' '}
          <code className='font-mono'>NOT_VERIFIED</code> unless the record says
          otherwise. <BuildStamp />
        </p>
      </Main>
    </>
  )
}

function ProgressCard() {
  return (
    <Card>
      <CardHeader>
        <div className='flex items-center gap-2'>
          <ListChecks className='size-4 text-primary' />
          <CardTitle>Progress</CardTitle>
        </div>
        <CardDescription>
          Tasks per gate in the{' '}
          <a
            className={linkCls}
            href={sourceUrl(meta.sources.checklist)}
            {...ext}
          >
            execution checklist
          </a>{' '}
          rev {progress.revision} · {progress.updated}. Gates are work stages,
          not the project phase.
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-4'>
        <ul className='space-y-3'>
          {progress.gates.map((g) => {
            const total = Object.entries(g.counts)
              .filter(([k]) => k !== 'N/A')
              .reduce((t, [, n]) => t + n, 0)
            return (
              <li key={g.id} className='space-y-1.5 text-sm'>
                <div className='flex items-center gap-2'>
                  <Link
                    to='/checklist'
                    search={{ gate: g.id }}
                    className='rounded border border-primary/40 px-1.5 py-0.5 font-mono text-[11px] leading-none text-primary hover:bg-primary/10'
                  >
                    {g.id}
                  </Link>
                  <span className='min-w-0 font-medium' title={g.exit}>
                    {g.name}
                  </span>
                  <span className='ms-auto flex shrink-0 items-center gap-2 text-xs text-muted-foreground'>
                    {g.counts.DONE ?? 0} of {total} done
                    <Pill
                      className='px-2 py-0.5 text-[11px]'
                      title={g.note || undefined}
                    >
                      {g.status}
                    </Pill>
                  </span>
                </div>
                <GateBar counts={g.counts} />
              </li>
            )
          })}
        </ul>
        <TaskLegend />
      </CardContent>
    </Card>
  )
}

function NextActionCard() {
  return (
    <div className='rounded-xl border border-primary/30 bg-primary/5 p-6 text-sm'>
      <div className='mb-3 text-sm font-semibold text-primary'>
        Current next action{' '}
        <a
          className='text-xs font-normal text-muted-foreground underline-offset-2 hover:underline'
          href={sourceUrl(meta.sources.checklist, progress.nextActionLine)}
          {...ext}
        >
          (checklist)
        </a>
      </div>
      <ol className='space-y-2'>
        {progress.nextAction.map((t, i) => (
          <li key={t} className='flex gap-3 leading-relaxed'>
            <span className='w-5 shrink-0 text-end font-mono text-xs leading-relaxed text-muted-foreground'>
              {i + 1}.
            </span>
            <span className='min-w-0'>
              <TaskText text={t} />
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function ChangesCard() {
  return (
    <Card>
      <CardHeader>
        <div className='flex items-center gap-2'>
          <FileClock className='size-4 text-primary' />
          <CardTitle>Recent spec changes</CardTitle>
          <Link
            to='/history'
            className='group ms-auto flex items-center gap-1 text-xs text-primary hover:underline'
          >
            Full history
            <ArrowRight className='size-3.5 transition-transform group-hover:translate-x-0.5' />
          </Link>
        </div>
        <CardDescription>
          Latest change notes in the{' '}
          <a className={linkCls} href={sourceUrl(meta.sources.spec)} {...ext}>
            specification
          </a>
          .
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className='divide-y divide-border text-sm'>
          {meta.specChanges.map((c) => (
            <li key={c.revision} className='flex gap-3 py-2 first:pt-0'>
              <Link
                to='/history'
                search={{ rev: c.revision }}
                className='mt-0.5 h-fit rounded border border-primary/40 px-1.5 py-0.5 font-mono text-[11px] leading-none whitespace-nowrap text-primary hover:bg-primary/10'
              >
                rev {c.revision}
              </Link>
              <div className='min-w-0'>
                <p className='line-clamp-2'>
                  <MdText text={c.description} />
                </p>
                <p className='text-xs text-muted-foreground'>
                  {c.date} · {c.approvedBy}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

/** Commit and date of this build, so a reader can tell the site is current. */
function BuildStamp() {
  const sha = meta.build.commit.slice(0, 7)
  const url = commitUrl(meta.build.commit)
  return (
    <>
      Built from commit{' '}
      {url ? (
        <a className={cn(linkCls, 'font-mono')} href={url} {...ext}>
          {sha}
        </a>
      ) : (
        <code className='font-mono'>{sha}</code>
      )}{' '}
      on {meta.build.date}.
    </>
  )
}

/** A stat tile with a page of its own links to it. */
function StatLink({
  to,
  children,
}: {
  to?: '/open'
  children: React.ReactNode
}) {
  if (!to) return <div>{children}</div>
  return (
    <Link to={to} className='group'>
      {children}
    </Link>
  )
}

function Pill({
  children,
  className,
  title,
}: {
  children: React.ReactNode
  className?: string
  title?: string
}) {
  return (
    <span
      title={title}
      className={cn(
        'rounded-full border bg-background/40 px-2.5 py-1 font-medium backdrop-blur',
        className
      )}
    >
      {children}
    </span>
  )
}
