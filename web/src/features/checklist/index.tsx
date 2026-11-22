import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import {
  type ColumnDef,
  type FilterFn,
  type SortingState,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { type Task, ids, meta, progress, sourceUrl } from '@/data'
import { ChevronDown, ChevronRight } from 'lucide-react'
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
import { RecordTable, SiteRowList } from '@/components/record-table'
import { SpecText } from '@/components/spec-text'
import {
  GateBar,
  StatusBadge,
  TaskLegend,
  allTaskStates,
  taskState,
} from '@/components/task-status'
import { TASK_ID, openItemsNaming } from '@/features/open-items/cites'

const route = getRouteApi('/_site/checklist')

/** Every task row, in record order. */
const tasks = Object.values(progress.tasks)

/** The owners of a task: the Owner cell split on "," and "+". */
const ownersOf = (t: Task) =>
  t.owner
    .split(/[,+]/)
    .map((o) => o.trim())
    .filter(Boolean)

/** Every owner name, most tasks first. */
const ownerNames = (() => {
  const n = new Map<string, number>()
  for (const t of tasks)
    for (const o of ownersOf(t)) n.set(o, (n.get(o) ?? 0) + 1)
  return [...n]
    .sort(([a, x], [b, y]) => y - x || a.localeCompare(b))
    .map(([o]) => o)
})()

/**
 * For each gate that is not done, the open items (not closed or removed)
 * whose "Owner / next action" cell names one of the gate's tasks.
 */
const gateBlockers = new Map(
  progress.gates
    .filter((g) => g.status !== 'DONE')
    .map((g) => {
      const open = Object.values(ids)
        .filter((s) => s.kind === 'OPEN' && !s.closed && !s.removed)
        .filter((s) =>
          // matchAll works on a copy, so the shared regex keeps no lastIndex
          [...(s.fields['Owner / next action'] ?? '').matchAll(TASK_ID)].some(
            ([id]) => progress.tasks[id]?.gate === g.id
          )
        )
        .map((s) => s.id)
        .sort()
      return [g.id, open]
    })
)

/** The filter searches the whole row. */
const rowText: FilterFn<Task> = (row, _col, value: string) => {
  const q = value.trim().toLowerCase()
  const t = row.original
  return (
    !q ||
    [t.id, t.task, t.req, t.owner, t.statusText, t.evidence]
      .join(' ')
      .toLowerCase()
      .includes(q)
  )
}

const label = detailLabel

export function ChecklistPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const [sorting, setSorting] = useState<SortingState>([])
  const filter = search.q ?? ''
  const set = (patch: Partial<typeof search>, replace = true) =>
    navigate({ search: { ...search, ...patch }, replace })
  const toggle = (id: string) =>
    set({ id: id === search.id ? undefined : id }, false)

  const byGate = (t: Task) => !search.gate || t.gate === search.gate
  const byStatus = (t: Task) => !search.status || t.status === search.status
  const byOwner = (t: Task) =>
    !search.owner || ownersOf(t).includes(search.owner)

  // A link to one task shows it even when the gate, status or owner filter
  // hides it.
  const data = useMemo(
    () =>
      tasks.filter(
        (t) =>
          t.id === search.id ||
          ((!search.gate || t.gate === search.gate) &&
            (!search.status || t.status === search.status) &&
            (!search.owner || ownersOf(t).includes(search.owner)))
      ),
    [search.gate, search.status, search.owner, search.id]
  )
  // Each chip row counts the tasks the other filters leave.
  const forStates = tasks.filter((t) => byGate(t) && byOwner(t))
  const forOwners = tasks.filter((t) => byGate(t) && byStatus(t))
  // A ?status= or ?owner= value no chip names (an old or mistyped link)
  // still shows as a pressed chip, so the filter is visible and one click
  // clears it.
  const otherStatus =
    search.status && !allTaskStates.some((s) => s.key === search.status)
      ? {
          ...taskState(search.status),
          n: forStates.filter((t) => t.status === search.status).length,
        }
      : undefined
  const otherOwner =
    search.owner && !ownerNames.includes(search.owner)
      ? search.owner
      : undefined

  const columns = useMemo<ColumnDef<Task>[]>(
    () => [
      {
        accessorKey: 'id',
        meta: { thClassName: 'w-24 sm:w-28' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='ID' />
        ),
        cell: ({ row }) => (
          <span className='flex items-center gap-1 font-mono text-xs font-semibold whitespace-nowrap'>
            {row.original.id === search.id ? (
              <ChevronDown className='size-3.5 text-muted-foreground' />
            ) : (
              <ChevronRight className='size-3.5 text-muted-foreground' />
            )}
            {/* on a phone the status column is hidden; a dot keeps it */}
            <span
              className='size-2 shrink-0 rounded-full sm:hidden'
              style={{ background: taskState(row.original.status).color }}
              title={row.original.status}
            />
            {row.original.id}
          </span>
        ),
      },
      {
        accessorKey: 'task',
        header: 'Task',
        enableSorting: false,
        cell: ({ row }) => (
          <span className='line-clamp-2 [overflow-wrap:anywhere]'>
            <MdText text={row.original.task} />
          </span>
        ),
      },
      {
        accessorKey: 'req',
        meta: { className: 'hidden lg:table-cell', thClassName: 'w-[18%]' },
        header: 'Req',
        enableSorting: false,
        cell: ({ row }) => (
          <span className='line-clamp-2 font-mono text-xs [overflow-wrap:anywhere] text-muted-foreground'>
            {row.original.req || '-'}
          </span>
        ),
      },
      {
        accessorKey: 'owner',
        meta: { className: 'hidden md:table-cell', thClassName: 'w-[14%]' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Owner' />
        ),
        cell: ({ row }) => (
          <span className='line-clamp-2 [overflow-wrap:anywhere] text-muted-foreground'>
            <MdText text={row.original.owner || '-'} />
          </span>
        ),
      },
      {
        accessorKey: 'status',
        meta: { className: 'hidden sm:table-cell', thClassName: 'w-28' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Status' />
        ),
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
    ],
    [search.id]
  )

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    globalFilterFn: rowText,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  useScrollToRow(search.id)

  const rows = table.getRowModel().rows
  const chip = (on: boolean) =>
    cn('h-7 px-2.5 text-xs', on && 'border-primary/60 bg-primary/10')

  return (
    <>
      <SiteHeader title='Checklist' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Checklist</h1>
          <p className='text-sm text-muted-foreground'>
            Every gate and task of the{' '}
            <a
              href={sourceUrl(meta.sources.checklist)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              execution checklist
            </a>{' '}
            (rev {progress.revision} · {progress.updated}), as written there.
            Gates are work stages, not the project phase. A{' '}
            <span className='font-mono'>DONE</span> task is not a measured or
            verified result.
          </p>
        </div>

        <Card className='gap-3'>
          <CardHeader>
            <CardTitle className='text-base'>Gates</CardTitle>
            <CardDescription>
              Click a gate to list its tasks below.
            </CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <ul className='divide-y divide-border'>
              {progress.gates.map((g) => {
                const total = Object.entries(g.counts)
                  .filter(([k]) => k !== 'N/A')
                  .reduce((t, [, n]) => t + n, 0)
                const on = search.gate === g.id
                const blockers = gateBlockers.get(g.id) ?? []
                return (
                  <li key={g.id}>
                    <button
                      type='button'
                      aria-pressed={on}
                      onClick={() =>
                        set({ gate: on ? undefined : g.id, id: undefined })
                      }
                      className={cn(
                        '-mx-2 grid w-[calc(100%+1rem)] gap-x-6 gap-y-1.5 rounded-md px-2 py-3 text-start text-sm transition-colors hover:bg-muted/50 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]',
                        on && 'bg-primary/10 hover:bg-primary/10'
                      )}
                    >
                      <div className='space-y-1.5'>
                        <div className='flex items-center gap-2'>
                          <span className='rounded border border-primary/40 px-1.5 py-0.5 font-mono text-[11px] leading-none text-primary'>
                            {g.id}
                          </span>
                          <span className='min-w-0 font-medium'>{g.name}</span>
                          <span className='ms-auto flex shrink-0 items-center gap-2 text-xs text-muted-foreground'>
                            {g.counts.DONE ?? 0} of {total} done
                            <StatusBadge status={g.status} />
                          </span>
                        </div>
                        <GateBar counts={g.counts} />
                      </div>
                      <div className='text-xs leading-relaxed text-muted-foreground'>
                        <MdText text={g.exit} />
                        {g.note && (
                          <span className='mt-1 block'>
                            <MdText text={g.note} />
                          </span>
                        )}
                      </div>
                    </button>
                    {blockers.length > 0 && (
                      <div
                        className='flex flex-wrap items-center gap-1.5 pb-3 text-xs text-muted-foreground'
                        data-gate-blockers={g.id}
                      >
                        <span>Open items naming this gate's tasks:</span>
                        {blockers.map((id) => (
                          <IdChip key={id} id={id} />
                        ))}
                      </div>
                    )}
                  </li>
                )
              })}
            </ul>
            <TaskLegend />
          </CardContent>
        </Card>

        <Card className='gap-3'>
          <CardHeader className='space-y-3'>
            <div className='flex flex-row flex-wrap items-center justify-between gap-2'>
              <div>
                <CardTitle className='text-base'>
                  Tasks{search.gate && ` in ${search.gate}`}
                </CardTitle>
                <CardDescription>
                  {rows.length} of {tasks.length} tasks
                </CardDescription>
              </div>
              <Input
                aria-label='Filter tasks'
                placeholder='Filter: ERC, OPEN-023, Human…'
                value={filter}
                onChange={(e) => set({ q: e.target.value || undefined })}
                className='h-8 w-full sm:w-72'
              />
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='Gate'>
              <Button
                variant='outline'
                size='sm'
                aria-pressed={!search.gate}
                className={chip(!search.gate)}
                onClick={() => set({ gate: undefined })}
              >
                All gates
              </Button>
              {progress.gates.map((g) => (
                <Button
                  key={g.id}
                  variant='outline'
                  size='sm'
                  aria-pressed={search.gate === g.id}
                  className={cn(chip(search.gate === g.id), 'font-mono')}
                  onClick={() =>
                    set({ gate: search.gate === g.id ? undefined : g.id })
                  }
                >
                  {g.id}
                </Button>
              ))}
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='Status'>
              <Button
                variant='outline'
                size='sm'
                aria-pressed={!search.status}
                className={chip(!search.status)}
                onClick={() => set({ status: undefined })}
              >
                All states
              </Button>
              {allTaskStates.map((s) => {
                const n = forStates.filter((t) => t.status === s.key).length
                if (!n && search.status !== s.key) return null
                const on = search.status === s.key
                return (
                  <Button
                    key={s.key}
                    variant='outline'
                    size='sm'
                    aria-pressed={on}
                    className={chip(on)}
                    onClick={() => set({ status: on ? undefined : s.key })}
                  >
                    <span
                      className='size-2 rounded-sm'
                      style={{ background: s.color }}
                    />
                    {s.label}
                    <span className='text-muted-foreground'>{n}</span>
                  </Button>
                )
              })}
              {otherStatus && (
                <Button
                  variant='outline'
                  size='sm'
                  aria-pressed
                  className={chip(true)}
                  onClick={() => set({ status: undefined })}
                >
                  <span
                    className='size-2 rounded-sm'
                    style={{ background: otherStatus.color }}
                  />
                  {otherStatus.label}
                  <span className='text-muted-foreground'>{otherStatus.n}</span>
                </Button>
              )}
            </div>
            <div className='flex flex-wrap gap-1.5' aria-label='Owner'>
              <Button
                variant='outline'
                size='sm'
                aria-pressed={!search.owner}
                className={chip(!search.owner)}
                onClick={() => set({ owner: undefined })}
              >
                All owners
              </Button>
              {ownerNames.map((o) => {
                const n = forOwners.filter((t) =>
                  ownersOf(t).includes(o)
                ).length
                if (!n && search.owner !== o) return null
                const on = search.owner === o
                return (
                  <Button
                    key={o}
                    variant='outline'
                    size='sm'
                    aria-pressed={on}
                    className={chip(on)}
                    onClick={() => set({ owner: on ? undefined : o })}
                  >
                    {o}
                    <span className='text-muted-foreground'>{n}</span>
                  </Button>
                )
              })}
              {otherOwner && (
                <Button
                  variant='outline'
                  size='sm'
                  aria-pressed
                  className={chip(true)}
                  onClick={() => set({ owner: undefined })}
                >
                  {otherOwner}
                  <span className='text-muted-foreground'>0</span>
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className='px-0'>
            <RecordTable
              table={table}
              openId={search.id}
              getId={(t) => t.id}
              onToggle={toggle}
              detail={(t) => <TaskDetail task={t} />}
              rowClassName={(t) =>
                t.status === 'N/A' && 'text-muted-foreground'
              }
              empty='No tasks match.'
            />
          </CardContent>
        </Card>
      </Main>
    </>
  )
}

function TaskDetail({ task }: { task: Task }) {
  const open = openItemsNaming(task.id, `${task.task} ${task.req}`)
  return (
    <div className='grid gap-4 text-sm lg:grid-cols-[minmax(0,1fr)_18rem]'>
      <div className='min-w-0 space-y-2'>
        <div className={label}>Task</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <SpecText text={task.task} />
        </p>
        <div className={label}>Req</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          {task.req ? <SpecText text={task.req} /> : '-'}
        </p>
        <div className={label}>Owner · status</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          <MdText text={task.owner || '-'} /> ·{' '}
          <MdText text={task.statusText} />
        </p>
        <div className={label}>Evidence required / link</div>
        <p className='leading-relaxed [overflow-wrap:anywhere]'>
          {task.evidence ? <SpecText text={task.evidence} /> : '-'}
        </p>
        <a
          href={sourceUrl(meta.sources.checklist, task.line)}
          target='_blank'
          rel='noreferrer'
          className='inline-block text-xs text-primary hover:underline'
        >
          Checklist line {task.line}
        </a>
      </div>
      <div className='min-w-0 space-y-2'>
        <div className={label}>Open items</div>
        <SiteRowList
          rows={open}
          text={(o) => o.fields['Description'] ?? ''}
          none='No open item names this task.'
        />
      </div>
    </div>
  )
}
