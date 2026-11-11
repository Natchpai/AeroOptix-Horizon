# query_pcb.py command semantics

Read this when interpreting a command's output. Output is JSON, bounded and deterministically ordered.

`summary` reports board metadata, declared layers, footprint counts, and bounded footprint samples.
It also reports `net_count` (distinct net names assigned to saved pads, tracks, vias and
zones), `track_count`, `via_count`, `zone_count` and `edge_cuts_bbox`. The box uses
top-level `Edge.Cuts` graphics only. `edge_cuts_bbox_status` is `STRUCTURAL_EVIDENCE`
when the outline has only lines, rectangles, circles and plain polygons. With arcs or
curves only their saved points are used, so the status is `NOT_VERIFIED`; it is also
`NOT_VERIFIED` when no outline is found.
`nets` lists assigned net names with `pad_count`, `track_count`, `via_count` and
`zone_count`, in natural order. `--match` keeps names that contain the text (case
insensitive). `net_count` is the number of matches and `board_net_count` the number on
the board. Unconnected items are not listed.
`footprint` reports saved footprint reference/value, library ID, side/layer, placement,
rotation, and UUID. If a reference has multiple matches, report `AMBIGUOUS_REFERENCE`.
`pads` reports saved pad numbers, types, shapes, declared layers, nominal sizes, saved
net assignment, and board-space pad centres. It supports SMD and through-hole pads,
including footprint translation and rotation. A back-side footprint's local pad
coordinates are used as saved; the file already stores them flipped. Unconnected pads are
reported as `UNCONNECTED`; a custom or unsupported pad outline is `NOT_VERIFIED`.
`net` reports a net's assigned footprint/pad records. A net absent from the
saved assignments is `MISSING`. KiCad 10 boards have no net table and store
`(net "name")` on each item: such a net is `ASSIGNED`, with
`net_declaration_status: NOT_APPLICABLE`. `ASSIGNED_WITHOUT_DECLARATION` (declaration
`NOT_VERIFIED`) is used only when the board has a net table that lacks the name. Matching saved net names are an assignment lookup only, not
evidence of copper connectivity.
`tracks` reports saved straight segments and arcs assigned to one exact net, including
layer, width, start/end coordinates, and geometric length in millimeters. Arc records
also include their saved `mid` point. A zero-length segment is reported as `0.0`; a
missing or malformed geometry, or an arc that cannot be resolved from its three points,
has `length_mm: null` and `length_status: NOT_VERIFIED` rather than an estimate.
`totals` covers every matching primitive, not only those listed under `--limit`:
`segment_count`, `arc_count`, `total_length_mm`, `length_by_layer_mm`, `widths` (each
width with a count) and `length_not_verified_count` (primitives with no usable length,
left out of the sums). The total is the sum of saved primitives on that net. It is not a
routed-path, signal-path or return-path length.
`vias` reports saved net assignment, board-space position, size, drill, layer span, and
the saved via type when present. An omitted via type is `null` with
`via_type_status: NOT_VERIFIED`; it is not assumed to be through-hole.
`totals.groups` counts every matching via per size, drill, layer span and type.
`zones` reports saved zones assigned to one exact net: `layers`, `name`, `priority`
(`null` when the file saves none), `outline_bbox` and `outline_point_count` of the saved
outline, `connect_pads` (`mode` and `clearance_mm`; a `null` mode means the file saves no
mode token), `min_thickness_mm`, thermal settings, `teardrop`, `rule_area`, and
`saved_fill_present` with the saved fill polygon count and layers. `fill_status` is always
`NOT_VERIFIED`: saved fill polygons may be stale and are not checked. `totals` gives zones
per layer and the teardrop, rule-area and saved-fill counts. An empty target lists zones
with no net, such as rule areas.
`nearby` reports all other saved footprints ordered by Euclidean distance from the
requested footprint's saved origin, in board coordinates. The queried footprint is not
included as its own neighbor. `origin`, each neighbor origin, and `distance_mm` explicitly
identify the measurement points; no package outline or copper geometry is used.
`--layer <name>` keeps footprints on that layer and `--radius <mm>` keeps those within
that origin distance. `filters_applied` shows both values (`null` when not used),
`neighbor_count` is the count after filtering and `unfiltered_neighbor_count` the count
before.
`pad-distance` reports the Euclidean distance between two uniquely resolved saved pad
centres after the saved footprint translation and rotation. Pad identifiers
are matched against complete saved references before their exact pad numbers, so references
and pad numbers may themselves contain dots or other unusual characters. A requested
identifier that resolves to multiple saved pads returns `AMBIGUOUS`; missing or unresolvable
saved geometry returns structured `NOT_FOUND` or `NOT_VERIFIED` JSON without a distance.
Malformed saved S-expressions, conflicting net declarations, malformed geometry, and
unresolvable coordinates return structured `NOT_VERIFIED` JSON; they do not fall back to
guessed geometry. Duplicate references retain `AMBIGUOUS_REFERENCE`; a pad identifier that
matches more than one saved pad returns `AMBIGUOUS` with a bounded candidate list.

For `tracks`, `vias` and `zones`, an empty quoted target (`""`) requests explicitly unconnected
items. `MISSING`, `UNCONNECTED`, `ASSIGNED` and `ASSIGNED_WITHOUT_DECLARATION` are distinct saved
assignment states. A declared net with no matching routing items returns `NOT_FOUND` with
`net_status: DECLARED`.

Output is bounded by `--limit` (1 through 1000) and JSON object keys plus result lists
have deterministic ordering. The CLI never infers physical copper connectivity,
clearance, route completeness, signal-path length, filled zones, or electrical continuity
from an assigned net name or geometric distance. Never claim a planned mode is an
implemented CLI command.
