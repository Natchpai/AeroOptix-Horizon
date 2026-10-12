# Changelog

Notable changes to this hardware project are documented here.

## [Unreleased]

### Added

- KiCad 10 project scaffold under `hardware/AO-Horizon/`: root schematic, `top_hierarchical`, `block_diagram`, `power_supplies` and `revision_history` sheets, and an empty PCB file. No schematic symbols or PCB footprints are placed yet.
- Draft advanced specification, handoff and execution checklist (`documents/design/`), rev 0.1, marked "NOT FOR FABRICATION". Defines the STM32H743VIT6 + STM32F103C8T6 dual-MCU architecture and lists open items OPEN-001 to OPEN-010.
- Custom KiCad worksheet templates, theme, and fabrication, assembly and impedance note templates (`templates/`).
- STEP 3D model for LQFP-100 14×14 mm, 0.5 mm pitch (`library/3D/`).
- Documentation folder structure with README stubs for manufacturing, schematic, verification and images.
- Project README, CERN-OHL-W-2.0 licence, and a pull request template.
- Claude Code project configuration (rules, skills, KiCad file-protection hook, permissions).
- `.gitattributes` marking development-only files (`.claude/`, `CLAUDE.md`, `README.md`, `.github/`, `.gitignore`, `.gitattributes`, `.vscode/`) as `export-ignore`.
- `CLAUDE.md` with repository layout, read-only design rules and git approval rules.
- `CHANGELOG.md`.

### Changed

- Root `README.md` rewritten from the draft specification: overview, key features, specifications, architecture, logical interface allocations, design considerations and open items. Undecided values are marked `TBD`; all verification checks are `NOT_VERIFIED`.
- `.gitignore` now ignores `settings.local.json`.
- Library folder references in `.claude/` (permission deny rule, hook message, skills, README template) changed from `Library/` to lowercase `library/` to match the actual directory.
- Removed the stale `meta/` entry from the repository tree in `hardware/AO-Horizon/README.md`.

### Fixed

- Renamed the misspelled `.cluade/` configuration folder to `.claude/` so rules, skills, hook and permissions load.
- The `Edit(**/Library/**)` deny rule did not match the lowercase `library/` directory; it now uses `library`.

### Removed

- `.claude/settings.local.json` is no longer tracked (local-only file, now git-ignored).

### Verification

- None recorded. No ERC, DRC or design review results are confirmed. `NOT_VERIFIED`.
