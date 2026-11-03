# What Next

**Updated:** 2026-11-03
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, 2026-10-31); eFuse replaced by the TPS2121 power mux (2026-11-01); mux status LED, OV and ST dividers, input capacitors and LDO enable from PG set (2026-11-03); ERC run and `sch-review` done, P2-019 closed, 5 V budget closed, CN101 is CLIK-Mate (2026-11-03) | OPEN-023, OPEN-025 |
| Z2 Servo power rail (6 V bus, XT30) | Not drawn | Not started | OPEN-007, OPEN-021, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | Not drawn | Pins allocated (P1-001), not drawn | P1-001, P1-006 to P1-008, P1-014 |
| Z4 F100 IO MCU (px4io) | Not drawn | Pins allocated (P1-002), not drawn | P1-002, P1-014, P2-014 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | Not drawn | Library starting points only | OPEN-004, OPEN-013, OPEN-019, P2-012 |
| Z6 External connectors and outputs (telemetry, GPS, I2C, ESC and servo headers, spare outputs) | Not drawn | Pinouts not checked | OPEN-018, OPEN-023, P2-013, P2-015, P2-018 |
| Z7 PCB and mechanical | `AO-Horizon.kicad_pcb` | 27 × 29 mm placeholder outline, no footprints | OPEN-009, P3-001 |

## 1. Git

Done items live in Git history and the changelog.

- [ ] `block_diagram.kicad_sch`: the working copy holds only its title text; the drawing is gone. Keep it cleared on purpose, or restore it from Git.
- [ ] Review and squash-merge draft PR #34 (spec 0.25 to 0.33), then merge `main` back into `dev`.

## 2. Zone Z1: Power supply

Done (2026-11-03). See spec 4.3 and DEC-029 to DEC-042. Resistor fields: section "Before the BOM"; bench checks: section "Bench".

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
- [ ] Wire `3V3_PG` to the H743 as an input only (it also drives the `+3V3A` LDO EN, DEC-039).
- [ ] USB FS: connector, VBUS sensing, ESD (P1-006); USB-C CC resistors so a USB-C source turns on VBUS (DEC-038); then remove the temporary `PWR_FLAG` on `VBUS` from the power sheet; OR-ing with the PM02D 5 V is the TPS2121 in Z1; `VBUS` already enters the power sheet from a power symbol.
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
- [ ] CN101 CLIK-Mate pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D cable and DS-009 (OPEN-023).

## 8. Zone Z7: PCB and mechanical

- [ ] Board outline: the saved PCB has a 27 × 29 mm placeholder rectangle (drawn, not decided). Pick the outline under MEC-001, cable entry sides and dampers at placement, then send them to the CAD team (OPEN-009, MEC-002 to MEC-004).
- [ ] Forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount.

## 9. Waiting on the team

Pinmap review 0.3 and the integration answers are applied (spec rev 0.12 to 0.14).

- [ ] Send `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.4 to the team (P0-022). It asks only D13 (Skywalker ESCs look PWM-only: how do the motors stop on an H743 hang?), the parts table and test results.
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team bench tests, not hardware work: RC-loss failsafe over ELRS MAVLink (S5); ESC on signal loss (OPEN-017, P4-011); servo current and stall current (OPEN-007).

## 10. Before the BOM

- [ ] Resistor MFR, MFR.P/N and LCSC on the power sheet (P2-021). Use 1 % parts in the PR1, CP2, OV and ST dividers.

## 11. Bench, after the board is built

- [ ] On USB, measure ST and check D103 is fully off, cold and warm (P4-012, OPEN-025).
- [ ] Hot-plug the PM02D and scope `PM02_5V` and `+5V`; check the tantalum after repeated plugs (P4-013, DEC-037).
- [ ] On a USB-C port above 1 A with all external devices, check `+5V` (P4-014, DEC-038).
- [ ] Scope `+3V3` and `+3V3A` at power-up; IMUs answer after every cold start (P4-015, DEC-039).

## 12. Team website

From `web/HANDOFF.md`. The site follows the records; a design change still goes into the spec first.

- [ ] Review the rest of the live site: Overview, Interface view, detail panel, search. List changes.
- [ ] Check the fuchsia +3.3V rail colour on screen (between GPIO pink and UART purple).
- [ ] Check the light theme on the pinout page and the Board view.
- [ ] Keep `web/src/data/topology.ts` in step with the spec: the build catches removed IDs, not new interfaces.
- [ ] Showcase page: 3D viewer, renders and photos once there is a PCB.
