# AeroOptix-Horizon: STM32H743VI Price and Stock

**Revision:** 0.1
**Updated:** 2026-10-16
**Status:** Working summary. Not a quote. No part is approved.
**Decision owner:** Human engineer

Single record for price and stock of the STM32H743VI main MCU. Add a new part number as a new column.

Evidence labels follow `.claude/rules/engineering.md`. Values come from supplier product pages read with a web fetch tool that returns a summarized extract, not raw HTML. Search snippets are noted below the table and are not live quotes.

## 1. Price and stock

Date: 2026-10-16 | Region: digikey.com, lcsc.com, jlcpcb.com (ship-to not set, `ASSUMED` US/global pricing) | Currency: USD | Qty: 1 and 10

| Detail | STM32H743VIT6 | STM32H743VIH6 | STM32H743VIH6TR | (new P/N) |
| ------ | ------------- | ------------- | --------------- | --------- |
| Package | LQFP-100 14x14 | TFBGA-100 | TFBGA-100, tape and reel | |
| DigiKey SKU | 497-17720-ND | 497-STM32H743VIH6-ND | `NOT_VERIFIED` (not checked) | |
| DigiKey stock | `NOT_VERIFIED` (no figure on page) | 0 (backorder) | `NOT_VERIFIED` | |
| DigiKey qty 1 | $18.90 | $18.11 | `NOT_VERIFIED` | |
| DigiKey qty 10 | $14.929 | $14.31 | `NOT_VERIFIED` | |
| DigiKey lead time | 52 weeks (mfr standard) | 52 weeks (mfr standard) | `NOT_VERIFIED` | |
| DigiKey packaging | Tray | Tray | `NOT_VERIFIED` | |
| Mouser SKU | 511-STM32H743VIT6 (snippet) | 511-STM32H743VIH6 (snippet) | `NOT_VERIFIED` (not checked) | |
| Mouser stock | 0, ~6,400 on order (snippet, `NOT_VERIFIED`) | 4,626 (snippet, `NOT_VERIFIED`) | `NOT_VERIFIED` | |
| Mouser qty 1 | $17.03 or $17.09 (snippet, `NOT_VERIFIED`) | $16.85 (snippet, `NOT_VERIFIED`) | `NOT_VERIFIED` | |
| Mouser qty 10 | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | |
| Mouser lead time | 52 weeks (snippet, `NOT_VERIFIED`) | 30 weeks (snippet, `NOT_VERIFIED`) | `NOT_VERIFIED` | |
| LCSC SKU | C114409 | C964146 | C1857444 | |
| LCSC stock | 11 | 0 (out of stock) | 1,269 (seen on C964146 page) | |
| LCSC qty 1 | $12.108 | $9.8374 (reference only) | $10.9733 (single price) | |
| LCSC qty 10 | $10.363 | $8.4631 (reference only) | `NOT_VERIFIED` (only one price seen) | |
| LCSC MOQ / packaging | 1 / tray of 90 | 1 / tray of 348 | `NOT_VERIFIED` | |
| JLCPCB code | C114409, Extended | Not listed | C1857444, Extended | |
| JLCPCB stock | `NOT_VERIFIED` (JS page) | Not listed | `NOT_VERIFIED` (JS page) | |
| JLCPCB qty 1 | `NOT_VERIFIED` | Not listed | `NOT_VERIFIED` | |
| JLCPCB qty 10 | `NOT_VERIFIED` | Not listed | `NOT_VERIFIED` | |
| Status | Active (DigiKey) | Active (DigiKey) | `NOT_VERIFIED` | |

LCSC extra breaks: VIT6 30+ $9.2985, 100+ $8.4071. VIH6 30+ $7.6244, 100+ $6.9208. DigiKey extra breaks: VIT6 24 $13.975, 90 $12.91378, 270 $12.28707, 450 $12.05527. VIH6 50 $12.789, 100 $12.3179, 500 $11.52078.

## 2. Best verified in-stock source

| Detail | STM32H743VIT6 | STM32H743VIH6 | STM32H743VIH6TR |
| ------ | ------------- | ------------- | --------------- |
| Supplier | LCSC | None found in stock | LCSC |
| Stock | 11 | 0 | 1,269 |
| Qty 1 price | $12.108 | n/a | $10.9733 |

## 3. Sources

- DigiKey VIT6: https://www.digikey.com/en/products/detail/stmicroelectronics/STM32H743VIT6/7809237
- DigiKey VIH6: https://www.digikey.com/en/products/detail/stmicroelectronics/STM32H743VIH6/10326786
- LCSC VIT6: https://www.lcsc.com/product-detail/C114409.html
- LCSC VIH6 (also shows the VIH6TR listing): https://www.lcsc.com/product-detail/C964146.html
- JLCPCB VIT6: https://jlcpcb.com/partdetail/C114409
- JLCPCB VIH6TR: https://jlcpcb.com/partdetail/STM32H743VIH6TR/C1857444
- Mouser VIT6 (timed out, snippet only): https://www.mouser.com/en/ProductDetail/STMicroelectronics/STM32H743VIT6?qs=FNcb6ahWXRw0Me5k2ZHgWw%3D%3D
- Mouser VIH6 (timed out, snippet only): https://www.mouser.com/ProductDetail/STMicroelectronics/STM32H743VIH6?qs=EU6FO9ffTwep%2BmI4YnA3%2Fw%3D%3D

## 4. Notes and live checks before buying

- Search snippets conflicted with the fetched pages, so treat these as stale. LCSC VIT6 snippets showed 2,960 at about $8.38, and also out of stock at about $8.11. LCSC VIH6 snippets showed about 40 at $6.88 and about 2,000 at $13.36. Aggregators showed DigiKey VIT6 at 2.6K to 4.6K, $15.92 at qty 1, and a 15 to 20 week lead time.
- DigiKey VIT6 stock: the page shows no figure. Check it live.
- LCSC VIT6 has only 11 in stock. That covers a small prototype run only. Check it live before ordering.
- LCSC VIH6TR stock and price came from the C964146 page, not its own page. Check C1857444 live.
- JLCPCB stock and price did not load (JS-rendered page). LCSC stock does not prove JLCPCB assembly stock. Check both codes live if JLCPCB assembly is planned. The BGA part needs X-ray inspection at JLCPCB (search snippet only, `NOT_VERIFIED`).
- Mouser: both product pages timed out. Every Mouser value is search-snippet data. The VIT6 snippets disagree ($17.03 vs $17.09, 6,480 vs 6,416 on order). VIH6 snippet also shows 12,528 on order, 10,440 expected 2026-10-30. Check all Mouser rows live.
- Mouser also lists STM32H743VIT6TR (tape and reel, separate MPN, not in the table): 16 in stock, $16.23 at qty 1 (snippet, `NOT_VERIFIED`). https://www.mouser.com/en/ProductDetail/STMicroelectronics/STM32H743VIT6TR?qs=sPbYRqrBIVlqa%2BT88Fil4w%3D%3D
- No independent brokers were used.
