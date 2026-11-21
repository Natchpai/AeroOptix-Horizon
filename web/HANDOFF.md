# Handoff: team website

**Updated:** 2026-11-21

**Status:** live on GitHub Pages. The engineer approved the Pinout page and reviewed the Block diagram. Text is synced to spec rev 0.83.

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
- **Search:** Ctrl+K over pins, signals, blocks and spec IDs. A DEC result opens it on the Decisions page; other IDs open their spec row on GitHub.
- **SVG export:** on each diagram view and each package card. The export uses native SVG with hex colours, plus a footer with the spec revision, the phase, "not for fabrication" and the date.
- **Showcase:** placeholder.

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
  - the Decisions page (both themes, 390 px) and Ctrl+K on a DEC ID.

## Verified (2026-11-21)

- `npm run build` passes, and so does `npm run test:ui` (installed Edge, Windows).
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

1. Engineer reviews the `npm run drift` list and decides which site texts to fix.
2. Buzzer-to-GPS1 line (Batch 3) and Showcase 3D viewer (Batch 4), per the plan of 2026-11-21.
3. Keep `topology.ts` in step with the spec. `npm run check` now flags a new IF row that is on no link.

## Known gaps

- Far-end pins and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD`.
- F100 reserved pins have no package pin numbers, so they are in a table only.
- `block_diagram.kicad_sch` still says F103 (P2-014, an engineer item). The site does not use it.
- The pinout table rows from pin 22 down are very tall at 1440 px (seen 2026-11-21, not changed).
- The minimap covers the right end of the Surface servo headers block at 1440 px on the System view.

## Preview

Run `npm run dev`, then open `http://localhost:5173/AeroOptix-Horizon/#/diagram?level=board`.
