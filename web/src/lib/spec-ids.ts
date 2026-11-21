import { ids } from '@/data'

/** Spec ID kinds that are requirements (the rows of the Traceability page). */
export const REQ_KINDS = [
  'SYS',
  'MCU',
  'IF',
  'SEN',
  'PWR',
  'SAF',
  'FUN',
  'ENV',
  'CMP',
  'MEC',
  'PCB',
  'MFG',
  'TST',
]

const pad = (n: number, width: number) => String(n).padStart(width, '0')

/**
 * Every spec ID a text names, with ranges written as "IF-030 to IF-043"
 * expanded to the IDs between them that exist in the spec.
 */
export function idsIn(text: string): Set<string> {
  const out = new Set<string>()
  const re = /\b([A-Z]{2,5})-(\d{2,3})\b(?:\s+to\s+\1-(\d{2,3})\b)?/g
  for (const m of text.matchAll(re)) {
    const [, kind, from, to] = m
    if (!to) {
      out.add(`${kind}-${from}`)
      continue
    }
    for (let n = Number(from); n <= Number(to); n++) {
      const id = `${kind}-${pad(n, from.length)}`
      if (ids[id]) out.add(id)
    }
  }
  return out
}
