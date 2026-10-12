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
### Fixed

- Renamed the misspelled `.cluade/` configuration folder to `.claude/` so rules, skills, hook and permissions load.

### Changed

- README overview, key features, repository tree and documentation links updated from the draft specification.

### Verification

- None recorded. No ERC, DRC or design review results are confirmed. `NOT_VERIFIED`.
