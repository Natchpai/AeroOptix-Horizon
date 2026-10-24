/**
 * Native SVG of a package view: the on-screen SVG with every colour and
 * font written out as plain attributes, plus a bus key and a footer.
 * Colours come from the current theme.
 */
import { type Mcu, busInfo, busOfSignal, mcuInfo, pins } from '@/data'
import {
  downloadSvg,
  esc,
  fonts,
  footerText,
  paint,
  paintAttr,
  textWidth,
} from '@/lib/svg-export'

const HEAD = 44
const KEY = 30
const FOOT = 32

/** Presentation properties copied from the computed style. */
const props = [
  'fill',
  'stroke',
  'stroke-width',
  'opacity',
  'fill-opacity',
  'stroke-opacity',
  'font-family',
  'font-size',
  'font-weight',
  'text-anchor',
] as const

function inline(src: Element, dst: Element) {
  const cs = getComputedStyle(src)
  const isText = src.tagName === 'text'
  for (const p of props) {
    const v = cs.getPropertyValue(p)
    if (!v || (!isText && (p.startsWith('font') || p === 'text-anchor')))
      continue
    if (p === 'fill' || p === 'stroke') {
      if (v === 'none' || v.startsWith('url(')) {
        dst.setAttribute(p, v)
        continue
      }
      const c = paint(v)
      dst.setAttribute(p, c.hex)
      if (c.alpha < 1) dst.setAttribute(`${p}-opacity`, String(c.alpha))
    } else if (!(p.endsWith('opacity') && dst.hasAttribute(p))) {
      dst.setAttribute(p, v)
    }
  }
  // Office ignores dominant-baseline; shift the text by hand instead
  if (isText && cs.getPropertyValue('dominant-baseline') === 'central') {
    dst.removeAttribute('dominant-baseline')
    dst.setAttribute('dy', '0.35em')
  }
  dst.removeAttribute('class')
  for (let i = 0; i < src.children.length; i++)
    inline(src.children[i], dst.children[i])
}

export function packageSvg(mcu: Mcu, el: SVGSVGElement) {
  const f = fonts()
  const info = mcuInfo[mcu]
  const vb = el.viewBox.baseVal
  const W = vb.width
  const clone = el.cloneNode(true) as SVGSVGElement
  inline(el, clone)

  // bus key: the buses this MCU's allocated pins use
  const used = [...new Set(pins[mcu].map((p) => busOfSignal(p.signal)))]
  const font = `400 13px ${f.sans}`
  const items = used.map((b) => ({
    b,
    w: 16 + textWidth(busInfo[b].label, font) + 18,
  }))
  // wrap into centered rows that fit the drawing width
  const rows: (typeof items)[] = []
  let row: typeof items = []
  let rowW = 0
  for (const it of items) {
    if (rowW + it.w > W - 40 && row.length) {
      rows.push(row)
      row = []
      rowW = 0
    }
    row.push(it)
    rowW += it.w
  }
  rows.push(row)
  const key = rows
    .map((row, r) => {
      let kx = (W - row.reduce((s, i) => s + i.w, 0)) / 2
      const ky = HEAD + vb.height + KEY / 2 + r * KEY
      return row
        .map(({ b, w }) => {
          const s =
            `<rect x="${kx}" y="${ky - 5}" width="10" height="10" rx="2" ${paintAttr('fill', busInfo[b].color)}/>` +
            `<text x="${kx + 16}" y="${ky + 4.5}" font-family="${esc(f.sans)}" font-size="13" ${paintAttr('fill', 'var(--muted-foreground)')}>${esc(busInfo[b].label)}</text>`
          kx += w
          return s
        })
        .join('')
    })
    .join('\n')

  const H = HEAD + vb.height + rows.length * KEY + FOOT
  const title = `${info.part} ${info.pkg} pin map`
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`,
    `<title>${esc(title)}</title>`,
    `<rect width="${W}" height="${H}" ${paintAttr('fill', 'var(--card)')}/>`,
    `<text x="20" y="30" font-family="${esc(f.sans)}" font-size="18" font-weight="600" ${paintAttr('fill', 'var(--foreground)')}>${esc(title)}</text>`,
    `<g transform="translate(${-vb.x} ${HEAD - vb.y})">${clone.innerHTML}</g>`,
    key,
    `<text x="20" y="${H - 12}" font-family="${esc(f.sans)}" font-size="11" ${paintAttr('fill', 'var(--muted-foreground)')}>${esc(footerText('Pinout'))}</text>`,
    '</svg>',
  ].join('\n')
}

export function exportPackage(mcu: Mcu) {
  const el = document.getElementById(`package-view-${mcu}`)
  if (!(el instanceof SVGSVGElement)) return
  downloadSvg(packageSvg(mcu, el), `ao-horizon-${mcu}-pinout.svg`)
}
