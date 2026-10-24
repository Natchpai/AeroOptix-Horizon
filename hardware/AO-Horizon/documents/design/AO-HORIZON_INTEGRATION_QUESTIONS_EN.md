# AeroOptix-Horizon: Integration Questions for the Team

**Revision:** 0.3
**Updated:** 2026-10-24
**From:** Hardware
**To:** Software team, CAD team and all members
**Status:** Sections 3 to 5 were answered by the software team on 2026-10-24 and applied in spec rev 0.13. Hardware changed D8 to a Pixhawk-style servo rail (section 8). D9 stays a proposal until the CAD team confirms it. **Section 9 is new in rev 0.3 and is sent for your answers** (checklist P0-022).

## 1. How to reply

The pinmap is agreed (pinmap review 0.3). The questions below are about how the board connects to Model G: devices, cables, servo power, mounting and environment. The team owns the drone spec and the software. Hardware follows your answers.

You can fill this in by hand or ask Claude to do it.

1. Section 3 is for the whole team. Section 4 lists the external devices: fill the `Team` column. Section 5 is for the software team.
2. In tables, fill only the `Team` column with one of:
   - `OK`: accept the hardware proposal as written.
   - `CHANGE: <what>`: say exactly what you want instead.
   - `?: <question>`: you need hardware to explain.
   Add the device model or cable where the row asks for it.
3. Under each question, fill the `Decision:` or `Answer:` line, and the `By:` line with the name or role of whoever decided.
4. Numbering continues from the decisions file (D1 to D7, S1 to S7). Section 6 is for information only.
5. Keep the file name. Send the whole file back.

## 2. What changed since pinmap review 0.3

For information. Details are in spec rev 0.12 and pinmap review 0.3, section 9.

- The IO MCU is now the STM32F100C8T6B with a 24 MHz crystal, as you proposed. Stock px4io-v2 and the stock px4io bootloader run unchanged. No pin moved: the F100 and F103 LQFP48 pin data match on all 48 pins (ST pin data).
- The three px4io LEDs are fitted. PA10 and PB11 get a weak pull-up. The BMP384 fallback is at 0x76.

## 3. Decisions for the whole team

**D8. Servo power path (PWR-002, PWR-011, OPEN-007).**
The 8 servos run on 6 V from a UBEC rated 10 A continuous and 15 A peak (spec PWR-011). The board is smaller than 80 × 80 mm (MEC-001).
Options:
- (a) The 6 V enters the board, and each servo plugs into a 3-pin header on the board (signal, +6 V, GND). All servo current flows through the board.
- (b) The 6 V goes from the PDB or UBEC to the servos through the wiring harness. The board gives each servo only signal and GND, plus one sense wire from the 6 V rail to the servo rail sense input (IF-050). No servo current flows through the board.
- (c) Other.

Hardware impact: (a) needs a high-current input connector, wide copper, bulk capacitors and 8 headers, which take a large part of the board. (b) is smaller and keeps servo current away from the sensors.

Also tell us the servo models and their stall current, and how many servos can move or stall at the same time. Hardware needs this to check the 10 A / 15 A rating.

Decision: (b). Servo power goes from the UBEC/PDB through the harness. The board gives each servo signal and GND, plus the sense wire to the servo rail sense input. All 8 servos can move at the same time: the 4 tilt servos move together in every transition and all the time in hover (differential tilt is the hover yaw control), and the flaperons and ruddervators move together in cruise. Bench target from the CAD team's build checks: the 4 tilt servos together stay at or below 10 A on the UBEC while tilting 0 to 90° at hover thrust.
Servo models and stall current: Tilt servos: RDS3235 (team parts list) or DS3218 (design document), not chosen yet. Flaperon and ruddervator servos: ES08 class. Stall current: not measured yet (open item in the CAD team's handoff); we will send it after the bench test.
By: Software team (proposal for the team)

**D9. Mounting, size and cable entry (MEC-001 to MEC-004, OPEN-009).**
Hardware needs, before PCB placement:
- Mounting hole pattern and screw size (for example 30.5 × 30.5 mm with M3, or 20 × 20 mm with M2).
- Hard mount or soft (vibration-damped) mount.
- Maximum height above and below the board (enclosure or frame space).
- Which board edge faces forward, and from which sides the cables come in.
- Whether USB and the microSD card must be reachable when the board is installed. The H743 debug connector already must be (team answer S6).

Decision: From the current CAD model; the CAD team confirms the rest. The FC sits on a tray on the fuselage floor near the CG, held by 4 × M3×8 screws with rubber dampers (soft mount); older CAD notes ask for a rigid mount, so the CAD team settles this. The tray was drawn for a Pixhawk 6X placeholder and will be redrawn for this board. Proposal: 30.5 × 30.5 mm hole pattern with M3, soft mount. The GPS sits above the FC under the fiberglass canopy, so it limits the height above the board; the CAD team gives the clearances and cable entry sides. Forward edge: any, since PX4 sets the board rotation in software; please mark the forward direction on the silkscreen. USB and microSD: both reachable with the canopy open (USB for setup, microSD to download logs after every flight).
By: Software team (proposal; CAD team to confirm)

**D10. Environment (ENV-001 to ENV-004).**
Operating and storage temperature range, rain or dust exposure, and maximum flight altitude. Hardware uses this to choose part temperature grades and to decide on conformal coating.
If the team has no requirement, hardware proposes: parts rated −40 to +85 °C, no conformal coating, no rain exposure. Answer `OK` or give your values.

Decision: OK to the hardware proposal (parts rated −40 to +85 °C, no conformal coating, no rain exposure). Our conditions: hot-weather flights at a field near sea level (our model assumes about 32 °C afternoons near Bangkok); the inside of the fuselage can get hotter in the sun. Low-altitude flights only.
By: Software team (proposal for the team)

**D11. Safety switch, buzzer and GPS module (IF-012, IF-046, IF-049).**
The PX4 docs describe the Pixhawk 6C GPS1 port as "Full GPS port (GPS plus safety switch)". Many Pixhawk GPS modules carry the safety switch, its LED and sometimes a buzzer on the same cable (`ASSUMED`, not checked per module).
Options:
- (a) The GPS module carries the safety switch and LED. The board GPS connector carries them to the F100 (PB5 button, PB13 LED). The board buzzer stays (IF-046).
- (b) A separate safety switch with LED on its own board connector. The GPS connector carries only GPS and compass.
- (c) No physical safety switch (disabled in PX4). The F100 safety pins stay unconnected.

Hardware impact: connector pin count only.

Which GPS module (model) do you use?

Decision: (a) in hardware, (c) in use. Make GPS1 the 10-pin full GPS port, so a GPS module's safety switch and LED can reach the F100 (PB5, PB13) at no extra cost. On Model G we will fly with the safety switch disabled in PX4; the CAD team has already dropped the separate safety switch. It can be turned on later with no hardware change. The board buzzer stays.
GPS model: Holybro M9N (u-blox NEO-M9N with an IST8310 compass), as in the CAD model; to be confirmed when bought.
By: Software team (proposal for the team)

## 4. External devices and connectors

Hardware proposal for every external port: the Pixhawk connector standard (JST-GH, 1.25 mm), so cables made for Pixhawk boards fit. Hardware has not read the standard (DS-009) yet; the pinouts will be checked before the schematic (`NOT_VERIFIED`). If your device comes with a different cable, write it in the `Team` column.

| Interface | Spec ID | Hardware proposal | Hardware needs from you | Team |
|---|---|---|---|---|
| Telemetry 1: ELRS receiver | IF-010 | JST-GH 6-pin, Pixhawk TELEM layout, 5 V supply. TX and RX only (no CTS/RTS on UART7) | Receiver model and supply voltage | OK. The same ELRS setup we flew on our AAVC competition drone (RadioMaster Nomad on the transmitter, ELRS receiver in MAVLink mode; receiver model to follow). 5 V supply, 3.3 V logic, TX and RX only is fine. No FlySky and no SiK: the FS-iA6B and SiK radio still drawn in the CAD model are both replaced by this one receiver |
| Telemetry 2 (free) | IF-011 | JST-GH 6-pin, as Telemetry 1 | Keep a connector, or pads only (no device is planned) | OK, keep the connector, so a second receiver can be added later with no hardware change (D6) |
| GPS1 + compass | IF-012 | JST-GH 6-pin (GPS and I2C) or 10-pin (with safety switch, see D11) | GPS model (D11) | OK, 10-pin with the safety switch lines (D11). GPS: Holybro M9N (u-blox NEO-M9N + IST8310), to be confirmed |
| Airspeed MS4525DO | IF-014 | JST-GH 4-pin, Pixhawk I2C layout (5 V, SCL, SDA, GND) on I2C4 | Exact part number: the 3.3 V or the 5 V version | OK for the 5 V Pixhawk I2C layout if the module has its own regulator (most Pixhawk airspeed modules do). We confirm the part number before the schematic |
| Power module PM02D | IF-048 | Connector that matches the cable on your PM02D | Connector type and pin count on your unit; chip on the label (INA228 or INA226) | OK. Holybro ships the PM02D with a 6-pin 2.00 mm CLIK-Mate cable (PX4 docs). The chip on the label is to follow |
| Rangefinder TF-Luna | IF-015 | JST-GH 4-pin (5 V, TX, RX, GND) on UART8 | Cable you use (TF-Luna has its own 6-pin connector) | OK. We make an adapter cable from the TF-Luna 6-pin connector to JST-GH 4-pin |
| ESC 4-in-1 | IF-040 to IF-043 | Connector that matches the ESC signal cable | ESC model and its cable pinout. Do you want the ESC current sense or ESC telemetry wire connected? Both are possible with free H743 pins | OK. Planned ESC: Holybro Tekko32 F4 4-in-1 50 A (AM32), on 30.5 x 30.5 mm standoffs in the CAD model; not confirmed yet, cable pinout to follow. Yes to both: current sense on the PC1 ADC reserve, telemetry on a free UART RX (for example UART4_RX, PD0) |
| 8 servos | IF-030 to IF-037 | 3-pin 2.54 mm headers, or signal-only connector (see D8) | Set by D8 | OK: signal and GND only (D8 b) |
| 3 spare outputs | IF-017 to IF-019 | Pads only (no use planned, decisions file D4) | OK or a connector | OK, pads only |
| USB | IF-022 | USB-C on a board edge | USB-C or Micro-B, or a cable to the frame. Should USB power the board on the bench without the battery? | OK: USB-C on a board edge, reachable when the board is installed. Yes, USB should power the board on the bench without the battery |

## 5. Questions for the software team

**S8. Stock px4io on the F100.**
Do you ship the stock `px4_io-v2_default` image in the port's `extras/` folder, as `px4/fmu-v6c` does? Your Q20 answer mentions bringing up an 8 MHz px4io build. With the F100 that build is not needed. Please confirm.

Answer: Yes. We ship the stock `px4_io-v2_default` image in our board's `extras/` folder, as `px4/fmu-v6c` does. The 8 MHz px4io build is no longer needed.
By: Software team

**S9. IMU heater.**
Hardware plans no IMU heater. On px4io-v2, PB14 is the blue LED and also a heater output; on this board it drives only the LED. Do you need an IMU heater for Model G (for example for cold-weather flights)?

Answer: No heater. Model G flies in warm weather, and PX4 can apply IMU temperature calibration if we need it.
By: Software team

**S10. Status of team tests.**
Two items wait on team tests: the RC-loss failsafe over ELRS MAVLink (S5), and how the chosen ESC reacts when DShot frames stop (spec OPEN-017, SAF-015). Any results yet? Which ESC is confirmed?

Answer: No results yet; both tests are still open. Background for S5: RC control over ELRS MAVLink is not new to us; we flew our AAVC competition hexacopter (PX4 on a Pixhawk 6X) with it, but did not test the RC-loss failsafe there. The ESC is not confirmed: the candidate is the Holybro Tekko32 F4 4-in-1 50 A (AM32) from the CAD team's parts list. We will send the results when the tests are done.
By: Software team

## 6. For information, no reply needed

Hardware does these without your input:
- 5 V input protection, ESD protection on external connectors, and keeping USB VBUS and the PM02D 5 V from back-feeding each other.
- Values for pull-ups, pull-downs and LED resistors, and the crystal parts.
- Current limits on the 5 V supply to external connectors.

## 7. Sources

- Spec: `AO-HORIZON_SPEC_EN.md` rev 0.12 (PWR-002, PWR-011, MEC-001 to MEC-004, ENV-001 to ENV-004, IF rows, OPEN-007, OPEN-009, OPEN-017)
- Pinmap: `AO-HORIZON_PINMAP_REVIEW_EN.md` rev 0.3 (answered) and `AO-HORIZON_PINMAP_DECISIONS_EN.md` rev 0.2
- Power: `AO-HORIZON_POWER_BUDGET_EN.md` rev 0.5, section 9
- PX4 docs, Pixhawk 6C: https://docs.px4.io/main/en/flight_controller/pixhawk6c.html (read 2026-10-24)

## 8. What hardware decided after your answers (rev 0.3)

For information, no reply needed.

- **Servos (changes D8).** Hardware uses the Pixhawk-style servo rail instead of D8 (b). Each servo plugs straight into a 3-pin header on the board (signal, +6 V, GND), so your harness needs no split servo cables. The UBEC plugs into the board too; hardware will tell you the exact UBEC plug after it sizes it for 10 A continuous and 15 A peak (spec DEC-019).
- **ESC current sense.** PC1 stays reserved for an analog power module. The ESC current goes to another free ADC pin; hardware sends you the pin for `board.h` (spec DEC-023). ESC telemetry stays on UART4_RX (PD0) as you asked, after hardware checks it in ST pin data.
- **Connector pinouts.** Hardware checks every JST-GH pinout against the Pixhawk connector standard before the schematic. No action from you.

## 9. Follow-up questions (rev 0.3)

Only things the team knows: your parts, your aircraft and how you use PX4. Reply as in section 1. Write `later` if you do not know yet.

**D12. Mounting details (MEC-002 to MEC-004, OPEN-009). For the CAD team.**
- Soft or rigid mount? Older CAD notes say rigid; the D9 answer says soft.
- If soft: which rubber dampers (model or a link)?
- How much space above the board (under the GPS) and below it, in mm?
- From which sides do the cables come in? Which side should USB-C and the microSD face, so you can reach them with the canopy open?
- Does the board sit on top of the ESC (both 30.5 × 30.5 mm), or on its own tray?

Answer:
By:

**S11. Devices you need on USB alone (IF-022).**
On the bench without the battery, which devices must run from USB? For example: GPS (compass calibration), ELRS receiver, TF-Luna, airspeed sensor. Hardware sizes the USB power path from your answer.

Answer:
By:

**S12. ESC current in PX4 (IF-052).**
How will PX4 use the ESC current: as a battery monitor (for example a second battery), or only in the log? The PM02D already measures the battery current.

Answer:
By:

### 9.1 Parts still needed

Give the model and a product link or a photo. Hardware reads the technical data from that. Write `later` if the part is not bought yet.

| Item | Spec ID | What we need | Team |
|---|---|---|---|
| ELRS receiver | IF-010 | Model and link | |
| GPS module | IF-012 | Confirm Holybro M9N when bought, and a photo of its cable plug | |
| Airspeed module (MS4525DO) | IF-014 | Model and link, or a photo of the board | |
| PM02D | IF-048 | Chip name on the label (INA228 or INA226), and a photo of the plug on its cable | |
| ESC 4-in-1 | IF-040 to IF-043 | Confirmed model and link, and a photo of its signal cable plug | |
| Tilt servos | IF-034 to IF-037 | Chosen model (RDS3235 or DS3218) | |
| UBEC | PWR-011 | Model and link | |

### 9.2 Team tests still open

No new question. Please send the results when you have them:
- S5: RC-loss failsafe over ELRS MAVLink.
- OPEN-017: how the ESC reacts when DShot frames stop (halt the H743 over SWD while armed, checklist P4-011).
- Servo current: the current of all servos together, and of one servo stalled, from your bench test (OPEN-007).
