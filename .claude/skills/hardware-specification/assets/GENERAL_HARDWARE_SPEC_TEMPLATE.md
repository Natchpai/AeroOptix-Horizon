# Hardware Design Specification : [Project Name]

> **Template guidance:** This is a reusable engineering specification, not a completed design or approval record. Replace bracketed prompts with confirmed information. Remove sections that do not apply; do not invent values. Keep requirements distinct from design decisions, assumptions, and verification results.

| Property          | Value |
| ----------------- |---|
| Project           | [Project name] |
| Document owner    | [Human engineer / team] |
| Document revision | [e.g., 0.1] |
| Last updated      | [YYYY-MM-DD, when confirmed] |
| Design tool       | [e.g., KiCad 10] |
| Hardware phase    | [Only if explicitly declared by the human: DRAFT / PRELIMINARY / CHECK / RELEASE] |
| Related baseline  | [Commit/revision or Not established] |

## 1. Project Definition

### 1.1 Purpose and application
[What the hardware does, who/what uses it, and why it is needed.]

### 1.2 Scope
**In scope:** bullet of [Functions and deliverables covered by this specification.]

**Out of scope:** bullet of [Functions, software, mechanical systems, certification, etc. not covered.]

### 1.3 Operating scenarios
[Normal operation, start-up/shutdown, hot-plug, loss of supply, fault recovery, service/debug, and any other applicable use cases.]

### 1.4 Terminology and references
| Reference | Document / URL | Revision / date | Purpose |
| --------- |---|---|---|
| REF-01    | [Source] | [Revision] | [Relevant requirement or design basis] |

## 2. Requirements Management

### 2.1 Writing rules
- Use **shall** for mandatory requirements, **should** for design preferences, and **may** for optional capabilities.
- Assign a stable, unique requirement ID; never reuse an ID after removal.
- State measurable thresholds, ranges, conditions, units, tolerances, and verification method where applicable.
- Separate **required behavior** from **implementation choices** (e.g., “shall provide USB device connectivity” versus “use connector X”).
- Record unknowns as **TBD** (decision needed) or **NOT_VERIFIED** (evidence unavailable), not as assumed facts.
- Design targets are not measured results. ERC/DRC and file presence alone do not establish hardware correctness.

### 2.2 Requirement register
Maintain entries in relevant sections below; use this table as a compact cross-reference if helpful.

| ID      | Requirement (shall) | Conditions / limits | Verification method | Status / source |
| ------- |---|---|---|---|
| SYS-001 | [System shall ...] | [Condition] | Analysis / Inspection / Test / Demonstration | TBD / [REF] |

**ID prefixes (suggested):** `SYS` System, `PWR` Power, `FUN` Functional, `IF` Interface, `SAF` Safety/Protection, `ENV` Environment, `CMP` Components, `PCB` PCB, `MEC` Mechanical, `MFG` Manufacturing, `TST` Testability. Only create IDs that are used.

## 3. System Requirements

### 3.1 Functional requirements
| ID      | Function / required behavior | Operating condition | Verification |
| ------- |---|---|---|
| FUN-001 | [System shall perform ...] | [When / mode] | [Method] |

### 3.2 Operating modes and state behavior
| Mode                             | Entry condition | Required behavior | Exit / fault behavior |
| -------------------------------- |---|---|---|
| [Normal / Sleep / Reset / Fault] | [Condition] | [Behavior] | [Condition] |

### 3.3 Electrical system requirements
| ID      | Parameter | Minimum | Nominal | Maximum | Unit | Conditions / note |
| ------- |---|---:|---:|---:|---|---|
| PWR-001 | [Input supply voltage] | [TBD] | [TBD] | [TBD] | V | [At connector / transient handling] |
| PWR-002 | [Power / current demand] | [TBD] | [TBD] | [TBD] | [W/A] | [Continuous / peak, duty cycle] |
| PWR-003 | [Output / rail tolerance] | [TBD] | [TBD] | [TBD] | [V/%] | [Load / temperature] |

[Add ripple, noise, accuracy, efficiency, timing, load-step, clock stability, etc., only when applicable.]

### 3.4 External interfaces
| ID     | Interface / connector | Function | Direction | Electrical levels | Protocol / rate | Protection / constraints |
| ------ |---|---|---|---|---|---|
| IF-001 | [Interface] | [Purpose] | [In/Out/Bidirectional] | [TBD] | [TBD] | [ESD, cable, termination, etc.] |

### 3.5 Environmental and reliability requirements
| ID      | Parameter / condition | Required range or limit | Verification |
| ------- |---|---|---|
| ENV-001 | [Ambient temperature] | [TBD] | [Analysis / Test] |

[Consider humidity, vibration, ingress, cooling, altitude, ESD/EMC expectations, lifetime and maintenance only if relevant. Applicable regulatory or safety standards must be explicitly identified and verified, not guessed.]

### 3.6 Protection and fault behavior
| ID      | Hazard / fault | Required response | Recovery method | Verification |
| ------- |---|---|---|---|
| SAF-001 | [Overvoltage / reverse polarity / short / ESD / thermal] | [TBD] | [TBD] | [Method] |

## 4. Hardware Architecture and Design Constraints

### 4.1 Functional block diagram
[Link to an existing image or give a concise text description. Do not create a diagram unless requested.]

### 4.2 Functional blocks
| Block   | Role | Inputs / outputs | Dependencies | Key constraints |
| ------- |---|---|---|---|
| [Block] | [Purpose] | [Signals/rails] | [Other block] | [Limits] |

### 4.3 Power architecture
[Power tree, rail dependencies, input selection, power-up/down sequencing, isolation/grounding strategy, transient and fault management. Omit non-applicable parts.]

### 4.4 Clock, reset, boot and programming
[Clock sources, reset behavior, boot mode, debug/flash connectors, start-up constraints. Optional for projects without programmable devices.]

### 4.5 Control, sensing, analog and digital considerations
[Accuracy, ADC/DAC resolution, sensors, filtering, synchronization, signal levels, isolation, timing and digital latency as applicable.]

### 4.6 Component selection constraints
| ID      | Category / function | Mandatory constraints | Preferred constraints | Sourcing / lifecycle |
| ------- |---|---|---|---|
| CMP-001 | [Component class] | [Electrical rating, package or tolerance] | [Optional preference] | [Approved distributors / stock / lifecycle] |

[Record manufacturer part numbers only when selected or mandated. Confirm pinout, footprint, thermal ratings and orderable variant against source documents.]

### 4.7 Engineering calculations and margins
| Analysis                                        | Inputs / operating corner | Method / reference | Result | Margin / open questions |
| ----------------------------------------------- |---|---|---|---|
| [Thermal / loss / ripple / current / impedance] | [TBD] | [Equation / reference] | [TBD] | [TBD] |

## 5. PCB Design Specification

### 5.1 Mechanical envelope
| ID      | Item | Requirement / limit | Verification |
| ------- |---|---|---|
| MEC-001 | [Board outline / mounting / height / keepout] | [TBD] | [Inspection / measurement] |

### 5.2 Fabrication and stackup
| ID      | Parameter | Requirement / target | Fabricator confirmation |
| ------- |---|---|---|
| PCB-001 | Copper layer count | [TBD] | [TBD] |
| PCB-002 | Stackup / dielectric / copper weight | [TBD] | [TBD] |
| PCB-003 | Minimum trace / spacing | [TBD] | [TBD] |
| PCB-004 | Hole / via / annular-ring capability | [TBD] | [TBD] |
| PCB-005 | Soldermask / surface finish | [TBD] | [TBD] |

*Separate board-fabricator absolute capabilities from project-specific design margins.*

### 5.3 Layout and routing constraints
| ID      | Circuit / net class / region | Constraint | Reason | Verification |
| ------- |---|---|---|---|
| PCB-010 | [Critical nets] | [Clearance, width, loop area, length, placement, return path] | [Electrical reason] | [Review / DRC / analysis] |

[Consider switch-node loop, current return, decoupling placement, sensitive analog nets, isolation barriers, clocks, high-speed buses, differential pairs, matched lengths, impedance and reference-plane transitions as applicable.]

### 5.4 Power integrity, signal integrity and EMC
[Identify rails, current paths, voltage drop limits, impedance/timing targets, decoupling strategy, stitching/return-path needs, and EMI mitigation. Avoid claiming compliance from layout rules alone.]

### 5.5 Thermal and current carrying
[Hot components, copper spreading, vias, heatsinks, allowable temperature rise, load profile, thermal model assumptions.]

### 5.6 Design-rule implementation in KiCad
| Specification requirement               | KiCad mechanism, if supported | Manual / external check |
| --------------------------------------- |---|---|
| [Clearance / width / differential pair] | [Board Setup / Net Classes / Custom Rules] | [Inspection / simulation] |

[Do not claim every constraint is enforceable in DRC. Configuration is a design implementation, not the requirement itself.]

## 6. Manufacturing, Assembly and Service

### 6.1 Manufacturability and assembly
| ID      | Requirement | Rationale | Verification |
| ------- |---|---|---|
| MFG-001 | [Assembly/fabrication constraint] | [Reason] | [Fabricator / assembler review] |

[Optional: tooling, fiducials, polarity, placement access, hand assembly, stencil, panelization, connector orientation and rework.]

### 6.2 Debug and testability
| ID      | Signal / function | Access / observation requirement | Method |
| ------- |---|---|---|
| TST-001 | [Rail, debug signal, interface] | [Test point / connector / measurement access] | [Inspection / Test] |

## 7. Verification Plan (Planning Only)

**No automatic gates:** This table plans how each requirement could be checked; it does not declare phase completion, design approval, or release readiness.

| Requirement ID | Verification method | Planned evidence / procedure | Result | Reviewer |
| -------------- |---|---|---|---|
| [ID]           | Analysis / Inspection / Test / Demonstration | [Planned evidence] | NOT_VERIFIED | [Human, when applicable] |

[Record observed results only after verification has actually occurred. Requirements and checks may be updated independently of the human-declared project phase.]

## 8. Design Decisions and Open Items

### 8.1 Decisions
| Decision ID | Topic | Selected option | Alternatives / reasoning | Date / owner |
| ----------- |---|---|---|---|
| DEC-001     | [Topic] | [TBD] | [Tradeoffs] | [When confirmed] |

### 8.2 Open questions and assumptions
| Item     | Description | Impact | Owner / next action |
| -------- |---|---|---|
| OPEN-001 | [Unknown, assumption or dependency] | [Risk / scope] | [Decision needed] |

## 9. Specification Change Notes

| Revision | Date | Description | Human-approved by (if applicable) |
| -------- |---|---|---|
| [0.1]    | [YYYY-MM-DD] | Initial specification draft | [Optional] |

---

## Usage Notes (remove from finalized project specification if preferred)

1. Start with sections **1–3** to establish what the system must do; add hardware and PCB constraints as design knowledge becomes available.
2. Populate **Section 4** with selected architecture and decisions, not invented requirements.
3. Populate **Section 5** once board/fabrication constraints become meaningful; confirm fabrication limits with the chosen manufacturer.
4. Use **TBD** for undefined values; use **NOT_VERIFIED** for unconfirmed claims/results. Do not claim measured performance from targets.
5. Review impact when a requirement changes; human engineers alone declare `DRAFT`, `PRELIMINARY`, `CHECK`, or `RELEASE`.
6. This specification does not authorize design-file edits, documentation exports, Git actions, or release operations.
