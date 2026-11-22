import { type Block, type BomRow, type SpecId, blocks, ids } from '@/data'

/**
 * Links from a BOM row to the rest of the site, found by its MFR.P/N. The
 * site adds no values: a link only says that two records name the same
 * part number.
 */

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

/** The part number as a whole word: no letter or digit right before or after. */
const wordRe = (mpn: string) =>
  new RegExp(`(?<![A-Za-z0-9])${esc(mpn)}(?![A-Za-z0-9])`)

/** A part number in a block's `sub`: 4+ characters with a letter and a digit. */
const isPartNo = (s: string) =>
  s.length >= 4 && /[A-Z]/i.test(s) && /\d/.test(s)

/**
 * Diagram blocks (every view) for a row: the block's `sub` names the
 * MFR.P/N, or, as on the Power budget page, a part number in the `sub`
 * starts the MFR.P/N (TPS2121RUX in TPS2121RUXR, an ordering suffix).
 * The `sub` splits on "," and "+", so "STM32H743 + STM32F100" names both.
 */
export function blocksFor(row: BomRow): Block[] {
  if (!row.mpn) return []
  const re = wordRe(row.mpn)
  return blocks.filter((b) => {
    const sub = b.sub ?? ''
    return (
      re.test(sub) ||
      sub
        .split(/\s*[,+]\s*/)
        .map((p) => p.split(' ')[0])
        .some((p) => isPartNo(p) && row.mpn.startsWith(p))
    )
  })
}

const decisions = Object.values(ids).filter((s) => s.kind === 'DEC')

/** DEC rows whose Topic or Selected option names the MFR.P/N as a whole word. */
export function decisionsFor(row: BomRow): SpecId[] {
  if (!row.mpn) return []
  const re = wordRe(row.mpn)
  return decisions.filter((d) =>
    re.test(`${d.fields['Topic'] ?? ''}\n${d.fields['Selected option'] ?? ''}`)
  )
}

/** Report only: what a fitted row lacks (MFR.P/N, LCSC). DNP rows are never flagged. */
export function missingOf(row: BomRow): string[] {
  if (row.dnp) return []
  return [!row.mpn && 'MFR.P/N', !row.lcsc && 'LCSC'].filter(
    (x): x is string => !!x
  )
}
