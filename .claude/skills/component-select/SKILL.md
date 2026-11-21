---
name: component-select
description: >-
  Finds and shortlists electronic parts by engineering fit: requirements,
  operating conditions, trade-offs and availability, and builds a spec
  comparison table of candidates, one column per part number. Use when the
  user asks to choose an IC or component, find alternatives or a replacement
  for an obsolete part, decide which candidate fits a circuit best, or wants a
  spec comparison table. Not for supplier stock and price.
argument-hint: "[requirements | function | existing MPN] | table <MPN> [<MPN> ...] | table add <MPN>"
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

## Table mode: spec comparison for given part numbers

Use it when the user gives candidates and wants a spec table (`table <MPN>
...`), or adds a part to an existing one (`table add <MPN>`). One column per
part, one row per spec. It compares; it does not pick a winner unless asked.

Rules (on top of the evidence baseline):
- Every cell has an evidence label; a cell with no source is `NOT_VERIFIED`.
  Leave no blank. Give the source in the cell or in a list under the table.
- Keep recommended operating values and absolute maximum values in separate
  rows, and name which one a row holds. Use one unit per row.
- Say which row decides the choice.
- Keep every row and every `NOT_VERIFIED` cell; a summary may add to the
  table, not replace it.
- Write the file only when asked, in the KiCad project's existing documents
  folder (near the `.kicad_pro`); if there is none or more than one, ask once.
  Keep one file per topic and update it.
- Pad the first column of every table to its longest cell, with matching
  separator dashes; leave the other columns unpadded.

Steps: get the exact orderable MPNs and the use case. Pick the rows that
matter (usually 15 to 25), always including status, interface, supply range
(VDD and I/O), package and size, footprint match to the main candidate,
operating temperature, the key performance numbers, and driver or software
support when it applies; add the project's spec rows (`SEN-*`, `PWR-*`) that
apply, and reuse an existing table's rows. Adding a part adds a column and
leaves the others unchanged. End with the `NOT_VERIFIED` cells and how to
close them. Price and stock go in `stock-select` table mode, same column order.

```text
| Parameter      | <MPN 1> | <MPN 2> | (new P/N) |
| -------------- | --- | --- | --- |
| Manufacturer   | name | name | |
| Product status | Production `VERIFIED` | `NOT_VERIFIED` | |
| Supply range   | 1.71 to 3.6 V `VERIFIED` | `NOT_VERIFIED` | |
| Package        | LGA-14 2.5x3 mm `VERIFIED` | ... | |
```
