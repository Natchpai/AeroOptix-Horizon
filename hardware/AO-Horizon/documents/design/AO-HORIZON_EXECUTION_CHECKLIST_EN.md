# AeroOptix-Horizon: Execution Checklist

**Revision:** 0.9
**Updated:** 2026-10-24
**Status:** Active execution tracker; not an approval or verification record
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md)

Use the specification for confirmed requirements and decisions. This checklist records the sequence of work and the evidence needed to close each gate. Diagram content is reference material. User-confirmed requirements take precedence. Sensor parts are chosen (DEC-008, DEC-010, DEC-011) except the second barometer (OPEN-014); their lifecycle and sourcing risks are open.

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

Groups: P0.1 scope and operating intent (P0-001 to P0-003). P0.2 MCU and safety boundary (P0-004 to P0-007). P0.3 sensors (P0-008 to P0-011). P0.4 interfaces, power, actuators, and envelope (P0-012 to P0-015). Tasks added by audit are P0-016 to P0-018, P1-014, P2-010, P3-010, and P3-011. P0-019 was added on 2026-10-24 for the team's pinmap answers.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P0-001 | Define the flight-controller role and system boundary. Scope confirmed on 2026-10-13. | SYS-001, SYS-002 | Human | DONE | User confirmation, 2026-10-13. DEC-013 (Pixhawk 6C and 6X as references, 2026-10-24). |
| P0-002 | Record PX4 target/version and supported modes as Software-owned deferred work. Not needed to proceed with hardware. | DEC-004 | Human | DONE | DEC-004 |
| P0-003 | Define first-revision scope. In scope: H743 main control, F103 auxiliary I/O/PWM/safety, and the stated external interfaces. Deferred: PX4, bootloader, QGC, and detailed software behavior. | SYS-001, DEC-004 | Human | DONE | DEC-004; spec 1.2 |
| P0-004 | Confirm STM32H743VIT6 as the main MCU. Implementation not verified. | MCU-001, CMP-001, FUN-001 | Human | DONE | DEC-001 |
| P0-005 | Confirm STM32F103C8T6 as operational auxiliary I/O/PWM/ESC/safety MCU. Implementation not verified. | MCU-002, CMP-002 | Human | DONE | DEC-002 |
| P0-006 | Reserve H743↔F103 USART. Pins, levels, instance, rate, and test access remain for P1/P2. | IF-001, IF-024 | Human | DONE | DEC-003 |
| P0-007 | Record the immediate-landing requirement if H743 is unavailable. USART is the monitoring path. Software owns detection, command behavior, and timing. Hardware must preserve the physical path and test access. Team answer on 2026-10-24: stock px4io cannot land; the team decides the wording (OPEN-016, P0-019). | SAF-001, FUN-004 | Human | DONE | DEC-005 |
| P0-008 | Select two IMU MFR/MPNs. Team confirmed 2 × ICM-45686 on 2026-10-18. SPI, supply range and sourcing checks stay open in the selection record. | SEN-001, CMP-003 | Team | DONE | DEC-008; [AO-HORIZON_IMU_SELECTION_EN.md](AO-HORIZON_IMU_SELECTION_EN.md) |
| P0-009 | Select two barometer MFR/MPNs. Team confirmed ICP-20100 + BMP390 on 2026-10-18. BMP390 removed on 2026-10-21 (not available at LCSC); BMP581 (LCSC C5362283) proposed, team to confirm. In pinmap review 0.2 the team put BMP581 on I2C2 at 0x46 but did not confirm the part (decisions file D7). ICP-20100 EOL stays open in the selection record. | SEN-002, CMP-004, OPEN-014 | Team | IN_PROGRESS | DEC-010; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-010 | Decide magnetometer MFR/MPN and allocation. Team confirmed 1 × BMM150 onboard on 2026-10-18; no second magnetometer. The human owner changed the part to iSentek IST8310 on 2026-10-24. | SEN-003, CMP-005 | Team | DONE | DEC-011; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-011 | Define sensor rates, DRDY/interrupt needs, calibration, and redundancy. | SEN-001, SEN-002, SEN-003 | Human | OPEN | Sensor requirement record |
| P0-012 | Confirm logical H743/F103 external interface allocations. Exact pins and electrical implementation unverified. See specification section 3. The team's 2026-10-24 answers change some of these allocations (OPEN-016, P0-019). | IF-010 to IF-024 | Human | DONE | User confirmation, date TBD. No DEC record yet. |
| P0-013 | Confirm board and servo power requirements. Protection, transients, distribution, and component choice are open (see P0-017). | PWR-001, PWR-002, PWR-010, PWR-011 | Human | DONE | DEC-007 |
| P0-014 | Confirm logical F103 PWM/expanded-I/O functions: TILT, ESC, COAX, AIL, and FlySky. Timer/channel validity and electrical implementation unverified. The team's 2026-10-24 answers rename the 8 outputs as servos, move the ESCs to the H743 and drop FlySky (OPEN-016, P0-019). | IF-030 to IF-038, FUN-003 | Human | DONE | User confirmation, date TBD. No DEC record yet. |
| P0-015 | Confirm maximum PCB envelope. Shape, mounting, connector orientation, and environment open for P3. | MEC-001 | Human | DONE | DEC-006 |
| P0-016 | Select non-MCU parts: regulators, protection, connectors, PDB/UBEC, and interface ICs. Main 3.3 V buck chosen: TPS62142RGTR (DEC-012). `+3V3A` LDO and the rest are open. | CMP-006, CMP-007, OPEN-010, OPEN-011 | Human | IN_PROGRESS | DEC-012; part selection record for the remaining parts |
| P0-017 | Define power budget, rail tolerances, brownout thresholds, and 5 V and 6 V protection and transient requirements. | PWR-012 to PWR-014, SAF-012 to SAF-014, OPEN-006, OPEN-007 | Hardware | OPEN | Power budget table and protection requirement record. Draft: [AO-HORIZON_POWER_BUDGET_EN.md](AO-HORIZON_POWER_BUDGET_EN.md) |
| P0-018 | Define environmental limits: operating and storage temperature, vibration and shock, humidity, ingress, altitude, maintenance. | ENV-001 to ENV-004 | TBD | OPEN | Decision record with a verification method per limit |
| P0-019 | Get team decisions on the spec rows that the pinmap review 0.2 answers change, then update the spec. Send `AO-HORIZON_PINMAP_DECISIONS_EN.md` (spec rows, decisions D1 to D7, software questions S1 to S7, proposals H1 and H2). | OPEN-016, OPEN-015, SAF-001, FUN-002, FUN-003 | Team | OPEN | Returned decisions file; spec change note |

## P1: Allocation

Any candidate pin mapping stays labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete. P1-006 to P1-008 are proposed allocations, not confirmed.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P1-001 | Assign exact H743 pins and alternate functions for all confirmed and approved interfaces. Draft in the pin allocation record; the team answered pinmap review 0.2 on 2026-10-24. Pinmap 0.3 waits on OPEN-016. | IF-010 to IF-024, OPEN-001 | Hardware | IN_PROGRESS | Versioned MCU pin-allocation table. Draft: [AO-HORIZON_PIN_ALLOCATION_EN.md](AO-HORIZON_PIN_ALLOCATION_EN.md); answers: [AO-HORIZON_PINMAP_REVIEW_EN.md](AO-HORIZON_PINMAP_REVIEW_EN.md) |
| P1-002 | Assign exact F103 pins and alternate functions for its approved role. Draft as for P1-001. Team answer: stock px4io-v2 pins (Q7). | IF-030 to IF-038, FUN-002, OPEN-001 | Hardware | IN_PROGRESS | Versioned F103 pin-allocation table. Draft and answers as for P1-001 |
| P1-003 | Allocate both SPI IMUs: CS, DRDY, bus ownership, DMA. No IMU reset line; reset is by software (DEC-009). Team: IMU pin 9 (INT2/CLKIN) not used (Q16). | SEN-001 | Hardware | OPEN | SPI allocation and timing review |
| P1-004 | Allocate both I2C barometers: addresses, pull-ups, recovery, bus ownership. | SEN-002 | Hardware | OPEN | I2C address/bus review |
| P1-005 | Allocate the I2C magnetometer (IST8310, DEC-011): address (CAD0/CAD1), pull-ups, DRDY and RSTN use, recovery, placement constraints. Team: 0x0E, DRDY and RSTN not connected (Q11). | SEN-003 | Hardware | OPEN | I2C and magnetic-placement review |
| P1-006 | Allocate USB FS, VBUS sensing, ESD/protection, connector, and reset support for H743 flashing (proposed). | IF-022 | Hardware | OPEN | USB interface review and schematic net list |
| P1-007 | Allocate selectable H743 BOOT0 and define its default/reset behavior (proposed). | FUN-006, TST-003 | Hardware | OPEN | Boot-state table and circuit review |
| P1-008 | Allocate SWD access for both MCUs: SWDIO, SWCLK, NRST, GND, probe access (proposed). | FUN-005, IF-023, TST-001, TST-002 | Hardware | OPEN | Debug-access review |
| P1-009 | Check alternate-function conflicts across every assigned pin. | OPEN-001, OPEN-003 | Hardware | OPEN | Conflict report with no unresolved critical conflicts |
| P1-010 | Check DMA, interrupt, timer/PWM, clock, and priority conflicts. | OPEN-003 | Hardware | OPEN | Resource matrix and resolution record |
| P1-011 | Check voltage domains, IO levels, pull states, reset states, and boot-time behavior. | OPEN-002 | Hardware | OPEN | Electrical compatibility review |
| P1-012 | Review package pin availability, reserved pins, unused pins, and ERC/DRC implications. | OPEN-001 | Hardware | OPEN | Package/resource review |
| P1-013 | Record mapping revision, reviewer, date, conflicts, resolutions, and remaining obligations. | OPEN-001 | TBD | OPEN | Signed or attributable review record |
| P1-014 | Define clock sources, reset topology, watchdog use, and F103 boot behavior. Added by audit. F103: stock px4io expects 24 MHz, outside the F103 crystal range (OPEN-015). H743: 16 MHz proposed to the team (decisions file H1). | Spec 4.4, OPEN-015 | Hardware | OPEN | Clock/reset/boot decision record |

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
| P2-007 | Define H743↔F103 firmware ownership, protocol version, startup, timeout, and fault behavior. | IF-001, SAF-010, SAF-011, OPEN-008 | Software | DEFERRED | Later versioned firmware interface contract. Hardware shall document the reserved electrical path before schematic freeze. |
| P2-008 | Run ERC and resolve or disposition all relevant findings. |  | TBD | OPEN | ERC output and issue disposition |
| P2-009 | Complete line-by-line schematic review. |  | TBD | OPEN | Review checklist with reviewer and evidence links |
| P2-010 | Complete the spec 4.7 calculations: board input current, servo rail current, rail tolerance, thermal margin, and safety response timing. Added by audit. | Spec 4.7, PWR-012 to PWR-014 | Hardware | OPEN | Calculation records with margins |
| P2-011 | Capture the power sheet (`power_supplies.kicad_sch`): power module input, `+VIN` to `+5V` path, TPS62142 3.3 V buck, `+3V3A` LDO, indicator. Does not depend on P1. Drawn so far: see spec 4.3 "Schematic state". Open: `+VIN` to `+5V` path (OPEN-012), `+3V3A` decision and its NR and output capacitors (OPEN-011), the 0.1 µF AVIN-to-AGND capacitor TI recommends for the TPS62142, annotation, LCSC C162430 on both the 1 µF (GCM188R71C105KA64J) and 10 µF (GRM21BZ71C106KE15L) capacitors, `PM02_SCL` / `PM02_SDA` going nowhere, the DNP DF2S6.2CT on `+VIN`. | DEC-012, OPEN-011, OPEN-012 | Hardware | IN_PROGRESS | Saved `power_supplies.kicad_sch`; power-sheet review record |
| P2-012 | Check the sensor footprints against the datasheet drawings and app notes: pad geometry, land pattern, pin 1 corner, 3D model. Pin maps already match the datasheet tables. IST8310 uses the stock symbol and `LGA-16_3x3mm_P0.5mm` footprint (fit `ESTIMATED`, no land pattern in the datasheet). See spec 4.6 "Library state". Bosch LGA-10 pads set to the BMP581 land pattern (DS004-13 Fig. 32) on 2026-10-21; the values were read from an image and need a human check. | OPEN-013, CMP-003 to CMP-005 | Human | IN_PROGRESS | Per-part review record naming the datasheet figure or app note used |

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
| P3-010 | Define PCB fabrication parameters: layer count, stackup, copper weight, trace/space, hole/via, soldermask, finish. Added by audit. | PCB-001 to PCB-005, MFG-001 | TBD | OPEN | Parameter record confirmed by the fabricator |
| P3-011 | Route PWM/actuator outputs and the H743↔F103 USART with return path, drive, protection, voltage compatibility, and test access. Added by audit. | PCB-014, PCB-015 | TBD | BLOCKED BY P0, P2 | Layout review and electrical test |

## P4: Bring-up and validation

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P4-001 | Inspect the assembled board for shorts, assembly defects, polarity, and component identity. |  | TBD | OPEN | Inspection record |
| P4-002 | Verify power rails, sequencing, reset behavior, and current consumption before firmware loading. | PWR-001, PWR-002, TST-004, TST-005 | TBD | OPEN | Measured bring-up log |
| P4-003 | Verify SWD access for H743. | FUN-005, TST-001 | TBD | OPEN | Probe/session log |
| P4-004 | Verify SWD access for F103. | FUN-005, TST-002 | TBD | OPEN | Probe/session log |
| P4-005 | Verify the H743 USB FS hardware path, connector, protection, continuity, and relevant electrical behavior. | IF-022 | TBD | OPEN | Hardware inspection/measurement record. Host enumeration may stay deferred. |
| P4-006 | Verify firmware flashing through QGC for the approved workflow. | DEC-004 | Software | DEFERRED | Later reproducible software test record. Not a hardware release blocker. |
| P4-007 | Verify bootloader, PX4 startup, sensor detection, and calibration flow. | DEC-004 | Software | DEFERRED | Later firmware/console/test log. Not a hardware release blocker. |
| P4-008 | Verify the H743↔F103 physical link, electrical levels, continuity, and test access. Protocol behavior is deferred to Software. | IF-001, IF-024, TST-006 | Hardware, Software | OPEN | Hardware link test record and later software protocol test record |
| P4-009 | Verify actuator outputs, arming behavior, failsafe behavior, and fault handling. | SAF-001, SAF-010 to SAF-013, TST-007 | TBD | OPEN | Safety/actuator test record |
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
| OI-001 | OPEN-008, SAF-001 | Immediate-landing requirement and F103 safety implementation | Requirement confirmed. Team answer (2026-10-24): stock px4io cannot land; outputs go to failsafe values after 0.5 s. The team decides the wording and the motor outputs (OPEN-016). | Team + Software / P0, P2, P4 |
| OI-002 | OPEN-004 | Sensor MFR/MPN and electrical properties | Parts chosen: IMU 2 × ICM-45686 (DEC-008), barometer 1 ICP-20100 (DEC-010), barometer 2 TBD (OPEN-014), magnetometer IST8310 (DEC-011, replaced BMM150 on 2026-10-24). Electrical properties `NOT_VERIFIED` except the IST8310 values in the selection record. ICP-20100 EOL and IST8310 lifecycle open. | Human owner / P0 |
| OI-003 | OPEN-001 | External interfaces and exact MCU pins | Logical requirements confirmed; mapping unverified. | Hardware / P1 |
| OI-004 | OPEN-006, OPEN-007 | Power protection, transients, downstream budgets, and distribution | Input and servo ratings recorded; design details open. | Hardware / P0, P2 |
| OI-005 | OPEN-001, OPEN-003 | Exact MCU pin mapping and resource conflicts (overlaps OI-003) | `NOT_VERIFIED` | Hardware / P1 |
| OI-006 | OPEN-002 | H743↔F103 USART implementation and software contract | Physical protocol confirmed. Team answer: px4io-v2, H743 USART6 to F103 USART2, 1.5 Mb/s; not yet in the spec (OPEN-016). | Hardware + Software / P1, P2 |
| OI-007 | DEC-004 | PX4 target and bootloader plan | `DEFERRED`; non-blocking. | Software / post-hardware |
| OI-008 | OPEN-003, OPEN-008 | F103 PWM outputs and failsafe behavior | Team confirmed TIM3_CH1 to CH4 (Q3) and renamed the 8 outputs as servos; failsafe positions asked (decisions file D3). Electrical behavior unverified. | Hardware + Software / P1, P2 |
| OI-009 | OPEN-009 | Exact outline, mounting, connector placement, and environment | Maximum envelope confirmed; remaining mechanics TBD. | Human owner / P0, P3 |
| OI-010 | OPEN-005 | Magnetometer count/allocation and sensor requirements | Closed: 1 magnetometer (DEC-011), now IST8310. | Team / closed 2026-10-18 |
| OI-011 | None (checklist only) | Physical actuator/ESC signal distribution | Diagram captured. The team plans 4 ESCs on the H743 (TIM5) and 8 servos on the F103, pending decision D2. | Hardware / P1, P2 |
| OI-012 | OPEN-010 | All non-MCU part numbers (added by audit) | Sensors (DEC-008, DEC-010, DEC-011) and the main 3.3 V buck TPS62142RGTR (DEC-012) are chosen. No other non-MCU part is approved. | Human owner / component selection gate (P0-016) |
| OI-013 | OPEN-011 | `+3V3A` rail purpose, load and LDO part | TPS73533DRBR drawn, not decided. As drawn, NR capacitor above TI's limit and output capacitance at TI's minimum. | Human owner / P0, P2 |
| OI-014 | OPEN-012 | `+VIN` to `+5V` path | Not drawn; both regulators have no input source yet. | Hardware / P2 (P2-011) |
| OI-015 | OPEN-013 | Sensor symbol and footprint starting points | In the project library, not placed. Pin maps match the datasheet tables; land patterns and pin 1 not checked. IST8310 uses the stock symbol and footprint (fit `ESTIMATED`). Bosch LGA-10 pads follow BMP581 Fig. 32 (image-read, not checked). | Human owner / P2 (P2-012) |
| OI-016 | OPEN-014 | Second barometer part number | BMP390 removed 2026-10-21. BMP581 (LCSC C5362283) proposed; the team put it on I2C2 at 0x46 but has not confirmed it (D7). BMP581 library starting point added (spec 4.6). | Team / P0 (P0-009) |
| OI-017 | OPEN-015 | F103 clock for stock px4io | 24 MHz is outside the F103 crystal range (DS5319 Table 22). Team asked which px4io build they accept (S7). | Hardware + Team / P1 (P1-014) |
| OI-018 | OPEN-016 | Spec rows changed by the team's pinmap answers | Decisions file ready to send. | Team / P0 (P0-019) |

## Current next action

Send `AO-HORIZON_PINMAP_DECISIONS_EN.md` to the team and wait for their decisions (P0-019, OPEN-016); then update the spec rows and issue pinmap 0.3. Settle the F103 clock with the team's S7 answer (OPEN-015). In parallel, continue the power sheet (P2-011): connect `+VIN` to `+5V`, decide the `+3V3A` rail (and its NR and output capacitors if TPS73533DRBR stays), fix the C162430 LCSC field, then annotate. Get the team decision on the second barometer (P0-009, OPEN-014). Check the sensor footprints against the datasheets (P2-012) before placing them. Keep sensor-specific resources provisional until the sensor requirements are decided. Keep the candidate/unverified label on all pin mappings. Reserve the USART safety path and test access. Do not begin fabrication release until the applicable P0 to P3 evidence and Human approval are complete.
