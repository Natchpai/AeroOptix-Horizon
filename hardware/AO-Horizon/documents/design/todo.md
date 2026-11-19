# To Do

**Updated:** 2026-11-19
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review"), the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6) and a team pre-layout review of commit `2356489` (2026-11-19, kicad-cli 10.0.7; its ERC, field and pin-trace results are the team's, `NOT_VERIFIED` here). References follow the 2026-11-19 16:03 save. Cleaned 2026-11-19: done items removed.

## MAJOR

- [ ] MAJOR | CN706 / `RC_IN_TR` | `VERIFIED` (CAD) | CN706 is a 3-pin JST-GH 1.25 mm (footprint `JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal`, C514175) with pin 1 `+5V`, pin 2 signal, pin 3 `GND`. DEC-053, DEC-056 and P2-023 say a 1x3 2.54 mm right-angle header with pin 1 PPM, pin 2 `+5V`, pin 3 `GND`, so the FS-iA6B servo cable plugs in directly. The team review asks for that header. | Change CN706 to the 1x3 2.54 mm right-angle header (pin 1 PPM, 2 `+5V`, 3 `GND`), place it away from the `+6V` servo headers and label it "RC IN 5V" (P2-023, OPEN-031); or keep JST-GH and amend DEC-053. (OPEN-034 item 6a)
- [ ] MAJOR | MAIN 1 to 8, AUX 1 to 4, SPARE 1 to 3 / PWM lines | `VERIFIED` (spec 4.4) | Spec 4.4 asks for a weak pull-down on every PWM line, 15 in total since DEC-069. The team review found only the 22 Ω series resistors on the 12 MAIN and AUX lines (`NOT_VERIFIED` here); the spares have neither (`VERIFIED`, `sch-inspect`). | Pick the value and draw 15 pull-downs to `GND` (P2-018, OPEN-031 item 5); bench check in P4-011.
- [ ] MAJOR | SPARE1 to SPARE3 / `SPARE1_TIM1_CH1`, `SPARE2_TIM4_CH3`, `SPARE3_TIM4_CH4` | `VERIFIED` (`sch-inspect`) | Each spare net reaches only U201 (PE9, PD14, PD15); no pads are drawn, but IF-017 to IF-019 say pads only. | Draw per DEC-069 on `conn-peripherals`: one 4-pad row (SPARE1, SPARE2, SPARE3, GND), 22 Ω series per line (as R801, RC0402FR-0722RL, C114765) and the pull-down above. Confirm the pad footprint (proposed: 1x4 2.54 mm hole row, not fitted) and bring the pad part in with `kicad-part-start` and `kicad-link-audit`.

## MINOR

- [ ] MINOR | D706 pins 5 and 6 / `GPS1_BUZZER_B` | `NOT_VERIFIED` | Pin 9 swings 0 to 5 V when Q701 is off, but the PESD4USB3BBTBR-QZ standoff voltage is unknown. Below 5 V, the ESD channel leaks or conducts. | Get the D706 standoff voltage; if it is below 5 V, use a 5 V part on this line. (OPEN-023)
- [ ] MINOR | MCU, sensor and USB sheets | `NOT_VERIFIED` | Not reviewed yet; the connector sheets are done. | Run `sch-review` on these sheets before layout (P2-009).

## INFO

- [ ] INFO | GPS module / buzzer | `ASSUMED` | DEC-068 drops the board buzzer because the GPS has one. DEC-021 names the Holybro M9N, to be confirmed; the team review says the Holybro M10/M9N V2 has no buzzer (`NOT_VERIFIED`). With no GPS buzzer, the aircraft makes no tone. | Confirm the GPS model and that it has a buzzer on GPS1 pin 9. (DEC-068, OPEN-023)
- [ ] INFO | Q701 drain / `GPS1_BUZZER_B` | `ASSUMED` | No flyback diode on the board. If the GPS buzzer is magnetic and the module has no diode, the drain sees a spike at turn-off. | Check the GPS module, or add a diode from the drain to `+5V`. (OPEN-023)
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 88 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | R813, R814 / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | U303 / `0_Logic_74x:SN74LVC1G34DCK` | `NOT_VERIFIED` | Committed in `1993716` and the link audit is clean; the pin map is not checked against the datasheet. | Check the U303 pin map (`/component-check`).

## Not checked yet (need data)

- [ ] DS-009 pinouts of TELEM 1 and 2, GPS1, I2C4 and the rangefinder (OPEN-023). Signal levels are known from the Holybro Pixhawk 6X baseboard pinout page (`VERIFIED`, official page, read 2026-11-19): all +3.3 V, except GPS 1 pin 9 `BUZZER-` at 0~5 V. No I2C pull-up note there.
- [ ] Oscillator HSE input limits of both MCUs in bypass mode (level, duty cycle, frequency range), before layout (OPEN-028, CMP-010).
- [ ] Ratings: PESD4USB3BBTBR-QZ (also on the 0~5 V buzzer line) and PESD5V0U2BT standoff voltage; SMF7.5A (MDD, DEC-059) breakdown voltage and leakage at 7.4 V; C803 T495C686M016ATE250 data; TSW-104 and XT30PW-M current per contact against the 13.2 A all-stall estimate (OPEN-021). Each needs a NotebookLM source (your approval) or your values. DEC-057 parts (U303, D707, Q701) are accepted; their data is optional evidence.
