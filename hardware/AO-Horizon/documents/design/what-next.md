# What Next

**Updated:** 2026-11-19
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 0. To do later: found on 2026-11-19 (not yet in the spec)

Found by `/progress-update` on the saved files (2026-11-18 16:52 save, KiCad closed, not committed before this run), with `sch-inspect` and the preflight. The spec 4.2 "Schematic state" still describes the 2026-11-17 16:40 save. Decide each item, then ask Claude to record it.

Drawing issues:
- [ ] MAJOR | CN802, CN803 / `+6V` | `VERIFIED` | The + rows are swapped. CN802 (MAIN 1 to 4, ESCs, via R805 to R808) has `+6V` on pins 1b to 4b, but IF-040 says the ESC headers drop the + pin. CN803 (MAIN 5 to 8, control surfaces, via R809 to R812) has no-connect flags on pins 1b to 4b, so the surface servos get no power (DEC-019). CN801 (AUX 1 to 4, tilt servos) is on `+6V` as expected. With the DEC-054 adapter cable (signal and GND only) no ESC BEC reaches `+6V`, but IF-040 and OPEN-031 (1) still need the + pin removed.
- [ ] MAJOR | `Connector - Peripherals` sheet symbol | `VERIFIED` | The sheet symbol on `top_hierarchical` has no sheet pins, so none of the 14 hierarchical labels on `conn-peripherals` (TEL1, TEL2, GPS1 UART and I2C, RNG, `{EXT_I2C4}`, buzzer, safety) reach the MCU sheets. Add the sheet pins (P2-022, OPEN-032).
- [ ] MINOR | `mcu-io` sheet pins | `VERIFIED` | The `MCU - IO` sheet symbol still has `SAFETY_SW` and `SAFETY_LED_B`; the child labels are now `GPS1_SAFETY_SWITCH` and `GPS1_SAFTY_LED`. ERC will flag the mismatch. `SAFTY` also breaks the DEC-052 full-word rule (OPEN-032).
- [ ] MINOR | Q901 to Q903, D901 to D903 / `LED_RED`, `LED_BLUE`, `LED_GREEN` | `VERIFIED` | Each board LED is switched low-side by a 2SK3018W N-FET (22 Ω gate resistor, 10 kΩ gate pull-down), so the LED is on when the H743 pin is high. IF-047 and the `px4/fmu-v6c` LEDs are active low. Choose: set the LEDs active high in the board config, or drive the LEDs straight from the pins. R903, R906, R909 and D901, D902 have value `?`.
- [ ] INFO | `+6V` | `VERIFIED` | `+6V` has no source: only C801 to C804, the CN801 and CN802 + rows and R813 are on it. The XT30 UBEC input is not drawn (P2-016).
- [ ] MINOR | C208, C214, C215, C301, C307, C507 | `VERIFIED` (preflight) | No footprint.

Drawn, not decided (record in the spec when you agree):
- [ ] `conn-external` removed; `conn-peripherals` has CN701 and CN702 (TELEM 1 and 2, JST-GH 6-pin, pins 4 and 5 with no-connect flags, so CTS/RTS are unconnected as DEC-053 needs), CN703 (I2C4 airspeed, 4-pin), CN704 (rangefinder, 4-pin) and CN705 (GPS1, 10-pin: 5 V, TX, RX, SCL, SDA, safety switch, safety LED, 3.3 V, buzzer, GND), each signal through PESD4USB3BBTBR-Q ESD (D701 to D706) and 22 Ω, I2C pull-ups 5 kΩ to `+3V3` (R705, R706, R712, R713), 100 nF on `+5V` (C701 to C705). Pinouts against DS-009 still open (OPEN-023).
- [ ] `conn-actuator`: CN801 to CN803 Samtec TSW-104-08-F-T-RA (3-row right-angle, 4 positions each), 22 Ω (R801 to R812) and PESD5V0U2BT (D801 to D806) on each signal, 4 × 10 µF on `+6V`. Servo rail divider R813 46.4 kΩ / R814 23.2 kΩ with C805 100 nF (3:1, about 2.0 V at 6 V, `ESTIMATED`), which answers the missing divider in OPEN-033.
- [ ] `conn-usb-debug`: CN602 (H743) and CN603 (F100), JST-SH 6-pin `SM06B-SRSS-TB`, both in the Pixhawk Debug Mini order (1 VREF, 2 TX, 3 RX, 4 SWDIO, 5 SWCLK, 6 GND) with 22 Ω on each signal. H743 console on USART3 (PD8, PD9), F100 TX on PA9; CN603 pin 3 (`DBG_F1_RX`) reaches nothing. Still no NRST pad (OPEN-029). IF-051 said pads for the F100; now a connector.
- [ ] `user-interface`: reset button annotated B901; LEDs D901 to D903 with Q901 to Q903 (see the LED item above).
- [ ] `power_supplies`: D102 changed from PESD2USB3UV-T to PESD5V0U2BT (LCSC C85399) on the PM02D I2C lines at CN101.
- [ ] `mcu-main-fc`, `mcu-io`: passives annotated (C201 to C217, R201 to R208, C301 to C310, R301 to R309).
- [ ] RC IN (DEC-053) not drawn yet (P2-023). Waits for the buffer decision below.

Docs to catch up after the decisions: spec 4.2 and 4.3 for the 16:52 save, OPEN-023, OPEN-029, OPEN-031, OPEN-032, OPEN-033, and the checklist trackers. Then run `/progress-update`.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, P2-019) | P2-020, P2-021, OPEN-025 |
| Z2 Servo power rail (6 V bus, XT30) | Not drawn | Not started | OPEN-007, OPEN-021, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | `mcu-main-fc.kicad_sch`, `conn-usb-debug.kicad_sch`, `user-interface.kicad_sch` | In capture (spec 4.2 "Schematic state"); U201, U202 annotated, passives not | P1-001, P1-006 to P1-008, P1-014, P2-022, OPEN-026, OPEN-028, OPEN-029 |
| Z4 F100 IO MCU (px4io) | `mcu-io.kicad_sch` | In capture (spec 4.2 "Schematic state"); U301, U302 annotated, passives not | P1-002, P1-014, P2-014, P2-022, OPEN-026, OPEN-028, OPEN-029 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | `sensor-imu.kicad_sch`, `sensor-navigation.kicad_sch` | All five sensors drawn (U401, U402, U501, U502, U503; spec 4.2); rails per DEC-043; IST8310 at 0x0C (DEC-047) | DEC-043, OPEN-011, DEC-047, SEN-002, P1-003, P1-004, OPEN-004, OPEN-013, OPEN-019, P2-012 |
| Z6 External connectors and outputs (telemetry, GPS, I2C, ESC and servo headers, spare outputs) | `conn-external.kicad_sch` (5 JST-GH, not wired); actuator headers not drawn | Pinouts not checked; outputs per DEC-051 (MAIN 1 to 8, AUX 1 to 4) | OPEN-018, OPEN-023, OPEN-031, P2-013, P2-015, P2-018 |
| Z7 PCB and mechanical | `AO-Horizon.kicad_pcb` | 27 × 29 mm placeholder outline, no footprints | OPEN-009, P3-001 |

## 1. Git

Done items live in Git history and the changelog.

- [ ] `block_diagram.kicad_sch`: the working copy holds only its title text; the drawing is gone. Keep it cleared on purpose, or restore it from Git.

## 2. Zone Z1: Power supply

Done (2026-11-03). See spec 4.3 and DEC-029 to DEC-042. Resistor fields: section "Before the BOM"; bench checks: section "Bench".

## 3. Zone Z2: Servo power rail

Not drawn. Servo current passes through the board (DEC-019).

- [ ] Check the board-mount XT30 rating against PWR-011 and the 13.2 A all-stall estimate (OPEN-021, P2-016).
- [ ] Size the 6 V and servo GND copper, pick where servo GND joins logic GND (away from the sensors), and add bulk capacitors (OPEN-021).
- [ ] 8 × 3-pin servo headers (signal, +6 V, GND) on the bussed 6 V rail (DEC-019).
- [ ] Servo rail divider on F100 PA4: match the px4io 3:1 scaling (IF-050). Drawn so far: 22 Ω and 10 nF only (OPEN-033).
- [ ] Datasheet all-stall estimate: 13.2 A at 6 V (4 × DS3235 2.1 A + 4 × C507 1.2 A, OPEN-007), over the 10 A UBEC continuous rating. Wait for the team's bench current under load (P0-022) and their confirmation that the UBEC output plug is an XT30 (OPEN-021).

## 4. Zone Z3: H743 main MCU

Pins in the pin allocation (P1-001). Current state: spec 4.2 "Schematic state" (saved files, 2026-11-14).

H743 values below are from ST DS12110 Rev 11 via NotebookLM (2026-11-12).

- [x] VREF+ tied to VDDA on one 22 Ω RC filter from `+3V3` (DEC-049, drawn in the 17:35 save).
- [ ] Human review of the pin choices (P1-001).
- [ ] 16 MHz clock: CMOS oscillator U202 (DEC-044), part decided (DEC-048). Check its data against the HSE external-clock limits (OPEN-028). Firmware side: P1-017.
- [ ] Reset (DEC-046: one shared `RESET_B` for H743 and F100 NRST, one button): check the drawn button B? (LCSC C2689510) and its `B` reference prefix. Check in NotebookLM whether an internal reset (IWDG, software, debugger) drives NRST low on the H743 and F100; if so, an H743 reset also resets the F100 (OPEN-026, SAF-001). `3V3_PG` stays local (DEC-039). NRST is on H743 debug connector pin 4; the F100 pads have none (OPEN-029).
- [ ] BOOT0: the DNP pull-up gives selection by rework only. Decide if that meets FUN-006 and TST-003 ("selectable and observable"), or add a pad, jumper or button (P1-007).
- [ ] Net names (OPEN-032, DEC-052): choose for `OSC_16M00_OUT` and `OSC_24M00_OUT` (add `H7_`/`F1_`, or amend DEC-052); set the spare output order and update the pin allocation; add `DBG_UART3_*` members on `conn-usb-debug` with the debug pin set; info: `SS{slash}TR`, `3V3_LED_A`, `USB_FS_VBUS` carried twice. Then run ERC.
- [ ] Replace the remaining `H7_<pin>` stub labels with function names from the pin allocation, and carry the signals that leave the sheet through sheet pins.
- [ ] Mark unused pins with no-connect flags once the allocation is final (PA10, PA15, PB3, PB4 and the other free pins).
- [ ] Annotate the passives (P2-022).
- [ ] Debug: drawn as a 6-pin connector with SWDIO and SWCLK on pins 2 and 3, pins 4 and 5 open, no console and no NRST (16:40 save). The Pixhawk Debug Mini puts SWD on pins 4 and 5 and the console on 2 and 3; IF-045 also asks for an NRST pad. Decide the pin set (OPEN-029, P1-008).
- [ ] `3V3_PG` reaches no MCU pin now (local net, DEC-039). Decide if the H743 should read it; the pin allocation gives it no pin (OPEN-026).
- [ ] USB: VBUS reaches PA9 through 0 Ω with no divider; settle the PA9 FT_u question (pin allocation F-06, P1-006). Then remove the temporary `PWR_FLAG` on `VBUS` from the power sheet if ERC allows (P2-022).
- [ ] INFO | U601 / USB D+, D- | `NOT_VERIFIED` | On `conn-usb-debug` the data lines pass through U601 USBLC6-2SC6 (connector side on pins 1 and 3, MCU side on pins 6 and 4), so they depend on the internal link between pins 1-6 and 3-4. Check in the ST datasheet that those pin pairs are joined inside, or route D+ and D- past the pins on one net.
- [ ] INFO | R601, R602 / CC1, CC2 | `NOT_VERIFIED` | The CC pull-downs are 5 kΩ; the usual USB-C sink Rd is 5.1 kΩ. Check the allowed Rd range in the USB Type-C specification, or change to 5.1 kΩ.
- [ ] INFO | Library `0_Conn_Card:Micro_SD_Card_Det1`, `0_Conn_USB:USB_C_Receptacle_USB2.0_16P` | `VERIFIED` (preflight, 2026-11-14) | The library symbols have an empty Footprint field; the placed SD? and CN601 have footprints. Fill the library field or leave it generic, then run `/kicad-link-audit`.
- [ ] microSD: socket drawn; DET reaches no MCU pin; add CMD and DAT pull-ups and ESD (P2-022).
- [ ] Buzzer (TIM3_CH3, PB0) and the 3 board LEDs (PE2 to PE4, active low): pick the drive parts and resistors. Only stubs drawn.

## 5. Zone Z4: F100 IO MCU (px4io)

Pins from `px4/io-v2` (P1-002). Current state: spec 4.2 "Schematic state".

- [ ] F100 library part from stock `MCU_ST_STM32F1:STM32F100C8Tx`, and the block diagram text (P2-014).
- [ ] 24 MHz clock: CMOS oscillator U302 (DEC-044), part decided (DEC-048). Check its data against the HSE external-clock limits (OPEN-028). Custom px4io build: P1-017.
- [ ] VDDA (`F1_VDDA`): 22 Ω from `+3V3` with only 100 nF. Add 1 µF (Fig. 35 shows 1 µF // 10 nF; DocID16455 Rev 9 via NotebookLM, `VERIFIED`). Table 8 says VDDA "must be the same potential as VDD" (`VERIFIED`); the note allowing up to 300 mV of difference is `NOT_VERIFIED` (not in the cited text). Expected drop about 20 mV with the ADC on (0.8 mA, `ESTIMATED`).
- [ ] px4io LEDs (blue PB14, amber PB15, green PA11): pick the resistors.
- [ ] PA10 and PB11: weak pull-up to 3.3 V; pick the value.
- [ ] NRST (pin 7) on the shared `RESET_B` (DEC-046); the internal-reset check is in Z3 (OPEN-026).
- [ ] Debug pads: drawn as 4 pads (VREF, SWDIO, SWCLK, GND), no NRST and no console TX (PA9). Decide the pin set (OPEN-029, P1-008).

## 6. Zone Z5: Sensors

Parts decided (DEC-008, DEC-010, DEC-011). Current state: spec 4.2 "Schematic state": all five sensors drawn, rails per DEC-043, IMU SPI and INT1 lines and I2C2 (`NAV_I2C2_*`) reach the H743.

- [x] IST8310 address: 0x0C as strapped (DEC-047). The software team sets 0x0C in the PX4 start script (P1-018).

To do:
- [ ] Barometer address straps: check in NotebookLM that AD0 low on the ICP-20100 and SA0 low on the BMP581 give the SEN-002 addresses (`NOT_VERIFIED`).
- [ ] I2C pull-ups (P1-004): one set for I2C2, sized for all three devices. 5k is not an E24 or E96 value; pick 4.7k, 4.99k or 5.1k.
- [ ] Sensor decoupling: only 100 nF per supply pin is drawn. Check each datasheet's recommended capacitors (`NOT_VERIFIED`).
- [ ] IST8310 C507: add a footprint (P2-022).
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

Not drawn.

- [ ] Connector pinouts against the Pixhawk standard DS-009: Telemetry 1 and 2, GPS1 10-pin (3.3 V and buzzer pins), airspeed, TF-Luna (OPEN-023, P2-015).
- [ ] Telemetry 2 (USART1, PB14, PB15): JST-GH 6-pin, as Telemetry 1.
- [ ] Decide on the team RC IN proposal (OPEN-034 item 5): 74LVC1G17 buffer on `+3V3` (1 kΩ in, 100 kΩ to `GND`, 22 Ω out, 100 nF) instead of the 6.2 kΩ / 10 kΩ divider. If yes: amend DEC-053, IF-038, F-21, P2-023 and P4-016, and add the part with `kicad-part-start` (datasheet values `NOT_VERIFIED`, notebook upload needs your approval). If no: the team measures the FS-iA6B PPM level first.
- [ ] RC IN per DEC-053 (or the buffer if accepted): CN706 1x3 header, input circuit, `RCIN_TIM1_CH1` to F100 PA8 (P2-023, OPEN-034).
- [ ] I2C4 (PD12, PD13): check 5 V tolerance in case a module pulls up to 5 V (OPEN-023).
- [ ] Actuator headers per DEC-051: MAIN 1 to 4 ESC headers (3-pin, + pin removed), MAIN 5 to 8 and AUX 1 to 4 servo headers on the 6 V bus; keep them apart (IF-030 to IF-043, P2-018, OPEN-031).
- [ ] PWM pull-downs: pick the value (P2-013, OPEN-018; no DShot since DEC-050).
- [ ] Spare outputs PD14, PD15, PE9: pads only.
- [ ] PM02D monitor chip and address: asked in the integration questions parts table (P0-022; pin allocation F-09).
- [ ] CN101 CLIK-Mate pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D cable and DS-009 (OPEN-023).

## 8. Zone Z7: PCB and mechanical

- [ ] Board outline: the saved PCB has a 27 × 29 mm placeholder rectangle (drawn, not decided). Pick the outline under MEC-001, cable entry sides and dampers at placement, then send them to the CAD team (OPEN-009, MEC-002 to MEC-004).
- [ ] Forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount.

## 9. Waiting on the team

Pinmap review 0.3 and the integration answers are applied (spec rev 0.12 to 0.14).

- [ ] Collect the rest of `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.5 from the team (P0-022): the parts table, test results and the ESC PWM rate (OPEN-031). D13 to D16 are answered (DEC-050, DEC-051).
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team inputs for DEC-053 and DEC-054: FS-iA6B current, PPM level and failsafe; Tekko32 8-pin pinout and the adapter cable (OPEN-034).
- [ ] Team bench tests, not hardware work: RC loss with the FS-iA6B in PPM mode (P4-016, replaces S5); ESC stop on the F100 failsafe pulse and the surface failsafe position (OPEN-017, P4-011); servo current and stall current (OPEN-007).

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
