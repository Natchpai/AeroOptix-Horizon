# To Do

**Updated:** 2026-11-19
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review"), the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6) and a team pre-layout review of commit `2356489` (2026-11-19, kicad-cli 10.0.7; its ERC, field and pin-trace results are the team's, `NOT_VERIFIED` here). Datasheet and DS-009 checks by Claude (2026-11-19, spec 0.63: CMP-010, CMP-011, OPEN-021, OPEN-023, OPEN-028). References follow the 2026-11-19 16:03 save. Cleaned 2026-11-19: done items removed.

## MAJOR

- [ ] MAJOR | CN706 / `RC_IN_TR` | `VERIFIED` (CAD) | CN706 is a 3-pin JST-GH 1.25 mm (footprint `JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal`, C514175) with pin 1 `+5V`, pin 2 signal, pin 3 `GND`. DEC-053, DEC-056 and P2-023 say a 1x3 2.54 mm right-angle header with pin 1 PPM, pin 2 `+5V`, pin 3 `GND`, so the FS-iA6B servo cable plugs in directly. The team review asks for that header. | Change CN706 to the 1x3 2.54 mm right-angle header (pin 1 PPM, 2 `+5V`, 3 `GND`), place it away from the `+6V` servo headers and label it "RC IN 5V" (P2-023, OPEN-031); or keep JST-GH and amend DEC-053. (OPEN-034 item 6a)
- [ ] MAJOR | MAIN 1 to 8, AUX 1 to 4, SPARE 1 to 3 / PWM lines | `VERIFIED` (spec 4.4) | Spec 4.4 asks for a weak pull-down on every PWM line, 15 in total since DEC-069. The team review found only the 22 Ω series resistors on the 12 MAIN and AUX lines (`NOT_VERIFIED` here); the spares have neither (`VERIFIED`, `sch-inspect`). | Pick the value and draw 15 pull-downs to `GND` (P2-018, OPEN-031 item 5); bench check in P4-011.
- [ ] MAJOR | SPARE1 to SPARE3 / `SPARE1_TIM1_CH1`, `SPARE2_TIM4_CH3`, `SPARE3_TIM4_CH4` | `VERIFIED` (`sch-inspect`) | Each spare net reaches only U201 (PE9, PD14, PD15); no pads are drawn, but IF-017 to IF-019 say pads only. | Draw per DEC-069 on `conn-peripherals`: one 4-pad row (SPARE1, SPARE2, SPARE3, GND), 22 Ω series per line (as R801, RC0402FR-0722RL, C114765) and the pull-down above. Confirm the pad footprint (proposed: 1x4 2.54 mm hole row, not fitted) and bring the pad part in with `kicad-part-start` and `kicad-link-audit`.
- [ ] MAJOR | D706 pin 5 (channel 4) / `GPS1_BUZZER_B`, CN705 pin 9 | `VERIFIED` (Nexperia PESD4USB3BBTBR-Q v.1, Tables 5 and 6, via NotebookLM) | VRWM is ±3.3 V as a limiting value and VBR is 5.5 V min at 1 mA. Pin 9 idles at 5 V when Q701 is off: above the limit and 0.5 V from breakdown. The other D701 to D706 channels carry 3.3 V and are fine. | Move pin 9 to a 5 V rated ESD channel or part, or drop ESD on that line. (OPEN-023, P2-015)

## MINOR

- [ ] MINOR | R705, R706 / `EXT_I2C4_SCL`, `EXT_I2C4_SDA` | `VERIFIED` (DS-009 rev 0.1.0, I2C port) | DS-009 says "1.5K pullup on autopilot"; the board has 5.1 kΩ to `+3V3` (OPEN-038 closed with 5.1 kΩ). | Pick 1.5 kΩ to follow the standard, or keep 5.1 kΩ and record the deviation. (OPEN-023)
- [ ] MINOR | C803 MFR field | `VERIFIED` (KEMET T495 datasheet via NotebookLM; CAD field) | MFR says Kyocera AVX; T495 is a KEMET series. The spec is corrected (0.63); the CAD field is not. | Set MFR to KEMET. (CMP-011)
- [ ] MINOR | D701 to D706 Datasheet field | `VERIFIED` (CAD field) | Value is PESD4USB3BBTBR-QZ, but the Datasheet field links `PESD4USB5BTBR-Q.pdf`, a different part. | Point it at the PESD4USB3BBTBR-Q data sheet. (OPEN-023)
- [ ] MINOR | MCU, sensor and USB sheets | `NOT_VERIFIED` | Not reviewed yet; the connector sheets are done. | Run `sch-review` on these sheets before layout (P2-009).

## INFO

- [ ] INFO | Q701 drain / `GPS1_BUZZER_B` | `ASSUMED` | No flyback diode on the board. The GPS is V1 with an onboard buzzer (DEC-070), but its type is not stated. If it is magnetic and the module has no diode, the drain sees a spike at turn-off. | Check the GPS module, or add a diode from the drain to `+5V`. (OPEN-023)
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 88 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | R813, R814 / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | CN704 (TF-Luna) | `VERIFIED` (DS-009) | DS-009 has no 4-pin UART port; its 4-pin JST-GH port is CAN (VCC, CAN_H, CAN_L, GND). | Label CN704 clearly on the silkscreen. (OPEN-023)
- [ ] INFO | U302 / F100 PD0 | `VERIFIED` / `ESTIMATED` | ASDDV symmetry 45 to 55 % equals the F100 limit (zero margin); 24 MHz + 50 ppm is 24.0012 MHz, 1.2 kHz over the F100 24 MHz maximum. Same clock as stock px4io. | Accept, or pick a ±20 or ±25 ppm code (J or R). (OPEN-028, CMP-010)
- [ ] INFO | D807 / `+6V` | `VERIFIED` (MDD SMF7.5A via NotebookLM) | VRWM 7.5 V against the 7.4 V servo maximum leaves 0.1 V; the 12.9 V clamp is below C803's 16 V. | Fine at 6 V; at 7.4 V check the UBEC maximum output. (CMP-011, OPEN-021)
- [ ] INFO | U303 / `0_Logic_74x:SN74LVC1G34DCK` | `NOT_VERIFIED` | Committed in `1993716` and the link audit is clean; the pin map is not checked against the datasheet. | Check the U303 pin map (`/component-check`).

## Not checked yet (need data)

- [ ] CN101 PM02D pin order (1-2 5 V, 3 SCL, 4 SDA, 5-6 GND) against the PM02D documentation; DS-009 has only an analog power port (OPEN-023).
- [ ] Oscillator LCSC codes C405461 and C17195695 against the part numbers (OPEN-028).
- [ ] Servo plug contact rating on CN801 to CN803 (about 2.1 A per pin at stall; the Samtec TSW rating applies only with Samtec sockets) and servo tolerance of the 12.9 V D807 clamp (OPEN-021, CMP-011).
- [ ] Device-side pinouts of the SiK V3 and the GPS V1: Holybro shows them only as images (OPEN-023).
