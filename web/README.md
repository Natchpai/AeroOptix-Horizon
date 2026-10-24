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
```

`npm run check` re-reads the docs and checks the hand-written data on its own.

## Where the data comes from

| Data | Source | How |
|---|---|---|
| Spec IDs (IF, DEC, OPEN, SEN, PWR ...) | `AO-HORIZON_SPEC_EN.md` | `scripts/extract-docs.ts`, every table row whose first cell is an ID |
| MCU pins | `AO-HORIZON_PIN_ALLOCATION_EN.md` | same script, the H743, F100 and F100-reserved tables |
| Phase, board and spec revision, key features | root `README.md` | same script |
| Blocks and links | `src/data/topology.ts` | hand-written; every block and link names its spec IDs |
| Block positions | `src/data/places.ts` | hand-written drawing data |

The extracted JSON goes to `src/data/generated/`. It is git-ignored and rebuilt on every `dev` and `build`.

## Checks (`scripts/check-data.ts`)

The build fails when:

- a spec ID in the topology is not in the spec, or is a removed row
- a pin row is used by no link (rows that are not drawn are listed in `pinsNotOnDiagram` with a reason)
- a pin or package pin number is assigned twice
- a block has no position, or two blocks are closer than 24 px
- a link is not one straight line, runs through another block, or crosses another link

## Editing the diagram

- New link or block: add it to `topology.ts` with its spec IDs, then give each new block a place in `places.ts`.
- Keep every link straight. Put a block beside the edge of the block it talks to, inside that edge's span. Make the MCU larger if it needs more room.
- To stop two links crossing, swap the order of the blocks along the edge.
- `lineAt` in `places.ts` moves a straight link along the overlap when the middle would pass too close to another block.

## Deploy

GitHub Pages serves `dist/` under `/AeroOptix-Horizon/` (`base` in `vite.config.ts`). The router uses hash URLs (`#/diagram?level=board`), so deep links work without server rewrites. The Pages workflow is not added yet.

## Template and licences

Based on [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) at commit `e16c87f213a5ba5e45964e9b67c792105ec74d26` (MIT, see `LICENSE`). The auth, chat, user, task and settings demo pages were removed. Diagrams use [React Flow](https://reactflow.dev) (`@xyflow/react`, MIT).
