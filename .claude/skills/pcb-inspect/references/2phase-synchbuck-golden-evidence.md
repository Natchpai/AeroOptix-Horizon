# 2Phase_SynchBuck PCB Golden Evidence

## Scope

This record supplies the independent native evidence for the opt-in
`test_query_pcb_golden.py` checks. It is intentionally limited to saved KiCad
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
