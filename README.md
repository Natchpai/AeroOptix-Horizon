<p align="center">
  <img src="assets/AO-Horizon-v2.png" alt="AO-Horizon title" width="100%" >
</p>

> **Status:** `DRAFT`
> **Board revision:** `A`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.8`

> **Draft specification (rev 0.55, 2026-11-19): NOT FOR FABRICATION.** Everything below is a design target from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The STM32H743VIT6 runs the flight stack and drives the 4 tilt servo outputs. The STM32F100C8T6B runs px4io and drives the 4 ESC outputs, the 4 control-surface servo outputs, the safety switch and the output failsafe (DEC-050, DEC-051).

Pixhawk 6C and 6X are functional references only; their schematics and PCBs are not copied. H743 pins mostly follow `px4/fmu-v6c`, F100 pins follow `px4/io-v2` (DEC-014).

The team website, [natchpai.github.io/AeroOptix-Horizon](https://natchpai.github.io/AeroOptix-Horizon/), shows the block diagram, the MCU pinouts and the status, built from the design records.

## Key Features

- STM32H743VIT6 flight MCU and STM32F100C8T6B px4io MCU, linked over USART at 1.5 Mb/s
- 4 ESC outputs (MAIN 1 to 4) and 4 control-surface outputs (MAIN 5 to 8) on the F100, 4 tilt servo outputs (AUX 1 to 4) on the H743; 8 servo headers on an on-board 6 V rail, 3 spare outputs
- 2× ICM-45686 IMU on SPI; ICP-20100 and BMP581 barometers and IST8310 magnetometer on I2C
- 5 V input through a TPS2121 power mux (power module or USB), 3.3 V buck, separate LDO for the sensor VDD pins
- USB FS, microSD, debug access to both MCUs, selectable BOOT0

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
| Servo supply | 6 V UBEC into a board-mount XT30, 7.4 V maximum (servo rating), 10 A continuous, 15 A peak; all 8 servos stalled about 13.2 A, `ESTIMATED` (PWR-011, DEC-019, OPEN-007; XT30 rating `TBD`, OPEN-021) |
| Board outline | Under 80 mm each side; exact outline `TBD` (MEC-001, OPEN-009) |
| Mounting | M3, 3.2 mm holes, soft mount; pattern `TBD` (MEC-002, OPEN-009) |
| Layers / stackup | `TBD` (PCB-001, PCB-002) |
| Temperature | Parts rated −40 to +85 °C (ENV-001, DEC-020) |

*Specifications describe design targets unless explicitly identified as measured or verified results.*

## Project Status

**Current Phase:** `DRAFT`

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

    class A review
    class B inactive
    class C inactive
    class D inactive
```

> Slate: not started, Amber: current phase, Green: completed

The diagram is for reference only. It does not enforce gates or approve releases.

### Design progress

State of the saved KiCad files (2026-11-19 12:49 save, not committed). Sheets not listed have no parts. Part lists, references and save dates are in specification 4.2 "Schematic state", 4.3 and 4.6.

| Area | State |
|---|---|
| Power sheet | Drawn; human ERC and a `sch-review` of the 2026-11-03 save are under Verification; LCSC codes on all resistors; PR1, CP2 and OV bottom resistors 5.1 kΩ, OV trip 5.51 to 6.21 V (DEC-055); MFR fields open (P2-021). |
| MCU sheets | In capture; one shared reset with one button decided, button drawn on `user-interface` and its part not checked (DEC-046, OPEN-026); board LEDs drawn, driven straight from the pins, active low, 220 Ω (OPEN-035); oscillator parts decided, data open (DEC-048, OPEN-028); VREF+ tied to VDDA (DEC-049); all allocated pins labelled with DEC-052 net names and every sheet pin matching its label; a few names open (OPEN-032); new 22 Ω and 10 nF on the ADC inputs, servo-rail divider drawn on `conn-actuator` (OPEN-033). |
| Sensor sheets | In capture with all five sensors; IST8310 at 0x0C as strapped (DEC-047, closes OPEN-027). |
| USB and debug sheet | In capture; parts drawn, not approved (OPEN-010); CN602 (H743) and CN603 (F100) JST-SH 6-pin in the Pixhawk Debug Mini order, no NRST (OPEN-029); USB-C CC resistors 5.1 kΩ. |
| External connectors | Drawn, not decided (spec 4.2): `conn-peripherals` (TELEM 1 and 2, I2C4, rangefinder, GPS1) linked to the MCU sheets by sheet pins; `conn-actuator` with MAIN 1 to 4 ESC headers (no + pin), MAIN 5 to 8 and AUX 1 to 4 on `+6V`, the CN804 XT30 UBEC input, 6 V bulk capacitors, a TVS and the servo-rail divider. Decided 2026-11-19: C803 68 µF 16 V tantalum (DEC-058) and D807 SMF7.5A unidirectional TVS (DEC-059). RC IN drawn (2026-11-19 15:25 save): D707 SP3031-01ETG ESD, R715 22 Ω (R714 before the 16:03 save) and the U303 SN74LVC1G34DCKR buffer to F100 PA8 (DEC-056, DEC-057); the CN706 JST-GH connector and its pin order differ from DEC-053 and wait on a team decision (OPEN-034 item 6a, P2-023). Pinouts open (OPEN-023). |
| PCB | No footprints. The 80 × 80 mm `Edge.Cuts` rectangle is a working area, not the board outline (OPEN-009). |
| Library | Project parts for the parts in use; sensor footprints not checked against the drawings (OPEN-013). New: Amass XT30PW-M symbol, footprint and 3D model. |

## Hardware Design

### Architecture

| Block | Role |
|---|---|
| H743 main controller | Flight stack and interface host; 4 tilt servo outputs (AUX 1 to 4) |
| F100 IO controller | px4io: 4 ESC and 4 control-surface outputs (MAIN 1 to 8), safety switch and LED, servo rail sense, output failsafe (DEC-051) |
| Sensors | 2 IMU on SPI1 and SPI4; 2 barometers and the magnetometer on I2C2 |
| External I/O | SiK telemetry radio, RC receiver (PPM, F100), GPS and compass, air-data sensor, rangefinder, power module, motors (one 4in1 ESC), spare outputs, microSD, buzzer, LEDs (DEC-053, DEC-054, DEC-056, DEC-057) |
| USB / debug | USB FS; H743 debug connector (target: console + SWD, IF-045; as drawn: OPEN-029); F100 SWD pads |
| Power | 5 V input, 3.3 V buck, sensor LDO, 6 V servo rail |

### External interfaces

Interface allocations agreed with the software team (DEC-014, DEC-018) are in specification sections 3.4 and 3.5 ([spec](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md)) and the [pin allocation record](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md); connector pinouts are not checked yet (OPEN-023).

### Design Considerations

- IO MCU and clocks: STM32F100C8T6B for px4io at 24 MHz; CMOS oscillators with HSE bypass set in firmware (DEC-002, DEC-017, DEC-044, DEC-045).
- USB power: bench supply only, needs a USB-C port above 1 A; the power module has priority (DEC-031 to DEC-034, DEC-038).
- Actuator outputs and H743 failure: the ESCs run timer PWM from the F100 (no DShot). When the H743 stops, the F100 turns the motors off and sets the surfaces to a fixed position, with no landing; the tilt servos on the H743 hold their last angle (DEC-050, DEC-051). Whether the ESCs stop on the failsafe pulse is open (OPEN-017).
- Net names: a signal that leaves its sheet starts with its port, plus the MCU peripheral on peripheral pins (for example `GPS1_UART2_TX`); `H7_`/`F1_` on nets local to an MCU sheet; `_B` for active-low. Bus names and port numbering are the designer's choice (DEC-052, partly drawn).
- Sensor sourcing: ICP-20100 is EOL, BMP581 stock is short (OPEN-004).
- Firmware: owned by the software team, PX4 v1.16.2 based on `px4/fmu-v6c` (DEC-014).

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | Whole schematic, 2026-11-19 12:49 save: 0 errors, 0 warnings | Run by the human owner; [`ERC.rpt`](hardware/AO-Horizon/documents/verification/ERC.rpt). An ERC pass is not a proof of correctness |
| Schematic review | Power sheet (2026-11-03 save); connector and actuator sheets (2026-11-19 12:49 save) | `sch-review`, spec 4.3 and 4.2; findings open (OPEN-021, OPEN-037); OPEN-038 closed |
| PCB DRC | `NOT_VERIFIED` | PCB is empty |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | Bench tasks P4-012 to P4-015 open |

## Open Items

The specification tracks every open item in section 8.2 of the [specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md). Top items now:

- ESC stop on the F100 failsafe pulse, now the Tekko32 with AM32 (OPEN-017)
- RC IN: buffer and parts decided (DEC-056, DEC-057); CN706 connector type and pin order against DEC-053 to decide with the team; FS-iA6B PPM level and RC-loss behavior, Tekko32 pinout (OPEN-034)
- Reset: the button's LCSC part is not checked (B901 pad pairs confirmed), and an H743 internal reset may also reset the F100 (OPEN-026)
- Debug access: CN602 and CN603 drawn in the Pixhawk Debug Mini order, no NRST (OPEN-029)
- H743 VDDA capacitor drawn 2.2 µF where DEC-049 says 4.7 µF (OPEN-030)
- Actuator headers: keep the ESC headers (no + pin) apart from the +6 V servo headers; ESC PWM rate (OPEN-031)
- Net names: `OSC_*` prefix choice, spare output order against the pin allocation (OPEN-032)
- Servo rail sense: the 3:1 divider on F100 PA4 is drawn, not decided (OPEN-033)
- Servo power: all 8 servos stalled draw about 13.2 A, over the 10 A UBEC continuous rating (OPEN-007); XT30 rating (OPEN-021)
- Board LEDs: LED current and H743 sink current not checked (OPEN-035)
- GPS1 port: Q701 buzzer FET accepted (DEC-057); D706 standoff on the 0~5 V buzzer line not checked; buzzer type and flyback diode unknown; R711 0 Ω on the CN705 pin 8 `+3V3` export, short risk accepted (DEC-060) (OPEN-037)
- Servo bus: C803 now 16 V (DEC-058); D807 SMF7.5A breakdown and leakage at 7.4 V not checked (DEC-059); XT30 rating, copper and GND join open (OPEN-021)

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
