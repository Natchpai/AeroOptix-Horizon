import { useMemo } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import { idTitle, meta, sourceUrl } from '@/data'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { detailLabel, useScrollToRow } from '@/lib/record-rows'
import { REQ_KINDS } from '@/lib/spec-ids'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { IdChip } from '@/components/id-chip'
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { MdText } from '@/components/md-text'
import {
  DiagramItemList,
  SiteRowList,
  TaskRowList,
} from '@/components/record-table'
import { SpecText } from '@/components/spec-text'
import { type TraceRow, traceRows } from './matrix'

const route = getRouteApi('/_site/trace')

const noTask = traceRows.filter((r) => r.noTask)
const noLink = traceRows.filter((r) => r.noLink)
/** Removed rows stay in the table, greyed, but are not counted as live. */
const live = traceRows.filter((r) => !r.req.removed).length
const removed = traceRows.length - live

const label = detailLabel

function Flag({ children }: { children: string }) {
  return (
    <span className='inline-flex items-center rounded border border-status-open/50 px-1.5 py-0.5 text-[11px] leading-none whitespace-nowrap text-status-open'>
      {children}
    </span>
  )
}

function Count({ n, warn }: { n: number; warn?: boolean }) {
  return (
    <span
      className={cn(
        'font-mono text-xs',
        n ? 'text-foreground' : 'text-muted-foreground',
        warn && 'text-status-open'
      )}
    >
      {n || '-'}
    </span>
  )
}

export function TracePage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const filter = search.q ?? ''
  const set = (patch: Partial<typeof search>, replace = true) =>
    navigate({ search: { ...search, ...patch }, replace })
  const toggle = (id: string) =>
    set({ id: id === search.id ? undefined : id }, false)

  // A link to one requirement shows it even when a filter hides it.
  const rows = useMemo(() => {
    const q = filter.trim().toLowerCase()
    return traceRows.filter(
      (r) =>
        r.req.id === search.id ||
        ((!search.kind || r.req.kind === search.kind) &&
          (!search.flag || (search.flag === 'task' ? r.noTask : r.noLink)) &&
          (!q ||
            `${r.req.id} ${Object.values(r.req.fields).join(' ')}`
              .toLowerCase()
              .includes(q)))
    )
  }, [filter, search.id, search.kind, search.flag])

  useScrollToRow(search.id)

  const chip = (on: boolean) =>
    cn('h-7 px-2.5 text-xs', on && 'border-primary/60 bg-primary/10')

  return (
    <>
      <SiteHeader title='Traceability' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Traceability</h1>
          <p className='text-sm text-muted-foreground'>
            Each requirement of the{' '}
            <a
              href={sourceUrl(meta.sources.spec)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              specification
            </a>{' '}
            (rev {meta.specRevision}) with the decisions and open items that
            name it, the checklist tasks that list it in Req, and the diagram
            items that cite it. Ranges such as "IF-030 to IF-043" count for
            every ID in them. The flags are leads for review, not defects.
          </p>
        </div>

        <div className='grid grid-cols-3 gap-2 sm:gap-4'>
          {[
            {
              title: 'Requirements',
              value: live,
              hint: `Live rows; ${removed} removed rows are listed greyed`,
              flag: undefined,
            },
            {
              title: 'No checklist task',
              value: noTask.length,
              hint: 'No task names it in Req',
              flag: 'task' as const,
            },
            {
              title: 'No decision or diagram item',
              value: noLink.length,
              hint: 'No live DEC row and no diagram item cites it',
              flag: 'link' as const,
            },
          ].map((s) => {
            const on = !!s.flag && search.flag === s.flag
            return (
              <button
                key={s.title}
                type='button'
                aria-pressed={on}
                disabled={!s.flag}
                onClick={() => set({ flag: on ? undefined : s.flag })}
                className='text-start disabled:cursor-default'
              >
                <Card
                  className={cn(
                    'h-full gap-1 py-3 transition-colors sm:py-6',
                    s.flag && 'hover:border-primary/60',
                    on && 'border-primary/60 bg-primary/5'
                  )}
                >
                  <CardHeader className='px-3 pb-0 sm:px-6'>
                    <CardTitle className='text-xs font-medium text-muted-foreground sm:text-sm'>
                      {s.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className='px-3 sm:px-6'>
                    <div
                      className={cn(
                        'text-xl font-bold tracking-tight sm:text-2xl',
                        s.flag && s.value > 0 && 'text-status-open'
                      )}
                    >
                      {s.value}
                    </div>
                    <p className='hidden text-xs text-muted-foreground sm:block'>
                      {s.hint}
                    </p>
                  </CardContent>
                </Card>
              </button>
            )
          })}
        </div>

        <Card className='gap-3'>
          <CardHeader className='space-y-3'>
            <div className='flex flex-row flex-wrap items-center justify-between gap-2'>
              <div>
                <CardTitle className='text-base'>Trace table</CardTitle>
                <CardDescription>
                  {rows.length} of {traceRows.length} rows ({live} live,{' '}
                  {removed} removed, greyed)
                </CardDescription>
              </div>
              <Input
                aria-label='Filter requirements'
                placeholder='Filter: USB, 6S, IF-040…'
                value={filter}
                onChange={(e) => set({ q: e.target.value || undefined })}
                className='h-8 w-full sm:w-72'
              />
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='Kind'>
              <Button
                variant='outline'
                size='sm'
                aria-pressed={!search.kind}
                className={chip(!search.kind)}
                onClick={() => set({ kind: undefined })}
              >
                All kinds
              </Button>
              {REQ_KINDS.map((k) => {
                const on = search.kind === k
                return (
                  <Button
                    key={k}
                    variant='outline'
                    size='sm'
                    aria-pressed={on}
                    className={cn(chip(on), 'font-mono')}
                    onClick={() => set({ kind: on ? undefined : k })}
                  >
                    {k}
                  </Button>
                )
              })}
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='Flag'>
              {(
                [
                  [undefined, 'All rows'],
                  ['task', `No task (${noTask.length})`],
                  ['link', `No decision or diagram (${noLink.length})`],
                ] as const
              ).map(([f, text]) => (
                <Button
                  key={text}
                  variant='outline'
                  size='sm'
                  aria-pressed={search.flag === f}
                  className={chip(search.flag === f)}
                  onClick={() => set({ flag: f })}
                >
                  {text}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent className='px-0'>
            <div className='overflow-x-auto'>
              <Table className='sm:table-fixed'>
                <TableHeader>
                  <TableRow>
                    <TableHead className='w-28 ps-6'>ID</TableHead>
                    <TableHead>Requirement</TableHead>
                    <TableHead className='hidden w-20 text-center md:table-cell'>
                      DEC
                    </TableHead>
                    <TableHead className='hidden w-20 text-center md:table-cell'>
                      OPEN
                    </TableHead>
                    <TableHead className='hidden w-20 text-center md:table-cell'>
                      Tasks
                    </TableHead>
                    <TableHead className='hidden w-20 text-center md:table-cell'>
                      Diagram
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((r) => {
                    const id = r.req.id
                    const open = id === search.id
                    return (
                      <TraceTableRow
                        key={id}
                        row={r}
                        open={open}
                        onToggle={() => toggle(id)}
                      />
                    )
                  })}
                  {!rows.length && (
                    <TableRow>
                      <TableCell
                        colSpan={6}
                        className='px-6 py-6 text-center text-sm text-muted-foreground'
                      >
                        No requirements match.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function TraceTableRow({
  row,
  open,
  onToggle,
}: {
  row: TraceRow
  open: boolean
  onToggle: () => void
}) {
  const r = row
  const cell = 'py-2 align-top'
  const count = cn(cell, 'hidden text-center md:table-cell')
  return (
    <>
      <TableRow
        id={`row-${r.req.id}`}
        onClick={onToggle}
        data-state={open ? 'selected' : undefined}
        className={cn(
          'cursor-pointer scroll-mt-20 data-[state=selected]:bg-primary/10',
          r.req.removed && 'text-muted-foreground'
        )}
      >
        <TableCell className={cn(cell, 'ps-6')}>
          <span className='flex items-center gap-1'>
            {open ? (
              <ChevronDown className='size-3.5 text-muted-foreground' />
            ) : (
              <ChevronRight className='size-3.5 text-muted-foreground' />
            )}
            {/* its own page: the row click opens it, so no link */}
            <IdChip id={r.req.id} plain />
          </span>
        </TableCell>
        <TableCell className={cn(cell, 'whitespace-normal')}>
          <span className='line-clamp-2 [overflow-wrap:anywhere]'>
            <MdText text={idTitle(r.req.id)} />
          </span>
          {(r.noTask || r.noLink || r.req.removed) && (
            <span className='mt-1 flex flex-wrap gap-1'>
              {r.req.removed && (
                <span className='text-[11px] text-muted-foreground'>
                  Removed row
                </span>
              )}
              {r.noTask && <Flag>No task</Flag>}
              {r.noLink && <Flag>No decision or diagram</Flag>}
            </span>
          )}
        </TableCell>
        <TableCell className={count}>
          <Count n={r.decisions.length} warn={r.noLink} />
        </TableCell>
        <TableCell className={count}>
          <Count n={r.open.length} />
        </TableCell>
        <TableCell className={count}>
          <Count n={r.tasks.length} warn={r.noTask} />
        </TableCell>
        <TableCell className={count}>
          <Count n={r.diagram.length} warn={r.noLink} />
        </TableCell>
      </TableRow>
      {open && (
        <TableRow className='bg-primary/5 hover:bg-primary/5'>
          <TableCell colSpan={6} className='px-6 py-3 whitespace-normal'>
            <TraceDetail row={r} />
          </TableCell>
        </TableRow>
      )}
    </>
  )
}

function TraceDetail({ row }: { row: TraceRow }) {
  const { req } = row
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_22rem]'>
      <div className='min-w-0 space-y-2'>
        <div className={label}>{req.section}</div>
        {Object.entries(req.fields).map(([k, v]) => (
          <div key={k}>
            <div className='text-xs text-muted-foreground'>{k}</div>
            <p className='leading-relaxed [overflow-wrap:anywhere]'>
              {v ? <SpecText text={v} /> : '-'}
            </p>
          </div>
        ))}
        <a
          href={sourceUrl(req.file, req.line)}
          target='_blank'
          rel='noreferrer'
          className='inline-block text-xs text-primary hover:underline'
        >
          Spec line {req.line}
        </a>
      </div>
      <div className='min-w-0 space-y-4'>
        <div className='space-y-2'>
          <div className={label}>Decisions</div>
          <SiteRowList rows={row.decisions} text={(d) => idTitle(d.id)} />
        </div>
        <div className='space-y-2'>
          <div className={label}>Open items</div>
          <SiteRowList
            rows={row.open}
            text={(o) => o.fields['Description'] ?? ''}
          />
        </div>
        <div className='space-y-2'>
          <div className={label}>Checklist tasks</div>
          <TaskRowList tasks={row.tasks} />
        </div>
        <div className='space-y-2'>
          <div className={label}>On the diagram</div>
          <DiagramItemList items={row.diagram} none='None.' />
        </div>
      </div>
    </div>
  )
}
