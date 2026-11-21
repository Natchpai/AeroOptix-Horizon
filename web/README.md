# AO-Horizon team website

Static site for the team. Pages: Overview, About this site, Block diagram (three views), Pinout (as a table or by peripheral), Decisions, Open items, Checklist (filter by gate, state and owner), Spec history, Traceability, Power budget and Showcase (the board 3D model; renders and photos come later).

The design records in `hardware/AO-Horizon/documents/design/` stay the source of truth. The site reads them at build time and adds no values of its own.

## Run

Node 24 and npm.

```sh
cd web
npm ci
npm run dev      # http://localhost:5173/AeroOptix-Horizon/
npm run build    # extract + check + type-check + build to dist/
npm run preview  # serve dist/ under /AeroOptix-Horizon/
npm run test:ui  # browser checks on dist/, after build (also in CI)
npm run drift    # report only: site text that may have drifted from the spec
```

`npm run check` re-reads the docs and checks the hand-written data on its own.

## Where the data comes from

| Data                                                           | Source                                 | How                                                                                                                                                                                                                                                          |
| -------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Spec IDs (IF, DEC, OPEN, SEN, PWR ...)                         | `AO-HORIZON_SPEC_EN.md`                | `scripts/extract-docs.ts`, every table row whose first cell is an ID                                                                                                                                                                                         |
| MCU pins                                                       | `AO-HORIZON_PIN_ALLOCATION_EN.md`      | same script, the H743, F100 and F100-reserved tables; a row with Signal `-` (a pin whose function was removed, such as PC0 and PC1 by DEC-107) is skipped, so the pin shows as free                                                                          |
| Spec change notes                                              | `AO-HORIZON_SPEC_EN.md` section 9      | same script: every note to `history.json` (Spec history page); the last 5 and the revision and date of each note go to `meta.json` (Overview, Ctrl+K)                                                                                                        |
| Phase, board and spec revision, key features, MCU part numbers | root `README.md`                       | same script, `Specifications` table for the MCUs                                                                                                                                                                                                             |
| Gates, tasks and current next action                           | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | same script: `Gate summary` table; every `P<n>-<nnn>` task row with its Task, Req, Owner, Status and `Evidence required / link` cells (a missing column fails the build); `Current next action` paragraph                                                    |
| Power budget                                                   | `AO-HORIZON_POWER_BUDGET_EN.md`        | same script, to `power.json`: the section 4 `### Rail summary` table (Rail, Typical load, Worst-case load, Limit in mA, Limit from, Label; `TBD` stays empty, other text fails the build), the four section 3 load tables and the section 4, 5 and 11 tables |
| Board model (Showcase)                                         | `public/models/ao-horizon.glb`         | exported by the engineer with `kicad-cli pcb export glb` (see `HANDOFF.md`); the script stores its size and last commit date                                                                                                                                 |
| Build stamp (commit, date)                                     | Git                                    | same script: `GITHUB_SHA` in CI, `git rev-parse HEAD` locally                                                                                                                                                                                                |
| Blocks and links                                               | `src/data/topology.ts`                 | hand-written; every block and link names its spec IDs                                                                                                                                                                                                        |
| Block positions                                                | `src/data/places.ts`                   | hand-written drawing data                                                                                                                                                                                                                                    |
| Traceability                                                   | the data above                         | built in the browser (`src/features/trace/matrix.ts`), not by the script: one row per requirement ID with the DEC, OPEN, task (Req cell) and diagram items that cite it                                                                                      |

The extracted JSON (`meta`, `ids`, `pins`, `progress`, `history`, `power`) goes to `src/data/generated/`. It is git-ignored and rebuilt on every `dev` and `build`. `meta`, `ids`, `pins` and `progress` are read by every page, so `vite.config.ts` bundles them into one `records` chunk that caches apart from the code; `history` and `power` load with their own pages. The script throws when a table or heading it needs is missing, so a record that changes shape fails the build instead of showing `TBD`.

## Checks (`scripts/check-data.ts`)

The build fails when:

- a spec ID in the topology is not in the spec, or a block or link cites a removed row
- a pin row is used by no link (rows that are not drawn are listed in `pinsNotOnDiagram` with a reason)
- a live IF row in the spec is on no link (rows that are not drawn are listed in `ifNotOnLink` with a reason), or an `ifNotOnLink` entry is unknown, removed or on a link
- a pin or package pin number is assigned twice
- a block has no position, or two blocks are closer than 24 px
- a link is not one straight line, runs through another block, or crosses another link
- the link ends on one side of a block are not equally spaced, or not centred on that side
- a zone lists an unknown block, holds a block it does not list, or comes within 24 px of another zone

## Drift report (`scripts/drift.ts`)

`npm run drift` never fails. It lists two kinds of finding:

- hard words in block and link text (hex addresses, part numbers, pin and peripheral names) that are in none of the spec rows the item cites
- items whose `open` list names a closed OPEN item

For a DEC row only Topic and Selected option count, and history phrases such as "replaces the 0x0E" are ignored. A finding is a lead: check the spec row, then fix the text by hand.

## Browser checks (`tests/ui.ts`)

`npm run test:ui` serves `dist/` and opens it through `playwright-core`: in the installed Microsoft Edge locally (no browser download), in Playwright's bundled Chromium when `CI` is set. `UI_BROWSER` overrides the channel (for example `UI_BROWSER=chrome`). It lists every failure and exits 1 when:

- a page throws an error, in dark or light: every page, plus linked rows (`?id=`), filters and an Interface view
- a drawn line is not straight on screen, in dark or light
- a link label covers a block, another label or another line: with no block selected, with blocks selected in turn, and in light theme
- an SVG export (3 diagram views and both pinouts, dark and light) is not valid XML, or still holds CSS (`var(`, `color-mix`, `oklab`, `class=`)
- a page scrolls sideways at 390 px (dark and light), or a diagram view opens there below zoom 0.35
- a hash link changed in an open tab (as when a URL is pasted) does not show the new view, block selection or pin
- a Ctrl+K result does not open its row: DEC-050 (Decisions), OPEN-023 and closed OPEN-001 (Open items), PWR-011 (Traceability), task P3-007 (Checklist), revision 0.10 (Spec history, not 0.1)
- an ID chip does not open its site row, or a chip in a closed history row does not open that row
- the next-action task chip or the Overview revision chip does not open its row
- an opened table row has cells that are not top-aligned
- the Power budget page does not draw one bar per Rail summary row
- a Decisions Date cell is wider than its cell, two pages share a tab title, or the diagram view tabs do not fit at 390 px
- a light-theme badge (OPEN, DONE, ESTIMATED, NOT_VERIFIED) or the sidebar PRELIMINARY text is below 4.5:1 contrast
- a "Mentioned in" chip does not open its revision (DEC-030 to 0.21, DEC-013 to 0.10), or a failed notes load does not show the reload note
- the Checklist owner filter shows the wrong row count, a gate blocker list differs from the records or lists a closed item, or an unknown `?owner=` or `?status=` shows no pressed chip
- the Pinout By peripheral view does not list every H743 pin once or select a clicked pin, or the filter finds different pins in Table and By peripheral

It takes about 5 to 12 minutes locally (about 2 minutes in CI) and prints `test:ui: OK` on a pass. `.github/workflows/web-test.yml` runs it on pushes to `dev` and PRs to `main` that touch `web/`, the design records or the root `README.md`, and by hand. Google Fonts are fetched once per run and then served from memory. If they cannot be fetched, the run warns that label checks used fallback fonts.

## Editing the diagram

- Line widths, block border, corner radius, end dots, dashes and label box sizes are in `src/features/diagram/style.ts`. The canvas, the SVG export and the legend all read them from there.
- Colours are tokens in `src/styles/theme.css` (`--rail-*`, `--bus-*`).

- New link or block: add it to `topology.ts` with its spec IDs, then give each new block a place in `places.ts`.
- Views: id `system` is shown as Overview (L0), id `board` as System (L1), id `power` as Power. The Power view (ids `pw-*`) holds every power part and runs left to right: source, input, protection, +5V bar, converters, +3V3 bar, loads. The System (L1) view has no power parts. A power change in the spec goes into the Power view, and into the Overview (L0) when it touches the battery chain.
- Link ends on one side of a block are spaced equally and centred on that side; a `bundles` group in `places.ts` counts as one end. `npm run check` names the block and side that break it.
- Zones: `zones` in `places.ts` lists the blocks of each titled box (System view: Connectors, USB and debug, On-board I/O; Overview: one In board (PCB) zone with the FC and its ports, out-board power, devices and actuators). The box is sized to fit them. Connectors (kind `connector`) draw a tab on the cable side; on-board parts with no cable are kind `io`.
- A shared bus (kind `bus`, such as I2C2) is a bar: one line from the MCU, one tap per device. The MCU pins sit on the MCU line.
- Keep every link straight. Put a block beside the edge of the block it talks to, inside that edge's span. Make the MCU larger if it needs more room.
- To stop two links crossing, swap the order of the blocks along the edge.
- `lineAt` in `places.ts` moves a straight link along the overlap when the middle would pass too close to another block.

## Deploy

GitHub Pages serves `dist/` under `/AeroOptix-Horizon/` (`base` in `vite.config.ts`). The router uses hash URLs (`#/diagram?level=board`), so deep links work without server rewrites.

`.github/workflows/pages.yml` builds and deploys on every push to `main` that touches `web/`, the design records or the root `README.md`, so a merged record change shows on the site without any edit here. It builds only; the browser checks run in `web-test.yml`. The Overview footer and the sidebar show the commit the live site was built from.

## Template and licences

Based on [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) at commit `e16c87f213a5ba5e45964e9b67c792105ec74d26` (MIT, see `LICENSE`). The auth, chat, user, task and settings demo pages were removed. Diagrams use [React Flow](https://reactflow.dev) (`@xyflow/react`, MIT).
