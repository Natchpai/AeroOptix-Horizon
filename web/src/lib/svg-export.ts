/**
 * Helpers for native SVG export. Colours are resolved from the current
 * theme to plain hex (plus opacity), because Inkscape, PowerPoint and Word
 * do not read CSS variables, color-mix() or oklab().
 */
import { meta } from '@/data'

export type Paint = { hex: string; alpha: number }

let probe: HTMLSpanElement | null = null
let pixel: CanvasRenderingContext2D | null = null

/** Any CSS colour (var(), color-mix(), oklab ...) to sRGB hex and alpha. */
export function paint(css: string): Paint {
  if (!probe) {
    probe = document.createElement('span')
    probe.style.display = 'none'
    document.body.appendChild(probe)
    const c = document.createElement('canvas')
    c.width = c.height = 1
    pixel = c.getContext('2d', { willReadFrequently: true })!
  }
  probe.style.color = ''
  probe.style.color = css
  const resolved = getComputedStyle(probe).color
  const ctx = pixel!
  ctx.clearRect(0, 0, 1, 1)
  ctx.fillStyle = resolved
  ctx.fillRect(0, 0, 1, 1)
  const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data
  if (a === 0) return { hex: 'none', alpha: 0 }
  // undo premultiplied alpha
  const un = (v: number) => Math.min(255, Math.round((v * 255) / a))
  const hex =
    '#' + [r, g, b].map((v) => un(v).toString(16).padStart(2, '0')).join('')
  return { hex, alpha: Math.round((a / 255) * 1000) / 1000 }
}

/** fill="..." and fill-opacity="..." (or stroke) for an SVG element. */
export function paintAttr(kind: 'fill' | 'stroke', css: string) {
  const p = paint(css)
  if (p.hex === 'none') return `${kind}="none"`
  return p.alpha < 1
    ? `${kind}="${p.hex}" ${kind}-opacity="${p.alpha}"`
    : `${kind}="${p.hex}"`
}

/**
 * Font families the site uses, read from the theme. A generic family goes
 * last: the theme writes 'sans-serif' in quotes, which names a font rather
 * than the generic, so a viewer without Inter would fall back to serif.
 */
export function fonts() {
  const root = getComputedStyle(document.documentElement)
  const sans =
    root.getPropertyValue('--font-inter').trim() ||
    getComputedStyle(document.body).fontFamily
  const mono = root.getPropertyValue('--font-mono').trim() || 'ui-monospace'
  const generic = (list: string, g: string) =>
    new RegExp(`(^|,)\\s*${g}\\s*$`).test(list) ? list : `${list}, ${g}`
  return { sans: generic(sans, 'sans-serif'), mono: generic(mono, 'monospace') }
}

let measureCtx: CanvasRenderingContext2D | null = null

/** Width of a text run in px, measured with the real font. */
export function textWidth(text: string, font: string) {
  measureCtx ??= document.createElement('canvas').getContext('2d')!
  measureCtx.font = font
  return measureCtx.measureText(text).width
}

/** Cut text with "…" so it fits max px, like CSS truncate. */
export function fitText(text: string, font: string, max: number) {
  if (textWidth(text, font) <= max) return text
  let t = text
  while (t.length > 1 && textWidth(t + '…', font) > max) t = t.slice(0, -1)
  return t.trimEnd() + '…'
}

export function esc(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** Footer line: what this is, its source revision and phase. */
export function footerText(title: string) {
  const date = new Date().toISOString().slice(0, 10)
  return `${meta.project} · ${title} · spec rev ${meta.specRevision} · ${meta.phase}, not for fabrication · exported ${date}`
}

export function downloadSvg(svg: string, filename: string) {
  const blob = new Blob([`<?xml version="1.0" encoding="UTF-8"?>\n${svg}`], {
    type: 'image/svg+xml',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
