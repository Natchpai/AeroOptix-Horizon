# Handoff: team website

**Updated:** 2026-10-24
**Status:** Clickable mockup, live on GitHub Pages. The engineer approved the Pinout page and reviewed the Block diagram for size and labels. The diagram update (`6d00f58`) is on `dev` only: the live site still shows the old diagram until it reaches `main`.

## Where things are

- Live site: https://natchpai.github.io/AeroOptix-Horizon/
- Code: `web/`, merged to `main` in PR #18 (squash commit `e7def40`). Deploy: `.github/workflows/pages.yml`, on push to `main` when `web/`, the design docs or `README.md` change; it can also be started by hand.
- Pages is enabled with source "GitHub Actions". The first run failed because Pages was not enabled yet; the re-run passed.
- Branches: `dev` is still 1 commit behind `origin/main` (the squash commit `e7def40`), and `6d00f58` is not pushed. Merge `main` into `dev` before the next PR, with the engineer's approval.

## What the site does

- Overview: phase, revisions, key features, open OPEN items.
- Block Diagram: System (L0) and Board (L1) views, hand-placed, every link straight. Click a block for its detail panel; click a link label for the Interface view (L2): each signal with the MCU pin at each end, far end `TBD`.
- Pinout: LQFP100 / LQFP48 package views and pin tables; a pin links back to its diagram link.
- Showcase: placeholder.
- Ctrl+K search over pins, signals, blocks and spec IDs.

## Decisions the engineer made (2026-10-24)

- GitHub Pages hosting; the site is public with the repo.
- Template: satnaing/shadcn-admin (chosen over the ThemeSelection templates).
- Dark theme, logo colours as accents.
- Diagram: straight lines, wide spacing, no shared line ends, no crossings. No Mermaid. The ELK auto-layout was tried and dropped for hand placement (`src/data/places.ts`).
- Mockup first, then deploy (done).
- Pinout page: OK as it is.
- Block diagram, Board view only: Main MCU block 720x640 (was 900x700), Buzzer moved from the top edge to the left edge, XT30 above the servo headers. The System view keeps its FC block size.
- Center blocks (MCUs, FC): icon and text centered, larger type. Other block and link text larger; blocks are 200x60.
- Link labels must not cover a block, another label or another line. Parallel pairs: labels centered on horizontal pairs, beside the line on vertical pairs (`layout.ts`).

## Verified

- `npm run check`: OK (43 blocks, 50 links, 67 pins on links). It fails, as intended, on a fake spec ID and on a block moved out of line.
- `npm ci` + `npm run build` on a fresh clone of `dev`.
- Pins spot-checked against the pin allocation record: H743 PE8 UART7_TX #38, H743 PA5 SPI1_SCK #29, F100 PA2 USART2_TX #12.
- Screenshots at 1440 px and 390 px: no horizontal scroll. The live Board view renders.
- After `6d00f58`: `npm run check` and `npm run build` pass. A headless Edge script measured every link label on both views, also with a block selected (bold labels): no label overlaps a block, a label or a line. The script lives outside the repo; `npm run check` cannot test this, because it has no font widths.

## Not verified

- Light theme on the diagram and pinout pages.
- Every block and link text against the spec: only spot checks were done. `topology.ts` is hand-written.
- Same-tab deep links: pasting a new `#/…` URL into an open tab was not tested (a fresh load works).

## Next steps

1. Publish the diagram update. Each step needs its own approval: merge `main` into `dev`, push `dev`, open a PR to `main` with `.github/pull_request_template.md`. The engineer merges it, and the Pages workflow deploys.
2. Engineer reviews the rest of the live site (Overview, Interface view, detail panel, search) and lists changes.
3. Optional: add the label-overlap script to `web/` as its own command (it needs `playwright-core` and Edge, so keep it out of `npm run build` and CI).
4. Add the site to the root `README.md` and `CHANGELOG.md`, using `hw-git-readme` and `hw-git-changelog`, when asked.
5. Keep `topology.ts` in step with the spec as it changes. The build check catches IDs that no longer exist, but not new interfaces: add them by hand.
6. Showcase, once there is a PCB: a 3D viewer (`@google/model-viewer` with a GLB from KiCad 10; the exact `kicad-cli` export command is `NOT_VERIFIED`), then renders and photos in `web/public/`.

## Known gaps in the content

- Far-end pins (sensor and connector pins) and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD` there.
- Which rail feeds each sensor is not drawn: only the `ASSUMED` 3.3 V feeds to the MCUs are, as candidate (dashed) links.
- The F100 reserved pins have no package pin numbers in the record, so they appear in a table only, not on the package view.
- The KiCad `block_diagram.kicad_sch` still says F103 (P2-014, the engineer's item); the site does not use it.
- Long block names are cut with "…" on the Board view ("Power module conn", "Servo headers × 8"); the full name is in the detail panel.
- At 390 px the whole Board view is tiny on first load; the canvas zoom controls work.
- Light theme on the new diagram layout is not checked.

## Preview in VS Code

`cd web`, `npm run dev`, then `Ctrl+Shift+P` > **Simple Browser: Show** and open `http://localhost:5173/AeroOptix-Horizon/#/diagram?level=board`. The page reloads on save.
