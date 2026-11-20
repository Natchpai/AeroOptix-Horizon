# To Do

**Updated:** 2026-11-20
**Status:** Personal to-do list for the human owner, from reviews. Not a requirement, decision or verification record.

The specification and the execution checklist stay the source of truth; each item points to their IDs. `what-next.md` keeps the zone-by-zone reminder list. Tick an item here when it is done, then ask Claude to record it (`/progress-update light`). Done items are removed when the list is cleaned; they stay in Git history and the spec.

Format: severity | reference / net | evidence label | what is wrong | what to do.

Sources: `sch-review` of `conn-actuator` and `conn-peripherals` (2026-11-19, commit `10a0782`; spec 4.2 "Schematic review"), the RC IN drawing (15:03 to 15:25 saves; spec OPEN-034 item 6) and a team pre-layout review of commit `2356489` (2026-11-19, kicad-cli 10.0.7; its ERC, field and pin-trace results are the team's, `NOT_VERIFIED` here). Datasheet and DS-009 checks by Claude (2026-11-19, spec 0.63: CMP-010, CMP-011, OPEN-021, OPEN-023, OPEN-028). References follow the 2026-11-19 16:03 save. Cleaned 2026-11-19: done items removed. Team review notes from Jakarin (`hardware/message.md`, dated 2026-11-20, commit `5ea77f9`): first-pass review of the MCU, sensor and USB sheets and the shared NRST finding; their results are the team's, `NOT_VERIFIED` here unless marked. Updated 2026-11-20 for commit `f40784c` (spec 0.67; `kicad-cli` netlist and preflight by Claude). Cleaned 2026-11-20: done items removed (D706 buzzer channel, C803 MFR field, D701 to D706 Datasheet field, oscillator LCSC codes; then CN706 pin order, DEC-072, and the 100 kΩ PWM pull-down, DEC-073). Updated again for the 2026-11-20 12:36 save (not committed; spec OPEN-039), and for the 12:56 and 13:01 saves (TP605 linked, NRST split with D201 and D301; spec OPEN-026, OPEN-039). Cleaned again 2026-11-20 for the 13:37 save (spec 0.68: DEC-074 to DEC-079 recorded; the human owner's KiCad ERC at 13:37 gives 0 errors, 0 warnings, `ERC.rpt` not committed). `sch-review` of `mcu-main-fc` and `mcu-io` by Claude (2026-11-20, commit `6b01a14`, KiCad closed): `sch-inspect` local-net on U201 and U301 (all 148 pins connected), `kicad-cli` netlist, NotebookLM (DS12110 Rev 11, AN4879, DocID16455 Rev 9, RM0041) and PX4 v1.16.2 source; a targeted review, not a PASS.

## MAJOR

None open. (The `sch-review` of the sensor and USB sheets on 2026-11-20 raised IST8310 RSTN; it has an internal pull-up, so it is not a defect.) (The PA9 VBUS MAJOR from the 2026-11-20 `sch-review` is fixed in the 14:21 save, DEC-080.)

## MINOR

None open. (The ICM-45686 and ICP-20100 land patterns are accepted without the TDK app notes, DEC-086.)

## INFO

None open.

Closed 2026-11-20 (human owner's answers): LED Datasheet fields (filled), Q701 diode (DEC-087), PA12 pull-down (DEC-088), U302 margins (DEC-089), D807 at 6 V (DEC-090), U303 and U601 pin maps (DEC-091), capacitor `Rate` fields (filled), software notes (moved to `AO-HORIZON_SW_NOTES_EN.md`), layout and silkscreen notes (checklist P3-002, P3-007), `+6V` bulk (OPEN-021), servo ADC during spikes (OPEN-033 closed), ICP-20100 power-up (P4-015), library audit (P3-007).

## Not checked yet (need data)

None open. Closed 2026-11-20: CN101 pin order (confirmed by the human owner), servo plug rating and clamp tolerance (DEC-093), SiK V3 and GPS V1 pinouts (OPEN-023, DEC-092).
