---
name: hw-git-readme
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

## Writing style
- Write simple, direct English, like one engineer talking to another.
- Use everyday words. Avoid fancy words, marketing phrases, AI-style filler
  ("robust", "seamless", "leverage", "comprehensive") and long intros.
- Use short sentences and active voice. Start bullets with the fact, not a
  lead-in.
- Keep standard engineering terms and exact names (refs, nets, part numbers).
  Do not simplify a technical term if it loses accuracy.
- Do not use the em dash (`—`). Use a period, comma, colon or parentheses.
- Do not reword existing text that is already clear and correct.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Create
1. Create `README.md` only when the user explicitly requests it.
2. If a README already exists, treat the request as an update unless the user
   explicitly authorizes replacement after reviewing the existing content.
3. Use `assets/readme_template.md` as the starting structure and only its
   applicable, confirmed sections: Overview, Key Features, Specifications,
   Project Status, Hardware Design, Repository Structure, Documentation,
   Results, References and License.
4. Omit unknown sections rather than filling them with assumptions.
5. Include `Current Phase` only when a human engineer explicitly declares one.
   Otherwise, remove the `Current Phase` placeholder line entirely; do not
   substitute a default value.
6. Show the proposed content and wait for approval before writing the file,
   unless the user already asked for the file to be written.

## Update
1. Read the existing README before proposing an update.
2. Preserve valid, unrelated content and its established structure where
   practical.
3. Make the smallest requested edit. Do not remove substantial content without
   explicit review and authorization.
4. Keep an existing Mermaid workflow diagram's structure. Its `class` lines
   follow the declared phase; see "Template rules". Change the diagram's
   structure only on explicit request.

## Output
- State which README sections were created or changed and which facts remain
  unavailable.
- Do not claim that documentation proves design verification or approval.

## Template rules
- Remove unused placeholders and optional sections; adapt the repository tree
  and links to files that actually exist. Use the real directory name as the
  tree root. Omit Overview when it would only repeat the tagline.
- Remove maintainer comments (`<!-- ... -->`) from the generated README.
- Specifications are design targets unless the user identifies them as
  measured or verified; keep the template's note saying so.
- If no human phase declaration is available, remove the `Current Phase`
  placeholder line entirely. Do not substitute `DRAFT`, `Not declared`,
  `Unknown` or an inferred value. Recording a later phase change is a separate
  task (`hw-phase-record`, if installed).
- Keep the template's Mermaid workflow diagram. Its `class` lines mirror the
  `Current Phase` value with this mapping: earlier phases `done`, the declared phase `review`, later phases
  `inactive`, all four `done` for RELEASE. With no declared phase, all four
  stay `inactive`. When updating a README, make the diagram agree with the
  `Current Phase` it contains; never derive a phase from the diagram.
- Do not modify the template file during normal README generation.
- Writing the README is a content edit. Staging or committing it needs
  separate approval. Follow `rules/git-workflow.md` if present.
