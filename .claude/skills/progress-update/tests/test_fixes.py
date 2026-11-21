#!/usr/bin/env python3
"""Regression tests for parser and check bugs fixed in register.py and progress_preflight.py.

Run: python -I -X utf8 .claude/skills/progress-update/tests/test_fixes.py
Standard library only. The git cases need git on PATH and skip without it.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
import progress_preflight as pp  # noqa: E402
import register as reg  # noqa: E402

TASK_HDR = "| ID | Task | Req | Owner | Status | Evidence |\n|---|---|---|---|---|---|\n"
OPEN_HDR = "| ID | Description | Impact | Owner / next action |\n|---|---|---|---|\n"
NOTE_HDR = "| Revision | Date | Description | Approved by |\n|---|---|---|---|\n"
EM = chr(0x2014)  # em dash, kept out of the source text


def lint_rules(spec, cl):
    return {(f[1], f[2]) for f in reg.lint(spec, cl)}


def review_rules(spec, cl, readme=None):
    rows, _ = pp.review_items(spec, cl, readme, None, None, {}.get)
    return {(r[1].split(":", 1)[1], r[2]) for r in rows}


def make_ctx(root: Path, finds: list) -> pp.Ctx:
    return pp.Ctx(root, root, "", {}, {}, False, finds)


class StatusWords(unittest.TestCase):
    def test_bold_and_title_case_status_still_a_task_table(self):  # U1
        cl = TASK_HDR + "| P2-001 | t | | | **DONE** | ev |\n| P2-002 | u | | | Done | ev |\n"
        tasks = reg.records(cl).kind("task")
        self.assertIn("P2-001", tasks)
        rules = lint_rules(OPEN_HDR, cl)
        self.assertIn(("bad_status", "P2-001"), rules)
        self.assertIn(("bad_status", "P2-002"), rules)

    def test_blocked_needs_by_id(self):  # U7
        cl = TASK_HDR + ("| P2-001 | t | | | BLOCKED | ev |\n"
                         "| P2-002 | t | | | BLOCKED (waiting) | ev |\n"
                         "| P2-003 | t | | | BLOCKED BY P2-001 | ev |\n")
        rules = lint_rules(OPEN_HDR, cl)
        self.assertIn(("bad_status", "P2-001"), rules)
        self.assertIn(("bad_status", "P2-002"), rules)
        self.assertNotIn(("bad_status", "P2-003"), rules)


class Revisions(unittest.TestCase):
    def test_template_revision_row(self):  # U3
        text = "# Execution Checklist: X\n\n| Field | Value |\n|---|---|\n| Revision            | 0.1 |\n"
        self.assertEqual("0.1", reg.doc_revision(text))
        self.assertEqual("0.1", pp.REV_HEADER_RE.search(text).group(1))

    def test_duplicate_change_note_revision(self):  # U6
        spec = NOTE_HDR + "| 0.2 | 2026-01-01 | a | x |\n| 0.2 | 2026-01-02 | b | x |\n| 0.3 | 2026-01-03 | c | x |\n"
        self.assertIn(("rev_order", "0.2"), lint_rules(spec, None))


class ClosedRows(unittest.TestCase):
    def test_closed_loop_is_not_closed(self):  # U4
        spec = OPEN_HDR + "| OPEN-001 | Closed-loop gimbal control gain not verified | x | H / P2-001 |\n"
        cl = TASK_HDR + "| P2-001 | t | | | DONE | ev |\n"
        self.assertIn(("tasks_closed", "OPEN-001"), review_rules(spec, cl))
        self.assertNotIn(("closed_no_date", "OPEN-001"), lint_rules(spec, cl))

    def test_documented_closed_forms_still_closed(self):  # U4 guard
        spec = OPEN_HDR + ("| OPEN-001 | Closed 2026-01-02: done. | - | Closed |\n"
                           "| OPEN-002 | Closed: done. | - | Closed |\n")
        cl = TASK_HDR + "| P2-001 | t | | | DONE | ev |\n"
        rules = lint_rules(spec, cl)
        self.assertNotIn(("closed_no_date", "OPEN-001"), rules)
        self.assertIn(("closed_no_date", "OPEN-002"), rules)
        self.assertFalse({r for r in review_rules(spec, cl) if r[0] == "tasks_closed"})


class BacktickIds(unittest.TestCase):
    def test_backticked_ids_read(self):  # U5
        spec = OPEN_HDR + "| `OPEN-001` | a | - | H |\n| `OPEN-001` | b | - | H |\n"
        r = reg.records(spec)
        self.assertIn("OPEN-001", r.kind("open"))
        self.assertEqual(1, len(r.duplicates))


class SummaryHeadings(unittest.TestCase):
    def test_readme_open_items_subsection(self):  # U13
        spec = OPEN_HDR + "| OPEN-001 | Closed 2026-01-02: done. | - | Closed |\n"
        cl = TASK_HDR + "| P2-001 | t | | | OPEN | - |\n"
        readme = "# X\n\n## Project Status\n\n### Open items\n\n- OPEN-001 clock margin\n\n## Hardware Design\n"
        self.assertIn(("summary_cites_closed", "README open items"), review_rules(spec, cl, readme))


@unittest.skipUnless(shutil.which("git"), "git not on PATH")
class GitDocs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

        def g(*a):
            subprocess.run(["git", "-C", str(self.repo), *a], check=True, capture_output=True)
        self.g = g
        g("init", "-q")
        g("config", "user.email", "t@example.invalid")
        g("config", "user.name", "t")
        for p in ("docs/a.md", ".claude/skills/s/SKILL.md", "p-backups/b.md"):
            f = self.repo / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("start\n", encoding="utf-8")
        g("add", "-A")
        g("commit", "-q", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def docs(self, mds, finds):
        return pp.check_docs(self.repo, "HEAD", mds, set(), None, None, [], "OPEN", "OI", finds)

    def test_em_dash_ignores_claude_and_backups(self):  # U2
        for p in (".claude/skills/s/SKILL.md", "p-backups/b.md"):
            (self.repo / p).write_text(f"start\nnew {EM} line\n", encoding="utf-8")
        finds = []
        self.assertEqual(0, self.docs(["docs/a.md"], finds)["em_dash_lines"])
        (self.repo / "docs/a.md").write_text(f"start\nnew {EM} line\n", encoding="utf-8")
        self.assertEqual(1, self.docs(["docs/a.md"], [])["em_dash_lines"])

    def test_deleted_tracked_md_does_not_crash(self):  # U8
        (self.repo / "docs/a.md").unlink()
        self.docs(["docs/a.md"], [])
        self.assertIsNone(pp.find_doc(self.repo, ["docs/a.md"], "SPEC", "specification"))

    def test_anchor_links(self):  # U9
        (self.repo / "docs/a.md").write_text(
            "start\n[x](#sec) [y](a.md#sec) [z](missing.md#sec)\n", encoding="utf-8")
        finds = []
        self.docs(["docs/a.md"], finds)
        broken = {f[2] for f in finds if f[1] == "broken_link"}
        self.assertEqual({"docs/a.md -> missing.md#sec"}, broken)


SCH = """(kicad_sch (version 20250114) (generator "eeschema")
 (symbol (lib_id "Device:R") (at 0 0 0)
  (property "Reference" "R1" (at 0 0 0)) (property "Value" "10k" (at 0 0 0))
  (property "LCSC" "C25804" (at 0 0 0)) (property "MFR.P/N" "PART-A" (at 0 0 0)))
 (symbol (lib_id "Device:R") (at 0 0 0)
  (property "Reference" "R2" (at 0 0 0)) (property "Value" "10k" (at 0 0 0))
  (property "LCSC" "C25804" (at 0 0 0)) (property "MFR.P/N" "PART-B" (at 0 0 0)))
)
"""

SYM = """(kicad_symbol_lib (version 20241209) (generator "t")
 (symbol "IC1" (property "Footprint" "" (at 0 0 0))
  (symbol "IC1_1_1"
   (pin input line (at 0 0 0) (length 2.54) (name "~{RESET}" (effects)) (number "3" (effects)))))
)
"""


class SchematicChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_lcsc_conflict_uses_mfr_pn(self):  # U10
        sch = self.root / "a.kicad_sch"
        sch.write_text(SCH, encoding="utf-8")
        finds = []
        pp.check_sheets([sch], set(), make_ctx(self.root, finds))
        self.assertTrue(any(f[1] == "lcsc_conflict" for f in finds))

    def test_sheet_outside_project_folder(self):  # U12
        proj = self.root / "proj"
        proj.mkdir()
        sch = self.root / "shared.kicad_sch"
        sch.write_text(SCH, encoding="utf-8")
        out = pp.check_sheets([sch], set(), pp.Ctx(self.root, proj, "", {}, {}, False, []))
        self.assertEqual(1, len(out))

    def test_overbar_pin_name_matches_text(self):  # U11
        sym = self.root / "lib.kicad_sym"
        sym.write_text(SYM, encoding="utf-8")
        for text in ("3 RESET Reset input\n", "3 ~RESET Reset input\n"):
            finds = []
            pp.check_library([sym], [], {"IC1": text}, make_ctx(self.root, finds))
            self.assertFalse([f for f in finds if f[1] == "pin_text_mismatch"], text)


if __name__ == "__main__":
    unittest.main()
