# AeroOptix-Horizon: Power Budget

**Revision:** 0.6
**Updated:** 2026-10-24
**Status:** Draft record with open `TBD` rows. The main 3.3 V buck is TPS62142RGTR (DEC-012). No other rail, regulator or protection part is approved. Not a verification record.
**Requirement refs:** PWR-010 to PWR-014, SAF-012 to SAF-014, OPEN-006, OPEN-007, OPEN-011, OPEN-012, OPEN-021 (spec rev 0.13). Decisions: DEC-010, DEC-012, DEC-016, DEC-018, DEC-019. Checklist task: P0-017.
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
| Servo supply (PWR-011) | 6 V nominal, min/max TBD; 10 A continuous, 15 A instantaneous (UBEC-10A reference, not an approved part). On the board: the UBEC plugs into one servo header and the 8 headers share a 6 V bus (DEC-019) | Spec, DEC-007, DEC-019 | `VERIFIED` (requirement) |

## 2. Candidate power tree

From the spec diagram. Candidate only, not approved (spec PWR-013).

```text
6S battery -> XT90-S -> PM02D -> CRIUS PDB v1.0
                           |            |
                           |            +-> 6 V UBEC -> board servo header -> on-board 6 V bus
                           |                             -> 8 servo headers (+ IF-050 sense)
                           +-> 5 V board input -> 3.3 V (MCUs, baro, mag)
                                              +-> 3.3 V_IMU (2 × IMU)
                                              +-> 5 V external connectors
USB VBUS (bench, no battery) -> OR-ing TBD -> 5 V board rail
```

- `ASSUMED`: the 5 V input feeds the external connectors directly, and both 3.3 V rails come from the 5 V input.
- `TBD`: whether 3.3 V_IMU is a separate LDO or a filtered branch of 3.3 V. The schematic draws a separate `+3V3A` LDO, but its purpose is not decided (OPEN-011).
- USB VBUS powers the board on the bench without the battery (team, integration questions). `TBD`: how it is isolated from the PM02D 5 V, and which external 5 V ports it feeds (OPEN-006).
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
| STM32H743VIT6 | 1 | TBD | TBD | Not read yet (NotebookLM notebook `STM32H743VI`) | `NOT_VERIFIED` |
| STM32F100C8T6B | 1 | 15.4 mA max at 24 MHz, all peripherals on, code from Flash, TA 85 °C | Not stated | F1 value-line DS Table 12 (NotebookLM) | `VERIFIED` for the table condition (8 MHz external clock with PLL); at a 24 MHz HSE without PLL `ESTIMATED` as no higher |
| ICP-20100 | 1 | TBD | TBD | invensense.tdk.com unreachable | `NOT_VERIFIED` |
| BMP581 (barometer 2, DEC-010) | 1 | TBD | TBD | Not read yet (NotebookLM notebook `BMP581`) | `NOT_VERIFIED` |
| IST8310 (magnetometer, DEC-011) | 1 | 1.2 mA at 200 sps, 0.32 mA at 50 sps (typ, AVDD 2.8 V) | Not stated | IST8310 DS V1.2, 4.3 (NotebookLM) | `VERIFIED` at 2.8 V; at 3.3 V `NOT_VERIFIED` |
| I2C pull-ups | TBD | TBD | - | Depends on P1-004, P1-005 | `TBD` |
| LEDs: 3 board (IF-047), 3 px4io, safety LED (IF-049) | 7 | TBD (set by the resistors) | - | Resistors not chosen | `TBD` |
| External 3.3 V devices | TBD | TBD | TBD | Not defined | `TBD` |

### 5 V (external connectors and regulator input)

| Load | Ref | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| Telemetry 1, ELRS receiver | IF-010 | TBD (5 V supply; model TBD, team) | TBD | Team | `TBD` |
| Telemetry 2 | IF-011 | TBD (no device planned; connector fitted for a second receiver) | TBD | Team | `TBD` |
| GPS1 + compass | IF-012 | TBD (Holybro M9N, to be confirmed) | TBD | Team | `TBD` |
| MS4525DO | IF-014 | TBD (5 V Pixhawk layout if the module has a regulator; part number TBD, team) | TBD | Snippet | `NOT_VERIFIED` |
| TF-Luna | IF-015 | 70 mA or less average (3.7 to 5.2 V supply) | 150 mA | Snippet (third-party PDF) | `NOT_VERIFIED` |
| 3.3 V regulator input | - | Sum of section 3.3 V loads | TBD | - | `TBD` |

### 6 V servo rail (on the board, DEC-019)

All of this current passes through the UBEC input header and the on-board 6 V and servo GND bus (OPEN-021). Each servo header pin carries only its own servo's current.

| Load | Ref | Qty | Current each | Stall / peak | Label |
| ---- | --- | --- | ------------ | ------------ | ----- |
| Tilt servos, RDS3235 or DS3218 (not chosen) | IF-034 to IF-037 | 4 | TBD; team bench target: all 4 at or below 10 A while tilting 0 to 90° at hover thrust | TBD (team bench test) | `TBD` |
| Flaperon and ruddervator servos, ES08 class | IF-030 to IF-033 | 4 | TBD | TBD (team bench test) | `TBD` |
| Spare outputs on the H743 | IF-017 to IF-019 | 0 planned (DEC-018); pads only | - | - | - |

All 8 servos can move at the same time (team): the tilt servos move all the time in hover, and the 4 surface servos move together in cruise.

The 4 motor outputs (IF-040 to IF-043) carry only the DShot signal to the ESCs (DEC-016); motor power does not pass through the board (`ASSUMED`).

## 4. Totals

| Rail | Known subtotal | Missing | Budget | Margin | Label |
| ---- | -------------- | ------- | ------ | ------ | ----- |
| 3.3 V_IMU | 0.88 mA (2 × 0.44 mA) | IMU peak | TBD. The drawn `+3V3A` LDO TPS73533DRBR is rated 500 mA (TI SBVS087M 5.3) but is not decided (OPEN-011). | TBD | `ESTIMATED` from `NOT_VERIFIED` inputs |
| 3.3 V | about 17 mA (IST8310 at 200 sps, F100 max 15.4 mA) | H743, ICP-20100, BMP581, pull-ups, LEDs | 2 A, TPS62142RGTR (DEC-012, TI SLVSAJ0F) | TBD | `ESTIMATED` from partial inputs |
| 5 V | 70 mA average, 150 mA peak (TF-Luna only) | All other external loads, 3.3 V regulator input | 2 A source (PWR-010) | TBD | `ESTIMATED` from partial inputs |
| 6 V (on the board) | none | All servo loads | 10 A cont., 15 A inst. (PWR-011), UBEC and board input | TBD | `TBD` |

The subtotals are far from complete. Do not use them to size a regulator. The MCUs and the external 5 V devices are likely the largest loads (`ASSUMED`).

## 5. Rail tolerances (PWR-013)

| Rail | Nominal | Min | Max | Load step | Ripple / noise | Label |
| ---- | ------- | --- | --- | --------- | -------------- | ----- |
| 5 V input | 5 V | 4.5 V | 5.5 V | TBD | TBD | `VERIFIED` (PWR-010) for min/max |
| 3.3 V | 3.3 V | TBD | TBD, at most 3.6 V | TBD | TBD | `TBD` |
| 3.3 V_IMU | 3.3 V | TBD | TBD, at most 3.6 V | TBD | TBD | `TBD` |
| 6 V servo | 6 V | TBD | TBD | TBD | TBD | `TBD` |

Known upper bounds for the 3.3 V rails:
- ICM-45686 VDD and VDDIO max 3.6 V recommended, 4 V absolute maximum (IMU rec, `NOT_VERIFIED`).
- IST8310 AVDD and DVDD max 3.6 V recommended and 3.6 V absolute maximum (IST8310 DS V1.2, 4.1 and 4.2, `VERIFIED` via NotebookLM). This is the tightest limit on the 3.3 V rail.
- `ESTIMATED`: 3.3 V nominal leaves 0.3 V (9 %) to the 3.6 V limit for regulator tolerance, load transients and overshoot.
- F100 VDD 2 to 3.6 V (F1 value-line DS Table 8, `VERIFIED`). H743 VDD range `TBD`.

## 6. Brownout and reset thresholds (PWR-014)

| Item | Threshold | Source | Label |
| ---- | --------- | ------ | ----- |
| H743 BOR level (option bytes) | TBD | ST datasheet / RM | `NOT_VERIFIED` |
| H743 PVD level | TBD | ST datasheet / RM | `NOT_VERIFIED` |
| F100 POR/PDR | Falling 1.8 / 1.88 / 1.96 V, rising 1.84 / 1.92 / 2.0 V (min / typ / max), 40 mV hysteresis | F1 value-line DS Table 10 (NotebookLM) | `VERIFIED` |
| F100 PVD level | 8 levels, falling-edge typ 2.08 to 2.78 V, 100 mV hysteresis; enabled by software | F1 value-line DS Table 10 (NotebookLM) | `VERIFIED` |
| 5 V input undervoltage detect | TBD (does the board monitor 5 V?) | Not defined | `TBD` |
| 6 V servo rail monitor | Read by the F100 through the 3:1 divider (IF-050); threshold TBD | px4io-v2 | `TBD` |

## 7. Protection requirements (OPEN-006, OPEN-007, SAF-012 to SAF-014)

All `TBD`. Items to decide:

- [ ] 5 V input: reverse polarity, overvoltage clamp, transient (TVS) rating, inrush.
- [ ] USB VBUS and PM02D 5 V: OR-ing or isolation, so neither back-feeds the other.
- [ ] 6 V servo bus on the board (DEC-019): UBEC input rated for 10 A continuous and 15 A peak; 6 V and servo GND copper; servo GND joined to logic GND at one point away from the sensors; no back-feed from the 6 V bus into the 5 V side (OPEN-021).
- [ ] 6 V servo rail: overcurrent behavior, pulse duration of the 15 A rating, bulk capacitance.
- [ ] USB-only power: VBUS current limit and which external 5 V ports it feeds (OPEN-006).
- [ ] External 5 V connectors: short-circuit protection per connector or per group.
- [ ] ESD on external connectors and USB (SAF-014).
- [ ] Safe output state on 5 V loss or 6 V fault (SAF-012, SAF-013).

## 8. Findings

| Severity | Ref | Label | Finding | Source |
| -------- | --- | ----- | ------- | ------ |
| MAJOR | PWR-012 | `NOT_VERIFIED` | Board current budget cannot be closed: MCU currents and all external 5 V device models are missing. | Section 4 |
| MAJOR | IF-030 to IF-037 / UBEC | `NOT_VERIFIED` | All 8 servos can move at once and stall current is not known. The 10 A team target covers only the 4 tilt servos (OPEN-007). | Section 3 |
| MAJOR | UBEC input header / 6 V bus | `ESTIMATED` | The UBEC input + and GND pins carry the total servo current, up to 10 A continuous and 15 A peak. One 2.54 mm header pin is usually rated about 3 A (header not chosen, NOT_VERIFIED), so one header position is not enough (OPEN-021). | DEC-019, PWR-011 |
| MINOR | IST8310 / 3.3 V | `VERIFIED` | IST8310 absolute maximum supply is 3.6 V, so the 3.3 V rail must never overshoot by more than 0.3 V (9 %), including start-up and load steps. | IST8310 DS V1.2, 4.1 |
| INFO | IF-022 / 5 V | `VERIFIED` (team answer) | USB VBUS powers the board on the bench, so it needs OR-ing or isolation from the PM02D 5 V. | Section 2 |
| INFO | IF-022 / 5 V | `ESTIMATED` | If USB also feeds the external 5 V ports, GPS, ELRS, TF-Luna (150 mA peak alone) and airspeed together may exceed a 500 mA USB port. | Section 3 |

## 9. Open inputs

- [ ] ELRS receiver model and supply current (team, P0-022). GPS: Holybro M9N supply current. Telemetry 2: no device planned.
- [ ] Servo stall current (team bench test, P0-022). Servo power passes through the board (DEC-019), so it also sizes the board input and bus.
- [ ] 3.3 V_IMU rail structure: separate LDO or filtered branch (human).
- [x] USB VBUS as a board power source: yes, on the bench (team). Which loads it feeds: open (section 7).
- [ ] STM32H743 VDD range, run current at the planned clock, BOR/PVD levels (user-supplied values or approved datasheet route). STM32F100: done (VDD 2 to 3.6 V, Table 8; sections 3.3 V and 6).
- [ ] ICP-20100 supply range and current.
- [ ] MS4525DO part number and supply current (team, P0-022). The team accepts the 5 V Pixhawk layout if the module has its own regulator.
- [ ] Retry the official pages for TF-Luna and MS4525DO.

## 10. Sources

- IST8310 Datasheet, Version 1.2 (NotebookLM notebook `IST8301`, not opened by Claude)
- F1 value-line DS: ST DocID16455 Rev 9 (STM32F100x4/6/8/B), NotebookLM notebook `STM32F100`, read as source fulltext
- TF-Luna snippet source (third-party PDF, not opened): https://files.waveshare.com/upload/c/c3/SJ-GU-TF-Luna_A05_Datasheet.pdf
- TI TPS62142: https://www.ti.com/product/TPS62142
- TI TPS735 (TPS73533DRBR): https://www.ti.com/product/TPS735 and https://www.ti.com/document-viewer/TPS735/datasheet/electrical-characteristics-slvscd4719
- ICM-45686: see `AO-HORIZON_IMU_SELECTION_EN.md`
- Requirements: `AO-HORIZON_SPEC_EN.md` sections on power, safety and interfaces
