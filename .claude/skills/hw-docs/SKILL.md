---
name: hw-docs
description: >-
  Creates or updates the root README.md and CHANGELOG.md of a hardware project,
  and records a phase the human declares (DRAFT, PRELIMINARY, CHECK, RELEASE).
  Use when the user asks to create or revise the README, create, update or
  release-note the changelog, or declares a project phase. Uses confirmed
  facts only. Does not judge readiness, read schematic or PCB PDFs, edit
  KiCad files, commit, tag or release.
argument-hint: "readme create|update | changelog init|update [range]|release <version> | phase <PHASE>"
---

# Project docs: README, CHANGELOG, phase

One skill for the three root documents a hardware repo keeps for people:
`README.md`, `CHANGELOG.md`, and the phase line in the README. The design
records (spec, checklist) belong to `progress-update`, `hardware-specification`
and `hardware-checklist`; this skill points to them and does not copy them.

Pick the mode from the argument or the request. If it is unclear, ask.

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

## Rules for every mode
- Write a file only when the user asks for it. Read the existing file first,
  keep valid content, and make the smallest edit that does the job.
- Use facts from the user, existing Markdown or text files, repo file and
  folder names, and targeted read-only Git queries. A commit message is a clue,
  not proof that a check was run.
- Never invent a title, specification, test result, phase, approval or
  release state. Leave out what is unknown rather than filling it in.
- Do not derive design facts from raw `git diff` of KiCad files (UUID and
  coordinate noise); confirm a reference, value or footprint with
  `sch-inspect` or `pcb-inspect` if installed, else mark it `NOT_VERIFIED`.
- A phase is never inferred from files, ERC, DRC, Git state or a release.
  `RELEASE` never authorizes a commit, tag, push, PR or GitHub release.
- Writing a doc is a content edit. Staging, committing, tagging and releasing
  each need separate approval; follow `rules/git-workflow.md` if present.
- Style: simple, direct English with everyday words and short sentences. Keep
  exact names (refs, nets, part numbers). No em dash. Do not reword text that
  is already clear and correct. Priority: accuracy, clarity, brevity, style.

## Mode: `readme create | update`
**Create** (only on request; if a README exists, treat it as an update unless
the user approves a replacement after seeing the current one):
1. Start from `assets/readme_template.md`. Keep only the sections with
   confirmed content: Overview, Key Features, Specifications, Project Status,
   Hardware Design, Repository Structure, Documentation, Results, References,
   License. Omit Overview when it only repeats the tagline.
2. Adapt the repository tree and links to files that exist; use the real
   folder name as the tree root. Remove maintainer comments and unused
   placeholders.
3. Specifications are design targets unless the user says they are measured;
   keep the template note that says so.
4. Include `Current Phase` only if a human declared one. Otherwise remove the
   line; do not write `DRAFT`, `Not declared` or a guess.
5. Show the content and wait for approval, unless the user already asked for
   the file to be written. Do not edit the template itself.

**Update:**
1. Read the README, keep unrelated content and its structure, make the
   requested edit only. Do not drop substantial content without review.
2. In a project that uses `progress-update`, the README holds summaries that
   point to the spec: spec revision, key features, specifications table,
   open-items summary and documentation links. Sync those from the spec; do
   not copy decision or open-item detail.
3. Keep the Mermaid workflow diagram's structure; its `class` lines follow
   the phase (see Mode: phase).

## Mode: `changelog init | update [range] | release <version>`
`CHANGELOG.md` is a short record of notable, confirmed changes, not a Git log
and not an approval record. Start a new one from `assets/changelog_template.md`.

**One history.** When the project keeps a spec change-note table, the spec is
the design history. The changelog gets **one pointer line per spec
revision**, not a second copy of it:
```markdown
- Specification rev 0.81 (2026-11-21): P2-016, P2-021, P4-011; see the change-note.
```
List the IDs the revision added or changed (DEC, OPEN, tasks). Schematic,
PCB, library, website and tooling commits that people need to know about get
their own short lines.

**Entries:**
1. Group under `## [Unreleased]` with Keep a Changelog categories: `Added`,
   `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`, and an optional
   `Verification` category for checks the human confirmed, with their scope.
2. Keep design intent, implemented changes and confirmed results apart. Never
   infer a measurement, ERC or DRC pass, or approval.
3. Start an entry with `**BREAKING:**` when it breaks mating hardware,
   firmware or an earlier board (connector pinout, outline or mounting holes,
   a net name firmware depends on).
4. Merge related commits into one entry. Skip typo, CI and `.claude/` changes
   unless they affect users. Ask for a missing fact instead of guessing.

**Release `<version>`:** only when the human has set the version and date.
Move the `[Unreleased]` entries into `## [<version>] - <YYYY-MM-DD>`. Build
the design part from the pointer lines (first and last spec revision in the
release, with the main IDs) and the rest from the entries and
`git log <last tag>..HEAD`. Do not tag or publish.

## Mode: `phase <DRAFT | PRELIMINARY | CHECK | RELEASE>`
- `DRAFT`: schematic capture in progress; PCB not started.
- `PRELIMINARY`: schematic nearly complete; PCB started.
- `CHECK`: schematic and PCB mostly final; the human runs ERC and DRC on a
  saved baseline.
- `RELEASE`: an approved CHECK baseline is published.
`rules/workflow.md`, when present, holds the full definitions.

1. Accept a phase only when the human states one of these values; write it
   in upper case. A step back (CHECK to DRAFT) is recorded as declared.
2. Without a request to record it ("record it in the README", "update the
   README"), acknowledge it in chat only.
3. To record it, find exactly one `**Current Phase:**` or `- Current Phase:`
   line and replace only its value. If it already holds that phase, say so.
   If the line is missing (create mode leaves it out until a phase is
   declared), add `**Current Phase:** <PHASE>` as the first line under the
   `## Project Status` heading, as in the template, and say so; with no such
   heading, report it and change nothing. If the line is duplicated or
   ambiguous, report it and change nothing. Do not create `PHASE.md` or any
   other state file.
4. If the README has the Mermaid workflow diagram (nodes `A` to `D` for
   DRAFT, PRELIMINARY, CHECK, RELEASE), update only its `class` lines:
   earlier phases `done`, the declared phase `review`, later phases
   `inactive`; for `RELEASE` all four `done`. With no declared phase all four
   stay `inactive`. Do not change nodes, edges, labels or `classDef` lines,
   and never add a diagram that is not there.

## Output
State the file and mode, the sections created or changed, the sources used,
facts still missing, and for `phase` whether the phase was only acknowledged
or recorded and whether the diagram changed. Do not claim a document proves
verification or approval.
