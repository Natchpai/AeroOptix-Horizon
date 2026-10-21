# AeroOptix-Horizon: Pinmap Review for the Software Team

**Revision:** 0.1
**Updated:** 2026-10-22
**From:** Hardware
**To:** Software / PX4 dev team
**Status:** Draft for review. Nothing here is approved. Return this file with the `Team` column and section 6 filled in.

## 1. How to reply

You can fill this in by hand or ask Claude to do it. Rules for the reply:

1. Fill only the `Team` column in each table. Use one of:
   - `OK`: the row is right.
   - `CHANGE: <new pin or signal>`: give the exact pin name (for example `PE5`) and signal (for example `TIM15_CH1`).
   - `?: <question>`: you are not sure, or need hardware to explain.
2. Do not edit the other columns. Hardware updates them after your reply.
3. Answer every question in section 6 under its `Answer:` line.
4. Add new pins you need (LEDs, buzzer, safety switch, ADC, extra GPIO) in section 7.
5. Keep the file name. Send the whole file back.

## 2. Board summary

| Item | Value |
|---|---|
| Main MCU (FMU) | STM32H743VIT6, LQFP100 |
| IO MCU | STM32F103C8T6, LQFP48 |
| Link between MCUs | H743 USART6 to F103 USART1 |
| Flashing | H743 over USB FS (PX4 bootloader); first flash over SWD or ST DFU with BOOT0 |
| Debug | SWD on both MCUs |
| IMU | 2 × ICM-45686, each on its own SPI bus |
| Barometer | ICP-20100 + barometer 2 (BMP581 proposed, not confirmed) |
| Magnetometer | 1 × BMM150 |
| Logic level | 3.3 V on both MCUs |

The pins in sections 3 and 4 come from the pinout the team sent to hardware. Hardware checked that each pin can carry its signal (ST pin data and datasheets). Hardware did not check DMA streams, interrupt priorities or timer clocks.

## 3. STM32H743VIT6 (FMU)

`Pkg` is the LQFP100 package pin number.

### 3.1 Serial ports

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Telemetry 1 | UART7_TX | PE8 | 38 | |
| Telemetry 1 | UART7_RX | PE7 | 37 | |
| Telemetry 2 | USART1_TX | PB14 | 53 | |
| Telemetry 2 | USART1_RX | PB15 | 54 | |
| GPS1 | USART2_TX | PD5 | 86 | |
| GPS1 | USART2_RX | PD6 | 87 | |
| GPS2 (reserved) | USART3_TX | PD8 | 55 | |
| GPS2 (reserved) | USART3_RX | PD9 | 56 | |
| TF-Luna rangefinder | UART8_TX | PE1 | 98 | |
| TF-Luna rangefinder | UART8_RX | PE0 | 97 | |
| Link to F103 | USART6_TX | PC6 | 63 | |
| Link to F103 | USART6_RX | PC7 | 64 | |
| "UART7 TX (reserved)" | not assigned, see Q4 | - | - | |

### 3.2 I2C buses

| Bus | Devices | SCL | SDA | Team |
|---|---|---|---|---|
| I2C1 | GPS1 compass (external) | PB8 (95) | PB9 (96) | |
| I2C2 | ICP-20100 + BMM150 (onboard) | PB10 (46) | PB11 (47) | |
| I2C3 | Barometer 2 (onboard, BMP581 proposed) | PA8 (67) | PC9 (66) | |
| I2C4 | MS4525DO airspeed (external) | PD12 (59) | PD13 (60) | |

### 3.3 SPI buses (IMUs)

| Device | SCK | MISO | MOSI | CS | INT1 (EXTI) | Team |
|---|---|---|---|---|---|---|
| IMU1 ICM-45686 on SPI1 | PA5 (29) | PA6 (30) | PA7 (31) | PA4 (28) | PC4 (32), EXTI4 | |
| IMU2 ICM-45686 on SPI4 | PE12 (42) | PE13 (43) | PE14 (44) | PE11 (41) | PE15 (45), EXTI15 | |

No IMU reset line. Reset is by software (`SOFT_RST`). IMU INT2 and CLKIN are not connected yet.

### 3.4 PWM outputs on the H743

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| VT L | TIM4_CH3 | PD14 | 61 | |
| VT R | TIM4_CH4 | PD15 | 62 | |
| SP2 (reserved) | TIM1_CH1 | PE9 | 39 | |
| TL2 | TIM15_CH1 | PA2 | 24 | |
| TR2 | TIM15_CH2 | PA3 | 25 | |

### 3.5 USB, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| USB FS | OTG_FS_DM | PA11 | 70 | |
| USB FS | OTG_FS_DP | PA12 | 71 | |
| USB VBUS sense | OTG_FS_VBUS | PA9 | 68 | |
| SWD | SWDIO | PA13 | 72 | |
| SWD | SWCLK | PA14 | 76 | |
| Reset | NRST | NRST | 14 | |
| Boot select | BOOT0 | BOOT0 | 94 | |
| HSE crystal | OSC_IN | PH0 | 12 | |
| HSE crystal | OSC_OUT | PH1 | 13 | |

HSE frequency is not decided (see Q6).

Free H743 pins: PA0, PA1, PA10, PB0, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC0, PC1, PC2_C, PC3_C, PC5, PC8, PC10 to PC15, PD0 to PD4, PD7, PD10, PD11, PE2 to PE6, PE10. PA15, PB3 and PB4 are also free (JTAG pins, SWD only is used).

## 4. STM32F103C8T6 (IO MCU)

`Pkg` is the LQFP48 package pin number. All timer outputs use the default mapping (no AFIO remap).

### 4.1 PWM outputs on the F103

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| TILT L | TIM2_CH1 | PA0 | 10 | |
| TILT R | TIM2_CH2 | PA1 | 11 | |
| ESC L | TIM4_CH3 | PB8 | 45 | |
| ESC R | TIM4_CH4 | PB9 | 46 | |
| COAX T | TIM3_CH1 (your pinout says TIM3_CH5, see Q3) | PA6 | 16 | |
| COAX B | TIM3_CH2 (your pinout says TIM3_CH6) | PA7 | 17 | |
| AIL L | TIM3_CH3 (your pinout says TIM3_CH7) | PB0 | 18 | |
| AIL R | TIM3_CH4 (your pinout says TIM3_CH8) | PB1 | 19 | |

### 4.2 Serial, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Link to H743 | USART1_TX | PA9 | 30 | |
| Link to H743 | USART1_RX | PA10 | 31 | |
| FlySky receiver (candidate) | USART2_RX | PA3 | 13 | |
| FlySky receiver (candidate) | USART2_TX | PA2 | 12 | |
| SWD | SWDIO | PA13 | 34 | |
| SWD | SWCLK | PA14 | 37 | |
| Reset | NRST | NRST | 7 | |
| Boot select | BOOT0 | BOOT0 | 44 | |
| Boot select | BOOT1 | PB2 | 20 | |
| HSE crystal | OSC_IN | PD0 | 5 | |
| HSE crystal | OSC_OUT | PD1 | 6 | |

PA0 to PA3 are not 5 V tolerant. A 5 V receiver signal on PA3 needs a level check (see Q5).

Free F103 pins: PA4, PA5, PA8, PA11, PA12, PA15, PB3 to PB7, PB10 to PB15, PC13 to PC15. PA15, PB3 and PB4 need the SWJ remap (SWD only) before use as GPIO.

## 5. Sensor addresses and drivers

Address straps are not decided. Pick one address per part, or say "any" (see Q8). The address sets do not overlap.

| Part | Bus | Address options | Set by | PX4 driver | Team |
|---|---|---|---|---|---|
| ICM-45686 (×2) | SPI1, SPI4 | - | - | `imu/invensense/icm45686` | |
| ICP-20100 | I2C2 | 0x63 or 0x64 | AD0 pin | `barometer/invensense/icp201xx` (ICP-20100 coverage not checked) | |
| BMM150 | I2C2 | 0x10 to 0x13 | CSB and SDO pins | `magnetometer/bosch/bmm150` | |
| BMP581 (proposed) | I2C3 | 0x46 (SDO low) or 0x47 (SDO high) | SDO pin | `barometer/bmp581` | |
| MS4525DO (external) | I2C4 | 0x28 | part variant | `differential_pressure/ms4525do` (not checked) | |

## 6. Questions for the software team

**Q1. Source of the pinout.** Did this pinout come from Pixhawk 6C, Pixhawk 6X, or both? Which PX4 board target did you test with (for example `px4_fmu-v6c`)?

Answer:

**Q2. What "it works" covered.** Was it tested on the Pixhawk hardware only? Note: the 6C uses an STM32H743, and the 6X uses an STM32H753 in a different package, so 6X pins may not carry over to our LQFP100 part.

Answer:

**Q3. F103 TIM3 channels.** The F103 TIM3 has CH1 to CH4 only. TIM3_CH5 to CH8 do not exist. Hardware proposes TIM3_CH1 to CH4 on PA6, PA7, PB0, PB1 (section 4.1). OK, or a different mapping?

Answer:

**Q4. "UART7 TX (reserved)".** UART7 is already Telemetry 1. What was this reserved output for? Drop it, or move it to another UART (UART4 or UART5)?

Answer:

**Q5. FlySky receiver.** Which protocol: PPM, PWM, i-BUS or S.BUS? What signal voltage (3.3 V or 5 V)? PPM needs a timer input, and S.BUS needs an inverter.

Answer:

**Q6. Clocks.** HSE crystal frequency for the H743 and for the F103? Do you use the LSE (32.768 kHz) on either MCU?

Answer:

**Q7. F103 firmware.** Will the F103 run stock PX4 IO firmware (`px4io`) or custom firmware? The F103 must also command an immediate landing if the H743 stops (SAF-001), which stock `px4io` may not do. This choice sets the F103 pins and the USART protocol.

Answer:

**Q8. Sensor addresses.** Any preferred I2C address for ICP-20100, BMM150 and BMP581 (section 5)? Does your board config expect the defaults?

Answer:

**Q9. F103 reflash path.** Should the H743 be able to reflash the F103 over the USART link (F103 system bootloader)? If yes, the H743 must also drive the F103 BOOT0 and NRST.

Answer:

**Q10. Boot-time outputs.** What should the PWM outputs do before firmware starts (low, high-Z, pulled down)?

Answer:

## 7. Extra pins you need

Add rows. Hardware picks the pin from the free list if you leave `Pin` empty.

| Function | MCU (H743 or F103) | Type (GPIO out, GPIO in, ADC, PWM, UART...) | Pin | Notes |
|---|---|---|---|---|
| Status LED | | | | |
| Buzzer | | | | |
| Safety switch | | | | |
| Battery voltage sense | | ADC | | |
| Battery current sense | | ADC | | |
| BMM150 DRDY | H743 | GPIO in | | |
| | | | | |
