# CLAUDE.md

Guidance for Claude Code in this repository.

## Project

AeroOptix-Horizon is a KiCad 10 hardware design for a dual-MCU flight controller (STM32H743 + STM32F103) by AeroOptix Club. There is no firmware and no build, test or lint command. The human engineer makes every design and approval decision and declares the phase (DRAFT, PRELIMINARY, CHECK, RELEASE). Read the current status and phase from `README.md`; never infer them.

## Layout

- `hardware/AO-Horizon/` is the KiCad project. The root `AO-Horizon.kicad_sch` links `block_diagram`, `top_hierarchical` and `revision_history`. `power_supplies` is a child of `top_hierarchical`, not of the root.
- `sym-lib-table` and `fp-lib-table` sit next to the project, and every entry uses `${KIPRJMOD}/library/...`. Project library: `library/symbols/0_<Family>.kicad_symdir/<Symbol>.kicad_sym` (one file per symbol), `library/footprints/0_<Family>.pretty/`, `library/3D/<Family>/*.step` (3D folders have no `0_` prefix). Stock models stay on `${KICAD10_3DMODEL_DIR}`.
- `AO-Horizon-backups/` and `*.bak` are KiCad backups, not design sources. A `~AO-Horizon.kicad_pro.lck` file means KiCad has the project open: read only the saved files, and say the editor may hold unsaved changes.
- `documents/design/` holds the Markdown records, listed in `documents/design/README.md`. The specification (`AO-HORIZON_SPEC_EN.md`) owns requirements, decisions (`DEC-xxx`) and open items (`OPEN-xxx`); read it before proposing a design change. The checklist and the other records point to spec IDs instead of copying values.
- `README.md` and `CHANGELOG.md` are maintained with the `hw-git-readme` and `hw-git-changelog` skills.

## Rules

`.claude/rules/` loads every session and owns the rules: `engineering.md` (design authority, change proposals, evidence labels, datasheet sources, NotebookLM), `hardware-workflow.md` (phases, PDFs, Markdown docs) and `git-workflow.md` (hardware Git notes on top of the global `~/.claude/rules/git-workflow.md`). This repo adds:

- **Protected paths.** The `protect_kicad_v2.py` PreToolUse hook (rules in `.claude/hooks/protect.json`, order allow > deny > ask) and the permission lists in `.claude/settings.json` control edits to KiCad files, `library/` and `templates/`. The engineer edits both often, and they can disagree (one may allow what the other asks for), so read both before acting on a protected path. A permission `allow` is not design authorization: a KiCad or library change still needs the engineer's approval of that specific change.
- **Git.** Every Git mutation (stage, commit, branch, push, PR, tag) needs explicit, action-specific approval in chat, even where `settings.json` lets the command run without a prompt. Never merge a PR, force-push or `reset --hard`. Work on `dev`, and open PRs to `main` with `.github/pull_request_template.md`. Conventional Commits: `<type>(<scope>): <desc>`, at most 72 characters, English.
- **External-model providers** (`agent-coworker`: `agy` or `codex`): send them no PDFs, native KiCad files, `library/` contents, secrets or anything on the deny or ask lists. Hooks and `settings.json` do not apply inside a provider.

## Workflow

- **Library part:** `kicad-part-start` for a new MPN (names from `kicad-naming`, imports and stock copies through `kicad-lib-organize`), then `kicad-link-audit` (read-only) before the part is placed. Link fixes go through `/kicad-symbol-sync` or `/kicad-footprint-sync`, with approval. These are global skills in `~/.claude/skills/`; this repo keeps no copy.
- **Design data:** `sch-inspect` and `pcb-inspect` extract evidence from the saved files; `sch-review` and `pcb-review` judge it. Query narrow targets (sheet, ref, net). Unannotated refs such as `U?` return every match.
- **Docs after design work:** the human runs `/progress-update`. It updates the spec, then the checklist, the touched design records, the README and the CHANGELOG, tags each part DECISION or DRAWN, and ends with a proposed commit message.
- **Datasheets:** each sensor and MCU has a NotebookLM notebook (`notebooklm list --json`). If TI's English HTML datasheet viewer shows no body text for a section, try the `document-viewer/ja-jp/...` page, which can show the same section in English. JLCPCB stock and price are JavaScript-rendered and Mouser often times out, so supplier values from search snippets stay `NOT_VERIFIED`; spot-check key values before writing them into a `design/` record.

## Subagents

Global agents in `~/.claude/agents/`: `research-scout` (local files only), `web-research`, `hardware-researcher` (datasheets through official pages or NotebookLM) and `agent-coworker` (external model, only on request). Hooks and `settings.json` deny rules apply to Claude subagents but not to external providers. Brief a subagent with narrow KiCad targets and exact paths.

## Language Rules
- Use English for all files, code, error messages, and git's activity messages.
- Use English for user-facing explanations, conversational text in CLI, unless otherwise specified by the user.
