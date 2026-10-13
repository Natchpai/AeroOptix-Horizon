# AeroOptix-Horizon — Execution Checklist

**Revision:** 0.2
**Updated:** 2026-10-13
**Status:** Active execution tracker; not an approval or verification record
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md)

Use the specification for confirmed requirements and design decisions. This checklist records the sequence of work and evidence needed to close each gate. Diagram content is reference material; user-confirmed requirements take precedence. Sensor choices remain TBD.

## Status rules

- `[x]` — Requirement or decision confirmed, or task completed with the stated evidence.
- `[ ]` — Open, proposed, TBD, or lacking required evidence.
- `NOT_VERIFIED` — Implementation or result lacks sufficient evidence.
- `BLOCKED` — Work cannot close until an upstream decision or artifact exists.
- `DEFERRED` — Assigned to a later owner or stage; not a hardware approval.

A checkbox does not imply that implementation has been measured or verified. Counts, candidate mappings, and file presence are not evidence by themselves.

## Current checkpoint

- [x] Project scope: custom PX4 flight controller; H743 main MCU; F103 operational auxiliary MCU and the specified external interfaces.
- [x] Software-owned/deferred items: PX4 target, bootloader, QGC workflow, and detailed USART/safety behavior.
- [x] Board input: 5 V ±10% (4.5–5.5 V), 2 A source capacity.
- [x] Servo rail: 6 V, 10 A continuous and 15 A instantaneous, based on the user-provided UBEC-10A specification reference; component selection is not approved.
- [x] Maximum PCB envelope: each dimension less than 80 mm × 80 mm. Exact outline, mounting, and connector placement remain open for P3.
- [ ] Sensor MFR/MPN and sensor-specific operating requirements remain TBD.
- [ ] P1 MCU pin/resource review and exact mapping are incomplete.
- [ ] Native schematic, PCB, fabrication package, and bring-up evidence are not established in this documents set.

## P0 — Architecture-impacting requirements

**Exit gate:** No unresolved requirement prevents MCU-resource, bus, connector, or power-architecture allocation. Sensor-specific choices remain explicitly TBD and must block only the allocations they affect.

### P0.1 Scope and operating intent

- [x] `P0-001` Define the flight-controller role and system boundary. **Status:** Scope confirmed by the user on 2026-10-13.
- [x] `P0-002` Record PX4 target/version and supported modes as Software-owned deferred work. **Status:** `DEFERRED / NON-BLOCKING`; hardware decision not required to proceed.
- [x] `P0-003` Define first-revision scope. **Status:** H743 main control, F103 auxiliary I/O/PWM/safety, and the stated external interfaces are in scope; PX4/bootloader/QGC and detailed software behavior are deferred.

### P0.2 MCU and safety boundary

- [x] `P0-004` Confirm STM32H743VIT6 as the main MCU. **Status:** Requirement confirmed; implementation not verified.
- [x] `P0-005` Confirm STM32F103C8T6 as operational auxiliary I/O/PWM/ESC/safety MCU. **Status:** Requirement confirmed; implementation not verified.
- [x] `P0-006` Reserve H743↔F103 USART. **Status:** Interface confirmed; pins, levels, instance, rate, and test access remain for P1/P2.
- [x] `P0-007` Record immediate-landing requirement if H743 is unavailable. **Status:** USART is the monitoring path; detailed detection, command behavior, and timing belong to Software. Hardware must preserve the physical path and test access.

### P0.3 Sensors

- [ ] `P0-008` Select two IMU MFR/MPNs. **Status:** `TBD`; diagram-listed parts are candidates only.
- [ ] `P0-009` Select two barometer MFR/MPNs. **Status:** `TBD`; diagram-listed parts are candidates only.
- [ ] `P0-010` Decide magnetometer MFR/MPN and onboard/external allocation. **Status:** `TBD`.
- [ ] `P0-011` Define sensor rates, DRDY/interrupt needs, calibration, and redundancy. **Status:** `TBD`.

### P0.4 Interfaces, power, actuators, and envelope

- [x] `P0-012` Confirm logical H743/F103 external interface allocations. **Status:** Confirmed; exact pins and electrical implementation remain unverified. See specification section 3.
- [x] `P0-013` Confirm board and servo power requirements. **Status:** Board input 5 V ±10%, 2 A source capacity; servo 6 V, 10 A continuous / 15 A instantaneous. Protection, transients, distribution, and component choice remain open.
- [x] `P0-014` Confirm logical F103 PWM/expanded-I/O functions. **Status:** TILT, ESC, COAX, AIL, and FlySky requirements captured; timer/channel validity and electrical implementation remain unverified.
- [x] `P0-015` Confirm maximum PCB envelope. **Status:** Each dimension <80 mm × 80 mm. Exact shape, mounting, connector orientation, and environment remain open for P3.

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

> **Status rule:** Any candidate pin mapping must remain labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete.

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

| ID | Open item | Current status | Owner / target |
|---|---|---|---|
| OI-001 | Immediate-landing requirement and F103 safety implementation | Requirement confirmed; detailed behavior/timing Software-owned and deferred | Software / P2, P4 |
| OI-002 | Sensor MFR/MPN and electrical properties | `TBD`; diagram suggestions are not selections | Human owner / P0 |
| OI-003 | External interfaces and exact MCU pins | Logical requirements confirmed; mapping unverified | Hardware / P1 |
| OI-004 | Power protection, transients, downstream budgets, and distribution | Input and servo ratings recorded; design details open | Hardware / P0, P2 |
| OI-005 | Exact MCU pin mapping and resource conflicts | `NOT_VERIFIED` | Hardware / P1 |
| OI-006 | H743↔F103 USART implementation and software contract | Physical protocol confirmed; detailed software contract deferred | Hardware + Software / P1, P2 |
| OI-007 | PX4 target and bootloader plan | `DEFERRED / NON-BLOCKING` | Software / post-hardware |
| OI-008 | F103 PWM outputs and failsafe behavior | Logical functions confirmed; timer AF/electrical behavior unverified | Hardware + Software / P1, P2 |
| OI-009 | Exact outline, mounting, connector placement, and environment | Maximum envelope confirmed; remaining mechanics TBD | Human owner / P3 |
| OI-010 | Magnetometer count/allocation and sensor requirements | `TBD` | Human owner / P0 |
| OI-011 | Physical actuator/ESC signal distribution | Diagram captured; native allocation and fanout require review | Hardware / P1, P2 |

## Current next action

Continue P1 allocation and conflict review using the confirmed logical interfaces. Keep sensor-specific resources provisional until the sensor requirements are decided. Preserve the candidate/unverified label on all pin mappings, and reserve the USART safety path and test access. Do not begin fabrication release until the applicable P0–P3 evidence and Human approval are complete.

