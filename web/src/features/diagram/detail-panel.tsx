import { Link as RouterLink } from '@tanstack/react-router'
import {
  type Block,
  type Link,
  blockById,
  busInfo,
  ids,
  idTitle,
  linkSignals,
  linksOf,
  meta,
  openItems,
  sourceUrl,
  statusOf,
} from '@/data'
import { ArrowRight, Cpu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IdChip, IdList } from '@/components/id-chip'
import { MdText } from '@/components/md-text'
import { StatusBadge } from '@/components/status-badge'
import { kindInfo } from './kinds'

type PanelProps = {
  block?: Block
  link?: Link
  onClose: () => void
  onLink: (id: string) => void
}

/** Right-hand panel for the selected block or link. */
export function DetailPanel({ block, link, onClose, onLink }: PanelProps) {
  if (!block && !link) return null
  return (
    <aside className='absolute inset-x-2 bottom-2 z-10 flex max-h-[55%] flex-col overflow-hidden rounded-xl border bg-popover/95 shadow-2xl backdrop-blur md:inset-x-auto md:top-3 md:right-3 md:bottom-3 md:max-h-none md:w-96'>
      <div className='flex items-start gap-2 border-b p-3'>
        <div className='min-w-0 flex-1'>
          {block ? <BlockHead block={block} /> : <LinkHead link={link!} />}
        </div>
        <Button
          size='icon'
          variant='ghost'
          className='size-7'
          onClick={onClose}
          aria-label='Close panel'
        >
          <X className='size-4' />
        </Button>
      </div>
      <div className='min-h-0 flex-1 overflow-y-auto'>
        <div className='space-y-4 p-3 text-sm'>
          {block ? (
            <BlockBody block={block} onLink={onLink} />
          ) : (
            <LinkBody link={link!} />
          )}
          <Evidence />
        </div>
      </div>
    </aside>
  )
}

function BlockHead({ block }: { block: Block }) {
  const k = kindInfo[block.kind]
  return (
    <div className='flex items-start gap-2.5'>
      <span
        className='mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-md'
        style={{
          color: k.color,
          background: `color-mix(in oklab, ${k.color} 16%, transparent)`,
        }}
      >
        <k.icon className='size-4' />
      </span>
      <div className='min-w-0'>
        <div className='flex flex-wrap items-center gap-2'>
          <h3 className='font-semibold'>{block.label}</h3>
          <StatusBadge status={statusOf(block)} />
        </div>
        {block.sub && (
          <div className='font-mono text-xs text-muted-foreground'>
            {block.sub}
          </div>
        )}
        <div className='text-[11px] text-muted-foreground'>{k.label}</div>
      </div>
    </div>
  )
}

function LinkHead({ link }: { link: Link }) {
  const color = busInfo[link.bus].color
  const from = blockById.get(link.from)!
  const to = blockById.get(link.to)!
  return (
    <div>
      <div className='flex flex-wrap items-center gap-2'>
        <span
          className='rounded border px-1.5 font-mono text-[11px] font-semibold'
          style={{
            color,
            borderColor: `color-mix(in oklab, ${color} 50%, transparent)`,
          }}
        >
          {busInfo[link.bus].label}
        </span>
        <h3 className='font-semibold'>{link.label}</h3>
        <StatusBadge status={statusOf(link)} />
      </div>
      <div className='text-xs text-muted-foreground'>
        {from.label} → {to.label}
      </div>
    </div>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section className='space-y-1.5'>
      <h4 className='text-[11px] font-semibold tracking-wide text-muted-foreground uppercase'>
        {title}
      </h4>
      {children}
    </section>
  )
}

function OpenList({ list }: { list: string[] }) {
  if (!list.length) return null
  return (
    <Section title='Open items'>
      <ul className='space-y-2'>
        {list.map((id) => (
          <li
            key={id}
            className='rounded-md border border-status-open/30 bg-status-open/5 p-2'
          >
            <IdChip id={id} />
            <p className='mt-1 line-clamp-4 text-xs'>
              <MdText text={ids[id]?.fields['Description'] ?? ''} />
            </p>
          </li>
        ))}
      </ul>
    </Section>
  )
}

/** The spec text behind the first few interface / sensor / decision IDs. */
function SpecRows({ refs }: { refs: string[] }) {
  const shown = refs.filter((r) => ids[r] && !ids[r].removed).slice(0, 4)
  if (!shown.length) return null
  return (
    <Section title='From the spec'>
      <ul className='space-y-2'>
        {shown.map((id) => {
          const s = ids[id]
          const body =
            s.fields['Note'] ||
            s.fields['Selected option'] ||
            s.fields['Allocation'] ||
            s.fields['Conditions / limits'] ||
            s.fields['Requirement'] ||
            ''
          return (
            <li key={id} className='rounded-md border bg-card p-2'>
              <div className='flex items-center gap-2'>
                <IdChip id={id} />
                <span className='truncate text-xs font-medium'>
                  {idTitle(id)}
                </span>
              </div>
              {body && (
                <p className='mt-1 line-clamp-5 text-xs text-muted-foreground'>
                  <MdText text={body} />
                </p>
              )}
            </li>
          )
        })}
      </ul>
    </Section>
  )
}

function BlockBody({
  block,
  onLink,
}: {
  block: Block
  onLink: (id: string) => void
}) {
  const ls = linksOf(block.id)
  return (
    <>
      {block.note && <p className='text-muted-foreground'>{block.note}</p>}
      {block.mcu && (
        <Button asChild size='sm' className='w-full'>
          <RouterLink to='/pinout' search={{ mcu: block.mcu }}>
            <Cpu className='size-4' /> Open {block.sub} pinout
          </RouterLink>
        </Button>
      )}
      <Section title='Source IDs'>
        <IdList list={block.refs} />
      </Section>
      <OpenList list={openItems(block)} />
      {ls.length > 0 && (
        <Section title={`Links (${ls.length})`}>
          <ul className='divide-y rounded-md border'>
            {ls.map((l) => {
              const other = blockById.get(l.from === block.id ? l.to : l.from)!
              const color = busInfo[l.bus].color
              return (
                <li key={l.id}>
                  <button
                    onClick={() => onLink(l.id)}
                    className='flex w-full items-center gap-2 px-2 py-1.5 text-start text-xs transition-colors hover:bg-accent/50'
                  >
                    <span
                      className='size-2 shrink-0 rounded-full'
                      style={{ background: color }}
                    />
                    <span className='font-mono font-medium' style={{ color }}>
                      {l.label}
                    </span>
                    <span className='truncate text-muted-foreground'>
                      {other.label}
                    </span>
                    <ArrowRight className='ms-auto size-3 shrink-0 text-muted-foreground' />
                  </button>
                </li>
              )
            })}
          </ul>
        </Section>
      )}
      <SpecRows refs={block.refs} />
    </>
  )
}

function LinkBody({ link }: { link: Link }) {
  const sig = linkSignals(link)
  return (
    <>
      {link.note && <p className='text-muted-foreground'>{link.note}</p>}
      <Section title='Source IDs'>
        <IdList list={link.refs} />
      </Section>
      <OpenList list={openItems(link)} />
      {sig.length > 0 && (
        <Section title={`MCU pins (${sig.length})`}>
          <table className='w-full text-xs'>
            <tbody className='divide-y'>
              {sig.map((s) => (
                <tr key={s.key}>
                  <td className='py-1 font-mono font-semibold'>
                    {s.a?.row.pin}
                  </td>
                  <td className='py-1 font-mono text-muted-foreground'>
                    #{s.a?.row.number ?? '-'}
                  </td>
                  <td className='py-1 font-mono'>{s.a?.row.signal}</td>
                  {s.b && <td className='py-1 font-mono'>↔ {s.b.row.pin}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}
      <SpecRows refs={link.refs} />
    </>
  )
}

function Evidence() {
  return (
    <p className='rounded-md border border-dashed p-2 text-[11px] text-muted-foreground'>
      Design target from spec rev {meta.specRevision} ({meta.phase}).{' '}
      <code className='font-mono'>NOT_VERIFIED</code> as a built design.{' '}
      <a
        className='text-primary hover:underline'
        href={sourceUrl(meta.sources.spec)}
        target='_blank'
        rel='noreferrer'
      >
        Open the spec
      </a>
    </p>
  )
}
