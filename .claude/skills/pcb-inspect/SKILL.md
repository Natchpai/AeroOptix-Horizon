---
name: pcb-inspect
description: >-
  Inspects and explains KiCad 10 PCB layout data in read-only mode: footprints,
  pads, nets, tracks, vias, placement, and distances in the saved .kicad_pcb.
  Use when the user asks to inspect, locate, or measure a footprint, pad, net,
  trace, via, or board area. Targeted queries only; it extracts evidence and
  does not judge the layout.
argument-hint: "[summary | footprint <ref> | pads <ref> | net <name> | tracks <net> | vias <net> | nearby <ref> | pad-distance <ref.pin> <ref.pin>]"
---

# PCB Inspection

## Scope and safety
- Read-only: do not modify PCB, project, library, or design-rule files.
- Operate independently of any formal review framework.
- The saved `.kicad_pcb` is the source of truth; disclose that unsaved editor
  changes may exist.
- Never claim a check passed without supporting data and a stated method.
- Do not assume a parser, IPC connection, or local DRC capability exists; verify
  tools before using them. Never present an unimplemented mode as available.

## Commands (v1.0, Stable (Scoped))
Run `scripts/query_pcb.py` (Python 3.10+, standard library). Resolve the script
and board paths first.

`python <skill dir>/scripts/query_pcb.py <command> [targets] --board <file.kicad_pcb> [--limit 20]`

| Command | Purpose |
|---|---|
| `summary` | Board metadata, layers, footprint counts, bounded samples. |
| `footprint <ref>` | Saved placement, rotation, side, library ID, UUID. |
| `pads <ref>` | Pad numbers, shapes, sizes, saved net, board-space centres. |
| `net <name>` | Saved footprint/pad assignments of a net. |
| `tracks <net>` | Saved segments and arcs on one net, with length. |
| `vias <net>` | Saved via position, size, drill, layers, type. |
| `nearby <ref>` | Other footprints by distance between saved origins. |
| `pad-distance <ref.pin> <ref.pin>` | Distance between two pad centres. |

`--limit` is 1-1000. For `tracks` and `vias`, an empty quoted target (`""`)
requests unconnected items. States such as `AMBIGUOUS_REFERENCE`, `AMBIGUOUS`,
`MISSING`, `UNCONNECTED`, `ASSIGNED_WITHOUT_DECLARATION`, `NOT_FOUND` and
`NOT_VERIFIED` are distinct results, not passes. Read
[references/cli.md](references/cli.md) for exact semantics when interpreting
output.

Not implemented (do not offer as commands): extended `component`, `area`, `check`
(DRC is not a local check). If no mode is given, infer the smallest useful scope.

## Procedure
1. Identify the project, target, question, and scope.
2. Locate the target with the cheapest read-only method; prefer the CLI or native
   `.kicad_pcb` queries over loading the file.
3. Return only relevant geometry and connectivity: footprints, pads, nets,
   tracks, vias, layers, applicable constraints.
4. Expand to connected regions, stackup, or datasheet guidance only when needed;
   datasheet content comes from the user, official web pages or cited
   NotebookLM answers (no direct PDF reads).
5. If structural data is insufficient, request a targeted visual inspection, not
   an export of the whole board.
6. Report with references, net and layer names, coordinates, evidence, and
   unresolved checks.

## Verification boundaries
- Saved zone outlines are not filled copper; do not assume fills are current.
- DRC results do not establish signal integrity, power integrity, EMI, thermal
  performance, or manufacturability. No reported violation is not proof of
  correctness.
- Distance alone does not prove decoupling effectiveness. Origin and pad-centre
  distances are not package or copper clearances, routed length, or timing length.
- Track lengths are single saved primitives, not routed-path or return-path length.
- A via's geometry and shared net do not prove it contacts a given track, pad,
  zone, or layer. A shared net name is an assignment lookup, not copper continuity.
- Unrecognized constructs, filled-zone state, stackup, copper contact, and
  anything not safely parsed remain `NOT_VERIFIED`.

## Context and output
- Never put the complete board file, full track list, or unfiltered DRC report in
  context. Limit to the target, summarize large sets, state truncation, and offer
  a scoped expansion.
- Output: **Target / Scope**, **Findings**, **Evidence**, **Limitations / NOT_VERIFIED**,
  **Recommended next checks**.
- Create no reports, temporary exports, caches, or other files unless authorized.
- Test commands for maintainers are in [references/testing.md](references/testing.md);
  golden evidence is in `references/2phase-synchbuck-golden-evidence.md`.
