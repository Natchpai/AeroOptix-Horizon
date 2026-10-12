# Git Workflow Baseline

This file contains portable Git safety and communication rules for KiCad
projects. Keep project-specific branch, pull-request, release, and hardware
workflow policies in separate files under `.claude/rules/`.

Use `.claude/skills/git-workflow/SKILL.md` for the operational procedure.

## Scope and safety
- Follow Conventional Commits 1.0.0 and keep changes focused and reviewable.
- Use English for commit messages, branch names, and pull requests.
- Preserve existing user changes, repository history, protected branches, and
  review/approval state.
- Git inspection is not permission to edit engineering files. Staging an
  existing change is distinct from writing the design and still requires
  approval for the exact paths.
- Native KiCad files and libraries remain subject to configured protections.
- Never modify project files solely to prepare Git history.

## Required approval boundary
- Read-only inspection may proceed without approval.
- Explicit, action-specific user approval is required before any repository or
  remote mutation: staging, committing, creating/switching/deleting/renaming
  branches, merging, rebasing, reset/restore/clean, creating/deleting tags,
  creating/updating/deleting releases, pushing, or creating/updating/closing
  pull requests.
- Do not infer approval from an earlier request, a proposed message, or tool
  permission prompts. Never merge a pull request automatically.
- Force-push, destructive reset/clean, history rewriting, and branch deletion
  remain prohibited unless explicitly authorized and permitted by tooling.

## Commit conventions
- Commit format: `<type>(<scope>): <description>`.
- Allowed types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`.
- Use lowercase types, imperative wording, a meaningful scope when useful,
  and a subject no longer than 72 characters.
- Add a body when rationale or impact needs explanation; use `BREAKING CHANGE`
  for incompatible interfaces.
- Never claim validation that was not performed.

## Pull requests and reporting
- Use a Conventional Commit-style PR title.
- Summarize purpose, affected components, design impact, risks, and only the
  validation actually performed.
- Mark missing or incomplete checks as `NOT_VERIFIED`.
- Present proposed branch actions, exact paths, commit messages, and PR title/
  summary before the corresponding approved action.
- Keep Git summaries concise, factual, and actionable.
