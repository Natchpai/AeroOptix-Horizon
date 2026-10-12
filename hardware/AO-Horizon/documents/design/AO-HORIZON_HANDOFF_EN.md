# AeroOptix-Horizon — Custom PX4 Flight Controller Handoff Package

This document is prepared for handoff to a coworker for review and continuation of the AeroOptix-Horizon Custom PX4 Flight Controller project. It is provided to the user for download only and is **not sent to the coworker automatically**.

## 1. Scope and status

| Item | Status | Details |
|---|---|---|
| Project type | **CONFIRMED** | Custom PX4 Flight Controller |
| Reference architecture | **CONFIRMED** | Pixhawk 6C is used as a conceptual and functional reference; this does not confirm copying its schematic, PCB, or pinout |
| Firmware direction | **CONFIRMED** | Custom PX4 firmware for the custom hardware |
| MCU part-number baseline | **CONFIRMED PART NUMBERS / IMPLEMENTATION NOT VERIFIED** | Main MCU: STM32H743VIT6; auxiliary/secondary MCU: STM32F103C8T6 |
| Nucleo usage | **CONFIRMED** | Nucleo is used through the Boot + QGC path only, according to the agreed test/bring-up workflow |
| Firmware integration details | **DEFERRED / NON-BLOCKING** | Software may choose the PX4 target, bootloader, firmware contract, and detailed flashing implementation later; hardware work proceeds on electrical and resource requirements |
| Current design maturity | **PROPOSED / NOT VERIFIED** | The project is at the allocation and candidate-mapping stage, not at release-ready design stage |

## 2. MCU baseline and programming/debug

### 2.1 STM32H743VIT6

- **PROPOSED:** Main flight-controller MCU for PX4 execution and primary sensor, communication, actuator, and system functions
- **CONFIRMED:** The Software team confirmed the USB FS flashing approach through the H743 using QGC
- **CONFIRMED:** H743 USB FS is the firmware flashing channel
- **CONFIRMED:** BOOT0 must remain selectable to support boot/flash selection during development and recovery
- **CONFIRMED:** An SWD debug interface is required
- **TBD / DEFERRED:** Bootloader details, USB descriptor, PX4 board target, and detailed software boot sequencing; hardware reset/BOOT0 access remains in scope

### 2.2 STM32F103C8T6

- **CONFIRMED:** Required during operation as the auxiliary I/O and PWM controller for ESC-related outputs and expanded I/O
- **CONFIRMED SAFETY REQUIREMENT:** If the H743 is not operating, the F103 shall command immediate landing; fault-detection timing and implementation are not verified
- **CONFIRMED:** H743↔F103 physical link uses USART; protocol details remain deferred
- **CONFIRMED:** It must be flashable through the H743 USB FS workflow as confirmed by the Software team; this does not confirm a separate USB boot path for the F103
- **CONFIRMED:** SWD debug access is required
- **TBD / DEFERRED:** USART instance/pins, voltage levels, baud/rate, timeout, recovery behavior, firmware-update coordination, and detailed flight-mode behavior

## 3. Sensor set

The following quantities and interfaces are confirmed at the requirement level. Exact parts are still open:

| Sensor group | Quantity / interface | Status | Current limitation |
|---|---:|---|---|
| IMU | 2 × SPI | **CONFIRMED** | MFR/MPN, voltage, data rate, chip-select, and interrupt allocation are not selected |
| Barometer | 2 × I2C | **CONFIRMED** | MFR/MPN, I2C address, and bus separation/redundancy strategy are not selected |
| Magnetometer | 2 × I2C | **CONFIRMED** | MFR/MPN, I2C address, bus topology, and placement are not selected |

**Sensor MFR/MPN:** **TBD / DEFERRED** until part selection and checks for availability, driver support, electrical limits, layout, and noise sensitivity are completed.

## 3.1 Diagram-derived hardware snapshot

The following items are transcribed from the user-provided architecture and power diagrams. Only `STM32H743VIT6`, `STM32F103C8T6`, and the H743↔F103 `USART` interface protocol are currently confirmed. All other part numbers remain **UNCONFIRMED / TBD**, even when visible in a diagram. Diagram-derived implementation details remain **SOURCE IMAGE / PROPOSED / NOT VERIFIED** until the native design source, part list, and engineering review confirm them:

- The controller board is labeled `FC_H743 rev2` with an approximate envelope of `~90 mm × 95 mm`.
- The MCU blocks shown are `STM32H743VIT6` and `STM32F103C8T6`.
- Candidate IMUs shown are `ICM-42688-P` and `BMI088`.
- Candidate barometers shown are `BMP280` and `MS5611`.
- `IST8310` is visibly shown as an onboard magnetometer candidate. The second magnetometer requirement is not resolved by the image alone; an external GPS/compass-related block is also shown and requires explicit allocation.
- USB FS protection, microSD, SWD, telemetry/GPS/RC/UART, safety, companion-computer, air-data/rangefinder, and actuator-related blocks are shown, but exact connectors and electrical specifications remain open.
- The power diagram shows a 6S battery path through XT90-S, PM02D, and CRIUS PDB v1.0, with 5 V, 3.3 V, 3.3 V_IMU, and a separate 6 V UBEC path. These are diagram-derived proposals, not verified power limits.
- Four ESC paths are visibly labeled; the servo/actuator channel count is not sufficiently clear from the image and remains open.

## 3.2 User-confirmed hardware interface allocation

The following allocations were provided directly by the user. They are confirmed requirements, but exact MCU pin numbers, alternate functions, electrical levels, timer capability, and conflict status remain subject to P1/P2 review.

### H743 interfaces

| Connector / function | Allocation |
|---|---|
| Conn1 | Tel1 — UART7 |
| Conn2 | Tel2 — UART1 |
| Conn3 | GPS1 + compass — UBX via UART2; compass via I2C1 |
| Conn4 | GPS2 — UART3, blank |
| Conn5 | MS4525DO — I2C4, address `0x28` |
| Conn6 | TF-Luna — UART8 |
| Conn7 | UART7 TX, blank |
| Conn8 | VT L — TIM4_CH3 |
| Conn9 | VT R — TIM4_CH4 |
| Conn10 | SP2 — TIM1_CH1, blank |
| Conn11 | TL2 — TIM15_CH1 |
| Conn12 | TR2 — TIM15_CH2 |
| USB | USB FS |
| Debug | SWD |

### F103 PWM and expanded I/O

| Logical output | Allocation |
|---|---|
| TILT L | TIM2_CH1 |
| TILT R | TIM2_CH2 |
| ESC L | TIM4_CH3 |
| ESC R | TIM4_CH4 |
| COAX T | TIM3_CH5 |
| COAX B | TIM3_CH6 |
| AIL L | TIM3_CH7 |
| AIL R | TIM3_CH8 |
| FlySky | Bulk pinheader / connector pinout TBD |

Timer/channel labels are recorded verbatim from the user input. They are not claims that the STM32F103 package or alternate-function matrix supports them. P1 must validate every assignment against the selected MCU package and native design data.

### Board power inputs

- Flight-controller board input: **5 V from the power module** — confirmed requirement; input tolerance and current budget are TBD.
- Servo supply: **6 V** — confirmed requirement; current budget, protection, and distribution are TBD.
- The upstream 6S/PM02D/CRIUS PDB arrangement remains a diagram-derived system proposal until explicitly approved.

## 4. USB, BOOT0, and SWD constraints

The following requirements must remain in the schematic and PCB design:

1. H743 USB FS must reach the connector and include the support circuitry required for QGC firmware flashing.
2. BOOT0 must be selectable and accessible according to the actual operating procedure, without creating an ambiguous boot state.
3. Both H743 and F103 must provide SWD access for debug, recovery, and manufacturing bring-up.
4. Reset, power sequencing, ground reference, and protection for USB/SWD/BOOT0 must be defined before fabrication release.
5. Confirmation that the USB flash workflow is possible does not by itself confirm the schematic, signal integrity, bootloader image, or QGC board integration.

## 5. Candidate MCU peripheral allocation / pin mapping v0.1

The table below is **CANDIDATE ONLY** and is intended solely as a starting point for conflict review.

> **Important warning:** This v0.1 pin mapping has **not passed conflict checking**. It must not be described as verified, validated, final, or fabrication-ready until the required evidence is complete.

| Function | Proposed owner | Candidate interface/resource | Status | Checks still required |
|---|---|---|---|---|
| PX4 main execution | H743 | H743 core/peripheral set | **PROPOSED** | PX4 target, clock, DMA, interrupt, and resource conflicts |
| IMU-1 | H743 | SPI instance 1 + CS + DRDY | **PROPOSED** | Exact pins, alternate functions, DMA, interrupt priority, and electrical limits |
| IMU-2 | H743 | SPI instance 2 or suitable bus arrangement + CS + DRDY | **PROPOSED** | Bus independence, CS/DRDY conflicts, driver support, DMA, and timing |
| Barometer-1 | H743 | I2C bus candidate 1 | **PROPOSED** | Address, pull-up, bus ownership, level compatibility, and recovery |
| Barometer-2 | H743 | I2C bus candidate 2 or address-separated topology | **PROPOSED** | Address collision, redundancy intent, pull-up, and bus recovery |
| Magnetometer-1 | H743 | I2C bus candidate | **PROPOSED** | Address, magnetic placement, bus loading, and noise |
| Magnetometer-2 | H743 | I2C bus candidate | **PROPOSED** | Address, magnetic placement, bus loading, and noise |
| USB FS flash path | H743 | USB FS D+/D- + VBUS/ESD/reset support | **CONFIRMED requirement / PROPOSED implementation** | Exact pins, USB routing, protection, bootloader, and QGC integration |
| H743 ↔ F103 link | H743/F103 | USART; exact instance/pins TBD | **CONFIRMED INTERFACE PROTOCOL / IMPLEMENTATION NOT VERIFIED** | USART instance, pins, voltage levels, baud/rate, fail-safe behavior, and firmware contract details |
| H743 SWD | H743 | SWDIO/SWCLK/RESET/GND access | **CONFIRMED requirement / TBD allocation** | Connector/test pads, routing, probe access, and production policy |
| F103 SWD | F103 | SWDIO/SWCLK/RESET/GND access | **CONFIRMED requirement / TBD allocation** | Connector/test pads, routing, probe access, and production policy |
| H743 BOOT0 | H743 | Selectable BOOT0 network | **CONFIRMED requirement / TBD implementation** | Default state, pull resistor, user/service access, and reset interaction |
| F103 BOOT0 | F103 | Boot selection as required by the final architecture | **TBD** | Decide whether it is required based on the final F103 role |

### 5.1 Minimum conflict-check checklist

Before this mapping can be treated as a usable baseline, check at least:

- Alternate-function conflicts for every H743 and F103 pin
- SPI/I2C instances, chip-selects, data-ready/interrupts, and DMA channel conflicts
- USB FS pin assignment, VBUS sensing, USB protection, and connector orientation
- SWDIO/SWCLK/NRST/BOOT0 conflicts with peripherals or nets that could prevent debug/recovery
- Timer/PWM/actuator resources and the DMA/interrupt priorities required by PX4
- UART/CAN/telemetry/RC/GPS and other communication resources that may be added later
- Voltage domains, IO levels, pull-up/pull-down states, reset states, and boot-time pin behavior
- Package pin availability, reserved pins, unused pins, and ERC/DRC implications
- Hardware net labels and reserved resources are documented so the Software team can map them later; final PX4 board configuration and firmware contract are deferred

The review result must be retained as traceable evidence, including mapping revision, reviewer, conflict list, resolutions, and test results.

## 6. Power, communication, and actuator requirements

The following are **PROPOSED REQUIREMENTS** for design initiation. They are not yet approved electrical specifications.

### 6.1 Power

- **PROPOSED:** Separate digital MCU, sensor, and external-I/O power domains according to noise and current requirements
- **PROPOSED:** Define input-voltage range, regulator topology, current budget, sequencing, brownout behavior, and reset behavior
- **PROPOSED:** Provide decoupling, bulk capacitance, filtering, protection, and test points for each power domain
- **TBD:** Actual source limits, nominal/maximum voltage, transient profile, rail current budgets, protection, sequencing, and thermal limits. The diagram-derived 6S/5 V/3.3 V/3.3 V_IMU/6 V arrangement remains unverified.

### 6.2 Communication

- **CONFIRMED requirement / PROPOSED implementation:** Reserve resources for USB FS, telemetry, debug, the user-defined H743 interfaces, and the USART H743↔F103 link
- **PROPOSED:** Consider UART/CAN/other links according to the flight-controller and external-system roles
- **TBD:** Electrical standards, termination, isolation, exact connector pinout, USART instance/pins, and protocol ownership

### 6.3 Actuator / I/O

- **PROPOSED:** Allocate PWM/timer outputs for actuators based on required quantity and update rate
- **PROPOSED:** Make safety-critical outputs, arming state, failsafe state, and power-enable behavior reviewable
- **CONFIRMED requirement / NOT VERIFIED implementation:** F103 owns PWM/expanded I/O for ESC-related outputs, TILT, COAX, AIL, and FlySky expansion.
- **TBD:** Output voltage, current/drive method, connector pinout, input capture, servo channel count, and failsafe policy. The user-provided timer/channel labels require P1 validation.

## 7. Current status

Current status: **DESIGN DRAFT — NOT VERIFIED / NOT READY FOR FABRICATION**

Confirmed items:

- The project is a Custom PX4 Flight Controller using Pixhawk 6C as a reference
- The proposed MCU baseline is STM32H743VIT6 + STM32F103C8T6
- Confirmed sensor count/interface: 2×SPI IMU, 2×I2C barometer, and 2×I2C magnetometer
- Sensor MFR/MPN selection is deferred
- H743 USB FS is the QGC firmware-flashing path according to the Software team confirmation
- Selectable BOOT0 must be retained
- SWD debug access is required
- F103 is required during operation for auxiliary I/O, PWM/ESC control, expanded I/O, and immediate-landing safety behavior if H743 is unavailable
- H743↔F103 physical link is USART
- H743 interface allocation and F103 PWM/expanded-I/O allocation are user-confirmed requirements, pending pin/resource validation
- Board power inputs are 5 V from the power module and 6 V for servo power

Not yet confirmed:

- Pin mapping and peripheral allocation
- Exact MCU pin numbers, alternate functions, DMA, and interrupt assignments
- Sensor MFR/MPN, addresses, and electrical characteristics
- Exact MCU pin numbers, alternate functions, timer capability, USART instance, electrical levels, and interrupt/DMA assignments
- Power tolerance, current budget, rail topology, communication electrical standards, and actuator electrical specification
- Safety fault-detection timing and the hardware boundary for the F103 immediate-landing command
- PX4 board target, bootloader integration, and QGC board support
- Schematic/PCB correctness, ERC/DRC, signal integrity, thermal margin, and fabrication readiness

## 8. Prioritized next steps

### P0 — Close architecture-impacting requirements

1. Validate the user-confirmed F103 role, USART link, safety boundary, and PWM/expanded-I/O allocations against the selected MCU package and native design data.
2. Validate the user-confirmed H743 connectors and interface resources, including the blank/reserved connections.
3. Select sensor MFR/MPN or define verifiable selection criteria.
4. Define power input, voltage rails, current budget, sequencing, and protection requirements.

**P0 gate:** No remaining `TBD` may prevent selection of the MCU resources, bus topology, or connector/power architecture.

### P1 — Complete allocation and conflict review

1. Convert candidate mapping v0.1 and the user-confirmed interface allocation into a mapping revision with actual pins and alternate functions.
2. Check resource conflicts, DMA, interrupts, timers/PWM, boot/debug, and voltage domains.
3. Check I2C address/bus strategy and SPI independence for all sensors.
4. Record conflicts, resolutions, and reviewer evidence.

**P1 gate:** The mapping passes a documented conflict review. It may then be called `ALLOCATED`, but not `VERIFIED` until schematic and bench evidence are available.

### P2 — Schematic and hardware interface boundary

1. Create the schematic from the P1 allocation while retaining BOOT0, USB FS, and SWD access.
2. Define net names, connector pinout, reset/boot behavior, and test points.
3. Reserve the hardware resources required for a later PX4 board configuration, bootloader, and H743 USB/QGC workflow.
4. Document the H743↔F103 physical interface and resource ownership; defer software protocol details.
5. Run ERC and perform a line-by-line schematic review using the required evidence.

**P2 gate:** Hardware schematic review is closed, electrical interfaces and reserved resources are documented, and no unresolved hardware blocker affects bring-up. Firmware contract ownership and version may remain deferred.

### P3 — PCB and fabrication release

1. Complete placement/routing with attention to IMUs, barometers, magnetometers, USB, clock, power, and debug access.
2. Check DRC, return paths, preliminary power integrity, thermal/current constraints, and manufacturability.
3. Confirm BOM, footprints, alternate parts, assembly notes, and test-point access.
4. Create a hardware release package linked to the schematic/PCB/BOM revisions and explicitly record firmware integration as deferred.

**P3 gate:** A Human engineering owner approves fabrication release with ERC/DRC evidence and a release manifest.

### P4 — Bring-up and validation

1. Check for shorts, rails, current consumption, and reset/BOOT0 state before loading firmware.
2. Test SWD access for both H743 and F103.
3. Test the H743 USB FS hardware path and preserve the physical path for later Software-team enumeration/QGC testing.
4. Defer bootloader, PX4 startup, sensor detection, and calibration-flow verification to the Software-owned follow-up.
5. Test the H743↔F103 physical link and electrical access; defer protocol behavior, actuator software, and software fault policy.
6. Record results in a bring-up log with hardware revision, available firmware revision, test conditions, and any deferred software items.

**P4 gate:** Repeatable bench bring-up evidence exists, and remaining issues are classified as closed, accepted limitations, or deferred obligations with an owner and next action.

## 9. Handoff rules

- Do not use peripheral or sensor counts as evidence that the design has passed review.
- Do not call candidate pin mapping v0.1 verified or final.
- When information is incomplete, use `TBD`, `NOT VERIFIED`, or `MISSING_INFORMATION` instead of inference.
- Native design files, firmware configuration, and test evidence become the source of truth once implementation starts.
- Every mapping change must increment the revision and document its reason and impact on schematic, PCB, and firmware.
- Final fabrication approval and final engineering decisions remain with the Human engineering owner.

## 10. Short handoff summary

The project is a Custom PX4 Flight Controller using Pixhawk 6C as a reference, with STM32H743VIT6 as the proposed main MCU and STM32F103C8T6 as the confirmed operational auxiliary I/O/PWM/safety MCU role. The user confirmed the H743 connector allocation, F103 PWM/expanded-I/O allocation, USART H743↔F103 link, 5 V board input, and 6 V servo supply. Sensor MFR/MPN selection, exact pin/alternate-function validation, timer capability, electrical limits, power budgets, and safety timing remain open. Candidate pin mapping v0.1 is only a draft for starting conflict review and **has not been verified**. Firmware implementation remains deferred and non-blocking; the next hardware action is P1 validation of the confirmed resource allocation.

