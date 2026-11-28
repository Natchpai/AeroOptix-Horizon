#!/usr/bin/env python3
"""Tests for progress-update/scripts/sch_state.py.

Run: python -I -X utf8 .claude/skills/progress-update/tests/test_sch_state.py
Standard library only. Uses the sch-inspect netlist fixture; no kicad-cli.
"""
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
import sch_state as ss  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[2] / "sch-inspect" / "tests" / "fixtures" / "netlist_small"


class SchState(unittest.TestCase):
    def test_compress_runs(self):
        self.assertEqual(ss.compress(["R903", "R901", "R902", "R905"]), "R901 to R903, R905")
        self.assertEqual(ss.compress(["C1", "C2"]), "C1, C2")
        self.assertEqual(ss.compress(["U1"]), "U1")

    def test_render_from_fixture(self):
        q = ss.query_module()
        text = (FIXTURE / "netlist_small.xml").read_text(encoding="utf-8")
        md = ss.render(q.parse_netlist_parts(text), q.parse_netlist(text)[1], "a test netlist", "2026-01-01")
        self.assertIn("# Schematic State (generated)", md)
        self.assertIn("Do not edit by hand", md)
        self.assertNotIn(chr(0x2014), md)  # no em dash
        self.assertIn("| References | Value | MFR.P/N | LCSC | DNP | STATUS |", md)
        # D0, D1 and COM join the root sheet and the child sheet
        self.assertIn("Nets to other sheets:", md)
        self.assertIn("`COM`", md)

    def test_cli_with_netlist(self):
        done = subprocess.run([sys.executable, "-I", str(SCRIPTS / "sch_state.py"), "--project",
                               str(FIXTURE / "netlist_small.kicad_sch"), "--netlist",
                               str(FIXTURE / "netlist_small.xml")],
                              capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("parts)", done.stdout)
        bad = subprocess.run([sys.executable, "-I", str(SCRIPTS / "sch_state.py"), "--project", "x.kicad_sch",
                              "--netlist", "missing.xml"], capture_output=True, text=True, timeout=60)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("NOT_VERIFIED", bad.stderr)


if __name__ == "__main__":
    unittest.main()
