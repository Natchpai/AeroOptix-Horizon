---
name: hardware-specification
description: >-
  Gathers, refines and documents hardware and PCB requirements with beginner
  and general specification templates. Use when the user asks to collect
  stakeholder needs, draft or update a hardware specification, turn beginner
  requirements into an engineering spec, or analyze requirements and PCB
  constraints. Not for task tracking.
argument-hint: "beginner | general | translate | update"
---

# Hardware Specification

Turn what the user knows into a specification, one step at a time, using only confirmed information.

## Templates

- **Beginner:** `assets/beginner_requirements_template.md`. For non-engineers, stakeholders or beginners. Plain language, no circuit knowledge needed, unknown answers allowed.
- **General:** `assets/GENERAL_HARDWARE_SPEC_TEMPLATE.md`. Engineering requirements for hardware and PCB design. Match the depth to the project; not every section has to be filled.

Load only the template the mode needs; load both only to translate or compare. A template is a structure to adapt, not a checklist to complete. Leave the template files unchanged during normal work.

## Modes

Pick the mode from `$ARGUMENTS` or the request. If unclear, ask.

- **Beginner:** collect intended use, functions, operating environment, available power, interfaces, size, quantity, budget and constraints in plain language. Accept unknown answers.
- **General:** write measurable functional, electrical, interface, PCB, mechanical and manufacturing requirements from confirmed information.
- **Translate:** turn beginner requirements into an engineering specification. Keep the user's intent and where each fact came from. Carry over confirmed information, mark open values `TBD`, and flag proposals that need human confirmation.
- **Update:** read the existing specification first. Change only the sections the user authorized, keep requirement IDs and unrelated content, and report conflicts for the human to resolve.

## Procedure

1. Get the project purpose, scope, intended use and constraints from the user or from project data you may read.
2. Pick the template and ask for the most important missing facts.
3. Keep user needs, confirmed requirements, assumptions, proposed implementations and verification results apart.
4. Put confirmed information in the right sections. Never invent a requirement to fill a gap.
5. List conflicts, ambiguities and open requirements. Values and approvals come from the human.
6. Write or update the file only when the user asks. Keep existing requirement IDs, values, units, tolerances, constraints and unrelated content.
7. Keep the specification as large as the project's real requirements, no larger.

## Requirements Quality

- Use `shall` for confirmed mandatory requirements, `should` for preferences, and `may` for optional capabilities.
- Assign stable unique IDs to engineering requirements when useful.
- Include units, tolerances, operating conditions, and verification criteria where relevant.
- Use `TBD` for unresolved requirements and `NOT_VERIFIED` for claims lacking sufficient evidence.
- Distinguish design targets from measured or verified results.
- ERC/DRC results or file presence do not establish design correctness or approval.

## Keep It Short

- Define the status defaults once in a conventions block at the top (for example: every requirement is `NOT_VERIFIED` unless stated, and `TBD` means open). Do not repeat `NOT_VERIFIED` or `TBD` in every row when a default covers it.
- State each fact once. A requirement lives in one place. Other sections refer to it by ID (for example "see PWR-001"). Do not repeat the same value in the register, the topic tables, the architecture text, and the decisions.
- Put each numeric limit in one topic table (for example the electrical table). The register and the decisions table refer to it by ID. Decisions keep the topic, the date, and the owner, not a second copy of the value.
- Keep tables and their template columns, even when cells are `TBD`. Do not replace a table with a sentence or a list.
- Do not fill a template table with placeholder rows. Add rows only for real requirements.
- Table format: pad the first column of every table to the width of its longest cell (header included), so the source lines up. Match the dashes in the separator row to that width. Leave the other columns unpadded.
- Remove template sections that do not apply. Fold the verification plan into the Verification column when it would only repeat it.
- Do not copy usage notes, template guidance, or maintainer comments into the specification.

## Writing Style

- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences, and active voice.
- Avoid fancy words, marketing phrases, and AI-style filler.
- Keep standard engineering terms and exact identifiers. Do not simplify a term if it loses accuracy.
- Do not use the em dash (`—`). Use a period, comma, colon, or parentheses.
- Use `TBD` for open values. Do not mix it with other spellings such as "TO BE DECIDED".
- Do not reword existing text that is already clear and correct.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Boundaries

- Never open or read a PDF. Datasheet values come from the user, official manufacturer web pages, or NotebookLM answers with cited text, used only after the user approves uploading the file. If the project has `.claude/rules/engineering.md`, follow its "Datasheet evidence" section.
- KiCad design and library files are read-only.
- The project phase (`DRAFT`, `PRELIMINARY`, `CHECK`, `RELEASE`) is declared by the human; a specification never sets or changes it.
- Electrical specs, component ratings, manufacturing capabilities and test results come from the user or a cited source. Without one, write `TBD` or `NOT_VERIFIED`.
- Architecture, components, suppliers, PCB stackup and fabrication process come from the requirements, not from a default.
- Write only the specification file asked for: no extra logs, manifests, reports, skills, scripts or Git actions.

## Output

- Suggested names: `HARDWARE_BRIEF.md` (beginner stakeholder requirements) and `HARDWARE_SPEC.md` (general engineering specification). An existing project name wins.
- Report the file written, the sections added or changed, and the open `TBD` items and conflicts.
- Optional companion: `hardware-checklist`, if installed, tracks work and evidence against the specification.
