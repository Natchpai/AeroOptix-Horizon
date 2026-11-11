# Example golden evidence: 2Phase_SynchBuck PCB

This is an example. It belongs to one real project and records where the
values in `golden.example.json` come from. For another board, write your own
expectation file and keep your own evidence with it.

## Scope

This record supplies the independent native evidence for the cases in
`golden.example.json`, which `test_query_pcb_golden.py` runs when it is
configured. It is intentionally limited to saved KiCad
PCB geometry and does not establish DRC status, copper contact, clearance,
route completeness, signal integrity, or electrical correctness.

## Source inspected

- Native file: `hardware/2Phase_SynchBuck/2Phase_SynchBuck.kicad_pcb`
- Evidence method: direct inspection of native KiCad S-expression fields; no
  `query_pcb.py` output was used to derive the expected values.

## R313 pad geometry and centre distance

The native footprint begins near line 185 with `(at 127.5 117.25)`. Its saved
pad records near lines 393 and 402 specify:

| Pad | Local centre (mm) | Size (mm) | Board centre (mm) |
| --- | --- | --- | --- |
| `1` | `(-0.825, 0)` | `(0.8, 1)` | `(126.675, 117.25)` |
| `2` | `(0.825, 0)` | `(0.8, 1)` | `(128.325, 117.25)` |

The Euclidean distance between those two saved centres is `1.65 mm`.

## U304 back-side pad centre

U304 is saved on `B.Cu` with `(at 158.1125 86.2 90)`. Its pad `1` has the
local centre `(-1.25, 0.95)` and net `+5V`. A saved `B.Cu` segment on `+5V`
starts at `(159.0625, 87.45)` mm, which is the board centre of that pad when
the saved local coordinates are rotated without an extra mirror. A mirrored
local X would give `(159.0625, 84.95)` mm, where no `+5V` track ends.

## Board totals

The saved file has 306 top-level `footprint` forms, 1599 `segment` forms, no
`arc` track forms, 797 `via` forms and 133 `zone` forms, and no net table.

## `/Top/Power Supplies/+5VUSB` routing geometry

The direct saved routing sequence begins near line 100884. It contains 17
`segment` records before the matching via, followed by one B.Cu `segment`, for
18 target track primitives total. The first target segment is:

- start `(111.1, 117.95)` mm
- end `(116.8, 117.95)` mm
- width `0.3` mm on `F.Cu`
- geometric length `5.7` mm

The following matching via is at `(111.1, 117.95)` mm with size `0.8` mm,
drill `0.4` mm, and span `F.Cu` to `B.Cu`. No explicit `(type ...)` field is
saved for this via; its type remains `NOT_VERIFIED`.
