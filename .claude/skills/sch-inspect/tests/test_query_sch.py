#!/usr/bin/env python3
"""Black-box regression tests for sch-inspect/scripts/query_sch.py.

Run: python .claude/skills/sch-inspect/tests/run_tests.py --pattern test_query_sch.py --label synthetic
No third-party packages. Uses temporary synthetic .kicad_sch fixtures.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
       (symbol "0_Power:GND" (power)
         (symbol "GND_1_1"
           (pin power_in line (at 0 0 0) (length 0)
             (name "GND") (number "1"))))
       (symbol "power:VBUS" (power)
         (symbol "VBUS_1_1"
           (pin power_in line (at 0 0 0) (length 0)
             (name "VBUS") (number "1"))))
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

    def test_22_each_mode_prints_its_own_verification_and_limitations(self):
        expected = {
            'summary': ((), 'STRUCTURAL_DISCOVERY_ONLY'),
            'component': (('U1',), 'STRUCTURAL_DISCOVERY_ONLY'),
            'sheet': (('MCU IOs',), 'STRUCTURAL_DISCOVERY_ONLY'),
            'pins': (('U1',), 'LOCAL_GEOMETRY_EVIDENCE_ONLY'),
            'local-net': (('U1',), 'SHEET_LOCAL_ONLY'),
            'hier-net': (('U1',), 'HIERARCHICAL_INTERFACE_EVIDENCE_ONLY'),
            'connected-pins': (('U1',), 'PARENT_CONNECTED_PINS_GEOMETRY_ONLY'),
            'project-net': (('U1', '--pin', '1'), 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY'),
            'instances': ((), 'HIERARCHICAL_INSTANCE_DISCOVERY_ONLY'),
            'net': (('TEST_GLOBAL',), 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY'),
            'components': ((), 'STRUCTURAL_DISCOVERY_ONLY'),
        }
        for mode, (args, verification) in expected.items():
            with self.subTest(mode=mode):
                r = self.call(mode, *args)
                self.assertEqual(r['verification'], verification)
                self.assertTrue(r['limitations'])
        # project-net and instances are instance-aware: the structural
        # discovery limitations must not be printed for them.
        for mode, args in (('project-net', ('U1', '--pin', '1')), ('instances', ())):
            with self.subTest(limitations=mode):
                text = ' '.join(self.call(mode, *args)['limitations'])
                self.assertNotIn('No electrical connectivity or pin-net verification', text)
                self.assertNotIn('not expanded into unique hierarchical instances', text)
        project = self.call('project-net', 'U1', '--pin', '1')
        self.assertIn('not KiCad netlist parity', ' '.join(project['limitations']))
        self.assertEqual(project['limitations'], project['results'][0]['limitations'])

    def test_23_skill_md_lists_every_verification_value(self):
        # Fails when the script gains a verification value or a command that
        # the JSON contract in SKILL.md does not name.
        spec = importlib.util.spec_from_file_location('_query_sch_under_test', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        skill = (SCRIPT.parents[1] / 'SKILL.md').read_text(encoding='utf-8')
        start = skill.index('## JSON contract')
        contract = skill[start:skill.index('\n## ', start + 1)]
        for mode, info in module.MODES.items():
            with self.subTest(mode=mode):
                self.assertIn(f'`{info["verification"]}`', contract)
                self.assertIn(f'`{mode}`', contract)
        self.assertIn('`NOT_VERIFIED`', contract)

    def test_24_power_symbol_outside_power_library_is_not_a_component(self):
        # Power symbols are found by the (power) flag of the library symbol,
        # not by the "power:" library name.
        root = self.dir / 'project power lib.kicad_sch'
        root.write_text(content(ROOT_ID,
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}'),
            wire(10, 10, 20, 10),
            component('#PWR01', 20, 10, 'gnd1', f'/{ROOT_ID}', 'GND', '0_Power:GND'),
            component('U2', 40, 10, 'u2', f'/{ROOT_ID}'),
            wire(40, 10, 50, 10),
            component('#PWR02', 50, 10, 'gnd2', f'/{ROOT_ID}', 'GND', '0_Power:GND')), encoding='utf-8')
        self.files.append(root)
        self.before[root] = sha(root)
        one = self.call('project-net', 'U1', '--pin', '1', project=root)['results'][0]
        refs = {p['reference'] for p in one['connected_component_pins']}
        self.assertEqual(refs, {'U1', 'U2'})
        self.assertEqual(one['power_net_names'], ['GND'])

    def test_25_global_label_and_power_symbol_with_one_name_are_one_net(self):
        first = '11111111-1111-1111-1111-111111111111'
        second = '22222222-2222-2222-2222-222222222222'
        root = self.dir / 'vbus root.kicad_sch'
        a = self.dir / 'vbus label.kicad_sch'
        b = self.dir / 'vbus power.kicad_sch'
        root.write_text(content(ROOT_ID,
            sheet('Label side', a.name, first, 'UNUSED_A', 10, 10),
            sheet('Power side', b.name, second, 'UNUSED_B', 60, 10)), encoding='utf-8')
        a.write_text(content('dddddddd-dddd-dddd-dddd-dddddddddddd',
            component('U1', 10, 10, 'u1', f'/{ROOT_ID}/{first}'),
            wire(10, 10, 20, 10),
            '(global_label "VBUS" (at 20 10 0))'), encoding='utf-8')
        b.write_text(content('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
            component('U2', 10, 10, 'u2', f'/{ROOT_ID}/{second}'),
            wire(10, 10, 20, 10),
            component('#PWR01', 20, 10, 'vbus1', f'/{ROOT_ID}/{second}', 'VBUS', 'power:VBUS'),
            component('U3', 10, 30, 'u3', f'/{ROOT_ID}/{second}'),
            wire(10, 30, 20, 30),
            '(label "VBUS" (at 20 30 0))'), encoding='utf-8')
        self.files.extend([root, a, b])
        self.before.update({x: sha(x) for x in (root, a, b)})
        for start, other in (('U1', 'U2'), ('U2', 'U1')):
            with self.subTest(start=start):
                one = self.call('project-net', start, '--pin', '1', project=root)['results'][0]
                refs = {p['reference'] for p in one['connected_component_pins']}
                self.assertEqual(refs, {'U1', 'U2'})
                self.assertEqual(one['global_labels'], ['VBUS'])
                self.assertEqual(one['power_net_names'], ['VBUS'])
        # A local label with the same text stays local to its sheet.
        local = self.call('project-net', 'U3', '--pin', '1', project=root)['results'][0]
        self.assertEqual({p['reference'] for p in local['connected_component_pins']}, {'U3'})

    def test_26_mirror_is_applied_after_rotation(self):
        # KiCad rotates the symbol, then mirrors it on the canvas axis.
        # Checked against a KiCad 10.0.8 netlist of a real project for
        # mirror x at 90 and 270 degrees. Mirror y at 90 and 270 uses the same
        # rule but has no real-project evidence yet (NOT_VERIFIED).
        lib = '''(lib_symbols
          (symbol "TEST:Tri"
            (symbol "Tri_1_1"
              (pin input line (at -5.08 2.54 0) (length 2.54) (name "A") (number "1"))
              (pin input line (at 5.08 2.54 180) (length 2.54) (name "B") (number "2"))
              (pin input line (at 0 -5.08 90) (length 2.54) (name "C") (number "3")))))'''
        expected = {
            ('x', 0): {'1': [94.92, 52.54], '2': [105.08, 52.54], '3': [100.0, 44.92]},
            ('x', 90): {'1': [97.46, 44.92], '2': [97.46, 55.08], '3': [105.08, 50.0]},
            ('x', 270): {'1': [102.54, 55.08], '2': [102.54, 44.92], '3': [94.92, 50.0]},
            ('y', 90): {'1': [102.54, 55.08], '2': [102.54, 44.92], '3': [94.92, 50.0]},
            ('y', 270): {'1': [97.46, 44.92], '2': [97.46, 55.08], '3': [105.08, 50.0]},
        }
        for (axis, angle), pins in expected.items():
            with self.subTest(mirror=axis, angle=angle):
                root = self.dir / f'mirror {axis} {angle}.kicad_sch'
                placed = component('U9', 100, 50, 'u9', f'/{ROOT_ID}', lib='TEST:Tri')
                placed = placed.replace('(at 100 50 0)', f'(at 100 50 {angle}) (mirror {axis})')
                root.write_text('(kicad_sch (version 20250114) (generator "test") (uuid "' + ROOT_ID + '")\n'
                                + lib + '\n' + placed + '\n)', encoding='utf-8')
                self.files.append(root)
                self.before[root] = sha(root)
                got = {x['number']: x['position_mm']
                       for x in self.call('pins', 'U9', project=root)['results'][0]['pins']}
                self.assertEqual(got, pins)

    def net_pins(self, result):
        return {(p['reference'], p['pin_number']) for p in result['connected_component_pins']}

    def test_27_net_starts_from_each_kind_of_name(self):
        cases = {
            'TEST_GLOBAL': ('global_label', {('U1', '1'), ('R1', '1')}),
            'PWM_LI_CH2': ('hierarchical_label', {('U1', '1'), ('R1', '1')}),
            'GND': ('power_symbol', {('U104', '1')}),
            'LOCAL_TEST': ('label', {('U104', '1')}),
        }
        for name, (kind, pins) in cases.items():
            with self.subTest(net=name):
                r = self.call('net', name)
                self.assertEqual(r['verification'], 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY')
                self.assertEqual(r['total_matches'], 1)
                one = r['results'][0]
                self.assertEqual(one['status'], 'PROJECT_CONNECTIVITY_EVIDENCE')
                self.assertEqual(one['net_name'], name)
                self.assertIn(kind, [m['kind'] for m in one['matched_by']])
                self.assertEqual(self.net_pins(one), pins)
                self.assertFalse(one['project_net_verified'])
                self.assertFalse(one['connected_pins_truncated'])
        # Same evidence as project-net from a pin on that net.
        by_pin = self.call('project-net', 'U1', '--pin', '1')['results'][0]
        by_name = self.call('net', 'TEST_GLOBAL')['results'][0]
        for field in ('connected_component_pins', 'global_labels', 'power_net_names', 'groups_visited'):
            self.assertEqual(by_name[field], by_pin[field])

    def test_28_net_unknown_name_truncation_and_arguments(self):
        r = self.call('net', 'NO_SUCH_NET')
        self.assertEqual(r['results'][0]['status'], 'NET_NAME_NOT_FOUND')
        self.assertFalse(r['results'][0]['project_net_verified'])
        self.assertEqual(self.call('net', 'test_global')['results'][0]['status'], 'NET_NAME_NOT_FOUND')
        one = self.call('net', 'TEST_GLOBAL', '--limit', '1')['results'][0]
        self.assertTrue(one['connected_pins_truncated'])
        self.assertEqual(one['total_connected_component_pins'], 2)
        self.call('net', ok=False)
        self.call('net', 'GND', '--pin', '1', ok=False)
        self.call('net', 'GND', '--prefix', 'U', ok=False)

    def reused_project(self):
        child = self.dir / 'shared.kicad_sch'
        root = self.dir / 'reused.kicad_sch'
        first = '11111111-1111-1111-1111-111111111111'
        second = '22222222-2222-2222-2222-222222222222'
        root.write_text(content(ROOT_ID,
            sheet('First', child.name, first, 'UNUSED', 10, 10),
            sheet('Second', child.name, second, 'UNUSED', 60, 10)), encoding='utf-8')
        placed = component('U1', 10, 10, 'u1', f'/{ROOT_ID}/{first}').replace(
            '(unit 1))))', f'(unit 1)) (path "/{ROOT_ID}/{second}" (reference "U2") (unit 1))))')
        child.write_text(content('dddddddd-dddd-dddd-dddd-dddddddddddd',
            placed, wire(10, 10, 20, 10), '(label "SIG" (at 20 10 0))'), encoding='utf-8')
        self.files.extend([root, child])
        self.before.update({root: sha(root), child: sha(child)})
        return root, first, second

    def test_29_net_local_label_in_reused_sheet_gives_one_result_per_instance(self):
        root, first, second = self.reused_project()
        r = self.call('net', 'SIG', project=root)
        self.assertEqual(r['total_matches'], 2)
        found = {r2['matched_by'][0]['instance_path']: self.net_pins(r2) for r2 in r['results']}
        self.assertEqual(found, {f'/{ROOT_ID}/{first}': {('U1', '1')},
                                 f'/{ROOT_ID}/{second}': {('U2', '1')}})

    def test_30_components_lists_and_filters(self):
        r = self.call('components')
        self.assertEqual(r['verification'], 'STRUCTURAL_DISCOVERY_ONLY')
        refs = [x['reference'] for x in r['results']]
        self.assertEqual(sorted(refs), ['PWR_FLAG1', 'PWR_FLAG2', 'R1', 'U1', 'U104', 'U105'])
        self.assertNotIn('#PWR01', refs)
        r = self.call('components', '--prefix', 'U')
        self.assertEqual([x['reference'] for x in r['results']], ['U1', 'U104', 'U105'])
        r = self.call('components', '--sheet', 'MCU IOs')
        self.assertEqual(r['total_matches'], 1)
        self.assertEqual(r['results'][0], {
            'reference': 'R1', 'value': 'Generic', 'lib_id': 'TEST:OnePin',
            'sheet_name': 'MCU IOs', 'instance_path': f'/{ROOT_ID}/{MCU_SHEET_ID}',
            'file': str((self.dir / 'MCU IOs.kicad_sch').resolve()), 'units': ['1']})
        r = self.call('components', '--sheet', 'Power State', '--prefix', 'U', '--limit', '1')
        self.assertEqual([x['reference'] for x in r['results']], ['U1'])
        self.assertEqual(r['total_matches'], 3)
        self.assertTrue(r['truncated'])
        r = self.call('components', '--prefix', '#PWR')
        self.assertEqual([x['reference'] for x in r['results']], ['#PWR01'])
        r = self.call('components', '--sheet', 'No Such Sheet')
        self.assertEqual(r['total_matches'], 0)
        self.assertIn('No Such Sheet', ' '.join(r['warnings']))
        self.call('components', 'U1', ok=False)
        self.call('summary', '--sheet', 'MCU IOs', ok=False)

    def test_31_components_resolve_references_per_sheet_instance(self):
        root, first, second = self.reused_project()
        r = self.call('components', project=root)
        self.assertEqual([(x['reference'], x['sheet_name'], x['instance_path']) for x in r['results']],
                         [('U1', 'First', f'/{ROOT_ID}/{first}'),
                          ('U2', 'Second', f'/{ROOT_ID}/{second}')])
        r = self.call('components', '--sheet', 'Second', project=root)
        self.assertEqual([x['reference'] for x in r['results']], ['U2'])

    def test_32_each_file_is_read_once_per_query(self):
        spec = importlib.util.spec_from_file_location('_query_sch_read_count', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = Path.read_text
        for args in (['connected-pins', 'U1'], ['project-net', 'U1', '--pin', '1'],
                     ['net', 'GND'], ['local-net', 'U104'], ['components']):
            with self.subTest(command=args[0]):
                reads = []

                def counting(path, *a, **k):
                    reads.append(str(path))
                    return original(path, *a, **k)

                with mock.patch.object(Path, 'read_text', counting), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.main([*args, '--project', str(self.root)]), 0)
                self.assertEqual(len(reads), 3, reads)
                self.assertEqual(len(set(reads)), 3, reads)

    def test_33_output_is_utf8_whatever_the_console_encoding(self):
        # A Windows console or pipe often uses a legacy code page. A project
        # path with non-ASCII characters must still give valid UTF-8 JSON.
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'cp1252'}
        for args, stream in ((['summary'], 'stdout'), (['pins'], 'stderr')):
            with self.subTest(stream=stream):
                done = subprocess.run([sys.executable, str(SCRIPT), *args, '--project', str(self.root)],
                                      capture_output=True, cwd=self.dir, timeout=25, env=env)
                self.assertEqual(done.returncode, 0 if stream == 'stdout' else 2, done.stderr)
                obj = json.loads(getattr(done, stream).decode('utf-8'))
                if stream == 'stdout':
                    self.assertIn('ไทย', obj['root'])
                else:
                    self.assertEqual(obj['verification'], 'NOT_VERIFIED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
