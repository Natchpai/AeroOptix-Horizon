import type { PinRow } from '@/data'

/**
 * Pins grouped by peripheral instance (SPI1, USART6, TIM5 ...), for the
 * Pinout "By peripheral" view. The name comes from the start of the signal
 * text; nothing is added to the record.
 */
export type PeripheralGroup = {
  name: string
  /** Sort rank of the group kind, see KINDS. */
  rank: number
  rows: { row: PinRow; label: string }[]
}

const PERIPHERAL =
  /^(USART\d+|UART\d+|I2C\d+|SPI\d+|TIM\d+|SDMMC\d+|OTG_FS|ADC\d+)(?=_|$)/

/** Group kinds in display order. */
const KINDS: [RegExp, number][] = [
  [/^U(S)?ART/, 0],
  [/^I2C/, 1],
  [/^SPI/, 2],
  [/^TIM/, 3],
  [/^SDMMC/, 4],
  [/^OTG_FS/, 5],
  [/^ADC/, 6],
]

export const GPIO_GROUP = 'GPIO and EXTI'
export const DEBUG_GROUP = 'Debug, reset, clock, boot'
/** Only shown when a signal fits no other group (none do today). */
export const OTHER_GROUP = 'Other'

function groupOf(signal: string): { name: string; rank: number } {
  const m = signal.match(PERIPHERAL)
  if (m)
    return {
      name: m[1],
      rank: KINDS.find(([re]) => re.test(m[1]))![1],
    }
  if (/^(SWDIO|SWCLK|NRST|OSC_|BOOT)/.test(signal))
    return { name: DEBUG_GROUP, rank: 8 }
  if (/^(GPIO|EXTI)/.test(signal)) return { name: GPIO_GROUP, rank: 7 }
  return { name: OTHER_GROUP, rank: 9 }
}

const num = (name: string) => Number(name.match(/\d+$/)?.[0] ?? 0)

export function peripheralGroups(rows: PinRow[]): PeripheralGroup[] {
  const groups = new Map<string, PeripheralGroup>()
  for (const row of rows) {
    const { name, rank } = groupOf(row.signal)
    let g = groups.get(name)
    if (!g) groups.set(name, (g = { name, rank, rows: [] }))
    // "SPI1_SCK" shows as "SCK" under SPI1; fixed groups keep the full text
    const rest = row.signal.startsWith(name + '_')
      ? row.signal.slice(name.length + 1)
      : ''
    g.rows.push({ row, label: rest || row.signal })
  }
  const list = [...groups.values()]
  for (const g of list)
    g.rows.sort((a, b) =>
      a.row.signal.localeCompare(b.row.signal, 'en', { numeric: true })
    )
  return list.sort((a, b) => a.rank - b.rank || num(a.name) - num(b.name))
}
