# CLAUDE.md (web/)

The team website: a Vite + React + TypeScript site (shadcn-admin template) that shows the block diagram, the MCU pinouts and the project status. Live at https://natchpai.github.io/AeroOptix-Horizon/. Commands, data sources and checks are in `README.md`; current state and next steps are in `HANDOFF.md`. The root `CLAUDE.md` and `.claude/rules/` still apply here, including the Git approval rules.

## Content rule

The design records stay the source of truth. The site reads them at build time (`scripts/extract-docs.ts`) and shows what they say. A value the records do not give (sensor-side pins, connector pinouts, rails to sensors) shows as `TBD`. Every block and link in `src/data/topology.ts` names the spec IDs it comes from, and its text is copied from the spec. A design change goes into the spec first, through the engineer; the site follows.

## Diagram drawing rules

The engineer set these after reviewing the mockup:

- Every link is one **straight** line. Place a block beside the edge of the block it talks to, inside that edge's span. Grow a block (an MCU, a tall connector, a rail bar) to make room rather than bending a line. MCU blocks stay close to square.
- Blocks keep **wide gaps**, and link ends on one side keep 28 px apart, so parallel lines stay distinct.
- Blocks **spread out**: a block takes a free edge or a free spot before it queues in a tight column with other blocks (the F100 SWD pads sit under the F100, not under the servo headers).
- Each signal reads as its **own line**: the servo headers get one PWM line per spec row, labelled with its timer channel. A different signal between the same two blocks (rail sense) sits clearly apart from the group. Pin such lines with `lineAt`.
- Names show in **full**: make a block taller instead of shortening its name. A small block at least `TALL` px high (`layout.ts`) draws as a centred column, with the name across the full width.
- Lines never **cross**: swap block order along an edge to clear a crossing.
- Power rails are wide bars that loads tap with a vertical line.
- Positions live in `src/data/places.ts`; `lineAt` there sets where a straight line runs along its overlap (absolute px).

`npm run check` enforces the straight lines, gaps, line-end spacing and crossings, and names the link or block to move. It has no font widths: `npm run test:ui` checks label overlap in the browser, and spread and full names still need a screenshot.

Line widths, the block border, corners, end dots, dashes and label box sizes live in `src/features/diagram/style.ts`; change them there, never as a literal in a component.

## Look

Dark theme by default, with the club logo colours as accents (blue `#529AD6`, navy `#35496A`), not plain black and white. Colour tokens are in `src/styles/theme.css`, including the bus colours (`--bus-*`), the power rail colours (`--rail-*`) and design-state colours (`--status-*`). Each power rail has its own colour (the engineer picked them; the table is in `HANDOFF.md`), drawn thicker than signals and never dashed: a candidate power line is faded instead. The engineer chose this template and look; propose larger visual changes before making them.

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
