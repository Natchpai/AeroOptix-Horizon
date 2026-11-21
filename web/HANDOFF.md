# Handoff: team website

**Updated:** 2026-11-21

**Status:** live on GitHub Pages. The engineer approved the Pinout page and the Open items page look, and reviewed the Block diagram. Text is synced to spec rev 0.86 (DEC-106 actuator headers, DEC-107 no H743 battery ADC) and pin allocation rev 0.31.

Rules for content, drawing, look and checks are in `CLAUDE.md`. Commands are in `README.md`. Earlier history is in Git (`git log -- web`).

## Where things are

- **Live site:** https://natchpai.github.io/AeroOptix-Horizon/
- **Deploy:** `.github/workflows/pages.yml`, on a push to `main` that touches `web/`, the design docs or `README.md`. It can also be started by hand.
- **Merging:** `main` needs linear history, so PRs from `dev` are squash-merged. After each PR, merge `main` into `dev`.
- **What the build reads** (`scripts/extract-docs.ts`), so a merged record change updates the site:
  - the spec: every ID row, the header, and the last 5 change notes;
  - the pin allocation: H743, F100 and F100-reserved tables;
  - the checklist: `Gate summary`, task status and `Current next action`;
  - the root `README.md`: phase, revisions, key features, MCUs.
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
  - The Overview open-items card links here ("All open items" and each description). It is also a sidebar item.
- **Search:** Ctrl+K over pins, signals, blocks and spec IDs. A DEC result opens it on the Decisions page and an OPEN result on the Open items page; other IDs open their spec row on GitHub.
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
  - the Decisions and Open items pages (both themes, 390 px), and Ctrl+K on DEC-050, OPEN-023 and the closed OPEN-001.

## Verified (2026-11-21)

- `npm run build` passes, and so does `npm run test:ui` (installed Edge, Windows), with the Open items page.
- Open items page screenshots at 1440 and 390 px, dark and light; the engineer approved the look.
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

1. New pages: see "Next pages (plan, 2026-11-21)" below. Page 1 (Open items) is built; page 2 (Checklist) is next.
2. Engineer reviews the `npm run drift` list (24 findings) and decides which site texts to fix.
3. Re-export the board GLB once the parts are placed on the board.
4. Keep `topology.ts` in step with the spec. `npm run check` flags a new IF row that is on no link.
5. Optional: a note on the Power view power-mux block for the DNP Plan B diode-OR (spec 0.87, DEC-108). Do not draw the diodes, since they are not fitted.

## Next pages (plan, 2026-11-21)

The engineer asked for these pages. Page 1 is built (2026-11-21); the others are not built yet.

**Pattern for each page** (copy the Decisions page, `src/features/decisions/index.tsx`):
- route `src/routes/_site/<page>.tsx` with `validateSearch` (`q`, `id`);
- the TanStack table with the `rowText` filter, `meta.className` for phone columns, a detail row on click and a `usedOn` map;
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

1. **Open items** (`/open`), **built 2026-11-21** (see "What the site does"). Left: add checklist tasks to the opened row after page 2's extractor change.
   - All OPEN rows from `ids.json` (`kind === 'OPEN'`; fields Description, Impact, Owner / next action; `closed`). Open rows first, with a toggle to show closed rows.
   - The detail row shows the full text and "cited by": diagram blocks and links (`refs`, `open`), DEC rows whose text names the ID, and checklist tasks (after page 2's extractor change).
   - Ctrl+K: an OPEN result opens `/open?id=`, as DEC does in `src/components/command-menu.tsx`.
   - The Overview open-items card links here.
   - No extractor change.
2. **Checklist** (`/checklist`)
   - Every gate and `Pn-xxx` task: ID, Task, Req, Owner, Status, Evidence. Filter by gate and status.
   - Gate rows show the exit criterion and the stacked bar from the Overview `ProgressCard`.
   - **Extractor:** `progress.tasks` keeps only `{status, line}` today. Add `task`, `req`, `owner` and `evidence` from the task tables (header `| ID | Task | Req | Owner | Status | Evidence required / link |` under `## P<n>: ...`).
   - The Overview next-action task links go to `/checklist?id=` instead of GitHub.
3. **Traceability** (`/trace`)
   - One row per requirement ID (kinds `SYS MCU IF SEN PWR SAF FUN ENV CMP MEC PCB MFG TST`). Columns:
     - DEC rows citing it (in Topic or Selected option);
     - OPEN rows citing it;
     - checklist tasks with it in Req (after page 2);
     - diagram items with it in `refs`.
   - Flag a requirement with no task, or with no decision and no diagram item.
   - Report only: the page never fails the build.
   - Expand ranges written as "IF-030 to IF-043" (like `range()` in `topology.ts`).
4. **Spec history** (`/history`)
   - The full section 9 change-note table (revision, date, description, approved by), newest first, with search. Spec IDs in the text become `IdChip`s.
   - **Extractor:** `specChanges` keeps only the last 5 (`extract-docs.ts`, `.slice(-5)`). Add `specHistory` with every row, and keep `specChanges` for the Overview.
5. **Power budget** (`/power`)
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

## Known gaps

- Far-end pins and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD`.
- F100 reserved pins have no package pin numbers, so they are in a table only.
- `block_diagram.kicad_sch` still says F103 (P2-014, an engineer item). The site does not use it.
- The pinout table rows from pin 22 down are very tall at 1440 px (seen 2026-11-21, not changed).
- The minimap covers the right end of the Surface servo headers block at 1440 px on the System view.

## Preview

Run `npm run dev`, then open `http://localhost:5173/AeroOptix-Horizon/#/diagram?level=board`.
