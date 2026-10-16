# AeroOptix-Horizon: IMU Selection Summary

**Revision:** 0.2
**Updated:** 2026-10-16
**Status:** Working summary. No part is approved. Not a verification record.
**Requirement refs:** SEN-001, CMP-003 (spec). Checklist task: P0-008.
**Decision owner:** Human engineer

One-page summary of the IMU selection. It is the single record for specs, price and stock. Add a new part number as a new column or row.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet was read. TDK values are product-page values.

## 1. Decision

| Item | Value |
| ---- | ----- |
| Need | 2 × SPI IMU with CS, DRDY and reset (SEN-001) |
| Pairing chosen | `PENDING`, human to decide |
| Part chosen | `PENDING`, human to decide |
| Decision date | `PENDING` |
| Decision record ID | `PENDING` (no DEC number yet) |

Assumptions: `ASSUMED` the 3.3 V_IMU rail supplies the IMUs (candidate only in the spec). `ASSUMED` no temperature or vibration filter, because ENV-001 and ENV-003 are TBD.

### Pairing options

| Option | Parts | Gain | Cost |
| ------ | ----- | ---- | ---- |
| A | 2 × ICM-42688-P | One footprint, one driver, fewest pins | Same errata and failure modes on both |
| B | ICM-42688-P + BMI088 | Vendor and failure-mode diversity | More pins (BMI088 needs 2 CS), second footprint, BMI088 lifecycle risk |
| C | ICM-42688-P + ICM-45686 | Newer generation next to the established part, same footprint (claimed) | Footprint match `NOT_VERIFIED`, sourcing is weak now |

## 2. Candidate assessment

| MPN | Assessment |
| --- | ---------- |
| **ICM-42688-P** | Best engineering fit so far. In production (TDK), SPI, lowest noise on the list, PX4 driver present. Weak point: DigiKey stock 0 with 45-week lead time. |
| **ICM-45686** | Newer generation (BalancedGyro per TDK). Noise higher than ICM-42688-P on paper. PX4 driver present. SPI and supply range not on the TDK page. DigiKey stock 0. |
| **ICM-45605** | Same noise and package as ICM-45686 on TDK pages, SPI listed. No PX4 driver found. DigiKey stock 0. |
| **ICM-40609-D** | Older drone part. Noisier, 3 × 3 mm package (different footprint). In stock at DigiKey. Not recommended unless a specific reason appears. |
| **BMI088** | Vibration suppression stated by Bosch (`NOT_VERIFIED`). Needs 2 CS and 2 interrupt lines. Lifecycle unclear (one cached LCSC page says NRND). DigiKey stock 0. |

The deciding rows for SEN-001 are: PX4 driver, supply range against the 3.3 V_IMU rail, CS count (pin budget), footprint, noise, and sourcing.

## 3. Spec table

Full table. Sources: **TDK** = TDK product page. **Bosch** = Bosch product page or flyer excerpt from search. **PX4** = PX4-Autopilot repo, `src/drivers/imu`, main branch. **3P** = third-party summary. **BF** = Betaflight issue 14249 (community). No datasheet was read, so TDK values are product-page values, not datasheet limits. No row holds an absolute maximum rating.

| Parameter | ICM-42688-P | BMI088 | ICM-45686 | ICM-45605 | ICM-40609-D | (new P/N) |
| --------- | ----------- | ------ | --------- | --------- | ----------- | --------- |
| Manufacturer | TDK InvenSense | Bosch Sensortec | TDK InvenSense | TDK InvenSense | TDK InvenSense | |
| Product status | Production (TDK) `VERIFIED` | `NOT_VERIFIED` (Bosch page shows none; one LCSC cache says NRND) | Production (TDK) `VERIFIED` | Production (TDK) `VERIFIED` | Production (TDK) `VERIFIED` | |
| Axes | 6 | 6 (separate gyro and accel dies) | 6 | 6 | 6 | |
| Host interface | 24 MHz SPI (TDK) `VERIFIED` | SPI, I2C `NOT_VERIFIED` | `NOT_VERIFIED` on page | I3C, I2C, SPI (TDK) `VERIFIED` | `NOT_VERIFIED` on page; SPI, I2C per 3P | |
| CS lines (assumed) | 1 `ASSUMED` | 2 `ASSUMED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| Supply VDD (recommended) | `NOT_VERIFIED` | 2.4 to 3.6 V (Bosch) `NOT_VERIFIED` vs datasheet | `NOT_VERIFIED` | `NOT_VERIFIED` | 1.71 to 3.6 V (3P) `NOT_VERIFIED` | |
| I/O supply VDDIO (recommended) | `NOT_VERIFIED` | 1.2 to 3.6 V (Bosch) `NOT_VERIFIED` vs datasheet | `NOT_VERIFIED` | `NOT_VERIFIED` | 1.71 to 3.6 V (3P) `NOT_VERIFIED` | |
| Operating temperature | `NOT_VERIFIED` | -40 to +85 °C (Bosch) `NOT_VERIFIED` vs datasheet | `NOT_VERIFIED` | `NOT_VERIFIED` | -40 to +85 °C (3P) `NOT_VERIFIED` | |
| Gyro noise density | 2.8 mdps/√Hz (TDK) `VERIFIED` | `NOT_VERIFIED` | 3.8 mdps/√Hz (TDK) `VERIFIED` | 3.8 mdps/√Hz (TDK) `VERIFIED` | 4.5 mdps/√Hz (TDK) `VERIFIED` | |
| Accel noise density | 70 µg/√Hz (TDK) `VERIFIED` | `NOT_VERIFIED` | 70 µg/√Hz (TDK) `VERIFIED` | 70 µg/√Hz (TDK) `VERIFIED` | 100 µg/√Hz (TDK) `VERIFIED` | |
| Gyro full-scale | `NOT_VERIFIED` | `NOT_VERIFIED` | up to ±4000 dps (TDK) `VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| Accel full-scale | `NOT_VERIFIED` | up to ±24 g (Bosch) `NOT_VERIFIED` vs datasheet | up to ±32 g (TDK) `VERIFIED` | `NOT_VERIFIED` | up to ±32 g (TDK) `VERIFIED` | |
| Max output data rate | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | 32 kHz (TDK) `VERIFIED` | |
| Current, 6-axis | `NOT_VERIFIED` | 5.15 mA typ (Bosch) `NOT_VERIFIED` vs datasheet | `NOT_VERIFIED` | 0.42 mA low-noise, 0.22 mA low-power (TDK) `VERIFIED` | 0.77 mA (TDK) `VERIFIED` | |
| Temperature stability | `NOT_VERIFIED` | `NOT_VERIFIED` | gyro ±0.005 °/s/°C, accel ±0.15 mg/°C (TDK) `VERIFIED` | gyro ±0.01 °/s/°C, accel ±0.15 mg/°C (TDK) `VERIFIED` | gyro offset ±10 mdps/°C (search result of TDK page) `NOT_VERIFIED` | |
| Package, size | LGA-14, 2.5 × 3.0 × 0.91 mm (TDK) `VERIFIED` | LGA-16, 3 × 4.5 × 0.95 mm (Bosch) `NOT_VERIFIED` vs datasheet | 2.5 × 3.0 × 0.81 mm (TDK) `VERIFIED` | 2.5 × 3.0 × 0.81 mm (TDK) `VERIFIED` | 3.0 × 3.0 × 0.91 mm (TDK); 24-pin LGA per DigiKey listing `NOT_VERIFIED` | |
| Footprint same as ICM-42688-P | n/a | No (larger) | Claimed (BF) `NOT_VERIFIED` | Claimed (BF) `NOT_VERIFIED` | No (3 × 3 mm) | |
| Vibration feature | `NOT_VERIFIED` | Vibration suppression stated (Bosch flyer) `NOT_VERIFIED` | BalancedGyro stated (TDK); no vibration spec on page | BalancedGyro stated (TDK); no vibration spec on page | none on TDK page | |
| PX4 driver in main | `invensense/icm42688p` (PX4) `VERIFIED` | `bosch/bmi088`, `bosch/bmi088_i2c` (PX4) `VERIFIED` | `invensense/icm45686` (PX4) `VERIFIED` | `NOT_VERIFIED` (no 45605 directory; source not read) | `invensense/icm40609d` (PX4) `VERIFIED` | |

## 4. Price and stock summary

Checked 2026-10-16. DigiKey .com and LCSC, USD, qty 1 and 10. Mouser excluded on request. Not a quote.

| Detail | ICM-42688-P | BMI088 | ICM-45686 | ICM-45605 | ICM-40609-D | (new P/N) |
| ------ | ----------- | ------ | --------- | --------- | ----------- | --------- |
| DigiKey SKU (cut tape) | 1428-ICM-42688-PCT-ND | 828-1082-1-ND | 1428-ICM-45686CT-ND | 1428-ICM-45605CT-ND | 1428-ICM-40609-DCT-ND | |
| DigiKey stock | 0 (backorder) | 0 | 0 (backorder) | 0 (backorder) | 18,395 | |
| DigiKey qty 1 | $4.86 | $5.92 | $5.26 | $5.26 | $5.87 (Digi-Reel $5.54) | |
| DigiKey qty 10 | $4.17 | $5.10 | $4.53 | $4.53 | $5.06 (Digi-Reel $4.77) | |
| DigiKey lead time | 45 weeks | 16 weeks | 45 weeks | 45 weeks | 45 weeks (manufacturer standard) | |
| LCSC SKU | C1850418 | C194919 | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| LCSC stock | 1,875 | 2,107 | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| LCSC qty 1 | $21.00 | $6.83 | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| LCSC qty 10 | $18.74 | $6.07 | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |

Sourcing notes:
- Only ICM-40609-D is in stock at DigiKey. The other four are at 0 there.
- Independent brokers (for example Win Source) showed stock for some parts in aggregator pages. They are not authorized distributors, so traceability is `NOT_VERIFIED`.
- JLCPCB: ICM-42688-P (C1850418) and BMI088 (C194919) were seen as Extended parts. Stock and assembly eligibility are `NOT_VERIFIED`. The other three were not found.

## 5. Open checks before commitment

- [ ] Confirm VDD, VDDIO, recommended operating and absolute maximum tables from each datasheet (user-supplied values, or NotebookLM with your approval naming files and notebook).
- [ ] Confirm lifecycle status and errata. BMI088 lifecycle is unresolved.
- [ ] Read the pin tables for CS, INT/DRDY and reset, and compare land patterns for ICM-45686 and ICM-45605 against ICM-42688-P.
- [ ] Check whether a PX4 driver covers ICM-45605.
- [ ] Settle the LCSC ICM-42688-P price conflict and check live LCSC, JLCPCB and DigiKey stock.
- [ ] Check 3.3 V_IMU rail noise and current budget (P0-017).
- [ ] Human decides the pairing and records a DEC entry.

## 6. Sources

- TDK: https://invensense.tdk.com/products/motion-tracking/6-axis/ (pages for ICM-42688-P, ICM-45686, ICM-45605, ICM-40609-D)
- Bosch BMI088: https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi088/
- PX4 drivers: https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/imu
- Betaflight issue 14249: https://github.com/betaflight/betaflight/issues/14249
- DigiKey: https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/10824934 (also ICM-45686 `24374985`, ICM-45605 `24883424`, ICM-40609-D `19200630`, BMI088 `8634936` under the same path pattern)
- LCSC: https://www.lcsc.com/product-detail/C1850418.html (ICM-42688-P), https://www.lcsc.com/product-detail/C194919.html (BMI088)
