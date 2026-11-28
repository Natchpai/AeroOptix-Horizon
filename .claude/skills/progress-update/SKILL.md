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
(`sch-inspect`, `pcb-inspect`, `hardware-checklist`, `hw-docs`) are used
when installed there; when one is missing, do that part by hand and say so in
the report.

**One history.** The spec change-note table is the design history. The
checklist, README and CHANGELOG point to spec IDs and revisions; they do not
repeat the decision or open-item text.

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

## Rules
- Report that you read the **saved** KiCad files; the editor may hold unsaved
  changes.
- Write one line per finding: `SEVERITY | ref / net | label | statement | source`.
- Tag every part you report as one of:
  - **DECISION**: the human chose it in this session. Quote their words. Only
    a DECISION gets a decision-record row.
  - **DRAWN**: it is in the CAD data but nobody stated a choice. Record it as
    "drawn, not decided" and give it an open item.
- Copy the phase and status as they are. Report a mismatch between documents
  instead of resolving it.
- Leave out every `ignore` item (a reference, value or library) from findings
  and docs.
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

### 0. Preflight and tier
Run the deterministic checks first, from the repo root:
```bash
python -I -X utf8 <skills dir>/progress-update/scripts/progress_preflight.py [--since <ref>]
```
It prints one JSON: paths, since point, commits, changed files, the change
`tier`, sheet counts, library checks, doc checks and `findings` (`review:*`
rows, step 4). Use it for steps 1, 2, 3 and 7; read the JSON, not the KiCad
files, for anything it covers. `tier` comes from `sch-inspect diff` against
the since point, with ERC when it asks (`tier.erc`). The tier caps the work:

| Tier | Netlist change | Work |
|---|---|---|
| 0 | none (wire, label, text, PCB only) | No trace, ERC or doc edit. At commit, one CHANGELOG line: "schematic cleanup, no connectivity change". Stop unless a decision was stated. |
| 1 | fields or net names only | No trace. Edit only rows that state a changed value. |
| 2 | parts or pin groups | Trace only the parts and nets the tier lists. |
| 3 | the human states a decision (`tier3_hints` only suggest one) | All steps. |

`tier: NOT_VERIFIED` (no `kicad-cli` or `sch-inspect`): work as tier 3 and
say why. `--tier-only` prints just the tier; run it when the human says they
edited the schematic. Options:
- `--project <file.kicad_pro or folder>` when the repo has several projects.
- `--spec <md>` and `--checklist <md>` when the names do not contain `SPEC`
  and `CHECKLIST` (the spec is also found by an H1 that says
  "Specification").
- `--id-prefixes DEC,OPEN,...` when the spec's ID prefixes are not found right
  (default: short or zero-padded IDs in the first column of table rows).
  `--open-prefix` (default `OPEN`), `--dec-prefix` (default `DEC`) and
  `--tracker-prefix` (default `OI`) set the open-item, decision and checklist
  tracker IDs. With no tracker rows in the
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
- **Since point:** the argument (a date becomes a ref, see step 0); else the
  last commit that touched the spec, as preflight does; else `HEAD`.

Done when you know the project folder, root schematic, each doc path (or
`MISSING`), and the since point.

### 2. Baseline
Preflight keys `commits`, `changed_by_kind` and `uncommitted`; if preflight
failed, use `git log`, `git diff --name-only <ref>` and `git status --short`
on the project folder. Done when you have the changed CAD, library table and
library files.

### 3. Collect
- **Sheets (tier 1 and up):** regenerate the state record with
  `python -I <skills dir>/progress-update/scripts/sch_state.py --project <root.kicad_sch> --out <spec dir>/schematic-state.md`.
  At tier 2, trace only the listed parts and nets with `sch-inspect`
  (`query_sch.py local-net <ref> --project <root.kicad_sch> --limit 0`).
- **PCB:** if `.kicad_pcb` changed, run `pcb-inspect` `summary`.
- **Library:** list new symbol, footprint and 3D model names (preflight
  `library`). Items marked `human_checked` (schematic `STATUS` `CHECKED`) are
  not checked again; `human_check_older_than_file` means the file changed
  after the check. For the rest, suggest `/kicad-link-audit`.
- **Session:** list each design decision the human stated, with a quote.

Done when the state record is current and every changed part is tagged
DECISION or DRAWN.

### 4. Findings
Preflight `findings` already covers: one LCSC code on two values,
unannotated references, single-use local labels, no `PWR_FLAG`, board parts
with no footprint, unresolved symbol or footprint links, pin and pad
mismatches and missing 3D models. Read its `limitations` list: without the
global KiCad library tables, stock links are not checked.

It also covers the table structure (`register.py lint`, also runnable alone:
`python -I register.py lint --spec <md> --checklist <md>`):

| Check | Means |
|---|---|
| `duplicate_id` | A DEC, OPEN, REF, task or gate ID is defined twice (INFO). |
| `bad_status` | A task status is not `OPEN`, `IN_PROGRESS`, `BLOCKED BY <ID>`, `DEFERRED`, `DONE` or `N/A`. |
| `closed_no_date` | A closed open item does not start with `Closed <YYYY-MM-DD>:` (INFO). |
| `rev_order` | Change-note revisions out of order, or the spec header is not the newest row. |
| `long_task` | Task text over 600 characters; keep the statement, `Left:` and the current state, and move history to the spec change-note (INFO). |
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
| `review:newer_dec` | A DEC on or after the row's newest date cites the item (or the open item a task waits on), and the row does not cite that DEC. A cite that names items (`OPEN-031 item 5`) counts only for rows that name one of those items. |
| `review:field_filled` | The text waits for MFR, MFR.P/N, LCSC or a footprint field that is filled on every part it names (or every BOM part). |
| `review:ref_missing` | The still-open text names a reference that is not in the saved schematic, or an unannotated one. |
| `review:rev_drift` | A cited record revision (a task, the checklist header, a spec REF row, or the README spec revision) differs from the record's header. |
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
   rows; component-constraint rows for decided parts; a link to
   `schematic-state.md` (do not copy part lists); open-item rows, each with
   its owner and the checklist task that closes it; change-note row; verdict
   or status summary line.
2. **Checklist:** follow `hardware-checklist` update rules. Revision and date
   (open-revision rule);
   task status (`DONE` needs an evidence record and the human's
   confirmation); tasks for new work, including one for each new open item
   that no task covers yet; a tracker row for each new open item only if the
   checklist keeps a tracker table; the next-action line.
3. **Design records:** edit only records that own a changed value (power
   budget for rails, selection records for part choices, pin allocation for
   MCU pins). A row that only names a reference is not stale; records cite
   nets and pins. Keep their labels.
4. **README:** follow `hw-docs` readme update mode. Sync the spec revision,
   features, specifications table, open-items summary and documentation links.
5. **CHANGELOG:** follow `hw-docs` changelog mode. Add **one pointer line per
   spec revision** under `[Unreleased]`, for example
   `- Specification rev 0.81 (2026-11-21): P2-016, P2-021, P4-011; see the change-note.`
   (the IDs the revision added or changed). Schematic, PCB, library and
   website commits get their own short lines. Do not copy change-note text.

**Review answers (step 5):** apply only what the human chose, in the same
order:
- Close an open item: start its description with
  `Closed <date>: <reason, the human's words>` and set the owner cell to
  `Closed`.
- Re-point an item: change its owner cell to the new task.
- Change a task or gate status: set the status and put the evidence record in
  the last cell. `DONE` needs both.
- Fix a stale summary line or revision number.
- Note each change in the open change-note row (open-revision rule), drop
  closed items from the README open-items list, and name them in the
  revision's CHANGELOG pointer line.

Done when every decision and open item added to the spec is named by its
checklist task, the README summary (when it is a top item) and the
CHANGELOG pointer line (for each doc that exists).

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
run instead of acting on them. Done when the open revision has its CHANGELOG
pointer line, the README summary names the top open items, and every design
record that owns an affected value is updated.

### 7. Check
Run preflight again with `--findings-only --no-tier` and the same `--since`. It reads
the working tree, so it sees your edits. No `em_dash`, `undefined_id`,
`no_tracker_row`, `open_without_task`, `broken_link`, `bad_status`,
`rev_order` or `duplicate_id` row may be new, and
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
