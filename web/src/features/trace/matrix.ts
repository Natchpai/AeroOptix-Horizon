import {
  type Block,
  type Link,
  type SpecId,
  type Task,
  blocks,
  ids,
  links,
  progress,
} from '@/data'

/** Spec ID kinds that are requirements (the rows of the trace table). */
export const REQ_KINDS = [
  'SYS',
  'MCU',
  'IF',
  'SEN',
  'PWR',
  'SAF',
  'FUN',
  'ENV',
  'CMP',
  'MEC',
  'PCB',
  'MFG',
  'TST',
]

const pad = (n: number, width: number) => String(n).padStart(width, '0')

/**
 * Every spec ID a text names, with ranges written as "IF-030 to IF-043"
 * expanded to the IDs between them that exist in the spec.
 */
export function idsIn(text: string): Set<string> {
  const out = new Set<string>()
  const re = /\b([A-Z]{2,5})-(\d{2,3})\b(?:\s+to\s+\1-(\d{2,3})\b)?/g
  for (const m of text.matchAll(re)) {
    const [, kind, from, to] = m
    if (!to) {
      out.add(`${kind}-${from}`)
      continue
    }
    for (let n = Number(from); n <= Number(to); n++) {
      const id = `${kind}-${pad(n, from.length)}`
      if (ids[id]) out.add(id)
    }
  }
  return out
}

export type TraceRow = {
  req: SpecId
  decisions: SpecId[]
  open: SpecId[]
  tasks: Task[]
  diagram: (Block | Link)[]
  /** No checklist task names it in Req. */
  noTask: boolean
  /** No live decision and no diagram item cites it. */
  noLink: boolean
}

const specRows = Object.values(ids)
const decRows = specRows.filter((s) => s.kind === 'DEC')
const openRows = specRows.filter((s) => s.kind === 'OPEN')
const taskRows = Object.values(progress.tasks)

// what each source names, computed once
const decCites = decRows.map((d) => ({
  row: d,
  ids: idsIn(`${d.fields['Topic'] ?? ''} ${d.fields['Selected option'] ?? ''}`),
}))
const openCites = openRows.map((o) => ({
  row: o,
  ids: idsIn(Object.values(o.fields).join(' ')),
}))
const taskCites = taskRows.map((t) => ({ row: t, ids: idsIn(t.req) }))
const diagramCites = [...blocks, ...links].map((item) => ({
  row: item,
  ids: idsIn(item.refs.join(' ')),
}))

const citing = <T>(list: { row: T; ids: Set<string> }[], id: string) =>
  list.filter((c) => c.ids.has(id)).map((c) => c.row)

/** One row per requirement ID, in spec order. */
export const traceRows: TraceRow[] = specRows
  .filter((s) => REQ_KINDS.includes(s.kind))
  .map((req) => {
    const decisions = citing(decCites, req.id)
    const open = citing(openCites, req.id)
    const tasks = citing(taskCites, req.id)
    const diagram = citing(diagramCites, req.id)
    return {
      req,
      decisions,
      open,
      tasks,
      diagram,
      // a removed requirement needs nothing, so it is never flagged
      noTask: !req.removed && tasks.length === 0,
      noLink:
        !req.removed &&
        !decisions.some((d) => !d.removed) &&
        diagram.length === 0,
    }
  })
