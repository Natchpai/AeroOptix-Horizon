---
name: pcb-inspect
description: >-
  Inspects and explains KiCad 10 PCB layout data in read-only mode: footprints,
  pads, nets, tracks, vias, zones, placement, and distances in the saved
  .kicad_pcb. Use when the user asks to inspect, locate, or measure a footprint,
  pad, net, trace, via, zone, or board area. Targeted queries only; it extracts evidence and
  does not judge the layout.
argument-hint: "[summary | footprint <ref> | pads <ref> | nets [--match <text>] | net <name> | tracks <net> | vias <net> | zones <net> | nearby <ref> [--layer <l>] [--radius <mm>] | pad-distance <ref.pin> <ref.pin> [--group]]"
---

# PCB Inspection

## Evidence baseline

- Label each significant claim `VERIFIED` (named evidence: CAD data, a
  calculation or an official source), `ASSUMED` (assumption stated),
  `ESTIMATED` (method and margin stated) or `NOT_VERIFIED` (evidence missing
  or check not run).
- Schematic and PCB PDFs are not read, by any tool. Project report PDFs may
  be read.
- Datasheet values come from the user, official manufacturer web pages, or
  NotebookLM answers with cited text. Query an existing notebook without
  asking. Adding a source or creating a notebook uploads a file and needs the
  user's approval. A datasheet PDF is read directly only after the user
  approves that file, citing file, revision, page and table. With no source,
  the value is `NOT_VERIFIED`.
- KiCad design and library files are read-only. Propose changes; do not apply
  them.
- If the project has `.claude/rules/engineering.md` and `pdf.md`, follow them;
  they are the full policy.

## Scope and safety
- Read-only: do not modify PCB, project, library, or design-rule files.
- Operate independently of any formal review framework.
- The saved `.kicad_pcb` is the source of truth; disclose that unsaved editor
  changes may exist.
- Never claim a check passed without supporting data and a stated method.
- Do not assume a parser, IPC connection, or local DRC capability exists; verify
  tools before using them. Never present an unimplemented mode as available.

## Commands (v1.2.0, Stable (Scoped))
Run `scripts/query_pcb.py` (Python 3.10+, standard library). Resolve the script
and board paths first.

`python <skill dir>/scripts/query_pcb.py <command> [targets] --board <file.kicad_pcb> [--limit 20]`

Output is UTF-8 JSON on stdout. Errors, including bad arguments, are UTF-8
JSON on stderr with exit code 2 and `verification: NOT_VERIFIED`; infer
nothing from them.

| Command | Purpose |
|---|---|
| `summary` | Board metadata (including `generator_version`), layers with user names, footprint, net, track, via and zone counts, `Edge.Cuts` bounding box. |
| `footprint <ref>` | Saved placement, rotation, layer, side (`top`/`bottom`), library ID, UUID. |
| `pads <ref>` | Pad numbers, shapes, sizes, rotation, drill, saved net, board-space centres. |
| `nets [--match <text>]` | Net names with pad, track, via and zone counts. |
| `net <name>` | Saved footprint/pad assignments of a net. |
| `tracks <net>` | Saved segments and arcs on one net, with length and per-net totals. |
| `vias <net>` | Saved via position, size, drill, layers, type, and counts per kind. |
| `zones <net>` | Saved zones on one net, including zones inside footprints: layers, priority, outline box, pad connection settings. |
| `nearby <ref> [--layer <l>] [--radius <mm>]` | Other footprints by distance between saved origins. |
| `pad-distance <ref.pin> <ref.pin> [--group]` | Distance between two pad centres. `--group` treats all pads with one number on one footprint (a split exposed pad) as one group and uses the nearest pair. |

`--limit` is 1-1000. For `tracks`, `vias` and `zones`, an empty quoted target
(`""`) requests items with no net. A net name is the full saved name,
including any sheet path such as `/Top/Power Supplies/+5VUSB`; when the exact
name is not known, find it with `nets --match <text>`. For a length, a count
or a width question, read `totals` from `tracks` or `vias`: it covers every
match, so there is no need to raise `--limit` and add up the list. States such as `AMBIGUOUS_REFERENCE`, `AMBIGUOUS`,
`MISSING`, `UNCONNECTED`, `ASSIGNED_WITHOUT_DECLARATION`, `NOT_FOUND` and
`NOT_VERIFIED` are distinct results, not passes. A KiCad 10 board has no net
table, so its nets report `ASSIGNED`; `ASSIGNED_WITHOUT_DECLARATION` means a
net table exists and lacks that name. `MISSING` means no saved item of any
kind uses the name. When `tracks`, `vias` or `zones` finds nothing on a net
that exists on other items (for example an unrouted net), the result is
`NOT_FOUND` with the net's real status and `net_item_counts`. Read
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
- Test commands for maintainers are in [references/testing.md](references/testing.md).
