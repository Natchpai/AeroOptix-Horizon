# To Do

**Updated:** 2026-11-19
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`).

Format: severity | reference / net | evidence label | what is wrong | what to do.

## `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19)

Saved files at commit `10a0782` (12:49 save). Full text: spec 4.2 "Schematic review" paragraph.

### MAJOR

- [x] MAJOR | CN705 pin 9 / `GPS1_BUZZER_B`, H743 PB0 (U201 pin 34) | `VERIFIED` (CAD), `NOT_VERIFIED` (GPS side) | The GPS buzzer pin is driven straight from PB0 through R711 22 Ω, with no transistor. If the GPS module has its buzzer between its own 5 V and pin 9, PB0 must sink more than its 20 mA limit and sees about 5 V. | Check the GPS1 pin 9 wiring in DS-009 or a GPS module schematic. If it is the buzzer minus side, add a low-side N-FET driver. (OPEN-037)
  - Done in the 2026-11-19 13:33 save (`VERIFIED`, CAD): pin 9 is `BUZZER-` at 0~5 V on the Holybro Pixhawk 6X GPS 1 table (official page, `VERIFIED`). PB0 (`BUZZER_TIM3_CH3`) now drives the gate of Q701 (2SK3018W, SOT-323); R711 is a 10k gate pull-down to `GND`; the Q701 source is on `GND` and the drain drives `GPS1_BUZZER_B` (CN705 pin 9, D706 pins 5 and 6). Not yet recorded in the spec (OPEN-037 still open there).
- [ ] MAJOR | R705, R706 / `EXT_I2C4_SCL`, `EXT_I2C4_SDA` | `VERIFIED` | The I2C4 pull-ups are DNP, and no other pull-up is on the bus. | Check that the MS4525DO module and the PM02D have pull-ups, or fit R705 and R706. 5 V pull-ups are safe: PD12 and PD13 are FT. (OPEN-038)
- [ ] MAJOR | C803 / `+6V` | `VERIFIED` (`Rate` field) | 47 µF solid tantalum, Kyocera AVX TPSB476K010R0250, rated 10 V: 60 % of its rating at 6 V and 74 % at 7.4 V, on the hot-plugged 10 A servo bus. Solid tantalum is usually derated to about 50 % on such rails; a surge can short it. | Use 16 V or more (twice the 7.4 V maximum), or a polymer or MLCC part. (OPEN-021)

### MINOR

- [x] MINOR | D807 / `+6V` | `ASSUMED` | The SMF7.0A standoff is 7.0 V (part-number convention), below the 7.4 V servo supply maximum (PWR-011). Fine at 6 V. | Confirm the standoff and breakdown voltage, or pick about 8 V standoff if the UBEC may run at 7.4 V. (OPEN-021)
  - Done in the 2026-11-19 13:57 save (`VERIFIED`, CAD): D807 is SMF7.5CA (GOODWORK, LCSC C2980404), bidirectional, symbol `D_TVS-ESD_bi`, A1 on `GND`, A2 on `+6V`; Datasheet field cleared (it pointed to the R+O SMF7.0A). The 13:44 Description gave 7.5 V standoff and 12.9 V clamp; the 13:57 Description gives only the 12.9 V clamp and 15.5 A Ipp. 7.4 V is 0.1 V (1.4 %) under the standoff (`ESTIMATED`). Not yet recorded in the spec (OPEN-021).
- [x] MINOR | F100 PB13 (U301 pin 26) / `GPS1_SAFETY_LED` | `VERIFIED` | The line is active low (open drain), but the net name has no `_B` (DEC-052). | Rename to `GPS1_SAFETY_LED_B` on `conn-peripherals`, `mcu-io` and both sheet symbols, or note the exception in DEC-052. (OPEN-032)
  - Done in the 2026-11-19 15:20 save (`VERIFIED`, CAD): the net is `GPS1_SAFETY_LED_B` on `conn-peripherals`, `mcu-io` and `top_hierarchical` (CN705 pin 7, D706 pins 4 and 7, U301 pin 26 PB13); no `GPS1_SAFETY_LED` label is left. Not yet recorded in the spec (OPEN-032).
- [x] MINOR | F100 PB5 (U301 pin 41) / `GPS1_SAFETY_SWITCH` | `NOT_VERIFIED` | No board pull resistor; the input floats with no GPS cable. The signal is 3.3 V (Holybro 6X table, `VERIFIED`), so PB5 not being 5 V tolerant is fine. | Check the px4io `io-v2` setup for PB5. If it floats, add a pull resistor. (OPEN-037)
  - Done in the 15:20 save (`VERIFIED`, CAD): R312 10 kΩ (C144807) from `GPS1_SAFETY_SWITCH` to `GND` on `mcu-io`; the net also reaches D706 pins 1 and 10, CN705 pin 6 and U301 pin 41. A pull-down suits a switch to 3.3 V; that the GPS module switches to 3.3 V, and the px4io `io-v2` pull setting, are `NOT_VERIFIED`. Not yet recorded in the spec (OPEN-037).
- [ ] MINOR | CN705 pin 8 / `+3V3` | `VERIFIED` | The main `+3V3` rail goes off the board with no protection; a cable short pulls down the MCU rail. The 6X also puts VDD_3V3 on pin 8 (Holybro table). | Accept it, or add a series resistor or load switch. (OPEN-037)
- [ ] MINOR | D706 pins 5 and 6 / `GPS1_BUZZER_B` | `NOT_VERIFIED` | Pin 9 swings 0 to 5 V when Q701 is off, but the PESD4USB3BBTBR-QZ standoff voltage is unknown. Below 5 V, the ESD channel leaks or conducts. | Get the D706 standoff voltage; if it is below 5 V, use a 5 V part on this line. (OPEN-037)
  - No longer applies in the 15:20 save (`VERIFIED`, CAD): D706 now protects `GPS1_SAFETY_SWITCH` (pins 1, 10) and `GPS1_SAFETY_LED_B` (pins 4, 7); `GPS1_BUZZER_B` reaches only CN705 pin 9 and the Q701 drain. See the new MINOR below.
  - Applies again in the 15:25 save (`VERIFIED`, CAD): `GPS1_BUZZER_B` is back on D706 pins 5 and 6.
- [x] MINOR | Q701 2SK3018W | `NOT_VERIFIED` | Ratings and pinout are not checked. The symbol uses 1 G, 2 S, 3 D on SOT-323 (LCSC C20069149). | Confirm the pinout against this maker's datasheet and R<sub>DS(on)</sub> at V<sub>GS</sub> = 3.3 V against the buzzer current (`/component-check`, or your values). (OPEN-037)
  - Accepted by the human owner 2026-11-19 ("Q701 is fine"; spec DEC-057). Datasheet values not checked by Claude.
- [x] MINOR | Q701 drain / `GPS1_BUZZER_B` | `VERIFIED` (CAD) | Since the 15:20 save the buzzer line has no ESD part: CN705 pin 9 goes straight to the Q701 drain, a small-signal FET, on an off-board cable. | Put an ESD part with 5 V or more standoff on pin 9 (the line swings 0 to 5 V), or accept it. (OPEN-037)
  - Done in the 15:25 save: back on D706 pins 5 and 6 (see the D706 standoff item above).

### INFO

- [ ] INFO | R813, R814 / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 67 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | `{SPARE_TIM}` / SPARE1 to SPARE3 | `VERIFIED` | The spare outputs reach `conn-peripherals` with no pads. | Add pads, or leave them unrouted. (OPEN-032)
- [ ] INFO | D807 / `+6V` | `ASSUMED` | Bidirectional: a reversed UBEC is clamped at about −8 V instead of about −0.7 V. The standoff (7.5 V) now comes only from the part number; the Description field no longer states it. | Accept the trade-off, or go back to a unidirectional part. Optionally add `7.5VWM` or the datasheet link to the fields. (OPEN-021)
- [ ] INFO | Q701 drain / `GPS1_BUZZER_B` | `ASSUMED` | No flyback diode on the board. If the GPS buzzer is magnetic and the module has no diode, the drain sees a spike at turn-off. | Check the GPS module, or add a diode from the drain to `+5V`. (OPEN-037)
- [x] INFO | D706 pins 4 and 7 | `VERIFIED` (CAD) | No wire and no no-connect flag on the unused channel. | Re-run ERC on the 13:33 save; add no-connect flags if it warns.
  - Pins 4 and 7 carry `GPS1_SAFETY_LED_B` since the 15:20 save. New: D706 pins 2, 9 and 5, 6 now have no wire and no no-connect flag (`VERIFIED`, CAD); re-run ERC and add flags if it warns. 15:25 save: pins 5 and 6 carry `GPS1_BUZZER_B` again; only pins 2 and 9 are open.
- [ ] INFO | C102 / `PM02_5V` | `VERIFIED` (`Rate` field) | The 5 V input capacitor is the same 10 V tantalum: 55 % at 5.5 V, 62 % at the 6.2 V OV trip. | Decide together with C803; the hot-plug bench check is P4-013 (DEC-037).

### Not checked yet (need data)

- [ ] DS-009 pinouts of TELEM 1 and 2, GPS1, I2C4 and the rangefinder (OPEN-023). Signal levels are answered by the Holybro Pixhawk 6X baseboard pinout page (`VERIFIED`, official page, read 2026-11-19): every TELEM, I2C, UART4 and GPS 1 signal is +3.3 V, except GPS 1 pin 9 `BUZZER-` at 0~5 V. The page gives no I2C pull-up note (OPEN-038 stays open).
- [ ] Ratings: PESD4USB3BBTBR-QZ (now also on the 0~5 V buzzer line) and PESD5V0U2BT standoff voltage; SMF7.5CA (GOODWORK) breakdown voltage and leakage at 7.4 V; C803 derating against an AVX document (C801 and C802 are 16 V X7R, C803 10 V, from the `Rate` fields); TSW-104 and XT30PW-M current per contact. Each needs a NotebookLM source (your approval) or your values.
- [x] H743 PB0 pin type (NotebookLM gave `TT_a` without a cited row). No longer needed: since the 13:33 save PB0 drives only the Q701 gate at 3.3 V.
- [ ] Bus links `{ESC}`, `{AUX_TIM5}`, `{SURFACE}`, `{EXT_I2C4}`: not traced by `sch-inspect`; ERC is clean.

## RC IN as drawn (2026-11-19 15:03 save, re-read 15:20 and 15:25)

Drawn, not decided. Spec OPEN-034 item 6. Signal path traced (`VERIFIED`, CAD): CN706 pin 2 `RC_IN_TR`, ESD diode to `GND` (D707 at 15:03, `D?` at 15:20), R714 22 Ω, `RC_IN` to U303 pin 2 (R310 100 kΩ to `GND`), U303 pin 4 `RC_IN_BUFFER`, R311 22 Ω, `RCIN_TIM1_CH1` to F100 PA8 (U301 pin 29); U303 VCC `+3V3` with C311 100 nF.

- [ ] MAJOR | CN706 / `RC_IN_TR` | `VERIFIED` (CAD) | CN706 is a 3-pin JST-GH 1.25 mm (SM03B-GHS-TB footprint) with pin 1 `+5V`, pin 2 signal, pin 3 `GND`. DEC-053 and IF-038 say a 1x3 2.54 mm servo header with pin 1 PPM, so the FS-iA6B servo cable plugs in directly; as drawn it needs an adapter cable. | Keep JST-GH and amend DEC-053 and IF-038 (the team makes the adapter cable), or change to the 2.54 mm header. (OPEN-034)
  - Deferred 2026-11-19: you decide it with your partner later.
- [x] MINOR | U303 SN74LVC1G34DCKR | `VERIFIED` (CAD) | A plain buffer with no input hysteresis; DEC-056 names the 74LVC1G17 Schmitt trigger for the cable input. | Swap to a 74LVC1G17 (check its pinout against the U303 footprint), or amend DEC-056. (OPEN-034)
  - Accepted by the human owner 2026-11-19 ("U303 is fine"; spec DEC-057 amends DEC-056).
- [x] MINOR | R714 / `RC_IN_TR` | `VERIFIED` (CAD) | 22 Ω where DEC-056 says 1 kΩ; less current limit into U303 and the ESD diode during ESD or a 5 V overdrive. | Change to 1 kΩ, or amend DEC-056. (OPEN-034)
  - Accepted by the human owner 2026-11-19 ("R714 is fine"; spec DEC-057 amends DEC-056).
- [x] MINOR | `D?` SP3031-01ETG (was D707) / `RC_IN_TR` | `NOT_VERIFIED` | The Description field says "5V(MAX)" at 15:03 and "5V(Vswr)" at 15:20; a 5 V receiver high can reach 5.25 V, above a 5 V working voltage (leakage or clamping). DEC-056 asks for 5 V or more. | Get the SP3031 working and breakdown voltage, or pick a part with more than 5.25 V working voltage. (OPEN-034)
  - Accepted by the human owner 2026-11-19 ("D707 is fine"; spec DEC-057). Standoff and breakdown not checked by Claude.
- [x] MINOR | `D?` on `conn-peripherals` | `VERIFIED` (preflight) | The RC IN ESD diode was re-placed in the 15:20 save as SP3031-01ETG (Littelfuse, LCSC C207283, SOD-882) and is not annotated. | Annotate it (D707).
  - Done in the 15:25 save: D707 (SP3031-01ETG, C207283). The library symbol Description now reads "5V(Vswr)".
- [x] INFO | CN706, D707 | `VERIFIED` (CAD) | CN706 has no MPN, MFR or LCSC field; D707 has no LCSC field. | Fill before the BOM (P2-021).
  - Done in the 15:20 save (`VERIFIED`, CAD): CN706 is JST SM03B-GHS-TB(LF)(SN), LCSC C514175; the re-placed ESD diode has LCSC C207283.
- [ ] INFO | New library parts | `NOT_VERIFIED` | `0_Logic_74x:SN74LVC1G34DCK`, `Conn_01x03_MountingPin` and the JST-GH SM03B footprint are untracked and not audited. | Run `/kicad-link-audit`; check the U303 pin map against the datasheet (`/component-check`).
- [ ] INFO | R711 to R713 | `VERIFIED` (CAD) | Re-annotated again in the 15:03 save: R711 and R712 are the GPS1 I2C1 pull-ups (5.1 kΩ), R713 is the Q701 gate pull-down (10 kΩ). Older items above use the 13:33 names. | None.
