import type { SpecChange } from '@/data'

/**
 * Spec change notes (section 9) that name a spec ID. The notes JSON is
 * loaded on first use with a dynamic import, so the pages that only open a
 * row now and then do not carry it in their own or the `records` chunk.
 */

let notes: Promise<SpecChange[]> | undefined

/**
 * Every change note, newest first (the order the extractor writes). A failed
 * load is not cached, so the next call tries again.
 */
export function loadHistory(): Promise<SpecChange[]> {
  notes ??= import('@/data/generated/history.json')
    .then((m) => m.default as SpecChange[])
    .catch((e) => {
      notes = undefined
      throw e
    })
  return notes
}

/**
 * The notes whose description names `id` exactly, on word boundaries:
 * DEC-030 does not match DEC-0301. A range such as "IF-030 to IF-043" names
 * only its two ends; the IDs between are not expanded.
 */
export function mentionsOf(history: SpecChange[], id: string): SpecChange[] {
  const re = new RegExp(`\\b${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`)
  return history.filter((c) => re.test(c.description))
}
