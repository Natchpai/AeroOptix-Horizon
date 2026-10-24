import idsJson from './generated/ids.json'
import metaJson from './generated/meta.json'
import pinsJson from './generated/pins.json'
import progressJson from './generated/progress.json'
import { blocks, links } from './topology'
import type {
  Block,
  Bus,
  Level,
  Link,
  Mcu,
  Meta,
  PinRow,
  PinSelect,
  Progress,
  ReservedRow,
  SpecId,
  Status,
} from './types'

export * from './types'
export { blocks, links } from './topology'

export const meta = metaJson as Meta
export const ids = idsJson as Record<string, SpecId>
export const pins = pinsJson as {
  h743: PinRow[]
  f100: PinRow[]
  f100Reserved: ReservedRow[]
}
// counts keys differ per gate, so the JSON type does not match Record directly
export const progress = progressJson as unknown as Progress

export const REPO_URL = 'https://github.com/Natchpai/AeroOptix-Horizon'

/** Link to a line in a repo file on GitHub (main branch, plain view). */
export function sourceUrl(file: string, line?: number) {
  const base = `${REPO_URL}/blob/main/${file}`
  return line ? `${base}?plain=1#L${line}` : base
}

/** Link to a commit on GitHub. A local build has no commit to link. */
export function commitUrl(sha: string) {
  return /^[0-9a-f]{7,40}$/.test(sha) ? `${REPO_URL}/commit/${sha}` : undefined
}

export const mcuInfo: Record<
  Mcu,
  { label: string; part: string; pkg: string; pinCount: number }
> = {
  h743: { label: 'H743', part: 'STM32H743VIT6', pkg: 'LQFP100', pinCount: 100 },
  f100: { label: 'F100', part: 'STM32F100C8T6B', pkg: 'LQFP48', pinCount: 48 },
}

/** Power rails run warm (high voltage) to cold (low) and draw thicker. */
export const busInfo: Record<
  Bus,
  { label: string; color: string; power?: boolean }
> = {
  batt: { label: 'Battery', color: 'var(--rail-batt)', power: true },
  v6: { label: '+6V', color: 'var(--rail-6v)', power: true },
  v5: { label: '+5V', color: 'var(--rail-5v)', power: true },
  v3v3: { label: '+3.3V', color: 'var(--rail-3v3)', power: true },
  v3v3a: { label: '+3.3VA', color: 'var(--rail-3v3a)', power: true },
  spi: { label: 'SPI', color: 'var(--bus-spi)' },
  i2c: { label: 'I2C', color: 'var(--bus-i2c)' },
  uart: { label: 'UART', color: 'var(--bus-uart)' },
  pwm: { label: 'PWM / timer', color: 'var(--bus-pwm)' },
  usb: { label: 'USB', color: 'var(--bus-usb)' },
  sdmmc: { label: 'SDMMC', color: 'var(--bus-sdmmc)' },
  debug: { label: 'Debug', color: 'var(--bus-debug)' },
  gpio: { label: 'GPIO', color: 'var(--bus-gpio)' },
  analog: { label: 'Analog', color: 'var(--bus-analog)' },
}

export const statusInfo: Record<Status, { label: string; hint: string }> = {
  decided: {
    label: 'Decided',
    hint: 'Backed by a DEC row or a confirmed allocation',
  },
  open: { label: 'Open item', hint: 'An OPEN item still affects it' },
  candidate: { label: 'Candidate', hint: 'From the spec diagram only, TBD' },
}

/** Open items that are still open in the spec (closed ones drop out). */
export function openItems(item: Pick<Block, 'open'>) {
  return (item.open ?? []).filter((id) => ids[id] && !ids[id].closed)
}

export function statusOf(item: Block | Link): Status {
  if (item.status === 'candidate') return 'candidate'
  if (openItems(item).length) return 'open'
  return item.status ?? 'decided'
}

export const blockById = new Map(blocks.map((b) => [b.id, b]))
export const linkById = new Map(links.map((l) => [l.id, l]))

export function blocksAt(level: Level) {
  return blocks.filter((b) => b.level === level)
}
export function linksAt(level: Level) {
  return links.filter((l) => l.level === level)
}
export function linksOf(blockId: string) {
  return links.filter((l) => l.from === blockId || l.to === blockId)
}

function selectPins(sel: PinSelect): PinRow[] {
  const fn = sel.fn ? new RegExp(sel.fn) : null
  const sig = sel.signal ? new RegExp(sel.signal) : null
  return pins[sel.mcu].filter(
    (p) =>
      (!sel.refs || p.refs.some((r) => sel.refs!.includes(r))) &&
      (!fn || fn.test(p.function)) &&
      (!sig || sig.test(p.signal))
  )
}

export type SignalLine = {
  key: string
  name: string
  a?: { mcu: Mcu; row: PinRow }
  b?: { mcu: Mcu; row: PinRow }
}

/** Short signal name: "SPI1_SCK" -> "SCK", "GPIO output" -> function text. */
function signalName(row: PinRow) {
  const s = row.signal.replace(/\s*\(.*\)$/, '')
  if (/^GPIO/.test(s) || s === row.pin) return row.function
  return s
}

/**
 * Signals on a link. With pins on both ends (the MCU link), UART TX on one
 * side pairs with RX on the other; everything else lists one end only and
 * the far-end pin stays TBD.
 */
export function linkSignals(link: Link): SignalLine[] {
  const sels = link.pins ?? []
  const fromMcu = blockById.get(link.from)?.mcu
  const toMcu = blockById.get(link.to)?.mcu
  if (fromMcu && toMcu && sels.length === 2) {
    const a = selectPins(sels.find((s) => s.mcu === fromMcu)!)
    const b = selectPins(sels.find((s) => s.mcu === toMcu)!)
    const swap = (sig: string) =>
      sig.endsWith('_TX') ? '_RX' : sig.endsWith('_RX') ? '_TX' : null
    return a.map((ra, i) => {
      const want = swap(ra.signal)
      const rb = want ? b.find((x) => x.signal.endsWith(want)) : b[i]
      return {
        key: `${ra.pin}-${rb?.pin ?? i}`,
        name: `${signalName(ra)} → ${rb ? signalName(rb) : 'TBD'}`,
        a: { mcu: fromMcu, row: ra },
        b: rb ? { mcu: toMcu, row: rb } : undefined,
      }
    })
  }
  return sels.flatMap((s) =>
    selectPins(s).map((row) => ({
      key: `${s.mcu}-${row.pin}`,
      name: signalName(row),
      a: { mcu: s.mcu, row },
    }))
  )
}

/** Bus colour group for a pin, from its signal name. */
export function busOfSignal(signal: string): Bus {
  if (/^SPI/.test(signal)) return 'spi'
  if (/^I2C/.test(signal)) return 'i2c'
  if (/U(S)?ART/.test(signal)) return 'uart'
  if (/^TIM/.test(signal)) return 'pwm'
  if (/^OTG/.test(signal)) return 'usb'
  if (/^SDMMC/.test(signal)) return 'sdmmc'
  if (/^ADC/.test(signal)) return 'analog'
  if (/^(SWD|SWCLK|NRST|BOOT|OSC)/.test(signal)) return 'debug'
  return 'gpio'
}

/** Link that carries a given MCU pin, for pinout -> diagram jumps. */
export function linkForPin(mcu: Mcu, pin: string): Link | undefined {
  return links.find(
    (l) =>
      l.level === 'board' &&
      (l.pins ?? []).some(
        (s) => s.mcu === mcu && selectPins(s).some((r) => r.pin === pin)
      )
  )
}

/** Every spec ID, for display: removed rows are flagged by the extractor. */
export function idTitle(id: string) {
  const s = ids[id]
  if (!s) return id
  const f = s.fields
  const first =
    f['Function'] ||
    f['Topic'] ||
    f['Logical output'] ||
    f['Description'] ||
    f['Requirement'] ||
    f['Required behavior'] ||
    f['Parameter'] ||
    f['Parameter / condition'] ||
    f['Hazard / fault'] ||
    f['Signal / function'] ||
    f['Item'] ||
    f['Category'] ||
    f['Source'] ||
    s.section
  const plain = first.replace(/[`*]/g, '')
  return plain.length > 90 ? `${plain.slice(0, 88)}…` : plain
}
