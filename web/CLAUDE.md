# CLAUDE.md (web/)

The team website: a Vite + React + TypeScript site (shadcn-admin template) that shows the block diagram, the MCU pinouts and the project status. Live at https://natchpai.github.io/AeroOptix-Horizon/. Commands, data sources and checks are in `README.md`; current state and next steps are in `HANDOFF.md`. The root `CLAUDE.md` and `.claude/rules/` still apply here, including the Git approval rules.

## Content rule

The design records stay the source of truth. The site reads them at build time (`scripts/extract-docs.ts`) and shows what they say. A value the records do not give (sensor-side pins, connector pinouts, rails to sensors) shows as `TBD`. Every block and link in `src/data/topology.ts` names the spec IDs it comes from, and its text is copied from the spec. A design change goes into the spec first, through the engineer; the site follows.

## View names

The diagram views show names that differ from their ids (engineer, 2026-10-26): id `system` is shown as **Overview** (L0, the board and what it connects to), id `board` as **System** (L1, how the blocks inside the board connect), id `power` as **Power** (L1, power flow left to right). Keep the ids; change only labels. Power parts live on the Power view only, not on the System (L1) view.

## Diagram drawing rules

The engineer set these after reviewing the mockup:

- Every link is one **straight** line. Place a block beside the edge of the block it talks to, inside that edge's span. Grow a block (an MCU, a tall connector, a rail bar) to make room rather than bending a line. MCU blocks stay close to square.
- Blocks keep **wide gaps**, and link ends on one side keep 28 px apart, so parallel lines stay distinct.
- Blocks **spread out**: a block takes a free edge or a free spot before it queues in a tight column with other blocks.
- Each signal reads as its **own line**: the servo headers get one PWM line per spec row, labelled with its timer channel. A different signal between the same two blocks (rail sense) sits clearly apart from the group. Pin such lines with `lineAt`.
- Names show in **full**: make a block taller instead of shortening its name. A small block at least `TALL` px high (`layout.ts`) draws as a centred column, with the name across the full width.
- Lines never **cross**: swap block order along an edge to clear a crossing.
- Link ends on one side of a block are **spaced equally and centred** on that side (engineer, 2026-10-26). A group in `bundles` (`places.ts`) counts as one end: the servo PWM lines with the rail-sense line set apart, and the Overview servo-headers-to-servos pair. A block with one end on a side sits level with the other end, so the line meets it in the middle. Move blocks or set `lineAt` to meet it.
- Power rails are wide bars that loads tap with a vertical line. A shared signal bus is drawn the same way (kind `bus`): one line out of the MCU to a bar, then one tap per device (I2C2, engineer, 2026-10-26).
- **Zones** (engineer, 2026-10-26): on the System (L1) view, blocks sit in titled zones: Connectors (one column on the right), USB and debug (USB-C, H743 debug, F100 SWD pads; the engineer asked to keep them apart from the other connectors) and On-board I/O (top). On the Overview (engineer, 2026-10-26), each device line starts at the board port it plugs into, and one In board (PCB) zone holds the FC and all its ports (power ports left of the FC, normal connectors right of it); Out board zones hold the outside modules: power, devices and actuators. The engineer wants the PCB read as one zone, joined to the outside modules only by lines. The FC block has no lines. `zones` in `places.ts` lists each zone's blocks; the box is sized to fit them, and no other block may sit inside it.
- **Connectors** (kind `connector`, a cable plugs in) have small corners and a solid tab on the cable side: away from their links on the System view, toward them on the Overview, where the links are the cables. Parts with no cable (microSD slot, LEDs, buzzer, spare and SWD pads) are kind `io` with the plain look.
- Positions live in `src/data/places.ts`; `lineAt` there sets where a straight line runs along its overlap (absolute px).

`npm run check` enforces the straight lines, gaps, line-end spacing, equal and centred ends, crossings and zone boxes, and names the link or block to move. It has no font widths: `npm run test:ui` checks label overlap in the browser, and spread and full names still need a screenshot.

Line widths, the block border, corners, end dots, dashes and label box sizes live in `src/features/diagram/style.ts`; change them there, never as a literal in a component.

## Look

Dark theme by default, with blue `#529AD6` and navy `#35496A` accents, not plain black and white. Those colours come from the nP mark, the engineer's co-op logo; the engineer keeps them as the theme. The team logo is the orange AeroOptix flame (`public/images/aeroOptix_*_logo.png`): it is the main logo (sidebar, Overview hero, tab icon), and the nP mark appears only as a small "In co-op with" credit in the sidebar footer (`src/components/brand-logo.tsx`). Keep the flame's orange in the logo only. Colour tokens are in `src/styles/theme.css`, including the bus colours (`--bus-*`), the power rail colours (`--rail-*`) and design-state colours (`--status-*`). Each power rail has its own colour (the engineer picked them; the table is in `HANDOFF.md`), drawn thicker than signals and never dashed: a candidate power line is faded instead. The engineer chose this template and look; propose larger visual changes before making them.

## Checking your work

- `npm run build` must pass: it runs extract, check, `tsc -b` and the Vite build.
- Then `npm run test:ui` must pass (about 2 minutes, local only): page errors, straight lines on screen, label overlap, SVG export validity, no sideways scroll at 390 px. Add a check to `tests/ui.ts` when you fix a bug it could have caught. Functions passed to `page.evaluate` run in the page; `tsx` adds a `__name` helper to them, which the init script defines.
- For a look the test cannot judge (colours, spread, full names), take headless screenshots with `playwright-core` and the installed Edge (`chromium.launch({ channel: 'msedge' })`), from a script in the scratchpad. Open a new browser context per URL; in Git Bash prefix the command with `MSYS_NO_PATHCONV=1`, or arguments starting with `/` turn into Windows paths. Check 1440 px and 390 px widths, dark and light.
- A fresh clone for a CI-style test needs a sparse checkout (`web` and `hardware/AO-Horizon/documents/design`): the full repo hits the Windows path-length limit in the scratchpad.

## Gotchas

- SVG export draws the diagram again from layout data (`src/features/diagram/export-svg.ts`). Sizes come from `style.ts`, but block text layout (icon box, font sizes, line positions) is still mirrored by hand, so a change to block text in `block-node.tsx` must be made there too. The canvas draws the block border inside the box; the export insets its stroke by half the border, and `block-node.tsx` offsets each handle by the border width so lines stay straight. Export colours go through `paint()` in `src/lib/svg-export.ts`, which turns any CSS colour into hex, because Inkscape and Office do not read CSS variables or `color-mix()`.
- `scripts/extract-docs.ts` throws when a record heading or table it reads is missing. Renaming the spec `9. Specification Change Notes` table, the checklist `Gate summary` table or `Current next action` heading, or the README `Specifications` rows `Main MCU` and `IO MCU`, needs a matching change in the script.
- Routing uses hash history (`#/diagram?level=board`) and `base: '/AeroOptix-Horizon/'`; both are needed on GitHub Pages.
- `src/routeTree.gen.ts` is generated by the TanStack Router plugin on `dev`/`build`; it is committed.
- npm 12 blocks the esbuild postinstall script locally; the build still works. CI uses Node 24 and runs it normally.
- Generated JSON in `src/data/generated/` is git-ignored; run `npm run extract` (or `dev`) before reading it.
