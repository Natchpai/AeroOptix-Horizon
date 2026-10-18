# Git Workflow: Hardware Overrides (KiCad projects)

The general Git rules (approval tiers, never pushing to the default branch,
English-only, `NOT_VERIFIED` reporting) live in the global
`~/.claude/rules/git-workflow.md`. Commit, branch and PR conventions live in
the `git-workflow` skill. This file only adds hardware specifics. It never relaxes the global rules or the English-only rule.
If the global file is missing, apply the defaults built into the `git-workflow`
skill.

Hardware workflow phases and engineering policy live in `hardware-workflow.md`
and `engineering.md`.

- Git inspection is not permission to edit engineering files. Staging an
  existing change is distinct from writing the design and still needs approval
  for the exact paths.
- Native KiCad files (schematics, PCB layouts, symbol and footprint libraries,
  project files) and libraries remain subject to configured protections. Never
  modify them solely to prepare Git history.
- Never infer a project phase (DRAFT, PRELIMINARY, CHECK, RELEASE) from Git
  status, files or history. Do not tag, release or open a release PR unless the
  human declares the phase and approves that Git action separately.
- Do not open, read or assess PDF documents while inspecting changes; report
  their paths and metadata only. Mark ERC/DRC or document checks that were not
  run as `NOT_VERIFIED`.
- In commit and PR text, describe design changes, impact and risks factually.
  Do not claim a design is correct, safe or approved based on ERC/DRC results.
