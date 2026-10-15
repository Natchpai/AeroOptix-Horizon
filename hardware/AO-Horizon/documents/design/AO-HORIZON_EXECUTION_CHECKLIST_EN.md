# AeroOptix-Horizon: Execution Checklist

**Revision:** 0.2
**Updated:** 2026-10-13
**Status:** Active execution tracker; not an approval or verification record
**Requirements authority:** [AO-HORIZON_SPEC_EN.md](AO-HORIZON_SPEC_EN.md)

Use the specification for confirmed requirements and decisions. This checklist records the sequence of work and the evidence needed to close each gate. Diagram content is reference material. User-confirmed requirements take precedence. Sensor choices remain TBD.

## Status rules

- `[x]`: requirement or decision confirmed, or task completed with the stated evidence.
- `[ ]`: open, proposed, TBD, or lacking required evidence.
- `NOT_VERIFIED`: implementation or result lacks sufficient evidence.
- `BLOCKED`: work cannot close until an upstream decision or artifact exists.
- `DEFERRED`: assigned to a later owner or stage; not a hardware approval.

A checkbox does not mean the implementation was measured or verified. Counts, candidate mappings, and file presence are not evidence by themselves.

## Current checkpoint

- [x] Project scope: custom PX4 flight controller; H743 main MCU; F103 operational auxiliary MCU and the specified external interfaces.
- [x] Software-owned/deferred items: PX4 target, bootloader, QGC workflow, and detailed USART/safety behavior.
- [x] Board input: 5 V ±10% (4.5–5.5 V), 2 A source capacity.
- [x] Servo rail: 6 V, 10 A continuous and 15 A instantaneous, from the user-provided UBEC-10A specification reference. Component selection is not approved.
- [x] Maximum PCB envelope: each dimension less than 80 mm × 80 mm. Exact outline, mounting, and connector placement remain open for P3.
- [ ] Sensor MFR/MPN and sensor-specific operating requirements remain TBD.
- [ ] P1 MCU pin/resource review and exact mapping are incomplete.
- [ ] Native schematic, PCB, fabrication package, and bring-up evidence are not established in this documents set.

## P0: Architecture-impacting requirements

**Exit gate:** No unresolved requirement prevents MCU-resource, bus, connector, or power-architecture allocation. Sensor-specific choices stay TBD and block only the allocations they affect.

Groups: P0.1 scope and operating intent (P0-001 to P0-003). P0.2 MCU and safety boundary (P0-004 to P0-007). P0.3 sensors (P0-008 to P0-011). P0.4 interfaces, power, actuators, and envelope (P0-012 to P0-015).

| Done | ID | Task | Status |
|---|---|---|---|
| [x] | `P0-001` | Define the flight-controller role and system boundary. | Scope confirmed by the user on 2026-10-13. |
| [x] | `P0-002` | Record PX4 target/version and supported modes as Software-owned deferred work. | `DEFERRED / NON-BLOCKING`. No hardware decision needed to proceed. |
| [x] | `P0-003` | Define first-revision scope. | H743 main control, F103 auxiliary I/O/PWM/safety, and the stated external interfaces are in scope. PX4, bootloader, QGC, and detailed software behavior are deferred. |
| [x] | `P0-004` | Confirm STM32H743VIT6 as the main MCU. | Requirement confirmed; implementation not verified. |
| [x] | `P0-005` | Confirm STM32F103C8T6 as operational auxiliary I/O/PWM/ESC/safety MCU. | Requirement confirmed; implementation not verified. |
| [x] | `P0-006` | Reserve H743↔F103 USART. | Interface confirmed. Pins, levels, instance, rate, and test access remain for P1/P2. |
| [x] | `P0-007` | Record the immediate-landing requirement if H743 is unavailable. | USART is the monitoring path. Software owns detection, command behavior, and timing. Hardware must preserve the physical path and test access. |
| [ ] | `P0-008` | Select two IMU MFR/MPNs. | `TBD`. Diagram parts are candidates only. |
| [ ] | `P0-009` | Select two barometer MFR/MPNs. | `TBD`. Diagram parts are candidates only. |
| [ ] | `P0-010` | Decide magnetometer MFR/MPN and onboard/external allocation. | `TBD`. |
| [ ] | `P0-011` | Define sensor rates, DRDY/interrupt needs, calibration, and redundancy. | `TBD`. |
| [x] | `P0-012` | Confirm logical H743/F103 external interface allocations. | Confirmed. Exact pins and electrical implementation unverified. See specification section 3. |
| [x] | `P0-013` | Confirm board and servo power requirements. | Board 5 V ±10%, 2 A source capacity. Servo 6 V, 10 A continuous / 15 A instantaneous. Protection, transients, distribution, and component choice are open. |
| [x] | `P0-014` | Confirm logical F103 PWM/expanded-I/O functions. | TILT, ESC, COAX, AIL, and FlySky captured. Timer/channel validity and electrical implementation unverified. |
| [x] | `P0-015` | Confirm maximum PCB envelope. | Each dimension <80 mm × 80 mm. Shape, mounting, connector orientation, and environment open for P3. |

## P1: MCU allocation and conflict review

**Exit gate:** The mapping has actual pins and alternate functions, passes documented resource checks, and has review evidence. It may then be called `ALLOCATED`. It is not automatically `VERIFIED`.

Any candidate pin mapping stays labeled `CANDIDATE / NOT VERIFIED` until P1 evidence is complete.

| Done | ID | Task | Status | Evidence required |
|---|---|---|---|---|
| [ ] | `P1-001` | Assign exact H743 pins and alternate functions for all confirmed and approved interfaces. | `NOT_VERIFIED` | Versioned MCU pin-allocation table |
| [ ] | `P1-002` | Assign exact F103 pins and alternate functions for its approved role. | `NOT_VERIFIED` | Versioned F103 pin-allocation table |
| [ ] | `P1-003` | Allocate both SPI IMUs: CS, DRDY, reset, bus ownership, DMA. | `NOT_VERIFIED` | SPI allocation and timing review |
| [ ] | `P1-004` | Allocate both I2C barometers: addresses, pull-ups, recovery, bus ownership. | `NOT_VERIFIED` | I2C address/bus review |
| [ ] | `P1-005` | Allocate both I2C magnetometers: addresses, pull-ups, recovery, placement constraints. | `NOT_VERIFIED` | I2C and magnetic-placement review |
| [ ] | `P1-006` | Allocate USB FS, VBUS sensing, ESD/protection, connector, and reset support for H743 flashing. | `PROPOSED / NOT_VERIFIED` | USB interface review and schematic net list |
| [ ] | `P1-007` | Allocate selectable H743 BOOT0 and define its default/reset behavior. | `PROPOSED / NOT_VERIFIED` | Boot-state table and circuit review |
| [ ] | `P1-008` | Allocate SWD access for both MCUs: SWDIO, SWCLK, NRST, GND, probe access. | `PROPOSED / NOT_VERIFIED` | Debug-access review |
| [ ] | `P1-009` | Check alternate-function conflicts across every assigned pin. | `OPEN` | Conflict report with no unresolved critical conflicts |
| [ ] | `P1-010` | Check DMA, interrupt, timer/PWM, clock, and priority conflicts. | `OPEN` | Resource matrix and resolution record |
| [ ] | `P1-011` | Check voltage domains, IO levels, pull states, reset states, and boot-time behavior. | `OPEN` | Electrical compatibility review |
| [ ] | `P1-012` | Review package pin availability, reserved pins, unused pins, and ERC/DRC implications. | `OPEN` | Package/resource review |
| [ ] | `P1-013` | Record mapping revision, reviewer, date, conflicts, resolutions, and remaining obligations. | `OPEN` | Signed or attributable review record |

## P2: Schematic and hardware interface boundary

**Exit gate:** Hardware schematic review is closed, electrical interfaces and reserved resources are documented, and no unresolved hardware blocker affects bring-up. Firmware ownership, PX4 target, bootloader, and software protocol details may stay deferred.

| Done | ID | Task | Status | Evidence required |
|---|---|---|---|---|
| [ ] | `P2-001` | Create the schematic from the P1 allocation. | `BLOCKED BY P1` | Versioned native schematic |
| [ ] | `P2-002` | Implement USB FS, BOOT0, SWD, reset, power, and protection circuits. | `BLOCKED BY P1` | Schematic review evidence |
| [ ] | `P2-003` | Implement sensor buses, addresses, CS/DRDY, pull-ups, and recovery provisions. | `BLOCKED BY P0/P1` | Sensor interface review |
| [ ] | `P2-004` | Define hardware net names and connector pinout. Reserve resources for later firmware mapping. | `BLOCKED BY P0/P1` | Hardware net/connector cross-check |
| [ ] | `P2-005` | Create the PX4 board configuration and bootloader plan. | `DEFERRED / NON-BLOCKING` | Later versioned firmware configuration and build/flash procedure. Not a hardware release blocker. |
| [ ] | `P2-006` | Define the H743 USB FS/QGC flashing workflow for both MCU firmware images. | `DEFERRED / NON-BLOCKING` | Later reproducible software procedure and test record. Hardware shall preserve the physical path and access. |
| [ ] | `P2-007` | Define H743↔F103 firmware ownership, protocol version, startup, timeout, and fault behavior. | `DEFERRED / NON-BLOCKING` | Later versioned firmware interface contract. Hardware shall document the reserved electrical path before schematic freeze. |
| [ ] | `P2-008` | Run ERC and resolve or disposition all relevant findings. | `NOT_VERIFIED` | ERC output and issue disposition |
| [ ] | `P2-009` | Complete line-by-line schematic review. | `NOT_VERIFIED` | Review checklist with reviewer and evidence links |

## P3: PCB and fabrication release

**Exit gate:** PCB, BOM, fabrication data, and release manifest are reviewed and approved by the Human engineering owner.

| Done | ID | Task | Status | Evidence required |
|---|---|---|---|---|
| [ ] | `P3-001` | Confirm board envelope, mounting, connector placement, and service/debug access. | `TBD` | Mechanical constraint review |
| [ ] | `P3-002` | Place IMUs, barometers, magnetometers, clock, power, USB, and debug interfaces by their constraints. | `BLOCKED BY P0/P2` | Placement review |
| [ ] | `P3-003` | Route power and return paths with documented current and noise assumptions. | `BLOCKED BY P0/P2` | Power/layout review |
| [ ] | `P3-004` | Route USB FS and high-sensitivity sensor/debug signals with appropriate layout review. | `BLOCKED BY P0/P2` | Signal/layout review |
| [ ] | `P3-005` | Run DRC and disposition all relevant findings. | `NOT_VERIFIED` | DRC output and issue disposition |
| [ ] | `P3-006` | Review thermal/current constraints and manufacturability. | `NOT_VERIFIED` | Manufacturing and thermal review |
| [ ] | `P3-007` | Confirm BOM, footprints, alternates, assembly notes, and test-point access. | `TBD` | Controlled BOM and assembly review |
| [ ] | `P3-008` | Create a hardware release package linked to schematic, PCB, BOM, and the deferred-firmware status. | `NOT_VERIFIED` | Hardware release manifest that records firmware integration as deferred |
| [ ] | `P3-009` | Obtain Human engineering-owner approval for fabrication release. | `NOT_VERIFIED` | Explicit approval record |

## P4: Bring-up and validation

**Exit gate:** Repeatable bench evidence exists, and every remaining issue has an owner and a defined disposition.

| Done | ID | Task | Status | Evidence required |
|---|---|---|---|---|
| [ ] | `P4-001` | Inspect the assembled board for shorts, assembly defects, polarity, and component identity. | `NOT_STARTED` | Inspection record |
| [ ] | `P4-002` | Verify power rails, sequencing, reset behavior, and current consumption before firmware loading. | `NOT_STARTED` | Measured bring-up log |
| [ ] | `P4-003` | Verify SWD access for H743. | `NOT_STARTED` | Probe/session log |
| [ ] | `P4-004` | Verify SWD access for F103. | `NOT_STARTED` | Probe/session log |
| [ ] | `P4-005` | Verify the H743 USB FS hardware path, connector, protection, continuity, and relevant electrical behavior. | `NOT_STARTED` | Hardware inspection/measurement record. Host enumeration may stay deferred. |
| [ ] | `P4-006` | Verify firmware flashing through QGC for the approved workflow. | `DEFERRED / NON-BLOCKING` | Later reproducible software test record |
| [ ] | `P4-007` | Verify bootloader, PX4 startup, sensor detection, and calibration flow. | `DEFERRED / NON-BLOCKING` | Later firmware/console/test log |
| [ ] | `P4-008` | Verify the H743↔F103 physical link, electrical levels, continuity, and test access. Defer protocol behavior. | `NOT_STARTED / SOFTWARE DEFERRED` | Hardware link test record and later software protocol test record |
| [ ] | `P4-009` | Verify actuator outputs, arming behavior, failsafe behavior, and fault handling. | `NOT_STARTED` | Safety/actuator test record |
| [ ] | `P4-010` | Record hardware revision, firmware revision, test conditions, measurements, and deviations. | `NOT_STARTED` | Controlled bring-up report |

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
| OI-001 | Immediate-landing requirement and F103 safety implementation | Requirement confirmed. Detailed behavior and timing are Software-owned and deferred. | Software / P2, P4 |
| OI-002 | Sensor MFR/MPN and electrical properties | `TBD`. Diagram suggestions are not selections. | Human owner / P0 |
| OI-003 | External interfaces and exact MCU pins | Logical requirements confirmed; mapping unverified. | Hardware / P1 |
| OI-004 | Power protection, transients, downstream budgets, and distribution | Input and servo ratings recorded; design details open. | Hardware / P0, P2 |
| OI-005 | Exact MCU pin mapping and resource conflicts | `NOT_VERIFIED` | Hardware / P1 |
| OI-006 | H743↔F103 USART implementation and software contract | Physical protocol confirmed; detailed software contract deferred. | Hardware + Software / P1, P2 |
| OI-007 | PX4 target and bootloader plan | `DEFERRED / NON-BLOCKING` | Software / post-hardware |
| OI-008 | F103 PWM outputs and failsafe behavior | Logical functions confirmed; timer AF and electrical behavior unverified. | Hardware + Software / P1, P2 |
| OI-009 | Exact outline, mounting, connector placement, and environment | Maximum envelope confirmed; remaining mechanics TBD. | Human owner / P3 |
| OI-010 | Magnetometer count/allocation and sensor requirements | `TBD` | Human owner / P0 |
| OI-011 | Physical actuator/ESC signal distribution | Diagram captured; native allocation and fanout need review. | Hardware / P1, P2 |

## Current next action

Continue P1 allocation and conflict review using the confirmed logical interfaces. Keep sensor-specific resources provisional until the sensor requirements are decided. Keep the candidate/unverified label on all pin mappings. Reserve the USART safety path and test access. Do not begin fabrication release until the applicable P0 to P3 evidence and Human approval are complete.
