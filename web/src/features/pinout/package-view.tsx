import {
  type Mcu,
  type PinRow,
  busInfo,
  busOfSignal,
  mcuInfo,
  pins,
} from '@/data'

type Props = {
  mcu: Mcu
  selected?: string
  onPick: (pin: string) => void
}

/**
 * Quad flat package seen from the top. Pin 1 is top of the left side and
 * numbers run counter-clockwise, as on ST LQFP drawings. Only pins in the
 * allocation table get a name; the rest show their number only.
 */
export function PackageView({ mcu, selected, onPick }: Props) {
  const info = mcuInfo[mcu]
  const n = info.pinCount / 4
  const byNumber = new Map<number, PinRow>()
  for (const p of pins[mcu]) if (p.number !== null) byNumber.set(p.number, p)

  const S = 640 // viewBox size
  const body = mcu === 'h743' ? 330 : 280
  const b0 = (S - body) / 2
  const pitch = (body - 24) / (n - 1)
  const padLen = 16
  const padW = Math.min(8, pitch * 0.62)
  const labelGap = 6

  const items = Array.from({ length: info.pinCount }, (_, i) => {
    const num = i + 1
    const side = Math.floor(i / n) // 0 left, 1 bottom, 2 right, 3 top
    const k = i % n
    const t = b0 + 12 + k * pitch
    const tr = b0 + 12 + (n - 1 - k) * pitch
    switch (side) {
      case 0:
        return {
          num,
          side,
          x: b0 - padLen,
          y: t - padW / 2,
          w: padLen,
          h: padW,
          cx: b0 - padLen - labelGap,
          cy: t,
        }
      case 1:
        return {
          num,
          side,
          x: t - padW / 2,
          y: b0 + body,
          w: padW,
          h: padLen,
          cx: t,
          cy: b0 + body + padLen + labelGap,
        }
      case 2:
        return {
          num,
          side,
          x: b0 + body,
          y: tr - padW / 2,
          w: padLen,
          h: padW,
          cx: b0 + body + padLen + labelGap,
          cy: tr,
        }
      default:
        return {
          num,
          side,
          x: tr - padW / 2,
          y: b0 - padLen,
          w: padW,
          h: padLen,
          cx: tr,
          cy: b0 - padLen - labelGap,
        }
    }
  })

  return (
    <svg
      id={`package-view-${mcu}`}
      viewBox={`0 0 ${S} ${S}`}
      className='h-auto w-full select-none'
      role='img'
      aria-label={`${info.part} ${info.pkg} pin map`}
    >
      <rect
        x={b0}
        y={b0}
        width={body}
        height={body}
        rx={10}
        fill='var(--card)'
        stroke='color-mix(in oklab, var(--brand) 45%, var(--border))'
        strokeWidth={2}
      />
      <circle
        cx={b0 + 22}
        cy={b0 + 22}
        r={6}
        fill='var(--muted-foreground)'
        opacity={0.6}
      />
      <text
        x={S / 2}
        y={S / 2 - 12}
        textAnchor='middle'
        className='fill-foreground font-mono'
        fontSize={20}
        fontWeight={700}
      >
        {info.part}
      </text>
      <text
        x={S / 2}
        y={S / 2 + 14}
        textAnchor='middle'
        className='fill-muted-foreground font-mono'
        fontSize={14}
      >
        {info.pkg} · {pins[mcu].length} allocated
      </text>
      {items.map((p) => {
        const row = byNumber.get(p.num)
        const color = row
          ? busInfo[busOfSignal(row.signal)].color
          : 'var(--border)'
        const isSel = !!row && row.pin === selected
        const vertical = p.side === 1 || p.side === 3
        const anchor = p.side === 0 ? 'end' : 'start'
        // both vertical sides read bottom to top
        const rot = vertical ? -90 : 0
        const label = row
          ? `${row.pin} · ${row.signal.replace(/\s*\(.*\)$/, '').replace(/^GPIO.*/, 'GPIO')}`
          : String(p.num)
        return (
          <g
            key={p.num}
            className={row ? 'cursor-pointer' : undefined}
            onClick={() => row && onPick(row.pin)}
          >
            <title>
              {row
                ? `#${p.num} ${row.pin} · ${row.signal} · ${row.function}`
                : `#${p.num} not allocated`}
            </title>
            <rect
              x={p.x}
              y={p.y}
              width={p.w}
              height={p.h}
              rx={1.5}
              fill={row ? color : 'transparent'}
              stroke={isSel ? 'var(--foreground)' : color}
              strokeWidth={isSel ? 2 : 1}
              opacity={row ? 1 : 0.7}
            />
            <text
              x={p.cx}
              y={p.cy}
              textAnchor={vertical ? (p.side === 1 ? 'end' : 'start') : anchor}
              dominantBaseline='central'
              transform={rot ? `rotate(${rot} ${p.cx} ${p.cy})` : undefined}
              fontSize={row ? (mcu === 'h743' ? 10.5 : 12) : 8.5}
              fontWeight={isSel ? 700 : row ? 600 : 400}
              className='font-mono'
              fill={
                row
                  ? isSel
                    ? 'var(--foreground)'
                    : color
                  : 'var(--muted-foreground)'
              }
              opacity={row ? 1 : 0.55}
            >
              {label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
