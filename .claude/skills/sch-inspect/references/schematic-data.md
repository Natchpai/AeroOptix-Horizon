# KiCad 10 Schematic Data Reference

Native `.kicad_sch` structure, for when a `query_sch.py` result has to be
checked against the file itself. Rules, commands and the JSON contract are in
`SKILL.md`.

## Locating the target

- The root sheet's `sheet` entries name the child files (`Sheetfile`
  property). Follow only the branch the question needs.
- One `.kicad_sch` file can have several **sheet instances**. The file path
  does not identify an instance; the hierarchical UUID path does
  (`/<root uuid>/<sheet symbol uuid>/...`).
- A symbol's `Reference` property is a search hint. The reference and unit of
  each instance are stored under `instances / project / path`, one entry per
  project name and instance path. A copied sheet can carry entries for
  another project name.

## Native constructs

| Construct | What it holds |
| --- | --- |
| `symbol`, `lib_id`, properties, `unit`, `instances` | Part identity, reference, unit, per-instance assignment |
| `symbol` `at` (x, y, angle), `mirror` | Placement. KiCad rotates first, then mirrors on the canvas axis |
| `lib_symbols`, symbol pins | Pin numbers, names, electrical types, pin positions in symbol coordinates (Y up) |
| `lib_symbols` symbol `(power)` flag | Marks a power symbol; its `Value` is the net name |
| `wire`, `junction`, `no_connect` | Local connections and deliberate unconnected pins. Crossing wires join only at an endpoint or a junction |
| `label` | Named connection local to one sheet instance |
| `hierarchical_label`, parent `sheet` pins | Connection across a parent-child sheet boundary, matched by name |
| `global_label`, power symbols | Project-wide connection by name |
| `bus`, bus labels | Not expanded by the tool |
| `sheet`, `Sheetfile`, UUID | Hierarchy and reused-sheet identity |

A pin-to-net association depends on the symbol definition, unit, placement
transform, pin coordinates, wires and the connection rules above.

## References

- KiCad Schematic File Format: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
- KiCad S-expression format: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/
