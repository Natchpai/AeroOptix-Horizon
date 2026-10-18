# AeroOptix-Horizon: MCU Pin Allocation

**Revision:** 0.1
**Updated:** 2026-10-18
**Status:** Draft proposal. Pin choices are not approved. DMA, interrupt priority and clock checks (P1-010) are not done. Not a verification record.
**Requirement refs:** IF-010 to IF-024, IF-030 to IF-038, SEN-001 to SEN-003 (spec). Checklist tasks: P1-001, P1-002, P1-003 to P1-005 (partial), P1-009 (partial).
**Decision owner:** Hardware

Single record for the STM32H743VIT6 (LQFP100) and STM32F103C8T6 (LQFP48) pin allocation.

Evidence labels follow `.claude/rules/engineering.md`: `VERIFIED`, `ASSUMED`, `ESTIMATED`, `NOT_VERIFIED`.

Source keys used below:
- **ST XML**: ST `STM32_open_pin_data` repo, files `mcu/STM32H743VITx.xml` and `mcu/STM32F103C(8-B)Tx.xml`, latest commit `7d1f151` (2026-06-29), fetched 2026-10-18. Lists the signals that each package pin can carry.
- **H7 DS**: ST DS12110 Rev 11 (STM32H742xI/G, STM32H743xI/G), Table 9 pin/ball definition, read as NotebookLM source fulltext (notebook `STM32H743VI`).
- **F1 DS**: ST DS5319 Rev 20 (STM32F103x8/B), Table 5 pin definitions, read as NotebookLM source fulltext (notebook `STM32F103C8T`).

How each row was checked:
- **Pin/signal**: a script confirmed the signal is listed for that pin in ST XML, so it is `VERIFIED`.
- **DS**: a script found the signal name in that pin's row of the datasheet text. This is a text match on extracted PDF text, so a human should still confirm the critical pins against the datasheet.
- **Conflicts**: a script confirmed that no pin is assigned twice and that the interrupt pins use different EXTI lines.
- **Choice**: which pin and instance to use is a proposal (`ASSUMED`) for the human to accept or change.

Script inputs and outputs are not kept in the repo.

## 1. STM32H743VIT6 (LQFP100)

| Function | Ref | Signal | Pin | LQFP100 | DS |
| -------- | --- | ------ | --- | ------- | -- |
| Telemetry 1 | IF-010 | UART7_TX | PE8 | 38 | match |
| Telemetry 1 | IF-010 | UART7_RX | PE7 | 37 | match |
| Telemetry 2 | IF-011 | USART1_TX | PB14 | 53 | match |
| Telemetry 2 | IF-011 | USART1_RX | PB15 | 54 | match |
| GPS1 | IF-012 | USART2_TX | PD5 | 86 | match |
| GPS1 | IF-012 | USART2_RX | PD6 | 87 | match |
| GPS1 compass | IF-012 | I2C1_SCL | PB8 | 95 | match |
| GPS1 compass | IF-012 | I2C1_SDA | PB9 | 96 | match |
| GPS2 (reserved) | IF-013 | USART3_TX | PD8 | 55 | match |
| GPS2 (reserved) | IF-013 | USART3_RX | PD9 | 56 | match |
| MS4525DO | IF-014 | I2C4_SCL | PD12 | 59 | match |
| MS4525DO | IF-014 | I2C4_SDA | PD13 | 60 | match |
| TF-Luna | IF-015 | UART8_TX | PE1 | 98 | match |
| TF-Luna | IF-015 | UART8_RX | PE0 | 97 | match |
| UART7 TX (reserved) | IF-016 | see finding F-01 | - | - | - |
| VT L | IF-017 | TIM4_CH3 | PD14 | 61 | match |
| VT R | IF-018 | TIM4_CH4 | PD15 | 62 | match |
| SP2 (reserved) | IF-019 | TIM1_CH1 | PE9 | 39 | match |
| TL2 | IF-020 | TIM15_CH1 | PA2 | 24 | match |
| TR2 | IF-021 | TIM15_CH2 | PA3 | 25 | match |
| USB FS | IF-022 | OTG_FS_DM | PA11 | 70 | match |
| USB FS | IF-022 | OTG_FS_DP | PA12 | 71 | match |
| USB VBUS sense | IF-022 | OTG_FS_VBUS | PA9 | 68 | match |
| SWD | IF-023 | SWDIO | PA13 | 72 | not checked |
| SWD | IF-023 | SWCLK | PA14 | 76 | not checked |
| SWD | IF-023 | NRST | NRST | 14 | - |
| F103 link | IF-024 | USART6_TX | PC6 | 63 | match |
| F103 link | IF-024 | USART6_RX | PC7 | 64 | match |
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
| ICP-20100 + BMM150 | SEN-002, SEN-003 | I2C2_SCL | PB10 | 46 | match |
| ICP-20100 + BMM150 | SEN-002, SEN-003 | I2C2_SDA | PB11 | 47 | match |
| BMP390 | SEN-002 | I2C3_SCL | PA8 | 67 | match |
| BMP390 | SEN-002 | I2C3_SDA | PC9 | 66 | match |
| HSE crystal | P1-014 | OSC_IN | PH0 | 12 | - |
| HSE crystal | P1-014 | OSC_OUT | PH1 | 13 | - |
| Boot select | P1-007 | BOOT0 | BOOT0 | 94 | - |

Design choices behind the table (`ASSUMED`, for review):
- Each IMU has its own SPI bus (SPI1, SPI4), so a fault on one bus does not take out both IMUs.
- The two barometers are on separate I2C buses (I2C2, I2C3) for the same reason. The BMM150 shares I2C2 with the ICP-20100.
- USART6 for the F103 link, because its only LQFP100 pins (PC6, PC7) are not needed elsewhere.
- TIM15 on PA2/PA3 rather than PE5/PE6, which keeps PE5/PE6 free as SPI4 alternates. USART2 then uses PD5/PD6.
- TIM4 on PD14/PD15 rather than PB8/PB9, which leaves PB8/PB9 for I2C1.
- USART1 on PB14/PB15, because PA9/PA10 are used for USB VBUS sensing and OTG_FS_ID.
- PA15, PB3 and PB4 (JTAG-only pins) are left free, since only SWD is used.

Free I/O after this allocation (37 pins): PA0, PA1, PA10, PB0, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC0, PC1, PC2_C, PC3_C, PC5, PC8, PC10 to PC15, PD0 to PD4, PD7, PD10, PD11, PE2 to PE6, PE10. PA15, PB3 and PB4 are also free but not counted. Not yet allocated: LEDs, buzzer, safety switch, BMM150 DRDY, ADC inputs for voltage sensing, IMU INT2 and CLKIN.

## 2. STM32F103C8T6 (LQFP48)

| Function | Ref | Signal | Pin | LQFP48 | DS (default / remap) |
| -------- | --- | ------ | --- | ------ | -------------------- |
| TILT L | IF-030 | TIM2_CH1 | PA0 | 10 | match, default (TIM2_CH1_ETR) |
| TILT R | IF-031 | TIM2_CH2 | PA1 | 11 | match, default |
| ESC L | IF-032 | TIM4_CH3 | PB8 | 45 | match, default |
| ESC R | IF-033 | TIM4_CH4 | PB9 | 46 | match, default |
| COAX T | IF-034 | TIM3_CH1 (spec says TIM3_CH5, see F-02) | PA6 | 16 | match, default |
| COAX B | IF-035 | TIM3_CH2 (spec says TIM3_CH6) | PA7 | 17 | match, default |
| AIL L | IF-036 | TIM3_CH3 (spec says TIM3_CH7) | PB0 | 18 | match, default |
| AIL R | IF-037 | TIM3_CH4 (spec says TIM3_CH8) | PB1 | 19 | match, default |
| FlySky (candidate) | IF-038 | USART2_RX | PA3 | 13 | match, default |
| FlySky (candidate) | IF-038 | USART2_TX | PA2 | 12 | match, default |
| H743 link | IF-024 | USART1_TX | PA9 | 30 | match, default |
| H743 link | IF-024 | USART1_RX | PA10 | 31 | match, default |
| SWD | IF-023 | SWDIO | PA13 | 34 | match (row text) |
| SWD | IF-023 | SWCLK | PA14 | 37 | match (row text) |
| SWD | IF-023 | NRST | NRST | 7 | - |
| HSE crystal | P1-014 | OSC_IN | PD0 | 5 | - |
| HSE crystal | P1-014 | OSC_OUT | PD1 | 6 | - |
| Boot select | P1-014 | BOOT0 | BOOT0 | 44 | - |
| Boot select | P1-014 | BOOT1 | PB2 | 20 | DS row: PB2/BOOT1 |

"Default" means the F1 DS lists the signal in the default alternate-function column, so no AFIO remap is needed.

Design choices behind the table (`ASSUMED`, for review):
- All timer outputs use default mapping, so no AFIO remap is needed.
- USART1 (PA9/PA10) for the H743 link. This may also let the H743 reflash the F103 through the F103 system bootloader. Which bootloader USART pins the F103 uses is `NOT_VERIFIED` (ST AN2606 is not in the notebooks).
- USART2 is held for the FlySky receiver until its protocol is known (see F-04).

Free I/O after this allocation (20 pins): PA4, PA5, PA8, PA11, PA12, PA15, PB3 to PB7, PB10 to PB15, PC13 to PC15. PB2 is BOOT1 and is not counted as free. PA15, PB3 and PB4 are JTAG pins after reset and need the SWJ remap (SWD only) in firmware before use as GPIO (`ASSUMED`, F1 reference manual not checked).

## 3. Findings

| ID | Severity | Ref | Label | Finding | Source |
| -- | -------- | --- | ----- | ------- | ------ |
| F-02 | MAJOR | IF-034 to IF-037 | `VERIFIED` | Spec labels TIM3_CH5 to TIM3_CH8 do not exist. F103 TIM3 has CH1 to CH4 only. Proposed: TIM3_CH1 to CH4 on PA6, PA7, PB0, PB1. The spec needs correcting. | ST XML; F1 DS Table 5 |
| F-01 | MINOR | IF-016 | `VERIFIED` | IF-016 "UART7 TX (reserved)" uses the same UART7 as Telemetry 1 (IF-010). One UART7 TX pin cannot serve both. The intent of IF-016 needs clarifying (drop it, or move it to another UART such as UART4 or UART5). | Spec section 3 |
| F-03 | MINOR | F103 PA0 to PA3 | `VERIFIED` | PA0 to PA3 are not 5 V tolerant (no FT in the type column). A 5 V receiver signal on PA3 (FlySky) or 5 V servo feedback needs a level check. The TIM2 outputs on PA0/PA1 are outputs only. | F1 DS Table 5 |
| F-04 | MINOR | IF-038 | `ASSUMED` | FlySky receiver protocol (PPM, PWM, i-BUS or S.BUS) is not defined. USART2 is held as a candidate. PPM would need a timer input instead, and S.BUS would need an inverter. | Spec IF-038 |
| F-05 | INFO | H743 PC4 | `VERIFIED` | PC4 (IMU1 INT1) is TT_a, so it is 3.3 V tolerant only, not 5 V. This is fine for a 3.3 V IMU. | H7 DS Table 9 |
| F-06 | INFO | H743 PA9 | `NOT_VERIFIED` | PA9 (OTG_FS_VBUS) is FT_u. Whether VBUS can connect directly, or needs a divider when VDD is off, is not checked. | H7 DS Table 9 |
| F-07 | INFO | IF-024 | `ASSUMED` | The F103 USART1 link may also serve as the F103 bootloader path. Needs AN2606 confirmation and a BOOT0 control plan for the F103. | Section 2 |

## 4. Open checks

- [ ] Human reviews the pin choices and the design choices in sections 1 and 2.
- [ ] Correct the TIM3 channel labels in the spec (F-02), and clarify IF-016 (F-01).
- [ ] Define the FlySky receiver protocol and signal level (F-03, F-04).
- [ ] P1-010: DMA streams, interrupt priorities and timer clock per peripheral.
- [ ] P1-011: pull-ups, reset states and boot-time pin states (for example the PWM outputs before firmware starts).
- [ ] P1-014: HSE frequency for both MCUs, and whether LSE (PC14/PC15) is used.
- [ ] Allocate LEDs, buzzer, safety switch, voltage and current sense ADC, and BMM150 DRDY from the free pins.
- [ ] Human confirms critical pins (power, SWD, USB, BOOT0) against the datasheet pinout figures.

## 5. Sources

- ST open pin data: https://github.com/STMicroelectronics/STM32_open_pin_data (commit `7d1f151`)
- STM32H743VI datasheet (NotebookLM source): https://www.st.com/resource/en/datasheet/stm32h743vi.pdf
- STM32F103C8 datasheet (NotebookLM source): https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
- Requirements: `AO-HORIZON_SPEC_EN.md` section 3
