# KiCad 10 Schematic Data Inspection Reference

Use this reference only when `sch-inspect` needs to locate a target or reason about native `.kicad_sch` data. `scripts/query_sch.py` is the tested local,
read-only query tool for bounded structural, geometry, hierarchy, and
conservative project-connectivity evidence. It is **not** a KiCad-equivalent
netlist resolver.

## Data access policy

1. **Read-only.** Do not modify `.kicad_sch`, libraries, or project settings.
2. **Sheet-scoped first.** Locate the specified component, net, or block; inspect its owning schematic file and sheet instance before expanding the scope.
3. **No full-project netlist export by default.** Do not export a whole-project netlist as the normal inspection path. Do not send complete schematic files or large S-expression dumps to the model when a bounded query suffices.
4. **Prefer deterministic extraction.** If a tested local reader is available, request small structured results. Otherwise inspect only necessary excerpts and explicitly mark unverified connectivity; do not pretend a parser exists.
5. **No silent scope expansion.** If a finding needs parent/child sheets or global connectivity, identify why, then load only relevant additional files or return `NOT_VERIFIED`.

## Locating the target

- Read the root sheet's `sheet` entries to find referenced filenames (sheet `Sheetfile` property), then follow the relevant hierarchy as needed.
- The same `.kicad_sch` file may have multiple **sheet instances**. File path alone does not uniquely identify an instance; retain the hierarchical instance UUID path and project when available.
- Symbol `Reference` properties are useful search hints, but instance-specific references and units can be stored under `instances / project / path`. Do not assume a text match identifies the correct physical unit or instance.
- If a reference or sheet is ambiguous, list the candidates instead of arbitrarily selecting one.

## Useful native constructs

| Construct | Why inspect it |
| --- | --- |
| `symbol`, `lib_id`, properties, `unit`, `instances` | Part identity, reference, unit, instance-specific assignment |
| `lib_symbols`, symbol pins | Pin numbers, names, electrical types, and symbol geometry |
| `wire`, `junction`, `no_connect` | Local graphical electrical connections and deliberate unconnected pins |
| `label` | Sheet-instance-local named connections |
| `hierarchical_label`, parent `sheet` pins | Connections across parent-child sheet boundary |
| `global_label`, power symbols | Potential project-wide connections (resolve with appropriate scope) |
| `sheet`, `Sheetfile`, UUID / instance paths | Hierarchy and reused-sheet identity |

A symbol pin-to-net association must account for the symbol definition, unit, transformation, pin coordinates, wires, and connection semantics. **Text proximity or matching label names alone is not proof of connectivity.**

## Inspection scope and evidence

- **LOCAL:** Target sheet instance, its symbols, wires, labels, and local connections.
- **HIERARCHICAL:** LOCAL plus explicitly resolved parent/child sheet pins and hierarchical labels.
- **GLOBAL:** Relevant cross-sheet global labels and power-symbol connections, with complete enough coverage for the asserted result.
- Mark the *achieved* scope, not just the requested scope. If a tool cannot resolve a required edge, use `NOT_VERIFIED` for that claim.
- Keep evidence traceable: schematic filename, sheet instance path (when relevant), reference, pin number, label/net, and source of any datasheet claim.

## Minimal result format

Return a short human-readable report; structured query tools may use this shape:

```yaml
target: U12
source_file: powerSupplies.kicad_sch
sheet_instance: null    # fill with resolved path when known
scope_requested: LOCAL
scope_achieved: LOCAL
findings: []
unverified:
  - "Cross-sheet connectivity not inspected"
evidence: []
```

The example is a **format illustration**, not an actual inspection result. Prefer brief findings and only expand individual nets or neighboring components when necessary. Do not turn unchecked items into `PASS`.

## Current query-tool contract

`scripts/query_sch.py` accepts a resolved root schematic through `--project`
and supports exactly these commands: `summary`, `component`, `sheet`, `pins`,
`local-net`, `hier-net`, `connected-pins`, `project-net`, and `instances`.
Use absolute or otherwise correctly quoted paths; this is required for Windows
and macOS paths containing spaces.

Successful responses use the bounded top-level fields `mode`, `target`,
`root`, `results`, `total_matches`, `truncated`, `missing_sheets`,
`skipped_outside_project`, `verification`, `limitations`, and `warnings`.
`project-net` reports `PROJECT_CONNECTIVITY_EVIDENCE`,
`TARGET_NOT_FOUND_OR_UNRESOLVED`, or `AMBIGUOUS_TARGET_NETS` in its result,
and sets `project_net_verified` to false. Report either unresolved status as
`NOT_VERIFIED`; do not convert absent, ambiguous, or truncated evidence into a
connection claim. Errors emit JSON with `verification: NOT_VERIFIED`.

The current parser has targeted fixtures for malformed input, bus-label
isolation, reused-sheet instances, cycles and file bounds, multi-unit and
inherited symbols, and truncation. Native KiCad comparison remains necessary
before calling any connectivity result parity or electrical correctness.

## References

- KiCad Schematic File Format: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
- KiCad S-expression format: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/
