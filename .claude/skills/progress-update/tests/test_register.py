#!/usr/bin/env python3
"""Tests for progress-update/scripts/register.py and the review fixes that use it.

Run: python -I -X utf8 .claude/skills/progress-update/tests/test_register.py
Standard library only.
"""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
import progress_preflight as pp  # noqa: E402
import register as reg  # noqa: E402

SPEC = """| Property | Value |
| -------- |---|
| Document revision    | 0.12 |

## 2. References

| Reference | Source | Revision / date | Purpose |
| --------- |---|---|---|
| REF-01    | `CHECKLIST.md` | 0.03 | Tasks |
| REF-02    | Vendor datasheet | Rev F | Data |

## 6. Decisions

| ID | Topic | Selected option | Notes | Date |
| -- |---|---|---|---|
| DEC-001 | Pull-downs (OPEN-002 item 5, P2-001) | 100 k | Owner: "fine". Closes OPEN-002 item 5. | 2026-01-05 |

| ID | Topic | Selected option | Notes | Extra | Date |
| -- |---|---|---|---|---|
| DEC-002 | Clock (OPEN-001) | Osc | Owner | x | 2026-01-06 |

## 8. Open items

| ID | Description | Impact | Owner / next action |
| -- |---|---|---|
| OPEN-001 | Clock margin (2026-01-01). | - | Hardware / P2-002 |
| OPEN-002 | Follow-ups (2026-01-01): (1) headers apart, (5) pull-down value. | - | Hardware / P2-001 |
| OPEN-003 | Closed: done. | - | Closed |

## 9. Change notes

| Revision | Date | Description | Approved by |
| -------- |---|---|---|
| 0.11 | 2026-01-04 | A. | Pending |
| 0.12 | 2026-01-06 | B. | Pending |

```
| DEC-099 | in a code fence | x | y | 2026-01-01 |
```
"""

CHECKLIST = """**Revision:** 0.04

## Gate summary

| Gate | Name | Exit criterion | Status |
| ---- |---|---|---|
| P2   | Schematic | Done when reviewed. | OPEN |

## P2

| ID | Task | Req | Owner | Status | Evidence required / link |
| -- |---|---|---|---|---|
| P2-001 | Pull-downs 2026-01-04. Left: value (OPEN-002). | IF-001 | HW | IN_PROGRESS | - |
| P2-002 | RC IN drawn 2026-01-04. Left: place apart (OPEN-002, item 1). | IF-002 | HW | IN_PROGRESS | - |
| P2-003 | Bad status. | IF-003 | HW | MAYBE | - |
| P2-001 | Duplicate row. | IF-001 | HW | OPEN | - |

## Current next action

- Finish P2.
"""


class Parse(unittest.TestCase):
    def test_tables_and_kinds(self):
        r = reg.records(SPEC)
        self.assertEqual(set(r.kind("dec")), {"DEC-001", "DEC-002"})  # two tables merged, fence skipped
        self.assertEqual(r.kind("dec")["DEC-002"].cells["date"], "2026-01-06")  # by header, not position
        self.assertEqual(set(r.kind("open")), {"OPEN-001", "OPEN-002", "OPEN-003"})
        self.assertEqual(r.kind("ref")["REF-01"].cells["rev"], "0.03")
        self.assertEqual(list(r.kind("note")), ["0.11", "0.12"])
        c = reg.records(CHECKLIST)
        self.assertEqual(c.kind("gate")["P2"].cells["status"], "OPEN")
        self.assertEqual(c.kind("task")["P2-001"].cells["status"], "IN_PROGRESS")
        self.assertEqual(c.duplicates[0][:2], ("task", "P2-001"))

    def test_escaped_pipe(self):
        self.assertEqual(reg.split_row(r"| A | b \| c | d |"), ["A", "b | c", "d"])

    def test_ids_skip_gates_and_revisions(self):
        ids = reg.records(SPEC).ids() | reg.records(CHECKLIST).ids()
        self.assertNotIn("P2", ids)
        self.assertNotIn("0.12", ids)
        self.assertIn("REF-02", ids)


class Lint(unittest.TestCase):
    def finds(self, revs=None, spec=SPEC, cl=CHECKLIST):
        return {(f[1], f[2]) for f in reg.lint(spec, cl, (revs or {}).get)}

    def test_lint_rows(self):
        f = self.finds({"CHECKLIST.md": "0.04"})
        self.assertIn(("review:rev_drift", "REF-01"), f)   # REF cell 0.03, file 0.04
        self.assertIn(("bad_status", "P2-003"), f)
        self.assertIn(("duplicate_id", "P2-001"), f)
        self.assertIn(("closed_no_date", "OPEN-003"), f)
        self.assertNotIn(("review:rev_drift", "REF-02"), f)  # not a Markdown record

    def test_rev_order(self):
        bad = SPEC.replace("| 0.12 | 2026-01-06", "| 0.10 | 2026-01-06")
        f = self.finds(spec=bad)
        self.assertIn(("rev_order", "0.10"), f)
        self.assertIn(("rev_order", "spec header"), f)
        self.assertFalse({x for x in self.finds() if x[0] == "rev_order"})

    def test_long_task(self):
        cl = CHECKLIST.replace("Bad status.", "x" * 700)
        self.assertTrue(any(c == "long_task" for c, _ in self.finds(cl=cl)))


class ItemCites(unittest.TestCase):
    def test_item_cites(self):
        self.assertEqual(pp.item_cites("OPEN-002 item 5, P2-001. Closes OPEN-002 item 5."), {"OPEN-002": {"5"}})
        self.assertEqual(pp.item_cites("OPEN-002 item 5 and OPEN-002"), {})  # one bare cite: whole item
        self.assertEqual(pp.row_items("(1) a, (5) b; items 2 and 7"), {"1", "5", "2", "7"})

    def test_newer_dec_item_qualified(self):
        rows, _ = pp.review_items(SPEC, CHECKLIST, None, None, None, {}.get)
        hit = {(r[1], r[2]) for r in rows}
        # P2-002 waits on OPEN-002 for item 1; DEC-001 settles item 5 only: no finding (the P2-023 case)
        self.assertNotIn(("review:newer_dec", "P2-002"), hit)
        # OPEN-002 names item (5) and does not cite DEC-001: finding
        self.assertIn(("review:newer_dec", "OPEN-002"), hit)
        # P2-001 is cited by DEC-001 directly: finding
        self.assertIn(("review:newer_dec", "P2-001"), hit)



class PickProject(unittest.TestCase):
    def test_ignores_projects_under_dot_claude(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            for rel in ("hw/board.kicad_pro", ".claude/skills/sch-inspect/tests/fixtures/x/x.kicad_pro"):
                f = repo / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("{}", encoding="utf-8")
            self.assertEqual(pp.pick_project(repo, None), repo / "hw" / "board.kicad_pro")


if __name__ == "__main__":
    unittest.main(verbosity=1)
