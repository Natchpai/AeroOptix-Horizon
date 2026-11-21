---
name: progress-update
description: Update the spec, checklist, design records, README and CHANGELOG from saved CAD data, git history and decisions stated in this session. Modes: full (default), light (spec and checklist only, during DRAFT), sync (catch up the other docs before a commit).
argument-hint: "[light | sync] [since <git-ref|YYYY-MM-DD>] [ignore <ref|lib>...]"
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
- The review (step 4) only proposes. Never close an open item, change a task
  or gate status, or drop a summary line without the human's answer in step 5.

## Modes

The first argument picks the mode. The rules above apply in every mode.

| Mode | Use it for | Steps | Docs edited |
| ---- | ---------- | ----- | ----------- |
| full (default) | A full catch-up, or any work in CHECK or RELEASE | 0 to 8 | All, step 6 |
| `light` | Recording decisions and drawing changes as they happen in DRAFT or PRELIMINARY | 0 to 8, with the light lines in 3, 6 and 8 | Spec and checklist only |
| `sync` | Right before a commit, after one or more `light` runs | 0, 6 (sync), 7, 8 | Design records, README, CHANGELOG |

- Read the phase from `README.md`. `light` and `sync` run only when it says
  `DRAFT` or `PRELIMINARY`. In any other phase, or if the phase is missing,
  run full mode and say why in the report.
- **Open revision:** a spec change-note row that is not in `HEAD`
  (`git diff HEAD -- <spec>` shows it as added). The spec and checklist each
  get at most one open revision. A run that finds one adds to it and keeps
  its revision number. A run that finds none adds one new revision. This
  gives one revision per commit instead of one per decision.
- A `light` run leaves README, CHANGELOG and the design records behind on
  purpose. `sync` catches them up from `git diff HEAD` of the spec and
  checklist, so `light` needs no notes or marker files.

## Steps

### 0. Preflight
Run the deterministic checks first, from the repo root:
```bash
python -I -X utf8 <skills dir>/progress-update/scripts/progress_preflight.py [--since <ref>]
```
It prints one JSON: project, spec and checklist paths, since point, commits,
changed files by kind, per-sheet parts, library checks, doc checks, a
`review` count and a `findings` list. The review checks every open spec item,
every checklist task and gate status, and the summary lists against the
spec, checklist, README and saved schematic fields (`review:*` findings, see
step 4). Use it for steps 1, 2, the sheet and library parts of 3, the
listed checks in 4, and 7. Read the JSON, not the KiCad files, for anything it
covers. Options:
- `--project <file.kicad_pro or folder>` when the repo has several projects
  (run from inside a project folder also picks it).
- `--spec <md>` and `--checklist <md>` when the names do not contain `SPEC`
  and `CHECKLIST` (the spec is also found by an H1 that says
  "Specification").
- `--id-prefixes DEC,OPEN,...` when the spec's ID prefixes are not found right
  (default: short or zero-padded IDs in the first column of table rows).
  `--open-prefix` (default `OPEN`) and `--tracker-prefix` (default `OI`) set
  the open-item and checklist tracker IDs. With no tracker rows in the
  checklist, the spec's open-item table is the register, and preflight checks
  that each open row names an active checklist task (`open_without_task`).
- `--pin-text SYMBOL=<fulltext.txt>` (for example a NotebookLM
  `source fulltext` dump) to match a new symbol's pins against its datasheet.

If it prints `"verification": "NOT_VERIFIED"` with an `error` (several
projects, no git, bad ref), fix the option it names or report the error and
do steps 1 to 4 by hand.
`--since` takes a git ref only; for a date, find the ref with
`git log -1 --before=<date> --format=%h`.

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
Preflight keys `commits`, `changed_by_kind` and `uncommitted`. By hand:
```bash
git log --oneline --since=<date>            # or <ref>..HEAD
git diff --name-only <ref> -- <project dir>
git status --short -- <project dir>
```
Done when you have the list of changed `.kicad_sch` / `.kicad_pcb` files, lib
table changes, and new library items.

### 3. Collect
- **Sheets:** preflight `sheets` lists each sheet's parts and labels. By
  hand: `python -I <skills dir>/progress-update/scripts/list_symbols.py <sheet.kicad_sch>`.
  Then trace each IC and connector with `sch-inspect`
  (`query_sch.py local-net <ref> --project <root.kicad_sch>`). Unannotated
  refs such as `U?` work as targets; the tool returns every match.
- **PCB:** if `.kicad_pcb` changed, run `pcb-inspect` `summary`.
- **Library:** list new symbol, footprint and 3D model names (preflight
  `library`: pins against pads, missing 3D models, unresolved links). Suggest
  `/kicad-link-audit`; leave it to the human to run.
- **Session:** list each design decision the human stated, with a quote.

`light`: compare against the spec's current "Schematic state" rows and trace
only the parts and nets that differ from them. If the human only stated a
decision and no sheet changed since the open revision, skip the sheet trace.

Done when every changed sheet has a state table (block, as drawn, evidence)
and every part in it is tagged DECISION or DRAWN.

### 4. Findings
Preflight `findings` already covers: one LCSC code on two values,
unannotated references, single-use local labels, no `PWR_FLAG`, board parts
with no footprint, unresolved symbol or footprint links, pin and pad
mismatches and missing 3D models. Read its `limitations` list: without the
global KiCad library tables, stock links are not checked.
Copy those rows; each is `[severity, check, item, detail]` and its evidence
is the saved file, so label it `VERIFIED` with "preflight" as the source.

Check by hand, because they need connectivity or a datasheet:
- power nets with no source (a rail used but never driven), with `sch-inspect`
- LCSC or MPN fields that conflict with the Value
- labels that reach nothing on any sheet (preflight sees one sheet at a time)
- parts a checked datasheet recommends that are missing

**Review of open items, status and lists.** Preflight `review:*` rows are
`INFO` questions, not defects. Each means "this may be stale":

| Check | Means |
|---|---|
| `review:tasks_closed` | Every task an open item names is `DONE` or `N/A`. |
| `review:newer_dec` | A DEC on or after the row's newest date cites the item (or the open item a task waits on), and the row does not cite that DEC. |
| `review:field_filled` | The text waits for MFR, MFR.P/N, LCSC or a footprint field that is filled on every part it names (or every BOM part). |
| `review:ref_missing` | The still-open text names a reference that is not in the saved schematic, or an unannotated one. |
| `review:rev_drift` | A cited record revision (or the README spec revision) differs from the record's header. |
| `review:status_mismatch` | A task is `DONE` with no evidence, or a gate status does not match its tasks. |
| `review:summary_cites_closed` | The spec "Current verdict", the checklist "Current next action" or the README "Open Items" calls a closed item open. |

Read the row behind each one and drop false hits (a DEC that only mentions
the item, a field word used in another sense). Report the rest under their
own heading with the stale text and the evidence. Each is `VERIFIED` only for
what it compares; whether the item is done is the human's call.

Done when each finding has a severity, a label and its evidence.

### 5. Confirm
If a stated decision is ambiguous ("maybe X", "try X"), ask once with
AskUserQuestion: DECISION or DRAWN.

For each `review:*` finding kept in step 4, ask with AskUserQuestion, up to 4
per call. Quote the stale text and the evidence, and offer: close the item or
set the new status (name it, for example `DONE`), re-point it to another task,
or keep it as it is. Record the answer with the human's words. Otherwise go
on.

### 6. Update docs
Edit in this order so each fact has one home and the others point to it.
Read each file first. Reuse its ID prefixes, tables and headings; new rows
take the next unused ID. Where a doc has no place for a fact, add the smallest
fitting row or table and mention it in the report.

1. **Spec:** revision and date (open-revision rule in Modes); the confirmed part-number list; decision
   rows; component-constraint rows for decided parts; a "Schematic state"
   table under the matching architecture section; open-item rows, each with
   its owner and the checklist task that closes it; change-note row; verdict
   or status summary line.
2. **Checklist:** follow `hardware-checklist` update rules. Revision and date
   (open-revision rule);
   task status (`DONE` needs an evidence record and the human's
   confirmation); tasks for new work, including one for each new open item
   that no task covers yet; a tracker row for each new open item only if the
   checklist keeps a tracker table; the next-action line.
3. **Design records:** edit only the ones the change touches (power budget for
   regulators and rails, selection records for part choices, pin allocation
   for MCU pins). Change rows; keep their labels.
4. **README:** follow `hw-git-readme` update mode. Sync the spec revision,
   features, specifications table, open-items summary and documentation links.
5. **CHANGELOG:** follow `hw-git-changelog`. Add entries under
   `[Unreleased]` and state the verification status.

**Review answers (step 5):** apply only what the human chose, in the same
order:
- Close an open item: start its description with
  `Closed <date>: <reason, the human's words>` and set the owner cell to
  `Closed`.
- Re-point an item: change its owner cell to the new task.
- Change a task or gate status: set the status and put the evidence record in
  the last cell. `DONE` needs both.
- Fix a stale summary line or revision number.
- Note each change in the open change-note row (open-revision rule), and
  carry closed items into the README open-items list and the CHANGELOG.

Done when every decision and open item added to the spec also appears in the
checklist, the README and the CHANGELOG (for each doc that exists).

**`light`:** do items 1 and 2 only, using the open-revision rule in Modes:
the revision and date change only when a new revision starts; otherwise add
to the open change-note row. Skip items 3 to 5. Done when every decision and
open item added to the spec names its checklist task (and has a tracker row,
if the checklist keeps a tracker table).

**`sync`:** read `git diff HEAD` of the spec and checklist and treat every
added or changed DEC and OPEN row as input. Do items 3 to 5 for them, and set
the README spec revision to the open revision. Leave the spec and checklist
as they are, except for a broken cross-reference. If there is no open
revision, say that nothing needs syncing and stop. `sync` skips steps 4 and
5, so list any `review:*` rows in the report for the next full or `light`
run instead of acting on them. Done when every DEC and
OPEN row in that diff also appears in the README and the CHANGELOG, and every
design record that owns an affected value is updated.

### 7. Check
Run preflight again with `--findings-only` and the same `--since`. It reads
the working tree, so it sees your edits. No `em_dash`, `undefined_id`,
`no_tracker_row`, `open_without_task` or `broken_link` row may be new, and
`review:*` rows may remain only for items the human chose to keep. Then:
```bash
git diff --stat
```
By hand, if preflight failed:
```bash
git diff -U0 | grep -cP '^\+.*\x{2014}'     # em dashes added: must be 0
```
and confirm that every new open item names an active checklist task (and has
a tracker row, if the checklist keeps a tracker table), and every
decision and open-item ID you cite exists in the spec.

### 8. Report
- Target and scope: project, sheets read, since point, saved-file note.
- Findings, most severe first.
- Review: n found, n closed or changed by the human, n kept, n dropped as
  false hits.
- Doc changes, one line per file; docs `MISSING`.
- Not changed, with the reason (phase, records not touched, ignored items).
- A proposed commit message, for example
  `docs(design): record <topic> and <sheet> state`.

`light` report, at most 10 lines: the IDs added or changed, the open revision
number, MAJOR and CRITICAL findings in full, a count of MINOR and INFO
findings, the review count, the step 7 result, and the line "README, CHANGELOG and design
records not synced; run `/progress-update sync` before committing." No commit
message.

Stop there. Staging, committing and pushing wait for the human.
