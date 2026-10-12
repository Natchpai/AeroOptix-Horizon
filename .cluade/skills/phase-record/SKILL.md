---
name: phase-record
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
- `DRAFT`
- `PRELIMINARY`
- `CHECK`
- `RELEASE`

## Record
1. Accept a phase only when the human explicitly states one of the accepted values.
2. If persistence is not explicitly requested, acknowledge the declaration in
   conversation only and make no file changes.
3. If the human explicitly requests persistence in `README.md`, locate exactly
   one existing `Current Phase` record. Recognize either `**Current Phase:**`
   or `- Current Phase:`.
4. Replace only that phase value with the human-declared phase. Preserve all
   other README content, including Mermaid diagrams, phase descriptions, status
   notes, and established formatting.
5. If the `Current Phase` record is missing, duplicated, or ambiguous, report
   the problem and do not modify the file.

## Boundaries
- Never infer, validate, advance, or reject a phase from project files, ERC,
  DRC, document presence, Git state, or a GitHub release.
- Do not create `PHASE.md`, JSON state, a database, or other phase records.
- `RELEASE` never authorizes a commit, tag, push, pull request, or GitHub
  release.
- Do not generate, open, read, parse, or assess PDF documents.
- Keep KiCad files and libraries read-only.

## Output
- State the declared phase and whether it was acknowledged only or recorded in
  `README.md`.
- If persistence could not be completed, state whether the `Current Phase`
  record was missing, duplicated, or ambiguous. Do not create a replacement
  section.
