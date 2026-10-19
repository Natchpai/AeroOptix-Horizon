# AO-Horizon KiCad Project

KiCad 10 project for the AeroOptix-Horizon flight controller. Project status, decisions and open items are in the [repository README](../../README.md) and the [specification](documents/design/AO-HORIZON_SPEC_EN.md).

The saved native KiCad files in this folder are the design authority.

## Layout

- `AO-Horizon.kicad_pro`, `AO-Horizon.kicad_sch`, `AO-Horizon.kicad_pcb`: project, root schematic and PCB.
- `top_hierarchical.kicad_sch`, `block_diagram.kicad_sch`, `power_supplies.kicad_sch`, `revision_history.kicad_sch`: schematic sheets.
- `sym-lib-table`, `fp-lib-table`: project library tables. Every entry points into `library/` through `${KIPRJMOD}`.
- `library/`: project symbols (`symbols/0_<Family>.kicad_symdir`), footprints (`footprints/0_<Family>.pretty`) and 3D models (`3D/<Family>/`).
- `documents/`: design records (`design/`), images, manufacturing, schematic and verification outputs.
- `templates/`: title-block worksheets, board theme, and fabrication, assembly and impedance notes.

KiCad backups (`AO-Horizon-backups/`, `*.bak`) are git-ignored and are not design sources.

## Directory tree

```text
AO-Horizon/
├── AO-Horizon.kicad_pro
├── AO-Horizon.kicad_sch
├── AO-Horizon.kicad_pcb
├── top_hierarchical.kicad_sch
├── block_diagram.kicad_sch
├── power_supplies.kicad_sch
├── revision_history.kicad_sch
├── sym-lib-table
├── fp-lib-table
├── documents/
│   ├── design/            # Specification, checklist and design records
│   ├── images/            # Documentation images and logos
│   ├── manufacturing/     # Assembly (BOM) and fabrication (Gerbers) outputs
│   ├── schematic/         # Schematic outputs
│   └── verification/      # Review reports and test evidence
├── library/
│   ├── symbols/           # 0_<Family>.kicad_symdir
│   ├── footprints/        # 0_<Family>.pretty
│   └── 3D/                # <Family>/*.step
├── templates/             # Worksheets, theme, notes
└── README.md
```
