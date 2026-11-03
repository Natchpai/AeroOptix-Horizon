<p align="center">
  <img src="assets\AO-Horizon-v2.png" alt="AO-Horizon title" width="100%" >
</p>

> **Status:** `DRAFT`
> **Board revision:** `A`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.8`

> **Draft specification (rev 0.32, 2026-11-03): NOT FOR FABRICATION.** Everything below is a design target from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The STM32H743VIT6 runs the flight stack and drives the 4 motor outputs. The STM32F100C8T6B runs px4io and drives the 8 servo outputs, the safety switch and the servo failsafe.

Pixhawk 6C and 6X are functional references only; their schematics and PCBs are not copied. H743 pins mostly follow `px4/fmu-v6c`, F100 pins follow `px4/io-v2` (DEC-014).

The team website, [natchpai.github.io/AeroOptix-Horizon](https://natchpai.github.io/AeroOptix-Horizon/), shows the block diagram, the MCU pinouts and the status, built from the design records.

## Key Features

- STM32H743VIT6 main MCU; STM32F100C8T6B IO MCU (px4io) over USART at 1.5 Mb/s
- 4 motor outputs (H743 TIM5), 8 servo headers on an on-board 6 V rail (UBEC through an XT30), 3 spare outputs
- 2× ICM-45686 IMU (SPI), ICP-20100 + BMP581 barometers and IST8310 magnetometer (I2C)
- 5 V input through a TPS2121 power mux (power module and USB), 3.3 V from a TPS62142RGTR buck, IMU rail from a TPS73533DRBR LDO
- USB FS, microSD, Pixhawk Debug Mini, F100 SWD pads, selectable BOOT0

## Specifications

| Parameter | Specification |
|---|---|
| Main / IO MCU | STM32H743VIT6 / STM32F100C8T6B (px4io) |
| Clocks | H743 16 MHz, F100 24 MHz crystal |
| Outputs | 4 motors (H743), 8 servos (F100, 50 Hz PWM), 3 spare (H743) |
| Sensors | 2× ICM-45686, ICP-20100 + BMP581 (BMP384 fallback), IST8310 |
| Board input | 5 V, 4.5 to 5.5 V, 2 A source; power mux limit 1.5 A; overvoltage cut-off 5.6 to 6.3 V (DEC-029, DEC-030, DEC-036) |
| 3.3 V rails | `+3V3` buck, design current about 0.6 A (DEC-040); `+3V3A` LDO for the 2 IMUs only (DEC-025, DEC-027) |
| Servo supply | 6 V UBEC into an XT30, 10 A continuous, 15 A peak (XT30 rating `TBD`, OPEN-021) |
| Board outline | Under 80 mm each side; exact outline `TBD` (OPEN-009) |
| Mounting | M3, 3.2 mm holes, soft mount; pattern `TBD` |
| Layers / stackup | `TBD` |
| Temperature | Parts rated −40 to +85 °C (DEC-020) |

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

State of the saved KiCad files on 2026-11-03. Details: specification 4.3 and 4.6.

| Area | State |
|---|---|
| Power sheet | Drawn, 53 parts. ERC run by the human owner (only sheet pins to other sheets left) and a `sch-review` found no defect (2026-11-03; not an approval). Open: CN101 to CLIK-Mate (DEC-042), resistor part numbers (P2-021). |
| Other sheets | No parts yet. |
| PCB | No footprints; 27 × 29 mm placeholder outline (OPEN-009). |
| Library | Project symbols, footprints and 3D models for the parts in use. Sensor footprints are starting points, not checked against the drawings (OPEN-013). |

## Hardware Design

### Architecture

| Block | Role |
|---|---|
| H743 main controller | Flight stack and interface host |
| F100 IO controller | px4io: 8 servo outputs, safety switch and LED, servo rail sense, servo failsafe |
| Sensors | 2 IMU on SPI1 and SPI4; 2 barometers and the magnetometer on I2C2 |
| External I/O | ELRS, GPS and compass, air-data sensor, rangefinder, power module, motors, spare outputs, microSD, buzzer, LEDs |
| USB / debug | USB FS, H743 debug connector (console + SWD), F100 SWD pads |
| Power | 5 V input, 3.3 V buck, IMU LDO, 6 V servo rail |

### External interfaces

Allocations agreed with the software team (DEC-014, DEC-018). Connector pinouts are not checked yet (OPEN-023).

| Interface | Function | Allocation |
|---|---|---|
| Tel1 | ELRS receiver (RC and MAVLink), JST-GH 6-pin | UART7 |
| Tel2 | Telemetry 2 (free) | USART1 |
| GPS1 + compass | 10-pin full GPS port | USART2 + I2C1 |
| Debug | Pixhawk Debug Mini | USART3 + SWD |
| MS4525DO + PM02D | Air-data sensor and power module | I2C4 |
| TF-Luna | Rangefinder | UART8 |
| Motors 1 to 4 | Skywalker 80A V2 ESCs, 3-pin headers, + pin removed (OPEN-017) | TIM5_CH1 to CH4 |
| Spare 1 to 3 | Spare outputs | TIM4_CH3, TIM4_CH4, TIM1_CH1 |
| microSD | Flight logs | SDMMC1, 4-bit |
| Buzzer | PX4 tone alarm | TIM3_CH3 |
| F100 servos 1 to 8 | Flaperons, ruddervators, 4 tilt servos | TIM2, TIM3, TIM4 channels |
| F100 safety | Safety button and LED, through GPS1 | GPIO |

### Design Considerations

- The IO MCU is an STM32F100C8T6B so stock px4io runs with its 24 MHz crystal (DEC-002, DEC-017).
- USB is a bench supply and needs a USB-C port above 1 A; the power module has priority (DEC-031 to DEC-034, DEC-038).
- The ESCs look PWM-only, so motor stop on an H743 hang is open (OPEN-017).
- Sensor sourcing risk: ICP-20100 is EOL, BMP581 stock is short (OPEN-004).
- Firmware is owned by the software team: PX4 v1.16.2, based on `px4/fmu-v6c`.
- Decisions, values and evidence are in the specification; this README only summarizes them.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | Power sheet only | Run by the human owner, 2026-11-03; sheet pins to other sheets left |
| Schematic review | Power sheet only | `sch-review`, spec 4.3, 2026-11-03 |
| PCB DRC | `NOT_VERIFIED` | PCB is empty |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | Bench tasks P4-012 to P4-015 open |

## Open Items

The specification tracks OPEN-001 to OPEN-025. Still open:

- MCU pins not in the schematic yet (OPEN-001)
- Sensor data, sourcing and footprints (OPEN-004, OPEN-013, OPEN-019)
- 6 V servo rail budget and XT30 (OPEN-007, OPEN-021)
- Board outline (OPEN-009) and remaining part numbers (OPEN-010)
- `+3V3A` start-up on the bench (OPEN-011)
- Motor stop with PWM-only ESCs (OPEN-017) and PWM pull-downs (OPEN-018)
- Connector pinouts; PM02D CLIK-Mate not drawn yet (OPEN-023, DEC-042)
- Status LED ST level on the bench (OPEN-025)

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
| [Pin allocation](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md) | H743 and F100 pin allocation (rev 0.6) |
| [Design records index](hardware/AO-Horizon/documents/design/README.md) | All other records: sensor selection, pinmap review and decisions, integration questions, sourcing |
| [Team website](https://natchpai.github.io/AeroOptix-Horizon/) | Block diagram, MCU pinouts and status ([source](web/README.md)) |

## License

Copyright (c) 2026 AeroOptix Club.

The hardware design files are licensed under CERN-OHL-S-2.0.

The complete license text is available in:

[CERN Open Hardware Licence Version 2 - Strongly Reciprocal](LICENSE)

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
