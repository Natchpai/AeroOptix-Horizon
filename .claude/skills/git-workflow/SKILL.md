---
name: git-workflow
description: >-
  Assists with Git and GitHub workflows: inspecting repository status,
  analyzing changes, managing branches, writing Conventional Commits, and
  preparing pull requests. Use when the user asks what changed, wants to
  commit, create or switch a branch, summarize a diff, or open a PR.
argument-hint: "status | branch [name] | commit [scope] | pr [base]"
---

# Git Workflow

Manage Git and GitHub changes without modifying project content except as
explicitly approved by the user.

Shared policy (approval boundary, commit types and format, PR reporting,
`NOT_VERIFIED`) lives in `rules/git-workflow.md`; follow it. This skill adds
the procedure. If that file is not in the project, apply the defaults here.
Examples and the proposal template are in `references/examples.md`; read it
when drafting a proposal, commit message or PR body.

## Local safeguards
- Read repository-local instructions (CONTRIBUTING, CLAUDE.md, branch rules);
  they override the defaults here.
- A Git operation does not grant permission to edit source files, generated
  artifacts, or repository configuration.
- Tool permissions and branch protection still apply; this skill grants none.

## Execution gate
- Read-only inspection needs no approval.
- Before any state-changing action, present one **proposal** (template in
  `references/examples.md`) listing every action with exact paths, then stop.
- Apply the approval tiers in the rules: one approval covers the Tier 1
  actions the proposal lists; each Tier 2 action (push, PR, tag, amend, ...)
  needs its own explicit approval, even within the same proposal. Any later
  action or change of scope needs a new proposal.
- Advance or blanket approval ("approve everything", "no need to ask again")
  does not skip the proposal: show it and ask once. Approval is tied to the
  listed actions.
- If asked to push to the default or a protected branch, decline whatever the
  user says and offer the allowed route: push a feature branch and open a PR.
  Repeating the request does not change the answer.
- After each approved action, verify the real result (`git status`,
  `git log -1`, or the tool output) and report it. Do not infer success from
  an exit code alone.

## Dispatch
Interpret `$ARGUMENTS` as one of:
- `status` : inspect only.
- `branch [name]` : propose creating or switching a branch.
- `commit [scope]` : propose and, after approval, create focused commit(s).
  `scope` is an optional commit-scope hint (for example `uart`), not a path.
- `pr [base]` : propose and, after approval, push and open a PR.
- Omitted or unsupported : list these choices; change nothing.
- Tag, release, merge, rebase, reset and deletion requests need their own
  proposal; never fold them into a commit or PR workflow.

## Shared inspection
1. Establish repository root, branch, upstream and working-tree state
   (`git status --short --branch`). Untracked files count as candidates for
   "my changes".
2. Separate staged, unstaged and untracked changes (`git diff --stat`,
   `git diff --cached --stat`); open only relevant diffs.
3. Read recent history (`git log --oneline -n 20`) and follow the repo's
   existing conventions for scopes, language and issue references, unless
   they conflict with the rules.
4. For binary or non-reviewable files, report path and metadata, not a diff.
5. Flag unrelated files, caches and generated artifacts; propose leaving them
   out.
6. Secrets and large files (see rules): check staged and candidate paths and
   diffs for credential files (`.env`, key and certificate files), tokens or
   private keys in content, and unusually large files. Inspect secret files
   by key names only; never print their values. Block staging until the user
   explicitly confirms each flagged item, and list flagged items as
   "Excluded" in the proposal. Suggesting a `.gitignore` entry is fine; editing
   it needs its own request.
7. Preserve user changes and staged content. Never edit, discard or rewrite
   files as part of Git work.
8. Report unavailable evidence as `NOT_VERIFIED`. If inspection fails, report
   the failure and change nothing.

## Repository states
Detect these during inspection and adapt the proposal:
- **Merge, rebase, cherry-pick or bisect in progress** : report it and stop;
  do not commit or switch branches until the user decides how to proceed.
- **Detached HEAD** : propose a new branch before committing.
- **On `main`/`master` or a protected branch** : propose a new branch first;
  commit there only if the user explicitly says so. Never push to it
  directly; deliver through a branch and PR.
- **No upstream** : note it; propose `git push -u origin <branch>` in the PR
  flow.
- **No remote** : report that pushing and PRs are not possible yet. Adding a
  remote changes repository configuration and needs its own proposal.
- **Dirty tree when switching branches** : creating a new branch carries the
  changes by default; switching to an existing branch may conflict, so
  propose carrying or stashing. Stash is a mutation and needs approval.
- **Empty repository (no commits)** : say so; the first commit is a normal
  commit proposal.
- **Behind the base or upstream** : report it; propose a merge or rebase
  only as a separate proposal.

## status
Report branch, upstream, clean/dirty state, and concise logical change
groups, distinguishing staged, unstaged and untracked paths, plus any state
from "Repository states". Suggest a commit or branch name only when useful.
Perform no writes.

## branch
1. Inspect current branch and ahead/behind state.
2. Propose `<type>/<short-kebab-description>` using a commit type from the
   rules.
3. After approval, create or switch (`git switch -c <name>` or
   `git switch <name>`). Never delete, rename or force-move a branch.

## commit
1. Inspect staged and unstaged diffs, including pre-existing staged content.
2. Group changes by purpose, one commit per logical group. Splitting is at
   path level (interactive staging is unsupported); flag files that mix
   concerns and ask how to proceed. Propose the split by default; the user may
   ask for a single commit. Name a new branch after the primary group's type.
3. Draft each message per the rules' commit conventions, reusing scopes
   seen in history.
4. Present the proposal. Stop for approval.
5. After approval, stage only the listed paths (`git add -- <paths>`), recheck
   `git diff --cached`, and stop if it differs materially from the proposal.
6. Commit. Amend only with explicit Tier 2 approval and an unpushed commit.
7. If a hook fails, report its output and propose a fix; do not retry
   silently or bypass it.
8. Report the hash and remaining changes. Push only if the user separately
   approved it.

## pr
1. Determine the base branch; inspect branch, upstream and ahead/behind.
2. Check whether a PR already exists for the branch
   (`gh pr list --head <branch>`); if so, propose updating it instead of
   creating a duplicate.
3. Review the whole range (`git log <base>..HEAD`,
   `git diff <base>...HEAD --stat`); separate committed work from local
   changes.
4. Fill the repository PR template (`.github/pull_request_template.md` or
   `pull_request_template.md`), preserving its sections:
   - Check **Type of Change** and **Affected Areas** only from the diff.
   - Check **Validation Performed** only for checks actually run; otherwise
     leave unchecked and write `NOT_VERIFIED` under Results.
   - Add `Closes #n` only when the branch name, commits or user supply the
     issue.
5. Use a Conventional Commit-style title. Propose a draft PR when validation
   is `NOT_VERIFIED` (see rules).
6. Present base/head, required push, title, body, impact and risks as one
   proposal.
7. After approval, push the feature branch (`git push -u origin <branch>`;
   never the base or default branch) and create the PR (`gh pr create`) only
   if `gh` is available and authenticated.
8. Report the PR URL only if the tool returned one. Never merge.

## Platform notes
Line-ending warnings (LF/CRLF) are informational; do not report them as risks
or change settings unless asked.
Commands are shown in POSIX form. On Windows PowerShell, quote arguments
containing spaces or special characters, and pass multi-line commit messages
or PR bodies with a here-string or a message file outside the repository
rather than relying on shell escapes. Use forward slashes in paths.

## Output
Keep summaries concise, factual and actionable. Do not create logs, reports
or temporary files in the repository unless asked.
