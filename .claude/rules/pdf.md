# PDF Rules

The single source for how Claude reads, generates and handles PDFs. Other
rules point here.

## Read
- Claude may read PDFs the project produces or keeps, such as reports,
  review notes and other project documents.
- Claude does not read schematic or PCB output PDFs: schematic plots, PCB
  plots, fabrication and assembly drawings. Use the native `.kicad_sch` and
  `.kicad_pcb` files through `sch-inspect` and `pcb-inspect` instead.
- Claude reads a datasheet only through the route in Datasheets: any vendor
  document such as a datasheet, reference manual, application note or
  errata, wherever it is stored.
- These limits apply to every route: the Read tool, `pdftotext`, Python
  libraries or any other tool. If unsure which kind a PDF is, ask.

## Guard
- The `pdf` block of `.claude/hooks/protect.json` sets the level per project,
  checked deny > ask > allow, ignoring case, for the Read tool and for shell
  commands that name a `.pdf`. A PDF that matches no glob gets `ask`.
- Defaults: schematic and manufacturing output folders are denied, project
  report folders and the scratchpad are allowed, and every other PDF
  (datasheets included) asks.
- The guard is a safety net, not the rule. An `allow` or a granted prompt
  does not replace the approval that Datasheets asks for.

## Generate
- Claude may generate report PDFs when asked: with the `engineering-report-pdf`
  skill or another report tool, from Markdown or other text sources.
- Claude may read and render the PDFs it generated to check them.
- Generating schematic, PCB, fabrication or assembly outputs (KiCad plots,
  Gerbers, drawings) stays a human action (`workflow.md`).
- A generated PDF is a document, not evidence. Its values keep the evidence
  label of their source (`engineering.md`).

## Datasheets
- NotebookLM is the default source for datasheet content. Query an existing
  notebook without asking; follow `notebooklm.md`.
- Adding a new PDF source or creating a notebook needs the user's approval,
  because it uploads the file to an external service. A PDF path in the
  request is not that approval.
- Values the user supplies and official manufacturer web pages are also
  allowed sources.
- If NotebookLM has a problem (not installed, auth fails, no notebook or
  source for the part, no citation, conflicting answers), stop and ask the
  human what to do: for example fix the login, add the source, supply the
  values, keep the claim `NOT_VERIFIED`, or let Claude read the datasheet
  PDF.
- **Direct read (fallback).** Claude reads a datasheet PDF only after the
  human approves it in chat for that file. Then:
  - read only the pages or sections the question needs;
  - label a value `VERIFIED` only with the file name, document revision,
    page and table or figure;
  - never upload the file or send it to an external model.

## Other
- During Git review, report PDFs by path and metadata only.
- Send no PDFs to external-model providers (`agent-coworker`).
