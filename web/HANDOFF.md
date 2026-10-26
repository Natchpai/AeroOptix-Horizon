# Handoff: team website

**Updated:** 2026-10-26
**Status:** Clickable mockup, live on GitHub Pages. The engineer approved the Pinout page and reviewed the Block diagram for size and labels. Rail colours, SVG export, the record-driven Overview (progress, spec changes, next action, build stamp) and the IO MCU layout are live (PR #20, squash commit `2fd8638`).

## Where things are

- Live site: https://natchpai.github.io/AeroOptix-Horizon/
- Code: `web/`, merged to `main` in PR #18 (squash commit `e7def40`). Deploy: `.github/workflows/pages.yml`, on push to `main` when `web/`, the design docs or `README.md` change; it can also be started by hand.
- What the build reads, so a merge to `main` updates the site with no code change:
  - spec: every ID row (open items, decisions, interfaces), the header (revision, date) and the last 5 rows of section 9 change notes
  - pin allocation: the H743, F100 and F100-reserved tables
  - execution checklist: `Gate summary`, every `P<n>-<nnn>` task status, `Current next action`
  - root `README.md`: phase, board revision, baseline, KiCad, key features, `Main MCU` and `IO MCU`
  - `extract-docs` throws when one of these is missing, so a changed record layout fails the build and the old site stays up.
- Still hand-written: blocks and links (`topology.ts`) and their positions (`places.ts`).
- Pages is enabled with source "GitHub Actions". The first run failed because Pages was not enabled yet; the re-run passed.
- Branches: `dev` contains all of `main` (the engineer merged `main` into `dev` after PR #20, `4947719`). PRs #18, #19 and #20 were squash-merged, which leaves `dev` behind `main` each time. Merge with "Create a merge commit", or turn off squash merging in the repo settings, to avoid that.

## What the site does

- Overview: phase, revisions, key features, open OPEN items, and (engineer's request, 2026-10-24) gate progress per checklist gate with a stacked task bar, the checklist's current next action (one numbered line per sentence or list item, words unchanged; task IDs link to their checklist row and take their status colour), the last 5 spec change notes, and a build stamp (commit and date, also in the sidebar). Order, from `lg` up: Progress (left half) beside Recent spec changes (right half), then the next action at full width, then Key features beside Open items. Below `lg` the cards stack.
- **View names (engineer, 2026-10-26):** the outer view was renamed Board ("board mean overview system, system mean how to connect in board"), then **Overview** (L0, URL id `system`); the inner view is **System** (L1, URL id `board`). Only the labels changed; the ids stayed so old links work. History below uses the names of its date.
- **Equal spacing (engineer, 2026-10-26):** link ends on one side of a block are spaced equally and centred, first asked for the PM02D on the Overview, then for every block. `bundles` in `places.ts` count as one end (servo PWM group with the rail-sense line, Overview FC-to-servos pair). `npm run check` enforces it. To meet it, the Overview PM02D now sends the battery down to the PDB (PDB under the PM02D), and the Power view columns were re-spaced: the +5V bar is centred on the LDO line, the +3V3 bar on the buck line.
- **Overview zones (engineer, 2026-10-26):** the Overview now shows the board ports. Each device line starts at its port (`o-*` blocks, refs copied from the spec rows of the matching System view connectors); the FC block has no lines. Zones: one In board (PCB) zone with the FC and its ports (power module conn, XT30 6 V in and servo headers left of the FC; Tel1, Tel2, GPS1, air-data, TF-Luna, USB-C, microSD slot, debug and ESC headers right of it), then Out board: power (battery, PM02D, PDB, UBEC), Out board: devices, Out board: actuators. Link ids are unchanged (`s-fc-*`), so old links still open.
- **System view zones (engineer, 2026-10-26):** I2C2 is one line out of the H743 to a bus bar, which taps Baro 1, Baro 2 and the magnetometer (addresses on the taps, from the pin allocation). Blocks sit in titled zones: Connectors (right column: Tel1, Tel2, power module, air-data, TF-Luna, ESC, GPS1, servo headers), USB and debug (USB-C, H743 debug, F100 SWD pads, kept apart at the engineer's request) and On-board I/O (top: microSD, spare pads, LEDs, buzzer). Connectors have small corners and a tab on the cable side; parts with no cable are the new kind `io`. GPS1 is tall so it faces both MCUs; the F100 sits centred under the H743 and its SWD pads are on its left. `npm run check` tests the zone boxes.
- Block Diagram: Overview (L0) and System (L1) views, hand-placed, every link straight. Click a block for its detail panel; click a link label for the Interface view (L2): each signal with the MCU pin at each end, far end `TBD`.
- Power view (L1, engineer's request, 2026-10-26): power only, left to right: battery, PM02D (tall, `+VIN` out at the top, battery out at the bottom), eFuse and USB-C, the +5V bar, the buck, LDO, UBEC and XT30, the +3V3 bar, then grouped loads (Main MCU, IO MCU, baro × 2 + mag, IMU × 2 on `+3V3A` (DEC-025), 5 V external ports, 8 servos, 4 ESCs). Feeds the records do not give (3.3 V to the MCUs, baro and mag, and the battery chain) are candidate; the LDO block is dashed because its part is not decided. Rail bars stand upright, 120 px wide, so the name fits.
- Pinout: LQFP100 / LQFP48 package views and pin tables; a pin links back to its diagram link.
- Showcase: placeholder.
- Ctrl+K search over pins, signals, blocks and spec IDs.
- SVG export (engineer's request, 2026-10-24): "Export SVG" on the System and Board views, "SVG" on each pinout package card. Native SVG (rect, line, text; no `foreignObject`), in the current site theme, with a title and a footer (spec revision, phase, "not for fabrication", export date). Diagrams are drawn from the same `placedLayout` as the canvas (`src/features/diagram/export-svg.ts`); the package view is the on-screen SVG with colours written out as hex (`src/features/pinout/export-svg.ts`). Shared helpers: `src/lib/svg-export.ts`.

## Decisions the engineer made (2026-10-24)

- GitHub Pages hosting; the site is public with the repo.
- Template: satnaing/shadcn-admin (chosen over the ThemeSelection templates).
- Dark theme, with blue and navy accents from the nP mark (the engineer's co-op logo).
- Logos (engineer's request, 2026-10-24): the team AeroOptix flame (`AeroOptix_v2_light_theme.png` / `AeroOptix_v2_dark_theme.png`, 1468 px square, sized by the engineer) is the main logo in the sidebar, the Overview hero and the tab icon. The nP mark is a small "In co-op with" credit in the sidebar footer. The theme colours did not change.
- Diagram: straight lines, wide spacing, no shared line ends, no crossings. No Mermaid. The ELK auto-layout was tried and dropped for hand placement (`src/data/places.ts`).
- Mockup first, then deploy (done).
- Pinout page: OK as it is.
- Block diagram, Board view only: Main MCU block 720x640 (was 900x700), Buzzer moved from the top edge to the left edge, XT30 above the servo headers. The System view keeps its FC block size.
- Board view, IO MCU area (engineer's request, 2026-10-24):
  - The F100 block is square, 400x400.
  - Servo headers are one tall block, 200x300, so "Servo headers × 8" shows in full.
  - One PWM line per servo output (IF-030 to IF-037), labelled with its timer channel from the spec, 28 px apart. The rail-sense line is set apart below them.
  - The F100 SWD pads moved under the F100, so XT30 and the servo headers are the only blocks on its right. The +3V3 rail bar moved down to make room.
  - Any small block at least 120 px tall is drawn as a centred column (icon, then name, then sub-line). This also applies to the PDB on the System view.
- Center blocks (MCUs, FC): icon and text centered, larger type. Other block and link text larger; blocks are 200x60.
- Link labels must not cover a block, another label or another line. Parallel pairs: labels centered on horizontal pairs, beside the line on vertical pairs (`layout.ts`).
- Power rails: one colour per rail. Battery is red (danger), +6V orange, +5V yellow, +3.3V fuchsia, +3.3VA indigo. Power lines are 5 px (signals 2.75 px) and never dashed; a candidate power line is faded to 45 % instead.
- Line and border weight (engineer's request, 2026-10-24, +1 px on each): block border 2 px, signal line 2.75 px (3 → 4 px selected), power line 5 px (5.5 → 6.5 px selected), end dot 7 px. All sizes are in `src/features/diagram/style.ts`, read by the canvas, the SVG export and the legend. The border sits inside the block, so `block-node.tsx` offsets each handle by the border width to keep the lines exactly straight.
- +3.3V and GPIO colours (engineer's requests): on 2026-10-24 +3.3V and GPIO swapped colours (+3.3V pink, GPIO blue). On 2026-10-25 GPIO went back to pink, and +3.3V took fuchsia, since blue is kept for high-speed buses (SPI, USB). +3.3VA unchanged.

  | Rail or bus | Bus id | Light | Dark |
  |---|---|---|---|
  | Battery (6S) | `batt` | `#dc2626` | `#ef4444` |
  | +6V | `v6` | `#ea580c` | `#f97316` |
  | +5V (incl. `+VIN`, VBUS) | `v5` | `#ca8a04` | `#facc15` |
  | +3.3V | `v3v3` | `#c026d3` (was `#db2777`) | `#e879f9` (was `#f472b6`) |
  | +3.3VA | `v3v3a` | `#4f46e5` | `#818cf8` |
  | GPIO (signal) | `gpio` | `#db2777` (back to the old colour, 2026-10-25) | `#f472b6` (back to the old colour, 2026-10-25) |

  Power blocks that output one rail take its colour (`rail` field in `topology.ts`: battery, PDB, UBEC, eFuse, buck, LDO, rail bars). PM02D keeps the kind colour, since it outputs two rails. The GPIO colour also shows on the Pinout page.

## Verified

- `npm run check`: OK (43 blocks, 57 links, 67 pins on links; 50 links before the servo lines were split). It fails, as intended, on a fake spec ID and on a block moved out of line.
- `npm ci` + `npm run build` on a fresh clone of `dev`.
- Pins spot-checked against the pin allocation record: H743 PE8 UART7_TX #38, H743 PA5 SPI1_SCK #29, F100 PA2 USART2_TX #12.
- Screenshots at 1440 px and 390 px: no horizontal scroll. The live Board view renders.
- After `6d00f58`: `npm run check` and `npm run build` pass. A headless Edge script measured every link label on both views, also with a block selected (bold labels): no label overlaps a block, a label or a line. That script is now `npm run test:ui` (see below).
- `npm run test:ui` (2026-10-24): passes in about 1.5 minutes. It fails, as intended, on a broken attribute in the SVG dot markup (all 4 diagram exports reported as invalid XML). Moving the servo headers 40 px down makes `npm run check` report all 8 PWM lines as bent. Both faults were put back.
- Code review (2026-10-24) found and fixed: the legend drew 2 px / 4 px line samples and the old dash after the +1 px change; SVG block corners were 8 px against 10 px on the canvas; a misplaced comment in `layout.ts`.

- Record-driven Overview: `npm run build` passes. The extracted gate counts match a separate count of the checklist (P0 17 done of 22; P1 0 of 15 plus 1 N/A; P2 0 of 18; P3 0 of 11; P4 0 of 11). A copy of the records with `Gate summary` renamed makes `extract-docs` fail. `GITHUB_SHA` sets the build stamp. Screenshots at 1440 and 390 px, dark and light: no horizontal scroll.
- Live after PR #20: the deploy passed and the sidebar shows `Build 2fd8638`, the merge commit, so the CI build stamp works. The Progress card, the 8 servo lines and Export SVG are on the live site.
- Light-theme +6V changed from `#c2410c` to `#ea580c` (engineer's request, 2026-10-24): the old one looked like Battery red. `#ea580c` was compared with `#f97316` on the System view; `#f97316` drifts toward the +5V amber and its 12 px label reads weaker on white (about 2.8:1 against white, `#ea580c` about 3.6:1).

- 2026-10-26, second pass (engineer's requests): view names swapped; power parts removed from the System (L1) view (the `+5V` and `+3V3` bars, eFuse, buck, LDO, XT30 and their lines), USB-C moved level with the F100, the power module port drawn tall so its name shows in full; the Board (L0) power chain runs left to right (battery, PM02D, PDB, UBEC); the Power view splits the sensors into IMU × 2 on `+3V3A` (DEC-025, decided) and baro × 2 + mag on `+3V3` (candidate). `npm run check` (55 blocks, 65 links), `npm run build` and `npm run test:ui` pass; screenshots of all three views at 1440 px dark and light, and the Overview with the new Power card.
- Power view (2026-10-26): `npm run check` passes (61 blocks, 74 links), `npm run build` and `npm run test:ui` pass with the Power view in the page-error, straight-line, label-overlap (4 states) and SVG-export lists. Headless Edge screenshots at 1440 px (dark and light) show every name and sub in full. At 390 px the view is tiny on first load, as the Board view is.

## Not verified

- Light theme on the pinout page.
- Every block and link text against the spec: only spot checks were done. `topology.ts` is hand-written.
- Same-tab deep links: pasting a new `#/…` URL into an open tab was not tested (a fresh load works).
- SVG export: all 8 files (4 views × 2 themes) were downloaded in headless Edge from the production build, parse as valid SVG, contain no CSS variables, `color-mix` or classes, and render correctly in Edge. Opening them in Inkscape, PowerPoint or Word was not tested. Text uses Inter and JetBrains Mono when installed, else the generic sans-serif and monospace.

## Next steps

1. Engineer reviews the rest of the live site (Overview, Interface view, detail panel, search) and lists changes.
2. Engineer checks fuchsia +3.3V on screen: it sits between GPIO pink and UART purple.
3. Done 2026-10-26: the root `README.md` links the site (Overview, Documentation, repository tree) and `CHANGELOG.md` records it. The eFuse block now also names `CMP-008` (spec rev 0.15).
4. Keep `topology.ts` in step with the spec as it changes. The build check catches IDs that no longer exist, but not new interfaces: add them by hand.
5. Showcase, once there is a PCB: a 3D viewer (`@google/model-viewer` with a GLB from KiCad 10; the exact `kicad-cli` export command is `NOT_VERIFIED`), then renders and photos in `web/public/`.

## Known gaps in the content

- Far-end pins (sensor and connector pins) and connector pinouts are not in the records (OPEN-023), so the Interface view shows `TBD` there.
- Which rail feeds each sensor is not drawn: only the `ASSUMED` 3.3 V feeds to the MCUs are, as candidate (dashed) links.
- The F100 reserved pins have no package pin numbers in the record, so they appear in a table only, not on the package view.
- The KiCad `block_diagram.kicad_sch` still says F103 (P2-014, the engineer's item); the site does not use it.
- At 390 px the System (L1) and Power views are tiny on first load; the canvas zoom controls work.
- Light theme on the new diagram layout is not checked.

## Preview in VS Code

`cd web`, `npm run dev`, then `Ctrl+Shift+P` > **Simple Browser: Show** and open `http://localhost:5173/AeroOptix-Horizon/#/diagram?level=board`. The page reloads on save.
