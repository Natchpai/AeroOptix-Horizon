/**
 * Report-only check: hand-written block and link text in topology.ts that
 * may have drifted from the spec. It never fails the build (exit 0).
 *
 * For each block and link, it takes the "hard" words from label, sub and
 * note (hex addresses, part numbers, pin and peripheral names) and lists
 * every word that is in none of the spec rows the item cites (refs and open)
 * and in none of the pin rows those refs select. For a DEC row only the
 * decided value counts (Topic and Selected option), not its Notes, and
 * history phrases ("replaces the 0x0E") are cut from every row. It also
 * lists items that still name a closed OPEN item.
 *
 * A finding is a lead, not a defect: check the spec row, then fix the site
 * text by hand. Run `npm run extract` first (or use `npm run drift`).
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { blocks, links } from '../src/data/topology'
import type { Block, Link, Mcu, PinRow, SpecId } from '../src/data/types'

const here = path.dirname(fileURLToPath(import.meta.url))
const gen = path.resolve(here, '../src/data/generated')
const load = <T>(name: string): T =>
  JSON.parse(fs.readFileSync(path.join(gen, name), 'utf8')) as T

const ids = load<Record<string, SpecId>>('ids.json')
const pins = load<Record<Mcu, PinRow[]>>('pins.json')

/** Spec IDs are references, not values; skip them as words. */
const SPEC_ID = /^[A-Z]{2,5}-\d{2,3}$/
const HEX = /\b0x[0-9a-f]+\b/gi
/** Words of 4+ letters, digits, `_`, `-` or `/` with at least one digit and one letter. */
const PART = /[A-Za-z0-9][A-Za-z0-9_\-/]{2,}[A-Za-z0-9]/g
/** MCU pins such as PA8 or PC13. */
const PIN = /\bP[A-K]\d{1,2}\b/g

const norm = (s: string) => s.toLowerCase().replace(/[`*]/g, '')

function words(text: string): string[] {
  const out = new Set<string>()
  for (const m of text.match(HEX) ?? []) out.add(m)
  for (const m of text.match(PIN) ?? []) out.add(m)
  for (const m of text.match(PART) ?? []) {
    if (!/\d/.test(m) || !/[a-z]/i.test(m) || SPEC_ID.test(m)) continue
    // Split "USART6/USART2" or "A-B" style joins into parts too.
    for (const part of m.split('/')) if (part.length >= 3) out.add(part)
  }
  return [...out]
}

/**
 * History phrases name an old value ("Replaces the 0x0E in DEC-011",
 * "replaced BMM150 on ..."); they are cut up to the next punctuation mark.
 */
const HISTORY = /\b(replaces|replaced|instead of|was|previously|formerly)\b[^.;,()]*/gi

/**
 * The text that states a row's current value. DEC Notes often keep the old
 * value ("Replaces the 0x0E in DEC-011"), so for DEC rows only Topic and
 * Selected option count; other rows use the whole row.
 */
function current(row: SpecId): string {
  const f = row.fields
  const text =
    row.kind === 'DEC'
      ? [f['Topic'], f['Selected option']].filter(Boolean).join(' ')
      : row.text
  return text.replace(HISTORY, ' ')
}

function source(item: Block | Link): string {
  const cited = [...item.refs, ...(item.open ?? [])]
  const parts: string[] = []
  for (const r of cited) if (ids[r]) parts.push(current(ids[r]))
  for (const mcu of ['h743', 'f100'] as Mcu[])
    for (const p of pins[mcu])
      if (p.refs.some((r) => cited.includes(r)))
        parts.push(`${p.function} ${p.signal} ${p.pin}`)
  return norm(parts.join(' '))
}

type Finding = { level: string; id: string; what: string; refs: string }
const findings: Finding[] = []

for (const item of [...blocks, ...links]) {
  const kind = 'from' in item ? 'link' : 'block'
  const refs = [...item.refs, ...(item.open ?? [])].join(', ')
  const src = source(item)
  const text = [item.label, 'sub' in item ? item.sub : '', item.note]
    .filter(Boolean)
    .join(' ')
  for (const w of words(text))
    if (!src.includes(norm(w)))
      findings.push({ level: item.level, id: `${kind} ${item.id}`, what: `"${w}" not in cited rows`, refs })
  for (const o of item.open ?? [])
    if (ids[o]?.closed)
      findings.push({ level: item.level, id: `${kind} ${item.id}`, what: `${o} is closed`, refs })
}

if (!findings.length) {
  console.log('drift: no findings')
} else {
  console.log(`drift: ${findings.length} finding(s), report only (level | item | finding | cited refs)`)
  for (const f of findings) console.log(`  ${f.level} | ${f.id} | ${f.what} | ${f.refs}`)
}
