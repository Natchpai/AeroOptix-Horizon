# Git Workflow Rules

## General
- Follow Conventional Commits 1.0.0.
- Use English for commit messages, branches, and pull requests.
- Keep changes logically focused and independently reviewable.
- Respect repository permissions and protected branches.
- Never modify project files solely to prepare Git history.

## Commits
- Format: <type>(<scope>): <description>
- Types: feat, fix, refactor, docs, chore, test.
- Use lowercase types and imperative descriptions.
- Use a meaningful scope when applicable.
- Keep the subject within 72 characters.
- Add a body when rationale or impact needs explanation.
- Use BREAKING CHANGE for incompatible interface changes.
- Never claim validation that was not performed.

## Staging and Commit Safety
- Inspect staged and unstaged changes before committing.
- Stage only files relevant to the intended change.
- Never stage unrelated, temporary, or generated artifacts unless explicitly intended.
- Preserve existing user changes and commit history.
- Never amend, reset, rebase, or force-push without explicit authorization.
- Require user approval before creating commits.

## Branches
- Keep main as the integration branch.
- Use short-lived branches for logical changes.
- Prefer feature/, fix/, docs/, and chore/ prefixes.
- Reuse the current branch for related changes.
- Do not create branches for individual commits.
- Use Git tags to identify released versions.
- Create release branches only when maintenance requires them.
- Do not commit directly to protected branches.
- Never delete or overwrite branches without approval.

## Pull Requests
- Use Conventional Commit format for PR titles.
- Summarize what changed and why.
- Identify affected components or functional blocks.
- Describe relevant design impact and risks.
- Include only validation actually performed.
- Mark incomplete checks as NOT_VERIFIED.
- Prefer Draft PRs until ready for review.
- Require approval before pushing or creating PRs.
- Never merge PRs automatically.

## Output
- Present proposed commit messages before execution.
- Present PR titles and summaries before creation.
- Keep Git summaries concise, factual, and actionable.
