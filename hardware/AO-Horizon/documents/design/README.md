# Design Documents

The specification is the requirements source of truth. The other records point to its IDs instead of repeating them.

Status: `live` records are kept up to date; `closed, historical` records are answered team exchanges, kept as sent; `snapshot` records hold dated values that are not refreshed.

| File | Status | Content |
| ---- | ------ | ------- |
| `AO-HORIZON_SPEC_EN.md` | live | Hardware requirements, decisions (DEC-xxx) and open items (OPEN-xxx). |
| `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | live | P0 to P4 work plan and evidence tracker. |
| `AO-HORIZON_IMU_SELECTION_EN.md` | live | ICM-45686 selection, key data and sourcing (DEC-008, DEC-009, DEC-043). |
| `AO-HORIZON_BARO_MAG_SELECTION_EN.md` | live | ICP-20100, BMP581 (BMP384 fallback) and IST8310 selection (BMM150 replaced, BMP390 removed): key data and sourcing (DEC-010, DEC-011, DEC-043, OPEN-019). |
| `AO-HORIZON_POWER_BUDGET_EN.md` | live | Draft rail loads, tolerances, brownout and protection needs (P0-017). |
| `AO-HORIZON_PIN_ALLOCATION_EN.md` | live | Draft STM32H743 and STM32F100 pin allocation (P1). |
| `AO-HORIZON_POWER_MUX_NOTES_EN.md` | live | TPS2121 power mux: the four modes and how to calculate the PR1, CP2, OV, ILIM and SS parts, with the values as drawn (DEC-029 to DEC-034). Design note, not a record. |
| `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` | live | Open integration questions for the team (P0-022): ESC (D13), parts and team tests. Earlier answers are in the spec (DEC-019 to DEC-023, MEC-002 to MEC-004) and in Git history. |
| `AO-HORIZON_SW_CLOCK_NOTE_EN.md` | live | Note to the software team: HSE bypass for the CMOS oscillators in the H743 board config and bootloader and a custom px4io build (DEC-044, DEC-045, P1-017), with the PX4 v1.16.2 source evidence and questions. |
| `AO-HORIZON_H7_MCU_SOURCING_EN.md` | snapshot | STM32H743VI price and stock, 2026-10-16. Refresh before buying. |
| `AO-HORIZON_PINMAP_REVIEW_EN.md` | closed, historical | H743 and IO MCU pinmap review 0.3, answered by the software team on 2026-10-24 (0.2 answers kept). Current pins are in the pin allocation record and the spec. |
| `AO-HORIZON_PINMAP_DECISIONS_EN.md` | closed, historical | Spec changes, team decisions and software answers after pinmap review 0.2, answered on 2026-10-24. Later decisions (DEC-017, DEC-044, DEC-045) change its S7 clock answer. |
| `what-next.md` | live | Personal reminder list of next steps. Points to spec and checklist IDs; not a record. |
