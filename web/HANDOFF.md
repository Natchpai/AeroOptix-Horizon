# Handoff: team website

**Updated:** 2026-11-21

**Status:** live on GitHub Pages. Pages: Overview, Block diagram, Pinout, Decisions, Open items, Checklist, Spec history, Traceability, Power budget, Showcase. The engineer approved the Pinout page and the five pages added on 2026-11-21, and reviewed the Block diagram. Hand-written diagram text is synced to spec rev 0.86 and pin allocation rev 0.31.

Rules for content, drawing, look and checks are in `CLAUDE.md`. Commands are in `README.md`. History is in Git (`git log -- web`).

## Where things are

- **Live site:** https://natchpai.github.io/AeroOptix-Horizon/
- **Deploy:** `.github/workflows/pages.yml`, on a push to `main` that touches `web/`, the design docs or `README.md`; it can also be started by hand.
- **Merging:** `main` needs linear history, so PRs from `dev` are squash-merged. After each PR, merge `main` into `dev`.
- **What the build reads** (`scripts/extract-docs.ts`). A missing heading, table or column fails the build, and the old site stays up.
  - Spec: every ID row, the header, and every section 9 change note (`history.json`; `meta.specChanges` keeps the last 5, `meta.specRevisions` the revision and date of each for Ctrl+K).
  - Pin allocation: H743, F100 and F100-reserved tables.
  - Checklist: `Gate summary`, every task row (ID, Task, Req, Owner, Status, Evidence required / link) and `Current next action`.
  - Root `README.md`: phase, revisions, key features, MCUs.
  - Power budget (`power.json`): the section 4 `### Rail summary` table (mA; `TBD` stays empty, other text fails), the section 3 load tables and the section 4, 5 and 11 tables.
- **Hand-written:** blocks and links in `src/data/topology.ts`, positions in `src/data/places.ts`.
- **Shared code for the table pages:** `RecordTable`, `DiagramItemList`, `SiteRowList` and `TaskRowList` in `src/components/record-table.tsx`; `useScrollToRow`, `detailLabel` and `levelName` in `src/lib/record-rows.ts`; `idsIn` (range expansion) and `REQ_KINDS` in `src/lib/spec-ids.ts`; `SpecText` (ID and task chips, `labels` for evidence badges) in `src/components/spec-text.tsx`.

## How the site behaves (non-obvious parts)

- **Links between pages.** An ID chip opens its site row: DEC on Decisions, OPEN on Open items, a requirement kind on Traceability; other kinds (REF) open the spec on GitHub. A task chip opens Checklist, a revision chip Spec history. Ctrl+K results do the same. On an ID's own page the ID column chip is `plain`, so the row click opens it and the filter stays.
- **`?id=` beats filters.** On every table page a linked row shows even when a filter (or "hide closed") would hide it.
- **Revision URLs.** Revisions 0.1 and 0.10 both exist, and the router reads a typed `?rev=0.10` as the number 0.1. Site links keep the string (`?rev=%220.10%22`); `test:ui` checks it.
- **Open items** show the full description only in the opened row: OPEN-023 is about 4,600 characters.
- **Traceability** is built in the browser (`src/features/trace/matrix.ts`), report only. Flags: no task names the requirement in Req; no live DEC row and no diagram item cites it. Removed rows are never flagged. On 2026-11-21: 3 without a task (CMP-010 to CMP-012; CMP-010 is in the P1-014 task text but not its Req) and 29 without a decision or diagram item.
- **Power budget** draws one bullet bar per Rail summary row, each on its own scale; values are never recomputed. A load links to its Power view block when the block's part number is in the load name or its refs share an ID with the row's Ref. The rail colours fail the dataviz validator as a categorical set (light: 6 V against 5 V; dark: 3.3 V against 3.3 V_IMU, protan), so every bar also carries its rail name and numbers.
- **Diagram on a phone** (canvas under 640 px): a view that would fit below zoom 0.35 opens centred on its start block (FC, Main MCU or the power mux) at 0.35.
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
- **`npm run test:ui`** (local Edge, about 5 to 12 minutes; prints `test:ui: OK` on a pass):
  - every page loads without errors in both themes, and has no sideways scroll at 390 px;
  - diagram lines straight and labels clear (dark and light); SVG exports valid with plain colours; readable phone zoom; same-tab hash links;
  - table pages: opened-row cells top-aligned; ID chips open their site row, and a chip in a closed history row opens that row;
  - Ctrl+K: DEC-050, OPEN-023, closed OPEN-001, PWR-011, task P3-007, revision 0.10;
  - next-action task chip and Overview revision chip open their rows; one Power budget bar per Rail summary row.

**Verified 2026-11-21:** `npm run build` and `npm run test:ui` pass on `dev` (`43a6b0c`). Fault injection: removing IF-001 from `b-link` fails `npm run check`; a `0x0E` magnetometer tap shows in `npm run drift`.

**Not verified:** every block and link text against the spec (`npm run drift` lists 24 unreviewed findings); SVG exports opened in Inkscape, PowerPoint or Word; the newer `test:ui` checks were seen passing only, never failing on a broken build.

## Next steps

1. Engineer reviews the Traceability flag lists (3 no task, 29 no decision or diagram).
2. Engineer reviews the `npm run drift` list (24 findings) and decides which site texts to fix.
3. Update `README.md` in `web/`: its data table and browser-check list predate the five new pages (`history.json`, `power.json`, task fields, the new tests).
4. Re-export the board GLB once the parts are placed.
5. Keep `topology.ts` in step with the spec; `npm run check` flags a new IF row on no link.
6. Optional: a note on the Power view power-mux block for the DNP Plan B diode-OR (spec 0.87, DEC-108). Do not draw the diodes; they are not fitted.

**Later, when the data exists:** connector pinout pages after OPEN-023 gives the far-end pins (this also fills the Interface view `TBD`s); the BOM page (idea 15).

**Adding a table page:** copy the Decisions page (`src/features/decisions/index.tsx`, the shortest): a route in `src/routes/_site/` with `validateSearch`, a TanStack table drawn by `RecordTable`, a sidebar item in `src/components/layout/data/sidebar-data.ts`, and `tests/ui.ts` page-load and 390 px entries. A new record field needs an extractor change and a type in `src/data/types.ts`. Process: build, `npm run build` and `npm run test:ui` pass, screenshots at 1440 and 390 px in both themes, the engineer approves the look, then each Git step with its own approval.

## Improvement ideas (proposed 2026-11-21, not approved)

The engineer picks; nothing here is decided.

1. **Overview cards for the new pages.** The Explore grid shows six cards; Open items, Checklist, Traceability and Power budget are only in the sidebar. The Open items stat tile could link to `/open`.
2. **Power view to the Power budget.** The Power view rail and regulator blocks could link to `/power`.
3. **Record revision drift (report only).** The checklist names the spec revision it follows ("Requirements authority: ... rev 0.87"), and the spec and power budget cite each other's revisions. A check could list records that point to an older revision than the one the site reads.
4. **Traceability rule option.** A toggle to count task text, not only Req.
5. **Run `test:ui` in CI** with Playwright's bundled Chromium instead of the local Edge.
6. **Rail colours.** A re-stepped set that passes the validator would help the Power view. The engineer picked these colours, so any change is theirs.
7. **Bundle size.** The `search-provider` chunk is about 593 kB (Vite warns). Loading the Ctrl+K index on first open would speed up the first page load.
8. **Copy link** button in each opened row.
9. **Evidence badges elsewhere** (`SpecText labels`): the Checklist evidence column and the Decisions notes.
10. **About page** for new team members: how to read the site (phases, evidence labels, ID kinds, which record each page reads, what `TBD` means).
11. **Progress over time.** Plot the DONE task count per gate from the checklist's Git history at build time. CI would need `fetch-depth: 0` in the checkout.
12. **Recent decisions on the Overview.** DEC rows carry a Date; a card could list the ones from the last 7 days or since the previous spec revision.
13. **Full-text search.** Ctrl+K matches IDs and titles only; descriptions and notes could join a lazy-loaded index (see idea 7).
14. **Print view** for Decisions, Open items and Checklist (print CSS, rows expanded) for team meetings.
15. **BOM page** (`/bom`), once the engineer exports a BOM from KiCad and commits it (a schematic output, so a human step; the site never reads `.kicad_sch`).
    - One row per part: references, quantity, value, footprint, `MFR`, `MFR.P/N`, `LCSC`, DNP (for example D105 and D106, Plan B, DEC-108). Filter by text, group and DNP.
    - The detail row links the part to its diagram blocks (part number in a block's `sub`, as the Power budget does) and to the DEC rows that name it.
    - Report-only flags: a fitted part without `MFR.P/N` or `LCSC`.
    - The extractor reads the exported file and fails the build on a missing column, like the other records. Stock and price stay off the page: supplier pages are JavaScript-rendered, so those values would be `NOT_VERIFIED`.
    - Before building: agree the export format (CSV columns) and where the file lives with the engineer.

## Known gaps

- Far-end pins and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD`.
- F100 reserved pins have no package pin numbers, so they are in a table only.
- `block_diagram.kicad_sch` still says F103 (P2-014, an engineer item). The site does not use it.
- The pinout table rows from pin 22 down are very tall at 1440 px.
- The minimap covers the right end of the Surface servo headers block at 1440 px on the System view.
- Renders and photos on the Showcase are still placeholders.
