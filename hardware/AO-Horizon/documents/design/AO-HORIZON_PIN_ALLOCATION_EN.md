# AeroOptix-Horizon: MCU Pin Allocation

**Revision:** 0.32
**Updated:** 2026-11-24
**Status:** `ALLOCATED`, not `VERIFIED`: signed off by the human owner on 2026-11-21 (section 6; checklist P1 closed). The software team's answers (pinmap review 0.2 and 0.3, decisions file) are applied. The IO MCU is the STM32F100C8T6B (DEC-002). Partly drawn in the schematic (spec 4.2 "Schematic state"); the drawn labels match this allocation (F-19). HSE from CMOS oscillators (DEC-044, DEC-045). Actuator outputs per DEC-050 and DEC-051 (F100 MAIN 1 to 8, H743 AUX 1 to 4); no pin changed. Since 2026-11-24, F100 PA5 is the second servo rail sense (DEC-110, DEC-113), and the `mcu-io` resistors are re-annotated (spec 4.2 F100 row). DMA and interrupt priority checks are firmware work (P2-005); timer clocks are part of the pin review (P1-001). Not a verification record.
**Requirement refs:** IF-010 to IF-024, IF-030 to IF-037, IF-040 to IF-051, SEN-001 to SEN-003, DEC-002, DEC-014 to DEC-018, DEC-043 to DEC-047, DEC-050, DEC-051, DEC-053, DEC-054, DEC-056, DEC-057, DEC-060, DEC-068, DEC-069, DEC-079. Checklist tasks: P1-001 (partial), P1-003 (partial).
**Decision owner:** Hardware

Single record for the STM32H743VIT6 (LQFP100) and STM32F100C8T6B (LQFP48) pin allocation.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`.

Source keys used below:
- **ST XML**: ST `STM32_open_pin_data` repo, `mcu/STM32H743VITx.xml` and `mcu/STM32F103C(8-B)Tx.xml` (commit `7d1f151`), and `mcu/STM32F100C(8-B)Tx.xml` (`master`, fetched 2026-10-24). Lists the signals that each package pin can carry.
- **H7 DS**: ST DS12110 Rev 11 (STM32H742xI/G, STM32H743xI/G), Table 9 pin/ball definition, read as NotebookLM source fulltext (notebook `STM32H743VI`).
- **F1 DS**: ST DS5319 Rev 20 (STM32F103x8/B), Table 5, NotebookLM notebook `STM32F103C8T`; used for the section 2 checks before the IO MCU changed.
- **F100 DS**: ST DocID16455 Rev 9 (STM32F100x4/6/8/B), Table 4 pin definitions and Tables 8, 10, 21, read as NotebookLM source fulltext (notebook `STM32F100`), 2026-10-24.

How each row was checked:
- **Pin/signal**: a script confirmed the signal is listed for that pin in ST XML, so it is `VERIFIED`.
- **DS**: a script found the signal name in that pin's row of the datasheet text. This is a text match on extracted PDF text, so a human should still confirm the critical pins against the datasheet. `not checked` means the row was added after the datasheet pass.
- **Conflicts**: no pin is assigned twice, and the interrupt pins use different EXTI lines (checked by script, 2026-10-24).
- **Source**: the H743 pins mostly follow Pixhawk 6C (`px4/fmu-v6c`) and the F100 pins follow `px4/io-v2`, by team decision (DEC-014). The team tested them on a NUCLEO-H753ZI and in PX4 SITL only (pinmap review Q2). Some pins were proposed by hardware and accepted by the team (pinmap review section 3.6, decisions file H2).

Script inputs and outputs are not kept in the repo.

## 1. STM32H743VIT6 (LQFP100)

| Function | Ref | Signal | Pin | LQFP100 | DS |
| -------- | --- | ------ | --- | ------- | -- |
| Telemetry 1 (SiK radio, DEC-053) | IF-010 | UART7_TX | PE8 | 38 | match |
| Telemetry 1 (SiK radio, DEC-053) | IF-010 | UART7_RX | PE7 | 37 | match |
| Telemetry 2 | IF-011 | USART1_TX | PB14 | 53 | match |
| Telemetry 2 | IF-011 | USART1_RX | PB15 | 54 | match |
| GPS1 | IF-012 | USART2_TX | PD5 | 86 | match |
| GPS1 | IF-012 | USART2_RX | PD6 | 87 | match |
| GPS1 compass | IF-012 | I2C1_SCL | PB8 | 95 | match |
| GPS1 compass | IF-012 | I2C1_SDA | PB9 | 96 | match |
| Debug console | IF-045 | USART3_TX | PD8 | 55 | match |
| Debug console | IF-045 | USART3_RX | PD9 | 56 | match |
| MS4525DO + power module | IF-014, IF-048 | I2C4_SCL | PD12 | 59 | match |
| MS4525DO + power module | IF-014, IF-048 | I2C4_SDA | PD13 | 60 | match |
| TF-Luna | IF-015 | UART8_TX | PE1 | 98 | match |
| TF-Luna | IF-015 | UART8_RX | PE0 | 97 | match |
| AUX 1, tilt servo | IF-034, IF-035, IF-036, IF-037 | TIM5_CH1 (AF2) | PA0 | 22 | not checked |
| AUX 2, tilt servo | IF-034, IF-035, IF-036, IF-037 | TIM5_CH2 (AF2) | PA1 | 23 | not checked |
| AUX 3, tilt servo | IF-034, IF-035, IF-036, IF-037 | TIM5_CH3 (AF2) | PA2 | 24 | not checked |
| AUX 4, tilt servo | IF-034, IF-035, IF-036, IF-037 | TIM5_CH4 (AF2) | PA3 | 25 | not checked |
| Spare output 1 | IF-017 | TIM1_CH1 | PE9 | 39 | match |
| Spare output 2 | IF-018 | TIM4_CH3 | PD14 | 61 | match |
| Spare output 3 | IF-019 | TIM4_CH4 | PD15 | 62 | match |
| USB FS | IF-022 | OTG_FS_DM | PA11 | 70 | match |
| USB FS | IF-022 | OTG_FS_DP | PA12 | 71 | match |
| USB VBUS sense | IF-022 | OTG_FS_VBUS | PA9 | 68 | match |
| SWD | IF-045 | SWDIO | PA13 | 72 | not checked |
| SWD | IF-045 | SWCLK | PA14 | 76 | not checked |
| Reset (one button, DEC-046; since the 2026-11-20 13:01 save on `H7_RESET_B`, to B901 through D201, drawn, not decided, spec OPEN-026) | TST-001 | NRST | NRST | 14 | - |
| F100 link | IF-024 | USART6_TX | PC6 | 63 | match |
| F100 link | IF-024 | USART6_RX | PC7 | 64 | match |
| IMU1 | SEN-001 | SPI1_SCK | PA5 | 29 | match |
| IMU1 | SEN-001 | SPI1_MISO | PA6 | 30 | match |
| IMU1 | SEN-001 | SPI1_MOSI | PA7 | 31 | match |
| IMU1 CS | SEN-001 | GPIO output | PA4 | 28 | - |
| IMU1 INT1 | SEN-001 | GPIO input, EXTI4 | PC4 | 32 | - |
| IMU2 | SEN-001 | SPI4_SCK | PE12 | 42 | match |
| IMU2 | SEN-001 | SPI4_MISO | PE13 | 43 | match |
| IMU2 | SEN-001 | SPI4_MOSI | PE14 | 44 | match |
| IMU2 CS | SEN-001 | GPIO output | PE11 | 41 | - |
| IMU2 INT1 | SEN-001 | GPIO input, EXTI15 | PE15 | 45 | - |
| ICP-20100 + BMP581 + IST8310 | SEN-002, SEN-003 | I2C2_SCL | PB10 | 46 | match |
| ICP-20100 + BMP581 + IST8310 | SEN-002, SEN-003 | I2C2_SDA | PB11 | 47 | match |
| microSD | IF-044 | SDMMC1_D0 | PC8 | 65 | not checked |
| microSD | IF-044 | SDMMC1_D1 | PC9 | 66 | not checked |
| microSD | IF-044 | SDMMC1_D2 | PC10 | 78 | not checked |
| microSD | IF-044 | SDMMC1_D3 | PC11 | 79 | not checked |
| microSD | IF-044 | SDMMC1_CK | PC12 | 80 | not checked |
| microSD | IF-044 | SDMMC1_CMD | PD2 | 83 | not checked |
| Buzzer | IF-046 | TIM3_CH3 (AF2) | PB0 | 34 | not checked |
| LED red | IF-047 | GPIO output, active low | PE2 | 1 | - |
| LED blue | IF-047 | GPIO output, active low | PE3 | 2 | - |
| LED green | IF-047 | GPIO output, active low | PE4 | 3 | - |
| Analog battery V: removed, PC0 unused (spec DEC-107, 2026-11-21) | IF-048 | - | PC0 | 15 | - |
| Analog battery I: removed, PC1 unused (spec DEC-107, 2026-11-21) | IF-048 | - | PC1 | 16 | - |
| HSE CMOS oscillator, 16 MHz | DEC-044 | OSC_IN | PH0 | 12 | - |
| Not used (HSE bypass, DEC-045) | DEC-045 | OSC_OUT | PH1 | 13 | - |
| Boot select | P1-007 | BOOT0 (push button B902 to 3.3 V, R202 pull-down; spec DEC-095) | BOOT0 | 94 | - |

AF numbers (`VERIFIED`): the NuttX pinmap gives AF2 for TIM5_CH1 to CH4 on PA0 to PA3 and for TIM3_CH3 on PB0 (`documents/reference/px4-matek-h743-slim/stm32h7x3xx_pinmap.h`). HRT runs on TIM8, which needs no pin (team, Q15). IMU pin 9 (INT2/FSYNC/CLKIN) is not connected to the MCU; it is handled as the ICM-45686 datasheet says for an unused pin (team, Q16).

Design choices behind the table (`ASSUMED`, for review):
- Each IMU has its own SPI bus (SPI1, SPI4), so a fault on one bus does not take out both IMUs.
- Both barometers and the magnetometer share I2C2 (I2C3 dropped by the team to free PC9 for microSD). Addresses: ICP-20100 0x63, BMP581 0x46, IST8310 0x0C (spec DEC-047; the PX4 start script sets it, P1-017). They do not overlap. One bus fault can now take out both barometers.
- USART6 for the F100 link, same as `px4/fmu-v6c`.
- TIM5 (PA0 to PA3) drives the 4 tilt servos as AUX 1 to 4 (spec DEC-050, DEC-051); the team sets which tilt servo is on which AUX output in PX4. No DShot. Before DEC-050 TIM5 drove the motors with bidirectional DShot (team, S3).
- microSD on SDMMC1, because the `px4/fmu-v6c` SDMMC2 pins clash with GPS1 RX and Telemetry 2 (F-14).
- Buzzer on TIM3_CH3, PB0, same as `px4/fmu-v6c` (decisions file H2). No board buzzer: PB0 drives the GPS module buzzer on GPS1 through Q701 (spec DEC-068). No pin changed.
- Spare outputs PE9, PD14, PD15 go to one row of 4 pads (SPARE1 to SPARE3, GND), each with 22 Ω series and the PWM pull-down (spec DEC-069). The 22 Ω and 100 kΩ pull-downs are drawn (2026-11-20, R716 to R721; 100 kΩ decided, spec DEC-073), and the pads CN707 to CN710 in the 12:36 save (pad footprint open, spec OPEN-039). No pin changed.
- TIM4 on PD14/PD15 rather than PB8/PB9, which leaves PB8/PB9 for I2C1.
- USB device only: PA10 (OTG_FS_ID) is not used (team, Q19).
- PA15, PB3 and PB4 (JTAG-only pins) are left free, since only SWD is used.

Free I/O after this allocation (25 pins): PA8, PA10, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC2_C, PC3_C, PC5, PC13, PC14, PC15, PD0, PD1, PD3, PD4, PD7, PD10, PD11, PE5, PE6, PE10. PA15, PB3 and PB4 are also free but not counted. PC14 and PC15 are free because no LSE is used (team, Q6).

PH1 (H743) and PD1 (F100) are OSC_OUT pins, unused in HSE bypass (DEC-045). They are not in any free I/O list or count: their use as GPIO is `NOT_VERIFIED`.

Debug console (USART3), SWD and NRST: the drawn H743 debug connector has SWD and NRST (`RESET_B` on pin 4) but no console (spec OPEN-029). Since the 2026-11-18 16:52 save CN602 is in the Debug Mini order with the console; no NRST, reset by B901 (spec DEC-065, 2026-11-19).

## 2. STM32F100C8T6B (LQFP48)

Output numbers and the first actuator mapping follow spec DEC-051. The team sets the mapping in PX4 (QGC Actuators) and may change it; the pins do not change.

| Function | Ref | Signal | Pin | LQFP48 | DS (default / remap) |
| -------- | --- | ------ | --- | ------ | -------------------- |
| MAIN 1, motor 1 (front-R) | IF-040 | TIM2_CH1 | PA0 | 10 | match, default (TIM2_CH1_ETR) |
| MAIN 2, motor 2 (rear-L) | IF-041 | TIM2_CH2 | PA1 | 11 | match, default |
| MAIN 3, motor 3 (front-L) | IF-042 | TIM4_CH3 | PB8 | 45 | match, default |
| MAIN 4, motor 4 (rear-R) | IF-043 | TIM4_CH4 | PB9 | 46 | match, default |
| MAIN 5, flaperon L | IF-030 | TIM3_CH1 | PA6 | 16 | match, default |
| MAIN 6, flaperon R | IF-031 | TIM3_CH2 | PA7 | 17 | match, default |
| MAIN 7, ruddervator L | IF-032 | TIM3_CH3 | PB0 | 18 | match, default |
| MAIN 8, ruddervator R | IF-033 | TIM3_CH4 | PB1 | 19 | match, default |
| H743 link | IF-024 | USART2_TX | PA2 | 12 | match, default |
| H743 link | IF-024 | USART2_RX | PA3 | 13 | match, default |
| px4io console | IF-051 | USART1_TX | PA9 | 30 | match, default |
| RC IN, PPM (DEC-053), net `RCIN_TIM1_CH1` | IF-038 | TIM1_CH1 input capture | PA8 | 29 | FT; F100 DS Table 4 lists TIM1_CH1 as default; driven by the RC IN buffer U303 SN74LVC1G34DCKR (DEC-056, DEC-057, F-21) |
| Safety button | IF-049 | GPIO input | PB5 | 41 | R309 10 kΩ to `GND` (R310 before the 2026-11-24 re-annotation; F-22) |
| Safety LED | IF-049 | GPIO output, open drain, active low | PB13 | 26 | net `GPS1_SAFETY_LED_B` since the 2026-11-19 15:20 save |
| Servo rail 1 sense (`+VSERVO1`) | IF-050 | ADC1_IN4 (3:1 divider) | PA4 | 14 | not checked |
| Servo rail 2 sense (`+VSERVO2`) | IF-050 | ADC1_IN5 (3:1 divider), net `F1_ADC1_IN5` (DEC-110, DEC-113) | PA5 | 15 | not checked |
| SWD | IF-051 | SWDIO | PA13 | 34 | match (row text) |
| SWD | IF-051 | SWCLK | PA14 | 37 | match (row text) |
| Reset (one button, DEC-046; since the 2026-11-20 13:01 save on `F1_RESET_B`, to B901 through D301, drawn, not decided, spec OPEN-026) | IF-051 | NRST | NRST | 7 | - |
| HSE CMOS oscillator, 24 MHz | DEC-044 | OSC_IN | PD0 | 5 | - |
| Not used (HSE bypass, DEC-045) | DEC-045 | OSC_OUT | PD1 | 6 | - |
| Boot select | P1-014 | BOOT0 (pull-down) | BOOT0 | 44 | - |
| Boot select | P1-014 | BOOT1: no resistor, not connected (ignored while BOOT0 = 0; spec DEC-095) | PB2 | 20 | DS row: PB2/BOOT1 |

"Default" means the F1 DS lists the signal in the default alternate-function column, so no AFIO remap is needed. The DS column comes from the F103 datasheet. For the F100, every signal in this table is listed on the same pin in ST XML, and all 48 pin names and types match the F103 (F-18); the F100 DS text match is not rerun. The link, PWM, safety and servo-rail pins are the px4io-v2 pins (PX4 v1.16.2 `boards/px4/io-v2/src/board_config.h` and `timer_config.cpp`).

Reserved for px4io-v2 functions (F-13). Not used for anything else. The LEDs are fitted, active low with 220 Ω from `+3V3` (DEC-079, 2026-11-20 13:37 save); the others stay unconnected:

| Pin | px4io-v2 function | Plan |
| --- | ----------------- | ---- |
| PB14 | Blue LED (also heater output) | Fitted (team, Q20): D905, net `LED_IO_BLUE_B`. PC14 and PC15 unconnected, so px4io drives the LED, not the heater (DEC-079) |
| PB15 | Amber LED (`LED_AMBER`) | Fitted (team, Q20) as a red LED in place of amber: D904, net `LED_IO_RED_B` (DEC-079) |
| PA11 | Green LED | Fitted (team, Q20): D906, net `LED_IO_GREEN_B`; off when armed with active-low wiring (DEC-079) |
| PA15 | Servo fault input | Unconnected |
| PA5, PA12 | RSSI | PA5: `+VSERVO2` sense (ADC1_IN5, DEC-110, DEC-113); px4io reads it only with a firmware change (P2-005). PA12: unconnected (the FS-iA6B gives no analog or PWM RSSI on this board), 10 kΩ pull-down R308 (R313 in spec DEC-088) |
| PC13, PA10 | Spektrum (PA10 is also USART1_RX) | Unconnected; R307 10 kΩ pull-up to 3.3 V on PA10 (team, review 0.3; DEC-079) |
| PB10, PB11, PB4 | SBUS | Unconnected; R310 10 kΩ pull-up to 3.3 V on PB11 (R311 before the 2026-11-24 re-annotation) (team, review 0.3; DEC-079) |
| PC14, PC15 | Board sense, read at boot | Unconnected (team, Q6) |

Console (PA9) and NRST: the drawn F100 debug pads have neither (spec OPEN-029). Since the 2026-11-18 16:52 save CN603 carries the console; no NRST, reset by B901 (spec DEC-065, 2026-11-19). 2026-11-20 12:36 save (not committed): CN603 removed; the console (PA9 through R609), SWD, VREF, `RESET_B` and GND go to test pads TP601 to TP606, against DEC-065. TP605 is on `RESET_B` since the 12:56 save and reaches both NRST pins through D201 and D301 (spec OPEN-026, OPEN-039). No pin changed.

Free I/O after this allocation (4 pins): PB3, PB6, PB7, PB12. PB3 is a JTAG pin after reset and needs the SWJ remap (SWD only) before use as GPIO (`ASSUMED`, F1 reference manual not checked).

## 3. Findings

Closed findings stay listed with their outcome.

| ID | Severity | Ref | Label | Finding | Source |
| -- | -------- | --- | ----- | ------- | ------ |
| F-21 | MAJOR | IF-038, PA8 | `VERIFIED` | PA8 is FT, but an FT pin above VDD + 0.3 V needs its internal pull-up off, and px4io turns the PA8 pull-up on (`GPIO_PPM_IN`). A 5 V PPM signal straight onto PA8 would break that rule. DEC-053 adds a 6.2 kΩ series and 10 kΩ to `GND` divider: worst-case margin about 0.23 V to VDD + 0.3 V and 0.25 V above VIH min (`ESTIMATED`, spec DEC-053). FS-iA6B PPM level `NOT_VERIFIED` (OPEN-034). DEC-056 (2026-11-19) replaces the divider with a 74LVC1G17 buffer on `+3V3` (1 kΩ in, 100 kΩ to `GND`, 22 Ω out), so PA8 sees a 3.3 V push-pull level from a 3.3 V or 5 V receiver; the buffer's 5.5 V input tolerance is `NOT_VERIFIED`. Drawn in the 2026-11-19 15:03 save as U303 SN74LVC1G34DCKR, R308 100 kΩ and R309 22 Ω to PA8 (U301 pin 29), with R714 22 Ω at CN706 (`VERIFIED`, CAD); part and resistor differ from DEC-056 (spec OPEN-034 item 6). DEC-057 (2026-11-19) accepts U303 SN74LVC1G34DCKR, R714 22 Ω and D707 SP3031-01ETG as drawn; their datasheet values stay `NOT_VERIFIED`, except the SP3031-01ETG data, checked in spec CMP-012. Since the 2026-11-19 23:17 save the RC IN ESD diode is D708 (same part) and D707 protects GPS1 pin 9 (DEC-071). Since the 16:03 save the 22 Ω at CN706 is R715. | F100 DS16455 Rev 9 Tables 4, 5 and 34 via NotebookLM; PX4 v1.16.2 `boards/px4/io-v2/src/board_config.h` |
| F-22 | MAJOR | H743 PB0 (buzzer), F100 PB5 (safety button) | `VERIFIED` (CAD) | `sch-review` 2026-11-19: PB0 drives GPS1 pin 9 (`GPS1_BUZZER_B`) through 22 Ω with no transistor; if the GPS module puts its buzzer between 5 V and pin 9 (`ASSUMED` at the time; DS-009 rev 0.1.0, read 2026-11-19, gives pin 9 as "BUZZER (driven by a buzzer driver)" at +5-24V, spec REF-10), PB0 exceeds its 20 mA sink limit (DS12110 Table 12 via NotebookLM, `VERIFIED`) and sees about 5 V. PB5 has no board pull resistor; the px4io pin setup is `NOT_VERIFIED`. (spec OPEN-023, was OPEN-037) Update 2026-11-19 13:33 save (drawn, not decided): PB0 now drives the gate of Q701 2SK3018W (R711 10 kΩ gate pull-down), and Q701 drives pin 9, which is `BUZZER-` at 0~5 V on the Holybro Pixhawk 6X GPS 1 table; PB0 no longer sinks the buzzer current or sees 5 V. GPS1 pins 6 and 7 are 3.3 V signals, so PB5 is within its rating. The PB5 pull stays open. Update 2026-11-19 15:20 save (drawn, not decided): R310 10 kΩ from `GPS1_SAFETY_SWITCH` (PB5) to `GND`; the GPS module switch wiring and the px4io PB5 setup stay `NOT_VERIFIED`. Q701 accepted as drawn (spec DEC-057). 2026-11-19: the GPS module safety switch connects to 3.3 V (human owner), so the R310 pull-down fits; the px4io PB5 setup stays `NOT_VERIFIED`. 16:03 save: the Q701 gate pull-down is R714. | Net trace; DS12110 Table 12; Holybro Pixhawk 6X baseboard pinout page |
| F-23 | INFO | H743 PD12, PD13 (I2C4) | `VERIFIED` | `FT_fh`, so 5 V pull-ups from the MS4525DO or PM02D are allowed; the internal pull-ups must be off above 4 V. No board pull-ups are fitted (R705, R706 DNP; spec OPEN-038). 13:57 save: R705 and R706 fitted, 5.1 kΩ to `+3V3`. The MS4525DO and PM02D have no pull-ups (human owner, 2026-11-19); OPEN-038 closed. | DS12110 Table 9 and Table 11 note via NotebookLM |
| F-15 | MAJOR | IF-040 to IF-043 | `NOT_VERIFIED` | Motor stop on an H743 hang: since DEC-050 the ESCs run PWM from the F100, which sets the disarmed value 0.5 s after H743 data stops (DEC-051). Whether the Tekko32 F4 4in1 with AM32 (DEC-054; was the Skywalker 80A V2) stops on that pulse is not checked (spec OPEN-017, SAF-015). | Decisions file S1; spec DEC-051 |
| F-16 | MINOR | IF-030 to IF-043 | `NOT_VERIFIED` | Every PWM line gets a weak pull-down (Q10). Since DEC-050 no line carries DShot. Pick the pull-down and any series resistor for PWM and the boot-time output state (spec OPEN-031, was OPEN-018). Drawn 2026-11-20: 22 Ω series and 100 kΩ to `GND` on all 15 lines; 100 kΩ decided by the human owner (spec DEC-073). | Pinmap review Q10, decisions file S3 |
| F-18 | INFO | IO MCU | `VERIFIED` | STM32F100C(8-B)Tx and STM32F103C(8-B)Tx LQFP48: all 48 pin names and types match, and every signal in section 2 is on the same pin. The F103 adds USB, CAN and ADC2; the F100 adds DAC, CEC and TIM6, TIM7, TIM15 to TIM17. None of these is used. | ST XML, compared by script 2026-10-24 |
| F-17 | INFO | IF-045 | `VERIFIED` | The Pixhawk Debug Mini connector has no NRST pin (1 VREF, 2 Console TX, 3 Console RX, 4 SWDIO, 5 SWCLK, 6 GND). Add an NRST pad next to it. As drawn (2026-11-17 16:40 save): 6-pin with VREF on pin 1, SWDIO on pin 2, SWCLK on pin 3, pins 4 and 5 open, GND on pin 6; no console and no NRST, so SWD sits on the Debug Mini console pins (spec OPEN-029). 2026-11-18 16:52 save: CN602 (H743) and CN603 (F100), JST-SH 6-pin, both in the Debug Mini order; still no NRST (spec 4.2, OPEN-029). Decided 2026-11-19: no NRST pin or pad, reset by B901 (spec DEC-065). | `https://docs.px4.io/main/en/debug/swd_debug.html` (read 2026-10-24); DS-009 rev 0.1.0 Pixhawk Debug Mini table gives the same order (spec REF-10, read 2026-11-19) |
| F-19 | INFO | H743, F100 | `VERIFIED` | Saved 2026-11-17 16:40 schematic (not committed): every H743 and F100 pin with a function label carries the signal this allocation gives it. Net names follow spec DEC-052 (for example `GPS1_UART2_TX`, `AUX1_TIM5_CH1`, `MAIN1_TIM2_CH1`, `BATT_V_INP10`, `SAFETY_SW`). One numbering differs: the schematic names PE9 `SPARE1_TIM1_CH1`, PD14 `SPARE2_TIM4_CH3` and PD15 `SPARE3_TIM4_CH4`, while section 1 has spare output 1 = TIM4_CH3 (IF-017), 2 = TIM4_CH4, 3 = TIM1_CH1. DEC-052 lets the designer set the numbering; this table follows once the connector labels are set (spec OPEN-032). Since the 2026-11-19 12:30 save the safety lines are `GPS1_SAFETY_SWITCH` and `GPS1_SAFETY_LED` (were `SAFETY_SW`, `SAFETY_LED_B`) and the board LED nets `LED_RED_B`, `LED_BLUE_B`, `LED_GREEN_B` (active low, spec 4.2). 2026-11-19 12:49 save: the spare outputs reach `conn-peripherals` through `{SPARE_TIM}`, with no pads yet. 2026-11-19 16:03 save (commit `fe46bcf`): MAIN 1 to 8 (F100 PA0, PA1, PB8, PB9, PA6, PA7, PB0, PB1), AUX 1 to 4 (H743 PA0 to PA3) and I2C4 (H743 PD12, PD13) reach their actuator header and connector pins through `{ESC}`, `{SURFACE}`, `{AUX_TIM5}` and `{EXT_I2C4}` (KiCad 10.0.8 netlist, `VERIFIED`; spec 4.2). Same save, traced later on 2026-11-19: USB FS (PA12, PA11, PA9), H743 SWD and USART3 console (PA13, PA14, PD8, PD9 to CN602 pins 4, 5, 2, 3), F100 SWD (PA13, PA14 to CN603 pins 4, 5), SPI1 and SPI4 with their CS lines (PA4 to PA7, PE11 to PE14 to U401 and U402), the board LEDs (PE2 to PE4) and the spare outputs (PE9, PD14, PD15, no pad yet) reach their ends through the other eight buses (`VERIFIED`; spec 4.2 "Bus links" row). | `sch-inspect` `local-net U201`, `local-net U301`; label audit; KiCad netlist (16:03 save) |
| F-20 | MINOR | H743 PC0, PC1; F100 PA4 | `VERIFIED` | Drawn 2026-11-17 (16:14 save): each pin has a 22 Ω series resistor and 10 nF to `GND`. The H743 PC0 and PC1 parts were removed in the 2026-11-21 17:53 save (spec DEC-107); PC0 and PC1 are unused. The servo rail sense row asks for a 3:1 divider on PA4 (IF-050), which is not drawn; PA4 is not 5 V tolerant (F-03). Values not decided (spec OPEN-033). The 3:1 divider is drawn since the 2026-11-18 16:52 save: R813 46.4 kΩ, R814 23.2 kΩ, C804 100 nF (spec 4.2, OPEN-033; now R825, R826 and C805, spec DEC-097). Accepted as drawn 2026-11-19 (spec DEC-066). | `sch-inspect` `net`; spec 4.2 |
| F-06 | Closed | H743 PA9 | `VERIFIED` | PA9 (OTG_FS_VBUS) is FT_u, and its input maximum is Min(Min(VDD, VDDA, VDD33USB, VBAT) + 4.0, 6 V), so 4 V with VDD at 0 V; above 4 V the internal pull-up or pull-down must be off (Table 11 footnote 4). AN4879 §2.6: "it is mandatory to reduce the voltage on PA9 below 4 V" when the MCU can be unpowered, with a divider (33 kΩ to VBUS, 82 kΩ to GND for VDD 3.0 to 3.6 V). The board drives PA9 from `VBUS` through R603 0 Ω, and VBUS powers `+3V3`, so PA9 sees 5 V before VDD at every USB power-up; PX4 fmu-v6c sets PA9 as an input with pull-down (`board_config.h` line 202). `sch-review` 2026-11-20. Fixed in the 2026-11-20 14:21 save: R603 5k1 from VBUS and R604 10k to GND give PA9 3.12 to 3.50 V (2.81 to 3.28 V with the PX4 pull-down on), `ESTIMATED` (spec DEC-080). | H7 DS12110 Rev 11 Tables 9 and 11, AN4879 §2.6 (NotebookLM); PX4 v1.16.2 fmu-v6c `board_config.h`; `kicad-cli` netlist |
| F-05 | INFO | H743 PC4 | `VERIFIED` | PC4 (IMU1 INT1) is TT_a, so it is 3.3 V tolerant only, not 5 V. This is fine for a 3.3 V IMU. | H7 DS Table 9 |
| F-03 | INFO | F100 PA0 to PA7, PB0, PB1, PB5 | `VERIFIED` | These pins are not 5 V tolerant (no FT in the type column). They carry the ESC and servo outputs, the 3.3 V px4io link, the servo rail sense and the safety button (PA5 is the `+VSERVO2` sense, DEC-113). Keep 5 V off them: the servo rail sense goes through its divider, and the safety button switches to 3.3 V or GND. | F100 DS Table 4 (was F1 DS Table 5 for the F103) |
| F-13 | INFO | F100 reserved pins | `VERIFIED` | Stock px4io-v2 also drives or reads PB14, PB15, PA11 (LEDs), PA15 (servo fault), PA5 and PA12 (RSSI), PC13 and PA10 (Spektrum), PB10, PB11, PB4 (SBUS), PA8 (PPM), PC14 and PC15 (board sense). Applied in section 2. Since DEC-053 PA8 carries RC IN (PPM), its px4io function. | PX4 v1.16.2 `boards/px4/io-v2/src/board_config.h` |
| F-14 | INFO | H743 microSD | `VERIFIED` | `px4/fmu-v6c` puts microSD on SDMMC2, which clashes with GPS1 RX (PD6) and Telemetry 2 (PB14, PB15) here. SDMMC1 on PC8 to PC12 and PD2 is used instead; all six signals are listed in ST XML (checked 2026-10-24). | PX4 v1.16.2 `boards/px4/fmu-v6c/nuttx-config/include/board.h`; ST XML |
| F-02 | Closed | IF-034 to IF-037 | `VERIFIED` | Spec labels TIM3_CH5 to CH8 did not exist; corrected to TIM3_CH1 to CH4 (team, Q3). | ST XML; F1 DS Table 5 (F103) |
| F-11 | Closed | IO MCU HSE | `VERIFIED` | Stock px4io-v2 uses a 24 MHz HSE, outside the STM32F103 crystal range of 4 to 16 MHz (F1 DS Table 22). Resolved by the STM32F100C8T6B, HSE 4 to 24 MHz (F100 DS Table 21; DEC-002, DEC-017). Superseded by DEC-044 and DEC-045: CMOS oscillator and a custom px4io build. | F1 DS Tables 20 and 22; F100 DS Table 21 (NotebookLM source fulltext); PX4 v1.16.2 `boards/px4/io-v2/nuttx-config/include/board.h` |
| F-12 | Closed | H743 TIM5 | `ASSUMED` | `px4/fmu-v6c` gives DMA only to TIM1 and TIM4. The team will declare TIM5 with DMA in the port (decisions file S2); not checked by hardware. | PX4 v1.16.2 `boards/px4/fmu-v6c/src/timer_config.cpp` |
| F-01 | Closed | IF-016 | `VERIFIED` | IF-016 used the same UART7 as Telemetry 1. Dropped (team, Q4). | Spec section 3 |
| F-04 | Closed | IF-038 | `VERIFIED` | FlySky protocol was undefined. Dropped; RC came over ELRS on UART7 (team, Q5). Reversed 2026-11-19 by DEC-053: FS-iA6B in PPM mode on PA8 (F-21). | Spec IF-038, DEC-053 |
| F-07 | Closed | IF-024 | `VERIFIED` | No F100 reflash path from the H743. PX4 updates the F100 over the link; the first flash is over SWD (team, Q9). | Pinmap review Q9 |
| F-08 | Closed | H743 PA10 | `VERIFIED` | USB is device only, so PA10 (OTG_FS_ID) is free (team, Q19). | Section 1 |
| F-09 | Closed | Power module | `ASSUMED` | Power module on I2C4 with the MS4525DO. Team: INA228 at 0x45 (older units INA226 at 0x41). The module label is not checked. | Pinmap review Q14 |
| F-10 | Closed | H743 TIM15 | - | TIM15 dropped; motors moved to TIM5 (team, Q17). | Pinmap review Q17 |

## 4. Open checks

- [x] Human reviews the pin choices and the design choices in sections 1 and 2. Done 2026-11-21 (section 6).
- [ ] DMA streams and interrupt priorities (firmware, P2-005) and timer clock per peripheral (P1-001). TIM5 DMA and the SDMMC1 setup are in the software port (decisions file S2, S4).
- [ ] P2-018: pull-down value on the PWM lines (F-16; no DShot since DEC-050).
- [x] OPEN-028: oscillator data meets the HSE bypass limits of both MCUs and the LCSC codes match the part numbers (spec CMP-010, 2026-11-19); the two INFO margins on U302 were accepted 2026-11-20 (spec DEC-089).
- [x] Pick the weak pull-up value on F100 PA10 and PB11, and the resistors for the px4io LEDs on PB14, PB15 and PA11. Done 2026-11-20: 10 kΩ and 220 Ω (spec DEC-079).
- [ ] Run the datasheet text match on the rows marked `not checked`, and on the section 2 rows against the F100 DS. Carried to P3-009 (before release).
- [ ] Human confirms critical pins (power, SWD, USB, BOOT0, oscillator inputs) against the datasheet pinout figures. Carried to P3-009 (before release).

## 5. Sources

- ST open pin data: https://github.com/STMicroelectronics/STM32_open_pin_data (commit `7d1f151`)
- STM32H743VI datasheet (NotebookLM source): https://www.st.com/resource/en/datasheet/stm32h743vi.pdf
- STM32F103C8 datasheet (NotebookLM source, earlier checks): https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
- STM32F100 datasheet DocID16455 Rev 9 (NotebookLM notebook `STM32F100`)
- Requirements: `AO-HORIZON_SPEC_EN.md` sections 3.4, 3.5 and 8.1
- PX4 Matek H743-Slim board port and NuttX pinmap (reference copies): `documents/reference/px4-matek-h743-slim/`
- ICM-45686 DS-000489 Rev 1.1 and IST8310 Datasheet V1.2 (NotebookLM sources)
- Team answers: `AO-HORIZON_PINMAP_REVIEW_EN.md` rev 0.3 with the team's 0.2 and 0.3 answers and `AO-HORIZON_PINMAP_DECISIONS_EN.md` rev 0.2 (2026-10-24)
- PX4-Autopilot v1.16.2 board files: https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/ (`io-v2`, `fmu-v6c`)
- PX4 docs, SWD debug port: https://docs.px4.io/main/en/debug/swd_debug.html
- Holybro Pixhawk 6X baseboard pinout (signal levels of the GPS 1, TELEM and I2C ports), read 2026-11-19: https://docs.holybro.com/autopilot/pixhawk-6x/pixhawk-baseboard-pinout

## 6. Review record

| Item | Record |
| ---- |---|
| Reviewer | Human owner (sign-off in chat: "Sign off now") |
| Date | 2026-11-21 |
| Scope | Sections 1 and 2 (H743 and F100 pins, alternate functions, timers, reserved and unused pins) at rev 0.29, and the schematic labels on the MCU pins (F-19; ERC 2026-11-21 10:50, 0 errors, 0 warnings) |
| Conflicts resolved | F-01 to F-12 closed earlier (section 3). F-16 PWM pull-downs: 100 kΩ, spec DEC-073. F-20 servo rail sense divider: spec DEC-066. F-21 PA8 PPM level: U303 buffer, spec DEC-057. F-22 PB0 buzzer and PB5 safety switch: Q701 and R309 (was R310), spec DEC-057. Boot pins: spec DEC-095. |
| Carried | F-15 motor stop on an H743 hang: bench test P4-011 (spec OPEN-017). DMA streams and interrupt priorities: firmware, P2-005. Datasheet text match on rows marked `not checked` and the critical-pin check against the datasheet figures: P3-009. |
| Result | `ALLOCATED`. Not `VERIFIED`: no bench or firmware evidence yet. |
