/**
 * Reads the project Markdown records and writes JSON for the site.
 *
 * The design docs stay the source of truth. This script copies text out of
 * them as-is and adds no values of its own. Output goes to
 * src/data/generated/ (git-ignored, rebuilt on every dev and build run).
 */
import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const repo = path.resolve(here, '../..')
const designDir = 'hardware/AO-Horizon/documents/design'
const SPEC = `${designDir}/AO-HORIZON_SPEC_EN.md`
const PINS = `${designDir}/AO-HORIZON_PIN_ALLOCATION_EN.md`
const CHECKLIST = `${designDir}/AO-HORIZON_EXECUTION_CHECKLIST_EN.md`
const README = 'README.md'
const POWER = `${designDir}/AO-HORIZON_POWER_BUDGET_EN.md`
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
  // A row whose Signal is "-" records a pin that lost its function (for
  // example PC0 and PC1, spec DEC-107). It is not allocated, so the site
  // leaves it out: it shows as a free pin on the package view.
  return t.rows
    .filter((r) => r.cells[cS].trim() !== '-')
    .map((r) => ({
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

// README Specifications table: part numbers for the Overview cards
const specTable = parseTables(readme).find((t) => t.heading === 'Specifications')
function readmeSpec(name: string): string {
  const r = specTable?.rows.find((x) => x.cells[0] === name)
  if (!r) throw new Error(`README.md: "${name}" row not found in ## Specifications`)
  // drop a trailing note in brackets: "STM32F100C8T6B (px4io)"
  return r.cells[1].replace(/\s*\(.*\)$/, '')
}

// ---------- spec: section 9 change notes, newest first ----------
const changeTable = parseTables(specLines).find(
  (t) => /^9\.\s/.test(t.heading) && t.headers[0] === 'Revision'
)
if (!changeTable) throw new Error('spec: section 9 change notes table not found')
// every change note for the Spec history page; the last 5 for the Overview
const specHistory = changeTable.rows
  .map((r) => ({
    revision: r.cells[0],
    date: r.cells[1],
    description: r.cells[2] ?? '',
    approvedBy: r.cells[3] ?? '',
    line: r.line,
  }))
  .reverse()
if (!specHistory.length) throw new Error('spec: section 9 change notes table is empty')
const specChanges = specHistory.slice(0, 5)
// revision and date of every note, for Ctrl+K (the full text stays in history.json)
const specRevisions = specHistory.map((c) => ({ revision: c.revision, date: c.date }))

// heading number of the OPEN rows, e.g. "8.2 Open questions ..." -> "8.2"
const openSection =
  /^([\d.]+)\s/.exec(
    (Object.values(ids) as { kind: string; section: string }[]).find(
      (s) => s.kind === 'OPEN'
    )?.section ?? ''
  )?.[1] ?? ''
if (!openSection) throw new Error('spec: no OPEN rows under a numbered heading')

// ---------- checklist: gates, task counts, next action ----------
const checklist = read(CHECKLIST)
const clProp = (name: string) =>
  checklist
    .map((l) => new RegExp(`^\\*\\*${name}:\\*\\*\\s*(.+)$`).exec(l)?.[1])
    .find(Boolean) ?? 'TBD'
const clTables = parseTables(checklist)
const gateTable = clTables.find((t) => t.heading === 'Gate summary')
if (!gateTable) throw new Error('checklist: "## Gate summary" table not found')

const TASK_RE = /^P\d-\d{3}$/
type Task = {
  id: string
  gate: string
  task: string
  req: string
  owner: string
  status: string
  /** The whole Status cell, e.g. "BLOCKED BY P1-004" */
  statusText: string
  evidence: string
  line: number
}
const tasks: Task[] = []
for (const t of clTables) {
  const cS = t.headers.indexOf('Status')
  if (cS < 0 || !t.rows.some((r) => TASK_RE.test(r.cells[0]))) continue
  const col = (name: string) => {
    const k = t.headers.indexOf(name)
    if (k < 0)
      throw new Error(`checklist: "${t.heading}" task table has no "${name}" column`)
    return k
  }
  const [cT, cR, cO, cE] = [
    col('Task'),
    col('Req'),
    col('Owner'),
    col('Evidence required / link'),
  ]
  for (const r of t.rows) {
    if (!TASK_RE.test(r.cells[0])) continue
    const statusText = (r.cells[cS] ?? '').replace(/`/g, '').trim()
    tasks.push({
      id: r.cells[0],
      gate: r.cells[0].split('-')[0],
      task: r.cells[cT] ?? '',
      req: r.cells[cR] ?? '',
      owner: r.cells[cO] ?? '',
      // "BLOCKED BY P1-004" -> BLOCKED
      status: statusText.split(/\s/)[0],
      statusText,
      evidence: r.cells[cE] ?? '',
      line: r.line,
    })
  }
}
if (!tasks.length) throw new Error('checklist: no P<n>-<nnn> task rows found')

const gates = gateTable.rows.map((r) => {
  const id = r.cells[0]
  const counts: Record<string, number> = {}
  for (const t of tasks.filter((x) => x.id.startsWith(`${id}-`)))
    counts[t.status] = (counts[t.status] ?? 0) + 1
  // "DONE (closed by ..., 2026-11-19; ...)" -> status "DONE", note "closed by ..."
  const cell = r.cells[3].replace(/`/g, '').trim()
  const m = /^(\S+)\s*\((.*)\)\s*$/.exec(cell)
  return {
    id,
    name: r.cells[1],
    exit: r.cells[2],
    status: m ? m[1] : cell,
    note: m ? m[2] : '',
    counts,
    line: r.line,
  }
})

const naStart = checklist.findIndex((l) => /^##\s+Current next action/.test(l))
if (naStart < 0) throw new Error('checklist: "## Current next action" not found')
const blocks: string[] = []
for (let i = naStart + 1; i < checklist.length; i++) {
  if (/^#{1,6}\s/.test(checklist[i])) break
  const l = checklist[i].trim()
  if (!l) continue
  // a list item starts a new block; other lines join the one above
  if (blocks.length && checklist[i - 1].trim() && !/^([-*]|\d+\.)\s/.test(l))
    blocks[blocks.length - 1] += ` ${l}`
  else blocks.push(l)
}
// one entry per list item, or per sentence of a plain paragraph, so the
// site can show it as a list; the words are the record's own
const nextAction = blocks.flatMap((b) => {
  const item = /^(?:[-*]|\d+\.)\s+(.*)$/.exec(b)
  return item ? [item[1]] : b.split(/(?<=[.!?])\s+(?=[A-Z`(])/)
})
if (!nextAction.length) throw new Error('checklist: "Current next action" is empty')

const progress = {
  revision: clProp('Revision'),
  updated: clProp('Updated'),
  gates,
  nextAction,
  nextActionLine: naStart + 1,
  // every task row, for the Checklist page and links from the next action
  tasks: Object.fromEntries(tasks.map((t) => [t.id, t])),
}

// ---------- power budget: rail summary and the record's tables ----------
const powerLines = read(POWER)
const pwProp = (name: string) =>
  powerLines
    .map((l) => new RegExp(`^\\*\\*${name}:\\*\\*\\s*(.+)$`).exec(l)?.[1])
    .find(Boolean) ?? 'TBD'
const pwTables = parseTables(powerLines)
/** 1-based line of a "## n. ..." heading, or throw. */
const pwSection = (n: number) => {
  const i = powerLines.findIndex((l) => new RegExp(`^##\\s+${n}\\.\\s`).test(l))
  if (i < 0) throw new Error(`power budget: "## ${n}." heading not found`)
  return i + 1
}
/** Tables between two "## n." headings (to the end of the file without `to`). */
const pwTablesIn = (from: number, to?: number) => {
  const a = pwSection(from)
  const b = to === undefined ? Infinity : pwSection(to)
  return pwTables.filter((t) => t.rows.length && t.rows[0].line > a && t.rows[0].line < b)
}
const pwTable = (from: number, to: number | undefined, first: string) => {
  const t = pwTablesIn(from, to).find((x) => x.headers[0] === first)
  if (!t) throw new Error(`power budget: section ${from} table "${first}" not found`)
  return {
    heading: t.heading,
    headers: t.headers,
    rows: t.rows.map((r) => ({ cells: r.cells, line: r.line })),
  }
}

const summaryTable = pwTables.find((t) => t.heading === 'Rail summary')
if (!summaryTable) throw new Error('power budget: "### Rail summary" table not found')
const sumCol = (name: string) => {
  const k = summaryTable.headers.indexOf(name)
  if (k < 0) throw new Error(`power budget: Rail summary has no "${name}" column`)
  return k
}
const [sRail, sTyp, sWorst, sLimit, sFrom, sLabel] = [
  'Rail',
  'Typical load (mA)',
  'Worst-case load (mA)',
  'Limit (mA)',
  'Limit from',
  'Label',
].map(sumCol)
// numbers are copied as written; TBD stays null, anything else fails the build
const mA = (cell: string, where: string, required = false) => {
  const v = cell.trim()
  if (v === 'TBD' && !required) return null
  const n = Number(v)
  if (!v || !Number.isFinite(n))
    throw new Error(`power budget: Rail summary ${where} "${cell}" is not a number`)
  return n
}
const powerSummary = summaryTable.rows.map((r) => {
  const rail = r.cells[sRail]
  return {
    rail,
    typical: mA(r.cells[sTyp], `${rail} typical`),
    worst: mA(r.cells[sWorst], `${rail} worst case`),
    limit: mA(r.cells[sLimit], `${rail} limit`, true) as number,
    limitFrom: r.cells[sFrom] ?? '',
    label: r.cells[sLabel] ?? '',
    line: r.line,
  }
})
if (!powerSummary.length) throw new Error('power budget: Rail summary table is empty')

const loads = pwTablesIn(3, 4).map((t) => ({
  heading: t.heading,
  headers: t.headers,
  rows: t.rows.map((r) => ({ cells: r.cells, line: r.line })),
}))
if (loads.length < 4) throw new Error(`power budget: section 3 has ${loads.length} load tables, expected 4`)

const power = {
  file: POWER,
  revision: pwProp('Revision'),
  updated: pwProp('Updated'),
  summary: powerSummary,
  loads,
  loadsLine: pwSection(3),
  totals: pwTable(4, 5, 'Rail'),
  totalsLine: pwSection(4),
  tolerances: pwTable(5, 6, 'Rail'),
  tolerancesLine: pwSection(5),
  thermal: pwTable(11, undefined, 'Part'),
  thermalLine: pwSection(11),
}

// ---------- build stamp ----------
function commit(): string {
  if (process.env.GITHUB_SHA) return process.env.GITHUB_SHA
  try {
    return execSync('git rev-parse HEAD', { cwd: repo, encoding: 'utf8' }).trim()
  } catch {
    return 'local'
  }
}

// ---------- board model (Showcase) ----------
// The engineer exports the GLB with kicad-cli (a PCB output, so a human
// step) into web/public/models/. The site shows it when it is there. Its
// date is the last commit that changed it (CI checks out full history),
// or the file date for a model that is not committed yet.
const MODEL = 'models/ao-horizon.glb'
function boardModel() {
  const file = path.resolve(here, '../public', MODEL)
  if (!fs.existsSync(file)) return null
  let date = ''
  try {
    date = execSync(`git log -1 --format=%cs -- "web/public/${MODEL}"`, {
      cwd: repo,
      encoding: 'utf8',
    }).trim()
  } catch {
    // no git: fall back to the file date
  }
  if (!date) date = fs.statSync(file).mtime.toISOString().slice(0, 10)
  return { file: MODEL, bytes: fs.statSync(file).size, date }
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
  mainMcu: readmeSpec('Main MCU'),
  ioMcu: readmeSpec('IO MCU'),
  openSection,
  specChanges,
  specRevisions,
  build: { commit: commit(), date: new Date().toISOString().slice(0, 10) },
  boardModel: boardModel(),
  sources: {
    spec: SPEC,
    pins: PINS,
    readme: README,
    checklist: CHECKLIST,
    power: POWER,
  },
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
write('progress.json', progress)
write('history.json', specHistory)
write('power.json', power)

console.log(
  `extract-docs: ${Object.keys(ids).length} spec IDs, H743 ${h743.length} pins, ` +
    `F100 ${f100.length} pins + ${f100Reserved.length} reserved rows, phase ${meta.phase}, spec rev ${meta.specRevision}, ` +
    `${gates.length} gates, ${tasks.length} checklist tasks, build ${meta.build.commit.slice(0, 7)}`
)
