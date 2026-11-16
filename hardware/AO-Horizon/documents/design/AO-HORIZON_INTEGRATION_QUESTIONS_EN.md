# AeroOptix-Horizon: Integration Questions for the Team

**Revision:** 0.5
**Updated:** 2026-11-16
**From:** Hardware
**To:** Software team, CAD team and all members
**Status:** D14 to D16 answered by the team on 2026-11-16 (spec DEC-051, checklist P0-023). Still open: the parts table and the team tests (checklist P0-022). Answered questions from rev 0.1 to 0.4 are in the spec (DEC-019 to DEC-023, DEC-050, MEC-002 to MEC-004) and in Git history.

## 1. How to reply

Under each question, fill `Answer:` and `By:` (name or role). In the parts table, fill the `Team` column. Write `later` if you do not know yet. Keep the file name and send the whole file back.

## 2. Already done (no reply needed)

Your earlier answers and the hardware decisions that followed are in the spec: DEC-019 to DEC-023 and MEC-002 to MEC-004.

D13 (ESC) is answered (2026-11-16, DEC-050). The ESCs use plain timer PWM, no DShot ("my team doesn't use dshot nr, it just timer that drive esc"). The F100 now drives the 4 ESCs and the 4 tilt servos, and the H743 drives the 2 flaperons and 2 ruddervators. No pins change; which actuator sits on which output is set in software:

| MCU | Outputs | Drives |
|---|---|---|
| F100 | TIM3_CH1 to CH4 | 4 tilt servos |
| F100 | TIM2_CH1, TIM2_CH2, TIM4_CH3, TIM4_CH4 | 4 ESCs |
| H743 | TIM5_CH1 to CH4 (PA0 to PA3) | 2 flaperons, 2 ruddervators |

D14 to D16 below follow from this change. The D15 answer swapped the servos again (spec DEC-051): the tilt servos moved to the H743 and the surfaces to F100 TIM3.

## 3. Questions D14 to D16 (answered 2026-11-16)

**D14. What happens when the H743 stops (whole team).**
You told us: "if main is gone, i/o still can control esc and tile that can make drone landed". The spec still says the opposite: when the H743 stops, the F100 sets fixed failsafe values, the motors stop, and there is no landing (SAF-001, DEC-016). We need your answer before we draw the actuator headers.
The F100 (px4io) cannot fly the aircraft by itself. It has no IMU, and it has no RC input since DEC-018. As recorded in the spec (DEC-016), px4io only sets each output to one fixed failsafe value 0.5 s after the H743 data stops.
- When the H743 is gone, what should the F100 output on the 4 ESCs and the 4 tilt servos: motors off, or a fixed descent throttle with a fixed tilt angle?
- If a descent: what keeps the aircraft level with no attitude control? Has this been tested on this or another aircraft?
- Do you plan to change the px4io firmware for this? If yes, what will it do?

Answer: Motors off. When the H743 stops, the F100 sets the ESC outputs to the disarmed value, so the motors stop. No descent throttle: the IO has no sensors, so a fixed throttle with no attitude control is not safe. No landing. We will not change the px4io failsafe logic; we only set the failsafe values with PX4 parameters. See D15 for the surfaces and the tilt servos.
By: Jakarin

**D15. Control surfaces when the H743 hangs (whole team).**
The flaperons and ruddervators now run from the H743 (TIM5). The F100 failsafe does not reach them. If the H743 hangs, its timer most likely keeps sending the last pulse, so the surfaces stay where they were (not checked).
- Is that OK? If not, what should the surfaces do when the H743 stops?

Answer: Not OK. The surfaces should go to a fixed position: 0° first, later the glide trim we find in flight tests. We propose to swap the servos between the two MCUs. No pin change; the mapping is set in software:

| MCU | Outputs | Drives |
|---|---|---|
| F100 | TIM2_CH1, TIM2_CH2, TIM4_CH3, TIM4_CH4 | 4 ESCs (no change) |
| F100 | TIM3_CH1 to CH4 | 2 flaperons, 2 ruddervators |
| H743 | TIM5_CH1 to CH4 (PA0 to PA3) | 4 tilt servos |

Reason: with the motors off (D14), the tilt angle no longer changes the flight, but the surfaces still decide how the aircraft glides in fixed-wing flight. With the swap, the F100 failsafe reaches the surfaces. On an H743 hang, the tilt servos hold their last angle, which we accept. The ESCs stay on separate timers from the surfaces, so the ESC rate can differ from the 50 Hz servo rate.
By: Jakarin

**D16. Output settings (software team).**
We need these for the connector labels and the bench tests.
- Which F100 output drives which ESC (front-R, rear-L, front-L, rear-R)?
- Which H743 TIM5 channel drives which surface (flaperon L and R, ruddervator L and R)?
- What PWM rate and throttle range (µs) will you set for the ESCs? The tilt servos on TIM3 stay at 50 Hz, and px4io sets one rate per timer.
- What failsafe value will you set on the ESC outputs?

Answer: The mapping is set in PX4 (QGC Actuators), which is part of our project. Please label the connectors by output number like Pixhawk: F100 outputs MAIN 1 to 8, H743 TIM5 outputs AUX 1 to 4. First mapping: MAIN 1 to 4 = motors 1 to 4 (front-R, rear-L, front-L, rear-R), MAIN 5 to 8 = flaperon L, flaperon R, ruddervator L, ruddervator R, AUX 1 to 4 = tilt servos. We may change it in software later. ESC throttle range 1000 to 2000 µs after ESC calibration; ESC failsafe = disarmed value (motor off). ESC PWM rate: later, after we check what the Skywalker 80A V2 accepts.
By: Jakarin

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
- OPEN-017: halt the H743 over SWD while armed and check what the ESCs, tilt servos and surfaces do (checklist P4-011).
- Servo current: all servos together, and one servo stalled (OPEN-007).
