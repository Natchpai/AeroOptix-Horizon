# What Next

**Updated:** 2026-11-20
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth. This list only points to their IDs.

## 0. Next up (2026-11-19, after commit `fe46bcf`)

Spec rev 0.55 and the 16:03 save are committed and pushed (`bdb398d`, `fe46bcf`); the link audit was clean. ERC on the 16:03 save is clean (human owner) and the `{ESC}`, `{SURFACE}`, `{AUX_TIM5}`, `{EXT_I2C4}` bus links are traced; spec rev 0.56 is committed (`0cb73b5`). The other eight bus links are traced too (spec rev 0.57, not committed); `sch-inspect` 1.2.0 follows buses (`17af47b`). Review findings with actions are in `todo.md`.

- [ ] Re-run ERC after the next schematic change (P2-009); last clean KiCad run on the 2026-11-20 13:37 save (`ERC.rpt`), and `kicad-cli` ERC is clean on the 13:49 save.
- [x] CN706 RC IN pin order: kept as drawn, pin 1 `+5V`, 2 PPM, 3 `GND` (DEC-072, 2026-11-20). The receiver lead stays open (OPEN-034 item 1).
- [ ] Next review: the MCU, sensor and USB sheets (P2-022).
- [x] D706 on CN705 pin 9: the 5 V buzzer line exceeded the PESD4USB3BBTBR-Q ±3.3 V VRWM limit (MAJOR). Pin 9 is now on D707 SP3031-01ETG (DEC-071, CMP-012).
- [ ] Decide the drawn blocks (spec 4.2), then ask Claude to record them:
  - Peripheral connectors CN701 to CN705 (OPEN-023).
  - Actuator headers CN801 to CN803 and the XT30 input CN804 with its bulk capacitors and TVS (OPEN-021, OPEN-031, P2-016, P2-018).
- [x] TP605 `RESET_B` linked in the 12:56 save (OPEN-039).

After design work: `/progress-update light`; before a commit: `/progress-update sync`.

## Zone list

The board is split into design zones. Each zone below has its own to-do list.

| Zone | Sheet | State | Main open items |
| ---- | ----- | ----- | --------------- |
| Z1 Power supply | `power_supplies.kicad_sch` | Capture done (P2-011, P2-019) | P2-020, P2-021, OPEN-025 |
| Z2 Servo power rail (6 V bus, XT30) | `conn-actuator.kicad_sch` | Drawn, not decided (spec 4.2): CN804 XT30, bulk capacitors, D807 TVS, rail divider (DEC-066) | OPEN-021, P2-016 |
| Z3 H743 main MCU (core, clock, reset, BOOT0, debug, USB, microSD) | `mcu-main-fc.kicad_sch`, `conn-usb-debug.kicad_sch`, `user-interface.kicad_sch` | In capture (spec 4.2 "Schematic state"); U201, U202 and passives annotated | P1-001, P1-006 to P1-008, P1-014, P2-022, OPEN-026, OPEN-028 |
| Z4 F100 IO MCU (px4io) | `mcu-io.kicad_sch` | In capture (spec 4.2 "Schematic state"); U301, U302 and passives annotated | P1-001, P1-014, P2-022, OPEN-026, OPEN-028 |
| Z5 Sensors (2 × IMU, 2 × barometer, magnetometer) | `sensor-imu.kicad_sch`, `sensor-navigation.kicad_sch` | All five sensors drawn (U401, U402, U501, U502, U503; spec 4.2); rails per DEC-043; IST8310 at 0x0C (DEC-047) | DEC-043, OPEN-011, DEC-047, SEN-002, P1-003, OPEN-004, P2-012 |
| Z6 External connectors and outputs (telemetry, GPS, I2C, ESC and servo headers, spare outputs) | `conn-peripherals.kicad_sch` (CN701 to CN706), `conn-actuator.kicad_sch` (CN801 to CN804) | Drawn, not decided (spec 4.2); pinouts not checked; RC IN parts decided (DEC-056, DEC-057), CN706 connector open | OPEN-031, OPEN-023, OPEN-034, P2-015, P2-018, P2-023 |
| Z7 PCB and mechanical | `AO-Horizon.kicad_pcb` | 80 × 80 mm working area on `Edge.Cuts` (not the outline), no footprints | OPEN-009, P3-001 |

## 1. Git

Done items live in Git history and the changelog.

- [ ] `block_diagram.kicad_sch`: the working copy holds only its title text; the drawing is gone. Keep it cleared on purpose, or restore it from Git.

## 2. Zone Z1: Power supply

Done (2026-11-03). See spec 4.3 and DEC-029 to DEC-042. Resistor fields: section "Before the BOM"; bench checks: section "Bench".

## 3. Zone Z2: Servo power rail

Drawn on `conn-actuator` (11:38 save), not decided. Servo current passes through the board (DEC-019).

- [ ] Check the board-mount XT30 rating against PWR-011 and the 13.2 A all-stall estimate (OPEN-021, P2-016).
- [ ] Size the 6 V and servo GND copper, pick where servo GND joins logic GND (away from the sensors). Bulk drawn: 2 × 10 µF, 68 µF 16 V tantalum (DEC-058) and the D807 SMF7.5A TVS (DEC-059) (OPEN-021).
- [ ] Datasheet all-stall estimate: 13.2 A at 6 V (4 × DS3235 2.1 A + 4 × C507 1.2 A, OPEN-021), over the 10 A UBEC continuous rating. Wait for the team's bench current under load (P0-022) and their confirmation that the UBEC output plug is an XT30 (OPEN-021).

## 4. Zone Z3: H743 main MCU

Pins in the pin allocation (P1-001). Current state: spec 4.2 "Schematic state" (2026-11-19 12:30 save).

H743 values below are from ST DS12110 Rev 11 via NotebookLM (2026-11-12).

- [ ] Human review of the pin choices (P1-001).
- [ ] 16 MHz clock: CMOS oscillator U202 (DEC-044), part decided (DEC-048). Data meets the H743 HSE bypass limits (CMP-010). Firmware side: P1-017.
- [ ] Reset: check the drawn button B901 PTS815SJM250SMTRLFS (LCSC C2689510) and its `B` reference prefix (OPEN-026). NRST split with D201 and D301 BAT54XV2T1G behind B901 decided 2026-11-20 (DEC-074, amends DEC-046); bench check of the reset paths in P4. `3V3_PG` stays local (DEC-039). CN602 carries no NRST (DEC-065); the F100 has TP605 `RESET_B` (DEC-075).
- [ ] BOOT0: the DNP pull-up gives selection by rework only. Decide if that meets FUN-006 and TST-003 ("selectable and observable"), or add a pad, jumper or button (P1-007).
- [ ] Net names (OPEN-032): `OSC_*` names and the spare order are decided (DEC-064); left: info `SS{slash}TR`, `3V3_LED_A`, `USB_FS_VBUS` carried twice. Then run ERC.
- [ ] Replace the remaining `H7_<pin>` stub labels with function names from the pin allocation, and carry the signals that leave the sheet through sheet pins.
- [ ] Mark unused pins with no-connect flags once the allocation is final (PA10, PA15, PB3, PB4 and the other free pins).
- [ ] `3V3_PG` reaches no MCU pin now (local net, DEC-039). Decide if the H743 should read it; the pin allocation gives it no pin (OPEN-026).
- [ ] USB: PA9 VBUS divider done (DEC-080). Remove the temporary `PWR_FLAG` on `VBUS` from the power sheet if ERC allows (P2-022).
- [ ] INFO | U601 / USB D+, D- | `NOT_VERIFIED` | U601 is now the ST part, LCSC C7519 (DEC-084). On `conn-usb-debug` the data lines pass through U601 USBLC6-2SC6 (connector side on pins 1 and 3, MCU side on pins 6 and 4), so they depend on the internal link between pins 1-6 and 3-4. Check in the ST datasheet that those pin pairs are joined inside, or route D+ and D- past the pins on one net.
- [ ] INFO | Library `0_Conn_Card:Micro_SD_Card_Det1`, `0_Conn_USB:USB_C_Receptacle_USB2.0_16P` | `VERIFIED` (preflight, 2026-11-14) | The library symbols have an empty Footprint field; the placed SD? and CN601 have footprints. Fill the library field or leave it generic, then run `/kicad-link-audit`.
- [ ] microSD: 10 kΩ pull-ups on CMD and DAT0 to DAT3, no DET pull-up, no card detect (DEC-078); ESD still open (P2-022).
- [ ] Board LEDs decided as drawn (DEC-067); check brightness on the bench. No board buzzer: `BUZZER_TIM3_CH3` drives Q701, which switches GPS1 pin 9 (`GPS1_BUZZER_B`, 13:33 save; OPEN-023).

## 5. Zone Z4: F100 IO MCU (px4io)

Pins from `px4/io-v2` (P1-001). Current state: spec 4.2 "Schematic state".

- [ ] 24 MHz clock: CMOS oscillator U302 (DEC-044), part decided (DEC-048). Data meets the F100 HSE bypass limits, with zero duty-cycle margin (CMP-010, OPEN-028). Custom px4io build: P1-017.
- [ ] VDDA (`F1_VDDA`): 22 Ω from `+3V3` with C307 2.2 µF and 100 nF (spec 4.2). Confirm the value against Fig. 35 (Fig. 35 shows 1 µF // 10 nF; DocID16455 Rev 9 via NotebookLM, `VERIFIED`). Table 8 says VDDA "must be the same potential as VDD" (`VERIFIED`); the note allowing up to 300 mV of difference is `NOT_VERIFIED` (not in the cited text). Expected drop about 20 mV with the ADC on (0.8 mA, `ESTIMATED`).
- [x] px4io LEDs: blue PB14 (D905), red PB15 in place of amber (D904), green PA11 (D906), 220 Ω, active low (DEC-079).
- [x] PA10 and PB11: 10 kΩ pull-ups R314 and R313 (DEC-079).
- [x] NRST (pin 7) on `F1_RESET_B`, to B901 through D301 (DEC-074).
- [x] Debug: test pads TP601 to TP606, TP605 on `RESET_B` (DEC-075).

## 6. Zone Z5: Sensors

Parts decided (DEC-008, DEC-010, DEC-011). Current state: spec 4.2 "Schematic state": all five sensors drawn, rails per DEC-043, IMU SPI and INT1 lines and I2C2 (`NAV_I2C2_*`) reach the H743. IST8310 at 0x0C (DEC-047). I2C2 pull-ups R501, R502 5.1 kΩ; bus capacitance not checked.

- [ ] Barometer address straps: check in NotebookLM that AD0 low on the ICP-20100 and SA0 low on the BMP581 give the SEN-002 addresses (`NOT_VERIFIED`).
- [ ] Sensor decoupling: only 100 nF per supply pin is drawn. Check each datasheet's recommended capacitors (`NOT_VERIFIED`).
- [ ] Power-up order (OPEN-011): with DEC-039, VDDIO (`+3V3`) comes up before VDD (`+3V3A`). Check in NotebookLM that each sensor allows this (ICM-45686, ICP-20100, BMP581, IST8310).
- [ ] `+3V3A` load: add ICP-20100, BMP581 and IST8310 VDD currents to the power budget (3.3 V_IMU rows are `TBD`).
- [ ] IST8310 AVDD on the LDO: check the TPS73533DRBR output tolerance against the 3.6 V absolute maximum (OPEN-004).
- [x] BMP581 and IST8310 footprints confirmed by you on 2026-11-19 (spec 0.62), with a 30 µm solder mask margin on purpose (P2-012).
- [ ] ICP-20100: land pattern (AN-000140) and pin 1 corner (P2-012).
- [ ] ICM-45686: pad size and pin 1 corner against TDK AN-000393 (P2-012).
- [ ] BMP384 fallback: compare footprint and pinout with the BMP581 (P1-015, OPEN-004). Address per SEN-002.
- [ ] ICM-45686 pin 9 unused: drawn with a no-connect flag. Confirm NC or tie to VDDIO in the datasheet (the IMU record note is `NOT_VERIFIED`).
- [ ] SPI chip-selects (P1-003); I2C2 pull-ups are covered above (P1-003).
- [ ] Buy BMP581 early: DigiKey showed 0 in stock on 2026-10-08 (team note, not checked).

## 7. Zone Z6: External connectors and outputs

Drawn on `conn-peripherals` and `conn-actuator`, not decided (spec 4.2). Actuator headers per DEC-051 (CN802 ESC headers without the + pin; CN801, CN803 on the 6 V bus): keep them apart at layout (IF-030 to IF-043, P2-018, OPEN-031). RC IN drawn (CN706, D708, R715 on `conn-peripherals`; U303, R310, R311, C311 on `mcu-io`); U303, the 22 Ω (R714, now R715) and the SP3031-01ETG ESD diode decided (DEC-057, DEC-071; D707 until the 23:17 save). I2C4 pins PD12 and PD13 are FT (OPEN-023).

- [x] I2C4 pull-ups: R705 and R706 2 kΩ, a DS-009 deviation (DEC-077). Pin order of CN701 to CN703 and CN705 matches DS-009 (2026-11-19).
- [x] CN706 pin order kept as drawn (DEC-072, 2026-11-20).
- [ ] RC IN part data, only if you want evidence for DEC-057 (NotebookLM source needs your approval, or your values): U303 5.5 V input tolerance and I<sub>off</sub>; D707 working voltage against a 5 V PPM high (OPEN-034).
- [x] PWM pull-downs: 100 kΩ on all 15 lines (DEC-073, 2026-11-20); MCU reset-state check not run, bench check in P4-011.
- [ ] Spare outputs PE9, PD14, PD15 (SPARE1 to SPARE3, DEC-064): routed to `conn-peripherals` through `{SPARE_TIM}` (12:49 save). 22 Ω series and pull-downs drawn (2026-11-20, R716 to R721); pads CN707 to CN710 drawn as 2.0 mm SMD pads in the 12:36 save. Pick the pad footprint (DEC-069, OPEN-039, P2-018).
- [ ] PM02D monitor chip and address: asked in the integration questions parts table (P0-022; pin allocation F-09).
- [ ] CN101 CLIK-Mate pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D cable (DS-009 has no digital power port; OPEN-023).

## 8. Zone Z7: PCB and mechanical

- [ ] Board outline: the saved PCB has an 80 × 80 mm working-area rectangle on `Edge.Cuts`, not the outline. Pick the outline under MEC-001, cable entry sides and dampers at placement, then send them to the CAD team (OPEN-009, MEC-002 to MEC-004).
- [ ] Forward arrow on the silkscreen; USB-C and microSD on adjacent edges, reachable with the canopy open, with the H743 debug connector (MEC-003). M3, 3.2 mm holes, soft mount.

## 9. Waiting on the team

Pinmap review 0.3 and the integration answers are applied (spec rev 0.12 to 0.14).

- [ ] Collect the rest of `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` rev 0.6 from the team (P0-022): the parts table, test results and the ESC PWM rate (OPEN-031). D13 to D16 are answered (DEC-050, DEC-051).
- [ ] After the reply: ask Claude to apply it to the spec, power budget and checklist.
- [ ] Team inputs for DEC-053 and DEC-054: FS-iA6B current, PPM level and failsafe; Tekko32 8-pin pinout and the adapter cable (OPEN-034).
- [ ] Team bench tests, not hardware work: RC loss with the FS-iA6B in PPM mode (P4-016, replaces S5); ESC stop on the F100 failsafe pulse and the surface failsafe position (OPEN-017, P4-011); servo current and stall current (OPEN-021).

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
