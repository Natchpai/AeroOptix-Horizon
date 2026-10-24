# AeroOptix-Horizon: Integration Questions for the Team

**Revision:** 0.1
**Updated:** 2026-10-24
**From:** Hardware
**To:** Software team and all members
**Status:** Sent for the team's answers. Nothing here is decided. Hardware needs these answers before it picks connectors, designs the servo power path and places parts on the PCB (checklist P0-021).

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

Decision:
Servo models and stall current:
By:

**D9. Mounting, size and cable entry (MEC-001 to MEC-004, OPEN-009).**
Hardware needs, before PCB placement:
- Mounting hole pattern and screw size (for example 30.5 × 30.5 mm with M3, or 20 × 20 mm with M2).
- Hard mount or soft (vibration-damped) mount.
- Maximum height above and below the board (enclosure or frame space).
- Which board edge faces forward, and from which sides the cables come in.
- Whether USB and the microSD card must be reachable when the board is installed. The H743 debug connector already must be (team answer S6).

Decision:
By:

**D10. Environment (ENV-001 to ENV-004).**
Operating and storage temperature range, rain or dust exposure, and maximum flight altitude. Hardware uses this to choose part temperature grades and to decide on conformal coating.
If the team has no requirement, hardware proposes: parts rated −40 to +85 °C, no conformal coating, no rain exposure. Answer `OK` or give your values.

Decision:
By:

**D11. Safety switch, buzzer and GPS module (IF-012, IF-046, IF-049).**
The PX4 docs describe the Pixhawk 6C GPS1 port as "Full GPS port (GPS plus safety switch)". Many Pixhawk GPS modules carry the safety switch, its LED and sometimes a buzzer on the same cable (`ASSUMED`, not checked per module).
Options:
- (a) The GPS module carries the safety switch and LED. The board GPS connector carries them to the F100 (PB5 button, PB13 LED). The board buzzer stays (IF-046).
- (b) A separate safety switch with LED on its own board connector. The GPS connector carries only GPS and compass.
- (c) No physical safety switch (disabled in PX4). The F100 safety pins stay unconnected.

Hardware impact: connector pin count only.

Which GPS module (model) do you use?

Decision:
GPS model:
By:

## 4. External devices and connectors

Hardware proposal for every external port: the Pixhawk connector standard (JST-GH, 1.25 mm), so cables made for Pixhawk boards fit. Hardware has not read the standard (DS-009) yet; the pinouts will be checked before the schematic (`NOT_VERIFIED`). If your device comes with a different cable, write it in the `Team` column.

| Interface | Spec ID | Hardware proposal | Hardware needs from you | Team |
|---|---|---|---|---|
| Telemetry 1: ELRS receiver | IF-010 | JST-GH 6-pin, Pixhawk TELEM layout, 5 V supply. TX and RX only (no CTS/RTS on UART7) | Receiver model and supply voltage | |
| Telemetry 2 (free) | IF-011 | JST-GH 6-pin, as Telemetry 1 | Keep a connector, or pads only (no device is planned) | |
| GPS1 + compass | IF-012 | JST-GH 6-pin (GPS and I2C) or 10-pin (with safety switch, see D11) | GPS model (D11) | |
| Airspeed MS4525DO | IF-014 | JST-GH 4-pin, Pixhawk I2C layout (5 V, SCL, SDA, GND) on I2C4 | Exact part number: the 3.3 V or the 5 V version | |
| Power module PM02D | IF-048 | Connector that matches the cable on your PM02D | Connector type and pin count on your unit; chip on the label (INA228 or INA226) | |
| Rangefinder TF-Luna | IF-015 | JST-GH 4-pin (5 V, TX, RX, GND) on UART8 | Cable you use (TF-Luna has its own 6-pin connector) | |
| ESC 4-in-1 | IF-040 to IF-043 | Connector that matches the ESC signal cable | ESC model and its cable pinout. Do you want the ESC current sense or ESC telemetry wire connected? Both are possible with free H743 pins | |
| 8 servos | IF-030 to IF-037 | 3-pin 2.54 mm headers, or signal-only connector (see D8) | Set by D8 | |
| 3 spare outputs | IF-017 to IF-019 | Pads only (no use planned, decisions file D4) | OK or a connector | |
| USB | IF-022 | USB-C on a board edge | USB-C or Micro-B, or a cable to the frame. Should USB power the board on the bench without the battery? | |

## 5. Questions for the software team

**S8. Stock px4io on the F100.**
Do you ship the stock `px4_io-v2_default` image in the port's `extras/` folder, as `px4/fmu-v6c` does? Your Q20 answer mentions bringing up an 8 MHz px4io build. With the F100 that build is not needed. Please confirm.

Answer:
By:

**S9. IMU heater.**
Hardware plans no IMU heater. On px4io-v2, PB14 is the blue LED and also a heater output; on this board it drives only the LED. Do you need an IMU heater for Model G (for example for cold-weather flights)?

Answer:
By:

**S10. Status of team tests.**
Two items wait on team tests: the RC-loss failsafe over ELRS MAVLink (S5), and how the chosen ESC reacts when DShot frames stop (spec OPEN-017, SAF-015). Any results yet? Which ESC is confirmed?

Answer:
By:

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
