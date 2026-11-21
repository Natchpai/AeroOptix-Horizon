<p align="center">
  <img src="assets/AO-Horizon-v2.png" alt="AO-Horizon title" width="100%" >
</p>

**Flight controller for the AeroOptix Club aircraft, STM32H743 with an STM32F100 IO MCU**

> **Status:** `PRELIMINARY`
> **Board revision:** `A`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.8`

> **Draft specification (rev 0.81, 2026-11-21): NOT FOR FABRICATION.** Everything below is a design target from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The STM32H743VIT6 runs the flight stack and drives the 4 tilt servo outputs. The STM32F100C8T6B runs px4io and drives the 4 ESC outputs, the 4 control-surface servo outputs, the safety switch and the output failsafe (DEC-050, DEC-051).

Pixhawk 6C and 6X are functional references only; their schematics and PCBs are not copied. H743 pins mostly follow `px4/fmu-v6c`, F100 pins follow `px4/io-v2` (DEC-014).

The team website, [natchpai.github.io/AeroOptix-Horizon](https://natchpai.github.io/AeroOptix-Horizon/), shows the block diagram, the MCU pinouts and the status, built from the design records.

## Key Features

- STM32H743VIT6 flight MCU and STM32F100C8T6B px4io MCU, linked over USART at 1.5 Mb/s
- 4 ESC outputs (MAIN 1 to 4) and 4 control-surface outputs (MAIN 5 to 8) on the F100, 4 tilt servo outputs (AUX 1 to 4) on the H743; 8 servo headers on an on-board 6 V rail, 3 spare outputs
- 2× ICM-45686 IMU on SPI; ICP-20100 and BMP581 barometers and IST8310 magnetometer on I2C
- 5 V input through a TPS2121 power mux (power module or USB), 3.3 V buck, separate LDO for the sensor VDD pins
- USB FS, microSD, debug access to both MCUs, BOOT0 push button on the H743

## Specifications

| Parameter | Specification |
|---|---|
| Main MCU | STM32H743VIT6 (DEC-001) |
| IO MCU | STM32F100C8T6B (px4io, DEC-002) |
| Clocks | H743 16 MHz, F100 24 MHz, both from CMOS oscillators (DEC-017, DEC-044) |
| Outputs | F100 MAIN 1 to 4: 4 ESCs (PWM, 1000 to 2000 µs); F100 MAIN 5 to 8: 4 control surfaces (50 Hz PWM); H743 AUX 1 to 4: 4 tilt servos; 3 spare (H743) (DEC-050, DEC-051, FUN-002, FUN-003, IF-017 to IF-019) |
| Sensors | 2× ICM-45686, ICP-20100 + BMP581 (BMP384 fallback), IST8310 (DEC-008, DEC-010, DEC-011) |
| Board input | 5 V, 4.5 to 5.5 V, 2 A source; power mux limit 1.5 A; overvoltage cut-off 5.5 to 6.2 V (PWR-010, DEC-029, DEC-030, DEC-036, DEC-055) |
| 3.3 V rails | `+3V3` buck, design current about 0.6 A (DEC-012, DEC-040); `+3V3A` LDO for the sensor VDD pins; sensor VDDIO on `+3V3` (DEC-043, DEC-027) |
| Servo supply | 6 V UBEC into a board-mount XT30, 7.4 V maximum (servo rating), 10 A continuous, 15 A peak; all 8 servos stalled about 13.2 A, `ESTIMATED` (PWR-011, DEC-019); XT30PW-M rated 15 A; on-board bulk 156 µF nominal (DEC-097); copper and GND join set at layout (OPEN-021) |
| Board outline | Under 80 mm each side; exact outline `TBD` (MEC-001, OPEN-009) |
| Mounting | M3, 3.2 mm holes, soft mount; pattern `TBD` (MEC-002, OPEN-009) |
| Layers / stackup | Drawn, not decided: 4 copper layers, about 1.6 mm, 0.1 mm track and clearance (PCB-001 to PCB-005, OPEN-040) |
| Temperature | Parts rated −40 to +85 °C (ENV-001, DEC-020) |

*Specifications describe design targets unless explicitly identified as measured or verified results.*

## Project Status

**Current Phase:** `PRELIMINARY`

| Phase | Description |
|---|---|
| DRAFT | Schematic design in progress |
| PRELIMINARY | Schematic nearly complete; PCB design started |
| CHECK | Design mostly finalized; human-led verification |
| RELEASE | Human-approved design baseline released |

*The project owner declares the current phase. It does not independently establish design correctness or approval.*

### Project Workflow Diagram

```mermaid
flowchart LR
    A["DRAFT<br/>Schematic Design"]
    B["PRELIMINARY<br/>Schematic Finalization<br/>PCB Design"]
    C["CHECK<br/>Design Docs<br/>ERC / DRC<br/>Human Review"]
    D["RELEASE<br/>Approved Design<br/>Baseline Publication"]

    A --> B
    B --> C
    C --> D

    classDef inactive fill:#334155,color:#ffffff,stroke:#64748b
    classDef review fill:#b45309,color:#ffffff,stroke:#92400e
    classDef done fill:#15803d,color:#ffffff,stroke:#166534

    class A done
    class B review
    class C inactive
    class D inactive
```

> Slate: not started, Amber: current phase, Green: completed

The diagram is for reference only. It does not enforce gates or approve releases.

### Design progress

State of the saved KiCad files (2026-11-21 11:12 save, commit `3c111fc`). Sheets not listed have no parts. Part lists, references and save dates are in specification 4.2 "Schematic state", 4.3 and 4.6. Pin allocation `ALLOCATED`, not `VERIFIED` (P1 closed by the human owner, 2026-11-21).

| Area | State |
|---|---|
| Power sheet | Drawn; human ERC and a `sch-review` of the 2026-11-03 save are under Verification; LCSC codes on all resistors; PR1, CP2 and OV bottom resistors 5.1 kΩ, OV trip 5.51 to 6.21 V (DEC-055); MFR, MFR.P/N and LCSC filled on R101 to R115 (P2-021 done 2026-11-21; 1 % tolerance `ASSUMED`). |
| MCU sheets | In capture; one shared reset with one button decided; B901 PTS815SJM250SMTRLFS checked against LCSC C2689510, reset bench check open (DEC-046, OPEN-026); BOOT0 push button B902 to `+3V3` with R202 10 kΩ to `GND`, and F100 PB2 (BOOT1) without a resistor (DEC-095); separate NRST nets for each MCU behind D201 and D301, joined at B901 (DEC-074); board LEDs driven straight from the pins, active low, 220 Ω (DEC-067); F100 px4io LEDs (blue, red, green) and 10 kΩ pull-ups on PA10 and PB11 (DEC-079); microSD 10 kΩ pull-ups on CMD and DAT0 to DAT3, no card detect (DEC-078), 100 nF and 2.2 µF at the card supply (DEC-081); oscillator parts decided and their data meets both MCU HSE bypass limits (DEC-048, CMP-010); LCSC codes match the part numbers (CMP-010); U302 clock margins accepted (DEC-089); VREF+ tied to VDDA with 2.2 µF (DEC-049, DEC-063); all allocated pins labelled with DEC-052 net names and every sheet pin matching its label; the INFO names accepted as drawn (OPEN-032 closed); resistors renumbered without gaps (spec rev 0.75); 22 Ω and 10 nF on the ADC inputs and the servo-rail divider on `conn-actuator` decided (DEC-066). |
| Sensor sheets | In capture with all five sensors; IST8310 at 0x0C as strapped (DEC-047, closes OPEN-027). ICM-45686 RESV pin 7 not connected (DEC-082); BMP581 INT through 10 kΩ to `GND`, ICP-20100 INT not connected (DEC-083); ICP-20100 power-up order accepted, bench check (DEC-085). I2C2 pull-ups R501 and R502 5.1 kΩ kept, bus at 400 kHz (DEC-094); U503 placed as far as possible from the power parts (DEC-096). |
| USB and debug sheet | In capture; MFR, MFR.P/N and LCSC on every BOM part (OPEN-010 closed); CN602 (H743) JST-SH 6-pin in the Pixhawk Debug Mini order, no NRST, reset by B901 (DEC-065); F100 debug on test pads TP601 to TP606, with TP605 on `RESET_B` (DEC-075); USB-C CC resistors 5.1 kΩ; USB nets checked and no `VBUS` back-feed through U101 (P1-006); VBUS sense on PA9 through a 5.1 kΩ / 10 kΩ divider, so PA9 stays under 4 V when the MCU is unpowered (DEC-080); USB ESD is the ST USBLC6-2SC6, LCSC C7519 (DEC-084). |
| External connectors | Drawn, not decided (spec 4.2): `conn-peripherals` (TELEM 1 and 2, I2C4, rangefinder, GPS1) linked to the MCU sheets by sheet pins; `conn-actuator` with MAIN 1 to 4 ESC headers (no + pin), MAIN 5 to 8 and AUX 1 to 4 on `+6V`, the CN804 XT30 UBEC input, 6 V bulk capacitors, a TVS and the servo-rail divider. Decided 2026-11-19: C803 68 µF 16 V tantalum (DEC-058) and D807 SMF7.5A unidirectional TVS (DEC-059). RC IN drawn (2026-11-19 15:25 save): SP3031-01ETG ESD (D708 since the 23:17 save; DEC-071), R715 22 Ω (R714 before the 16:03 save) and the U303 SN74LVC1G34DCKR buffer to F100 PA8 (DEC-056, DEC-057); CN706 is a 1x3 2.54 mm header since the 2026-11-20 save, with pin 1 `+5V`, 2 PPM, 3 `GND`, kept as drawn (DEC-072). 100 kΩ pull-downs on all 15 PWM lines (DEC-073). Spare outputs: 22 Ω series, pull-downs and pads CN707 to CN710 drawn (DEC-069, DEC-076). Second 68 µF T495 (C804) on `+6V`, 156 µF bulk (DEC-097). Connector pinouts match DS-009; CN704 silkscreen left (OPEN-023). |
| PCB | 269 footprints imported (2026-11-20, commit `a70e6cc`), 9 placed inside the working area, no routing. 4-layer stackup and board rules drawn, not decided (OPEN-040). Not yet updated from the 2026-11-21 schematic. The 80 × 80 mm `Edge.Cuts` rectangle is a working area, not the board outline (OPEN-009). |
| Library | Project parts for the parts in use. Sensor footprints: IST8310 and BMP581 confirmed by the human owner, with a 30 µm solder mask margin on purpose; ICP-20100 and ICM-45686 match the datasheet body, pitch and pad numbers and are kept without the TDK land-pattern app notes (DEC-086). New: Amass XT30PW-M symbol, footprint and 3D model. MFR and MFR.P/N on the 20 placed, fully specified library symbols; descriptions in one pattern (2026-11-20). |

## Hardware Design

### Architecture

| Block | Role |
|---|---|
| H743 main controller | Flight stack and interface host; 4 tilt servo outputs (AUX 1 to 4) |
| F100 IO controller | px4io: 4 ESC and 4 control-surface outputs (MAIN 1 to 8), safety switch and LED, servo rail sense, output failsafe (DEC-051) |
| Sensors | 2 IMU on SPI1 and SPI4; 2 barometers and the magnetometer on I2C2 |
| External I/O | SiK telemetry radio, RC receiver (PPM, F100), GPS and compass, air-data sensor, rangefinder, power module, motors (one 4in1 ESC), spare output pads, microSD, GPS module buzzer (no board buzzer), LEDs (DEC-053, DEC-054, DEC-056, DEC-057, DEC-068, DEC-069) |
| USB / debug | USB FS; H743 debug connector CN602, console + SWD in the Pixhawk Debug Mini order, no NRST (IF-045, DEC-065); F100 console + SWD on test pads TP601 to TP606 (IF-051, DEC-075) |
| Power | 5 V input, 3.3 V buck, sensor LDO, 6 V servo rail |

### External interfaces

Interface allocations agreed with the software team (DEC-014, DEC-018) are in specification sections 3.4 and 3.5 ([spec](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md)) and the [pin allocation record](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md); connector pinouts are not checked yet (OPEN-023).

### Design Considerations

- IO MCU and clocks: STM32F100C8T6B for px4io at 24 MHz; CMOS oscillators with HSE bypass set in firmware (DEC-002, DEC-017, DEC-044, DEC-045).
- USB power: bench supply only, needs a USB-C port above 1 A; the power module has priority (DEC-031 to DEC-034, DEC-038).
- Actuator outputs and H743 failure: the ESCs run timer PWM from the F100 (no DShot). When the H743 stops, the F100 turns the motors off and sets the surfaces to a fixed position, with no landing; the tilt servos on the H743 hold their last angle (DEC-050, DEC-051). Whether the ESCs stop on the failsafe pulse is open (OPEN-017).
- Net names: a signal that leaves its sheet starts with its port, plus the MCU peripheral on peripheral pins (for example `GPS1_UART2_TX`); `H7_`/`F1_` on nets local to an MCU sheet; `_B` for active-low. Bus names and port numbering are the designer's choice (DEC-052, partly drawn).
- Sensor sourcing: ICP-20100 is EOL, BMP581 stock is short (OPEN-004).
- Sensor use and vibration: sample rates, calibration and how PX4 uses the redundant sensors are software work, deferred (DEC-061). No numeric vibration limit for revision 1: the soft mount is the control, checked with PX4 vibration metrics in the flight logs (DEC-062).
- Firmware: owned by the software team, PX4 v1.16.2 based on `px4/fmu-v6c` (DEC-014).

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | Whole schematic, 2026-11-21 11:18 export on the 11:12 save: 0 errors, 0 warnings | [`AO-Horizon-erc.rpt`](hardware/AO-Horizon/documents/verification/AO-Horizon-erc.rpt), run by the human owner. An ERC pass is not a proof of correctness |
| Schematic review | Power sheet (2026-11-03 save); connector and actuator sheets (2026-11-19 12:49 save); MCU sheets (2026-11-20, commit `6b01a14`); sensor and USB sheets (2026-11-20 14:29 save) | `sch-review`, spec 4.3 and 4.2; findings open (OPEN-021, OPEN-023); OPEN-038 closed. MCU sheets: the PA9 VBUS MAJOR is fixed (DEC-080); MINOR and INFO findings in `todo.md`. Sensor and USB sheets: no connectivity defect; findings closed by DEC-081 to DEC-085. All 12 bus links traced with the KiCad netlist (16:03 save): every member reaches its allocated pin; the spare outputs reach no pad yet |
| Pin allocation review | Signed off by the human owner, 2026-11-21: `ALLOCATED`, not `VERIFIED` | [Pin allocation](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md) section 6 |
| PCB DRC | `NOT_VERIFIED` | Not run; PCB not routed |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | Bench tasks P4-012 to P4-015 open |

## Open Items

The specification tracks every open item in section 8.2 of the [specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md). Top items now:

- ESC (Tekko32 with AM32): stop on the F100 failsafe pulse, PWM rate, 8-pin pinout, BEC and PWM level (OPEN-017)
- RC IN: U303 inputs take 5.5 V (ti.com); FS-iA6B PPM level, RC-loss behavior and receiver lead are bench and team items (OPEN-034, P4-016)
- PCB stackup and board rules drawn, not decided; fabricator confirmation needed (OPEN-040, P3-010)
- Board outline, mounting and cable entry (OPEN-009, P3-001)
- Servo power: 156 µF bulk (DEC-097); copper width and the servo/logic GND join set at layout (OPEN-021, P3-003)
- Actuator headers: keep the ESC and RC IN headers apart from the +6 V servo headers, at placement and on the silkscreen (OPEN-031, P3-002, P3-007)
- Sensors: ICP-20100 EOL, BMP581 stock and IST8310 lifecycle (OPEN-004, P3-007)
- Bench checks: reset paths (OPEN-026, P4-002) and sensor power-up order (OPEN-011, P4-015)
- Firmware: HSE bypass on both MCUs (OPEN-028, P2-005)

## How we work

1. A human engineer makes every design decision and declares the phase; decisions go into the specification first.
2. The saved KiCad files are the design authority; the Markdown records describe them.
3. Values carry evidence labels (`VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`). ERC and DRC are evidence, not proof.
4. Changes go through `dev` and a pull request to `main`, with Conventional Commits.

Claude Code support (rules, skills, file protection) is in `.claude/` and `CLAUDE.md`.

## Repository Structure

```text
AeroOptix-Horizon/
├── hardware/AO-Horizon/
│   ├── AO-Horizon.kicad_pro           # KiCad project
│   ├── *.kicad_sch, AO-Horizon.kicad_pcb
│   ├── library/                       # Project symbols, footprints, 3D models
│   ├── documents/design/              # Specification, checklist, design records
│   ├── documents/                     # Reference, manufacturing, schematic, verification, images
│   └── templates/                     # Worksheets, theme, fab/assembly notes
├── web/                               # Team website, built from the records
├── assets/                            # README title image
├── .claude/, .github/                 # Claude Code config; PR template and Pages workflow
├── CLAUDE.md, CHANGELOG.md, LICENSE
└── README.md
```

## Documentation

| Resource | Description |
|---|---|
| [Specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md) | Requirements, decisions, schematic and library state, open items |
| [Execution checklist](hardware/AO-Horizon/documents/design/AO-HORIZON_EXECUTION_CHECKLIST_EN.md) | Work plan and evidence tracker |
| [Power budget](hardware/AO-Horizon/documents/design/AO-HORIZON_POWER_BUDGET_EN.md) | Rail loads, tolerances and protection |
| [Power mux notes](hardware/AO-Horizon/documents/design/AO-HORIZON_POWER_MUX_NOTES_EN.md) | TPS2121 modes and resistor calculations |
| [Pin allocation](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md) | H743 and F100 pin allocation |
| [Software clock note](hardware/AO-Horizon/documents/design/AO-HORIZON_SW_CLOCK_NOTE_EN.md) | HSE bypass request to the software team (DEC-045, P1-017) |
| [Design records index](hardware/AO-Horizon/documents/design/README.md) | All other records: sensor selection, pinmap review and decisions, integration questions, sourcing |
| [Team website](https://natchpai.github.io/AeroOptix-Horizon/) | Block diagram, MCU pinouts and status ([source](web/README.md)) |

## License

Copyright (c) 2026 AeroOptix Club.

The hardware design files are licensed under CERN-OHL-S-2.0.

The complete license text is available in:

[CERN Open Hardware Licence Version 2 - Strongly Reciprocal](LICENSE)

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
