import { createFileRoute } from '@tanstack/react-router'
import { HistoryPage } from '@/features/history'

type HistorySearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to this revision, e.g. 0.86. */
  rev?: string
}

export const Route = createFileRoute('/_site/history')({
  validateSearch: (s: Record<string, unknown>): HistorySearch => {
    // a revision like 0.86 may arrive as a number
    const rev = typeof s.rev === 'number' ? String(s.rev) : s.rev
    return {
      q: typeof s.q === 'string' && s.q ? s.q : undefined,
      rev: typeof rev === 'string' && /^[\w.]+$/.test(rev) ? rev : undefined,
    }
  },
  component: HistoryPage,
})
