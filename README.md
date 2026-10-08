# AeroOptix-Horizon

High-performance dual-MCU flight controller powered by STM32H7 & STM32F1 by AeroOptix Club.

> **Status:** `CONCEPT`  
> **Revision:** `v1.0`  
> **Baseline:** `NOT_ESTABLISHED`  
> **KiCad:** `10.0.6`

## Overview

AeroOptix-Horizon is a flight controller something like this.
<!--

| Item | Value |
|---|---|
| Board size | `??` |
| Layers | `??` |
-->

## Repository files

```text
│
├── hardware/
│   ├── AO-Horizon.kicad_pro           # KiCad project settings
│   ├── AO-Horizon.kicad_sch           # Authoritative schematic source
│   ├── AO-Horizon.kicad_pcb           # Authoritative PCB source
│   ├── Library/
│   │   ├── symbols/                   # Project-specific symbols
│   │   ├── footprints/                # Project-specific footprints
│   │   └── 3D/                        # Project-specific 3Ds
│   ├── Documents/
│   │   ├── Design/                    # Design intent and architecture
│   │   ├── Manufacturing/             # Fab/assembly notes and outputs
│   │   ├── Schematics                 # Schematics diagram outputs
│   │   ├── Verification/              # Review reports and test evidence
│   │   └── Images/                    # documentation images and other
│   ...
│  
├── LICENSE
├── CHANGELOG.md
└── README.md
```

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
