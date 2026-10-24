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
| Telemetry 1 | UART7_TX | PE8 | 38 | OK (ELRS receiver, Q5) |
| Telemetry 1 | UART7_RX | PE7 | 37 | OK |
| Telemetry 2 | USART1_TX | PB14 | 53 | OK |
| Telemetry 2 | USART1_RX | PB15 | 54 | OK |
| GPS1 | USART2_TX | PD5 | 86 | OK |
| GPS1 | USART2_RX | PD6 | 87 | OK |
| GPS2 (reserved) | USART3_TX | PD8 | 55 | CHANGE: USART3_TX PD8 = debug console (no GPS2 needed) |
| GPS2 (reserved) | USART3_RX | PD9 | 56 | CHANGE: USART3_RX PD9 = debug console |
| TF-Luna rangefinder | UART8_TX | PE1 | 98 | OK |
| TF-Luna rangefinder | UART8_RX | PE0 | 97 | OK |
| Link to F103 | USART6_TX | PC6 | 63 | OK |
| Link to F103 | USART6_RX | PC7 | 64 | OK |
| "UART7 TX (reserved)" | not assigned, see Q4 | - | - | CHANGE: drop (Q4) |

### 3.2 I2C buses

| Bus | Devices | SCL | SDA | Team |
|---|---|---|---|---|
| I2C1 | GPS1 compass (external) | PB8 (95) | PB9 (96) | OK |
| I2C2 | ICP-20100 + IST8310 (onboard) | PB10 (46) | PB11 (47) | CHANGE: add BMP581 (0x46) here, I2C3 is dropped |
| I2C3 | Barometer 2 (onboard, BMP581 proposed) | PA8 (67) | PC9 (66) | CHANGE: drop. PC9 is needed for microSD (SDMMC1_D1, section 7) |
| I2C4 | MS4525DO airspeed (external) + PM02D power module (proposed, Q14) | PD12 (59) | PD13 (60) | OK (no address clash, Q14) |

### 3.3 SPI buses (IMUs)

| Device | SCK | MISO | MOSI | CS | INT1 (EXTI) | Team |
|---|---|---|---|---|---|---|
| IMU1 ICM-45686 on SPI1 | PA5 (29) | PA6 (30) | PA7 (31) | PA4 (28) | PC4 (32), EXTI4 | OK |
| IMU2 ICM-45686 on SPI4 | PE12 (42) | PE13 (43) | PE14 (44) | PE11 (41) | PE15 (45), EXTI15 | OK |

No IMU reset line. Reset is by software (`SOFT_RST`). IMU pin 9 (INT2/FSYNC/CLKIN) is proposed in section 3.6 (see Q16).

### 3.4 PWM outputs on the H743

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| VT L | TIM4_CH3 | PD14 | 61 | CHANGE: spare (Q17) |
| VT R | TIM4_CH4 | PD15 | 62 | CHANGE: spare (Q17) |
| SP2 (reserved) | TIM1_CH1 | PE9 | 39 | OK (spare) |
| TL2 | TIM15_CH1 | PA2 | 24 | CHANGE: TIM5_CH3 (AF2) on PA2, motor 3 (Q17) |
| TR2 | TIM15_CH2 | PA3 | 25 | CHANGE: TIM5_CH4 (AF2) on PA3, motor 4 (Q17) |

### 3.5 USB, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| USB FS | OTG_FS_DM | PA11 | 70 | OK |
| USB FS | OTG_FS_DP | PA12 | 71 | OK |
| USB VBUS sense | OTG_FS_VBUS | PA9 | 68 | OK |
| SWD | SWDIO | PA13 | 72 | OK |
| SWD | SWCLK | PA14 | 76 | OK |
| Reset | NRST | NRST | 14 | OK |
| Boot select | BOOT0 | BOOT0 | 94 | OK |
| HSE crystal | OSC_IN | PH0 | 12 | OK, 8 MHz (Q6) |
| HSE crystal | OSC_OUT | PH1 | 13 | OK |

HSE frequency is not decided (see Q6).

### 3.6 Proposed pins for the remaining functions

New in revision 0.2. Hardware picked these from the free list. Each signal was checked against ST pin data and the NuttX pinmap, no pin is used twice, and the EXTI lines are all different. Rows marked "only if" depend on your answer to the question named.

| Function | Signal | Pin | Pkg | Notes | Team |
|---|---|---|---|---|---|
| LED red | GPIO out, active low | PE2 | 1 | Q13 | OK |
| LED blue | GPIO out, active low | PE3 | 2 | Same as PX4 `matek/h743-slim`. Q13 | OK |
| LED green | GPIO out, active low | PE4 | 3 | Same as PX4 `matek/h743-slim`. Q13 | OK |
| Buzzer | TIM2_CH1 (AF1) | PA15 | 77 | Same as PX4 `matek/h743-slim`. Q15 | OK (Q15) |
| Safety LED | GPIO out | PD10 | 57 | Only if the safety switch is on the H743 (Q12) | CHANGE: not needed, safety is on the F103 (Q12) |
| Safety button | GPIO in, EXTI11 | PD11 | 58 | Only if the safety switch is on the H743 (Q12) | CHANGE: not needed, safety is on the F103 (Q12) |
| IST8310 DRDY | GPIO in, EXTI12 | PB12 | 51 | Optional. PX4 `ist8310` polls a status register instead (Q11) | CHANGE: not needed (Q11) |
| IST8310 RSTN | GPIO out, open drain | PB13 | 52 | Optional. Internal pull-up on the IST8310 (Q11) | CHANGE: not needed (Q11) |
| IMU1 pin 9 (INT2/CLKIN) | TIM3_CH3 (AF2) or GPIO in, EXTI0 | PB0 | 34 | Through a 0 Ω, fitted or not (Q16) | CHANGE: not needed (Q16) |
| IMU2 pin 9 (INT2/CLKIN) | TIM3_CH4 (AF2) or GPIO in, EXTI1 | PB1 | 35 | Same timer as IMU1 (Q16) | CHANGE: not needed (Q16) |
| F103 NRST control | GPIO out, open drain | PD3 | 84 | Only if Q9 is yes | CHANGE: not needed (Q9) |
| F103 BOOT0 control | GPIO out | PD4 | 85 | Only if Q9 is yes | CHANGE: not needed (Q9) |
| Analog battery V / I | ADC123_INP10 / INP11 | PC0 / PC1 | 15 / 16 | Reserve only, for an analog power module (Q14) | OK (reserve) |

Free H743 pins: PA0, PA1, PA10, PB0, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC0, PC1, PC2_C, PC3_C, PC5, PC8, PC10 to PC15, PD0 to PD4, PD7, PD10, PD11, PE2 to PE6, PE10. PA15, PB3 and PB4 are also free (JTAG pins, SWD only is used). This list still includes the pins proposed in section 3.6 until you accept them.

## 4. STM32F103C8T6 (IO MCU)

`Pkg` is the LQFP48 package pin number. All timer outputs use the default mapping (no AFIO remap).

### 4.1 PWM outputs on the F103

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| TILT L | TIM2_CH1 | PA0 | 10 | CHANGE: Output = flaperon L, pin/signal OK (Q17) |
| TILT R | TIM2_CH2 | PA1 | 11 | CHANGE: Output = flaperon R, pin/signal OK |
| ESC L | TIM4_CH3 | PB8 | 45 | CHANGE: Output = ruddervator L, pin/signal OK |
| ESC R | TIM4_CH4 | PB9 | 46 | CHANGE: Output = ruddervator R, pin/signal OK |
| COAX T | TIM3_CH1 (your pinout says TIM3_CH5, see Q3) | PA6 | 16 | CHANGE: Output = tilt servo 1 (front-R). TIM3_CH1 OK (Q3) |
| COAX B | TIM3_CH2 (your pinout says TIM3_CH6) | PA7 | 17 | CHANGE: Output = tilt servo 2 (rear-L). TIM3_CH2 OK |
| AIL L | TIM3_CH3 (your pinout says TIM3_CH7) | PB0 | 18 | CHANGE: Output = tilt servo 3 (front-L). TIM3_CH3 OK |
| AIL R | TIM3_CH4 (your pinout says TIM3_CH8) | PB1 | 19 | CHANGE: Output = tilt servo 4 (rear-R). TIM3_CH4 OK |

### 4.2 Serial, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Link to H743 | USART1_TX | PA9 | 30 | CHANGE: USART2_TX PA2 (pkg 12), required by px4io-v2 (Q7) |
| Link to H743 | USART1_RX | PA10 | 31 | CHANGE: USART2_RX PA3 (pkg 13), required by px4io-v2 (Q7) |
| FlySky receiver (candidate) | USART2_RX | PA3 | 13 | CHANGE: no RC receiver here (Q5). PA3 = link RX |
| FlySky receiver (candidate) | USART2_TX | PA2 | 12 | CHANGE: no RC receiver here (Q5). PA2 = link TX |
| SWD | SWDIO | PA13 | 34 | OK |
| SWD | SWCLK | PA14 | 37 | OK |
| Reset | NRST | NRST | 7 | OK |
| Boot select | BOOT0 | BOOT0 | 44 | OK (pull-down) |
| Boot select | BOOT1 | PB2 | 20 | OK (pull-down) |
| HSE crystal | OSC_IN | PD0 | 5 | OK, 24 MHz, required (Q6) |
| HSE crystal | OSC_OUT | PD1 | 6 | OK |

PA0 to PA3 are not 5 V tolerant. A 5 V receiver signal on PA3 needs a level check (see Q5).

Free F103 pins: PA4, PA5, PA8, PA11, PA12, PA15, PB3 to PB7, PB10 to PB15, PC13 to PC15. PA15, PB3 and PB4 need the SWJ remap (SWD only) before use as GPIO.

## 5. Sensor addresses and drivers

Address straps are not decided. Pick one address per part, or say "any" (see Q8). The address sets of the sensors do not overlap. The PM02D address is not checked yet (Q14).

| Part | Bus | Address options | Set by | PX4 driver | Team |
|---|---|---|---|---|---|
| ICM-45686 (×2) | SPI1, SPI4 | - | - | `imu/invensense/icm45686` | OK |
| ICP-20100 | I2C2 | 0x63 or 0x64 | AD0 pin | `barometer/invensense/icp201xx` (ICP-20100 coverage not checked) | OK, 0x63 (icp201xx covers ICP-20100) |
| IST8310 | I2C2 | 0x0C to 0x0F (0x0E if both pins float; PX4 default 0x0E) | CAD0 and CAD1 pins | `magnetometer/isentek/ist8310` | OK, 0x0E |
| BMP581 (proposed) | I2C3 | 0x46 (SDO low) or 0x47 (SDO high) | SDO pin | `barometer/bmp581` | CHANGE: bus I2C2, 0x46 |
| MS4525DO (external) | I2C4 | 0x28 | part variant | `differential_pressure/ms4525do` (not checked) | OK, 0x28 |
| PM02D power module (external) | I2C4 (proposed) | not checked | module | not checked (Q14) | CHANGE: driver power_monitor/ina228, address 0x45 (Q14) |

## 6. Questions for the software team

**Q1. Source of the pinout.** Did this pinout come from Pixhawk 6C, Pixhawk 6X, or both? Which PX4 board target did you test with (for example `px4_fmu-v6c`)?

Answer: Checked against the PX4 v1.16.2 source: most H743 pins match Pixhawk 6C (`px4/fmu-v6c`), the sensor list matches Pixhawk 6X Rev 8, and the F103 PWM pins match `px4/io-v2`. Targets we have run: our own port `kmutnb_nucleo-h753zi` on a NUCLEO-H753ZI bench, and `px4_sitl` (Gazebo) for our aircraft, Model G.

**Q2. What "it works" covered.** Was it tested on the Pixhawk hardware only? Note: the 6C uses an STM32H743, and the 6X uses an STM32H753 in a different package, so 6X pins may not carry over to our LQFP100 part.

Answer: No Pixhawk was used. "It works" covered the NUCLEO-H753ZI bench: PX4 boots, IMU on SPI, baro and mag on I2C, EKF2, GPS on UART7 with an outdoor position fix, and ELRS telemetry to QGC. Not tested: PWM outputs, the F103/px4io link, microSD, and the sensors on this board. The pins come from 6C (same STM32H743VI LQFP100), not 6X, so they carry over.

**Q3. F103 TIM3 channels.** The F103 TIM3 has CH1 to CH4 only. TIM3_CH5 to CH8 do not exist. Hardware proposes TIM3_CH1 to CH4 on PA6, PA7, PB0, PB1 (section 4.1). OK, or a different mapping?

Answer: OK. CH5 to CH8 meant IO outputs 5 to 8. In px4io-v2 these are TIM3_CH1 to CH4 on PA6, PA7, PB0, PB1.

**Q4. "UART7 TX (reserved)".** UART7 is already Telemetry 1. What was this reserved output for? Drop it, or move it to another UART (UART4 or UART5)?

Answer: Drop it.

**Q5. FlySky receiver.** Which protocol: PPM, PWM, i-BUS or S.BUS? What signal voltage (3.3 V or 5 V)? PPM needs a timer input, and S.BUS needs an inverter.

Answer: No FlySky. We use an ELRS receiver in MAVLink mode on Telemetry 1 (UART7, 460800 baud, 3.3 V logic). It carries both RC and telemetry. PX4 has no i-BUS support. The F103 needs no RC input.

**Q6. Clocks.** HSE crystal frequency for the H743 and for the F103? Do you use the LSE (32.768 kHz) on either MCU?

Answer: H743: 8 MHz; we already have a tested clock setup for it (16 MHz would also work). F103: 24 MHz, required by px4io-v2. No LSE on either MCU. Leave F103 PC14/PC15 unconnected, because px4io reads them at boot.

**Q7. F103 firmware.** Will the F103 run stock PX4 IO firmware (`px4io`) or custom firmware? The F103 must also command an immediate landing if the H743 stops (SAF-001), which stock `px4io` may not do. This choice sets the F103 pins and the USART protocol.

Answer: Stock PX4 IO firmware (px4io-v2). This fixes the F103 pins: link to the H743 on USART2 (PA2 TX, PA3 RX) at 1.5 Mb/s, PWM as in 4.1, and a 24 MHz crystal. SAF-001: stock px4io cannot land the aircraft, because the F103 has no IMU. If the H743 stops, the F103 sets its outputs to fixed failsafe values after 0.5 s, and the ESCs stop when their signal stops. We propose rewording SAF-001 to match that.

**Q8. Sensor addresses.** Any preferred I2C address for ICP-20100, IST8310 and BMP581 (section 5)? Does your board config expect the defaults?

Answer: No preference. The addresses are set in our start script, so any strap works. Defaults: ICP-20100 0x63, IST8310 0x0E, BMP581 0x46.

**Q9. F103 reflash path.** Should the H743 be able to reflash the F103 over the USART link (F103 system bootloader)? If yes, the H743 must also drive the F103 BOOT0 and NRST.

Answer: No. PX4 updates the F103 firmware by itself at boot, over the USART link. No BOOT0/NRST lines from the H743 are needed. The first F103 flash goes over SWD.

**Q10. Boot-time outputs.** What should the PWM outputs do before firmware starts (low, high-Z, pulled down)?

Answer: Low. Put a weak pull-down on every PWM line, and no pull-ups.

Questions Q11 to Q19 are new in revision 0.2.

**Q11. Magnetometer.** Hardware changed the onboard magnetometer from BMM150 to iSentek IST8310 (PX4 driver `magnetometer/isentek/ist8310`). It sits on I2C2, the internal bus, at 0x0E unless you want another address. PX4 polls the IST8310 status register, so the DRDY and RSTN lines in section 3.6 are optional. Is IST8310 OK for you? Do you want DRDY and RSTN connected? A GPS module on I2C1 may also carry an IST8310 at 0x0E; that is a different bus, so there is no clash.

Answer: IST8310 is OK, at 0x0E. DRDY and RSTN are not needed; leave them unconnected.

**Q12. Safety switch.** Should the safety switch and its LED connect to the H743 (PX4 `GPIO_BTN_SAFETY` and `GPIO_LED_SAFETY`) or to the F103? On Pixhawk boards with an IO MCU, it is on the IO MCU. The answer depends on Q7.

Answer: On the F103, as in px4io-v2: button on PB5, LED on PB13 (rows in section 7).

**Q13. LEDs.** How many board LEDs, and which colors? Section 3.6 proposes red, blue and green on the H743, active low. The PX4 Matek H743-Slim port uses only blue and green.

Answer: Three LEDs (red, blue, green), active low, as proposed.

**Q14. Power module.** The power connector is drawn for a PM02D with I2C (`PM02_SCL`, `PM02_SDA`). Is the module a Holybro PM02D (digital), and which PX4 driver and I2C address does it use? All four H743 I2C buses are in use, so hardware proposes sharing I2C4 with the MS4525DO (0x28). OK, or another bus?

Answer: Digital (I2C), as drawn; please check the label on the unit. The current Holybro PM02D uses a TI INA228: PX4 driver `power_monitor/ina228`, address 0x45 (an older 6S version uses an INA226 at 0x41). Sharing I2C4 with the MS4525DO (0x28) is OK.

**Q15. Buzzer.** Passive buzzer driven by PWM (PX4 `tone_alarm` on TIM2_CH1, PA15), or an active buzzer on a plain GPIO? With TIM2 used for the buzzer, which timer do you want for the PX4 high-resolution timer (HRT)?

Answer: Passive buzzer on TIM2_CH1 (PA15), driven by PX4 tone_alarm. The HRT goes on TIM8, which needs no pin. Note: matek/h743-slim drives PA15 as plain GPIO, because its HRT uses TIM2.

**Q16. IMU external clock.** The ICM-45686 can take a 20 to 40 kHz clock on pin 9 (CLKIN). The PX4 `icm45686` driver supports it, but its code says `// TODO: this is not tested`. Do you want CLKIN (H743 TIM3 on PB0/PB1), INT2 as a second interrupt, or neither? If neither, pin 9 stays unconnected.

Answer: Neither. Handle pin 9 as the ICM-45686 datasheet says for an unused pin. PB0 and PB1 stay free.

**Q17. DShot and output rates.** Which outputs need DShot or a fixed update rate, on the H743 (TIM4, TIM1, TIM15) and on the F103? In the PX4 Matek H743-Slim port, TIM15 has no DMA, so DShot on TL2/TR2 may not work.

Answer: Our aircraft, Model G, is a quad tilt-rotor. It needs 12 outputs: 4 ESCs, 4 tilt servos, 2 flaperons, 2 ruddervators. The old output names came from a cancelled design. Motors: put all four on one timer with DMA, so they can run DShot. PX4 runs bidirectional DShot (RPM feedback) on one timer only. Use TIM5_CH1 to CH4 on PA0 to PA3 (AF2): motor 1 front-R, 2 rear-L, 3 front-L, 4 rear-R. TIM5 can also run plain PWM. TIM15 has no DMA in PX4, so no DShot on TL2/TR2. Servos: PWM at 50 Hz on the F103, as in 4.1. PD14, PD15 and PE9 stay spare.

**Q18. PX4 board port.** Which existing PX4 board target will you base the AO-Horizon port on (for example `matek/h743-slim` or `px4/fmu-v6c`)? Hardware can follow its conventions where it costs nothing.

Answer: `px4/fmu-v6c`: same STM32H743VI, same F103 IO on USART6.

**Q19. USB.** VBUS sense is on PA9 (OTG_FS_VBUS). Do you need OTG_FS_ID (PA10), or is the board USB device only?

Answer: USB device only. OTG_FS_ID is not needed.

## 7. Extra pins you need

Add rows for pins not covered by sections 3.6 and 4. Hardware picks the pin from the free list if you leave `Pin` empty.

| Function | MCU (H743 or F103) | Type (GPIO out, GPIO in, ADC, PWM, UART...) | Pin | Notes |
|---|---|---|---|---|
| microSD card, 4-bit | H743 | SDMMC1 | PC12 (CK), PD2 (CMD), PC8, PC9, PC10, PC11 (D0-D3) | Flight logs. PC9 comes from I2C3 |
| Motor 1 ESC (front-R) | H743 | PWM / DShot, TIM5_CH1 (AF2) | PA0 | Same timer as PA1-PA3 (Q17) |
| Motor 2 ESC (rear-L) | H743 | PWM / DShot, TIM5_CH2 (AF2) | PA1 | Same timer as PA0, PA2, PA3 (Q17) |
| Safety button | F103 | GPIO in | PB5 | px4io-v2 (Q12) |
| Safety LED | F103 | GPIO out, open drain, active low | PB13 | px4io-v2 (Q12) |
| Servo rail voltage | F103 | ADC | PA4 | px4io-v2, 3:1 divider |
