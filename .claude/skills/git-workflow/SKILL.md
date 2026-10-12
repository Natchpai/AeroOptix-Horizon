---
name: git-workflow
description: >-
  Assists with Git and GitHub workflows, including repository
  status inspection, change analysis, branch management,
  Conventional Commits, and pull request preparation.
  Use when the user asks to review Git changes, prepare or
  create commits, organize branches, summarize changes,
  or prepare and open GitHub pull requests.
  Requires user approval before repository write operations.
argument-hint: "status | commit [scope] | pr [base]"
---


# Git Workflow

Manage Git changes without modifying engineering design content.

## Local safeguards
- Read `.claude/settings.json` first.
- Treat `.claude/hooks/protect_kicad.py` as defense-in-depth for native KiCad
  and `library/` writes. A Git operation does not grant design-write access;
  inspecting or staging an existing design change is separate from editing it.
- For PRs, read `.github/pull_request_template.md` and preserve its sections
  and checkboxes.
- Tool permissions and branch protection still apply; this skill grants none.

## Approval boundary
- Read-only inspection may proceed without approval.
- Obtain explicit, action-specific user approval before staging, committing,
  changing branches, merging, rebasing, resetting, restoring, cleaning,
  creating or deleting tags/releases, pushing, or changing a pull request.
- Do not infer approval from an earlier request, a proposed message, or a tool
  permission prompt. Never merge a pull request automatically.
- Do not force-push, rewrite history, delete branches, or use destructive
  reset/clean operations unless explicitly authorized and permitted by tooling.

## Dispatch
Interpret `$ARGUMENTS` as one of:
- `status` — inspect only; never change repository state.
- `commit [scope]` — propose and, after explicit approval, create focused commit(s).
- `pr [base]` — propose and, after separate approval, push/open a PR.
- If omitted or unsupported, show these choices without making changes.
- Tag or release requests use the same proposal-then-explicit-approval gate;
  do not create or publish them as part of a commit or PR workflow.

## Shared inspection
1. Establish repository root, current branch, upstream, and working-tree state.
2. Separate staged, unstaged, and untracked changes; inspect only relevant
   diffs and files.
3. For binary KiCad files, report paths and metadata rather than claiming a
   textual diff. Detect secrets, caches, generated exports, and unrelated files.
4. Preserve user changes and review state. Never edit, discard, or rewrite
   KiCad design/library files during Git work.
5. Report unavailable evidence as `NOT_VERIFIED`; do not invent ERC, DRC, or
   test results. If inspection itself fails, report the failure and do not
   mutate repository state.

## status
- Report branch, upstream when available, clean/dirty state, and concise
  logical change groups.
- Distinguish staged, unstaged, and untracked paths.
- Suggest a commit or branch name only when useful. Perform no writes.

## commit
1. Inspect staged and unstaged diffs, including pre-existing staged content.
2. Group changes by purpose and prepare a Conventional Commit message.
3. If a branch change is useful, propose its exact action and a short
   `feat/`, `fix/`, `docs/`, or `chore/` name; do not create or switch it.
4. Present the exact paths, proposed branch action, commit subject/body, and
   unverified checks. Stop for explicit approval before branch changes,
   staging, or committing.
5. After approval, stage only approved paths, recheck the staged diff, and
   stop if it differs materially from the approved scope.
6. Commit only the approved change. Report the resulting hash and remaining
   changes; do not push without separate approval.

## pr
1. Determine the base branch and inspect current branch, upstream, and
   ahead/behind state.
2. Compare the complete proposed range with the base, including all commits
   and changed files; distinguish committed work from local changes.
3. Prepare the PR title/body from the repository template and mark only
   supported checks; explain skipped or inconclusive checks as `NOT_VERIFIED`.
4. Present base/head, required push, title/body, impact, risks, and validation.
5. After separate approval, push only as approved and create a PR only when
   the GitHub capability is available and authenticated. Follow any applicable
   project rule for its draft or ready-for-review state.
6. Report a PR URL only when the tool returns one. Never merge automatically.

## Output
- Keep summaries concise, factual, and actionable.
- Do not create extra logs, reports, or temporary repository files unless the
  user explicitly requests them.
