---
name: price-compare-table
description: >-
  Builds or updates a Markdown table of price, stock and lead time for known
  part numbers across DigiKey, Mouser, LCSC and JLCPCB. Use when the user asks
  for a price or stock comparison table, or wants to add a part number to an
  existing one. Not for finding parts or judging design fit. Does not order
  anything.
argument-hint: "<MPN> [<MPN> ...] | add <MPN>"
---

# Price Compare Table

Make one table. One column per part, one row per supplier detail. Keep it simple.

## Rules

- Never invent stock, price, or lead time. If a value was not seen, write
  `NOT_VERIFIED`. Leave no blank.
- Put the date, region, currency, and quantity above the table. Prices change.
- Give the exact orderable MPN and the supplier SKU (LCSC code, DigiKey or
  Mouser number, JLCPCB code) when known. Do not merge parts that only look
  alike.
- Name the source of each row: the supplier page, or an aggregator or search
  snippet. An aggregator or snippet is not a live quote. Say so in the row.
- Flag independent brokers (not authorized distributors) in the notes. Their
  traceability is `NOT_VERIFIED`.
- Do not mix price breaks. Compare at the same quantity. If a supplier has no
  price at that quantity, write the nearest break and say so.
- LCSC stock does not prove JLCPCB assembly stock. Check JLCPCB separately and
  note Basic or Extended.
- Do not order, reserve, sign in, or upload a BOM. Do not edit KiCad files.
- Write the file only when the user asks. Save it in the KiCad project's
  existing documents folder (near the `.kicad_pro`). If there is none, or more
  than one, ask once.
- Search only the suppliers the user names. If the user drops a supplier (for
  example Mouser), leave it out of the table and the notes.
- Prefer the supplier product detail page over search snippets and aggregators.
  Open the detail page for stock and price breaks. If a page times out or shows
  no listing data, write `NOT_VERIFIED`. Do not read that as "not stocked".
- Keep price cells short: the price and at most a few words of detail. Put
  conflicts and long notes below the table, not in the cell.
- A short summary table is fine for price. Keep the full table too, unless the
  user asks to drop it.
- Keep one record per topic. Update the existing file. Do not delete files
  unless the user asks.
- Table format: pad the first column of every table to the width of its longest cell (header included), so the source lines up. Match the dashes in the separator row to that width. Leave the other columns unpadded.

## Steps

1. Get the part numbers, quantity (for example 2, 10, 100), ship-to region, and
   whether JLCPCB assembly is needed. If not given, state the assumption.
2. Check each supplier for each part. Search the exact MPN first.
3. Fill the table with qty 1 and qty 10 prices, stock, lead time and SKU. If
   two readings conflict (for example a snippet against a page fetch), show
   both and mark the row `NOT_VERIFIED`.
4. If the user adds a part, add its rows. Keep the other rows unchanged.
5. Add a short note: which rows need a live check before buying.

## Table shape

```text
Date: YYYY-MM-DD | Region: ... | Currency: ... | Qty: ...

| Detail            | <MPN 1> | <MPN 2> | (new P/N) |
| ----------------- | --- | --- | --- |
| DigiKey SKU       | ... | ... | |
| DigiKey stock     | 0 | 18,395 | |
| DigiKey qty 1     | $4.86 | $5.87 | |
| DigiKey qty 10    | $4.17 | $5.06 | |
| DigiKey lead time | 45 weeks | ... | |
| LCSC SKU          | C... | `NOT_VERIFIED` | |
| LCSC stock        | 1,875 | `NOT_VERIFIED` | |
| LCSC qty 1        | $21.00 | `NOT_VERIFIED` | |
| LCSC qty 10       | ... | ... | |
| LCSC lead time    | ... | ... | |
| Notes             | page fetch, conflict | ... | |
```

Layout: part numbers go across the top (one column per part). Details go down
the side (one row per supplier field: SKU, stock, qty 1, qty 10, lead time,
MOQ, notes). Use the same part order as the spec table. Adding a part means
adding a column. Repeat the detail rows for each supplier the user names.

Optional second table, same layout: one row each for best verified in-stock
supplier, stock, and price.

## Writing style

- Write simple, direct English, like one engineer talking to another. Use everyday words, short sentences and active voice.
- Avoid fancy words, marketing phrases and AI-style filler. Keep standard engineering terms and exact identifiers.
- Do not use the em dash (`—`). Use a period, comma, colon or parentheses.
- Do not reword existing text that is already clear and correct.
- Priority: technical accuracy, then clarity, then brevity, then style.

## Output

The table, the source list, and the rows that need a live check. No long text.
