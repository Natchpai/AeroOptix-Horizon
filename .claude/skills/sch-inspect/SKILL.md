---
name: sch-inspect
description: >-
  Inspects and explains KiCad 10 schematics from native .kicad_sch files:
  components, pins, nets, labels, hierarchical sheets, and sheet instances.
  Use when the user asks to inspect, trace, or explain schematic circuits,
  connections, or functional blocks. Targeted, read-only; it extracts evidence
  and does not judge the design.
argument-hint: "[summary | component <ref> | pins <ref> | local-net <ref> | hier-net <ref> | connected-pins <ref> | project-net <ref> --pin <n> | instances | sheet <name>]"
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
- Never claim `PASS` for an incomplete check; use `NOT_VERIFIED` with the missing
  evidence. Never infer electrical correctness from structure or geometry.
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
- `--limit` also truncates pins and connected pins; check the `*_truncated`
  flags before concluding.
- There is no command to list or search components by prefix. When the user
  describes a part ("the first IC") instead of giving a reference, use
  `summary` and ask which reference or sheet they mean; do not guess
  designators one by one.

| Command | Purpose |
|---|---|
| `summary` | Sheets and component counts. |
| `component <ref>` | Locate a component; its properties. |
| `sheet <name>` | Locate a hierarchical sheet. |
| `pins <ref>` | Symbol pins with local wire/label geometry. |
| `local-net <ref>` | Sheet-local wires, junctions, labels, power symbols. |
| `hier-net <ref>` | Hierarchical interfaces to parent sheet connections. |
| `connected-pins <ref>` | Connected component and sheet pins across supported hierarchy. |
| `instances` | Hierarchical sheet instances and reused sheet files. |
| `project-net <ref> --pin <n>` | Connectivity evidence across instances, global labels, power nets. |

Examples (root file `Top.kicad_sch`):
- `component U103 --project Top.kicad_sch`
- `project-net U103 --pin 8 --project Top.kicad_sch`

Policy: prefer `component`, `pins`, or `local-net`; use `hier-net` or
`connected-pins` when hierarchy matters; use `project-net` only when
project-level evidence is required, with a specific pin for multi-net parts.
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
   and power nets. A repeated local label in separate sheet instances is not
   globally connected.
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
`HIERARCHICAL`; `project-net` gives `GLOBAL`-level evidence only (still not
netlist parity). `summary`, `component`, `sheet`, and `instances` are
structural discovery below `LOCAL`.

Report the scope actually verified, not the one requested, if expansion failed.
`PASS` needs sufficient validated evidence for that specific check; otherwise
use `WARNING`, `FAIL`, or `NOT_VERIFIED`. Distinguish observed from suspected.

## JSON contract
- Every successful command returns `mode`, `target`, `root`, `results`,
  `total_matches`, `truncated`, `missing_sheets`, `skipped_outside_project`,
  `verification`, `limitations`, and `warnings`.
- `project-net` returns one result: `PROJECT_CONNECTIVITY_EVIDENCE` (source pin,
  connected pins, label/power evidence, truncation flags, limitations), or
  `TARGET_NOT_FOUND_OR_UNRESOLVED` / `AMBIGUOUS_TARGET_NETS`. Report either
  unresolved status as `NOT_VERIFIED`; it does not show a connection is absent.
  `project_net_verified` is always false: it is not KiCad netlist parity.
- `verification` varies by command: `STRUCTURAL_DISCOVERY_ONLY`,
  `LOCAL_GEOMETRY_EVIDENCE_ONLY`, `INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY`, or
  `NOT_VERIFIED`; none of them means the design was verified. A generic
  limitation line in `project-net` output does not override its instance-aware
  evidence, but report both.
- Errors (invalid input, unreadable files, bad bounds, traversal failure) exit
  nonzero with `verification: NOT_VERIFIED`; infer nothing from them.
- Honour `truncated`, `pins_truncated`, `connected_pins_truncated`, and
  `names_truncated`: a truncated result is not a complete enumeration.

## Limitations
- `summary`, `component`, `sheet`: structural discovery only.
- `pins`, `local-net`: local geometry evidence. `hier-net`, `connected-pins`:
  bounded parent/interface geometry evidence.
- `project-net`: conservative, instance-aware evidence through supported wires,
  labels, hierarchy, global labels, and power symbols; not netlist parity.
- Global labels and power symbols may connect nets across sheet instances.
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

For native file structure and evidence rules, read
[Schematic Data Reference](references/schematic-data.md) only when needed.
