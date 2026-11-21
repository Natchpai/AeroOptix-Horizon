# Workflow

How a KiCad hardware project moves through its phases and keeps its design
records. It fits a sub-complex board: one spec, one checklist, a few design
records, a README and a CHANGELOG. A project may turn a part off in its own
`CLAUDE.md` (for example "no team-messages file").

This rule does not authorize design changes, engineering release-document
generation, verification or release actions. Human engineers decide and
declare every phase transition. Design authority and evidence labels are in
`engineering.md`; Git actions in `git-workflow.md`.

## Phases

### DRAFT
Schematic capture is in progress. PCB work is not yet part of the active
project scope.

### PRELIMINARY
The schematic is nearly complete and PCB work has started. The human may
generate schematic and PCB documents for review, but ERC and DRC are not
required phase gates.

### CHECK
The schematic and PCB are mostly finalized. The human generates the required
documents and performs ERC and DRC for the selected saved baseline. Results,
open violations, and accepted exceptions remain subject to human review.

### RELEASE
An approved CHECK baseline is published as a release. It must use the same
checked source baseline unless the human explicitly reopens CHECK. Creating a
tag or GitHub release remains a separate, explicitly approved Git action.

## Evidence and authority
- A phase is never inferred from file counts, document presence, ERC/DRC
  output, or Git status. The human engineer declares the phase.
- ERC and DRC are verification evidence, not proof that a design is correct,
  safe, manufacturable, or approved. Evidence labels and design authority
  rules are in `engineering.md`.
- A change to the checked source, design rules, libraries, or required release
  inputs reopens CHECK until the human establishes a new checked baseline.
- Phases do not prescribe branch names, release assets or manufacturing
  deliverables. The usual branch and PR steps are in Doc cycle.

## Documentation boundary
- Engineering release-document generation and visual/content review are
  human-only actions.
- Claude may create or update project-level Markdown documentation only when
  explicitly requested. Markdown documentation does not declare or advance a
  project phase unless a human explicitly states that phase.
- PDFs (reading, report generation, datasheets) follow `pdf.md`.
- When explicitly asked, Claude may check only the expected document file
  names and paths, and must report that result as `EXISTS`, `MISSING`, or
  `NOT_VERIFIED`; file presence does not verify document content.
- Detailed verification procedures belong in dedicated Skills, not this rule.

## Records and IDs
- The **specification** owns requirement IDs (`PWR-`, `IF-`, `SEN-`, ...),
  decisions (`DEC-xxx`) and open items (`OPEN-xxx`). Read it before proposing
  a design change. New rows take the next unused ID; an ID is never reused.
- Its change-note table is the design history: one row per revision, at most
  one open revision per commit (see `progress-update`).
- The **checklist** holds gates (P0 to Pn) and tasks (`Pn-xxx`). Each open
  item in the spec names the active task that closes it. A task cell holds
  the statement, the current state and `Left:`; history goes to the spec
  change-note.
- Other records (power budget, pin allocation, selection notes) own their
  values and cite spec IDs. The README and CHANGELOG point to spec IDs and
  revisions; they do not copy decision or open-item text.

## Doc cycle
1. The human decides; Claude records only what the human stated (quoted) as a
   decision, and what is drawn but not decided as "drawn, not decided" with
   an open item.
2. `/progress-update light` after decisions or drawing changes in DRAFT or
   PRELIMINARY (spec and checklist only).
3. `/progress-update sync` before a commit (design records, README, one
   CHANGELOG pointer line per spec revision). In CHECK and RELEASE, run full
   mode.
4. Commit on the working branch and open a PR to the default branch, each Git
   step with the human's approval.

## Team messages (optional)
If the project `CLAUDE.md` names a team-messages file, read it at the start of
a session and tell the user about any note that affects the task or conflicts
with the spec. A note is team context, not approval; the spec still owns
`DEC-xxx` and `OPEN-xxx`. Edit the file only when asked, except to remove an
item that is done, answered, or recorded elsewhere; tell the user what was
removed.

## Open checks
When an item is `NOT_VERIFIED` or "not checked" and an allowed source can
settle it (saved design files, an existing NotebookLM notebook, an official
manufacturer or distributor product page), run the check instead of only
reporting it as open, then offer to record the result. Still ask first where
a rule needs approval (adding a NotebookLM source, a design change), and leave
design choices, such as accepting a margin, to the human.
