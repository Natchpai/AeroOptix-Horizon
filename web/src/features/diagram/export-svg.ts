/**
 * Native SVG of a diagram level, drawn from the same placed layout as the
 * canvas: rect, line and text only, so it opens in Inkscape and Office.
 * Colours come from the current theme.
 */
import { createElement } from 'react'
import { createRoot } from 'react-dom/client'
import {
  type Block,
  type Level,
  blocksAt,
  busInfo,
  linksAt,
  openItems,
  statusOf,
} from '@/data'
import { lineAt, places, sideOverrides } from '@/data/places'
import { flushSync } from 'react-dom'
import {
  downloadSvg,
  esc,
  fitText,
  fonts,
  footerText,
  paintAttr,
  textWidth,
} from '@/lib/svg-export'
import { blockColor, kindInfo } from './kinds'
import { type LaidNode, handlePoint, placedLayout } from './layout'

const PAD = 40
const HEAD = 44
const FOOT = 36

const levelTitle: Record<Level, string> = {
  system: 'Block diagram, System (L0)',
  board: 'Block diagram, Board (L1)',
}

const iconMarkup = new Map<string, string>()

/** Lucide icon as SVG markup, rendered once per kind and size. */
function iconSvg(block: Block, size: number) {
  const key = `${block.kind}:${size}`
  if (!iconMarkup.has(key)) {
    const div = document.createElement('div')
    const root = createRoot(div)
    flushSync(() =>
      root.render(
        createElement(kindInfo[block.kind].icon, { size, strokeWidth: 2 })
      )
    )
    iconMarkup.set(key, div.innerHTML)
    root.unmount()
  }
  return iconMarkup.get(key)!
}

function icon(block: Block, x: number, y: number, size: number) {
  // lucide draws with currentColor; give it the block colour
  return iconSvg(block, size)
    .replace('<svg ', `<svg x="${x}" y="${y}" `)
    .replace(/ class="[^"]*"/, '')
    .replace(/stroke="currentColor"/, paintAttr('stroke', blockColor(block)))
}

function blockSvg(n: LaidNode, f: ReturnType<typeof fonts>) {
  const { block: b, x, y, w, h } = n
  const color = blockColor(b)
  const big = b.kind === 'mcu' || b.kind === 'board'
  const out: string[] = []
  out.push(
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" ` +
      `${b.kind === 'board' ? 'fill="url(#board-fill)"' : paintAttr('fill', 'var(--card)')} ` +
      `${paintAttr('stroke', `color-mix(in oklab, ${color} 45%, var(--border))`)} stroke-width="1"` +
      (statusOf(b) === 'candidate' ? ' stroke-dasharray="4 3"' : '') +
      '/>'
  )
  const box = (bx: number, by: number, s: number) =>
    `<rect x="${bx}" y="${by}" width="${s}" height="${s}" rx="6" ${paintAttr('fill', `color-mix(in oklab, ${color} 16%, transparent)`)}/>`
  const labelFont = (px: number) => `600 ${px}px ${f.sans}`
  const subFont = (px: number) => `400 ${px}px ${f.mono}`
  const text = (
    s: string,
    tx: number,
    cy: number,
    font: string,
    px: number,
    fill: string,
    anchor: 'start' | 'middle'
  ) =>
    `<text x="${tx}" y="${cy + px * 0.35}" font-family="${esc(font.split('px ')[1])}" font-size="${px}" font-weight="${font.split(' ')[0]}" text-anchor="${anchor}" ${paintAttr('fill', fill)}>${esc(s)}</text>`

  if (big) {
    const total = 48 + 12 + 30 + (b.sub ? 24 : 0)
    const top = y + (h - total) / 2
    const cx = x + w / 2
    out.push(box(cx - 24, top, 48), icon(b, cx - 12, top + 12, 24))
    const max = w - 24
    out.push(
      text(
        fitText(b.label, labelFont(24), max),
        cx,
        top + 75,
        labelFont(24),
        24,
        'var(--card-foreground)',
        'middle'
      )
    )
    if (b.sub)
      out.push(
        text(
          fitText(b.sub, subFont(16), max),
          cx,
          top + 104,
          subFont(16),
          16,
          'var(--muted-foreground)',
          'middle'
        )
      )
  } else {
    out.push(
      box(x + 13, y + (h - 32) / 2, 32),
      icon(b, x + 21, y + (h - 16) / 2, 16)
    )
    const tx = x + 55
    const max = w - 55 - 12
    const ly = b.sub ? y + h / 2 - 8.5 : y + h / 2
    out.push(
      text(
        fitText(b.label, labelFont(15), max),
        tx,
        ly,
        labelFont(15),
        15,
        'var(--card-foreground)',
        'start'
      )
    )
    if (b.sub)
      out.push(
        text(
          fitText(b.sub, subFont(12), max),
          tx,
          y + h / 2 + 9,
          subFont(12),
          12,
          'var(--muted-foreground)',
          'start'
        )
      )
  }

  const open = openItems(b).length
  if (open > 0) {
    const cx = x + w - 2
    const cy = y + 2
    out.push(
      `<circle cx="${cx}" cy="${cy}" r="10" ${paintAttr('fill', 'var(--background)')} ${paintAttr('stroke', 'color-mix(in oklab, var(--status-open) 60%, transparent)')}/>`,
      `<text x="${cx}" y="${cy + 3.5}" font-family="${esc(f.sans)}" font-size="10" font-weight="700" text-anchor="middle" ${paintAttr('fill', 'var(--status-open)')}>${open}</text>`
    )
  }
  return out.join('\n')
}

export function diagramSvg(level: Level) {
  const f = fonts()
  const laid = placedLayout(
    blocksAt(level),
    linksAt(level),
    places[level],
    sideOverrides,
    lineAt
  )
  const node = new Map(laid.nodes.map((n) => [n.block.id, n]))

  const lines: string[] = []
  const dots: string[] = []
  const labels: string[] = []
  const xs: number[] = []
  const ys: number[] = []
  for (const n of laid.nodes) {
    xs.push(n.x, n.x + n.w)
    ys.push(n.y, n.y + n.h)
  }

  for (const e of laid.edges) {
    const s = node.get(e.link.from)!
    const t = node.get(e.link.to)!
    const p = handlePoint(
      s,
      s.handles.find((h) => h.id === e.sourceHandle)!
    )
    const q = handlePoint(
      t,
      t.handles.find((h) => h.id === e.targetHandle)!
    )
    const { color, power } = busInfo[e.link.bus]
    const status = statusOf(e.link)
    lines.push(
      `<line x1="${p.x}" y1="${p.y}" x2="${q.x}" y2="${q.y}" ${paintAttr('stroke', color)} stroke-width="${power ? 4 : 1.75}" stroke-linecap="butt"` +
        (!power && status === 'candidate' ? ' stroke-dasharray="6 5"' : '') +
        (power && status === 'candidate' ? ' opacity="0.45"' : '') +
        '/>'
    )
    for (const [n, pt] of [
      [s, p],
      [t, q],
    ] as const)
      dots.push(
        `<circle cx="${pt.x}" cy="${pt.y}" r="3" ${paintAttr('fill', blockColor(n.block))}/>`
      )

    // label, placed as on the canvas (link-edge.tsx)
    const lx = p.x + (q.x - p.x) * e.labelAt
    const ly = p.y + (q.y - p.y) * e.labelAt
    const font = `500 12px ${f.mono}`
    const bw = textWidth(e.link.label, font) + 14
    const bh = 20
    const bx =
      e.labelSide === 'left'
        ? lx - 6 - bw
        : e.labelSide === 'right'
          ? lx + 6
          : lx - bw / 2
    const by = ly - bh / 2
    xs.push(bx, bx + bw)
    ys.push(by, by + bh)
    labels.push(
      `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="4" ${paintAttr('fill', `color-mix(in oklab, ${color} 12%, var(--card))`)} ${paintAttr('stroke', `color-mix(in oklab, ${color} 45%, transparent)`)}/>` +
        (status === 'open'
          ? `<rect x="${bx - 1.5}" y="${by - 1.5}" width="${bw + 3}" height="${bh + 3}" rx="5" fill="none" ${paintAttr('stroke', 'color-mix(in oklab, var(--status-open) 50%, transparent)')}/>`
          : '') +
        `<text x="${bx + bw / 2}" y="${ly + 12 * 0.35}" font-family="${esc(f.mono)}" font-size="12" font-weight="500" text-anchor="middle" ${paintAttr('fill', color)}>${esc(e.link.label)}</text>`
    )
  }

  const minX = Math.min(...xs) - PAD
  const minY = Math.min(...ys) - PAD - HEAD
  const W = Math.ceil(Math.max(...xs) + PAD - minX)
  const H = Math.ceil(Math.max(...ys) + PAD + FOOT - minY)
  const title = levelTitle[level]

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="${minX} ${minY} ${W} ${H}">`,
    `<title>${esc(title)}</title>`,
    `<defs><linearGradient id="board-fill" x1="0" y1="0" x2="1" y2="1">` +
      `<stop offset="0" ${paintAttr('fill', 'color-mix(in oklab, var(--brand) 22%, var(--card))').replace('fill=', 'stop-color=').replace('fill-opacity=', 'stop-opacity=')}/>` +
      `<stop offset="1" ${paintAttr('fill', 'var(--card)').replace('fill=', 'stop-color=')}/>` +
      `</linearGradient></defs>`,
    `<rect x="${minX}" y="${minY}" width="${W}" height="${H}" ${paintAttr('fill', 'var(--background)')}/>`,
    `<text x="${minX + PAD}" y="${minY + PAD / 2 + 18}" font-family="${esc(f.sans)}" font-size="20" font-weight="600" ${paintAttr('fill', 'var(--foreground)')}>${esc(`${title}`)}</text>`,
    ...lines,
    ...laid.nodes.map((n) => blockSvg(n, f)),
    ...dots,
    ...labels,
    `<text x="${minX + PAD}" y="${minY + H - PAD / 2}" font-family="${esc(f.sans)}" font-size="12" ${paintAttr('fill', 'var(--muted-foreground)')}>${esc(footerText(title))}</text>`,
    '</svg>',
  ].join('\n')
}

export function exportDiagram(level: Level) {
  downloadSvg(diagramSvg(level), `ao-horizon-${level}-diagram.svg`)
}
