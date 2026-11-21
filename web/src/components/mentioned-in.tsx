import { useEffect, useState } from 'react'
import { Link } from '@tanstack/react-router'
import type { SpecChange } from '@/data'
import { loadHistory, mentionsOf } from '@/lib/history-mentions'
import { detailLabel } from '@/lib/record-rows'
import { Button } from '@/components/ui/button'

/** Chips shown before "+N more". */
const FIRST = 12

/**
 * "Mentioned in": the spec revisions whose change note names `id`, newest
 * first, each a revision chip that opens its row on Spec history. For the
 * detail rows of Decisions, Open items and Traceability. The notes load
 * when the first row opens. If they fail to load, a note offers a page
 * reload: after a deploy the old notes chunk is gone, so a retry alone would
 * fail again.
 */
export function MentionedIn({ id }: { id: string }) {
  const [history, setHistory] = useState<SpecChange[]>()
  const [failed, setFailed] = useState(false)
  const [all, setAll] = useState(false)
  useEffect(() => {
    let live = true
    loadHistory().then(
      (h) => live && setHistory(h),
      () => live && setFailed(true)
    )
    return () => {
      live = false
    }
  }, [])
  const found = history ? mentionsOf(history, id) : []
  const shown = all ? found : found.slice(0, FIRST)
  return (
    <div className='space-y-2' data-mentioned-in={id}>
      <div className={detailLabel}>Mentioned in</div>
      <p className='text-xs text-muted-foreground'>
        Spec change notes that name this ID; ranges are not expanded.
      </p>
      {failed ? (
        <div className='flex flex-wrap items-center gap-2 text-xs text-muted-foreground'>
          <span>Could not load the change notes.</span>
          <Button
            variant='outline'
            size='sm'
            className='h-6 px-2 text-xs'
            onClick={() => location.reload()}
          >
            Reload page
          </Button>
        </div>
      ) : !history ? (
        <p className='text-xs text-muted-foreground'>Loading…</p>
      ) : !found.length ? (
        <p className='text-xs text-muted-foreground'>
          Not named in any change note.
        </p>
      ) : (
        <div className='flex flex-wrap gap-1'>
          {shown.map((c) => (
            <Link
              key={c.revision}
              to='/history'
              // a string, so 0.10 stays 0.10 in the URL (not 0.1)
              search={{ rev: c.revision }}
              title={c.date}
              className='rounded border border-primary/40 px-1.5 py-0.5 font-mono text-[11px] leading-none whitespace-nowrap text-primary hover:bg-primary/10'
            >
              rev {c.revision}
            </Link>
          ))}
          {found.length > shown.length && (
            <button
              type='button'
              onClick={() => setAll(true)}
              className='rounded border border-dashed border-border px-1.5 py-0.5 text-[11px] leading-none whitespace-nowrap text-muted-foreground hover:bg-muted'
            >
              +{found.length - shown.length} more
            </button>
          )}
        </div>
      )}
    </div>
  )
}
