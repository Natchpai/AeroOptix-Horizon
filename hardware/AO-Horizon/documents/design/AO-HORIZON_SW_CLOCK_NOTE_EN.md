# AeroOptix-Horizon: Clock Note for the Software Team

**Revision:** 0.1
**Updated:** 2026-11-14
**From:** Hardware
**To:** Software team
**Status:** Request for firmware changes (checklist P1-017). Not a verification record. The board is in schematic capture; nothing is built yet.
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md) rev 0.38 (DEC-017, DEC-022, DEC-044, DEC-045, OPEN-028)

## 1. Summary

The board uses CMOS oscillators, not crystals, for both MCU clocks (DEC-044). An oscillator drives OSC_IN with a ready-made clock, so the HSE must run in **bypass mode** (`RCC_CR.HSEBYP = 1`). The stock PX4 images start the HSE in crystal mode. Hardware decided to keep the oscillators and asks for firmware changes instead (DEC-045).

We need three things from you:

1. H743 firmware: set HSE bypass in the board config.
2. H743 bootloader: build it from the same board config. The prebuilt fmu-v6c bootloader does not set bypass.
3. F100 px4io: a custom px4io build that sets HSE bypass, used in place of the stock `px4_io-v2_default.bin`.

Clock frequencies do not change: 16 MHz on the H743 (as `px4/fmu-v6c`) and 24 MHz on the F100 (as `px4/io-v2`), so the PLL settings and the 1.5 Mb/s px4io link (DEC-015) stay the same.

## 2. Hardware as drawn

Saved schematic of 2026-11-14 (16:36), not yet reviewed or ERC-checked. Oscillator part numbers are not decided yet (OPEN-010).

| MCU | Oscillator (drawn) | Connection | OSC_OUT |
| --- | --- | --- | --- |
| STM32H743VIT6 (U201) | U202 ECS-2520MV-160-CN-TR, 16 MHz | Output through 22 Ω to PH0 (OSC_IN, pin 12). VDD and EN on `+3V3`, so it runs whenever 3.3 V is up. | PH1 (pin 13) not driven (stub label) |
| STM32F100C8T6B (U301) | U302 ASDDV-24.000MHZ-LC-T, 24 MHz | Output through 22 Ω to PD0 (OSC_IN, pin 5). VDD and EN on `+3V3`. | PD1 (pin 6) not driven (stub label) |

There is no MCO test point. HSE checks on the bench go through SWD (read `RCC_CR`).

## 3. What the stock code does

Checked by Hardware in PX4-Autopilot `v1.16.2` and the NuttX commit it pins (`PX4/NuttX` `886acbb`). Read from source; not built or run.

| Target | Finding | Source |
| --- | --- | --- |
| `px4/fmu-v6c` firmware | `board.h` uses the HSE as the PLL source (`STM32_BOARD_USEHSE`, `STM32_BOARD_XTAL 16000000ul`) and does not define `STM32_HSEBYP_ENABLE`. NuttX sets HSEBYP only when that macro is defined, so the stock image runs the HSE in crystal mode. | `boards/px4/fmu-v6c/nuttx-config/include/board.h` lines 60 to 98; NuttX `arch/arm/src/stm32h7/stm32h7x3xx_rcc.c` lines 686 to 693 |
| `px4/fmu-v6c` bootloader | `nuttx-config/bootloader/defconfig` points to the same `nuttx-config` folder (`CONFIG_ARCH_BOARD_CUSTOM_DIR`), so the bootloader takes the same `board.h` clock setup. fmu-v6c ships it prebuilt as `extras/px4_fmu-v6c_bootloader.bin`, built without bypass. That it uses the same `include/board.h` is our reading of the NuttX board layout (`ASSUMED`). | `boards/px4/fmu-v6c/nuttx-config/bootloader/defconfig` line 14; `boards/px4/fmu-v6c/extras/` |
| `px4/io-v2` (px4io) | `board.h` runs the 24 MHz HSE directly as SYSCLK. NuttX `stm32_stdclockconfig()` for the F1 always clears HSEBYP before setting HSEON; there is no board macro for bypass. The io-v2 defconfig does not set `CONFIG_ARCH_BOARD_STM32_CUSTOM_CLOCKCONFIG`. | `boards/px4/io-v2/nuttx-config/include/board.h` lines 57 to 65; NuttX `arch/arm/src/stm32/stm32f10xxx_rcc.c` lines 628 to 645 |
| px4io on HSE failure | If HSERDY never sets, `stm32_stdclockconfig()` returns and the F100 stays on the 8 MHz HSI. Our estimate: px4io would then run at the wrong speed and the 1.5 Mb/s link to the H743 would fail. | `stm32f10xxx_rcc.c` lines 660 to 667 |
| px4io bootloader | Runs from HSI (`rcc_clock_setup_in_hsi_out_24mhz()`), so it does not need the HSE. No change. | PX4-Bootloader `main_f1.c`, `main` branch read 2026-10-24 (spec DEC-017) |

## 4. Requested changes (P1-017)

### 4.1 H743 firmware and bootloader

- In the board's `nuttx-config/include/board.h` (the target based on `px4/fmu-v6c`), add:

  ```c
  #define STM32_HSEBYP_ENABLE   /* CMOS oscillator on PH0, DEC-044 */
  ```

- Build the bootloader from the same board config (`bootloader.px4board`) and ship that binary. Do not use the prebuilt `px4_fmu-v6c_bootloader.bin`.
- Nothing else in the clock tree changes.

### 4.2 F100 px4io

px4io must set HSEBYP before HSEON. Two ways we can see in the source; the choice is yours:

- **(a) Board clock hook.** Set `CONFIG_ARCH_BOARD_STM32_CUSTOM_CLOCKCONFIG=y` in the px4io defconfig and provide `stm32_board_clockconfig()` in the board code. It can copy `stm32_stdclockconfig()` with `regval |= RCC_CR_HSEBYP;` in place of the line that clears it. NuttX calls this hook from `stm32_clockconfig()` and `stm32_clockenable()` (NuttX `arch/arm/src/stm32/stm32_rcc.c` lines 176 to 180 and 231 to 235). This keeps NuttX unpatched.
- **(b) NuttX patch.** Make `stm32f10xxx_rcc.c` honour `STM32_HSEBYP_ENABLE` the same way `stm32h7x3xx_rcc.c` does, and define it in the px4io `board.h`.

Then ship the custom px4io binary in the board's `extras/` in place of `px4_io-v2_default.bin` (DEC-022 changed by DEC-045). Hardware assumes the custom build changes only the clock setup, so pin use, LEDs, the servo failsafe (SAF-001) and the link protocol stay as stock px4io (`ASSUMED`). Please tell us if that is wrong.

## 5. Bench check (later)

With SWD on each MCU after boot: `RCC_CR` shows HSEON = 1, HSEBYP = 1 and HSERDY = 1, and the system clock source is the PLL (H743) or the HSE (F100). The H743 and F100 link comes up at 1.5 Mb/s. Hardware will add this to the bring-up tests.

## 6. Questions for you

Fill `Answer:` and `By:` (name or role). Write `later` if you do not know yet.

1. Which PX4 board target will this board use (a copy of `px4/fmu-v6c` under a new vendor and model, or something else)?
   Answer:
   By:
2. For px4io, (a) board clock hook or (b) NuttX patch? Where will the custom px4io build live?
   Answer:
   By:
3. Does anything else in px4io or the PX4 start-up assume a crystal (for example, clock security system or HSE timeout handling)?
   Answer:
   By:
4. Do you need anything from Hardware for this (MCO test point, oscillator start-up time, a different oscillator frequency)?
   Answer:
   By:

## 7. Sources

- PX4-Autopilot v1.16.2: https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/fmu-v6c and https://github.com/PX4/PX4-Autopilot/tree/v1.16.2/boards/px4/io-v2
- PX4/NuttX at `886acbbdb4f061e5c0ce1a76afbcfa7cb7df9849` (the v1.16.2 submodule): `arch/arm/src/stm32h7/stm32h7x3xx_rcc.c`, `arch/arm/src/stm32/stm32f10xxx_rcc.c`, `arch/arm/src/stm32/stm32_rcc.c`
- Spec rev 0.38: DEC-015, DEC-017, DEC-022, DEC-044, DEC-045, OPEN-028, SAF-001
