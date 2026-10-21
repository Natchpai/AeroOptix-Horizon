# AeroOptix-Horizon: Barometer and Magnetometer Selection Summary

**Revision:** 0.4
**Updated:** 2026-10-21
**Status:** ICP-20100 and BMM150 confirmed by the team (DEC-010, DEC-011). BMP390 removed on 2026-10-21; the second barometer is open (OPEN-014, BMP581 proposed). Lifecycle and availability risks are open. Datasheet values and implementation are not verified. Not a verification record.
**Requirement refs:** SEN-002, SEN-003, CMP-004, CMP-005, OPEN-014 (spec). Checklist tasks: P0-009, P0-010.
**Decision owner:** Team

Single record for the barometer and magnetometer parts, their key data and sourcing.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`. No datasheet was read. Manufacturer values are product-page values, not datasheet limits.

Source keys used below:
- **TDK**: TDK InvenSense product page.
- **Bosch**: Bosch Sensortec product page.
- **LCSC**: LCSC product page, fetched 2026-10-18.
- **PX4**: PX4-Autopilot repo, main branch, driver directory and register headers.
- **Bosch API**: Bosch BMP5_SensorAPI on GitHub, `bmp5_defs.h`, fetched 2026-10-21.
- **Snippet**: search-result text of a PDF datasheet. Not opened, always `NOT_VERIFIED`.
- **DS (NotebookLM)**: datasheet text checked through NotebookLM on 2026-10-19, with the text confirmed in the source fulltext: ICP-20100 DS-000416 Rev 1.3 (marked preliminary), BMP390 BST-BMP390-DS002-07 Rev 1.7, BMM150 BST-BMM150-DS001-05 Rev 1.4. BMP581: BST-BMP581-DS004-13 Rev 1.13, checked on 2026-10-21 (notebook `BMP581`, source added from the Bosch URL).
- **LCSC data (agy)**: LCSC page embedded data (`__NEXT_DATA__` JSON), extracted by the external model agy on 2026-10-18 (user-approved). Not shown on the rendered page and not checked by Claude, so always `NOT_VERIFIED`.

## 1. Decision

| Item | Value |
| ---- | ----- |
| Barometers (SEN-002) | 1 × TDK InvenSense ICP-20100 (LCSC C5343527), DEC-010, 2026-10-18. Second barometer TBD (OPEN-014). |
| BMP390 removed | The human owner removed Bosch BMP390 (LCSC C5124834) on 2026-10-21 because LCSC does not sell it. Its data stays below as a record. |
| Second barometer candidate | Bosch BMP581 (LCSC C5362283, checked at LCSC by the user). Proposed, not confirmed: the team decides (OPEN-014). |
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

### Re-check (2026-10-19)

| Severity | Part | Label | Finding | Source |
| -------- | ---- | ----- | ------- | ------ |
| INFO | I2C addresses | `VERIFIED` | ICP-20100 0x63 or 0x64 (AD0), BMP390 0x76 or 0x77 (SDO; SDO must not float), BMM150 0x10 to 0x13 (CSB and SDO). No two parts can share an address. | DS (NotebookLM): ICP-20100 §4.1.9, BMP390 I2C interface text, BMM150 Table 30 |
| MAJOR | BMM150 | `VERIFIED` | Bosch no longer lists BMM150. Its magnetometer page lists only BMM350, and the BMM150 product page returns 404. | Bosch |
| MAJOR | BMM150 | `NOT_VERIFIED` | DigiKey lists BMM150 as Obsolete ("no longer manufactured"). Search results point to a Bosch discontinuation notice, which was not read. | DigiKey (agent fetch), snippet |
| INFO | ICP-20100 | `VERIFIED` | TDK SmartPressure page: "Pressure products are EOL and not recommended for new designs". No successor or last-time-buy date is given. | TDK |
| INFO | BMP390 | `NOT_VERIFIED` | Bosch page is live and states no lifecycle status. DigiKey lists it as Active. | Bosch, DigiKey (agent fetch) |

### BMP390 removal and BMP581 check (2026-10-21)

| Severity | Part | Label | Finding | Source |
| -------- | ---- | ----- | ------- | ------ |
| INFO | BMP390 | `ASSUMED` | Removed from DEC-010 by the human owner because LCSC C5124834 is not available. Library files kept until OPEN-014 is decided. | User |
| INFO | BMP581 | `VERIFIED` | 2.0 × 2.0 × 0.75 mm metal-lid LGA, the same body size as BMP390. Pin count and pinout are not on the Bosch page, so reuse of `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y` is `NOT_VERIFIED`. | Bosch |
| INFO | I2C addresses | `VERIFIED` | BMP581 is 0x46 (primary) or 0x47 (secondary). This does not overlap ICP-20100 (0x63, 0x64) or BMM150 (0x10 to 0x13). The address-select pin is `NOT_VERIFIED`. | Bosch API |
| MINOR | BMP581 | `VERIFIED` | Bosch page states no lifecycle status. Every distributor listed on it showed 0 stock on 2026-10-21. | Bosch |
| INFO | BMP581 | `VERIFIED` | PX4 has a `barometer/bmp581` driver on main, with I2C and SPI files. The first PX4 release with it is `NOT_VERIFIED`. | PX4 |
| INFO | BMP581 | `NOT_VERIFIED` | LCSC C5362283 names Bosch BMP581, LGA-10 (2x2). Stock and price are not recorded here. | User; LCSC (agent fetch) |
| INFO | BMP581 | `VERIFIED` | Pin map is the same as BMP390: 1 VDDIO, 2 SCK, 3 VSS, 4 SDI, 5 SDO, 6 CSB, 7 INT, 8 VSS, 9 VSS, 10 VDD. 10 pins, body 2.0 × 2.0 mm (±0.1), 0.75 mm high. | DS (NotebookLM): Table 28, Table 3 |
| INFO | I2C addresses | `VERIFIED` | SDO selects the BMP581 address: 0x46 when SDO = 0, 0x47 when SDO = 1. SDO must not float in I2C mode. | DS (NotebookLM): §5 I2C text |
| MINOR | BMP581 | `VERIFIED` | The datasheet gives VDD min 1.71 V (Table 4); the product page says 1.65 V. 3.3 V is inside both. | DS (NotebookLM): Table 4; Bosch |
| MINOR | Footprint | `NOT_VERIFIED` | Land pattern 0.325 × 0.30 mm pads on ±0.7625 mm centers, pin 1 top-left, counterclockwise in top view: read by NotebookLM from Fig. 29 to 32 with no citation. The §8.2 text (`VERIFIED`) gives the rule: terminal +25 µm per side, at least 200 µm between pads, no solder mask, vias or traces under the part. | DS (NotebookLM) |

## 3. Key data

### ICP-20100 (barometer)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | EOL | TDK | `VERIFIED` |
| Pressure range | 30 to 110 kPa | TDK | `VERIFIED` |
| Package | LGA-10L, 2.000 × 2.000 × 0.800 mm nom, 0.5 mm pitch | LCSC; DS Table 19 | `VERIFIED` (DS via NotebookLM) |
| Interfaces, I2C address selection | Not on the page | TDK | `NOT_VERIFIED` |
| Default I2C address | 0x63 | PX4 `Inven_Sense_ICP201XX_registers.hpp` | `VERIFIED` (driver default) |
| Supply, temperature, noise, accuracy | Not on the page. Datasheet DS-000416 v1.4 not read. | TDK | `NOT_VERIFIED` |
| PX4 driver | `barometer/invensense/icp201xx`. ICP-20100 is not named in the headers read. | PX4 | `VERIFIED` (directory); coverage `NOT_VERIFIED` |

### BMP390 (removed 2026-10-21)

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

### BMP581 (barometer 2 candidate, OPEN-014)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | Not stated by Bosch. "Available via our distribution partners"; all listed distributors at 0 stock (2026-10-21). | Bosch | `NOT_VERIFIED` |
| Interfaces | I2C (up to 1.0 MHz), I3C, SPI (3- and 4-wire, up to 10 MHz) | Bosch | `VERIFIED` |
| I2C addresses | 0x46 (SDO = 0), 0x47 (SDO = 1). SDO must not float. | DS §5; Bosch API | `VERIFIED` (DS via NotebookLM) |
| Chip ID | 0x50 (primary), 0x51 (secondary) | Bosch API | `VERIFIED` |
| VDD | 1.71 to 3.6 V (the product page says 1.65 V) | DS Table 4; Bosch | `VERIFIED` (DS via NotebookLM) |
| VDDIO | 1.08 to 3.6 V | Bosch | `VERIFIED` |
| Current | 1.3 µA at 1 Hz pressure and temperature; 0.5 µA deep standby | Bosch | `VERIFIED` |
| Package | Metal-lid LGA-10, 2.0 × 2.0 × 0.75 mm | DS Table 3; Bosch | `VERIFIED` (DS via NotebookLM) |
| Pin map | 1 VDDIO, 2 SCK, 3 VSS, 4 SDI, 5 SDO, 6 CSB, 7 INT, 8 VSS, 9 VSS, 10 VDD (same as BMP390) | DS Table 28 | `VERIFIED` (DS via NotebookLM) |
| Unused INT | Tie to GND and keep `int_en` off | DS §6.2 | `VERIFIED` (DS via NotebookLM) |
| Noise, accuracy, temperature | Not checked | - | `NOT_VERIFIED` |
| PX4 driver | `barometer/bmp581` (I2C and SPI) | PX4 | `VERIFIED` (directory) |

### BMM150 (magnetometer)

| Parameter | Value | Source | Label |
| --------- | ----- | ------ | ----- |
| Product status | Not listed by Bosch (magnetometer page lists only BMM350, 2026-10-19). DigiKey: Obsolete. No Bosch EOL notice read. | Bosch; DigiKey | `VERIFIED` (not listed); EOL `NOT_VERIFIED` |
| Package | WLCSP-12, 1.56 × 1.56 × 0.6 mm, 0.4 mm diagonal ball pitch | DS §8.1 | `VERIFIED` (DS via NotebookLM) |
| Interfaces | I2C, SPI (3- and 4-wire), selected by the PS pin | DS Table 32 | `VERIFIED` (DS via NotebookLM) |
| Default I2C address | 0x10 | PX4 `Bosch_BMM150_registers.hpp` | `VERIFIED` (driver default) |
| VDD / VDDIO | 1.62 to 3.6 V / 1.2 to 3.6 V | Snippet | `NOT_VERIFIED` |
| Range | ±1300 µT (x, y), ±2500 µT (z) | Snippet | `NOT_VERIFIED` |
| Resolution | about 0.3 µT | Snippet | `NOT_VERIFIED` |
| Operating temperature | Not found | – | `NOT_VERIFIED` |
| PX4 driver | `magnetometer/bosch/bmm150` (chip ID 0x32). A `bmm350` driver also exists. | PX4 | `VERIFIED` |

3.3 V supply: inside the BMP581 range (`VERIFIED`, Bosch). ICP-20100 and BMM150 ranges are `NOT_VERIFIED`.

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
- BMP581 LCSC C5362283 was checked by the user on 2026-10-21. Stock and price are not recorded here (`NOT_VERIFIED`).
- DigiKey, Mouser and JLCPCB were not checked.
- JLCPCB assembly eligibility is not checked for any of the three.

## 5. Open checks

- [ ] Team confirms the second barometer (OPEN-014). Proposed: BMP581 (LCSC C5362283). ICP-20100 EOL still needs a last-time buy or a replacement.
- [ ] Check the BMP581 footprint against the datasheet figures (pin 1 corner, Fig. 32 pad sizes) before placing it. Library starting point: `0_Sensor_Pressure:BMP581` on the Bosch LGA-10 footprint (OPEN-013, P2-012).
- [ ] Confirm BMM150 lifecycle from Bosch, and consider BMM350 if BMM150 is EOL. Bosch no longer lists BMM150 (2026-10-19). BMM350 is not a drop-in part (`NOT_VERIFIED`, flyer snippet).
- [ ] Get supply, temperature, I2C address selection and land pattern from each datasheet (user-supplied values, or an approved datasheet route).
- [ ] Check the I2C address plan for all three parts on the chosen buses (P1-004, P1-005). The address sets do not overlap (re-check table); the strap choice for each part is open.
- [ ] Check the library footprints against the datasheet drawings (OPEN-013, P2-012). Symbol pin maps match ICP-20100 Table 18 and BMM150 Table 32. Open: ICP-20100 has no land pattern in its datasheet (AN-000140) and its pads are wider than terminal b; BMM150 A1 corner and 3D model.
- [ ] Confirm that PX4 `icp201xx` supports ICP-20100.
- [ ] Check JLCPCB assembly eligibility.

## 6. Sources

- TDK ICP-20100: https://invensense.tdk.com/products/smartpressure/icp-20100/
- TDK SmartPressure (EOL notice): https://invensense.tdk.com/smartpressure/
- Bosch magnetometers: https://www.bosch-sensortec.com/products/motion-sensors/magnetometers/
- DigiKey BMM150: https://www.digikey.com/en/products/detail/bosch-sensortec/BMM150/4196671
- Bosch BMP390: https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp390/
- Bosch BMP581: https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp581/
- Bosch BMP581 datasheet (NotebookLM source, not opened by Claude): https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf
- Bosch BMP5_SensorAPI: https://github.com/boschsensortec/BMP5_SensorAPI/blob/master/bmp5_defs.h
- Bosch BMM350 (BMM150 page returned 404): https://www.bosch-sensortec.com/products/motion-sensors/magnetometers/bmm350/
- LCSC: https://www.lcsc.com/product-detail/C5343527.html (ICP-20100), https://www.lcsc.com/product-detail/C5124834.html (BMP390), https://www.lcsc.com/product-detail/C171681.html (BMM150), https://www.lcsc.com/product-detail/C5362283.html (BMP581)
- PX4 drivers: https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/barometer/invensense/icp201xx, https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/barometer/bmp388, https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/barometer/bmp581, https://github.com/PX4/PX4-Autopilot/tree/main/src/drivers/magnetometer/bosch/bmm150
