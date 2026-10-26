/**
 * Drawing sizes for blocks and links, in px at zoom 1. The canvas
 * (block-node.tsx, link-edge.tsx), the SVG export and the legend all read
 * these, so a size changes in one place.
 */
export const draw = {
  /** Block border, drawn inside the box. */
  border: 2,
  /** Block corner radius (the same as Tailwind rounded-lg, --radius). */
  radius: 10,
  /** Connector blocks: small corner radius, and a solid tab on the cable side. */
  port: { radius: 3, tab: 5 },
  /** Zone: space around its blocks, title band on top, corner radius. */
  zone: { pad: 22, head: 26, radius: 14, font: 12 },
  /** Link end dot, diameter. */
  dot: 7,
  line: { signal: 2.75, power: 5 },
  /** Line width when the link or its block is selected or hovered. */
  lineStrong: { signal: 4, power: 6.5 },
  /** Invisible click area along a line. */
  hit: { signal: 14, power: 18 },
  /** Candidate signal line and candidate block border. */
  dash: { signal: '6 5', block: '4 3' },
  /** Opacity of a candidate power line (power lines are never dashed). */
  candidatePower: 0.45,
  /** Link label box: font size, side padding, height, gap from its line. */
  label: { font: 12, padX: 6, height: 20, gap: 6 },
}
