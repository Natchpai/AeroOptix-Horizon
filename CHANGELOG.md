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
- Pinmap decisions file for the team (`AO-HORIZON_PINMAP_DECISIONS_EN.md`): spec rows that the team's pinmap answers change, decisions D1 to D7, software questions S1 to S7 and proposals H1 and H2, checked against PX4 v1.16.2 board files.
- Integration questions for the team (`AO-HORIZON_INTEGRATION_QUESTIONS_EN.md`, rev 0.1): servo power path (D8), mounting and cable entry (D9), environment (D10), safety switch and GPS module (D11), external devices and connectors, and software questions S8 to S10. The proposed Pixhawk-style JST-GH pinouts are `NOT_VERIFIED`. Tracked as P0-021 and spec REF-09.
- Team website in `web/` (Vite, React, shadcn-admin template): block diagram (system and board views), MCU pinouts, and an Overview with phase, gate progress, open items and recent spec changes. It reads the spec, checklist, pin allocation and root README at build time and adds no values of its own. Deployed to GitHub Pages by `.github/workflows/pages.yml` on merges to `main` (PRs #18 to #24).
- Power view on the team website: power from source to load, left to right, with grouped loads. Feeds the records do not give are drawn as candidates. Built from the spec IDs, like the other views; no new design values.
- DEC-025 (specification rev 0.16, human owner): `+3V3A` feeds only the 2 ICM-45686 IMUs, on VDD and VDDIO. OPEN-011 now covers the LDO part, the load, and the IMU SPI level match with the H743 on `+3V3` and power-up order. Checklist rev 0.15, power budget rev 0.8, IMU selection rev 0.9, root `README.md` and `what-next.md` updated to match. No KiCad file read or changed.
- README title image (`assets/AO-Horizon-title-v2.png`) and the AeroOptix black-and-white logo (`documents/images/Logos/`); the two old nP logo files were replaced by `np_black.png`.

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
- Pinmap review rev 0.2 now holds the software team's answers (2026-10-24).
- Specification rev 0.10 and checklist rev 0.9: Pixhawk 6X Rev 8 added as a reference next to Pixhawk 6C by the human owner (DEC-013, REF-05, SYS-002). Team answers recorded on OPEN-001 to OPEN-003, OPEN-008, OPEN-014 and DEC-011 without changing requirement rows. New open items OPEN-015 (stock px4io expects a 24 MHz F103 clock; DS5319 Rev 20 Table 22 limits the crystal to 4 to 16 MHz) and OPEN-016 (spec rows the team's answers change), with task P0-019. The IST8310 library row now names the stock symbol and footprint.
- Pin allocation rev 0.4 (pin source note, team changes in section 2.1, findings F-11 to F-14), barometer and magnetometer selection rev 0.6 and IMU selection rev 0.8 record the team's answers. Pin tables are unchanged until the team decides. No KiCad file changed; ERC and DRC not run.
- Root `README.md`: header field `Revision` renamed `Board revision`.
- Specification rev 0.11: the software team's answers in the pinmap decisions file (rev 0.2) are applied, and the human owner accepted them. New decisions DEC-014 to DEC-018:
  - H743 pins follow `px4/fmu-v6c` and F103 pins follow `px4/io-v2`, with PX4 v1.16.2.
  - The px4io link runs on H743 USART6 to F103 USART2 at 1.5 Mb/s.
  - The 4 motors move from the F103 to H743 TIM5 (DShot only, bidirectional). The F103 drives 8 servos (flaperons, ruddervators, 4 tilt servos).
  - SAF-001 changes from "immediate landing" to: servo failsafe after 0.5 s without H743 data, and the motors stop when their DShot frames stop.
  - Crystals: H743 16 MHz; F103 8 MHz with PLL ×3, with px4io and its bootloader rebuilt by the software team. The human owner kept the F103 over the team's STM32F100 proposal.
  - The interface set changes: GPS2, the reserved UART7 TX, I2C3 and FlySky are dropped. Added: microSD on SDMMC1, a buzzer on TIM3_CH3, 3 LEDs, a Pixhawk Debug Mini connector, and the F103 safety switch.

  BMP581 is accepted as barometer 2 (BMP384 fallback). Interface rows IF-040 to IF-051 and SAF-015 are added. OPEN-002, 003, 008, 014, 015 and 016 are closed. New open items: motor stop depends on the ESC (OPEN-017), pull-down value with bidirectional DShot (OPEN-018), BMP384 fit (OPEN-019).
- Pin allocation rev 0.5: team changes applied to both MCU tables. New pins checked against ST open pin data, and the TIM5 and TIM3 AF numbers checked against the NuttX pinmap. px4io-v2 reserved F103 pins listed. Pinmap review rev 0.3 sent to the team for the new rows and questions Q20 to Q22, with the 0.2 answers kept.
- Checklist rev 0.10, barometer and magnetometer selection rev 0.7, root `README.md` and `what-next.md` updated to match. New tasks: P0-020 (team reply to pinmap 0.3), P1-015 (BMP384 fit), P2-013 (pull-down value) and P4-011 (H743 halt bench test). No KiCad file changed. ERC and DRC not run.
- IO MCU changed from STM32F103C8T6 to STM32F100C8T6B with a 24 MHz crystal, following the software team (specification rev 0.12: DEC-002, DEC-017, MCU-002, CMP-002). Stock px4io-v2 and its stock bootloader run unchanged; the bootloader runs from HSI (PX4-Bootloader `main_f1.c`). No pin moved: ST open pin data for both LQFP48 parts match on all 48 pins. F100 values from DocID16455 Rev 9 through NotebookLM: HSE 4 to 24 MHz, VDD 2 to 3.6 V, reset and PVD levels, 5 V tolerance (OPEN-020, added and closed). LCSC stock checked by the human owner. The F100 library part and the `block_diagram` text are still to do (P2-014).
- Pinmap review rev 0.3 now holds the software team's answers and a hardware response. Applied: the three px4io LEDs are fitted, F100 PA10 and PB11 get weak pull-ups, the BMP384 fallback is at 0x76 (OPEN-019), and the debug connector pinout is accepted.
- Pin allocation rev 0.6, checklist rev 0.11 (P0-020 done; new P0-021 and P2-014), power budget rev 0.5 (F100 current, reset and PVD levels), barometer and magnetometer selection rev 0.8, the decisions file, root `README.md`, `CLAUDE.md`, the design README and `what-next.md` updated to match. No KiCad file changed. ERC and DRC not run.
- Specification rev 0.13: the software team's answers to the integration questions are applied. New decisions:
  - DEC-019: 8 × 3-pin servo headers (signal, +6 V, GND) on an on-board 6 V rail, with the UBEC plugged into the board, Pixhawk style. The human owner chose this instead of the team's answer (signal and GND only, 6 V through the harness).
  - DEC-020: parts rated −40 to +85 °C, no conformal coating, no rain exposure.
  - DEC-021: GPS1 is the 10-pin full GPS port with the safety switch lines; Model G flies with the safety switch disabled in PX4; the board buzzer stays.
  - DEC-022: stock px4io image in the board's `extras/` folder, no IMU heater.
  - DEC-023: PC1 stays reserved for an analog power module; the ESC current sense goes to another ADC pin (human owner).

  Interface rows updated, and IF-052 (ESC current sense) and IF-053 (ESC telemetry) added. Mounting stays a proposal (30.5 × 30.5 mm M3, soft mount) until the CAD team confirms it (OPEN-009). New open items: UBEC input rating and servo rail copper (OPEN-021), ESC sense and telemetry pins (OPEN-022), connector pinouts and the PM02D connector, where the power sheet's JST-GH may not match the team's CLIK-Mate cable (OPEN-023).
- Checklist rev 0.12 (P0-021 done; new P0-022, P1-016, P2-015, P2-016), power budget rev 0.6 (servo rail on the board, USB-only bench power), the design README and `what-next.md` updated to match. No KiCad file changed. ERC and DRC not run.
- Integration questions rev 0.3: the team's answers kept, a note on what hardware decided after them, and follow-up questions for the team (mounting for the CAD team, devices needed on USB, ESC current use in PX4, part models and photos, test results).
- Specification rev 0.14: the human owner answered the hardware side of the follow-up questions.
  - Mounting: M3 screws, 3.2 mm holes, soft mount, board on its own tray, USB-C and microSD on adjacent edges, part height about 10 to 15 mm. Hardware sets the outline, cable entry sides and dampers at placement; the CAD team follows (MEC-002 to MEC-004, OPEN-009).
  - USB powers the board and all external 5 V ports on the bench (IF-022, OPEN-006).
  - UBEC input on a board-mount XT30 instead of a servo header position (DEC-019, PWR-011, OPEN-021).
  - PM02D board connector to match its 6-pin 2.00 mm CLIK-Mate cable; the power sheet still draws JST-GH (IF-048, OPEN-023).
  - ESC connectors: 4 × 3-pin headers with the + pin removed (IF-040).
  - DEC-024: TPS16412DRC eFuse between the PM02D and `+5V`, current limit 1.5 A. Placed, not wired (OPEN-012).
  - Team parts recorded: 4 × Skywalker 80A V2 ESCs, 4 × RDS3235 tilt servos, Kingmax C507 and DS-843MG servos (all rated for 6 V), 10 A UBEC with XT30, MS4525DO.

  The Skywalker ESCs look PWM-only (no source found for DShot), which conflicts with FUN-002 and SAF-015. FUN-002 is unchanged; the team is asked in D13 (OPEN-017).
- Integration questions rev 0.4: cleaned to open items only (D13 on the ESC, parts table, team tests). Answered sections are in rev 0.3 in Git history.
- Checklist rev 0.13 (P0-022 rewritten; P1-016 `N/A`; new P2-017 eFuse and P2-018 ESC headers), power budget rev 0.7, design README, root `README.md` and `what-next.md` updated to match. No KiCad file read or changed. ERC and DRC not run.
- Specification rev 0.15, a consistency pass with no new decisions: CMP-008 added for the TPS16412DRC eFuse (DEC-024) and the eFuse named in OPEN-010 and the verdict. Older text now matches rev 0.14 (UBEC on a board-mount XT30 in DEC-019 and the power-input scenario, USB feeding all 5 V ports, Skywalker ESCs in the DEC-016 notes). The spec now records that its power-sheet table (17 parts, DNP DF2S6.2CT) disagrees with the README and this changelog; not re-checked.
- Checklist rev 0.14 (P0-013 XT30 wording, P0-016 adds DEC-024, next action), root `README.md` (spec rev, website link, repository tree), `what-next.md` and `web/HANDOFF.md` updated to match. The website eFuse block names CMP-008. No KiCad file read or changed. ERC and DRC not run.
- Team website: the diagram views are renamed (the outer view is now Overview, the inner view System; URL ids unchanged). The System view has no power parts any more, the Overview's power chain runs left to right, and the Power view shows the IMUs on `+3V3A`. Link ends on each block side are spaced equally and centred, checked at build time. The home page has a Power view card. On the System view, I2C2 is drawn as one bus from the H743 to the two barometers and the magnetometer, connectors sit in titled zones (Connectors; USB and debug; On-board I/O) and have a tab on the cable side, and the F100 SWD pads are left of the F100.

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
- ESC current sense and ESC telemetry (IF-052, IF-053) removed from the specification: the separate Skywalker ESCs have neither wire (human owner). OPEN-022 closed.
- Stale rows in the design records: GPS2 and FlySky loads and the "barometer 2 not chosen" row in the power budget, the BMP390 and BMM150 columns in the barometer sourcing table (kept as one history line), and done items in `what-next.md` and the barometer record.

### Verification

- None recorded. No ERC, DRC or design review results are confirmed. `NOT_VERIFIED`.
- Read-only checks run by Claude on 2026-10-19 against the saved files at commit b34343e: a library link audit found no broken links, and a net trace of `power_supplies.kicad_sch` matched the spec's schematic-state table. The four sensor symbols' pin maps match their datasheet pin tables, and the TPS62142 and TPS73533 circuits were compared with TI SLVSAJ0F Rev F and SBVS087M (checked through NotebookLM, text confirmed in the source fulltext). These are not ERC, DRC or a human review.
- Read-only checks run by Claude on 2026-10-24: `klc_verify` passes, the IST8310 symbol pins match the LGA-16 footprint pads, and the library link audit is clean. Not ERC, DRC or a human review.
- Read-only checks run by Claude on 2026-10-24: STM32F100C(8-B)Tx and STM32F103C(8-B)Tx compared in ST open pin data, F100 datasheet values found in the NotebookLM source fulltext, and the `progress-update` preflight found no em dashes, undefined IDs, broken links or open items without a tracker row. Not ERC, DRC or a human review.
