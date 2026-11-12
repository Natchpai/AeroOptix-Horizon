# pcb-inspect regression and golden validation

For maintainers; not needed for normal inspection.

Run synthetic tests with:

- `python tests/run_tests.py --pattern test_query_pcb.py --label synthetic`

Golden tests check the CLI against one real board. They are opt-in and need
two environment variables. With either one unset they skip; a path that is set
but wrong makes them fail.

- `KICAD_PCB_GOLDEN_BOARD`: absolute path of a `.kicad_pcb` file.
- `KICAD_PCB_GOLDEN_EXPECT`: absolute path of a JSON file with the expected
  values for that board.

Then run:

- `python tests/run_tests.py --pattern test_query_pcb_golden.py --label golden`

The JSON file holds a list of `cases`. Each case has a `name`, a `command`
(the test adds `--board` and `--limit 200`), an optional `status`, and
`fields`: a map from a field path to its expected value. A path uses dots,
`[n]` for a list index and `[key=value]` for the one list item with that
value, for example `pads[number=1].position` or `tracks[0].length_mm`. An
unknown key, a path that is not in the output, or a selector that matches no
item or several items fails the case.

Start from `tests/golden.example.json`. Its values belong to one real project
and were read from the native KiCad PCB text, not from a CLI result;
`tests/golden.example-evidence.md` records where each one comes from. Expected
values for another board must be checked the same way. Golden coverage is
narrow and does not claim complete PCB Editor, DRC, or connectivity parity.
