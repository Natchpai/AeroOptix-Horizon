# AeroOptix-Horizon — Execution Checklist

**Document status:** Draft checklist / not an approval record  
**Current design status:** `DESIGN DRAFT — NOT VERIFIED / NOT READY FOR FABRICATION`  
**Source handoff:** `AO-HORIZON_HANDOFF_EN.md`

This checklist tracks closure from the current architecture draft through schematic, PCB, fabrication, and bring-up. A checked item means that the required evidence exists; it does not mean that a design target has been measured unless the evidence explicitly contains a measurement.

## Status rules

- `[x]` — Confirmed or completed with traceable evidence
- `[ ]` — Open, proposed, TBD, or not yet supported by sufficient evidence
- `NOT_VERIFIED` — A claim or result is not supported by the required evidence
- `BLOCKED` — Cannot close until an upstream decision or artifact is available
- `DEFERRED` — Intentionally postponed with an owner and follow-up point

Do not mark an item complete from a count, assumption, candidate mapping, or implementation report alone.

## Hardware-first execution rule

Firmware integration details are explicitly **DEFERRED / NON-BLOCKING** by human direction. Hardware work may proceed without a final PX4 target, bootloader, firmware contract, or software flashing implementation. Hardware shall still reserve the required electrical interfaces, pins, reset/boot access, and test points so the Software team can select the implementation later.

## Current checkpoint

- [x] English handoff document exists.
- [x] Confirmed/proposed/TBD distinctions are recorded.
- [x] Main baseline is recorded as H743 + F103.
- [x] Confirmed sensor interface quantities are recorded.
- [x] USB FS/QGC, selectable BOOT0, and SWD requirements are recorded.
- [x] Firmware integration details are recorded as deferred and non-blocking for the hardware path.
- [ ] P0 architecture-impacting requirements are closed.
- [ ] P1 pin/resource conflict review is complete.
- [ ] Exact pin mapping is verified.
- [ ] Schematic, firmware contract, PCB, fabrication package, and bring-up evidence exist.

## Part-number confirmation boundary

Only the following part numbers are currently confirmed by the user:

- `STM32H743VIT6`
- `STM32F103C8T6`

The H743↔F103 interface protocol is confirmed as `USART`. All other part numbers visible in diagrams or listed as candidates remain `UNCONFIRMED / TBD`, including sensors, regulators, protection devices, power modules, PDB/UBEC devices, connectors, and interface ICs.

## Diagram-derived hardware snapshot

The following items are transcribed from the user-provided architecture and power diagrams. They are **SOURCE IMAGE / PROPOSED / NOT VERIFIED** until the native design source, part list, and engineering review confirm them.

- [ ] `IMG-001` Intended controller board is labeled `FC_H743 rev2`, with an approximate envelope of `~90 mm × 95 mm`. **Status:** `SOURCE IMAGE / NOT VERIFIED`  
  **Required confirmation:** Board revision, exact outline, mounting pattern, and whether the dimensions are final design targets.
- [x] `IMG-002` Confirmed MCU part numbers are `STM32H743VIT6` and `STM32F103C8T6`. **Status:** `CONFIRMED PART NUMBERS / IMPLEMENTATION NOT VERIFIED`  
  **Required confirmation:** Native design placement, exact package data, final pin allocation, and electrical implementation.
- [ ] `IMG-003` IMU candidates shown are `ICM-42688-P` and `BMI088`. **Status:** `SOURCE IMAGE / PROPOSED`  
  **Required confirmation:** MFR/MPN approval, supply/IO voltage, bus assignment, data-ready behavior, and driver suitability.
- [ ] `IMG-004` Barometer candidates shown are `BMP280` and `MS5611`. **Status:** `SOURCE IMAGE / PROPOSED`  
  **Required confirmation:** MFR/MPN approval, bus/address strategy, pressure range, and environmental/placement requirements.
- [ ] `IMG-005` `IST8310` is visible as an onboard magnetometer candidate. **Status:** `SOURCE IMAGE / PROPOSED`  
  **Required confirmation:** Identify the second magnetometer required by the current baseline, or confirm that an external GPS/compass module supplies it.
- [ ] `IMG-006` USB FS protection, microSD, SWD, telemetry/GPS/RC/UART, safety, companion-computer, air-data/rangefinder, and actuator-related blocks are shown. **Status:** `SOURCE IMAGE / NOT VERIFIED`  
  **Required confirmation:** Exact interface list, connector count, electrical standard, and ownership.
- [ ] `IMG-007` Power diagram shows a 6S battery path through XT90-S, PM02D, and CRIUS PDB v1.0, with 5 V, 3.3 V, 3.3 V_IMU, and a separate 6 V UBEC path shown. **Status:** `SOURCE IMAGE / NOT VERIFIED`  
  **Required confirmation:** Input limits, rail current budgets, protection, sequencing, and whether the diagram is the approved power architecture.
- [ ] `IMG-008` Four ESC paths are visibly labeled in the power diagram; servo/actuator channel count is not sufficiently clear from the image. **Status:** `SOURCE IMAGE / NOT VERIFIED`  
  **Required confirmation:** ESC count, servo count, output levels, current/drive method, and failsafe hardware requirements.

## User-confirmed hardware requirements

The following requirements were provided directly by the user on 2026-10-12. They are treated as confirmed requirements, while pin alternate functions, electrical implementation, timing, and safety behavior remain subject to P1/P2 verification.

### F103 role and H743 link

- [x] `USR-001` STM32F103C8T6 is required for operation, not only development. **Status:** `CONFIRMED REQUIREMENT`
- [x] `USR-002` F103 provides auxiliary I/O, controls PWM for all ESC-related outputs, and expands I/O. **Status:** `CONFIRMED REQUIREMENT`
- [x] `USR-003` If the H743 is not operating, the F103 shall command immediate landing. **Status:** `CONFIRMED SAFETY REQUIREMENT / IMPLEMENTATION NOT VERIFIED`  
  **Open detail:** Fault detection, landing command path, output ownership, timing, and the behavior when the F103 itself cannot act.
- [x] `USR-004` H743↔F103 interface protocol is USART. **Status:** `CONFIRMED INTERFACE PROTOCOL / IMPLEMENTATION NOT VERIFIED`  
  **Open detail:** USART instance, pins, voltage levels, baud/rate, framing, timeout, redundancy, and test access.

### H743 external interfaces

| Connector / function | User-provided allocation | Status |
|---|---|---|
| Conn1 | Tel1 — UART7 | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn2 | Tel2 — UART1 | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn3 | GPS1 + Compass — UBX via UART2; compass via I2C1 | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn4 | GPS2 — UART3, currently blank | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn5 | MS4525DO — I2C4, address `0x28` | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn6 | TF-Luna — UART8 | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn7 | UART7 TX, currently blank | **CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED** |
| Conn8 | VT L — TIM4_CH3 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| Conn9 | VT R — TIM4_CH4 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| Conn10 | SP2 — TIM1_CH1, currently blank | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| Conn11 | TL2 — TIM15_CH1 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| Conn12 | TR2 — TIM15_CH2 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| USB | USB FS | **CONFIRMED REQUIREMENT / HARDWARE PATH NOT VERIFIED** |
| Debug | SWD | **CONFIRMED REQUIREMENT / HARDWARE ACCESS NOT VERIFIED** |

### F103 PWM and expanded I/O

| Logical output | User-provided allocation | Status |
|---|---|---|
| TILT L | TIM2_CH1 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| TILT R | TIM2_CH2 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| ESC L | TIM4_CH3 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| ESC R | TIM4_CH4 | **CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED** |
| COAX T | TIM3_CH5 | **CONFIRMED LOGICAL LABEL / MCU RESOURCE NOT VERIFIED** |
| COAX B | TIM3_CH6 | **CONFIRMED LOGICAL LABEL / MCU RESOURCE NOT VERIFIED** |
| AIL L | TIM3_CH7 | **CONFIRMED LOGICAL LABEL / MCU RESOURCE NOT VERIFIED** |
| AIL R | TIM3_CH8 | **CONFIRMED LOGICAL LABEL / MCU RESOURCE NOT VERIFIED** |
| FlySky | Pinheader bulk / connector unspecified | **CONFIRMED REQUIREMENT / PINOUT TBD** |

> Timer/channel labels above are captured verbatim from the user input. They are not claims that the STM32F103 package or alternate-function matrix supports those labels. P1 must validate every timer/channel assignment against the selected MCU package and electrical design.

### Power input

- [x] `USR-005` Flight-controller board input is `5 V from power module`. **Status:** `CONFIRMED REQUIREMENT / LIMITS TBD`
- [x] `USR-006` Servo power is `6 V`. **Status:** `CONFIRMED REQUIREMENT / CURRENT BUDGET TBD`
- [ ] `USR-007` Upstream battery/PDB arrangement shown in the diagrams is the approved system power architecture. **Status:** `SOURCE IMAGE / NOT VERIFIED`

## P0 — Architecture-impacting requirement closure

**Exit gate:** No remaining `TBD` prevents selection of MCU resources, bus topology, connector strategy, or power architecture.

### P0.1 System scope and operating intent

- [ ] `P0-001` Define the flight-controller role and system boundary. **Status:** `TBD`  
  **Evidence required:** Approved system-scope statement.
- [ ] `P0-002` Record the PX4 version, board target strategy, and supported operating modes as a software-owned deferred item. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later versioned firmware-target decision; not required to close the hardware architecture gate.
- [ ] `P0-003` Define in-scope and out-of-scope functions for the first hardware revision. **Status:** `TBD`  
  **Evidence required:** Scope baseline with owner approval.

### P0.2 MCU architecture

- [x] `P0-004` Confirm the final role of STM32H743VIT6 as the main flight-controller MCU. **Status:** `CONFIRMED REQUIREMENT / IMPLEMENTATION NOT VERIFIED`  
  **Evidence required:** Responsibility matrix and hardware review.
- [x] `P0-005` Confirm the final role of STM32F103C8T6 as the operational auxiliary I/O, PWM, ESC, and safety controller. **Status:** `CONFIRMED REQUIREMENT / IMPLEMENTATION NOT VERIFIED`  
  **Evidence required:** Responsibility matrix, flight-use policy, and recovery behavior.
- [x] `P0-006` Reserve a USART physical/electrical H743↔F103 communication path; defer protocol and software ownership. **Status:** `CONFIRMED INTERFACE / IMPLEMENTATION NOT VERIFIED`  
  **Evidence required:** USART instance, pins, voltage compatibility, test access, and deferred-protocol note.
- [x] `P0-007` Define the hardware safety requirement that F103 commands immediate landing if H743 is not operating; defer firmware implementation details. **Status:** `CONFIRMED SAFETY REQUIREMENT / IMPLEMENTATION NOT VERIFIED`  
  **Evidence required:** Fault-detection and landing-command hardware boundary, timing target, reset/boot access, and recovery plan.

### P0.3 Sensor selection and requirements

- [ ] `P0-008` Confirm the IMU MFR/MPN candidates shown in the diagram: `ICM-42688-P` and `BMI088`. **Status:** `PROPOSED / SOURCE IMAGE`  
  **Evidence required:** Approved parts list with availability, driver, voltage, range, rate, package, and placement review.
- [ ] `P0-009` Confirm the barometer MFR/MPN candidates shown in the diagram: `BMP280` and `MS5611`. **Status:** `PROPOSED / SOURCE IMAGE`  
  **Evidence required:** Approved parts list with address, voltage, driver, pressure range, and placement review.
- [ ] `P0-010` Resolve the second-magnetometer requirement against the diagram, which visibly identifies `IST8310` and an external GPS/compass-related block. **Status:** `OPEN / NOT_VERIFIED`  
  **Evidence required:** Explicit onboard/external sensor allocation and approved parts list.
- [ ] `P0-011` Define sensor sample rates, interrupt/data-ready behavior, calibration needs, and redundancy policy. **Status:** `TBD`  
  **Evidence required:** Sensor requirements table linked to the PX4 configuration.

### P0.4 External interfaces, power, and actuators

- [x] `P0-012` Confirm the H743 and F103 external interface allocations provided by the user. **Status:** `CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED`  
  **Evidence required:** Connector-level interface table, exact MCU pins, electrical standards, and resource review.
- [x] `P0-013` Confirm the board power inputs provided by the user: 5 V from the power module and 6 V for servo power. **Status:** `CONFIRMED REQUIREMENT / LIMITS NOT DEFINED`  
  **Evidence required:** Approved power tree, input limits, rail current budgets, sequencing, brownout, and protection review.
- [x] `P0-014` Confirm F103 PWM/expanded-I/O requirements for ESC, tilt, coax, aileron, and FlySky connections. **Status:** `CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED`  
  **Evidence required:** Actuator/I/O requirement table with exact resource validation, output levels, update rate, current/drive method, and failsafe behavior.
- [ ] `P0-015` Confirm the approximate `~90 mm × 95 mm` board envelope and mechanical constraints shown in the diagram. **Status:** `PROPOSED / SOURCE IMAGE`  
  **Evidence required:** Mechanical constraint record with exact outline, mounting, connector orientation, and environmental limits.

## P1 — MCU allocation and conflict review

**Exit gate:** The mapping has actual pins and alternate functions, passes documented resource checks, and has review evidence. It may then be called `ALLOCATED`; it is not yet automatically `VERIFIED`.

- [ ] `P1-001` Assign exact H743 pins and alternate functions for all confirmed and approved interfaces. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Versioned MCU pin-allocation table.
- [ ] `P1-002` Assign exact F103 pins and alternate functions for its approved role. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Versioned F103 pin-allocation table.
- [ ] `P1-003` Allocate both SPI IMUs, including CS, DRDY, reset, bus ownership, and DMA. **Status:** `NOT_VERIFIED`  
  **Evidence required:** SPI allocation and timing review.
- [ ] `P1-004` Allocate both I2C barometers, including addresses, pull-ups, recovery, and bus ownership. **Status:** `NOT_VERIFIED`  
  **Evidence required:** I2C address/bus review.
- [ ] `P1-005` Allocate both I2C magnetometers, including addresses, pull-ups, recovery, and placement constraints. **Status:** `NOT_VERIFIED`  
  **Evidence required:** I2C and magnetic-placement review.
- [ ] `P1-006` Allocate USB FS, VBUS sensing, ESD/protection, connector, and reset support for H743 flashing. **Status:** `PROPOSED / NOT_VERIFIED`  
  **Evidence required:** USB interface review and schematic net list.
- [ ] `P1-007` Allocate selectable H743 BOOT0 and define its default/reset behavior. **Status:** `PROPOSED / NOT_VERIFIED`  
  **Evidence required:** Boot-state table and circuit review.
- [ ] `P1-008` Allocate SWD access for both MCUs, including SWDIO, SWCLK, NRST, GND, and probe access. **Status:** `PROPOSED / NOT_VERIFIED`  
  **Evidence required:** Debug-access review.
- [ ] `P1-009` Check alternate-function conflicts across every assigned pin. **Status:** `OPEN`  
  **Evidence required:** Conflict report with no unresolved critical conflicts.
- [ ] `P1-010` Check DMA, interrupt, timer/PWM, clock, and priority conflicts. **Status:** `OPEN`  
  **Evidence required:** Resource matrix and resolution record.
- [ ] `P1-011` Check voltage domains, IO levels, pull states, reset states, and boot-time behavior. **Status:** `OPEN`  
  **Evidence required:** Electrical compatibility review.
- [ ] `P1-012` Review package pin availability, reserved pins, unused pins, and ERC/DRC implications. **Status:** `OPEN`  
  **Evidence required:** Package/resource review.
- [ ] `P1-013` Record mapping revision, reviewer, date, conflicts, resolutions, and remaining obligations. **Status:** `OPEN`  
  **Evidence required:** Signed or attributable review record.

> **Mandatory statement:** Candidate pin mapping v0.1 must remain labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete.

## P2 — Schematic and hardware interface boundary

**Exit gate:** Hardware schematic review is closed, electrical interfaces and reserved resources are documented, and no unresolved hardware blocker affects bring-up. Firmware ownership, PX4 target, bootloader, and software protocol details may remain deferred.

- [ ] `P2-001` Create the schematic from the P1 allocation. **Status:** `BLOCKED BY P1`  
  **Evidence required:** Versioned native schematic.
- [ ] `P2-002` Implement USB FS, BOOT0, SWD, reset, power, and protection circuits. **Status:** `BLOCKED BY P1`  
  **Evidence required:** Schematic review evidence.
- [ ] `P2-003` Implement sensor buses, addresses, CS/DRDY, pull-ups, and recovery provisions. **Status:** `BLOCKED BY P0/P1`  
  **Evidence required:** Sensor interface review.
- [ ] `P2-004` Define hardware net names and connector pinout while reserving resources for later firmware mapping. **Status:** `BLOCKED BY P0/P1`  
  **Evidence required:** Hardware net/connector cross-check.
- [ ] `P2-005` Create the PX4 board configuration and bootloader plan. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later versioned firmware configuration and build/flash procedure; not a hardware release blocker.
- [ ] `P2-006` Define the H743 USB FS/QGC flashing workflow for both MCU firmware images. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later reproducible software procedure and test record; hardware shall preserve the physical path and access.
- [ ] `P2-007` Define H743↔F103 firmware ownership, protocol version, startup, timeout, and fault behavior. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later versioned firmware interface contract; hardware shall document the reserved electrical path before schematic freeze.
- [ ] `P2-008` Run ERC and resolve or disposition all relevant findings. **Status:** `NOT_VERIFIED`  
  **Evidence required:** ERC output and issue disposition.
- [ ] `P2-009` Complete line-by-line schematic review. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Review checklist with reviewer and evidence links.

## P3 — PCB and fabrication release

**Exit gate:** PCB, BOM, fabrication data, and release manifest are reviewed and approved by the Human engineering owner.

- [ ] `P3-001` Confirm board envelope, mounting, connector placement, and service/debug access. **Status:** `TBD`  
  **Evidence required:** Mechanical constraint review.
- [ ] `P3-002` Place IMUs, barometers, magnetometers, clock, power, USB, and debug interfaces according to their constraints. **Status:** `BLOCKED BY P0/P2`  
  **Evidence required:** Placement review.
- [ ] `P3-003` Route power and return paths with documented current and noise assumptions. **Status:** `BLOCKED BY P0/P2`  
  **Evidence required:** Power/layout review.
- [ ] `P3-004` Route USB FS and high-sensitivity sensor/debug signals with appropriate layout review. **Status:** `BLOCKED BY P0/P2`  
  **Evidence required:** Signal/layout review.
- [ ] `P3-005` Run DRC and disposition all relevant findings. **Status:** `NOT_VERIFIED`  
  **Evidence required:** DRC output and issue disposition.
- [ ] `P3-006` Review thermal/current constraints and manufacturability. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Manufacturing and thermal review.
- [ ] `P3-007` Confirm BOM, footprints, alternates, assembly notes, and test-point access. **Status:** `TBD`  
  **Evidence required:** Controlled BOM and assembly review.
- [ ] `P3-008` Create a hardware release package linked to schematic, PCB, BOM, and the deferred-firmware status. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Hardware release manifest that explicitly records firmware integration as deferred.
- [ ] `P3-009` Obtain Human engineering-owner approval for fabrication release. **Status:** `NOT_VERIFIED`  
  **Evidence required:** Explicit approval record.

## P4 — Bring-up and validation

**Exit gate:** Repeatable bench evidence exists, and all remaining issues have an owner and a defined disposition.

- [ ] `P4-001` Inspect the assembled board for shorts, assembly defects, polarity, and component identity. **Status:** `NOT_STARTED`  
  **Evidence required:** Inspection record.
- [ ] `P4-002` Verify power rails, sequencing, reset behavior, and current consumption before firmware loading. **Status:** `NOT_STARTED`  
  **Evidence required:** Measured bring-up log.
- [ ] `P4-003` Verify SWD access for H743. **Status:** `NOT_STARTED`  
  **Evidence required:** Probe/session log.
- [ ] `P4-004` Verify SWD access for F103. **Status:** `NOT_STARTED`  
  **Evidence required:** Probe/session log.
- [ ] `P4-005` Verify the H743 USB FS hardware path, connector, protection, continuity, and relevant electrical behavior. **Status:** `NOT_STARTED`  
  **Evidence required:** Hardware inspection/measurement record; host enumeration may remain deferred.
- [ ] `P4-006` Verify firmware flashing through QGC for the approved workflow. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later reproducible software test record.
- [ ] `P4-007` Verify bootloader, PX4 startup, sensor detection, and calibration flow. **Status:** `DEFERRED / NON-BLOCKING`  
  **Evidence required:** Later firmware/console/test log.
- [ ] `P4-008` Verify the H743↔F103 physical link, electrical levels, continuity, and test access; defer protocol behavior. **Status:** `NOT_STARTED / SOFTWARE DEFERRED`  
  **Evidence required:** Hardware link test record and later software protocol test record.
- [ ] `P4-009` Verify actuator outputs, arming behavior, failsafe behavior, and fault handling. **Status:** `NOT_STARTED`  
  **Evidence required:** Safety/actuator test record.
- [ ] `P4-010` Record hardware revision, firmware revision, test conditions, measurements, and deviations. **Status:** `NOT_STARTED`  
  **Evidence required:** Controlled bring-up report.

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

## Open-item register

| ID | Open item | Status | Owner | Evidence / decision link | Target gate |
|---|---|---|---|---|---|
| OI-001 | Final F103 role and immediate-landing safety behavior | `CONFIRMED REQUIREMENT / IMPLEMENTATION NOT VERIFIED` | `TBD` | `TBD` | P0/P1/P2 |
| OI-002 | Sensor MFR/MPN selection from the diagrams | `PROPOSED / SOURCE IMAGE` | `TBD` | `TBD` | P0 |
| OI-003 | External I/O and connector list from user confirmation | `CONFIRMED REQUIREMENT / PIN IMPLEMENTATION NOT VERIFIED` | `TBD` | `TBD` | P0/P1 |
| OI-004 | 5 V board input, 6 V servo rail, and current budgets | `CONFIRMED REQUIREMENT / LIMITS TBD` | `TBD` | `TBD` | P0/P2 |
| OI-005 | Exact MCU pin mapping | `NOT_VERIFIED` | `TBD` | `TBD` | P1 |
| OI-006 | H743↔F103 USART physical path and later protocol | `CONFIRMED INTERFACE / PROTOCOL DEFERRED` | `TBD` | `TBD` | P0/P1/P2 |
| OI-007 | PX4 board target and bootloader plan | `DEFERRED / NON-BLOCKING` | `Software` | `TBD` | Post-hardware |
| OI-008 | F103 PWM/expanded-I/O allocation and failsafe behavior | `CONFIRMED REQUIREMENT / TIMER AF NOT VERIFIED` | `TBD` | `TBD` | P0/P1/P2 |
| OI-009 | Mechanical and environmental constraints | `TBD` | `TBD` | `TBD` | P0/P3 |
| OI-010 | Second magnetometer allocation | `OPEN / NOT_VERIFIED` | `TBD` | `TBD` | P0 |
| OI-011 | ESC and servo/actuator channel count | `OPEN / NOT_VERIFIED` | `TBD` | `TBD` | P0 |

## Current next action

Close the remaining hardware P0 items, especially `P0-010`, `P0-013`, and `P0-015`. Then start P1 validation of the user-provided H743/F103 USART, timer/channel, pin, voltage, and safety-resource allocations. Keep firmware-target, bootloader, QGC, and software-protocol items explicitly deferred. Do not treat the candidate pin mapping as an implementation baseline until the P1 conflict review has been completed.

