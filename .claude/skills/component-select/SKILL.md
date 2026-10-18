---
name: component-select
description: >-
  Finds and shortlists electronic parts by engineering fit: requirements,
  operating conditions, trade-offs and availability. Use when the user asks to
  choose an IC or component, find alternatives or a replacement for an obsolete
  part, or decide which candidate fits a circuit best. Not for supplier stock
  and price or a spec table.
argument-hint: "[requirements | function | existing MPN]"
---

# Component Selection

Help the engineer reach a part choice they can defend. **Search broadly;
recommend narrowly.** This skill sets the selection process, not a catalog of
preferred parts.

## Boundaries

- Propose changes to BOMs, symbols, footprints or project settings; do not
  apply them.
- Search across vendors, part families, topologies and packages unless the
  design fixes one. Include parts the user already stocks when they ask for
  that.
- Primary evidence: current manufacturer datasheets, product pages, errata and
  lifecycle notices. Stock, lead time and price come from authorized
  distributors, with region, quantity, date and uncertainty stated.
- Design to **recommended operating conditions**. Absolute maximum ratings are
  limits, not design targets.
- Every MPN, orderable suffix, datasheet figure, price, stock count and pin
  compatibility claim needs a source. Mark it `NOT_VERIFIED` when the source is
  missing.
- Return a ranked shortlist, not an open-ended catalog.
- Read only the documentation sections the current decision needs.

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

1. **Define the function and constraints.** Pull operating ranges, interfaces,
   electrical stress, temperature, accuracy, noise, speed, package, assembly,
   supply chain, cost and lifecycle needs from the request and the circuit
   context. Split hard requirements from preferences. Ask only for a missing
   constraint that would change the decision; otherwise state an assumption.
2. **Find candidates.** Search several manufacturers and, where useful,
   different implementation approaches. Start with parametric search,
   manufacturer technical material and application notes. Check the exact
   **orderable MPN**, not only the family name.
3. **Apply hard filters first.** Reject candidates that fail a mandatory
   functional, electrical, environmental, interface, package or lifecycle
   constraint. A missing critical spec is `NOT_VERIFIED`, not PASS. Score or
   weigh candidates only after the hard filters.
4. **Compare survivors.** Performance at the real operating conditions,
   tolerances and derating, external parts, board area, PCB complexity,
   thermal limits, documentation, availability, sourcing risk, cost at the
   user's quantities, and migration effort. Calculate where it helps and state
   assumptions and worst cases.
5. **Check integration risks.** Suffix and package differences, pin functions,
   exposed-pad needs, startup behavior, sequencing, protection, stability,
   layout needs and errata. When the user already has a part, say whether a
   candidate is a functional alternative, pin-compatible, or a drop-in
   replacement, and claim interchangeability only with evidence.
6. **Recommend a shortlist.** Two or three real choices: best overall fit, a
   strong alternative, and a cost or availability option when it matters. Say
   why the top part wins, what it gives up, and what would change the decision.
7. **Stop when the choice holds.** Stop once the hard constraints are met, the
   key trade-offs are clear, the main integration risks are checked, and an
   adequate alternative exists. Search further only if the evidence is weak or
   a clearly better candidate is likely.

## Optional companions

- `stock-select`: when supplier stock, price or JLCPCB assembly decides between
  survivors. Stock never overrides an engineering constraint.
- `component-check`: deep check of a chosen MPN, symbol and pinout, footprint
  and package, BOM entry, or substitution.
- `sch-inspect`: targeted as-designed schematic evidence.
- `eng-calc`: sizing, stress, thermal and tolerance checks.

These help if installed. If one is missing, do the step directly under the
same evidence rules, or mark the dependent check `NOT_VERIFIED`.

## Output

1. **Decision context:** function, hard constraints, preferences, assumptions.
2. **Shortlist:** exact manufacturer and MPN, the parameters that separate the
   candidates, trade-offs, and evidence links or datasheet sections.
3. **Disposition:** `RECOMMENDED`, `ALTERNATIVE`, `REJECTED` or `NOT_VERIFIED`,
   with the reason. Show the evidence label on each critical claim.
4. **Next verification:** only the most important open datasheet, electrical,
   footprint, thermal or sourcing checks before design commitment.

If no candidate passes the hard constraints, say so and name the constraint or
architecture choice that might need to change. An unverified part is never
"approved".

## Example

```text
Context:   3V3 LDO from 5 V, 300 mA load, -40 to 85 C, SOT-23-5 preferred (ASSUMED from request)
Shortlist: <MPN A> | RECOMMENDED | dropout below 1.7 V headroom at 300 mA (VERIFIED, maker page) | lowest quiescent current
           <MPN B> | ALTERNATIVE | pinout same as A (NOT_VERIFIED) | second source
           <MPN C> | REJECTED    | 200 mA max output, below the 300 mA load (VERIFIED, maker page)
Next:      check B's pinout against A's datasheet before using it as a second source.
```
