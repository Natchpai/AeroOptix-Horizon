---
name: design-assist
description: >-
  Designs or improves electronic hardware from functional requirements to
  architecture and circuit-level trade-offs. Use when the user asks how to
  design a circuit or subsystem, compare design approaches, choose a topology
  or interface, or review design assumptions before parts are chosen. Not for
  picking a specific part.
argument-hint: "[design objective | subsystem | requirements]"
---

# Hardware Design Assistance

Help the engineer reach a design approach they can defend, starting from the
real requirements. This skill sets **how to approach a design**, not **which
device or topology to use**.

## Boundaries

- Pick the approach from the requirements. Compare more than one manufacturer,
  circuit family or architecture unless the design already fixes one.
- Propose changes to files, parts, BOM or review state; do not apply them.
- An assumption stays an assumption; do not turn it into a requirement.
- Device-specific claims need the current datasheet, errata, application note
  or standard for that device or revision. Cite it, and keep recommended
  operating conditions apart from absolute maximum ratings.
- Reasoning, calculation and structural inspection do not show that a design
  is safe, compliant, production-ready or validated. Name the check that would.
- Load only the evidence the decision needs: the target sheet, section or
  page, not whole projects or catalogs.
- Stay in the scope the user asked for. Early design help does not start a
  schematic review, PCB review, purchase or documentation task.

## Evidence baseline

- Label each significant claim `VERIFIED` (named evidence: CAD data, a
  calculation or an official source), `ASSUMED` (assumption stated),
  `ESTIMATED` (method and margin stated) or `NOT_VERIFIED` (evidence missing
  or check not run).
- Never open or read a PDF. Datasheet values come from the user, official
  manufacturer web pages, or NotebookLM answers with cited text, used only
  after the user approves uploading the file. With none of these, the value is
  `NOT_VERIFIED`.
- KiCad design and library files are read-only. Propose changes; do not apply
  them.
- If the project has `.claude/rules/engineering.md`, follow it; it is the full
  policy.

## Workflow

1. **Frame the problem.** Get the function, interfaces, input and output
   ranges, operating modes, environment, performance targets, cost, assembly
   and the user's priorities. Split hard constraints from preferences. Ask only
   for a missing fact that would change the design; otherwise state a bounded
   assumption and go on.
2. **Read existing context.** For a redesign or an ongoing project, use
   targeted schematic evidence and the user's design notes. Partial data does
   not show that an existing circuit is correct.
3. **List viable approaches.** Compare topologies, architectures and
   implementation methods on complexity, efficiency, noise, thermal stress,
   control, reliability, manufacturability and maintenance, as they apply.
   Do not lock in a part yet.
4. **Check operating conditions.** Nominal and worst case, tolerances,
   transients, startup and shutdown, fault states, protection and margins.
   Show equations, units and assumptions.
5. **Look up critical evidence.** Device limits, interface requirements,
   reference designs, standards and layout guidance, only where they change the
   decision. Claim a source only after you have actually read it.
6. **Converge.** Recommend one approach: why it wins, what was rejected and
   why, key parameters, risks, and the few checks that matter next. Stop when
   the recommendation and its main risks are stated.
7. **Separate design from validation.** Name the inspection, simulation,
   measurement or review that would confirm the design. Untested behavior is
   not `PASS`.

## Optional companions

- `component-select`: candidate devices for the chosen approach. Keep part
  catalogs out of this skill.
- `stock-select`: when sourcing, price, quantity or JLCPCB assembly is a
  constraint. Stock is not design fit.
- `component-check`: verify a chosen MPN, package, pin mapping and integration
  needs.
- `sch-inspect`: targeted schematic evidence; its connectivity results are
  scoped and may be `NOT_VERIFIED`.
- `eng-calc`: auditable calculations, worst cases and tolerances.

These help if installed. If one is missing, do the step directly under the
same evidence rules, or mark the dependent check `NOT_VERIFIED`.

## Output

Give only what the decision needs:

1. **Requirements and assumptions:** hard constraints, preferences, unknowns.
2. **Recommendation:** the approach and why.
3. **Engineering basis:** calculations, source-backed limits and trade-offs,
   each with its evidence label.
4. **Risks and next checks:** the highest-priority open questions, tests or
   checks. Mark unsupported critical claims `NOT_VERIFIED`.

If more than one approach stays viable, give a short comparison and a
conditional recommendation ("buck if X, LDO if Y"). If the requirements
conflict, name the conflict before choosing parts.

## Example

```text
Requirements: 12 V in (ASSUMED +/-10%), 3V3 at 600 mA peak.
Recommendation: synchronous buck. LDO rejected on heat.
Basis:  LDO loss = (13.2 V - 3.3 V) x 0.6 A = 5.9 W at max input | ESTIMATED | too much for a small SMD package without a heatsink
        Buck at an ASSUMED 85% efficiency: about 0.35 W loss | ESTIMATED | efficiency NOT_VERIFIED until a part is chosen
Risks:  MAJOR | 3V3 | NOT_VERIFIED | Ripple limit for the ADC reference is unknown | ask the engineer
Next:   shortlist buck converters; get the ADC ripple limit.
```
