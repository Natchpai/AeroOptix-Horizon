# To Do

**Updated:** 2026-11-19
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review") and the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6). References follow the 15:25 save.

## MAJOR

- [ ] MAJOR | CN706 / `RC_IN_TR` | `VERIFIED` (CAD) | CN706 is a 3-pin JST-GH 1.25 mm (JST SM03B-GHS-TB(LF)(SN), C514175) with pin 1 `+5V`, pin 2 signal, pin 3 `GND`. DEC-053 and IF-038 say a 1x3 2.54 mm servo header with pin 1 PPM, so the FS-iA6B servo cable plugs in directly; as drawn it needs an adapter cable. | Decide with your partner: keep JST-GH and amend DEC-053 and IF-038 (the team makes the adapter cable), or change to the 2.54 mm header. (OPEN-034 item 6a)
- [ ] MAJOR | C803 / `+6V` | `VERIFIED` (`Rate` field) | 47 µF solid tantalum, Kyocera AVX TPSB476K010R0250, rated 10 V: 60 % of its rating at 6 V and 74 % at 7.4 V, on the hot-plugged 10 A servo bus. Solid tantalum is usually derated to about 50 % on such rails; a surge can short it. | Use 16 V or more (twice the 7.4 V maximum), or a polymer or MLCC part. (OPEN-021)

## MINOR

- [ ] MINOR | R705, R706 / `EXT_I2C4_SCL`, `EXT_I2C4_SDA` | `NOT_VERIFIED` | The board pull-ups (5.1 kΩ to `+3V3`) are fitted since the 13:33 save. If the MS4525DO module or the PM02D also has pull-ups, the total may be stronger than the bus needs. | Check the module pull-ups and the total against the I2C sink current. (OPEN-038)
- [ ] MINOR | D706 pins 5 and 6 / `GPS1_BUZZER_B` | `NOT_VERIFIED` | Pin 9 swings 0 to 5 V when Q701 is off, but the PESD4USB3BBTBR-QZ standoff voltage is unknown. Below 5 V, the ESD channel leaks or conducts. | Get the D706 standoff voltage; if it is below 5 V, use a 5 V part on this line. (OPEN-037)
- [ ] MINOR | CN705 pin 8 / `+3V3` | `VERIFIED` | The main `+3V3` rail goes off the board with no protection; a cable short pulls down the MCU rail. The 6X also puts VDD_3V3 on pin 8 (Holybro table). | Accept it, or add a series resistor or load switch. (OPEN-037)

## INFO

- [ ] INFO | C102 / `PM02_5V` | `VERIFIED` (`Rate` field) | The 5 V input capacitor is the same 10 V tantalum as C803: 55 % at 5.5 V, 62 % at the 6.2 V OV trip. | Decide together with C803; the hot-plug bench check is P4-013 (DEC-037).
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 67 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | D807 / `+6V` | `ASSUMED` | SMF7.5CA is bidirectional: a reversed UBEC is clamped at about −8 V instead of about −0.7 V. The 7.5 V standoff comes only from the part number; the Description field does not state it. | Accept the trade-off, or go back to a unidirectional part. Optionally add `7.5VWM` or the datasheet link to the fields. (OPEN-021)
- [ ] INFO | R813, R814 / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | Q701 drain / `GPS1_BUZZER_B` | `ASSUMED` | No flyback diode on the board. If the GPS buzzer is magnetic and the module has no diode, the drain sees a spike at turn-off. | Check the GPS module, or add a diode from the drain to `+5V`. (OPEN-037)
- [ ] INFO | R312 / `GPS1_SAFETY_SWITCH` | `NOT_VERIFIED` | The 10 kΩ pull-down suits a safety switch that connects to 3.3 V; the GPS module wiring and the px4io `io-v2` PB5 setup are not checked. | Check the switch side in DS-009 or the GPS module. (OPEN-037)
- [ ] INFO | D706 pins 2 and 9 | `VERIFIED` (CAD) | Unused channel with no wire and no no-connect flag. | Re-run ERC; add no-connect flags if it warns.
- [ ] INFO | `{SPARE_TIM}` / SPARE1 to SPARE3 | `VERIFIED` | The spare outputs reach `conn-peripherals` with no pads. | Add pads, or leave them unrouted. (OPEN-032)
- [ ] INFO | New library parts | `NOT_VERIFIED` | `0_Logic_74x:SN74LVC1G34DCK`, `Conn_01x03_MountingPin` and the JST-GH SM03B footprint are untracked and not audited. | Run `/kicad-link-audit`; check the U303 pin map against the datasheet (`/component-check`).

## Not checked yet (need data)

- [ ] DS-009 pinouts of TELEM 1 and 2, GPS1, I2C4 and the rangefinder (OPEN-023). Signal levels are known from the Holybro Pixhawk 6X baseboard pinout page (`VERIFIED`, official page, read 2026-11-19): all +3.3 V, except GPS 1 pin 9 `BUZZER-` at 0~5 V. No I2C pull-up note there.
- [ ] Ratings: PESD4USB3BBTBR-QZ (also on the 0~5 V buzzer line) and PESD5V0U2BT standoff voltage; SMF7.5CA (GOODWORK) breakdown voltage and leakage at 7.4 V; C803 derating against an AVX document; TSW-104 and XT30PW-M current per contact. Each needs a NotebookLM source (your approval) or your values. DEC-057 parts (U303, D707, Q701) are accepted; their data is optional evidence.
- [ ] Bus links `{ESC}`, `{AUX_TIM5}`, `{SURFACE}`, `{EXT_I2C4}`: not traced by `sch-inspect`; ERC was clean on the 12:49 save.
