import { createFileRoute } from '@tanstack/react-router'
import { BomPage } from '@/features/bom'

type BomSearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to the row that holds this reference, e.g. R306. */
  id?: string
  /** Fitted rows only, or DNP rows only. */
  dnp?: 'fitted' | 'dnp'
}

export const Route = createFileRoute('/_site/bom')({
  validateSearch: (s: Record<string, unknown>): BomSearch => ({
    q: typeof s.q === 'string' && s.q ? s.q : undefined,
    id: typeof s.id === 'string' && /^[A-Z]+\d+$/.test(s.id) ? s.id : undefined,
    dnp: s.dnp === 'fitted' || s.dnp === 'dnp' ? s.dnp : undefined,
  }),
  component: BomPage,
})
