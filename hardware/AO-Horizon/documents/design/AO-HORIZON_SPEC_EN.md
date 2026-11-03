# Hardware Design Specification: AeroOptix-Horizon

| Property             | Value |
| -------------------- |---|
| Project              | AeroOptix-Horizon |
| Document owner       | Human engineering owner (TBD) |
| Document revision    | 0.24 |
| Last updated         | 2026-11-03 |
| Design tool          | KiCad 10 (saved files written by eeschema 10.0) |
| Hardware phase       | TBD (declared by the human) |
| Related baseline     | FC_H743 rev2 reference from user-provided diagrams; native design baseline not established |
| Specification status | Draft / not for fabrication |

**Conventions**

- `CONFIRMED`: the human owner confirmed the requirement or value.
- `NOT_VERIFIED`: no evidence exists yet. This applies to every requirement in this document unless a row says otherwise.
- `TBD`: to be decided. A value written as `TBD`, or left out, is open.
- A part shown in a diagram is a candidate only. It is not an approved part number.

**Part-number boundary:** Only `STM32H743VIT6`, `STM32F100C8T6B`, `ICM-45686` (2 × IMU, DEC-008), `ICP-20100` (barometer 1, DEC-010), `BMP581` (barometer 2, DEC-010; fallback BMP384), `IST8310` (iSentek magnetometer, DEC-011), `TPS62142RGTR` (main 3.3 V buck, DEC-012), `TPS2121` in the RUX package (5 V power mux, DEC-029; orderable code TPS2121RUXR or TPS2121RUXT not chosen) and `TPS73533DRBR` (`+3V3A` LDO, DEC-027) are confirmed part numbers. The H743↔F100 interface is confirmed as `USART` with the px4io protocol (DEC-015). All other part numbers are `TBD`. This includes regulators, protection devices, power modules, connectors, and interface ICs.

## 1. Project Definition

### 1.1 Purpose and application

A custom PX4 flight controller hardware platform with a dual-MCU architecture. The STM32H743VIT6 is the main flight-controller MCU and drives the 4 motor outputs. The STM32F100C8T6B is the IO MCU: it runs px4io firmware and drives the 8 servo outputs, the safety switch and the servo failsafe (DEC-015, DEC-016).

Pixhawk 6C and Pixhawk 6X are conceptual and functional references. Their schematic and PCB are not copied. The pin allocation follows Pixhawk 6C (`px4/fmu-v6c`) on the H743 and `px4/io-v2` on the F100, by team decision (DEC-014).

### 1.2 Scope

**In scope:**

- H743 main-MCU hardware architecture
- F100 IO MCU hardware: servo PWM, safety switch, servo rail sense and failsafe
- H743↔F100 USART physical interface
- Sensor interfaces: 2 × SPI IMU, 2 × I2C barometer, 1 × I2C magnetometer (DEC-011)
- H743 external interfaces and F100 PWM/expanded-I/O allocation provided by the user
- 5 V flight-controller board input and 6 V servo supply
- USB FS, BOOT0, SWD, reset, protection, testability, PCB, manufacturing, and bring-up requirements
- Verification planning through hardware bring-up

**Out of scope or deferred:**

- PX4 board port (software team: PX4 v1.16.2, based on `px4/fmu-v6c`, DEC-014)
- Bootloader implementation (stock PX4 bootloader and stock px4io-v2 on the F100, DEC-017)
- Firmware image packaging and software flashing implementation
- Detailed USART message protocol and Software-owned behavior
- Final part numbers outside the part-number boundary above: regulators, protection devices, connectors, power module, and PDB/UBEC
- Fabrication release, measured performance, and regulatory approval

### 1.3 Operating scenarios

See section 3.2.

### 1.4 References

| Reference | Source | Revision / date | Purpose |
| --------- |---|---|---|
| REF-01    | Pixhawk 6C reference architecture | Not specified | Conceptual and functional reference only |
| REF-02    | User-provided FC_H743 architecture diagram | 2026-10-12 | Diagram-derived candidate architecture; not native design authority |
| REF-03    | User-provided power architecture diagram | 2026-10-12 | Diagram-derived power candidates; not an approved power specification |
| REF-04    | `AO-HORIZON_EXECUTION_CHECKLIST_EN.md` | 0.23 | Execution and evidence checklist |
| REF-05    | Pixhawk 6X reference architecture | Rev 8 | Conceptual and functional reference only |
| REF-06    | `AO-HORIZON_PINMAP_DECISIONS_EN.md` | 0.2, 2026-10-24 | Team answers behind DEC-014 to DEC-018 |
| REF-07    | `AO-HORIZON_PINMAP_REVIEW_EN.md` | 0.3, answered 2026-10-24 | Pinmap agreed with the software team |
| REF-08    | PX4-Autopilot `boards/px4/fmu-v6c` and `boards/px4/io-v2` | Tag v1.16.2 | Pin and firmware basis for the port (DEC-014) |
| REF-09    | `AO-HORIZON_INTEGRATION_QUESTIONS_EN.md` | 0.4; open questions only (D13, parts, tests). Answers D8 to D11 and S8 to S10 are in rev 0.3 (Git history) | Team answers behind DEC-019 to DEC-022: servo power, mounting, environment, connectors. Open questions: P0-022 |

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
| SYS-002 | Pixhawk 6C (REF-01) and Pixhawk 6X (REF-05) shall be used as conceptual and functional references. | No copied schematic or PCB. The pin allocation follows `px4/fmu-v6c` (H743) and `px4/io-v2` (F100), by team decision (DEC-014). | Architecture review. |
| MCU-001 | The main MCU shall be STM32H743VIT6. | Package placement and native design implementation are open. | Native schematic inspection. |
| MCU-002 | The IO MCU shall be STM32F100C8T6B. | Required during operation. Runs px4io firmware: 8 servo outputs, safety switch, servo failsafe (DEC-015, DEC-016). | Native schematic and responsibility review. |
| IF-001  | The H743↔F100 interface shall be USART with the px4io protocol. | H743 USART6 ↔ F100 USART2, 1.5 Mb/s, 3.3 V (DEC-015). The F100 uses this link to detect that the H743 has stopped. Software owns the protocol. | Allocation review and hardware test. |
| SEN-001 | The design shall provide 2 × SPI IMU interfaces. | Part: 2 × ICM-45686 (DEC-008). Resource allocation TBD. | Schematic inspection and hardware test. |
| SEN-002 | The design shall provide 2 × I2C barometer interfaces. | Parts: ICP-20100 at 0x63 and BMP581 at 0x46, both on I2C2 (DEC-010, DEC-018). Fallback for the BMP581: BMP384 (OPEN-019). | Schematic inspection and hardware test. |
| SEN-003 | The design shall provide 1 × I2C magnetometer interface. | Part: iSentek IST8310 (DEC-011, replaced BMM150 on 2026-10-24). Reduced from 2 by DEC-011. | Architecture and hardware test. |
| PWR-001 | The flight-controller board shall receive 5 V from the power module. | Limits: see PWR-010. | Power-tree inspection and measurement. |
| PWR-002 | The servo supply shall be 6 V. | Limits: see PWR-011. The UBEC plugs into a board-mount XT30; the 8 servo headers share a 6 V bus on the board, Pixhawk style (DEC-019). The board reads the bus (IF-050). | Power-tree inspection and measurement. |
| SAF-001 | If the H743 stops, the F100 shall set the 8 servo outputs to fixed failsafe values, and the motors shall stop. No landing is commanded. | Stock px4io acts after 0.5 s without H743 data (PX4 v1.16.2 `px4iofirmware/mixer.cpp`). Failsafe values are PX4 parameters, set after flight tests (decisions file D3). The motors stop because their DShot frames stop (SAF-015). Changed from "immediate landing" by DEC-016. | Fault-injection test. |

## 3. System Requirements

### 3.1 Functional requirements

| ID      | Required behavior | Condition | Verification |
| ------- |---|---|---|
| FUN-001 | H743 shall provide the primary flight-controller processing and primary system interface resources. | Normal operation | Schematic/resource inspection; later bring-up |
| FUN-002 | H743 shall drive the 4 ESC outputs on one timer with DMA (TIM5), DShot only with no PWM fallback, with bidirectional DShot (RPM feedback). | Normal operation. Changed from F100 ESC outputs by DEC-016. | Resource inspection; DShot bench test |
| FUN-003 | F100 shall drive the 8 servo outputs (IF-030 to IF-037) at 50 Hz PWM, and the safety switch, safety LED and servo rail sense (IF-049, IF-050). | Normal operation. FlySky input removed (DEC-018). | MCU resource review; hardware test |
| FUN-004 | F100 shall hold the servo outputs at their failsafe values when H743 data stops (see SAF-001). | H743 unavailable | Fault-injection test; timing measurement |
| FUN-005 | H743 and F100 shall provide SWD debug/recovery access. | Development, service, bring-up | Probe connection; debug test |
| FUN-006 | H743 shall retain selectable BOOT0 access. | Development, recovery | Inspection; boot-state test |

### 3.2 Operating scenarios and modes

Exit, transition, recovery, and restart behavior is `TBD` for all rows.

| Scenario / mode   | Entry | Required behavior |
| ----------------- |---|---|
| Normal            | Valid power and normal MCU operation | H743 performs primary functions and drives the motors. F100 drives the servos and the safety switch. |
| H743 unavailable  | No H743 data at the F100 for 0.5 s | F100 holds the servos at their failsafe values. Motors stop when their DShot frames stop (SAF-015). ESC stop time is `NOT_VERIFIED` (OPEN-017). |
| H743↔F100 link    | Normal operation | USART with the px4io protocol, 1.5 Mb/s (DEC-015). Software owns the protocol. |
| Boot / service    | BOOT0 or service procedure selects recovery | SWD and USB service access remain available as designed. USB FS on H743 is for later Software-owned flashing/QGC integration. |
| Power input       | Power module connected | Board receives 5 V. Servo supply is 6 V from the UBEC into a board-mount XT30 that feeds the on-board servo bus (DEC-019). Limits are in PWR-010 and PWR-011. |
| USB only          | USB connected, no battery | USB powers the board and all external 5 V ports on the bench (team, REF-09; human owner, IF-022). VBUS current budget TBD (OPEN-006). |
| Power abnormality | Brownout, reset, rail fault, or input loss | Hardware response, sequencing, and safe output state are `TBD`. Verify before release. |

### 3.3 Electrical system requirements

| ID      | Parameter | Min | Nom | Max | Unit | Note |
| ------- |---|---:|---:|---:|---|---|
| PWR-010 | Flight-controller board input | 4.5 | 5 | 5.5 | V | ±10%; source capacity 2 A. Transients and protection TBD. |
| PWR-011 | Servo supply | TBD | 6 | TBD | V | 10 A continuous, 15 A instantaneous, from the user-provided UBEC-10A specification reference. Pulse duration, protection, and distribution TBD. This does not approve a UBEC part. The team's UBEC is a 10 A unit with an XT30 connector (human owner); model TBD. Servo current passes through the board (DEC-019): the XT30 input and the 6 V and GND bus carry the total (OPEN-021). |
| PWR-012 | Board continuous current | TBD | TBD | TBD | A | Separate MCU, sensor, external-I/O, and servo budgets required. |
| PWR-013 | Sensor/MCU rail tolerance | TBD | TBD | TBD | V / % | Diagram rails are candidates, not approved. |
| PWR-014 | Brownout/reset threshold | TBD | TBD | TBD | V | Per MCU and rail. |

### 3.4 External interfaces

Allocations are `CONFIRMED` at the logical and peripheral level (DEC-014, DEC-018). Pins are in the pin allocation record and pinmap review 0.3 (REF-07), not repeated here. For every row, electrical levels, protection and connector pinout are `TBD` and `NOT_VERIFIED` unless noted. Removed rows keep their ID (2.1).

| ID     | Connector | Function | Resource | Note |
| ------ |---|---|---|---|
| IF-010 | Conn1 / Tel1 | Telemetry 1 and RC | UART7 | ELRS receiver in MAVLink mode, 460800 baud, 3.3 V. Carries RC and telemetry; no backup RC input (DEC-018). JST-GH 6-pin, Pixhawk TELEM layout, 5 V supply, TX and RX only (team, REF-09). Receiver model TBD (team). |
| IF-011 | Conn2 / Tel2 | Telemetry 2 | USART1 | Free; a second receiver can be added here later. Connector fitted, as IF-010 (team, REF-09). |
| IF-012 | Conn3 / GPS1 + compass | GPS (UBX) and compass | USART2 + I2C1 | Single GPS (DEC-018). 10-pin full GPS port with the safety switch and LED lines to the F100 (DEC-021). GPS: Holybro M9N (NEO-M9N + IST8310), to be confirmed by the team. Its IST8310 is on I2C1; the board IST8310 is on I2C2, so no address clash. Pull-ups TBD. Pinout and the 3.3 V and buzzer pins: OPEN-023. |
| IF-013 | Conn4 / GPS2 | Removed | - | GPS2 dropped; USART3 is the debug console (IF-045). DEC-018. |
| IF-014 | Conn5 / MS4525DO | Air-data sensor | I2C4, address `0x28` | Shares I2C4 with the power module (IF-048). Pull-ups TBD. JST-GH 4-pin, Pixhawk I2C layout with 5 V supply, if the module has its own regulator. MS4525DO module (team design); 3.3 V or 5 V version TBD (team, REF-09). 5 V pull-ups: OPEN-023. |
| IF-015 | Conn6 / TF-Luna | Rangefinder | UART8 | JST-GH 4-pin (5 V, TX, RX, GND). The team makes an adapter cable from the TF-Luna 6-pin connector (REF-09). |
| IF-016 | Conn7 / UART7 TX | Removed | - | Dropped by the team (DEC-018). |
| IF-017 | Spare output 1 | Spare PWM output | TIM4_CH3 | Output. Was VT L. No use planned for Model G (DEC-018). Pads only, no connector (team, REF-09). |
| IF-018 | Spare output 2 | Spare PWM output | TIM4_CH4 | Output. Was VT R. As IF-017. |
| IF-019 | Spare output 3 | Spare PWM output | TIM1_CH1 | Output. Was SP2. As IF-017. |
| IF-020 | Conn11 / TL2 | Removed | - | TIM15 dropped; its pins carry motors 3 and 4 (IF-042, IF-043). DEC-016. |
| IF-021 | Conn12 / TR2 | Removed | - | As IF-020. |
| IF-022 | USB FS | Service, firmware update, QGC | USB FS | Device only; OTG_FS_ID not used. VBUS sense on OTG_FS_VBUS. USB-C on a board edge, reachable with the canopy open; USB powers the board on the bench without the battery (team, REF-09), including all external 5 V ports (human owner; VBUS current budget: OPEN-006). VBUS and PM02D 5 V must not back-feed each other. ESD/protection and routing TBD. |
| IF-023 | SWD | Debug and recovery | SWD | H743: on the debug connector (IF-045). F100: IF-051. |
| IF-024 | H743↔F100 | MCU link | H743 USART6 ↔ F100 USART2 | px4io protocol, 1.5 Mb/s, 3.3 V (DEC-015). Protection and test access TBD. |
| IF-040 | ESC 1 (front-R) | Motor 1 | TIM5_CH1 | DShot only, bidirectional (FUN-002, DEC-016). Weak pull-down (OPEN-018). ESC: 4 × Hobbywing Skywalker 80A V2, separate ESCs (team design, replaces the Tekko32 F4 4-in-1). Connector: 4 × 3-pin header (signal, +, GND) with the + pin removed, so the ESC BEC 5 V does not reach the board, as in the old design (human owner). DShot support: OPEN-017, REF-09 D13. |
| IF-041 | ESC 2 (rear-L) | Motor 2 | TIM5_CH2 | As IF-040. |
| IF-042 | ESC 3 (front-L) | Motor 3 | TIM5_CH3 | As IF-040. |
| IF-043 | ESC 4 (rear-R) | Motor 4 | TIM5_CH4 | As IF-040. |
| IF-044 | microSD | Flight logs | SDMMC1, 4-bit | No card-detect pin. |
| IF-045 | H743 debug | Console and SWD | USART3 + SWD | One 6-pin JST-SH in the Pixhawk Debug Mini layout (1 VREF, 2 Console TX, 3 Console RX, 4 SWDIO, 5 SWCLK, 6 GND; PX4 docs, DS-009 not read). Reachable after assembly. NRST on a pad next to it (TST-001). |
| IF-046 | Buzzer | Passive buzzer, PX4 tone alarm | TIM3_CH3 | Same timer and pin as `px4/fmu-v6c`. HRT on TIM8 (no pin). Board buzzer stays (DEC-021). Buzzer pin on GPS1: OPEN-023. |
| IF-047 | Board LEDs | Red, blue, green, active low | 3 × GPIO | |
| IF-048 | Power module | Battery voltage and current over I2C | I2C4 | Holybro PM02D with TI INA228 at 0x45 (team; older units INA226 at 0x41). Module label not checked (team to send). PC0/PC1 stay reserved as ADC inputs for an analog module (DEC-023). The board connector shall match the PM02D cable: 6-pin 2.00 mm CLIK-Mate (human owner, 2026-10-24; cable type from the team and PX4 docs, not checked). The power sheet still draws a 6-pin JST-GH (OPEN-023). |
| IF-052 | ESC current sense | Removed | - | Separate ESCs have no current-sense wire, and the old design had none (human owner, 2026-10-24). |
| IF-053 | ESC telemetry | Removed | - | As IF-052. PD0 is free again. |

### 3.5 F100 servo outputs and I/O

`CONFIRMED` by the team (DEC-014, DEC-018). The timer channels are the px4io-v2 outputs (PX4 v1.16.2 `boards/px4/io-v2/src/timer_config.cpp`), default mapping, no AFIO remap. IF-030 to IF-037 are servo PWM at 50 Hz. Output names changed from TILT, ESC, COAX and AIL in rev 0.11. Electrical output is `TBD`. Each servo plugs into a 3-pin header (signal, +6 V, GND). The + pins and GND pins are bussed on the board, Pixhawk style, and the UBEC plugs into a board-mount XT30 (DEC-019). XT30 rating, copper and bulk capacitance: OPEN-021.

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
| IF-049 | Safety switch and LED | Button GPIO in, LED GPIO out open drain active low (px4io-v2 pins). Reached through GPS1 (IF-012). Disabled in PX4 on Model G; no separate switch (DEC-021) |
| IF-050 | Servo rail sense | ADC1_IN4, 3:1 divider (px4io-v2). Reads the on-board 6 V servo bus (DEC-019) |
| IF-051 | F100 debug | SWD and px4io console (USART1 TX) on pads or a header, bench use only |

Other F100 pins that stock px4io-v2 drives or reads (LEDs, RSSI, Spektrum, SBUS, PPM, servo fault, board sense) are reserved for that function and not used for anything else (pin allocation record F-13). The three px4io LEDs (PB14, PB15, PA11) are fitted (pinmap review Q20). PA10 and PB11 stay unconnected with a weak pull-up to 3.3 V (pinmap review 0.3, section 4.3).

### 3.6 Environmental and reliability requirements

| ID      | Parameter / condition | Required range or limit | Verification |
| ------- |---|---|---|
| ENV-001 | Operating temperature | Parts rated −40 to +85 °C (DEC-020). Field ambient about 32 °C near Bangkok (team model); the fuselage inside gets hotter in the sun, not measured | Part ratings in the BOM; temperature in the fuselage NOT_VERIFIED |
| ENV-002 | Storage temperature | Within the −40 to +85 °C part ratings (DEC-020); no separate limit given | BOM review |
| ENV-003 | Vibration and shock | TBD. Soft mount proposed (MEC-002) | Analysis / test TBD |
| ENV-004 | Humidity, ingress, altitude, and maintenance | No rain exposure, no conformal coating, low-altitude flight near sea level (DEC-020). Maintenance: microSD logs read after every flight (MEC-003) | Inspection |

### 3.7 Protection and fault behavior

| ID      | Hazard / fault | Required response | Recovery method | Verification |
| ------- |---|---|---|---|
| SAF-010 | H743 unavailable | See SAF-001. After 0.5 s without H743 data, the F100 holds the servos at their failsafe values. The H743 owns the 4 motor outputs; the F100 owns the 8 servo outputs (DEC-016). | Reset, recovery and F100-failure behavior are Software-owned. The F100 starts its own IWDG (px4io, team answer S1). | Fault-injection test; NOT_VERIFIED |
| SAF-011 | H743↔F100 USART loss | Same response as SAF-010; the F100 cannot tell a link loss from an H743 stop (`ASSUMED`). | As SAF-010. | Fault-injection test; NOT_VERIFIED |
| SAF-012 | 5 V input abnormality | Safe reset/output state TBD. | Power recovery procedure TBD. | Measurement and fault test; NOT_VERIFIED |
| SAF-013 | 6 V servo rail fault | Protection and safe actuator state TBD. The 6 V servo bus is on the board (DEC-019); the F100 reads it (IF-050). | TBD | Measurement and fault test; NOT_VERIFIED |
| SAF-014 | ESD, reverse polarity, overvoltage, short circuit | Protection requirements TBD. | Service/recovery method TBD. | Analysis / test; NOT_VERIFIED |
| SAF-015 | H743 hang with motors running | Motors stop. The motors run DShot only with no PWM fallback; PX4 starts each DShot frame from software, so a hang stops the frames and the ESC sees signal loss (team answer S1). PX4 v1.16.2 does not start the H743 IWDG (team answer S1, not checked by hardware). Depends on the ESC's signal-loss behavior (OPEN-017). | H743 reset or power cycle. | Bench test: halt the H743 over SWD while armed; NOT_VERIFIED |

## 4. Hardware Architecture and Design Constraints

### 4.1 Functional block diagram

The user-provided diagrams show an H743 main MCU, an F100 auxiliary MCU, sensor/interface blocks, USB/SWD, PWM/actuator paths, and a separate power architecture. The images are reference inputs only. Native schematic and PCB files remain the design authority.

### 4.2 Functional blocks

| Block                     | Role | Inputs / outputs | Dependencies | Key constraints |
| ------------------------- |---|---|---|---|
| H743 main controller      | Primary flight-controller processing and interface host | Sensors, external interfaces, USB, SWD, USART, outputs | 5 V input and defined rails | Pins/resources NOT_VERIFIED. |
| F100 IO controller        | px4io: servo PWM, safety switch, servo failsafe | USART link, 8 PWM outputs, safety switch and LED, servo rail sense | H743 data; defined power/reset; 24 MHz crystal (DEC-017) | Electrical implementation NOT_VERIFIED. |
| IMU subsystem             | Two SPI IMU interfaces | SPI, CS, DRDY; reset by software (DEC-009) | Selected sensor parts and rail | 2 × ICM-45686 (DEC-008). Rail: `+3V3A` on VDD and VDDIO (DEC-025). |
| Barometer subsystem       | Two I2C barometer interfaces | I2C, address, pull-ups | Selected sensor parts and rail | ICP-20100 + BMP581 (DEC-010), both on I2C2 with the IST8310. |
| Magnetometer subsystem    | One I2C magnetometer interface | I2C, address, placement | Selected sensor part | IST8310 (DEC-011). Placement TBD. |
| H743 external I/O         | Telemetry/RC, GPS, compass, air-data, rangefinder, power module, 4 motor outputs, 3 spare outputs, microSD, buzzer, LEDs | UART/I2C/timer/SDMMC interfaces | H743 resource allocation | Electrical implementation NOT_VERIFIED. |
| USB/SWD/BOOT0             | Service, debug, recovery | USB FS, debug connector (IF-045), F100 SWD pads (IF-051), BOOT0 | H743/F100 reset and power | Protection and circuit NOT_VERIFIED. |
| Power subsystem           | 5 V board input and 6 V servo supply | Rails, returns, protection | Power module and distribution | Tolerances, current, and protection TBD. |

### 4.3 Power architecture

- Board input and servo supply limits: see PWR-010 and PWR-011.
- The diagram-derived arrangement is a candidate only: 6S battery, XT90-S, PM02D, CRIUS PDB v1.0, 5 V, 3.3 V, 3.3 V_IMU, 6 V UBEC.
- The 6 V UBEC plugs into a board-mount XT30. The 8 headers share an on-board 6 V and servo GND bus, so all servo current passes through the board (DEC-019, OPEN-021).
- USB VBUS powers the board on the bench without the battery (IF-022). It reaches `+5V` through the power mux IN2 (DEC-029). The loads USB powers are TBD (OPEN-006). The PM02D has priority, with the XCOMP fast switchover (DEC-031 to DEC-034).
- 5 V input: TI TPS2121 power mux (DEC-029, 2026-11-01, replaces the DEC-026 eFuse): IN1 from the PM02D (`PM02_5V`), IN2 from USB `VBUS`, OUT to the `+5V` bus, current limit 1.5 A (DEC-030). TI data for the drawn parts is in CMP-008 and 4.7. The TPS2121 blocks reverse current on both channels (CMP-008), so neither source back-feeds the other through it.
- Main 3.3 V rail: TPS62142RGTR buck from the 5 V board input (DEC-012).
- IMU rail: `+3V3A` feeds only the 2 IMUs, on VDD and VDDIO (DEC-025), from a TPS73533DRBR LDO (DEC-027).
- TBD: rail dependencies, current budgets, load steps, sequencing, brownout, reverse-polarity protection, overvoltage protection, transient handling, grounding, filtering, thermal limits.

**Schematic state (`power_supplies.kicad_sch`, saved file, not committed, re-read 2026-11-03 from the 13:24 save with `sch-inspect` and a diff against `HEAD`; earlier rows from a `kicad-cli` netlist export of the saved files; KiCad had the project open, so the editor may hold unsaved changes).** The human owner declared the sheet's capture complete on 2026-10-31. On 2026-11-01 the human owner replaced the eFuse with the TPS2121 power mux ("in sch, I remove eFuse and replace by the Power MUX", DEC-029) and set its current limit to 1.5 A (DEC-030); later the same day the human owner added the PR1 divider for PM02D priority (DEC-031), removed the ST status LED, and then added the CP2 divider for the fast switchover (DEC-032). In the 00:11 save on 2026-11-02, R105 is fitted (DEC-033), R106 and its `GND` symbol moved with no net change, and the XCOMP text notes were rewritten. In the 00:32 save, R101 is 12.1 kΩ (DEC-034) and the PR1 notes follow it. In the 13:24 save on 2026-11-03, the ST status LED is drawn again (Q101 and D103, OPEN-025), D104 changed to LTST-C191GKT, part fields were added to D103, D104, Q101, C105, C112 and C119, and the resistors were renumbered with some values changed. The human owner will decide the resistor fields later ("ignore about resistors field, i will decide later", 2026-11-03), so resistor references and values in this section are still from the 00:32 save and may not match the saved sheet. This records what is drawn. It is not a reviewed or approved design. 47 parts: 45 annotated (U101 to U103, C101 to C121, R101 to R113, L101, L102, D101 to D104, Q101, CN101) and 2 unannotated DNP diodes (`D?`). References were renumbered against rev 0.20, so a reference here may name a different part than before. One `PWR_FLAG`, on `PM02_5V`. ERC not run; the netlist export reports annotation errors, from the 2 parked `D?` diodes. Apart from the power mux (DEC-029), its 1.5 A limit (DEC-030), its PR1 divider (DEC-031), its CP2 divider (DEC-032), R105 fitted (DEC-033) and R101 12.1 kΩ (DEC-034), the buck (DEC-012), the LDO (DEC-027) and the 10 nF SS/TR value (DEC-028), every part below is drawn, not decided. Findings from this check are tracked in P2-019 and P2-020.

| Block | As drawn | Evidence |
| ----- |---|---|
| Power module input | CN101 `SM06B-GHS-TB` (JST, MFR.P/N SM06B-GHS-TB(LF)(SN), LCSC C133065): pins 1-2 `PM02_5V`, pin 3 `PM02_SCL`, pin 4 `PM02_SDA`, pins 5-6 and MP `GND`. The input net has a name again: local label `PM02_5V`, assigned to the `+5V` net class. `PM02_SCL` and `PM02_SDA` are hierarchical labels with sheet pins on `top_hierarchical`, not wired further. The CLIK-Mate change (OPEN-023) is not drawn. | Netlist export of the saved files; `AO-Horizon.kicad_pro` net-class assignment, 2026-11-01 |
| Input protection | D101 SZSMF5.0A TVS (Littelfuse SZSMF5.0AT1G, LCSC C5299833) from `PM02_5V` to `GND`. D102 PESD2USB3UV-T (Nexperia, LCSC C3704436) on `PM02_SCL` and `PM02_SDA` to `GND`. Two DNP TVS diodes, PTVS6V0S1UR (SOD-123) and SLMESD5V0D9 (SOD-323), are unannotated (`D?`) and on no net. They are ESD parts the human owner chose for another sheet and parked here (human owner, 2026-11-02); not a finding. No datasheet for these diodes was checked (`NOT_VERIFIED`). | Netlist export, 2026-11-01 |
| 5 V power mux | U101 TPS2121 (Value `TPS2121RUX`, MFR TI, MFR.P/N TPS2121RUXR, LCSC C485916 not checked, VQFN-HR-12, DEC-029): IN1 (pin 7) `PM02_5V`, IN2 (pin 2) `VBUS`, OUT (pins 1 and 8) `+5V`, GND (pin 12). PR1 (pin 6, `PMUX_PR1`): R101 12.1 kΩ from `PM02_5V`, R102 5 kΩ to `GND` (DEC-031, DEC-034). CP2 (pin 3, `PMUX_CP2`): R105 16.5 kΩ from `VBUS`, fitted, and R106 5 kΩ to `GND` (DEC-032, DEC-033). With R105 fitted (as saved), the mux runs in XCOMP mode: PR1 against CP2, 5 µs fast switchover. With R105 removed, CP2 sits at `GND` and the mux runs in VREF mode: PR1 against the internal VREF, up to 100 µs. In both modes the PM02D has priority (CMP-008, 4.7). OV1 (pin 5, `PMUX_OV1`): R103 23.7 kΩ from `PM02_5V`, R104 5 kΩ to `GND`. OV2 (pin 4, `PMUX_OV2`): R107 23.7 kΩ from `VBUS`, R108 5 kΩ to `GND`. ILIM (pin 10, `PMUX_ILIM`): R109 80.6 kΩ to `GND` (DEC-030). SS (pin 11, `PMUX_SS`): C105 10 nF to `GND`. ST (pin 9, `PMUX_ST`) has a pull-up to `+5V` and drives the Q101 gate (Indicators row, OPEN-025). C101 and C102 100 nF on `PM02_5V`, C103 100 nF on `VBUS`. `VBUS` comes from a power symbol with no source on this sheet; the USB connector will be on another sheet (human owner, 2026-11-01). TI data for these values: CMP-008 and 4.7. | Saved file at 00:32, 2026-11-02 (diff against `HEAD`: R101 value and notes only); netlist export of the 00:11 save; ST net from the 13:24 save, 2026-11-03; TI SLVSEA3F (NotebookLM source fulltext) |
| `+5V` bus | C106, C107 and C117 10 µF, C104 and C118 100 nF (30 µF and 0.2 µF nominal). Feeds U103 and, through L101, the buck. | Netlist export, 2026-11-01 |
| Main 3.3 V buck | U102 TPS62142RGTR: pins 10 to 13 (VIN and EN) to `+5V_BUCK`. Input filter: `+5V` to L101 0.33 µH ASMPH-0603-R33M-T (LCSC C7217516) to `+5V_BUCK`, with C108 to C110 3 × 10 µF and C111 100 nF on `+5V_BUCK`. SW (pins 1 to 3, `3V3_SW`) to L102 3.3 µH JIERR PCR0420-3R3-M (LCSC C53896857) to `+3V3`; VOS (pin 14) to `+3V3`. FB, DEF and FSW (2.5 MHz) to `GND`. PG (pin 4) pulled up by R110 100 kΩ to `+3V3`, with local label `3V3_PG` and hierarchical label `3V3_DONE`; `top_hierarchical` now has a `3V3_DONE` sheet pin (output), not wired further. SS/TR (pin 9) C112 10 nF (DEC-028; this capacitor was C111 in rev 0.20), MFR murata, MFR.P/N GRM1555C1H103JE01D, LCSC C22400107 (added 2026-11-03, not checked). Output C114 to C116 3 × 10 µF and C113 100 nF on `+3V3`. The 10 µF parts are GRM21BZ71C106KE15L (X7R, 16 V, 0805). TI: FB to AGND on fixed versions is recommended; DEF low gives the nominal output; FSW low gives about 2.5 MHz; the PG pull-up may go to any voltage below 7 V (`VERIFIED`). TI Table 9-2 lists 3.3 µH as a proven inductor value (`VERIFIED`); which capacitances it is proven with, the effective capacitance after DC bias, the PCR0420-3R3-M saturation current and the damping of the 0.33 µH input filter are `NOT_VERIFIED`. | Netlist export, 2026-11-01; TI SLVSAJ0F Rev. F, Table 6-1, 8.3, 9.2.2.2 and Tables 9-2 and 9-3 (NotebookLM source fulltext) |
| `+3V3A` LDO | U103 TPS73533DRBR: IN (pin 8) and EN (pin 5) to `+5V`, OUT (pin 1) to `+3V3A` with C121 10 µF and C120 100 nF. NR/FB (pin 3, `LDO_FB`) C119 10 nF, 0402, MFR.P/N GRM1555C1H103JE01D, LCSC C22400107 (added 2026-11-03; dielectric and LCSC code not checked). NC pins 2, 6 and 7 are not connected. The rail's use (DEC-025, IMUs only) and the LDO part (DEC-027) are decided. TI asks for an NR capacitor of no more than 0.01 µF and at least 2 µF output capacitance: 10 nF and 10 µF nominal meet both before derating. | Netlist export, 2026-11-01; TI SBVS087M (NotebookLM source fulltext) |
| Indicators | D104 green LED LTST-C191GKT (Value was LTSL-C191TGKT until 2026-11-03; LCSC C99289) from `+3V3` through a series resistor (`3V3_LED_A`), not driven by PG. Power mux status LED, drawn again on 2026-11-03 and not decided (OPEN-025): Q101 DMG1012UW N-MOSFET (SOT-323, LCSC C48935695) with gate on `PMUX_ST`, source to `GND` and drain to the D103 cathode; D103 LTST-C191GKT (LCSC C99289), anode through a series resistor to `+5V`. TI: ST is high for IN1 or Hi-Z and low for IN2 (CMP-008, `VERIFIED`), so D103 is lit while the PM02D powers `+5V` and off on USB (`ESTIMATED` from the drawn circuit). Q101 threshold and VGS rating against the `+5V` gate drive are `NOT_VERIFIED`. No fault LED. | Saved file at 13:24, 2026-11-03 (`sch-inspect` local-net and project-net); TI SLVSEA3F via CMP-008 |
| Part fields | U101 has MFR TI, MFR.P/N TPS2121RUXR and LCSC C485916 (the LCSC code is not checked against the part); its Value stays `TPS2121RUX`. Q101: MFR GOODWORK, MFR.P/N DMG1012UW, LCSC C48935695 (not checked). D103 and D104: LCSC C99289, but MFR holds the part number LTST-C191GKT and MFR.P/N holds `LITEON` (swapped). C105, C112 and C119: MFR murata, MFR.P/N GRM1555C1H103JE01D, LCSC C22400107 (not checked). Resistor fields: the human owner decides them later (2026-11-03). The root sheet's design conventions note asks for Value, Footprint, MFR, MFR.P/N and LCSC on every part. | Saved file at 13:24, 2026-11-03 |

**Power mux library part (project library, 2026-11-01).** Symbol `0_Power_Management:TPS2121RUX`, drawn from the SLVSEA3F pin table (12 pins, pins match the footprint pads). Footprint `0_Package_DFN_QFN:Texas_VQFN-HR-12_2x2.5mm_P0.5mm_ThermalVias`, a stock copy whose pads match the RUX0012A land pattern (8 pads 0.2 × 0.6 mm and 4 pads 1.05 × 0.4 mm at the TI positions, `VERIFIED`). 3D model `Texas_VQFN-HR-12_2x2.5mm_P0.5mm_TPS2121RUXR.step`, supplied by the human owner. Pin 1 corner against the TI drawing and the 3D model alignment are human checks. A second, unused stock copy without thermal vias is also in the library.

**Q101 library part (project library, 2026-11-03, not committed).** Symbol `0_Transistor_FET:DMG1012UW` (pins 1 G, 2 S, 3 D) with footprint `0_Package_TO_SOT_SMD:SOT-323_SC-70` (3 pads, 3D model found, preflight). The pin map against the datasheet is `NOT_VERIFIED`. The `2N7002K` symbol changed only the position of its hidden Description field.

The root, `top_hierarchical`, `block_diagram` and `revision_history` sheets hold no parts; `top_hierarchical` has the power sheet symbol with sheet pins `3V3_DONE`, `PM02_SCL` and `PM02_SDA`. The root sheet now carries a "DESIGN CONVENTIONS" text note (net names, style, reference letters, units, part fields). On 2026-11-03 the title blocks of every sheet and the PCB changed from revision `1.0` to `A`, and the project text variables now set `PROJECT_ID` `NP-AO-2601`, `SCH_DRAWING_NAME`, `SCH_DRAWING_DATE` 01-Nov-2026, `RELEASE_DATE` 02-Nov-2026 and a new `STATUS` variable `DRAFT`, shown on the root sheet. These are drawing fields; they do not set the hardware phase row above. The saved PCB has no footprints; it has one 27 × 29 mm rectangle on `Edge.Cuts` (drawn, not decided; the outline is open in OPEN-009).

### 4.4 Clock, reset, boot and programming

- H743 shall retain selectable BOOT0 access (FUN-006).
- H743 and F100 shall provide SWD access (FUN-005).
- USB FS shall be physically available on H743 for later Software-owned flashing/QGC integration.
- H743 clock: 16 MHz HSE crystal, as `px4/fmu-v6c` (DEC-017). No LSE.
- F100 clock: 24 MHz HSE crystal, used directly as SYSCLK, as in stock px4io-v2 (DEC-017; PX4 v1.16.2 `boards/px4/io-v2/nuttx-config/include/board.h`). The F100 HSE oscillator takes 4 to 24 MHz (DocID16455 Rev 9 Table 21, OPEN-020). The stock px4io bootloader runs from HSI. No LSE; PC14 and PC15 unconnected (px4io reads them at boot).
- F100 boot: BOOT0 and BOOT1 (PB2) pulled down. The software team flashes the px4io bootloader over SWD once; after that PX4 updates the F100 over the USART link. No BOOT0/NRST control from the H743.
- H743 first flash: PX4 bootloader over SWD (software team, ST-LINK); updates over USB.
- Boot-time outputs: every PWM line low before firmware starts, with a weak pull-down and no pull-up (team, pinmap review Q10). Value TBD (OPEN-018).
- Watchdogs: px4io starts the F100 IWDG; PX4 v1.16.2 does not start the H743 IWDG (team answer S1).
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
| CMP-002 | IO MCU | Must be STM32F100C8T6B, the chip px4io-v2 is built for (DEC-002, DEC-017). Replaced the STM32F103C8T6 on 2026-10-24. | TBD | LCSC availability checked by the human owner on 2026-10-24 (stock value not recorded). Lifecycle and approved source TBD |
| CMP-003 | IMU | Two SPI positions required. Must be TDK InvenSense ICM-45686 (DEC-008). | TBD | TDK: Production (product page, 2026-10-19). PX4 driver present. SPI support, supply range, availability and approved source NOT_VERIFIED |
| CMP-004 | Barometer | Two I2C positions required. Position 1 must be TDK ICP-20100 (DEC-010). Position 2 must be Bosch BMP581 (DEC-010), PX4 driver `barometer/bmp581`; fallback Bosch BMP384 (PX4 `bmp388` driver) if the BMP581 cannot be bought (OPEN-019). | TBD | ICP-20100 is EOL (TDK page). TDK SmartPressure page: "Pressure products are EOL and not recommended for new designs" (2026-10-19). BMP390 removed on 2026-10-21 because LCSC C5124834 is not available. BMP581: DigiKey 0 in stock on 2026-10-08, 10,000 due 2026-11-19 (team answer D7, NOT_VERIFIED). Approved source TBD |
| CMP-005 | Magnetometer | One I2C position required. Must be iSentek IST8310 (DEC-011). AVDD and DVDD 1.72 to 3.6 V; absolute maximum also 3.6 V. LGA-16, 3.0 × 3.0 × 1.0 mm. I2C up to 400 kHz, address 0x0C to 0x0F (CAD1/CAD0). (IST8310 Datasheet V1.2, via NotebookLM.) | TBD | PX4 driver `magnetometer/isentek/ist8310` present. Lifecycle not stated in the datasheet; the iSentek web site did not render (NOT_VERIFIED). Approved source TBD |
| CMP-006 | Regulator, protection, connector, PDB/UBEC, interface parts | Electrical requirements shall be satisfied. | Specific parts TBD. | MFR/MPN, availability, lifecycle, approved source TBD |
| CMP-007 | Main 3.3 V regulator | Must be TI TPS62142RGTR (DEC-012). Fixed 3.3 V, VIN 3 to 17 V, 2 A, VQFN-16 3 × 3 mm (TI SLVSAJ0F Rev. F, HTML). | 2.5 MHz (FSW low) as drawn | TI: ACTIVE (2026-10-19; the page also points to a newer TPS62902). LCSC C129331: 632 in stock (snapshot 2026-10-18). Approved source TBD |
| CMP-008 | 5 V power mux | Must be TI TPS2121 in the RUX package (VQFN-HR-12, 2.0 × 2.5 mm) (DEC-029): IN1 from the PM02D 5 V, IN2 from USB VBUS, OUT to `+5V`; current limit 1.5 A (DEC-030). This row held the TPS259251DRC eFuse (DEC-026) until rev 0.20. TI SLVSEA3F (August 2020), NotebookLM notebook `TPS212x 2.8-V to 22-V Priority Power MUX with Seamless Switchover` (added by the human owner), `VERIFIED` in the source fulltext: IN1 and IN2 2.8 to 22 V recommended; IN and OUT 24 V absolute maximum; OV1, OV2 and ST 6 V absolute maximum, 5.5 V recommended; continuous input current 4.5 A; RON 56 mΩ typ, 70 mΩ max at 25 °C, 100 mΩ max at 125 °C; input UV rising 2.5 / 2.65 / 2.8 V; VREF on PR1, CP2, OV1 and OV2 rising 1.01 / 1.06 / 1.1 V; current limit with RILM 80 kΩ 1.0 / 1.5 / 2.0 A (RILM 18 to 100 kΩ); fast-trip at about 2.4 × ILM, then off for about 25 ms; reverse current blocking always on for each channel (threshold 0.2 / 1 / 2 A, response 10 µs); switchover 100 µs max with CP2 below VREF, 5 µs with CP2 at or above VREF; with PR1 and CP2 low, the higher input wins and IN2 wins at equal voltage, VCOMP 0 / 280 / 600 mV (Table 9-3, 9.3.8); ST is high for IN1 or Hi-Z and low for IN2; ST pull-up 6 to 20 kΩ recommended. | TBD | TI product page: ACTIVE, Rev. F is the latest datasheet (fetched 2026-11-01). Datasheet ordering addendum (31-Oct-2025): TPS2121RUXR and TPS2121RUXT Active. LCSC, availability and approved source TBD |
| CMP-009 | `+3V3A` LDO | Must be TI TPS73533DRBR (DEC-027), from `+5V` to `+3V3A`, feeding only the 2 IMUs (DEC-025). Fixed 3.3 V, 500 mA (TI SBVS087M 5.3), VSON-8 3 × 3 mm. NR capacitor at most 0.01 µF and output at least 2 µF (TI SBVS087M, NotebookLM source fulltext). | TBD | LCSC C388480 on the part (not checked). Lifecycle, availability and approved source TBD |

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
| 5 V power mux settings (U101) | RILM 80.6 kΩ (DEC-030), PR1 divider 12.1 kΩ / 5 kΩ from IN1 (DEC-031, DEC-034), CP2 divider 16.5 kΩ (fitted, DEC-033) / 5 kΩ from `VBUS` (DEC-032), OV dividers 23.7 kΩ / 5 kΩ on both inputs, CSS 10 nF; `+5V` and `+5V_BUCK` capacitance as drawn, about 60 µF nominal | TI SLVSEA3F Electrical Characteristics, 9.3.1, 9.3.2, 9.3.7, Table 9-1 and 10.2.4.2 (CMP-008) | Limit 1.0 / 1.5 / 2.0 A from the 80 kΩ table row (`VERIFIED`); 1.49 A typ from `ILM = 65.2 / RILM^0.861`, RILM in kΩ (`ESTIMATED`: equation form read from the flattened text, it reproduces TI's 59 kΩ to 1.95 A example). OV trip 6.08 V typ, the same divider as TI equation 6 (`VERIFIED`); 5.80 to 6.31 V over the VREF range, before resistor tolerance (`ESTIMATED`). Soft-start: TI Table 9-1 starts at 100 nF (780 V/s at 5 V); scaled as 1/C, 10 nF gives about 7.8 kV/s, about 0.65 ms to 5 V and about 0.47 A inrush into 60 µF (`ESTIMATED`, outside the table range). PR1 ratio 3.42, CP2 ratio 4.3 (TI equation 5 and 12 form, `ESTIMATED`, before resistor tolerance). XCOMP (R105 fitted): CP2 1.10 / 1.16 / 1.22 V for `VBUS` 4.75 / 5.0 / 5.25 V; switch to USB when the PM02D falls to 3.78 / 3.98 / 4.18 V (switch point `= CP2 × 17.1 / 5`). Worst case at `VBUS` 5.25 V: 1 % resistors in the bad direction give CP2 1.24 V and a PR1 ratio of 0.2883, so 4.30 V; the 40 mV maximum comparator offset (TI 7.5, 5 / 20 / 40 mV, `VERIFIED`) adds 0.14 V, so 4.44 V, 0.06 V below the 4.5 V input minimum (PWR-010). With R101 12.4 kΩ (DEC-032 value) the same case gave 4.52 V, 0.02 V above the minimum, which is why R101 changed (DEC-034). TI Table 9-3 (`VERIFIED`): IN1 needs PR1 ≥ VREF and PR1 > CP2, so the VREF-mode point below is the lowest IN1 the mux keeps. CP2 reaches the 1.10 V VREF maximum at `VBUS` 4.73 V (4.80 V with 1 % resistors); below that a part may run in the VREF mode (same priority, 100 µs). VREF mode (R105 not fitted): to USB at 3.39 / 3.56 / 3.73 V, back at 3.45 / 3.63 / 3.76 V. PR1 at the 6.31 V OV trip maximum: 1.85 V, below its 5.5 V limit. Divider currents about 0.29 mA (PR1) and 0.23 mA (CP2) at 5 V. Switchover dip in the VREF mode: up to 100 µs, `VDIP = IOUT × tSW / COUT`, about 1.7 V at 1 A into 60 µF (`ESTIMATED`, nominal capacitance) | Minimum limit 1.0 A against the unknown 5 V load (OPEN-006). XCOMP switch point 4.44 V worst case with 1 % resistors, 0.06 V below the 4.5 V minimum (DEC-034). Use 1 % resistors in the PR1 and CP2 dividers |
| Buck soft-start (U102) | SS/TR 10 nF (DEC-028), ISS 2.5 µA typ (2.3 to 2.7 µA), internal reference 1.25 V (equation 10 constant, as extracted) | TI SLVSAJ0F equation 10, ISS from Electrical Characteristics | 5 ms typ, about 4.6 to 5.4 ms over the ISS range, before capacitor tolerance (`ESTIMATED`) | C112 (C111 until rev 0.20) has MFR.P/N GRM1555C1H103JE01D and LCSC C22400107 since 2026-11-03 (not checked) |
| Servo rail current     | 6 V rail and actuator load (on the board, DEC-019) | TBD | NOT_VERIFIED | 8 servos can move at once (team). Tilt servos 4 × RDS3235; other servos Kingmax C507 and DS-843MG, positions TBD (team design). All stall currents TBD; team bench target: 4 tilt servos at or below 10 A. Sizes the UBEC (OPEN-007) and the board input and bus (OPEN-021) |
| Power rail tolerance   | All MCU/sensor rails | TBD | NOT_VERIFIED | Nominal, min, max, and load-step limits TBD |
| Thermal margin         | MCU, regulator, protection, output drivers | TBD | NOT_VERIFIED | Ambient, dissipation, copper, and cooling TBD |
| Safety response timing | H743 stop to servo failsafe; H743 hang to motor stop | px4io `FMU_INPUT_DROP_LIMIT_US` = 500000 (PX4 v1.16.2 `px4iofirmware/mixer.cpp`) | Servos: 0.5 s by firmware design (VERIFIED in source, not measured). Motors: NOT_VERIFIED | Motor stop time depends on the ESC signal-loss timeout (OPEN-017). Test: halt the H743 over SWD |

## 5. PCB Design Specification

### 5.1 Mechanical envelope

| ID      | Item | Requirement / limit | Verification |
| ------- |---|---|---|
| MEC-001 | Board outline | Each board dimension shall be less than `80 mm × 80 mm`. Exact outline and shape TBD. This supersedes the older diagram size of about `90 mm × 95 mm`. | Native PCB inspection / measurement |
| MEC-002 | Mounting | M3 screws, 3.2 mm hole with pad (human owner); the CAD team follows the hardware. Soft mount on rubber dampers; the dampers are a separate part and do not change the PCB. The board sits on its own tray on the fuselage floor near the CG, not on the ESC (human owner). Damper model: hardware picks it at placement | Native PCB inspection / measurement |
| MEC-003 | Connector orientation and service access | Any edge may face forward (PX4 sets the board rotation); the forward direction shall be marked on the silkscreen. USB-C, microSD and the H743 debug connector shall be reachable with the canopy open (team, REF-09). USB-C and microSD on adjacent edges (human owner). Cable entry sides TBD, set by hardware | Mechanical inspection |
| MEC-004 | Height, keepouts, enclosure, environmental constraints | Part height about 10 to 15 mm, with the Pixhawk 6C as the reference; hardware sets the final value at placement (human owner). The GPS sits above the board under the canopy; the CAD team draws the space to fit the board (OPEN-009) | Mechanical inspection / analysis |

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
| PCB-010 | H743/F100 power and returns | Width, return path, via, load-step | Current and noise control | Layout review / analysis |
| PCB-011 | IMU, barometer, magnetometer regions | Placement, vibration, magnetic, noise | Sensor integrity | Placement review / test |
| PCB-012 | USB FS | Routing, ESD, VBUS, connector, return path | USB physical integrity and protection | Layout review / hardware test |
| PCB-013 | SWD and BOOT0 | Probe access, reset/boot-state | Debug and recovery | Inspection / debug test |
| PCB-014 | PWM/actuator outputs | Return path, drive, protection, connector | Actuator integrity and safety | Layout review / electrical test |
| PCB-015 | USART H743↔F100 | Routing, voltage compatibility, return path, test access | Inter-MCU safety/control path | Review / hardware test |

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
| TST-002 | F100 SWD and console | Pads or header: SWDIO, SWCLK, NRST, GND, USART1 TX. Bench use only (IF-051) | Inspection; debug test |
| TST-003 | H743 BOOT0 | Selectable and observable boot state | Inspection; boot-state test |
| TST-004 | 5 V board input | Test point; current/voltage measurement access | Inspection; measurement |
| TST-005 | 6 V servo rail | Test point on the on-board 6 V servo bus (DEC-019); current measured in the UBEC lead | Inspection; measurement |
| TST-006 | H743↔F100 USART | Physical test access; signal observation | Inspection; hardware test |
| TST-007 | F100 safety path and motor stop | Fault-injection access for the H743-unavailable condition (halt the H743 over the IF-045 SWD) | Fault-injection test (SAF-001, SAF-015) |

## 7. Verification Plan (Planning Only)

No automatic gates. This table plans how requirements could be checked. It does not declare phase completion, design approval, or release readiness.

| Requirement ID | Method | Planned evidence | Result | Reviewer |
| ------------------------- |---|---|---|---|
| MCU-001, MCU-002          | Inspection | Native schematic/package review | NOT_VERIFIED | Human, TBD |
| IF-001                    | Inspection / Test | USART allocation review; physical link test | NOT_VERIFIED | Human, TBD |
| SEN-001, SEN-002, SEN-003 | Inspection / Test | Bus allocation review; sensor electrical access test | NOT_VERIFIED | Human, TBD |
| PWR-001, PWR-002          | Analysis / Test | Power-tree review; rail measurement; load/current test | NOT_VERIFIED | Human, TBD |
| SAF-001, SAF-015          | Test | Halt the H743 while armed: servo failsafe time at the F100, motor stop time at the ESC | NOT_VERIFIED | Human, TBD |
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
| DEC-002 | Auxiliary (IO) MCU part number | STM32F100C8T6B | Changed from STM32F103C8T6 by the human owner on 2026-10-24, following the software team (pinmap review 0.3 row 4.2, decisions file S7 option (d)): px4io-v2 is built for this chip. Same LQFP48 pin names and types as the STM32F103C8, and every allocated signal is on the same pin (ST pin data, checked 2026-10-24). Implementation not verified. | 2026-10-12, changed 2026-10-24 |
| DEC-003 | H743↔F100 physical interface protocol | USART | Instance, rate and protocol set by DEC-015. | 2026-10-12 |
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
| DEC-014 | Pin allocation basis and PX4 port (SYS-002, OPEN-001) | H743 pins mostly from Pixhawk 6C (`px4/fmu-v6c`), F100 pins from `px4/io-v2`. Port based on `px4/fmu-v6c`, PX4 v1.16.2 | Decisions file section 3, pinmap review Q1 and Q18. Pins tested by the team on a NUCLEO-H753ZI only. Schematic and PCB not copied. | 2026-10-24 |
| DEC-015 | H743↔F100 link (IF-001, IF-024, OPEN-002) | px4io protocol, H743 USART6 ↔ F100 USART2, 1.5 Mb/s | px4io-v2 uses USART2 at 1500000 b/s for the FMU link (PX4 v1.16.2 `io-v2/src/board_config.h`). The F100 runs stock px4io-v2 (DEC-017). | 2026-10-24 |
| DEC-016 | Output split and H743-failure behavior (SAF-001, FUN-002, FUN-004, SAF-010, SAF-011, OPEN-008) | H743 TIM5 drives the 4 motors, DShot only, bidirectional, TIM5 as timer 0 with DMA. F100 drives the 8 servos. After 0.5 s without H743 data the F100 holds the servos at failsafe values (PX4 disarmed values `PWM_MAIN_DISn` by default). No landing | Decisions file D1, D2, D3, S1, S2, S3. Needs DShot-capable ESCs; planned Holybro Tekko32 F4 4-in-1 with AM32, not confirmed. The team design changed to 4 × Hobbywing Skywalker 80A V2 (rev 0.14), whose DShot support is `NOT_VERIFIED`. Motor stop on a hang: OPEN-017. | 2026-10-24 |
| DEC-017 | Clocks and IO MCU firmware build (OPEN-015) | H743: 16 MHz crystal. F100: 24 MHz crystal as SYSCLK, stock px4io-v2 and stock px4io bootloader | Decisions file H1, and S7 option (d) taken after the team's pinmap review 0.3 answer. Replaces option (a) (F103 with an 8 MHz crystal, PLL ×3 and a custom px4io build). The px4io bootloader runs from HSI, so it needs no build for either crystal (PX4-Bootloader `main_f1.c`: `rcc_clock_setup_in_hsi_out_24mhz()`, `main` branch read 2026-10-24). | 2026-10-24, changed in rev 0.12 |
| DEC-018 | Interface set for Model G (IF-010 to IF-021, IF-038, IF-040 to IF-051) | One GPS; USART3 is the H743 debug console; UART7 TX spare, I2C3 and FlySky dropped; RC and telemetry over one ELRS receiver on UART7; 3 spare outputs kept; microSD on SDMMC1 without card-detect; buzzer TIM3_CH3; 3 LEDs; safety switch on the F100; H743 debug on a Pixhawk Debug Mini connector; F100 debug on pads, bench only | Decisions file section 3, D4, D5, D6, S4, S6, H2. RC over MAVLink is partly tested; the team runs the RC-loss bench test (S5). If it fails, the same receiver can run CRSF on UART7 with no pin change. | 2026-10-24 |

DEC-020 to DEC-022 come from the software team's answers to the integration questions (REF-09), accepted by the human owner on 2026-10-24. D10 and D11 are signed "Software team (proposal for the team)"; a separate whole-team confirmation is not recorded. DEC-019 started from the team's D8 answer and was changed by the human owner the same day. DEC-023 is the human owner's. D9 (mounting) is not a decision: the CAD team must confirm it, so it stays a proposal in MEC-002 to MEC-004 and OPEN-009.

| ID      | Topic | Selected option | Notes | Date |
| ------- |---|---|---|---|
| DEC-019 | Servo power path (PWR-002, PWR-011, IF-030 to IF-037, IF-050) | 8 × 3-pin servo headers (signal, +6 V, GND) with the + and GND pins bussed on the board, Pixhawk style. The UBEC plugs into a board-mount XT30 (changed the same day from one header position, see Notes) | Human owner: "PWR + SIG + GND", then "2. but 10A mean 10A all servo runing : 10A/6 if 6 servo because UBEC can give 10A contd." Replaces the team's D8 option (b) (signal and GND only, REF-09). Each servo pin carries one servo's current; the UBEC input pins and the bus carry the total, up to 10 A continuous and 15 A peak (OPEN-021). All 8 servos can move at once; stall current not known (OPEN-007). Changed the same day: the UBEC plugs into a board-mount XT30 instead of a header position, because one header pin is about 3 A (human owner). | 2026-10-24 |
| DEC-020 | Environment (ENV-001, ENV-002, ENV-004) | Parts rated −40 to +85 °C, no conformal coating, no rain exposure | REF-09 D10. Hot-weather flights near sea level, low altitude only. Vibration (ENV-003) still TBD. | 2026-10-24 |
| DEC-021 | Safety switch, buzzer and GPS port (IF-012, IF-046, IF-049) | GPS1 is the 10-pin full GPS port; the GPS module's safety switch and LED reach the F100. Model G flies with the safety switch disabled in PX4; no separate switch. Board buzzer stays | REF-09 D11. The switch can be enabled later with no hardware change. GPS: Holybro M9N, to be confirmed. Pinout: OPEN-023. | 2026-10-24 |
| DEC-022 | IO MCU image and IMU heater (DEC-017) | Stock `px4_io-v2_default` image in the board's `extras/` folder, as `px4/fmu-v6c`. No IMU heater; PB14 drives only the px4io blue LED | REF-09 S8 and S9. No 8 MHz px4io build. PX4 IMU temperature calibration if needed. | 2026-10-24 |
| DEC-023 | ESC current-sense pin (IF-048, IF-052) | PC1 stays reserved for an analog power module. The ESC current goes to another free ADC pin that hardware picks after checking ST pin data | Human owner: "Keep PC1, use other ADC pin". The team asked for PC1 (REF-09). Candidates PC5, PB1, PC2_C, PC3_C (pinmap review 0.3 free list). ESC current sense dropped on 2026-10-24 (IF-052 removed); PC1 stays reserved. | 2026-10-24 |
| DEC-024 | 5 V input protection (PWR-010, OPEN-006, OPEN-012) | TI TPS16412DRC eFuse between the PM02D `+VIN` and the main `+5V` bus. Part rated 1.8 A; current limit set to 1.5 A | Human owner: "eFuse 1.8A (set 1.5A) (TPS16412DRC) between PM02D and main +5VBus". The 1.8 A rating, the ILIM resistor for 1.5 A, reverse-current behavior (USB back-feed) and the 1.5 A budget against the board and external 5 V loads are `NOT_VERIFIED` (OPEN-012). Superseded on 2026-10-29 by DEC-026. | 2026-10-24 |
| DEC-025 | `+3V3A` use (PWR-013, SEN-001, OPEN-011) | `+3V3A` feeds only the 2 × ICM-45686 IMUs, on both VDD and VDDIO. No other load on `+3V3A` | Human owner: "just IMU will use +3V3A", then "VDD and VDDIO both". This is the 3.3 V_IMU rail of the power budget. The LDO part is not decided (TPS73533DRBR is drawn). With VDDIO on `+3V3A`, the IMU SPI levels come from `+3V3A` while the H743 runs on `+3V3`; level match and power-up order are `NOT_VERIFIED` (OPEN-011). | 2026-10-26 |
| DEC-026 | 5 V input protection (PWR-010, OPEN-006, OPEN-012); replaces DEC-024 | TI TPS259251DRC eFuse between the PM02D `+VIN` and the main `+5V` bus, current-limit target 2 A | Human owner: "i update the eFuse", then, asked how to record it, chose "DECISION, new limit" and "2 A". Replaces the TPS16412DRC of DEC-024. The part rating, the ILIM resistor for 2 A (45.3 kΩ drawn), reverse-current behavior (USB back-feed) and the 2 A budget against the board and external 5 V loads are `NOT_VERIFIED` (OPEN-012). The 2 A limit equals the PM02D source capacity (PWR-010). Superseded on 2026-11-01 by DEC-029. | 2026-10-29 |
| DEC-027 | `+3V3A` LDO (CMP-009, OPEN-011) | TI TPS73533DRBR, from `+5V` to `+3V3A` (LCSC C388480 on the part) | Human owner: "record LDO as decide" (2026-10-31). The part was drawn since rev 0.6. Load, IMU SPI level match with the H743 on `+3V3` and power-up order stay open (OPEN-011). | 2026-10-31 |
| DEC-028 | TPS62142 soft-start (U102, C111) | SS/TR capacitor 10 nF, for about 5 ms soft-start | Human owner: "C111 (SS/TR) i choose 10nF for about 5ms" (2026-10-31). 5 ms from TI SLVSAJ0F equation 10 with ISS 2.5 µA (4.7, `ESTIMATED`). As committed in `895c26a`, C111 is 0402, C0G, 50 V, with MFR.P/N and LCSC left empty. | 2026-10-31 |
| DEC-029 | 5 V input path (PWR-010, IF-022, OPEN-006); replaces DEC-026 | TI TPS2121 power mux (RUX, VQFN-HR-12): IN1 from the PM02D 5 V, IN2 from USB VBUS, OUT to the `+5V` bus. The eFuse is removed | Human owner: "in sch, I remove eFuse and replace by the Power MUX , i added in LM" (2026-11-01). Replaces the TPS259251DRC of DEC-026. The mux also joins USB and the PM02D and blocks reverse current on both channels (CMP-008). The priority mode as drawn (VCOMP, PR1 and CP2 at `GND`) is drawn, not decided (OPEN-024). Orderable code (RUXR or RUXT) not chosen. | 2026-11-01 |
| DEC-030 | Power mux current limit (U101, ILIM resistor) | 1.5 A | Human owner: "new decision current lim at 1.5A" (2026-11-01). 80.6 kΩ is drawn (R106 at the decision, R109 after the later renumbering); TI gives 1.0 / 1.5 / 2.0 A at 80 kΩ (CMP-008, 4.7). The 1.5 A budget against the board and external 5 V loads is open (OPEN-006). | 2026-11-01 |
| DEC-031 | Power mux source priority (U101 PR1, OPEN-024) | PM02D (IN1) has priority, set by a resistor divider from IN1 to PR1: R101 from IN1 (13.7 kΩ, then 12.4 kΩ with DEC-032, then 12.1 kΩ with DEC-034), R102 5 kΩ to `GND` | Human owner: "set PM02D priority with PR1 divider, i will update sch" (2026-11-01). Replaces the VCOMP mode as drawn (PR1 at `GND`), in which USB won. With PR1 at or above VREF, IN1 powers `+5V` whenever it is valid, and IN2 takes over when PR1 falls below VREF (TI Table 9-3, 10.2.3). Then: "use 13.7k / 5k divider" (2026-11-01): switchover to USB at about 3.9 V typ, 4.08 V max (4.7, `ESTIMATED`). Drawn in the 02:09 save. CP2 (fast switchover) is open (OPEN-024). The PR1 values are retuned for DEC-032 (OPEN-024). | 2026-11-01 |
| DEC-032 | Power mux fast switchover (U101 CP2, OPEN-024) | XCOMP mode (TI 10.3): a resistor divider from `VBUS` to CP2, compared against the PR1 divider, for the 5 µs fast switchover. The top CP2 resistor is a population option: fitted gives XCOMP; DNP leaves CP2 pulled to `GND` by the bottom resistor, which gives the VREF mode (100 µs) | Human owner chose the XCOMP option over keeping CP2 at `GND`: "i select B but use DNP or switc between A abd B for option" (2026-11-01). In XCOMP the switch point follows `VBUS`, so the window to the 4.5 V input minimum is tight (4.7, `ESTIMATED`). Values: "use 12k4 and 16k5, i updated sch" (2026-11-01): CP2 16.5 kΩ / 5 kΩ from `VBUS`, PR1 changed from 13.7 kΩ to 12.4 kΩ so the XCOMP switch point stays below 4.5 V. Drawn in the 02:49 save, with the 16.5 kΩ (R105) marked DNP. Default population: DEC-033. | 2026-11-01 |
| DEC-033 | Power mux default population (U101 CP2, R105, OPEN-024) | R105 16.5 kΩ is fitted in the default build, so U101 runs in XCOMP mode (5 µs switchover). Removing R105 still gives the VREF mode (DEC-032) | Human owner: "i update TPS2121RUX config in XCOMP mode about resistor div." (2026-11-01). Saved file: R105 no longer DNP; the sheet text notes now show the XCOMP calculation (CP2, PR1, switch point for `VBUS` 4.75 / 5.0 / 5.25 V) and the OV note uses 23.7 kΩ (00:11 save, 2026-11-02). The switch-point tolerance was settled by DEC-034. | 2026-11-01 |
| DEC-034 | Power mux PR1 top resistor (U101, R101, OPEN-024) | R101 12.1 kΩ (was 12.4 kΩ), R102 5 kΩ, 1 % parts | Human owner: "use R101 12k1, i updated sch" (2026-11-02), after the tolerance check: with 12.4 kΩ, 1 % resistors and the 40 mV comparator offset, the XCOMP switch point reached 4.52 V at `VBUS` 5.25 V, above the 4.5 V input minimum (PWR-010). With 12.1 kΩ: 4.44 V worst case, 3.98 V nominal at `VBUS` 5.0 V; VREF mode 3.39 to 3.76 V (4.7, `ESTIMATED`). The other option, 0.5 % resistors, was not chosen. Drawn in the 00:32 save, with the PR1 notes on the sheet updated. Closes OPEN-024. | 2026-11-02 |

### 8.2 Open questions and assumptions

| ID       | Description | Impact | Owner / next action |
| -------- |---|---|---|
| OPEN-001 | Exact H743/F100 pins and alternate functions. Pinmap review 0.3 was answered by the team on 2026-10-24 (REF-07); the IO MCU change to the F100 moves no pin (DEC-002). Each pin's signal is listed in ST pin data. Not yet drawn in the schematic; DMA streams and interrupt priorities are Software-owned and not checked by hardware (P1-010). | May invalidate the allocation. | Hardware review / P1 |
| OPEN-002 | Closed 2026-10-24 by DEC-015 (instance, pins, rate, protocol). Link protection and test access stay with PCB-015 and TST-006. | Affects safety/control path. | Closed |
| OPEN-003 | Closed 2026-10-24. F100 labels corrected to TIM3_CH1 to CH4 (IF-034 to IF-037); H743 motors on TIM5_CH1 to CH4 with DMA (DEC-016; the team says PX4 maps DMA for TIM5, decisions file S2). | Resolved by reassignment. | Closed |
| OPEN-004 | Sensor electrical properties and sourcing. Sensor parts chosen (DEC-008, DEC-010, DEC-011); datasheet values, ICP-20100 EOL, BMP581 stock and IST8310 lifecycle open. IST8310 has only 0.3 V from a 3.3 V rail to its 3.6 V absolute maximum. | Affects footprint, rail, layout, drivers, verification. | Human owner / P0 |
| OPEN-005 | Second magnetometer allocation. Closed by DEC-011 (single magnetometer). | Affects sensor redundancy and connector/bus architecture. | Closed 2026-10-18 |
| OPEN-006 | 5 V input transient/protection, board current budget, downstream rail budgets. USB powers the board on the bench (IF-022), including all external 5 V ports (human owner). VBUS current limit and the USB-only load (board plus GPS, ELRS, TF-Luna, airspeed) are TBD. Since 2026-11-01 the TPS2121 power mux (DEC-029) joins the PM02D and USB and blocks reverse current on both channels (CMP-008), so the eFuse back-feed concern of rev 0.19 is gone. Open: the 1.5 A limit (1.0 A minimum, DEC-030) against the board plus external 5 V loads; the same limit applies to USB, so the load can exceed a 500 or 900 mA USB port; input transients and PM02D cable ringing (TI suggests more input capacitance for long cables; IN1 has 2 × 100 nF). | Affects power design and protection. | Hardware review / P0, P2 |
| OPEN-007 | 6 V servo rail pulse duration, protection, distribution, actuator load profile. On the board since DEC-019. All 8 servos can move at once. Tilt servos 4 × RDS3235; the other 4 are Kingmax C507 and DS-843MG, positions TBD (team design). Every servo model is rated for 6 V (human owner, 2026-10-24; servo datasheets not checked by Claude). Stall currents not known; team bench target: 4 tilt servos at or below 10 A while tilting 0 to 90° at hover thrust. The other 4 add to that in cruise. | UBEC may be undersized; the stall total also sizes the board input and bus (OPEN-021). | Team (bench test) + Hardware / P0, P2, P4 |
| OPEN-008 | Closed 2026-10-24 by DEC-016: no landing; servo failsafe after 0.5 s; motors on the H743. The servo failsafe values are PX4 parameters that the software team sets after flight tests (decisions file D3). Motor stop: OPEN-017. | Affects F100 behavior, output ownership, test method. | Closed |
| OPEN-009 | Exact board outline under the MEC-001 limit, mounting, connector orientation. Environment set by DEC-020. Set by the human owner: M3, 3.2 mm hole; soft mount; own tray, not on the ESC; USB-C and microSD on adjacent edges; part height about 10 to 15 mm (MEC-002 to MEC-004). Open, set by hardware (the CAD team follows): board outline, cable entry sides, damper model (at placement). | Affects PCB and mechanical release. | Human owner, then CAD team / P0, P3 |
| OPEN-010 | All non-MCU part numbers except the sensors (DEC-008, DEC-010, DEC-011), the main 3.3 V buck (DEC-012), the 5 V power mux (DEC-029) and the `+3V3A` LDO (DEC-027). Passive MFR and MFR.P/N: the human owner chooses them later (2026-10-31) | No other non-MCU part is approved by this document. | Human owner / component selection gate |
| OPEN-011 | `+3V3A` rail: use decided on 2026-10-26 (DEC-025: the 2 IMUs only, VDD and VDDIO); LDO decided on 2026-10-31 (DEC-027: TPS73533DRBR). Open: the load, and whether the IMU VDDIO on `+3V3A` matches the H743 I/O on `+3V3` for the SPI levels and power-up order (check the ICM-45686 VDDIO limits). As drawn (2026-11-01, references renumbered), the NR capacitor C119 is 10 nF, within TI's 0.01 µF limit, with a footprint but no dielectric or part number. Its output capacitance is 1 × 10 µF and 100 nF, above TI's 2 µF minimum before DC-bias derating; derating not checked (see 4.3). | Affects sensor supply noise, start-up and the power budget. | Human owner / P0, P2 |
| OPEN-012 | Closed 2026-10-31. Path from `+VIN` to `+5V`: TPS259251DRC eFuse, current-limit target 2 A (DEC-026), wired (4.3). Checked against TI SLVSCQ3B through NotebookLM (notebook `TPS25925x eFuse`; CMP-008, 4.7): 45.3 kΩ gives 1.75 / 2.1 / 2.45 A; 6.1 V overvoltage clamp; thermal auto-retry; 1 nF gives about 5 ms ramp; turn-on at the internal 4.3 V UVLO. Moved to OPEN-006: reverse current when USB drives `+5V`, and the limit against the 5 V loads and the 2 A source. | Values set; the open parts are tracked in OPEN-006. | Closed |
| OPEN-013 | Sensor library starting points (see 4.6 "Library state"): pin maps match the datasheet tables, but pin 1 corner, pad geometry and land patterns are not checked against the datasheet drawings and app notes. The IST8310 uses the stock KiCad symbol and `LGA-16_3x3mm_P0.5mm` footprint; its datasheet has no land pattern, so the fit is `ESTIMATED`. The Bosch LGA-10 pads follow the BMP581 land pattern (Fig. 32, read from an image) since 2026-10-21. | A wrong land pattern or orientation reaches the PCB. | Human owner / P2 |
| OPEN-014 | Closed 2026-10-24: BMP581 accepted by the team as barometer 2, BMP384 fallback (DEC-010). Fallback fit: OPEN-019. | Affects footprint, I2C address plan, power budget, PX4 driver and sourcing. | Closed |
| OPEN-015 | Closed 2026-10-24 by DEC-017: the IO MCU is an STM32F100C8T6B with a 24 MHz crystal, so stock px4io-v2 runs unchanged. Background: stock px4io-v2 uses a 24 MHz HSE directly (PX4 v1.16.2 `boards/px4/io-v2/nuttx-config/include/board.h`); the STM32F103 crystal oscillator is specified for 4 to 16 MHz (DS5319 Rev 20 Table 22, NotebookLM source fulltext). | No custom px4io image needed. The F100 takes a 24 MHz crystal (OPEN-020). | Closed |
| OPEN-016 | Closed 2026-10-24: the team answered every row (decisions file section 3); applied in rev 0.11. | - | Closed |
| OPEN-017 | Motor stop on an H743 hang (SAF-015) relies on the ESC stopping when DShot frames stop. The team design now uses 4 × Hobbywing Skywalker 80A V2. No source found says it supports DShot; reseller pages describe PWM input only (`NOT_VERIFIED`). With PWM, the H743 timer keeps sending the last pulse after a CPU hang, so the ESC may never see signal loss (`ASSUMED`). Hobbywing Skywalker manuals (search snippets, model not matched to the 80A V2, `NOT_VERIFIED`) give a PWM throttle range of 1100 to 1940 µs and an output cut after 0.25 s of signal loss. These conflict with FUN-002 and SAF-015; asked in REF-09 D13. Signal-loss behavior and timeout are `NOT_VERIFIED`. No H743 IWDG in PX4 v1.16.2 (team, not checked by hardware). The team's answer covers a full CPU hang, not a partial software stall. | If the ESC holds its last command, a hang leaves the motors running. | Team + Hardware / P4: halt the H743 over SWD while armed on the bench |
| OPEN-018 | PWM pull-down value. Every PWM line gets a weak pull-down (team, Q10). The motor lines carry bidirectional DShot, where the line idles high and the ESC replies on the same wire; the value and any series resistor must not upset that. | Wrong value can break RPM feedback or boot-time output state. | Hardware / P2, then bench test |
| OPEN-019 | BMP384 fallback for barometer 2 (DEC-010). Footprint and pinout against the BMP581 not checked. Address 0x76 (SDO low), the PX4 `bmp388` driver default (team, pinmap review Q22); it does not clash with the I2C2 devices (0x63, 0x0E, 0x46). | A fallback that does not fit the BMP581 footprint needs a board change. | Hardware / P0, before PCB placement |
| OPEN-020 | Closed 2026-10-24. STM32F100C8T6B datasheet checked (ST DocID16455 Rev 9, NotebookLM source fulltext): HSE crystal 4 to 24 MHz (Table 21); VDD 2 to 3.6 V and fHCLK up to 24 MHz (Table 8); POR/PDR and PVD levels (Table 10, recorded in the power budget); PA0 to PA7, PB0, PB1 and PB5 are not 5 V tolerant (Table 4, pin allocation F-03). Crystal load capacitors stay with P1-014. | - | Closed |
| OPEN-021 | On-board servo bus (DEC-019). The UBEC input + and GND pins carry the total servo current, up to 10 A continuous and 15 A peak (PWR-011). One 2.54 mm header pin is usually rated about 3 A (`ESTIMATED`; header not chosen, rating NOT_VERIFIED). The UBEC input is a board-mount XT30 (human owner, 2026-10-24). Open: XT30 rating against 10 A continuous and 15 A peak (NOT_VERIFIED), 6 V and servo GND copper width, where the servo GND joins the logic GND (keep servo current away from the sensors), bulk capacitance, and back-feed into the 5 V side. | An overloaded input pin heats and drops voltage; servo current in the logic GND adds noise near the sensors. | Hardware / P2, P3 |
| OPEN-022 | Closed 2026-10-24: ESC current sense and telemetry dropped (IF-052, IF-053 removed). | - | Closed |
| OPEN-023 | External connector pinouts. The Pixhawk connector standard (DS-009) is not read; every JST-GH pinout is `NOT_VERIFIED`. GPS1 10-pin: whether it has 3.3 V and buzzer pins, and if TIM3_CH3 drives the buzzer pin. PM02D: the board connector will match the PM02D cable, a 6-pin 2.00 mm CLIK-Mate (human owner, 2026-10-24; cable type from the team and PX4 docs, not checked by hardware). The power sheet still draws a 6-pin JST-GH (`SM06B-GHS-TB`) and needs a schematic change (re-checked 2026-10-31, after the human owner declared the sheet complete). Confirm with the team's plug photo (REF-09 parts). I2C4: if the airspeed module or PM02D pulls up to 5 V, PD12 and PD13 must be 5 V tolerant (not checked). | A wrong pinout or connector means new cables or a board change. | Hardware / P1, P2 |
| OPEN-024 | Closed 2026-11-02. Power mux source priority and switchover (DEC-029): PM02D priority through the PR1 divider (DEC-031), the XCOMP fast switchover with a 16.5 kΩ / 5 kΩ CP2 divider from `VBUS` (DEC-032), R105 fitted by default (DEC-033) and R101 12.1 kΩ, so the worst-case switch point is 4.44 V, below the 4.5 V input minimum (DEC-034; 4.7, `ESTIMATED`). | Values set; bench test of the switchover stays with P2-020. | Closed |
| OPEN-025 | Power mux status LED, drawn on 2026-11-03 and not decided: Q101 DMG1012UW, gate on `PMUX_ST`, switches D103 LTST-C191GKT from `+5V` (4.3). It was removed on 2026-11-01 with ST tied to `GND` (rev 0.21). Open: keep it or not; Q101 threshold and VGS rating against the `+5V` gate drive (no datasheet checked); the ST pull-up against TI's 6 to 20 kΩ (CMP-008) and the LED current, which depend on resistor values the human owner decides later; D103 and D104 MFR and MFR.P/N fields swapped. | A VGS rating close to 5 V leaves little margin, because `+5V` follows the input up to the OV trip (4.7). Swapped fields reach the BOM. | Human owner / P2 (P2-019) |

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
| 0.12     | 2026-10-24 | Applied the team's pinmap review 0.3 answers (REF-07). Changed the IO MCU from STM32F103C8T6 to STM32F100C8T6B with a 24 MHz crystal and stock px4io, following the team (DEC-002, DEC-017, MCU-002, CMP-002); no pin moves. The px4io bootloader needs no rebuild. Renamed F103 to F100 in the current rows. Recorded the fitted px4io LEDs and the PA10 and PB11 pull-ups (3.5) and the BMP384 address 0x76 (OPEN-019). Added and closed OPEN-020 (F100 datasheet checks, DocID16455 Rev 9). Added REF-09 (integration questions to the team). | Human owner (team answers) |
| 0.13     | 2026-10-24 | Applied the team's answers to the integration questions (REF-09 rev 0.2). Added DEC-019 (8 × 3-pin servo headers with an on-board 6 V bus and the UBEC in one header, chosen by the human owner instead of the team's D8 option (b)), DEC-020 (environment), DEC-021 (GPS1 10-pin full port, safety switch disabled in use, buzzer kept), DEC-022 (stock px4io image, no IMU heater) and DEC-023 (PC1 kept for an analog power module; ESC current on another ADC pin). Recorded the D9 mounting proposal in MEC-002 to MEC-004 without a decision. Updated PWR-002, PWR-011, the operating scenarios, IF-010 to IF-012, IF-014, IF-015, IF-017, IF-022, IF-040, IF-046, IF-048 to IF-050, section 3.5, ENV-001 to ENV-004, SAF-013, 4.3, 4.7, TST-005, OPEN-006, OPEN-007 and OPEN-009. Added IF-052 (ESC current sense) and IF-053 (ESC telemetry), and OPEN-021 to OPEN-023. | Human owner (team answers) |
| 0.14     | 2026-10-24 | Recorded the human owner's answers to the REF-09 rev 0.3 follow-up questions: mounting, tray, edges and part height (MEC-002 to MEC-004, OPEN-009); USB feeds all 5 V ports (IF-022, OPEN-006); team parts: 4 × Skywalker 80A V2 ESCs, 4 × RDS3235 tilt servos, Kingmax C507 and DS-843MG servos, 10 A UBEC with XT30, MS4525DO (PWR-011, IF-014, IF-040, the servo rail current row, OPEN-007, OPEN-021). Recorded the ESC conflict with FUN-002 and SAF-015 in OPEN-017; FUN-002 unchanged until the team answers D13. ESC connector: 4 × 3-pin with the + pin removed (IF-040). Removed IF-052 and IF-053 (no ESC current sense or telemetry) and closed OPEN-022; noted in DEC-023. UBEC input changed to a board-mount XT30 (DEC-019, PWR-002, PWR-011, the servo output notes, the power tree notes, OPEN-021). PM02D board connector to match its CLIK-Mate cable (IF-048, OPEN-023). Added DEC-024: TPS16412DRC eFuse between the PM02D and `+5V`, 1.5 A limit (part-number boundary, 4.3, OPEN-012). | Human owner |
| 0.15     | 2026-10-26 | Consistency pass, no new decisions and no KiCad file read. Added CMP-008 for the DEC-024 eFuse and named it in OPEN-010 and the verdict. Brought older text in line with rev 0.14: the UBEC XT30 in DEC-019 and the power-input scenario, USB feeding all 5 V ports in the USB-only scenario, the Skywalker ESCs in the DEC-016 notes, and the out-of-scope part list (1.2). Set REF-04 to checklist rev 0.14. Recorded that the README and CHANGELOG disagree with the 4.3 schematic-state table (part count, DF2S6.2CT); not re-checked. | Pending human review |
| 0.16     | 2026-10-26 | Added DEC-025: `+3V3A` feeds only the 2 IMUs, on VDD and VDDIO. Updated the IMU subsystem row (4.2), the power architecture (4.3), the `+3V3A` LDO row and OPEN-011 (LDO part, load, SPI level match and power-up order still open). No KiCad file read. | Human owner |
| 0.17     | 2026-10-28 | No new decisions. Re-checked the saved `power_supplies.kicad_sch` with `sch-inspect` and rewrote the 4.3 schematic-state table: 28 parts, DF2S6.2CT gone, eFuse wired except EN/~SHDN, six eFuse part values still `?`, ferrite bead and `+5V_BUCK` node before the buck, new LDO capacitors, red fault LED on ~FLT, copied MPN and LCSC fields. Updated OPEN-011 and OPEN-012. | Pending human review |
| 0.18     | 2026-10-29 | Added DEC-026: TPS259251DRC eFuse with a 2 A current-limit target replaces the TPS16412DRC of DEC-024 (DEC-024 marked superseded). Updated the part-number boundary, 4.3, CMP-008, OPEN-010, OPEN-012 and the verdict. Re-checked the saved `power_supplies.kicad_sch` with `sch-inspect` and rewrote the 4.3 schematic-state table: 29 parts; eFuse wired with EN/UVLO, ILIM and dV/dT parts; fault LED gone; 0.33 µH inductor in place of the ferrite bead before the buck; 3.3 µH PCR0420 buck inductor (listed in TI Table 9-2); TPS62142 AVIN 100 nF and LDO NR 10 nF now drawn. Updated OPEN-011. Set REF-04 to checklist rev 0.17. | Human owner |
| 0.19     | 2026-10-31 | Added DEC-027 (TPS73533DRBR as the `+3V3A` LDO, CMP-009) and DEC-028 (C111 SS/TR 10 nF, about 5 ms). The human owner declared the power sheet capture complete ("I'am done with power supplies sch"). Re-checked the saved `power_supplies.kicad_sch` with `sch-inspect` and rewrote the 4.3 schematic-state table: 31 parts, now annotated; every part has a footprint; PG pull-up R103 and `5V_PG` hierarchical label added; SS/TR now 10 nF by value (3.3 nF by MPN); one 10 µF fewer on `+3V3A`, one more on each of `+5V` and `+5V_BUCK`; the `+VIN` label is gone. Recorded the TPS259251DRC data from TI SLVSCQ3B (NotebookLM notebook `TPS25925x eFuse`) in CMP-008 and two new 4.7 rows (eFuse settings, buck soft-start). Updated the part-number boundary, OPEN-010 (passive MFR and MFR.P/N chosen later by the human owner) and OPEN-011. Closed OPEN-012 and moved reverse current and the 5 V budget into OPEN-006. Updated 4.3 and OPEN-023. Set REF-04 to checklist rev 0.18. | Pending human review |
| 0.20     | 2026-10-31 | No new decisions. Corrected rev 0.19, which was written from the saved sheet before the human owner's last save: the TPS62142 PG net now has local label `3V3_PG` and hierarchical label `3V3_DONE` (named apart on purpose; no sheet pin on `top_hierarchical` yet), and C111 is 0402 with empty MFR.P/N and LCSC, so the 3.3 nF part-number mismatch is gone. Updated 4.3, the 4.7 soft-start row and the DEC-028 notes. Set REF-04 to checklist rev 0.19. | Pending human review |
| 0.21     | 2026-11-01 | Added DEC-029 (TPS2121 power mux replaces the TPS259251DRC eFuse; DEC-026 superseded), DEC-030 (power mux current limit 1.5 A) DEC-031 (PM02D priority through a 13.7 kΩ / 5 kΩ PR1 divider, drawn the same day; the ST status LED was removed and ST tied to `GND`) and DEC-032 (XCOMP fast switchover with a 16.5 kΩ / 5 kΩ CP2 divider from `VBUS`, the 16.5 kΩ as a DNP option for the VREF mode, and PR1 changed to 12.4 kΩ; drawn in the 02:49 save, R105 marked DNP). Rewrote CMP-008 for the TPS2121 from TI SLVSEA3F (NotebookLM notebook `TPS212x ...`, added by the human owner) and replaced the 4.7 eFuse row with a power mux row. Re-read the saved `power_supplies.kicad_sch` from a `kicad-cli` netlist export and rewrote the 4.3 schematic-state table: 41 parts, references renumbered, input net `PM02_5V`, USB `VBUS` on mux IN2, TVS and I2C ESD on the PM02D input, ST status LED, `3V3_DONE` sheet pin added, 2 unannotated DNP diodes. Added the power mux library part note (4.3) and OPEN-024 (priority mode). Updated the part-number boundary, 4.3, the 4.7 soft-start row, OPEN-006 (back-feed concern gone), OPEN-010, OPEN-011 and the verdict. Set REF-04 to checklist rev 0.20. | Human owner |
| 0.22     | 2026-11-02 | Added DEC-033: R105 (CP2 16.5 kΩ) fitted by default, so the power mux runs in XCOMP mode. Re-read the saved `power_supplies.kicad_sch` (00:11 save, 2026-11-02; diff against `HEAD` and a `kicad-cli` netlist export): R105 no longer DNP, R106 and its `GND` symbol moved with no net change, XCOMP and OV text notes rewritten; 43 parts as before. The 2 unannotated `D?` diodes are ESD parts parked for another sheet (human owner), so they are no longer a finding (P2-019). Narrowed OPEN-024 to the switch-point tolerance and replaced the 4.39 V worst case in 4.7 with 4.52 V, which adds 1 % resistor tolerance (`ESTIMATED`). Updated 4.3, 4.7, DEC-032 notes and the verdict. Set REF-04 to checklist rev 0.21. | Human owner |
| 0.23     | 2026-11-02 | Added DEC-034: R101 12.1 kΩ (was 12.4 kΩ), so the worst-case XCOMP switch point is 4.44 V, below the 4.5 V input minimum. Closed OPEN-024. Re-read the saved `power_supplies.kicad_sch` (00:32 save; diff against `HEAD`: R101 value and the PR1 notes only, no net change). Updated 4.3, the 4.7 power mux row (PR1 ratio 3.42; XCOMP 3.78 / 3.98 / 4.18 V; VREF mode 3.39 to 3.76 V), DEC-031 and DEC-033 notes and the verdict. Set REF-04 to checklist rev 0.22. | Human owner |
| 0.24     | 2026-11-03 | No new decisions. Re-read the saved `power_supplies.kicad_sch` (13:24 save, 2026-11-03; diff against `HEAD` and `sch-inspect`): 47 parts, 45 annotated. The power mux ST status LED is drawn again (Q101 DMG1012UW, D103 LTST-C191GKT), so ST is no longer tied to `GND`; added OPEN-025. D104 Value is now LTST-C191GKT. Part fields added to Q101, D103, D104, C105, C112 and C119; on D103 and D104 the MFR and MFR.P/N fields are swapped. Resistors were renumbered and some values changed; the human owner will decide the resistor fields later, so resistor references and values in 4.3 and 4.7 are not updated. Title blocks set to revision `A` with a `STATUS` text variable `DRAFT`. New library symbol `0_Transistor_FET:DMG1012UW`. Updated 4.3, the 4.7 soft-start row and the verdict. Set REF-04 to checklist rev 0.23. | Pending human review |

## Current verdict

**Draft only. NOT_VERIFIED and NOT FOR FABRICATION.**

The specification is structured enough for schematic capture against the agreed pinmap (REF-07). It does not approve any non-MCU part number other than the sensors (DEC-008, DEC-010, DEC-011), the main 3.3 V buck (DEC-012), the 5 V power mux (DEC-029) and the `+3V3A` LDO (DEC-027), nor power protection or rail detail, safety timing, schematic, PCB, or fabrication release. Sensor lifecycle and sourcing risks are open (OPEN-004): ICP-20100 is EOL, BMP581 stock is short, and the IST8310 lifecycle is not confirmed. Motor stop on an H743 hang depends on the ESC (OPEN-017). The PWM pull-down value must suit bidirectional DShot (OPEN-018). All servo current now passes through the board (DEC-019); the UBEC input rating and the servo bus copper are open (OPEN-021). The external connector pinouts (OPEN-023) are open, and the mounting is still a proposal (OPEN-009). The sensor library parts are starting points: their pin maps match the datasheet tables, but land patterns and pin 1 orientation are not checked (OPEN-013). The power sheet capture is declared complete by the human owner (2026-10-31), and its 5 V input changed to the TPS2121 power mux on 2026-11-01 (DEC-029, DEC-030), but it is not reviewed and ERC has not run. The power mux status LED is drawn again and not decided (OPEN-025); its findings (P2-019), the 5 V budget under the 1.5 A limit (OPEN-006), the `+3V3A` load and IMU level match (OPEN-011) and the PM02D connector (OPEN-023) are open.
