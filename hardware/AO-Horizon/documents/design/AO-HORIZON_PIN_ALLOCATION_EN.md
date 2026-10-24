# AeroOptix-Horizon: MCU Pin Allocation

**Revision:** 0.6
**Updated:** 2026-10-24
**Status:** Draft. The software team's answers (pinmap review 0.2 and 0.3, decisions file) are applied. The IO MCU is now the STM32F100C8T6B (DEC-002); no pin moved. Not drawn in the schematic yet. DMA, interrupt priority and timer clock checks (P1-010) are not done by hardware. Not a verification record.
**Requirement refs:** IF-010 to IF-024, IF-030 to IF-037, IF-040 to IF-051, SEN-001 to SEN-003, DEC-002, DEC-014 to DEC-018 (spec rev 0.12). Checklist tasks: P1-001, P1-002, P1-003 to P1-005 (partial), P1-009 (partial).
**Decision owner:** Hardware

Single record for the STM32H743VIT6 (LQFP100) and STM32F100C8T6B (LQFP48) pin allocation.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`.

Source keys used below:
- **ST XML**: ST `STM32_open_pin_data` repo, files `mcu/STM32H743VITx.xml` and `mcu/STM32F103C(8-B)Tx.xml`, commit `7d1f151` (2026-06-29), fetched 2026-10-18 and again 2026-10-24, and `mcu/STM32F100C(8-B)Tx.xml` (`master`, fetched 2026-10-24). Lists the signals that each package pin can carry.
- **H7 DS**: ST DS12110 Rev 11 (STM32H742xI/G, STM32H743xI/G), Table 9 pin/ball definition, read as NotebookLM source fulltext (notebook `STM32H743VI`).
- **F1 DS**: ST DS5319 Rev 20 (STM32F103x8/B), Table 5 pin definitions, read as NotebookLM source fulltext (notebook `STM32F103C8T`). Used for the section 2 checks before the IO MCU changed.
- **F100 DS**: ST DocID16455 Rev 9 (STM32F100x4/6/8/B), Table 4 pin definitions and Tables 8, 10, 21, read as NotebookLM source fulltext (notebook `STM32F100`), 2026-10-24.

How each row was checked:
- **Pin/signal**: a script confirmed the signal is listed for that pin in ST XML, so it is `VERIFIED`. Rows added on 2026-10-24 were checked the same way.
- **DS**: a script found the signal name in that pin's row of the datasheet text. This is a text match on extracted PDF text, so a human should still confirm the critical pins against the datasheet. `not checked` means the row was added after the datasheet pass.
- **Conflicts**: no pin is assigned twice, and the interrupt pins use different EXTI lines (checked by script, 2026-10-24).
- **Source**: the H743 pins mostly follow Pixhawk 6C (`px4/fmu-v6c`) and the F100 pins follow `px4/io-v2`, by team decision (DEC-014). The team tested them on a NUCLEO-H753ZI and in PX4 SITL only (pinmap review Q2). Some pins were proposed by hardware and accepted by the team (pinmap review section 3.6, decisions file H2).

Script inputs and outputs are not kept in the repo.

## 1. STM32H743VIT6 (LQFP100)

| Function | Ref | Signal | Pin | LQFP100 | DS |
| -------- | --- | ------ | --- | ------- | -- |
| Telemetry 1 (ELRS, RC) | IF-010 | UART7_TX | PE8 | 38 | match |
| Telemetry 1 (ELRS, RC) | IF-010 | UART7_RX | PE7 | 37 | match |
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
| Motor 1 (front-R) | IF-040 | TIM5_CH1 (AF2) | PA0 | 22 | not checked |
| Motor 2 (rear-L) | IF-041 | TIM5_CH2 (AF2) | PA1 | 23 | not checked |
| Motor 3 (front-L) | IF-042 | TIM5_CH3 (AF2) | PA2 | 24 | not checked |
| Motor 4 (rear-R) | IF-043 | TIM5_CH4 (AF2) | PA3 | 25 | not checked |
| Spare output 1 | IF-017 | TIM4_CH3 | PD14 | 61 | match |
| Spare output 2 | IF-018 | TIM4_CH4 | PD15 | 62 | match |
| Spare output 3 | IF-019 | TIM1_CH1 | PE9 | 39 | match |
| USB FS | IF-022 | OTG_FS_DM | PA11 | 70 | match |
| USB FS | IF-022 | OTG_FS_DP | PA12 | 71 | match |
| USB VBUS sense | IF-022 | OTG_FS_VBUS | PA9 | 68 | match |
| SWD | IF-045 | SWDIO | PA13 | 72 | not checked |
| SWD | IF-045 | SWCLK | PA14 | 76 | not checked |
| Reset | TST-001 | NRST | NRST | 14 | - |
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
| Analog battery V (reserve) | IF-048 | ADC123_INP10 | PC0 | 15 | - |
| Analog battery I (reserve) | IF-048 | ADC123_INP11 | PC1 | 16 | - |
| HSE crystal, 16 MHz | DEC-017 | OSC_IN | PH0 | 12 | - |
| HSE crystal, 16 MHz | DEC-017 | OSC_OUT | PH1 | 13 | - |
| Boot select | P1-007 | BOOT0 | BOOT0 | 94 | - |

AF numbers (`VERIFIED`): the NuttX pinmap gives AF2 for TIM5_CH1 to CH4 on PA0 to PA3 and for TIM3_CH3 on PB0 (`documents/reference/px4-matek-h743-slim/stm32h7x3xx_pinmap.h`). HRT runs on TIM8, which needs no pin (team, Q15). IMU pin 9 (INT2/FSYNC/CLKIN) is not connected to the MCU; it is handled as the ICM-45686 datasheet says for an unused pin (team, Q16).

Design choices behind the table (`ASSUMED`, for review):
- Each IMU has its own SPI bus (SPI1, SPI4), so a fault on one bus does not take out both IMUs.
- Both barometers and the magnetometer share I2C2 (I2C3 dropped by the team to free PC9 for microSD). Addresses: ICP-20100 0x63, BMP581 0x46, IST8310 0x0E. They do not overlap. One bus fault can now take out both barometers.
- USART6 for the F100 link, same as `px4/fmu-v6c`.
- Motors on TIM5, one timer with DMA, so all four can run bidirectional DShot from timer 0 (team, S3).
- microSD on SDMMC1, because the `px4/fmu-v6c` SDMMC2 pins clash with GPS1 RX and Telemetry 2 (F-14).
- Buzzer on TIM3_CH3, PB0, same as `px4/fmu-v6c` (decisions file H2).
- TIM4 on PD14/PD15 rather than PB8/PB9, which leaves PB8/PB9 for I2C1.
- USB device only: PA10 (OTG_FS_ID) is not used (team, Q19).
- PA15, PB3 and PB4 (JTAG-only pins) are left free, since only SWD is used.

Free I/O after this allocation (25 pins): PA8, PA10, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC2_C, PC3_C, PC5, PC13, PC14, PC15, PD0, PD1, PD3, PD4, PD7, PD10, PD11, PE5, PE6, PE10. PA15, PB3 and PB4 are also free but not counted. PC14 and PC15 are free because no LSE is used (team, Q6).

## 2. STM32F100C8T6B (LQFP48)

| Function | Ref | Signal | Pin | LQFP48 | DS (default / remap) |
| -------- | --- | ------ | --- | ------ | -------------------- |
| Flaperon L | IF-030 | TIM2_CH1 | PA0 | 10 | match, default (TIM2_CH1_ETR) |
| Flaperon R | IF-031 | TIM2_CH2 | PA1 | 11 | match, default |
| Ruddervator L | IF-032 | TIM4_CH3 | PB8 | 45 | match, default |
| Ruddervator R | IF-033 | TIM4_CH4 | PB9 | 46 | match, default |
| Tilt servo 1 (front-R) | IF-034 | TIM3_CH1 | PA6 | 16 | match, default |
| Tilt servo 2 (rear-L) | IF-035 | TIM3_CH2 | PA7 | 17 | match, default |
| Tilt servo 3 (front-L) | IF-036 | TIM3_CH3 | PB0 | 18 | match, default |
| Tilt servo 4 (rear-R) | IF-037 | TIM3_CH4 | PB1 | 19 | match, default |
| H743 link | IF-024 | USART2_TX | PA2 | 12 | match, default |
| H743 link | IF-024 | USART2_RX | PA3 | 13 | match, default |
| px4io console | IF-051 | USART1_TX | PA9 | 30 | match, default |
| Safety button | IF-049 | GPIO input | PB5 | 41 | - |
| Safety LED | IF-049 | GPIO output, open drain, active low | PB13 | 26 | - |
| Servo rail sense | IF-050 | ADC1_IN4 (3:1 divider) | PA4 | 14 | not checked |
| SWD | IF-051 | SWDIO | PA13 | 34 | match (row text) |
| SWD | IF-051 | SWCLK | PA14 | 37 | match (row text) |
| Reset | IF-051 | NRST | NRST | 7 | - |
| HSE crystal, 24 MHz | DEC-017 | OSC_IN | PD0 | 5 | - |
| HSE crystal, 24 MHz | DEC-017 | OSC_OUT | PD1 | 6 | - |
| Boot select | P1-014 | BOOT0 (pull-down) | BOOT0 | 44 | - |
| Boot select | P1-014 | BOOT1 (pull-down) | PB2 | 20 | DS row: PB2/BOOT1 |

"Default" means the F1 DS lists the signal in the default alternate-function column, so no AFIO remap is needed. The DS column comes from the F103 datasheet. For the F100, every signal in this table is listed on the same pin in ST XML, and all 48 pin names and types match the F103 (F-18); the F100 DS text match is not rerun. The link, PWM, safety and servo-rail pins are the px4io-v2 pins (PX4 v1.16.2 `boards/px4/io-v2/src/board_config.h` and `timer_config.cpp`).

Reserved for px4io-v2 functions (F-13). Not used for anything else. The LEDs are fitted; the others stay unconnected:

| Pin | px4io-v2 function | Plan |
| --- | ----------------- | ---- |
| PB14 | Blue LED (also heater output) | Fitted (team, Q20) |
| PB15 | Amber LED | Fitted (team, Q20) |
| PA11 | Green LED | Fitted (team, Q20) |
| PA15 | Servo fault input | Unconnected |
| PA5, PA12 | RSSI | Unconnected (no RC on the F100) |
| PC13, PA10 | Spektrum (PA10 is also USART1_RX) | Unconnected; weak pull-up to 3.3 V on PA10 (team, review 0.3) |
| PB10, PB11, PB4 | SBUS | Unconnected; weak pull-up to 3.3 V on PB11 (team, review 0.3) |
| PA8 | PPM | Unconnected |
| PC14, PC15 | Board sense, read at boot | Unconnected (team, Q6) |

Free I/O after this allocation (4 pins): PB3, PB6, PB7, PB12. PB3 is a JTAG pin after reset and needs the SWJ remap (SWD only) before use as GPIO (`ASSUMED`, F1 reference manual not checked).

## 3. Findings

Closed findings stay listed with their outcome.

| ID | Severity | Ref | Label | Finding | Source |
| -- | -------- | --- | ----- | ------- | ------ |
| F-15 | MAJOR | IF-040 to IF-043 | `NOT_VERIFIED` | Motor stop on an H743 hang relies on the ESC stopping when DShot frames stop. ESC signal-loss behavior is not checked (spec OPEN-017, SAF-015). | Decisions file S1 |
| F-16 | MINOR | IF-040 to IF-043 | `NOT_VERIFIED` | Every PWM line gets a weak pull-down (Q10). The motor lines carry bidirectional DShot, which idles high and turns the line around for the ESC reply. Pick the pull-down and any series resistor so they do not upset that (spec OPEN-018). | Pinmap review Q10, decisions file S3 |
| F-18 | INFO | IO MCU | `VERIFIED` | STM32F100C(8-B)Tx and STM32F103C(8-B)Tx LQFP48: all 48 pin names and types match, and every signal in section 2 is on the same pin. The F103 adds USB, CAN and ADC2; the F100 adds DAC, CEC and TIM6, TIM7, TIM15 to TIM17. None of these is used. | ST XML, compared by script 2026-10-24 |
| F-17 | INFO | IF-045 | `VERIFIED` | The Pixhawk Debug Mini connector has no NRST pin (1 VREF, 2 Console TX, 3 Console RX, 4 SWDIO, 5 SWCLK, 6 GND). Add an NRST pad next to it. | `https://docs.px4.io/main/en/debug/swd_debug.html` (read 2026-10-24; DS-009 not read) |
| F-06 | INFO | H743 PA9 | `NOT_VERIFIED` | PA9 (OTG_FS_VBUS) is FT_u. Whether VBUS can connect directly, or needs a divider when VDD is off, is not checked. | H7 DS Table 9 |
| F-05 | INFO | H743 PC4 | `VERIFIED` | PC4 (IMU1 INT1) is TT_a, so it is 3.3 V tolerant only, not 5 V. This is fine for a 3.3 V IMU. | H7 DS Table 9 |
| F-03 | INFO | F100 PA0 to PA7, PB0, PB1, PB5 | `VERIFIED` | These pins are not 5 V tolerant (no FT in the type column). They carry the servo outputs, the 3.3 V px4io link, the servo rail sense and the safety button (PA5 is unconnected). Keep 5 V off them: the servo rail sense goes through its divider, and the safety button switches to 3.3 V or GND. | F100 DS Table 4 (was F1 DS Table 5 for the F103) |
| F-13 | INFO | F100 reserved pins | `VERIFIED` | Stock px4io-v2 also drives or reads PB14, PB15, PA11 (LEDs), PA15 (servo fault), PA5 and PA12 (RSSI), PC13 and PA10 (Spektrum), PB10, PB11, PB4 (SBUS), PA8 (PPM), PC14 and PC15 (board sense). Applied in section 2. | PX4 v1.16.2 `boards/px4/io-v2/src/board_config.h` |
| F-14 | INFO | H743 microSD | `VERIFIED` | `px4/fmu-v6c` puts microSD on SDMMC2, which clashes with GPS1 RX (PD6) and Telemetry 2 (PB14, PB15) here. SDMMC1 on PC8 to PC12 and PD2 is used instead; all six signals are listed in ST XML (checked 2026-10-24). | PX4 v1.16.2 `boards/px4/fmu-v6c/nuttx-config/include/board.h`; ST XML |
| F-02 | Closed | IF-034 to IF-037 | `VERIFIED` | Spec labels TIM3_CH5 to CH8 did not exist. Corrected to TIM3_CH1 to CH4 in spec rev 0.11 (team, Q3). | ST XML; F1 DS Table 5 (F103) |
| F-11 | Closed | IO MCU HSE | `VERIFIED` | Stock px4io-v2 uses a 24 MHz HSE, outside the STM32F103 crystal range of 4 to 16 MHz (F1 DS Table 22). Resolved by the STM32F100C8T6B, whose HSE takes 4 to 24 MHz (F100 DS Table 21), with a 24 MHz crystal and stock px4io (DEC-002, DEC-017). | F1 DS Tables 20 and 22; F100 DS Table 21 (NotebookLM source fulltext); PX4 v1.16.2 `boards/px4/io-v2/nuttx-config/include/board.h` |
| F-12 | Closed | H743 TIM5 | `ASSUMED` | `px4/fmu-v6c` gives DMA only to TIM1 and TIM4. The team will declare TIM5 with DMA in the port (decisions file S2); not checked by hardware. | PX4 v1.16.2 `boards/px4/fmu-v6c/src/timer_config.cpp` |
| F-01 | Closed | IF-016 | `VERIFIED` | IF-016 used the same UART7 as Telemetry 1. Dropped (team, Q4). | Spec section 3 |
| F-04 | Closed | IF-038 | `VERIFIED` | FlySky protocol was undefined. Dropped; RC comes over ELRS on UART7 (team, Q5). | Spec IF-038 |
| F-07 | Closed | IF-024 | `VERIFIED` | No F100 reflash path from the H743. PX4 updates the F100 over the link; the first flash is over SWD (team, Q9). | Pinmap review Q9 |
| F-08 | Closed | H743 PA10 | `VERIFIED` | The note about OTG_FS_ID is reworded: USB is device only and PA10 is free (team, Q19). | Section 1 |
| F-09 | Closed | Power module | `ASSUMED` | Power module on I2C4 with the MS4525DO. Team: INA228 at 0x45 (older units INA226 at 0x41). The module label is not checked. | Pinmap review Q14 |
| F-10 | Closed | H743 TIM15 | - | TIM15 dropped; motors moved to TIM5 (team, Q17). | Pinmap review Q17 |

## 4. Open checks

- [ ] Human reviews the pin choices and the design choices in sections 1 and 2.
- [ ] P1-010: DMA streams, interrupt priorities and timer clock per peripheral. TIM5 DMA and the SDMMC1 setup are in the software port (decisions file S2, S4).
- [ ] P1-011: pull-down value on the PWM lines, with bidirectional DShot on the motor lines (F-16).
- [ ] P1-014: crystal parts and load capacitors for 16 MHz (H743) and 24 MHz (F100).
- [ ] Pick the weak pull-up value on F100 PA10 and PB11, and the resistors for the px4io LEDs on PB14, PB15 and PA11.
- [ ] Run the datasheet text match on the rows marked `not checked`, and on the section 2 rows against the F100 DS.
- [ ] Human confirms critical pins (power, SWD, USB, BOOT0, crystals) against the datasheet pinout figures.

## 5. Sources

- ST open pin data: https://github.com/STMicroelectronics/STM32_open_pin_data (commit `7d1f151`)
- STM32H743VI datasheet (NotebookLM source): https://www.st.com/resource/en/datasheet/stm32h743vi.pdf
- STM32F103C8 datasheet (NotebookLM source, earlier checks): https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
- STM32F100 datasheet DocID16455 Rev 9 (NotebookLM notebook `STM32F100`)
- Requirements: `AO-HORIZON_SPEC_EN.md` rev 0.12, sections 3.4 and 3.5
- PX4 Matek H743-Slim board port and NuttX pinmap (reference copies): `documents/reference/px4-matek-h743-slim/`
- ICM-45686 DS-000489 Rev 1.1 and IST8310 Datasheet V1.2 (NotebookLM sources)
- Team answers: `AO-HORIZON_PINMAP_REVIEW_EN.md` rev 0.3 with the team's 0.2 and 0.3 answers and `AO-HORIZON_PINMAP_DECISIONS_EN.md` rev 0.2 (2026-10-24)
- PX4-Autopilot v1.16.2 board files: https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/ (`io-v2`, `fmu-v6c`)
- PX4 docs, SWD debug port: https://docs.px4.io/main/en/debug/swd_debug.html
