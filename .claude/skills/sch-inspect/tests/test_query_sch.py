#!/usr/bin/env python3
"""Black-box regression tests for sch-inspect/scripts/query_sch.py.

Run: python .claude/skills/sch-inspect/tests/run_tests.py --pattern test_query_sch.py --label synthetic
No third-party packages. Uses temporary synthetic .kicad_sch fixtures.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'query_sch.py'
ROOT_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
POWER_SHEET_ID = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
MCU_SHEET_ID = 'cccccccc-cccc-cccc-cccc-cccccccccccc'


def wire(x1, y1, x2, y2):
    return f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})))'


def sheet(name, file, uid, pin_name, x, y):
    return f'''(sheet (at {x} {y}) (size 30 20)
       (property "Sheetname" "{name}") (property "Sheetfile" "{file}")
       (pin "{pin_name}" input (at {x} {y} 0) (uuid "pin-{uid}"))
       (uuid "{uid}"))'''


def lib_symbols():
    return '''(lib_symbols
       (symbol "TEST:OnePin"
         (symbol "OnePin_1_1"
           (pin input line (at 0 0 0) (length 2.54)
             (name "IN") (number "1"))))
       (symbol "power:GND" (power)
         (symbol "GND_1_1"
           (pin power_in line (at 0 0 0) (length 0)
             (name "GND") (number "1"))))
       (symbol "power:PWR_FLAG" (power)
         (symbol "PWR_FLAG_1_1"
           (pin power_out line (at 0 0 0) (length 0)
             (name "pwr") (number "1")))))'''


def component(ref, x, y, uid, path, value='Generic', lib='TEST:OnePin'):
    return f'''(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1)
       (property "Reference" "{ref}") (property "Value" "{value}")
       (uuid "{uid}")
       (instances (project "Test" (path "{path}" (reference "{ref}") (unit 1)))))'''


def content(uid, *blocks):
    return '(kicad_sch (version 20250114) (generator "test") (uuid "' + uid + '")\n' + lib_symbols() + '\n' + '\n'.join(blocks) + '\n)'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QuerySchRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            raise RuntimeError(f'Missing target script: {SCRIPT}')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kicad test ไทย ')
        self.dir = Path(self.temp.name)
        self.root = self.dir / 'Top hierarchical.kicad_sch'
        power = self.dir / 'Power State.kicad_sch'
        mcu = self.dir / 'MCU IOs.kicad_sch'
        self.root.write_text(content(ROOT_ID,
            sheet('Power State', power.name, POWER_SHEET_ID, 'PWM_LI_CH2', 10, 10),
            sheet('MCU IOs', mcu.name, MCU_SHEET_ID, 'PWM_LS_CH2', 30, 10),
            wire(10, 10, 30, 10)), encoding='utf-8')
        power.write_text(content('dddddddd-dddd-dddd-dddd-dddddddddddd',
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}/{POWER_SHEET_ID}'),
            wire(10, 10, 20, 10),
            '(hierarchical_label "PWM_LI_CH2" (at 20 10 0))',
            component('#PWR01', 10, 30, 'gnd1', f'/{ROOT_ID}/{POWER_SHEET_ID}', 'GND', 'power:GND'),
            component('PWR_FLAG1', 10, 30, 'pwrflag1', f'/{ROOT_ID}/{POWER_SHEET_ID}', 'PWR_FLAG', 'power:PWR_FLAG'),
            component('U104', 10, 30, 'u104', f'/{ROOT_ID}/{POWER_SHEET_ID}'),
            wire(10, 30, 15, 30),
            '(label "LOCAL_TEST" (at 15 30 0))',
            component('PWR_FLAG2', 40, 30, 'pwrflag2', f'/{ROOT_ID}/{POWER_SHEET_ID}', 'PWR_FLAG', 'power:PWR_FLAG'),
            component('U105', 40, 30, 'u105', f'/{ROOT_ID}/{POWER_SHEET_ID}'),
            wire(40, 30, 45, 30),
            '(label "OTHER_TEST" (at 45 30 0))'), encoding='utf-8')
        mcu.write_text(content('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
            component('R1', 40, 10, 'r1', f'/{ROOT_ID}/{MCU_SHEET_ID}'),
            wire(20, 10, 40, 10),
            '(hierarchical_label "PWM_LS_CH2" (at 20 10 0))',
            '(global_label "TEST_GLOBAL" (at 40 10 0))'), encoding='utf-8')
        self.files = [self.root, power, mcu]
        self.before = {p: sha(p) for p in self.files}

    def tearDown(self):
        self.assertEqual({p: sha(p) for p in self.files}, self.before,
                         'query_sch.py modified input .kicad_sch files')
        self.temp.cleanup()

    def call(self, *args, project=None, ok=True):
        cmd = [sys.executable, str(SCRIPT), *args, '--project', str(project or self.root)]
        completed = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                                   cwd=self.dir, timeout=25, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if ok:
            self.assertEqual(completed.returncode, 0, f'CMD: {cmd}\nSTDERR: {completed.stderr}')
            self.assertFalse(completed.stderr.strip(), completed.stderr)
            obj = json.loads(completed.stdout)
            self.assertEqual(obj['mode'], args[0])
            self.assertIn('results', obj)
            return obj
        self.assertNotEqual(completed.returncode, 0, f'Unexpected success: {cmd}')
        return completed

    def test_01_summary(self):
        r = self.call('summary')
        self.assertEqual(r['total_matches'], 3)
        self.assertEqual(r['missing_sheets'], [])

    def test_02_component(self):
        r = self.call('component', 'U1')
        self.assertEqual(r['total_matches'], 1)
        self.assertEqual(r['results'][0]['reference_property'], 'U1')

    def test_03_sheet(self):
        r = self.call('sheet', 'MCU IOs')
        self.assertEqual(r['total_matches'], 1)
        self.assertEqual(r['results'][0]['file'], 'MCU IOs.kicad_sch')

    def test_04_pins(self):
        r = self.call('pins', 'U1')
        self.assertEqual(r['total_matches'], 1)
        self.assertEqual(r['results'][0]['pins'][0]['number'], '1')

    def test_05_local_net(self):
        r = self.call('local-net', 'U1')
        p = r['results'][0]['pins'][0]
        self.assertEqual(p['local_connection_status'], 'LOCAL_WIRE_PATH')
        self.assertIn('PWM_LI_CH2', [x['name'] for x in p['interface_labels']])

    def test_06_hier_net(self):
        r = self.call('hier-net', 'U1')
        traces = r['results'][0]['pins'][0]['hierarchical_traces']
        self.assertTrue(any(t['status'] == 'PARENT_LOCAL_PATH_FOUND' for t in traces), traces)

    def test_07_connected_pins(self):
        r = self.call('connected-pins', 'U1')
        traces = r['results'][0]['pins'][0]['hierarchical_traces']
        endpoints = [x for t in traces for x in t.get('connected_sheet_pins', [])]
        self.assertIn('MCU IOs', [x['sheet_name'] for x in endpoints])
        refs = [p['reference'] for x in endpoints for d in x.get('destination_paths', [])
                for p in d.get('connected_component_pins', [])]
        self.assertIn('R1', refs)

    def test_08_instances(self):
        r = self.call('instances')
        self.assertEqual(r['total_matches'], 3)
        self.assertTrue(any(x['parent_sheet_name'] == 'MCU IOs' for x in r['results']))

    def test_09_project_net_regression(self):
        r = self.call('project-net', 'U1', '--pin', '1')
        one = r['results'][0]
        self.assertEqual(one['status'], 'PROJECT_CONNECTIVITY_EVIDENCE')
        refs = {(p['reference'], p['pin_number']) for p in one['connected_component_pins']}
        self.assertIn(('U1', '1'), refs)
        self.assertIn(('R1', '1'), refs, 'Cross-sheet regression: missing destination component')
        self.assertNotIn(('U104', '1'), refs, 'Cross-net contamination')
        self.assertFalse(one['project_net_verified'])

    def test_10_pwr_flag_does_not_merge_unrelated_nets(self):
        r = self.call('project-net', 'U104', '--pin', '1')
        pins = {(p['reference'], p['pin_number'])
                for p in r['results'][0]['connected_component_pins']}
        self.assertIn(('U104', '1'), pins)
        self.assertNotIn(('U105', '1'), pins, 'PWR_FLAG must not bridge unrelated nets')
        self.assertFalse(r['results'][0]['project_net_verified'])

    def test_11_power_symbol(self):
        r = self.call('local-net', 'U104')
        p = r['results'][0]['pins'][0]
        self.assertEqual(p['power_net_status'], 'LOCAL_POWER_SYMBOL_FOUND')
        self.assertIn('GND', [x['name'] for x in p['power_nets']])

    def test_12_missing_target(self):
        r = self.call('component', 'NO_SUCH_REFERENCE')
        self.assertEqual(r['total_matches'], 0)
        r = self.call('project-net', 'NO_SUCH_REFERENCE', '--pin', '1')
        self.assertEqual(r['results'][0]['status'], 'TARGET_NOT_FOUND_OR_UNRESOLVED')

    def test_13_limit_and_invalid_arguments(self):
        r = self.call('summary', '--limit', '1')
        self.assertEqual(len(r['results']), 1)
        self.assertTrue(r['truncated'])
        self.call('summary', '--limit', '0', ok=False)
        self.call('pins', 'U1', '--pin', '1', ok=False)
        self.call('component', ok=False)

    def test_14_root_directory_resolution(self):
        self.call('summary', project=self.dir, ok=False)  # multiple schematic files

    def test_15_malformed_file(self):
        bad = self.dir / 'broken.kicad_sch'
        bad.write_text('(kicad_sch (uuid "oops")', encoding='utf-8')
        self.call('summary', project=bad, ok=False)

    def test_16_malformed_geometry_returns_json_not_traceback(self):
        bad = self.dir / 'bad geometry.kicad_sch'
        bad.write_text(content(ROOT_ID,
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}'),
            '(wire (pts (xy bad 10) (xy 20 10)))'), encoding='utf-8')
        completed = self.call('pins', 'U1', project=bad, ok=False)
        error = json.loads(completed.stderr)
        self.assertEqual(error['verification'], 'NOT_VERIFIED')
        self.assertIn('bad', error['error'])

    def test_17_bus_labels_do_not_union_scalar_local_nets(self):
        # Bus expansion is unsupported.  A bus label must not be used as a
        # scalar local label just because the name matches on another bus.
        root = self.dir / 'bus labels.kicad_sch'
        root.write_text(content(ROOT_ID,
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}'),
            component('R1', 40, 10, 'r1', f'/{ROOT_ID}'),
            wire(10, 10, 20, 10), wire(30, 10, 40, 10),
            '(bus (pts (xy 20 10) (xy 30 10)))',
            '(label "DATA[0..1]" (at 20 10 0))',
            '(label "DATA[0..1]" (at 30 10 0))'), encoding='utf-8')
        r = self.call('project-net', 'U1', '--pin', '1', project=root)
        pins = {(p['reference'], p['pin_number']) for p in r['results'][0]['connected_component_pins']}
        self.assertIn(('U1', '1'), pins)
        self.assertNotIn(('R1', '1'), pins)
        self.assertFalse(r['results'][0]['project_net_verified'])

    def test_18_reused_sheet_instances_remain_distinct(self):
        child = self.dir / 'shared.kicad_sch'
        root = self.dir / 'reused.kicad_sch'
        first = '11111111-1111-1111-1111-111111111111'
        second = '22222222-2222-2222-2222-222222222222'
        root.write_text(content(ROOT_ID,
            sheet('First', child.name, first, 'NET', 10, 10),
            sheet('Second', child.name, second, 'NET', 30, 10)), encoding='utf-8')
        child.write_text(content('dddddddd-dddd-dddd-dddd-dddddddddddd',
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}/{first}'),
            component('U1', 30, 10, 'u1', f'/{ROOT_ID}/{second}'),
            wire(10, 10, 20, 10), wire(30, 10, 40, 10),
            '(hierarchical_label "NET" (at 20 10 0))',
            '(hierarchical_label "NET" (at 40 10 0))'), encoding='utf-8')
        self.files.extend([root, child])
        self.before.update({root: sha(root), child: sha(child)})
        instances = self.call('instances', project=root)
        self.assertEqual(instances['total_matches'], 3)
        query = self.call('project-net', 'U1', '--pin', '1', project=root)
        self.assertEqual(query['results'][0]['status'], 'AMBIGUOUS_TARGET_NETS')
        self.assertFalse(query['results'][0]['project_net_verified'])

    def test_19_cyclic_hierarchy_and_max_files_are_rejected(self):
        child = self.dir / 'cycle-child.kicad_sch'
        root = self.dir / 'cycle-root.kicad_sch'
        edge = '11111111-1111-1111-1111-111111111111'
        back = '22222222-2222-2222-2222-222222222222'
        root.write_text(content(ROOT_ID, sheet('Child', child.name, edge, 'NET', 10, 10)), encoding='utf-8')
        child.write_text(content('dddddddd-dddd-dddd-dddd-dddddddddddd',
            sheet('Root', root.name, back, 'NET', 10, 10)), encoding='utf-8')
        self.files.extend([root, child])
        self.before.update({root: sha(root), child: sha(child)})
        completed = self.call('instances', project=root, ok=False)
        self.assertEqual(json.loads(completed.stderr)['verification'], 'NOT_VERIFIED')
        self.assertIn('cyclic', completed.stderr)

        too_many = self.dir / 'too-many.kicad_sch'
        one = self.dir / 'one.kicad_sch'
        two = self.dir / 'two.kicad_sch'
        too_many.write_text(content(ROOT_ID,
            sheet('One', one.name, edge, 'NET', 10, 10),
            sheet('Two', two.name, back, 'NET', 20, 10)), encoding='utf-8')
        one.write_text(content('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'), encoding='utf-8')
        two.write_text(content('ffffffff-ffff-ffff-ffff-ffffffffffff'), encoding='utf-8')
        self.files.extend([too_many, one, two])
        self.before.update({p: sha(p) for p in (too_many, one, two)})
        completed = self.call('summary', '--max-files', '2', project=too_many, ok=False)
        self.assertEqual(json.loads(completed.stderr)['verification'], 'NOT_VERIFIED')
        self.assertIn('--max-files=2', completed.stderr)

    def test_20_multi_unit_and_inherited_symbols_remain_explicit(self):
        root = self.dir / 'symbols.kicad_sch'
        multi_lib = '''(lib_symbols
          (symbol "TEST:Multi"
            (symbol "Multi_1_1" (pin input line (at 0 0 0) (length 2.54) (name "A") (number "1")))
            (symbol "Multi_2_1" (pin input line (at 5 0 0) (length 2.54) (name "B") (number "2"))))
          (symbol "TEST:Derived" (extends "TEST:Base")
            (symbol "Derived_1_1" (pin input line (at 0 0 0) (length 2.54) (name "X") (number "1")))))'''
        root.write_text('(kicad_sch (version 20250114) (generator "test") (uuid "' + ROOT_ID + '")\n' + multi_lib + '\n' +
            component('U2', 10, 10, 'u2', f'/{ROOT_ID}', lib='TEST:Multi').replace('(unit 1)', '(unit 2)') + '\n' +
            component('U3', 30, 10, 'u3', f'/{ROOT_ID}', lib='TEST:Derived') + '\n)', encoding='utf-8')
        self.files.append(root)
        self.before[root] = sha(root)
        multi = self.call('pins', 'U2', project=root)
        self.assertEqual([p['number'] for p in multi['results'][0]['pins']], ['2'])
        inherited = self.call('pins', 'U3', project=root)
        self.assertEqual(inherited['results'][0]['pins'], [])
        self.assertIn('inherited lib symbol pins are not resolved', inherited['results'][0]['limitations'])

    def test_21_nested_result_truncation_is_reported(self):
        r = self.call('project-net', 'U1', '--pin', '1', '--limit', '1')
        result = r['results'][0]
        self.assertTrue(result['connected_pins_truncated'])
        self.assertLess(len(result['connected_component_pins']), result['total_connected_component_pins'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
