# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AeroOptix-Horizon is a KiCad 10 hardware design (no firmware, no build/test/lint commands) for a dual-MCU flight controller (STM32H7 + STM32F1) by AeroOptix Club. The human engineer makes all design and approval decisions. Status and phase are declared by the human, never inferred (see `.claude/rules/hardware-workflow.md`: DRAFT → PRELIMINARY → CHECK → RELEASE). The README currently lists status `CONCEPT`, baseline `NOT_ESTABLISHED`.

## Repository layout (big picture)

- `hardware/AO-Horizon/` is the KiCad project. The schematic is hierarchical: `AO-Horizon.kicad_sch` is the root, with sheet files `top_hierarchical`, `block_diagram`, `power_supplies`, `revision_history` (`*.kicad_sch`) alongside it. Check how sheets are linked before assuming which one is the root.
- `hardware/AO-Horizon/documents/` holds `design/` (spec, handoff, execution checklist, all Markdown), `manufacturing/`, `schematic/`, `verification/`, `images/`. Engineering PDFs and release documents live here and are human-generated.
- `hardware/AO-Horizon/library/` (`symbols`, `footprints`, `3D`) holds project-specific libraries; `templates/` holds title-block worksheets (`.kicad_wks`), notes and the board theme.
- `README.md` and `CHANGELOG.md` are project-level docs, written from the templates under `.claude/skills/hw-git-readme/assets` and `.claude/skills/hw-git-changelog/assets`.
- Treat the `documents/design/` spec files as the source of requirements; read them before proposing design changes.

## Rules that matter

- **Native KiCad files and `library/` are protected** (enforced by the hook and `settings.json`; the rules in `.claude/hooks/protect.json` are authoritative). Never edit without the engineer's explicit authorization, and propose changes with justification first; never silently alter connectivity, values, footprints, net names or geometry.
  - **Ask** (edit only after the engineer's explicit approval, one action at a time): `.kicad_sch`, `.kicad_pcb`, `.kicad_sym`, `.kicad_mod`, `library/**`.
  - **Deny** (do not edit; the engineer changes these): `.kicad_pro`, `.kicad_wks`, `templates/**`, `.step/.stp/.wrl`.
- KiCad files reflect only the **saved** design; the editor may hold unsaved changes.
- Inspect natively and narrowly (specific sheets/components/nets), not whole schematics or netlists. Verify component claims against datasheets. ERC/DRC PASS is not proof of correctness. Report `NOT_VERIFIED` when evidence is insufficient; do not invent specs or measurements.
- Never generate, open, read or assess PDFs. If asked about documents, check only file existence (`EXISTS` / `MISSING` / `NOT_VERIFIED`). Create Markdown docs only when explicitly asked.
- **Git:** Conventional Commits (`feat|fix|refactor|docs|chore|test|perf|build|ci`, `<type>(<scope>): <desc>`, ≤72 chars, English). Every mutation (stage, commit, branch, push, PR, tag) needs explicit, action-specific approval; never merge PRs, force-push or reset --hard. PRs follow `.github/pull_request_template.md`.

## Claude config

`.claude/` holds the rules, project skills (`git-workflow`, `hw-phase-record`, `hw-git-changelog`, `hw-git-readme`, `hw-git-session-log`; global KiCad library skills `hw-footprint-sync`, `hw-symbol-sync`, `hw-link-audit` live in `.claude/skills/`), the `protect_kicad_v2.py` PreToolUse hook (advisory, heuristic; rules in `hooks/protect.json`: deny / ask / allow globs) and the permission deny/ask lists in `settings.json`, which should be kept in sync with `protect.json`. It was renamed from the typo `.cluade/`; the rename takes effect after restarting Claude Code.

## Working approach

Establish objective and scope, inspect only the relevant saved design data, separate findings from proposed changes, and state assumptions and verification gaps. Keep answers concise and technical, citing refs/nets/sources.

## Language Rules
- Use English for all files, code, error messages, and git's activity messages.
- Use English for user-facing explanations, conversational text in CLI, unless otherwise specified by the user.
