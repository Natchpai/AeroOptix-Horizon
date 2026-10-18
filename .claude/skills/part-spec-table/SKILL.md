---
name: part-spec-table
description: >-
  Builds or updates a Markdown table that compares the specs of candidate
  parts, one column per part number. Use when the user asks for a spec
  comparison table, or wants to add a part number to an existing one. Not for
  choosing the part or price and stock.
argument-hint: "<MPN> [<MPN> ...] | add <MPN>"
---

# Part Spec Table

Make one table. One column per part, one row per spec. Keep it simple.

## Rules

- Never invent a value. Never open or read a PDF. Datasheet values come from
  the user, official manufacturer web pages, or NotebookLM answers with cited
  text, used only after the user approves uploading the file. If the project
  has `.claude/rules/engineering.md`, follow its "Datasheet evidence" section.
- Mark every cell with an evidence label: `VERIFIED`, `ASSUMED`, `ESTIMATED`,
  `NOT_VERIFIED`. If no source is known, write `NOT_VERIFIED`. Leave no blank.
- Put the source in the cell or in a short source list under the table
  (manufacturer page, datasheet section, user message).
- Do not mix recommended operating values with absolute maximum values. Name
  which one a row holds.
- Say which row decides the choice. Do not pick a winner unless asked.
- Write the file only when the user asks. Save it in the KiCad project's
  existing documents folder (near the `.kicad_pro`). If there is none, or more
  than one, ask once. Do not edit KiCad files.
- Never shorten the spec table to "key rows" unless the user asks. Keep every
  row and every `NOT_VERIFIED` cell. A summary may add to the table, not replace it.
- Keep one record per topic. If a file for the topic exists, update it. Do not
  split into extra files or delete files unless the user asks.
- Table format: pad the first column of every table to the width of its longest cell (header included), so the source lines up. Match the dashes in the separator row to that width. Leave the other columns unpadded.

## Steps

1. Get the part numbers (exact orderable MPN) and the use case. Ask only if
   missing.
2. Pick the rows that matter for the use case (usually 15 to 25). Always
   include: status, interface, supply range (VDD and I/O), package and size,
   footprint match to the main candidate, operating temperature, the key
   performance numbers, and a driver or software support row when it applies.
   Add rows from the project spec (`SEN-*`, `PWR-*`, ...) when they apply.
   Reuse the rows of an existing table so columns stay comparable.
3. Fill each cell from a source. Keep units. Use the same unit in a row.
4. If the user adds a part, add a column and fill its cells. Keep the other
   columns unchanged.
5. List what is still `NOT_VERIFIED` below the table and how to close it.

## Table shape

```text
| Parameter      | <MPN 1> | <MPN 2> | (new P/N) |
| -------------- | --- | --- | --- |
| Manufacturer   | name | name | |
| Product status | Production `VERIFIED` | `NOT_VERIFIED` | |
| Supply range   | 1.71 to 3.6 V `VERIFIED` | `NOT_VERIFIED` | |
| Package        | LGA-14 2.5x3 mm `VERIFIED` | ... | |
```

## Writing style

- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences and active voice.
- Avoid fancy words, marketing phrases and AI-style filler. Keep standard engineering terms and exact identifiers.
- Do not use the em dash (`—`). Use a period, comma, colon or parentheses.
- Do not reword existing text that is already clear and correct.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Output

The table, the source list, and a short list of `NOT_VERIFIED` cells. No long
text.
