---
name: progress-update
description: Update the spec, checklist, design records, README and CHANGELOG from saved CAD data, git history and decisions stated in this session.
argument-hint: "[since <git-ref|YYYY-MM-DD>] [ignore <ref|lib>...]"
disable-model-invocation: true
---

# Progress Update

Bring a KiCad project's Markdown docs in line with the saved design. Inputs
are the saved KiCad files, git history, and decisions the human stated in this
session. Outputs are Markdown edits only. The human keeps every design
decision, the phase, and every git action.

`<skills dir>` below is the folder that holds this skill. Sibling skills
(`sch-inspect`, `pcb-inspect`, `hardware-checklist`, `hw-git-readme`,
`hw-git-changelog`) are used when installed there; when one is missing, do
that part by hand and say so in the report.

## Rules
- KiCad files and project libraries are read-only. Report that you read the
  **saved** files; the editor may hold unsaved changes.
- Evidence and findings follow `.claude/rules/engineering.md` when the project
  has it. Otherwise label each statement `VERIFIED`, `ASSUMED`, `ESTIMATED` or
  `NOT_VERIFIED`, and write one line per finding:
  `SEVERITY | ref / net | label | statement | source`.
- Tag every part you report as one of:
  - **DECISION**: the human chose it in this session. Quote their words. Only
    a DECISION gets a decision-record row.
  - **DRAWN**: it is in the CAD data but nobody stated a choice. Record it as
    "drawn, not decided" and give it an open item.
- Copy the phase and status as they are. Report a mismatch between documents
  instead of resolving it.
- Leave out every `ignore` item (a reference, value or library) from findings
  and docs.
- Datasheet values come only from user-supplied text, official web pages or
  cited NotebookLM answers. PDFs stay closed.
- Write plain English: short sentences, exact names (refs, nets, part
  numbers), no em dash.

## Steps

### 1. Find the project
- **KiCad project:** `git ls-files '*.kicad_pro'`. The root schematic is the
  `.kicad_sch` with the same name. Several projects: ask which one.
- **Docs:** search the repo's Markdown files (skip `.claude/`):
  - spec: name contains `SPEC`, or the first heading says "Specification"
  - checklist: name contains `CHECKLIST`
  - design records: the other Markdown files next to the spec
  - `README.md` and `CHANGELOG.md` at the repo root

  A doc that is missing stays missing: report it as `MISSING` and skip it.
- **Since point:** the argument; else the spec's "Last updated" or "Updated"
  date; else the last commit that touched the spec.

Done when you know the project folder, root schematic, each doc path (or
`MISSING`), and the since point.

### 2. Baseline
```bash
git log --oneline --since=<date>            # or <ref>..HEAD
git diff --name-only <ref> -- <project dir>
git status --short -- <project dir>
```
Done when you have the list of changed `.kicad_sch` / `.kicad_pcb` files, lib
table changes, and new library items.

### 3. Collect
- **Sheets:** for each changed sheet, list its parts and labels:
  `python -I <skills dir>/progress-update/scripts/list_symbols.py <sheet.kicad_sch>`.
  Then trace each IC and connector with `sch-inspect`
  (`query_sch.py local-net <ref> --project <root.kicad_sch>`). Unannotated
  refs such as `U?` work as targets; the tool returns every match.
- **PCB:** if `.kicad_pcb` changed, run `pcb-inspect` `summary`.
- **Library:** list new symbol, footprint and 3D model names. Suggest
  `/kicad-link-audit`; leave it to the human to run.
- **Session:** list each design decision the human stated, with a quote.

Done when every changed sheet has a state table (block, as drawn, evidence)
and every part in it is tagged DECISION or DRAWN.

### 4. Findings
Check each changed sheet for:
- power nets with no source (a rail used but never driven)
- LCSC or MPN fields that conflict with the Value, or one code on two values
- unannotated references
- labels that reach nothing
- parts a checked datasheet recommends that are missing

Done when each finding has a severity, a label and its evidence.

### 5. Confirm
If a stated decision is ambiguous ("maybe X", "try X"), ask once with
AskUserQuestion: DECISION or DRAWN. Otherwise go on.

### 6. Update docs
Edit in this order so each fact has one home and the others point to it.
Read each file first. Reuse its ID prefixes, tables and headings; new rows
take the next unused ID. Where a doc has no place for a fact, add the smallest
fitting row or table and mention it in the report.

1. **Spec:** revision and date; the confirmed part-number list; decision
   rows; component-constraint rows for decided parts; a "Schematic state"
   table under the matching architecture section; open-item rows; change-note
   row; verdict or status summary line.
2. **Checklist:** follow `hardware-checklist` update rules. Revision and date;
   task status (`DONE` needs an evidence record and the human's
   confirmation); tasks for new work; a tracker row for each new open item;
   the next-action line.
3. **Design records:** edit only the ones the change touches (power budget for
   regulators and rails, selection records for part choices, pin allocation
   for MCU pins). Change rows; keep their labels.
4. **README:** follow `hw-git-readme` update mode. Sync the spec revision,
   features, specifications table, open-items summary and documentation links.
5. **CHANGELOG:** follow `hw-git-changelog`. Add entries under
   `[Unreleased]` and state the verification status.

Done when every decision and open item added to the spec also appears in the
checklist, the README and the CHANGELOG (for each doc that exists).

### 7. Check
```bash
git diff -U0 | grep -cP '^\+.*\x{2014}'     # em dashes added: must be 0
git diff --stat
```
Also confirm that every new open item has a checklist tracker row, and every
decision and open-item ID you cite exists in the spec.

### 8. Report
- Target and scope: project, sheets read, since point, saved-file note.
- Findings, most severe first.
- Doc changes, one line per file; docs `MISSING`.
- Not changed, with the reason (phase, records not touched, ignored items).
- A proposed commit message, for example
  `docs(design): record <topic> and <sheet> state`.

Stop there. Staging, committing and pushing wait for the human.
