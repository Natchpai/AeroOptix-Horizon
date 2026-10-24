# CLAUDE.md

Guidance for Claude Code in this repository.

## Project

AeroOptix-Horizon is a KiCad 10 hardware design for a dual-MCU flight controller (STM32H743 + STM32F100) by AeroOptix Club. There is no firmware and no build, test or lint command. The human engineer makes every design and approval decision and declares the phase (DRAFT, PRELIMINARY, CHECK, RELEASE). Read the current status and phase from `README.md`; never infer them. Write files, code, error messages, Git text and chat in English unless the user asks otherwise.

## Layout

- `hardware/AO-Horizon/` is the KiCad project. The root `AO-Horizon.kicad_sch` links `block_diagram`, `top_hierarchical` and `revision_history`. `power_supplies` is a child of `top_hierarchical`, not of the root.
- `sym-lib-table` and `fp-lib-table` sit next to the project, and every entry uses `${KIPRJMOD}/library/...` (`0_<Family>` symbol and footprint libraries, `library/3D/<Family>/`). Stock models stay on `${KICAD10_3DMODEL_DIR}`.
- `AO-Horizon-backups/` and `*.bak` are KiCad backups, not design sources. A `~AO-Horizon.kicad_pro.lck` file means KiCad has the project open: read only the saved files, and say the editor may hold unsaved changes.
- `hardware/AO-Horizon/documents/design/` holds the Markdown records, listed in its `README.md`. The specification (`AO-HORIZON_SPEC_EN.md`) owns requirements, decisions (`DEC-xxx`) and open items (`OPEN-xxx`); read it before proposing a design change. The checklist and the other records point to spec IDs instead of copying values.
- `README.md` and `CHANGELOG.md` are maintained with the `hw-git-readme` and `hw-git-changelog` skills.

## Rules

`.claude/rules/` loads every session and owns the rules: `engineering.md` (design authority, change proposals, evidence labels, datasheet sources, NotebookLM), `hardware-workflow.md` (phases, PDFs, Markdown docs), `notebooklm.md` (NotebookLM procedure, path-scoped) and `git-workflow.md` (hardware Git notes on top of the global `~/.claude/rules/git-workflow.md`). This repo adds:

- **Protected paths.** The `protect_kicad_v2.py` PreToolUse hook (rules in `.claude/hooks/protect.json`, order allow > deny > ask) and the permission lists in `.claude/settings.json` control edits to KiCad files, `library/` and `templates/`. The engineer edits both often, and they can disagree (one may allow what the other asks for), so read both before acting on a protected path. A permission `allow` is not design authorization: a KiCad or library change still needs the engineer's approval of that specific change.
- **Git.** Every Git mutation needs explicit, action-specific approval in chat, even where `settings.json` lets the command run without a prompt. Never merge a PR, force-push or `reset --hard`. Work on `dev`, and open PRs to `main` with `.github/pull_request_template.md`.
- **External-model providers** (`agent-coworker`: `agy` or `codex`): send them no PDFs, native KiCad files, `library/` contents, secrets or anything on the deny or ask lists. Hooks and `settings.json` do not apply inside a provider.

## Workflow

- **Library part:** `kicad-part-start`, then `kicad-link-audit` before the part is placed. Link fixes go through `/kicad-symbol-sync` or `/kicad-footprint-sync`, with approval. The `kicad-*` skills are global; this repo keeps no copy.
- **Design data:** `sch-inspect` and `pcb-inspect` extract evidence from the saved files; `sch-review` and `pcb-review` judge it. Query narrow targets (sheet, ref, net), and brief subagents the same way with exact paths. Unannotated refs such as `U?` return every match.
- **Docs after design work:** the human runs `/progress-update`.
- **Datasheets:** each sensor and MCU has a NotebookLM notebook (`notebooklm list --json`). JLCPCB stock and price are JavaScript-rendered and Mouser often times out, so supplier values from search snippets stay `NOT_VERIFIED`; spot-check key values before writing them into a `design/` record.

## Compact Instructions

When compacting, keep: spec IDs (`DEC-xxx`, `OPEN-xxx`) in play, files changed and not yet committed, pending approvals and the exact change each covers, evidence labels on open values, the branch and unpushed commits, and decisions the user made this session. Do not carry over the phase; read it from `README.md` again.
