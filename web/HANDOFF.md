# Handoff: team website

**Updated:** 2026-11-22

**Status:** live on GitHub Pages. Pages: Overview, About this site, Block diagram, Pinout, Decisions, Open items, Checklist, Spec history, Traceability, Power budget, Showcase. The engineer approved the Pinout page and the five pages added on 2026-11-21, reviewed the Block diagram, and merged the About page, Overview cards, CI test and layout fixes (PR #58, deployed from `6bed2d9`). Hand-written diagram text is synced to spec rev 0.87 and pin allocation rev 0.31. The 2026-11-22 run (`c437c20` to `e90818a`) is on `dev`, waiting for a PR to `main`: tab titles, small logo files, light-theme contrast, sidebar fade, "Mentioned in" revisions, Checklist owner filter and gate blockers, Pinout by peripheral, prettier and knip cleanup, and bug-hunt fixes. Each change is in `log.md`.

Rules for content, drawing, look and checks are in `CLAUDE.md`. Commands are in `README.md`. History is in Git (`git log -- web`).

## Where things are

- **Live site:** https://natchpai.github.io/AeroOptix-Horizon/
- **Deploy:** `.github/workflows/pages.yml`, on a push to `main` that touches `web/`, the design docs or `README.md`; it can also be started by hand. It builds only.
- **CI browser test:** `.github/workflows/web-test.yml` runs `npm run test:ui` in Playwright's bundled Chromium on pushes to `dev` and PRs to `main` (same paths), and by hand. About 4 minutes in all, 2 of them the test.
- **Change log:** `log.md`, one entry per change: what changed, why, and the files.
- **Merging:** `main` needs linear history, so PRs from `dev` are squash-merged. After each PR, merge `main` into `dev`.
- **What the build reads** (`scripts/extract-docs.ts`). A missing heading, table or column fails the build, and the old site stays up.
  - Spec: every ID row, the header, and every section 9 change note (`history.json`; `meta.specChanges` keeps the last 5, `meta.specRevisions` the revision and date of each for Ctrl+K).
  - Pin allocation: H743, F100 and F100-reserved tables.
  - Checklist: `Gate summary`, every task row (ID, Task, Req, Owner, Status, Evidence required / link) and `Current next action`.
  - Root `README.md`: phase, revisions, key features, MCUs.
  - Power budget (`power.json`): the section 4 `### Rail summary` table (mA; `TBD` stays empty, other text fails), the section 3 load tables and the section 4, 5 and 11 tables.
- **Hand-written:** blocks and links in `src/data/topology.ts`, positions in `src/data/places.ts`, page texts of the About page in `src/features/about/index.tsx` (phases and evidence labels follow `.claude/rules/workflow.md` and `engineering.md`; the phase itself comes from the README).
- **Shared code for the table pages:** `RecordTable`, `DiagramItemList`, `SiteRowList` and `TaskRowList` in `src/components/record-table.tsx`; `useScrollToRow`, `detailLabel` and `levelName` in `src/lib/record-rows.ts`; `idsIn` (range expansion) and `REQ_KINDS` in `src/lib/spec-ids.ts`; `SpecText` (ID and task chips, `labels` for evidence badges) in `src/components/spec-text.tsx`.

## How the site behaves (non-obvious parts)

- **Links between pages.** An ID chip opens its site row: DEC on Decisions, OPEN on Open items, a requirement kind on Traceability; other kinds (REF) open the spec on GitHub. A task chip opens Checklist, a revision chip Spec history. Ctrl+K results do the same. On an ID's own page the ID column chip is `plain`, so the row click opens it and the filter stays.
- **`?id=` beats filters.** On every table page a linked row shows even when a filter (or "hide closed") would hide it.
- **Revision URLs.** Revisions 0.1 and 0.10 both exist, and the router reads a typed `?rev=0.10` as the number 0.1. Site links keep the string (`?rev=%220.10%22`); `test:ui` checks it.
- **Tab titles.** `SiteHeader` sets `document.title` to "<page> · AeroOptix-Horizon" from its `pageTitle` prop, or from `title` when it is a string; the diagram adds the view name. It goes back to the site name on unmount.
- **Logos.** The sidebar, the Overview hero and the favicons use small copies: the flame at 256 px (`AeroOptix_v2_*_theme_256.png`), the nP mark at 128 px (`np_*_theme_128.png`). The full-size originals stay in `public/images/`.
- **Light-theme colours.** The light status, muted and primary values in `theme.css` (`:root`) are darker, so status and evidence text passes WCAG AA (4.5:1) on its background, tints included. Dark is unchanged. IN_PROGRESS and ESTIMATED use `--primary`, not `--brand` (3.0:1 in light).
- **Sidebar fade.** While nav links sit hidden below the sidebar's bottom edge, `data-fade` on `SidebarContent` turns on a CSS mask over the last 2.5rem. It goes away at the bottom of the list, and is off in icon mode.
- **"Mentioned in"** on opened Decisions, Open items and Traceability rows lists the spec revisions whose change note names the ID. The ID must match whole, and a range such as "IF-030 to IF-043" is not expanded. The notes JSON is a lazy chunk, loaded when the first row opens (`src/lib/history-mentions.ts`). If it fails (after a deploy the old hashed chunk is gone), the row says "Could not load the change notes." with a Reload page button.
- **Checklist owner filter** (`?owner=`): an Owner cell is split on "," and "+", so "Team + Hardware" counts under both. A `?owner=` or `?status=` value no chip names shows as a pressed chip with count 0; a click clears it.
- **Gate blockers.** Under each gate that is not DONE, the Gates card lists the OPEN rows (not closed or removed) whose "Owner / next action" names a task of that gate. Task IDs are found with the shared `TASK_ID` from `src/features/open-items/cites.ts`.
- **Open items** show the full description only in the opened row: OPEN-023 is about 4,600 characters.
- **Traceability** is built in the browser (`src/features/trace/matrix.ts`), report only. Flags: no task names the requirement in Req; no live DEC row and no diagram item cites it. Removed rows are never flagged. On 2026-11-21: 3 without a task (CMP-010 to CMP-012; CMP-010 is in the P1-014 task text but not its Req) and 29 without a decision or diagram item.
- **Power budget** draws one bullet bar per Rail summary row, each on its own scale; values are never recomputed. A load links to its Power view block when the block's part number is in the load name or its refs share an ID with the row's Ref. The rail colours fail the dataviz validator as a categorical set (light: 6 V against 5 V; dark: 3.3 V against 3.3 V_IMU, protan), so every bar also carries its rail name and numbers.
- **Diagram on a phone** (canvas under 640 px): a view that would fit below zoom 0.35 opens centred on its start block (FC, Main MCU or the power mux) at 0.35.
- **Diagram fit and minimap:** from 1024 px the fit (and the fit button) keeps a 200 px strip on the right free, so the bottom-right minimap covers no block.
- **Pinout layout:** the package and the pin details (or, with no pin picked, a per-bus pin count from 1280 px) sit side by side; the pin tables run full width below. Picking a table row scrolls the details into view. "By peripheral" (`?view=peripheral`) swaps the table for one box per peripheral; the group is the start of the signal text (`src/features/pinout/peripherals.ts`), and a pin pick or MCU switch keeps the view. Both views filter with the one `pinMatches`. Function, DS and Plan text render with `MdText`; the package pin hover titles drop the backticks, since the SVG export clones them.
- **knip** ignores exports used in their own file (`ignoreExportsUsedInFile: true`), which covers the per-view arrays in `topology.ts`.
- **Bundle:** the Ctrl+K menu loads when the browser is idle or on first open. `meta`, `ids`, `pins` and `progress` JSON form the `records` chunk (406 kB, 86 kB gzip), which every page needs; the old 593 kB `search-provider` chunk was mostly this data, so the first load fell only from 228 to 215 kB gzip. The remaining Vite size warning is `model-viewer`, loaded only on the Showcase.
- **Showcase** shows `web/public/models/ao-horizon.glb` with `@google/model-viewer`. The KiCad GLB sets only a base colour per material, so `fixMaterials()` sets metallic and roughness by colour; lighting is `legacy`, `neutral` tone mapping, exposure 1. The engineer re-exports the GLB after layout changes (a PCB output) and commits it:
  `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb export glb --subst-models --include-silkscreen --include-soldermask -o web/public/models/ao-horizon.glb hardware/AO-Horizon/AO-Horizon.kicad_pcb`
  The current GLB (2026-11-21, 8.1 MB) came from an uncommitted PCB with many parts not yet placed.

## Engineer decisions

- **2026-10-24:** GitHub Pages, public with the repo. shadcn-admin template. Dark theme with nP blue and navy; the AeroOptix flame is the main logo and nP a small co-op credit. Straight lines with hand placement (no Mermaid, no ELK).
- **2026-10-24 to 25:** one colour per power rail (table below). Power lines 5 px, never dashed; a candidate is faded. Line and border weights live in `style.ts`.
- **2026-10-26:** view names Overview, System, Power (ids unchanged). Link ends equally spaced and centred. Zones on the Overview and System views. Power parts on the Power view only.
- **2026-11-16:** actuator outputs follow DEC-050 and DEC-051 (F100 MAIN 1 to 8, H743 TIM5 AUX 1 to 4).
- **2026-11-19:** no PDB (DEC-054); the ESC takes its place. The F100 block stays tall (872 px) for four right-side ends.
- **2026-11-21:**
  - The drift check only reports. The Showcase uses a GLB the engineer exports. Try the buzzer-to-GPS1 layout and show screenshots first (built: Q701 under the H743, F100 moved 180 px left).
  - New pages: Open items, Checklist, Spec history, Traceability, Power budget; each look approved.
  - Power budget record rev 0.38 gets a `### Rail summary` table for the bars. Limits: 3.3 V_IMU 500 mA (TPS73533, DEC-027); 3.3 V 600 mA, the `+3V3` design current (DEC-040), not the buck IC's 2 A rating; 5 V 1000 mA (TPS2121 minimum limit, DEC-030); 6 V 10 A (UBEC continuous, PWR-011), with the 13.2 A all-stalled worst case shown above it.
  - ID chips open their site page instead of GitHub.
  - Declined: keyboard access to table rows (Tab, Enter, Space).
  - Claude may decide and build site improvements and commit and push them to `dev` without asking (engineer, later the same day). PRs to `main` still need the engineer.
- **2026-11-22:**
  - Look changes approved: light-theme contrast and the sidebar footer fade.
  - Not done: the phone header and the Overview order on a phone ("the phone not critical").
  - Features approved: "Mentioned in" revisions, gate blockers, Pinout by peripheral, Checklist owner filter.
  - Keep `log.md` as the change record ("what change, what edit").
  - For this run only: commit, push, the PR, and a merge to `main` if there are no conflicts.

| Rail or bus | Bus id | Light | Dark |
|---|---|---|---|
| Battery (6S) | `batt` | `#dc2626` | `#ef4444` |
| +6V | `v6` | `#ea580c` | `#f97316` |
| +5V (incl. `+VIN`, VBUS) | `v5` | `#ca8a04` | `#facc15` |
| +3.3V | `v3v3` | `#c026d3` | `#e879f9` |
| +3.3VA | `v3v3a` | `#4f46e5` | `#818cf8` |
| GPIO (signal) | `gpio` | `#db2777` | `#f472b6` |

## Checks

- **`npm run check`** (part of the build): spec IDs exist; no removed row is cited; every pin row is on a link or in `pinsNotOnDiagram`; every live IF row is on a link or in `ifNotOnLink`; the drawing rules.
- **`npm run drift`** (report only): hard words in block and link text (hex addresses, part numbers, pins) that the cited spec rows lack, and `open` lists naming a closed OPEN item. For DEC rows only Topic and Selected option count; history phrases ("replaces the 0x0E") are ignored.
- **`npm run test:ui`** (local Edge, about 5 to 12 minutes; bundled Chromium in CI, about 2 minutes; prints `test:ui: OK` on a pass):
  - every page (About included) loads without errors in both themes, and has no sideways scroll at 390 px;
  - diagram lines straight and labels clear (dark and light); SVG exports valid with plain colours; readable phone zoom; same-tab hash links;
  - table pages: opened-row cells top-aligned; ID chips open their site row, and a chip in a closed history row opens that row;
  - Ctrl+K: DEC-050, OPEN-023, closed OPEN-001, PWR-011, task P3-007, revision 0.10;
  - next-action task chip and Overview revision chip open their rows; one Power budget bar per Rail summary row;
  - Decisions Date cells hold their text; every page has its own tab title; the diagram view tabs fit at 390 px;
  - light-theme contrast: OPEN, DONE, ESTIMATED and NOT_VERIFIED badges and the sidebar PRELIMINARY text at least 4.5:1;
  - "Mentioned in" chips (DEC-030 to 0.21, DEC-013 to 0.10) open their Spec history rows; a blocked notes chunk shows the reload note;
  - Checklist: owner chip and `?owner=` row counts; gate blocker lists match `ids.json` and `progress.json` (OPEN-004 under P3, no closed item) and a chip opens its row; an unknown `?owner=` or `?status=` shows a pressed chip;
  - Pinout: By peripheral lists every H743 pin once and a SPI1_SCK click selects it; "Debug" and "not checked" find the same pins in both views.
- **`npm run format:check`** and **`npx knip`** pass (both failed at `b2b5b3c`).

**Verified 2026-11-22:** `npm run build`, `npm run lint` (0 errors, 6 warnings), `npm run format:check`, `npx knip` and the full `npm run test:ui` (local Edge) pass on `e90818a`. `npm run drift` 24 findings, unchanged. Earlier (2026-11-21): the CI `test:ui` run passed on `b1c0696`, the PR #58 head; the Pages deploy of `6bed2d9` succeeded. Fault injection: removing IF-001 from `b-link` fails `npm run check`; a `0x0E` magnetometer tap shows in `npm run drift`.

**Not verified:** every block and link text against the spec (`npm run drift` lists 24 unreviewed findings); SVG exports opened in Inkscape, PowerPoint or Word; the 2026-11-21 `test:ui` checks were seen passing only, never failing on a broken build. Of the 2026-11-22 checks, the contrast, "Mentioned in", owner filter, gate blocker, peripheral view, unknown chip and Pinout filter checks were also seen failing on the build before their change (`log.md`).

## Next steps

- [ ] Engineer reviews the Traceability flag lists (3 no task, 29 no decision or diagram).
- [ ] Engineer reviews the `npm run drift` list (24 findings) and decides which site texts to fix.
- [ ] Re-export the board GLB once the parts are placed.
- [ ] After the squash merge of this run's PR, merge `main` into `dev` (see Merging).
- [x] Plan B note on the Power view power mux block (DEC-108, OPEN-041), 2026-11-21.
- [x] Check and deploy the 2026-11-21 site changes (PR #58, merged 2026-11-21).

**Always:** keep `topology.ts` in step with the spec; `npm run check` flags a new IF row on no link.

**Later, when the data exists:** connector pinout pages after OPEN-023 gives the far-end pins (this also fills the Interface view `TBD`s); the BOM page (below).

**Adding a table page:** copy the Decisions page (`src/features/decisions/index.tsx`, the shortest): a route in `src/routes/_site/` with `validateSearch`, a TanStack table drawn by `RecordTable`, a sidebar item in `src/components/layout/data/sidebar-data.ts`, an Overview Explore card, a row in the About page `pages` list, and `tests/ui.ts` page-load and 390 px entries. A new record field needs an extractor change and a type in `src/data/types.ts`. A new route file needs one `npx vite build` before `tsc` knows it (the router plugin writes `routeTree.gen.ts`). Process: build, `npm run build` and `npm run test:ui` pass, screenshots at 1440 and 390 px in both themes, then commit.

## Improvement ideas

The engineer picks open ideas; nothing open is decided.

- [x] Overview cards for every page; the Open items tile links to `/open` (2026-11-21).
- [x] Power view blocks link to the Power budget (2026-11-21).
- [x] Lazy Ctrl+K menu and a `records` data chunk (2026-11-21).
- [x] `test:ui` in CI with bundled Chromium (2026-11-21).
- [x] About page (2026-11-21).
- [x] Pinout table full width; diagram fit keeps the minimap corner free (2026-11-21).
- [ ] **BOM page** (`/bom`), once the engineer exports a BOM from KiCad and commits it (a schematic output, so a human step; the site never reads `.kicad_sch`).
    - One row per part: references, quantity, value, footprint, `MFR`, `MFR.P/N`, `LCSC`, DNP (for example D105 and D106, Plan B, DEC-108). Filter by text, group and DNP.
    - The detail row links the part to its diagram blocks (part number in a block's `sub`, as the Power budget does) and to the DEC rows that name it.
    - Report-only flags: a fitted part without `MFR.P/N` or `LCSC`.
    - The extractor reads the exported file and fails the build on a missing column, like the other records. Stock and price stay off the page: supplier pages are JavaScript-rendered, so those values would be `NOT_VERIFIED`.
    - Before building: agree the export format (CSV columns) and where the file lives with the engineer.

Dropped from the list (2026-11-21), so later sessions do not propose them again: record revision drift check (`/progress-update` keeps revisions in step); a Traceability toggle for task text (fix the Req cell instead, as for CMP-010 in P1-014); re-stepped rail colours (the engineer's choice); a copy-link button (the address bar already holds `?id=`); evidence badges on more pages; a progress-over-time chart; recent decisions on the Overview (Spec history covers it); full-text search (works against the bundle-size idea); a print view.

## Known gaps

- Far-end pins and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD`.
- F100 reserved pins have no package pin numbers, so they are in a table only.
- `block_diagram.kicad_sch` still says F103 (P2-014, an engineer item). The site does not use it.
- Renders and photos on the Showcase are still placeholders.
- On a phone the pin tables scroll sideways inside their card, and wrapped Function text (NRST) makes some rows tall.
- `?id=` with an unknown ID selects nothing and shows no notice.
- Long Plan text in the F100 reserved table scrolls sideways inside the table.
- At 390 px the header page name is cut short by the search box (the phone layout is not critical, per the engineer).
