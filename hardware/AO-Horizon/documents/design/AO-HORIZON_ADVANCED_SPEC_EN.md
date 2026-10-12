# Hardware Design Specification — AeroOptix-Horizon

| Property | Value |
|---|---|
| Project | AeroOptix-Horizon |
| Document owner | Human engineering owner / TO BE DECIDED |
| Document revision | 0.1 |
| Last updated | 2026-10-12 |
| Design tool | TO BE DECIDED |
| Hardware phase | TO BE DECIDED BY HUMAN |
| Related baseline | FC_H743 rev2 reference from user-provided diagrams; native design baseline not established |
| Specification status | Draft / not for fabrication |

**Part-number confirmation boundary:** Only `STM32H743VIT6` and `STM32F103C8T6` are confirmed part numbers. The H743↔F103 interface protocol is confirmed as `USART`. All other part numbers, including sensors, regulators, protection devices, power modules, connectors, and interface ICs, are `TO BE DECIDED`.

## 1. Project Definition

### 1.1 Purpose and application

This project defines a custom PX4 Flight Controller hardware platform using a dual-MCU architecture. The STM32H743VIT6 is the main flight-controller MCU. The STM32F103C8T6 is an operational auxiliary MCU for expanded I/O, PWM/ESC control, and safety behavior.

The platform uses Pixhawk 6C as a conceptual and functional reference. The reference does not authorize copying the Pixhawk schematic, PCB, or pinout.

### 1.2 Scope

**In scope:**

- H743 main-MCU hardware architecture
- F103 operational auxiliary I/O, PWM, ESC, and safety hardware boundary
- H743↔F103 USART physical interface
- Sensor interface requirements: 2 × SPI IMU, 2 × I2C barometer, and 2 × I2C magnetometer
- H743 external interfaces and F103 PWM/expanded-I/O allocation provided by the user
- 5 V flight-controller board input and 6 V servo supply requirement
- USB FS, BOOT0, SWD, reset, protection, testability, PCB, manufacturing, and bring-up requirements
- Requirement verification planning through hardware bring-up

**Out of scope or deferred:**

- Final PX4 version and board target
- Bootloader implementation
- Firmware image packaging and software flashing implementation
- Detailed USART message protocol and Software-owned behavior
- Final sensor, regulator, protection, connector, power-module, and PDB/UBEC part numbers
- Fabrication release, measured performance, and regulatory approval

### 1.3 Operating scenarios

| Scenario | Required behavior | Status |
|---|---|---|
| Normal operation | H743 performs primary flight-controller functions; F103 provides auxiliary PWM/I/O and safety functions. | CONFIRMED REQUIREMENT / NOT_VERIFIED |
| H743 unavailable | F103 commands immediate landing through the defined safety boundary. | CONFIRMED SAFETY REQUIREMENT / TIMING NOT_VERIFIED |
| H743↔F103 link operation | The physical link uses USART. Detailed message protocol and software ownership are deferred. | CONFIRMED INTERFACE / IMPLEMENTATION NOT_VERIFIED |
| USB service | H743 USB FS is physically available for later Software-owned flashing/QGC integration. | CONFIRMED HARDWARE REQUIREMENT / NOT_VERIFIED |
| Debug and recovery | H743 and F103 provide SWD access; H743 retains selectable BOOT0. | CONFIRMED REQUIREMENT / NOT_VERIFIED |
| Power input | Flight-controller board receives 5 V from the power module; servo supply is 6 V. | CONFIRMED REQUIREMENT / LIMITS TO BE DECIDED |
| Power loss, brownout, or reset | Hardware response, sequencing, and safety behavior are TO BE DECIDED and verified before release. | TO BE DECIDED |

### 1.4 Terminology and references

| Reference | Document / source | Revision / date | Purpose |
|---|---|---|---|
| REF-01 | Pixhawk 6C reference architecture | Not specified | Conceptual and functional reference only |
| REF-02 | User-provided FC_H743 architecture diagram | 2026-10-12 | Source for diagram-derived candidate architecture; not native design authority |
| REF-03 | User-provided power architecture diagram | 2026-10-12 | Source for diagram-derived power candidates; not an approved power specification |
| REF-04 | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | 0.1 | Execution and evidence checklist |

## 2. Requirements Management

### 2.1 Writing rules

- Use **shall** for mandatory requirements, **should** for design preferences, and **may** for optional capabilities.
- Assign a stable, unique requirement ID; never reuse an ID after removal.
- Keep requirements distinct from implementation choices, assumptions, and verification results.
- Use `TO BE DECIDED` for an unconfirmed decision or value.
- Use `NOT_VERIFIED` for a claim, allocation, or result that lacks sufficient evidence.
- A candidate part shown in a diagram is not an approved part number.
- A candidate pin mapping, resource count, or implementation report is not verification by itself.
- Firmware details marked deferred are not hardware approval or release evidence.

### 2.2 Requirement register

| ID | Requirement | Conditions / limits | Verification method | Status / source |
|---|---|---|---|---|
| SYS-001 | The system shall be a custom PX4 Flight Controller hardware platform. | Custom hardware; PX4 implementation details deferred. | Inspection of approved system scope. | CONFIRMED / user request |
| SYS-002 | Pixhawk 6C shall be used as a conceptual and functional reference only. | No copied schematic, PCB, or pinout is assumed. | Architecture review. | CONFIRMED / user request |
| MCU-001 | The main MCU shall be STM32H743VIT6. | Exact package placement and native design implementation remain open. | Native schematic inspection. | CONFIRMED PART NUMBER / NOT_VERIFIED |
| MCU-002 | The operational auxiliary MCU shall be STM32F103C8T6. | Required during operation for auxiliary I/O, PWM/ESC, expanded I/O, and safety. | Native schematic and responsibility review. | CONFIRMED PART NUMBER / NOT_VERIFIED |
| IF-001 | The H743↔F103 interface protocol shall be USART. | Instance, pins, electrical levels, rate, timeout, and message details remain open. | Allocation review and hardware test. | CONFIRMED PROTOCOL / NOT_VERIFIED |
| SEN-001 | The design shall provide 2 × SPI IMU interfaces. | Parts and exact resource allocation are TO BE DECIDED. | Schematic inspection and hardware test. | CONFIRMED INTERFACE / NOT_VERIFIED |
| SEN-002 | The design shall provide 2 × I2C barometer interfaces. | Parts, addresses, and bus allocation are TO BE DECIDED. | Schematic inspection and hardware test. | CONFIRMED INTERFACE / NOT_VERIFIED |
| SEN-003 | The design shall provide 2 × I2C magnetometer interfaces. | The second magnetometer allocation is TO BE DECIDED. | Architecture and hardware test. | CONFIRMED INTERFACE / NOT_VERIFIED |
| PWR-001 | The flight-controller board shall receive 5 V from the power module. | Input tolerance, current budget, transients, and protection are TO BE DECIDED. | Power-tree inspection and measurement. | CONFIRMED REQUIREMENT / NOT_VERIFIED |
| PWR-002 | The servo supply shall be 6 V. | Current budget, protection, and distribution are TO BE DECIDED. | Power-tree inspection and measurement. | CONFIRMED REQUIREMENT / NOT_VERIFIED |
| SAF-001 | If H743 is not operating, F103 shall command immediate landing. | Detection method, timing, output ownership, and F103-failure behavior are TO BE DECIDED. | Fault-injection test. | CONFIRMED SAFETY REQUIREMENT / NOT_VERIFIED |

## 3. System Requirements

### 3.1 Functional requirements

| ID | Function / required behavior | Operating condition | Verification |
|---|---|---|---|
| FUN-001 | H743 shall provide the primary flight-controller processing and primary system interface resources. | Normal operation. | Schematic/resource inspection; later bring-up. |
| FUN-002 | F103 shall provide auxiliary I/O expansion and PWM control for ESC-related outputs. | Normal operation. | Resource inspection and PWM electrical test. |
| FUN-003 | F103 shall support the user-defined TILT, ESC, COAX, AIL, and FlySky logical interfaces. | Normal operation; exact timer validity remains open. | MCU resource review and hardware test. |
| FUN-004 | F103 shall command immediate landing when the defined H743-failure condition is detected. | H743 unavailable or failure condition. | Fault-injection test; timing measurement. |
| FUN-005 | H743 and F103 shall provide SWD debug/recovery access. | Development, service, and bring-up. | Probe connection and debug test. |
| FUN-006 | H743 shall retain selectable BOOT0 access. | Development and recovery. | Inspection and boot-state test. |

### 3.2 Operating modes and state behavior

| Mode | Entry condition | Required behavior | Exit / fault behavior |
|---|---|---|---|
| Normal | Valid power and normal MCU operation. | H743 performs primary functions; F103 provides auxiliary/safety functions. | Transition behavior TO BE DECIDED. |
| H743 fault | F103 detects H743 unavailable according to the future safety boundary. | F103 commands immediate landing. | Detection timeout and recovery are TO BE DECIDED. |
| Boot / service | BOOT0 or service procedure selects recovery mode. | SWD/USB/service access remains available as designed. | Boot-state and reset behavior TO BE DECIDED. |
| Power abnormality | Brownout, reset, rail fault, or input loss. | Hardware response and safe output state are TO BE DECIDED. | Recovery and restart behavior TO BE DECIDED. |

### 3.3 Electrical system requirements

| ID | Parameter | Minimum | Nominal | Maximum | Unit | Conditions / note |
|---|---|---:|---:|---:|---|---|
| PWR-010 | Flight-controller board input | TO BE DECIDED | 5 | TO BE DECIDED | V | Supplied by power module; input tolerance and transient profile open. |
| PWR-011 | Servo supply | TO BE DECIDED | 6 | TO BE DECIDED | V | Current budget, distribution, and protection open. |
| PWR-012 | Board continuous current | TO BE DECIDED | TO BE DECIDED | TO BE DECIDED | A | Separate MCU, sensor, external-I/O, and servo budgets required. |
| PWR-013 | Sensor/MCU rail tolerance | TO BE DECIDED | TO BE DECIDED | TO BE DECIDED | V / % | Candidate rails in diagrams are not approved specifications. |
| PWR-014 | Brownout/reset threshold | TO BE DECIDED | TO BE DECIDED | TO BE DECIDED | V | Per MCU and rail; verification method TO BE DECIDED. |

### 3.4 External interfaces

The interface allocations below are user-confirmed at the logical interface level. Exact MCU pins, alternate functions, electrical levels, protection, rates, and conflict status are NOT_VERIFIED.

| ID | Interface / connector | Function | Direction | Electrical levels | Protocol / rate | Protection / constraints |
|---|---|---|---|---|---|---|
| IF-010 | Conn1 / Tel1 | Telemetry 1 | TO BE DECIDED | TO BE DECIDED | UART7 / rate TO BE DECIDED | Connector, protection, and pinout TO BE DECIDED. |
| IF-011 | Conn2 / Tel2 | Telemetry 2 | TO BE DECIDED | TO BE DECIDED | UART1 / rate TO BE DECIDED | Connector, protection, and pinout TO BE DECIDED. |
| IF-012 | Conn3 / GPS1 + compass | GPS UBX and compass | TO BE DECIDED | TO BE DECIDED | UART2 + I2C1 / rate TO BE DECIDED | Compass address, pull-ups, protection, and pinout TO BE DECIDED. |
| IF-013 | Conn4 / GPS2 | GPS2 reserved interface | TO BE DECIDED | TO BE DECIDED | UART3 / blank | Blank/reserved status and pinout TO BE DECIDED. |
| IF-014 | Conn5 / MS4525DO | Air-data sensor | TO BE DECIDED | TO BE DECIDED | I2C4, address `0x28` | Electrical levels, pull-ups, protection, and pinout TO BE DECIDED. |
| IF-015 | Conn6 / TF-Luna | Rangefinder | TO BE DECIDED | TO BE DECIDED | UART8 / rate TO BE DECIDED | Electrical levels, protection, and pinout TO BE DECIDED. |
| IF-016 | Conn7 / UART7 TX | Reserved UART transmit | Output | TO BE DECIDED | UART7 TX | Blank/reserved status and protection TO BE DECIDED. |
| IF-017 | Conn8 / VT L | Logical output | Output | TO BE DECIDED | TIM4_CH3 | Timer alternate function and electrical output not verified. |
| IF-018 | Conn9 / VT R | Logical output | Output | TO BE DECIDED | TIM4_CH4 | Timer alternate function and electrical output not verified. |
| IF-019 | Conn10 / SP2 | Reserved logical output | Output | TO BE DECIDED | TIM1_CH1 | Blank/reserved status and electrical output TO BE DECIDED. |
| IF-020 | Conn11 / TL2 | Logical output | Output | TO BE DECIDED | TIM15_CH1 | Timer alternate function and electrical output not verified. |
| IF-021 | Conn12 / TR2 | Logical output | Output | TO BE DECIDED | TIM15_CH2 | Timer alternate function and electrical output not verified. |
| IF-022 | USB FS | Service and later software flashing path | Bidirectional | TO BE DECIDED | USB FS | ESD/protection, VBUS, connector, routing, and enumeration TO BE DECIDED. |
| IF-023 | SWD | Debug and recovery | Bidirectional / service | TO BE DECIDED | SWD | SWDIO, SWCLK, NRST, GND, connector/test pads TO BE DECIDED. |
| IF-024 | H743↔F103 | MCU link | Bidirectional | TO BE DECIDED | USART / message protocol deferred | Instance, pins, rate, timeout, protection, and test access TO BE DECIDED. |

### 3.5 F103 PWM and expanded I/O

The logical allocation below is user-confirmed. Timer/channel labels are captured verbatim and are not claims that the STM32F103 package or alternate-function matrix supports them.

| ID | Logical output | Candidate allocation | Electrical output | Status |
|---|---|---|---|---|
| IF-030 | TILT L | TIM2_CH1 | TO BE DECIDED | CONFIRMED LOGICAL REQUIREMENT / RESOURCE NOT_VERIFIED |
| IF-031 | TILT R | TIM2_CH2 | TO BE DECIDED | CONFIRMED LOGICAL REQUIREMENT / RESOURCE NOT_VERIFIED |
| IF-032 | ESC L | TIM4_CH3 | TO BE DECIDED | CONFIRMED LOGICAL REQUIREMENT / RESOURCE NOT_VERIFIED |
| IF-033 | ESC R | TIM4_CH4 | TO BE DECIDED | CONFIRMED LOGICAL REQUIREMENT / RESOURCE NOT_VERIFIED |
| IF-034 | COAX T | TIM3_CH5 | TO BE DECIDED | CONFIRMED LOGICAL LABEL / RESOURCE NOT_VERIFIED |
| IF-035 | COAX B | TIM3_CH6 | TO BE DECIDED | CONFIRMED LOGICAL LABEL / RESOURCE NOT_VERIFIED |
| IF-036 | AIL L | TIM3_CH7 | TO BE DECIDED | CONFIRMED LOGICAL LABEL / RESOURCE NOT_VERIFIED |
| IF-037 | AIL R | TIM3_CH8 | TO BE DECIDED | CONFIRMED LOGICAL LABEL / RESOURCE NOT_VERIFIED |
| IF-038 | FlySky | Bulk pinheader | TO BE DECIDED | Connector pinout and electrical levels TO BE DECIDED. |

### 3.6 Environmental and reliability requirements

| ID | Parameter / condition | Required range or limit | Verification |
|---|---|---|---|
| ENV-001 | Operating temperature | TO BE DECIDED | Analysis / test TO BE DECIDED |
| ENV-002 | Storage temperature | TO BE DECIDED | Analysis / test TO BE DECIDED |
| ENV-003 | Vibration and shock | TO BE DECIDED | Analysis / test TO BE DECIDED |
| ENV-004 | Humidity, ingress, altitude, and maintenance | TO BE DECIDED | Analysis / test TO BE DECIDED |

### 3.7 Protection and fault behavior

| ID | Hazard / fault | Required response | Recovery method | Verification |
|---|---|---|---|---|
| SAF-010 | H743 unavailable | F103 commands immediate landing. | Timeout, reset, recovery, and F103-failure behavior TO BE DECIDED. | Fault-injection test; NOT_VERIFIED. |
| SAF-011 | H743↔F103 USART loss | Safe response and output ownership TO BE DECIDED. | TO BE DECIDED. | Fault-injection test; NOT_VERIFIED. |
| SAF-012 | 5 V input abnormality | Safe reset/output state TO BE DECIDED. | Power recovery procedure TO BE DECIDED. | Measurement and fault test; NOT_VERIFIED. |
| SAF-013 | 6 V servo rail fault | Protection and safe actuator state TO BE DECIDED. | TO BE DECIDED. | Measurement and fault test; NOT_VERIFIED. |
| SAF-014 | ESD, reverse polarity, overvoltage, and short circuit | Protection requirements TO BE DECIDED. | Service/recovery method TO BE DECIDED. | Analysis/test; NOT_VERIFIED. |

## 4. Hardware Architecture and Design Constraints

### 4.1 Functional block diagram

The user-provided architecture diagrams show an H743 main MCU, an F103 auxiliary MCU, sensor/interface blocks, USB/SWD, PWM/actuator paths, and a separate power architecture. The images are reference inputs only; native schematic and PCB files remain the design authority.

### 4.2 Functional blocks

| Block | Role | Inputs / outputs | Dependencies | Key constraints |
|---|---|---|---|---|
| H743 main controller | Primary flight-controller processing and interface host | Sensors, external interfaces, USB, SWD, USART, outputs | 5 V input and defined rails | Part number confirmed; pins/resources NOT_VERIFIED. |
| F103 auxiliary controller | PWM/ESC, expanded I/O, and safety function | USART, PWM outputs, FlySky, safety path | H743 status and defined power/reset | Part number confirmed; timer/resource/safety implementation NOT_VERIFIED. |
| IMU subsystem | Two SPI IMU interfaces | SPI, CS, DRDY, reset | Selected sensor parts and rail | MFR/MPN and allocation TO BE DECIDED. |
| Barometer subsystem | Two I2C barometer interfaces | I2C, address, pull-ups | Selected sensor parts and rail | MFR/MPN and bus strategy TO BE DECIDED. |
| Magnetometer subsystem | Two I2C magnetometer interfaces | I2C, address, placement | Selected sensor parts and external compass decision | Second magnetometer allocation TO BE DECIDED. |
| H743 external I/O | Telemetry, GPS, compass, air-data, rangefinder, logical outputs | UART/I2C/timer interfaces | H743 resource allocation | Exact pins/electrical implementation NOT_VERIFIED. |
| F103 PWM/I/O | TILT, ESC, COAX, AIL, FlySky | Timer/PWM and bulk connector | F103 resource allocation | Timer/channel validity and electrical drive TO BE DECIDED. |
| USB/SWD/BOOT0 | Service, debug, recovery | USB FS, SWD, BOOT0 | H743/F103 reset and power | Access/protection/circuit NOT_VERIFIED. |
| Power subsystem | 5 V board input and 6 V servo supply | Rails, returns, protection | Power module and distribution | Tolerances/current/protection TO BE DECIDED. |

### 4.3 Power architecture

- Confirmed board input requirement: 5 V from the power module.
- Confirmed servo supply requirement: 6 V.
- The diagram-derived upstream 6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 5 V, 3.3 V, 3.3 V_IMU, and 6 V UBEC arrangement is a candidate architecture only.
- Rail dependencies, current budgets, load steps, sequencing, brownout, reverse-polarity protection, overvoltage protection, transient handling, grounding, filtering, and thermal limits are TO BE DECIDED.

### 4.4 Clock, reset, boot and programming

- H743 shall retain selectable BOOT0 access.
- H743 and F103 shall provide SWD access.
- USB FS shall be physically available on H743 for later Software-owned flashing/QGC integration.
- Clock sources, reset topology, power-on reset, watchdog interaction, boot-time pin states, F103 boot behavior, and service procedures are TO BE DECIDED.

### 4.5 Control, sensing, analog and digital considerations

- SPI/I2C bus ownership, chip-select, data-ready/interrupt, pull-up, address, DMA, timing, and recovery are TO BE DECIDED.
- PWM output voltage, drive method, current capability, update rate, input capture, actuator connector pinout, arming, and failsafe behavior are TO BE DECIDED.
- USART electrical levels, rate, timeout, framing, isolation, protection, and message protocol are TO BE DECIDED except for the confirmed physical protocol family `USART`.
- Signal integrity, return paths, sensor noise, magnetic placement, and EMI/EMC constraints are TO BE DECIDED and NOT_VERIFIED.

### 4.6 Component selection constraints

| ID | Category / function | Mandatory constraints | Preferred constraints | Sourcing / lifecycle |
|---|---|---|---|---|
| CMP-001 | Main MCU | Must be STM32H743VIT6. | TO BE DECIDED. | Availability, package, lifecycle, and approved source TO BE DECIDED. |
| CMP-002 | Auxiliary MCU | Must be STM32F103C8T6. | TO BE DECIDED. | Availability, package, lifecycle, and approved source TO BE DECIDED. |
| CMP-003 | IMU | Two SPI positions required. | Candidate parts from diagrams are not approved. | MFR/MPN, availability, driver, lifecycle TO BE DECIDED. |
| CMP-004 | Barometer | Two I2C positions required. | Candidate parts from diagrams are not approved. | MFR/MPN, availability, driver, lifecycle TO BE DECIDED. |
| CMP-005 | Magnetometer | Two I2C positions required. | Candidate parts from diagrams are not approved. | MFR/MPN, availability, driver, lifecycle TO BE DECIDED. |
| CMP-006 | Regulator, protection, connector, PDB/UBEC, and interface parts | Electrical requirements shall be satisfied. | Specific parts TO BE DECIDED. | MFR/MPN, availability, lifecycle, and approved source TO BE DECIDED. |

### 4.7 Engineering calculations and margins

| Analysis | Inputs / operating corner | Method / reference | Result | Margin / open questions |
|---|---|---|---|---|
| Board input current | 5 V input, MCU/sensor/I/O load | TO BE DECIDED | NOT_VERIFIED | Current budget and duty cycle TO BE DECIDED. |
| Servo rail current | 6 V rail and actuator load | TO BE DECIDED | NOT_VERIFIED | Servo count, peak current, and protection TO BE DECIDED. |
| Power rail tolerance | All MCU/sensor rails | TO BE DECIDED | NOT_VERIFIED | Rail nominal/min/max and load-step limits TO BE DECIDED. |
| Thermal margin | MCU, regulator, protection, and output drivers | TO BE DECIDED | NOT_VERIFIED | Ambient, dissipation, copper, and cooling TO BE DECIDED. |
| Safety response timing | H743 failure to F103 landing command | TO BE DECIDED | NOT_VERIFIED | Timeout, detection method, actuator path, and test method TO BE DECIDED. |

## 5. PCB Design Specification

### 5.1 Mechanical envelope

| ID | Item | Requirement / limit | Verification |
|---|---|---|---|
| MEC-001 | Board outline | Diagram reference is approximately `90 mm × 95 mm`; exact outline TO BE DECIDED. | Native PCB inspection / measurement. |
| MEC-002 | Mounting pattern | TO BE DECIDED. | Native PCB inspection / measurement. |
| MEC-003 | Connector orientation and service access | TO BE DECIDED. | Mechanical inspection. |
| MEC-004 | Height, keepouts, enclosure, and environmental constraints | TO BE DECIDED. | Mechanical inspection / analysis. |

### 5.2 Fabrication and stackup

| ID | Parameter | Requirement / target | Fabricator confirmation |
|---|---|---|---|
| PCB-001 | Copper layer count | TO BE DECIDED. | TO BE DECIDED. |
| PCB-002 | Stackup, dielectric, and copper weight | TO BE DECIDED. | TO BE DECIDED. |
| PCB-003 | Minimum trace and spacing | TO BE DECIDED. | TO BE DECIDED. |
| PCB-004 | Hole, via, and annular-ring capability | TO BE DECIDED. | TO BE DECIDED. |
| PCB-005 | Soldermask and surface finish | TO BE DECIDED. | TO BE DECIDED. |

### 5.3 Layout and routing constraints

| ID | Circuit / net class / region | Constraint | Reason | Verification |
|---|---|---|---|---|
| PCB-010 | H743/F103 power and returns | Width, return path, via, and load-step constraints TO BE DECIDED. | Current and noise control. | Layout review / analysis. |
| PCB-011 | IMU, barometer, and magnetometer regions | Placement, vibration, magnetic, and noise constraints TO BE DECIDED. | Sensor integrity. | Placement review / test. |
| PCB-012 | USB FS | Routing, ESD, VBUS, connector, and return-path constraints TO BE DECIDED. | USB physical integrity and protection. | Layout review / hardware test. |
| PCB-013 | SWD and BOOT0 | Probe access and reset/boot-state constraints TO BE DECIDED. | Debug and recovery. | Inspection / debug test. |
| PCB-014 | PWM/actuator outputs | Return path, drive, protection, and connector constraints TO BE DECIDED. | Actuator integrity and safety. | Layout review / electrical test. |
| PCB-015 | USART H743↔F103 | Routing, voltage compatibility, return path, and test access TO BE DECIDED. | Inter-MCU safety/control path. | Review / hardware test. |

### 5.4 Power integrity, signal integrity and EMC

Rail voltage-drop limits, ripple/noise limits, decoupling, filtering, return paths, ground strategy, USB routing, sensor noise, PWM output integrity, USART integrity, and EMI/EMC expectations are TO BE DECIDED. No compliance or signal-integrity result is established by the current diagrams or candidate mapping.

### 5.5 Thermal and current carrying

Hot components, copper spreading, vias, allowable temperature rise, load profile, thermal model assumptions, servo current paths, and protection-device dissipation are TO BE DECIDED.

### 5.6 Design-rule implementation in KiCad

| Specification requirement | KiCad mechanism, if supported | Manual / external check |
|---|---|---|
| Clearance and width | TO BE DECIDED net classes and board rules | DRC plus review |
| USB FS routing | TO BE DECIDED rules | Layout review and hardware test |
| Power and return paths | TO BE DECIDED net classes/regions | Current-path review |
| Sensor and clock placement | TO BE DECIDED constraints | Placement review |
| SWD/BOOT0/test access | TO BE DECIDED footprints/test pads | Inspection and bring-up |

## 6. Manufacturing, Assembly and Service

### 6.1 Manufacturability and assembly

| ID | Requirement | Rationale | Verification |
|---|---|---|---|
| MFG-001 | The fabrication process, stackup, materials, copper weight, and surface finish shall be defined before release. | Controlled manufacturing. | Fabricator review. |
| MFG-002 | Component footprints, package variants, alternates, assembly notes, and polarity shall be controlled before release. | Assembly correctness. | BOM/assembly review. |
| MFG-003 | Connector orientation, test access, rework access, and service access shall be defined. | Bring-up and serviceability. | Assembly/mechanical review. |
| MFG-004 | The final part list shall contain only approved or explicitly dispositioned part numbers. | Prevent unconfirmed candidate parts from entering release. | BOM audit. |

### 6.2 Debug and testability

| ID | Signal / function | Access / observation requirement | Method |
|---|---|---|---|
| TST-001 | H743 SWD | Connector or test pads with SWDIO, SWCLK, NRST, and GND. | Inspection and debug test. |
| TST-002 | F103 SWD | Connector or test pads with SWDIO, SWCLK, NRST, and GND. | Inspection and debug test. |
| TST-003 | H743 BOOT0 | Selectable and observable boot state. | Inspection and boot-state test. |
| TST-004 | 5 V board input | Input test point and current/voltage measurement access. | Inspection and measurement. |
| TST-005 | 6 V servo rail | Rail test point and current/voltage measurement access. | Inspection and measurement. |
| TST-006 | H743↔F103 USART | Physical test access and signal observation. | Inspection and hardware test. |
| TST-007 | F103 safety path | Fault-injection access for H743-unavailable condition. | Fault-injection test. |

## 7. Verification Plan (Planning Only)

No automatic gates: this table plans how requirements could be checked. It does not declare phase completion, design approval, or release readiness.

| Requirement ID | Verification method | Planned evidence / procedure | Result | Reviewer |
|---|---|---|---|---|
| MCU-001/002 | Inspection | Native schematic/package review. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| IF-001 | Inspection / Test | USART allocation review and physical link test. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| SEN-001/002/003 | Inspection / Test | Bus allocation review and sensor electrical access test. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| PWR-001/002 | Analysis / Test | Power-tree review, rail measurement, load/current test. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| SAF-001 | Test | H743 fault injection and F103 immediate-landing response measurement. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| IF-010–IF-024 | Inspection / Test | Connector, pin, electrical-level, protection, and interface test. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| IF-030–IF-038 | Inspection / Test | Timer/resource review and PWM/expanded-I/O electrical test. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| PCB-010–PCB-015 | Review / Analysis / Test | Layout, return path, DRC, signal, power, and hardware review. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |
| TST-001–TST-007 | Inspection / Test | Test-point and debug-access inspection followed by bring-up tests. | NOT_VERIFIED | Human reviewer TO BE DECIDED. |

## 8. Design Decisions and Open Items

### 8.1 Decisions

| Decision ID | Topic | Selected option | Alternatives / reasoning | Date / owner |
|---|---|---|---|---|
| DEC-001 | Main MCU part number | STM32H743VIT6 | Confirmed by user; implementation not verified. | 2026-10-12 / Human owner |
| DEC-002 | Auxiliary MCU part number | STM32F103C8T6 | Confirmed by user; implementation not verified. | 2026-10-12 / Human owner |
| DEC-003 | H743↔F103 physical interface protocol | USART | Detailed instance, pins, electrical levels, and message protocol TO BE DECIDED. | 2026-10-12 / Human owner |
| DEC-004 | Firmware implementation boundary | Deferred and non-blocking for current hardware path | Software team will decide firmware details later. | 2026-10-12 / Human owner |

### 8.2 Open questions and assumptions

| Item | Description | Impact | Owner / next action |
|---|---|---|---|
| OPEN-001 | Exact H743/F103 pins and alternate functions | May invalidate the candidate allocation. | Hardware review / P1. |
| OPEN-002 | USART instance, pins, voltage levels, rate, timeout, and recovery | Affects safety/control path. | Hardware + Software / P1/P2. |
| OPEN-003 | Timer/channel validity for all H743/F103 labels | May require reassignment or logical-to-physical mapping. | Hardware review / P1. |
| OPEN-004 | Sensor MFR/MPN and electrical properties | Affects footprint, rail, layout, drivers, and verification. | Human owner / P0. |
| OPEN-005 | Second magnetometer allocation | Affects sensor redundancy and connector/bus architecture. | Human owner / P0. |
| OPEN-006 | 5 V input tolerance, board current, and rail budgets | Affects power design and protection. | Hardware review / P0/P2. |
| OPEN-007 | 6 V servo current, protection, and distribution | Affects power and actuator safety. | Hardware review / P0/P2. |
| OPEN-008 | Safety detection timing and immediate-landing boundary | Affects F103 logic, output ownership, and test method. | Human owner / P0/P2/P4. |
| OPEN-009 | Board outline, mounting, connector orientation, and environment | Affects PCB and mechanical release. | Human owner / P0/P3. |
| OPEN-010 | All non-MCU part numbers | No non-MCU part is approved by this document. | Human owner / component selection gate. |

## 9. Specification Change Notes

| Revision | Date | Description | Human-approved by (if applicable) |
|---|---|---|---|
| 0.1 | 2026-10-12 | Initial advanced hardware specification draft based on confirmed H743/F103 part numbers, confirmed USART protocol, user-provided interface requirements, and diagram-derived references. | TO BE DECIDED |

## Current verdict

**Draft only — NOT_VERIFIED and NOT FOR FABRICATION.**

The specification is sufficiently structured for hardware P1 allocation and conflict review. It does not approve any non-MCU part number, exact pin mapping, timer allocation, power limit, safety timing, schematic, PCB, or fabrication release.

