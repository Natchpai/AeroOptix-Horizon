# To Do

**Updated:** 2026-11-19
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`).

Format: severity | reference / net | evidence label | what is wrong | what to do.

## `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19)

Saved files at commit `10a0782` (12:49 save). Full text: spec 4.2 "Schematic review" paragraph.

### MAJOR

- [ ] MAJOR | CN705 pin 9 / `GPS1_BUZZER_B`, H743 PB0 (U201 pin 34) | `VERIFIED` (CAD), `NOT_VERIFIED` (GPS side) | The GPS buzzer pin is driven straight from PB0 through R711 22 Ω, with no transistor. If the GPS module has its buzzer between its own 5 V and pin 9, PB0 must sink more than its 20 mA limit and sees about 5 V. | Check the GPS1 pin 9 wiring in DS-009 or a GPS module schematic. If it is the buzzer minus side, add a low-side N-FET driver. (OPEN-037)
- [ ] MAJOR | R705, R706 / `EXT_I2C4_SCL`, `EXT_I2C4_SDA` | `VERIFIED` | The I2C4 pull-ups are DNP, and no other pull-up is on the bus. | Check that the MS4525DO module and the PM02D have pull-ups, or fit R705 and R706. 5 V pull-ups are safe: PD12 and PD13 are FT. (OPEN-038)
- [ ] MAJOR | C803 / `+6V` | `VERIFIED` (`Rate` field) | 47 µF solid tantalum, Kyocera AVX TPSB476K010R0250, rated 10 V: 60 % of its rating at 6 V and 74 % at 7.4 V, on the hot-plugged 10 A servo bus. Solid tantalum is usually derated to about 50 % on such rails; a surge can short it. | Use 16 V or more (twice the 7.4 V maximum), or a polymer or MLCC part. (OPEN-021)

### MINOR

- [ ] MINOR | D807 / `+6V` | `ASSUMED` | The SMF7.0A standoff is 7.0 V (part-number convention), below the 7.4 V servo supply maximum (PWR-011). Fine at 6 V. | Confirm the standoff and breakdown voltage, or pick about 8 V standoff if the UBEC may run at 7.4 V. (OPEN-021)
- [ ] MINOR | F100 PB13 (U301 pin 26) / `GPS1_SAFETY_LED` | `VERIFIED` | The line is active low (open drain), but the net name has no `_B` (DEC-052). | Rename to `GPS1_SAFETY_LED_B` on `conn-peripherals`, `mcu-io` and both sheet symbols, or note the exception in DEC-052. (OPEN-032)
- [ ] MINOR | F100 PB5 (U301 pin 41) / `GPS1_SAFETY_SWITCH` | `NOT_VERIFIED` | No board pull resistor; the input floats with no GPS cable. | Check the px4io `io-v2` setup for PB5. If it floats, add a pull resistor. (OPEN-037)
- [ ] MINOR | CN705 pin 8 / `+3V3` | `VERIFIED` | The main `+3V3` rail goes off the board with no protection; a cable short pulls down the MCU rail. | Accept it, or add a series resistor or load switch. (OPEN-037)

### INFO

- [ ] INFO | R813, R814 / `SERVO_V_ADC1_IN4`, F100 PA4 | `ESTIMATED` | At a TVS clamp of about 12 V, PA4 sees about 4.0 V and about 26 µA flows into the pin: inside the ±5 mA absolute maximum, so no damage, but the ADC reading is disturbed during the spike. | No action unless the servo rail reading must stay accurate during spikes. (OPEN-033)
- [ ] INFO | `+6V` bulk / C801, C802, C803 | `VERIFIED` | About 67 µF on the board against up to 13.2 A of servo stall current; the UBEC output capacitors carry most of it. | Revisit at layout. (OPEN-021)
- [ ] INFO | `{SPARE_TIM}` / SPARE1 to SPARE3 | `VERIFIED` | The spare outputs reach `conn-peripherals` with no pads. | Add pads, or leave them unrouted. (OPEN-032)
- [ ] INFO | C102 / `PM02_5V` | `VERIFIED` (`Rate` field) | The 5 V input capacitor is the same 10 V tantalum: 55 % at 5.5 V, 62 % at the 6.2 V OV trip. | Decide together with C803; the hot-plug bench check is P4-013 (DEC-037).

### Not checked yet (need data)

- [ ] DS-009 pinouts of TELEM 1 and 2, GPS1, I2C4 and the rangefinder (OPEN-023).
- [ ] Ratings: PESD4USB3BBTBR-QZ and PESD5V0U2BT standoff voltage; SMF7.0A standoff, breakdown and clamping voltage; C803 derating against an AVX document (C801 and C802 are 16 V X7R, C803 10 V, from the `Rate` fields); TSW-104 and XT30PW-M current per contact. Each needs a NotebookLM source (your approval) or your values.
- [ ] H743 PB0 pin type (NotebookLM gave `TT_a` without a cited row).
- [ ] Bus links `{ESC}`, `{AUX_TIM5}`, `{SURFACE}`, `{EXT_I2C4}`: not traced by `sch-inspect`; ERC is clean.
