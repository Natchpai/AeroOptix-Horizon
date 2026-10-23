# AeroOptix-Horizon: Pinmap Review for the Software Team

**Revision:** 0.2
**Updated:** 2026-10-24
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
4. Section 3.6 proposes pins for LEDs, buzzer, safety switch and other extras. Review them like the other rows. Add any other pins you need in section 7.
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
| Magnetometer | 1 × iSentek IST8310 (changed from BMM150 on 2026-10-24, see Q11) |
| Power module | PM02D, digital (I2C), see Q14 |
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
| I2C2 | ICP-20100 + IST8310 (onboard) | PB10 (46) | PB11 (47) | |
| I2C3 | Barometer 2 (onboard, BMP581 proposed) | PA8 (67) | PC9 (66) | |
| I2C4 | MS4525DO airspeed (external) + PM02D power module (proposed, Q14) | PD12 (59) | PD13 (60) | |

### 3.3 SPI buses (IMUs)

| Device | SCK | MISO | MOSI | CS | INT1 (EXTI) | Team |
|---|---|---|---|---|---|---|
| IMU1 ICM-45686 on SPI1 | PA5 (29) | PA6 (30) | PA7 (31) | PA4 (28) | PC4 (32), EXTI4 | |
| IMU2 ICM-45686 on SPI4 | PE12 (42) | PE13 (43) | PE14 (44) | PE11 (41) | PE15 (45), EXTI15 | |

No IMU reset line. Reset is by software (`SOFT_RST`). IMU pin 9 (INT2/FSYNC/CLKIN) is proposed in section 3.6 (see Q16).

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

### 3.6 Proposed pins for the remaining functions

New in revision 0.2. Hardware picked these from the free list. Each signal was checked against ST pin data and the NuttX pinmap, no pin is used twice, and the EXTI lines are all different. Rows marked "only if" depend on your answer to the question named.

| Function | Signal | Pin | Pkg | Notes | Team |
|---|---|---|---|---|---|
| LED red | GPIO out, active low | PE2 | 1 | Q13 | |
| LED blue | GPIO out, active low | PE3 | 2 | Same as PX4 `matek/h743-slim`. Q13 | |
| LED green | GPIO out, active low | PE4 | 3 | Same as PX4 `matek/h743-slim`. Q13 | |
| Buzzer | TIM2_CH1 (AF1) | PA15 | 77 | Same as PX4 `matek/h743-slim`. Q15 | |
| Safety LED | GPIO out | PD10 | 57 | Only if the safety switch is on the H743 (Q12) | |
| Safety button | GPIO in, EXTI11 | PD11 | 58 | Only if the safety switch is on the H743 (Q12) | |
| IST8310 DRDY | GPIO in, EXTI12 | PB12 | 51 | Optional. PX4 `ist8310` polls a status register instead (Q11) | |
| IST8310 RSTN | GPIO out, open drain | PB13 | 52 | Optional. Internal pull-up on the IST8310 (Q11) | |
| IMU1 pin 9 (INT2/CLKIN) | TIM3_CH3 (AF2) or GPIO in, EXTI0 | PB0 | 34 | Through a 0 Ω, fitted or not (Q16) | |
| IMU2 pin 9 (INT2/CLKIN) | TIM3_CH4 (AF2) or GPIO in, EXTI1 | PB1 | 35 | Same timer as IMU1 (Q16) | |
| F103 NRST control | GPIO out, open drain | PD3 | 84 | Only if Q9 is yes | |
| F103 BOOT0 control | GPIO out | PD4 | 85 | Only if Q9 is yes | |
| Analog battery V / I | ADC123_INP10 / INP11 | PC0 / PC1 | 15 / 16 | Reserve only, for an analog power module (Q14) | |

Free H743 pins: PA0, PA1, PA10, PB0, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC0, PC1, PC2_C, PC3_C, PC5, PC8, PC10 to PC15, PD0 to PD4, PD7, PD10, PD11, PE2 to PE6, PE10. PA15, PB3 and PB4 are also free (JTAG pins, SWD only is used). This list still includes the pins proposed in section 3.6 until you accept them.

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

Address straps are not decided. Pick one address per part, or say "any" (see Q8). The address sets of the sensors do not overlap. The PM02D address is not checked yet (Q14).

| Part | Bus | Address options | Set by | PX4 driver | Team |
|---|---|---|---|---|---|
| ICM-45686 (×2) | SPI1, SPI4 | - | - | `imu/invensense/icm45686` | |
| ICP-20100 | I2C2 | 0x63 or 0x64 | AD0 pin | `barometer/invensense/icp201xx` (ICP-20100 coverage not checked) | |
| IST8310 | I2C2 | 0x0C to 0x0F (0x0E if both pins float; PX4 default 0x0E) | CAD0 and CAD1 pins | `magnetometer/isentek/ist8310` | |
| BMP581 (proposed) | I2C3 | 0x46 (SDO low) or 0x47 (SDO high) | SDO pin | `barometer/bmp581` | |
| MS4525DO (external) | I2C4 | 0x28 | part variant | `differential_pressure/ms4525do` (not checked) | |
| PM02D power module (external) | I2C4 (proposed) | not checked | module | not checked (Q14) | |

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

**Q8. Sensor addresses.** Any preferred I2C address for ICP-20100, IST8310 and BMP581 (section 5)? Does your board config expect the defaults?

Answer:

**Q9. F103 reflash path.** Should the H743 be able to reflash the F103 over the USART link (F103 system bootloader)? If yes, the H743 must also drive the F103 BOOT0 and NRST.

Answer:

**Q10. Boot-time outputs.** What should the PWM outputs do before firmware starts (low, high-Z, pulled down)?

Answer:

Questions Q11 to Q19 are new in revision 0.2.

**Q11. Magnetometer.** Hardware changed the onboard magnetometer from BMM150 to iSentek IST8310 (PX4 driver `magnetometer/isentek/ist8310`). It sits on I2C2, the internal bus, at 0x0E unless you want another address. PX4 polls the IST8310 status register, so the DRDY and RSTN lines in section 3.6 are optional. Is IST8310 OK for you? Do you want DRDY and RSTN connected? A GPS module on I2C1 may also carry an IST8310 at 0x0E; that is a different bus, so there is no clash.

Answer:

**Q12. Safety switch.** Should the safety switch and its LED connect to the H743 (PX4 `GPIO_BTN_SAFETY` and `GPIO_LED_SAFETY`) or to the F103? On Pixhawk boards with an IO MCU, it is on the IO MCU. The answer depends on Q7.

Answer:

**Q13. LEDs.** How many board LEDs, and which colors? Section 3.6 proposes red, blue and green on the H743, active low. The PX4 Matek H743-Slim port uses only blue and green.

Answer:

**Q14. Power module.** The power connector is drawn for a PM02D with I2C (`PM02_SCL`, `PM02_SDA`). Is the module a Holybro PM02D (digital), and which PX4 driver and I2C address does it use? All four H743 I2C buses are in use, so hardware proposes sharing I2C4 with the MS4525DO (0x28). OK, or another bus?

Answer:

**Q15. Buzzer.** Passive buzzer driven by PWM (PX4 `tone_alarm` on TIM2_CH1, PA15), or an active buzzer on a plain GPIO? With TIM2 used for the buzzer, which timer do you want for the PX4 high-resolution timer (HRT)?

Answer:

**Q16. IMU external clock.** The ICM-45686 can take a 20 to 40 kHz clock on pin 9 (CLKIN). The PX4 `icm45686` driver supports it, but its code says `// TODO: this is not tested`. Do you want CLKIN (H743 TIM3 on PB0/PB1), INT2 as a second interrupt, or neither? If neither, pin 9 stays unconnected.

Answer:

**Q17. DShot and output rates.** Which outputs need DShot or a fixed update rate, on the H743 (TIM4, TIM1, TIM15) and on the F103? In the PX4 Matek H743-Slim port, TIM15 has no DMA, so DShot on TL2/TR2 may not work.

Answer:

**Q18. PX4 board port.** Which existing PX4 board target will you base the AO-Horizon port on (for example `matek/h743-slim` or `px4/fmu-v6c`)? Hardware can follow its conventions where it costs nothing.

Answer:

**Q19. USB.** VBUS sense is on PA9 (OTG_FS_VBUS). Do you need OTG_FS_ID (PA10), or is the board USB device only?

Answer:

## 7. Extra pins you need

Add rows for pins not covered by sections 3.6 and 4. Hardware picks the pin from the free list if you leave `Pin` empty.

| Function | MCU (H743 or F103) | Type (GPIO out, GPIO in, ADC, PWM, UART...) | Pin | Notes |
|---|---|---|---|---|
| | | | | |
| | | | | |
