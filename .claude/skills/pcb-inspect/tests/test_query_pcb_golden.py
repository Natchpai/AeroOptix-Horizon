#!/usr/bin/env python3
"""Opt-in real-project golden checks for query_pcb.py (KiCad 10).

Set two environment variables:
  KICAD_PCB_GOLDEN_BOARD   absolute path of the project's .kicad_pcb file
  KICAD_PCB_GOLDEN_EXPECT  absolute path of a JSON file with the expected values
                           (format: golden.example.json, and README "Tests and CI")
With either one unset, every test skips.
Run: python .claude/skills/pcb-inspect/tests/run_tests.py --pattern test_query_pcb_golden.py --label golden
Read-only: hashes the configured board before/after running the query CLI.

Expected values must come from the native PCB text or from KiCad, not from
query_pcb.py output. These tests are scoped regression evidence, not complete
KiCad PCB Editor parity.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'query_pcb.py'
BOARD_ENV = 'KICAD_PCB_GOLDEN_BOARD'
EXPECT_ENV = 'KICAD_PCB_GOLDEN_EXPECT'
# Keys a case may use. An unknown key fails the case, so a typo is not a
# silent pass.
CASE_KEYS = {'name', 'command', 'status', 'fields'}
# One step of a field path: a key, optionally followed by [index] or
# [key=value] selectors, for example  pads[number=1]  or  tracks[0].
STEP = re.compile(r'^([^\[\]]+)((?:\[[^\[\]]+\])*)$')
SELECTOR = re.compile(r'\[([^\[\]]+)\]')
MISSING = object()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(obj, path):
    """Follow a dotted field path through dicts and lists; MISSING if absent.

    Dots separate steps. A step may end with [n] (list index) or
    [key=value] (the single list item whose key has that value as text).
    """
    current = obj
    for step in path.split('.'):
        match = STEP.match(step)
        if not match:
            raise ValueError(f'invalid field path step: {step!r}')
        if not isinstance(current, dict) or match.group(1) not in current:
            return MISSING
        current = current[match.group(1)]
        for selector in SELECTOR.findall(match.group(2)):
            if not isinstance(current, list):
                return MISSING
            if '=' in selector:
                key, wanted = selector.split('=', 1)
                found = [item for item in current if isinstance(item, dict) and str(item.get(key)) == wanted]
                if len(found) != 1:
                    return MISSING
                current = found[0]
            else:
                index = int(selector)
                if index >= len(current):
                    return MISSING
                current = current[index]
    return current


class KiCadPcbGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw_board = os.environ.get(BOARD_ENV, '').strip()
        raw_expect = os.environ.get(EXPECT_ENV, '').strip()
        cls.configured = bool(raw_board and raw_expect)
        cls.configuration_error = None
        cls.cases = []
        if not cls.configured:
            return
        cls.board = Path(raw_board).expanduser().resolve()
        expect = Path(raw_expect).expanduser().resolve()
        if not cls.board.is_file() or cls.board.suffix.lower() != '.kicad_pcb':
            cls.configuration_error = f'Invalid PCB board: {cls.board}'
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
        cls.before = sha256(cls.board)

    def setUp(self):
        if not self.configured:
            self.skipTest(f'{BOARD_ENV} and {EXPECT_ENV} are not both configured')
        if self.configuration_error:
            self.fail(self.configuration_error)

    @classmethod
    def tearDownClass(cls):
        if not cls.configured or cls.configuration_error:
            return
        if sha256(cls.board) != cls.before:
            raise AssertionError('PCB board content changed during query tests')

    def query(self, command, *args):
        args = [str(a) for a in args]
        process = subprocess.run(
            [sys.executable, str(SCRIPT), command, *args, '--board', str(self.board), '--limit', '200'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=120, check=False, cwd=str(self.board.parent))
        self.assertEqual(process.returncode, 0,
                         f'{command} failed (rc={process.returncode}): {process.stderr}')
        try:
            obj = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f'{command} returned invalid JSON: {exc}: {process.stdout[:400]}')
        return obj

    def check_case(self, case):
        unknown = set(case) - CASE_KEYS
        self.assertFalse(unknown, f'unknown keys: {sorted(unknown)}')
        command = case.get('command')
        self.assertTrue(isinstance(command, list) and command, 'case needs a "command" list')
        self.assertTrue('status' in case or case.get('fields'), 'case checks nothing: add "status" or "fields"')
        obj = self.query(*command)
        if 'status' in case:
            self.assertEqual(obj.get('status'), case['status'])
        fields = case.get('fields', {})
        self.assertIsInstance(fields, dict, '"fields" must map a field path to its expected value')
        for path, expected in fields.items():
            actual = resolve(obj, path)
            self.assertIsNot(actual, MISSING, f'{path}: not in the output (or not exactly one match)')
            self.assertEqual(actual, expected, path)

    def test_expected_cases(self):
        for index, case in enumerate(self.cases):
            label = case.get('name', index) if isinstance(case, dict) else index
            with self.subTest(case=label):
                self.assertIsInstance(case, dict)
                self.check_case(case)


if __name__ == '__main__':
    unittest.main()
