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
- [ ] IST8310: make the library starting point (`kicad-part-start`), then check the land pattern and pin 1 corner against the datasheet drawing. BMM150 is no longer used (DEC-011, 2026-10-24).

## 4. Waiting on the team

Pinmap review 0.2 is answered (`AO-HORIZON_PINMAP_REVIEW_EN.md`). The team answered the pinout source (Q1, Q2), the F103 TIM3 channels (Q3) and stock px4io (Q7).

- [ ] Send `AO-HORIZON_PINMAP_DECISIONS_EN.md` to the team: spec rows to change (section 3), decisions D1 to D7, software questions S1 to S6, proposals H1 and H2.
- [ ] After the reply: update the spec rows, fix the source note in `AO-HORIZON_PIN_ALLOCATION_EN.md`, and issue pinmap 0.3.

## 5. Hardware items from the pinmap review (answer later)

Hardware-only choices taken out of the team decisions file. None changes the drone spec or the software.

- [ ] F103 LEDs (blue PB14, amber PB15, green PA11): fit or leave unconnected. px4io drives them either way.
- [ ] F103 24 MHz crystal: check the F103 datasheet HSE crystal range and external clock limit. px4io-v2 expects 24 MHz; third-party sources say 4 to 16 MHz for a crystal (NOT_VERIFIED). Ask the team only if this forces a px4io build change.
- [ ] PWM pull-downs (team Q10): pick the resistor value.
- [ ] F103 PA9 (px4io console TX): test pad or connector.
- [ ] F103 PC14 and PC15 unconnected, and the px4io-v2 reserved pins: cut the free F103 list in pinmap 4.2.
- [ ] Telemetry 2 (USART1, PB14, PB15): connector.
- [ ] Spare outputs PD14, PD15, PE9: connector or pads, after the team answers D4.
- [ ] Debug connectors for both MCUs: form, after the team answers S6.
- [ ] Servo rail divider on F103 PA4: match the px4io scaling.
- [ ] ICM-45686 pin 9 and IST8310 RSTN: unused-pin handling from the datasheets.
- [ ] SDMMC1: check pins against ST pin data; add pull-ups and ESD protection.
- [ ] PM02D: read the label (INA228 at 0x45, or INA226 at 0x41).

## 6. Open questions for me

- [ ] What does `Revision: v1.0` in the README header mean (board rev or README rev)?
- [ ] Should Pixhawk 6X Rev 8 be added as a sensor reference next to 6C (SYS-002, REF-01)?
