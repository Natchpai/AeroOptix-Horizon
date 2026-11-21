#!/usr/bin/env python3
"""Tests for review_items() in progress-update/scripts/progress_preflight.py.

Run: python -I -X utf8 .claude/skills/progress-update/tests/test_review_items.py
Standard library only. Synthetic cases need nothing else. The regression cases
read the AeroOptix-Horizon history with git and skip in any other repo.
"""
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
import progress_preflight as pp  # noqa: E402

SPEC_HEAD = "| Document revision    | 0.10 |\n\n"
OPEN_HDR = "| ID | Item | Impact | Owner |\n|---|---|---|---|\n"
DEC_HDR = "| ID | Topic | Decision | Basis | Date |\n|---|---|---|---|---|\n"
TASK_HDR = "| ID | Task | Req | Owner | Status | Evidence |\n|---|---|---|---|---|---|\n"
GATE_HDR = "| Gate | Name | Exit | Status |\n|---|---|---|---|\n"


def spec(opens="", decs="", verdict=""):
    return SPEC_HEAD + OPEN_HDR + opens + "\n" + DEC_HDR + decs + "\n## Current verdict\n\n" + verdict + "\n"


def checklist(tasks="", gates="", nxt="", head="**Revision:** 0.1\n"):
    return head + "\n" + GATE_HDR + gates + "\n" + TASK_HDR + tasks + "\n## Current next action\n\n" + nxt + "\n"


def rules(rows):
    return {(r[1].split(":", 1)[1], r[2]) for r in rows}


def run(spec_t, cl_t, readme=None, refs=None, fields=None, revs=None):
    rows, _ = pp.review_items(spec_t, cl_t, readme, refs, fields, (revs or {}).get)
    return rules(rows)


class Synthetic(unittest.TestCase):
    def test_tasks_closed(self):
        cl = checklist("| P1-001 | Do it. | X | H | DONE | rec |\n| P1-002 | Later. | X | H | DEFERRED | - |\n")
        self.assertIn(("tasks_closed", "OPEN-001"),
                      run(spec("| OPEN-001 | Pins. | - | Human / P1 (P1-001) |\n"), cl))
        # a DEFERRED task parks the item: no finding
        self.assertNotIn(("tasks_closed", "OPEN-002"),
                         run(spec("| OPEN-002 | Fw. | - | Software / P1-002 |\n"), cl))
        # a closed item is not checked
        self.assertEqual(set(), run(spec("| OPEN-003 | Closed 2026-01-02: done. | - | Closed |\n"), cl))

    def test_newer_dec_open_row(self):
        s = spec("| OPEN-001 | Margins open (2026-01-01). | - | H / P1-001 |\n",
                 "| DEC-001 | Margins | Accept | Owner (OPEN-001) | 2026-01-02 |\n")
        self.assertIn(("newer_dec", "OPEN-001"), run(s, checklist()))
        s2 = spec("| OPEN-001 | Margins accepted (DEC-001, 2026-01-02). | - | H |\n",
                  "| DEC-001 | Margins | Accept | Owner (OPEN-001) | 2026-01-02 |\n")
        self.assertNotIn(("newer_dec", "OPEN-001"), run(s2, checklist()))

    def test_newer_dec_task_via_open(self):
        s = spec("| OPEN-001 | Margins. | - | H |\n",
                 "| DEC-001 | Margins | Accept | Owner (OPEN-001) | 2026-01-02 |\n")
        cl = checklist("| P1-001 | Clock 2026-01-02. Open: accept the margins (OPEN-001). | X | H | IN_PROGRESS | - |\n")
        self.assertIn(("newer_dec", "P1-001"), run(s, cl))
        # the OPEN is only history (before the marker): no finding
        cl2 = checklist("| P1-001 | Clock (OPEN-001) 2026-01-02. Open: bench check. | X | H | IN_PROGRESS | - |\n")
        self.assertNotIn(("newer_dec", "P1-001"), run(s, cl2))

    def test_field_filled(self):
        fields = {"R1": {"MFR", "MFR.P/N", "LCSC"}, "R2": {"MFR", "MFR.P/N", "LCSC"}, "C1": {"LCSC"}}
        refs = set(fields)
        cl = checklist("| P2-001 | Fill MFR and MFR.P/N on R1 to R2. | X | H | OPEN | - |\n")
        self.assertIn(("field_filled", "P2-001"), run(spec(), cl, refs=refs, fields=fields))
        s = spec("| OPEN-001 | Part numbers. Passive MFR: the owner chooses them later. | - | H / P2-001 |\n")
        self.assertNotIn(("field_filled", "OPEN-001"), run(s, cl, refs=refs, fields=fields))  # C1 has no MFR
        fields["C1"] |= {"MFR"}
        self.assertIn(("field_filled", "OPEN-001"), run(s, cl, refs=refs, fields=fields))
        # "LCSC C123" is a value, not a wait
        s2 = spec("| OPEN-002 | CN1 drawn, not decided (LCSC C32713262). | - | H / P2-001 |\n")
        self.assertNotIn(("field_filled", "OPEN-002"), run(s2, cl, refs=refs, fields=fields))

    def test_ref_missing(self):
        refs = {"R101", "R102", "B901", "Q101", "C101"}
        s = spec("| OPEN-001 | Old. Still open: check R315 and the button B? (team, Q10; ESD C7519). | - | H |\n")
        found = run(s, checklist(), refs=refs, fields={r: set() for r in refs})
        self.assertIn(("ref_missing", "OPEN-001"), found)
        rows, _ = pp.review_items(s, checklist(), None, refs, {r: set() for r in refs}, {}.get)
        detail = next(r[3] for r in rows if r[1] == "review:ref_missing")
        self.assertIn("R315", detail)
        self.assertIn("B?", detail)
        self.assertNotIn("Q10", detail)    # shorter than every drawn Q ref: a question number
        self.assertNotIn("C7519", detail)  # longer than every drawn C ref: an LCSC code

    def test_rev_drift(self):
        cl = checklist("| P1-001 | Pins. | X | H | IN_PROGRESS | [PIN.md](PIN.md) rev 0.26 |\n",
                       head="**Revision:** 0.1\n**Requirements authority:** [SPEC.md](SPEC.md) rev 0.09\n")
        found = run(spec(), cl, readme="**Draft specification (rev 0.08, x)**",
                    revs={"PIN.md": "0.28", "SPEC.md": "0.10"})
        self.assertIn(("rev_drift", "P1-001"), found)
        self.assertIn(("rev_drift", "checklist header"), found)
        self.assertIn(("rev_drift", "README"), found)
        ok = run(spec(), checklist("| P1-001 | Pins. | X | H | DONE | [PIN.md](PIN.md) rev 0.26 |\n"),
                 revs={"PIN.md": "0.28"})
        self.assertNotIn(("rev_drift", "P1-001"), ok)  # DONE evidence keeps its revision

    def test_status_mismatch(self):
        cl = checklist("| P1-001 | A. | X | H | DONE |  |\n| P1-002 | B. | X | H | N/A | See P1-001 |\n",
                       gates="| P1   | Alloc | Exit | OPEN |\n")
        found = run(spec(), cl)
        self.assertIn(("status_mismatch", "P1-001"), found)  # DONE with no evidence
        self.assertIn(("status_mismatch", "P1"), found)      # gate OPEN, all tasks closed
        cl2 = checklist("| P2-001 | A. | X | H | OPEN | - |\n", gates="| P2   | Sch | Exit | DONE (closed) |\n")
        self.assertIn(("status_mismatch", "P2"), run(spec(), cl2))

    def test_summary_cites_closed(self):
        s = spec("| OPEN-001 | Closed 2026-01-02: done. | - | Closed |\n| OPEN-002 | Open thing. | - | H / P1-001 |\n",
                 verdict="Main open risks: sensors (OPEN-002); the INFO names (OPEN-001).")
        cl = checklist("| P1-001 | A. | X | H | DONE | rec |\n",
                       nxt="- Human review of the pins (P1-001).\n- P1-001 closed 2026-01-02.\n")
        readme = "## Open Items\n\n- Names (OPEN-001)\n- Sensors (OPEN-002)\n"
        found = run(s, cl, readme=readme)
        self.assertIn(("summary_cites_closed", "spec verdict"), found)
        self.assertIn(("summary_cites_closed", "checklist next action"), found)
        self.assertIn(("summary_cites_closed", "README open items"), found)
        s_ok = spec("| OPEN-001 | Closed 2026-01-02: done. | - | Closed |\n", verdict="OPEN-001 closed in rev 0.2.")
        self.assertNotIn(("summary_cites_closed", "spec verdict"), run(s_ok, checklist()))


def git(*args):
    out = subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True, encoding="utf-8")
    return out.stdout if out.returncode == 0 else None


DESIGN = "hardware/AO-Horizon/documents/design"
SPEC = f"{DESIGN}/AO-HORIZON_SPEC_EN.md"
CHECK = f"{DESIGN}/AO-HORIZON_EXECUTION_CHECKLIST_EN.md"


@unittest.skipUnless(git("cat-file", "-e", f"a70e6cc:{SPEC}") is not None and git("cat-file", "-e", f"c5166d2:{SPEC}") is not None,
                     "AeroOptix-Horizon history not available")
class Regression(unittest.TestCase):
    """The stale items found by hand on 2026-11-21."""

    @classmethod
    def setUpClass(cls):
        root = Path(git("rev-parse", "--show-toplevel").strip())
        proj = root / "hardware/AO-Horizon"
        ctx = pp.Ctx(root, proj, "10", {}, {}, False, [])
        pp.check_sheets(pp.sheet_files(proj / "AO-Horizon.kicad_sch"), set(), ctx)  # working-tree fields
        cls.refs, cls.fields = ctx.refs, ctx.fields

    def at(self, ref):
        names = [p for p in git("ls-tree", "-r", "--name-only", ref, DESIGN).splitlines() if p.endswith(".md")]

        def rev_of(name):
            path = next((p for p in names if Path(p).name == name), None)
            text = git("show", f"{ref}:{path}") if path else None
            m = pp.REV_HEADER_RE.search(text) if text else None
            return m.group(1) if m else None
        rows, _ = pp.review_items(git("show", f"{ref}:{SPEC}"), git("show", f"{ref}:{CHECK}"),
                                  git("show", f"{ref}:README.md"), self.refs, self.fields, rev_of)
        return rows

    def test_a70e6cc(self):
        found = rules(self.at("a70e6cc"))
        self.assertIn(("field_filled", "OPEN-010"), found)
        self.assertIn(("newer_dec", "P1-014"), found)   # DEC-089 via OPEN-028
        self.assertIn(("rev_drift", "P1-001"), found)   # pin allocation rev 0.26 vs 0.28
        self.assertIn(("rev_drift", "checklist header"), found)  # spec rev 0.72 vs 0.73
        self.assertNotIn(("newer_dec", "OPEN-028"), found)       # its row cites DEC-089
        self.assertNotIn(("ref_missing", "OPEN-010"), found)     # "C7519" is an LCSC code

    def test_c5166d2(self):
        found = rules(self.at("c5166d2"))
        self.assertIn(("field_filled", "P2-021"), found)
        self.assertIn(("summary_cites_closed", "spec verdict"), found)          # OPEN-032, OPEN-039
        self.assertIn(("summary_cites_closed", "checklist next action"), found)  # P1-001
        self.assertIn(("summary_cites_closed", "README open items"), found)     # OPEN-032, OPEN-039
        self.assertNotIn(("field_filled", "OPEN-010"), found)                  # closed in rev 0.78


if __name__ == "__main__":
    unittest.main(verbosity=2)
