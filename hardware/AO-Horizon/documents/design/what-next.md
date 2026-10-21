# What Next

**Updated:** 2026-10-22
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 1. Git

- [ ] Push `dev` to `origin` (2 local commits: `ead5c2e`, `6cfbf11`).
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
- [ ] BMM150: A1 corner, mirroring, and the missing 3D model.

## 4. Waiting on the team

- [ ] Is BMP581 (LCSC C5362283) confirmed as barometer 2? (OPEN-014, P0-009)
- [ ] Did the pinout come from Pixhawk 6C, 6X or both? What board was "it works" tested on? Then fix the source note in `AO-HORIZON_PIN_ALLOCATION_EN.md`.
- [ ] Correct the F103 TIM3_CH5 to CH8 labels for COAX and AIL (OPEN-003). TIM3 has CH1 to CH4 only.
- [ ] Does the F103 run stock PX4 IO firmware or custom firmware? This sets its pins and the USART protocol (OPEN-002, SAF-001).

## 5. Open questions for me

- [ ] What does `Revision: v1.0` in the README header mean (board rev or README rev)?
- [ ] Should Pixhawk 6X Rev 8 be added as a sensor reference next to 6C (SYS-002, REF-01)?
