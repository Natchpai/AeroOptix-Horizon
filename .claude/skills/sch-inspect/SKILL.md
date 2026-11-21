---
name: sch-inspect
description: >-
  Inspects and explains KiCad 10 schematics from native .kicad_sch files:
  components, pins, nets, labels, buses, hierarchical sheets, and sheet instances.
  Use when the user asks to inspect, trace, or explain schematic circuits,
  connections, or functional blocks. Targeted, read-only; it extracts evidence
  and does not judge the design.
argument-hint: "[summary | components [--sheet <name>] [--prefix <p>] | component <ref> | pins <ref> | local-net <ref> | hier-net <ref> | connected-pins <ref> | project-net <ref> --pin <n> | net <name> | bus [name] | instances | sheet <name> | netlist <net|ref> | netlist-compare]"
---

# Schematic Inspection (KiCad 10)

## Evidence baseline

- Label each significant claim `VERIFIED` (named evidence: CAD data, a
  calculation or an official source), `ASSUMED` (assumption stated),
  `ESTIMATED` (method and margin stated) or `NOT_VERIFIED` (evidence missing
  or check not run).
- Datasheet, schematic and PCB PDFs are not read, by any tool. Project report
  PDFs may be read.
- Datasheet values come from the user, official manufacturer web pages, or
  NotebookLM answers with cited text. Query an existing notebook without
  asking. Adding a source or creating a notebook uploads a file and needs the
  user's approval. With no source, the value is `NOT_VERIFIED`.
- KiCad design and library files are read-only. Propose changes; do not apply
  them.
- If the project has `.claude/rules/engineering.md` and `pdf.md`, follow them;
  they are the full policy.

## Rules
- Treat `.kicad_sch`, `.kicad_pro`, libraries, and all other CAD files as
  read-only. Do not create indexes, reports, caches, or other files unless asked.
- Start from the requested sheet or instance; read the least data needed. Do not
  default to a full-project scan. Use the netlist commands only when the user
  asks for a netlist check; do not use them as the normal inspection method
  or as a silent fallback.
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
  `/Power/+5V`. A bus member name (for example `SPI_CLK` from `{SPI}`) is a
  net name; a bus name is not.
- `bus <name>` takes a bus label or sheet pin name (`{SPI}`, `D[0..7]`,
  `P{A B}`) or an alias name (`SPI` also matches `{SPI}`). Without a name it
  lists every bus name and alias.
- `netlist` and `netlist-compare` read KiCad's own netlist. Run them only
  when the user asks for a netlist check or a check against KiCad. They run
  `kicad-cli sch export netlist --format kicadxml` on the saved root sheet
  and write the export to a temporary folder only. `--kicad-cli <path>` picks
  the binary (default: the `KICAD_CLI` variable, then `PATH`, then the usual
  install folders); `--netlist <file.xml>` reads an export the user made and
  runs nothing.

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
| `bus [name]` | Bus members, the sheets each member reaches, and its pins; no name lists buses and aliases. |
| `netlist <net|ref>` | KiCad netlist nodes of a net (full name or last path part), or every net on a reference. |
| `netlist-compare` | Every multi-pin KiCad net against the `project-net` graph; lists the nets where the pin sets differ. |

Examples (root file `Top.kicad_sch`):
- `component U103 --project Top.kicad_sch`
- `project-net U103 --pin 8 --project Top.kicad_sch`
- `net +5V --project Top.kicad_sch`
- `components --sheet "Power State" --prefix U --project Top.kicad_sch`
- `bus "{SPI}" --project Top.kicad_sch`
- `netlist-compare --project Top.kicad_sch` (only when asked for a KiCad netlist check)

Policy: prefer `component`, `pins`, or `local-net`; use `hier-net` or
`connected-pins` when hierarchy matters; use `project-net` only when
project-level evidence is required, with a specific pin for multi-net parts.
Use `net` when the question starts from a net name, `bus` when it starts from
a bus, and `components` when it starts from a sheet or a part type.
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
`HIERARCHICAL`; `project-net`, `net` and `bus` give `GLOBAL`. `summary`,
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
- `project-net` and `net` results also hold `bus_links`: each bus member
  the net passes through (`bus_names`, `members`, `instance_path`, `file`,
  `member_net_on_sheet`), with `bus_links_truncated`.
- `bus <name>` returns one result per connected bus:
  `BUS_CONNECTIVITY_EVIDENCE` with `occurrences` (each sheet instance, the
  bus names there, and `members_resolved`: false when a plain name sits on
  that bus, which gives it no members, as in KiCad) and `members`. Each member has `member_names`, `sheets`
  (`member_net_on_sheet` false means no net on that sheet carries the member
  name), and the evidence fields of `project-net`. No match returns
  `BUS_NAME_NOT_FOUND`; report it as `NOT_VERIFIED`. `bus` without a name
  returns one row per bus name (`kind: bus_name`) and alias (`kind: alias`,
  with `used_by`). A name on a bus that is not a bus name gives a `warnings`
  entry.
- `components` returns one row per component and sheet instance. A
  `warnings` entry says when `--sheet` matched no sheet instance.
- `netlist <target>` returns `KICAD_NETLIST_NET` rows (`net_name`,
  `matched_by` net or reference, `nodes` with reference, pin number, pin
  function and type, `netlist_tool`, `netlist_source`), or
  `NET_OR_REFERENCE_NOT_FOUND`.
- `netlist-compare` returns `NETLIST_COMPARISON_SUMMARY` first (nets and pins
  compared, `differences`), then one `NETLIST_DIFFERENCE` per mismatch:
  `kind: split` (KiCad joins pins that `sch-inspect` keeps apart or misses:
  `pins_missing_in_sch_inspect`) or `kind: merged` (`sch-inspect` joins pins
  that KiCad keeps apart). A difference is a finding to read in KiCad, not
  proof that either tool is wrong. Zero differences is `VERIFIED` evidence
  that the `project-net` graph matches KiCad for every multi-pin net of the
  saved files, not that the design is correct.
- `verification` is set by the command. No value means the design was
  verified:

  | Command | `verification` |
  |---|---|
  | `summary`, `components`, `component`, `sheet` | `STRUCTURAL_DISCOVERY_ONLY` |
  | `pins` | `LOCAL_GEOMETRY_EVIDENCE_ONLY` |
  | `local-net` | `SHEET_LOCAL_ONLY` |
  | `hier-net` | `HIERARCHICAL_INTERFACE_EVIDENCE_ONLY` |
  | `connected-pins` | `PARENT_CONNECTED_PINS_GEOMETRY_ONLY` |
  | `project-net`, `net`, `bus` | `INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY` |
  | `instances` | `HIERARCHICAL_INSTANCE_DISCOVERY_ONLY` |
  | `netlist` | `KICAD_NETLIST_EVIDENCE` |
  | `netlist-compare` | `KICAD_NETLIST_COMPARISON` |
  | any error | `NOT_VERIFIED` |

- `limitations` is also set by the command; report the lines it prints.
- Errors (invalid input, unreadable files, bad bounds, traversal failure) exit
  nonzero with `verification: NOT_VERIFIED`; infer nothing from them.
- Truncation: check `truncated`, `pins_truncated`, `connected_pins_truncated`,
  `matched_by_truncated`, `names_truncated`, `bus_links_truncated`,
  `members_truncated`, `occurrences_truncated`, `sheets_truncated`,
  `candidate_labels_truncated` and `parent_labels_truncated` before
  concluding. A truncated
  list cannot show that an item is absent; raise `--limit` (maximum 200).

## Limitations
- Wires join as in KiCad 10 (checked against KiCad 10.0.8 netlists): a symbol
  pin or a wire end joins a wire only at that wire's end, or at a junction on
  it; labels and sheet pins join anywhere on a wire; crossings never join.
  Labels of any kind (local, global, hierarchical) with one name are one net
  on a sheet instance.
- Global labels and power symbols connect nets across sheet instances. A
  global label and a power symbol with the same name are one net. A power
  symbol is any symbol whose library symbol has the `(power)` flag. A
  `(power local)` symbol is one net per sheet instance.
- In a reused sheet, each instance uses the unit its instance entry names.
- KiCad 10 does not save `mirror y` at 90 or 270 degrees. It saves that
  placement as the equivalent `mirror x` form (`mirror y` at 90 is
  `mirror x` at 270, and the reverse), which is checked against a KiCad
  netlist. A file from another tool that holds `mirror y` at 90 or 270
  gets the same pin positions as that `mirror x` form.
- Buses (`project-net`, `net`, `bus`) follow the KiCad 10 rules, checked
  against KiCad 10.0.8 netlists: a bus member joins every net on that sheet
  with a label (local, global or hierarchical) of the member name, with or
  without a bus entry; a wire on a bus entry without such a label is not a
  member. A parent sheet pin on a bus meets the child hierarchical label of
  the same name; vector members match by index (`D[0..1]` to `DATA[0..1]`),
  group members by short name (`P{A B}` to `Q{A B}`; members are `P.A`,
  `P.B`). Global bus labels of one name are one bus. Aliases come from
  `<project>.kicad_pro` (`schematic.bus_aliases`) and from `bus_alias` forms
  in sheets; a malformed `.kicad_pro` is an error. An alias expands only in
  braces (`{SPI}`); a bare alias name is a plain net name. Members with one
  name on one sheet are one net, and members of a global bus are global. Not resolved: bus-to-bus
  entries, and member names held only by a power symbol or a sheet pin.
  `pins`, `local-net`, `hier-net` and `connected-pins` do not follow buses.
- Complex symbol inheritance and hidden connectivity may stay unresolved.
- If a trustworthy parser is unavailable, limit work to transparent observations
  from the target sheet and mark pin-to-net and cross-sheet claims `NOT_VERIFIED`.
  If project-wide proof is essential, say so and offer `netlist-compare` (it
  runs `kicad-cli`); run it only when the user agrees.

## Response format
- **Target & scope:** file, sheet instance, object; `LOCAL` / `HIERARCHICAL` / `GLOBAL`.
- **Findings:** result with reference, pin/net, and traceable evidence.
- **Not verified:** unresolved connectivity, missing data, tool limits.
- **Next action:** a focused check or human visual check, only if needed.

For the native `.kicad_sch` file structure, read
[Schematic Data Reference](references/schematic-data.md) only when a query
result has to be checked against the file itself.
