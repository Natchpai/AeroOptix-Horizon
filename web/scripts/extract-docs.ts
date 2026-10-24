/**
 * Reads the project Markdown records and writes JSON for the site.
 *
 * The design docs stay the source of truth. This script copies text out of
 * them as-is and adds no values of its own. Output goes to
 * src/data/generated/ (git-ignored, rebuilt on every dev and build run).
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const repo = path.resolve(here, '../..')
const designDir = 'hardware/AO-Horizon/documents/design'
const SPEC = `${designDir}/AO-HORIZON_SPEC_EN.md`
const PINS = `${designDir}/AO-HORIZON_PIN_ALLOCATION_EN.md`
const README = 'README.md'
const outDir = path.resolve(here, '../src/data/generated')

type Table = {
  heading: string
  headers: string[]
  rows: { cells: string[]; line: number }[]
}

function read(rel: string): string[] {
  return fs.readFileSync(path.join(repo, rel), 'utf8').split(/\r?\n/)
}

function splitRow(line: string): string[] {
  const inner = line.trim().replace(/^\|/, '').replace(/\|$/, '')
  return inner.split('|').map((c) => c.trim())
}

/** All pipe tables in a file, with the nearest heading above each one. */
function parseTables(lines: string[]): Table[] {
  const tables: Table[] = []
  let heading = ''
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const h = /^#{1,6}\s+(.*)$/.exec(line)
    if (h) {
      heading = h[1].trim()
      continue
    }
    const next = lines[i + 1] ?? ''
    if (line.trim().startsWith('|') && /^\s*\|[\s:|-]+\|?\s*$/.test(next)) {
      const table: Table = { heading, headers: splitRow(line), rows: [] }
      i += 2
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        table.rows.push({ cells: splitRow(lines[i]), line: i + 1 })
        i++
      }
      i--
      tables.push(table)
    }
  }
  return tables
}

const ID_RE = /^[A-Z]{2,5}-\d{2,3}$/

// ---------- spec: every row whose first cell is a stable ID ----------
const specLines = read(SPEC)
const ids: Record<string, unknown> = {}
for (const t of parseTables(specLines)) {
  for (const r of t.rows) {
    const id = r.cells[0]
    // keep the first (defining) row when an ID appears in more tables
    if (!ID_RE.test(id) || ids[id]) continue
    const fields: Record<string, string> = {}
    t.headers.forEach((h, k) => {
      if (k > 0) fields[h] = r.cells[k] ?? ''
    })
    const text = r.cells.slice(1).join(' ')
    ids[id] = {
      id,
      kind: id.split('-')[0],
      section: t.heading,
      fields,
      removed: /\bRemoved\b/.test(r.cells[2] ?? r.cells[1] ?? ''),
      // OPEN rows: closed when the description or the owner column says so
      closed:
        /^Closed\b/.test(r.cells[1] ?? '') ||
        /^Closed\b/.test(r.cells[r.cells.length - 1] ?? ''),
      file: SPEC,
      line: r.line,
      text,
    }
  }
}

function specProp(name: string): string {
  const row = specLines.find((l) => new RegExp(`^\\|\\s*${name}\\s*\\|`).test(l))
  return row ? splitRow(row)[1] : 'TBD'
}

// ---------- pin allocation ----------
type PinRow = {
  function: string
  refs: string[]
  signal: string
  pin: string
  number: number | null
  ds: string
  line: number
}

const pinTables = parseTables(read(PINS))
function pinRows(headingStart: string, pkgCol: string): PinRow[] {
  const t = pinTables.find(
    (x) => x.heading.startsWith(headingStart) && x.headers.includes(pkgCol)
  )
  if (!t) throw new Error(`pin table not found: ${headingStart} / ${pkgCol}`)
  const col = (name: string) => t.headers.findIndex((h) => h.startsWith(name))
  const [cF, cR, cS, cP, cN, cD] = [
    col('Function'),
    col('Ref'),
    col('Signal'),
    col('Pin'),
    col(pkgCol),
    col('DS'),
  ]
  return t.rows.map((r) => ({
    function: r.cells[cF],
    refs: r.cells[cR].split(',').map((s) => s.trim()).filter(Boolean),
    signal: r.cells[cS],
    pin: r.cells[cP],
    number: /^\d+$/.test(r.cells[cN]) ? Number(r.cells[cN]) : null,
    ds: r.cells[cD] ?? '',
    line: r.line,
  }))
}

const reservedTable = pinTables.find(
  (x) => x.headers[0] === 'Pin' && x.headers[1]?.startsWith('px4io-v2')
)
const f100Reserved = (reservedTable?.rows ?? []).map((r) => ({
  pins: r.cells[0].split(',').map((s) => s.trim()),
  function: r.cells[1],
  plan: r.cells[2],
  line: r.line,
}))

// ---------- README: status and key features ----------
const readme = read(README)
const grab = (re: RegExp) => {
  for (const l of readme) {
    const m = re.exec(l)
    if (m) return m[1]
  }
  return 'TBD'
}
const kfStart = readme.findIndex((l) => /^##\s+Key Features/.test(l))
const keyFeatures: string[] = []
for (let i = kfStart + 1; kfStart >= 0 && i < readme.length; i++) {
  if (/^##\s/.test(readme[i])) break
  const m = /^-\s+(.*)$/.exec(readme[i])
  if (m) keyFeatures.push(m[1])
}

const meta = {
  project: 'AeroOptix-Horizon',
  tagline: grab(/^\*\*(.+)\*\*$/),
  phase: grab(/\*\*Current Phase:\*\*\s*`([^`]+)`/),
  boardRevision: grab(/\*\*Board revision:\*\*\s*`([^`]+)`/),
  baseline: grab(/\*\*Baseline:\*\*\s*`([^`]+)`/),
  kicad: grab(/\*\*KiCad:\*\*\s*`([^`]+)`/),
  specRevision: specProp('Document revision'),
  specUpdated: specProp('Last updated'),
  specStatus: specProp('Specification status'),
  keyFeatures,
  sources: { spec: SPEC, pins: PINS, readme: README },
  generatedFrom: 'saved Markdown records in the repository',
}

fs.mkdirSync(outDir, { recursive: true })
const write = (name: string, data: unknown) =>
  fs.writeFileSync(path.join(outDir, name), JSON.stringify(data, null, 2) + '\n')

const h743 = pinRows('1. STM32H743', 'LQFP100')
const f100 = pinRows('2. STM32F100', 'LQFP48')
write('meta.json', meta)
write('ids.json', ids)
write('pins.json', { h743, f100, f100Reserved })

console.log(
  `extract-docs: ${Object.keys(ids).length} spec IDs, H743 ${h743.length} pins, ` +
    `F100 ${f100.length} pins + ${f100Reserved.length} reserved rows, phase ${meta.phase}, spec rev ${meta.specRevision}`
)
