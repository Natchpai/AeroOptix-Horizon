# AeroOptix-Horizon: Decisions and Questions after Pinmap Review 0.2

**Revision:** 0.2
**Updated:** 2026-10-24
**From:** Hardware
**To:** Software team and all members
**Status:** Answered by the software team on 2026-10-24 and accepted by the hardware owner. D1 to D7 are signed "Software team (proposal for the team)"; a separate whole-team confirmation is not recorded. The hardware owner's response is in section 9. The spec records the result in rev 0.11.

## 1. How to reply

Thank you for the answers in pinmap review 0.2 (`AO-HORIZON_PINMAP_REVIEW_EN.md`). They change several spec items and leave some decisions open. The team owns the drone spec and the software function spec. Hardware follows them.

You can fill this in by hand or ask Claude to do it.

1. Sections 3 and 4 are for the whole team. Section 5 is for the software team. Section 6 lists two hardware proposals that change your board config; accept or change them. Hardware design choices that do not affect the drone spec or the software are not in this file.
2. In tables, fill only the `Team` column with one of:
   - `OK`: accept the row as written.
   - `CHANGE: <what>`: say exactly what you want instead.
   - `?: <question>`: you need hardware to explain.
3. Under each question, fill the `Decision:` or `Answer:` line, and the `By:` line with the name or role of whoever decided.
4. Section 7 is for information only. It lists what hardware does without your input.
5. Keep the file name. Send the whole file back.

After your reply, hardware updates the spec (`AO-HORIZON_SPEC_EN.md`) and the pinmap to revision 0.3.

## 2. What hardware checked

Hardware checked your answers against the PX4 source at tag v1.16.2 (`boards/px4/io-v2` and `boards/px4/fmu-v6c`) and the STM32F103 datasheet. These facts are used below. Labels: `VERIFIED` = read in the source, `ASSUMED` = not checked, `NOT_VERIFIED` = check still open.

| # | Fact | Source | Label |
|---|---|---|---|
| F1 | px4io-v2 talks to the FMU on USART2 at 1.5 Mb/s. Its console is USART1. | io-v2 `board_config.h`: `PX4FMU_SERIAL_BASE STM32_USART2_BASE`, `PX4FMU_SERIAL_BITRATE 1500000`; `defconfig`: `CONFIG_USART1_SERIAL_CONSOLE=y` | VERIFIED |
| F2 | px4io-v2 PWM: TIM2 CH1/2 on PA0/PA1, TIM4 CH3/4 on PB8/PB9, TIM3 CH1 to CH4 on PA6, PA7, PB0, PB1. Same as pinmap 4.1. | io-v2 `timer_config.cpp` | VERIFIED |
| F3 | px4io-v2 is built for an STM32F100C8, with SYSCLK taken straight from a 24 MHz HSE. | io-v2 `defconfig`: `CONFIG_ARCH_CHIP_STM32F100C8=y`; `board.h`: `STM32_BOARD_XTAL 24000000ul`, `STM32_SYSCLK_SW RCC_CFGR_SW_HSE` | VERIFIED |
| F4 | If no FMU data arrives for 0.5 s, px4io sets its outputs to the failsafe values. | `px4iofirmware/mixer.cpp`: `FMU_INPUT_DROP_LIMIT_US 500000`, `r_page_servos[i] = r_page_servo_failsafe[i]` | VERIFIED |
| F5 | px4io-v2 also uses these F103 pins: LEDs PB14 (blue, also heater output), PB15 (amber), PA11 (green); servo fault input PA15; RSSI PA5 and PA12; Spektrum PC13 and PA10; SBUS PB10, PB11, PB4; PPM PA8; board sense PC14 and PC15. Safety button PB5, safety LED PB13, servo rail sense PA4. | io-v2 `board_config.h` | VERIFIED |
| F6 | fmu-v6c uses a 16 MHz HSE. | fmu-v6c `board.h`: `STM32_BOARD_XTAL 16000000ul` | VERIFIED |
| F7 | fmu-v6c: HRT on TIM8 CH3. Tone alarm on TIM3 CH3, PB0. | fmu-v6c `board_config.h` | VERIFIED |
| F8 | fmu-v6c: PWM on TIM1 (PA8, PE11, PE13, PE14), TIM4 (PD14, PD15), TIM5 (PA0, PA1). Only TIM1 and TIM4 have DMA. | fmu-v6c `timer_config.cpp`: `initIOTimer(Timer::Timer1, DMA{DMA::Index1})`, same for Timer4 | VERIFIED |
| F9 | fmu-v6c: console USART3 (PD8, PD9). PX4IO on USART6 (PC6, PC7). microSD on SDMMC2 (PD6, PD7, PB14, PB15, PB3, PB4), with no card-detect pin. | fmu-v6c `defconfig`, `board.h`, `board_config.h` | VERIFIED |
| F10 | fmu-v6c `defconfig` has `CONFIG_WATCHDOG=y`. Whether PX4 starts the H743 IWDG was not checked. | fmu-v6c `defconfig` | NOT_VERIFIED |
| F11 | Bidirectional DShot on STM32H7 must use the first 4 FMU outputs, all on one timer. Read in the v1.17 docs; v1.16.2 not checked. | docs.px4.io/v1.17/en/peripherals/dshot | NOT_VERIFIED for v1.16.2 |
| F12 | An STM32 timer in PWM mode keeps sending its last pulse width if the CPU hangs. DShot stops, because it needs the CPU to refill DMA for each frame. | General STM32 timer behavior | ASSUMED |
| F13 | The STM32F103 HSE crystal oscillator is specified for 4 to 16 MHz. An external clock on OSC_IN (HSE bypass) may be 1 to 25 MHz. So the 24 MHz crystal that stock px4io-v2 expects (F3) is outside the F103 datasheet range. | ST DS5319 Rev 20, Table 22 (HSE 4-16 MHz oscillator) and Table 20 (HSE user external clock), read in the datasheet text | VERIFIED |

## 3. Spec items your answers change

Your 0.2 answers do not match these spec rows. For each row, say whether the spec should change as listed. The spec tracks this list as OPEN-016.

| Spec ID | Spec now (short) | What your 0.2 answers mean | Team |
|---|---|---|---|
| SYS-002 | Pixhawk 6C and 6X are references only; no copied pinout. | Most H743 pins come from Pixhawk 6C, and the port is based on `px4/fmu-v6c` (Q1, Q18). | OK |
| IF-001, IF-024, OPEN-002 | H743↔F103 link is USART; instance, pins and rate are open. | H743 USART6 (PC6, PC7) to F103 USART2 (PA2, PA3), 1.5 Mb/s, px4io protocol (Q7, F1). | OK |
| SAF-001, FUN-004 | If the H743 stops, the F103 commands an immediate landing. | Stock px4io cannot land. It sets its outputs to failsafe values after 0.5 s (Q7, F4). See D1. | OK (D1 a) |
| SAF-010, SAF-011 | F103 monitors the H743; output ownership after a link loss is open. | Same as above. The motors are no longer on the F103 (Q17). See D1, D2. | OK. The H743 owns the 4 motor outputs, the F103 owns the 8 servo outputs (D1, D2) |
| FUN-002 | F103 drives the ESC-related PWM outputs. | All 4 ESCs move to the H743 (TIM5, PA0 to PA3). The F103 drives the 8 servos only (Q17). See D2. | OK (D2 a) |
| FUN-003, IF-030 to IF-037 | F103 outputs TILT, ESC, COAX, AIL. | 8 servo outputs, renamed: flaperon L/R, ruddervator L/R, tilt servo 1 to 4 (Q17, pinmap 4.1). | OK |
| IF-038 | FlySky receiver on the F103. | Dropped. RC comes from ELRS (MAVLink) on Telemetry 1, UART7 (Q5). See D6. | OK |
| IF-013 | GPS2 reserved on UART3. | Dropped. UART3 is the debug console (pinmap 3.1). See D5. | OK |
| IF-016 | Reserved UART7 TX. | Dropped (Q4). | OK |
| IF-017 to IF-021 | VT L/R (TIM4), SP2 (TIM1), TL2/TR2 (TIM15). | PD14, PD15 and PE9 are spare outputs. PA2 and PA3 become motors 3 and 4 on TIM5. Motors 1 and 2 are added on PA0 and PA1 (Q17). | OK |
| SEN-002, OPEN-014 | Barometer 2 is open; BMP581 proposed. | BMP581 on I2C2 at 0x46 (pinmap section 5). See D7. | OK (D7) |
| New | Not in the spec. | Add interface rows for: microSD (SDMMC1), buzzer, 3 board LEDs, safety switch and LED on the F103, power module on I2C4, servo rail sense on F103 PA4, H743 debug console (UART3). | OK |

## 4. Decisions for the whole team

Each decision sets drone behavior or the drone spec. Hardware can build any of the options; the hardware impact is listed so you can compare.

**D1. Behavior when the H743 stops (SAF-001, FUN-004, SAF-010).**
Options:
- (a) Reword the spec to match stock px4io: after 0.5 s without the H743, the F103 holds its outputs at fixed failsafe values (F4). No landing.
- (b) Keep "immediate landing". That needs custom F103 firmware, and a definition of how the F103 lands the aircraft without an IMU.
- (c) Other.

Hardware impact: none for (a). For (b), it depends on the definition; the F103 might need sensors or more pins.

Decision: (a). After 0.5 s without the H743, the F103 holds the 8 servos at fixed values (D3). The motors stop on ESC signal loss (D2, S1). No landing.
By: Software team (proposal for the team)

**D2. Where the 4 ESC outputs connect: H743 or F103 (FUN-002).**
Your plan puts them on the H743, TIM5, so they can run DShot (Q17). The trade-off: on the H743, the F103 failsafe (F4) does not cover the motors. If the H743 hangs with the motors in PWM mode, they keep their last throttle (F12). DShot or a watchdog reset would stop them (see S1).
Options:
- (a) H743 TIM5, PA0 to PA3, as you planned. Requires a safe answer to S1.
- (b) F103, with the F103 failsafe covering the motors. No DShot (stock px4io has no DShot, ASSUMED), and the F103 runs out of outputs for the 8 servos.

Hardware impact: pin assignment only. Both options fit the board.

Decision: (a) H743 TIM5, PA0 to PA3, with the motors in DShot only (S1). This needs DShot-capable ESCs; the planned ESC is a Holybro Tekko32 F4 4-in-1 with AM32 firmware, still to be confirmed.
By: Software team (proposal for the team)

**D3. Failsafe positions for the 8 servos.**
When the H743 stops, px4io moves each servo to a fixed failsafe value (F4). For a tilt-rotor this sets the aircraft's state after the failure. Give the position you want for the tilt servos (1 to 4), the flaperons (L, R) and the ruddervators (L, R). For example: tilt up for hover, or tilt forward for cruise. Flaperons and ruddervators centered.

Decision: No hardware impact: these positions are PX4 parameters, and we will set them after flight tests. With PX4 defaults (flight termination off), px4io uses the disarmed values (PWM_MAIN_DISn) when the H743 stops. These are the same values the servos hold on the ground before arming, so the tilt servos go to the hover position (rotors up). A different in-flight value, for example tilt forward for cruise, needs PWM_MAIN_FAILn with flight termination on, which is a separate team decision. Flaperons and ruddervators: centered.
By: Software team (proposal for the team)

**D4. Spare outputs.**
Model G uses 12 outputs: 4 on the H743 and 8 on the F103. That leaves 3 spares on the H743: PD14 and PD15 (TIM4) and PE9 (TIM1). Do you expect more outputs later, for example a gimbal, payload release or landing gear? If yes, list them.

Decision: No more outputs are planned for Model G (no gimbal, payload release or retractable gear). Keep the 3 spares.
By: Software team (proposal for the team)

**D5. Single GPS.**
GPS2 is dropped, and UART3 becomes the debug console. Is one GPS enough for Model G?

Decision: Yes, one GPS (with compass) is enough.
By: Software team (proposal for the team)

**D6. One link for RC and telemetry.**
RC and telemetry share one ELRS receiver on UART7, so losing that link loses both. There is no backup RC input on the board. Is that OK for Model G? If not, hardware can keep a second receiver input. Telemetry 2 (USART1) is free for this.

Decision: OK for Model G. When the ELRS link drops, we expect PX4 to run its RC-loss and data-link-loss failsafes; the S5 bench test will confirm it. Telemetry 2 stays free, so a second receiver can be added later with no hardware change.
By: Software team (proposal for the team)

**D7. Barometer 2 (OPEN-014).**
Your section 5 reply puts the BMP581 on I2C2 at 0x46, but it does not say that the BMP581 is accepted. Please confirm the BMP581 as barometer 2, or name another part.

Decision: Accept the BMP581 (PX4 driver bmp581, 0x46). If it cannot be bought (DigiKey showed 0 in stock on 2026-10-08, 10,000 due 2026-11-19), the fallback is a BMP384 (PX4 bmp388 driver).
By: Software team (proposal for the team)

## 5. Questions for the software team

**S1. Motor outputs when the H743 hangs (linked to D2).**
How will the port make sure the motors stop if the H743 hangs? Choose one or both:
- (a) The motors run DShot only, with no PWM fallback.
- (b) The H743 IWDG is enabled, so a hang resets the MCU and the pins go to their reset state.

F10: fmu-v6c has `CONFIG_WATCHDOG=y`, but hardware did not check that the IWDG is started.

Answer: (a). The motors run DShot only, with no PWM fallback (this needs DShot-capable ESCs, D2). PX4 starts a new DShot frame from software every cycle (`up_dshot_trigger` in `dshot.c`), so a hang stops the frames and the ESCs see signal loss. (b) is not available as is: PX4 v1.16.2 has no code that starts the STM32H7 IWDG (watchdog code exists only for STM32F4, the F1 used by px4io, and S32K1). `CONFIG_WATCHDOG=y` only builds the NuttX driver. This answers F10. The F103 side is covered: px4io starts its own IWDG.
By: Software team

**S2. DMA for TIM5.**
In fmu-v6c, TIM5 has no DMA (F8). DShot on PA0 to PA3 needs it. Can the AO-Horizon port add DMA for TIM5?

Answer: Yes. The PX4 STM32H7 timer code maps DMA for TIM5, both for the update and for the channel capture used by bidirectional DShot (`io_timer_hw_description.h`). Pixhawk 6X (`px4/fmu-v6x`, v1.16.2) declares TIM5 with DMA as its first timer, and the fmu-v6c `board_dma_map.h` already lists a DMA1 slot for TIM5UP. Our `timer_config.cpp` will declare TIM5 with DMA.
By: Software team

**S3. Bidirectional DShot and PX4 version.**
Do you need bidirectional DShot (RPM feedback)? If yes, TIM5 must be the first timer in `timer_config.cpp` (F11). Which PX4 version will the port use (v1.16.2, or later)?

Answer: Yes, we need bidirectional DShot: it gives the motor RPM our motor model needs. Checked in v1.16.2 (this answers F11): `dshot.c` runs bidirectional DShot on timer index 0 only (`_bidi_timer_index = 0`). So TIM5 will be the first timer in `timer_config.cpp`, and the motors will be FMU outputs 1 to 4. This is the stock Pixhawk 6X setup in v1.16.2 (TIM5 with DMA as timer 0). PX4 version: v1.16.2, the version our Model G work uses.
By: Software team

**S4. microSD on SDMMC1.**
fmu-v6c uses SDMMC2 (F9), but its pins clash with GPS1 RX (PD6) and Telemetry 2 (PB14, PB15) on our board. So the board uses SDMMC1: CK PC12, CMD PD2, D0 to D3 on PC8 to PC11. Is that OK for your `board.h`? Do you want a card-detect pin? fmu-v6c has none.

Answer: OK. SDMMC1 on those pins works (matek/h743-slim uses the same pins). No card-detect pin is needed.
By: Software team

**S5. RC over ELRS MAVLink.**
Your bench test covered ELRS telemetry to QGC (Q2). Did you also test RC control and RC-loss failsafe over MAVLink? If not, please test both before the pinmap is frozen.

Answer: Partly. RC values reached PX4 over ELRS MAVLink (`rc_update` source = MAVLink). Controlling the vehicle by RC and the RC-loss failsafe are not tested yet; we will test both on the bench. No pin depends on the result: if RC over MAVLink fails, the same receiver can run CRSF on the same UART7 (PX4 `crsf_rc` driver).
By: Software team

**S6. Debug and flashing access.**
Hardware will give you the H743 console (UART3) and SWD, and the F103 SWD and px4io console (USART1 TX). How will you use them: on the bench only, or also on the assembled drone with a cable plugged in? Who flashes the px4io bootloader on the first F103 flash (Q9)? Hardware picks the connector type from your answer.

Answer: H743: also on the assembled drone. Please put the console (UART3) and SWD on one 6-pin JST-SH connector in the Pixhawk Debug Mini layout (Pixhawk connector standard DS-009) that we can reach after assembly. Normal firmware updates go over USB. F103: bench only, so pads or a header are fine; PX4 updates the IO firmware over the link (Q9). The software team flashes the px4io bootloader on the first F103 flash, and the PX4 bootloader on the first H743 flash, with an ST-LINK.
By: Software team

**S7. F103 clock for px4io.**
Stock px4io-v2 runs the F103 straight from a 24 MHz HSE (F3), but a 24 MHz crystal is outside the F103 datasheet range (F13). Hardware sees three ways out:
- (a) An 8 MHz crystal (inside the range), and a px4io build that uses the PLL (×3) to make 24 MHz. Needs a changed `board.h` in your px4io build.
- (b) A 24 MHz oscillator module on OSC_IN (inside the external-clock range), and a px4io build with HSE bypass on. Needs a changed `board.h` in your px4io build.
- (c) Stock px4io with a 24 MHz crystal. No firmware change, but the F103 runs outside its datasheet. Hardware does not recommend it.

PX4 updates the F103 from the px4io image inside your H743 build (Q9), so a custom px4io build ships with your firmware (ASSUMED). Can you build and keep a custom px4io image? Which option do you accept?

Answer: Preferred: a fourth option, (d). Fit an STM32F100C8T6B, the chip px4io-v2 is built for (F3). Its crystal oscillator is specified for 4 to 24 MHz, so stock px4io and its bootloader run unchanged with a 24 MHz crystal. It comes in the same LQFP48 package; please check its pinout against the F103 (PA11/PA12 are USB on the F103 and plain GPIO on the F100; px4io uses them for an LED and RSSI). DigiKey had 988 in stock on 2026-10-08. If you must keep the F103, we accept (a), an 8 MHz crystal with PLL x3. We can build and keep a custom px4io image: it is built from the same PX4 tree, and the H743 build ships it from the board's `extras/` folder (fmu-v6c ships `px4_io-v2_default.bin` there). The px4io bootloader then has to be rebuilt for 8 MHz too. Not (c). For reference, the PX4 docs list an STM32F103 as the Pixhawk 6C IO processor, but do not show how its clock is wired.
By: Software team

## 6. Hardware proposals for pinmap 0.3

Both change your board config, so hardware needs your OK. Fill the `Team` column.

| # | Proposal | Reason | Team |
|---|---|---|---|
| H1 | H743 crystal 16 MHz instead of 8 MHz. | Same as fmu-v6c (F6), so the clock setup needs no change in the port. You said 16 MHz also works (Q6). | OK |
| H2 | Buzzer on TIM3_CH3, PB0, instead of TIM2_CH1, PA15. HRT stays on TIM8. | Same as fmu-v6c (F7), so the tone alarm config needs no change. PB0 is free since the IMU pin-9 rows were dropped. | OK |

## 7. For information, no reply needed

- Hardware follows your answers on the PWM pull-downs (Q10), F103 PC14 and PC15 (Q6), and the px4io-v2 pins (F5).
- Hardware checked the F103 clock limits (F13). The result affects the px4io build, so it is asked in S7.
- After your reply, hardware updates the spec rows in section 3 and issues pinmap 0.3.

## 8. Sources

PX4-Autopilot, tag v1.16.2, `https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/`:

- `io-v2/nuttx-config/nsh/defconfig`, `io-v2/nuttx-config/include/board.h`, `io-v2/src/board_config.h`, `io-v2/src/timer_config.cpp`
- `src/modules/px4iofirmware/mixer.cpp`
- `fmu-v6c/nuttx-config/nsh/defconfig`, `fmu-v6c/nuttx-config/include/board.h`, `fmu-v6c/src/board_config.h`, `fmu-v6c/src/timer_config.cpp`

PX4 docs: `https://docs.px4.io/v1.17/en/peripherals/dshot` (bidirectional DShot).

ST: DS5319 Rev 20, STM32F103x8/B datasheet, Tables 20 and 22 (`https://www.st.com/resource/en/datasheet/stm32f103c8.pdf`).

## 9. Hardware owner response (2026-10-24)

- All answers accepted as written, except S7.
- **S7:** the IO MCU stays STM32F103C8T6 (DEC-002). The proposed STM32F100C8T6B is not used. The team's fallback applies: option (a), an 8 MHz crystal with PLL ×3 to 24 MHz. The software team builds and keeps the px4io image and the px4io bootloader for 8 MHz.
- **S6:** the PX4 docs give the Pixhawk Debug Mini pinout as 1 VREF, 2 Console TX, 3 Console RX, 4 SWDIO, 5 SWCLK, 6 GND. NRST is not on the connector; hardware adds an NRST pad next to it (`https://docs.px4.io/main/en/debug/swd_debug.html`, read 2026-10-24; DS-009 itself not read).
- **New open items from the answers** (spec rev 0.11): motor stop on an H743 hang depends on the ESC's signal-loss behavior (OPEN-017); the PWM pull-down value must suit bidirectional DShot (OPEN-018); the BMP384 fallback needs a footprint check against the BMP581 (OPEN-019).
- Pinmap review 0.3 (`AO-HORIZON_PINMAP_REVIEW_EN.md`) shows the result.
