# Team Messages

## 2026-11-20 · Jakarin → Natchpai · Review notes

Checked on commit `5ea77f9` (the schematic is the same as `3661bb1`). These are review notes, not design decisions; the spec still owns `DEC-xxx` and `OPEN-xxx`.

### 1. ERC

- `kicad-cli` 10.0.7, all severities, on `3661bb1`: 0 violations.
- Netlist diff against `bb3c29c`: only D706 channel 4, D707 and D708 changed, as intended (DEC-071). 223 parts, all with footprint, MFR, MFR.P/N and LCSC.

### 2. MAJOR: shared NRST (DEC-046, OPEN-026)

STM32 internal resets (IWDG, software reset) drive NRST low for at least 20 µs (ST reference manuals of other STM32 families; the F1 and H7 manuals were not opened). On the shared `RESET_B` net, an F100 reset (px4io IWDG, or the reboot after a px4io update) would also reset the H743, in flight too.

Proposal, as on Pixhawk (FMU and IO resets are separate):

- Split `RESET_B`. H743 NRST keeps C209 and the B901 button. F100 NRST keeps only C308.
- No new parts. The F100 is reset by power, by SWD on CN603, or by PX4 over the px4io link (px4io update).
- If one button must still reset both MCUs: a dual Schottky (BAT54C type, common cathode on B901) to the two separate NRST nets.

### 3. First-pass review of the MCU, sensor and USB sheets (P2-009)

OK: H743 and F100 decoupling, VDDA filters, VCAP 2 × 2.2 µF, BOOT0/BOOT1 pull-downs, HSE bypass inputs, H7↔F1 UART cross with 22 Ω, SPI1/SPI4 IMU direction and INT lines, I2C2 pull-ups, sensor straps (0x63, 0x46, 0x0C), IST8310 C1 4.7 µF, USB D+/D−, CC 5.1 kΩ, USBLC6-2SC6, VBUS sense, debug connectors.

MINOR:

1. microSD CMD and DAT0 to DAT3 have no pull-ups (P2-022). Add 10 kΩ to 100 kΩ to `+3V3`, or confirm that the firmware enables the internal pull-ups.
2. Spec 3.5 says the px4io LEDs on F100 PB14, PB15 and PA11 are fitted, and that PA10 and PB11 have weak pull-ups. Neither is in the schematic (the pins have no-connect flags). Add them, or update the spec.
3. R208 (microSD DET pull-up) has no MCU connection (DEC-018, no card detect). Remove it, or keep it on purpose.
4. Spec 4.2 (peripheral connectors row) still has one stale "R705 and R706 DNP"; both are fitted (OPEN-038).

Not checked by me: sensor decoupling values against each datasheet, IST8310 VPP pin, power-up order (OPEN-011).

### 4. Still open before layout (already in `todo.md`)

- CN706 RC IN: 1x3 2.54 mm right-angle header, pin 1 PPM, pin 2 `+5V`, pin 3 `GND` (P2-023).
- Weak pull-downs on all 15 PWM lines (P2-018, OPEN-031).
- Spare output pad row SPARE1 to SPARE3 + GND (DEC-069).
- ICP-20100 and ICM-45686 footprints (P2-012).
- I2C4 pull-up value: 5.1 kΩ against the DS-009 1.5 kΩ (OPEN-023).

### 5. Answer

- Passive size: keep 0402 as drawn. We will update the report, which still says 0603.
