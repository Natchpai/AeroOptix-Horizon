import { createFileRoute } from '@tanstack/react-router'
import { OpenItemsPage } from '@/features/open-items'

type OpenSearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to this item, e.g. OPEN-023. */
  id?: string
  /** Also list closed items. */
  closed?: boolean
}

export const Route = createFileRoute('/_site/open')({
  validateSearch: (s: Record<string, unknown>): OpenSearch => ({
    q: typeof s.q === 'string' && s.q ? s.q : undefined,
    id:
      typeof s.id === 'string' && /^OPEN-\d{3}$/.test(s.id) ? s.id : undefined,
    closed: s.closed === true || s.closed === 'true' ? true : undefined,
  }),
  component: OpenItemsPage,
})
