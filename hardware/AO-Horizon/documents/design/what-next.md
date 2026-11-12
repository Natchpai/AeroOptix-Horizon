# What Next

**Updated:** 2026-11-12
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, 2026-10-31); eFuse replaced by the TPS2121 power mux (2026-11-01); mux status LED, OV and ST dividers, input capacitors and LDO enable from PG set (2026-11-03); ERC run and `sch-review` done, P2-019 closed, 5 V budget closed, CN101 is CLIK-Mate (2026-11-03) | OPEN-023, OPEN-025 |
| Z2 Servo power rail (6 V bus, XT30) | Not drawn | Not started | OPEN-007, OPEN-021, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | `main_mcu.kicad_sch` | Started (2026-11-11): MCU symbol, VDD decoupling, VDDA and VREF+ RC filters from `+3V3`, BOOT0 resistors; every GPIO on a local `H7_<pin>` stub label. NRST on hierarchical label `RESET_B` with 100 nF (2026-11-12). Gaps in section 4 (`sch-inspect`, 2026-11-12) | P1-001, P1-006 to P1-008, P1-014, DEC-025 |
| Z4 F100 IO MCU (px4io) | `io_mcu.kicad_sch` | Started (2026-11-11): MCU symbol, VDD decoupling, VDDA RC filter from `+3V3`, BOOT0 resistors; GPIOs on local `F1_<pin>` stub labels. NRST on hierarchical label `RESET_B` with 100 nF (2026-11-12) | P1-002, P1-014, P2-014 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | `sensor-imu.kicad_sch`, `sensor-barometer.kicad_sch` | Started (2026-11-12): U401, U402 ICM-45686; U501 ICP-20100, U502 BMP581. Rails decided (DEC-043); bus on I2C2; 1 conflict with the spec in section 6 (IMU INT1). Magnetometer not drawn | DEC-043, OPEN-011, SEN-002, P1-003, P1-004, OPEN-004, OPEN-013, OPEN-019, P2-012 |
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

Started on 2026-11-11. Pins in pin allocation rev 0.6 (P1-001).

On the saved sheet (`sch-inspect` of the 13:56 save, 2026-11-12, sheet-local evidence only; KiCad was open): U? STM32H743VITx; 5 × 100 nF on `+3V3` for the 5 VDD pins; VBAT on `+3V3`; VDDA (`H7_VDDA`) through 22 Ω from `+3V3` with 100 nF to `GND`; VREF+ (`H7_VREF`) through a second 22 Ω from `+3V3` with 100 nF to `GND`; BOOT0 10 kΩ to `GND` (fitted) and 10 kΩ to `+3V3` (DNP). The sheet no longer uses `+3V3A`, so DEC-025 holds. Every GPIO, VCAP and PH0/PH1 sits on a local stub label only.

Change in the 23:34 save (`sch-inspect`, 2026-11-12, `VERIFIED` from the saved file, drawn, not decided): NRST (pin 14) moved from the `NRST` stub to hierarchical label `RESET_B`, with a new 100 nF from `RESET_B` to `GND`. The "Main MCU" sheet symbol on `top_hierarchical.kicad_sch` has no sheet pins, so `RESET_B` does not leave the sheet yet. References are not annotated.

H743 values below are from ST DS12110 Rev 11 via NotebookLM (2026-11-12).

- [ ] VREF+: the two separate 22 Ω filters let VREF+ sit above VDDA, because VDDA carries the ADC current (about 16 mV at 720 µA typ for one ADC, `ESTIMATED`). Tables 77 and 174 allow VREF+ only up to VDDA (`VERIFIED`). Fix: delete the VREF+ 22 Ω and tie VREF+ (pin 20) to `H7_VDDA` (Fig. 41).
- [ ] VDDA/VREF+ decoupling: add 1 µF on the node, keep 100 nF at each pin (1 µF // 100 nF, Fig. 40/41, `VERIFIED`).
- [ ] Record the VDDA/VREF+ RC filter from `+3V3` as a decision in the spec (your choice, for cost).
- [ ] VCAP: pins 48 and 73 are on `H7_VCAP` with no capacitor. Add 2 × 2.2 µF, ±20 %, ESR < 100 mΩ (Table 15, `VERIFIED`).
- [ ] Bulk capacitor: add 1 × 4.7 µF on `+3V3` near the MCU (Fig. 15: N × 100 nF + 1 × 4.7 µF, `VERIFIED`).
- [ ] Human review of the pin choices (P1-001).
- [ ] 16 MHz crystal part and load capacitors on PH0/PH1 (P1-014). Only the `H7_PH0` and `H7_PH1` stubs are drawn.
- [ ] Reset topology (P1-014, TST-001): the 100 nF on `RESET_B` is drawn. Still open: the NRST pad, and whether the H743 and F100 share one reset net. Each sheet has its own `RESET_B` hierarchical label and neither sheet symbol has a pin, so today they are 2 separate nets. Record the choice in the spec.
- [ ] BOOT0: the DNP pull-up gives selection by rework only. Decide if that meets FUN-006 and TST-003 ("selectable and observable"), or add a pad, jumper or button (P1-007).
- [ ] Replace the `H7_<pin>` stubs with function names from the pin allocation, and add the hierarchical or global labels that carry signals to the other sheets (F100 link, sensors, connectors, power). Then add the matching sheet pins on `top_hierarchical.kicad_sch`: today only "Power Supplies" has pins (`3V3_PG`, `PM02_SCL`, `PM02_SDA`).
- [ ] Mark unused pins with no-connect flags once the allocation is final (PA10, PA15, PB3, PB4 and the other free pins).
- [ ] Annotate U?, C? and R?.
- [ ] Debug: Pixhawk Debug Mini 6-pin JST-SH (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND) on USART3 PD8/PD9 and SWD PA13/PA14 (only stubs drawn), plus an NRST pad. Check the pin order against DS-009 if you can get it (P1-008).
- [ ] Wire `3V3_PG` to the H743 as an input only (it also drives the `+3V3A` LDO EN, DEC-039). Pin allocation rev 0.6 gives it no H743 pin yet: pick one.
- [ ] USB FS on PA11/PA12, VBUS sense on PA9 (only stubs drawn): connector, VBUS sensing (PA9 FT_u divider question, pin allocation F-06), ESD (P1-006); USB-C CC resistors so a USB-C source turns on VBUS (DEC-038); then remove the temporary `PWR_FLAG` on `VBUS` from the power sheet; OR-ing with the PM02D 5 V is the TPS2121 in Z1; `VBUS` already enters the power sheet from a power symbol.
- [ ] SDMMC1 microSD (PC8 to PC12, PD2; only stubs drawn): socket, pull-ups and ESD protection.
- [ ] Buzzer (TIM3_CH3, PB0) and the 3 board LEDs (PE2 to PE4, active low): pick the drive parts and resistors. Only stubs drawn.

## 5. Zone Z4: F100 IO MCU (px4io)

Started on 2026-11-11. Pins from `px4/io-v2` (P1-002).

- [ ] F100 library part from stock `MCU_ST_STM32F1:STM32F100C8Tx`, and the block diagram text (P2-014).
- [ ] 24 MHz crystal part and load capacitors (P1-014).
- [ ] VDDA (`F1_VDDA`): 22 Ω from `+3V3` with only 100 nF. Add 1 µF (Fig. 35 shows 1 µF // 10 nF; DocID16455 Rev 9 via NotebookLM, `VERIFIED`). Table 8 says VDDA "must be the same potential as VDD" (`VERIFIED`); the note allowing up to 300 mV of difference is `NOT_VERIFIED` (not in the cited text). Expected drop about 20 mV with the ADC on (0.8 mA, `ESTIMATED`).
- [ ] px4io LEDs (blue PB14, amber PB15, green PA11): pick the resistors.
- [ ] PA10 and PB11: weak pull-up to 3.3 V; pick the value.
- [ ] BOOT0 and BOOT1 (PB2) pulled down.
- [ ] NRST (pin 7) is on hierarchical label `RESET_B` with a new 100 nF to `GND` (2026-11-12, drawn, not decided). Shared or separate reset with the H743: see the reset item in section 4.
- [ ] Debug pads: SWDIO, SWCLK, NRST, GND, USART1 TX (PA9).

## 6. Zone Z5: Sensors

Started on 2026-11-12. Parts decided (DEC-008, DEC-010, DEC-011). Both sheets are on `top_hierarchical.kicad_sch` with no sheet pins, so no sensor signal reaches the H743 yet. Magnetometer (IST8310) not drawn.

On the saved sheets (`sch-inspect` of the 23:34 save, 2026-11-12, sheet-local evidence only; all drawn, not decided):
- `sensor-imu.kicad_sch`: U401 and U402 ICM-45686. VDD on `+3V3A`, VDDIO on `+3V3`, RESV (pin 7) on `GND`, 100 nF on each of VDD and VDDIO (C401 to C404). SPI on `IMU1_SPI_*` / `IMU2_SPI_*` labels, carried by bus labels `{IMU1_SPI}` and `{IMU2_SPI}` (bus aliases in `AO-Horizon.kicad_pro`). INT1, INT2 (pin 9) and the AUX1 pins have no-connect flags.
- `sensor-barometer.kicad_sch`: U501 ICP-20100 and U502 BMP581. VDD on `+3V3A`, VDDIO on `+3V3`, 100 nF each (C501 to C504). Bus labels `BARO_I2C2_SCL` / `BARO_I2C2_SDA` (renamed from `BARO_I2C4_*` in `2f77b2f`) with 5k pull-ups to `+3V3` (R501, R502). ICP-20100 CSB tied to `+3V3`; AD0 5k to `GND` (R504, fitted) and 5k to `+3V3` (R503, DNP). BMP581 CSB 100k to `+3V3` (R507); SA0 5k to `GND` (R506, fitted) and 5k to `+3V3` (R505, DNP). INT pins have no-connect flags.

Conflicts with the spec (`VERIFIED` against the saved files and the spec text):
- [x] Sensor rails: settled by DEC-043 (2026-11-12, replaces DEC-025). VDD of every sensor on `+3V3A`, VDDIO on `+3V3`, as drawn.
- [x] Barometer bus: labels renamed to `BARO_I2C2_SCL` / `BARO_I2C2_SDA` (2026-11-12, `2f77b2f`), matching SEN-002 and DEC-010. The bus still has no sheet pin to the H743.
- [ ] MAJOR | U401, U402 / INT1 | INT1 has a no-connect flag, but the pin allocation gives IMU1 INT1 to PC4 and IMU2 INT1 to PE15 (P1-003, DRDY). Wire INT1 out, or change the allocation.

To do:
- [ ] Barometer address straps: check that AD0 low gives 0x63 on the ICP-20100 and SA0 low gives 0x46 on the BMP581 (SEN-002), in NotebookLM (`NOT_VERIFIED`).
- [ ] I2C pull-ups (P1-004): one set per bus, sized for the IST8310 too once it is on the same bus. 5k is not an E24 or E96 value; pick 4.7k, 4.99k or 5.1k.
- [ ] Sensor decoupling: only 100 nF per supply pin is drawn. Check each datasheet's recommended capacitors (`NOT_VERIFIED`).
- [ ] Add sheet pins for the IMU SPI buses and the barometer I2C bus on `top_hierarchical.kicad_sch`.
- [ ] Draw the IST8310 (P1-005, DEC-011).
- [ ] Power-up order (OPEN-011): with DEC-039, VDDIO (`+3V3`) comes up before VDD (`+3V3A`). Check in NotebookLM that each sensor allows this (ICM-45686, ICP-20100, BMP581, IST8310).
- [ ] `+3V3A` load: add ICP-20100, BMP581 and IST8310 VDD currents to the power budget (3.3 V_IMU rows are `TBD`).
- [ ] IST8310 AVDD on the LDO: check the TPS73533DRBR output tolerance against the 3.6 V absolute maximum (OPEN-004).
- [ ] Sync the checklist to DEC-043 (README synced 2026-11-12).
- [ ] BMP581: Fig. 32 pad sizes and the pin 1 corner (Fig. 29, 30) on `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y`; no solder mask under it, 20 µm clearance (DS004-13 §8.2) (P2-012).
- [ ] ICP-20100: land pattern (AN-000140) and pin 1 corner (P2-012).
- [ ] IST8310: check the stock `LGA-16_3x3mm_P0.5mm` footprint and pin 1 corner against the package drawing (P2-012).
- [ ] BMP384 fallback: compare footprint and pinout with the BMP581 (P1-015, OPEN-019). Address 0x76, SDO low.
- [ ] ICM-45686 pin 9 unused: drawn with a no-connect flag. Confirm NC or tie to VDDIO in the datasheet (the IMU record note is `NOT_VERIFIED`).
- [ ] SPI chip-selects (P1-003); I2C2 pull-ups are covered above (P1-004, P1-005).
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
