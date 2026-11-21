# Handoff: team website

**Updated:** 2026-11-21

**Status:** live on GitHub Pages. The engineer approved the Pinout page and the Open items, Checklist, Spec history, Traceability and Power budget page looks, and reviewed the Block diagram. Text is synced to spec rev 0.86 (DEC-106 actuator headers, DEC-107 no H743 battery ADC) and pin allocation rev 0.31.

Rules for content, drawing, look and checks are in `CLAUDE.md`. Commands are in `README.md`. Earlier history is in Git (`git log -- web`).

## Where things are

- **Live site:** https://natchpai.github.io/AeroOptix-Horizon/
- **Deploy:** `.github/workflows/pages.yml`, on a push to `main` that touches `web/`, the design docs or `README.md`. It can also be started by hand.
- **Merging:** `main` needs linear history, so PRs from `dev` are squash-merged. After each PR, merge `main` into `dev`.
- **What the build reads** (`scripts/extract-docs.ts`), so a merged record change updates the site:
  - the spec: every ID row, the header, and every change note (`history.json`; the Overview shows the last 5);
  - the pin allocation: H743, F100 and F100-reserved tables;
  - the checklist: `Gate summary`, every task row (ID, Task, Req, Owner, Status, Evidence) and `Current next action`. A task table without one of those columns fails the build;
  - the root `README.md`: phase, revisions, key features, MCUs;
  - the power budget (`power.json`): the section 4 `### Rail summary` table (numbers in mA; `TBD` stays empty, any other text fails the build), the section 3 load tables, and the section 4, 5 and 11 tables.
  - A missing heading or table fails the build, and the old site stays up.
- **Hand-written:** blocks and links in `src/data/topology.ts`, and positions in `src/data/places.ts`.

## What the site does

- **Overview:** phase, revisions, key features and open OPEN items. Also gate progress (stacked bars), the checklist next action, the last 5 spec change notes and a build stamp.
- **Block diagram:**
  - **Overview** (L0, id `system`): the PCB as one In board zone with its ports, and Out board zones for power and ESC, devices and actuators.
  - **System** (L1, id `board`): the blocks inside the board, in zones (Connectors, USB and debug, On-board I/O). I2C2 is drawn as a bus bar.
    - The buzzer driver (Q701) sits under the H743, right of the F100, outside the zones. It has `TIM3_CH3` from the H743 bottom and `BUZZER-, pin 9` to GPS1, which is the middle of GPS1's three left ends (796, 916, 1036).
    - The F100 moved 180 px left for this (x 380).
  - **Power** (L1, id `power`): source to load, left to right. A candidate feed is faded.
  - **Interface** (L2): click a link label to see each signal with its MCU pin. The far end shows `TBD`.
  - Click a block for its detail panel.
  - On a phone (canvas under 640 px), a view that would fit below zoom 0.35 opens centred on its start block at 0.35: FC, Main MCU, or the power mux.
- **Pinout:** LQFP100 and LQFP48 package views and pin tables. A pin links to its diagram link.
- **Decisions:** every `DEC-xxx` row of the spec in a sortable, filterable table (`?q=` filter, `?id=DEC-xxx` opens a row).
  - A row shows the ID, topic, decision (clamped), date and how many diagram items cite it.
  - Click a row for the full decision, the notes, the spec line and links to the diagram blocks and links that cite it.
  - On a phone only ID and topic show; the decision and date move into the opened row.
  - It is also an Overview card and a sidebar item.
- **Open items** (`/open`): every `OPEN-xxx` row of the spec. Open rows first; **Show closed** adds the closed ones (`?closed=true`). `?q=` filters, `?id=OPEN-xxx` opens a row, and a closed `id` shows even with closed rows hidden.
  - A row shows the ID, description and owner (both clamped to 2 lines) and how many diagram items cite it. On a phone only ID and description show.
  - The opened row, full width, shows the full description, owner, impact, spec line, the diagram blocks and links that cite it, the DEC rows whose text names it (links to the Decisions page) and other spec rows that name it.
  - The full text is not shown in the table cell: OPEN-023 is about 4,600 characters and made the row too tall.
  - The opened row also lists checklist tasks: the ones the item names (usually its owner column) and the ones whose text names the item.
  - The Overview open-items card links here ("All open items" and each description). It is also a sidebar item.
- **Checklist** (`/checklist`): every gate and `Pn-xxx` task of the execution checklist.
  - A Gates card shows each gate's name, status, the stacked bar, the exit criterion and the note. Click a gate to filter the tasks (`?gate=P3`).
  - The task table filters by gate, by status (`?status=OPEN`, with counts) and by text (`?q=`). `?id=P3-007` opens a row, even when a filter hides it.
  - Columns: ID, Task, Req (wide screens), Owner, Status. On a phone the status shows as a dot before the ID.
  - The opened row shows the task, Req, owner and status, evidence (spec IDs and task IDs as chips), the checklist line and the open items that name the task.
  - Task chips (`src/components/task-status.tsx`, shared with the Overview) open `/checklist?id=`: the Overview next action and the gate IDs in the Progress card link here, not to GitHub.
- **Spec history** (`/history`): the whole section 9 change-note table (`history.json`), newest first, with a text filter (`?q=`).
  - Rows show revision, date, the note (clamped to 3 lines) and who approved it. Spec IDs and task IDs in the note are chips. Click a row to open it in place, with a link to its spec line; in a closed row a chip click opens the row.
  - `?rev=` opens a revision even when the filter hides it. Revisions 0.1 and 0.10 both exist, and the router reads a typed `?rev=0.10` as the number 0.1. Site links keep the string (`?rev=%220.10%22`), and `test:ui` checks that 0.10 opens 0.10.
  - The Overview "Recent spec changes" card links here ("Full history" and each revision chip).
- **Traceability** (`/trace`): one row per requirement ID (kinds `SYS MCU IF SEN PWR SAF FUN ENV CMP MEC PCB MFG TST`, 109 rows, 6 removed), built in the browser from `ids.json`, `progress.json` and `topology.ts` (`src/features/trace/matrix.ts`). No extractor change.
  - Counts per row: DEC rows that name it in Topic or Selected option, OPEN rows that name it anywhere, checklist tasks with it in Req, and diagram items with it in `refs`. Ranges such as "IF-030 to IF-043" count for every existing ID in them.
  - Flags (report only, never a build failure): **No task** (no task Req names it) and **No decision or diagram** (no live DEC row and no diagram item). Removed rows are never flagged. On 2026-11-21: 3 without a task (CMP-010 to CMP-012; CMP-010 is in the P1-014 task text but not its Req) and 29 without a decision or diagram item.
  - Filters: kind (`?kind=PWR`), flag (`?flag=task` or `?flag=link`; the summary cards also toggle it), text (`?q=`); `?id=IF-010` opens a row even when a filter hides it.
  - The opened row shows every field of the requirement, its spec line, and the decisions, open items, tasks and diagram items, each linking to its page.
- **Power budget** (`/power`): from `AO-HORIZON_POWER_BUDGET_EN.md`, values as written with their evidence labels, never recomputed.
  - **Rail load against limit:** one bullet bar per Rail summary row, each on its own scale (small multiples, no shared axis): typical solid, worst case lighter, limit a tick. Hover for values; a "Table view" repeats the numbers. A worst case above the limit shows an icon and text (6 V: 13,200 against 10,000 mA).
  - The Rail summary table was added to the record by the engineer's approval (power budget rev 0.38, 2026-11-21). Limits: 3.3 V_IMU 500 mA (TPS73533), 3.3 V 600 mA (`+3V3` design current, DEC-040; the buck IC's 2 A is not the limit, engineer), 5 V 1000 mA (TPS2121 minimum limit), 6 V 10,000 mA (UBEC continuous).
  - Bar colours are the rail colours. The dataviz validator fails them as a categorical palette (light: 6 V against 5 V; dark: 3.3 V against 3.3 V_IMU for protan), so the page never relies on colour: every bar has its rail name, and the numbers are written under it.
  - Sections 3 (loads per rail), 4 (totals), 5 (tolerances) and 11 (thermal) as tables. Evidence labels show as coloured badges with the word (`SpecText labels`). A load links to its Power view block when the block's part number is in the load name or its refs share a spec ID with the row's Ref.
- **ID chips** (`src/components/id-chip.tsx`): a DEC chip opens its row on Decisions, OPEN on Open items, a requirement on Traceability; other kinds (REF ...) open their spec row on GitHub. Each site page links the spec line in its detail row. In the ID column of an ID's own page the chip is `plain` (no link), so the row click opens it and the filter stays. `REQ_KINDS` lives in `src/lib/spec-ids.ts`.
- **Search:** Ctrl+K over pins, signals, blocks, spec IDs (DEC, OPEN and every requirement kind), checklist tasks and spec revisions. Each result opens its site row: DEC on Decisions, OPEN on Open items, requirements on Traceability, tasks on Checklist, revisions on Spec history. Revisions come from `meta.specRevisions` (revision and date only), so the search bundle does not carry the full history.
- **SVG export:** on each diagram view and each package card. The export uses native SVG with hex colours, plus a footer with the spec revision, the phase, "not for fabrication" and the date.
- **Showcase:** a 3D board viewer (`@google/model-viewer` 4.4.0 with `three` 0.183.x), loaded only on this page. It shows `web/public/models/ao-horizon.glb` with its board revision, export date (last commit of the file), KiCad version, size, a "not for fabrication" tag and a GLB download. Without the file the page says "No board model yet".
  - **Lighting:** the KiCad GLB sets only a base colour per material, so glTF reads every material as rough metal and the board looks grey and flat. On load, `fixMaterials()` sorts materials by colour (solder mask, silkscreen, gold, tin, plastic) and sets metallic and roughness. Lighting is the `legacy` environment with `neutral` tone mapping, exposure 1 and full shadow, picked from screenshots on 2026-11-21.
  - **Re-export (manual):** the engineer runs this after layout changes, because it is a PCB output, then commits the GLB:
    `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb export glb --subst-models --include-silkscreen --include-soldermask -o web/public/models/ao-horizon.glb hardware/AO-Horizon/AO-Horizon.kicad_pcb`
  - The first export (2026-11-21, 8.1 MB) came from an uncommitted PCB with many parts not yet placed on the board.
  - Renders and photos are still placeholders.

## Engineer decisions

- **2026-10-24:**
  - GitHub Pages; the site is public with the repo.
  - shadcn-admin template.
  - Dark theme with nP blue and navy.
  - The AeroOptix flame is the main logo, and nP is a small co-op credit.
  - Straight lines with hand placement (no Mermaid, no ELK).
  - Pinout page OK as it is.
- **2026-10-24 to 25:**
  - One colour per power rail (table below).
  - Power lines 5 px, never dashed; a candidate is faded.
  - Line and border weights are in `style.ts`.
- **2026-10-26:**
  - View names: Overview, System, Power. Only the labels changed, the ids did not.
  - Link ends are equally spaced and centred.
  - Zones on the Overview and the System view.
  - Power parts are shown on the Power view only.
- **2026-11-16:**
  - Actuator outputs follow DEC-050 and DEC-051: F100 MAIN 1 to 8, H743 TIM5 AUX 1 to 4.
- **2026-11-19:**
  - No PDB (DEC-054): the ESC takes its place.
  - The F100 block stays tall (872 px) to fit four right-side ends.
- **2026-11-21:**
  - The drift check only reports.
  - The Showcase uses a GLB the engineer exports.
  - Try the buzzer-to-GPS1 layout (F100 shift) and show screenshots first.

| Rail or bus | Bus id | Light | Dark |
|---|---|---|---|
| Battery (6S) | `batt` | `#dc2626` | `#ef4444` |
| +6V | `v6` | `#ea580c` | `#f97316` |
| +5V (incl. `+VIN`, VBUS) | `v5` | `#ca8a04` | `#facc15` |
| +3.3V | `v3v3` | `#c026d3` | `#e879f9` |
| +3.3VA | `v3v3a` | `#4f46e5` | `#818cf8` |
| GPIO (signal) | `gpio` | `#db2777` | `#f472b6` |

## Checks

- **`npm run check`** (part of the build) covers:
  - spec IDs exist;
  - no removed rows are used as refs on blocks or links;
  - every pin row is on a link or in `pinsNotOnDiagram`;
  - every live IF row is on a link or in `ifNotOnLink`;
  - the drawing rules.
- **`npm run drift`** (report only) lists hard words in block and link text (hex addresses, part numbers, pins) that the cited spec rows do not contain, and `open` lists that name a closed OPEN item.
  - For DEC rows, only Topic and Selected option count.
  - History phrases ("replaces the 0x0E") are ignored.
- **`npm run test:ui`** (local, Edge, about 4 minutes) covers:
  - page errors in both themes;
  - straight lines and clear labels in dark and light;
  - SVG export;
  - no sideways scroll at 390 px in both themes;
  - a readable phone zoom;
  - same-tab hash links;
  - the Decisions, Open items, Checklist, Spec history, Traceability and Power budget pages (both themes, 390 px), one Power budget bar per Rail summary row, top-aligned cells in an opened row, ID chips opening their site row (and a chip in a closed history row opening that row), Ctrl+K on DEC-050, OPEN-023, the closed OPEN-001, PWR-011, task P3-007 and revision 0.10, a next-action task chip opening its Checklist row, and an Overview revision chip (and `0.10`) opening its Spec history row.

## Verified (2026-11-21)

- `npm run build` passes, and so does `npm run test:ui` (installed Edge, Windows), with the Open items page.
- Open items page screenshots at 1440 and 390 px, dark and light; the engineer approved the look.
- Checklist page: `npm run build` and `npm run test:ui` pass; screenshots at 1440 and 390 px, dark and light; the engineer approved the look.
- Spec history page: `npm run build` and `npm run test:ui` pass; screenshots at 1440 and 390 px, dark and light; the engineer approved the look.
- Traceability page: `npm run build` and `npm run test:ui` pass; screenshots at 1440 and 390 px, dark and light; the engineer approved the look. The no-task list was cross-checked by hand against the checklist Req cells.
- Power budget page: `npm run build` and `npm run test:ui` pass; screenshots at 1440 and 390 px, dark and light; the engineer approved the look.
- **Fault injection:**
  - Removing IF-001 from `b-link` makes `npm run check` fail on IF-001.
  - Setting the magnetometer tap to `0x0E` makes `npm run drift` list it.
- **390 px first-load zoom:** it was 0.15 to 0.17 (Power was clipped). It is now 0.35 on all three views. Screenshots were checked.
- Light theme was checked by screenshot on the Pinout page and the System view at 1440 px.

## Not verified

- Every block and link text against the spec. `npm run drift` gives leads only; its current list (24 findings) is not yet reviewed.
- SVG exports opened in Inkscape, PowerPoint or Word.
- The new phone-zoom and same-tab checks were not shown failing on a broken build. Only their passing run was seen.

## Next steps

1. New pages: see "Next pages (plan, 2026-11-21)" below. All five pages are built: Open items, Checklist, Spec history, Traceability and Power budget. The Traceability flag lists may still need the engineer's review. Then: "Later, when the data exists".
2. Engineer reviews the `npm run drift` list (24 findings) and decides which site texts to fix.
3. Re-export the board GLB once the parts are placed on the board.
4. Keep `topology.ts` in step with the spec. `npm run check` flags a new IF row that is on no link.
5. Optional: a note on the Power view power-mux block for the DNP Plan B diode-OR (spec 0.87, DEC-108). Do not draw the diodes, since they are not fitted.

## Next pages (plan, 2026-11-21)

The engineer asked for these pages. All five pages are built (2026-11-21).

**Pattern for each page** (see the Decisions page, `src/features/decisions/index.tsx`, the shortest one):
- route `src/routes/_site/<page>.tsx` with `validateSearch` (`q`, `id`);
- the TanStack table with the `rowText` filter and `meta.className` for phone columns, drawn by `RecordTable` (`src/components/record-table.tsx`: rows, detail row, empty text); `useScrollToRow`, `detailLabel` and `levelName` from `src/lib/record-rows.ts`;
- detail lists from the same file: `DiagramItemList`, `SiteRowList` (DEC and OPEN rows linking to their site page) and `TaskRowList`;
- `IdChip` and `MdText`;
- a sidebar item in `src/components/layout/data/sidebar-data.ts`;
- `tests/ui.ts` page-load and 390 px entries in both themes.

Data comes from `src/data/generated/*.json`, written by `scripts/extract-docs.ts`. A new field needs an extractor change and a type in `src/data/types.ts`.

**Process for each page:** one batch:
- build the page;
- `npm run build` and `npm run test:ui` pass;
- screenshots at 1440 and 390 px, dark and light;
- the engineer approves the look;
- commit on `dev`, PR to `main`, and after the squash merge `main` into `dev`, each Git step with its own approval.

Order: 1 and 2 first (cheap, most asked), then 4, 3, 5.

1. **Open items** (`/open`), **built 2026-11-21** (see "What the site does").
   - All OPEN rows from `ids.json` (`kind === 'OPEN'`; fields Description, Impact, Owner / next action; `closed`). Open rows first, with a toggle to show closed rows.
   - The detail row shows the full text and "cited by": diagram blocks and links (`refs`, `open`), DEC rows whose text names the ID, and checklist tasks (after page 2's extractor change).
   - Ctrl+K: an OPEN result opens `/open?id=`, as DEC does in `src/components/command-menu.tsx`.
   - The Overview open-items card links here.
   - No extractor change.
2. **Checklist** (`/checklist`), **built 2026-11-21** (see "What the site does"). Not done: Ctrl+K over task IDs.
   - Every gate and `Pn-xxx` task: ID, Task, Req, Owner, Status, Evidence. Filter by gate and status.
   - Gate rows show the exit criterion and the stacked bar from the Overview `ProgressCard`.
   - **Extractor:** `progress.tasks` keeps only `{status, line}` today. Add `task`, `req`, `owner` and `evidence` from the task tables (header `| ID | Task | Req | Owner | Status | Evidence required / link |` under `## P<n>: ...`).
   - The Overview next-action task links go to `/checklist?id=` instead of GitHub.
3. **Traceability** (`/trace`), **built 2026-11-21** (see "What the site does").
   - One row per requirement ID (kinds `SYS MCU IF SEN PWR SAF FUN ENV CMP MEC PCB MFG TST`). Columns:
     - DEC rows citing it (in Topic or Selected option);
     - OPEN rows citing it;
     - checklist tasks with it in Req (after page 2);
     - diagram items with it in `refs`.
   - Flag a requirement with no task, or with no decision and no diagram item.
   - Report only: the page never fails the build.
   - Expand ranges written as "IF-030 to IF-043" (like `range()` in `topology.ts`).
4. **Spec history** (`/history`), **built 2026-11-21** (see "What the site does").
   - The full section 9 change-note table (revision, date, description, approved by), newest first, with search. Spec IDs in the text become `IdChip`s.
   - **Extractor:** `specChanges` keeps only the last 5 (`extract-docs.ts`, `.slice(-5)`). Add `specHistory` with every row, and keep `specChanges` for the Overview.
5. **Power budget** (`/power`), **built 2026-11-21** (see "What the site does").
   - From `AO-HORIZON_POWER_BUDGET_EN.md`:
     - section 3 load tables per rail (3.3 V_IMU, 3.3 V, 5 V, 6 V servo);
     - section 4 totals;
     - section 5 rail tolerances;
     - section 11 thermal margin.
   - A bar per rail of load against the regulator limit. Use the `dataviz` skill and the `--rail-*` colours in `src/styles/theme.css`.
   - Each load links to its Power view block.
   - **Extractor:** a new `power.json`. Values keep the record's evidence labels (`ESTIMATED`, `VERIFIED`, `NOT_VERIFIED`) and are never recomputed in the site.
   - Read the record's table headers first. The extractor must throw on a missing table, like the other records.

Later, when the data exists:
- **Connector pinout pages**, after OPEN-023 gives the far-end pins. This also fills the Interface view `TBD`s.
- **BOM page**, from a BOM file the engineer exports.

## Improvement ideas (proposed 2026-11-21, not approved)

Claude's list after building the five pages. The engineer picks; nothing here is decided. Rough order: cheap fixes first.

Declined by the engineer (2026-11-21): keyboard access to table rows (Tab, Enter, Space on the row).

Done 2026-11-21: top-aligned cells in opened rows on all five table pages (`test:ui` checks it); one shared table and detail lists (`RecordTable` and friends; the five pages went from about 2,040 to 1,570 lines plus 270 shared, no visible change except DEC and OPEN IDs in detail lists now share one width); ID chips open their site page (DEC, OPEN, requirements), approved by the engineer ("do next"); Ctrl+K over tasks, revisions and every requirement kind.

**Linking (the site now has a page for most IDs):**
1. **Overview cards for the new pages.** The Explore grid shows six cards; Open items, Checklist, Traceability and Power budget are only in the sidebar. The Open items stat tile could link to `/open`.
2. **Power view to the Power budget.** Diagram panel spec IDs already open the site pages (with the chip change); the Power view rail and regulator blocks could also link to `/power`.

**Checks (report only, like `npm run drift`):**
3. **Record revision drift.** The checklist header names the spec revision it follows ("Requirements authority: ... rev 0.87"), and the spec and power budget cite each other's revisions. A check could list records that point to an older revision than the one the site reads.
4. **Traceability rule option.** A toggle to count task text, not only Req (CMP-010 is in the P1-014 text but not its Req).
5. **Run `test:ui` in CI** with Playwright's bundled Chromium instead of the local Edge, so a PR shows the browser checks.

**Look and speed:**
6. **Rail colours.** The dataviz validator fails the rail colours as a categorical set (light: 6 V against 5 V; dark: 3.3 V against 3.3 V_IMU for protan vision). The pages never rely on colour alone, but a re-stepped set would help the Power view. The engineer picked these colours, so any change is theirs.
7. **Bundle size.** The `search-provider` chunk is about 593 kB (545 kB before tasks joined the search index) (Vite warns). Loading the Ctrl+K index on first open would speed up the first page load.
8. **Copy link** button in each opened row, since `?id=` links are the main way to share a row.
9. **Evidence badges elsewhere.** `SpecText labels` colours `VERIFIED` and the other labels; the Checklist evidence column and the Decisions notes could use it too.

## Known gaps

- Far-end pins and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD`.
- F100 reserved pins have no package pin numbers, so they are in a table only.
- `block_diagram.kicad_sch` still says F103 (P2-014, an engineer item). The site does not use it.
- The pinout table rows from pin 22 down are very tall at 1440 px (seen 2026-11-21, not changed).
- The minimap covers the right end of the Surface servo headers block at 1440 px on the System view.

## Preview

Run `npm run dev`, then open `http://localhost:5173/AeroOptix-Horizon/#/diagram?level=board`.
