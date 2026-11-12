# Evaluation prompts

Maintainer test cases for checking the skill by hand. No run-time pointer
reaches this file. Each case lists the expected result.

1. Block with a known defect: "Review the 3V3 regulator block", where the
   regulator's EN pin has no wire, no label and no no-connect marker.
   Expect: pin coverage lists EN as unresolved; one finding row in the
   Output format with an evidence label and a `Status:` field; EN also
   appears under `NOT_VERIFIED` if the datasheet was not checked; no KiCad
   file is edited.
2. Block with missing constraints: "Review the input protection", in a
   project with no specification and no input range given. Expect: the
   operating range is `ASSUMED` and stated; datasheet values without a
   source are `NOT_VERIFIED`; the report says no requirements record was
   found; the conclusion is at most "No issue found within the inspected
   scope", never a pass.
3. Lookup only: "Which net is U5 pin 3 on?" Expect: `sch-review` does not
   trigger; `sch-inspect` answers with the net and its scope level.
