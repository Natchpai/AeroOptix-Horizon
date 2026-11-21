import { createFileRoute } from '@tanstack/react-router'
import { TracePage } from '@/features/trace'

type TraceSearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to this requirement, e.g. IF-010. */
  id?: string
  /** Show only this kind, e.g. PWR. */
  kind?: string
  /** Show only flagged rows: no task, or no decision and no diagram item. */
  flag?: 'task' | 'link'
}

export const Route = createFileRoute('/_site/trace')({
  validateSearch: (s: Record<string, unknown>): TraceSearch => ({
    q: typeof s.q === 'string' && s.q ? s.q : undefined,
    id:
      typeof s.id === 'string' && /^[A-Z]{2,5}-\d{2,3}$/.test(s.id)
        ? s.id
        : undefined,
    kind:
      typeof s.kind === 'string' && /^[A-Z]{2,5}$/.test(s.kind)
        ? s.kind
        : undefined,
    flag: s.flag === 'task' || s.flag === 'link' ? s.flag : undefined,
  }),
  component: TracePage,
})
