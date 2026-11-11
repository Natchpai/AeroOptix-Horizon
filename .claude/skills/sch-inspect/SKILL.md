---
name: sch-inspect
description: >-
  Inspects and explains KiCad 10 schematics from native .kicad_sch files:
  components, pins, nets, labels, hierarchical sheets, and sheet instances.
  Use when the user asks to inspect, trace, or explain schematic circuits,
  connections, or functional blocks. Targeted, read-only; it extracts evidence
  and does not judge the design.
argument-hint: "[summary | components [--sheet <name>] [--prefix <p>] | component <ref> | pins <ref> | local-net <ref> | hier-net <ref> | connected-pins <ref> | project-net <ref> --pin <n> | net <name> | instances | sheet <name>]"
---

# Schematic Inspection (KiCad 10)

## Rules
- Treat `.kicad_sch`, `.kicad_pro`, libraries, and all other CAD files as
  read-only. Do not create indexes, reports, caches, or other files unless asked.
- Start from the requested sheet or instance; read the least data needed. Do not
  default to a full-project scan, and do not export or ingest a whole-project
  netlist as the inspection method or as a fallback.
- Never imply a parser, resolver, or ERC check ran if it has not. Report a tool
  failure instead of guessing.
- Text search, matching net labels, nearby wires, or an empty result is not
  proof of connectivity (or of its absence).
- `PASS` needs validated evidence for that specific check. For an incomplete
  check use `NOT_VERIFIED` and name the missing evidence. Structure and
  geometry do not show electrical correctness. Keep observed and suspected
  apart.
- If no mode is given, ask for a target or offer the commands below.

## Commands
Run `scripts/query_sch.py` (Python 3.10+, standard library, Windows and macOS).
Resolve the script and project paths first; do not assume the working directory.

`python <skill dir>/scripts/query_sch.py <command> [target] --project <root.kicad_sch> [--limit <n>] [--max-files <n>]`

- `--project` takes the **root** schematic (the sheet at the top of the
  hierarchy) or its directory. Do not pass a child sheet as the root: parent
  links and other instances can be lost.
- `--pin <n>` works with `project-net` only (required when the component has
  several nets); other commands reject it.
- `--limit` bounds every list in the output, nested ones too (see JSON
  contract, truncation).
- `--sheet <name>` and `--prefix <p>` work with `components` only. `--sheet`
  takes a sheet name, file name or file stem. `--prefix U` keeps `U1` and
  `U104`, not `USB1`. References that start with `#` are listed only when
  the prefix starts with `#`.
- When the user describes a part ("the first IC") instead of giving a
  reference, list candidates with `components`; do not guess designators.
- `net <name>` matches the label or power symbol text exactly (case
  sensitive), for example `+5V` or `SPI_CLK`, not a KiCad net path such as
  `/Power/+5V`.

| Command | Purpose |
|---|---|
| `summary` | Sheets and component counts. |
| `components [--sheet <name>] [--prefix <p>]` | List reference, value, `lib_id` and instance path. |
| `component <ref>` | Locate a component; its properties. |
| `sheet <name>` | Locate a hierarchical sheet. |
| `pins <ref>` | Symbol pins with local wire/label geometry. |
| `local-net <ref>` | Sheet-local wires, junctions, labels, power symbols. |
| `hier-net <ref>` | Hierarchical interfaces to parent sheet connections. |
| `connected-pins <ref>` | Connected component and sheet pins across supported hierarchy. |
| `instances` | Hierarchical sheet instances and reused sheet files. |
| `project-net <ref> --pin <n>` | Connectivity evidence across instances, global labels, power nets. |
| `net <name>` | The same evidence, started from a label or power symbol name. |

Examples (root file `Top.kicad_sch`):
- `component U103 --project Top.kicad_sch`
- `project-net U103 --pin 8 --project Top.kicad_sch`
- `net +5V --project Top.kicad_sch`
- `components --sheet "Power State" --prefix U --project Top.kicad_sch`

Policy: prefer `component`, `pins`, or `local-net`; use `hier-net` or
`connected-pins` when hierarchy matters; use `project-net` only when
project-level evidence is required, with a specific pin for multi-net parts.
Use `net` when the question starts from a net name, and `components` when it
starts from a sheet or a part type.
Read JSON selectively. Structural checks have no separate command: build them
from these queries. ERC is a separate step, run only when requested or clearly
necessary; label its exact scope and output, and never equate ERC success with
circuit correctness.

## Procedure
1. **Locate** the project root and the sheet or symbol instance with a bounded lookup.
2. **Identify the instance.** Resolve the hierarchical instance path, especially
   for reused sheet files and multi-unit symbols. Output may list instances that
   belong to another project name (stale or copied sheets): use the instance
   whose project path matches the current project, and mention the others. If
   still ambiguous, list candidates and ask.
3. **Inspect locally:** symbols, pins, labels, wires, junctions, no-connects, and
   immediate neighbours.
4. **Assess connectivity.** Separate directly evidenced local connections from
   inferred or unresolved ones. Count power symbols and global connectivity only
   if the tool resolved them.
5. **Expand only as needed** through sheet pins, hierarchical or global labels,
   and power nets, and say why the wider scope was needed. A repeated local
   label in separate sheet instances is not one net.
6. **Validate** with calculations, datasheet evidence (from the user, official
   web pages or cited NotebookLM answers; never a direct PDF read), or
   targeted checks relevant to the question.
7. **Report** with file, sheet instance, reference, pin/net, evidence, and scope.

## Scope levels
- `LOCAL`: the selected sheet instance and locally established connections.
- `HIERARCHICAL`: includes traced parent/child interfaces.
- `GLOBAL`: includes relevant global labels and power connectivity; list the
  sources consulted.

The tool does not print a scope level; assign it from the command used:
`pins` and `local-net` give `LOCAL`; `hier-net` and `connected-pins` give
`HIERARCHICAL`; `project-net` and `net` give `GLOBAL`. `summary`,
`components`, `component`, `sheet`, and `instances` are structural discovery
below `LOCAL`.

Report the scope actually reached, not the one requested, if expansion failed.

## JSON contract
- Output is UTF-8 JSON on stdout; errors are UTF-8 JSON on stderr.
- Every successful command returns `mode`, `target`, `root`, `results`,
  `total_matches`, `truncated`, `missing_sheets`, `skipped_outside_project`,
  `verification`, `limitations`, and `warnings`.
- `project-net` returns one result: `PROJECT_CONNECTIVITY_EVIDENCE` (source pin,
  connected pins, label/power evidence, truncation flags, limitations), or
  `TARGET_NOT_FOUND_OR_UNRESOLVED` / `AMBIGUOUS_TARGET_NETS`. Report either
  unresolved status as `NOT_VERIFIED`; it does not show a connection is absent.
  `project_net_verified` is always false: it is not KiCad netlist parity.
- `net` returns one result per separate net that carries the name, with
  `matched_by` (label kind, instance path, file) and the same evidence
  fields as `project-net`. A local label repeated in several sheet instances
  gives several results: report them as separate nets. No match returns
  `NET_NAME_NOT_FOUND`; report it as `NOT_VERIFIED`.
- `components` returns one row per component and sheet instance. A
  `warnings` entry says when `--sheet` matched no sheet instance.
- `verification` is set by the command. No value means the design was
  verified:

  | Command | `verification` |
  |---|---|
  | `summary`, `components`, `component`, `sheet` | `STRUCTURAL_DISCOVERY_ONLY` |
  | `pins` | `LOCAL_GEOMETRY_EVIDENCE_ONLY` |
  | `local-net` | `SHEET_LOCAL_ONLY` |
  | `hier-net` | `HIERARCHICAL_INTERFACE_EVIDENCE_ONLY` |
  | `connected-pins` | `PARENT_CONNECTED_PINS_GEOMETRY_ONLY` |
  | `project-net`, `net` | `INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY` |
  | `instances` | `HIERARCHICAL_INSTANCE_DISCOVERY_ONLY` |
  | any error | `NOT_VERIFIED` |

- `limitations` is also set by the command; report the lines it prints.
- Errors (invalid input, unreadable files, bad bounds, traversal failure) exit
  nonzero with `verification: NOT_VERIFIED`; infer nothing from them.
- Truncation: check `truncated`, `pins_truncated`, `connected_pins_truncated`,
  `matched_by_truncated`, and `names_truncated` before concluding. A truncated
  list cannot show that an item is absent; raise `--limit` (maximum 200).

## Limitations
- Global labels and power symbols connect nets across sheet instances. A
  global label and a power symbol with the same name are one net. A power
  symbol is any symbol whose library symbol has the `(power)` flag; all of
  them are treated as global, including KiCad's local power symbols.
- KiCad 10 does not save `mirror y` at 90 or 270 degrees. It saves that
  placement as the equivalent `mirror x` form (`mirror y` at 90 is
  `mirror x` at 270, and the reverse), which is checked against a KiCad
  netlist. A file from another tool that holds `mirror y` at 90 or 270
  gets the same pin positions as that `mirror x` form.
- Buses, complex symbol inheritance, and hidden connectivity may stay unresolved.
- If a trustworthy parser is unavailable, limit work to transparent observations
  from the target sheet and mark pin-to-net and cross-sheet claims `NOT_VERIFIED`.
  If project-wide proof is essential, say so and ask before using any other route
  (for example `kicad-cli` netlist export).

## Response format
- **Target & scope:** file, sheet instance, object; `LOCAL` / `HIERARCHICAL` / `GLOBAL`.
- **Findings:** result with reference, pin/net, and traceable evidence.
- **Not verified:** unresolved connectivity, missing data, tool limits.
- **Next action:** a focused check or human visual check, only if needed.

For the native `.kicad_sch` file structure, read
[Schematic Data Reference](references/schematic-data.md) only when a query
result has to be checked against the file itself.
