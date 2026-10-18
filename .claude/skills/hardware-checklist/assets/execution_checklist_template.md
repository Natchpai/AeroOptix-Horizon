# Execution Checklist: [Project Name]

| Property            | Value |
| ------------------- |---|
| Revision            | [e.g., 0.1] |
| Updated             | [YYYY-MM-DD] |
| Requirements source | [Link to the specification] |
| Status              | Active tracker. Not an approval or verification record. |

> **Template guidance:** Replace bracketed text with confirmed information. Remove gates, rows, and columns that do not apply. Do not invent owners, dates, or results. Reference specification IDs. Do not copy their values.

**Conventions**

- Task status: `OPEN`, `IN_PROGRESS`, `BLOCKED BY <ID>`, `DEFERRED`, `DONE`, `N/A`.
- `DONE` needs a stated completion and a named or linked evidence record in the last column.
- A candidate, a count, a file, or an ERC/DRC pass is not evidence by itself.
- Gates are work stages. They are not the project phase. The human declares the project phase.
- `TBD` means to be decided. Owner `Human` means the human engineer decides or approves.

## Gate summary

| Gate | Name | Exit criterion | Status |
| ---- |---|---|---|
| P0   | Requirements | [No open requirement blocks allocation or architecture.] | OPEN |
| P1   | Allocation | [Interfaces, resources, and parts are allocated and reviewed.] | OPEN |
| P2   | Schematic | [Schematic review is closed. No hardware blocker for bring-up.] | OPEN |
| P3   | PCB and release package | [PCB, BOM, and fabrication data are reviewed and approved by the human.] | OPEN |
| P4   | Bring-up | [Repeatable bench evidence exists. Each remaining issue has an owner.] | OPEN |

## P0: Requirements

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P0-001 | [Confirm scope and operating intent.] | [SYS-001] | Human | OPEN | [Decision record] |
| P0-002 | [Select parts that block allocation.] | [CMP-001] | Human | OPEN | [Part selection record] |

## P1: Allocation

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P1-001 | [Assign pins and alternate functions.] | [IF-010] | Hardware | OPEN | [Versioned pin-allocation table] |
| P1-002 | [Check pin, DMA, timer, and clock conflicts.] | [IF-010] | Hardware | OPEN | [Conflict report and resolution record] |
| P1-003 | [Record mapping revision, reviewer, and date.] |  | Human | OPEN | [Attributable review record] |

## P2: Schematic

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P2-001 | [Create the schematic from the P1 allocation.] |  | Hardware | BLOCKED BY P1-003 | [Versioned native schematic] |
| P2-002 | [Run ERC and disposition all relevant findings.] |  | Hardware | OPEN | [ERC output and issue disposition] |
| P2-003 | [Complete line-by-line schematic review.] |  | Human | OPEN | [Review checklist with reviewer and links] |

## P3: PCB and release package

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P3-001 | [Confirm board envelope, mounting, and connector placement.] | [MEC-001] | Human | OPEN | [Mechanical constraint review] |
| P3-002 | [Run DRC and disposition all relevant findings.] |  | Hardware | OPEN | [DRC output and issue disposition] |
| P3-003 | [Confirm BOM, footprints, alternates, and assembly notes.] | [MFG-002] | Hardware | OPEN | [Controlled BOM and assembly review] |
| P3-004 | [Approve fabrication release.] |  | Human | OPEN | [Explicit approval record] |

## P4: Bring-up

| ID     | Task | Req | Owner | Status | Evidence required / link |
| ------ |---|---|---|---|---|
| P4-001 | [Inspect the assembled board.] | [TST-001] | Hardware | OPEN | [Inspection record] |
| P4-002 | [Verify power rails and current before loading firmware.] | [PWR-001] | Hardware | OPEN | [Measured bring-up log] |
| P4-003 | [Record hardware revision, test conditions, measurements, and deviations.] |  | Hardware | OPEN | [Controlled bring-up report] |

## Open items

| ID     | Open item | Spec ref | Owner | Needed by |
| ------ |---|---|---|---|
| OI-001 | [Short title] | [OPEN-001] | [Role] | [Gate] |

## Closure checks

- [ ] Every confirmed requirement has a source or decision record.
- [ ] Every requirement has at least one task, or is marked `N/A` with a reason.
- [ ] Every `DONE` row links to a test, inspection, analysis, or review record.
- [ ] Every `TBD` has an owner, a gate, or an explicit deferred obligation.
- [ ] Release package revisions are traceable to each other.
- [ ] The human provides the final approval for each gate.

## Next action

[One or two sentences: the next task to work on and what blocks it.]
