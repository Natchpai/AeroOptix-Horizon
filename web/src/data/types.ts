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
  /** Last spec change notes (section 9), newest first */
  specChanges: {
    revision: string
    date: string
    description: string
    approvedBy: string
    line: number
  }[]
  /** Commit and date the site was built from */
  build: { commit: string; date: string }
  sources: { spec: string; pins: string; readme: string; checklist: string }
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
    /** Task count per status (DONE, IN_PROGRESS, OPEN, BLOCKED ...) */
    counts: Record<string, number>
    line: number
  }[]
  /** One entry per sentence or list item, in record order */
  nextAction: string[]
  nextActionLine: number
  tasks: Record<string, { status: string; line: number }>
}
