import { useCallback } from 'react'
import { getRouteApi, Link as RouterLink } from '@tanstack/react-router'
import { type Level, blockById, linkById } from '@/data'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { DiagramCanvas } from './canvas'
import { DetailPanel } from './detail-panel'
import { InterfaceView } from './interface-view'
import { Legend } from './legend'

const route = getRouteApi('/_site/diagram')

const levels: { id: Level | 'interface'; label: string; hint: string }[] = [
  { id: 'system', label: 'System', hint: 'L0' },
  { id: 'board', label: 'Board', hint: 'L1' },
  { id: 'interface', label: 'Interface', hint: 'L2' },
]

export function DiagramPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const link = search.link ? linkById.get(search.link) : undefined
  const block = search.block ? blockById.get(search.block) : undefined
  const level: Level = search.level ?? link?.level ?? block?.level ?? 'system'
  const view = link ? 'interface' : level

  const set = useCallback(
    (next: { level?: Level; link?: string; block?: string }) =>
      navigate({ search: next, replace: false }),
    [navigate]
  )

  const onBlock = useCallback(
    (id: string) => {
      const b = blockById.get(id)
      if (b?.drill) return set({ level: b.drill })
      set({ level, block: id === search.block ? undefined : id })
    },
    [set, level, search.block]
  )
  const onLink = useCallback(
    (id: string) => set({ level, link: id }),
    [set, level]
  )
  const onPane = useCallback(() => set({ level }), [set, level])

  const crumbs = [
    { label: 'System', search: { level: 'system' as Level } },
    ...(level === 'board'
      ? [{ label: 'Board', search: { level: 'board' as Level } }]
      : []),
    ...(block && !link
      ? [{ label: block.label, search: { level, block: block.id } }]
      : []),
    ...(link ? [{ label: link.label, search: { level, link: link.id } }] : []),
  ]

  return (
    <>
      <SiteHeader
        title={
          <nav className='flex min-w-0 items-center gap-1 text-sm'>
            <span className='text-muted-foreground'>Block diagram</span>
            {crumbs.map((c, i) => (
              <span
                key={c.label + i}
                className='flex min-w-0 items-center gap-1'
              >
                <ChevronRight className='size-3.5 shrink-0 text-muted-foreground' />
                <RouterLink
                  to='/diagram'
                  search={c.search}
                  className={cn(
                    'truncate hover:text-primary',
                    i === crumbs.length - 1
                      ? 'font-semibold'
                      : 'text-muted-foreground'
                  )}
                >
                  {c.label}
                </RouterLink>
              </span>
            ))}
          </nav>
        }
      />
      <Main fixed fluid className='gap-3 px-3 pt-0 pb-3 sm:px-4'>
        <div className='flex flex-wrap items-center gap-2'>
          <div className='inline-flex rounded-lg border bg-muted/40 p-0.5'>
            {levels.map((l) => {
              const active = view === l.id
              const disabled = l.id === 'interface' && !link
              return (
                <button
                  key={l.id}
                  disabled={disabled}
                  onClick={() => l.id !== 'interface' && set({ level: l.id })}
                  className={cn(
                    'flex items-center gap-1.5 rounded-md px-3 py-1 text-sm font-medium transition-colors',
                    active
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground',
                    disabled &&
                      'cursor-not-allowed opacity-40 hover:text-muted-foreground'
                  )}
                >
                  {l.label}
                  <span
                    className={cn(
                      'font-mono text-[10px]',
                      active ? 'opacity-80' : 'opacity-60'
                    )}
                  >
                    {l.hint}
                  </span>
                </button>
              )
            })}
          </div>
          <p className='text-xs text-muted-foreground'>
            {view === 'system' &&
              'The board and the devices it connects to. Click the board to open it.'}
            {view === 'board' &&
              'Blocks inside the board. Click a link label for its signals and pins.'}
            {view === 'interface' &&
              'Every signal on the selected link, with MCU pins at each end.'}
          </p>
        </div>

        <div className='relative min-h-0 flex-1 overflow-hidden rounded-xl border bg-[radial-gradient(ellipse_at_top,color-mix(in_oklab,var(--navy)_25%,transparent),transparent_70%)]'>
          {link ? (
            <InterfaceView link={link} />
          ) : (
            <>
              <DiagramCanvas
                level={level}
                selectedBlock={block?.id}
                onBlock={onBlock}
                onLink={onLink}
                onPane={onPane}
              />
              <Legend level={level} />
            </>
          )}
          <DetailPanel
            block={link ? undefined : block}
            link={link}
            onClose={() => set({ level })}
            onLink={onLink}
          />
        </div>
      </Main>
    </>
  )
}
