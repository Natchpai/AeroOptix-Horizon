# Hardware Workflow

This rule defines a lightweight phase language for KiCad hardware projects.
It does not authorize design changes, engineering release-document generation,
verification, or release actions. Human engineers decide and declare every
phase transition.

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
  safe, manufacturable, or approved.
- A change to the checked source, design rules, libraries, or required release
  inputs reopens CHECK until the human establishes a new checked baseline.
- This workflow does not prescribe branch names, pull-request flow, release
  assets, or manufacturing deliverables.

## Documentation boundary
- Engineering release-document generation and visual/content review are
  human-only actions.
- Claude may create or update project-level Markdown documentation only when
  explicitly requested. Markdown documentation does not declare or advance a
  project phase unless a human explicitly states that phase.
- Claude must not generate, open, read, parse, or assess PDF documents.
- When explicitly asked, Claude may check only the expected document file
  names and paths, and must report that result as `EXISTS`, `MISSING`, or
  `NOT_VERIFIED`; file presence does not verify document content.
- Detailed verification procedures belong in dedicated Skills, not this rule.
