# AeroOptix-Horizon

High-performance dual-MCU flight controller powered by STM32H7 & STM32F1 by AeroOptix Club.

> **Status:** `CONCEPT`  
> **Revision:** `v1.0`  
> **Baseline:** `NOT_ESTABLISHED`  
> **KiCad:** `10.0.6`

## Overview

AeroOptix-Horizon is a custom PX4 flight controller with two MCUs. The Pixhawk 6C is a conceptual reference only; its schematic, PCB and pinout are not copied.

## Key Features

- Main MCU: STM32H743VIT6
- Auxiliary MCU: STM32F103C8T6 (PWM/ESC outputs, expanded I/O, safety), linked to the main MCU over USART
- Planned sensors: 2× SPI IMU, 2× I2C barometer, 2× I2C magnetometer (parts not yet selected)

*These are design targets from the draft specification (rev 0.1, "NOT FOR FABRICATION"), not verified results. Pin assignments, power budgets, board outline and most part numbers are still open (OPEN-001 to OPEN-010 in the specification).*
<!--

| Item | Value |
|---|---|
| Board size | `??` |
| Layers | `??` |
-->

## Repository files

```text
│
├── hardware/AO-Horizon/
│   ├── AO-Horizon.kicad_pro           # KiCad project settings
│   ├── AO-Horizon.kicad_sch           # Root schematic
│   ├── *.kicad_sch                    # Sheets: top_hierarchical, block_diagram,
│   │                                  #   power_supplies, revision_history
│   ├── AO-Horizon.kicad_pcb           # PCB source
│   ├── library/
│   │   ├── symbols/                   # Project-specific symbols
│   │   ├── footprints/                # Project-specific footprints
│   │   └── 3D/                        # Project-specific 3Ds
│   ├── documents/
│   │   ├── design/                    # Specification, handoff, execution checklist
│   │   ├── manufacturing/             # Fab/assembly notes and outputs
│   │   ├── schematic/                 # Schematic diagram outputs
│   │   ├── verification/              # Review reports and test evidence
│   │   └── images/                    # Documentation images
│   └── templates/                     # Worksheets, theme, fab/assembly notes
│
├── .github/                           # Pull request template
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## Documentation

| Resource | Description |
|---|---|
| [Advanced specification](hardware/AO-Horizon/documents/design/AO-HORIZON_ADVANCED_SPEC_EN.md) | Draft requirements, interfaces and open items |
| [Handoff](hardware/AO-Horizon/documents/design/AO-HORIZON_HANDOFF_EN.md) | Design handoff notes |
| [Execution checklist](hardware/AO-Horizon/documents/design/AO-HORIZON_EXECUTION_CHECKLIST_EN.md) | Execution checklist |

<!--

## Design notes

- Power: `<POWER_ARCHITECTURE>`
- Critical interfaces: `<INTERFACE_OR_PIN_NOTES>`
- Stackup / impedance: `<STACKUP_AND_IMPEDANCE_NOTES>`
- Mechanical constraints: `<MECHANICAL_NOTES>`
  

## Verification

| Check | Result | Evidence |
|---|---|---|
| Schematic ERC | `<PASS / FAIL / NOT VERIFIED>` | `<PATH_OR_LINK>` |
| PCB DRC | `<PASS / FAIL / NOT VERIFIED>` | `<PATH_OR_LINK>` |
| Connectivity / pin review | `<RESULT>` | `<PATH_OR_LINK>` |
| BOM / footprint review | `<RESULT>` | `<PATH_OR_LINK>` |
| Prototype functional test | `<RESULT>` | `<PATH_OR_LINK>` |

## Release

| Release | Tag | Baseline | Date |
|---|---|---|---|
| `<VERSION>` | `<GIT_TAG>` | `<BASELINE_ID>` | `<YYYY-MM-DD>` |

Release outputs must be generated from the stated baseline and include a hash or release manifest when applicable.
-->

<!-- Suggested STATUS_TOKEN values: CONCEPT, SCHEMATIC_IN_PROGRESS,
SCHEMATIC_REVIEW_REQUIRED, READY_FOR_PCB_DESIGN, PCB_LAYOUT_IN_PROGRESS,
PCB_REVIEW_REQUIRED, READY_FOR_FABRICATION, PROTOTYPE_BUILT, VALIDATED,
RELEASED, NOT_READY, NOT_VERIFIED -->


## License
Copyright (c) 2026 AeroOptix Club.

The hardware design files are licensed under CERN-OHL-W-2.0.

The complete licence text is available in: </br>
[CERN Open Hardware Licence Version 2 - Weakly Reciprocal](LICENSE)  

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
