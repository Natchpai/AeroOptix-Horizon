# AeroOptix-Horizon: Power Budget

**Revision:** 0.42
**Updated:** 2026-11-28
**Status:** Draft record with open `TBD` rows. The main 3.3 V buck is TPS62142RGTR (DEC-012), the 5 V input is a TPS2121 power mux with a 1.5 A limit (DEC-029, DEC-030) and the `+3V3A` LDO is TPS73533DRBR (DEC-027). No other rail, regulator or protection part is approved. Not a verification record.
**Requirement refs:** PWR-010 to PWR-015, SAF-012 to SAF-014, OPEN-006 (closed), OPEN-011, OPEN-021 (servo load, was OPEN-007), OPEN-024 (closed), OPEN-025 (closed; bench check P4-012), OPEN-028, OPEN-041. Decisions: DEC-007, DEC-010, DEC-011, DEC-012, DEC-018, DEC-019, DEC-053, DEC-054, DEC-025, DEC-027, DEC-028, DEC-029, DEC-030, DEC-031, DEC-032, DEC-033, DEC-034, DEC-035, DEC-036, DEC-037, DEC-038, DEC-039, DEC-040, DEC-043, DEC-044, DEC-048, DEC-055, DEC-058, DEC-059, DEC-108, DEC-110 to DEC-114 (servo rails). Checklist tasks: P0-017 (done), P2-010 (calculations in sections 5 and 11).
**Decision owner:** Hardware

Single record for rail loads, rail tolerances, brownout thresholds and power protection requirements.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet PDF was opened by Claude; TI values come from NotebookLM source fulltext.

Source keys used below:
- **Spec**: `AO-HORIZON_SPEC_EN.md`.
- **Bosch**: Bosch Sensortec product page, fetched 2026-10-18.
- **IMU rec**: `AO-HORIZON_IMU_SELECTION_EN.md` (datasheet values extracted by agy, `NOT_VERIFIED`).
- **Snippet**: search-result text of a PDF datasheet. Not opened, always `NOT_VERIFIED`.
- **TI**: ti.com product pages and HTML datasheets (TPS62142: SLVSAJ0F Rev. F; TPS735: SBVS087M), fetched 2026-10-18 and 2026-10-19.
- **TDK and iSentek text**: ICM-45686 DS-000489 Rev 1.1, ICP-20100 DS-000416 Rev 1.3, BMP581 Rev 1.13 and IST8310 V1.8, read as NotebookLM source fulltext (2026-11-21).
- **TI mux**: TPS212x datasheet SLVSEA3F (August 2020), NotebookLM notebook `TPS212x 2.8-V to 22-V Priority Power MUX with Seamless Switchover` (added by the human owner), read as source fulltext.

Fetches to st.com, invensense.tdk.com, te.com and en.benewake.com failed on 2026-10-18 (`getaddrinfo EAI_AGAIN`). The rows that depend on them are `TBD`.

## 1. Fixed limits

| Item | Value | Source | Label |
| ---- | ----- | ------ | ----- |
| Board input (PWR-010) | 4.5 / 5 / 5.5 V min/nom/max, ±10 %, source capacity 2 A | Spec, DEC-007 | `VERIFIED` (requirement) |
| Servo supply (PWR-011) | Two rails, `+VSERVO1` (4 tilt servos) and `+VSERVO2` (4 surface servos), 6 to 8.4 V each (DEC-110); the DS3235 above its 7.4 V rating is accepted (DEC-113). One UBEC per rail (DEC-114), each through a 1x3 header, CN804 and CN805, XT30 removed (DEC-111); UBEC model, setting and current TBD. The earlier single UBEC reference was 10 A continuous, 15 A instantaneous (UBEC-10A, not an approved part) | Spec, DEC-019, DEC-110, DEC-111, DEC-113, DEC-114 | `VERIFIED` (requirement) |

## 2. Candidate power tree

From the spec diagram. Candidate only, not approved (spec PWR-013).

```text
6S battery -> XT90-S -> PM02D -> Tekko32 4in1 ESC battery pads (no PDB, DEC-054)
                           |            |
                           |            +-> UBEC 1 (on the ESC pads) -> CN804 header -> +VSERVO1 -> 4 tilt servo headers
                           |            +-> UBEC 2 (on the ESC pads) -> CN805 header -> +VSERVO2 -> 4 surface servo headers
                           |                             (each rail sensed by the F100, IF-050)
                           +-> TPS2121 mux IN1, 1.5 A (DEC-029/030) -> 5 V bus -> 3.3 V (MCUs, sensor VDDIO)
                                                                  +-> +3V3A LDO -> 3.3 V_IMU (sensor VDD, DEC-043)
                                                                  +-> 5 V external connectors
USB VBUS (bench) -> TPS2121 mux IN2 ----------------------------^
```

- No PDB (spec 4.3, rev 0.58): the 6 V UBEC is soldered to the ESC battery pads (human owner, 2026-11-19).
- `ASSUMED`: the 5 V input feeds the external connectors directly, and both 3.3 V rails come from the 5 V input.
- 3.3 V_IMU is the `+3V3A` rail from its own LDO. It feeds the VDD pins of the 2 IMUs, both barometers and the IST8310 (AVDD); their VDDIO pins (IST8310 DVDD) stay on `+3V3` (DEC-043, human owner, 2026-11-12; replaces DEC-025). The LDO is TPS73533DRBR (DEC-027, 2026-10-31).
- USB VBUS powers the board and all external 5 V ports on the bench without the battery (team; all ports: human owner, 2026-10-24). The TPS2121 power mux joins USB (IN2) and the PM02D (IN1) and blocks reverse current on both channels (TI mux 9.3.6, `VERIFIED`). The PR1 and CP2 dividers give the PM02D priority with the XCOMP fast switchover (DEC-031 to DEC-034); switch points in section 6.
- The saved `power_supplies.kicad_sch` draws `+5V` from the TPS2121 power mux (U101), and `+3V3` from the TPS62142RGTR buck (DEC-012) and `+3V3A` from the TPS73533DRBR LDO (DEC-027), both fed from `+5V`. The LDO is enabled by the buck power-good, so `+3V3A` starts after `+3V3` (DEC-039). Mux settings: DEC-030 to DEC-036, checked against TI mux (sections 6 and 7). Status LED on the mux ST pin (DEC-035, DEC-036); LED current `TBD` (LED forward voltage not checked). Details: spec 4.3 "Schematic state".
- Plan B (DEC-108): D105 and D106 MBR230LSFT1G Schottky diodes, DNP, join `PM02_5V` and `VBUS` to `+5V` on a board where U101 is not fitted. The tables below cover the default build with U101 only. Plan B `+5V` (source minus the diode drop), current limit and OV protection are open (OPEN-041, P3-012; diode data `NOT_VERIFIED`).

## 3. Load table

Typical or average current per load. Peak current listed where known. "TBD" means no source yet.

### 3.3 V_IMU

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| ICM-45686, 6-axis low-noise, 6400 Hz | 2 | 0.44 mA typ (0.42 mA at 1600 Hz) | Not stated | DS-000489 Rev 1.1 Table 3 (VDD 1.8 V, characterization) | `VERIFIED` for the table condition; at 3.3 V `NOT_VERIFIED` |
| ICP-20100 | 1 | 0.25 mA typ, highest mode (MODE4); MODE0 0.211 mA, MODE1 0.222 mA; standby 2.65 µA | Not stated | DS-000416 Rev 1.3 Table 2 and Table 5 | `VERIFIED` for the table condition |
| BMP581 | 1 | 0.075 mA typ, 0.08 mA max (high resolution, 30 Hz) | 0.26 mA max | BMP581 Rev 1.13 Table 4 | `VERIFIED` for the table condition |
| IST8310 | 1 | 1.2 mA typ at 200 sps, 0.32 mA at 50 sps; standby 10 µA | Not stated | IST8310 V1.8 3.3 (AVDD 2.8 V, DVDD 1.8 V) | `VERIFIED` at 2.8 V; at 3.3 V `NOT_VERIFIED` |

Since DEC-043 (2026-11-12), this rail feeds the VDD pins of all sensors. VDDIO (IST8310 DVDD) stays on the 3.3 V rail. None of the four datasheets splits the current between VDD and VDDIO, so each row above books the whole device current on this rail (an upper bound for VDD, `ESTIMATED`). The I/O share on the 3.3 V rail is not stated and is bounded by the same values.

### 3.3 V

| Load | Qty | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| STM32H743VIT6 | 1 | 220 mA typ at Tj 25 °C; 436 mA max at Tj 85 °C, 546 mA max at Tj 105 °C (Run mode, 480 MHz VOS0, code from flash, cache on, all peripherals enabled, LDO on) | Same | ST DS12110 Rev 11 Table 120 (NotebookLM notebook `STM32H743VI`, cited_text, 2026-11-03) | `VERIFIED` for the table condition; the firmware clock and peripheral use are `ASSUMED` |
| STM32F100C8T6B | 1 | 15.4 mA max at 24 MHz, all peripherals on, code from Flash, TA 85 °C | Not stated | F1 value-line DS Table 12 (NotebookLM) | `VERIFIED` for the table condition (8 MHz external clock with PLL); at a 24 MHz HSE without PLL `ESTIMATED` as no higher |
| ICP-20100 VDDIO | 1 | Not stated; at most 0.25 mA (device total, 3.3 V_IMU row) | Not stated | DS-000416 Rev 1.3 Table 2 | `ESTIMATED` upper bound |
| BMP581 (barometer 2, DEC-010) VDDIO | 1 | Not stated; at most 0.08 mA (device total, 3.3 V_IMU row) | 0.26 mA max | BMP581 Rev 1.13 Table 4 | `ESTIMATED` upper bound |
| IST8310 (magnetometer, DEC-011) DVDD | 1 | Not stated; at most 1.2 mA at 200 sps (device total, 3.3 V_IMU row) | Not stated | IST8310 V1.8 3.3 | `ESTIMATED` upper bound; at 3.3 V `NOT_VERIFIED` |
| Clock oscillators U202 (ECS-2520MV-160-CN-TR, 16 MHz) and U302 (ASDDV-24.000MHZ-LC-T, 24 MHz), type decided 2026-11-14 (spec DEC-044), part numbers decided (DEC-048), data checked against the MCU HSE limits (spec CMP-010) | 2 | U202 6.0 mA max (3.3 V, up to 19 MHz); U302 4.0 mA max (3.3 V, 20 to 30 MHz); both into 15 pF | Not stated | ECS-2520MV and Abracon ASDDV datasheets via NotebookLM | `VERIFIED` |
| I2C pull-ups | TBD | TBD | - | Depends on P1-003 | `TBD` |
| LEDs: RGB LED D901 (board, IF-047) and RGB LED D902 (px4io), 3 elements each (DEC-115); safety LED (IF-049) | 7 elements | TBD (set by the resistors) | - | 220 Ω per element (DEC-067, DEC-079, DEC-115); LED forward voltage not checked | `TBD` |
| External 3.3 V devices | TBD | TBD | TBD | Not defined | `TBD` |

### 5 V (external connectors and regulator input)

| Load | Ref | Current each | Peak | Source | Label |
| ---- | --- | ------------ | ---- | ------ | ----- |
| Telemetry 1, Holybro SiK radio V3 (DEC-053; replaces ELRS) | IF-010 | 100 mA transmit at 20 dBm, 25 mA receive | - | Holybro SiK telemetry radio V3 docs page, https://docs.holybro.com/radio/sik-telemetry-radio-v3 (100 mW model `ASSUMED`) | `VERIFIED` |
| RC IN, FlySky FS-iA6B receiver (DEC-053) | IF-038 | about 50 mA (placeholder; human owner: "small") | - | No current on the FlySky product page (OPEN-034) | `ASSUMED` |
| Telemetry 2 | IF-011 | TBD (no device planned; connector fitted for a second receiver) | TBD | Team | `TBD` |
| GPS1 + compass | IF-012 | about 100 mA (Holybro M9N, to be confirmed; V1, spec DEC-070) | - | Human owner, 2026-11-03 | `ASSUMED` |
| MS4525DO | IF-014 | about 5 mA (5 V Pixhawk layout if the module has a regulator; 3.3 V or 5 V version TBD, team) | - | Snippet | `NOT_VERIFIED` |
| TF-Luna | IF-015 | 70 mA or less average (3.7 to 5.2 V supply); budgeted at 150 mA (human owner) | 150 mA | Snippet (third-party PDF); human owner, 2026-11-03 | `NOT_VERIFIED` |
| Buzzer (TIM3_CH3) | IF-046 | about 30 mA | - | Human owner, 2026-11-03 | `ASSUMED` |
| 3.3 V regulator input | - | Sum of section 3.3 V loads | TBD | - | `TBD` |

### Servo rails `+VSERVO1` and `+VSERVO2` (on the board, DEC-019, DEC-110)

All of this current passes through the rail input headers CN804 (`+VSERVO1`) and CN805 (`+VSERVO2`) and the on-board rails and servo GND bus (DEC-111, OPEN-021). Tilt servos are on `+VSERVO1`, surface servos on `+VSERVO2` (DEC-113). Every servo model is rated for 6 V (human owner). Each servo header pin carries only its own servo's current.

| Load | Ref | Qty | Current each | Stall / peak | Label |
| ---- | --- | --- | ------------ | ------------ | ----- |
| Tilt servos, RDS3235 (team design), `+VSERVO1` | IF-034 to IF-037 | 4 | Idle 5 mA; about 0.5 A peak while moving under hand load, about 0 A when stopped (human owner, 2026-11-24; supply voltage and instrument not stated, `NOT_VERIFIED`); loaded running current TBD (team bench target: all 4 at or below 10 A while tilting 0 to 90° at hover thrust) | Stall 2.1 A at 6 V (DS3235 sheet; RDS3235 match `ASSUMED`) | `VERIFIED` (sheet values); load current `TBD` |
| Flaperon and ruddervator servos, Kingmax C507 V2 (human owner, 2026-11-19), `+VSERVO2` | IF-030 to IF-033 | 4 | Idle 10 mA, no-load 130 mA, rated working 0.65 A at 2.0 kg·cm | Stall 1.2 A at 6 V (C507 sheet; V2 match `ASSUMED`) | `VERIFIED` (sheet values) |
| Spare outputs on the H743 | IF-017 to IF-019 | 0 planned (DEC-018); pads only | - | - | - |

All 8 servos can move at the same time (team): the tilt servos move all the time in hover, and the 4 surface servos move together in cruise.

Per rail at 6 V stall: `+VSERVO1` 4 × 2.1 A = 8.4 A and `+VSERVO2` 4 × 1.2 A = 4.8 A (`ESTIMATED`), each through one header pin (DEC-113; pin rating `NOT_VERIFIED`, accepted). Measured tilt servo peak: about 4 × 0.5 A = 2 A on `+VSERVO1` with all 4 moving (`ESTIMATED`). Both rails together, all 8 stalled at 6 V: 4 × 2.1 A + 4 × 1.2 A = 13.2 A (`ESTIMATED`); against one 10 A UBEC (the earlier reference) that is 32 % over the 10 A UBEC continuous rating and 12 % under the 15 A peak. Surfaces at rated load (4 × 0.65 A = 2.6 A) plus the tilt servos at the team's 10 A target give up to 12.6 A (`ESTIMATED`). Datasheet values via NotebookLM, notebook `Servos` (section 10).

The 4 motor outputs (IF-040 to IF-043) carry only the signal and GND to one Tekko32 F4 4in1 50A ESC through an adapter cable (DEC-054); motor power does not pass through the board (`ASSUMED`). The ESC headers have the + pin removed, so no ESC supply reaches the board; the ESC's VBAT, current and telemetry wires stay in the cable.

## 4. Totals

| Rail | Known subtotal | Missing | Budget | Margin | Label |
| ---- | -------------- | ------- | ------ | ------ | ----- |
| 3.3 V_IMU | about 2.4 mA typ (2 × 0.44 + 0.25 + 0.08 + 1.2 mA), about 2.6 mA with the BMP581 0.26 mA peak; whole device currents, so an upper bound for the VDD pins | IMU and IST8310 peaks not stated; currents at 3.3 V not stated | 500 mA, TPS73533DRBR (DEC-027, TI SBVS087M 5.3) | over 99 % | `ESTIMATED` from `VERIFIED` table values |
| 3.3 V | about 244 mA typ (design current about 0.6 A maximum, DEC-040; L101 1.2 A rating, distributor `NOT_VERIFIED`, allows about 0.5 A buck input); about 460 mA with the H743 at its Tj 85 °C maximum, about 570 mA at Tj 105 °C (H743, F100 max 15.4 mA, IST8310, D104 about 2.5 mA, and an assumed 5 mA for the barometers and pull-ups); U202 and U302 add up to 10 mA max, not yet in these sums | Pull-ups and px4io LEDs; the ICP-20100 and BMP581 I/O share is within the assumed 5 mA in the subtotal | 2 A, TPS62142RGTR (DEC-012, TI SLVSAJ0F) | TBD | `ESTIMATED` from partial inputs |
| 5 V | Board: about 190 to 215 mA typ, 360 to 400 mA with the H743 at its Tj 85 °C maximum, 445 to 495 mA at Tj 105 °C (3.3 V load through the buck at an assumed 85 % efficiency, 5.0 and 4.5 V in, plus D103 and the LDO). External: about 435 mA (SiK radio 100, FS-iA6B 50 placeholder, GPS 100, MS4525DO 5, TF-Luna 150, buzzer 30 mA; DEC-053, human owner). Total about 625 to 650 mA typ, 880 to 930 mA hot worst case | Telemetry 2 (no device planned) | 2 A source (PWR-010); power mux limit 1.0 / 1.5 / 2.0 A with 80.6 kΩ (DEC-030, TI mux, `VERIFIED`) | TBD | `ESTIMATED` from partial inputs |
| Servo rails (on the board) | none | All servo loads | Per rail: UBEC TBD (DEC-111); one header pin per rail, CN804 and CN805 | TBD | `TBD` |

The subtotals are far from complete. Do not use them to size a regulator. The MCUs and the external 5 V devices are likely the largest loads (`ASSUMED`).

**5 V headroom (`ESTIMATED` from the rows above).** Room left for GPS, the SiK radio, the RC receiver and the MS4525DO after the board and the TF-Luna 150 mA peak:

| 5 V source | Typical | Hot worst case (H743 at Tj 105 °C) |
| ---------- | ------- | ---------------------------------- |
| PM02D, power mux 1.0 A minimum limit (DEC-030) | about 640 mA | about 360 mA |
| USB 500 mA port | about 140 mA | below zero |
| USB 900 mA port | about 540 mA | about 260 mA |
| Bench USB-C port above 1 A (DEC-038) | as the PM02D row: the 1.0 A minimum mux limit sets the room | as the PM02D row |

With the loads in section 3 (SiK radio 100, FS-iA6B 50 placeholder, GPS 100, MS4525DO 5, TF-Luna 150, buzzer 30 mA, about 435 mA; DEC-053), the PM02D or a bench USB-C port above 1 A has about 350 mA left typical and about 70 mA in the hot worst case (`ESTIMATED`, 2026-11-19; was about 400 and 120 mA with ELRS on 2026-11-03). If the FS-iA6B draws more than the 50 mA placeholder, the hot worst-case room shrinks by the same amount (OPEN-034).

### Rail summary

One number per cell, in mA, copied from the totals table and section 3 above (the upper end where they give a range). The team website draws its power bars from this table. It is not for sizing a regulator; the rows above keep the conditions.

| Rail | Typical load (mA) | Worst-case load (mA) | Limit (mA) | Limit from | Label |
| ---- | ----------------- | -------------------- | ---------- | ---------- | ----- |
| 3.3 V_IMU | 2.4 | 2.6 | 500 | TPS73533DRBR rating (DEC-027) | `ESTIMATED` |
| 3.3 V | 244 | 570 | 600 | `+3V3` design current (DEC-040); the TPS62142RGTR is rated 2 A | `ESTIMATED` |
| 5 V | 650 | 930 | 1000 | TPS2121 minimum current limit (DEC-030) | `ESTIMATED` |
| `+VSERVO1` | TBD | 8400 | 10000 | UBEC-10A reference (PWR-011), one UBEC per rail (DEC-114); model TBD | `ESTIMATED` (worst case: 4 tilt servos stalled at 6 V) |
| `+VSERVO2` | TBD | 4800 | 10000 | UBEC-10A reference (PWR-011), one UBEC per rail (DEC-114); model TBD | `ESTIMATED` (worst case: 4 surface servos stalled at 6 V) |

## 5. Rail tolerances (PWR-013)

| Rail | Nominal | Min | Max | Load step | Ripple / noise | Label |
| ---- | ------- | --- | --- | --------- | -------------- | ----- |
| 5 V input | 5 V | 4.5 V | 5.5 V | TBD | TBD | `VERIFIED` (PWR-010) for min/max |
| 3.3 V (U102 TPS62142, fixed 3.3 V) | 3.3 V | 3.241 V PWM, 3.224 V power-save | 3.359 V PWM, 3.392 V power-save | Not stated (transient response depends on L and COUT); measure at P4-002 | Not stated | Accuracy `VERIFIED` (TI SLVSAJ0F 7.5: ±1.8 % over TJ −40 to 125 °C in PWM, −2.3 / +2.8 % in power-save with 22 µF; fixed versions include the internal divider); limits `ESTIMATED` (load regulation 0.05 %/A and line regulation 0.02 %/V add under 0.1 %) |
| 3.3 V_IMU (U103 TPS73533) | 3.3 V | 3.234 V | 3.366 V | Not stated | Not stated | Accuracy `VERIFIED` (TI SBVS087M 6.5: ±2 % for 1 to 500 mA and VOUT + 0.5 V ≤ VIN < 6.5 V, TJ −40 to 125 °C); limits `ESTIMATED` |
| `+5V` bus (after U101) | Input minus mux drop | 4.42 V (4.5 V input, 0.93 A, 85 mΩ) | 5.5 V | - | - | `ESTIMATED` (RON 85 mΩ max to TJ 85 °C, TI SLVSEA3F 7.5) |
| Servo rails `+VSERVO1`, `+VSERVO2` | TBD | 6 V | 8.4 V (DEC-110) | TBD | TBD | `VERIFIED` (PWR-011, DEC-110) for min and max |

Known upper bounds for the 3.3 V rails:
- ICM-45686 VDD and VDDIO max 3.6 V recommended, 4 V absolute maximum (IMU rec, `NOT_VERIFIED`).
- IST8310 AVDD and DVDD max 3.6 V recommended and 3.6 V absolute maximum (IST8310 DS V1.2, 4.1 and 4.2, `VERIFIED` via NotebookLM). This is the tightest limit on the 3.3 V rail.
- `ESTIMATED`: 3.3 V nominal leaves 0.3 V (9 %) to the 3.6 V limit for regulator tolerance, load transients and overshoot.
- F100 VDD 2 to 3.6 V (F1 value-line DS Table 8, `VERIFIED`). H743 VDD 1.71 to 3.6 V for LQFP100, which has no PDR_ON pin (DS12110 Rev 11 Table 14 and Table 2 note 5, via NotebookLM, `VERIFIED`, cited); VDD33USB 3.0 to 3.6 V when USB is used (Table 14, `VERIFIED`); the U201 symbol shows no separate VDD33USB pin, so the 3.0 V minimum is taken to apply to `+3V3` (`ASSUMED`).
- ICP-20100 VDD and VDDIO 2.97 to 3.63 V in the 3.3 V range (DS-000416 Rev 1.3 Table 5, source text, `VERIFIED`). ICM-45686 VDD 1.71 to 3.6 V (DS-000489 Rev 1.1 Table 3, source text, `VERIFIED`). BMP581 absolute maximum 4.3 V on VDD and VDDIO (rev 1.13, source text, `VERIFIED`).
- **Margins (`ESTIMATED`, static only):** `+3V3` 3.224 to 3.392 V against 3.0 V (USB) and 3.6 V (IST8310): 0.224 V low and 0.208 V high. `+3V3A` 3.234 to 3.366 V against 2.97 V (ICP-20100) and 3.6 V: 0.264 V low and 0.234 V high. Load steps and start-up overshoot must fit inside these margins; they are not stated by TI for this circuit and are measured at P4-002 and P4-015. The LDO has more than 1 V headroom from the 4.42 V `+5V` minimum at 2.6 mA (dropout 280 mV typ, 500 mV max at 500 mA, SBVS087M 6.5).

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
| 5 V input overvoltage (U101 OV1, OV2; DEC-036, DEC-055) | 5.88 V typ, 5.51 to 6.21 V with 1 % resistors and the 5.1 kΩ bottom resistors (DEC-055; the 14 mV margin above 5.5 V is accepted, OPEN-036 closed); the channel turns off, back on below 5.77 V typ. `+5V` stays below 5.5 V in normal operation (PWR-015) | TI mux 10.2.4.2, equation 6, VREF rising and falling (spec 4.7) | `ESTIMATED` (VREF values `VERIFIED`) |
| 3.3 V buck soft-start (U102) | 10 nF SS/TR (DEC-028): about 5 ms | TI SLVSAJ0F equation 10 (spec 4.7) | `ESTIMATED` |
| 3.3 V buck PG (U102) | Open drain, pulled up by R113 100 kΩ to `+3V3`; local net `3V3_PG` to U103 EN through R115 (DEC-039); reaches no MCU pin and no sheet pin | Saved schematic; spec 4.3, OPEN-026 | `VERIFIED` (as drawn) |
| Servo rail monitor | Read by the F100 through two 3:1 dividers: `+VSERVO1` on PA4, `+VSERVO2` on PA5 (IF-050, DEC-113); about 2.8 V at 8.4 V (`ESTIMATED`); threshold TBD; the PA5 read needs firmware work (P2-005) | px4io-v2 | `TBD` |

## 7. Protection requirements (OPEN-006, OPEN-021, SAF-012 to SAF-014)

All `TBD`. Items to decide:

- [x] 5 V power mux values (P2-020), TI mux, `VERIFIED` unless marked: TPS2121, 80.6 kΩ ILIM gives 1.0 / 1.5 / 2.0 A (DEC-030); OV trip per DEC-036 (section 6); IN and OUT 24 V absolute maximum; input UV 2.65 V typ; 10 nF SS gives about 0.65 ms ramp and about 0.47 A inrush into about 60 µF (`ESTIMATED`, outside TI Table 9-1); fast-trip at about 2.4 × ILM, then off for about 25 ms; thermal shutdown auto-recovers. Priority and switchover: DEC-031 to DEC-034.
- [ ] 5 V input, still open: reverse polarity; D101 SZSMF5.0A TVS: breakdown voltage 6.4 V, fine at the 5.5 V input (human owner, 2026-11-03); hot-plug peak on the PM02D cable (TI mux section 11 suggests a large capacitance near the input for long cables; since 2026-11-03 IN1 has 2 × 10 µF and a 47 µF 10 V tantalum with 0.25 Ω ESR, DEC-037, kept by DEC-058; bench check P4-013).
- [x] USB VBUS and PM02D 5 V OR-ing: TPS2121 power mux (DEC-029), reverse current blocking on both channels (TI mux 9.3.6, `VERIFIED`). Source priority: PM02D first, XCOMP switchover (DEC-031 to DEC-034).
- [ ] 6 V servo bus on the board (DEC-019): board-mount XT30 input, rating against 10 A continuous and 15 A peak `NOT_VERIFIED`; 6 V and servo GND copper; servo GND joined to logic GND at one point away from the sensors; no back-feed from the 6 V bus into the 5 V side (OPEN-021). Drawn (2026-11-19 11:38 save, not decided): CN804 XT30PW-M, C801 and C802 10 µF, C803 47 µF tantalum and D807 SMF7.0A TVS on `+6V` (spec 4.2); D807 clamping voltage against the 7.4 V servo limit `NOT_VERIFIED`. `sch-review` 2026-11-19: C803 is a 10 V solid tantalum (Kyocera AVX TPSB476K010R0250, `Rate` field) at 60 % of its rating at 6 V and 74 % at 7.4 V (`ESTIMATED`) on a hot-plugged 10 A bus, so a surge can short it; use 16 V or more, or a polymer or MLCC part (MAJOR). C801 and C802 are 16 V X7R; the D807 7.0 V standoff (`ASSUMED`) is below the 7.4 V maximum (MINOR) (spec OPEN-021). 13:57 save: D807 is SMF7.5CA (bidirectional, 7.5 V standoff, 12.9 V clamp, CAD Description fields), 0.1 V (1.4 %) above the 7.4 V maximum (`ESTIMATED`); breakdown voltage and leakage `NOT_VERIFIED`. Decided 2026-11-19 (16:03 save): C803 is KEMET T495C686M016ATE250 (named Kyocera AVX before spec 0.63; CAD MFR field KEMET since the 23:17 save, spec OPEN-021), 68 µF 16 V, at 38 % of its rating at 6 V and 46 % at 7.4 V (`ESTIMATED`; DEC-058); D807 is MDD SMF7.5A, unidirectional (DEC-059), breakdown and leakage at 7.4 V `NOT_VERIFIED`. `+6V` bulk on the board is now about 88 µF nominal (`ESTIMATED`). Datasheet checks 2026-11-19 (spec CMP-011, OPEN-021): C803 is a KEMET T495 part, inside the KEMET 50 % voltage guideline at 7.4 V; D807 VRWM 7.5 V, VBR 8.33 V min, IR 50 µA max, VC 12.9 V at 15.5 A; XT30PW-M rated 15 A, 30 A instantaneous (`VERIFIED` via NotebookLM). Bulk since 2026-11-22 (DEC-097, DEC-109; 10:23 save): C801 and C802 68 µF 16 V tantalum (were C803 and C804) and C803 to C806 4 × 22 µF 25 V X7R 1210 (GRM32ER71E226KE15L) for low-ESR bulk, 224 µF nominal; about 204 µF at 6 V with 17 µF per ceramic (human owner value; `ESTIMATED`, no DC-bias loss on the tantalums `ASSUMED`); 7.4 V value `NOT_VERIFIED`. The 10 µF 0805 parts are removed. Since 2026-11-24 (12:47 save; DEC-110 to DEC-113): two rails, `+VSERVO1` and `+VSERVO2`, 6 to 8.4 V; the XT30 is replaced by a 1x3 header per rail, CN804 and CN805, one pin each (rating `NOT_VERIFIED`, accepted); D807 and D808 SMF8.5A (DEC-112); per rail one 68 µF tantalum (C801 or C802, 52.5 % of VR at 8.4 V, accepted) and 2 × 22 µF, 112 µF nominal.
- [ ] Servo rails: overcurrent behavior; the UBEC per rail (DEC-114), its rating and peak duration. Bulk set by DEC-109 (112 µF nominal per rail since DEC-110).
- [x] USB-only power: the bench USB-C port shall supply more than 1 A; brown-out of the external devices on a weaker port is accepted (DEC-038, 2026-11-03). The power mux 1.0 A minimum limit also applies on USB. USB-C CC resistors and the current advertisement are open in P1-006.
- [ ] External 5 V connectors: short-circuit protection per connector or per group.
- [ ] ESD on external connectors and USB (SAF-014).
- [ ] Safe output state on 5 V loss or 6 V fault (SAF-012, SAF-013).

## 8. Findings

| Severity | Ref | Label | Finding | Source |
| -------- | --- | ----- | ------- | ------ |
| MINOR | PWR-012 | `ESTIMATED` | 5 V budget closed on 2026-11-03 (see spec OPEN-006) with the human owner's external load estimates: about 880 mA hot worst case against the 1.0 A minimum mux limit, about 120 mA margin. Barometer currents and the external device models are still estimates; check on the bench (P4-014). | Section 4 |
| MAJOR | IF-030 to IF-037 / UBEC | `ESTIMATED` | All 8 servos can move at once. Stall at 6 V: 8.4 A on `+VSERVO1` and 4.8 A on `+VSERVO2` (13.2 A together); the UBEC per rail is not chosen. Measured tilt servo peak about 0.5 A each while moving, under hand load (OPEN-021). | Section 3; DS3235 and C507 sheets |
| MAJOR (accepted, DEC-113) | CN804, CN805 / servo rails | `NOT_VERIFIED` | Each rail enters through one TSW-101 header pin: 8.4 A on `+VSERVO1` and 4.8 A on `+VSERVO2` at 6 V stall (section 3). Pin rating not checked. | DEC-111, DEC-113 |
| MAJOR (accepted, DEC-113) | IF-034 to IF-037 / `+VSERVO1` | `VERIFIED` | DS3235 is rated 5 to 7.4 V; the rail can reach 8.4 V (DEC-110). | DS3235 sheet via NotebookLM; DEC-113 |
| MINOR (accepted, DEC-113) | C801, C802 / servo rails | `ESTIMATED` | 16 V tantalum at 52.5 % of VR at 8.4 V, above the KEMET 50 % guideline (spec CMP-011). | DEC-113 |
| MINOR | DEC-030 / 5 V | `VERIFIED` | The power mux limit with 80.6 kΩ is 1.0 to 2.0 A (1.5 A typ). The board plus all external 5 V loads must fit under 1.0 A for a worst-case part, with the load currents still unknown. | Section 4; TI mux |
| MINOR | IST8310 / 3.3 V | `VERIFIED` | IST8310 absolute maximum supply is 3.6 V, so the 3.3 V rail must never overshoot by more than 0.3 V (9 %), including start-up and load steps. | IST8310 DS V1.2, 4.1 |
| INFO | IF-022 / 5 V | `VERIFIED` (team answer) | USB VBUS powers the board on the bench. It joins the PM02D 5 V through the power mux IN2 (DEC-029). | Section 2 |
| MINOR | IF-022 / 5 V | `ESTIMATED` | USB feeds all external 5 V ports (human owner). On a 500 mA port the board at its hot maximum plus the TF-Luna peak already uses the whole port. Accepted: USB is a bench supply, the bench USB-C port shall supply more than 1 A, and brown-out on a weaker port is accepted (DEC-038, 2026-11-03). | Section 4 |

## 9. Open inputs

- [x] GPS about 100 mA (human owner estimate, 2026-11-03). SiK radio 100 mA transmit (Holybro, `VERIFIED`; replaces ELRS 100 mA, DEC-053). Model still from the team (P0-022). Telemetry 2: no device planned.
- [ ] FS-iA6B supply current (50 mA placeholder, OPEN-034).
- [ ] Servo current under load and measured stall current (team bench test, P0-022); tilt servo peak about 0.5 A while moving under hand load (human owner, 2026-11-24); datasheet stall values are in section 3. Servo power passes through the board (DEC-019), so it also sizes the board input and bus.
- [x] 3.3 V_IMU rail structure: `+3V3A` from its own LDO, sensor VDD pins (DEC-043, 2026-11-12; was IMUs only, DEC-025). LDO TPS73533DRBR (DEC-027, 2026-10-31).
- [x] USB VBUS as a board power source: yes, on the bench (team). It feeds all external 5 V ports (human owner, 2026-10-24).
- [x] TPS2121 values from TI: done 2026-11-01 (section 7, TI mux).
- [x] Power mux priority and switchover: PM02D first, XCOMP with R105 fitted, 4.44 V worst-case switch point with 1 % resistors (DEC-031 to DEC-034; OPEN-024 closed).
- [x] XT30 current rating: XT30 removed; header inputs CN804 and CN805 accepted without a rating check (DEC-111, DEC-113).
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
- DS3235 servo: DS SERVO sheet for DS3235 / DS3235-180 / DS3235-270, no revision or date, copy at https://hajim.rochester.edu/me/sites/kelley/me240/DS3235-270_datasheet.pdf, NotebookLM notebook `Servos` (added 2026-11-19 with the human owner's approval; not opened by Claude)
- Kingmax C507 servo: Kingmax spec sheet, French translation, no version, https://www.intermodel.fr/fichiers/C507KINGMAX.pdf, NotebookLM notebook `Servos` (added 2026-11-19 with the human owner's approval; not opened by Claude)
- Requirements: `AO-HORIZON_SPEC_EN.md` sections on power, safety and interfaces
- TI TPS6214x SLVSAJ0F Rev F (NotebookLM notebook `TPS6214x 3-17V 2A Step-down`), TI TPS735 SBVS087M (notebook `TPS735`), TI TPS212x SLVSEA3F (notebook `TPS212x ...`), ST DS12110 Rev 11 (notebook `STM32H743VI`): NotebookLM answers with cited text, 2026-11-21.

## 11. Thermal margin (spec 4.7, P2-010)

Method: `TJ = TA + P × RθJA`, with the JEDEC RθJA from each datasheet (`ESTIMATED`; the real board, copper and enclosure change it). TA 32 °C is the field ambient near Bangkok (ENV-001, team model); the fuselage gets hotter in the sun and is not measured (`NOT_VERIFIED`). The 85 °C column is the part rating corner (DEC-020).

| Part | Dissipation | RθJA | Rise | TJ at TA 32 °C | TJ at TA 85 °C | TJ limit | Source | Label |
| ---- | ----------- | ---- | ---- | -------------- | -------------- | -------- | ------ | ----- |
| U201 STM32H743, typical | 0.73 W (3.3 V × 220 mA typ at TJ 25 °C, Table 120 condition: 480 MHz, all peripherals on) | 45 °C/W (LQFP100) | 33 °C | about 65 °C | about 118 °C | 125 °C (suffix 6) | DS12110 Rev 11 Table 120, Table 222, Table 14 | `ESTIMATED` from `VERIFIED` values |
| U201 STM32H743, worst-case part | 1.44 W at TJ 85 °C (436 mA max), 1.80 W at TJ 105 °C (546 mA max) | 45 °C/W | 65 °C, 81 °C | Not settled: TJ 85 °C needs TA ≤ 20 °C, TJ 105 °C needs TA ≤ 24 °C | Over the limit | 125 °C | Same | `ESTIMATED`; see finding below |
| U301 STM32F100 | 0.05 W (15.4 mA max at 24 MHz, all peripherals on) | 55 °C/W (LQFP48) | 3 °C | about 35 °C | about 88 °C | 105 °C (suffix 6) | DocID16455 Rev 9 Table 12, Table 53, Table 8 | `ESTIMATED` |
| U102 TPS62142 buck | 0.14 W typ, 0.33 W hot case (output 0.81 W and 1.88 W at an assumed 85 % efficiency, all loss in the IC as an upper bound) | 45 °C/W (RGT) | 6 °C, 15 °C | under 50 °C | about 100 °C | 125 °C | SLVSAJ0F 7.3, 7.4; efficiency `ASSUMED` (figures only, no number in the text) | `ESTIMATED` |
| U103 TPS73533 LDO | 6 mW ((5.5 − 3.3) V × 2.6 mA) | 52.2 °C/W (DRB) | 0.3 °C | about 32 °C | about 85 °C | 125 °C operating | SBVS087M 6.4, 6.5 | `ESTIMATED` |
| U101 TPS2121 mux | 0.07 W at 0.93 A (85 mΩ), 0.19 W at 1.5 A, 0.40 W at the 2.0 A limit maximum (100 mΩ) | 72.2 °C/W | 5, 14, 29 °C | under 61 °C | up to 114 °C at 2.0 A | 125 °C (`ASSUMED`, the TJ row was not read) | SLVSEA3F 7.4, 7.5 (the thermal table names the column "RNW (PKG FAM) 11 PINS"; the board uses RUX, `ASSUMED` the same) | `ESTIMATED` |
| TVS and ESD parts (D101, D807, D808, ESD arrays) | None in normal operation | - | - | - | - | - | - | `ASSUMED` |
| Servo rail copper and inputs CN804, CN805 | Per rail at 6 V stall: 8.4 A (`+VSERVO1`), 4.8 A (`+VSERVO2`) | Set by copper | - | - | - | - | OPEN-021, P3-003, P3-010 | `NOT_VERIFIED` (layout) |

Findings:
- MINOR | U201 | `ESTIMATED` | At the DS12110 Table 120 maximum currents (480 MHz, all peripherals on, worst-case part), the JEDEC RθJA gives no stable junction temperature below 105 °C at a 32 °C ambient. The typical part settles near 65 °C. PX4 does not turn on every peripheral, so the real current is lower (`ASSUMED`). Measure the H743 current with PX4 running and the board temperature at P4-002; the human owner decides whether more copper under U201 or a lower clock is needed.
- INFO | U102, U103, U101, U301 | `ESTIMATED` | Each stays at least 10 °C under its TJ limit at the 85 °C part rating corner, except U101 at the 2.0 A limit maximum (114 °C against 125 °C, `ASSUMED`). At the 0.93 A hot load it is under 61 °C at 32 °C ambient.
