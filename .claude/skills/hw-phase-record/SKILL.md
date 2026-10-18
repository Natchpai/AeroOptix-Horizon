---
name: hw-phase-record
description: >-
  Acknowledges a hardware project phase explicitly declared by a human engineer
  and, only when requested, records it in README.md.
  Use when the user declares DRAFT, PRELIMINARY, CHECK, or RELEASE.
  Does not evaluate readiness, create state files, or perform Git release actions.
argument-hint: "DRAFT | PRELIMINARY | CHECK | RELEASE"
---

# Phase Record

Record only a phase explicitly declared by the human engineer. A recorded phase
is project context, not evidence of verification, approval, or release.

## Accepted phases
- `DRAFT`: schematic capture in progress; PCB work not started.
- `PRELIMINARY`: schematic nearly complete; PCB work started.
- `CHECK`: schematic and PCB mostly final; the human runs ERC and DRC on a
  saved baseline.
- `RELEASE`: an approved CHECK baseline is published.

If the project has `rules/hardware-workflow.md`, it holds the full phase
definitions.

## Record
1. Accept a phase only when the human explicitly states one of the accepted
   values (case-insensitive; write it in upper case).
2. Treat wording such as "record it in README.md" or "update the README" as
   explicit persistence. Otherwise acknowledge the declaration in
   conversation only and make no file changes. A phase that is a step back
   (for example CHECK to DRAFT) is recorded as declared.
3. If the human explicitly requests persistence in `README.md`, locate exactly
   one existing `Current Phase` record. Recognize either `**Current Phase:**`
   or `- Current Phase:`.
4. Replace only that phase value with the human-declared phase. Preserve all
   other README content, including phase descriptions, status notes, and
   established formatting. The one other permitted edit is the Mermaid workflow
   diagram, updated as described in "Diagram sync".
5. If the record already holds the declared phase, report that and change
   nothing.
6. If the `Current Phase` record is missing, duplicated, or ambiguous, report
   the problem and do not modify the file.

## Diagram sync
When persistence is requested (this includes creating a new README with a
declared phase) and the README has the Mermaid workflow diagram (nodes
`A`-`D` for DRAFT, PRELIMINARY, CHECK, RELEASE, matched by order and label),
update only
its `class` assignment lines to match the declared phase:
- Phases before the declared one: `done`.
- The declared phase: `review`.
- Phases after it: `inactive`.
- `RELEASE` declared: all four nodes `done`.

Do not change nodes, edges, labels or `classDef` lines. If the diagram is
missing or its class lines are ambiguous, update the `Current Phase` value
only and report that the diagram was not updated. Never add a diagram that is
not already there.

## Boundaries
- Never infer, validate, advance, or reject a phase from project files, ERC,
  DRC, document presence, Git state, or a GitHub release.
- Do not create `PHASE.md`, JSON state, a database, or other phase records.
- `RELEASE` never authorizes a commit, tag, push, pull request, or GitHub
  release.
- Do not generate, open, read, parse, or assess PDF documents.
- Keep KiCad files and libraries read-only.
- Editing `README.md` is a content edit; staging or committing it needs
  separate approval. Follow `rules/git-workflow.md` if present.

## Output
- State the declared phase and whether it was acknowledged only or recorded in
  `README.md`, and whether the diagram was updated.
- If persistence could not be completed, state whether the `Current Phase`
  record was missing, duplicated, or ambiguous. Do not create a replacement
  section.
