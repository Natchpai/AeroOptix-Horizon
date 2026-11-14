# AeroOptix-Horizon: Execution Checklist

**Revision:** 0.36
**Updated:** 2026-11-14
**Status:** Active execution tracker; not an approval or verification record
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md) rev 0.40

Use the specification for confirmed requirements and decisions. This checklist records the sequence of work and the evidence needed to close each gate. Diagram content is reference material. User-confirmed requirements take precedence. All sensor parts are chosen (DEC-008, DEC-010, DEC-011); their lifecycle and sourcing risks are open.

**Conventions**

- Task status: `OPEN`, `IN_PROGRESS`, `BLOCKED BY <ID>`, `DEFERRED`, `DONE`, `N/A`.
- `DONE` needs a stated completion and a named or linked evidence record in the last column.
- A candidate, a count, a file, or an ERC/DRC pass is not evidence by itself. A `DONE` task does not mean the implementation was measured or verified.
- Gates are work stages. They are not the project phase. The human declares the project phase and closes each gate.
- `Req` holds spec IDs. Values stay in the specification. `TBD` means to be decided. Owner `Human` means the human engineer decides or approves.

## Gate summary

| Gate | Name | Exit criterion | Status |
| ---- |---|---|---|
| P0   | Requirements | No unresolved requirement prevents MCU-resource, bus, connector, or power-architecture allocation. Sensor-specific choices stay TBD and block only the allocations they affect. | OPEN |
| P1   | Allocation | The mapping has actual pins and alternate functions, passes documented resource checks, and has review evidence. It may then be called `ALLOCATED`. It is not automatically `VERIFIED`. | OPEN |
| P2   | Schematic | Hardware schematic review is closed, electrical interfaces and reserved resources are documented, and no unresolved hardware blocker affects bring-up. Firmware ownership, PX4 target, bootloader, and software protocol details may stay deferred. | OPEN |
| P3   | PCB and release package | PCB, BOM, fabrication data, and release manifest are reviewed and approved by the Human engineering owner. | OPEN |
| P4   | Bring-up | Repeatable bench evidence exists, and every remaining issue has an owner and a defined disposition. | OPEN |

## P0: Requirements

Groups: P0.1 scope and operating intent (P0-001 to P0-003). P0.2 MCU and safety boundary (P0-004 to P0-007). P0.3 sensors (P0-008 to P0-011). P0.4 interfaces, power, actuators, and envelope (P0-012 to P0-015). Later tasks: P0-016 to P0-022.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P0-001 | Define the flight-controller role and system boundary. Scope confirmed on 2026-10-13. | SYS-001, SYS-002 | Human | DONE | User confirmation, 2026-10-13. DEC-013 (Pixhawk 6C and 6X as references, 2026-10-24). |
| P0-002 | Record PX4 target/version and supported modes as Software-owned deferred work. Not needed to proceed with hardware. | DEC-004 | Human | DONE | DEC-004 |
| P0-003 | Define first-revision scope. In scope: H743 main control, F100 auxiliary I/O/PWM/safety, and the stated external interfaces. Deferred: PX4, bootloader, QGC, and detailed software behavior. | SYS-001, DEC-004 | Human | DONE | DEC-004; spec 1.2 |
| P0-004 | Confirm STM32H743VIT6 as the main MCU. Implementation not verified. | MCU-001, CMP-001, FUN-001 | Human | DONE | DEC-001 |
| P0-005 | Confirm the IO MCU (px4io: servo PWM, safety switch, servo failsafe): STM32F100C8T6B, replacing the STM32F103C8T6 on 2026-10-24. Implementation not verified. | MCU-002, CMP-002 | Human | DONE | DEC-002, DEC-017 |
| P0-006 | Reserve H743↔F100 USART. Instance, rate and protocol set by DEC-015 (USART6 ↔ USART2, 1.5 Mb/s, px4io). Test access remains for P2. | IF-001, IF-024 | Human | DONE | DEC-003, DEC-015 |
| P0-007 | Record the H743-failure behavior: servo failsafe on the F100 and motor stop when DShot frames stop (DEC-016, replaces "immediate landing"). Hardware preserves the physical path and test access. | SAF-001, FUN-004, SAF-015 | Human | DONE | DEC-005, DEC-016 |
| P0-008 | Select two IMU MFR/MPNs. Team confirmed 2 × ICM-45686 on 2026-10-18. SPI, supply range and sourcing checks stay open in the selection record. | SEN-001, CMP-003 | Team | DONE | DEC-008; [AO-HORIZON_IMU_SELECTION_EN.md](AO-HORIZON_IMU_SELECTION_EN.md) |
| P0-009 | Select two barometer MFR/MPNs. Done 2026-10-24: ICP-20100 + BMP581, BMP384 fallback (DEC-010). ICP-20100 EOL and the BMP384 fit (OPEN-019) stay open. | SEN-002, CMP-004 | Team | DONE | DEC-010; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-010 | Decide magnetometer MFR/MPN and allocation. Done 2026-10-24: 1 × iSentek IST8310 onboard, no second magnetometer (DEC-011). | SEN-003, CMP-005 | Team | DONE | DEC-011; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-011 | Define sensor rates, DRDY/interrupt needs, calibration, and redundancy. | SEN-001, SEN-002, SEN-003 | Human | OPEN | Sensor requirement record |
| P0-012 | Confirm logical H743/F100 external interface allocations (DEC-014, DEC-018). Electrical implementation unverified. | IF-010 to IF-024, IF-040 to IF-048 | Human | DONE | DEC-014, DEC-018 |
| P0-013 | Confirm board and servo power requirements. Servo current passes through the board on an on-board 6 V bus with a board-mount XT30 UBEC input (DEC-019). Protection, transients, distribution, and component choice are open (see P0-017). | PWR-001, PWR-002, PWR-010, PWR-011 | Human | DONE | DEC-007, DEC-019 |
| P0-014 | Confirm logical F100 functions: 8 servo outputs on the px4io-v2 timers, safety switch and LED, servo rail sense; ESCs on the H743 (DEC-014, DEC-016, DEC-018). Electrical implementation unverified. | IF-030 to IF-038, IF-049 to IF-051, FUN-003 | Human | DONE | DEC-014, DEC-016, DEC-018 |
| P0-015 | Confirm maximum PCB envelope. Shape, mounting, connector orientation, and environment open for P3. | MEC-001 | Human | DONE | DEC-006 |
| P0-016 | Select non-MCU parts: regulators, protection, connectors, PDB/UBEC, and interface ICs. Chosen: TPS62142RGTR buck (DEC-012), TPS2121 power mux (DEC-029, DEC-030), TPS73533DRBR `+3V3A` LDO (DEC-027). Passive MFR and MFR.P/N: the human owner chooses them later. The rest are open. | CMP-006 to CMP-009, OPEN-010, OPEN-011 | Human | IN_PROGRESS | DEC-012, DEC-027, DEC-029, DEC-030; part selection record for the remaining parts |
| P0-017 | Define power budget, rail tolerances, brownout thresholds, and 5 V and 6 V protection and transient requirements. | PWR-012 to PWR-014, SAF-012 to SAF-014, OPEN-006, OPEN-007 | Hardware | OPEN | Power budget table and protection requirement record. Draft: [AO-HORIZON_POWER_BUDGET_EN.md](AO-HORIZON_POWER_BUDGET_EN.md) |
| P0-018 | Define environmental limits: operating and storage temperature, vibration and shock, humidity, ingress, altitude, maintenance. | ENV-001 to ENV-004 | TBD | OPEN | Decision record with a verification method per limit |
| P0-019 | Get team decisions on the spec rows that the pinmap review 0.2 answers change, then update the spec. Done 2026-10-24: applied in spec rev 0.11. | OPEN-016, OPEN-015, SAF-001, FUN-002, FUN-003 | Team | DONE | Returned decisions file rev 0.2; spec change note 0.11; commit `c9fe9ed` |
| P0-020 | Get the team's reply to pinmap review 0.3 (`NEW` rows and questions Q20 to Q22). Done 2026-10-24: all answered and applied in the spec and the pin allocation. | OPEN-001 | Team | DONE | [AO-HORIZON_PINMAP_REVIEW_EN.md](AO-HORIZON_PINMAP_REVIEW_EN.md) rev 0.3 (answered) |
| P0-021 | Get the team's answers to the integration questions (D8 to D11, external devices and connectors, S8 to S10). Done 2026-10-24 (DEC-019 to DEC-022). Remaining inputs: P0-022. | PWR-002, PWR-011, MEC-002 to MEC-004, ENV-001 to ENV-004, IF-010 to IF-022, IF-040 to IF-049, OPEN-007, OPEN-009 | Team | DONE | [AO-HORIZON_INTEGRATION_QUESTIONS_EN.md](AO-HORIZON_INTEGRATION_QUESTIONS_EN.md) rev 0.2; spec change note 0.13 |
| P0-022 | Get the remaining team inputs: D13 (the Skywalker 80A V2 ESCs look PWM-only; how the motors stop on an H743 hang), ELRS receiver model, MS4525DO version, chip and plug on the PM02D, UBEC model, positions of the Kingmax C507 and DS-843MG servos, stall current of all servos (bench test). | OPEN-007, OPEN-017, IF-010, IF-014, IF-048, PWR-011 | Team | OPEN | Team reply to [AO-HORIZON_INTEGRATION_QUESTIONS_EN.md](AO-HORIZON_INTEGRATION_QUESTIONS_EN.md) rev 0.4 (D13, parts table, tests) |

## P1: Allocation

Any candidate pin mapping stays labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete. P1-006 to P1-008 are proposed allocations, not confirmed.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P1-001 | Assign exact H743 pins and alternate functions for all confirmed and approved interfaces. Team answers applied (pinmap review 0.3, 2026-10-24); pins checked against ST pin data. Waits for the human review of the pin choices. | IF-010 to IF-024, IF-040 to IF-048, OPEN-001 | Hardware | IN_PROGRESS | Versioned MCU pin-allocation table: [AO-HORIZON_PIN_ALLOCATION_EN.md](AO-HORIZON_PIN_ALLOCATION_EN.md) rev 0.7; [AO-HORIZON_PINMAP_REVIEW_EN.md](AO-HORIZON_PINMAP_REVIEW_EN.md) rev 0.3 |
| P1-002 | Assign exact F100 pins and alternate functions for its approved role. px4io-v2 pins applied on the STM32F100C8T6B (same pins as the F103, pin allocation F-18). px4io LEDs fitted; PA10 and PB11 pulled up. | IF-030 to IF-037, IF-049 to IF-051, OPEN-001 | Hardware | IN_PROGRESS | As for P1-001 |
| P1-003 | Allocate both SPI IMUs: CS, DRDY, bus ownership, DMA. No IMU reset line; reset is by software (DEC-009). IMU pin 9 (INT2/CLKIN) not used (team, Q16). Drawn: SPI and INT1 of both IMUs reach the H743 (INT1 on PC4 and PE15; spec 4.2 "Schematic state"). | SEN-001 | Hardware | IN_PROGRESS | SPI allocation and timing review |
| P1-004 | Allocate both I2C barometers: addresses, pull-ups, recovery, bus ownership. Addresses on I2C2 per SEN-002 (BMP384 fallback: OPEN-019). Open: pull-ups and recovery. | SEN-002 | Hardware | OPEN | I2C address/bus review |
| P1-005 | Allocate the I2C magnetometer (IST8310, DEC-011): address (CAD0/CAD1), pull-ups, DRDY and RSTN use, recovery, placement constraints. Team: DRDY and RSTN not connected (Q11). Address decided 2026-11-14: 0x0C, as strapped on U503 (DEC-047); PX4 start at 0x0C is P1-018. | SEN-003, DEC-047, P1-018 | Hardware | IN_PROGRESS | I2C and magnetic-placement review |
| P1-006 | Allocate USB FS, VBUS sensing, ESD/protection, connector, and reset support for H743 flashing (proposed). Drawn on `conn-usb-debug` (spec 4.2 "Schematic state"): USB-C receptacle, USBLC6-2SC6, CC resistors, VBUS to PA9 through 0 Ω with no divider (pin allocation F-06). Parts not decided (OPEN-010). | IF-022 | Hardware | IN_PROGRESS | USB interface review and schematic net list |
| P1-007 | Allocate selectable H743 BOOT0 and define its default/reset behavior (proposed). | FUN-006, TST-003 | Hardware | OPEN | Boot-state table and circuit review |
| P1-008 | Allocate SWD access for both MCUs. H743: Pixhawk Debug Mini 6-pin JST-SH (console + SWD) plus an NRST pad. F100: SWD, NRST and console TX on pads, bench only (DEC-018). As drawn: SWD only on both MCUs, no console, no NRST, no footprints (OPEN-029). | FUN-005, IF-023, IF-045, IF-051, TST-001, TST-002, OPEN-029 | Hardware | IN_PROGRESS | Debug-access review; pinout from PX4 docs (DS-009 not read) |
| P1-009 | Check alternate-function conflicts across every assigned pin. | OPEN-001, OPEN-003 | Hardware | OPEN | Conflict report with no unresolved critical conflicts |
| P1-010 | Check DMA, interrupt, timer/PWM, clock, and priority conflicts. | OPEN-003 | Hardware | OPEN | Resource matrix and resolution record |
| P1-011 | Check voltage domains, IO levels, pull states, reset states, and boot-time behavior. Includes the PWM pull-down value with bidirectional DShot on the motor lines (OPEN-018). | OPEN-018 | Hardware | OPEN | Electrical compatibility review |
| P1-012 | Review package pin availability, reserved pins, unused pins, and ERC/DRC implications. | OPEN-001 | Hardware | OPEN | Package/resource review |
| P1-013 | Record mapping revision, reviewer, date, conflicts, resolutions, and remaining obligations. | OPEN-001 | TBD | OPEN | Signed or attributable review record |
| P1-014 | Define clock sources, reset topology, watchdog use, and F100 boot behavior. Frequencies per DEC-017 (no LSE); CMOS oscillators, no crystals or load capacitors (DEC-044); HSE bypass in firmware (DEC-045, P1-017); F100 BOOT0 and BOOT1 pulled down; watchdogs per spec 4.4. Reset decided 2026-11-14: one shared NRST net with one reset button (DEC-046). Oscillator parts decided (DEC-048). Open: draw the reset button and check the ST internal-reset behavior (OPEN-026); oscillator data (OPEN-028). | Spec 4.4, DEC-017, DEC-044, DEC-045, DEC-046, DEC-048, OPEN-026, OPEN-028 | Hardware | IN_PROGRESS | Clock/reset/boot decision record |
| P1-015 | Check the BMP384 fallback against the BMP581 footprint, pinout and I2C address. | OPEN-019, CMP-004 | Hardware | OPEN | Datasheet comparison record |
| P1-016 | Pick the ESC current-sense ADC pin and the ESC telemetry UART RX. Closed 2026-10-24: dropped, no ESC current sense or telemetry (IF-052, IF-053 removed, OPEN-022 closed). | OPEN-022, DEC-023 | Hardware | N/A | Spec rev 0.14 change note |
| P1-017 | Set HSE bypass in firmware for the CMOS oscillators (DEC-044, DEC-045): define `STM32_HSEBYP_ENABLE` in the H743 board config (`board.h`) and build the H743 bootloader from it; build px4io for the F100 with HSEBYP set and package it in place of the stock image (DEC-022). Note sent to the team: `AO-HORIZON_SW_CLOCK_NOTE_EN.md` rev 0.1. | DEC-017, DEC-022, DEC-044, DEC-045, OPEN-028 | Software | OPEN | Board config and px4io build in the firmware repo; bench check that both MCUs run from HSE (P4) |
| P1-018 | Start the IST8310 at I2C address 0x0C in the PX4 board start script (DEC-047; PX4 default is 0x0E). Check that the PX4 `ist8310` driver accepts the address. | DEC-047, SEN-003 | Software | OPEN | Board start script in the firmware repo; magnetometer found on the bench (P4) |

## P2: Schematic

Firmware tasks P2-005 to P2-007 do not block the hardware release.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P2-001 | Create the schematic from the P1 allocation. |  | Hardware | BLOCKED BY P1 | Versioned native schematic |
| P2-002 | Implement USB FS, BOOT0, SWD, reset, power, and protection circuits. | IF-022, IF-023, FUN-005, FUN-006, SAF-014 | Hardware | BLOCKED BY P1 | Schematic review evidence |
| P2-003 | Implement sensor buses, addresses, CS/DRDY, pull-ups, and recovery provisions. | SEN-001, SEN-002, SEN-003 | Hardware | BLOCKED BY P0, P1 | Sensor interface review |
| P2-004 | Define hardware net names and connector pinout. Reserve resources for later firmware mapping. | IF-010 to IF-024 | Hardware | BLOCKED BY P0, P1 | Hardware net/connector cross-check |
| P2-005 | Create the PX4 board configuration and bootloader plan. | DEC-004 | Software | DEFERRED | Later versioned firmware configuration and build/flash procedure. Not a hardware release blocker. |
| P2-006 | Define the H743 USB FS/QGC flashing workflow for both MCU firmware images. | DEC-004 | Software | DEFERRED | Later reproducible software procedure and test record. Hardware shall preserve the physical path and access. |
| P2-007 | Define H743↔F100 firmware ownership, protocol version, startup, timeout, and fault behavior. | IF-001, SAF-010, SAF-011, OPEN-008 | Software | DEFERRED | Later versioned firmware interface contract. Hardware shall document the reserved electrical path before schematic freeze. |
| P2-008 | Run ERC and resolve or disposition all relevant findings. |  | TBD | OPEN | ERC output and issue disposition |
| P2-009 | Complete line-by-line schematic review. |  | TBD | OPEN | Review checklist with reviewer and evidence links |
| P2-010 | Complete the spec 4.7 calculations: board input current, servo rail current, rail tolerance, thermal margin, and safety response timing. | Spec 4.7, PWR-012 to PWR-014 | Hardware | OPEN | Calculation records with margins |
| P2-011 | Capture the power sheet (`power_supplies.kicad_sch`). Done 2026-10-31 (human owner). Changed after that for the TPS2121 power mux (DEC-029, P2-020). Findings: P2-019; resistor fields: P2-021. | DEC-012, DEC-029, OPEN-011 | Hardware | DONE | Human statement 2026-10-31; saved `power_supplies.kicad_sch`; spec 4.3 "Schematic state" |
| P2-012 | Check the sensor footprints against the datasheet drawings and app notes: pad geometry, land pattern, pin 1 corner, 3D model. Pin maps already match the datasheet tables. IST8310 uses the stock `LGA-16_3x3mm_P0.5mm` footprint (fit `ESTIMATED`, no land pattern in the datasheet). Bosch LGA-10 pads follow the BMP581 land pattern (DS004-13 Fig. 32), read from an image; needs a human check. See spec 4.6 "Library state". | OPEN-013, CMP-003 to CMP-005 | Human | IN_PROGRESS | Per-part review record naming the datasheet figure or app note used |
| P2-013 | Pick the weak pull-down and any series resistor on the PWM lines so bidirectional DShot still works on the motor lines. | OPEN-018, IF-040 to IF-043 | Hardware | OPEN | Calculation or reference design note, then the P4-011 bench result |
| P2-014 | Add the STM32F100C8T6B to the project library from stock KiCad `MCU_ST_STM32F1:STM32F100C8Tx` (`kicad-part-start`, then `kicad-link-audit`), and change the IO MCU text in `block_diagram.kicad_sch` from STM32F103C8T6. Added 2026-10-24. | MCU-002, CMP-002 | Hardware | OPEN | Library audit record; approved schematic change |
| P2-015 | Check the external connector pinouts against the Pixhawk connector standard (DS-009): Telemetry 1 and 2, GPS1 10-pin (3.3 V and buzzer pins), airspeed, TF-Luna; the PM02D connector CN101 (DEC-042) against the PM02D cable; and whether PD12 and PD13 take 5 V I2C pull-ups. | OPEN-023, IF-010 to IF-015, IF-046, IF-048 | Hardware | OPEN | Pinout record citing DS-009 and the PM02D page |
| P2-016 | Design the on-board servo bus (DEC-019): check the board-mount XT30 UBEC input against PWR-011, size the 6 V and servo GND copper, pick where servo GND joins logic GND, and add bulk capacitance. Needs the stall current (P0-022). | OPEN-021, OPEN-007, DEC-019, IF-030 to IF-037, IF-050 | Hardware | OPEN | Calculation record (XT30 and copper current) and header part choice |
| P2-017 | Wire the 5 V input eFuse and set its parts from TI data. Done 2026-10-31 for the TPS259251DRC (DEC-026); superseded 2026-11-01 when the eFuse was removed for the TPS2121 power mux (DEC-029, P2-020). | DEC-026, OPEN-012, OPEN-006, PWR-010 | Hardware | DONE | Spec CMP-008 and 4.7 "5 V eFuse settings" (rev 0.19); human statement 2026-10-31 closing the power section |
| P2-018 | Draw the 4 ESC connectors: 3-pin headers with the + pin removed (IF-040 to IF-043). | IF-040 to IF-043 | Hardware | OPEN | Saved schematic |
| P2-019 | Resolve the power-sheet findings (spec 4.3), then run ERC on the sheet and ask for a `sch-review`. Done 2026-11-03 (closed by the human owner): findings fixed; ERC run by the human owner, only the hierarchical sheet pins `3V3_PG`, `PM02_SCL` and `PM02_SDA` left; `sch-review` found no defect (spec 4.3). Decisions on the way: DEC-035 to DEC-041. Not a finding: the two DNP diodes D105 and D106 are ESD parts parked for another sheet (human owner, 2026-11-02). Left over: resistor part fields (P2-021); the temporary `PWR_FLAG` on `VBUS` (P1-006, P2-022); ST low level (P4-012). | OPEN-011, OPEN-023, OPEN-025, DEC-028, DEC-029 | Hardware | DONE | Saved schematic, commit `304de41`; ERC run by the human owner, only hierarchical sheet pins left; `sch-review` in spec 4.3 |
| P2-020 | Set the TPS2121 power mux parts from TI data (DEC-029). Wired and checked against TI SLVSEA3F (spec CMP-008 and 4.7): current limit (DEC-030), PM02D priority and XCOMP switchover (DEC-031 to DEC-034), OV dividers (DEC-036, PWR-015). The 10 nF soft-start capacitor C108 is below the TI Table 9-1 range (extrapolated). OPEN-024 closed. Open: input capacitance for the PM02D cable (see DEC-037, P4-013); bench test of the switchover. | DEC-029, DEC-030, DEC-031, DEC-032, DEC-033, DEC-034, DEC-036, PWR-015, OPEN-006 | Hardware | IN_PROGRESS | Spec CMP-008 and 4.7 "5 V power mux settings"; bench switchover measurement |
| P2-021 | Fill MFR, MFR.P/N and LCSC on the power-sheet resistors R101 to R115, with 1 % parts in the PR1, CP2, OV and ST dividers (DEC-031 to DEC-036). The human owner chooses the parts. | P2-019, DEC-031 to DEC-036 | Hardware | OPEN | Saved schematic with filled fields |
| P2-022 | Finish the MCU, sensor and USB sheets (spec 4.2 "Schematic state"): annotate the passives on `mcu-main-fc`, `mcu-io` and `conn-usb-debug`; footprints and part fields for the new capacitors and the debug connector and pads; oscillator footprints and fields per DEC-048; microSD DET to an MCU pin, CMD and DAT pull-ups and ESD; C507 footprint; the reset button (DEC-046, OPEN-026) and debug pin set (OPEN-029, P1-008); run `/kicad-link-audit` for the new `0_Oscillator` library; remove the temporary `PWR_FLAG` on `VBUS` if ERC allows. Then run ERC and ask for a `sch-review`. | DEC-046, DEC-048, OPEN-026, OPEN-028, OPEN-029, P1-008, P1-014, SEN-001 to SEN-003, IF-022, IF-044 | Hardware | IN_PROGRESS | Saved, annotated schematic; ERC output; `sch-review` record |

## P3: PCB and fabrication release

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P3-001 | Confirm board envelope, mounting, connector placement, and service/debug access. | MEC-001 to MEC-004, OPEN-009 | Human | OPEN | Mechanical constraint review |
| P3-002 | Place IMUs, barometers, magnetometers, clock, power, USB, and debug interfaces by their constraints. | PCB-011, PCB-012, PCB-013 | TBD | BLOCKED BY P0, P2 | Placement review |
| P3-003 | Route power and return paths with documented current and noise assumptions. | PCB-010 | TBD | BLOCKED BY P0, P2 | Power/layout review |
| P3-004 | Route USB FS and high-sensitivity sensor/debug signals with appropriate layout review. | PCB-011, PCB-012 | TBD | BLOCKED BY P0, P2 | Signal/layout review |
| P3-005 | Run DRC and disposition all relevant findings. |  | TBD | OPEN | DRC output and issue disposition |
| P3-006 | Review thermal/current constraints and manufacturability. | MFG-001 to MFG-003 | TBD | OPEN | Manufacturing and thermal review |
| P3-007 | Confirm BOM, footprints, alternates, assembly notes, and test-point access. | MFG-002 to MFG-004, TST-001 to TST-007 | TBD | OPEN | Controlled BOM and assembly review |
| P3-008 | Create a hardware release package linked to schematic, PCB, BOM, and the deferred-firmware status. |  | TBD | OPEN | Hardware release manifest that records firmware integration as deferred |
| P3-009 | Obtain Human engineering-owner approval for fabrication release. |  | Human | OPEN | Explicit approval record |
| P3-010 | Define PCB fabrication parameters: layer count, stackup, copper weight, trace/space, hole/via, soldermask, finish. | PCB-001 to PCB-005, MFG-001 | TBD | OPEN | Parameter record confirmed by the fabricator |
| P3-011 | Route PWM/actuator outputs and the H743↔F100 USART with return path, drive, protection, voltage compatibility, and test access. | PCB-014, PCB-015 | TBD | BLOCKED BY P0, P2 | Layout review and electrical test |

## P4: Bring-up and validation

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P4-001 | Inspect the assembled board for shorts, assembly defects, polarity, and component identity. |  | TBD | OPEN | Inspection record |
| P4-002 | Verify power rails, sequencing, reset behavior, and current consumption before firmware loading. | PWR-001, PWR-002, TST-004, TST-005 | TBD | OPEN | Measured bring-up log |
| P4-003 | Verify SWD access for H743. | FUN-005, TST-001 | TBD | OPEN | Probe/session log |
| P4-004 | Verify SWD access for F100. | FUN-005, TST-002 | TBD | OPEN | Probe/session log |
| P4-005 | Verify the H743 USB FS hardware path, connector, protection, continuity, and relevant electrical behavior. | IF-022 | TBD | OPEN | Hardware inspection/measurement record. Host enumeration may stay deferred. |
| P4-006 | Verify firmware flashing through QGC for the approved workflow. | DEC-004 | Software | DEFERRED | Later reproducible software test record. Not a hardware release blocker. |
| P4-007 | Verify bootloader, PX4 startup, sensor detection, and calibration flow. | DEC-004 | Software | DEFERRED | Later firmware/console/test log. Not a hardware release blocker. |
| P4-008 | Verify the H743↔F100 physical link, electrical levels, continuity, and test access. Protocol behavior is deferred to Software. | IF-001, IF-024, TST-006 | Hardware, Software | OPEN | Hardware link test record and later software protocol test record |
| P4-009 | Verify actuator outputs, arming behavior, failsafe behavior, and fault handling. | SAF-001, SAF-010 to SAF-013, TST-007 | TBD | OPEN | Safety/actuator test record |
| P4-011 | Halt the H743 over SWD while armed: measure the servo failsafe time at the F100 and the motor stop time at the ESC. Check bidirectional DShot RPM feedback with the chosen pull-downs. | SAF-015, OPEN-017, OPEN-018 | Team + Hardware | OPEN | Bench test record with ESC model and firmware |
| P4-012 | On USB power (IN2), measure the U101 ST voltage and check that D103 is fully off, at room temperature and warm. On the PM02D, check that D103 is lit. | OPEN-025, DEC-035, DEC-036 | Hardware | OPEN | Bench measurement record |
| P4-013 | Plug in the PM02D with its real cable, with the board on USB and with it unpowered; scope `PM02_5V` and `+5V`. Check that the peak stays well below the tantalum rating (DEC-037), that `+5V` has no OV dropout, and that the tantalum shows no damage after repeated plugs. | DEC-037, DEC-036, PWR-010 | Hardware | OPEN | Bench measurement record with scope captures |
| P4-014 | With no PM02D, power the board from a USB-C port that meets DEC-038, with GPS, ELRS, TF-Luna and the airspeed sensor connected; check that `+5V` stays inside PWR-010 and the power mux does not reach its current limit. | DEC-038, IF-022, OPEN-006 | Hardware | OPEN | Bench measurement record |
| P4-015 | Scope `+3V3` and `+3V3A` at power-up from the PM02D and from USB: `+3V3A` starts after `+3V3`, its 10 % to 90 % ramp is 0.01 to 1 ms, and both IMUs answer WHO_AM_I after every cold start. | DEC-039, OPEN-011 | Hardware | OPEN | Bench measurement record with scope captures |
| P4-010 | Record hardware revision, firmware revision, test conditions, measurements, and deviations. |  | TBD | OPEN | Controlled bring-up report |

## Evidence and closure checklist

- [ ] `E-001` Every confirmed requirement has a source or decision record.
- [ ] `E-002` Every proposed design choice has a human owner and confirmation status.
- [ ] `E-003` Every TBD item has an owner, due point, or explicit deferred obligation.
- [ ] `E-004` Every verification claim links to a test, inspection, analysis, or review record.
- [ ] `E-005` No candidate mapping, count, report, or file-existence claim is treated as verification by itself.
- [ ] `E-006` Native schematic/PCB files and firmware configuration are the source of truth for implementation.
- [ ] `E-007` Release package revisions are mutually traceable.
- [ ] `E-008` Remaining issues are classified as closed, accepted limitation, or deferred obligation.
- [ ] `E-009` Human engineering owner provides the final approval for the applicable release gate.
- [ ] `E-010` Every spec requirement ID has at least one task, or is marked `N/A` with a reason.

## Open items

Descriptions are in the specification (section 8.2). Status and owner below are tracked here.

| ID     | Spec ref | Open item | Status | Owner / target |
| ------ |---|---|---|---|
| OI-001 | OPEN-008, SAF-001 | H743-failure behavior and F100 safety implementation | Closed 2026-10-24: no landing, servo failsafe on the F100, motors on the H743 (DEC-016). Motor stop on a hang: OI-019. | Closed |
| OI-002 | OPEN-004 | Sensor MFR/MPN and electrical properties | Parts chosen: IMU 2 × ICM-45686 (DEC-008), barometers ICP-20100 + BMP581 (DEC-010), magnetometer IST8310 (DEC-011). Electrical properties `NOT_VERIFIED` except the IST8310 values in the selection record. ICP-20100 EOL, BMP581 stock and IST8310 lifecycle open. | Human owner / P0 |
| OI-003 | OPEN-001 | External interfaces and exact MCU pins | Logical allocation by the team (DEC-014, DEC-018). Pins in the pin allocation; pinmap review 0.3 answered (P0-020). Partly drawn (spec 4.2 "Schematic state"). | Hardware / P1 |
| OI-004 | OPEN-006, OPEN-007 | Power protection, transients, downstream budgets, and distribution | Design details open. Servo current on the board (DEC-019); sizing waits on the team's stall-current test (OPEN-007). 5 V input: TPS2121 power mux (DEC-029, DEC-030), reverse current blocked on both channels. USB is a bench supply (DEC-038). 5 V budget closed 2026-11-03 (spec OPEN-006; power budget section 4, `ESTIMATED`). Priority mode: OI-026. | Hardware / P0, P2; Team for OPEN-007 |
| OI-005 | OPEN-001, OPEN-003 | Exact MCU pin mapping and resource conflicts (overlaps OI-003) | Signals checked against ST pin data, no duplicate pins (pin allocation). OPEN-003 closed. DMA and interrupt checks (P1-010) not done by hardware. | Hardware / P1 |
| OI-006 | OPEN-002 | H743↔F100 USART implementation and software contract | Closed 2026-10-24 by DEC-015: px4io, USART6 ↔ USART2, 1.5 Mb/s. Test access stays with TST-006. | Closed |
| OI-007 | DEC-004 | PX4 target and bootloader plan | `DEFERRED`; non-blocking. | Software / post-hardware |
| OI-008 | OPEN-003, OPEN-008 | F100 PWM outputs and failsafe behavior | Closed 2026-10-24: 8 servos on the px4io-v2 timers (IF-030 to IF-037); failsafe values are PX4 parameters set after flight tests (D3). Electrical behavior unverified. | Closed |
| OI-009 | OPEN-009 | Exact outline, mounting, connector placement, and environment | Maximum envelope confirmed. Environment set (DEC-020). Set by the human owner on 2026-10-24: M3, 3.2 mm holes, soft mount, own tray, USB-C and microSD on adjacent edges, part height about 10 to 15 mm. Hardware sets the outline, cable entry sides and dampers at placement; the CAD team follows. | Human owner, then CAD team / P3 |
| OI-010 | OPEN-005 | Magnetometer count/allocation and sensor requirements | Closed: 1 magnetometer (DEC-011), now IST8310. | Team / closed 2026-10-18 |
| OI-011 | None (checklist only) | Physical actuator/ESC signal distribution | 4 ESCs on the H743 (TIM5) and 8 servos on the F100 (DEC-016). Servos plug into 3-pin headers on an on-board 6 V bus (DEC-019). Bus and UBEC input: OI-023. ESCs: 4 × Skywalker 80A V2 (team design); 3-pin headers with the + pin removed (P2-018). | Hardware / P2 |
| OI-012 | OPEN-010 | All non-MCU part numbers | Sensors (DEC-008, DEC-010, DEC-011), the main 3.3 V buck TPS62142RGTR (DEC-012), the 5 V power mux TPS2121 (DEC-029) and the `+3V3A` LDO TPS73533DRBR (DEC-027) are chosen. Passive MFR and MFR.P/N later (human owner). No other non-MCU part is approved. | Human owner / component selection gate (P0-016) |
| OI-013 | OPEN-011 | `+3V3A` rail purpose, load and level match | `+3V3A` feeds the VDD pins of all sensors (DEC-043, replaces DEC-025), drawn that way (spec 4.2). LDO TPS73533DRBR (DEC-027). Level match and power-up order: LDO EN from the buck PG (DEC-039). Load: IMUs only so far; barometer and IST8310 VDD currents not added (power budget). NR and output capacitors: spec 4.3 (output derating not checked). Open: bench ramp check (P4-015). | Human owner / P0, P2 |
| OI-014 | OPEN-012 | `+VIN` to `+5V` path | Closed 2026-10-31: eFuse values checked against TI (spec CMP-008, 4.7); eFuse later removed (DEC-029). Reverse current and the 5 V budget moved to OI-004. | Closed |
| OI-015 | OPEN-013 | Sensor symbol and footprint starting points | In the project library and placed (U401, U402, U501, U502, U503; spec 4.2). Pin maps match the datasheet tables; land patterns and pin 1 not checked. IST8310 stock footprint fit `ESTIMATED`; Bosch LGA-10 pads image-read, not checked. | Human owner / P2 (P2-012) |
| OI-016 | OPEN-014 | Second barometer part number | Closed 2026-10-24: BMP581, BMP384 fallback (DEC-010). | Closed |
| OI-017 | OPEN-015 | IO MCU clock for stock px4io | Closed 2026-10-24 by DEC-017: STM32F100C8T6B at 24 MHz. Clock source and px4io image later changed by DEC-044 and DEC-045 (CMOS oscillator, custom px4io). | Closed |
| OI-018 | OPEN-016 | Spec rows changed by the team's pinmap answers | Closed 2026-10-24: applied in spec rev 0.11. | Closed |
| OI-019 | OPEN-017 | Motor stop on an H743 hang depends on the ESC's signal-loss behavior | ESC: 4 × Skywalker 80A V2 (team design), DShot support `NOT_VERIFIED`, looks PWM-only. Conflicts with FUN-002 and SAF-015; asked in D13. | Team + Hardware / P4 (P4-011) |
| OI-020 | OPEN-018 | PWM pull-down value with bidirectional DShot | Value TBD. | Hardware / P2 (P2-013), P4 (P4-011) |
| OI-021 | OPEN-019 | BMP384 fallback fit against the BMP581 | Not checked. | Hardware / P1 (P1-015) |
| OI-022 | OPEN-020 | STM32F100 datasheet values | Closed 2026-10-24: HSE 4 to 24 MHz, VDD 2 to 3.6 V, POR/PDR and PVD, 5 V tolerance checked (DocID16455 Rev 9). | Closed |
| OI-023 | OPEN-021 | On-board servo bus and UBEC input rating | Headers chosen (DEC-019); UBEC input on a board-mount XT30. XT30 rating against PWR-011 `NOT_VERIFIED`. Copper, GND join and bulk capacitance open. | Hardware / P2 (P2-016) |
| OI-024 | OPEN-022 | ESC current sense and telemetry pins | Closed 2026-10-24: dropped (IF-052, IF-053 removed). PC1 stays reserved (DEC-023). | Closed |
| OI-025 | OPEN-023 | External connector pinouts and the PM02D connector | DS-009 not read. GPS1 10-pin extra pins and I2C4 5 V tolerance open. PM02D: CN101 CLIK-Mate drawn (DEC-042); pin order against the cable open. | Hardware / P2 (P2-015) |
| OI-026 | OPEN-024 | Power mux source priority and switchover | Closed 2026-11-02: PM02D priority with the XCOMP fast switchover, R105 fitted (DEC-031 to DEC-034). | Closed |
| OI-027 | OPEN-025 | Power mux status LED (Q101, D103) | Kept (DEC-035); ST and OV dividers set (DEC-036); D103 and D104 fields fixed. Open: ST low level against the Q101 minimum threshold (TI gives no ST VOL), LED currents. | Hardware / P4 (P4-012) |
| OI-028 | OPEN-026 | Reset: button and internal-reset behavior | Decided 2026-11-14: one shared NRST net with one reset button (DEC-046). Open: the button is not drawn; whether an MCU's internal reset drives NRST low is `NOT_VERIFIED`. | Hardware / P1 (P1-014), P2 (P2-022) |
| OI-029 | OPEN-027 | IST8310 I2C address straps | Closed 2026-11-14: 0x0C as strapped (DEC-047); PX4 start at 0x0C (P1-018). | Closed |
| OI-030 | OPEN-028 | Clock sources: oscillator parts and data | Type decided: CMOS oscillators (DEC-044), HSE bypass in firmware (DEC-045). Drawn: U202 16 MHz into PH0, U302 24 MHz into PD0, each through 22 Ω; part numbers decided 2026-11-14 (DEC-048). Oscillator data and the HSE external-clock limits `NOT_VERIFIED`. | Hardware / P1 (P1-014), P2 (P2-022); software team (P1-017) |
| OI-031 | OPEN-029 | Debug connector and pads: no console, no NRST | Drawn, not decided: H743 4-pin connector and F100 4 pads with VREF, SWDIO, SWCLK, GND; IF-045, IF-051 and TST-001 ask for the console and NRST too. | Human owner / P1 (P1-008), P2 (P2-022) |

## Current next action

- Finish the MCU, sensor and USB sheets, then run ERC and ask for a `sch-review` (P2-022).
- Draw the reset button (DEC-046, OPEN-026) and decide the debug pin set (OPEN-029, P1-008).
- Check the oscillator data and the HSE external-clock limits before layout (OPEN-028, CMP-010); the software team sets HSE bypass and the IST8310 address (P1-017, P1-018).
- Send integration questions rev 0.4 and collect the team inputs, mainly D13 on the ESC (P0-022).
- Before PCB placement: check the connector pinouts against DS-009 and the CN101 pin order (P2-015), design the servo bus and XT30 input (P2-016), and draw the ESC headers (P2-018).
- Human review of the pin choices (P1-001, P1-002); fill the power-sheet resistor fields (P2-021).
- Check the sensor footprints and the BMP384 fallback (P2-012, P1-015), and pick the PWM pull-down value (P2-013).
- Keep the candidate label on all pin mappings. Do not begin fabrication release until the applicable P0 to P3 evidence and Human approval are complete.
