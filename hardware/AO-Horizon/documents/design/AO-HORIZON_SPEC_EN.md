# Hardware Design Specification: AeroOptix-Horizon

| Property             | Value |
| -------------------- |---|
| Project              | AeroOptix-Horizon |
| Document owner       | Human engineering owner (TBD) |
| Document revision    | 0.11 |
| Last updated         | 2026-10-24 |
| Design tool          | KiCad 10 (saved files written by eeschema 10.0) |
| Hardware phase       | TBD (declared by the human) |
| Related baseline     | FC_H743 rev2 reference from user-provided diagrams; native design baseline not established |
| Specification status | Draft / not for fabrication |

**Conventions**

- `CONFIRMED`: the human owner confirmed the requirement or value.
- `NOT_VERIFIED`: no evidence exists yet. This applies to every requirement in this document unless a row says otherwise.
- `TBD`: to be decided. A value written as `TBD`, or left out, is open.
- A part shown in a diagram is a candidate only. It is not an approved part number.

**Part-number boundary:** Only `STM32H743VIT6`, `STM32F103C8T6`, `ICM-45686` (2 × IMU, DEC-008), `ICP-20100` (barometer 1, DEC-010), `BMP581` (barometer 2, DEC-010; fallback BMP384), `IST8310` (iSentek magnetometer, DEC-011) and `TPS62142RGTR` (main 3.3 V buck, DEC-012) are confirmed part numbers. The H743↔F103 interface is confirmed as `USART` with the px4io protocol (DEC-015). All other part numbers are `TBD`. This includes regulators, protection devices, power modules, connectors, and interface ICs.

## 1. Project Definition

### 1.1 Purpose and application

A custom PX4 flight controller hardware platform with a dual-MCU architecture. The STM32H743VIT6 is the main flight-controller MCU and drives the 4 motor outputs. The STM32F103C8T6 is the IO MCU: it runs px4io firmware and drives the 8 servo outputs, the safety switch and the servo failsafe (DEC-015, DEC-016).

Pixhawk 6C and Pixhawk 6X are conceptual and functional references. Their schematic and PCB are not copied. The pin allocation follows Pixhawk 6C (`px4/fmu-v6c`) on the H743 and `px4/io-v2` on the F103, by team decision (DEC-014).

### 1.2 Scope

**In scope:**

- H743 main-MCU hardware architecture
- F103 IO MCU hardware: servo PWM, safety switch, servo rail sense and failsafe
- H743↔F103 USART physical interface
- Sensor interfaces: 2 × SPI IMU, 2 × I2C barometer, 1 × I2C magnetometer (DEC-011)
- H743 external interfaces and F103 PWM/expanded-I/O allocation provided by the user
- 5 V flight-controller board input and 6 V servo supply
- USB FS, BOOT0, SWD, reset, protection, testability, PCB, manufacturing, and bring-up requirements
- Verification planning through hardware bring-up

**Out of scope or deferred:**

- PX4 board port (software team: PX4 v1.16.2, based on `px4/fmu-v6c`, DEC-014)
- Bootloader implementation, including the px4io build for the 8 MHz F103 crystal (DEC-017)
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
| REF-04    | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | 0.8 | Execution and evidence checklist |
| REF-05    | Pixhawk 6X reference architecture | Rev 8 | Conceptual and functional reference only |
| REF-06    | `AO-HORIZON_PINMAP_DECISIONS_EN.md` | 0.2, 2026-10-24 | Team answers behind DEC-014 to DEC-018 |
| REF-07    | `AO-HORIZON_PINMAP_REVIEW_EN.md` | 0.3, 2026-10-24 | Pinmap agreed with the software team |
| REF-08    | PX4-Autopilot `boards/px4/fmu-v6c` and `boards/px4/io-v2` | Tag v1.16.2 | Pin and firmware basis for the port (DEC-014) |

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
| SYS-002 | Pixhawk 6C (REF-01) and Pixhawk 6X (REF-05) shall be used as conceptual and functional references. | No copied schematic or PCB. The pin allocation follows `px4/fmu-v6c` (H743) and `px4/io-v2` (F103), by team decision (DEC-014). | Architecture review. |
| MCU-001 | The main MCU shall be STM32H743VIT6. | Package placement and native design implementation are open. | Native schematic inspection. |
| MCU-002 | The IO MCU shall be STM32F103C8T6. | Required during operation. Runs px4io firmware: 8 servo outputs, safety switch, servo failsafe (DEC-015, DEC-016). | Native schematic and responsibility review. |
| IF-001  | The H743↔F103 interface shall be USART with the px4io protocol. | H743 USART6 ↔ F103 USART2, 1.5 Mb/s, 3.3 V (DEC-015). The F103 uses this link to detect that the H743 has stopped. Software owns the protocol. | Allocation review and hardware test. |
| SEN-001 | The design shall provide 2 × SPI IMU interfaces. | Part: 2 × ICM-45686 (DEC-008). Resource allocation TBD. | Schematic inspection and hardware test. |
| SEN-002 | The design shall provide 2 × I2C barometer interfaces. | Parts: ICP-20100 at 0x63 and BMP581 at 0x46, both on I2C2 (DEC-010, DEC-018). Fallback for the BMP581: BMP384 (OPEN-019). | Schematic inspection and hardware test. |
| SEN-003 | The design shall provide 1 × I2C magnetometer interface. | Part: iSentek IST8310 (DEC-011, replaced BMM150 on 2026-10-24). Reduced from 2 by DEC-011. | Architecture and hardware test. |
| PWR-001 | The flight-controller board shall receive 5 V from the power module. | Limits: see PWR-010. | Power-tree inspection and measurement. |
| PWR-002 | The servo supply shall be 6 V. | Limits: see PWR-011. | Power-tree inspection and measurement. |
| SAF-001 | If the H743 stops, the F103 shall set the 8 servo outputs to fixed failsafe values, and the motors shall stop. No landing is commanded. | Stock px4io acts after 0.5 s without H743 data (PX4 v1.16.2 `px4iofirmware/mixer.cpp`). Failsafe values are PX4 parameters, set after flight tests (decisions file D3). The motors stop because their DShot frames stop (SAF-015). Changed from "immediate landing" by DEC-016. | Fault-injection test. |

## 3. System Requirements

### 3.1 Functional requirements

| ID      | Required behavior | Condition | Verification |
| ------- |---|---|---|
| FUN-001 | H743 shall provide the primary flight-controller processing and primary system interface resources. | Normal operation | Schematic/resource inspection; later bring-up |
| FUN-002 | H743 shall drive the 4 ESC outputs on one timer with DMA (TIM5), DShot only with no PWM fallback, with bidirectional DShot (RPM feedback). | Normal operation. Changed from F103 ESC outputs by DEC-016. | Resource inspection; DShot bench test |
| FUN-003 | F103 shall drive the 8 servo outputs (IF-030 to IF-037) at 50 Hz PWM, and the safety switch, safety LED and servo rail sense (IF-049, IF-050). | Normal operation. FlySky input removed (DEC-018). | MCU resource review; hardware test |
| FUN-004 | F103 shall hold the servo outputs at their failsafe values when H743 data stops (see SAF-001). | H743 unavailable | Fault-injection test; timing measurement |
| FUN-005 | H743 and F103 shall provide SWD debug/recovery access. | Development, service, bring-up | Probe connection; debug test |
| FUN-006 | H743 shall retain selectable BOOT0 access. | Development, recovery | Inspection; boot-state test |

### 3.2 Operating scenarios and modes

Exit, transition, recovery, and restart behavior is `TBD` for all rows.

| Scenario / mode   | Entry | Required behavior |
| ----------------- |---|---|
| Normal            | Valid power and normal MCU operation | H743 performs primary functions and drives the motors. F103 drives the servos and the safety switch. |
| H743 unavailable  | No H743 data at the F103 for 0.5 s | F103 holds the servos at their failsafe values. Motors stop when their DShot frames stop (SAF-015). ESC stop time is `NOT_VERIFIED` (OPEN-017). |
| H743↔F103 link    | Normal operation | USART with the px4io protocol, 1.5 Mb/s (DEC-015). Software owns the protocol. |
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

Allocations are `CONFIRMED` at the logical and peripheral level (DEC-014, DEC-018). Pins are in the pin allocation record and pinmap review 0.3 (REF-07), not repeated here. For every row, electrical levels, protection and connector pinout are `TBD` and `NOT_VERIFIED` unless noted. Removed rows keep their ID (2.1).

| ID     | Connector | Function | Resource | Note |
| ------ |---|---|---|---|
| IF-010 | Conn1 / Tel1 | Telemetry 1 and RC | UART7 | ELRS receiver in MAVLink mode, 460800 baud, 3.3 V. Carries RC and telemetry; no backup RC input (DEC-018). |
| IF-011 | Conn2 / Tel2 | Telemetry 2 | USART1 | Free; a second receiver can be added here later. |
| IF-012 | Conn3 / GPS1 + compass | GPS (UBX) and compass | USART2 + I2C1 | Single GPS (DEC-018). Compass address and pull-ups TBD. |
| IF-013 | Conn4 / GPS2 | Removed | - | GPS2 dropped; USART3 is the debug console (IF-045). DEC-018. |
| IF-014 | Conn5 / MS4525DO | Air-data sensor | I2C4, address `0x28` | Shares I2C4 with the power module (IF-048). Pull-ups TBD. |
| IF-015 | Conn6 / TF-Luna | Rangefinder | UART8 | |
| IF-016 | Conn7 / UART7 TX | Removed | - | Dropped by the team (DEC-018). |
| IF-017 | Spare output 1 | Spare PWM output | TIM4_CH3 | Output. Was VT L. No use planned for Model G (DEC-018). |
| IF-018 | Spare output 2 | Spare PWM output | TIM4_CH4 | Output. Was VT R. As IF-017. |
| IF-019 | Spare output 3 | Spare PWM output | TIM1_CH1 | Output. Was SP2. As IF-017. |
| IF-020 | Conn11 / TL2 | Removed | - | TIM15 dropped; its pins carry motors 3 and 4 (IF-042, IF-043). DEC-016. |
| IF-021 | Conn12 / TR2 | Removed | - | As IF-020. |
| IF-022 | USB FS | Service, firmware update, QGC | USB FS | Device only; OTG_FS_ID not used. VBUS sense on OTG_FS_VBUS. ESD/protection, connector and routing TBD. |
| IF-023 | SWD | Debug and recovery | SWD | H743: on the debug connector (IF-045). F103: IF-051. |
| IF-024 | H743↔F103 | MCU link | H743 USART6 ↔ F103 USART2 | px4io protocol, 1.5 Mb/s, 3.3 V (DEC-015). Protection and test access TBD. |
| IF-040 | ESC 1 (front-R) | Motor 1 | TIM5_CH1 | DShot only, bidirectional (FUN-002, DEC-016). Weak pull-down (OPEN-018). |
| IF-041 | ESC 2 (rear-L) | Motor 2 | TIM5_CH2 | As IF-040. |
| IF-042 | ESC 3 (front-L) | Motor 3 | TIM5_CH3 | As IF-040. |
| IF-043 | ESC 4 (rear-R) | Motor 4 | TIM5_CH4 | As IF-040. |
| IF-044 | microSD | Flight logs | SDMMC1, 4-bit | No card-detect pin. |
| IF-045 | H743 debug | Console and SWD | USART3 + SWD | One 6-pin JST-SH in the Pixhawk Debug Mini layout (1 VREF, 2 Console TX, 3 Console RX, 4 SWDIO, 5 SWCLK, 6 GND; PX4 docs, DS-009 not read). Reachable after assembly. NRST on a pad next to it (TST-001). |
| IF-046 | Buzzer | Passive buzzer, PX4 tone alarm | TIM3_CH3 | Same timer and pin as `px4/fmu-v6c`. HRT on TIM8 (no pin). |
| IF-047 | Board LEDs | Red, blue, green, active low | 3 × GPIO | |
| IF-048 | Power module | Battery voltage and current over I2C | I2C4 | Holybro PM02D with TI INA228 at 0x45 (team; older units INA226 at 0x41). Module label not checked. PC0/PC1 reserved as ADC inputs for an analog module. |

### 3.5 F103 servo outputs and I/O

`CONFIRMED` by the team (DEC-014, DEC-018). The timer channels are the px4io-v2 outputs (PX4 v1.16.2 `boards/px4/io-v2/src/timer_config.cpp`), default mapping, no AFIO remap. IF-030 to IF-037 are servo PWM at 50 Hz. Output names changed from TILT, ESC, COAX and AIL in rev 0.11. Electrical output is `TBD`.

| ID     | Logical output | Allocation |
| ------ |---|---|
| IF-030 | Flaperon L | TIM2_CH1 |
| IF-031 | Flaperon R | TIM2_CH2 |
| IF-032 | Ruddervator L | TIM4_CH3 |
| IF-033 | Ruddervator R | TIM4_CH4 |
| IF-034 | Tilt servo 1 (front-R) | TIM3_CH1 |
| IF-035 | Tilt servo 2 (rear-L) | TIM3_CH2 |
| IF-036 | Tilt servo 3 (front-L) | TIM3_CH3 |
| IF-037 | Tilt servo 4 (rear-R) | TIM3_CH4 |
| IF-038 | Removed | FlySky input dropped; RC comes over ELRS on IF-010 (DEC-018) |
| IF-049 | Safety switch and LED | Button GPIO in, LED GPIO out open drain active low (px4io-v2 pins) |
| IF-050 | Servo rail sense | ADC1_IN4, 3:1 divider (px4io-v2) |
| IF-051 | F103 debug | SWD and px4io console (USART1 TX) on pads or a header, bench use only |

Other F103 pins that stock px4io-v2 drives or reads (LEDs, RSSI, Spektrum, SBUS, PPM, servo fault, board sense) are reserved for that function and not used for anything else (pin allocation record F-13).

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
| SAF-010 | H743 unavailable | See SAF-001. After 0.5 s without H743 data, the F103 holds the servos at their failsafe values. The H743 owns the 4 motor outputs; the F103 owns the 8 servo outputs (DEC-016). | Reset, recovery and F103-failure behavior are Software-owned. The F103 starts its own IWDG (px4io, team answer S1). | Fault-injection test; NOT_VERIFIED |
| SAF-011 | H743↔F103 USART loss | Same response as SAF-010; the F103 cannot tell a link loss from an H743 stop (`ASSUMED`). | As SAF-010. | Fault-injection test; NOT_VERIFIED |
| SAF-012 | 5 V input abnormality | Safe reset/output state TBD. | Power recovery procedure TBD. | Measurement and fault test; NOT_VERIFIED |
| SAF-013 | 6 V servo rail fault | Protection and safe actuator state TBD. | TBD | Measurement and fault test; NOT_VERIFIED |
| SAF-014 | ESD, reverse polarity, overvoltage, short circuit | Protection requirements TBD. | Service/recovery method TBD. | Analysis / test; NOT_VERIFIED |
| SAF-015 | H743 hang with motors running | Motors stop. The motors run DShot only with no PWM fallback; PX4 starts each DShot frame from software, so a hang stops the frames and the ESC sees signal loss (team answer S1). PX4 v1.16.2 does not start the H743 IWDG (team answer S1, not checked by hardware). Depends on the ESC's signal-loss behavior (OPEN-017). | H743 reset or power cycle. | Bench test: halt the H743 over SWD while armed; NOT_VERIFIED |

## 4. Hardware Architecture and Design Constraints

### 4.1 Functional block diagram

The user-provided diagrams show an H743 main MCU, an F103 auxiliary MCU, sensor/interface blocks, USB/SWD, PWM/actuator paths, and a separate power architecture. The images are reference inputs only. Native schematic and PCB files remain the design authority.

### 4.2 Functional blocks

| Block                     | Role | Inputs / outputs | Dependencies | Key constraints |
| ------------------------- |---|---|---|---|
| H743 main controller      | Primary flight-controller processing and interface host | Sensors, external interfaces, USB, SWD, USART, outputs | 5 V input and defined rails | Pins/resources NOT_VERIFIED. |
| F103 IO controller        | px4io: servo PWM, safety switch, servo failsafe | USART link, 8 PWM outputs, safety switch and LED, servo rail sense | H743 data; defined power/reset; 8 MHz crystal (DEC-017) | Electrical implementation NOT_VERIFIED. |
| IMU subsystem             | Two SPI IMU interfaces | SPI, CS, DRDY; reset by software (DEC-009) | Selected sensor parts and rail | 2 × ICM-45686 (DEC-008). Rail TBD. |
| Barometer subsystem       | Two I2C barometer interfaces | I2C, address, pull-ups | Selected sensor parts and rail | ICP-20100 + BMP581 (DEC-010), both on I2C2 with the IST8310. |
| Magnetometer subsystem    | One I2C magnetometer interface | I2C, address, placement | Selected sensor part | IST8310 (DEC-011). Placement TBD. |
| H743 external I/O         | Telemetry/RC, GPS, compass, air-data, rangefinder, power module, 4 motor outputs, 3 spare outputs, microSD, buzzer, LEDs | UART/I2C/timer/SDMMC interfaces | H743 resource allocation | Electrical implementation NOT_VERIFIED. |
| USB/SWD/BOOT0             | Service, debug, recovery | USB FS, debug connector (IF-045), F103 SWD pads (IF-051), BOOT0 | H743/F103 reset and power | Protection and circuit NOT_VERIFIED. |
| Power subsystem           | 5 V board input and 6 V servo supply | Rails, returns, protection | Power module and distribution | Tolerances, current, and protection TBD. |

### 4.3 Power architecture

- Board input and servo supply limits: see PWR-010 and PWR-011.
- The diagram-derived arrangement is a candidate only: 6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 5 V, 3.3 V, 3.3 V_IMU, 6 V UBEC.
- Main 3.3 V rail: TPS62142RGTR buck from the 5 V board input (DEC-012).
- TBD: rail dependencies, current budgets, load steps, sequencing, brownout, reverse-polarity protection, overvoltage protection, transient handling, grounding, filtering, thermal limits.

**Schematic state (`power_supplies.kicad_sch`, saved file, re-checked 2026-10-19 after commit f1ead00).** This records what is drawn. It is not a reviewed or approved design. All 17 parts are unannotated. No `PWR_FLAG` is placed. ERC not run.

| Block | As drawn | Evidence |
| ----- |---|---|
| Power module input | 6-pin JST GH connector (`SM06B-GHS-TB`): pins 1-2 `+VIN`, pin 3 `PM02_SCL`, pin 4 `PM02_SDA`, pins 5-6 and MP `GND`. `PM02_SCL` and `PM02_SDA` reach only the connector. | Local net check |
| `+VIN` ESD | DF2S6.2CT (SOD-882), marked DNP, from `+VIN` to `GND`. No MPN or LCSC field. Not a recorded decision. | Local net check |
| `+VIN` to `+5V` | No part connects `+VIN` to `+5V`. No other sheet has components, so `+5V` has no source yet (OPEN-012). | Local net check; project summary |
| Main 3.3 V buck | TPS62142RGTR: VIN and EN to `+5V`; SW to 2.2 µH (Abracon AOTA-B252010S) to `+3V3`; VOS to `+3V3`; FB, DEF, FSW (2.5 MHz) and PG to `GND`; SS/TR 3.3 nF. Input 3 × 10 µF on `+5V`, output 3 × 10 µF on `+3V3`. The pin ties follow TI's rules for the fixed version. No 0.1 µF capacitor from AVIN (pin 10) to AGND is drawn; TI recommends one close to the IC. | Local net check; TI SLVSAJ0F Rev. F (HTML, and Table 6-1 and 9.2.2.2.2.2 via NotebookLM) |
| `+3V3A` LDO | TPS73533DRBR: IN and EN to `+5V`, OUT to `+3V3A`, NR/FB (pin 3) 100 nF X7R, 2 × 1 µF on `+3V3A`. Placed in the schematic, not a recorded decision (OPEN-011). TI asks for an NR capacitor of no more than 0.01 µF (10 nF typical, low leakage, C0G) and at least 2 µF output capacitance. Start-up time is characterized only up to CNR = 47 nF. | Local net check; TI SBVS087M (HTML, and pin table and Electrical Characteristics via NotebookLM) |
| 3.3 V indicator | LED LTSL-C191TGKT with 1 kΩ from `+3V3`. Not driven by PG. | Local net check |

The root, `top_hierarchical`, `block_diagram` and `revision_history` sheets hold no parts. The saved PCB has no footprints and no board outline.

### 4.4 Clock, reset, boot and programming

- H743 shall retain selectable BOOT0 access (FUN-006).
- H743 and F103 shall provide SWD access (FUN-005).
- USB FS shall be physically available on H743 for later Software-owned flashing/QGC integration.
- H743 clock: 16 MHz HSE crystal, as `px4/fmu-v6c` (DEC-017). No LSE.
- F103 clock: 8 MHz HSE crystal, PLL ×3 to 24 MHz SYSCLK (DEC-017). Stock px4io-v2 uses a 24 MHz HSE directly, which is outside the F103 crystal range (4 to 16 MHz, DS5319 Rev 20 Table 22), so the software team builds px4io and its bootloader for 8 MHz. No LSE; PC14 and PC15 unconnected (px4io reads them at boot).
- F103 boot: BOOT0 and BOOT1 (PB2) pulled down. The software team flashes the px4io bootloader over SWD once; after that PX4 updates the F103 over the USART link. No BOOT0/NRST control from the H743.
- H743 first flash: PX4 bootloader over SWD (software team, ST-LINK); updates over USB.
- Boot-time outputs: every PWM line low before firmware starts, with a weak pull-down and no pull-up (team, pinmap review Q10). Value TBD (OPEN-018).
- Watchdogs: px4io starts the F103 IWDG; PX4 v1.16.2 does not start the H743 IWDG (team answer S1).
- TBD: crystal parts and load capacitors, reset topology, power-on reset, service procedures.

### 4.5 Control, sensing, analog and digital considerations

All items are `TBD` and `NOT_VERIFIED`.

- SPI/I2C: bus ownership, chip-select, data-ready/interrupt, pull-up, address, DMA, timing, recovery.
- PWM: output voltage, drive method, current capability, actuator connector pinout. Motor lines carry bidirectional DShot, so the line also carries the ESC reply; the pull-down value and any series resistor must not upset that (OPEN-018).
- USART: protection and test access. Rate (1.5 Mb/s) and protocol (px4io) are set by DEC-015.
- Signal integrity, return paths, sensor noise, magnetic placement, EMI/EMC constraints.

### 4.6 Component selection constraints

| ID      | Category | Mandatory constraints | Preferred constraints | Sourcing / lifecycle |
| ------- |---|---|---|---|
| CMP-001 | Main MCU | Must be STM32H743VIT6. | TBD | Availability, package, lifecycle, approved source TBD |
| CMP-002 | IO MCU | Must be STM32F103C8T6. The software team proposed an STM32F100C8T6B (the chip px4io-v2 is built for); the hardware owner kept the F103 (DEC-002, DEC-017). | TBD | Availability, package, lifecycle, approved source TBD |
| CMP-003 | IMU | Two SPI positions required. Must be TDK InvenSense ICM-45686 (DEC-008). | TBD | TDK: Production (product page, 2026-10-19). PX4 driver present. SPI support, supply range, availability and approved source NOT_VERIFIED |
| CMP-004 | Barometer | Two I2C positions required. Position 1 must be TDK ICP-20100 (DEC-010). Position 2 must be Bosch BMP581 (DEC-010), PX4 driver `barometer/bmp581`; fallback Bosch BMP384 (PX4 `bmp388` driver) if the BMP581 cannot be bought (OPEN-019). | TBD | ICP-20100 is EOL (TDK page). TDK SmartPressure page: "Pressure products are EOL and not recommended for new designs" (2026-10-19). BMP390 removed on 2026-10-21 because LCSC C5124834 is not available. BMP581: DigiKey 0 in stock on 2026-10-08, 10,000 due 2026-11-19 (team answer D7, NOT_VERIFIED). Approved source TBD |
| CMP-005 | Magnetometer | One I2C position required. Must be iSentek IST8310 (DEC-011). AVDD and DVDD 1.72 to 3.6 V; absolute maximum also 3.6 V. LGA-16, 3.0 × 3.0 × 1.0 mm. I2C up to 400 kHz, address 0x0C to 0x0F (CAD1/CAD0). (IST8310 Datasheet V1.2, via NotebookLM.) | TBD | PX4 driver `magnetometer/isentek/ist8310` present. Lifecycle not stated in the datasheet; the iSentek web site did not render (NOT_VERIFIED). Approved source TBD |
| CMP-006 | Regulator, protection, connector, PDB/UBEC, interface parts | Electrical requirements shall be satisfied. | Specific parts TBD. | MFR/MPN, availability, lifecycle, approved source TBD |
| CMP-007 | Main 3.3 V regulator | Must be TI TPS62142RGTR (DEC-012). Fixed 3.3 V, VIN 3 to 17 V, 2 A, VQFN-16 3 × 3 mm (TI SLVSAJ0F Rev. F, HTML). | 2.5 MHz (FSW low) as drawn | TI: ACTIVE (2026-10-19; the page also points to a newer TPS62902). LCSC C129331: 632 in stock (snapshot 2026-10-18). Approved source TBD |

**Library state (project library, saved files, 2026-10-21).** Symbol and footprint starting points for the decided sensors, including the BMP581 (barometer 2 since rev 0.11). They are drawn, not decided, and no sensor symbol is placed on a sheet yet. A read-only link audit found no broken links, and the symbol pin numbers match the footprint pad numbers 1:1. Each symbol's pin map was checked against the datasheet pin table through NotebookLM, with the table text confirmed in the source fulltext. Pin 1 corner, pad positions and land patterns are shown only in datasheet drawings (images), so they stay `NOT_VERIFIED` (OPEN-013).

| Part | Symbol | Footprint | Pin map vs datasheet | Still open |
| ---- |---|---|---|---|
| ICM-45686 | `0_Sensor_Motion:ICM-45686` | `0_Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm` (stock Bosch copy, KiCad stock model) | Matches DS-000489 Rev 1.1 Table 10 (pins 1 to 14). Pad count, 0.5 mm pitch, 2.5 × 3 mm body and pad-row spans (D1 1.5, E1 1.0) match section 10.2. | Land pattern against TDK AN-000393 (not in the notebook); pin 1 corner |
| ICP-20100 | `0_Sensor_Pressure:ICP-20100` | `0_Package_LGA:ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y` (stock ST copy, KiCad stock model) | Matches DS-000416 Rev 1.3 Table 18 (pins 1 to 10). The datasheet is marked preliminary. INT is open-drain; RESV pins 8 and 9: "Connect to Ground". | No land pattern in the datasheet (it refers to AN-000140). Pads are 0.35 mm wide; terminal width b is 0.25 nom, 0.30 max (Table 19). Pin 1 corner |
| BMP390 (not used) | `0_Sensor_Pressure:BMP390` | `0_Package_LGA:Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y` (pads set to the BMP581 land pattern on 2026-10-21, see the BMP581 row; local model, source not recorded) | Matches BST-BMP390-DS002-07 Rev 1.7 Table 52 (pins 1 to 10). | Removed from DEC-010 on 2026-10-21; library files kept until the human decides to remove them. The footprint now follows the BMP581 land pattern; not checked against the BMP390 drawing (7.2). Pin 1 corner; 3D model rotation |
| BMP581 (barometer 2, DEC-010) | `0_Sensor_Pressure:BMP581` | `0_Package_LGA:Bosch_LGA-10_2x2mm_P0.5mm_LayoutBorder3x2y` (shared with BMP390; pads 0.325 × 0.30 mm on ±0.7625 mm centers, smallest gap 0.20 mm) | Matches BST-BMP581-DS004-13 Rev 1.13 Table 28 (pins 1 to 10), the same pin map as BMP390. 10 pins, body 2.0 × 2.0 × 0.75 mm (Table 3). | Pad sizes, pad centers, pin 1 corner and numbering were read by NotebookLM from Fig. 29 to 32 with no citation (`NOT_VERIFIED`). §8.2: no solder mask, vias or traces under the part, 20 µm mask clearance; the footprint uses the board default mask. |
| BMM150 (not used) | `0_Sensor_Magnetic:BMM150` | `0_Package_CSP:WLCSP-12_1.56x1.56mm_P0.4mm` (stock copy) | Matches BST-BMM150-DS001-05 Rev 1.4 Table 32 (12 balls). Body 1.56 mm and 0.283 mm grid (0.4 mm diagonal) match. | Replaced by IST8310 in DEC-011 on 2026-10-24. Library files kept until the human decides to remove them |
| IST8310 | `0_Sensor_Magnetic:IST8310` (stock KiCad copy, with MFR, MPN and LCSC C2683055 fields) | `0_Package_LGA:LGA-16_3x3mm_P0.5mm` (stock) | Not recorded here | Added after the 2026-10-21 check (CHANGELOG); not re-read for this table. The datasheet (V1.2 and V1.8) has no land pattern, so the footprint fit is `ESTIMATED` from the package drawing. Pin 1 corner |

### 4.7 Engineering calculations and margins

| Analysis               | Inputs / operating corner | Method / reference | Result | Margin / open questions |
| ---------------------- |---|---|---|---|
| Board input current    | 5 V input, MCU/sensor/I/O load | TBD | NOT_VERIFIED | Current budget and duty cycle TBD |
| Servo rail current     | 6 V rail and actuator load | TBD | NOT_VERIFIED | Servo count, peak current, and protection TBD |
| Power rail tolerance   | All MCU/sensor rails | TBD | NOT_VERIFIED | Nominal, min, max, and load-step limits TBD |
| Thermal margin         | MCU, regulator, protection, output drivers | TBD | NOT_VERIFIED | Ambient, dissipation, copper, and cooling TBD |
| Safety response timing | H743 stop to servo failsafe; H743 hang to motor stop | px4io `FMU_INPUT_DROP_LIMIT_US` = 500000 (PX4 v1.16.2 `px4iofirmware/mixer.cpp`) | Servos: 0.5 s by firmware design (VERIFIED in source, not measured). Motors: NOT_VERIFIED | Motor stop time depends on the ESC signal-loss timeout (OPEN-017). Test: halt the H743 over SWD |

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
| TST-001 | H743 SWD and console | Pixhawk Debug Mini connector (IF-045), reachable on the assembled drone, plus an NRST pad next to it | Inspection; debug test |
| TST-002 | F103 SWD and console | Pads or header: SWDIO, SWCLK, NRST, GND, USART1 TX. Bench use only (IF-051) | Inspection; debug test |
| TST-003 | H743 BOOT0 | Selectable and observable boot state | Inspection; boot-state test |
| TST-004 | 5 V board input | Test point; current/voltage measurement access | Inspection; measurement |
| TST-005 | 6 V servo rail | Test point; current/voltage measurement access | Inspection; measurement |
| TST-006 | H743↔F103 USART | Physical test access; signal observation | Inspection; hardware test |
| TST-007 | F103 safety path and motor stop | Fault-injection access for the H743-unavailable condition (halt the H743 over the IF-045 SWD) | Fault-injection test (SAF-001, SAF-015) |

## 7. Verification Plan (Planning Only)

No automatic gates. This table plans how requirements could be checked. It does not declare phase completion, design approval, or release readiness.
| Requirement ID | Method | Planned evidence | Result | Reviewer |
| ------------------------- |---|---|---|---|
| MCU-001, MCU-002          | Inspection | Native schematic/package review | NOT_VERIFIED | Human, TBD |
| IF-001                    | Inspection / Test | USART allocation review; physical link test | NOT_VERIFIED | Human, TBD |
| SEN-001, SEN-002, SEN-003 | Inspection / Test | Bus allocation review; sensor electrical access test | NOT_VERIFIED | Human, TBD |
| PWR-001, PWR-002          | Analysis / Test | Power-tree review; rail measurement; load/current test | NOT_VERIFIED | Human, TBD |
| SAF-001, SAF-015          | Test | Halt the H743 while armed: servo failsafe time at the F103, motor stop time at the ESC | NOT_VERIFIED | Human, TBD |
| IF-010 to IF-024, IF-040 to IF-048 | Inspection / Test | Connector, pin, electrical-level, protection, and interface test; DShot and bidirectional DShot bench test | NOT_VERIFIED | Human, TBD |
| IF-030 to IF-037, IF-049 to IF-051 | Inspection / Test | Timer/resource review; servo PWM and I/O electrical test | NOT_VERIFIED | Human, TBD |
| PCB-010 to PCB-015        | Review / Analysis / Test | Layout, return path, DRC, signal, power, and hardware review | NOT_VERIFIED | Human, TBD |
| TST-001 to TST-007        | Inspection / Test | Test-point and debug-access inspection, then bring-up tests | NOT_VERIFIED | Human, TBD |

## 8. Design Decisions and Open Items

### 8.1 Decisions

All decisions are by the human owner, unless the Notes say otherwise.

| ID      | Topic | Selected option | Notes | Date |
| ------- |---|---|---|---|
| DEC-001 | Main MCU part number | STM32H743VIT6 | Implementation not verified. | 2026-10-12 |
| DEC-002 | Auxiliary (IO) MCU part number | STM32F103C8T6 | Implementation not verified. Kept by the human owner on 2026-10-24 over the software team's STM32F100C8T6B proposal (decisions file S7). | 2026-10-12, reconfirmed 2026-10-24 |
| DEC-003 | H743↔F103 physical interface protocol | USART | Instance, rate and protocol set by DEC-015. | 2026-10-12 |
| DEC-004 | Firmware implementation boundary | Deferred and non-blocking for the current hardware path | Software team decides firmware details later. | 2026-10-12 |
| DEC-005 | H743 availability monitoring path | USART | See SAF-001. | 2026-10-13 |
| DEC-006 | Maximum PCB dimensions | Limit in MEC-001 | See MEC-001. | 2026-10-13 |
| DEC-007 | Power input and servo rail limits | Limits in PWR-010 and PWR-011 | Budgets and component selection are open (OPEN-006, OPEN-007, OPEN-010). | 2026-10-13 |
| DEC-008 | IMU part number (SEN-001, CMP-003) | 2 × TDK InvenSense ICM-45686 | Confirmed by the team. Implementation not verified. SPI, supply range and sourcing open; see `AO-HORIZON_IMU_SELECTION_EN.md`. | 2026-10-18 |
| DEC-009 | IMU reset method | Software reset only (ICM-45686 `SOFT_RST`); no hardware reset line | ICM-45686 has no reset pin (DS-000489 Rev 1.1 Table 10, checked through NotebookLM on 2026-10-19). No hardware power control of the IMU rail is planned. | 2026-10-18 |
| DEC-010 | Barometer part numbers (SEN-002, CMP-004) | 1 × TDK ICP-20100 (0x63) + 1 × Bosch BMP581 (0x46), both on I2C2; fallback BMP384 | Confirmed by the team on 2026-10-18 as ICP-20100 + Bosch BMP390. The human owner removed BMP390 on 2026-10-21 because LCSC C5124834 is not available. The team accepted BMP581 with BMP384 as fallback on 2026-10-24 (decisions file D7); closes OPEN-014. ICP-20100 is EOL per TDK. See `AO-HORIZON_BARO_MAG_SELECTION_EN.md`. | 2026-10-18, revised 2026-10-21 and 2026-10-24 |
| DEC-011 | Magnetometer count and part number (SEN-003, CMP-005) | 1 × iSentek IST8310 | Confirmed by the team as 1 × Bosch BMM150 on 2026-10-18. Reduces SEN-003 from 2 to 1 magnetometer and closes OPEN-005. The human owner changed the part to IST8310 on 2026-10-24. The team accepted IST8310 at 0x0E, with DRDY and RSTN not connected, in pinmap review 0.2 (Q11, 2026-10-24). Lifecycle NOT_VERIFIED. See `AO-HORIZON_BARO_MAG_SELECTION_EN.md`. | 2026-10-18, revised 2026-10-24 |
| DEC-012 | Main 3.3 V supply (CMP-007) | TI TPS62142RGTR buck, 5 V to 3.3 V (LCSC C129331) | Selected by the human owner. Datasheet fit checked against TI HTML (SLVSAJ0F Rev. F). 3.3 V load current, inductor and output-capacitor derating NOT_VERIFIED. | 2026-10-18 |
| DEC-013 | Reference designs (SYS-002, REF-01, REF-05) | Pixhawk 6C and Pixhawk 6X Rev 8, conceptual and functional references | Human owner: "6X and 6C are ref." This does not authorize copying their schematic or PCB. The pinout question is decided in DEC-014. | 2026-10-24 |

DEC-014 to DEC-018 come from the software team's answers in the decisions file (REF-06), accepted by the human owner on 2026-10-24. D1 to D7 are signed "Software team (proposal for the team)"; a separate whole-team confirmation is not recorded.

| ID      | Topic | Selected option | Notes | Date |
| ------- |---|---|---|---|
| DEC-014 | Pin allocation basis and PX4 port (SYS-002, OPEN-001) | H743 pins mostly from Pixhawk 6C (`px4/fmu-v6c`), F103 pins from `px4/io-v2`. Port based on `px4/fmu-v6c`, PX4 v1.16.2 | Decisions file section 3, pinmap review Q1 and Q18. Pins tested by the team on a NUCLEO-H753ZI only. Schematic and PCB not copied. | 2026-10-24 |
| DEC-015 | H743↔F103 link (IF-001, IF-024, OPEN-002) | px4io protocol, H743 USART6 ↔ F103 USART2, 1.5 Mb/s | px4io-v2 uses USART2 at 1500000 b/s for the FMU link (PX4 v1.16.2 `io-v2/src/board_config.h`). The F103 runs px4io built for the 8 MHz crystal (DEC-017). | 2026-10-24 |
| DEC-016 | Output split and H743-failure behavior (SAF-001, FUN-002, FUN-004, SAF-010, SAF-011, OPEN-008) | H743 TIM5 drives the 4 motors, DShot only, bidirectional, TIM5 as timer 0 with DMA. F103 drives the 8 servos. After 0.5 s without H743 data the F103 holds the servos at failsafe values (PX4 disarmed values `PWM_MAIN_DISn` by default). No landing | Decisions file D1, D2, D3, S1, S2, S3. Needs DShot-capable ESCs; planned Holybro Tekko32 F4 4-in-1 with AM32, not confirmed. Motor stop on a hang: OPEN-017. | 2026-10-24 |
| DEC-017 | Clocks and IO MCU firmware build (OPEN-015) | H743: 16 MHz crystal. F103: 8 MHz crystal, PLL ×3 to 24 MHz, with px4io and its bootloader rebuilt for 8 MHz by the software team | Decisions file H1 and S7 option (a). The team preferred an STM32F100C8T6B with a 24 MHz crystal; the human owner kept the F103 (DEC-002). | 2026-10-24 |
| DEC-018 | Interface set for Model G (IF-010 to IF-021, IF-038, IF-040 to IF-051) | One GPS; USART3 is the H743 debug console; UART7 TX spare, I2C3 and FlySky dropped; RC and telemetry over one ELRS receiver on UART7; 3 spare outputs kept; microSD on SDMMC1 without card-detect; buzzer TIM3_CH3; 3 LEDs; safety switch on the F103; H743 debug on a Pixhawk Debug Mini connector; F103 debug on pads, bench only | Decisions file section 3, D4, D5, D6, S4, S6, H2. RC over MAVLink is partly tested; the team runs the RC-loss bench test (S5). If it fails, the same receiver can run CRSF on UART7 with no pin change. | 2026-10-24 |

### 8.2 Open questions and assumptions

| ID       | Description | Impact | Owner / next action |
| -------- |---|---|---|
| OPEN-001 | Exact H743/F103 pins and alternate functions. Pinmap review 0.3 (2026-10-24) applies the team's answers; each pin's signal is listed in ST pin data. Not yet drawn in the schematic; DMA streams and interrupt priorities are Software-owned and not checked by hardware (P1-010). | May invalidate the allocation. | Hardware review / P1 |
| OPEN-002 | Closed 2026-10-24 by DEC-015 (instance, pins, rate, protocol). Link protection and test access stay with PCB-015 and TST-006. | Affects safety/control path. | Closed |
| OPEN-003 | Closed 2026-10-24. F103 labels corrected to TIM3_CH1 to CH4 (IF-034 to IF-037); H743 motors on TIM5_CH1 to CH4 with DMA (DEC-016; the team says PX4 maps DMA for TIM5, decisions file S2). | Resolved by reassignment. | Closed |
| OPEN-004 | Sensor electrical properties and sourcing. Sensor parts chosen (DEC-008, DEC-010, DEC-011); datasheet values, ICP-20100 EOL, BMP581 stock and IST8310 lifecycle open. IST8310 has only 0.3 V from a 3.3 V rail to its 3.6 V absolute maximum. | Affects footprint, rail, layout, drivers, verification. | Human owner / P0 |
| OPEN-005 | Second magnetometer allocation. Closed by DEC-011 (single magnetometer). | Affects sensor redundancy and connector/bus architecture. | Closed 2026-10-18 |
| OPEN-006 | 5 V input transient/protection, board current budget, downstream rail budgets | Affects power design and protection. | Hardware review / P0, P2 |
| OPEN-007 | 6 V servo rail pulse duration, protection, distribution, actuator load profile | Affects power and actuator safety. | Hardware review / P0, P2 |
| OPEN-008 | Closed 2026-10-24 by DEC-016: no landing; servo failsafe after 0.5 s; motors on the H743. The servo failsafe values are PX4 parameters that the software team sets after flight tests (decisions file D3). Motor stop: OPEN-017. | Affects F103 behavior, output ownership, test method. | Closed |
| OPEN-009 | Exact board outline under the MEC-001 limit, mounting, connector orientation, environment | Affects PCB and mechanical release. | Human owner / P0, P3 |
| OPEN-010 | All non-MCU part numbers except the sensors (DEC-008, DEC-010, DEC-011) and the main 3.3 V buck (DEC-012) | No other non-MCU part is approved by this document. | Human owner / component selection gate |
| OPEN-011 | `+3V3A` rail: purpose (for example 3.3 V_IMU), load, and LDO part. TPS73533DRBR is drawn but not decided. As drawn, its NR capacitor (100 nF) is above TI's 0.01 µF limit and its output capacitance (2 × 1 µF) is at TI's 2 µF minimum before derating (see 4.3). | Affects sensor supply noise, start-up and the power budget. | Human owner / P0, P2 |
| OPEN-012 | Path from `+VIN` (power module connector) to `+5V`. Nothing connects them in the schematic yet. | Without it, both regulators have no input. | Hardware / P2 |
| OPEN-013 | Sensor library starting points (see 4.6 "Library state"): pin maps match the datasheet tables, but pin 1 corner, pad geometry and land patterns are not checked against the datasheet drawings and app notes. The IST8310 uses the stock KiCad symbol and `LGA-16_3x3mm_P0.5mm` footprint; its datasheet has no land pattern, so the fit is `ESTIMATED`. The Bosch LGA-10 pads follow the BMP581 land pattern (Fig. 32, read from an image) since 2026-10-21. | A wrong land pattern or orientation reaches the PCB. | Human owner / P2 |
| OPEN-014 | Closed 2026-10-24: BMP581 accepted by the team as barometer 2, BMP384 fallback (DEC-010). Fallback fit: OPEN-019. | Affects footprint, I2C address plan, power budget, PX4 driver and sourcing. | Closed |
| OPEN-015 | Closed 2026-10-24 by DEC-017: 8 MHz F103 crystal with PLL ×3, px4io and its bootloader rebuilt for 8 MHz. Background: stock px4io-v2 uses a 24 MHz HSE directly (PX4 v1.16.2 `boards/px4/io-v2/nuttx-config/include/board.h`); the F103 crystal oscillator is specified for 4 to 16 MHz (DS5319 Rev 20 Table 22, NotebookLM source fulltext). | Software team keeps a custom px4io image in the port's `extras/` folder. | Closed |
| OPEN-016 | Closed 2026-10-24: the team answered every row (decisions file section 3); applied in rev 0.11. | - | Closed |
| OPEN-017 | Motor stop on an H743 hang (SAF-015) relies on the ESC stopping when DShot frames stop. ESC not confirmed (Holybro Tekko32 F4 4-in-1 with AM32 planned); its signal-loss behavior and timeout are `NOT_VERIFIED`. No H743 IWDG in PX4 v1.16.2 (team, not checked by hardware). The team's answer covers a full CPU hang, not a partial software stall. | If the ESC holds its last command, a hang leaves the motors running. | Team + Hardware / P4: halt the H743 over SWD while armed on the bench |
| OPEN-018 | PWM pull-down value. Every PWM line gets a weak pull-down (team, Q10). The motor lines carry bidirectional DShot, where the line idles high and the ESC replies on the same wire; the value and any series resistor must not upset that. | Wrong value can break RPM feedback or boot-time output state. | Hardware / P2, then bench test |
| OPEN-019 | BMP384 fallback for barometer 2 (DEC-010). Footprint, pinout and I2C address against the BMP581 not checked. Its address (0x76 or 0x77) does not clash with the I2C2 devices (0x63, 0x0E, 0x46). | A fallback that does not fit the BMP581 footprint needs a board change. | Hardware / P0, before PCB placement |

## 9. Specification Change Notes

| Revision | Date | Description | Approved by |
| -------- |---|---|---|
| 0.1      | 2026-10-12 | Initial advanced hardware specification draft based on confirmed H743/F103 part numbers, confirmed USART protocol, user-provided interface requirements, and diagram-derived references. | TBD |
| 0.2      | 2026-10-13 | Recorded user-confirmed power limits, maximum PCB dimensions, USART safety-monitoring path, and Software ownership of detailed safety behavior. Sensor part selection remains TBD. | Human owner |
| 0.3      | 2026-10-18 | Recorded team-confirmed IMU part: 2 × ICM-45686 (DEC-008). Barometer and magnetometer selection remain TBD. | Team |
| 0.4      | 2026-10-18 | Recorded IMU software reset (DEC-009) and removed the IMU hardware reset signal from the interface table. | Human owner |
| 0.5      | 2026-10-18 | Recorded team-confirmed barometers ICP-20100 + BMP390 (DEC-010) and single magnetometer BMM150 (DEC-011). SEN-003 reduced to 1 magnetometer; OPEN-005 closed. | Team |
| 0.6      | 2026-10-19 | Recorded TPS62142RGTR as the main 3.3 V buck (DEC-012, CMP-007). Added the power-sheet schematic state to 4.3. Added OPEN-011 (`+3V3A` rail) and OPEN-012 (`+VIN` to `+5V` path). | Human owner |
| 0.7      | 2026-10-19 | No new decisions. Re-checked the power-sheet state (4.3) against the saved file and the TPS62142 and TPS735 datasheets: added the DNP `+VIN` ESD diode, the missing TPS62142 AVIN capacitor and the TPS73533DRBR NR and output capacitor notes. Added the sensor library state (4.6), with pin maps checked against the datasheet tables through NotebookLM, and OPEN-013. Recorded sensor and regulator lifecycle checks (CMP-003 to CMP-005, CMP-007). Set the design tool and the checklist revision (REF-04). | Pending human review |
| 0.8      | 2026-10-21 | Removed BMP390 from DEC-010 because LCSC C5124834 is not available. Barometer 2 is open (OPEN-014); BMP581 (LCSC C5362283) is proposed and waits for team confirmation. Updated SEN-002, CMP-004, OPEN-004 and the library state. Added the BMP581 library starting point and set the Bosch LGA-10 footprint pads to the BMP581 land pattern (4.6, OPEN-013). | Human owner |
| 0.9      | 2026-10-24 | Changed the magnetometer in DEC-011 from Bosch BMM150 to iSentek IST8310. Updated SEN-003, the magnetometer subsystem row, CMP-005 (values from IST8310 Datasheet V1.2 via NotebookLM), OPEN-004, OPEN-013 and the library state. | Human owner |
| 0.10     | 2026-10-24 | Added Pixhawk 6X Rev 8 as a second conceptual and functional reference next to Pixhawk 6C (DEC-013, REF-05, SYS-002, 1.1). The no-copied-pinout wording is unchanged; the team decides it (OPEN-016). Recorded the team's pinmap review 0.2 answers on OPEN-001 to OPEN-003, OPEN-008, OPEN-014 and DEC-011, without changing the requirement rows. Added OPEN-015 (F103 24 MHz clock) and OPEN-016 (spec rows the team's answers change). Updated the IST8310 library row and OPEN-013. | Human owner |
| 0.11     | 2026-10-24 | Applied the team's answers from the decisions file (REF-06). Added DEC-014 to DEC-018: pin basis `px4/fmu-v6c` and `px4/io-v2`, px4io link on USART6 ↔ USART2 at 1.5 Mb/s, 4 motors on H743 TIM5 with DShot only and 8 servos on the F103, no landing on H743 failure, 16 MHz H743 and 8 MHz F103 crystals (F103 kept over the F100 proposal), and the Model G interface set. BMP581 accepted as barometer 2 (DEC-010). Rewrote SYS-002, MCU-002, IF-001, SEN-002, SAF-001, FUN-002 to FUN-004, SAF-010, SAF-011, IF-010 to IF-024 and IF-030 to IF-038; added IF-040 to IF-051 and SAF-015. Closed OPEN-002, 003, 008, 014, 015 and 016; added OPEN-017 to OPEN-019. | Human owner (team answers) |

## Current verdict

**Draft only. NOT_VERIFIED and NOT FOR FABRICATION.**

The specification is structured enough for schematic capture against the agreed pinmap (REF-07). It does not approve any non-MCU part number other than the sensors (DEC-008, DEC-010, DEC-011) and the main 3.3 V buck (DEC-012), nor power protection or rail detail, safety timing, schematic, PCB, or fabrication release. Sensor lifecycle and sourcing risks are open (OPEN-004): ICP-20100 is EOL, BMP581 stock is short, and the IST8310 lifecycle is not confirmed. Motor stop on an H743 hang depends on the ESC (OPEN-017). The PWM pull-down value must suit bidirectional DShot (OPEN-018). The sensor library parts are starting points: their pin maps match the datasheet tables, but land patterns and pin 1 orientation are not checked (OPEN-013).
