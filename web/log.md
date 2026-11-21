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
  0.10. The ID must match whole (DEC-030 does not match DEC-0301), and a
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
