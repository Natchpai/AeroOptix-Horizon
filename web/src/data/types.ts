/** Power rails come first, high to low voltage; the rest are signal buses. */
export type Bus =
  | 'batt'
  | 'v6'
  | 'v5'
  | 'v3v3'
  | 'v3v3a'
  | 'spi'
  | 'i2c'
  | 'uart'
  | 'pwm'
  | 'usb'
  | 'sdmmc'
  | 'debug'
  | 'gpio'
  | 'analog'

/**
 * Design state of a block or link, from the spec:
 * - decided: a DEC row or a confirmed part/allocation exists
 * - open: an open OPEN-xxx item still affects it
 * - candidate: shown in the spec diagram only, part or path TBD
 * Every item is still NOT_VERIFIED as a built design.
 */
export type Status = 'decided' | 'open' | 'candidate'

export type Level = 'system' | 'board' | 'power'

export type BlockKind =
  | 'board'
  | 'mcu'
  | 'sensor'
  | 'power'
  | 'rail'
  | 'bus'
  | 'connector'
  | 'io'
  | 'external'

export type Mcu = 'h743' | 'f100'

export type Block = {
  id: string
  level: Level
  label: string
  /** Part number or short detail, copied from the spec. */
  sub?: string
  kind: BlockKind
  /** Spec IDs (IF, DEC, SEN, PWR ...) this block comes from. */
  refs: string[]
  /** Open items that still affect this block. */
  open?: string[]
  status?: Status
  note?: string
  /** Clicking opens this level (system board node -> board view). */
  drill?: Level
  /** For MCU blocks: the pin table to use. */
  mcu?: Mcu
  /** Power rail or signal bus the block carries or outputs; sets its colour. */
  rail?: Bus
}

/** Picks rows from a pin table. All given filters must match. */
export type PinSelect = {
  mcu: Mcu
  refs?: string[]
  /** Regex on the Function column. */
  fn?: string
  /** Regex on the Signal column. */
  signal?: string
}

export type Link = {
  id: string
  level: Level
  from: string
  to: string
  bus: Bus
  label: string
  refs: string[]
  open?: string[]
  status?: Status
  note?: string
  /** MCU pins on each end; far ends without pins show TBD. */
  pins?: PinSelect[]
}

export type SpecId = {
  id: string
  kind: string
  section: string
  fields: Record<string, string>
  removed: boolean
  closed: boolean
  file: string
  line: number
  text: string
}

export type PinRow = {
  function: string
  refs: string[]
  signal: string
  pin: string
  number: number | null
  ds: string
  line: number
}

export type ReservedRow = {
  pins: string[]
  function: string
  plan: string
  line: number
}

export type Meta = {
  project: string
  tagline: string
  phase: string
  boardRevision: string
  baseline: string
  kicad: string
  specRevision: string
  specUpdated: string
  specStatus: string
  keyFeatures: string[]
  mainMcu: string
  ioMcu: string
  /** Spec heading number of the OPEN rows, e.g. "8.2" */
  openSection: string
  /** Last 5 spec change notes (section 9), newest first */
  specChanges: SpecChange[]
  /** Revision and date of every change note, newest first (for search) */
  specRevisions: { revision: string; date: string }[]
  /** Commit and date the site was built from */
  build: { commit: string; date: string }
  /** Board GLB for the Showcase (web/public), or null when not exported */
  boardModel: { file: string; bytes: number; date: string } | null
  sources: {
    spec: string
    pins: string
    readme: string
    checklist: string
    power: string
    /** The one BOM CSV the build read */
    bom: string
  }
  generatedFrom: string
}

/** Execution checklist: gates, task counts per status, next action. */
export type Progress = {
  revision: string
  updated: string
  gates: {
    id: string
    name: string
    exit: string
    status: string
    /** Text in brackets after the status in the record, or '' */
    note: string
    /** Task count per status (DONE, IN_PROGRESS, OPEN, BLOCKED ...) */
    counts: Record<string, number>
    line: number
  }[]
  /** One entry per sentence or list item, in record order */
  nextAction: string[]
  nextActionLine: number
  tasks: Record<string, Task>
}

/** One P<n>-<nnn> row of the checklist, cells as written there. */
export type Task = {
  id: string
  /** Gate the task belongs to, e.g. P3 */
  gate: string
  task: string
  /** Spec IDs, as written (ranges like "IF-030 to IF-043" stay text) */
  req: string
  owner: string
  /** First word of the Status cell: OPEN, DONE, BLOCKED, N/A ... */
  status: string
  /** The whole Status cell, e.g. "BLOCKED BY P1-004" */
  statusText: string
  evidence: string
  line: number
}

/** One row of the spec section 9 change-note table. */
export type SpecChange = {
  revision: string
  date: string
  description: string
  approvedBy: string
  line: number
}

/** A table from a design record, cells as written there. */
export type RecordTable = {
  heading: string
  headers: string[]
  rows: { cells: string[]; line: number }[]
}

/** One row of the power budget "Rail summary" table; numbers in mA. */
export type RailSummary = {
  rail: string
  /** null where the record says TBD */
  typical: number | null
  worst: number | null
  limit: number
  limitFrom: string
  label: string
  line: number
}

/** The power budget record, as `power.json` holds it. */
export type Power = {
  file: string
  revision: string
  updated: string
  summary: RailSummary[]
  /** Section 3, one table per rail */
  loads: RecordTable[]
  loadsLine: number
  totals: RecordTable
  totalsLine: number
  tolerances: RecordTable
  tolerancesLine: number
  thermal: RecordTable
  thermalLine: number
}

/** One row of the engineer's BOM export, cells as written there. */
export type BomRow = {
  /** Reference cell split on ",", ranges such as R1-R5 expanded */
  refs: string[]
  qty: number
  value: string
  dnp: boolean
  lcsc: string
  mfr: string
  /** The MFR.P/N column */
  mpn: string
  /** Only when the export has the column */
  description?: string
  footprint?: string
  status?: string
  /** The "Exclude from BOM" cell, only where it is not empty */
  exclude?: string
  /** CSV line the row starts on */
  line: number
}

/** The BOM export, as `bom.json` holds it. */
export type Bom = {
  meta: {
    /** Repo path of the CSV */
    file: string
    name: string
    /** Last commit that changed the file, or "uncommitted" */
    date: string
    rows: number
    /** Qty sum */
    parts: number
    /** Qty sum of the DNP rows */
    dnpParts: number
    /** Which optional columns the export has */
    columns: {
      description: boolean
      footprint: boolean
      status: boolean
      exclude: boolean
    }
  }
  rows: BomRow[]
}
