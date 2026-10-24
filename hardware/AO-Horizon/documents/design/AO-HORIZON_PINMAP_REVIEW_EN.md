# AeroOptix-Horizon: Pinmap Review for the Software Team

**Revision:** 0.3
**Updated:** 2026-10-24
**From:** Hardware
**To:** Software / PX4 dev team
**Status:** Answered by the software team on 2026-10-24. The `Team` column and section 6 hold their answers, kept as written. The hardware owner's response is in section 9; the spec records the result in rev 0.12. The IO MCU is now the STM32F100C8T6B on the same pins (section 9); the board summary and the section 4 title show it. Other rows and the answers still say F103 or 8 MHz as sent. Nothing here is drawn in the schematic yet.

## 1. How to reply

1. Rows you already answered in 0.2 show `OK (0.2)` in the `Team` column. You do not need to answer them again; write `CHANGE: <what>` only if something is wrong.
2. Rows marked `NEW` are new or changed in 0.3. Fill the `Team` column with `OK`, `CHANGE: <what>` or `?: <question>`.
3. Answer the questions in section 6 under their `Answer:` lines.
4. Keep the file name. Send the whole file back.

## 2. Board summary

| Item | Value |
|---|---|
| Main MCU (FMU) | STM32H743VIT6, LQFP100, 16 MHz crystal |
| IO MCU | STM32F100C8T6B, LQFP48, 24 MHz crystal, stock px4io-v2 (changed from STM32F103C8T6 after your 0.3 answers, section 9) |
| Link between MCUs | H743 USART6 to F100 USART2, px4io protocol, 1.5 Mb/s |
| PX4 | v1.16.2, port based on `px4/fmu-v6c`; IO runs px4io-v2 |
| Outputs | 4 motors on the H743 (TIM5, DShot only, bidirectional); 8 servos on the F103 (50 Hz PWM); 3 spare outputs on the H743 |
| Flashing | H743 over USB (PX4 bootloader); first flash of both MCUs over SWD by the software team |
| Debug | H743: console and SWD on one Pixhawk Debug Mini connector. F103: SWD and console TX on pads, bench only |
| IMU | 2 × ICM-45686, each on its own SPI bus |
| Barometer | ICP-20100 (0x63) + BMP581 (0x46), both on I2C2. Fallback for the BMP581: BMP384 |
| Magnetometer | 1 × iSentek IST8310 (0x0E) on I2C2 |
| Power module | PM02D, digital, INA228 at 0x45 on I2C4 |
| Logic level | 3.3 V on both MCUs |

Hardware checked each pin against ST pin data (`STM32_open_pin_data`). The TIM5 and TIM3_CH3 AF numbers match the NuttX pinmap (AF2). No pin is used twice. Hardware did not check DMA streams, interrupt priorities or timer clocks; those are in your port.

## 3. STM32H743VIT6 (FMU)

`Pkg` is the LQFP100 package pin number.

### 3.1 Serial ports

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Telemetry 1 (ELRS: RC and telemetry) | UART7_TX | PE8 | 38 | OK (0.2) |
| Telemetry 1 (ELRS: RC and telemetry) | UART7_RX | PE7 | 37 | OK (0.2) |
| Telemetry 2 (free) | USART1_TX | PB14 | 53 | OK (0.2) |
| Telemetry 2 (free) | USART1_RX | PB15 | 54 | OK (0.2) |
| GPS1 | USART2_TX | PD5 | 86 | OK (0.2) |
| GPS1 | USART2_RX | PD6 | 87 | OK (0.2) |
| Debug console | USART3_TX | PD8 | 55 | OK (0.2) |
| Debug console | USART3_RX | PD9 | 56 | OK (0.2) |
| TF-Luna rangefinder | UART8_TX | PE1 | 98 | OK (0.2) |
| TF-Luna rangefinder | UART8_RX | PE0 | 97 | OK (0.2) |
| Link to F103 | USART6_TX | PC6 | 63 | OK (0.2) |
| Link to F103 | USART6_RX | PC7 | 64 | OK (0.2) |

### 3.2 I2C buses

| Bus | Devices | SCL | SDA | Team |
|---|---|---|---|---|
| I2C1 | GPS1 compass (external) | PB8 (95) | PB9 (96) | OK (0.2) |
| I2C2 | ICP-20100 (0x63), BMP581 (0x46), IST8310 (0x0E), onboard | PB10 (46) | PB11 (47) | OK (0.2) |
| I2C4 | MS4525DO (0x28) + PM02D power module (0x45), external | PD12 (59) | PD13 (60) | OK (0.2) |

### 3.3 SPI buses (IMUs)

| Device | SCK | MISO | MOSI | CS | INT1 (EXTI) | Team |
|---|---|---|---|---|---|---|
| IMU1 ICM-45686 on SPI1 | PA5 (29) | PA6 (30) | PA7 (31) | PA4 (28) | PC4 (32), EXTI4 | OK (0.2) |
| IMU2 ICM-45686 on SPI4 | PE12 (42) | PE13 (43) | PE14 (44) | PE11 (41) | PE15 (45), EXTI15 | OK (0.2) |

No IMU reset line (software reset). IMU pin 9 is not connected to the MCU (Q16).

### 3.4 Motor and spare outputs

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Motor 1 (front-R), FMU output 1 | TIM5_CH1 (AF2) | PA0 | 22 | OK (0.2) |
| Motor 2 (rear-L), FMU output 2 | TIM5_CH2 (AF2) | PA1 | 23 | OK (0.2) |
| Motor 3 (front-L), FMU output 3 | TIM5_CH3 (AF2) | PA2 | 24 | OK (0.2) |
| Motor 4 (rear-R), FMU output 4 | TIM5_CH4 (AF2) | PA3 | 25 | OK (0.2) |
| Spare 1 | TIM4_CH3 | PD14 | 61 | OK (0.2) |
| Spare 2 | TIM4_CH4 | PD15 | 62 | OK (0.2) |
| Spare 3 | TIM1_CH1 | PE9 | 39 | OK (0.2) |

TIM5 is timer 0 in `timer_config.cpp`, with DMA (your S2, S3). Every output has a weak pull-down and no pull-up (Q10). Hardware picks the pull-down value so that bidirectional DShot still works, and checks it on the bench.

### 3.5 USB, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| USB FS (device only) | OTG_FS_DM | PA11 | 70 | OK (0.2) |
| USB FS (device only) | OTG_FS_DP | PA12 | 71 | OK (0.2) |
| USB VBUS sense | OTG_FS_VBUS | PA9 | 68 | OK (0.2) |
| SWD | SWDIO | PA13 | 72 | OK (0.2) |
| SWD | SWCLK | PA14 | 76 | OK (0.2) |
| Reset | NRST | NRST | 14 | OK (0.2) |
| Boot select | BOOT0 | BOOT0 | 94 | OK (0.2) |
| HSE crystal, 16 MHz | OSC_IN | PH0 | 12 | OK (H1) |
| HSE crystal, 16 MHz | OSC_OUT | PH1 | 13 | OK (H1) |

**Debug connector (`NEW`).** One 6-pin JST-SH in the Pixhawk Debug Mini layout, as you asked in S6. Pinout from the PX4 docs (`docs.px4.io/main/en/debug/swd_debug.html`):

| Connector pin | Signal | H743 pin | Team |
|---|---|---|---|
| 1 | VREF (3.3 V) | - | OK (matches the PX4 docs, DS-009) |
| 2 | Console TX (from the H743) | PD8 (USART3_TX) | OK |
| 3 | Console RX (to the H743) | PD9 (USART3_RX) | OK |
| 4 | SWDIO | PA13 | OK |
| 5 | SWCLK | PA14 | OK |
| 6 | GND | - | OK |

The Debug Mini has no NRST pin. Hardware adds an NRST pad next to the connector for connect-under-reset.

### 3.6 Other functions

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| microSD | SDMMC1_D0 | PC8 | 65 | OK (S4) |
| microSD | SDMMC1_D1 | PC9 | 66 | OK (S4) |
| microSD | SDMMC1_D2 | PC10 | 78 | OK (S4) |
| microSD | SDMMC1_D3 | PC11 | 79 | OK (S4) |
| microSD | SDMMC1_CK | PC12 | 80 | OK (S4) |
| microSD | SDMMC1_CMD | PD2 | 83 | OK (S4) |
| Buzzer (passive, tone_alarm) | TIM3_CH3 (AF2) | PB0 | 34 | OK (H2) |
| LED red | GPIO out, active low | PE2 | 1 | OK (0.2) |
| LED blue | GPIO out, active low | PE3 | 2 | OK (0.2) |
| LED green | GPIO out, active low | PE4 | 3 | OK (0.2) |
| Analog battery V / I (reserve) | ADC123_INP10 / INP11 | PC0 / PC1 | 15 / 16 | OK (0.2) |

No microSD card-detect pin (S4). HRT on TIM8, no pin (Q15). PA15 is free again now that the buzzer is on PB0.

Free H743 pins (25): PA8, PA10, PB1, PB2, PB5, PB6, PB7, PB12, PB13, PC2_C, PC3_C, PC5, PC13, PC14, PC15, PD0, PD1, PD3, PD4, PD7, PD10, PD11, PE5, PE6, PE10. PA15, PB3 and PB4 are also free (JTAG pins, SWD only is used).

## 4. STM32F100C8T6B (IO MCU)

`Pkg` is the LQFP48 package pin number. All timer outputs use the default mapping (no AFIO remap). All pins are the px4io-v2 pins.

### 4.1 Servo outputs (50 Hz PWM)

| Output | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| IO output 1: flaperon L | TIM2_CH1 | PA0 | 10 | OK (0.2) |
| IO output 2: flaperon R | TIM2_CH2 | PA1 | 11 | OK (0.2) |
| IO output 3: ruddervator L | TIM4_CH3 | PB8 | 45 | OK (0.2) |
| IO output 4: ruddervator R | TIM4_CH4 | PB9 | 46 | OK (0.2) |
| IO output 5: tilt servo 1 (front-R) | TIM3_CH1 | PA6 | 16 | OK (0.2) |
| IO output 6: tilt servo 2 (rear-L) | TIM3_CH2 | PA7 | 17 | OK (0.2) |
| IO output 7: tilt servo 3 (front-L) | TIM3_CH3 | PB0 | 18 | OK (0.2) |
| IO output 8: tilt servo 4 (rear-R) | TIM3_CH4 | PB1 | 19 | OK (0.2) |

### 4.2 Serial, safety, debug, boot, clock

| Function | Signal | Pin | Pkg | Team |
|---|---|---|---|---|
| Link to H743 | USART2_TX | PA2 | 12 | OK (0.2) |
| Link to H743 | USART2_RX | PA3 | 13 | OK (0.2) |
| px4io console (TX only, to a pad) | USART1_TX | PA9 | 30 | OK (Q21) |
| Safety button | GPIO in | PB5 | 41 | OK (0.2) |
| Safety LED | GPIO out, open drain, active low | PB13 | 26 | OK (0.2) |
| Servo rail sense (3:1 divider) | ADC1_IN4 | PA4 | 14 | OK (0.2) |
| SWD (pads) | SWDIO | PA13 | 34 | OK (0.2) |
| SWD (pads) | SWCLK | PA14 | 37 | OK (0.2) |
| Reset (pad) | NRST | NRST | 7 | OK (0.2) |
| Boot select | BOOT0 (pull-down) | BOOT0 | 44 | OK (0.2) |
| Boot select | BOOT1 (pull-down) | PB2 | 20 | OK (0.2) |
| HSE crystal, 8 MHz | OSC_IN | PD0 | 5 | OK, we can rebuild px4io for 8 MHz (S7 a). Simpler, if you can buy it: an STM32F100C8T6B with a 24 MHz crystal. px4io-v2 is built for that chip, so stock px4io runs unchanged and nothing needs a custom build. Same speed: px4io runs at 24 MHz on either chip. Please check that its LQFP48 pinout matches the F103 (PA11/PA12 are USB on the F103, plain GPIO on the F100). DigiKey had 988 in stock on 2026-10-08. Correction to our S7 answer: the stock px4io bootloader runs from the internal HSI clock, so it needs no rebuild either way |
| HSE crystal, 8 MHz | OSC_OUT | PD1 | 6 | OK |

### 4.3 Other px4io-v2 pins

These are left for their px4io-v2 function and not used for anything else (F5 in the decisions file).

| Pin | px4io-v2 function | Plan | Team |
|---|---|---|---|
| PB14 | Blue LED (also heater output) | See Q20 | OK, fit the LED (Q20) |
| PB15 | Amber LED | See Q20 | OK, fit the LED (Q20) |
| PA11 | Green LED | See Q20 | OK, fit the LED (Q20) |
| PA15 | Servo fault input | Unconnected | OK |
| PA5, PA12 | RSSI | Unconnected | OK |
| PC13, PA10 | Spektrum (PA10 is also USART1_RX) | Unconnected | CHANGE: keep unconnected, but add a weak pull-up to 3.3 V on PA10. It is a UART RX input (DSM); left floating, noise could be decoded as RC input |
| PB10, PB11, PB4 | SBUS | Unconnected | CHANGE: keep unconnected, but add a weak pull-up to 3.3 V on PB11 (SBUS input), same reason as PA10 |
| PA8 | PPM | Unconnected | OK (px4io turns on the internal pull-up) |
| PC14, PC15 | Board sense, read at boot | Unconnected (Q6) | OK (0.2) |

Free F103 pins (4): PB3, PB6, PB7, PB12. PB3 needs the SWJ remap (SWD only) before use as GPIO.

## 5. Sensor addresses and drivers

| Part | Bus | Address | PX4 driver | Team |
|---|---|---|---|---|
| ICM-45686 (×2) | SPI1, SPI4 | - | `imu/invensense/icm45686` | OK (0.2) |
| ICP-20100 | I2C2 | 0x63 | `barometer/invensense/icp201xx` | OK (0.2) |
| BMP581 | I2C2 | 0x46 (SDO low) | `barometer/bmp581` | OK (D7) |
| BMP384 (fallback only) | I2C2 | 0x76 or 0x77 | `barometer/bmp388` | OK, 0x76 (Q22) |
| IST8310 | I2C2 | 0x0E | `magnetometer/isentek/ist8310` | OK (0.2) |
| MS4525DO (external) | I2C4 | 0x28 | `differential_pressure/ms4525do` | OK (0.2) |
| PM02D power module (external) | I2C4 | 0x45 (INA228) | `power_monitor/ina228` | OK (0.2) |

## 6. New questions in 0.3

**Q20. px4io LEDs.** px4io-v2 drives a blue LED on PB14 (also used as a heater output), an amber LED on PB15 and a green LED on PA11. Do you want them fitted on the board, or left unconnected? They show the IO status during bench work.

Answer: Fit all three. Blue blinks as the px4io heartbeat, amber blinks when the H743 link is down, and green breathes when disarmed and stays on when armed. We need them to bring up our 8 MHz px4io build.

**Q21. px4io console.** PA10 is both USART1_RX and the px4io Spektrum input, so hardware brings out only USART1 TX (PA9) to a pad, with GND. Is a TX-only console enough for you?

Answer: Yes. The px4io console only prints (px4io-v2 has no shell), so TX is enough.

**Q22. BMP384 fallback address.** If the BMP384 is fitted instead of the BMP581, which address do you want, 0x76 or 0x77? Your start script sets it.

Answer: 0x76 (SDO low), the default of the PX4 bmp388 driver.

## 7. Answers from review 0.2 (kept for reference)

Your 0.2 answers, unchanged. The spec and the other records cite them by question number. Pins named here may have moved since; sections 3 to 5 are the current pinmap.

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


## 8. Sources

- Decisions and software answers: `AO-HORIZON_PINMAP_DECISIONS_EN.md` rev 0.2 (2026-10-24)
- Hardware pin record: `AO-HORIZON_PIN_ALLOCATION_EN.md` rev 0.5
- ST open pin data: https://github.com/STMicroelectronics/STM32_open_pin_data (commit `7d1f151`)
- PX4-Autopilot v1.16.2: https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/ (`io-v2`, `fmu-v6c`)
- PX4 docs, SWD debug port: https://docs.px4.io/main/en/debug/swd_debug.html

## 9. Hardware owner response (2026-10-24)

- All 0.3 answers accepted as written.
- **IO MCU (row 4.2):** changed to the STM32F100C8T6B with a 24 MHz crystal, as you proposed. Stock px4io-v2 and the stock px4io bootloader run unchanged, so no custom px4io build is needed (spec DEC-002, DEC-017). LCSC stock checked by the hardware owner.
- **F100 pinout check (your request):** ST pin data for STM32F100C(8-B)Tx and STM32F103C(8-B)Tx, LQFP48: all 48 pin names and types match, and every signal in sections 4.1 to 4.3 is on the same pin. No pin moves. The F100 datasheet (DocID16455 Rev 9) gives HSE 4 to 24 MHz (Table 21).
- **Bootloader correction:** confirmed. The PX4 F1 bootloader sets its clock with `rcc_clock_setup_in_hsi_out_24mhz()` (PX4-Bootloader `main_f1.c`, `main` branch read 2026-10-24).
- **PA10 and PB11:** both stay unconnected, with a weak pull-up to 3.3 V. Hardware picks the value.
- **Q20 LEDs:** blue (PB14), amber (PB15) and green (PA11) fitted.
- **Q22:** BMP384 fallback at 0x76, SDO low. 0x76 is the default in PX4 v1.16.2 `bmp388_main.cpp`.
