# What Next

**Updated:** 2026-10-31
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, 2026-10-31); ERC and review open | P2-019, OPEN-006, OPEN-011, OPEN-023 |
| Z2 Servo power rail (6 V bus, XT30) | Not drawn | Not started | OPEN-007, OPEN-021, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | Not drawn | Pins allocated (P1-001), not drawn | P1-001, P1-006 to P1-008, P1-014 |
| Z4 F100 IO MCU (px4io) | Not drawn | Pins allocated (P1-002), not drawn | P1-002, P1-014, P2-014 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | Not drawn | Library starting points only | OPEN-004, OPEN-013, OPEN-019, P2-012 |
| Z6 External connectors and outputs (telemetry, GPS, I2C, ESC and servo headers, spare outputs) | Not drawn | Pinouts not checked | OPEN-018, OPEN-023, P2-013, P2-015, P2-018 |
| Z7 PCB and mechanical | `AO-Horizon.kicad_pcb` | 27 × 29 mm placeholder outline, no footprints | OPEN-009, P3-001 |

## 1. Git

- [x] Hardware answers, spec 0.14 (`2b89d07`), merged to `main` in PR #17.
- [x] Team website merged to `main` in PRs #18 to #24; title image and logos on `dev`.
- [x] Consistency pass (spec 0.15) and DEC-025 (spec 0.16) merged to `main` in PR #27.
- [ ] `block_diagram.kicad_sch`: the working copy holds only its title text; the drawing is gone. Keep it cleared on purpose, or restore it from Git.
- [x] TPS259251DRC eFuse change and the spec 0.18 docs pass merged to `main` in PR #30 (`cce0b2b`).
- [x] Power sheet close-out, spec 0.19 and the generated outputs merged to `main` in PR #31 (`2d90af3`); `main` merged back into `dev` (`6ff99b7`, not pushed yet).
- [ ] Commit the spec 0.20 docs pass (PG labels, C111), the README KiCad 10.0.8 header and this file, then push `dev`.
- [ ] `documents/export_jobset.log` stays untracked: ignore it or delete it.

## 2. Zone Z1: Power supply (`power_supplies.kicad_sch`)

Capture declared complete on 2026-10-31. See spec 4.3 "Schematic state" (31 parts, annotated, as committed in `895c26a`) and P2-019 for the findings.

Done:
- [x] TPS259251DRC eFuse, 2 A target (DEC-026), with EN/UVLO, ILIM and dV/dT wired (2026-10-29).
- [x] eFuse values checked against TI SLVSCQ3B (NotebookLM `TPS25925x eFuse`, 2026-10-31): 1.75 / 2.1 / 2.45 A, about 5 ms ramp, UVLO 4.3 V, 6.1 V clamp, auto-retry (P2-017 done, OPEN-012 closed).
- [x] `+3V3A` LDO: TPS73533DRBR (DEC-027, 2026-10-31).
- [x] C111 soft-start: 10 nF, about 5 ms (DEC-028); 3.3 nF part number removed, 0402 (2026-10-31).
- [x] PG renamed: local label `3V3_PG`, hierarchical label `3V3_DONE` (2026-10-31).
- [x] TPS62142 AVIN 100 nF; 0.33 µH ASMPH-0603-R33M-T input inductor (2026-10-29).
- [x] Footprints on every part, all parts annotated (2026-10-31).

Open:
- [ ] Add a `3V3_DONE` sheet pin on the power sheet symbol in `top_hierarchical`, and expect an ERC warning for two names on one net (P2-019).
- [ ] Put the `+VIN` label back on the input net (now `Net-(CN101-Pin_1)`) (P2-019).
- [ ] Fill MFR, MFR.P/N and LCSC on R101 to R104, C103, C111, C118, CN101 and D101 (P2-019). Passive part numbers: your choice, later. C118 (LDO NR) needs a low-leakage dielectric (TI: C0G).
- [ ] Change the PM02D connector from JST-GH to a 6-pin 2.00 mm CLIK-Mate (decided 2026-10-24, OPEN-023, P2-015).
- [ ] Plan the USB OR-ing so USB cannot drive the eFuse OUT above its VIN: the eFuse has no reverse blocking (OPEN-006). Check the VBUS budget: USB feeds all external 5 V ports.
- [ ] `+3V3A` follow-ups (OPEN-011): check the IMU SPI levels against the H743 on `+3V3`, and the power-up order.
- [ ] Check the 3.3 µH PCR0420-3R3-M saturation current and the 3 × 10 µF output against TI Table 9-2, and the damping of the 0.33 µH input filter.
- [ ] Optional style: no-connect markers on LDO pins 2, 6 and 7 (pins are no_connect type).
- [ ] Run ERC, then ask Claude for a `sch-review` of `power_supplies.kicad_sch`.

## 3. Zone Z2: Servo power rail

Not drawn. Servo current passes through the board (DEC-019).

- [ ] Check the board-mount XT30 rating against 10 A continuous and 15 A peak (OPEN-021, P2-016).
- [ ] Size the 6 V and servo GND copper, pick where servo GND joins logic GND (away from the sensors), and add bulk capacitors (OPEN-021).
- [ ] 8 × 3-pin servo headers (signal, +6 V, GND) on the bussed 6 V rail (DEC-019).
- [ ] Servo rail divider on F100 PA4: match the px4io 3:1 scaling (IF-050).
- [ ] Wait for the team's servo stall current (OPEN-007, P0-022).

## 4. Zone Z3: H743 main MCU

Not drawn. Pins in pin allocation rev 0.6 (P1-001).

- [ ] Human review of the pin choices (P1-001).
- [ ] 16 MHz crystal part and load capacitors (P1-014).
- [ ] Reset topology, NRST pad, BOOT0 (P1-007, P1-014).
- [ ] Debug: Pixhawk Debug Mini 6-pin JST-SH (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND) plus an NRST pad. Check the pin order against DS-009 if you can get it (P1-008).
- [ ] USB FS: connector, VBUS sensing, ESD (P1-006); OR-ing with the PM02D 5 V is in Z1.
- [ ] SDMMC1 microSD: pull-ups and ESD protection.
- [ ] Buzzer (TIM3_CH3) and the 3 board LEDs: pick the drive parts and resistors.

## 5. Zone Z4: F100 IO MCU (px4io)

Not drawn. Pins from `px4/io-v2` (P1-002).

- [ ] F100 library part from stock `MCU_ST_STM32F1:STM32F100C8Tx`, and the block diagram text (P2-014).
- [ ] 24 MHz crystal part and load capacitors (P1-014).
- [ ] px4io LEDs (blue PB14, amber PB15, green PA11): pick the resistors.
- [ ] PA10 and PB11: weak pull-up to 3.3 V; pick the value.
- [ ] BOOT0 and BOOT1 (PB2) pulled down.
- [ ] Debug pads: SWDIO, SWCLK, NRST, GND, USART1 TX (PA9).

## 6. Zone Z5: Sensors

Not drawn. Parts decided (DEC-008, DEC-010, DEC-011); library starting points only.

- [ ] BMP581: Fig. 32 pad sizes and the pin 1 corner (Fig. 29, 30) on `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y`; no solder mask under it, 20 µm clearance (DS004-13 §8.2) (P2-012).
- [ ] ICP-20100: land pattern (AN-000140) and pin 1 corner (P2-012).
- [ ] IST8310: check the stock `LGA-16_3x3mm_P0.5mm` footprint and pin 1 corner against the package drawing (P2-012).
- [ ] BMP384 fallback: compare footprint and pinout with the BMP581 (P1-015, OPEN-019). Address 0x76, SDO low.
- [ ] ICM-45686 pin 9 unused: confirm NC or tie to VDDIO in the datasheet (the IMU record note is `NOT_VERIFIED`).
- [ ] I2C2 pull-ups and SPI chip-selects (P1-003 to P1-005).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).

## 7. Zone Z6: External connectors and outputs

Not drawn.

- [ ] Connector pinouts against the Pixhawk standard DS-009: Telemetry 1 and 2, GPS1 10-pin (3.3 V and buzzer pins), airspeed, TF-Luna (OPEN-023, P2-015).
- [ ] Telemetry 2 (USART1, PB14, PB15): JST-GH 6-pin, as Telemetry 1.
- [ ] I2C4 (PD12, PD13): check 5 V tolerance in case a module pulls up to 5 V (OPEN-023).
- [ ] ESC connectors: 4 × 3-pin headers with the + pin removed (IF-040 to IF-043, P2-018).
- [ ] PWM pull-downs: pick the value so bidirectional DShot still works on the motor lines (P2-013, OPEN-018).
- [ ] Spare outputs PD14, PD15, PE9: pads only.
- [ ] PM02D label (INA228 at 0x45, or INA226 at 0x41): asked in the integration questions parts table.

## 8. Zone Z7: PCB and mechanical

- [ ] Board outline: the saved PCB has a 27 × 29 mm placeholder rectangle (drawn, not decided). Pick the outline under MEC-001, cable entry sides and dampers at placement, then send them to the CAD team (OPEN-009, MEC-002 to MEC-004).
- [ ] Forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount.

## 9. Waiting on the team

Pinmap review 0.3 and the integration answers are applied (spec rev 0.12 to 0.14).

- [x] Send integration questions rev 0.1 (P0-021). Answered and applied 2026-10-24.
- [ ] Send `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.4 to the team (P0-022). It asks only D13 (Skywalker ESCs look PWM-only: how do the motors stop on an H743 hang?), the parts table and test results.
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team bench tests, not hardware work: RC-loss failsafe over ELRS MAVLink (S5); ESC on signal loss (OPEN-017, P4-011); servo current and stall current (OPEN-007).

## 10. Team website

From `web/HANDOFF.md`. The site follows the records; a design change still goes into the spec first.

- [ ] Review the rest of the live site: Overview, Interface view, detail panel, search. List changes.
- [ ] Check the fuchsia +3.3V rail colour on screen (between GPIO pink and UART purple).
- [ ] Check the light theme on the pinout page and the Board view.
- [ ] Keep `web/src/data/topology.ts` in step with the spec: the build catches removed IDs, not new interfaces.
- [ ] Showcase page: 3D viewer, renders and photos once there is a PCB.
