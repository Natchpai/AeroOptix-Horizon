import { Link } from '@tanstack/react-router'
import { blocksAt, ids, meta, pins, sourceUrl } from '@/data'
import {
  ArrowRight,
  CircleAlert,
  Cpu,
  Gauge,
  Microchip,
  Network,
  Workflow,
} from 'lucide-react'
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

const openList = Object.values(ids).filter(
  (s) => s.kind === 'OPEN' && !s.closed
)
const sensors = blocksAt('board').filter((b) => b.kind === 'sensor')

const stats = [
  {
    title: 'Main MCU',
    value: 'STM32H743VIT6',
    hint: `${pins.h743.length} pins allocated, LQFP100`,
    icon: Cpu,
    color: 'var(--bus-spi)',
  },
  {
    title: 'IO MCU',
    value: 'STM32F100C8T6B',
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
  },
]

const explore = [
  {
    title: 'System view',
    text: 'The board and everything it connects to on the aircraft.',
    to: '/diagram',
    search: { level: 'system' },
    icon: Workflow,
    color: 'var(--bus-usb)',
  },
  {
    title: 'Board view',
    text: 'MCUs, sensors, power chain and connectors. Click a link for signals and pins.',
    to: '/diagram',
    search: { level: 'board' },
    icon: Network,
    color: 'var(--bus-spi)',
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
] as const

export function Overview() {
  return (
    <>
      <SiteHeader title='Overview' />
      <Main className='space-y-6'>
        {/* Hero */}
        <Card className='relative overflow-hidden border-primary/30'>
          <div className='pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_85%_20%,color-mix(in_oklab,var(--brand)_28%,transparent),transparent_55%),linear-gradient(135deg,color-mix(in_oklab,var(--navy)_35%,transparent),transparent_60%)]' />
          <CardContent className='relative flex flex-col gap-6 sm:flex-row sm:items-center'>
            <BrandLogo className='h-20 w-28 shrink-0' />
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
            <Card key={s.title} className='gap-2'>
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
          ))}
        </div>

        {/* Explore */}
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
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
              <CardTitle>Open items</CardTitle>
              <CardDescription>
                Still open in the{' '}
                <a
                  className='text-primary underline-offset-2 hover:underline'
                  href={sourceUrl(meta.sources.spec)}
                  target='_blank'
                  rel='noreferrer'
                >
                  specification
                </a>{' '}
                (section 8.2).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className='divide-y divide-border text-sm'>
                {openList.map((o) => (
                  <li key={o.id} className='flex gap-3 py-2 first:pt-0'>
                    <IdChip id={o.id} className='mt-0.5 h-fit' />
                    <div className='min-w-0'>
                      <p className='line-clamp-2'>
                        <MdText text={o.fields['Description'] ?? ''} />
                      </p>
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
          otherwise.
        </p>
      </Main>
    </>
  )
}

function Pill({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'rounded-full border bg-background/40 px-2.5 py-1 font-medium backdrop-blur',
        className
      )}
    >
      {children}
    </span>
  )
}
