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
- Design records in `documents/design/`: IMU selection (ICM-45686), barometer and magnetometer selection (ICP-20100, BMP390, BMM150), draft power budget, draft STM32H743 and STM32F103 pin allocation, and STM32H743VI price and stock.
- Power sheet parts in `power_supplies.kicad_sch`: JST GH power module connector (`+VIN`, `PM02_SCL`, `PM02_SDA`), TPS62142RGTR 3.3 V buck with 2.2 µH inductor, TPS73533DRBR `+3V3A` LDO (drawn, not decided), 3.3 V indicator LED, and a DNP DF2S6.2CT on `+VIN`. All parts are unannotated, and `+5V` has no source yet (OPEN-012).
- Project library under `library/` with `sym-lib-table` and `fp-lib-table`: STM32 MCU, regulator, ESD, diode, connector, FET and passive parts with footprints and 3D models.
- Library starting points for the sensors: ICM-45686, ICP-20100, BMP390 and BMM150 symbols with LGA and WLCSP footprints. Not placed. Pin maps match the datasheet tables; land patterns and pin 1 orientation are not checked yet (OPEN-013). The BMM150 3D model is missing from the KiCad 10 install.
- BMP581 library starting point: `0_Sensor_Pressure:BMP581`, pin map checked against BST-BMP581-DS004-13 Rev 1.13 Table 28 through NotebookLM. Not placed. BMP581 is a candidate, not a decided part (OPEN-014).
- TPS16412DRC eFuse symbol and `Texas_VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm_ThermalVias` footprint in the project library.
- TPS16412DRC eFuse placed on `power_supplies.kicad_sch` (unannotated). ERC not run.
- IST8310 library part: stock KiCad `0_Sensor_Magnetic:IST8310` symbol and `0_Package_LGA:LGA-16_3x3mm_P0.5mm` footprint, with MFR, MPN and LCSC C2683055 fields. Not placed. The IST8310 datasheet (V1.2 and V1.8) has no land pattern, so the footprint fit is `ESTIMATED` from the package drawing.
- Pinmap review sheet for the software team (`AO-HORIZON_PINMAP_REVIEW_EN.md`). Rev 0.2 adds proposed pins for the remaining functions and questions Q11 to Q19. No answers received yet.
- Pin allocation rev 0.3: draft pins for LEDs, buzzer, safety switch, IST8310 DRDY and RSTN, IMU pin 9 and F103 NRST/BOOT0 control (`ASSUMED`, not approved), and findings F-08 to F-10 (PA10 note, PM02D I2C bus not assigned, TIM15 DMA).
- PX4 Matek H743-Slim board port files as a pin-map reference in `documents/reference/px4-matek-h743-slim/`: unmodified copies from PX4-Autopilot `b26146e` and PX4/NuttX `8626377`. Not design data.
- `documents/design/what-next.md`: personal reminder list of next steps.

### Changed

- Root `README.md` rewritten from the draft specification: overview, key features, specifications, architecture, logical interface allocations, design considerations and open items. Undecided values are marked `TBD`; all verification checks are `NOT_VERIFIED`.
- `.gitignore` now ignores `settings.local.json`.
- Library folder references in `.claude/` (permission deny rule, hook message, skills, README template) changed from `Library/` to lowercase `library/` to match the actual directory.
- Licence changed from CERN-OHL-W-2.0 (weakly reciprocal) to CERN-OHL-S-2.0 (strongly reciprocal); `LICENSE` text and the README licence section updated.
- Removed the stale `meta/` entry from the repository tree in `hardware/AO-Horizon/README.md`.
- Specification rev 0.1 to 0.7: recorded decisions DEC-005 to DEC-012 (USART monitoring path, board size limit under 80 mm × 80 mm, power input and servo limits, 2 × ICM-45686 with software reset, ICP-20100 + BMP390, 1 × BMM150, TPS62142RGTR main 3.3 V buck), open items up to OPEN-013, and the power-sheet and sensor-library state. Execution checklist is at rev 0.6.
- Sensor lifecycle recorded: ICP-20100 is EOL (TDK), and Bosch no longer lists BMM150. Both are decided parts (DEC-010, DEC-011), so their sourcing stays open (OPEN-004).
- Library names follow KLC: `STM32F103C8Tx`, `0_Conn:Conn_ARM_JTAG_SWD_10`, `0_Diode:SMBJ30A`, the VSON-8 thermal-via footprint (its two schematic Footprint fields updated), and lowercase `.step` model files.
- Claude Code configuration: KiCad library checks and syncs now run from the global `kicad-*` skills, the local `hw-link-audit` and `hw-*-sync` copies are removed, the `progress-update` skill is added, and all project skills are tracked.
- BMP390 removed from the design because LCSC C5124834 is not available (DEC-010 revised, specification rev 0.8, checklist rev 0.7). The second barometer is open (OPEN-014); Bosch BMP581 (LCSC C5362283) is proposed and waits for team confirmation. The BMP390 library symbol and footprint are kept until then.
- `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y` pads changed from the ST size (0.425 × 0.35 mm) to the BMP581 land pattern (0.325 × 0.30 mm, smallest gap 0.20 mm); description and tags updated. The pad sizes were read from a datasheet figure and are `NOT_VERIFIED`. DRC not run.
- Root `README.md`: `Status` changed from `CONCEPT` to `DRAFT` to match the declared phase.
- Root `README.md` and `CLAUDE.md` rewritten for the current design state and workflow. `hardware/AO-Horizon/README.md` and the `documents/` and `documents/design/` indexes now name the real project files and records.
- Magnetometer changed from Bosch BMM150 to iSentek IST8310 by the human owner (DEC-011 revised, specification rev 0.9, checklist rev 0.8, selection record rev 0.5, power budget rev 0.4). IST8310 values come from its datasheet V1.2 through NotebookLM. Its absolute maximum supply is 3.6 V, so the 3.3 V rail has only 0.3 V of margin. The BMM150 library files are kept and marked not used.
- Project library restyled to the KLC house style: symbols redrawn with separate pins, footprint fab, silkscreen and courtyard redrawn. Later, field and body positions moved on the IST8310, BMP390, BMP581 and TPS62142 symbols.
- `.gitignore` now ignores the `hardware/AO-Horizon/libDump/` staging folder.

### Fixed

- Renamed the misspelled `.cluade/` configuration folder to `.claude/` so rules, skills, hook and permissions load.
- The `Edit(**/Library/**)` deny rule did not match the lowercase `library/` directory; it now uses `library`.
- `hardware/AO-Horizon/README.md` still had template text (`my_Kicad10_Template_Rev4` file names and a `meta/` folder). It now describes the AO-Horizon project.
- The README board outline now follows MEC-001 (each dimension under 80 mm) instead of the older diagram size of about 90 mm × 95 mm.
- The power budget record (rev 0.2) no longer says that no regulator is approved; it cites DEC-012.

### Removed

- `.claude/settings.local.json` is no longer tracked (local-only file, now git-ignored).
- `AO-HORIZON_HANDOFF_EN.md`: its content was merged into the execution checklist.
- DNP DF2S6.2CT ESD diode removed from `power_supplies.kicad_sch`.

### Verification

- None recorded. No ERC, DRC or design review results are confirmed. `NOT_VERIFIED`.
- Read-only checks run by Claude on 2026-10-19 against the saved files at commit b34343e: a library link audit found no broken links, and a net trace of `power_supplies.kicad_sch` matched the spec's schematic-state table. The four sensor symbols' pin maps match their datasheet pin tables, and the TPS62142 and TPS73533 circuits were compared with TI SLVSAJ0F Rev F and SBVS087M (checked through NotebookLM, text confirmed in the source fulltext). These are not ERC, DRC or a human review.
- Read-only checks run by Claude on 2026-10-24: `klc_verify` passes, the IST8310 symbol pins match the LGA-16 footprint pads, and the library link audit is clean. Not ERC, DRC or a human review.
