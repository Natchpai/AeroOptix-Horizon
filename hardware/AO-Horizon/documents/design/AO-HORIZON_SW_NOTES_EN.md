# AeroOptix-Horizon: Board Notes for the Software Team

**Revision:** 0.2
**Updated:** 2026-11-20
**From:** Hardware
**To:** Software team
**Status:** Firmware notes from the schematic reviews of 2026-11-20. Not a verification record. The board is in schematic capture; nothing is built yet. The HSE bypass request is in [AO-HORIZON_SW_CLOCK_NOTE_EN.md](AO-HORIZON_SW_CLOCK_NOTE_EN.md).
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md) rev 0.72 (IF-047, DEC-080, DEC-083, DEC-088, DEC-092, 4.2)

Each note says what the board does, what we ask from the firmware, and where the evidence is. "Needed" means the board will not work as intended without it; "preferred" means it works either way.

## 1. Notes

| # | Board item | As drawn | Firmware ask | Level | Evidence |
|---|---|---|---|---|---|
| SW-1 | H743 board LEDs D901 to D903 (IF-047, DEC-067) | PE2 red, PE3 blue, PE4 green, active low, anodes to `+3V3` through 220 Ω | `px4/fmu-v6c` drives only red (PD10, `BOARD_OVERLOAD_LED`) and blue (PD11, `BOARD_ARMED_STATE_LED`). Name PE2 to PE4 in the board config, add a green LED entry and choose what it shows. Silkscreen: D901 `ERR`, D902 `STAT`, D903 `ARM`. | Needed (green stays off otherwise) | PX4 v1.16.2 `px4/fmu-v6c` `board_config.h`, `led.c` (`VERIFIED`); spec IF-047 |
| SW-2 | H743 PA9 VBUS sense (DEC-080) | `VBUS` through R603 5k1 / R604 10k to PA9, 100 nF (C216) | Read PA9 as a plain input with no pull-down and `VBDEN` off. With the fmu-v6c `GPIO_PULLDOWN`, PA9 still reads high (2.81 to 3.28 V, `ESTIMATED`). | Preferred | DS12110 Rev 11 Table 11 and Table 50; fmu-v6c `board_config.h` line 202 (`VERIFIED`) |
| SW-3 | IST8310 magnetometer U503 (DEC-011) | RSTN and DRDY not connected; AVDD on `+3V3A`, DVDD on `+3V3` | Soft-reset the IST8310 at driver start. A new power-on reset needs AVDD below 0.1 V for at least 10 ms, so a short USB replug may leave the old register state. The datasheet also asks for PDCTNL (0x42) = 0xC0 and, for low noise, AVGCNTL (0x41) = 0x24. | Needed (soft reset) | IST8310 datasheet V1.2 §3.1 and V1.8 §3.5 via NotebookLM (`VERIFIED` for the register values; the 10 ms re-POR from the `sch-review` subagent) |
| SW-4 | BMP581 INT, U502 pin 7 (DEC-083) | INT through R512 10 kΩ to `GND` | Keep `INT_CONFIG.int_en` off (the reset default). Do not turn on the interrupt output. | Needed | BMP581 DS004-13 §6.2 via NotebookLM (`VERIFIED`) |
| SW-5 | F100 PA12 RSSI input (DEC-088) | `F1_PA12` with R315 10 kΩ to `GND`; nothing else connected | px4io sets PA12 as a timer input for PWM RSSI. Keep PWM RSSI off; with the pull-down the input reads low. | Preferred | PX4 v1.16.2 io-v2 `board_config.h` line 130 (`VERIFIED`) |
| SW-6 | ICP-20100 INT, U501 pin 7 (DEC-083) | Not connected | None needed: INT is open-drain with an internal pull-up. Leave its interrupt sources masked. | Info | DS-000416 §8 via NotebookLM (`VERIFIED`) |
| SW-7 | SiK V3 telemetry radios on TELEM1 and TELEM2, CN701 and CN702 (DEC-092) | TX, RX, `+5V`, `GND` only; CTS and RTS not connected | Keep hardware flow control off, on the radio (SiK `RTSCTS` setting) and on the H743 serial port. | Needed | Holybro SiK V3 pinout image (radio has CTS and RTS pins); the SiK default is `ASSUMED` |

## 2. Not for firmware

- ICM-45686 RESV (pin 7) is not connected on U401 and U402 (DEC-082), so the `pads_pin7_pe_trim_d2a` write in DS-000489 Table 10 is not needed.
- The ICP-20100 power-up order (VDDIO before VDD by about 0.5 ms) is accepted for a bench check (DEC-085, P4-015). If the barometer does not answer after a cold start, a soft reset is the first thing to try.
