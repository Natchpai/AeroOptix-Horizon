---
name: project-changelog
description: Create or maintain a human-readable CHANGELOG.md for a hardware engineering repository when explicitly asked. Curate confirmed changes from user instructions and targeted Git history; do not commit, push, tag, or release.
---

# Project Changelog

Maintain the repository-root `CHANGELOG.md` as a concise record of **notable, confirmed project changes**, not a raw Git log or an engineering approval record. Use `assets/changelog_template.md` as an adaptable starting point only when creating a new changelog.

## Trigger and scope

- Write or update `CHANGELOG.md` **only upon an explicit user request**. Do not update it automatically after a design change, Git commit, or phase declaration.
- Read the existing changelog first. Preserve existing version history, links, custom sections, and entries unless the user explicitly requests a change.
- Gather evidence from user-provided notes, relevant text files, and targeted read-only Git queries such as `git log`, `git show`, or `git diff`. Git messages are clues, **not** proof that hardware verification occurred.
- Never open, parse, generate, or assess PDFs. Do not alter KiCad design/library files or formal approval records.

## Entry rules

1. Write entries for meaningful changes visible to project users or future maintainers: circuit/PCB/interface changes, component substitutions, corrected design defects, manufacturing-impacting changes, released capabilities, and confirmed verification milestones.
2. Distinguish **design intent**, **implemented changes**, and **confirmed test/verification results**. Never infer measurements, ERC/DRC pass, functional correctness, production readiness, or approval from file presence or commits.
3. Group changes under `## [Unreleased]` by default. Use versioned sections (`## [x.y.z] - YYYY-MM-DD`) only when the human explicitly establishes the version and release date. Git history may support source provenance, but does not establish a hardware release.
4. Use relevant Keep a Changelog categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. An optional `Verification` category may record **explicitly confirmed** checks with their scope/baseline; it is not an approval signal.
5. Prefer short, precise entries with identifiers where useful (reference designators, interfaces, subsystem names), without dumping complete netlists or calculations.
6. If evidence is insufficient, ask for the missing fact or omit the unverified entry; do not fabricate. Label significant uncertainty `NOT_VERIFIED` if an explicit draft is needed.
7. Never infer or change hardware lifecycle phase from changelog data. `RELEASE` phase does not authorize a Git tag or GitHub Release.

## Procedure

1. Determine whether the user wants an initial changelog, a new Unreleased entry, an update from a specified commit range, or an explicitly approved version section.
2. Inspect the existing `CHANGELOG.md` and the smallest relevant source range. Do not scan unrelated design files or bulk export project evidence.
3. Draft categorized, deduplicated entries; identify any assumptions or verification gaps.
4. Apply only the explicitly requested changelog edit; preserve other sections and report the change succinctly.
5. If the user did not authorize writing a file, present a proposed entry instead. Never stage, commit, push, tag, publish a GitHub Release, or alter Git branches without separate explicit approval.

## Output

Report the target file, sections updated, sources considered, and unresolved evidence gaps. Do not create auxiliary logs, manifests, or release assets.
