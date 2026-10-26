# AO-Horizon team website

Static site for the team: a multi-level block diagram, the MCU pinouts and the project status. Later it will also show project output (3D model, renders, photos).

The design records in `hardware/AO-Horizon/documents/design/` stay the source of truth. The site reads them at build time and adds no values of its own.

## Run

Node 24 and npm.

```sh
cd web
npm ci
npm run dev      # http://localhost:5173/AeroOptix-Horizon/
npm run build    # extract + check + type-check + build to dist/
npm run preview  # serve dist/ under /AeroOptix-Horizon/
npm run test:ui  # browser checks on dist/, after build (local only)
```

`npm run check` re-reads the docs and checks the hand-written data on its own.

## Where the data comes from

| Data | Source | How |
|---|---|---|
| Spec IDs (IF, DEC, OPEN, SEN, PWR ...) | `AO-HORIZON_SPEC_EN.md` | `scripts/extract-docs.ts`, every table row whose first cell is an ID |
| MCU pins | `AO-HORIZON_PIN_ALLOCATION_EN.md` | same script, the H743, F100 and F100-reserved tables |
| Spec change notes (last 5) | `AO-HORIZON_SPEC_EN.md` section 9 | same script |
| Phase, board and spec revision, key features, MCU part numbers | root `README.md` | same script, `Specifications` table for the MCUs |
| Gate progress and current next action | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | same script, `Gate summary` table, every `P<n>-<nnn>` task row, `Current next action` paragraph |
| Build stamp (commit, date) | Git | same script: `GITHUB_SHA` in CI, `git rev-parse HEAD` locally |
| Blocks and links | `src/data/topology.ts` | hand-written; every block and link names its spec IDs |
| Block positions | `src/data/places.ts` | hand-written drawing data |

The extracted JSON goes to `src/data/generated/`. It is git-ignored and rebuilt on every `dev` and `build`. The script throws when a table or heading it needs is missing, so a record that changes shape fails the build instead of showing `TBD`.

## Checks (`scripts/check-data.ts`)

The build fails when:

- a spec ID in the topology is not in the spec, or is a removed row
- a pin row is used by no link (rows that are not drawn are listed in `pinsNotOnDiagram` with a reason)
- a pin or package pin number is assigned twice
- a block has no position, or two blocks are closer than 24 px
- a link is not one straight line, runs through another block, or crosses another link
- the link ends on one side of a block are not equally spaced, or not centred on that side
- a zone lists an unknown block, holds a block it does not list, or comes within 24 px of another zone

## Browser checks (`tests/ui.ts`)

`npm run test:ui` serves `dist/` and opens it in the installed Microsoft Edge (through `playwright-core`; no browser download). It lists every failure and exits 1 when:

- a page throws an error (Overview, the Board, System and Power views, an Interface view, both pinouts)
- a drawn line is not straight on screen
- a link label covers a block, another label or another line, with no block selected and with five blocks selected in turn
- an SVG export (4 views, dark and light) is not valid XML, or still holds CSS (`var(`, `color-mix`, `oklab`, `class=`)
- a page scrolls sideways at 390 px

It takes about 2 minutes. CI does not run it, because CI has no Edge. Google Fonts are fetched once per run and then served from memory. If they cannot be fetched, the run warns that label checks used fallback fonts.

## Editing the diagram

- Line widths, block border, corner radius, end dots, dashes and label box sizes are in `src/features/diagram/style.ts`. The canvas, the SVG export and the legend all read them from there.
- Colours are tokens in `src/styles/theme.css` (`--rail-*`, `--bus-*`).

- New link or block: add it to `topology.ts` with its spec IDs, then give each new block a place in `places.ts`.
- Views: id `system` is shown as Overview (L0), id `board` as System (L1), id `power` as Power. The Power view (ids `pw-*`) holds every power part and runs left to right: source, input, protection, +5V bar, converters, +3V3 bar, loads. The System (L1) view has no power parts. A power change in the spec goes into the Power view, and into the Overview (L0) when it touches the battery chain.
- Link ends on one side of a block are spaced equally and centred on that side; a `bundles` group in `places.ts` counts as one end. `npm run check` names the block and side that break it.
- Zones: `zones` in `places.ts` lists the blocks of each titled box (System view: Connectors, USB and debug, On-board I/O). The box is sized to fit them. Connectors (kind `connector`) draw a tab on the cable side; on-board parts with no cable are kind `io`.
- A shared bus (kind `bus`, such as I2C2) is a bar: one line from the MCU, one tap per device. The MCU pins sit on the MCU line.
- Keep every link straight. Put a block beside the edge of the block it talks to, inside that edge's span. Make the MCU larger if it needs more room.
- To stop two links crossing, swap the order of the blocks along the edge.
- `lineAt` in `places.ts` moves a straight link along the overlap when the middle would pass too close to another block.

## Deploy

GitHub Pages serves `dist/` under `/AeroOptix-Horizon/` (`base` in `vite.config.ts`). The router uses hash URLs (`#/diagram?level=board`), so deep links work without server rewrites.

`.github/workflows/pages.yml` builds and deploys on every push to `main` that touches `web/`, the design records or the root `README.md`, so a merged record change shows on the site without any edit here. The Overview footer and the sidebar show the commit the live site was built from.

## Template and licences

Based on [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) at commit `e16c87f213a5ba5e45964e9b67c792105ec74d26` (MIT, see `LICENSE`). The auth, chat, user, task and settings demo pages were removed. Diagrams use [React Flow](https://reactflow.dev) (`@xyflow/react`, MIT).
