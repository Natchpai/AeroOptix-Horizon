# Hardware Project Brief : [Project Name]

> **For project owners and beginners.** Explain what you need the hardware to do, not how to design the circuit. You do not need to know electronics terminology or choose ICs, components, PCB layers, or trace widths. An engineer will translate this brief into a detailed design specification.
>
> **How to fill in:** Replace the brackets with your answers. Write **Don't know** when unsure and **Not needed** when a feature is unnecessary. Examples below are illustrations, **not default specifications**. Only fill in what you know; leave other fields for discussion.

## 1. Project Overview

| Question | Your answer |
|---|---|
| Project name (working name is fine) | [ ] |
| What do you want to build? (1–3 sentences) | [ ] |
| What problem will it solve? | [ ] |
| Who will use it, and where? | [ ] |
| Is this a prototype, personal project, research project, or product? | [ ] |

## 2. What Must It Do?

Describe what a successful device does in everyday language. Focus on outcomes, not parts.

| Importance | Function / expected behavior |
|---|---|
| Must have | [e.g., measure room temperature and send results to a computer] |
| Must have | [ ] |
| Nice to have | [ ] |

**How will you know it is working?** [Describe something you can see, read, or demonstrate.]

## 3. Power and Connections

You can describe the source or device even if you don't know the voltage or connector name.

| Question | Your answer |
|---|---|
| Where will it get power? | [USB / battery / wall adapter / another board / Don't know] |
| Does it need to run from a battery? For how long? | [ ] |
| What will connect to it? | [Computer / sensor / motor / display / network / other] |
| Wired, wireless, or both? | [ ] |
| Any connectors or cables you must use? | [ ] |
| Any required input/output voltage, current, or power already known? | [Value + unit + source, or Don't know] |

## 4. Use Conditions

| Question | Your answer |
|---|---|
| Used indoors, outdoors, or inside another machine? | [ ] |
| Expected usage | [Continuous / occasionally / short bursts / Don't know] |
| Exposure to heat, water, dust, vibration, or electrical noise? | [ ] |
| What should happen if power is lost or something goes wrong? | [ ] |
| Any safety-critical use (medical, vehicle control, high voltage, etc.)? | [ ] |

## 5. Size and Physical Design

| Question | Your answer |
|---|---|
| Maximum board/device size, if known | [Dimensions or Don't know] |
| Must it fit in an existing enclosure? | [Yes / No / Don't know; provide drawing if available] |
| Mounting requirements (holes, location, orientation) | [ ] |
| User-facing parts (buttons, LEDs, screen, switches) | [ ] |
| Preferred shape or appearance | [ ] |

## 6. Constraints and Preferences

| Question | Your answer |
|---|---|
| Budget per board/device (and expected quantity) | [Currency and amount or Don't know] |
| How many units initially? | [ ] |
| Target completion date, if any | [ ] |
| Must-use / must-avoid parts, brands, or suppliers | [Reason, or None] |
| Who will write the software/firmware? | [ ] |
| Who will assemble and test the hardware? | [ ] |
| Any legal, certification, or company requirements already known? | [ ] |

## 7. Existing Materials

- Similar products, reference designs, photos, sketches, or links: [ ]
- Existing boards, sensors, batteries, modules, or equipment you already have: [ ]
- Previous prototypes or problems encountered: [ ]
- Documents or other information to share with the engineer: [ ]

## 8. Priorities and Open Questions

**Pick your top 3 priorities** (examples: low cost, small size, low power, performance, reliability, ease of assembly, repairability):

1. [ ]
2. [ ]
3. [ ]

**Decisions you want the engineer to recommend:** [ ]

**Important unknowns or concerns:** [ ]

## 9. Agreement on Scope

- **In scope:** [What the requested hardware project includes]
- **Out of scope / to be handled separately:** [e.g., enclosure, firmware, mobile app, manufacturing]
- **Desired deliverables:** [e.g., schematic, PCB design files, prototype board, assembly files, or Don't know]

---

## For the Engineer : Follow-up (not required for beginners)

This brief records user needs, **not verified electrical design requirements**. Before designing, the engineer should:

1. Confirm unclear answers and resolve contradictory requirements with the project owner.
2. Translate the intended functions into measurable engineering requirements, with tolerances and operating conditions where relevant.
3. Determine architecture, components, interfaces, PCB constraints, protection, manufacturability, and verification methods.
4. Record assumptions and unresolved decisions explicitly; do not invent missing ratings or specifications.
5. Transfer confirmed requirements into `GENERAL_HARDWARE_SPEC_TEMPLATE.md` (advanced engineering specification). Do not treat examples in this brief as approved design values.

**Owner's confirmation:** [Optional name/date after reviewing the completed brief]
