---
name: stock-select
description: >-
  Finds and filters electronic parts that can be sourced from DigiKey, Mouser,
  LCSC, or the JLCPCB Parts Library, and builds a price, stock and lead-time
  table for known part numbers. Use when the user asks for in-stock parts,
  supplier-specific alternatives, availability, price breaks, MOQ, JLCPCB
  assembly-ready parts, or a price or stock comparison table. Not for
  engineering fit. Does not order anything.
argument-hint: "[function | MPN | requirements] [supplier] [quantity] | table <MPN> [<MPN> ...] | table add <MPN>"
---

# Stock-Based Component Selection

Find a shortlist of parts that can be bought now. This skill covers **supplier
stock and purchase constraints**, not the electrical design. Search by the
requirement, not by a preferred manufacturer, part number or category.

## Evidence baseline

- Label each significant claim `VERIFIED` (named evidence: CAD data, a
  calculation or an official source), `ASSUMED` (assumption stated),
  `ESTIMATED` (method and margin stated) or `NOT_VERIFIED` (evidence missing
  or check not run).
- Datasheet, schematic and PCB PDFs are not read, by any tool. Project report
  PDFs may be read.
- Datasheet values come from the user, official manufacturer web pages, or
  NotebookLM answers with cited text. Query an existing notebook without
  asking. Adding a source or creating a notebook uploads a file and needs the
  user's approval. With no source, the value is `NOT_VERIFIED`.
- KiCad design and library files are read-only. Propose changes; do not apply
  them.
- If the project has `.claude/rules/engineering.md` and `pdf.md`, follow them;
  they are the full policy.

## Scope and boundaries

- Sources: **DigiKey, Mouser, LCSC and the JLCPCB Parts Library**. Search the
  suppliers the user names; with none named, use all that apply. Their catalogs
  differ.
- Keep **supplier stock** apart from **the user's own inventory**. Use the
  user's stock records only when they supply them.
- Stock, price and lead time change. Take them from current supplier listings,
  authorized APIs or exports the user gives, and record the source and date.
  Without live access, the value is `NOT_VERIFIED`.
- Source genuine, traceable parts. Check the exact **manufacturer MPN with
  suffix**, and keep it apart from the supplier SKU (DigiKey or Mouser number,
  LCSC code, JLCPCB part number).
- *Available to order* is not *on hand*, *listed* is not *assembly-ready*, and
  supplier stock is not a reservation.
- Ordering, reserving, uploading a BOM, signing in and changing a KiCad project
  all need explicit authorization. Inspection is read-only.
- Engineering fit and trade-offs, and datasheet, package, footprint and pinout
  checks, are separate work (`component-select` and `component-check`, if
  installed). Passing the stock filters does **not** mean the part is
  electrically approved.

## Workflow

1. **Scope the purchase.** The function or existing MPN, required electrical
   and package constraints, quantity, ship-to region, budget, needed delivery
   date, and whether JLCPCB assembly is needed. State assumptions for missing
   items, and give total cost only when quantity and region are known.
2. **Search the catalogs.** Search the exact MPN first for replacements or BOM
   sourcing; use parametric search to find alternatives. Record the exact
   listing URL or source record for each candidate.
3. **Normalize identifiers.** Manufacturer, full orderable MPN, supplier,
   supplier SKU, package, lifecycle when shown, and any listing ambiguity. Merge
   two listings only when the MPN matches, not because the descriptions look
   alike.
4. **Apply hard filters.** Reject candidates that fail a required electrical,
   environmental, package, assembly, traceability or lead-time constraint. A
   missing critical value is `NOT_VERIFIED`, not PASS.
5. **Check purchase conditions.** Sellable quantity versus non-stock, lead time
   or backorder; order increments, MOQ, packaging (cut tape, reel, tray), price
   breaks at the requested quantity, currency, and shipping-region limits.
   Tax and shipping stay estimates.
6. **Check JLCPCB on its own.** Look up the **JLCPCB assembly parts library**
   directly: part code, assembly eligibility, Basic or Extended when shown,
   stock usable for the PCBA order, and pre-order or consignment limits. **LCSC
   stock does not prove JLCPCB assembly stock**, and a JLCPCB library part may
   not ship on its own.
7. **Shortlist and stop.** Give two or three qualified purchase options that
   differ in a real way, or say that none pass. Prefer parts that can actually
   be bought, but never trade a required engineering constraint for stock.

## Output contract

- **Search context:** requirements, quantity, region, suppliers searched, and
  date and time checked.
- **Candidate table:** exact MPN, supplier SKU, source, stock, price at the
  relevant quantity, MOQ or increment, package, and assembly eligibility where
  it applies. Missing fields are `NOT_VERIFIED`.
- **Recommendation:** `RECOMMENDED`, `ALTERNATIVE`, `REJECTED` or
  `NOT_VERIFIED`, with the reason and any main sourcing risk.
- **Next step:** the critical electrical or package check, or a stock recheck
  right before purchase or PCBA submission.

Being in stock does not make a part pin-compatible, drop-in or approved. With
no live supplier data, give a clearly labeled sourcing plan or provisional
shortlist.

## Example

```text
Context: <MPN A>, qty 10, ship to <region>, DigiKey + LCSC + JLCPCB, checked YYYY-MM-DD
<MPN A> | DigiKey <SKU> | stock 1,200 | $0.42 at qty 10 | page fetch    | RECOMMENDED
<MPN A> | LCSC <code>   | stock NOT_VERIFIED (page timed out)            | NOT_VERIFIED
<MPN A> | JLCPCB <code> | Extended, stock 0 for PCBA                     | REJECTED for assembly
Next:    recheck LCSC stock before ordering; JLCPCB assembly needs another part or consignment.
```

## Table mode: price and stock for known part numbers

Use it when the user gives part numbers and wants a comparison table (`table
<MPN> ...`), or adds a part to an existing one (`table add <MPN>`). It
compares sourcing only; it does not find parts or judge fit.

Rules (on top of the ones above):
- Never invent stock, price or lead time. A value not seen is `NOT_VERIFIED`;
  leave no blank. A page that times out or shows no listing data is
  `NOT_VERIFIED`, not "not stocked".
- Put the date, region, currency and quantity above the table.
- Search only the suppliers the user names; a supplier they drop stays out of
  the table and the notes. Prefer the supplier product page over snippets and
  aggregators, and say in the row when a value came from a snippet.
- Compare at the same quantity. If a supplier has no break there, give the
  nearest one and say so. Flag independent brokers; their traceability is
  `NOT_VERIFIED`.
- Keep price cells short; conflicts and long notes go below the table.
- Write the file only when asked, in the KiCad project's existing documents
  folder (near the `.kicad_pro`); if there is none or more than one, ask once.
  Keep one file per topic and update it.
- Pad the first column of every table to its longest cell, with matching
  separator dashes; leave the other columns unpadded.

Steps: get the part numbers, quantity, region and whether JLCPCB assembly is
needed (state assumptions). Search each exact MPN at each supplier. Fill qty 1
and qty 10 prices, stock, lead time, SKU and MOQ; show both readings and mark
`NOT_VERIFIED` when two sources conflict. Adding a part adds a column and
leaves the others unchanged. End with the rows that need a live check before
buying.

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
| Notes             | page fetch, conflict | ... | |
```

Part numbers go across the top in the same order as the spec table
(`component-select` table mode); supplier details go down the side, repeated
for each supplier the user names. An optional second table in the same layout
gives the best verified in-stock supplier, its stock and price.
