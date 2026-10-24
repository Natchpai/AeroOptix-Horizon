# What Next

**Updated:** 2026-10-24
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 1. Git

- [ ] Push `dev` to `origin` (local commits not yet pushed, starting with `1a5e7ae`).
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

Pinmap review 0.2 is answered (`AO-HORIZON_PINMAP_REVIEW_EN.md`). The team answered the pinout source (Q1, Q2), the F103 TIM3 channels (Q3) and stock px4io (Q7).

- [ ] Send `AO-HORIZON_PINMAP_DECISIONS_EN.md` to the team: spec rows to change (section 3, OPEN-016), decisions D1 to D7, software questions S1 to S7, proposals H1 and H2 (P0-019).
- [ ] After the reply: update the spec rows, apply pin allocation section 2.1, and issue pinmap 0.3.

## 5. Hardware items from the pinmap review (answer later)

Hardware-only choices taken out of the team decisions file. None changes the drone spec or the software.

- [ ] F103 LEDs (blue PB14, amber PB15, green PA11): fit or leave unconnected. px4io drives them either way.
- [x] F103 24 MHz crystal: checked 2026-10-24. DS5319 Rev 20 Table 22 limits the crystal to 4 to 16 MHz; Table 20 allows an external clock of 1 to 25 MHz. Out of range, so the team gets S7 (OPEN-015).
- [ ] F103 clock part: pick it after the team answers S7 (8 MHz crystal, or 24 MHz oscillator module).
- [ ] PWM pull-downs (team Q10): pick the resistor value.
- [ ] F103 PA9 (px4io console TX): test pad or connector.
- [ ] F103 PC14 and PC15 unconnected, and the px4io-v2 reserved pins: cut the free F103 list in pinmap 4.2.
- [ ] Telemetry 2 (USART1, PB14, PB15): connector.
- [ ] Spare outputs PD14, PD15, PE9: connector or pads, after the team answers D4.
- [ ] Debug connectors for both MCUs: form, after the team answers S6.
- [ ] Servo rail divider on F103 PA4: match the px4io scaling.
- [ ] ICM-45686 pin 9 unused: the IMU record (section 3) says leave it NC or tie it to VDDIO, but that note came from agy and is `NOT_VERIFIED`. Confirm in the datasheet.
- [x] IST8310 RSTN unused: internal pull-up, MCU connection "not necessary" (IST8310 DS 2.2, barometer and magnetometer record). It can stay unconnected.
- [ ] SDMMC1: check pins against ST pin data; add pull-ups and ESD protection.
- [ ] PM02D: read the label (INA228 at 0x45, or INA226 at 0x41).

## 6. Open questions for me

- [x] `Revision: v1.0` in the README header is the board revision (renamed to `Board revision`, 2026-10-24).
- [x] Pixhawk 6C and 6X are both references (REF-01, REF-05, SYS-002; spec 0.10, 2026-10-24).
