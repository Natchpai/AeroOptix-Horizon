# AeroOptix-Horizon: Barometer and Magnetometer Selection Summary

**Revision:** 0.2
**Updated:** 2026-10-18
**Status:** Parts confirmed by the team (DEC-010, DEC-011). Lifecycle and availability risks are open. Datasheet values and implementation are not verified. Not a verification record.
**Requirement refs:** SEN-002, SEN-003, CMP-004, CMP-005 (spec). Checklist tasks: P0-009, P0-010.
**Decision owner:** Team

Single record for the barometer and magnetometer parts, their key data and sourcing.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet was read. Manufacturer values are product-page values, not datasheet limits.

Source keys used below:
- **TDK**: TDK InvenSense product page.
- **Bosch**: Bosch Sensortec product page.
- **LCSC**: LCSC product page, fetched 2026-10-18.
- **PX4**: PX4-Autopilot repo, main branch, driver directory and register headers.
- **Snippet**: search-result text of a PDF datasheet. Not opened, always `NOT_VERIFIED`.
- **LCSC data (agy)**: LCSC page embedded data (`__NEXT_DATA__` JSON), extracted by the external model agy on 2026-10-18 (user-approved). Not shown on the rendered page and not checked by Claude, so always `NOT_VERIFIED`.

## 1. Decision

| Item | Value |
| ---- | ----- |
| Barometers (SEN-002) | 1 × TDK InvenSense ICP-20100 (LCSC C5343527) + 1 × Bosch BMP390 (LCSC C5124834). DEC-010, 2026-10-18. |
| Magnetometer (SEN-003) | 1 × Bosch BMM150 (LCSC C171681). DEC-011, 2026-10-18. |
| Requirement change | SEN-003 reduced from 2 × to 1 × I2C magnetometer (DEC-011). OPEN-005 closed. |
| Barometer gain | Vendor diversity between the two barometers. |

## 2. Risks at decision time

| Severity | Part | Label | Finding | Source |
| -------- | ---- | ----- | ------- | ------ |
| MAJOR | ICP-20100 | `VERIFIED` | TDK product page marks the part **EOL**. No successor is named. LCSC still lists stock. | TDK, LCSC (2026-10-18) |
| MAJOR | BMP390 | `VERIFIED` | LCSC C5124834 shows "Not available now", with no stock and no price. | LCSC (2026-10-18) |
| MAJOR | BMP390 | `NOT_VERIFIED` | LCSC page data marks C5124834 `productCycle: "stop_product"` with `stockNumber: 0`. This likely means LCSC stopped selling it, not a Bosch EOL; not confirmed. | LCSC data (agy) |
| MAJOR | Both barometers | `ASSUMED` | Both barometer parts have supply risk at the same time (ICP-20100 EOL, BMP390 not sold at LCSC). The team is reviewing DEC-010. | Rows above |
| MINOR | BMM150 | `NOT_VERIFIED` | Bosch BMM150 product page returned 404. Distributor text calls BMM350 the successor, but no official EOL notice was found. | Bosch, snippet |
| MINOR | BMM150 | `ASSUMED` | Single magnetometer: no onboard redundancy for heading. | DEC-011 |
| INFO | I2C addresses | `NOT_VERIFIED` | PX4 defaults are ICP-20100 0x63 and BMM150 0x10. BMP390 address and the selectable addresses are not confirmed, so a bus conflict check is open. | PX4 |

## 3. Key data

### ICP-20100 (barometer)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | EOL | TDK | `VERIFIED` |
| Pressure range | 30 to 110 kPa | TDK | `VERIFIED` |
| Package | LGA-10L | LCSC | `VERIFIED` (name only); size `NOT_VERIFIED` |
| Interfaces, I2C address selection | Not on the page | TDK | `NOT_VERIFIED` |
| Default I2C address | 0x63 | PX4 `Inven_Sense_ICP201XX_registers.hpp` | `VERIFIED` (driver default) |
| Supply, temperature, noise, accuracy | Not on the page. Datasheet DS-000416 v1.4 not read. | TDK | `NOT_VERIFIED` |
| PX4 driver | `barometer/invensense/icp201xx`. ICP-20100 is not named in the headers read. | PX4 | `VERIFIED` (directory); coverage `NOT_VERIFIED` |

### BMP390 (barometer)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | Not stated by Bosch. The page promotes BMP581 but does not call it a successor. LCSC page data says `stop_product` for C5124834. | Bosch; LCSC data (agy) | `NOT_VERIFIED` |
| Interfaces | I2C, SPI | Bosch | `VERIFIED` |
| I2C addresses | Not on the page | Bosch | `NOT_VERIFIED` |
| VDD | 1.65 to 3.6 V | Bosch | `VERIFIED` |
| VDDIO | 1.2 to 3.6 V | Bosch | `VERIFIED` |
| Operating temperature | Not on the page. Absolute accuracy is given for 0 to 65 °C. | Bosch | `NOT_VERIFIED` |
| Package | 10-pin LGA, metal lid, 2.0 × 2.0 × 0.75 mm | Bosch | `VERIFIED` |
| Noise | 0.02 Pa RMS (lowest bandwidth, highest resolution) | Bosch | `VERIFIED` |
| Relative accuracy | ±0.03 hPa typ (700 to 1100 hPa, 25 to 40 °C) | Bosch | `VERIFIED` |
| PX4 driver | `barometer/bmp388`; header defines `BMP390_CHIP_ID = 0x60` | PX4 | `VERIFIED` |

### BMM150 (magnetometer)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | Unknown. Bosch page 404; no official EOL notice found. | Bosch | `NOT_VERIFIED` |
| Package | WLCSP-12, 1.6 × 1.6 mm (LCSC); 1.56 × 1.56 × 0.6 mm (snippet) | LCSC, snippet | `VERIFIED` (LCSC name); size `NOT_VERIFIED` |
| Interfaces | I2C, SPI | Snippet | `NOT_VERIFIED` |
| Default I2C address | 0x10 | PX4 `Bosch_BMM150_registers.hpp` | `VERIFIED` (driver default) |
| VDD / VDDIO | 1.62 to 3.6 V / 1.2 to 3.6 V | Snippet | `NOT_VERIFIED` |
| Range | ±1300 µT (x, y), ±2500 µT (z) | Snippet | `NOT_VERIFIED` |
| Resolution | about 0.3 µT | Snippet | `NOT_VERIFIED` |
| Operating temperature | Not found | – | `NOT_VERIFIED` |
| PX4 driver | `magnetometer/bosch/bmm150` (chip ID 0x32). A `bmm350` driver also exists. | PX4 | `VERIFIED` |

3.3 V supply: inside the BMP390 range (`VERIFIED`, Bosch). ICP-20100 and BMM150 ranges are `NOT_VERIFIED`.

## 4. Sourcing

LCSC, fetched 2026-10-18. USD. Not a quote.

| Detail | ICP-20100 | BMP390 | BMM150 |
| ------ | --------- | ------ | ------ |
| LCSC SKU | C5343527 | C5124834 | C171681 |
| MPN on page | ICP-20100 (exact) | BMP390 (exact) | BMM150 (exact) |
| Stock | 5,372 | Not available now (page data: 0, `stop_product`) | 10,019 |
| Qty 1 | $1.39 | none shown (page data: $5.39) | $1.30 |
| Qty 10 | not listed | none shown (page data: $5.29) | $1.10 |

- BMP390 page data (agy, `NOT_VERIFIED`) also lists 30+ $5.22 and 100+ $5.15, MOQ 1, 10,000 per reel. LCSC lists this bare IC as `Module: Yes` in its spec table, which looks like an LCSC data error.
- LCSC search (`lcsc.com/search?q=BMP390`) does not render without JavaScript, so other BMP390 SKUs or boards at LCSC are unknown.
- DigiKey, Mouser and JLCPCB were not checked.
- JLCPCB assembly eligibility is not checked for any of the three.

## 5. Open checks

- [ ] Team reviews DEC-010 because both barometers have supply risk: ICP-20100 EOL (last-time buy or replacement) and BMP390 not sold at LCSC (other source or replacement).
- [ ] Confirm BMM150 lifecycle from Bosch, and consider BMM350 if BMM150 is EOL.
- [ ] Get supply, temperature, I2C address selection and land pattern from each datasheet (user-supplied values, or an approved datasheet route).
- [ ] Check the I2C address plan for all three parts on the chosen buses (P1-004, P1-005).
- [ ] Confirm that PX4 `icp201xx` supports ICP-20100.
- [ ] Check JLCPCB assembly eligibility.

## 6. Sources

- TDK ICP-20100: https://invensense.tdk.com/products/smartpressure/icp-20100/
- Bosch BMP390: https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp390/
- Bosch BMM350 (BMM150 page returned 404): https://www.bosch-sensortec.com/products/motion-sensors/magnetometers/bmm350/
- LCSC: https://www.lcsc.com/product-detail/C5343527.html (ICP-20100), https://www.lcsc.com/product-detail/C5124834.html (BMP390), https://www.lcsc.com/product-detail/C171681.html (BMM150)
- PX4 drivers: https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/barometer/invensense/icp201xx, https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/barometer/bmp388, https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/magnetometer/bosch/bmm150
