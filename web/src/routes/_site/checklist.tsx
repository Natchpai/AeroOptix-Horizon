import { createFileRoute } from '@tanstack/react-router'
import { ChecklistPage } from '@/features/checklist'

type ChecklistSearch = {
  /** Filter text. */
  q?: string
  /** Open and scroll to this task, e.g. P3-007. */
  id?: string
  /** Show only this gate's tasks, e.g. P3. */
  gate?: string
  /** Show only tasks with this status, e.g. OPEN. */
  status?: string
}

const str = (v: unknown, re: RegExp) =>
  typeof v === 'string' && re.test(v) ? v : undefined

export const Route = createFileRoute('/_site/checklist')({
  validateSearch: (s: Record<string, unknown>): ChecklistSearch => ({
    q: typeof s.q === 'string' && s.q ? s.q : undefined,
    id: str(s.id, /^P\d-\d{3}$/),
    gate: str(s.gate, /^P\d$/),
    status: str(s.status, /^[A-Z_/]+$/),
  }),
  component: ChecklistPage,
})
