# AeroOptix-Horizon: Integration Questions for the Team

**Revision:** 0.4
**Updated:** 2026-10-24
**From:** Hardware
**To:** Software team, CAD team and all members
**Status:** Open questions only (checklist P0-022). Answered questions from rev 0.1 to 0.3 are in the spec (DEC-019 to DEC-023, MEC-002 to MEC-004) and in Git history.

## 1. How to reply

Under each question, fill `Answer:` and `By:` (name or role). In the parts table, fill the `Team` column. Write `later` if you do not know yet. Keep the file name and send the whole file back.

## 2. Already done (no reply needed)

- **Answered by you (rev 0.2):** servo power, environment, GPS port and safety switch, external devices, stock px4io, no IMU heater (S8 to S10). Hardware changed the servo power to a Pixhawk-style servo rail: each servo plugs into a 3-pin header on the board (DEC-019).
- **Set by hardware:** M3 screws (3.2 mm holes), soft mount, board on its own tray (not on the ESC), USB-C and microSD on adjacent edges, parts up to about 10 to 15 mm tall. USB powers the board and all 5 V ports on the bench. Every servo model is rated for 6 V.
- **ESC:** 4 × 3-pin headers with the + pin removed, so the ESC BEC does not reach the board. No ESC current sense or telemetry.
- **For the CAD team:** hardware sends the board outline, height, cable entry sides and dampers. Please draw the tray and the space under the GPS to fit.

## 3. Open question

**D13. ESC (whole team).**
You chose 4 × Skywalker 80A V2. It looks like a PWM ESC; we found no source saying it supports DShot. The spec says DShot only (FUN-002), and the motors stop on an H743 hang because DShot frames stop (SAF-015). With PWM, the signal may keep going after a hang, so the motors may not stop.
- Is PWM OK for you? If yes, how should the motors stop if the H743 hangs?

Answer:
By:

## 4. Parts

| Item | What we need | Known | Team |
|---|---|---|---|
| ELRS receiver | Model and link | | |
| GPS module | Confirm Holybro M9N, photo of the plug | | |
| Airspeed | Link or photo; 3.3 V or 5 V version | MS4525DO | |
| PM02D | Chip on the label (INA228 or INA226), photo of the plug | | |
| ESC | Link | 4 × Skywalker 80A V2 | |
| Tilt servos | Stall current | 4 × RDS3235 | |
| Other servos | Which goes where (flaperon, ruddervator), how many, stall current | Kingmax C507, DS-843MG | |
| UBEC | Model and link | 10 A, XT30 | |

## 5. Team tests still open

Send the results when you have them:
- S5: RC-loss failsafe over ELRS MAVLink.
- OPEN-017: how the ESC reacts when the H743 stops sending (halt the H743 over SWD while armed, checklist P4-011).
- Servo current: all servos together, and one servo stalled (OPEN-007).
