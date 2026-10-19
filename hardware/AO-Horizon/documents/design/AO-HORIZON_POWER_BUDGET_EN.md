# AeroOptix-Horizon: Power Budget

**Revision:** 0.2
**Updated:** 2026-10-19
**Status:** Draft record with open `TBD` rows. The main 3.3 V buck is TPS62142RGTR (DEC-012). No other rail, regulator or protection part is approved. Not a verification record.
**Requirement refs:** PWR-010 to PWR-014, SAF-012 to SAF-014, OPEN-006, OPEN-007, OPEN-011, OPEN-012 (spec). Decision: DEC-012. Checklist task: P0-017.
**Decision owner:** Hardware

Single record for rail loads, rail tolerances, brownout thresholds and power protection requirements.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet was read by Claude.

Source keys used below:
- **Spec**: `AO-HORIZON_SPEC_EN.md`.
- **Bosch**: Bosch Sensortec product page, fetched 2026-10-18.
- **IMU rec**: `AO-HORIZON_IMU_SELECTION_EN.md` (datasheet values extracted by agy, `NOT_VERIFIED`).
- **Snippet**: search-result text of a PDF datasheet. Not opened, always `NOT_VERIFIED`.
- **TI**: ti.com product pages and HTML datasheets (TPS62142: SLVSAJ0F Rev. F; TPS735: SBVS087M), fetched 2026-10-18 and 2026-10-19.

Fetches to st.com, invensense.tdk.com, te.com and en.benewake.com failed on 2026-10-18 (`getaddrinfo EAI_AGAIN`). The rows that depend on them are `TBD`.

## 1. Fixed limits

| Item | Value | Source | Label |
| ---- | ----- | ------ | ----- |
| Board input (PWR-010) | 4.5 / 5 / 5.5 V min/nom/max, ±10 %, source capacity 2 A | Spec, DEC-007 | `VERIFIED` (requirement) |
| Servo supply (PWR-011) | 6 V nominal, min/max TBD; 10 A continuous, 15 A instantaneous (UBEC-10A reference, not an approved part) | Spec, DEC-007 | `VERIFIED` (requirement) |

## 2. Candidate power tree

From the spec diagram. Candidate only, not approved (spec PWR-013).

```text
6S battery -> XT90-S -> PM02D -> CRIUS PDB v1.0
                           |            |
                           |            +-> 6 V UBEC -> servo rail
                           +-> 5 V board input -> 3.3 V (MCUs, baro, mag)
                                              +-> 3.3 V_IMU (2 × IMU)
                                              +-> 5 V external connectors
```

- `ASSUMED`: the 5 V input feeds the external connectors directly, and both 3.3 V rails come from the 5 V input.
- `TBD`: whether 3.3 V_IMU is a separate LDO or a filtered branch of 3.3 V. The schematic draws a separate `+3V3A` LDO, but its purpose is not decided (OPEN-011).
- `TBD`: whether USB VBUS can power the board, and how it is isolated from the PM02D 5 V.
- The saved `power_supplies.kicad_sch` (re-checked 2026-10-19) draws `+3V3` from the TPS62142RGTR buck (DEC-012) and `+3V3A` from a TPS73533DRBR LDO (drawn, not decided), both fed from `+5V`. Nothing drives `+5V` yet (OPEN-012). Details: spec 4.3 "Schematic state".

## 3. Load table

Typical or average current per load. Peak current listed where known. "TBD" means no source yet.

### 3.3 V_IMU

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| ICM-45686, 6-axis low-noise, 6400 Hz | 2 | 0.44 mA | TBD | IMU rec (DS Table 3) | `NOT_VERIFIED` |

### 3.3 V

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| STM32H743VIT6 | 1 | TBD | TBD | st.com unreachable | `NOT_VERIFIED` |
| STM32F103C8T6 | 1 | TBD | TBD | st.com unreachable | `NOT_VERIFIED` |
| ICP-20100 | 1 | TBD | TBD | invensense.tdk.com unreachable | `NOT_VERIFIED` |
| BMP390 | 1 | 3.2 µA average at 1 Hz | TBD | Bosch | `VERIFIED` |
| BMM150, regular preset | 1 | 0.5 mA average (4.9 mA in high-accuracy preset) | 18 to 20 mA during measurement | Snippet (Bosch DS PDF) | `NOT_VERIFIED` |
| I2C pull-ups | TBD | TBD | - | Depends on P1-004, P1-005 | `TBD` |
| Status LEDs | TBD | TBD | - | Not defined | `TBD` |
| External 3.3 V devices | TBD | TBD | TBD | Not defined | `TBD` |

### 5 V (external connectors and regulator input)

| Load | Ref | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| Telemetry 1 | IF-010 | TBD (model TBD) | TBD | - | `TBD` |
| Telemetry 2 | IF-011 | TBD (model TBD) | TBD | - | `TBD` |
| GPS1 + compass | IF-012 | TBD (model TBD) | TBD | - | `TBD` |
| GPS2 (reserved) | IF-013 | TBD | TBD | - | `TBD` |
| MS4525DO | IF-014 | TBD (3.3 V and 5 V versions exist) | TBD | Snippet | `NOT_VERIFIED` |
| TF-Luna | IF-015 | 70 mA or less average (3.7 to 5.2 V supply) | 150 mA | Snippet (third-party PDF) | `NOT_VERIFIED` |
| FlySky receiver | IF-038 | TBD (model TBD) | TBD | - | `TBD` |
| 3.3 V regulator input | - | Sum of section 3.3 V loads | TBD | - | `TBD` |

### 6 V servo rail

| Load | Ref | Qty | Current each | Stall / peak | Label |
| ---- | --- | --- | ------------ | ------------ | ----- |
| Servos on F103 outputs | IF-030 to IF-037 | TBD | TBD | TBD | `TBD` |
| Servos or devices on H743 outputs | IF-017 to IF-021 | TBD | TBD | TBD | `TBD` |

Which outputs drive servos (6 V) and which drive ESC signal inputs only is not recorded. `TBD`.

## 4. Totals

| Rail | Known subtotal | Missing | Budget | Margin | Label |
| ---- | -------------- | ------- | ------ | ------ | ----- |
| 3.3 V_IMU | 0.88 mA (2 × 0.44 mA) | IMU peak | TBD. The drawn `+3V3A` LDO TPS73533DRBR is rated 500 mA (TI SBVS087M 5.3) but is not decided (OPEN-011). | TBD | `ESTIMATED` from `NOT_VERIFIED` inputs |
| 3.3 V | about 0.5 mA (BMP390 + BMM150 regular) | Both MCUs, ICP-20100, pull-ups, LEDs | 2 A, TPS62142RGTR (DEC-012, TI SLVSAJ0F) | TBD | `ESTIMATED` from partial inputs |
| 5 V | 70 mA average, 150 mA peak (TF-Luna only) | All other external loads, 3.3 V regulator input | 2 A source (PWR-010) | TBD | `ESTIMATED` from partial inputs |
| 6 V | none | All servo loads | 10 A cont., 15 A inst. (PWR-011) | TBD | `TBD` |

The subtotals are far from complete. Do not use them to size a regulator. The MCUs and the external 5 V devices are likely the largest loads (`ASSUMED`).

## 5. Rail tolerances (PWR-013)

| Rail | Nominal | Min | Max | Load step | Ripple / noise | Label |
| ---- | ------- | --- | --- | --------- | -------------- | ----- |
| 5 V input | 5 V | 4.5 V | 5.5 V | TBD | TBD | `VERIFIED` (PWR-010) for min/max |
| 3.3 V | 3.3 V | TBD | TBD, at most 3.6 V | TBD | TBD | `TBD` |
| 3.3 V_IMU | 3.3 V | TBD | TBD, at most 3.6 V | TBD | TBD | `TBD` |
| 6 V servo | 6 V | TBD | TBD | TBD | TBD | `TBD` |

Known upper bounds for the 3.3 V rails:
- BMP390 VDD and VDDIO max 3.6 V (Bosch, `VERIFIED`).
- ICM-45686 VDD and VDDIO max 3.6 V recommended, 4 V absolute maximum (IMU rec, `NOT_VERIFIED`).
- BMM150 VDD max 3.6 V (snippet, `NOT_VERIFIED`).
- `ESTIMATED`: 3.3 V nominal leaves 0.3 V (9 %) to the 3.6 V limit for regulator tolerance, load transients and overshoot.
- MCU VDD ranges `TBD` (st.com unreachable).

## 6. Brownout and reset thresholds (PWR-014)

| Item | Threshold | Source | Label |
| ---- | --------- | ------ | ----- |
| H743 BOR level (option bytes) | TBD | ST datasheet / RM | `NOT_VERIFIED` |
| H743 PVD level | TBD | ST datasheet / RM | `NOT_VERIFIED` |
| F103 POR/PDR | TBD | ST datasheet | `NOT_VERIFIED` |
| F103 PVD level | TBD | ST datasheet | `NOT_VERIFIED` |
| 5 V input undervoltage detect | TBD (does the board monitor 5 V?) | Not defined | `TBD` |
| 6 V servo rail monitor | TBD | Not defined | `TBD` |

## 7. Protection requirements (OPEN-006, OPEN-007, SAF-012 to SAF-014)

All `TBD`. Items to decide:

- [ ] 5 V input: reverse polarity, overvoltage clamp, transient (TVS) rating, inrush.
- [ ] USB VBUS and PM02D 5 V: OR-ing or isolation, so neither back-feeds the other.
- [ ] 6 V servo rail: separation from the 5 V logic input, so servo current does not flow through board logic copper. Back-feed from servo connectors into the board.
- [ ] 6 V servo rail: overcurrent behavior, pulse duration of the 15 A rating, bulk capacitance.
- [ ] External 5 V connectors: short-circuit protection per connector or per group.
- [ ] ESD on external connectors and USB (SAF-014).
- [ ] Safe output state on 5 V loss or 6 V fault (SAF-012, SAF-013).

## 8. Findings

| Severity | Ref | Label | Finding | Source |
| -------- | --- | ----- | ------- | ------ |
| MAJOR | PWR-012 | `NOT_VERIFIED` | Board current budget cannot be closed: MCU currents and all external 5 V device models are missing. | Section 4 |
| MINOR | BMM150 / 3.3 V | `NOT_VERIFIED` | BMM150 peak current of 18 to 20 mA during measurement is about 40 × its regular average. Local decoupling must cover it. | Snippet |
| INFO | IF-022 / 5 V | `ASSUMED` | If USB VBUS can power the board, it needs OR-ing or isolation from the PM02D 5 V. | Section 2 |
| INFO | IF-030 to IF-037 | `TBD` | Servo count and stall current are needed before the 10 A / 15 A rating can be checked. | Section 3 |

## 9. Open inputs

- [ ] Telemetry 1 and 2, GPS, FlySky receiver: model and supply current (human).
- [ ] Servo count, servo model and stall current; which outputs carry servo power (human).
- [ ] 3.3 V_IMU rail structure: separate LDO or filtered branch (human).
- [ ] USB VBUS as a board power source: yes or no (human).
- [ ] STM32H743 and STM32F103 VDD range, run current at the planned clock, BOR/POR/PVD levels (user-supplied values or approved datasheet route).
- [ ] ICP-20100 supply range and current.
- [ ] MS4525DO version (3.3 V or 5 V) and supply current.
- [ ] Retry the official pages for TF-Luna, MS4525DO and BMM150.

## 10. Sources

- Bosch BMP390: https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp390/
- BMM150 snippet source (PDF, not opened): https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmm150-ds001.pdf
- TF-Luna snippet source (third-party PDF, not opened): https://files.waveshare.com/upload/c/c3/SJ-GU-TF-Luna_A05_Datasheet.pdf
- TI TPS62142: https://www.ti.com/product/TPS62142
- TI TPS735 (TPS73533DRBR): https://www.ti.com/product/TPS735 and https://www.ti.com/document-viewer/TPS735/datasheet/electrical-characteristics-slvscd4719
- ICM-45686: see `AO-HORIZON_IMU_SELECTION_EN.md`
- Requirements: `AO-HORIZON_SPEC_EN.md` sections on power, safety and interfaces
