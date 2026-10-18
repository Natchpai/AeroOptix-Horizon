#!/usr/bin/env python3
"""Opt-in real-project golden checks for query_sch.py (KiCad 10).

Set KICAD_GOLDEN_PROJECT to the absolute path of Top_hierarchical.kicad_sch.
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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class KiCadGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw_project = os.environ.get(PROJECT_ENV, '').strip()
        cls.configured = bool(raw_project)
        cls.project = Path(raw_project).expanduser().resolve() if cls.configured else None
        cls.configuration_error = None
        if not cls.configured:
            return
        if not cls.project.is_file() or cls.project.suffix.lower() != '.kicad_sch':
            cls.configuration_error = f'Invalid root schematic: {cls.project}'
            return
        if not SCRIPT.is_file():
            cls.configuration_error = f'Missing script: {SCRIPT}'
            return
        # Snapshot every schematic in this project directory tree, without editing any.
        cls.files = sorted(cls.project.parent.rglob('*.kicad_sch'))
        cls.before = {str(p): sha256(p) for p in cls.files}

    def setUp(self):
        if not self.configured:
            self.skipTest(f'{PROJECT_ENV} is not configured')
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

    def test_instances_have_expected_named_sheets(self):
        obj = self.query('instances')
        rows = obj.get('results', [])
        names = {str(r.get('parent_sheet_name', r.get('sheet_name', r.get('name', '')))).lower() for r in rows}
        joined = ' '.join(names)
        self.assertIn('power state', joined, 'Power State instance not found')
        self.assertIn('mcu ios', joined, 'MCU IOs instance not found')

    def test_project_net_reaches_r506_pin_1(self):
        obj = self.query('project-net', 'U103', '--pin', '8')
        self.assertEqual(obj.get('total_matches'), 1)
        result = obj['results'][0]
        self.assertEqual(result.get('status'), 'PROJECT_CONNECTIVITY_EVIDENCE')
        self.assertFalse(result.get('connected_pins_truncated'))
        pins = {(p.get('reference'), str(p.get('pin_number'))) for p in result.get('connected_component_pins', [])}
        self.assertIn(('U103', '8'), pins)
        self.assertIn(('R506', '1'), pins, 'Cross-sheet regression: R506 pin 1 missing')
        self.assertFalse(result.get('project_net_verified'), 'Tool must not claim KiCad parity')

    def test_pin_9_and_11_resolve_ground(self):
        for number in ('9', '11'):
            with self.subTest(pin=number):
                obj = self.query('project-net', 'U103', '--pin', number)
                self.assertEqual(obj.get('total_matches'), 1)
                result = obj['results'][0]
                self.assertEqual(result.get('status'), 'PROJECT_CONNECTIVITY_EVIDENCE')
                names = set(result.get('power_net_names', []))
                self.assertIn('GND', names, f'U103 pin {number}: expected GND power net')

    def test_power_nets_remain_distinct(self):
        plus9 = self.query('project-net', 'U103', '--pin', '1')['results'][0]
        gnd9 = self.query('project-net', 'U103', '--pin', '9')['results'][0]
        gnd11 = self.query('project-net', 'U103', '--pin', '11')['results'][0]

        plus9_pins = {(p.get('reference'), str(p.get('pin_number')))
                      for p in plus9.get('connected_component_pins', [])}
        gnd9_pins = {(p.get('reference'), str(p.get('pin_number')))
                     for p in gnd9.get('connected_component_pins', [])}
        gnd11_pins = {(p.get('reference'), str(p.get('pin_number')))
                      for p in gnd11.get('connected_component_pins', [])}

        self.assertIn('+9V', set(plus9.get('power_net_names', [])))
        self.assertNotIn('GND', set(plus9.get('power_net_names', [])))
        self.assertIn('GND', set(gnd9.get('power_net_names', [])))
        self.assertNotIn('+9V', set(gnd9.get('power_net_names', [])))
        self.assertIn('GND', set(gnd11.get('power_net_names', [])))
        self.assertNotIn('+9V', set(gnd11.get('power_net_names', [])))

        self.assertNotIn(('U103', '9'), plus9_pins)
        self.assertNotIn(('U103', '11'), plus9_pins)
        self.assertNotIn(('U103', '1'), gnd9_pins)
        self.assertNotIn(('U103', '1'), gnd11_pins)

    def test_unrelated_known_pin_not_merged_with_pwm(self):
        # U103 LO pin 10 was observed on DRV_LO2, not PWM_LI_CH2.
        obj = self.query('project-net', 'U103', '--pin', '8')
        pins = {(p.get('reference'), str(p.get('pin_number'))) for p in obj['results'][0].get('connected_component_pins', [])}
        self.assertNotIn(('U103', '10'), pins, 'False-positive merge with U103 LO pin 10')


if __name__ == '__main__':
    unittest.main()
