---
name: hw-git-changelog
description: >-
  Creates or maintains a human-readable CHANGELOG.md for a hardware
  engineering repository from confirmed changes. Use only when the user
  explicitly asks to create, update or release-note the changelog. Does not
  commit, push, tag or release.
argument-hint: "init | update [range] | release <version>"
---

# Project Changelog

Maintain the repository-root `CHANGELOG.md` as a concise record of **notable, confirmed project changes**, not a raw Git log or an engineering approval record. Use `assets/changelog_template.md` as an adaptable starting point only when creating a new changelog.

## Trigger and scope

- Write or update `CHANGELOG.md` **only upon an explicit user request**. Do not update it automatically after a design change, Git commit, or phase declaration.
- Read the existing changelog first. Preserve existing version history, links, custom sections, and entries unless the user explicitly requests a change.
- Gather evidence from user-provided notes, relevant text files, and targeted read-only Git queries such as `git log`, `git show`, or `git diff`. Git messages are clues, **not** proof that hardware verification occurred.
- Raw `git diff` of KiCad files is mostly UUID, coordinate and ordering noise. Do not derive design changes from it. Use user notes and commit messages, or targeted read-only queries of the saved files (`sch-inspect`/`pcb-inspect` if installed) to confirm a reference designator, value or footprint. Mark changes you cannot confirm `NOT_VERIFIED`.
- Never open, parse, generate, or assess PDFs. Do not alter KiCad design/library files or formal approval records.

## Writing style

- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences and active voice.
- Avoid fancy words, marketing phrases and AI-style filler. Keep standard engineering terms and exact identifiers.
- Do not use the em dash (`—`). Use a period, comma, colon or parentheses.
- Do not reword existing entries that are already clear and correct.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Entry rules

1. Write entries for meaningful changes visible to project users or future maintainers: circuit/PCB/interface changes, component substitutions, corrected design defects, manufacturing-impacting changes, released capabilities, and confirmed verification milestones.
2. Distinguish **design intent**, **implemented changes**, and **confirmed test/verification results**. Never infer measurements, ERC/DRC pass, functional correctness, production readiness, or approval from file presence or commits.
3. Group changes under `## [Unreleased]` by default. Use versioned sections (`## [x.y.z] - YYYY-MM-DD`) only when the human explicitly establishes the version and release date. Git history may support source provenance, but does not establish a hardware release.
4. Use relevant Keep a Changelog categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. An optional `Verification` category may record **explicitly confirmed** checks with their scope/baseline; it is not an approval signal.
5. Prefer short, precise entries with identifiers where useful (reference designators, interfaces, subsystem names), without dumping complete netlists or calculations. Merge duplicate or closely related commits into one entry. Skip typo fixes, CI and `.claude/` tooling changes unless they affect users or maintainers.
6. Start an entry with `**BREAKING:**` when it breaks compatibility with mating hardware, firmware or an earlier board, for example: a connector pinout or mating-part change, a board outline or mounting-hole change, or a net or signal rename that firmware depends on.
7. If evidence is insufficient, ask for the missing fact or omit the unverified entry; do not fabricate. Label significant uncertainty `NOT_VERIFIED` if an explicit draft is needed.
8. Never infer or change hardware lifecycle phase from changelog data. `RELEASE` phase does not authorize a Git tag or GitHub Release.

## Procedure

1. Determine the mode from `$ARGUMENTS` or the request: `init` (new changelog), `update [range]` (new Unreleased entries, optionally from a commit range) or `release <version>` (move Unreleased entries into a version section the human has established). Omitted or unclear: ask.
2. Inspect the existing `CHANGELOG.md` and the smallest relevant source range. Do not scan unrelated design files or bulk export project evidence.
3. Draft categorized, deduplicated entries; identify any assumptions or verification gaps.
4. Apply only the explicitly requested changelog edit; preserve other sections and report the change succinctly.
5. If the user did not authorize writing a file, present a proposed entry instead. Never stage, commit, push, tag, publish a GitHub Release, or alter Git branches without separate explicit approval; follow `rules/git-workflow.md` if present.

## Example

```markdown
## [Unreleased]

### Changed
- Replaced U3 (LDO) with a 1 A part for 3V3 rail margin; footprint unchanged.

### Fixed
- Corrected swapped SDA/SCL labels on the sensor connector J4.

### Verification
- Human-run ERC on the schematic at the CHECK baseline: no open violations (reported by the engineer).
```

## Output

Report the target file, sections updated, sources considered, and unresolved evidence gaps. Do not create auxiliary logs, manifests, or release assets.
