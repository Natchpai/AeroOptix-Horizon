# To Do

**Updated:** 2026-11-20
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review"), the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6) and a team pre-layout review of commit `2356489` (2026-11-19, kicad-cli 10.0.7; its ERC, field and pin-trace results are the team's, `NOT_VERIFIED` here). Datasheet and DS-009 checks by Claude (2026-11-19, spec 0.63: CMP-010, CMP-011, OPEN-021, OPEN-023, OPEN-028). References follow the 2026-11-19 16:03 save. Cleaned 2026-11-19: done items removed. Team review notes from Jakarin (`hardware/message.md`, dated 2026-11-20, commit `5ea77f9`): first-pass review of the MCU, sensor and USB sheets and the shared NRST finding; their results are the team's, `NOT_VERIFIED` here unless marked. Updated 2026-11-20 for commit `f40784c` (spec 0.67; `kicad-cli` netlist and preflight by Claude). Cleaned 2026-11-20: done items removed (D706 buzzer channel, C803 MFR field, D701 to D706 Datasheet field, oscillator LCSC codes; then CN706 pin order, DEC-072, and the 100 kΩ PWM pull-down, DEC-073). Updated again for the 2026-11-20 12:36 save (not committed; spec OPEN-039), and for the 12:56 and 13:01 saves (TP605 linked, NRST split with D201 and D301; spec OPEN-026, OPEN-039). Cleaned again 2026-11-20 for the 13:37 save (spec 0.68: DEC-074 to DEC-079 recorded; the human owner's KiCad ERC at 13:37 gives 0 errors, 0 warnings, `ERC.rpt` not committed).

## MAJOR

None open.

## MINOR

- [ ] MINOR | MCU, sensor and USB sheets | `NOT_VERIFIED` | Team first pass found OK: H743 and F100 decoupling, VDDA filters, VCAP 2 × 2.2 µF, BOOT0/BOOT1 pull-downs, HSE bypass inputs, H7↔F1 UART cross with 22 Ω, SPI1/SPI4 IMU direction and INT lines, I2C2 pull-ups, sensor straps (0x63, 0x46, 0x0C), IST8310 C1 4.7 µF, USB D+/D−, CC 5.1 kΩ, USBLC6-2SC6, VBUS sense, debug connectors. Not checked by the team: sensor decoupling values against each datasheet, IST8310 VPP pin, power-up order (OPEN-011). | Check the open points, and run `sch-review` on these sheets before layout (P2-009).
- [ ] MINOR | ICP-20100, ICM-45686 footprints | `NOT_VERIFIED` | Team list of items open before layout. ICP-20100 has no land pattern in its datasheet (BARO_MAG_SELECTION line 185); the ICM-45686 footprint is not checked against TDK AN-000393 (IMU_SELECTION line 91). | Check both footprints before layout (OPEN-004, P2-012).

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

## Not checked yet (need data)

- [ ] CN101 PM02D pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D documentation; DS-009 has only an analog power port (OPEN-023).
- [ ] Servo plug contact rating on CN801 to CN803 (about 2.1 A per pin at stall; the Samtec TSW rating applies only with Samtec sockets) and servo tolerance of the 12.9 V D807 clamp (OPEN-021, CMP-011).
- [ ] Device-side pinouts of the SiK V3 and the GPS V1: Holybro shows them only as images (OPEN-023).
