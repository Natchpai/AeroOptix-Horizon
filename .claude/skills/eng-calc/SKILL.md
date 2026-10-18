---
name: eng-calc
description: >-
  Performs, checks, or audits engineering calculations for electronic
  hardware. Use when the user asks to calculate component values, power,
  current, voltage, timing, filters, control parameters, losses, thermal
  behavior, tolerances, margins or worst cases, or to check an existing
  equation or result.
argument-hint: "[calculation | specifications | equation to verify]"
---

# Engineering Calculations

Give calculations another engineer can audit. This skill sets a **calculation
method**, not a formula bank, a topology, a component value or a part choice.

## Boundaries

- Name the quantity and the physical model before choosing equations. Use a
  formula only inside its assumptions (for example ideal converter,
  steady state, CCM, small-signal).
- Keep **given**, **derived**, **assumed** and **datasheet** values apart. Every
  rating, parasitic, material parameter or test value needs a source; ask for
  it or mark it `NOT_VERIFIED`.
- Use SI units throughout, convert prefixes explicitly where mistakes are
  likely, and say whether a value is peak, RMS, average, instantaneous or
  rated.
- Absolute maximum ratings are limits, not operating points. Include
  tolerances, derating, temperature, transients and margins when they change
  the answer.
- When an assumption changes the answer, give a range or a conditional result,
  not one falsely precise number.
- A calculated result is an **estimate, not hardware verification**. Claims of
  compliance, safety, thermal adequacy or design closure need source data and
  independent validation.
- Read KiCad files with targeted, read-only queries. Write files only when the
  user asks.
- Cite only sources you actually read.

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

1. **Define the target.** The quantity, operating mode, constraints, available
   inputs and needed accuracy. Ask only for a fact without which the answer
   would mislead; otherwise state a bounded assumption.
2. **Choose and justify the model.** State the equations and the conditions
   under which they hold. Add non-ideal effects where they matter.
3. **Normalize inputs.** Show units, prefixes and operating ranges, and mark
   each value as nominal, worst case or manufacturer-specified.
4. **Calculate reproducibly.** Substitute values and check dimensions. Use a
   calculator or local Python for error-prone numbers, sweeps, optimization,
   matrices or several operating points. Report a number from code only after
   the code has run.
5. **Check the result.** Limiting cases, signs, dimensions, conservation laws
   and physical sense. Cross-check with an independent method when an error
   would be costly.
6. **Check sensitivity.** Min, nominal and max conditions, tolerances,
   temperature, losses, derating and parameter uncertainty, where they apply.
   Find the worst case; do not assume it sits at nominal.
7. **Report evidence and limits.** Keep math correctness, model validity and
   measured performance apart. Mark missing evidence `NOT_VERIFIED`.

## Optional companions

- `design-assist`: calculations compare architectures; a formula alone does
  not choose the architecture.
- `component-select`: turn calculated limits into device requirements. One
  matching parameter does not pick an MPN.
- `stock-select`: sourcing comes after technical fit.
- `component-check`: actual datasheet ratings, tolerances, operating
  conditions and package limits.
- `sch-inspect`: targeted schematic facts; inferred connectivity stays
  unverified.

These help if installed. If one is missing, do the step directly under the
same evidence rules, or mark the dependent check `NOT_VERIFIED`.

## Output

Match the size of the answer to the request. For a real calculation:

1. **Inputs and assumptions:** values with units and the operating range.
2. **Model and equations:** formulas, conditions and limits.
3. **Results:** values with sensible precision and units; a compact table for
   several operating points. Label each result `ESTIMATED` and state the
   method and margin.
4. **Checks and implications:** sanity checks, margins, sensitivity, and the
   next evidence the design decision needs. Mark critical unknowns
   `NOT_VERIFIED`.

For simple arithmetic, give the result and the key assumptions only. When the
user supplies an equation to review, check its derivation and conditions
before substituting numbers.

## Example

```text
Inputs:  R = 10 kOhm +/-1%, C = 100 nF +/-10% (given); first-order RC low-pass, no load (ASSUMED)
Model:   fc = 1 / (2 pi R C)
Results: fc nominal 159 Hz | ESTIMATED | exact formula, nominal values
         fc range 143 to 179 Hz | ESTIMATED | R and C at tolerance extremes
Checks:  C tolerance dominates; C temperature drift NOT_VERIFIED (dielectric unknown).
```
