# Hardware Design Specification: AeroOptix-Horizon

| Property             | Value |
| -------------------- |---|
| Project              | AeroOptix-Horizon |
| Document owner       | Human engineering owner (TBD) |
| Document revision    | 0.4 |
| Last updated         | 2026-10-18 |
| Design tool          | TBD |
| Hardware phase       | TBD (declared by the human) |
| Related baseline     | FC_H743 rev2 reference from user-provided diagrams; native design baseline not established |
| Specification status | Draft / not for fabrication |

**Conventions**

- `CONFIRMED`: the human owner confirmed the requirement or value.
- `NOT_VERIFIED`: no evidence exists yet. This applies to every requirement in this document unless a row says otherwise.
- `TBD`: to be decided. A value written as `TBD`, or left out, is open.
- A part shown in a diagram is a candidate only. It is not an approved part number.

**Part-number boundary:** Only `STM32H743VIT6`, `STM32F103C8T6` and `ICM-45686` (2 × IMU, DEC-008) are confirmed part numbers. The H743↔F103 interface protocol is confirmed as `USART`. All other part numbers are `TBD`. This includes barometers, magnetometers, regulators, protection devices, power modules, connectors, and interface ICs.

## 1. Project Definition

### 1.1 Purpose and application

A custom PX4 flight controller hardware platform with a dual-MCU architecture. The STM32H743VIT6 is the main flight-controller MCU. The STM32F103C8T6 is an operational auxiliary MCU for expanded I/O, PWM/ESC control, and safety behavior.

Pixhawk 6C is a conceptual and functional reference only. It does not authorize copying the Pixhawk schematic, PCB, or pinout.

### 1.2 Scope

**In scope:**

- H743 main-MCU hardware architecture
- F103 operational auxiliary I/O, PWM, ESC, and safety hardware boundary
- H743↔F103 USART physical interface
- Sensor interfaces: 2 × SPI IMU, 2 × I2C barometer, 2 × I2C magnetometer
- H743 external interfaces and F103 PWM/expanded-I/O allocation provided by the user
- 5 V flight-controller board input and 6 V servo supply
- USB FS, BOOT0, SWD, reset, protection, testability, PCB, manufacturing, and bring-up requirements
- Verification planning through hardware bring-up

**Out of scope or deferred:**

- Final PX4 version and board target
- Bootloader implementation
- Firmware image packaging and software flashing implementation
- Detailed USART message protocol and Software-owned behavior
- Final sensor, regulator, protection, connector, power-module, and PDB/UBEC part numbers
- Fabrication release, measured performance, and regulatory approval

### 1.3 Operating scenarios

See section 3.2.

### 1.4 References

| Reference | Source | Revision / date | Purpose |
| --------- |---|---|---|
| REF-01    | Pixhawk 6C reference architecture | Not specified | Conceptual and functional reference only |
| REF-02    | User-provided FC_H743 architecture diagram | 2026-10-12 | Diagram-derived candidate architecture; not native design authority |
| REF-03    | User-provided power architecture diagram | 2026-10-12 | Diagram-derived power candidates; not an approved power specification |
| REF-04    | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | 0.2 | Execution and evidence checklist |

## 2. Requirements Management

### 2.1 Writing rules

- Use **shall** for mandatory requirements, **should** for design preferences, **may** for optional capabilities.
- Each requirement has a stable, unique ID. Never reuse an ID after removal.
- Keep requirements separate from implementation choices, assumptions, and verification results.
- A candidate part, pin mapping, resource count, or implementation report is not verification.
- Deferred firmware details are not hardware approval or release evidence.

### 2.2 Requirement register

All rows are `CONFIRMED` by the user and `NOT_VERIFIED`. SYS-001 and SYS-002 come from the user request.

| ID      | Requirement | Conditions / limits | Verification |
| ------- |---|---|---|
| SYS-001 | The system shall be a custom PX4 Flight Controller hardware platform. | Custom hardware; PX4 implementation details deferred. | Inspection of approved system scope. |
| SYS-002 | Pixhawk 6C shall be used as a conceptual and functional reference only. | No copied schematic, PCB, or pinout is assumed. | Architecture review. |
| MCU-001 | The main MCU shall be STM32H743VIT6. | Package placement and native design implementation are open. | Native schematic inspection. |
| MCU-002 | The operational auxiliary MCU shall be STM32F103C8T6. | Required during operation for auxiliary I/O, PWM/ESC, expanded I/O, and safety. | Native schematic and responsibility review. |
| IF-001  | The H743↔F103 interface protocol shall be USART. | Path for F103 to monitor H743 availability. Instance, pins, levels, rate, timeout, and message details are open. Software owns detection and command behavior. | Allocation review and hardware test. |
| SEN-001 | The design shall provide 2 × SPI IMU interfaces. | Part: 2 × ICM-45686 (DEC-008). Resource allocation TBD. | Schematic inspection and hardware test. |
| SEN-002 | The design shall provide 2 × I2C barometer interfaces. | Parts, addresses, and bus allocation TBD. | Schematic inspection and hardware test. |
| SEN-003 | The design shall provide 2 × I2C magnetometer interfaces. | Second magnetometer allocation TBD. | Architecture and hardware test. |
| PWR-001 | The flight-controller board shall receive 5 V from the power module. | Limits: see PWR-010. | Power-tree inspection and measurement. |
| PWR-002 | The servo supply shall be 6 V. | Limits: see PWR-011. | Power-tree inspection and measurement. |
| SAF-001 | If H743 is not operating, F103 shall command immediate landing. | H743 availability is monitored over the USART path. Software owns detection, landing-command behavior, and timing. The electrical path and test access are hardware requirements. | Fault-injection test. |

## 3. System Requirements

### 3.1 Functional requirements

| ID      | Required behavior | Condition | Verification |
| ------- |---|---|---|
| FUN-001 | H743 shall provide the primary flight-controller processing and primary system interface resources. | Normal operation | Schematic/resource inspection; later bring-up |
| FUN-002 | F103 shall provide auxiliary I/O expansion and PWM control for ESC-related outputs. | Normal operation | Resource inspection; PWM electrical test |
| FUN-003 | F103 shall support the user-defined TILT, ESC, COAX, AIL, and FlySky logical interfaces. | Normal operation; timer validity open | MCU resource review; hardware test |
| FUN-004 | F103 shall command immediate landing when the H743-failure condition is detected (see SAF-001). | H743 unavailable | Fault-injection test; timing measurement |
| FUN-005 | H743 and F103 shall provide SWD debug/recovery access. | Development, service, bring-up | Probe connection; debug test |
| FUN-006 | H743 shall retain selectable BOOT0 access. | Development, recovery | Inspection; boot-state test |

### 3.2 Operating scenarios and modes

Exit, transition, recovery, and restart behavior is `TBD` for all rows.

| Scenario / mode   | Entry | Required behavior |
| ----------------- |---|---|
| Normal            | Valid power and normal MCU operation | H743 performs primary functions. F103 provides auxiliary and safety functions. |
| H743 unavailable  | F103 detects H743 unavailable under the future safety boundary | F103 commands immediate landing. Timing is `NOT_VERIFIED`. |
| H743↔F103 link    | Normal operation | The physical link uses USART. Message protocol and software ownership are deferred. |
| Boot / service    | BOOT0 or service procedure selects recovery | SWD and USB service access remain available as designed. USB FS on H743 is for later Software-owned flashing/QGC integration. |
| Power input       | Power module connected | Board receives 5 V. Servo supply is 6 V. Limits are in PWR-010 and PWR-011. |
| Power abnormality | Brownout, reset, rail fault, or input loss | Hardware response, sequencing, and safe output state are `TBD`. Verify before release. |

### 3.3 Electrical system requirements

| ID      | Parameter | Min | Nom | Max | Unit | Note |
| ------- |---|---:|---:|---:|---|---|
| PWR-010 | Flight-controller board input | 4.5 | 5 | 5.5 | V | ±10%; source capacity 2 A. Transients and protection TBD. |
| PWR-011 | Servo supply | TBD | 6 | TBD | V | 10 A continuous, 15 A instantaneous, from the user-provided UBEC-10A specification reference. Pulse duration, protection, and distribution TBD. This does not approve a UBEC part. |
| PWR-012 | Board continuous current | TBD | TBD | TBD | A | Separate MCU, sensor, external-I/O, and servo budgets required. |
| PWR-013 | Sensor/MCU rail tolerance | TBD | TBD | TBD | V / % | Diagram rails are candidates, not approved. |
| PWR-014 | Brownout/reset threshold | TBD | TBD | TBD | V | Per MCU and rail. |

### 3.4 External interfaces

Allocations are `CONFIRMED` at the logical level only. For every row, exact pins, alternate functions, direction (unless noted), electrical levels, rate, protection, and connector pinout are `TBD` and `NOT_VERIFIED`. Timer alternate functions are also `NOT_VERIFIED` (OPEN-003).

| ID     | Connector | Function | Resource | Note |
| ------ |---|---|---|---|
| IF-010 | Conn1 / Tel1 | Telemetry 1 | UART7 | |
| IF-011 | Conn2 / Tel2 | Telemetry 2 | UART1 | |
| IF-012 | Conn3 / GPS1 + compass | GPS (UBX) and compass | UART2 + I2C1 | Compass address and pull-ups TBD. |
| IF-013 | Conn4 / GPS2 | GPS2 | UART3 | Reserved / blank. |
| IF-014 | Conn5 / MS4525DO | Air-data sensor | I2C4, address `0x28` | Pull-ups TBD. |
| IF-015 | Conn6 / TF-Luna | Rangefinder | UART8 | |
| IF-016 | Conn7 / UART7 TX | Reserved UART transmit | UART7 TX | Output. Reserved / blank. |
| IF-017 | Conn8 / VT L | Logical output | TIM4_CH3 | Output. |
| IF-018 | Conn9 / VT R | Logical output | TIM4_CH4 | Output. |
| IF-019 | Conn10 / SP2 | Reserved logical output | TIM1_CH1 | Output. Reserved / blank. |
| IF-020 | Conn11 / TL2 | Logical output | TIM15_CH1 | Output. |
| IF-021 | Conn12 / TR2 | Logical output | TIM15_CH2 | Output. |
| IF-022 | USB FS | Service and later software flashing | USB FS | Bidirectional. ESD/protection, VBUS, connector, routing, and enumeration TBD. |
| IF-023 | SWD | Debug and recovery | SWD | Bidirectional. SWDIO, SWCLK, NRST, GND, and connector or test pads TBD. |
| IF-024 | H743↔F103 | MCU link | USART | Bidirectional. Message protocol deferred. Instance, pins, rate, timeout, protection, and test access TBD. |

### 3.5 F103 PWM and expanded I/O

IF-030 to IF-033 are `CONFIRMED` logical requirements. IF-034 to IF-037 are `CONFIRMED` logical labels. Resource support is `NOT_VERIFIED`. Timer/channel labels are copied as given. They do not claim that the STM32F103 package or alternate-function matrix supports them. Electrical output is `TBD`.

| ID     | Logical output | Allocation |
| ------ |---|---|
| IF-030 | TILT L | TIM2_CH1 |
| IF-031 | TILT R | TIM2_CH2 |
| IF-032 | ESC L | TIM4_CH3 |
| IF-033 | ESC R | TIM4_CH4 |
| IF-034 | COAX T | TIM3_CH5 |
| IF-035 | COAX B | TIM3_CH6 |
| IF-036 | AIL L | TIM3_CH7 |
| IF-037 | AIL R | TIM3_CH8 |
| IF-038 | FlySky | Bulk pinheader; pinout and electrical levels TBD |

### 3.6 Environmental and reliability requirements

| ID      | Parameter / condition | Required range or limit | Verification |
| ------- |---|---|---|
| ENV-001 | Operating temperature | TBD | Analysis / test TBD |
| ENV-002 | Storage temperature | TBD | Analysis / test TBD |
| ENV-003 | Vibration and shock | TBD | Analysis / test TBD |
| ENV-004 | Humidity, ingress, altitude, and maintenance | TBD | Analysis / test TBD |

### 3.7 Protection and fault behavior

| ID      | Hazard / fault | Required response | Recovery method | Verification |
| ------- |---|---|---|---|
| SAF-010 | H743 unavailable | See SAF-001. F103 monitors H743 over USART. Software owns detailed detection and landing-command behavior. | Timing, reset, recovery, and F103-failure behavior TBD by Software. | Fault-injection test; NOT_VERIFIED |
| SAF-011 | H743↔F103 USART loss | Safe response and output ownership are Software-owned and TBD. | TBD by Software. | Fault-injection test; NOT_VERIFIED |
| SAF-012 | 5 V input abnormality | Safe reset/output state TBD. | Power recovery procedure TBD. | Measurement and fault test; NOT_VERIFIED |
| SAF-013 | 6 V servo rail fault | Protection and safe actuator state TBD. | TBD | Measurement and fault test; NOT_VERIFIED |
| SAF-014 | ESD, reverse polarity, overvoltage, short circuit | Protection requirements TBD. | Service/recovery method TBD. | Analysis / test; NOT_VERIFIED |

## 4. Hardware Architecture and Design Constraints

### 4.1 Functional block diagram

The user-provided diagrams show an H743 main MCU, an F103 auxiliary MCU, sensor/interface blocks, USB/SWD, PWM/actuator paths, and a separate power architecture. The images are reference inputs only. Native schematic and PCB files remain the design authority.

### 4.2 Functional blocks

| Block                     | Role | Inputs / outputs | Dependencies | Key constraints |
| ------------------------- |---|---|---|---|
| H743 main controller      | Primary flight-controller processing and interface host | Sensors, external interfaces, USB, SWD, USART, outputs | 5 V input and defined rails | Pins/resources NOT_VERIFIED. |
| F103 auxiliary controller | PWM/ESC, expanded I/O, safety function | USART, PWM outputs, FlySky, safety path | H743 status; defined power/reset | Timer, resource, and safety implementation NOT_VERIFIED. |
| IMU subsystem             | Two SPI IMU interfaces | SPI, CS, DRDY; reset by software (DEC-009) | Selected sensor parts and rail | 2 × ICM-45686 (DEC-008). Rail and allocation TBD. |
| Barometer subsystem       | Two I2C barometer interfaces | I2C, address, pull-ups | Selected sensor parts and rail | MFR/MPN and bus strategy TBD. |
| Magnetometer subsystem    | Two I2C magnetometer interfaces | I2C, address, placement | Selected sensor parts; external compass decision | Second magnetometer allocation TBD. |
| H743 external I/O         | Telemetry, GPS, compass, air-data, rangefinder, logical outputs | UART/I2C/timer interfaces | H743 resource allocation | Pins and electrical implementation NOT_VERIFIED. |
| F103 PWM/I/O              | TILT, ESC, COAX, AIL, FlySky | Timer/PWM and bulk connector | F103 resource allocation | Timer/channel validity and electrical drive TBD. |
| USB/SWD/BOOT0             | Service, debug, recovery | USB FS, SWD, BOOT0 | H743/F103 reset and power | Access, protection, and circuit NOT_VERIFIED. |
| Power subsystem           | 5 V board input and 6 V servo supply | Rails, returns, protection | Power module and distribution | Tolerances, current, and protection TBD. |

### 4.3 Power architecture

- Board input and servo supply limits: see PWR-010 and PWR-011.
- The diagram-derived arrangement is a candidate only: 6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 5 V, 3.3 V, 3.3 V_IMU, 6 V UBEC.
- TBD: rail dependencies, current budgets, load steps, sequencing, brownout, reverse-polarity protection, overvoltage protection, transient handling, grounding, filtering, thermal limits.

### 4.4 Clock, reset, boot and programming

- H743 shall retain selectable BOOT0 access (FUN-006).
- H743 and F103 shall provide SWD access (FUN-005).
- USB FS shall be physically available on H743 for later Software-owned flashing/QGC integration.
- TBD: clock sources, reset topology, power-on reset, watchdog interaction, boot-time pin states, F103 boot behavior, service procedures.

### 4.5 Control, sensing, analog and digital considerations

All items are `TBD` and `NOT_VERIFIED`.

- SPI/I2C: bus ownership, chip-select, data-ready/interrupt, pull-up, address, DMA, timing, recovery.
- PWM: output voltage, drive method, current capability, update rate, input capture, actuator connector pinout, arming, failsafe behavior.
- USART: electrical levels, rate, timeout, framing, isolation, protection, message protocol. Only the physical protocol family `USART` is confirmed.
- Signal integrity, return paths, sensor noise, magnetic placement, EMI/EMC constraints.

### 4.6 Component selection constraints

| ID      | Category | Mandatory constraints | Preferred constraints | Sourcing / lifecycle |
| ------- |---|---|---|---|
| CMP-001 | Main MCU | Must be STM32H743VIT6. | TBD | Availability, package, lifecycle, approved source TBD |
| CMP-002 | Auxiliary MCU | Must be STM32F103C8T6. | TBD | Availability, package, lifecycle, approved source TBD |
| CMP-003 | IMU | Two SPI positions required. Must be TDK InvenSense ICM-45686 (DEC-008). | TBD | PX4 driver present. SPI support, supply range, availability and approved source NOT_VERIFIED |
| CMP-004 | Barometer | Two I2C positions required. | Diagram parts are not approved. | MFR/MPN, availability, driver, lifecycle TBD |
| CMP-005 | Magnetometer | Two I2C positions required. | Diagram parts are not approved. | MFR/MPN, availability, driver, lifecycle TBD |
| CMP-006 | Regulator, protection, connector, PDB/UBEC, interface parts | Electrical requirements shall be satisfied. | Specific parts TBD. | MFR/MPN, availability, lifecycle, approved source TBD |

### 4.7 Engineering calculations and margins

| Analysis               | Inputs / operating corner | Method / reference | Result | Margin / open questions |
| ---------------------- |---|---|---|---|
| Board input current    | 5 V input, MCU/sensor/I/O load | TBD | NOT_VERIFIED | Current budget and duty cycle TBD |
| Servo rail current     | 6 V rail and actuator load | TBD | NOT_VERIFIED | Servo count, peak current, and protection TBD |
| Power rail tolerance   | All MCU/sensor rails | TBD | NOT_VERIFIED | Nominal, min, max, and load-step limits TBD |
| Thermal margin         | MCU, regulator, protection, output drivers | TBD | NOT_VERIFIED | Ambient, dissipation, copper, and cooling TBD |
| Safety response timing | H743 failure to F103 landing command | TBD | NOT_VERIFIED | Timeout, detection method, actuator path, and test method TBD |

## 5. PCB Design Specification

### 5.1 Mechanical envelope

| ID      | Item | Requirement / limit | Verification |
| ------- |---|---|---|
| MEC-001 | Board outline | Each board dimension shall be less than `80 mm × 80 mm`. Exact outline and shape TBD. This supersedes the older diagram size of about `90 mm × 95 mm`. | Native PCB inspection / measurement |
| MEC-002 | Mounting pattern | TBD | Native PCB inspection / measurement |
| MEC-003 | Connector orientation and service access | TBD | Mechanical inspection |
| MEC-004 | Height, keepouts, enclosure, environmental constraints | TBD | Mechanical inspection / analysis |

### 5.2 Fabrication and stackup

| ID      | Parameter | Requirement / target | Fabricator confirmation |
| ------- |---|---|---|
| PCB-001 | Copper layer count | TBD | TBD |
| PCB-002 | Stackup, dielectric, and copper weight | TBD | TBD |
| PCB-003 | Minimum trace and spacing | TBD | TBD |
| PCB-004 | Hole, via, and annular-ring capability | TBD | TBD |
| PCB-005 | Soldermask and surface finish | TBD | TBD |

### 5.3 Layout and routing constraints

All constraints are `TBD`.

| ID      | Circuit / region | Constraint topics | Reason | Verification |
| ------- |---|---|---|---|
| PCB-010 | H743/F103 power and returns | Width, return path, via, load-step | Current and noise control | Layout review / analysis |
| PCB-011 | IMU, barometer, magnetometer regions | Placement, vibration, magnetic, noise | Sensor integrity | Placement review / test |
| PCB-012 | USB FS | Routing, ESD, VBUS, connector, return path | USB physical integrity and protection | Layout review / hardware test |
| PCB-013 | SWD and BOOT0 | Probe access, reset/boot-state | Debug and recovery | Inspection / debug test |
| PCB-014 | PWM/actuator outputs | Return path, drive, protection, connector | Actuator integrity and safety | Layout review / electrical test |
| PCB-015 | USART H743↔F103 | Routing, voltage compatibility, return path, test access | Inter-MCU safety/control path | Review / hardware test |

### 5.4 Power integrity, signal integrity and EMC

TBD: rail voltage-drop limits, ripple/noise limits, decoupling, filtering, return paths, ground strategy, USB routing, sensor noise, PWM output integrity, USART integrity, EMI/EMC expectations. The diagrams and candidate mapping establish no compliance or signal-integrity result.

### 5.5 Thermal and current carrying

TBD: hot components, copper spreading, vias, allowable temperature rise, load profile, thermal model assumptions, servo current paths, protection-device dissipation.

### 5.6 Design-rule implementation in KiCad

| Specification requirement  | KiCad mechanism, if supported | Manual / external check |
| -------------------------- |---|---|
| Clearance and width        | TBD net classes and board rules | DRC plus review |
| USB FS routing             | TBD rules | Layout review and hardware test |
| Power and return paths     | TBD net classes/regions | Current-path review |
| Sensor and clock placement | TBD constraints | Placement review |
| SWD/BOOT0/test access      | TBD footprints/test pads | Inspection and bring-up |

## 6. Manufacturing, Assembly and Service

### 6.1 Manufacturability and assembly

| ID      | Requirement | Rationale | Verification |
| ------- |---|---|---|
| MFG-001 | The fabrication process, stackup, materials, copper weight, and surface finish shall be defined before release. | Controlled manufacturing | Fabricator review |
| MFG-002 | Component footprints, package variants, alternates, assembly notes, and polarity shall be controlled before release. | Assembly correctness | BOM/assembly review |
| MFG-003 | Connector orientation, test access, rework access, and service access shall be defined. | Bring-up and serviceability | Assembly/mechanical review |
| MFG-004 | The final part list shall contain only approved or explicitly dispositioned part numbers. | Keep unconfirmed candidate parts out of release | BOM audit |

### 6.2 Debug and testability

| ID      | Signal / function | Access requirement | Method |
| ------- |---|---|---|
| TST-001 | H743 SWD | Connector or test pads: SWDIO, SWCLK, NRST, GND | Inspection; debug test |
| TST-002 | F103 SWD | Connector or test pads: SWDIO, SWCLK, NRST, GND | Inspection; debug test |
| TST-003 | H743 BOOT0 | Selectable and observable boot state | Inspection; boot-state test |
| TST-004 | 5 V board input | Test point; current/voltage measurement access | Inspection; measurement |
| TST-005 | 6 V servo rail | Test point; current/voltage measurement access | Inspection; measurement |
| TST-006 | H743↔F103 USART | Physical test access; signal observation | Inspection; hardware test |
| TST-007 | F103 safety path | Fault-injection access for the H743-unavailable condition | Fault-injection test |

## 7. Verification Plan (Planning Only)

No automatic gates. This table plans how requirements could be checked. It does not declare phase completion, design approval, or release readiness.
| Requirement ID | Method | Planned evidence | Result | Reviewer |
| ------------------------- |---|---|---|---|
| MCU-001, MCU-002          | Inspection | Native schematic/package review | NOT_VERIFIED | Human, TBD |
| IF-001                    | Inspection / Test | USART allocation review; physical link test | NOT_VERIFIED | Human, TBD |
| SEN-001, SEN-002, SEN-003 | Inspection / Test | Bus allocation review; sensor electrical access test | NOT_VERIFIED | Human, TBD |
| PWR-001, PWR-002          | Analysis / Test | Power-tree review; rail measurement; load/current test | NOT_VERIFIED | Human, TBD |
| SAF-001                   | Test | H743 fault injection; F103 immediate-landing response measurement | NOT_VERIFIED | Human, TBD |
| IF-010 to IF-024          | Inspection / Test | Connector, pin, electrical-level, protection, and interface test | NOT_VERIFIED | Human, TBD |
| IF-030 to IF-038          | Inspection / Test | Timer/resource review; PWM/expanded-I/O electrical test | NOT_VERIFIED | Human, TBD |
| PCB-010 to PCB-015        | Review / Analysis / Test | Layout, return path, DRC, signal, power, and hardware review | NOT_VERIFIED | Human, TBD |
| TST-001 to TST-007        | Inspection / Test | Test-point and debug-access inspection, then bring-up tests | NOT_VERIFIED | Human, TBD |

## 8. Design Decisions and Open Items

### 8.1 Decisions

All decisions are by the human owner, unless the Notes say otherwise.

| ID      | Topic | Selected option | Notes | Date |
| ------- |---|---|---|---|
| DEC-001 | Main MCU part number | STM32H743VIT6 | Implementation not verified. | 2026-10-12 |
| DEC-002 | Auxiliary MCU part number | STM32F103C8T6 | Implementation not verified. | 2026-10-12 |
| DEC-003 | H743↔F103 physical interface protocol | USART | Instance, pins, levels, and message protocol TBD. | 2026-10-12 |
| DEC-004 | Firmware implementation boundary | Deferred and non-blocking for the current hardware path | Software team decides firmware details later. | 2026-10-12 |
| DEC-005 | H743 availability monitoring path | USART | See SAF-001. | 2026-10-13 |
| DEC-006 | Maximum PCB dimensions | Limit in MEC-001 | See MEC-001. | 2026-10-13 |
| DEC-007 | Power input and servo rail limits | Limits in PWR-010 and PWR-011 | Budgets and component selection are open (OPEN-006, OPEN-007, OPEN-010). | 2026-10-13 |
| DEC-008 | IMU part number (SEN-001, CMP-003) | 2 × TDK InvenSense ICM-45686 | Confirmed by the team. Implementation not verified. SPI, supply range and sourcing open; see `AO-HORIZON_IMU_SELECTION_EN.md`. | 2026-10-18 |
| DEC-009 | IMU reset method | Software reset only (ICM-45686 `SOFT_RST`); no hardware reset line | ICM-45686 has no reset pin (datasheet via agy, `NOT_VERIFIED`). No hardware power control of the IMU rail is planned. | 2026-10-18 |

### 8.2 Open questions and assumptions

| ID       | Description | Impact | Owner / next action |
| -------- |---|---|---|
| OPEN-001 | Exact H743/F103 pins and alternate functions | May invalidate the candidate allocation. | Hardware review / P1 |
| OPEN-002 | USART instance, pins, voltage levels, rate, timeout, recovery | Affects safety/control path. | Hardware + Software / P1, P2 |
| OPEN-003 | Timer/channel validity for all H743/F103 labels | May require reassignment or a logical-to-physical mapping. | Hardware review / P1 |
| OPEN-004 | Sensor MFR/MPN and electrical properties. IMU part chosen (DEC-008); IMU electrical properties, barometer and magnetometer open. | Affects footprint, rail, layout, drivers, verification. | Human owner / P0 |
| OPEN-005 | Second magnetometer allocation | Affects sensor redundancy and connector/bus architecture. | Human owner / P0 |
| OPEN-006 | 5 V input transient/protection, board current budget, downstream rail budgets | Affects power design and protection. | Hardware review / P0, P2 |
| OPEN-007 | 6 V servo rail pulse duration, protection, distribution, actuator load profile | Affects power and actuator safety. | Hardware review / P0, P2 |
| OPEN-008 | Software-owned safety detection timing, immediate-landing behavior, F103-failure response | Affects F103 behavior, output ownership, test method. | Software / P2, P4 |
| OPEN-009 | Exact board outline under the MEC-001 limit, mounting, connector orientation, environment | Affects PCB and mechanical release. | Human owner / P0, P3 |
| OPEN-010 | All non-MCU part numbers except the IMU (DEC-008) | No other non-MCU part is approved by this document. | Human owner / component selection gate |

## 9. Specification Change Notes

| Revision | Date | Description | Approved by |
| -------- |---|---|---|
| 0.1      | 2026-10-12 | Initial advanced hardware specification draft based on confirmed H743/F103 part numbers, confirmed USART protocol, user-provided interface requirements, and diagram-derived references. | TBD |
| 0.2      | 2026-10-13 | Recorded user-confirmed power limits, maximum PCB dimensions, USART safety-monitoring path, and Software ownership of detailed safety behavior. Sensor part selection remains TBD. | Human owner |
| 0.3      | 2026-10-18 | Recorded team-confirmed IMU part: 2 × ICM-45686 (DEC-008). Barometer and magnetometer selection remain TBD. | Team |
| 0.4      | 2026-10-18 | Recorded IMU software reset (DEC-009) and removed the IMU hardware reset signal from the interface table. | Human owner |

## Current verdict

**Draft only. NOT_VERIFIED and NOT FOR FABRICATION.**

The specification is structured enough for hardware P1 allocation and conflict review. It does not approve any non-MCU part number other than the IMU (DEC-008), pin mapping, timer allocation, power protection or rail detail, safety timing, schematic, PCB, or fabrication release. Barometer and magnetometer selection remains TBD. Diagram-listed sensor parts are not approved.
