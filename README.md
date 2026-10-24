# AeroOptix-Horizon

**Dual-MCU PX4 flight controller hardware (STM32H743 + STM32F103) by AeroOptix Club.**

> **Status:** `DRAFT`
> **Board revision:** `v1.0`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.7`

> **Draft specification (rev 0.10, 2026-10-24): NOT FOR FABRICATION.** Everything below is a design target from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The STM32H743VIT6 is the main flight-controller MCU. The STM32F103C8T6 is an auxiliary MCU for PWM/ESC outputs, expanded I/O and a safety function. A USART link connects the two MCUs, and the F103 uses it to watch the H743.

Pixhawk 6C and Pixhawk 6X are only conceptual and functional references. Their schematics, PCBs and pinouts are not copied.

## Key Features

- Main MCU: STM32H743VIT6
- Auxiliary MCU: STM32F103C8T6 (PWM/ESC, expanded I/O, safety)
- H743 to F103 link over USART
- 2× SPI IMU (ICM-45686), 2× I2C barometer (ICP-20100 + second part `TBD`), 1× I2C magnetometer (IST8310)
- 3.3 V rail from a TPS62142RGTR buck on the 5 V board input
- USB FS, SWD on both MCUs, selectable BOOT0 on the H743
- F103 commands immediate landing if the H743 stops operating (detection and timing `TBD`)

## Specifications

| Parameter | Specification |
|---|---|
| Main MCU | STM32H743VIT6 |
| Auxiliary MCU | STM32F103C8T6 |
| Inter-MCU link | USART (instance, pins, levels, rate `TBD`) |
| IMU | 2× SPI, ICM-45686 |
| Barometer | 2× I2C, ICP-20100 + second part `TBD` (BMP581 proposed, OPEN-014) |
| Magnetometer | 1× I2C, iSentek IST8310 (DEC-011, replaced BMM150) |
| Board input | 5 V from power module, 4.5 to 5.5 V, 2 A source |
| 3.3 V rail | TPS62142RGTR buck from 5 V, 2 A part (load current `TBD`) |
| 3.3 V analog rail (`+3V3A`) | Purpose and part `TBD` (TPS73533DRBR drawn, not decided) |
| Servo supply | 6 V, 10 A continuous, 15 A instantaneous (protection and distribution `TBD`) |
| Board outline | Each dimension under 80 mm; exact outline `TBD` |
| Mounting pattern | `TBD` |
| Copper layers / stackup | `TBD` |
| Operating / storage temperature | `TBD` |
| Vibration and shock | `TBD` |

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

State of the saved KiCad files on 2026-10-24. Details are in the specification (4.3 "Schematic state", 4.6 "Library state").

| Area | State |
|---|---|
| Schematic | Only `power_supplies.kicad_sch` has parts (19, all unannotated): power module connector, TPS16412DRC eFuse, TPS62142RGTR buck, TPS73533DRBR LDO and a 3.3 V LED. Nothing drives `+5V` yet. The other sheets hold no parts. |
| PCB | Empty: no footprints and no board outline. |
| Library | Project symbols, footprints and 3D models for the MCUs, regulators, ESD parts, connectors and passives. Sensor symbols and footprints are starting points: their pin maps match the datasheet tables, but land patterns and pin 1 orientation are not checked yet. A BMP581 symbol is a starting point for the second barometer candidate (OPEN-014), and the Bosch LGA-10 footprint pads now follow the BMP581 land pattern (not checked against the drawing). The IST8310 uses the stock KiCad symbol and `LGA-16_3x3mm_P0.5mm` footprint; its datasheet has no land pattern, so the fit is estimated. A read-only link audit found no broken links. |
| ERC / DRC | Not run. |

## Hardware Design

### Architecture

| Block | Role |
|---|---|
| H743 main controller | Primary flight-controller processing and interface host |
| F103 auxiliary controller | PWM/ESC outputs, expanded I/O, safety function |
| IMU / barometer / magnetometer | 2 IMU, 2 barometer, 1 magnetometer; bus allocation `TBD` |
| H743 external I/O | Telemetry, GPS, compass, air-data sensor, rangefinder, logical outputs |
| F103 PWM / I/O | TILT, ESC, COAX, AIL outputs and FlySky bulk header |
| USB / SWD / BOOT0 | Service, debug and recovery access |
| Power | 5 V board input, 3.3 V buck, 6 V servo supply |

The specification's candidate power chain (6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 6 V UBEC) comes from user diagrams and is not an approved design.

### External interfaces (logical level)

These allocations are user-confirmed at the logical level only. Exact pins, alternate functions, electrical levels and protection are `TBD` and not verified.

| Interface | Function | Allocation |
|---|---|---|
| Tel1 | Telemetry 1 | UART7 |
| Tel2 | Telemetry 2 | UART1 |
| GPS1 + compass | GPS and compass | UART2 + I2C1 |
| GPS2 | Reserved | UART3 |
| MS4525DO | Air-data sensor | I2C4, address `0x28` |
| TF-Luna | Rangefinder | UART8 |
| VT L / VT R | H743 outputs | TIM4_CH3 / TIM4_CH4 |
| SP2 | Reserved output | TIM1_CH1 |
| TL2 / TR2 | H743 outputs | TIM15_CH1 / TIM15_CH2 |
| F103 TILT L/R | F103 outputs | TIM2_CH1 / TIM2_CH2 |
| F103 ESC L/R | F103 outputs | TIM4_CH3 / TIM4_CH4 |
| F103 COAX T/B, AIL L/R | F103 outputs | TIM3_CH5..CH8 (labels as provided) |
| F103 FlySky | Bulk pin header | Pinout `TBD` |

### Design Considerations

- Timer labels are not confirmed (OPEN-003). The F103 TIM3 has CH1 to CH4 only; the team confirmed CH1 to CH4 on PA6, PA7, PB0, PB1.
- The software team answered the pinmap review on 2026-10-24. Their answers change several spec rows: 4 ESCs on the H743 (TIM5) and 8 servos on the F103, stock PX4 IO firmware on the F103, no FlySky, no GPS2, and the SAF-001 landing wording. These wait for team decisions (OPEN-016, `AO-HORIZON_PINMAP_DECISIONS_EN.md`).
- Stock PX4 IO firmware expects a 24 MHz F103 clock, which is outside the F103 crystal range of 4 to 16 MHz (OPEN-015).
- Sourcing risk on the sensors (OPEN-004): ICP-20100 is EOL (TDK says its pressure products are not for new designs), and the IST8310 lifecycle is not confirmed.
- The magnetometer changed from BMM150 to IST8310 (DEC-011). Its absolute maximum supply is 3.6 V, so the 3.3 V rail has only 0.3 V of margin.
- BMP390 was removed because LCSC does not sell it. BMP581 (LCSC C5362283) is proposed as the second barometer and waits for team confirmation (OPEN-014).
- The power sheet is in progress: `+VIN` to `+5V` is not drawn (OPEN-012), and the `+3V3A` LDO is not decided (OPEN-011). As drawn, the LDO's NR capacitor (100 nF) is above TI's 0.01 µF limit, and the TPS62142 lacks the 0.1 µF AVIN capacitor TI recommends.
- Power budgets, rail tolerances, sequencing, brownout/reset thresholds and protection (reverse polarity, overvoltage, ESD, short circuit) are `TBD`.
- Clock sources, reset topology and F103 boot behavior are `TBD`.
- Safety detection method, timing and output ownership for the H743-failure case are `TBD`.
- Firmware (PX4 version and target, bootloader, USART message protocol) is deferred. The PX4 Matek H743-Slim board port is kept in `documents/reference/` as a pin-map reference only.
- Confirmed part numbers: STM32H743VIT6, STM32F103C8T6, ICM-45686, ICP-20100, IST8310 and TPS62142RGTR. All other parts are `TBD`.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | `NOT_VERIFIED` | Not run |
| PCB DRC | `NOT_VERIFIED` | Not run; PCB is empty |
| Connectivity / pin review | `NOT_VERIFIED` | `TBD` |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | `TBD` |

## Open Items

The specification tracks OPEN-001 to OPEN-016 (OPEN-005 is closed):

- MCU pins, alternate functions and timer validity (OPEN-001, OPEN-003)
- USART instance, levels and timing (OPEN-002)
- Sensor electrical data and sourcing (OPEN-004)
- Second barometer part number (OPEN-014)
- 5 V and 6 V budgets and protection (OPEN-006, OPEN-007)
- Safety timing, owned by Software (OPEN-008)
- Board outline, mounting and environment (OPEN-009)
- Remaining non-MCU part numbers (OPEN-010)
- `+3V3A` rail (OPEN-011) and the `+VIN` to `+5V` path (OPEN-012)
- Sensor footprints to check against the datasheet drawings and app notes (OPEN-013)
- F103 clock for the stock PX4 IO firmware (OPEN-015)
- Spec rows changed by the team's pinmap answers, waiting for team decisions (OPEN-016)

## How we work

1. A human engineer makes every design decision and declares the phase. Decisions go into the specification first.
2. The execution checklist tracks each task and the evidence needed to close it. A task is `DONE` only with a named evidence record.
3. The saved KiCad files are the design authority. The Markdown records describe them and never replace them.
4. New library parts start from the stock KiCad library where it fits, use KLC names with a `0_` family prefix, and get a link check before use.
5. After design work, the docs are updated in this order: specification, checklist, design records, README, CHANGELOG.
6. Datasheet values come from official sources and are labeled `VERIFIED`, `ASSUMED`, `ESTIMATED` or `NOT_VERIFIED`. ERC and DRC results are evidence, not proof of a correct design.
7. Changes go through `dev` and a pull request to `main` (see `.github/pull_request_template.md`), with Conventional Commits.

Claude Code support for this workflow (rules, skills and file protection) is in `.claude/` and `CLAUDE.md`.

## Repository Structure

```text
AeroOptix-Horizon/
├── hardware/AO-Horizon/
│   ├── AO-Horizon.kicad_pro           # KiCad project settings
│   ├── AO-Horizon.kicad_sch           # Root schematic
│   ├── *.kicad_sch                    # Sheets: top_hierarchical, block_diagram,
│   │                                  #   power_supplies, revision_history
│   ├── AO-Horizon.kicad_pcb           # PCB source
│   ├── sym-lib-table, fp-lib-table    # Project library tables
│   ├── library/
│   │   ├── symbols/                   # 0_<Family>.kicad_symdir
│   │   ├── footprints/                # 0_<Family>.pretty
│   │   └── 3D/                        # 3D models by family
│   ├── documents/
│   │   ├── design/                    # Specification, checklist, design records
│   │   ├── reference/                 # Third-party reference files (PX4 board port)
│   │   ├── manufacturing/             # Fab/assembly notes and outputs
│   │   ├── schematic/                 # Schematic diagram outputs
│   │   ├── verification/              # Review reports and test evidence
│   │   └── images/                    # Documentation images
│   └── templates/                     # Worksheets, theme, fab/assembly notes
├── .claude/                           # Claude Code rules, skills and hooks
├── .github/                           # Pull request template
├── CLAUDE.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Documentation

| Resource | Description |
|---|---|
| [Specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md) | Requirements, decisions, schematic and library state, open items |
| [Execution checklist](hardware/AO-Horizon/documents/design/AO-HORIZON_EXECUTION_CHECKLIST_EN.md) | Work plan and evidence tracker |
| [IMU selection](hardware/AO-Horizon/documents/design/AO-HORIZON_IMU_SELECTION_EN.md) | ICM-45686 selection record |
| [Barometer and magnetometer selection](hardware/AO-Horizon/documents/design/AO-HORIZON_BARO_MAG_SELECTION_EN.md) | ICP-20100 and IST8310 selection and lifecycle (BMM150 replaced), BMP390 removal, BMP581 candidate |
| [Power budget](hardware/AO-Horizon/documents/design/AO-HORIZON_POWER_BUDGET_EN.md) | Draft rail and load budget (P0-017) |
| [Pin allocation](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md) | Draft H743 and F103 pin allocation |
| [Pinmap review](hardware/AO-Horizon/documents/design/AO-HORIZON_PINMAP_REVIEW_EN.md) | Pinmap review 0.2 with the software team's answers |
| [Pinmap decisions](hardware/AO-Horizon/documents/design/AO-HORIZON_PINMAP_DECISIONS_EN.md) | Spec changes, team decisions and software questions from the pinmap answers (OPEN-016) |
| [H7 MCU sourcing](hardware/AO-Horizon/documents/design/AO-HORIZON_H7_MCU_SOURCING_EN.md) | STM32H743VI price and stock |
| [KiCad project](hardware/AO-Horizon/README.md) | Project folder layout |

## License

Copyright (c) 2026 AeroOptix Club.

The hardware design files are licensed under CERN-OHL-S-2.0.

The complete license text is available in:

[CERN Open Hardware Licence Version 2 - Strongly Reciprocal](LICENSE)

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
