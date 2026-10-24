/**
 * Checks the hand-written topology against the generated doc data.
 * Exits non-zero on any error, so `npm run build` stops.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { lineAt, places, sideOverrides } from '../src/data/places'
import { blocks, links, pinsNotOnDiagram } from '../src/data/topology'
import type {
  Level,
  Mcu,
  PinRow,
  PinSelect,
  Progress,
  SpecId,
} from '../src/data/types'
import { handlePoint, placedLayout } from '../src/features/diagram/layout'

const here = path.dirname(fileURLToPath(import.meta.url))
const gen = path.resolve(here, '../src/data/generated')
const load = <T>(name: string): T =>
  JSON.parse(fs.readFileSync(path.join(gen, name), 'utf8')) as T

const ids = load<Record<string, SpecId>>('ids.json')
const pins = load<Record<Mcu, PinRow[]>>('pins.json')
const progress = load<Progress>('progress.json')

const errors: string[] = []
const err = (msg: string) => errors.push(msg)

// 1. Every block has a source ID, and every ID exists in the spec.
const blockIds = new Set<string>()
for (const b of blocks) {
  if (blockIds.has(b.id)) err(`block ${b.id}: duplicate id`)
  blockIds.add(b.id)
  if (!b.refs.length) err(`block ${b.id}: no source ID`)
  for (const r of [...b.refs, ...(b.open ?? [])])
    if (!ids[r]) err(`block ${b.id}: ${r} is not in the spec`)
}

// 2. Links point at blocks on the same level, and their IDs exist.
const blockLevel = new Map(blocks.map((b) => [b.id, b.level]))
const linkIds = new Set<string>()
for (const l of links) {
  if (linkIds.has(l.id)) err(`link ${l.id}: duplicate id`)
  linkIds.add(l.id)
  for (const end of [l.from, l.to])
    if (blockLevel.get(end) !== l.level)
      err(`link ${l.id}: block ${end} is missing or not on level ${l.level}`)
  if (!l.refs.length) err(`link ${l.id}: no source ID`)
  for (const r of [...l.refs, ...(l.open ?? [])])
    if (!ids[r]) err(`link ${l.id}: ${r} is not in the spec`)
  for (const r of l.refs)
    if (ids[r]?.removed) err(`link ${l.id}: ${r} is a removed row`)
}

// 3. Pin selectors match rows, and every pin row is used or explained.
const select = (sel: PinSelect) => {
  const fn = sel.fn ? new RegExp(sel.fn) : null
  const sig = sel.signal ? new RegExp(sel.signal) : null
  return pins[sel.mcu].filter(
    (p) =>
      (!sel.refs || p.refs.some((r) => sel.refs!.includes(r))) &&
      (!fn || fn.test(p.function)) &&
      (!sig || sig.test(p.signal))
  )
}
const used = new Set<string>()
for (const l of links)
  for (const sel of l.pins ?? []) {
    const rows = select(sel)
    if (!rows.length) err(`link ${l.id}: pin selector matches no ${sel.mcu} row`)
    rows.forEach((r) => used.add(`${sel.mcu}:${r.pin}`))
  }
for (const mcu of ['h743', 'f100'] as Mcu[]) {
  const seenPin = new Map<string, number>()
  const seenNum = new Map<number, number>()
  for (const row of pins[mcu]) {
    if (seenPin.has(row.pin))
      err(`${mcu}: pin ${row.pin} on lines ${seenPin.get(row.pin)} and ${row.line}`)
    seenPin.set(row.pin, row.line)
    if (row.number !== null) {
      if (seenNum.has(row.number))
        err(`${mcu}: package pin ${row.number} on lines ${seenNum.get(row.number)} and ${row.line}`)
      seenNum.set(row.number, row.line)
    }
    if (used.has(`${mcu}:${row.pin}`)) continue
    const explained = pinsNotOnDiagram.some(
      (x) => x.mcu === mcu && row.refs.some((r) => x.refs.includes(r))
    )
    if (!explained)
      err(`${mcu}: pin ${row.pin} (${row.function}, line ${row.line}) is on no link`)
  }
}

// 4. Drawing: every block is placed, blocks keep apart, and every link is
//    one straight line that crosses no other line and no other block.
const GAP = 24
for (const level of ['system', 'board'] as Level[]) {
  const lv = blocks.filter((b) => b.level === level)
  const pl = places[level]
  for (const b of lv)
    if (!pl[b.id]) err(`${level}: block ${b.id} has no place in places.ts`)
  for (const id of Object.keys(pl))
    if (!lv.some((b) => b.id === id)) err(`${level}: places.ts has unknown block ${id}`)
  if (lv.some((b) => !pl[b.id])) continue

  const laid = placedLayout(lv, links.filter((l) => l.level === level), pl, sideOverrides, lineAt)
  const node = new Map(laid.nodes.map((n) => [n.block.id, n]))
  for (const a of laid.nodes)
    for (const b of laid.nodes)
      if (a.block.id < b.block.id &&
          a.x < b.x + b.w + GAP && b.x < a.x + a.w + GAP &&
          a.y < b.y + b.h + GAP && b.y < a.y + a.h + GAP)
        err(`${level}: blocks ${a.block.id} and ${b.block.id} are closer than ${GAP}px`)

  const segs = laid.edges.map((e) => {
    const s = node.get(e.link.from)!
    const t = node.get(e.link.to)!
    const p = handlePoint(s, s.handles.find((h) => h.id === e.sourceHandle)!)
    const q = handlePoint(t, t.handles.find((h) => h.id === e.targetHandle)!)
    return { id: e.link.id, from: e.link.from, to: e.link.to, p, q }
  })
  for (const g of segs)
    if (Math.abs(g.p.x - g.q.x) > 0.5 && Math.abs(g.p.y - g.q.y) > 0.5)
      err(`${level}: link ${g.id} is bent (${Math.round(g.p.x)},${Math.round(g.p.y)} to ${Math.round(g.q.x)},${Math.round(g.q.y)})`)

  // straight segments only from here
  const straight = segs.filter((g) => Math.abs(g.p.x - g.q.x) <= 0.5 || Math.abs(g.p.y - g.q.y) <= 0.5)
  const inside = (v: number, a: number, b: number) => v > Math.min(a, b) + 0.5 && v < Math.max(a, b) - 0.5
  for (const g of straight)
    for (const n of laid.nodes) {
      if (n.block.id === g.from || n.block.id === g.to) continue
      const vertical = Math.abs(g.p.x - g.q.x) <= 0.5
      const hit = vertical
        ? g.p.x > n.x && g.p.x < n.x + n.w && Math.max(g.p.y, g.q.y) > n.y && Math.min(g.p.y, g.q.y) < n.y + n.h
        : g.p.y > n.y && g.p.y < n.y + n.h && Math.max(g.p.x, g.q.x) > n.x && Math.min(g.p.x, g.q.x) < n.x + n.w
      if (hit) err(`${level}: link ${g.id} runs through block ${n.block.id}`)
    }
  for (const a of straight)
    for (const b of straight) {
      if (a.id >= b.id) continue
      const av = Math.abs(a.p.x - a.q.x) <= 0.5
      const bv = Math.abs(b.p.x - b.q.x) <= 0.5
      if (av === bv) continue
      const [v, h] = av ? [a, b] : [b, a]
      if (inside(v.p.x, h.p.x, h.q.x) && inside(h.p.y, v.p.y, v.q.y))
        err(`${level}: links ${a.id} and ${b.id} cross`)
    }
}

if (errors.length) {
  console.error(`check-data: ${errors.length} error(s)`)
  for (const e of errors) console.error(`  - ${e}`)
  process.exit(1)
}
const openCount = Object.values(ids).filter(
  (s) => s.kind === 'OPEN' && !s.closed
).length
console.log(
  `check-data: OK (${blocks.length} blocks, ${links.length} links, ${used.size} pins on links, ` +
    `${openCount} open items, ${progress.gates.length} gates)`
)
