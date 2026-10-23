# PX4 Matek H743-Slim board files (reference)

Unmodified copies of the PX4 board port for the Matek H743-Slim (STM32H743VIT6, LQFP100). Used only as a reference for AO-Horizon pin allocation. Not AO-Horizon design data.

Source, checked 2026-10-24:
- PX4-Autopilot `main` @ `b26146e`, folder `boards/matek/h743-slim/`. Last change to that folder: `633af12` (2026-10-13). `board.h`, `board_config.h`, `spi.cpp` and `timer_config.cpp` match upstream line for line.
- `stm32h7x3xx_pinmap.h`: PX4/NuttX @ `8626377` (the NuttX submodule of PX4 `main`), `arch/arm/src/stm32h7/hardware/`. Matches upstream.

| File | Upstream path | Content |
|---|---|---|
| `board.h` | `nuttx-config/include/board.h` | Clocks, UART/SPI/I2C/CAN pin selection |
| `board_dma_map.h` | `nuttx-config/include/board_dma_map.h` | DMA streams for SPI1 and SPI4 |
| `defconfig.txt` | `nuttx-config/nsh/defconfig` | Enabled NuttX peripherals |
| `board_config.h` | `src/board_config.h` | LEDs, ADC, buzzer, VBUS sense, GPIO |
| `spi.cpp` | `src/spi.cpp` | SPI chip selects and DRDY per sensor |
| `i2c.cpp` | `src/i2c.cpp` | Internal and external I2C buses |
| `timer_config.cpp` | `src/timer_config.cpp` | PWM outputs: timers, channels, pins |
| `default.px4board` | `default.px4board` | Serial port roles (GPS, TELEM) and drivers |
| `rc.board_sensors` | `init/rc.board_sensors` | Sensor drivers started at boot |
| `stm32h7x3xx_pinmap.h` | NuttX (see above) | Decodes `GPIO_xxx_n` macros to port, pin and AF |

Known issues in the source:
- PE2 is both `GPIO_OTGFS_VBUS` (`board_config.h`) and SPI3 external CS2 (`spi.cpp`).
- The `board.h` USB comment says VBUS is on PA9, and the `board_config.h` HRT comment says "timer8". Both comments are stale.
- `PROBE_*` pins in `board.h` use ports H and I, which LQFP100 does not have.
- One port covers three board versions (V1.0, V1.5, V3) with different IMUs and SPI4 chip selects.
