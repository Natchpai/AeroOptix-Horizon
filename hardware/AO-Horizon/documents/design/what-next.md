# What Next

**Updated:** 2026-10-24
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 1. Git

- [ ] Commit the doc sync (checklist 0.10, selection record 0.7, README, CHANGELOG, this file). `c9fe9ed` (spec 0.11, pinmap 0.3) is already committed on `dev`.
- [ ] Push `dev` to `origin` (not pushed yet).
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

The decisions file is answered and applied (spec rev 0.11, 2026-10-24). You kept the F103; the F103 gets an 8 MHz crystal and the team rebuilds px4io (DEC-017).

- [ ] Send `AO-HORIZON_PINMAP_REVIEW_EN.md` rev 0.3 to the team (P0-020). They fill the `NEW` rows and answer Q20 (px4io LEDs), Q21 (TX-only px4io console), Q22 (BMP384 address).
- [ ] After the reply: ask Claude to apply it to the pin allocation record and the spec.
- [ ] Team bench tests, not hardware work: RC and RC-loss failsafe over ELRS MAVLink (S5).

## 5. Hardware items (from the pinmap work)

Hardware-only choices. None changes the drone spec or the software.

- [ ] F103 LEDs (blue PB14, amber PB15, green PA11): fit or leave unconnected. Asked the team (Q20).
- [x] F103 24 MHz crystal: out of range (DS5319 Table 22). Resolved: 8 MHz crystal, PLL ×3 (DEC-017).
- [ ] Crystal parts and load capacitors: 16 MHz (H743) and 8 MHz (F103) (P1-014).
- [ ] PWM pull-downs: pick the value so bidirectional DShot still works on the motor lines (P2-013, OPEN-018).
- [ ] BMP384 fallback: compare footprint, pinout and address with the BMP581 (P1-015, OPEN-019).
- [ ] F103 debug pads: SWDIO, SWCLK, NRST, GND, USART1 TX (PA9).
- [ ] H743 debug: Pixhawk Debug Mini 6-pin JST-SH (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND) plus an NRST pad. Check the pin order against DS-009 if you can get it.
- [x] F103 PC14/PC15 and the px4io-v2 reserved pins: done in pin allocation rev 0.5 (4 free F103 pins left).
- [ ] Telemetry 2 (USART1, PB14, PB15): connector.
- [ ] Spare outputs PD14, PD15, PE9: connector or pads (team keeps all 3, D4).
- [ ] Servo rail divider on F103 PA4: match the px4io 3:1 scaling.
- [ ] ICM-45686 pin 9 unused: the IMU record (section 3) says leave it NC or tie it to VDDIO, but that note came from agy and is `NOT_VERIFIED`. Confirm in the datasheet.
- [x] IST8310 RSTN unused: internal pull-up, MCU connection "not necessary" (IST8310 DS 2.2, barometer and magnetometer record). It can stay unconnected.
- [x] SDMMC1 pins checked against ST pin data (2026-10-24).
- [ ] SDMMC1: add pull-ups and ESD protection.
- [ ] PM02D: read the label (INA228 at 0x45, or INA226 at 0x41).
- [ ] ESC: confirm the model (Tekko32 F4 4-in-1, AM32 planned) and how it acts on DShot signal loss (OPEN-017, P4-011).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).

## 6. Open questions for me

- [x] `Revision: v1.0` in the README header is the board revision (renamed to `Board revision`, 2026-10-24).
- [x] Pixhawk 6C and 6X are both references (REF-01, REF-05, SYS-002; spec 0.10, 2026-10-24).
