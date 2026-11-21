import { useMemo } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import { type SpecChange, meta, sourceUrl } from '@/data'
import historyJson from '@/data/generated/history.json'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { useScrollToRow } from '@/lib/record-rows'
import { cn } from '@/lib/utils'
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
import { Main } from '@/components/layout/main'
import { SiteHeader } from '@/components/layout/site-header'
import { SpecText } from '@/components/spec-text'

const route = getRouteApi('/_site/history')

/** Every spec change note, newest first, as the extractor read it. */
const history = historyJson as SpecChange[]

export function HistoryPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const filter = search.q ?? ''
  const setFilter = (q: string) =>
    navigate({ search: { ...search, q: q || undefined }, replace: true })
  const toggle = (rev: string) =>
    navigate({
      search: { ...search, rev: rev === search.rev ? undefined : rev },
    })

  // A link to one revision shows it even when the filter hides it.
  const rows = useMemo(() => {
    const q = filter.trim().toLowerCase()
    return history.filter(
      (c) =>
        c.revision === search.rev ||
        !q ||
        `rev ${c.revision} ${c.date} ${c.description} ${c.approvedBy}`
          .toLowerCase()
          .includes(q)
    )
  }, [filter, search.rev])

  useScrollToRow(search.rev, 'rev-')

  return (
    <>
      <SiteHeader title='Spec history' />
      <Main className='space-y-4'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Spec history</h1>
          <p className='text-sm text-muted-foreground'>
            The change-note table (section 9) of the{' '}
            <a
              href={sourceUrl(meta.sources.spec)}
              target='_blank'
              rel='noreferrer'
              className='text-primary hover:underline'
            >
              specification
            </a>
            , newest first, as written there. Spec IDs open their row. Click a
            revision for its full note.
          </p>
        </div>

        <Card className='gap-3'>
          <CardHeader className='flex flex-row flex-wrap items-center justify-between gap-2'>
            <div>
              <CardTitle className='text-base'>Change notes</CardTitle>
              <CardDescription>
                {rows.length} of {history.length} revisions ·{' '}
                {history[history.length - 1]?.date} to {history[0]?.date}
              </CardDescription>
            </div>
            <Input
              placeholder='Filter: TPS2121, DEC-050, 2026-11…'
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className='h-8 w-full sm:w-72'
            />
          </CardHeader>
          <CardContent className='px-0'>
            <div className='overflow-x-auto'>
              <Table className='sm:table-fixed'>
                <TableHeader>
                  <TableRow>
                    <TableHead className='w-24 ps-6'>Rev</TableHead>
                    <TableHead className='hidden w-28 sm:table-cell'>
                      Date
                    </TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className='hidden w-36 md:table-cell'>
                      Approved by
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((c) => {
                    const open = c.revision === search.rev
                    return (
                      <TableRow
                        key={c.revision}
                        id={`rev-${c.revision}`}
                        onClick={() => toggle(c.revision)}
                        data-state={open ? 'selected' : undefined}
                        className='cursor-pointer scroll-mt-20 align-top data-[state=selected]:bg-primary/10'
                      >
                        <TableCell className='py-2 ps-6 align-top'>
                          <span className='flex items-center gap-1 font-mono text-xs font-semibold whitespace-nowrap'>
                            {open ? (
                              <ChevronDown className='size-3.5 text-muted-foreground' />
                            ) : (
                              <ChevronRight className='size-3.5 text-muted-foreground' />
                            )}
                            {c.revision}
                          </span>
                        </TableCell>
                        <TableCell className='hidden py-2 align-top font-mono text-xs whitespace-nowrap text-muted-foreground sm:table-cell'>
                          {c.date}
                        </TableCell>
                        <TableCell className='py-2 align-top whitespace-normal'>
                          <div className='mb-1 font-mono text-xs text-muted-foreground sm:hidden'>
                            {c.date} · {c.approvedBy}
                          </div>
                          <p
                            className={cn(
                              'leading-relaxed [overflow-wrap:anywhere]',
                              !open && 'line-clamp-3'
                            )}
                          >
                            {/* in a collapsed row a chip click opens the
                                row; in an open row it opens the chip only */}
                            <span
                              onClickCapture={(e) => {
                                if (!open) e.preventDefault()
                              }}
                              onClick={(e) => {
                                const t = e.target as HTMLElement
                                if (open && t.closest('a')) e.stopPropagation()
                              }}
                            >
                              <SpecText text={c.description} />
                            </span>
                          </p>
                          {open && (
                            <a
                              href={sourceUrl(meta.sources.spec, c.line)}
                              target='_blank'
                              rel='noreferrer'
                              onClick={(e) => e.stopPropagation()}
                              className='mt-2 inline-block text-xs text-primary hover:underline'
                            >
                              Spec line {c.line}
                            </a>
                          )}
                        </TableCell>
                        <TableCell className='hidden py-2 align-top text-xs whitespace-normal text-muted-foreground md:table-cell'>
                          {c.approvedBy}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  {!rows.length && (
                    <TableRow>
                      <TableCell
                        colSpan={4}
                        className='px-6 py-6 text-center text-sm text-muted-foreground'
                      >
                        No change notes match.
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
