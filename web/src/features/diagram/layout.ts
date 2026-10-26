import type { Block, Link } from '@/data'
import type { Place, Side, Zone } from '@/data/places'
import { draw } from './style'

const NODE_W = 200
const NODE_H = 60

export type { Side }
export type Point = { x: number; y: number }

/** One link end on a block side; pos runs 0..1 along that side. */
export type HandleSpec = {
  id: string
  side: Side
  pos: number
  type: 'source' | 'target'
}

export type LaidNode = {
  block: Block
  x: number
  y: number
  w: number
  h: number
  handles: HandleSpec[]
}

export type LaidEdge = {
  link: Link
  sourceHandle: string
  targetHandle: string
  /** Label position along the line, 0..1; staggered for parallel links. */
  labelAt: number
  /** Side of a vertical line the label sits beside; centered when unset. */
  labelSide?: 'left' | 'right'
}

export type LaidOut = { nodes: LaidNode[]; edges: LaidEdge[] }

/** Absolute position of a link end. */
export function handlePoint(n: LaidNode, h: HandleSpec): Point {
  switch (h.side) {
    case 'left':
      return { x: n.x, y: n.y + h.pos * n.h }
    case 'right':
      return { x: n.x + n.w, y: n.y + h.pos * n.h }
    case 'top':
      return { x: n.x + h.pos * n.w, y: n.y }
    default:
      return { x: n.x + h.pos * n.w, y: n.y + n.h }
  }
}

export type LaidZone = {
  zone: Zone
  x: number
  y: number
  w: number
  h: number
}

/** A zone's box: its blocks, plus padding and a title band on top. */
export function zoneBoxes(zones: Zone[], nodes: LaidNode[]): LaidZone[] {
  const { pad, head } = draw.zone
  return zones.map((zone) => {
    const ns = nodes.filter((n) => zone.blocks.includes(n.block.id))
    const x = Math.min(...ns.map((n) => n.x)) - pad
    const y = Math.min(...ns.map((n) => n.y)) - pad - head
    const r = Math.max(...ns.map((n) => n.x + n.w)) + pad
    const b = Math.max(...ns.map((n) => n.y + n.h)) + pad
    return { zone, x, y, w: r - x, h: b - y }
  })
}

/**
 * Side of a connector where its cable plugs in. On the Overview its links
 * are the cables, so the tab faces them; inside the board its links go to
 * the MCU, so the tab faces away.
 */
export function cableSide(block: Block, handles: HandleSpec[]): Side {
  const opposite: Record<Side, Side> = {
    left: 'right',
    right: 'left',
    top: 'bottom',
    bottom: 'top',
  }
  if (!handles.length) return 'right'
  const side = handles[0].side
  return block.level === 'system' ? side : opposite[side]
}

/** Height from which a small block is drawn as a centred column. */
export const TALL = 120

/** Smallest gap between two link ends on one side, and from a corner. */
const END_GAP = 28
const END_MARGIN = 12

/**
 * Hand-placed layout. Each link end sits on the side of its block that
 * faces the other block (or the side given in `sides`). Where the two
 * blocks overlap along that side, both ends sit at the middle of the
 * overlap, so the line runs straight. Ends on one side keep END_GAP
 * apart, so lines never meet at one point.
 */
export function placedLayout(
  blocks: Block[],
  links: Link[],
  places: Record<string, Place>,
  sides: Record<string, [Side, Side]> = {},
  lineAt: Record<string, number> = {}
): LaidOut {
  const box = new Map(
    blocks.map((b) => {
      const p = places[b.id]
      return [b.id, { x: p.x, y: p.y, w: p.w ?? NODE_W, h: p.h ?? NODE_H }]
    })
  )
  const facing = (from: string, to: string): [Side, Side] => {
    const a = box.get(from)!
    const b = box.get(to)!
    if (b.x >= a.x + a.w) return ['right', 'left']
    if (b.x + b.w <= a.x) return ['left', 'right']
    if (b.y >= a.y + a.h) return ['bottom', 'top']
    return ['top', 'bottom']
  }
  const isVertical = (side: Side) => side === 'left' || side === 'right'
  /** Span of a block along a side: [start, end] in absolute px. */
  const span = (id: string, side: Side): [number, number] => {
    const b = box.get(id)!
    return isVertical(side) ? [b.y, b.y + b.h] : [b.x, b.x + b.w]
  }
  const clamp = (v: number, [lo, hi]: [number, number]) =>
    Math.min(Math.max(v, lo + END_MARGIN), hi - END_MARGIN)

  type End = {
    node: string
    side: Side
    id: string
    type: 'source' | 'target'
    want: number
  }
  const ends: End[] = []
  const sourceSide = new Map<string, Side>()
  const edges: LaidEdge[] = links.map((l) => {
    const [ss, ts] = sides[l.id] ?? facing(l.from, l.to)
    sourceSide.set(l.id, ss)
    const sa = span(l.from, ss)
    const ta = span(l.to, ts)
    let ws: number
    let wt: number
    const lo = Math.max(sa[0], ta[0]) + END_MARGIN
    const hi = Math.min(sa[1], ta[1]) - END_MARGIN
    if (isVertical(ss) === isVertical(ts) && lo <= hi) {
      ws = wt = lineAt[l.id] ?? (lo + hi) / 2
    } else {
      ws = clamp((ta[0] + ta[1]) / 2, sa)
      wt = clamp((sa[0] + sa[1]) / 2, ta)
    }
    const sourceHandle = `${l.id}:s`
    const targetHandle = `${l.id}:t`
    ends.push({
      node: l.from,
      side: ss,
      id: sourceHandle,
      type: 'source',
      want: ws,
    })
    ends.push({
      node: l.to,
      side: ts,
      id: targetHandle,
      type: 'target',
      want: wt,
    })
    return { link: l, sourceHandle, targetHandle, labelAt: 0.5 }
  })

  const handles = new Map<string, HandleSpec[]>()
  const groups = new Map<string, End[]>()
  for (const e of ends) {
    const k = `${e.node}|${e.side}`
    groups.set(k, [...(groups.get(k) ?? []), e])
  }
  for (const list of groups.values()) {
    const [a, b] = span(list[0].node, list[0].side)
    const len = b - a
    list.sort((p, q) => p.want - q.want)
    const at = list.map((e) => e.want)
    // push apart forwards, then back from the far corner
    for (let i = 0; i < at.length; i++)
      at[i] = Math.max(at[i], i ? at[i - 1] + END_GAP : a + END_MARGIN)
    for (let i = at.length - 1; i >= 0; i--)
      at[i] = Math.min(
        at[i],
        i < at.length - 1 ? at[i + 1] - END_GAP : b - END_MARGIN
      )
    const fits = at[0] >= a + END_MARGIN - 0.5
    list.forEach((e, i) => {
      const pos = fits ? (at[i] - a) / len : (i + 1) / (list.length + 1)
      handles.set(e.node, [
        ...(handles.get(e.node) ?? []),
        { id: e.id, side: e.side, pos, type: e.type },
      ])
    })
  }

  // Links between the same two blocks run side by side, END_GAP apart.
  // On horizontal lines that is taller than a label, so labels stay in the
  // middle. On vertical lines a label is wider than the gap: the outer two
  // sit beside their line, facing out, and any others stagger along it.
  const pairs = new Map<string, LaidEdge[]>()
  for (const e of edges) {
    const k = [e.link.from, e.link.to].sort().join('|')
    pairs.set(k, [...(pairs.get(k) ?? []), e])
  }
  const sourceX = (e: LaidEdge) => {
    const b = box.get(e.link.from)!
    const h = handles.get(e.link.from)!.find((h) => h.id === e.sourceHandle)!
    return b.x + h.pos * b.w
  }
  for (const list of pairs.values()) {
    if (list.length < 2 || isVertical(sourceSide.get(list[0].link.id)!))
      continue
    list.sort((p, q) => sourceX(p) - sourceX(q))
    list[0].labelSide = 'left'
    list[list.length - 1].labelSide = 'right'
    const inner = list.slice(1, -1)
    inner.forEach((e, i) => (e.labelAt = (i + 1) / (inner.length + 1)))
  }

  return {
    nodes: blocks.map((b) => ({
      block: b,
      ...box.get(b.id)!,
      handles: handles.get(b.id) ?? [],
    })),
    edges,
  }
}
