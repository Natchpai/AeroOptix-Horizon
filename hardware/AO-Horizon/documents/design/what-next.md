# What Next

**Updated:** 2026-11-21
**Status:** Personal reminder list. Not a requirement, decision or verification record.

The specification and the execution checklist hold all state. Each line here is one next action and the ID that tracks it. Keep values and status out of this file. Delete a line when it is done; do not tick it.

## Next actions

- [ ] Commit the 2026-11-21 work (DEC-098, DEC-099, netclass rule areas). Run `/progress-update light` first if the rule areas should be in the spec.
- [ ] Update the PCB from the schematic, then continue placement (P3-002).
- [ ] Decide the drawn connector and servo-power blocks, CN701 to CN706 and CN801 to CN804 (spec 4.2; P2-016, P2-018, OPEN-023, OPEN-031).
- [ ] Clear the sheet leftovers (P2-024) and the temporary `PWR_FLAG` on `VBUS` (P2-022).
- [ ] Re-run ERC after each schematic change (P2-009).
- [ ] Set the netclass rules and the stackup with the fabricator (P3-010, OPEN-040); servo copper and GND join (P3-003, OPEN-021).
- [ ] Board outline, mounting and cable entry for the CAD team (P3-001, OPEN-009).
- [ ] Sourcing before the BOM: ICP-20100 EOL, BMP581 stock, IST8310 lifecycle (P3-007, OPEN-004).
- [ ] Team inputs: integration questions, ESC and receiver data (P0-022; OPEN-017, OPEN-034).
- [ ] After the board is built: bench tasks P4-002 and P4-011 to P4-016.
- [ ] Team website follow-ups: `web/HANDOFF.md`.

After design work: `/progress-update light`; before a commit: `/progress-update sync`.
