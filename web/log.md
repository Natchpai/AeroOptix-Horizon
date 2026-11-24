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

## 2026-11-22 T6: light-theme contrast and sidebar fade

- What: darker light-theme values for the status, muted and primary
  colours, so status and evidence text passes WCAG AA (4.5:1) on the
  background it sits on, tints included:
  - `--status-open` `#d97706` to `#a34a0c`
  - `--status-decided` `#16a34a` to `#15773a`
  - `--status-candidate` `#64748b` to `#5a697f`
  - `--muted-foreground` `#5b6b85` to `#55647d`
  - `--primary` `#2e78bd` to `#2a6fae`

  The ESTIMATED evidence badge now uses `--primary` instead of `--brand`
  (`#529ad6` in light, 3.0:1). In dark both are `#529ad6`, so dark looks
  the same. Dark values, rails and bus colours are unchanged.

  The sidebar nav list now fades out over its last 2.5rem (CSS mask) while
  links sit hidden below it; the fade goes away when the list is scrolled
  to the bottom or fits. Not in icon mode.
- Why: in light, OPEN, PRELIMINARY and open ID chips measured 2.6 to
  3.2:1, DONE and VERIFIED 3.3:1, ESTIMATED 3.0:1; muted text in the
  sidebar footer box 4.36:1, "Current next action" 4.11:1, deferred task
  chips 4.22:1. Lowest after, measured in the built site on Overview, Open
  items, Checklist, Spec history, Power budget and Decisions: open 4.61,
  decided 5.63, candidate 4.95, muted 4.66, primary 4.68 (ESTIMATED 5.27).
  The worst case is open and muted text in the sidebar footer box, a 10%
  tint of `--status-open`. At 1440 x 900 with a sub-menu open, the footer
  box cut "Design records" or "Specification" in half with no cue that the
  list scrolls.
- Files:
  - `src/styles/theme.css`: the five light (`:root`) values above.
  - `src/components/spec-text.tsx`: ESTIMATED uses `var(--primary)`.
  - `src/components/task-status.tsx`: the IN_PROGRESS task colour uses
    `var(--primary)` instead of `var(--brand)` (3.0:1 in light), as for
    ESTIMATED. No IN_PROGRESS task shows today.
  - `src/components/layout/app-sidebar.tsx`: `fadeWhenMore` callback ref
    sets `data-fade` on `SidebarContent` (scroll listener plus
    ResizeObserver, so sub-menus and the mobile sheet work); the mask
    classes on `SidebarContent`.
  - `tests/ui.ts`: new `lightContrast` check (OPEN, DONE, ESTIMATED,
    NOT_VERIFIED badges and the sidebar PRELIMINARY text, light theme,
    at least 4.5:1). With the old colours injected it fails at 2.57 to
    3.30:1.
  - `log.md`: this entry.

## 2026-11-22 T7: "Mentioned in" revisions on opened rows

- What: an opened row on Decisions, Open items and Traceability now lists
  "Mentioned in": the spec revisions whose change note (spec section 9)
  names that ID, newest first. Each is a revision chip that opens its row
  on Spec history; the URL keeps the revision as a string, so 0.10 stays
  0.10. The ID must match whole (DEC-030 does not match a longer ID that
  starts with it), and a
  range such as "IF-030 to IF-043" is not expanded; a muted note says so.
  Up to 12 chips show, then a "+N more" button. An ID no note names shows
  "Not named in any change note."
- Why: to see when and why a decision, open item or requirement changed
  without searching the history by hand. The chips only point to existing
  notes. The notes JSON (about 60 kB) loads with a dynamic import when the
  first row opens, so `records` (406.40 kB) is unchanged and the entry
  chunk grew 0.08 kB. Spot check against a word-boundary grep of the spec
  section 9 table: DEC-030 (0.21), DEC-013 (0.10), PWR-011 (0.47, 0.14,
  0.13) and OPEN-023 (15 revisions) match.
- Files:
  - `src/lib/history-mentions.ts`: `loadHistory` (cached dynamic import)
    and `mentionsOf` (word-boundary match).
  - `src/components/mentioned-in.tsx`: the `MentionedIn` list.
  - `src/features/decisions/index.tsx`, `src/features/open-items/index.tsx`,
    `src/features/trace/index.tsx`: the list in each detail row.
  - `src/features/about/index.tsx`: one sentence under "Finding things".
  - `tests/ui.ts`: new `mentionedInChips` check (DEC-030 to 0.21, DEC-013
    to 0.10, each lands on the Spec history row). Its page logic fails on
    the build before this change.
  - `log.md`: this entry.

## 2026-11-22 T8: Checklist owner filter and gate blockers

- What: the Checklist task list has a row of owner chips under the gate
  and state chips: All owners, then each owner with its task count, most
  tasks first. An Owner cell is split on "," and "+", so "Team +
  Hardware" counts under Team and under Hardware. A chip sets `?owner=`;
  a second click clears it. Owner, gate, state and text filters combine,
  and `?id=` still shows its row. Each chip row counts the tasks the
  other chip filters leave, so the state counts now follow the owner
  filter too. Under each gate that is not DONE, the Gates card lists
  "Open items naming this gate's tasks": open items (not closed or
  removed) whose "Owner / next action" cell names a task of that gate,
  as ID chips that open the row on Open items. Today P3 shows OPEN-004,
  009, 021, 023, 031, 040, 041 and P4 shows OPEN-011, 017, 021, 026,
  031, 034.
- Why: to see one person's or team's tasks at a glance, and which open
  items stand between an open gate and done. Both only cross-reference
  record text; the site adds no values.
- Files:
  - `src/routes/_site/checklist.tsx`: `owner` search param.
  - `src/features/checklist/index.tsx`: owner split, owner chips and
    filter, gate blocker lists.
  - `src/features/open-items/cites.ts`: `TASK_ID` exported (no change in
    behaviour), so the gate blockers find task IDs with the same regex.
  - `src/features/about/index.tsx`: one sentence under "Finding things".
  - `tests/ui.ts`: new `ownerFilter` (Software chip and `?owner=` show
    the computed row count) and `gateBlockers` (lists equal a computation
    from `ids.json` and `progress.json`; a chip opens its Open items row)
    checks, and `checklist?owner=Software` in the page-load list. Both
    fail on the build before this change.
  - `log.md`: this entry.

## 2026-11-22 T9: Pinout grouped by peripheral

- What: the "Allocated pins" card on the Pinout page has a view toggle,
  Table or By peripheral. By peripheral lists the pins in one small box
  per peripheral instance (USART1, I2C2, SPI1, TIM5, SDMMC1, OTG_FS,
  ADC1 ...), then "GPIO and EXTI" and "Debug, reset, clock, boot". The
  group name is the start of the signal text. Each box shows the name,
  the pin count and one row per pin: pin, the rest of the signal (SCK,
  CH1 (AF2)) and the function, as written in the record. Groups sort by
  kind (UART/USART, I2C, SPI, TIM, SDMMC, OTG_FS, ADC, GPIO, debug), then
  by number; pins by signal. The box colour is the existing bus colour.
  A pin click selects it like a table row (`?pin=`, details scroll into
  view). The view is kept in `?view=peripheral`, so a pin pick and the
  MCU switch keep it. The text filter works in both views. A signal that
  fits no group would go to an "Other" box (none today).
- Why: so the firmware team sees one peripheral's pins together. The
  site only regroups record rows; it adds no values.
- Files:
  - `src/features/pinout/peripherals.ts`: new grouping helper.
  - `src/features/pinout/index.tsx`: view toggle, `PeripheralList`,
    `view` kept on pin pick and MCU switch.
  - `src/routes/_site/pinout.tsx`: `view` search param.
  - `src/features/about/index.tsx`: one sentence under "Finding things".
  - `tests/ui.ts`: new `peripheralView` check (every H743 pin once, a
    SPI1_SCK click selects the pin), `pinout?mcu=h743&view=peripheral` in
    the page-load and phone-width lists. The check fails on the build
    before this change.
  - `log.md`: this entry.

## 2026-11-22 T5: prettier and knip cleanup

- What: `npm run format:check` and `npx knip` now pass. Prettier
  reformatted three files (whitespace and line endings only). Unused
  template helpers were removed: `useFont`, `sleep`, `getPageNumbers`
  and `getDisplayNameInitials`; nothing imported them. Names used only
  in their own file lost `export`: `NavItem`, `LaidEdge`, `GPIO_GROUP`,
  `DEBUG_GROUP`, `OTHER_GROUP`. knip now ignores exports used in their
  own file (`ignoreExportsUsedInFile: true`), which covers the per-view
  arrays in `topology.ts`, and `src/tanstack-table.d.ts` left the knip
  ignore list (knip hint). The object form `{ variable: true }` did not
  clear the topology arrays, so the option is the plain `true`.
- Why: so both checks can run clean and catch new issues. No behaviour
  change.
- Files:
  - `eslint.config.js`, `README.md`, `src/components/md-text.tsx`:
    prettier only (`md-text.tsx` had CRLF line endings; the content is
    the same as in Git).
  - `src/context/font-provider.tsx`: `useFont` and its `useContext`
    import removed.
  - `src/lib/utils.ts`: `sleep`, `getPageNumbers`,
    `getDisplayNameInitials` removed; `cn` stays.
  - `src/components/layout/types.ts`: `NavItem` no longer exported.
  - `src/features/diagram/layout.ts`: `LaidEdge` no longer exported.
  - `src/features/pinout/peripherals.ts`: the three group name
    constants no longer exported.
  - `knip.config.ts`: `ignoreExportsUsedInFile: true`, one ignore entry
    removed.
  - `log.md`: this entry.

## 2026-11-22 T11: bug-hunt fixes

- What: six small fixes from the bug hunt.
  - "Mentioned in" no longer shows "Loading…" forever when the change
    notes chunk fails to load. It shows "Could not load the change
    notes." and a "Reload page" button. A failed load is not cached, and
    the rejection is handled, so no unhandled rejection reaches the page.
  - The Pinout filter uses one match for Table and By peripheral: pin,
    package pin number, signal, function, refs, DS check and peripheral
    group name, any case. "Debug" now gives 8 pins in both views (was 2
    and 8), "not checked" 13 in both (was 13 and 0).
  - The Checklist shows a pressed chip for a `?owner=` or `?status=`
    value no chip names, with its count (0). A click clears the filter.
  - Pinout record text renders `code` and **bold** with `MdText`: the
    function in the table, the By peripheral list, the px4io reserved
    table and the pin details; the DS column and the pin details DS
    check; the reserved table Plan column. The package pin hover titles
    drop the backticks and stay plain text, since the SVG export clones
    the on-screen package with them; no CSS or HTML reaches the file.
  - `tests/ui.ts`: the tab title check waits for each page's exact title
    (up to 10 s) instead of a fixed 800 ms. The gate blocker check also
    asserts OPEN-004 under P3 and no closed OPEN item under any gate.
- Why: bugs found in the bug hunt. A retry alone would not fix the notes
  load: after a deploy the old hashed chunk is gone, so the page must
  reload. The site adds no values.
- Files:
  - `src/lib/history-mentions.ts`: `loadHistory` drops a failed promise.
  - `src/components/mentioned-in.tsx`: error note and reload button.
  - `src/features/pinout/peripherals.ts`: new `pinMatches`.
  - `src/features/pinout/index.tsx`: table `globalFilterFn` and the
    groups both use `pinMatches`; `MdText` for function, DS and Plan
    text.
  - `src/features/pinout/package-view.tsx`: pin titles without
    backticks (`plain`).
  - `src/features/checklist/index.tsx`: chips for unknown owner and
    status values.
  - `tests/ui.ts`: new `mentionedInFails` (notes chunk blocked),
    `unknownChipFilters` (`?owner=Nobody`, `?status=WAITING`) and
    `pinFilterSame` ("Debug", "not checked") checks, which fail on the
    build before this change; `pageTitles` and `gateBlockers` as above;
    `open()` takes a `setup` hook for routes and init scripts.
  - `log.md`: this entry.

## 2026-11-22 T1b: unknown id notice and reserved Plan wrap

- What: two fixes from the Known gaps list.
  - A linked `?id=` that names no record now shows one muted line above
    the table: "DEC-nnn is not in the spec." (Decisions, Open items),
    "Pn-nnn is not in the checklist." (Checklist), "IF-nnn is not a
    requirement in the spec." (Traceability, which lists requirements
    only) and "Revision 9.99 is not in the spec change notes." (Spec
    history, `?rev=`). The check uses every record of the page before
    any filter, so q, kind, flag, owner, status or "hide closed" never
    shows the notice for a known ID. A malformed ID is still dropped by
    the route's `validateSearch`, so it shows no notice; that is
    accepted.
  - The F100 reserved table's Plan column wraps (`min-w-64`,
    `whitespace-normal`, `break-words`), so at 1440 px the table fits its
    card. At 390 px it still scrolls sideways inside the card (the phone
    is not critical). Other tables are unchanged.
  - `tests/ui.ts`: `unknownIdNotice` (an unknown ID on each of the five
    pages shows the notice; a known ID, alone and with a filter that
    hides it, shows none) and `reservedPlanFits` (no scroll wrapper of
    the reserved card scrolls sideways at 1440 px). Both fail on the
    build before this change. The filter case also fails on a test build
    that checked only the visible rows.
- Why: an unknown link selected nothing with no word why, and long Plan
  text pushed the reserved table wider than its card. The site adds no
  values.
- Files:
  - `src/components/unknown-id-notice.tsx`: new shared `UnknownIdNotice`.
  - `src/features/decisions/index.tsx`, `src/features/open-items/index.tsx`,
    `src/features/checklist/index.tsx`, `src/features/history/index.tsx`,
    `src/features/trace/index.tsx`: a set of all record IDs and the
    notice above the table.
  - `src/features/pinout/index.tsx`: reserved table Plan cell classes.
  - `tests/ui.ts`: the two checks above.
  - `HANDOFF.md`: the two Known gaps lines removed.
  - `log.md`: this entry.

## 2026-11-22 T3: BOM page

- What: a new `/bom` page shows the engineer's KiCad BOM export as
  written.
  - The extractor reads the one `*.csv` in
    `hardware/AO-Horizon/documents/manufacturing/Assembly/BOM/`, any
    name; none or two CSV files fail the build and list the names
    found. Other files there are ignored. A small CSV parser handles
    quoted cells with commas, `""` escapes, a UTF-8 byte order mark and
    CRLF or LF. Required columns: Reference, Qty, Value, DNP, LCSC, MFR,
    MFR.P/N; optional: Footprint, STATUS, Exclude from BOM. The build
    also fails when a row's Qty differs from its reference count, a
    reference is in two rows, a DNP cell is not `DNP` or empty, or the
    parsed row count differs from the file's data lines. `bom.json`
    holds the rows (refs as a list, ranges such as `R1-R5` expanded)
    and the file name, last commit date (`uncommitted` before a
    commit), row count and Qty sum, all computed from the file.
  - "Exclude from BOM" is empty on every row of the 2026-11-22 export,
    so it is only copied where a cell has text and shown in the detail
    row. The export has no Footprint column, so the Footprint column
    stays hidden.
  - The page: Refs (compact, with a count), Qty, Value, MFR, MFR.P/N,
    LCSC and DNP columns; a DNP filter (All rows, Fitted, DNP); a text
    filter. The header line gives the file name and date, rows, parts
    and DNP parts. `?id=R306` opens the row that holds that reference
    (whole reference only), also when a filter would hide it; an
    unknown reference shows "R999 is not in the BOM.". The detail row
    lists every reference, the diagram blocks whose `sub` names the
    MFR.P/N or whose part number starts it (as the Power budget links
    loads), and the DEC rows whose Topic or Selected option names the
    MFR.P/N as a whole word. Report-only flag: a fitted row without
    MFR.P/N or LCSC (TP605 today). No stock or price. On a phone Qty
    and the part columns hide; the Refs cell carries the count.
  - Sidebar item, Overview card and About pages-list row. The Ctrl+K
    menu lists it through the sidebar data.
  - `bom.json` loads with the page (its own chunk); the `records` chunk
    is unchanged at 406 kB.
- Why: the BOM page idea in `HANDOFF.md`, now that the engineer exports
  the BOM. The site adds no values.
- Files:
  - `scripts/extract-docs.ts`: `parseCsv`, `expandRefs`, `readBom`;
    writes `bom.json`; `meta.sources.bom`; `AO_BOM_DIR` points it at
    another folder (used for the failure tests).
  - `src/data/types.ts`: `BomRow`, `Bom`, `Meta.sources.bom`.
  - `src/routes/_site/bom.tsx`: route with `q`, `id`, `dnp`.
  - `src/routeTree.gen.ts`: regenerated by the router plugin.
  - `src/features/bom/index.tsx`: the page.
  - `src/features/bom/links.ts`: block and DEC matching, flags.
  - `src/components/layout/data/sidebar-data.ts`,
    `src/features/overview/index.tsx`, `src/features/about/index.tsx`:
    nav item, card, pages-list row.
  - `tests/ui.ts`: `bomPage` (see `README.md`), `/bom` in the page-load,
    390 px, tab title, cell alignment and unknown-ID lists. Refs and
    counts come from `bom.json`. The checks fail on the build before
    this change (no `/bom` page), on a test copy of `bom.json` with one
    row changed, on a build whose `?id=` matched by prefix, and on a
    build with Qty shown on phones (table 367 px in 356 px).
  - `HANDOFF.md`, `README.md`, `log.md`: docs.

## 2026-11-22 T4: BOM Description column

- What: the BOM page shows the Description text of the engineer's KiCad
  export when the export has a Description column.
  - The extractor reads Description as an optional column, like
    Footprint: each `bom.json` row gets `description` and
    `meta.columns.description` is set. An export without it still
    builds, and the page then looks as before.
  - At `sm` and up the Description is a muted second line under Value.
    That fits better than a new column: the table already has eight
    columns at `xl`, and Description explains the Value. With a
    Description, Value gets wider and Refs narrower (Refs
    22/18/16 %, Value 24/20/22/24 % at sm/md/lg/xl), so MFR.P/N keeps
    about the width it had. At 1440 px the longest text wraps to three
    lines inside the card, and the table is 1142 px in 1142 px.
  - On a phone the row hides it; the detail row lists it first, in the
    normal font.
  - The text filter `q` also searches Description.
- Why: the engineer's rev-A export (2026-11-22) has a Description on
  every row.
- Files:
  - `scripts/extract-docs.ts`: optional Description column.
  - `src/data/types.ts`: `BomRow.description`,
    `Bom.meta.columns.description`.
  - `src/features/bom/index.tsx`: second line under Value, column widths
    with a Description, detail row field, filter text.
  - `tests/ui.ts`: `bomPage` checks, when `bom.json` has descriptions,
    that the first described row shows its Description at 1440 px, and
    that `?q=` with a word found only in Descriptions (picked from the
    data at run time) lists exactly the rows whose Description has it.
    Both checks fail on the build from before this change (no
    Description shown, no row found) and pass after it. With a test
    export that has no Description column, the checks are skipped with
    a warning and the column widths match the old build.
  - `HANDOFF.md`, `README.md`, `log.md`: docs.

## 2026-11-22 T5: no sideways scroll at 768 px

- What: at 768 px every page was 840 px wide in a 768 px window (825 px
  on the light Showcase), in both themes. The header row did not fit:
  from `md` the 256 px sidebar shows and leaves a 504 px content column,
  but the header needs about 598 px (sidebar button, the 211 px
  "PRELIMINARY · not for fabrication" badge, the 160 px search, theme and
  settings buttons, gaps). The theme and settings buttons sat past the
  right edge and the page title shrank to nothing. It happened from 768
  to about 860 px; 640, 1024 and 1280 px had no sideways scroll.
  - The header badge now shows only when the content column is at least
    42rem (672 px) wide (`md:@2xl/content:inline-flex`, a container query
    on the existing `@container/content`). With the sidebar open that is
    from about 936 px; with it closed, from 768 px. The sidebar footer
    shows the same phase text, so nothing is lost. At 390 and 1440 px the
    page looks the same as before (screenshots compared).
  - After the fix, all 15 pages (Overview, About, the three diagram
    views, both Pinout peripheral views, Decisions, Open items,
    Checklist, Spec history, Traceability, Power budget, BOM, Showcase)
    are exactly as wide as the window at 640, 768, 1024 and 1280 px, in
    dark and light.
- Why: a tablet-width window could scroll sideways, and the theme and
  settings buttons were off screen.
- Files:
  - `src/components/layout/site-header.tsx`: the badge class.
  - `tests/ui.ts`: the no-sideways-scroll loop also runs at 768 px (both
    themes) and 1024 px (dark), for every route it covered at 390 px.
    The zoom and view-tab checks still run at 390 px only. On the build
    from before this change the loop fails 40 times, all at 768 px (20
    routes, two themes, "840 px wide at 768 px"); after it, it passes.
  - `HANDOFF.md`: Checks list.
- Fix round 1: table headers at 768 px. With the 504 px content column,
  two tables gave one column almost no width, and its header text ran
  into the next header: Decisions ("Decision" over "Date") and
  Traceability ("Requirement" over "DEC"). The other table pages (Open
  items, Checklist, Spec history, Power budget, BOM, the Pinout tables)
  had no overlap.
  - Decisions: the On diagram column shows from the same 42rem content
    width as the header badge (`md:@2xl/content:table-cell`), so Decision
    gets 98 px at 768 px (0 px before). The row detail still lists the diagram
    items.
  - Traceability: the four count columns (DEC, OPEN, Tasks, Diagram) use
    the same rule, so Requirement gets the width at 768 px, as on a phone.
  - At 390 and 1440 px the tables are pixel-identical before and after.
  - Files: `src/features/decisions/index.tsx`,
    `src/features/trace/index.tsx`, `tests/ui.ts` (`headersClear`: at
    768 px, dark, no two `thead th` text boxes overlap on Decisions, Open
    items, Checklist, Spec history, Traceability, Power budget, BOM and
    the four Pinout views; it fails on the build before this round with
    the two overlaps above and passes after), `HANDOFF.md` (Checks).
