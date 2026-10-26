# What Next

**Updated:** 2026-10-26
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 1. Git

- [x] Hardware answers, spec 0.14 (`2b89d07`), merged to `main` in PR #17.
- [x] Team website merged to `main` in PRs #18 to #24; title image and logos on `dev`.
- [ ] Commit the consistency pass: spec 0.15, checklist 0.14, root README, CHANGELOG, this file, the eFuse `CMP-008` link in `web/src/data/topology.ts` and `web/HANDOFF.md`.
- [ ] Push `dev` and open a PR to `main` with `.github/pull_request_template.md`. The site updates on the merge.

## 2. Power sheet (P2-011)

Does not depend on the pinout or sensor answers. See spec 4.3 "Schematic state".

- [ ] Re-check the saved sheet first: the spec 4.3 table says 17 parts with the DNP DF2S6.2CT, the README says 19 parts and the CHANGELOG says the DF2S6.2CT was removed. Ask Claude for `sch-inspect` on `power_supplies.kicad_sch`, then fix the spec table.
- [ ] Wire the TPS16412DRC eFuse between `+VIN` and `+5V` (DEC-024). Placed, only GND wired. Set the ILIM resistor for 1.5 A and the OVP, EN/UVLO, dV/dt and FLT parts from TI data; check reverse current with USB (P2-017, OPEN-012).
- [ ] Change the PM02D connector from JST-GH to a 6-pin 2.00 mm CLIK-Mate (decided 2026-10-24, OPEN-023).
- [ ] Decide the `+3V3A` rail and its LDO (OPEN-011). As drawn, the TPS73533DRBR NR capacitor is above TI's limit.
- [ ] Add the 0.1 µF AVIN capacitor TI recommends for the TPS62142.
- [ ] Fix the LCSC field: C162430 is on both the 1 µF and the 10 µF capacitor.
- [ ] Annotate all parts.
- [ ] Ask Claude for a `sch-review` of `power_supplies.kicad_sch` after saving.

## 3. Footprint checks (P2-012, OPEN-013)

Check against the datasheet figures yourself:

- [ ] BMP581: Fig. 32 pad sizes and the pin 1 corner (Fig. 29, 30) on `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y`.
- [ ] Solder mask under BMP581: Bosch asks for none, with 20 µm clearance (DS004-13 §8.2).
- [ ] ICP-20100: land pattern (AN-000140) and pin 1 corner.
- [ ] IST8310: check the stock `LGA-16_3x3mm_P0.5mm` footprint and pin 1 corner against the datasheet package drawing (no land pattern in the datasheet). BMM150 is no longer used (DEC-011, 2026-10-24).

## 4. Waiting on the team

Pinmap review 0.3 is answered and applied (spec rev 0.12). The integration answers are applied in spec rev 0.13 (DEC-019 to DEC-023, 2026-10-24): Pixhawk-style servo rail on the board (your change to D8), GPS1 10-pin, parts −40 to +85 °C, stock px4io, no IMU heater, PC1 kept. On 2026-10-24 you set mounting, USB loads, the ESC connector, the UBEC XT30 and the PM02D connector, and dropped the ESC current sense (spec rev 0.14).

- [x] Send integration questions rev 0.1 (P0-021). Answered and applied 2026-10-24.
- [ ] Send `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.4 to the team (P0-022). It asks only D13 (Skywalker ESCs look PWM-only: how do the motors stop on an H743 hang?), the parts table and test results.
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team bench tests, not hardware work: RC-loss failsafe over ELRS MAVLink (S5); ESC on signal loss (OPEN-017, P4-011); servo current and stall current (OPEN-007).

## 5. Hardware items (from the pinmap work)

Hardware-only choices. None changes the drone spec or the software.

- [ ] px4io LEDs (blue PB14, amber PB15, green PA11) are fitted (team, Q20): pick the resistors.
- [ ] F100 PA10 and PB11: weak pull-up to 3.3 V (team, review 0.3). Pick the value.
- [ ] F100 library part from stock `MCU_ST_STM32F1:STM32F100C8Tx`, and the block diagram text (P2-014).
- [ ] Crystal parts and load capacitors: 16 MHz (H743) and 24 MHz (F100) (P1-014).
- [ ] PWM pull-downs: pick the value so bidirectional DShot still works on the motor lines (P2-013, OPEN-018).
- [ ] BMP384 fallback: compare footprint and pinout with the BMP581 (P1-015, OPEN-019). Address 0x76, SDO low (team, Q22).
- [ ] F100 debug pads: SWDIO, SWCLK, NRST, GND, USART1 TX (PA9).
- [ ] H743 debug: Pixhawk Debug Mini 6-pin JST-SH (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND) plus an NRST pad. Check the pin order against DS-009 if you can get it.
- [ ] Telemetry 2 (USART1, PB14, PB15): JST-GH 6-pin connector, as Telemetry 1 (team, integration answers).
- [ ] Spare outputs PD14, PD15, PE9: pads only (team, integration answers).
- [ ] Servo rail divider on F100 PA4: match the px4io 3:1 scaling. It reads the on-board 6 V servo bus (DEC-019).
- [ ] ICM-45686 pin 9 unused: the IMU record (section 3) says leave it NC or tie it to VDDIO, but that note came from agy and is `NOT_VERIFIED`. Confirm in the datasheet.
- [ ] SDMMC1: add pull-ups and ESD protection.
- [ ] PM02D label (INA228 at 0x45, or INA226 at 0x41): asked in the integration questions parts table.
- [ ] ESC: 4 × Skywalker 80A V2 (team design). DShot or PWM and signal-loss behavior: asked in D13 (OPEN-017, P4-011).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).

## 6. Hardware items (from the integration answers)

Hardware work that does not need the team's section 9 reply, unless noted.

- [ ] PM02D connector: CLIK-Mate chosen (section 2). Confirm with the team's plug photo or the Holybro page (OPEN-023, P2-015).
- [ ] Connector pinouts against the Pixhawk standard DS-009: Telemetry 1 and 2, GPS1 10-pin (3.3 V and buzzer pins), airspeed, TF-Luna (OPEN-023, P2-015).
- [ ] I2C4 (PD12, PD13): check 5 V tolerance in case a module pulls up to 5 V (OPEN-023).
- [ ] ESC connectors: 4 × 3-pin headers with the + pin removed (IF-040 to IF-043, P2-018).
- [ ] Servo rail (DEC-019): check the board-mount XT30 rating against 10 A continuous and 15 A peak. Then the 6 V and servo GND copper, the servo GND to logic GND join, and bulk capacitors (OPEN-021, P2-016).
- [ ] USB VBUS and PM02D 5 V OR-ing. USB feeds all external 5 V ports: check the VBUS budget (OPEN-006).
- [ ] PCB: forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount; pick the outline, cable entry sides and dampers at placement, then send them to the CAD team (MEC-002, MEC-004).

## 7. Team website

From `web/HANDOFF.md`. The site follows the records; a design change still goes into the spec first.

- [ ] Review the rest of the live site: Overview, Interface view, detail panel, search. List changes.
- [ ] Check the fuchsia +3.3V rail colour on screen (between GPIO pink and UART purple).
- [ ] Check the light theme on the pinout page and the Board view.
- [ ] Keep `web/src/data/topology.ts` in step with the spec: the build catches removed IDs, not new interfaces.
- [ ] Showcase page: 3D viewer, renders and photos once there is a PCB.
