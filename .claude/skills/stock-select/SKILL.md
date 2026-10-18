---
name: stock-select
description: >-
  Finds and filters electronic parts that can be sourced from DigiKey, Mouser,
  LCSC, or the JLCPCB Parts Library. Use when the user asks for in-stock parts,
  supplier-specific alternatives, availability, price breaks, MOQ, or JLCPCB
  assembly-ready parts. Not for engineering fit or a price table for known
  part numbers.
argument-hint: "[function | MPN | requirements] [supplier] [quantity]"
---

# Stock-Based Component Selection

Find a shortlist of parts that can be bought now. This skill covers **supplier
stock and purchase constraints**, not the electrical design. Search by the
requirement, not by a preferred manufacturer, part number or category.

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
