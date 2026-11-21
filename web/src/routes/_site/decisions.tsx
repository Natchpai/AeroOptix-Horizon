import { createFileRoute } from '@tanstack/react-router'
import { DecisionsPage } from '@/features/decisions'

type DecisionsSearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to this decision, e.g. DEC-050. */
  id?: string
}

export const Route = createFileRoute('/_site/decisions')({
  validateSearch: (s: Record<string, unknown>): DecisionsSearch => ({
    q: typeof s.q === 'string' && s.q ? s.q : undefined,
    id: typeof s.id === 'string' && /^DEC-\d{3}$/.test(s.id) ? s.id : undefined,
  }),
  component: DecisionsPage,
})
