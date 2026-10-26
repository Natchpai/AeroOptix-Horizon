# AeroOptix-Horizon: IMU Selection Summary

**Revision:** 0.9
**Updated:** 2026-10-26
**Status:** Part confirmed by the team (DEC-008). Datasheet values and implementation are not verified. Not a verification record.
**Requirement refs:** SEN-001, CMP-003 (spec). Decisions: DEC-008, DEC-009, DEC-025. Checklist task: P0-008.
**Decision owner:** Team

Single record for the IMU part, its key data, sourcing, and the candidates that were compared.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`.

Source keys used below:
- **DS**: TDK datasheet DS-000489 Rev 1.1 (11/25/2023) for ICM-45686. Values were extracted by the external model agy (user-approved, 2026-10-18). Claude and a human have not checked them, so every DS value is `NOT_VERIFIED`, except the Table 10 pin list and the section 10.2 package table. Those were checked through NotebookLM on 2026-10-19 (notebook ICM-45686, source `24bd0600`), with the text confirmed in the source fulltext.
- **TDK**: TDK product page. Product-page values, not datasheet limits.
- **LCSC**: LCSC product page, fetched 2026-10-18.
- **PX4**: PX4-Autopilot repo, `src/drivers/imu`, main branch.
- **Bosch**, **3P** (third-party summary), **BF** (Betaflight issue 14249, community): used only in the candidate comparison.

## 1. Decision

| Item | Value |
| ---- | ----- |
| Need | 2 × SPI IMU with CS and DRDY (SEN-001) |
| Part chosen | 2 × TDK InvenSense ICM-45686 (DEC-008, 2026-10-18) |
| Reset method | Software reset only, no hardware reset line (DEC-009, 2026-10-18) |
| Gain | One footprint, one driver (PX4 `invensense/icm45686`), newer generation |
| Cost | Same errata and failure modes on both IMUs. No vendor diversity. |

Supply: the `+3V3A` rail (3.3 V_IMU) feeds both IMUs on VDD and VDDIO, and nothing else (DEC-025, 2026-10-26). Assumptions: `ASSUMED` no temperature or vibration filter, because ENV-001 and ENV-003 are TBD.

## 2. ICM-45686 key data

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | Production | TDK | `VERIFIED` |
| Package | LGA-14, 2.5 × 3.0 × 0.81 mm, 0.5 mm pitch | TDK; DS §10.2 | `VERIFIED` (size, TDK; pitch, DS §10.2 via NotebookLM) |
| Land pattern | Not in the datasheet. TDK app note AN-000393 is referenced. | DS §10.2, §22 | `NOT_VERIFIED` |
| VDD (recommended) | 1.71 / 1.8 / 3.6 V min/typ/max | DS Table 3 | `NOT_VERIFIED` |
| VDDIO (recommended) | 1.08 / 1.8 / 3.6 V; 1.1 V min with I3C | DS Table 3 | `NOT_VERIFIED` |
| Operating temperature | -40 to +85 °C | DS Tables 3, 9 | `NOT_VERIFIED` |
| Absolute maximum, supplies | VDD, VDDIO: -0.5 to +4 V | DS Table 9 | `NOT_VERIFIED` |
| Absolute maximum, inputs | FSYNC, SCL, SDA: -0.5 V to VDDIO + 0.5 V. No rating stated for other inputs. | DS Table 9 | `NOT_VERIFIED` |
| Absolute maximum, other | 20,000 g for 0.2 ms unpowered; ESD 2 kV HBM, 500 V CDM; storage -40 to +125 °C | DS Table 9 | `NOT_VERIFIED` |
| Host interface | SPI 3- or 4-wire, max 24 MHz at VDDIO ≥ 1.71 V (20 MHz below), mode 0/3 by default. I2C and I3C share the pins. | DS §4.10, Table 7, §9.5 | `NOT_VERIFIED` |
| CS lines | 1 (pin 12, AP_CS) | DS Table 10 | `VERIFIED` (via NotebookLM) |
| Interrupts | INT1 pin 4 (push-pull or open drain); INT2/FSYNC/CLKIN pin 9 | DS Table 10 | `VERIFIED` (via NotebookLM) |
| Hardware reset pin | None: no reset pin in the 14-pin Table 10. Software reset `SOFT_RST` in `REG_MISC2`. | DS Table 10; DS p.109 | `VERIFIED` (no pin, via NotebookLM); `SOFT_RST` `NOT_VERIFIED` |
| Gyro full-scale | ±15.625 to ±4000 dps (9 settings) | TDK (±4000); DS Table 1 | `VERIFIED` (max, TDK); `NOT_VERIFIED` (settings) |
| Accel full-scale | ±2 to ±32 g (5 settings) | TDK (±32); DS Table 2 | `VERIFIED` (max, TDK); `NOT_VERIFIED` (settings) |
| Max output data rate | 6400 Hz gyro and accel, low-noise mode | DS Tables 1, 2 | `NOT_VERIFIED` |
| Gyro noise density | 3.8 mdps/√Hz | TDK | `VERIFIED` |
| Accel noise density | 70 µg/√Hz | TDK | `VERIFIED` |
| Temperature stability | gyro ±0.005 °/s/°C, accel ±0.15 mg/°C | TDK | `VERIFIED` |
| Current, 6-axis low-noise | 420 µA typ at 1600 Hz, 440 µA typ at 6400 Hz | DS Table 3 | `NOT_VERIFIED` |
| Vibration feature | BalancedGyro stated; no vibration spec on the page | TDK | `VERIFIED` (claim only) |
| PX4 driver | `invensense/icm45686` | PX4 | `VERIFIED` |

## 3. Schematic notes

All from DS via agy, so `NOT_VERIFIED` until the human check in section 5.

- **Pins used per IMU:** pin 12 CS, pin 13 SCLK, pin 14 SDI, pin 1 SDO, pin 4 INT1. Pin 9 INT2/FSYNC/CLKIN is optional; if unused, leave it NC or tie it to VDDIO. The team does not use pin 9 (no CLKIN, no INT2; pinmap review Q16, 2026-10-24).
- **Reserved pins 2, 3, 7, 10, 11:** NC, VDDIO or GND. The internal pull-up setting (`pe_trim`) must match the choice, so firmware needs to know it.
- **Bypass:** 0.1 µF X7R ±10% on VDD and on VDDIO, one each (DS §4.5 Table 11). Use larger capacitors if supply ripple exceeds 50 mV pk-pk.
- **Reset:** no reset line to route (DEC-009).
- **3.3 V supply margin:** `ESTIMATED` 3.3 V is inside the 1.71 to 3.6 V VDD and 1.08 to 3.6 V VDDIO ranges, with 0.7 V margin to the 4 V absolute maximum. Rail overshoot is not known yet.
- **Inputs without a stated maximum** (CS, SCLK, CLKIN): keep them in the VDDIO domain.
- **Datasheet typos noted by agy:** C1 is drawn as "0.1 mF" in the application figures but listed as 0.1 µF in Table 11. Section 1.2 says 8 gyro and 4 accel full-scale settings, while the tables list 9 and 5.

## 4. Sourcing

DigiKey checked 2026-10-16; LCSC checked 2026-10-18 from a page fetch. USD. Not a quote. Stock and price are `NOT_VERIFIED` until spot-checked on the live page.

| Detail | DigiKey | LCSC |
| ------ | ------- | ---- |
| SKU | 1428-ICM-45686CT-ND (cut tape) | C22459454 |
| Stock | 0 (backorder), 45-week lead time | 5,945 |
| Qty 1 | $5.26 | $11.84 |
| Qty 10 | $4.53 | $10.09 |
| Other breaks | | 30+ $9.02, 100+ $8.12; MOQ 1; full reel 5000 |

- LCSC price is about 2.25× DigiKey at qty 1. Two IMUs per board.
- The LCSC page does not list supply voltage, temperature or lifecycle. Its features text is marked "AI Translation".
- JLCPCB assembly eligibility of C22459454 is not checked.
- Independent brokers showed stock for some TDK parts on aggregator pages. They are not authorized distributors, so traceability is `NOT_VERIFIED`.

## 5. Open checks

- [ ] Human confirms the DS values in sections 2 and 3 against DS-000489 Rev 1.1: Table 3, Table 9, Table 10, §4.5, §10.2.
- [ ] Get the land pattern from TDK AN-000393 and compare it with the library footprint `0_Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm` (a stock Bosch land copied on 2026-10-19; OPEN-013, P2-012). Its pad count, pitch and pad-row spans match DS §10.2; pad size and pin 1 corner are not checked. The BF claim of a footprint shared with ICM-42688-P is `NOT_VERIFIED`.
- [ ] Decide how to tie reserved pins 2, 3, 7, 10, 11 and record the matching `pe_trim` setting for firmware.
- [ ] Confirm errata for ICM-45686.
- [ ] Secure a source for 2 × ICM-45686 per board, and check JLCPCB eligibility.
- [ ] Check 3.3 V_IMU (`+3V3A`) rail noise and current budget (P0-017).
- [ ] Check the ICM-45686 VDDIO range and SPI input levels with VDDIO on `+3V3A` and the H743 on `+3V3`, and the power-up order of the two rails (OPEN-011).

Closed:
- [x] Team chose the part and recorded DEC-008 (2026-10-18).
- [x] Reset method decided: software reset, DEC-009 (2026-10-18).
- [x] Datasheet read for SPI, CS count, supply, absolute maximum and pinout (agy, 2026-10-18).
- [x] Library symbol `0_Sensor_Motion:ICM-45686` pin map checked against DS Table 10 through NotebookLM (2026-10-19).

## Appendix A. Candidates compared before DEC-008

Kept as the selection record. These values were not updated after the decision. ICM-45686 data is in section 2.

### Pairing options

| Option | Parts | Gain | Cost |
| ------ | ----- | ---- | ---- |
| A | 2 × ICM-42688-P | One footprint, one driver, fewest pins | Same errata and failure modes on both |
| B | ICM-42688-P + BMI088 | Vendor and failure-mode diversity | More pins (BMI088 needs 2 CS), second footprint, BMI088 lifecycle risk |
| C | ICM-42688-P + ICM-45686 | Newer generation next to the established part, same footprint (claimed) | Footprint match `NOT_VERIFIED`, weak sourcing |
| **D (chosen)** | 2 × ICM-45686 | One footprint, one driver, newer generation | Same errata and failure modes on both, weak DigiKey sourcing |

### Candidate assessment

| MPN | Assessment |
| --- | ---------- |
| ICM-42688-P | In production (TDK), SPI, lowest noise on the list, PX4 driver present. DigiKey stock 0 with 45-week lead time. |
| ICM-45686 | Chosen. Newer generation (BalancedGyro per TDK). Gyro noise higher than ICM-42688-P on paper. PX4 driver present. |
| ICM-45605 | Same noise and package as ICM-45686 on TDK pages, SPI listed. No PX4 driver found. DigiKey stock 0. |
| ICM-40609-D | Older drone part. Noisier, 3 × 3 mm package (different footprint). In stock at DigiKey. |
| BMI088 | Vibration suppression stated by Bosch (`NOT_VERIFIED`). Needs 2 CS and 2 interrupt lines. Lifecycle unclear (one cached LCSC page says NRND). DigiKey stock 0. |

### Spec comparison (product pages, no datasheets)

| Parameter | ICM-42688-P | BMI088 | ICM-45605 | ICM-40609-D |
| --------- | ----------- | ------ | --------- | ----------- |
| Manufacturer | TDK InvenSense | Bosch Sensortec | TDK InvenSense | TDK InvenSense |
| Product status | Production (TDK) `VERIFIED` | `NOT_VERIFIED` (Bosch page shows none; one LCSC cache says NRND) | Production (TDK) `VERIFIED` | Production (TDK) `VERIFIED` |
| Axes | 6 | 6 (separate gyro and accel dies) | 6 | 6 |
| Host interface | 24 MHz SPI (TDK) `VERIFIED` | SPI, I2C `NOT_VERIFIED` | I3C, I2C, SPI (TDK) `VERIFIED` | SPI, I2C per 3P `NOT_VERIFIED` |
| CS lines | 1 `ASSUMED` | 2 `ASSUMED` | `NOT_VERIFIED` | `NOT_VERIFIED` |
| Supply VDD | `NOT_VERIFIED` | 2.4 to 3.6 V (Bosch) `NOT_VERIFIED` | `NOT_VERIFIED` | 1.71 to 3.6 V (3P) `NOT_VERIFIED` |
| Supply VDDIO | `NOT_VERIFIED` | 1.2 to 3.6 V (Bosch) `NOT_VERIFIED` | `NOT_VERIFIED` | 1.71 to 3.6 V (3P) `NOT_VERIFIED` |
| Operating temperature | `NOT_VERIFIED` | -40 to +85 °C (Bosch) `NOT_VERIFIED` | `NOT_VERIFIED` | -40 to +85 °C (3P) `NOT_VERIFIED` |
| Gyro noise density | 2.8 mdps/√Hz (TDK) `VERIFIED` | `NOT_VERIFIED` | 3.8 mdps/√Hz (TDK) `VERIFIED` | 4.5 mdps/√Hz (TDK) `VERIFIED` |
| Accel noise density | 70 µg/√Hz (TDK) `VERIFIED` | `NOT_VERIFIED` | 70 µg/√Hz (TDK) `VERIFIED` | 100 µg/√Hz (TDK) `VERIFIED` |
| Accel full-scale | `NOT_VERIFIED` | up to ±24 g (Bosch) `NOT_VERIFIED` | `NOT_VERIFIED` | up to ±32 g (TDK) `VERIFIED` |
| Max output data rate | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | 32 kHz (TDK) `VERIFIED` |
| Current, 6-axis | `NOT_VERIFIED` | 5.15 mA typ (Bosch) `NOT_VERIFIED` | 0.42 mA low-noise, 0.22 mA low-power (TDK) `VERIFIED` | 0.77 mA (TDK) `VERIFIED` |
| Temperature stability | `NOT_VERIFIED` | `NOT_VERIFIED` | gyro ±0.01 °/s/°C, accel ±0.15 mg/°C (TDK) `VERIFIED` | gyro offset ±10 mdps/°C (search result) `NOT_VERIFIED` |
| Package | LGA-14, 2.5 × 3.0 × 0.91 mm (TDK) `VERIFIED` | LGA-16, 3 × 4.5 × 0.95 mm (Bosch) `NOT_VERIFIED` | 2.5 × 3.0 × 0.81 mm (TDK) `VERIFIED` | 3.0 × 3.0 × 0.91 mm (TDK); 24-pin LGA per DigiKey `NOT_VERIFIED` |
| Footprint same as ICM-42688-P | n/a | No (larger) | Claimed (BF) `NOT_VERIFIED` | No (3 × 3 mm) |
| Vibration feature | `NOT_VERIFIED` | Vibration suppression stated (Bosch flyer) `NOT_VERIFIED` | BalancedGyro stated (TDK) | none on TDK page |
| PX4 driver in main | `invensense/icm42688p` `VERIFIED` | `bosch/bmi088`, `bosch/bmi088_i2c` `VERIFIED` | `NOT_VERIFIED` (no 45605 directory) | `invensense/icm40609d` `VERIFIED` |

### Price and stock (checked 2026-10-16, not a quote)

| Detail | ICM-42688-P | BMI088 | ICM-45605 | ICM-40609-D |
| ------ | ----------- | ------ | --------- | ----------- |
| DigiKey SKU (cut tape) | 1428-ICM-42688-PCT-ND | 828-1082-1-ND | 1428-ICM-45605CT-ND | 1428-ICM-40609-DCT-ND |
| DigiKey stock | 0 (backorder) | 0 | 0 (backorder) | 18,395 |
| DigiKey qty 1 | $4.86 | $5.92 | $5.26 | $5.87 (Digi-Reel $5.54) |
| DigiKey qty 10 | $4.17 | $5.10 | $4.53 | $5.06 (Digi-Reel $4.77) |
| DigiKey lead time | 45 weeks | 16 weeks | 45 weeks | 45 weeks (manufacturer standard) |
| LCSC SKU | C1850418 | C194919 | `NOT_VERIFIED` | `NOT_VERIFIED` |
| LCSC stock | 1,875 | 2,107 | `NOT_VERIFIED` | `NOT_VERIFIED` |
| LCSC qty 1 | $21.00 (price conflict, unresolved) | $6.83 | `NOT_VERIFIED` | `NOT_VERIFIED` |
| LCSC qty 10 | $18.74 | $6.07 | `NOT_VERIFIED` | `NOT_VERIFIED` |

JLCPCB: ICM-42688-P (C1850418) and BMI088 (C194919) were seen as Extended parts; stock and assembly eligibility `NOT_VERIFIED`. ICM-45605 and ICM-40609-D were not found.

## 6. Sources

- ICM-45686 datasheet: TDK DS-000489 Rev 1.1, 11/25/2023, 199 pages, downloaded from LCSC (https://www.lcsc.com/datasheet/C22459454.pdf). Read by agy on 2026-10-18, not by Claude.
- TDK: https://invensense.tdk.com/products/motion-tracking/6-axis/ (pages for ICM-42688-P, ICM-45686, ICM-45605, ICM-40609-D)
- PX4 drivers: https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/imu
- DigiKey: https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/10824934 (also ICM-45686 `24374985`, ICM-45605 `24883424`, ICM-40609-D `19200630`, BMI088 `8634936` under the same path pattern)
- LCSC: https://www.lcsc.com/product-detail/C22459454.html (ICM-45686), https://www.lcsc.com/product-detail/C1850418.html (ICM-42688-P), https://www.lcsc.com/product-detail/C194919.html (BMI088)
- Bosch BMI088: https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi088/
- Betaflight issue 14249: https://github.com/betaflight/betaflight/issues/14249
