---
name: project-readme
description: >-
  Creates or updates a concise, general-purpose README for a hardware project
  using confirmed information and explicit user direction.
  Use when the user asks to create, revise, or maintain README.md.
  Does not inspect PDF content, infer engineering facts, or modify KiCad files.
argument-hint: "create | update"
---

# Project README

Create or maintain only project-level Markdown documentation requested by the
user. This skill is independent and does not determine engineering readiness.

## Information boundary
- Use facts supplied by the user, existing Markdown or text documentation, and
  repository file and directory names.
- Do not invent a project title, specifications, architecture, test result,
  phase, approval, or release state.
- Do not derive engineering facts from PDF content or native KiCad design files.
- Keep KiCad files and libraries read-only. Do not create supporting reports,
  images, or documents unless explicitly requested.

## Create
1. Create `README.md` only when the user explicitly requests it.
2. If a README already exists, treat the request as an update unless the user
   explicitly authorizes replacement after reviewing the existing content.
3. Use only applicable, confirmed sections: Project Title, Overview,
   Specifications, Hardware Architecture, Project Status, Repository Structure,
   Design Notes, and Documentation.
4. Omit unknown sections rather than filling them with assumptions.
5. Include `Current Phase` only when a human engineer explicitly declares one.
   Otherwise, remove the `Current Phase` placeholder line entirely; do not
   substitute a default value.

## Update
1. Read the existing README before proposing an update.
2. Preserve valid, unrelated content and its established structure where
   practical.
3. Make the smallest requested edit. Do not remove substantial content without
   explicit review and authorization.
4. Include a project phase only when the human explicitly declares one.
5. Preserve an existing static Mermaid workflow diagram unless the user
   explicitly requests a diagram change.

## Output
- State which README sections were created or changed and which facts remain
  unavailable.
- Do not claim that documentation proves design verification or approval.

## README Template

- Use `assets/readme_template.md` as the starting structure for new project READMEs.
- Adapt the template to the actual hardware project and available evidence.
- Include only relevant sections supported by known project information.
- Remove unused placeholders and optional sections.
- If no human phase declaration is available, remove the `Current Phase`
  placeholder line entirely. Do not substitute `DRAFT`, `Not declared`,
  `Unknown`, or an inferred value.
- Preserve existing information and custom sections when updating a README.
- Preserve the template's static Mermaid workflow diagram; it is not a
  current-phase indicator.
- Do not infer or change the project phase. Record only a human-declared phase.
- Do not open, parse, or assess PDF content.
- Do not modify the template file during normal README generation.
