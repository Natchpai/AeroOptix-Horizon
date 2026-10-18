---
name: component-check
description: >-
  Checks and compares one or two electronic components used in a KiCad design,
  read-only, with evidence. Use when the user asks to verify a part number
  (MPN), datasheet, ratings, pinout, schematic symbol, footprint, package,
  pad-to-pin mapping, BOM entry, or a possible replacement part. Not for
  project-wide library link checks.
argument-hint: "[<reference> | <MPN> | compare <MPN1> <MPN2>]"
---

# Component Check

## Scope and safety
- Read-only: KiCad files, libraries, BOMs and design records stay unchanged.
- Check only the reference, MPN or pair the user asked about.
- Use the manufacturer datasheet and package drawing for the exact variant and revision, and name the source.
- A footprint name, pin count, ERC result or similar-looking package does not prove compatibility.
- Every datasheet value, stock status and check result needs a source.

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
1. Resolve `$ARGUMENTS` or the request into a reference, an MPN, or a pair of MPNs. For a KiCad reference, find its sheet instance and read only the relevant properties from the native `.kicad_sch` data, not a full-project netlist.
2. Resolve the exact manufacturer and orderable MPN, including package and suffix. If it is ambiguous, list the candidate identities and let the user pick. If the reference is not found, report `NOT_VERIFIED`; you may list similar references, but do not choose one.
3. Get the needed datasheet sections and package drawing from an allowed source. For a PDF, use NotebookLM only after the user approves: pin the notebook, and quote the cited table or pin text for the exact MPN. Record source and revision, or say the document could not be checked.
4. Pick the checks the question needs:
   - **Identity/BOM:** manufacturer, MPN, value, variants and orderable package.
   - **Electrical:** absolute maximum ratings versus recommended operating conditions, limits, tolerances and derating.
   - **Symbol:** pin numbers, names, functions, power pins, special or multiplexed pins, and omitted pins.
   - **Footprint:** package variant, pad count and numbers, pin-1 orientation, dimensions and land pattern versus the exact datasheet package.
   - **Substitution:** electrical, functional, pinout, footprint and operating-condition compatibility; list the design changes it would need.
5. Compare only the evidence you have for those checks. For a pin-to-net connection, get targeted connectivity from the saved schematic (with `sch-inspect` if installed); nearby text or labels are not a connection.
6. For PCB pad, net or geometry evidence, use targeted board queries (with `pcb-inspect` if installed). For symbol, footprint and 3D-model links across the project, `hw-link-audit` helps if installed. If a companion skill is missing, say so and do the check directly or mark it `NOT_VERIFIED`.
7. Report each finding with its evidence source, the specific mismatch or limit, and the next action.

## Result format
- **Target:** reference or MPN, and the scope inspected.
- **Checks:** `PASS`, `FAIL`, `WARNING` or `NOT_VERIFIED`, each with a short reason. `PASS` needs evidence for that check.
- **Evidence:** datasheet revision, table or pin section, and CAD references when available.
- **Action:** the correction to consider, or the human check needed.

## Example
```text
Target:   U7 (MPN as in BOM), symbol pins 1-8
Checks:   Pinout vs datasheet pin table  PASS   (pins 1-8, via NotebookLM, cited)
          Footprint land pattern         NOT_VERIFIED (package drawing not available)
          Absolute max VIN               WARNING (6 V max; net VIN_5V can reach 5.5 V, margin 0.5 V)
Evidence: datasheet rev C, table 5 and package drawing section; schematic U7 pins
Action:   Provide the package drawing values, then re-run the footprint check.
```

## Efficiency
- Start with part metadata and only the datasheet sections the request needs.
- Load datasheets, BOMs, symbol libraries and PCB files in targeted parts, not whole.
- Use supporting files or scripts only when they exist and apply. Write files only when the user asks.
