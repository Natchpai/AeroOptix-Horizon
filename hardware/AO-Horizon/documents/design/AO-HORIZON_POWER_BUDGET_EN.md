# AeroOptix-Horizon: Power Budget

**Revision:** 0.23
**Updated:** 2026-11-14
**Status:** Draft record with open `TBD` rows. The main 3.3 V buck is TPS62142RGTR (DEC-012), the 5 V input is a TPS2121 power mux with a 1.5 A limit (DEC-029, DEC-030) and the `+3V3A` LDO is TPS73533DRBR (DEC-027). No other rail, regulator or protection part is approved. Not a verification record.
**Requirement refs:** PWR-010 to PWR-015, SAF-012 to SAF-014, OPEN-006 (closed), OPEN-007, OPEN-011, OPEN-021, OPEN-024 (closed), OPEN-025, OPEN-028. Decisions: DEC-007, DEC-010, DEC-011, DEC-012, DEC-018, DEC-019, DEC-025, DEC-027, DEC-028, DEC-029, DEC-030, DEC-031, DEC-032, DEC-033, DEC-034, DEC-035, DEC-036, DEC-037, DEC-038, DEC-039, DEC-040, DEC-043, DEC-044, DEC-048. Checklist task: P0-017.
**Decision owner:** Hardware

Single record for rail loads, rail tolerances, brownout thresholds and power protection requirements.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet PDF was opened by Claude; TI values come from NotebookLM source fulltext.

Source keys used below:
- **Spec**: `AO-HORIZON_SPEC_EN.md`.
- **Bosch**: Bosch Sensortec product page, fetched 2026-10-18.
- **IMU rec**: `AO-HORIZON_IMU_SELECTION_EN.md` (datasheet values extracted by agy, `NOT_VERIFIED`).
- **Snippet**: search-result text of a PDF datasheet. Not opened, always `NOT_VERIFIED`.
- **TI**: ti.com product pages and HTML datasheets (TPS62142: SLVSAJ0F Rev. F; TPS735: SBVS087M), fetched 2026-10-18 and 2026-10-19.
- **TI mux**: TPS212x datasheet SLVSEA3F (August 2020), NotebookLM notebook `TPS212x 2.8-V to 22-V Priority Power MUX with Seamless Switchover` (added by the human owner), read as source fulltext.

Fetches to st.com, invensense.tdk.com, te.com and en.benewake.com failed on 2026-10-18 (`getaddrinfo EAI_AGAIN`). The rows that depend on them are `TBD`.

## 1. Fixed limits

| Item | Value | Source | Label |
| ---- | ----- | ------ | ----- |
| Board input (PWR-010) | 4.5 / 5 / 5.5 V min/nom/max, ±10 %, source capacity 2 A | Spec, DEC-007 | `VERIFIED` (requirement) |
| Servo supply (PWR-011) | 6 V nominal, min/max TBD; 10 A continuous, 15 A instantaneous (UBEC-10A reference, not an approved part). UBEC into a board-mount XT30, 8 headers on a shared 6 V bus (DEC-019) | Spec, DEC-007, DEC-019 | `VERIFIED` (requirement) |

## 2. Candidate power tree

From the spec diagram. Candidate only, not approved (spec PWR-013).

```text
6S battery -> XT90-S -> PM02D -> CRIUS PDB v1.0
                           |            |
                           |            +-> 6 V UBEC -> board XT30 -> on-board 6 V bus
                           |                             -> 8 servo headers (+ IF-050 sense)
                           +-> TPS2121 mux IN1, 1.5 A (DEC-029/030) -> 5 V bus -> 3.3 V (MCUs, sensor VDDIO)
                                                                  +-> +3V3A LDO -> 3.3 V_IMU (sensor VDD, DEC-043)
                                                                  +-> 5 V external connectors
USB VBUS (bench) -> TPS2121 mux IN2 ----------------------------^
```

- `ASSUMED`: the 5 V input feeds the external connectors directly, and both 3.3 V rails come from the 5 V input.
- 3.3 V_IMU is the `+3V3A` rail from its own LDO. It feeds the VDD pins of the 2 IMUs, both barometers and the IST8310 (AVDD); their VDDIO pins (IST8310 DVDD) stay on `+3V3` (DEC-043, human owner, 2026-11-12; replaces DEC-025). The LDO is TPS73533DRBR (DEC-027, 2026-10-31).
- USB VBUS powers the board and all external 5 V ports on the bench without the battery (team; all ports: human owner, 2026-10-24). The TPS2121 power mux joins USB (IN2) and the PM02D (IN1) and blocks reverse current on both channels (TI mux 9.3.6, `VERIFIED`). The PR1 and CP2 dividers give the PM02D priority with the XCOMP fast switchover (DEC-031 to DEC-034); switch points in section 6.
- The saved `power_supplies.kicad_sch` draws `+5V` from the TPS2121 power mux (U101), and `+3V3` from the TPS62142RGTR buck (DEC-012) and `+3V3A` from the TPS73533DRBR LDO (DEC-027), both fed from `+5V`. The LDO is enabled by the buck power-good, so `+3V3A` starts after `+3V3` (DEC-039). Mux settings: DEC-030 to DEC-036, checked against TI mux (sections 6 and 7). Status LED on the mux ST pin (DEC-035, DEC-036); LED current `TBD` (LED forward voltage not checked). Details: spec 4.3 "Schematic state".

## 3. Load table

Typical or average current per load. Peak current listed where known. "TBD" means no source yet.

### 3.3 V_IMU

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| ICM-45686, 6-axis low-noise, 6400 Hz | 2 | 0.44 mA | TBD | IMU rec (DS Table 3) | `NOT_VERIFIED` |
| ICP-20100 VDD | 1 | TBD | TBD | Not read | `NOT_VERIFIED` |
| BMP581 VDD | 1 | TBD | TBD | Not read | `NOT_VERIFIED` |
| IST8310 AVDD | 1 | TBD | TBD | Not read | `NOT_VERIFIED` |

Since DEC-043 (2026-11-12), this rail feeds the VDD pins of all sensors. VDDIO (IST8310 DVDD) stays on the 3.3 V rail, so the sensor I/O current stays in the 3.3 V row.

### 3.3 V

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| STM32H743VIT6 | 1 | 220 mA typ at Tj 25 °C; 436 mA max at Tj 85 °C, 546 mA max at Tj 105 °C (Run mode, 480 MHz VOS0, code from flash, cache on, all peripherals enabled, LDO on) | Same | ST DS12110 Rev 11 Table 120 (NotebookLM notebook `STM32H743VI`, cited_text, 2026-11-03) | `VERIFIED` for the table condition; the firmware clock and peripheral use are `ASSUMED` |
| STM32F100C8T6B | 1 | 15.4 mA max at 24 MHz, all peripherals on, code from Flash, TA 85 °C | Not stated | F1 value-line DS Table 12 (NotebookLM) | `VERIFIED` for the table condition (8 MHz external clock with PLL); at a 24 MHz HSE without PLL `ESTIMATED` as no higher |
| ICP-20100 | 1 | TBD | TBD | invensense.tdk.com unreachable | `NOT_VERIFIED` |
| BMP581 (barometer 2, DEC-010) | 1 | TBD | TBD | Not read yet (NotebookLM notebook `BMP581`) | `NOT_VERIFIED` |
| IST8310 (magnetometer, DEC-011) | 1 | 1.2 mA at 200 sps, 0.32 mA at 50 sps (typ, AVDD 2.8 V) | Not stated | IST8310 DS V1.2, 4.3 (NotebookLM) | `VERIFIED` at 2.8 V; at 3.3 V `NOT_VERIFIED` |
| Clock oscillators U202 (ECS-2520MV-160-CN-TR, 16 MHz) and U302 (ASDDV-24.000MHZ-LC-T, 24 MHz), type decided 2026-11-14 (spec DEC-044), part numbers decided (DEC-048), data open (OPEN-028) | 2 | TBD | TBD | Datasheets not read | `NOT_VERIFIED` |
| I2C pull-ups | TBD | TBD | - | Depends on P1-004, P1-005 | `TBD` |
| LEDs: 3 board (IF-047), 3 px4io, safety LED (IF-049) | 7 | TBD (set by the resistors) | - | Resistors not chosen | `TBD` |
| External 3.3 V devices | TBD | TBD | TBD | Not defined | `TBD` |

### 5 V (external connectors and regulator input)

| Load | Ref | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| Telemetry 1, ELRS receiver | IF-010 | about 100 mA (model TBD) | - | Human owner, 2026-11-03 | `ASSUMED` |
| Telemetry 2 | IF-011 | TBD (no device planned; connector fitted for a second receiver) | TBD | Team | `TBD` |
| GPS1 + compass | IF-012 | about 100 mA (Holybro M9N, to be confirmed) | - | Human owner, 2026-11-03 | `ASSUMED` |
| MS4525DO | IF-014 | about 5 mA (5 V Pixhawk layout if the module has a regulator; 3.3 V or 5 V version TBD, team) | - | Snippet | `NOT_VERIFIED` |
| TF-Luna | IF-015 | 70 mA or less average (3.7 to 5.2 V supply); budgeted at 150 mA (human owner) | 150 mA | Snippet (third-party PDF); human owner, 2026-11-03 | `NOT_VERIFIED` |
| Buzzer (TIM3_CH3) | IF-047 | about 30 mA | - | Human owner, 2026-11-03 | `ASSUMED` |
| 3.3 V regulator input | - | Sum of section 3.3 V loads | TBD | - | `TBD` |

### 6 V servo rail (on the board, DEC-019)

All of this current passes through the XT30 input and the on-board 6 V and servo GND bus (OPEN-021). Every servo model is rated for 6 V (human owner). Each servo header pin carries only its own servo's current.

| Load | Ref | Qty | Current each | Stall / peak | Label |
| ---- | --- | --- | ------------ | ------------ | ----- |
| Tilt servos, RDS3235 (team design) | IF-034 to IF-037 | 4 | TBD; team bench target: all 4 at or below 10 A while tilting 0 to 90° at hover thrust | TBD (team bench test) | `TBD` |
| Flaperon and ruddervator servos, Kingmax C507 and DS-843MG (positions TBD, team) | IF-030 to IF-033 | 4 | TBD | TBD (team bench test) | `TBD` |
| Spare outputs on the H743 | IF-017 to IF-019 | 0 planned (DEC-018); pads only | - | - | - |

All 8 servos can move at the same time (team): the tilt servos move all the time in hover, and the 4 surface servos move together in cruise.

The 4 motor outputs (IF-040 to IF-043) carry only the signal to 4 separate Skywalker 80A V2 ESCs; motor power does not pass through the board (`ASSUMED`). The ESC headers have the + pin removed, so the ESC BECs (5 V) do not reach the board.

## 4. Totals

| Rail | Known subtotal | Missing | Budget | Margin | Label |
| ---- | -------------- | ------- | ------ | ------ | ----- |
| 3.3 V_IMU | 0.88 mA (2 × 0.44 mA, IMUs only) | IMU peak; ICP-20100, BMP581 and IST8310 VDD currents (DEC-043) | TBD. 500 mA, TPS73533DRBR (DEC-027, TI SBVS087M 5.3). | TBD | `ESTIMATED` from `NOT_VERIFIED` inputs |
| 3.3 V | about 244 mA typ (design current about 0.6 A maximum, DEC-040; L101 1.2 A rating, distributor `NOT_VERIFIED`, allows about 0.5 A buck input); about 460 mA with the H743 at its Tj 85 °C maximum, about 570 mA at Tj 105 °C (H743, F100 max 15.4 mA, IST8310, D104 about 2.5 mA, and an assumed 5 mA for the barometers and pull-ups) | ICP-20100, BMP581, pull-ups and px4io LEDs not read | 2 A, TPS62142RGTR (DEC-012, TI SLVSAJ0F) | TBD | `ESTIMATED` from partial inputs |
| 5 V | Board: about 190 to 215 mA typ, 360 to 400 mA with the H743 at its Tj 85 °C maximum, 445 to 495 mA at Tj 105 °C (3.3 V load through the buck at an assumed 85 % efficiency, 5.0 and 4.5 V in, plus D103 and the LDO). External: about 385 mA (ELRS 100, GPS 100, MS4525DO 5, TF-Luna 150, buzzer 30 mA; human owner). Total about 575 to 600 mA typ, 830 to 880 mA hot worst case | Telemetry 2 (no device planned) | 2 A source (PWR-010); power mux limit 1.0 / 1.5 / 2.0 A with 80.6 kΩ (DEC-030, TI mux, `VERIFIED`) | TBD | `ESTIMATED` from partial inputs |
| 6 V (on the board) | none | All servo loads | 10 A cont., 15 A inst. (PWR-011), UBEC and XT30 input | TBD | `TBD` |

The subtotals are far from complete. Do not use them to size a regulator. The MCUs and the external 5 V devices are likely the largest loads (`ASSUMED`).

**5 V headroom (`ESTIMATED` from the rows above).** Room left for GPS, ELRS and the MS4525DO after the board and the TF-Luna 150 mA peak:

| 5 V source | Typical | Hot worst case (H743 at Tj 105 °C) |
| ---------- | ------- | ---------------------------------- |
| PM02D, power mux 1.0 A minimum limit (DEC-030) | about 640 mA | about 360 mA |
| USB 500 mA port | about 140 mA | below zero |
| USB 900 mA port | about 540 mA | about 260 mA |
| Bench USB-C port above 1 A (DEC-038) | as the PM02D row: the 1.0 A minimum mux limit sets the room | as the PM02D row |

With the human owner's estimates (ELRS 100, GPS 100, MS4525DO 5, TF-Luna 150, buzzer 30 mA, about 385 mA), the PM02D or a bench USB-C port above 1 A has about 400 mA left typical and about 120 mA in the hot worst case (`ESTIMATED`, 2026-11-03).

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
| 5 V power mux input UV (U101) | Rising 2.5 / 2.65 / 2.8 V, falling 2.4 / 2.55 / 2.7 V | TI mux, Electrical Characteristics | `VERIFIED` |
| 5 V source priority (U101 PR1, CP2; DEC-031 to DEC-034) | XCOMP (R105 fitted, DEC-033): to USB at 3.78 / 3.98 / 4.18 V for `VBUS` 4.75 / 5.0 / 5.25 V; worst case 4.44 V at `VBUS` 5.25 V with 1 % resistors and the 40 mV comparator offset, below the 4.5 V minimum (DEC-034). VREF mode (R105 removed): to USB at 3.39 / 3.56 / 3.73 V, back at 3.45 / 3.63 / 3.76 V. Divider values in the spec DEC rows; method in the power mux notes | TI mux equations 5 and 12 form, VREF (spec 4.7) | `ESTIMATED` |
| 5 V input overvoltage (U101 OV1, OV2; DEC-036) | 5.98 V typ, 5.60 to 6.31 V with 1 % resistors; the channel turns off, back on below 5.87 V typ. `+5V` stays below 5.5 V in normal operation (PWR-015) | TI mux 10.2.4.2, equation 6, VREF rising and falling (spec 4.7) | `ESTIMATED` (VREF values `VERIFIED`) |
| 3.3 V buck soft-start (U102) | 10 nF SS/TR (DEC-028): about 5 ms | TI SLVSAJ0F equation 10 (spec 4.7) | `ESTIMATED` |
| 3.3 V buck PG (U102) | Open drain, pulled up by R113 100 kΩ to `+3V3`; local net `3V3_PG` to U103 EN through R115 (DEC-039); reaches no MCU pin and no sheet pin | Saved schematic; spec 4.3, OPEN-026 | `VERIFIED` (as drawn) |
| 6 V servo rail monitor | Read by the F100 through the 3:1 divider (IF-050); threshold TBD | px4io-v2 | `TBD` |

## 7. Protection requirements (OPEN-006, OPEN-007, SAF-012 to SAF-014)

All `TBD`. Items to decide:

- [x] 5 V power mux values (P2-020), TI mux, `VERIFIED` unless marked: TPS2121, 80.6 kΩ ILIM gives 1.0 / 1.5 / 2.0 A (DEC-030); OV trip per DEC-036 (section 6); IN and OUT 24 V absolute maximum; input UV 2.65 V typ; 10 nF SS gives about 0.65 ms ramp and about 0.47 A inrush into about 60 µF (`ESTIMATED`, outside TI Table 9-1); fast-trip at about 2.4 × ILM, then off for about 25 ms; thermal shutdown auto-recovers. Priority and switchover: DEC-031 to DEC-034.
- [ ] 5 V input, still open: reverse polarity; D101 SZSMF5.0A TVS: breakdown voltage 6.4 V, fine at the 5.5 V input (human owner, 2026-11-03); hot-plug peak on the PM02D cable (TI mux section 11 suggests a large capacitance near the input for long cables; since 2026-11-03 IN1 has 2 × 10 µF and a 47 µF 10 V tantalum with 0.25 Ω ESR, DEC-037; bench check P4-013).
- [x] USB VBUS and PM02D 5 V OR-ing: TPS2121 power mux (DEC-029), reverse current blocking on both channels (TI mux 9.3.6, `VERIFIED`). Source priority: PM02D first, XCOMP switchover (DEC-031 to DEC-034).
- [ ] 6 V servo bus on the board (DEC-019): board-mount XT30 input, rating against 10 A continuous and 15 A peak `NOT_VERIFIED`; 6 V and servo GND copper; servo GND joined to logic GND at one point away from the sensors; no back-feed from the 6 V bus into the 5 V side (OPEN-021).
- [ ] 6 V servo rail: overcurrent behavior, pulse duration of the 15 A rating, bulk capacitance.
- [x] USB-only power: the bench USB-C port shall supply more than 1 A; brown-out of the external devices on a weaker port is accepted (DEC-038, 2026-11-03). The power mux 1.0 A minimum limit also applies on USB. USB-C CC resistors and the current advertisement are open in P1-006.
- [ ] External 5 V connectors: short-circuit protection per connector or per group.
- [ ] ESD on external connectors and USB (SAF-014).
- [ ] Safe output state on 5 V loss or 6 V fault (SAF-012, SAF-013).

## 8. Findings

| Severity | Ref | Label | Finding | Source |
| -------- | --- | ----- | ------- | ------ |
| MINOR | PWR-012 | `ESTIMATED` | 5 V budget closed on 2026-11-03 (see spec OPEN-006) with the human owner's external load estimates: about 880 mA hot worst case against the 1.0 A minimum mux limit, about 120 mA margin. Barometer currents and the external device models are still estimates; check on the bench (P4-014). | Section 4 |
| MAJOR | IF-030 to IF-037 / UBEC | `NOT_VERIFIED` | All 8 servos can move at once and stall current is not known. The 10 A team target covers only the 4 tilt servos (OPEN-007). | Section 3 |
| MAJOR | XT30 input / 6 V bus | `NOT_VERIFIED` | The XT30 input carries the total servo current, up to 10 A continuous and 15 A peak. Its rating is not checked. (OPEN-021). | DEC-019, PWR-011 |
| MINOR | DEC-030 / 5 V | `VERIFIED` | The power mux limit with 80.6 kΩ is 1.0 to 2.0 A (1.5 A typ). The board plus all external 5 V loads must fit under 1.0 A for a worst-case part, with the load currents still unknown. | Section 4; TI mux |
| MINOR | IST8310 / 3.3 V | `VERIFIED` | IST8310 absolute maximum supply is 3.6 V, so the 3.3 V rail must never overshoot by more than 0.3 V (9 %), including start-up and load steps. | IST8310 DS V1.2, 4.1 |
| INFO | IF-022 / 5 V | `VERIFIED` (team answer) | USB VBUS powers the board on the bench. It joins the PM02D 5 V through the power mux IN2 (DEC-029). | Section 2 |
| MINOR | IF-022 / 5 V | `ESTIMATED` | USB feeds all external 5 V ports (human owner). On a 500 mA port the board at its hot maximum plus the TF-Luna peak already uses the whole port. Accepted: USB is a bench supply, the bench USB-C port shall supply more than 1 A, and brown-out on a weaker port is accepted (DEC-038, 2026-11-03). | Section 4 |

## 9. Open inputs

- [x] ELRS about 100 mA, GPS about 100 mA (human owner estimates, 2026-11-03). Models still from the team (P0-022). Telemetry 2: no device planned.
- [ ] Servo stall current (team bench test, P0-022). Servo power passes through the board (DEC-019), so it also sizes the board input and bus.
- [x] 3.3 V_IMU rail structure: `+3V3A` from its own LDO, sensor VDD pins (DEC-043, 2026-11-12; was IMUs only, DEC-025). LDO TPS73533DRBR (DEC-027, 2026-10-31).
- [x] USB VBUS as a board power source: yes, on the bench (team). It feeds all external 5 V ports (human owner, 2026-10-24).
- [x] TPS2121 values from TI: done 2026-11-01 (section 7, TI mux).
- [x] Power mux priority and switchover: PM02D first, XCOMP with R105 fitted, 4.44 V worst-case switch point with 1 % resistors (DEC-031 to DEC-034; OPEN-024 closed).
- [ ] XT30 current rating (OPEN-021).
- [x] STM32H743 run current at the DS12110 Table 120 condition (section 3.3 V, `VERIFIED`). STM32F100: VDD 2 to 3.6 V (Table 8), POR/PDR and PVD (sections 5 and 6), `VERIFIED`.
- [ ] STM32H743 VDD range, BOR and PVD levels, and run current at the firmware's clock and peripheral use (`NOT_VERIFIED`; user-supplied values or approved datasheet route).
- [ ] ICP-20100 supply range and current.
- [ ] MS4525DO version (3.3 V or 5 V) and supply current (team, P0-022). The team accepts the 5 V Pixhawk layout if the module has its own regulator.
- [ ] Retry the official pages for TF-Luna and MS4525DO.

## 10. Sources

- IST8310 Datasheet, Version 1.2 (NotebookLM notebook `IST8301`, not opened by Claude)
- F1 value-line DS: ST DocID16455 Rev 9 (STM32F100x4/6/8/B), NotebookLM notebook `STM32F100`, read as source fulltext
- TF-Luna snippet source (third-party PDF, not opened): https://files.waveshare.com/upload/c/c3/SJ-GU-TF-Luna_A05_Datasheet.pdf
- TI TPS62142: https://www.ti.com/product/TPS62142
- TI TPS735 (TPS73533DRBR): https://www.ti.com/product/TPS735 and https://www.ti.com/document-viewer/TPS735/datasheet/electrical-characteristics-slvscd4719
- TI TPS212x (TPS2121): SLVSEA3F, https://www.ti.com/product/TPS2121 (ACTIVE, fetched 2026-11-01), in NotebookLM notebook `TPS212x 2.8-V to 22-V Priority Power MUX with Seamless Switchover` (added by the human owner; not opened by Claude)
- ST STM32H743VI: DS12110 Rev 11, NotebookLM notebook `STM32H743VI` (not opened by Claude)
- ICM-45686: see `AO-HORIZON_IMU_SELECTION_EN.md`
- Requirements: `AO-HORIZON_SPEC_EN.md` sections on power, safety and interfaces
