# AeroOptix-Horizon: Execution Checklist

**Revision:** 0.15
**Updated:** 2026-10-26
**Status:** Active execution tracker; not an approval or verification record
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md) rev 0.16

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

Groups: P0.1 scope and operating intent (P0-001 to P0-003). P0.2 MCU and safety boundary (P0-004 to P0-007). P0.3 sensors (P0-008 to P0-011). P0.4 interfaces, power, actuators, and envelope (P0-012 to P0-015). Tasks added by audit are P0-016 to P0-018, P1-014, P2-010, P3-010, and P3-011. P0-019 was added on 2026-10-24 for the team's pinmap answers, and P0-020, P1-015, P2-013 and P4-011 for the follow-up items. P2-014 was added on 2026-10-24 for the IO MCU change, and P0-021 for the integration questions. P0-022, P1-016, P2-015 and P2-016 were added on 2026-10-24 for the follow-up to the integration answers.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P0-001 | Define the flight-controller role and system boundary. Scope confirmed on 2026-10-13. | SYS-001, SYS-002 | Human | DONE | User confirmation, 2026-10-13. DEC-013 (Pixhawk 6C and 6X as references, 2026-10-24). |
| P0-002 | Record PX4 target/version and supported modes as Software-owned deferred work. Not needed to proceed with hardware. | DEC-004 | Human | DONE | DEC-004 |
| P0-003 | Define first-revision scope. In scope: H743 main control, F100 auxiliary I/O/PWM/safety, and the stated external interfaces. Deferred: PX4, bootloader, QGC, and detailed software behavior. | SYS-001, DEC-004 | Human | DONE | DEC-004; spec 1.2 |
| P0-004 | Confirm STM32H743VIT6 as the main MCU. Implementation not verified. | MCU-001, CMP-001, FUN-001 | Human | DONE | DEC-001 |
| P0-005 | Confirm the IO MCU (px4io: servo PWM, safety switch, servo failsafe). Changed from STM32F103C8T6 to STM32F100C8T6B on 2026-10-24, following the team; LCSC stock checked by the human owner. Implementation not verified. | MCU-002, CMP-002 | Human | DONE | DEC-002, DEC-017 |
| P0-006 | Reserve H743↔F100 USART. Instance, rate and protocol set by DEC-015 (USART6 ↔ USART2, 1.5 Mb/s, px4io). Test access remains for P2. | IF-001, IF-024 | Human | DONE | DEC-003, DEC-015 |
| P0-007 | Record the H743-failure behavior. Changed on 2026-10-24 from "immediate landing" to: the F100 holds the servos at failsafe values after 0.5 s without H743 data, and the motors stop when DShot frames stop. Hardware preserves the physical path and test access. | SAF-001, FUN-004, SAF-015 | Human | DONE | DEC-005, DEC-016 |
| P0-008 | Select two IMU MFR/MPNs. Team confirmed 2 × ICM-45686 on 2026-10-18. SPI, supply range and sourcing checks stay open in the selection record. | SEN-001, CMP-003 | Team | DONE | DEC-008; [AO-HORIZON_IMU_SELECTION_EN.md](AO-HORIZON_IMU_SELECTION_EN.md) |
| P0-009 | Select two barometer MFR/MPNs. Team confirmed ICP-20100 + BMP390 on 2026-10-18. BMP390 removed on 2026-10-21 (not available at LCSC). Team accepted BMP581 with BMP384 fallback on 2026-10-24 (decisions file D7). ICP-20100 EOL and the BMP384 fit (OPEN-019) stay open. | SEN-002, CMP-004 | Team | DONE | DEC-010; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-010 | Decide magnetometer MFR/MPN and allocation. Team confirmed 1 × BMM150 onboard on 2026-10-18; no second magnetometer. The human owner changed the part to iSentek IST8310 on 2026-10-24. | SEN-003, CMP-005 | Team | DONE | DEC-011; [AO-HORIZON_BARO_MAG_SELECTION_EN.md](AO-HORIZON_BARO_MAG_SELECTION_EN.md) |
| P0-011 | Define sensor rates, DRDY/interrupt needs, calibration, and redundancy. | SEN-001, SEN-002, SEN-003 | Human | OPEN | Sensor requirement record |
| P0-012 | Confirm logical H743/F100 external interface allocations. Revised by the team on 2026-10-24 (one GPS, debug console on USART3, motors on TIM5, microSD, buzzer, LEDs, power module, debug connector). Electrical implementation unverified. | IF-010 to IF-024, IF-040 to IF-048 | Human | DONE | DEC-014, DEC-018 |
| P0-013 | Confirm board and servo power requirements. Protection, transients, distribution, and component choice are open (see P0-017). Servo current passes through the board: 8 × 3-pin headers with an on-board 6 V bus, and the UBEC on a board-mount XT30 (DEC-019, 2026-10-24). | PWR-001, PWR-002, PWR-010, PWR-011 | Human | DONE | DEC-007, DEC-019 |
| P0-014 | Confirm logical F100 functions. Revised by the team on 2026-10-24: 8 servo outputs (flaperon L/R, ruddervator L/R, tilt servo 1 to 4) on the px4io-v2 timers, safety switch and LED, servo rail sense; ESCs moved to the H743; FlySky dropped. Electrical implementation unverified. | IF-030 to IF-038, IF-049 to IF-051, FUN-003 | Human | DONE | DEC-014, DEC-016, DEC-018 |
| P0-015 | Confirm maximum PCB envelope. Shape, mounting, connector orientation, and environment open for P3. | MEC-001 | Human | DONE | DEC-006 |
| P0-016 | Select non-MCU parts: regulators, protection, connectors, PDB/UBEC, and interface ICs. Main 3.3 V buck chosen: TPS62142RGTR (DEC-012). 5 V input eFuse chosen: TPS16412DRC (DEC-024). `+3V3A` LDO and the rest are open. | CMP-006 to CMP-008, OPEN-010, OPEN-011 | Human | IN_PROGRESS | DEC-012, DEC-024; part selection record for the remaining parts |
| P0-017 | Define power budget, rail tolerances, brownout thresholds, and 5 V and 6 V protection and transient requirements. | PWR-012 to PWR-014, SAF-012 to SAF-014, OPEN-006, OPEN-007 | Hardware | OPEN | Power budget table and protection requirement record. Draft: [AO-HORIZON_POWER_BUDGET_EN.md](AO-HORIZON_POWER_BUDGET_EN.md) |
| P0-018 | Define environmental limits: operating and storage temperature, vibration and shock, humidity, ingress, altitude, maintenance. | ENV-001 to ENV-004 | TBD | OPEN | Decision record with a verification method per limit |
| P0-019 | Get team decisions on the spec rows that the pinmap review 0.2 answers change, then update the spec. Team answered on 2026-10-24; applied in spec rev 0.11. | OPEN-016, OPEN-015, SAF-001, FUN-002, FUN-003 | Team | DONE | Returned decisions file rev 0.2; spec change note 0.11; commit `c9fe9ed` |
| P0-020 | Get the team's reply to pinmap review 0.3: `NEW` rows (debug connector pinout, IO MCU crystal, px4io console, px4io reserved pins, BMP384 fallback) and questions Q20 to Q22. Answered 2026-10-24: all OK, plus PA10 and PB11 pull-ups, the three px4io LEDs fitted, BMP384 at 0x76, and the F100 instead of the F103. | OPEN-001 | Team | DONE | [AO-HORIZON_PINMAP_REVIEW_EN.md](AO-HORIZON_PINMAP_REVIEW_EN.md) rev 0.3 (answered) |
| P0-021 | Get the team's answers to the integration questions: servo power path (D8), mounting and cable entry (D9), environment (D10), safety switch and GPS module (D11), external devices and connectors, software questions S8 to S10. Added 2026-10-24. | PWR-002, PWR-011, MEC-002 to MEC-004, ENV-001 to ENV-004, IF-010 to IF-022, IF-040 to IF-049, OPEN-007, OPEN-009 | Team | DONE | Answered 2026-10-24: [AO-HORIZON_INTEGRATION_QUESTIONS_EN.md](AO-HORIZON_INTEGRATION_QUESTIONS_EN.md) rev 0.2; spec change note 0.13 (DEC-019 to DEC-022). Remaining inputs: P0-022 |
| P0-022 | Get the remaining team inputs: D13 (the Skywalker 80A V2 ESCs look PWM-only; how the motors stop on an H743 hang), ELRS receiver model, MS4525DO version, chip and plug on the PM02D, UBEC model, positions of the Kingmax C507 and DS-843MG servos, stall current of all servos (bench test). Mounting, USB loads, ESC connector and ESC current sense were set by hardware on 2026-10-24 (spec rev 0.14). Added 2026-10-24. | OPEN-007, OPEN-017, IF-010, IF-014, IF-048, PWR-011 | Team | OPEN | Team reply to [AO-HORIZON_INTEGRATION_QUESTIONS_EN.md](AO-HORIZON_INTEGRATION_QUESTIONS_EN.md) rev 0.4 (D13, parts table, tests) |

## P1: Allocation

Any candidate pin mapping stays labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete. P1-006 to P1-008 are proposed allocations, not confirmed.

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P1-001 | Assign exact H743 pins and alternate functions for all confirmed and approved interfaces. Team changes applied in pin allocation rev 0.6, with the team's pinmap review 0.3 answers (2026-10-24). New pins checked against ST pin data. Waits for the human review of the pin choices. | IF-010 to IF-024, IF-040 to IF-048, OPEN-001 | Hardware | IN_PROGRESS | Versioned MCU pin-allocation table: [AO-HORIZON_PIN_ALLOCATION_EN.md](AO-HORIZON_PIN_ALLOCATION_EN.md) rev 0.6; [AO-HORIZON_PINMAP_REVIEW_EN.md](AO-HORIZON_PINMAP_REVIEW_EN.md) rev 0.3 |
| P1-002 | Assign exact F100 pins and alternate functions for its approved role. px4io-v2 pins applied on the STM32F100C8T6B (same pins as the F103, pin allocation F-18). px4io LEDs fitted; PA10 and PB11 pulled up (pin allocation rev 0.6). | IF-030 to IF-037, IF-049 to IF-051, OPEN-001 | Hardware | IN_PROGRESS | As for P1-001 |
| P1-003 | Allocate both SPI IMUs: CS, DRDY, bus ownership, DMA. No IMU reset line; reset is by software (DEC-009). Team: IMU pin 9 (INT2/CLKIN) not used (Q16). | SEN-001 | Hardware | OPEN | SPI allocation and timing review |
| P1-004 | Allocate both I2C barometers: addresses, pull-ups, recovery, bus ownership. Addresses set on I2C2: ICP-20100 0x63, BMP581 0x46, BMP384 fallback 0x76 (SEN-002, OPEN-019). Open: pull-ups and recovery. | SEN-002 | Hardware | OPEN | I2C address/bus review |
| P1-005 | Allocate the I2C magnetometer (IST8310, DEC-011): address (CAD0/CAD1), pull-ups, DRDY and RSTN use, recovery, placement constraints. Team: 0x0E, DRDY and RSTN not connected (Q11). | SEN-003 | Hardware | OPEN | I2C and magnetic-placement review |
| P1-006 | Allocate USB FS, VBUS sensing, ESD/protection, connector, and reset support for H743 flashing (proposed). | IF-022 | Hardware | OPEN | USB interface review and schematic net list |
| P1-007 | Allocate selectable H743 BOOT0 and define its default/reset behavior (proposed). | FUN-006, TST-003 | Hardware | OPEN | Boot-state table and circuit review |
| P1-008 | Allocate SWD access for both MCUs. H743: Pixhawk Debug Mini 6-pin JST-SH (console + SWD) plus an NRST pad. F100: SWD, NRST and console TX on pads, bench only (DEC-018). | FUN-005, IF-023, IF-045, IF-051, TST-001, TST-002 | Hardware | IN_PROGRESS | Debug-access review; pinout from PX4 docs (DS-009 not read) |
| P1-009 | Check alternate-function conflicts across every assigned pin. | OPEN-001, OPEN-003 | Hardware | OPEN | Conflict report with no unresolved critical conflicts |
| P1-010 | Check DMA, interrupt, timer/PWM, clock, and priority conflicts. | OPEN-003 | Hardware | OPEN | Resource matrix and resolution record |
| P1-011 | Check voltage domains, IO levels, pull states, reset states, and boot-time behavior. Includes the PWM pull-down value with bidirectional DShot on the motor lines (OPEN-018). | OPEN-018 | Hardware | OPEN | Electrical compatibility review |
| P1-012 | Review package pin availability, reserved pins, unused pins, and ERC/DRC implications. | OPEN-001 | Hardware | OPEN | Package/resource review |
| P1-013 | Record mapping revision, reviewer, date, conflicts, resolutions, and remaining obligations. | OPEN-001 | TBD | OPEN | Signed or attributable review record |
| P1-014 | Define clock sources, reset topology, watchdog use, and F100 boot behavior. Added by audit. Decided 2026-10-24: H743 16 MHz crystal, F100 24 MHz crystal used directly (stock px4io), no LSE, F100 BOOT0/BOOT1 pulled down, watchdogs per spec 4.4 (DEC-017). Open: crystal parts, load capacitors, reset topology. Re-decided 2026-10-24 with the IO MCU change (DEC-002). | Spec 4.4, DEC-017 | Hardware | IN_PROGRESS | Clock/reset/boot decision record |
| P1-015 | Check the BMP384 fallback against the BMP581 footprint, pinout and I2C address. Added 2026-10-24. | OPEN-019, CMP-004 | Hardware | OPEN | Datasheet comparison record |
| P1-016 | Pick the ESC current-sense ADC pin and the ESC telemetry UART RX. Dropped 2026-10-24: separate Skywalker ESCs, no current sense or telemetry (IF-052, IF-053 removed, OPEN-022 closed). | OPEN-022, DEC-023 | Hardware | N/A | Spec rev 0.14 change note |

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
| P2-010 | Complete the spec 4.7 calculations: board input current, servo rail current, rail tolerance, thermal margin, and safety response timing. Added by audit. | Spec 4.7, PWR-012 to PWR-014 | Hardware | OPEN | Calculation records with margins |
| P2-011 | Capture the power sheet (`power_supplies.kicad_sch`): power module input, `+VIN` to `+5V` path, TPS62142 3.3 V buck, `+3V3A` LDO, indicator. Does not depend on P1. Drawn so far: see spec 4.3 "Schematic state". Open: `+VIN` to `+5V` path (OPEN-012): TPS16412DRC eFuse placed (DEC-024), only GND wired, ILIM resistor for 1.5 A not drawn; `+3V3A` LDO part and its NR and output capacitors (rail use decided: IMUs only, DEC-025; OPEN-011), the 0.1 µF AVIN-to-AGND capacitor TI recommends for the TPS62142, annotation, LCSC C162430 on both the 1 µF (GCM188R71C105KA64J) and 10 µF (GRM21BZ71C106KE15L) capacitors, `PM02_SCL` / `PM02_SDA` going nowhere, the DNP DF2S6.2CT on `+VIN`. | DEC-012, DEC-024, OPEN-011, OPEN-012 | Hardware | IN_PROGRESS | Saved `power_supplies.kicad_sch`; power-sheet review record |
| P2-012 | Check the sensor footprints against the datasheet drawings and app notes: pad geometry, land pattern, pin 1 corner, 3D model. Pin maps already match the datasheet tables. IST8310 uses the stock symbol and `LGA-16_3x3mm_P0.5mm` footprint (fit `ESTIMATED`, no land pattern in the datasheet). See spec 4.6 "Library state". Bosch LGA-10 pads set to the BMP581 land pattern (DS004-13 Fig. 32) on 2026-10-21; the values were read from an image and need a human check. | OPEN-013, CMP-003 to CMP-005 | Human | IN_PROGRESS | Per-part review record naming the datasheet figure or app note used |
| P2-013 | Pick the weak pull-down and any series resistor on the PWM lines so bidirectional DShot still works on the motor lines. Added 2026-10-24. | OPEN-018, IF-040 to IF-043 | Hardware | OPEN | Calculation or reference design note, then the P4-011 bench result |
| P2-014 | Add the STM32F100C8T6B to the project library from stock KiCad `MCU_ST_STM32F1:STM32F100C8Tx` (`kicad-part-start`, then `kicad-link-audit`), and change the IO MCU text in `block_diagram.kicad_sch` from STM32F103C8T6. Added 2026-10-24. | MCU-002, CMP-002 | Hardware | OPEN | Library audit record; approved schematic change |
| P2-015 | Check the external connector pinouts against the Pixhawk connector standard (DS-009): Telemetry 1 and 2, GPS1 10-pin (3.3 V and buzzer pins), airspeed, TF-Luna. Change the PM02D connector to a 6-pin 2.00 mm CLIK-Mate to match its cable (decided 2026-10-24; the sheet still draws JST-GH; schematic change needs approval) and check PD12 and PD13 take 5 V I2C pull-ups. Added 2026-10-24. | OPEN-023, IF-010 to IF-015, IF-046, IF-048 | Hardware | OPEN | Pinout record citing DS-009 and the PM02D page |
| P2-016 | Design the on-board servo bus (DEC-019): check the board-mount XT30 UBEC input (decided 2026-10-24) against 10 A continuous and 15 A peak, size the 6 V and servo GND copper, pick where servo GND joins logic GND, and add bulk capacitance. Needs the stall current (P0-022). Added 2026-10-24. | OPEN-021, OPEN-007, DEC-019, IF-030 to IF-037, IF-050 | Hardware | OPEN | Calculation record (XT30 and copper current) and header part choice |
| P2-017 | Wire the TPS16412DRC eFuse (DEC-024) and set its parts from TI data: ILIM resistor for 1.5 A, OVP, EN/UVLO, dV/dt, FLT. Check reverse-current behavior with USB on `+5V`, and the 1.5 A limit against the board and external 5 V loads. Added 2026-10-24. | DEC-024, OPEN-012, OPEN-006, PWR-010 | Hardware | OPEN | Saved schematic; calculation record citing TI data |
| P2-018 | Draw the 4 ESC connectors: 3-pin headers with the + pin removed (IF-040 to IF-043). Added 2026-10-24. | IF-040 to IF-043 | Hardware | OPEN | Saved schematic |

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
| P3-011 | Route PWM/actuator outputs and the H743↔F100 USART with return path, drive, protection, voltage compatibility, and test access. Added by audit. | PCB-014, PCB-015 | TBD | BLOCKED BY P0, P2 | Layout review and electrical test |

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
| P4-011 | Halt the H743 over SWD while armed: measure the servo failsafe time at the F100 and the motor stop time at the ESC. Check bidirectional DShot RPM feedback with the chosen pull-downs. Added 2026-10-24. | SAF-015, OPEN-017, OPEN-018 | Team + Hardware | OPEN | Bench test record with ESC model and firmware |
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
| OI-001 | OPEN-008, SAF-001 | H743-failure behavior and F100 safety implementation | Closed 2026-10-24 by DEC-016: no landing; servo failsafe after 0.5 s; motors on the H743. Motor stop on a hang: OI-019. | Closed |
| OI-002 | OPEN-004 | Sensor MFR/MPN and electrical properties | Parts chosen: IMU 2 × ICM-45686 (DEC-008), barometers ICP-20100 + BMP581 (DEC-010), magnetometer IST8310 (DEC-011). Electrical properties `NOT_VERIFIED` except the IST8310 values in the selection record. ICP-20100 EOL, BMP581 stock and IST8310 lifecycle open. | Human owner / P0 |
| OI-003 | OPEN-001 | External interfaces and exact MCU pins | Logical allocation revised by the team (DEC-014, DEC-018). Pins in pin allocation rev 0.6; pinmap review 0.3 answered by the team (P0-020). Not in the schematic yet. | Hardware / P1 |
| OI-004 | OPEN-006, OPEN-007 | Power protection, transients, downstream budgets, and distribution | Input and servo ratings recorded; design details open. Servo current on the board (DEC-019), UBEC on a board-mount XT30; sizing waits on the team's stall-current test. 5 V input eFuse TPS16412DRC at 1.5 A (DEC-024). USB powers the board and all external 5 V ports on the bench; VBUS budget TBD. | Hardware / P0, P2; Team for OPEN-007 |
| OI-005 | OPEN-001, OPEN-003 | Exact MCU pin mapping and resource conflicts (overlaps OI-003) | Signals checked against ST pin data, no duplicate pins (pin allocation rev 0.6). OPEN-003 closed. DMA and interrupt checks (P1-010) not done by hardware. | Hardware / P1 |
| OI-006 | OPEN-002 | H743↔F100 USART implementation and software contract | Closed 2026-10-24 by DEC-015: px4io, USART6 ↔ USART2, 1.5 Mb/s. Test access stays with TST-006. | Closed |
| OI-007 | DEC-004 | PX4 target and bootloader plan | `DEFERRED`; non-blocking. | Software / post-hardware |
| OI-008 | OPEN-003, OPEN-008 | F100 PWM outputs and failsafe behavior | Closed 2026-10-24: 8 servos on the px4io-v2 timers (IF-030 to IF-037); failsafe values are PX4 parameters set after flight tests (D3). Electrical behavior unverified. | Closed |
| OI-009 | OPEN-009 | Exact outline, mounting, connector placement, and environment | Maximum envelope confirmed. Environment set (DEC-020). Set by the human owner on 2026-10-24: M3, 3.2 mm holes, soft mount, own tray, USB-C and microSD on adjacent edges, part height about 10 to 15 mm. Hardware sets the outline, cable entry sides and dampers at placement; the CAD team follows. | Human owner, then CAD team / P3 |
| OI-010 | OPEN-005 | Magnetometer count/allocation and sensor requirements | Closed: 1 magnetometer (DEC-011), now IST8310. | Team / closed 2026-10-18 |
| OI-011 | None (checklist only) | Physical actuator/ESC signal distribution | 4 ESCs on the H743 (TIM5) and 8 servos on the F100 (DEC-016). Servos plug into 3-pin headers on an on-board 6 V bus (DEC-019). Bus and UBEC input: OI-023. ESCs: 4 × Skywalker 80A V2 (team design); 3-pin headers with the + pin removed (P2-018). | Hardware / P2 |
| OI-012 | OPEN-010 | All non-MCU part numbers (added by audit) | Sensors (DEC-008, DEC-010, DEC-011) the main 3.3 V buck TPS62142RGTR (DEC-012) and the 5 V input eFuse TPS16412DRC (DEC-024) are chosen. No other non-MCU part is approved. | Human owner / component selection gate (P0-016) |
| OI-013 | OPEN-011 | `+3V3A` rail purpose, load and LDO part | Use decided 2026-10-26: the 2 IMUs only, VDD and VDDIO (DEC-025). Open: LDO part, load, SPI level match with the H743 and power-up order. TPS73533DRBR drawn, not decided. As drawn, NR capacitor above TI's limit and output capacitance at TI's minimum. | Human owner / P0, P2 |
| OI-014 | OPEN-012 | `+VIN` to `+5V` path | TPS16412DRC eFuse chosen (DEC-024), placed but not wired; both regulators have no input source yet. | Hardware / P2 (P2-011, P2-017) |
| OI-015 | OPEN-013 | Sensor symbol and footprint starting points | In the project library, not placed. Pin maps match the datasheet tables; land patterns and pin 1 not checked. IST8310 uses the stock symbol and footprint (fit `ESTIMATED`). Bosch LGA-10 pads follow BMP581 Fig. 32 (image-read, not checked). | Human owner / P2 (P2-012) |
| OI-016 | OPEN-014 | Second barometer part number | Closed 2026-10-24: BMP581, BMP384 fallback (DEC-010). | Closed |
| OI-017 | OPEN-015 | IO MCU clock for stock px4io | Closed 2026-10-24 by DEC-017: STM32F100C8T6B with a 24 MHz crystal, stock px4io and stock bootloader. Replaces the earlier F103 with an 8 MHz crystal and a custom px4io. | Closed |
| OI-018 | OPEN-016 | Spec rows changed by the team's pinmap answers | Closed 2026-10-24: applied in spec rev 0.11. | Closed |
| OI-019 | OPEN-017 | Motor stop on an H743 hang depends on the ESC's signal-loss behavior | ESC: 4 × Skywalker 80A V2 (team design), DShot support `NOT_VERIFIED`, looks PWM-only. Conflicts with FUN-002 and SAF-015; asked in D13. | Team + Hardware / P4 (P4-011) |
| OI-020 | OPEN-018 | PWM pull-down value with bidirectional DShot | Value TBD. | Hardware / P2 (P2-013), P4 (P4-011) |
| OI-021 | OPEN-019 | BMP384 fallback fit against the BMP581 | Not checked. | Hardware / P1 (P1-015) |
| OI-022 | OPEN-020 | STM32F100 datasheet values | Closed 2026-10-24: HSE 4 to 24 MHz, VDD 2 to 3.6 V, POR/PDR and PVD, 5 V tolerance checked (DocID16455 Rev 9). | Closed |
| OI-023 | OPEN-021 | On-board servo bus and UBEC input rating | Headers chosen (DEC-019); UBEC input on a board-mount XT30 (2026-10-24). XT30 rating against 10 A / 15 A `NOT_VERIFIED`. Copper, GND join and bulk capacitance open. | Hardware / P2 (P2-016) |
| OI-024 | OPEN-022 | ESC current sense and telemetry pins | Closed 2026-10-24: dropped (IF-052, IF-053 removed). PC1 stays reserved (DEC-023). | Closed |
| OI-025 | OPEN-023 | External connector pinouts and the PM02D connector | DS-009 not read. GPS1 10-pin extra pins and I2C4 5 V tolerance open. PM02D: CLIK-Mate chosen, sheet still JST-GH. | Hardware / P2 (P2-015) |

## Current next action

Integration answers are in (P0-021, spec rev 0.13) and hardware set mounting, ESC connector, UBEC XT30, PM02D connector and the 5 V eFuse (spec rev 0.14). Send integration questions rev 0.4 and collect the team inputs, mainly D13 on the ESC (P0-022). Wire the TPS16412DRC eFuse and set its parts from TI data (P2-017). Check the connector pinouts against the Pixhawk standard and change the PM02D connector to CLIK-Mate (P2-015), the servo bus and XT30 input (P2-016), and draw the ESC headers (P2-018). Human review of the pin choices in pin allocation rev 0.6 (P1-001, P1-002). Add the STM32F100C8T6B library part and fix the block diagram text (P2-014). Continue the power sheet (P2-011): re-check its saved state, since the spec 4.3 table and the README disagree on the part count and the DF2S6.2CT; connect `+VIN` to `+5V`, pick the `+3V3A` LDO for the IMUs (DEC-025) and fix its NR and output capacitors if TPS73533DRBR stays, fix the C162430 LCSC field, then annotate. Check the BMP384 fallback (P1-015) and the sensor footprints against the datasheets (P2-012) before placing them. Pick the PWM pull-down value (P2-013). Keep sensor-specific resources provisional until the sensor requirements are decided. Keep the candidate/unverified label on all pin mappings. Reserve the USART safety path and test access. Do not begin fabrication release until the applicable P0 to P3 evidence and Human approval are complete.
