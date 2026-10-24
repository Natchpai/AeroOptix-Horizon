# What Next

**Updated:** 2026-10-24
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 1. Git

- [ ] Commit the pinmap 0.3 answers and the F100 change: spec 0.12, pin allocation 0.6, checklist 0.11, power budget 0.5, pinmap review 0.3 (answered), decisions file note, barometer and magnetometer record 0.8, integration questions 0.1, design README, root README, CLAUDE.md, this file. `dev` matched `origin/dev` before these edits.
- [ ] Run `/progress-update` for the root README and CHANGELOG.
- [ ] Push `dev` to `origin`.
- [ ] Open a PR from `dev` to `main` with `.github/pull_request_template.md`.

## 2. Power sheet (P2-011)

Does not depend on the pinout or sensor answers. See spec 4.3 "Schematic state".

- [ ] Draw the `+VIN` to `+5V` path. Nothing drives `+5V` yet (OPEN-012).
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

Pinmap review 0.3 is answered and applied (spec rev 0.12, 2026-10-24). Following the team, the IO MCU is now the STM32F100C8T6B with a 24 MHz crystal and stock px4io (DEC-002, DEC-017). No pin moved.

- [ ] Send `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.1 to the team (P0-021): servo power path (D8), mounting (D9), environment (D10), safety switch and GPS (D11), devices and connectors, S8 to S10.
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team bench tests, not hardware work: RC and RC-loss failsafe over ELRS MAVLink (S5).

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
- [ ] Telemetry 2 (USART1, PB14, PB15): connector.
- [ ] Spare outputs PD14, PD15, PE9: connector or pads (team keeps all 3, D4).
- [ ] Servo rail divider on F100 PA4: match the px4io 3:1 scaling.
- [ ] ICM-45686 pin 9 unused: the IMU record (section 3) says leave it NC or tie it to VDDIO, but that note came from agy and is `NOT_VERIFIED`. Confirm in the datasheet.
- [ ] SDMMC1: add pull-ups and ESD protection.
- [ ] PM02D: read the label (INA228 at 0x45, or INA226 at 0x41).
- [ ] ESC: confirm the model (Tekko32 F4 4-in-1, AM32 planned) and how it acts on DShot signal loss (OPEN-017, P4-011).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).
