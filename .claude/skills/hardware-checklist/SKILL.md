---
name: hardware-checklist
description: Create, update, or audit an execution checklist for a hardware or PCB project. Turns specification requirements into gated tasks with owner, status, and required evidence. Use when the user asks for a hardware checklist, work plan, gate list, bring-up plan, or wants to check that every requirement has a task.
argument-hint: "create | update | audit"
---

# Hardware Checklist

Track the work and evidence needed to close each gate of a hardware or PCB project. The checklist is a tracker. It is not an approval record, a verification record, or a phase declaration.

Human engineers keep authority over decisions, approvals, and gate closure.

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
- KiCad design and library files are read-only. Propose changes; do not apply
  them.
- If the project has `.claude/rules/engineering.md` and `pdf.md`, follow them;
  they are the full policy.

## Template

- Use `assets/execution_checklist_template.md` when creating a new checklist.
- Adapt gates, columns, and rows to the project. Remove gates and rows that do not apply.
- Do not modify the template during normal work.

## Modes

- **Create:** Read the specification first. Draft one or more tasks for each requirement or open item that needs work or evidence. Show the draft before writing the file, unless the user asked for the file.
- **Update:** Read the existing checklist first. Change only the rows the user names. Keep IDs, order, and unrelated rows. Never reuse a removed ID.
- **Audit:** Read-only. Compare the checklist with the specification and report:
  - requirement IDs with no task
  - tasks with no requirement or reason
  - `DONE` rows without evidence
  - open items without an owner, or without an active checklist task (not `DONE` or `N/A`)
  - rows that conflict with the specification
  - status cells that do not use the defined task states
  - open-item IDs that do not match the specification

## Audit Output

Report ID coverage and topic coverage separately. ID coverage is a script or exact-match count and is `VERIFIED`. Topic coverage (a requirement is covered by a task that has no ID link) is a judgment and is `ASSUMED`. Do not mix the two.

1. A counts table. Use a script for the counts when the files are large.

   | Check | Result |
   |---|---|
   | Spec requirement IDs linked from the checklist | N of M |
   | Spec decision IDs linked | N of M |
   | Open spec items that name an active checklist task | N of M |
   | Task rows with an owner | N of M |
   | `DONE` rows with a named evidence record | N of M |

2. One line per finding, in this format:

   `SEVERITY | ref | label | statement | source`

   - Severity: `MAJOR` (requirement with no task, or `DONE` with no evidence), `MINOR` (missing detail or mismatch), `INFO` (wording or format). `CRITICAL` is not used here.
   - Label: `VERIFIED` (exact match or script count), `ASSUMED` (judgment), or `NOT_VERIFIED` (not checked).
   - Source: the script, or the spec and checklist sections read.

3. A short list of proposed fixes. Do not apply them. The user chooses which to apply.

## Rules

1. **Source of truth.** Requirements and decisions come from the specification. Do not copy their values into the checklist. Reference the ID (for example `PWR-001`).
2. **Task states.** Use only: `OPEN`, `IN_PROGRESS`, `BLOCKED BY <ID>`, `DEFERRED`, `DONE`, `N/A`. Define them once in a conventions block. Do not put evidence labels in the status column.
3. **Done needs evidence.** Mark `DONE` only when the user states the task is complete and the evidence column names or links the record. A checkbox, file presence, or an ERC/DRC pass is not evidence by itself.
4. **Gates.** Group tasks into gates. Each gate has an exit criterion. Default gates are P0 to P4: requirements, allocation, schematic, PCB and release package, bring-up. Gates are work stages. They are not the project phase (`DRAFT`, `PRELIMINARY`, `CHECK`, `RELEASE`). Never infer or change the project phase.
5. **Owner.** Every row has an owner role (Human owner, Hardware, Software, Fabricator, and so on). Approval and gate-closure rows are owned by the human.
6. **Evidence required.** Say what record closes the row: a table, a log, a review, a measurement. Be specific. Do not invent results.
7. **Deferred work.** Mark non-hardware or later work `DEFERRED` and say who owns it. Say if it does not block the gate.
8. **Open items.** The specification's open-item table is the register. Each open row there names its owner and the checklist task that closes it. The checklist does not keep a second register: one line that points to the spec section is enough. A new open item that no task covers gets a new task. If the specification has no open-item table, keep one short register in the checklist that points to the spec's open-item IDs, without copying their descriptions.
9. **Unknowns.** Use `TBD`. Do not guess owners, dates, or evidence.
10. **Task rows hold the present, not the history.** A task cell has three parts: the task statement, the current state (what is drawn, decided or measured, with spec IDs), and `Left:` with what still closes it. Dated history ("drawn in the 11:38 save, then ...") goes into the spec change-note, not the task cell. Aim for 600 characters or less; `progress-update` preflight lists longer cells as `long_task` (INFO). When a task changes, rewrite the current state and `Left:` instead of appending.

## Keep it short

- Define status values once. Do not repeat them per row.
- One task per row. Keep the task statement to one sentence (rule 10 covers the rest of the cell).
- Table format: pad the first column of every table to the width of its longest cell (header included), so the source lines up. Match the dashes in the separator row to that width. Leave the other columns unpadded.
- Use tables. Remove a column only if it is empty in every row.
- Do not repeat the same fact in the checkpoint, the gate rows, and the specification. State it once.
- Merge tasks that cover the same work. Keep a retired ID as a one-line `N/A` row that names the task it moved to, so links from other records still work. Never reuse it.
- Prefer a few specific tasks over many vague ones.

## Writing style

- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences, and active voice.
- Avoid fancy words, marketing phrases, and AI-style filler.
- Keep standard engineering terms and exact IDs.
- Do not use the em dash (`—`). Use a period, comma, colon, or parentheses.
- Use `TBD` for open values. Do not mix it with other spellings.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Boundaries

- Do not open, parse, assess, or generate PDF content.
- Keep KiCad design and library files read-only.
- Do not run ERC or DRC, claim their results, or treat a pass as proof of correctness.
- Do not mark a task done, approve a gate, or declare a phase for the human.
- Do not stage, commit, or push. Git actions need separate approval.
- Do not create logs, manifests, or other files that were not requested.

## Output

Report the file written, the rows added or changed, and any gap, such as a requirement with no task. Preserve existing project file names.

Suggested name: `HARDWARE_CHECKLIST.md`.
