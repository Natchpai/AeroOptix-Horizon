import { useEffect } from 'react'

/**
 * Non-component helpers of the record table pages (Decisions, Open items,
 * Checklist, Spec history, Traceability). The components are in
 * `src/components/record-table.tsx`.
 */

/** Small caps heading inside a detail row. */
export const detailLabel =
  'text-xs font-semibold tracking-wide text-muted-foreground uppercase'

/** Display names of the diagram levels (ids differ, engineer 2026-10-26). */
export const levelName = { system: 'Overview', board: 'System', power: 'Power' }

/** A link such as ?id=DEC-050 scrolls its row (`${prefix}${id}`) into view once. */
export function useScrollToRow(
  id: string | undefined,
  prefix = 'row-',
  block: ScrollLogicalPosition = 'start'
) {
  useEffect(() => {
    if (!id) return
    const t = setTimeout(
      () =>
        document.getElementById(`${prefix}${id}`)?.scrollIntoView({ block }),
      50
    )
    return () => clearTimeout(t)
  }, [id, prefix, block])
}
