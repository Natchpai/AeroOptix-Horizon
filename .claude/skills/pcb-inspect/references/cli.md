# query_pcb.py command semantics

Read this when interpreting a command's output. Output is JSON, bounded and deterministically ordered.

`summary` reports board metadata, declared layers, footprint counts, and bounded footprint samples.
`footprint` reports saved footprint reference/value, library ID, side/layer, placement,
rotation, and UUID. If a reference has multiple matches, report `AMBIGUOUS_REFERENCE`.
`pads` reports saved pad numbers, types, shapes, declared layers, nominal sizes, saved
net assignment, and board-space pad centres. It supports SMD and through-hole pads,
including footprint translation, rotation, and B.Cu mirroring. Unconnected pads are
reported as `UNCONNECTED`; a custom or unsupported pad outline is `NOT_VERIFIED`.
`net` reports a declared net's assigned footprint/pad records. A net absent from the
saved assignments is `MISSING`. KiCad files that store a name-only pad assignment without
a declared net table are reported as `ASSIGNED_WITHOUT_DECLARATION` with declaration
semantics `NOT_VERIFIED`. Matching saved net names are an assignment lookup only, not
evidence of copper connectivity.
`tracks` reports saved straight segments and arcs assigned to one exact net, including
layer, width, start/end coordinates, and geometric length in millimeters. Arc records
also include their saved `mid` point. A zero-length segment is reported as `0.0`; a
missing or malformed geometry, or an arc that cannot be resolved from its three points,
has `length_mm: null` and `length_status: NOT_VERIFIED` rather than an estimate.
`vias` reports saved net assignment, board-space position, size, drill, layer span, and
the saved via type when present. An omitted via type is `null` with
`via_type_status: NOT_VERIFIED`; it is not assumed to be through-hole.
`nearby` reports all other saved footprints ordered by Euclidean distance from the
requested footprint's saved origin, in board coordinates. The queried footprint is not
included as its own neighbor. `origin`, each neighbor origin, and `distance_mm` explicitly
identify the measurement points; no package outline or copper geometry is used.
`pad-distance` reports the Euclidean distance between two uniquely resolved saved pad
centres after the existing footprint rotation and B.Cu mirror transforms. Pad identifiers
are matched against complete saved references before their exact pad numbers, so references
and pad numbers may themselves contain dots or other unusual characters. A requested
identifier that resolves to multiple saved pads returns `AMBIGUOUS`; missing or unresolvable
saved geometry returns structured `NOT_FOUND` or `NOT_VERIFIED` JSON without a distance.
Malformed saved S-expressions, conflicting net declarations, malformed geometry, and
unresolvable coordinates return structured `NOT_VERIFIED` JSON; they do not fall back to
guessed geometry. Duplicate references retain `AMBIGUOUS_REFERENCE`; a pad identifier that
matches more than one saved pad returns `AMBIGUOUS` with a bounded candidate list.

For `tracks` and `vias`, an empty quoted target (`""`) requests explicitly unconnected
items. `MISSING`, `UNCONNECTED`, and `ASSIGNED_WITHOUT_DECLARATION` are distinct saved
assignment states. A declared net with no matching routing items returns `NOT_FOUND` with
`net_status: DECLARED`.

Output is bounded by `--limit` (1 through 1000) and JSON object keys plus result lists
have deterministic ordering. The CLI never infers physical copper connectivity,
clearance, route completeness, signal-path length, filled zones, or electrical continuity
from an assigned net name or geometric distance. Never claim a planned mode is an
implemented CLI command.
