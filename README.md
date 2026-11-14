<p align="center">
  <img src="assets/AO-Horizon-v2.png" alt="AO-Horizon title" width="100%" >
</p>

> **Status:** `DRAFT`
> **Board revision:** `A`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.8`

> **Draft specification (rev 0.40, 2026-11-14): NOT FOR FABRICATION.** Everything below is a design target from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The STM32H743VIT6 runs the flight stack and drives the 4 motor outputs. The STM32F100C8T6B runs px4io and drives the 8 servo outputs, the safety switch and the servo failsafe.

Pixhawk 6C and 6X are functional references only; their schematics and PCBs are not copied. H743 pins mostly follow `px4/fmu-v6c`, F100 pins follow `px4/io-v2` (DEC-014).

The team website, [natchpai.github.io/AeroOptix-Horizon](https://natchpai.github.io/AeroOptix-Horizon/), shows the block diagram, the MCU pinouts and the status, built from the design records.

## Key Features

- STM32H743VIT6 flight MCU and STM32F100C8T6B px4io MCU, linked over USART at 1.5 Mb/s
- 4 motor outputs on the H743, 8 servo headers on an on-board 6 V rail, 3 spare outputs
- 2× ICM-45686 IMU on SPI; ICP-20100 and BMP581 barometers and IST8310 magnetometer on I2C
- 5 V input through a TPS2121 power mux (power module or USB), 3.3 V buck, separate LDO for the sensor VDD pins
- USB FS, microSD, debug access to both MCUs, selectable BOOT0

## Specifications

| Parameter | Specification |
|---|---|
| Main MCU | STM32H743VIT6 (DEC-001) |
| IO MCU | STM32F100C8T6B (px4io, DEC-002) |
| Clocks | H743 16 MHz, F100 24 MHz, both from CMOS oscillators (DEC-017, DEC-044) |
| Outputs | 4 motors (H743), 8 servos (F100, 50 Hz PWM), 3 spare (H743) (DEC-016, FUN-003, IF-017 to IF-019) |
| Sensors | 2× ICM-45686, ICP-20100 + BMP581 (BMP384 fallback), IST8310 (DEC-008, DEC-010, DEC-011) |
| Board input | 5 V, 4.5 to 5.5 V, 2 A source; power mux limit 1.5 A; overvoltage cut-off 5.6 to 6.3 V (PWR-010, DEC-029, DEC-030, DEC-036) |
| 3.3 V rails | `+3V3` buck, design current about 0.6 A (DEC-012, DEC-040); `+3V3A` LDO for the sensor VDD pins; sensor VDDIO on `+3V3` (DEC-043, DEC-027) |
| Servo supply | 6 V UBEC into an XT30, 10 A continuous, 15 A peak (PWR-011, DEC-019; XT30 rating `TBD`, OPEN-021) |
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

State of the saved KiCad files. The MCU, sensor and USB sheets and some power-sheet fields are not committed yet. Sheets not listed have no parts. Part lists, references and save dates are in specification 4.2 "Schematic state", 4.3 and 4.6.

| Area | State |
|---|---|
| Power sheet | Drawn; human ERC and a `sch-review` of the 2026-11-03 save are under Verification; resistor part numbers open (P2-021). |
| MCU sheets | In capture; one shared reset with one button decided, button not drawn (DEC-046, OPEN-026); oscillator parts decided, data open (DEC-048, OPEN-028); VREF+ tied to VDDA (DEC-049). |
| Sensor sheets | In capture with all five sensors; IST8310 at 0x0C as strapped (DEC-047, closes OPEN-027). |
| USB and debug sheet | In capture; parts drawn, not approved (OPEN-010); debug access has no console or NRST yet (OPEN-029). |
| PCB | No footprints, placeholder outline only (OPEN-009). |
| Library | Project parts for the parts in use; sensor footprints not checked against the drawings (OPEN-013). |

## Hardware Design

### Architecture

| Block | Role |
|---|---|
| H743 main controller | Flight stack and interface host |
| F100 IO controller | px4io: 8 servo outputs, safety switch and LED, servo rail sense, servo failsafe |
| Sensors | 2 IMU on SPI1 and SPI4; 2 barometers and the magnetometer on I2C2 |
| External I/O | ELRS, GPS and compass, air-data sensor, rangefinder, power module, motors, spare outputs, microSD, buzzer, LEDs |
| USB / debug | USB FS; H743 debug connector (target: console + SWD, IF-045; as drawn: OPEN-029); F100 SWD pads |
| Power | 5 V input, 3.3 V buck, sensor LDO, 6 V servo rail |

### External interfaces

Interface allocations agreed with the software team (DEC-014, DEC-018) are in specification sections 3.4 and 3.5 ([spec](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md)) and the [pin allocation record](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md); connector pinouts are not checked yet (OPEN-023).

### Design Considerations

- IO MCU and clocks: STM32F100C8T6B for px4io at 24 MHz; CMOS oscillators with HSE bypass set in firmware (DEC-002, DEC-017, DEC-044, DEC-045).
- USB power: bench supply only, needs a USB-C port above 1 A; the power module has priority (DEC-031 to DEC-034, DEC-038).
- Motor stop: the ESCs look PWM-only, so motor stop on an H743 hang is open (OPEN-017).
- Sensor sourcing: ICP-20100 is EOL, BMP581 stock is short (OPEN-004).
- Firmware: owned by the software team, PX4 v1.16.2 based on `px4/fmu-v6c` (DEC-014).

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | Power sheet, 2026-11-03 save only | Run by the human owner; only sheet pins to other sheets left. Later saves and other sheets not checked |
| Schematic review | Power sheet, 2026-11-03 save only | `sch-review`, spec 4.3 |
| PCB DRC | `NOT_VERIFIED` | PCB is empty |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | Bench tasks P4-012 to P4-015 open |

## Open Items

The specification tracks every open item in section 8.2 of the [specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md). Top items now:

- Motor stop with PWM-only ESCs (OPEN-017)
- Reset: the button is not drawn, and an H743 internal reset may also reset the F100 (OPEN-026)
- Debug access: no console or NRST on the drawn connector and pads (OPEN-029)

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
