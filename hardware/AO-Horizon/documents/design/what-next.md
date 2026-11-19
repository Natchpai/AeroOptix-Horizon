# What Next

**Updated:** 2026-11-19
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 0. Next up (2026-11-19, after commit `dbe3c61`)

Spec rev 0.53 is committed and pushed (DEC-056, DEC-057, RC IN drawn). The KiCad sheets and new library parts of the 15:25 save are not committed yet. Review findings with actions are in `todo.md`.

- [ ] Commit the 15:25 schematic and library changes (KiCad sheets, `sym-lib-table`, `SP3031-01E` symbol, SN74LVC1G34, Conn_01x03, JST-GH SM03B), after `/kicad-link-audit`.
- [ ] Re-run ERC: last run on the 12:49 save; since then Q701, R312, RC IN (CN706, D707, R714, U303) and the D706 changes (P2-022).
- [ ] CN706 RC IN connector: decide with your partner (OPEN-034 item 6a): keep the JST-GH (pin 1 `+5V`, 2 signal) and amend DEC-053, or go back to the 2.54 mm servo header with PPM on pin 1 (section 7, P2-023).
- [ ] C803 and C102 10 V tantalum (OPEN-021): see `todo.md`.
- [ ] Next review: the MCU, sensor and USB sheets (P2-022).
- [ ] Datasheet checks (NotebookLM source or your values; a new source needs your approval):
  - XT30PW-M current rating against the 13.2 A all-stall estimate (OPEN-021).
  - D807 SMF7.5CA: breakdown voltage and leakage at 7.4 V (PWR-011, OPEN-021).
  - D706 PESD4USB3BBTBR-QZ standoff against the 0~5 V buzzer line (OPEN-037).
  - LED forward voltage and current through 220 Ω, and the H743 pin sink current (OPEN-035).
- [ ] Decide the drawn blocks (spec 4.2), then ask Claude to record them:
  - Peripheral connectors CN701 to CN705 (OPEN-023).
  - Actuator headers CN801 to CN803 and the XT30 input CN804 with its bulk capacitors and TVS (OPEN-021, OPEN-031, P2-016, P2-018).
  - Servo rail divider R813, R814, C804 (OPEN-033).
  - Debug connectors CN602 and CN603, no NRST (OPEN-029).
  - Board LEDs D901 to D903 (OPEN-035).
- [ ] INFO | CN603 pin 3 / `DBG_F1_RX` | `ASSUMED` | Single-use label, so it likely reaches no MCU pin (OPEN-029).

After design work: `/progress-update light`; before a commit: `/progress-update sync`.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, P2-019) | P2-020, P2-021, OPEN-025 |
| Z2 Servo power rail (6 V bus, XT30) | `conn-actuator.kicad_sch` | Drawn, not decided (spec 4.2): CN804 XT30, bulk capacitors, D807 TVS, rail divider | OPEN-007, OPEN-021, OPEN-033, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | `mcu-main-fc.kicad_sch`, `conn-usb-debug.kicad_sch`, `user-interface.kicad_sch` | In capture (spec 4.2 "Schematic state"); U201, U202 and passives annotated | P1-001, P1-006 to P1-008, P1-014, P2-022, OPEN-026, OPEN-028, OPEN-029 |
| Z4 F100 IO MCU (px4io) | `mcu-io.kicad_sch` | In capture (spec 4.2 "Schematic state"); U301, U302 and passives annotated | P1-002, P1-014, P2-014, P2-022, OPEN-026, OPEN-028, OPEN-029 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | `sensor-imu.kicad_sch`, `sensor-navigation.kicad_sch` | All five sensors drawn (U401, U402, U501, U502, U503; spec 4.2); rails per DEC-043; IST8310 at 0x0C (DEC-047) | DEC-043, OPEN-011, DEC-047, SEN-002, P1-003, P1-004, OPEN-004, OPEN-013, OPEN-019, P2-012 |
| Z6 External connectors and outputs (telemetry, GPS, I2C, ESC and servo headers, spare outputs) | `conn-peripherals.kicad_sch` (CN701 to CN706), `conn-actuator.kicad_sch` (CN801 to CN804) | Drawn, not decided (spec 4.2); pinouts not checked; RC IN parts decided (DEC-056, DEC-057), CN706 connector open | OPEN-018, OPEN-023, OPEN-031, OPEN-034, OPEN-037, P2-013, P2-015, P2-018, P2-023 |
| Z7 PCB and mechanical | `AO-Horizon.kicad_pcb` | 27 × 29 mm placeholder outline, no footprints | OPEN-009, P3-001 |

## 1. Git

Done items live in Git history and the changelog.

- [ ] `block_diagram.kicad_sch`: the working copy holds only its title text; the drawing is gone. Keep it cleared on purpose, or restore it from Git.

## 2. Zone Z1: Power supply

Done (2026-11-03). See spec 4.3 and DEC-029 to DEC-042. Resistor fields: section "Before the BOM"; bench checks: section "Bench".

## 3. Zone Z2: Servo power rail

Drawn on `conn-actuator` (11:38 save), not decided. Servo current passes through the board (DEC-019).

- [ ] Check the board-mount XT30 rating against PWR-011 and the 13.2 A all-stall estimate (OPEN-021, P2-016).
- [ ] Size the 6 V and servo GND copper, pick where servo GND joins logic GND (away from the sensors). Bulk drawn: 2 × 10 µF, 47 µF tantalum and the D807 TVS (OPEN-021).
- [ ] Servo rail divider on F100 PA4 (IF-050): R813 46.4 kΩ / R814 23.2 kΩ with C804 100 nF, 3:1, drawn. Confirm it (OPEN-033).
- [ ] Datasheet all-stall estimate: 13.2 A at 6 V (4 × DS3235 2.1 A + 4 × C507 1.2 A, OPEN-007), over the 10 A UBEC continuous rating. Wait for the team's bench current under load (P0-022) and their confirmation that the UBEC output plug is an XT30 (OPEN-021).

## 4. Zone Z3: H743 main MCU

Pins in the pin allocation (P1-001). Current state: spec 4.2 "Schematic state" (2026-11-19 12:30 save).

H743 values below are from ST DS12110 Rev 11 via NotebookLM (2026-11-12).

- [ ] Human review of the pin choices (P1-001).
- [ ] 16 MHz clock: CMOS oscillator U202 (DEC-044), part decided (DEC-048). Check its data against the HSE external-clock limits (OPEN-028). Firmware side: P1-017.
- [ ] Reset (DEC-046: one shared `RESET_B` for H743 and F100 NRST, one button): check the drawn button B901 PTS815SJM250SMTRLFS (LCSC C2689510) and its `B` reference prefix. Check in NotebookLM whether an internal reset (IWDG, software, debugger) drives NRST low on the H743 and F100; if so, an H743 reset also resets the F100 (OPEN-026, SAF-001). `3V3_PG` stays local (DEC-039). Neither debug connector (CN602, CN603) carries NRST (OPEN-029).
- [ ] BOOT0: the DNP pull-up gives selection by rework only. Decide if that meets FUN-006 and TST-003 ("selectable and observable"), or add a pad, jumper or button (P1-007).
- [ ] Net names (OPEN-032, DEC-052): choose for `OSC_16M00_OUT` and `OSC_24M00_OUT` (add `H7_`/`F1_`, or amend DEC-052); set the spare output order and update the pin allocation; add `DBG_UART3_*` members on `conn-usb-debug` with the debug pin set; info: `SS{slash}TR`, `3V3_LED_A`, `USB_FS_VBUS` carried twice. Then run ERC.
- [ ] Replace the remaining `H7_<pin>` stub labels with function names from the pin allocation, and carry the signals that leave the sheet through sheet pins.
- [ ] Mark unused pins with no-connect flags once the allocation is final (PA10, PA15, PB3, PB4 and the other free pins).
- [ ] Debug: CN602 JST-SH 6-pin in the Pixhawk Debug Mini order (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND; 16:52 save). IF-045 and TST-001 also ask for an NRST pad, not drawn. Decide (OPEN-029, P1-008).
- [ ] `3V3_PG` reaches no MCU pin now (local net, DEC-039). Decide if the H743 should read it; the pin allocation gives it no pin (OPEN-026).
- [ ] USB: VBUS reaches PA9 through 0 Ω with no divider; settle the PA9 FT_u question (pin allocation F-06, P1-006). Then remove the temporary `PWR_FLAG` on `VBUS` from the power sheet if ERC allows (P2-022).
- [ ] INFO | U601 / USB D+, D- | `NOT_VERIFIED` | On `conn-usb-debug` the data lines pass through U601 USBLC6-2SC6 (connector side on pins 1 and 3, MCU side on pins 6 and 4), so they depend on the internal link between pins 1-6 and 3-4. Check in the ST datasheet that those pin pairs are joined inside, or route D+ and D- past the pins on one net.
- [ ] INFO | Library `0_Conn_Card:Micro_SD_Card_Det1`, `0_Conn_USB:USB_C_Receptacle_USB2.0_16P` | `VERIFIED` (preflight, 2026-11-14) | The library symbols have an empty Footprint field; the placed SD? and CN601 have footprints. Fill the library field or leave it generic, then run `/kicad-link-audit`.
- [ ] microSD: socket drawn; DET reaches no MCU pin; add CMD and DAT pull-ups and ESD (P2-022).
- [ ] Board LEDs drawn: direct drive, active low, 220 Ω from `+3V3`; check LED current (OPEN-035). No board buzzer: `BUZZER_TIM3_CH3` drives Q701, which switches GPS1 pin 9 (`GPS1_BUZZER_B`, 13:33 save; OPEN-037).

## 5. Zone Z4: F100 IO MCU (px4io)

Pins from `px4/io-v2` (P1-002). Current state: spec 4.2 "Schematic state".

- [ ] F100 library part from stock `MCU_ST_STM32F1:STM32F100C8Tx`, and the block diagram text (P2-014).
- [ ] 24 MHz clock: CMOS oscillator U302 (DEC-044), part decided (DEC-048). Check its data against the HSE external-clock limits (OPEN-028). Custom px4io build: P1-017.
- [ ] VDDA (`F1_VDDA`): 22 Ω from `+3V3` with C307 2.2 µF and 100 nF (spec 4.2). Confirm the value against Fig. 35 (Fig. 35 shows 1 µF // 10 nF; DocID16455 Rev 9 via NotebookLM, `VERIFIED`). Table 8 says VDDA "must be the same potential as VDD" (`VERIFIED`); the note allowing up to 300 mV of difference is `NOT_VERIFIED` (not in the cited text). Expected drop about 20 mV with the ADC on (0.8 mA, `ESTIMATED`).
- [ ] px4io LEDs (blue PB14, amber PB15, green PA11): pick the resistors.
- [ ] PA10 and PB11: weak pull-up to 3.3 V; pick the value.
- [ ] NRST (pin 7) on the shared `RESET_B` (DEC-046); the internal-reset check is in Z3 (OPEN-026).
- [ ] Debug: CN603 JST-SH 6-pin in the Debug Mini order replaces the pads (16:52 save); no NRST; pin 3 `DBG_F1_RX` likely reaches no MCU pin. Decide (OPEN-029, P1-008).

## 6. Zone Z5: Sensors

Parts decided (DEC-008, DEC-010, DEC-011). Current state: spec 4.2 "Schematic state": all five sensors drawn, rails per DEC-043, IMU SPI and INT1 lines and I2C2 (`NAV_I2C2_*`) reach the H743. IST8310 at 0x0C (DEC-047). I2C2 pull-ups R501, R502 5.1 kΩ; bus capacitance not checked.

- [ ] Barometer address straps: check in NotebookLM that AD0 low on the ICP-20100 and SA0 low on the BMP581 give the SEN-002 addresses (`NOT_VERIFIED`).
- [ ] Sensor decoupling: only 100 nF per supply pin is drawn. Check each datasheet's recommended capacitors (`NOT_VERIFIED`).
- [ ] Power-up order (OPEN-011): with DEC-039, VDDIO (`+3V3`) comes up before VDD (`+3V3A`). Check in NotebookLM that each sensor allows this (ICM-45686, ICP-20100, BMP581, IST8310).
- [ ] `+3V3A` load: add ICP-20100, BMP581 and IST8310 VDD currents to the power budget (3.3 V_IMU rows are `TBD`).
- [ ] IST8310 AVDD on the LDO: check the TPS73533DRBR output tolerance against the 3.6 V absolute maximum (OPEN-004).
- [ ] BMP581: Fig. 32 pad sizes and the pin 1 corner (Fig. 29, 30) on `Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y`; no solder mask under it, 20 µm clearance (DS004-13 §8.2) (P2-012).
- [ ] ICP-20100: land pattern (AN-000140) and pin 1 corner (P2-012).
- [ ] IST8310: check the stock `LGA-16_3x3mm_P0.5mm` footprint and pin 1 corner against the package drawing (P2-012).
- [ ] BMP384 fallback: compare footprint and pinout with the BMP581 (P1-015, OPEN-019). Address per SEN-002.
- [ ] ICM-45686 pin 9 unused: drawn with a no-connect flag. Confirm NC or tie to VDDIO in the datasheet (the IMU record note is `NOT_VERIFIED`).
- [ ] SPI chip-selects (P1-003); I2C2 pull-ups are covered above (P1-004, P1-005).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).

## 7. Zone Z6: External connectors and outputs

Drawn on `conn-peripherals` and `conn-actuator`, not decided (spec 4.2). Actuator headers per DEC-051 (CN802 ESC headers without the + pin; CN801, CN803 on the 6 V bus): keep them apart at layout (IF-030 to IF-043, P2-018, OPEN-031). RC IN drawn (CN706, D707, R714 on `conn-peripherals`; U303, R310, R311, C311 on `mcu-io`); U303, R714 and D707 decided (DEC-057). I2C4 pins PD12 and PD13 are FT (OPEN-023).

- [ ] Connector pinouts against the Pixhawk standard DS-009: Telemetry 1 and 2, GPS1 10-pin, airspeed, TF-Luna (OPEN-023, P2-015). Signal levels done: all 3.3 V, GPS1 pin 9 `BUZZER-` 0~5 V (Holybro Pixhawk 6X page).
- [ ] CN706 against DEC-053 (OPEN-034 item 6a, P2-023): JST-GH 1.25 mm with pin 1 `+5V` as drawn, against the 2.54 mm servo header with PPM on pin 1. You decide with your partner later.
- [ ] RC IN part data, only if you want evidence for DEC-057 (NotebookLM source needs your approval, or your values): U303 5.5 V input tolerance and I<sub>off</sub>; D707 working voltage against a 5 V PPM high (OPEN-034).
- [ ] PWM pull-downs: pick the value (P2-013, OPEN-018; no DShot since DEC-050).
- [ ] Spare outputs PD14, PD15, PE9: routed to `conn-peripherals` through `{SPARE_TIM}` (12:49 save); pads not drawn.
- [ ] PM02D monitor chip and address: asked in the integration questions parts table (P0-022; pin allocation F-09).
- [ ] CN101 CLIK-Mate pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D cable and DS-009 (OPEN-023).

## 8. Zone Z7: PCB and mechanical

- [ ] Board outline: the saved PCB has a 27 × 29 mm placeholder rectangle (drawn, not decided). Pick the outline under MEC-001, cable entry sides and dampers at placement, then send them to the CAD team (OPEN-009, MEC-002 to MEC-004).
- [ ] Forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount.

## 9. Waiting on the team

Pinmap review 0.3 and the integration answers are applied (spec rev 0.12 to 0.14).

- [ ] Collect the rest of `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.6 from the team (P0-022): the parts table, test results and the ESC PWM rate (OPEN-031). D13 to D16 are answered (DEC-050, DEC-051).
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team inputs for DEC-053 and DEC-054: FS-iA6B current, PPM level and failsafe; Tekko32 8-pin pinout and the adapter cable (OPEN-034).
- [ ] Team bench tests, not hardware work: RC loss with the FS-iA6B in PPM mode (P4-016, replaces S5); ESC stop on the F100 failsafe pulse and the surface failsafe position (OPEN-017, P4-011); servo current and stall current (OPEN-007).

## 10. Before the BOM

- [ ] Resistor MFR and MFR.P/N on the power sheet (P2-021); LCSC codes are in since the 12:26 save. Use 1 % parts in the PR1, CP2, OV and ST dividers (DEC-055).

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
