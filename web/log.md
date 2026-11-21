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

## 2026-11-22 T3: page titles and diagram tabs on phones

- What: every page now sets its own browser tab title, "<page> ·
  AeroOptix-Horizon" (diagram views add the view name, for example "Block
  diagram · System · AeroOptix-Horizon"). The static meta description no
  longer names a phase. Below the sm breakpoint the diagram view tabs hide
  their L0/L1/L2 hints, so all four tabs fit at 390 px. Two new browser
  checks: tab titles are distinct and end with the site name, and the view
  tabs fit at 390 px.
- Why: every tab read "AeroOptix-Horizon", the description said "Draft"
  while the README phase is PRELIMINARY, and "Interface L2" ran off the
  right edge on phones.
- Files:
  - `src/components/layout/site-header.tsx`: sets `document.title` from a
    new `pageTitle` prop, or from `title` when it is a string; resets it to
    the site name on unmount.
  - `src/features/diagram/index.tsx`: passes `pageTitle` with the view
    name; `data-view-tabs` on the tab group; level hints `hidden sm:inline`.
  - `index.html`: description drops "Draft, not for fabrication."; Prettier
    split the two icon `<link>` tags over several lines.
  - `tests/ui.ts`: new `pageTitles` check, new `viewTabsFit` check in the
    390 px diagram loop, file header updated.
  - `log.md`: this entry.

## 2026-11-22 T4: smaller logo files

- What: new small copies of the four logo PNGs (flame 256 x 256 px, nP
  128 x 91 px, transparency kept), made with Edge canvas at high smoothing
  quality. The sidebar, the Overview hero and the two favicon links now use
  them. The original PNGs stay in `public/images/`.
- Why: the logos show at 16 to 80 px, but each page fetched about 1.5 MB of
  3000 x 3000 and 2800 x 2000 px PNGs (both theme variants load, one is
  hidden with CSS). Image bytes on the Overview, dark and light, measured
  in the built site: 1,723,079 B before, 47,305 B after (4 logo files plus
  the light flame fetched again as favicon; the 4 distinct files went from
  1,567,391 B to 35,719 B). Screenshots at 1440 px look the same, still
  sharp. The favicon hrefs were already fine: Vite rewrites `/images/...`
  to `/AeroOptix-Horizon/images/...`.
- Files:
  - `public/images/AeroOptix_v2_dark_theme_256.png` (new, 11,624 B)
  - `public/images/AeroOptix_v2_light_theme_256.png` (new, 11,586 B)
  - `public/images/np_dark_theme_128.png` (new, 6,254 B)
  - `public/images/np_light_theme_128.png` (new, 6,255 B)
  - `src/components/brand-logo.tsx`: `BrandLogo` and `CoopLogo` use the
    small files.
  - `index.html`: the two icon links use the small flame files.
  - `log.md`: this entry.
