# AeroOptix-Horizon

Dual-MCU flight controller based on an STM32H7 and an STM32F1, by AeroOptix Club.

> **Status:** `CONCEPT`
> **Revision:** `v1.0`
> **Baseline:** `NOT_ESTABLISHED`
> **KiCad:** `10.0.7`

## Overview

AeroOptix-Horizon is a custom PX4 flight controller hardware platform with a dual-MCU architecture. The STM32H743VIT6 is the main flight-controller MCU. The STM32F103C8T6 is an auxiliary MCU for expanded I/O, PWM/ESC control and safety behavior. A USART link connects the two MCUs.

Pixhawk 6C is only a conceptual and functional reference. Its schematic, PCB and pinout are not copied.

> **Draft specification (rev 0.6, 2026-10-19): NOT FOR FABRICATION.** Everything below is a design target taken from the specification, not a verified result. Values not yet decided are shown as `TBD`.

## Key Features

- Main MCU: STM32H743VIT6
- Auxiliary MCU: STM32F103C8T6 (PWM/ESC, expanded I/O, safety)
- H743 to F103 link over USART
- 2× SPI IMU (ICM-45686), 2× I2C barometer (ICP-20100, BMP390), 1× I2C magnetometer (BMM150)
- 3.3 V rail from a TPS62142 buck on the 5 V board input
- USB FS, SWD on both MCUs, selectable BOOT0 on the H743
- F103 commands immediate landing if the H743 is not operating (detection and timing `TBD`)

## Specifications

| Parameter | Specification |
|---|---|
| Main MCU | STM32H743VIT6 |
| Auxiliary MCU | STM32F103C8T6 |
| Inter-MCU link | USART (instance, pins, levels, rate `TBD`) |
| IMU | 2× SPI, ICM-45686 |
| Barometer | 2× I2C, ICP-20100 + BMP390 |
| Magnetometer | 1× I2C, BMM150 |
| Board input | 5 V from power module, 4.5 to 5.5 V, 2 A source |
| 3.3 V rail | TPS62142RGTR buck from 5 V (load current `TBD`) |
| 3.3 V analog rail (`+3V3A`) | Purpose and part `TBD` (TPS73533DRBR drawn, not decided) |
| Servo supply | 6 V (current and protection `TBD`) |
| Board outline | Approx. 90 mm × 95 mm from diagram; exact outline `TBD` |
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

A human engineer declares phase changes.

- Slate: not started
- Amber: current phase, under review
- Green: completed

The diagram is for reference only. It does not enforce gates or approve releases.

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

The specification's candidate power arrangement (6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 6 V UBEC) comes from user diagrams and is not an approved design.

### External interfaces (logical level)

Allocations below are user-confirmed at the logical level only. Exact pins, alternate functions, electrical levels and protection are `TBD` and not verified.

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

- Timer/channel validity of the H743 and F103 labels is unconfirmed (OPEN-003). The same timer channels appear on both MCUs, and TIM3 labels CH5..CH8 need checking against the STM32F103 datasheet.
- Power budgets, rail tolerances, sequencing, brownout/reset thresholds and protection (reverse polarity, overvoltage, ESD, short circuit) are `TBD`.
- Clock sources, reset topology and F103 boot behavior are `TBD`.
- Safety detection method, timing and output ownership for the H743-failure case are `TBD`.
- Firmware (PX4 version and target, bootloader, USART message protocol) is deferred.
- Confirmed part numbers: STM32H743VIT6, STM32F103C8T6, ICM-45686, ICP-20100, BMP390, BMM150 and TPS62142RGTR. All other parts are `TBD`.
- Sensor sourcing risks are open: ICP-20100 is EOL and BMP390 is not available at LCSC.
- Power sheet in progress: the path from the power module input (`+VIN`) to `+5V` is not drawn yet.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | `NOT_VERIFIED` | `TBD` |
| PCB DRC | `NOT_VERIFIED` | `TBD` |
| Connectivity / pin review | `NOT_VERIFIED` | `TBD` |
| BOM / footprint review | `NOT_VERIFIED` | `TBD` |
| Prototype functional test | `NOT_VERIFIED` | `TBD` |

## Open Items

The specification tracks open items OPEN-001 to OPEN-012 (OPEN-005 is closed): pin and alternate-function validity, USART details, timer validity, sensor electrical properties and sourcing, 5 V and 6 V budgets, safety timing, board outline and mounting, remaining non-MCU part numbers, the `+3V3A` rail, and the `+VIN` to `+5V` path.

## Repository Structure

```text
AeroOptix-Horizon/
├── hardware/AO-Horizon/
│   ├── AO-Horizon.kicad_pro           # KiCad project settings
│   ├── AO-Horizon.kicad_sch           # Root schematic
│   ├── *.kicad_sch                    # Sheets: top_hierarchical, block_diagram,
│   │                                  #   power_supplies, revision_history
│   ├── AO-Horizon.kicad_pcb           # PCB source
│   ├── library/
│   │   ├── symbols/                   # Project-specific symbols
│   │   ├── footprints/                # Project-specific footprints
│   │   └── 3D/                        # Project-specific 3D models
│   ├── documents/
│   │   ├── design/                    # Specification and execution checklist
│   │   ├── manufacturing/             # Fab/assembly notes and outputs
│   │   ├── schematic/                 # Schematic diagram outputs
│   │   ├── verification/              # Review reports and test evidence
│   │   └── images/                    # Documentation images
│   └── templates/                     # Worksheets, theme, fab/assembly notes
├── .github/                           # Pull request template
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## Documentation

| Resource | Description |
|---|---|
| [Specification](hardware/AO-Horizon/documents/design/AO-HORIZON_SPEC_EN.md) | Draft requirements, interfaces and open items |
| [Execution checklist](hardware/AO-Horizon/documents/design/AO-HORIZON_EXECUTION_CHECKLIST_EN.md) | Work plan and evidence tracker |
| [IMU selection](hardware/AO-Horizon/documents/design/AO-HORIZON_IMU_SELECTION_EN.md) | ICM-45686 selection record |
| [Barometer and magnetometer selection](hardware/AO-Horizon/documents/design/AO-HORIZON_BARO_MAG_SELECTION_EN.md) | ICP-20100, BMP390 and BMM150 selection record |
| [Power budget](hardware/AO-Horizon/documents/design/AO-HORIZON_POWER_BUDGET_EN.md) | Draft rail and load budget (P0-017) |
| [Pin allocation](hardware/AO-Horizon/documents/design/AO-HORIZON_PIN_ALLOCATION_EN.md) | Draft H743 and F103 pin allocation |
| [H7 MCU sourcing](hardware/AO-Horizon/documents/design/AO-HORIZON_H7_MCU_SOURCING_EN.md) | STM32H743VI price and stock |

## License

Copyright (c) 2026 AeroOptix Club.

The hardware design files are licensed under CERN-OHL-S-2.0.

The complete license text is available in:

[CERN Open Hardware Licence Version 2 - Strongly Reciprocal](LICENSE)

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
