# To Do

**Updated:** 2026-11-20
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review"), the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6) and a team pre-layout review of commit `2356489` (2026-11-19, kicad-cli 10.0.7; its ERC, field and pin-trace results are the team's, `NOT_VERIFIED` here). Datasheet and DS-009 checks by Claude (2026-11-19, spec 0.63: CMP-010, CMP-011, OPEN-021, OPEN-023, OPEN-028). References follow the 2026-11-19 16:03 save. Cleaned 2026-11-19: done items removed. Team review notes from Jakarin (`hardware/message.md`, dated 2026-11-20, commit `5ea77f9`): first-pass review of the MCU, sensor and USB sheets and the shared NRST finding; their results are the team's, `NOT_VERIFIED` here unless marked. Updated 2026-11-20 for commit `f40784c` (spec 0.67; `kicad-cli` netlist and preflight by Claude). Cleaned 2026-11-20: done items removed (D706 buzzer channel, C803 MFR field, D701 to D706 Datasheet field, oscillator LCSC codes; then CN706 pin order, DEC-072, and the 100 kΩ PWM pull-down, DEC-073). Updated again for the 2026-11-20 12:36 save (not committed; spec OPEN-039), and for the 12:56 and 13:01 saves (TP605 linked, NRST split with D201 and D301; spec OPEN-026, OPEN-039). Cleaned again 2026-11-20 for the 13:37 save (spec 0.68: DEC-074 to DEC-079 recorded; the human owner's KiCad ERC at 13:37 gives 0 errors, 0 warnings, `ERC.rpt` not committed). `sch-review` of `mcu-main-fc` and `mcu-io` by Claude (2026-11-20, commit `6b01a14`, KiCad closed): `sch-inspect` local-net on U201 and U301 (all 148 pins connected), `kicad-cli` netlist, NotebookLM (DS12110 Rev 11, AN4879, DocID16455 Rev 9, RM0041) and PX4 v1.16.2 source; a targeted review, not a PASS.

## MAJOR

None open. (The `sch-review` of the sensor and USB sheets on 2026-11-20 raised IST8310 RSTN; it has an internal pull-up, so it is not a defect.) (The PA9 VBUS MAJOR from the 2026-11-20 `sch-review` is fixed in the 14:21 save, DEC-080.)

## MINOR

- [ ] MINOR | ICP-20100, ICM-45686 land patterns | `NOT_VERIFIED` | Body, pad count, pitch, pad width and pad numbers match the datasheets (check 2026-11-20). Pad length, keep-out and pin 1 corner need TDK AN-000393 (ICM-45686) and AN-000140 (ICP-20100), which are not in the notebooks. U501 corner pads are 0.125 mm apart with 0 mask margin. | Download both app notes from the TDK product pages; Claude adds them to the notebooks with approval and re-checks. Check the fab mask-bridge minimum. (OPEN-004, P2-012)

## INFO

- [ ] INFO | New project libraries (`0_Resistor`, `0_Capacitor`, `0_Inductor`, `0_LED`, `0_Conn_PinHeader`, `0_MountingHole`, `0_TestPoint`, `Conn_01x03`) | `NOT_VERIFIED` | Preflight found no missing 3D model or unresolved link, but `/kicad-link-audit` has not run on commit `f40784c`. The generic R, C, L, LED and Conn symbols have no Footprint field, as expected for generic parts. The 12:36 and 13:01 saves add `TestPoint_Pad_D2.0mm` and `0_Diode:D_Schottky` (both staged in Git, not committed) and use `0_Conn:SolderPad` and the stock `Connector:TestPoint` symbol; the spare pads use the `CN` prefix and the debug pads `TP` (OPEN-039 item 4). | Run `/kicad-link-audit`; pick one prefix. (spec 4.6)
- [ ] INFO | Q701 drain / `GPS1_BUZZER_B` | `ASSUMED` | No flyback diode on the board. The GPS is V1 with an onboard buzzer (DEC-070), but its type is not stated. If it is magnetic and the module has no diode, the drain sees a spike at turn-off. | Check the GPS module, or add a diode from the drain to `+5V`. (OPEN-023)
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 88 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | R825, R826 (R813, R814 before the 2026-11-20 save) / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | CN704 (TF-Luna) | `VERIFIED` (DS-009) | DS-009 has no 4-pin UART port; its 4-pin JST-GH port is CAN (VCC, CAN_H, CAN_L, GND). | Label CN704 clearly on the silkscreen. (OPEN-023)
- [ ] INFO | U302 / F100 PD0 | `VERIFIED` / `ESTIMATED` | ASDDV symmetry 45 to 55 % equals the F100 limit (zero margin); 24 MHz + 50 ppm is 24.0012 MHz, 1.2 kHz over the F100 24 MHz maximum. Same clock as stock px4io. | Accept, or pick a ±20 or ±25 ppm code (J or R). (OPEN-028, CMP-010)
- [ ] INFO | D807 / `+6V` | `VERIFIED` (MDD SMF7.5A via NotebookLM) | VRWM 7.5 V against the 7.4 V servo maximum leaves 0.1 V; the 12.9 V clamp is below C803's 16 V. | Fine at 6 V; at 7.4 V check the UBEC maximum output. (CMP-011, OPEN-021)
- [ ] INFO | U303 / `0_Logic_74x:SN74LVC1G34DCK` | `NOT_VERIFIED` | Committed in `1993716` and the link audit is clean; the pin map is not checked against the datasheet. | Check the U303 pin map (`/component-check`).
- [ ] INFO | D903 / `LED_MAIN_GREEN_B` (H743 PE4) | `VERIFIED` (PX4 v1.16.2 `px4/fmu-v6c` `board_config.h`, `led.c`) | fmu-v6c drives only red (PD10, overload) and blue (PD11, armed state), active low; it has no green LED entry, so D903 stays off with the stock LED code. The F100 green D906 is off when armed and breathes when disarmed (px4io, DEC-079). | Tell the software team: name PE2 to PE4 in the board config, add the green LED entry and pick what it shows. (IF-047)
- [ ] INFO | D902, D903, D905, D906 | `VERIFIED` (`kicad-cli` netlist, 13:37 save) | The blue and green LEDs have an empty Datasheet field; the red ones (D901, D904) link the LCSC data sheet. | Fill in the Datasheet field. (DEC-067, DEC-079)
- [ ] INFO | C201 to C311 (100n, 2u2, 4u7) | `VERIFIED` (CAD); ratings from LCSC | The `Rate` field is empty on every MCU-sheet capacitor except the 10 nF parts. LCSC pages (2026-11-20): C85858 GCM155R71H104KE02D 50 V X7R, C576485 GRM188Z71C225KE43D 16 V, C389010 GRM188Z71C475KE21D 16 V (part numbers from the page titles, ratings from a page summary); all rails are 3.3 V or lower, so the ratings are fine. | Fill in the `Rate` field.
- [ ] INFO | C301, C214, C215, MCU 100 nF | `VERIFIED` (DocID16455 Rev 9 Figure 10, DS12110 Rev 11 Table 15 via NotebookLM) | Layout notes: C301 4.7 µF must connect at F100 VDD3 (pin 48); C214 and C215 need ESR under 100 mΩ (MLCC normally meets it, `ASSUMED`); each 100 nF close to its VDD pin. | Apply at placement (P3).
- [ ] INFO | U301 PA12 / `F1_PA12` | `VERIFIED` (PX4 v1.16.2 io-v2 `board_config.h` line 130) | px4io sets PA12 as a floating timer input (`GPIO_TIM_RSSI`); on this board it is unconnected. | Keep PWM RSSI off in PX4, or add a pull-down.
- [ ] INFO | U201 PA9 / `USB_FS_VBUS` | `VERIFIED` (DS12110 Table 11 footnote 4, Table 50; PX4 v1.16.2 fmu-v6c `board_config.h` line 202) | With the R603 5k1 / R604 10k divider PA9 reads high with or without the PX4 pull-down (2.81 to 3.28 V with it on, `ESTIMATED`). | Tell the software team: PA9 as a plain input with no pull-down and `VBDEN` off is preferred; bench-check PA9 and USB detection (P4). (DEC-080)

- [ ] INFO | C218 (2u2, C576485) | `VERIFIED` (`kicad-cli` netlist, 14:29 save) | `Rate` field empty; GRM188Z71C225KE43D is 16 V. | Fill in `16V`. (DEC-081)
- [ ] INFO | U601 USBLC6-2SC6 (C7519) | `NOT_VERIFIED` | D+ and D- reach the MCU only through the U601 links (pins 1 to 6, 3 to 4); the ST page timed out, so the pinout is not checked on the ST datasheet. | Check the ST datasheet pin diagram. (DEC-084, OPEN-010)
- [ ] INFO | U503 IST8310 | `VERIFIED` (IST8310 V1.8 §3.5, `sch-review` subagent) | Re-POR needs AVDD below 0.1 V for 10 ms, so a short USB replug may not reset it. | Tell the software team: soft-reset the IST8310 at driver start.
- [ ] INFO | U501 power-up order | `ESTIMATED` | VDDIO is up about 0.5 ms before VDD; accepted (DEC-085). | Bench check of baro start-up (P4-015).

## Not checked yet (need data)

- [ ] CN101 PM02D pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D documentation; DS-009 has only an analog power port (OPEN-023).
- [ ] Servo plug contact rating on CN801 to CN803 (about 2.1 A per pin at stall; the Samtec TSW rating applies only with Samtec sockets) and servo tolerance of the 12.9 V D807 clamp (OPEN-021, CMP-011).
- [ ] Device-side pinouts of the SiK V3 and the GPS V1: Holybro shows them only as images (OPEN-023).
