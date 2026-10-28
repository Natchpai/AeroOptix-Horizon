---
paths:
  - "**/*.pdf"
  - "**/documents/**"
---

# NotebookLM procedure

Full procedure for datasheet answers through NotebookLM. `engineering.md`
keeps the gating rules and points here; read this file before any
`notebooklm` command. PDF access and upload approval follow `pdf.md`.

- After explicit approval naming the file and the notebook, either the user
  adds the source, or Claude runs `notebooklm source add <path> -n <id>`, which
  passes the path to the CLI without reading the file. Claude does not need to
  open the PDF or check its contents.
- Get the notebook ID from the user, or find it with `notebooklm list --json`
  (read-only). Creating a notebook needs approval.
- If the `notebooklm` skill or CLI is missing, or `notebooklm auth check
  --test --passive --json` does not report `status: ok` with
  `checks.token_fetch: true`, tell the user plainly that NotebookLM is not
  available, name what is missing, and stop and ask the human what to do
  (`pdf.md`). Do not install it or log in yourself, and do not carry on as if
  the datasheet was checked.
- Pin the notebook (`-n <id>`), wait until every source is `ready`, and ask
  with `--json`. Name the exact MPN and variant in the question, and ask which
  datasheet section or variant the answer comes from.
- Record the citation from the JSON `references`: `source_id` and the
  `cited_text` excerpt, plus the section and table the answer names. There are
  no page numbers. Label a value `VERIFIED` only when the `cited_text` actually
  contains the value, and write "via NotebookLM" with the source name and
  revision.
- An answer without a citation, or one that conflicts with another source, is
  `NOT_VERIFIED`.
- Ask it to quote the exact table or pin text for critical values (absolute
  maximum and recommended ratings, pinout, package dimensions, thermal data)
  and tell the human to confirm those against the datasheet before design
  commitment. NotebookLM is a reading aid, not an approval.
- Parse JSON output with `PYTHONUTF8=1` (answers contain non-ASCII symbols
  that break the default Windows code page). Asking adds a turn to the
  notebook's chat history; do not use `ask --new` without approval.
- Never print or commit its auth files, and do not generate NotebookLM
  artifacts, notes or shares unless asked.
- If neither the user nor NotebookLM can supply the source, report
  `NOT_VERIFIED` or ask the human for the values.
