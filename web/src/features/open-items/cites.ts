import { type SpecId, type Task, ids, progress } from '@/data'

const OPEN_ID = /\bOPEN-\d{3}\b/g
export const TASK_ID = /\bP\d-\d{3}\b/g

const openRows = Object.values(ids).filter((s) => s.kind === 'OPEN')
const rowText = (s: SpecId) => Object.values(s.fields).join(' ')
const taskText = (t: Task) => [t.task, t.req, t.owner, t.evidence].join(' ')

/**
 * Open items that name a task in their own row (usually the owner column),
 * plus the ones the task's text names. Open items first, then closed.
 */
export function openItemsNaming(taskId: string, text: string): SpecId[] {
  const named = new Set(text.match(OPEN_ID) ?? [])
  const re = new RegExp(`\\b${taskId}\\b`)
  return openRows
    .filter((s) => named.has(s.id) || re.test(rowText(s)))
    .sort(
      (a, b) => Number(a.closed) - Number(b.closed) || a.id.localeCompare(b.id)
    )
}

/**
 * Checklist tasks an open item names in its row, plus the tasks whose
 * text names the open item. In ID order.
 */
export function tasksNaming(row: SpecId): Task[] {
  const named = new Set(rowText(row).match(TASK_ID) ?? [])
  const re = new RegExp(`\\b${row.id}\\b`)
  return Object.values(progress.tasks)
    .filter((t) => named.has(t.id) || re.test(taskText(t)))
    .sort((a, b) => a.id.localeCompare(b.id))
}
