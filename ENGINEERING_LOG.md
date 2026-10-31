# Engineering Log

## 2026-11-01 : 5 V input power mux (TPS2121)

**Context:** The TPS259251DRC eFuse on `power_supplies.kicad_sch` was replaced by a TI TPS2121 power mux that joins the PM02D 5 V (IN1) and USB VBUS (IN2); limit, priority and switchover set.

**Decisions:**
- [ACCEPTED] TPS2121 power mux replaces the eFuse (DEC-029); its reverse blocking stops USB back-feed.
- [ACCEPTED] Current limit 1.5 A, RILM 80.6 kΩ (DEC-030); TI gives 1.0 to 2.0 A.
- [ACCEPTED] PM02D priority through a PR1 divider (DEC-031), now 12.4 kΩ / 5 kΩ.
- [ACCEPTED] XCOMP fast switchover: CP2 16.5 kΩ / 5 kΩ from VBUS; the 16.5 kΩ is a DNP option for VREF mode (DEC-032).

**Findings / Open Items:**
- R105 is marked DNP, so the default build is VREF mode (100 µs); confirm the default (OPEN-024, owner: human).
- XCOMP switch point 4.39 V worst case, 0.11 V below 4.5 V before resistor tolerance (`ESTIMATED`); use 1 % resistors.
- ERC not run; 2 unannotated DNP diodes; VBUS has no source until the USB sheet exists (P2-019).

**References:** `power_supplies.kicad_sch` U101, R101 to R109; spec rev 0.21; `AO-HORIZON_POWER_MUX_NOTES_EN.md`.
