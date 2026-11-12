---
name: sch-review
description: >-
  Reviews an electronic schematic or a focused circuit block for engineering
  correctness, risks, missing protection, component suitability and design
  assumptions. Use when the user asks for a schematic review, a circuit design
  check, a power or signal-path review, or an assessment of a KiCad schematic
  before PCB layout. Not for looking up schematic data only.
argument-hint: "[sheet | subsystem | reference | concern]"
---

# Schematic Engineering Review

Review the **engineering design**, not just the schematic's structure. Pick the
checks from the circuit's purpose and constraints, not from a fixed topology,
manufacturer or device checklist.

## Boundaries

- KiCad schematic, project, library, BOM and review records are read-only.
  Recommend changes to symbols, connectivity, review status or approvals; do
  not apply them.
- The review covers the saved `.kicad_sch` files. A
  `~<project>.kicad_pro.lck` file means KiCad has the project open, so the
  editor may hold unsaved changes; say so in the report.
- A targeted review rates the inspected scope only. It is not a project-wide
  PASS, a gate closure, or part of a formal review framework.
- Query the requested block or concern only. Use targeted queries, not full
  schematic dumps or a full netlist export.
- Keep schematic evidence, calculations, datasheet requirements, inferences
  and unknowns apart. An unsupported or ambiguous connection is
  `NOT_VERIFIED`.
- Matching net labels, a parser's proposed connection, ERC success, or no
  visible errors do not show electrical correctness.
- Check part-specific claims against the actual MPN and current documentation.
- Changes, purchases, commits, reports and logs happen only when the user asks
  and the repository rules allow them.
- ERC, simulation, lab measurement, PCB checks and formal release are separate
  activities. Recommend them where needed and say they were not performed.

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
- If the project has `.claude/rules/engineering.md`, follow it; it is the full
  policy.

## Workflow

1. **Scope the review.** The block's intended function, its known operating
   range, and the review goal. Prefer the user's specific concern over a
   project-wide sweep. Ask for a missing constraint only if going on without it
   would mislead; otherwise state the assumption.
   Look for the project's specification or requirements record (for example
   the output of `hardware-specification`). If there is one, read the entries
   for the block in scope and cite the requirement, decision or open-item ID
   (for example `PWR-001`) in each finding it relates to. If there is none,
   the operating range is `ASSUMED`; state it in the report.
2. **Collect targeted evidence.** Query the saved `.kicad_sch` (with
   `sch-inspect` if installed) for the relevant symbols, pins, local,
   hierarchical and project connectivity, and instance paths. Start from the
   target type:

   | Target | Start with |
   |---|---|
   | Sheet | `components --sheet <name>`, then `pins` or `local-net` per reference |
   | Subsystem | `components --sheet <name> --prefix <p>` or `net <name>` to find the parts, then confirm the list with the user |
   | Reference | `component <ref>` and `pins <ref>`, then `project-net <ref> --pin <n>` as needed |
   | Concern | `net <name>`, or the references the concern names |

   Without `sch-inspect`, ask the user for the references, or read the
   sheet's symbol list from the `.kicad_sch` directly.
   Record the scope the queries actually covered and any parser limits. Ask for a human
   visual check where native data cannot settle a question.
3. **Account for every pin.** For each IC in scope, run `local-net <ref>` (`pins <ref>` does not print the
   status) and put
   every pin of every unit in one group by its `local_connection_status`:
   - connected: `LOCAL_WIRE_PATH` or `LABEL_ANCHOR_ONLY`
   - no-connect: `NO_CONNECT_MARKER`
   - unresolved: `NO_LOCAL_CONNECTION_FOUND`, `CONFLICTING_NO_CONNECT`, no
     status, or a truncated pin list

   Compare no-connect and strap pins with the datasheet: may the pin float,
   and which level does the strap need. Unresolved pins go to the
   `NOT_VERIFIED` section, not to a pass. Without `sch-inspect`, name the
   source of the pin list, or mark pin coverage `NOT_VERIFIED`.
4. **Rebuild the intended behavior.** Signal and power path, operating modes,
   startup and shutdown, interfaces, expected loading and fault cases for the
   block. Being wired is not the same as working.
5. **Choose risk-based checks.** Operating limits, component stress, power
   paths, decoupling, biasing, pull-ups and pull-downs, protection, feedback
   stability, timing, signal integrity, grounding, sequencing and interface
   compatibility, as they apply. Report only the checks you actually ran.
6. **Check calculations and components.** Calculate stress, tolerance,
   thermal, timing or worst-case numbers; check pin mapping, MPN, package and
   datasheet requirements. Look at alternatives or sourcing only when the user
   asks for them, or a finding cannot be resolved without them.
7. **Challenge assumptions.** Test at least one adverse condition where it
   applies: input extremes, transients, reverse current, reset, an unpowered
   interface, startup or a short circuit. Keep a demonstrated defect apart
   from a plausible risk that needs more evidence.
8. **Report and stop.** Lead with actionable findings and targeted next checks.
   Stop at the requested scope. Where evidence is missing, report the gap
   instead of a verification result.

## Findings

Give each finding a severity and a status:

- **Severity:** `CRITICAL` (credible hazard or severe defect with clear
  evidence), `MAJOR` (likely functional or reliability issue), `MINOR`
  (bounded margin or documentation issue) or `INFO` (observation, not a
  defect). Severity rates the individual finding, not the whole schematic.
- **Status:** **Confirmed defect** (direct CAD, datasheet or calculation
  evidence shows a specific mismatch), **Potential risk** (a plausible concern
  that lacks the constraint, model or inspection to confirm it), or
  **Undecided** (the evidence is not enough to decide; **not** a PASS or
  FAIL).

The evidence label rates the observation; the status rates the conclusion
drawn from it. A `VERIFIED` observation can still be a Potential risk.

State uncertainties plainly, and keep hypothetical worst cases as risks, not
proven faults.

## Optional companions

- `sch-inspect`: scoped structural evidence. Its `project-net` results are not
  full KiCad netlist or ERC parity. Respect its limits on buses, inherited
  symbols, hidden connectivity and ambiguous instances.
- `eng-calc`: auditable equations, units, tolerances and worst cases.
- `component-check`: datasheet and physical mapping of a chosen device.
- `component-select` and `stock-select`: alternatives and sourcing.
- `design-assist`: architecture alternatives when the review raises a basic
  design-choice question.

These help if installed. If one is missing, do the step directly under the
same evidence rules, or mark the dependent check `NOT_VERIFIED`.

## Output

Match the size of the output to the requested review. For a full review:

1. **Target and scope:** block or sheet, operating assumptions, evidence
   reviewed, and the requirements record used (or that none was found).
2. **Findings:** one row per finding: severity, reference/pin/net, evidence
   label, statement, and source or calculation, then the named fields
   `Status:`, `Req:` (left out when no requirement applies), `Impact:` and
   `Action:`.
3. **NOT_VERIFIED:** missing requirements, ambiguous connectivity, unchecked
   datasheet data, or untested behavior.
4. **Next checks:** a short, ordered list of the visual checks, calculations,
   simulations, ERC runs or measurements that would close the gaps.

Example finding row:

```text
MAJOR | U3 pin 4 / EN | VERIFIED | EN is tied to VIN through R12 only; no divider for UVLO | local-net query, datasheet table 6 (NotebookLM) | Status: Potential risk | Req: PWR-003 | Impact: startup below the intended input voltage | Action: add a divider or confirm the intended threshold
```

If no supported issue is found, say **"No issue found within the inspected
scope"**, not "schematic verified" or "ready for fabrication".
