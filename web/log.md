# Website change log

One entry per change: what changed, why, and which files were edited.

## 2026-11-22 T2: table and text fixes

- What: four display fixes. The Decisions Date cell shows the first date on
  one line and the change note (", changed ...", ", revised ...") on a second,
  wrapped line. Power budget table cells wrap only between words, so short
  values such as "TBD" stay whole. Every text filter input has an
  `aria-label`. The Traceability tile and table header now say the same thing
  about removed rows. A new browser check fails when a Decisions Date cell is
  wider than its cell.
- Why: long dates ran into the "On diagram" column, "TBD" broke into "TB / D",
  filter inputs had no accessible name (placeholder only), and the tile said
  "103" while the header said "109 of 109" without saying why.
- Files:
  - `src/features/decisions/index.tsx`: Date cell split at the first ", "
    into two lines; `aria-label='Filter decisions'`.
  - `src/features/power/index.tsx`: record table cells use `break-words`
    instead of `[overflow-wrap:anywhere]`.
  - `src/features/pinout/index.tsx`: `aria-label='Filter pins'`.
  - `src/features/open-items/index.tsx`: `aria-label='Filter open items'`.
  - `src/features/checklist/index.tsx`: `aria-label='Filter tasks'`.
  - `src/features/history/index.tsx`: `aria-label='Filter spec revisions'`.
  - `src/features/trace/index.tsx`: `aria-label='Filter requirements'`; live
    and removed counts computed once; tile hint says removed rows are listed
    greyed; header reads "N of 109 rows (103 live, 6 removed, greyed)".
  - `tests/ui.ts`: new `decisionDatesFit` check at 1440 px, run from `main`,
    and listed in the file header.
