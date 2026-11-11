#!/usr/bin/env python3
"""Opt-in real-project golden checks for query_sch.py (KiCad 10).

Set two environment variables:
  KICAD_GOLDEN_PROJECT  absolute path of the project's root .kicad_sch
  KICAD_GOLDEN_EXPECT   absolute path of a JSON file with the expected values
                        (format: golden.example.json, and README "Tests and CI")
With either one unset, every test skips.
Run: python .claude/skills/sch-inspect/tests/run_tests.py --pattern test_query_sch_golden.py --label golden
Read-only: executes query_sch.py and hashes all discovered .kicad_sch files before/after.
These tests validate previously observed examples, not complete KiCad netlist parity.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'query_sch.py'
PROJECT_ENV = 'KICAD_GOLDEN_PROJECT'
EXPECT_ENV = 'KICAD_GOLDEN_EXPECT'
# Keys a case may use. An unknown key fails the case, so a typo is not a
# silent pass.
CASE_KEYS = {'name', 'command', 'status', 'has_pins', 'lacks_pins',
             'has_power', 'lacks_power', 'has_global', 'lacks_global',
             'has_sheet_names'}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class KiCadGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw_project = os.environ.get(PROJECT_ENV, '').strip()
        raw_expect = os.environ.get(EXPECT_ENV, '').strip()
        cls.configured = bool(raw_project and raw_expect)
        cls.configuration_error = None
        cls.cases = []
        if not cls.configured:
            return
        cls.project = Path(raw_project).expanduser().resolve()
        expect = Path(raw_expect).expanduser().resolve()
        if not cls.project.is_file() or cls.project.suffix.lower() != '.kicad_sch':
            cls.configuration_error = f'Invalid root schematic: {cls.project}'
            return
        if not SCRIPT.is_file():
            cls.configuration_error = f'Missing script: {SCRIPT}'
            return
        try:
            cls.cases = json.loads(expect.read_text(encoding='utf-8'))['cases']
        except (OSError, ValueError, KeyError, TypeError) as exc:
            cls.configuration_error = f'Invalid expectation file {expect}: {exc!r}'
            return
        if not isinstance(cls.cases, list) or not cls.cases:
            cls.configuration_error = f'No cases in {expect}'
            return
        # Snapshot every schematic in this project directory tree, without editing any.
        cls.files = sorted(cls.project.parent.rglob('*.kicad_sch'))
        cls.before = {str(p): sha256(p) for p in cls.files}

    def setUp(self):
        if not self.configured:
            self.skipTest(f'{PROJECT_ENV} and {EXPECT_ENV} are not both configured')
        if self.configuration_error:
            self.fail(self.configuration_error)

    @classmethod
    def tearDownClass(cls):
        if not cls.configured or cls.configuration_error:
            return
        current = {str(p): sha256(p) for p in cls.files}
        if current != cls.before:
            raise AssertionError('Schematic file hashes changed during query tests')

    def query(self, mode, *args):
        args = [str(a) for a in args]
        process = subprocess.run(
            [sys.executable, str(SCRIPT), mode, *args, '--project', str(self.project),
             '--limit', '200', '--max-files', '1000'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=120, check=False, cwd=str(self.project.parent))
        self.assertEqual(process.returncode, 0,
                         f'{mode} failed (rc={process.returncode}): {process.stderr}')
        try:
            obj = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f'{mode} returned invalid JSON: {exc}: {process.stdout[:400]}')
        self.assertFalse(obj.get('truncated'), f'{mode}: outer result truncated')
        self.assertFalse(obj.get('missing_sheets'), f'{mode}: missing sheets: {obj.get("missing_sheets")}')
        return obj

    def check_case(self, case):
        unknown = set(case) - CASE_KEYS
        self.assertFalse(unknown, f'unknown keys: {sorted(unknown)}')
        command = case.get('command')
        self.assertTrue(isinstance(command, list) and command, 'case needs a "command" list')
        obj = self.query(*command)
        rows = obj.get('results', [])
        if 'has_sheet_names' in case:
            names = {str(r.get('parent_sheet_name') or r.get('name') or '').lower() for r in rows}
            for name in case['has_sheet_names']:
                self.assertIn(name.lower(), names, f'sheet instance not found: {name}')
        result_keys = set(case) & (CASE_KEYS - {'name', 'command', 'has_sheet_names'})
        if not result_keys:
            return
        self.assertEqual(obj.get('total_matches'), 1, 'expected exactly one result')
        result = rows[0]
        if 'status' in case:
            self.assertEqual(result.get('status'), case['status'])
        self.assertFalse(result.get('project_net_verified'), 'Tool must not claim KiCad parity')
        # A truncated list cannot show that a pin or a name is present or absent.
        if result_keys & {'has_pins', 'lacks_pins'}:
            self.assertFalse(result.get('connected_pins_truncated'),
                             'connected pins truncated: has_pins/lacks_pins cannot be checked')
        if result_keys & {'has_power', 'lacks_power', 'has_global', 'lacks_global'}:
            self.assertFalse(result.get('names_truncated'), 'net names truncated')
        pins = {(p.get('reference'), str(p.get('pin_number')))
                for p in result.get('connected_component_pins', [])}
        for ref, number in case.get('has_pins', []):
            self.assertIn((ref, str(number)), pins)
        for ref, number in case.get('lacks_pins', []):
            self.assertNotIn((ref, str(number)), pins)
        for key, field in (('power', 'power_net_names'), ('global', 'global_labels')):
            found = set(result.get(field, []))
            for name in case.get(f'has_{key}', []):
                self.assertIn(name, found, f'{field}: {name} missing')
            for name in case.get(f'lacks_{key}', []):
                self.assertNotIn(name, found, f'{field}: {name} must not be present')

    def test_expected_cases(self):
        for index, case in enumerate(self.cases):
            label = case.get('name', index) if isinstance(case, dict) else index
            with self.subTest(case=label):
                self.assertIsInstance(case, dict)
                self.check_case(case)


if __name__ == '__main__':
    unittest.main()
