# pcb-inspect regression and golden validation

For maintainers; not needed for normal inspection.

Run synthetic tests with:

- `python tests/run_tests.py --pattern test_query_pcb.py --label synthetic`

For opt-in project evidence, set `KICAD_PCB_GOLDEN_BOARD` to an absolute
`.kicad_pcb` path, then run:

- `python tests/run_tests.py --pattern test_query_pcb_golden.py --label golden`

Golden tests skip when the environment variable is absent and fail when it is explicitly
configured to a missing or non-PCB path. The 2Phase_SynchBuck values are independently
transcribed from native KiCad PCB text and checked against this read-only CLI; they are not
derived from a previous CLI result. See
`references/2phase-synchbuck-golden-evidence.md` for the recorded native evidence.
Golden coverage is intentionally narrow and does not claim complete PCB Editor, DRC, or
connectivity parity.
