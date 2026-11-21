# query_pcb.py command semantics

Read this when interpreting a command's output. Output is JSON, bounded and deterministically ordered.

`summary` reports board metadata (`version`, `generator`, and `generator_version` when
saved), declared layers, footprint counts, and bounded footprint samples. Each layer has
`id`, `name` (canonical, for example `F.SilkS`), `type`, and `user_name` (the saved user
name, for example `F.Silkscreen`, or `null` when none is saved).
It also reports `net_count` (distinct net names assigned to saved pads, tracks, vias and
zones), `track_count`, `via_count`, `zone_count` (including zones inside footprints) and
`edge_cuts_bbox`. The box uses
top-level `Edge.Cuts` graphics only. `edge_cuts_bbox_status` is `STRUCTURAL_EVIDENCE`
when the outline has only lines, rectangles, circles and plain polygons. With arcs or
curves, including arc pieces inside a polygon, only their saved points (start, mid, end)
are used, so the status is `NOT_VERIFIED`; it is also `NOT_VERIFIED` when no outline is
found.
`nets` lists assigned net names with `pad_count`, `track_count`, `via_count` and
`zone_count`, in natural order. `--match` keeps names that contain the text (case
insensitive). `net_count` is the number of matches and `board_net_count` the number on
the board. Unconnected items are not listed.
`footprint` reports saved footprint reference/value, library ID, `layer`, `side` (`top` for
`F.Cu`, `bottom` for `B.Cu`, otherwise `null`), placement, rotation, and UUID. If a
reference has multiple matches, report `AMBIGUOUS_REFERENCE`.
`pads` reports saved pad numbers, types, shapes, declared layers, nominal sizes, saved
net assignment, and board-space pad centres. It supports SMD and through-hole pads,
including footprint translation and rotation. A back-side footprint's local pad
coordinates are used as saved; the file already stores them flipped. Unconnected pads are
reported as `UNCONNECTED`; a custom or unsupported pad outline is `NOT_VERIFIED`.
`rotation_deg` is the saved pad angle. KiCad saves it in board terms (it already includes
the footprint rotation), so `size_mm` x and y lie along the board axes when it is 0 or
180 and swap when it is 90 or 270. `drill_mm` is `{x_mm, y_mm}` (equal for a round hole)
or `null` with no drill; `drill_shape` is `circle`, `oval`, `null` with no drill, or
`NOT_VERIFIED` when the saved drill cannot be read.
`net` reports a net's assigned footprint/pad records. A net that no saved pad, track, via
or zone uses is `MISSING`. A net with no pads that exists only on tracks, vias or zones
is `FOUND` with `pad_count: 0` and `net_item_counts`. KiCad 10 boards have no net table and store
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
the via type. KiCad saves the type as a bare word after `via` (`blind`, `buried` or
`micro`) and saves no word for a through via, which is reported as `through`.
`via_type_status` is `STRUCTURAL_EVIDENCE`: the type is read from the file, not checked
against the stackup or the layer span.
`totals.groups` counts every matching via per size, drill, layer span and type.
`zones` reports saved zones assigned to one exact net: `layers`, `name`, `priority`
(`null` when the file saves none), `outline_bbox` and `outline_point_count` of the saved
outline, `connect_pads` (`mode` and `clearance_mm`; a `null` mode means the file saves no
mode token), `min_thickness_mm`, thermal settings, `teardrop`, `rule_area`, and
`saved_fill_present` with the saved fill polygon count and layers. `fill_status` is always
`NOT_VERIFIED`: saved fill polygons may be stale and are not checked. `totals` gives zones
per layer and the teardrop, rule-area and saved-fill counts. An empty target lists zones
with no net, such as rule areas. Zones saved inside a footprint (for example a keepout
that comes with the footprint) are included and name it in `footprint`; top-level zones
have `footprint: null`. KiCad saves footprint zone outlines in board coordinates.
`nearby` reports all other saved footprints ordered by Euclidean distance from the
requested footprint's saved origin, in board coordinates. The queried footprint is not
included as its own neighbor. `origin`, each neighbor origin, and `distance_mm` explicitly
identify the measurement points; no package outline or copper geometry is used.
`--layer <name>` keeps footprints on that layer and `--radius <mm>` keeps those within
that origin distance. The layer must be a canonical layer name on the board, matched
case-sensitively (`F.Cu`, `B.Cu`); any other name is a `NOT_VERIFIED` error. `filters_applied` shows both values (`null` when not used),
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
With `--group`, all pads with the requested number on one footprint (for example a split
exposed pad saved as several pads `9`) form one group. The result is the smallest distance
between any pad of the first group and any pad of the second; each side's `position` is
the pad centre used and `group_size` the number of pads in its group. Pads on more than one
footprint with the same reference still return `AMBIGUOUS`.

For `tracks`, `vias` and `zones`, an empty quoted target (`""`) requests explicitly unconnected
items. `MISSING`, `UNCONNECTED`, `ASSIGNED` and `ASSIGNED_WITHOUT_DECLARATION` are distinct saved
assignment states. A declared net with no matching items returns `NOT_FOUND` with
`net_status: DECLARED`. A net with no matching items that still exists on other saved items
(for example an unrouted net with pads only) returns `NOT_FOUND` with `ASSIGNED` (or
`ASSIGNED_WITHOUT_DECLARATION`) and `net_item_counts` (pad, track, via and zone counts);
only a name that no saved item uses is `MISSING`. On a board with a net table, a bare net
code that the table does not declare is `NOT_VERIFIED` and is not listed as a net name.

Output is bounded by `--limit` (1 through 1000) and JSON object keys plus result lists
have deterministic ordering. The CLI never infers physical copper connectivity,
clearance, route completeness, signal-path length, filled zones, or electrical continuity
from an assigned net name or geometric distance. Never claim a planned mode is an
implemented CLI command.
