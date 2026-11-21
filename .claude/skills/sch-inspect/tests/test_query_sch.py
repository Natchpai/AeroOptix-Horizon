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


def bus(x1, y1, x2, y2):
    return f'(bus (pts (xy {x1} {y1}) (xy {x2} {y2})))'


def bus_entry(x, y):
    return f'(bus_entry (at {x} {y}) (size 2.54 2.54))'


def multi_sheet(name, file, uid, pins):
    blocks = ' '.join(f'(pin "{n}" bidirectional (at {x} {y} 0) (uuid "pin-{uid}-{i}"))'
                      for i, (n, x, y) in enumerate(pins))
    return f'''(sheet (at 0 0) (size 30 20)
       (property "Sheetname" "{name}") (property "Sheetfile" "{file}")
       {blocks}
       (uuid "{uid}"))'''


def bus_child(uid, path, refs, names):
    """One child sheet of the bus fixture. Rules checked with a KiCad 10.0.8 netlist."""
    alias_bus, vector, group, member, prefixed = names
    rows = [
        bus(10, 10, 40, 10), f'(hierarchical_label "{alias_bus}" (at 40 10 0))',
        # A label with the member name joins the member; no bus entry needed.
        component(refs[0], 100, 10, f'{refs[0]}-u', path), wire(100, 10, 110, 10),
        '(label "SIG_A" (at 110 10 0))',
        # A wire on a bus entry without a member label is not a member.
        bus_entry(12.46, 10), wire(15, 12.54, 15, 20), component(refs[1], 15, 20, f'{refs[1]}-u', path),
        bus(10, 40, 40, 40), f'(hierarchical_label "{vector}" (at 40 40 0))',
        component(refs[2], 100, 40, f'{refs[2]}-u', path), wire(100, 40, 110, 40),
        f'(label "{member}" (at 110 40 0))',
        bus(10, 60, 40, 60), f'(hierarchical_label "{group}" (at 40 60 0))',
        component(refs[3], 100, 60, f'{refs[3]}-u', path), wire(100, 60, 110, 60),
        f'(label "{prefixed}" (at 110 60 0))',
        bus(10, 80, 40, 80), '(global_label "{GX GY}" (at 40 80 0))',
        component(refs[4], 100, 80, f'{refs[4]}-u', path), wire(100, 80, 110, 80),
        '(label "GX" (at 110 80 0))',
        bus(10, 100, 40, 100), '(global_label "{AL2}" (at 40 100 0))',
        component(refs[5], 100, 100, f'{refs[5]}-u', path), wire(100, 100, 110, 100),
        '(label "X1" (at 110 100 0))',
        # A bare short name is not a member of a prefixed group.
        component(refs[6], 100, 120, f'{refs[6]}-u', path), wire(100, 120, 110, 120),
        '(label "X" (at 110 120 0))']
    return content(uid, *rows)


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
            'bus': ((), 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY'),
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
        # mirror x at 90 and 270 degrees. KiCad 10 never saves mirror y at 90
        # or 270: it is the same placement as mirror x at 270 or 90 and is
        # saved in that form. A file that holds it must give the same pins.
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
        self.assertEqual(expected[('y', 90)], expected[('x', 270)])
        self.assertEqual(expected[('y', 270)], expected[('x', 90)])
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

    def write_root(self, name, lib, *blocks):
        root = self.dir / name
        root.write_text('(kicad_sch (version 20250114) (generator "test") (uuid "' + ROOT_ID + '")\n'
                        + lib + '\n' + '\n'.join(blocks) + '\n)', encoding='utf-8')
        self.files.append(root)
        self.before[root] = sha(root)
        return root

    def test_34_lib_name_selects_the_embedded_symbol_definition(self):
        # KiCad writes (lib_name "X_1") when two placed symbols share a lib_id
        # but differ, and stores that definition under the lib_name.
        lib = '''(lib_symbols
          (symbol "TEST:OnePin"
            (symbol "OnePin_1_1" (pin input line (at 0 0 0) (length 2.54) (name "IN") (number "1"))))
          (symbol "OnePin_1"
            (symbol "OnePin_1_1_1" (pin input line (at 5.08 0 0) (length 2.54) (name "IN") (number "1"))))
          (symbol "GND_1" (power)
            (symbol "GND_1_1_1" (pin power_in line (at 0 0 0) (length 0) (name "GND") (number "1")))))'''
        root = self.write_root('lib name.kicad_sch', lib,
            component('U1', 100, 100, 'u1', f'/{ROOT_ID}').replace('(symbol ', '(symbol (lib_name "OnePin_1") ', 1),
            component('U2', 120, 100, 'u2', f'/{ROOT_ID}'),
            wire(105.08, 100, 120, 100),
            component('#PWR01', 120, 100, 'gnd', f'/{ROOT_ID}', 'GND', 'power:GND').replace(
                '(symbol ', '(symbol (lib_name "GND_1") ', 1))
        pins = self.call('pins', 'U1', project=root)['results'][0]
        self.assertEqual([p['position_mm'] for p in pins['pins']], [[105.08, 100.0]])
        self.assertEqual(pins['limitations'], [])
        net = self.call('project-net', 'U1', '--pin', '1', project=root)['results'][0]
        self.assertEqual(self.net_pins(net), {('U1', '1'), ('U2', '1')})
        self.assertEqual(net['power_net_names'], ['GND'])

    def test_35_only_the_placed_body_style_gives_pins(self):
        # Sub-symbols are NAME_<unit>_<style>; style 0 is shared by all styles.
        lib = '''(lib_symbols
          (symbol "TEST:Gate"
            (symbol "Gate_0_0" (pin power_in line (at 0 5.08 270) (length 2.54) (name "VCC") (number "14")))
            (symbol "Gate_1_1" (pin output line (at 7.62 0 180) (length 2.54) (name "Y") (number "3")))
            (symbol "Gate_1_2" (pin output inverted (at 10.16 0 180) (length 2.54) (name "Y") (number "3")))))'''
        base = component('U1', 50, 50, 'u1', f'/{ROOT_ID}', lib='TEST:Gate')
        cases = (('', 57.62), ('(body_style 1)', 57.62), ('(body_style 2)', 60.16), ('(convert 2)', 60.16))
        for index, (token, output_x) in enumerate(cases):
            with self.subTest(token=token):
                root = self.write_root(f'body style {index}.kicad_sch', lib,
                                       base.replace('(unit 1)', '(unit 1) ' + token, 1))
                pins = self.call('pins', 'U1', project=root)['results'][0]['pins']
                self.assertEqual({p['number']: p['position_mm'] for p in pins},
                                 {'14': [50.0, 44.92], '3': [output_x, 50.0]})
                self.assertEqual(len(pins), 2)

    def test_36_malformed_forms_return_json_not_traceback(self):
        cases = (
            ('empty uuid', '(kicad_sch (uuid))', ['summary']),
            ('one coordinate', content(ROOT_ID, component('U1', 10, 10, 'u1', f'/{ROOT_ID}'),
                                       '(wire (pts (xy 1) (xy 20 10)))'), ['local-net', 'U1']),
        )
        for name, text, args in cases:
            with self.subTest(case=name):
                bad = self.dir / f'{name}.kicad_sch'
                bad.write_text(text, encoding='utf-8')
                completed = self.call(*args, project=bad, ok=False)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertEqual(completed.stdout, '')
                error = json.loads(completed.stderr)
                self.assertEqual(error['verification'], 'NOT_VERIFIED')
                self.assertTrue(error['error'])

    def test_37_component_units_are_sorted_as_numbers(self):
        lib = '(lib_symbols (symbol "TEST:Big" ' + ' '.join(
            f'(symbol "Big_{u}_1" (pin passive line (at 0 0 0) (length 1) (name "P{u}") (number "{u}")))'
            for u in (1, 2, 10, 11)) + '))'
        blocks = [component('U3', 10 * u, 20, f'u3-{u}', f'/{ROOT_ID}', lib='TEST:Big').replace('(unit 1)', f'(unit {u})')
                  for u in (10, 2, 11, 1)]
        root = self.write_root('units.kicad_sch', lib, *blocks)
        r = self.call('components', project=root)
        self.assertEqual([(x['reference'], x['units']) for x in r['results']], [('U3', ['1', '2', '10', '11'])])

    def test_38_sheet_matches_the_file_name_of_a_sheet_in_a_subfolder(self):
        sub = self.dir / 'sub'
        sub.mkdir()
        child = sub / 'child.kicad_sch'
        child.write_text(content('ffffffff-ffff-ffff-ffff-ffffffffffff'), encoding='utf-8')
        self.files.append(child)
        self.before[child] = sha(child)
        root = self.write_root('subfolder.kicad_sch', lib_symbols(),
                               sheet('Child', 'sub/child.kicad_sch', 'child-sheet', 'X', 10, 10))
        for target in ('Child', 'child', 'child.kicad_sch', 'sub/child.kicad_sch'):
            with self.subTest(target=target):
                self.assertEqual(self.call('sheet', target, project=root)['total_matches'], 1)
        self.assertEqual(self.call('components', '--sheet', 'child.kicad_sch', project=root)['warnings'], [])

    def bus_project(self, alias_file=True):
        root = self.dir / 'bus top.kicad_sch'
        a, b = self.dir / 'bus a.kicad_sch', self.dir / 'bus b.kicad_sch'
        sa, sb = '1aaaaaaa-0000-0000-0000-000000000000', '1bbbbbbb-0000-0000-0000-000000000000'
        root.write_text(content(ROOT_ID,
            multi_sheet('A', a.name, sa, [('{AL}', 50, 10), ('D[0..1]', 50, 20), ('P{X Y}', 50, 30)]),
            multi_sheet('B', b.name, sb, [('{AL}', 80, 10), ('DATA[0..1]', 80, 20), ('Q{X Y}', 80, 30)]),
            bus(50, 10, 80, 10), bus(50, 20, 80, 20), bus(50, 30, 80, 30)), encoding='utf-8')
        a.write_text(bus_child('2aaaaaaa-0000-0000-0000-000000000000', f'/{ROOT_ID}/{sa}',
                               ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7'],
                               ('{AL}', 'D[0..1]', 'P{X Y}', 'D1', 'P.X')
                               ).replace('\n)', '\n(bus_alias "AL2" (members "X1" "X2")))'), encoding='utf-8')
        b.write_text(bus_child('2bbbbbbb-0000-0000-0000-000000000000', f'/{ROOT_ID}/{sb}',
                               ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'],
                               ('{AL}', 'DATA[0..1]', 'Q{X Y}', 'DATA1', 'Q.X')), encoding='utf-8')
        files = [root, a, b]
        if alias_file:
            pro = root.with_suffix('.kicad_pro')
            pro.write_text(json.dumps({'schematic': {'bus_aliases': {'AL': ['SIG_A', 'SIG_B']}}}), encoding='utf-8')
            files.append(pro)
        self.files.extend(files)
        self.before.update({f: sha(f) for f in files})
        return root

    def pins_of(self, root, ref):
        r = self.call('project-net', ref, '--pin', '1', project=root)
        one = r['results'][0]
        self.assertEqual(one['status'], 'PROJECT_CONNECTIVITY_EVIDENCE')
        self.assertFalse(one['project_net_verified'])
        return {p['reference'] for p in one['connected_component_pins']}, one

    def test_39_bus_members_join_by_name_across_sheets(self):
        # Each expectation matches a KiCad 10.0.8 netlist of the same layout.
        root = self.bus_project()
        cases = {'U1': {'U1', 'R1'},          # alias member, no bus entry
                 'U2': {'U2'},                # bus entry without a member label
                 'U3': {'U3', 'R3'},          # vector members match by index
                 'U4': {'U4', 'R4'},          # P{X Y} and Q{X Y} match by short name
                 'R7': {'R7'},                # bare X is not a member of Q{X Y}
                 'U5': {'U5', 'R5'},          # global bus label
                 'U6': {'U6', 'R6'}}          # legacy bus_alias in a sheet file
        for ref, expected in cases.items():
            with self.subTest(ref=ref):
                self.assertEqual(self.pins_of(root, ref)[0], expected)
        _, one = self.pins_of(root, 'U1')
        self.assertTrue(one['bus_links'])
        self.assertTrue(all(x['bus_names'] == ['{AL}'] for x in one['bus_links']))
        self.assertFalse(one['bus_links_truncated'])
        net = self.call('net', 'SIG_A', project=root)
        self.assertEqual(net['total_matches'], 1, 'a bus joins the two SIG_A labels into one net')

    def test_40_without_the_alias_the_bus_has_no_members(self):
        root = self.bus_project(alias_file=False)
        self.assertEqual(self.pins_of(root, 'U1')[0], {'U1'})
        self.assertEqual(self.pins_of(root, 'U3')[0], {'U3', 'R3'})

    def test_41_bus_command_traces_each_member(self):
        root = self.bus_project()
        for name in ('AL', '{AL}'):
            with self.subTest(name=name):
                r = self.call('bus', name, project=root)
                self.assertEqual(r['verification'], 'INSTANCE_AWARE_PROJECT_EVIDENCE_ONLY')
                self.assertEqual(r['total_matches'], 1)
                one = r['results'][0]
                self.assertEqual(one['status'], 'BUS_CONNECTIVITY_EVIDENCE')
                self.assertFalse(one['project_net_verified'])
                self.assertEqual(len(one['occurrences']), 3)
                members = {m['member']: m for m in one['members']}
                self.assertEqual(set(members), {'SIG_A', 'SIG_B'})
                self.assertEqual({p['reference'] for p in members['SIG_A']['connected_component_pins']}, {'U1', 'R1'})
                self.assertEqual(members['SIG_B']['connected_component_pins'], [])
                self.assertFalse(any(x['member_net_on_sheet'] for x in members['SIG_B']['sheets']))
        missing = self.call('bus', 'NOPE', project=root)
        self.assertEqual(missing['results'][0]['status'], 'BUS_NAME_NOT_FOUND')
        listing = self.call('bus', project=root, ok=True)
        rows = {(x['kind'], x['name']): x for x in listing['results']}
        self.assertEqual(rows[('alias', 'AL')]['used_by'], ['{AL}'])
        self.assertIn(('alias', 'AL2'), rows)
        self.assertEqual(rows[('bus_name', 'D[0..1]')]['members'], ['D0', 'D1'])
        self.call('bus', '--pin', '1', project=root, ok=False)

    def test_42_bus_names_are_parsed_as_kicad_does(self):
        spec = importlib.util.spec_from_file_location('_query_sch_bus', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        names = lambda text, aliases={}: [n for _, n in module.bus_members(text, aliases) or []]
        self.assertIsNone(module.bus_members('SS{slash}TR', {}))
        self.assertIsNone(module.bus_members('{slash}', {}))
        self.assertIsNone(module.bus_members('PLAIN', {}))
        self.assertEqual(names('D[3..1]'), ['D3', 'D2', 'D1'])
        self.assertEqual(names('P{A B}'), ['P.A', 'P.B'])
        self.assertEqual(names('{D[0..1] CLK}'), ['D0', 'D1', 'CLK'])
        self.assertEqual(names('{AL}', {'AL': ['X', 'Y']}), ['X', 'Y'])
        # A bare alias name is a plain net name in KiCad 10 (netlist check).
        self.assertIsNone(module.bus_members('AL', {'AL': ['X', 'Y']}))
        self.assertIsNone(module.bus_members('A{lt}B{gt}', {}))
        # A self-referencing alias does not recurse.
        self.assertEqual(names('{AL}', {'AL': ['X', '{AL}']}), ['X', 'AL'])
        self.assertEqual(module.bus_members('D[1..2]', {})[0][0], ('v', 1))
        self.assertEqual(module.bus_members('P{A}', {})[0][0], ('g', 'A'))

    def test_43_malformed_project_aliases_return_json_error(self):
        root = self.bus_project(alias_file=False)
        pro = root.with_suffix('.kicad_pro')
        pro.write_text('{broken', encoding='utf-8')
        self.files.append(pro)
        self.before[pro] = sha(pro)
        completed = self.call('bus', 'AL', project=root, ok=False)
        error = json.loads(completed.stderr)
        self.assertEqual(error['verification'], 'NOT_VERIFIED')
        self.assertIn('bus aliases', error['error'])

    # Tests 44 to 49: each expectation matches a KiCad 10.0.8 netlist of the
    # same layout.
    def pins_on(self, root, ref, pin='1'):
        r = self.call('project-net', ref, '--pin', pin, project=root)
        return {(p['reference'], p['pin_number']) for p in r['results'][0]['connected_component_pins']}

    def test_44_pins_and_wire_ends_join_a_wire_only_at_its_ends(self):
        path = f'/{ROOT_ID}'
        root = self.write_root('mid wire.kicad_sch', lib_symbols(),
            # T without a junction: R2's wire ends on the middle of R1-R3.
            wire(10, 10, 30, 10), wire(20, 10, 20, 20),
            component('R1', 10, 10, 'r1', path), component('R2', 20, 20, 'r2', path),
            component('R3', 30, 10, 'r3', path),
            # Pin on the middle of a wire, no junction.
            wire(10, 30, 30, 30), component('R4', 10, 30, 'r4', path), component('R5', 20, 30, 'r5', path),
            # Pin on a junction on the middle of a wire.
            wire(10, 40, 30, 40), component('R6', 10, 40, 'r6', path),
            '(junction (at 20 40))', component('R7', 20, 40, 'r7', path),
            # Label on the middle of a wire.
            wire(10, 50, 30, 50), component('R8', 10, 50, 'r8', path), '(label "N2" (at 20 50 0))',
            wire(10, 60, 20, 60), component('R9', 10, 60, 'r9', path), '(label "N2" (at 20 60 0))')
        self.assertEqual(self.pins_on(root, 'R1'), {('R1', '1'), ('R3', '1')})
        self.assertEqual(self.pins_on(root, 'R2'), {('R2', '1')})
        self.assertEqual(self.pins_on(root, 'R4'), {('R4', '1')})
        self.assertEqual(self.pins_on(root, 'R6'), {('R6', '1'), ('R7', '1')})
        self.assertEqual(self.pins_on(root, 'R8'), {('R8', '1'), ('R9', '1')})
        pins = self.call('local-net', 'R5', project=root)['results'][0]['pins'][0]
        self.assertEqual(pins['local_wire_segments_at_pin'], 0)
        self.assertNotEqual(pins['local_connection_status'], 'LOCAL_WIRE_PATH')

    def test_45_labels_of_any_kind_with_one_name_join_on_a_sheet(self):
        path = f'/{ROOT_ID}'
        root = self.write_root('kinds.kicad_sch', lib_symbols(),
            wire(10, 10, 15, 10), component('R1', 10, 10, 'r1', path), '(label "N1" (at 15 10 0))',
            wire(10, 20, 15, 20), component('R2', 10, 20, 'r2', path), '(global_label "N1" (at 15 20 0))',
            wire(10, 30, 15, 30), component('R3', 10, 30, 'r3', path), '(hierarchical_label "H1" (at 15 30 0))',
            wire(10, 40, 15, 40), component('R4', 10, 40, 'r4', path), '(hierarchical_label "H1" (at 15 40 0))')
        self.assertEqual(self.pins_on(root, 'R1'), {('R1', '1'), ('R2', '1')})
        self.assertEqual(self.pins_on(root, 'R3'), {('R3', '1'), ('R4', '1')})

    def test_46_a_local_power_symbol_is_one_net_per_sheet_instance(self):
        child = self.dir / 'local power.kicad_sch'
        sid = '3ccccccc-0000-0000-0000-000000000000'
        lib = lib_symbols().replace('(symbol "power:VBUS" (power)', '(symbol "power:VBUS" (power local)')
        root = self.write_root('local power top.kicad_sch', lib,
            sheet('Child', child.name, sid, 'UNUSED', 50, 50),
            component('#PWR1', 10, 10, 'p1', f'/{ROOT_ID}', 'VBUS', 'power:VBUS'),
            component('R1', 10, 10, 'r1', f'/{ROOT_ID}'),
            component('#PWR2', 10, 20, 'p2', f'/{ROOT_ID}', 'GND', 'power:GND'),
            component('R2', 10, 20, 'r2', f'/{ROOT_ID}'))
        child.write_text(content('3ddddddd-0000-0000-0000-000000000000',
            component('#PWR3', 10, 10, 'p3', f'/{ROOT_ID}/{sid}', 'VBUS', 'power:VBUS'),
            component('R3', 10, 10, 'r3', f'/{ROOT_ID}/{sid}'),
            component('#PWR4', 10, 20, 'p4', f'/{ROOT_ID}/{sid}', 'GND', 'power:GND'),
            component('R4', 10, 20, 'r4', f'/{ROOT_ID}/{sid}')).replace(
                '(symbol "power:VBUS" (power)', '(symbol "power:VBUS" (power local)'), encoding='utf-8')
        self.files.append(child)
        self.before[child] = sha(child)
        self.assertEqual(self.pins_on(root, 'R1'), {('R1', '1')})
        self.assertEqual(self.pins_on(root, 'R2'), {('R2', '1'), ('R4', '1')})

    def test_47_each_sheet_instance_uses_its_own_unit(self):
        child = self.dir / 'units child.kicad_sch'
        first, second = '4aaaaaaa-0000-0000-0000-000000000000', '4bbbbbbb-0000-0000-0000-000000000000'
        dual = ('(symbol "TEST:Dual" (symbol "Dual_1_1" (pin passive line (at 0 0 0) (length 1) (name "A") (number "1")))'
                ' (symbol "Dual_2_1" (pin passive line (at 0 0 0) (length 1) (name "B") (number "2"))))')
        lib = lib_symbols()[:-1] + dual + ')'
        root = self.write_root('units top.kicad_sch', lib,
            sheet('First', child.name, first, 'UNUSED', 50, 50), sheet('Second', child.name, second, 'UNUSED2', 90, 50))
        child.write_text('(kicad_sch (version 20250114) (generator "test") (uuid "4ccccccc-0000-0000-0000-000000000000")\n'
            + lib + f'''
            (symbol (lib_id "TEST:Dual") (at 10 10 0) (unit 1) (property "Reference" "UM1") (uuid "um1")
              (instances (project "Test" (path "/{ROOT_ID}/{first}" (reference "UM1") (unit 1))
                                         (path "/{ROOT_ID}/{second}" (reference "UM1") (unit 2)))))
            (symbol (lib_id "TEST:OnePin") (at 20 10 0) (unit 1) (property "Reference" "RG1") (uuid "rg")
              (instances (project "Test" (path "/{ROOT_ID}/{first}" (reference "RG1") (unit 1))
                                         (path "/{ROOT_ID}/{second}" (reference "RG2") (unit 1)))))
            {wire(10, 10, 20, 10)})''', encoding='utf-8')
        self.files.append(child)
        self.before[child] = sha(child)
        self.assertEqual(self.pins_on(root, 'RG1'), {('RG1', '1'), ('UM1', '1')})
        self.assertEqual(self.pins_on(root, 'RG2'), {('RG2', '1'), ('UM1', '2')})

    def test_48_bus_members_of_one_name_and_global_bus_members(self):
        a, b = self.dir / 'bm a.kicad_sch', self.dir / 'bm b.kicad_sch'
        sa, sb = '5aaaaaaa-0000-0000-0000-000000000000', '5bbbbbbb-0000-0000-0000-000000000000'
        root = self.write_root('bm top.kicad_sch', lib_symbols(),
            multi_sheet('A', a.name, sa, [('D[0..1]', 50, 10)]),
            multi_sheet('B', b.name, sb, [('D[0..3]', 80, 10)]),
            # Two separate root buses; their D0 members are one net.
            bus(50, 10, 60, 10), '(label "D[0..1]" (at 55 10 0))',
            bus(70, 10, 80, 10), '(label "D[0..3]" (at 75 10 0))',
            # A bus T without a junction does not join.
            bus(10, 70, 60, 70), '(label "G[0..1]" (at 15 70 0))',
            bus(40, 70, 40, 90), '(label "K[0..1]" (at 40 85 0))',
            wire(10, 100, 20, 100), component('R3', 10, 100, 'r3', f'/{ROOT_ID}'), '(label "K0" (at 20 100 0))',
            wire(10, 110, 20, 110), component('R4', 10, 110, 'r4', f'/{ROOT_ID}'), '(label "G0" (at 20 110 0))')
        a.write_text(content('5ccccccc-0000-0000-0000-000000000000',
            bus(10, 10, 40, 10), '(hierarchical_label "D[0..1]" (at 40 10 0))',
            component('RA0', 100, 10, 'ra0', f'/{ROOT_ID}/{sa}'), wire(100, 10, 110, 10), '(label "D0" (at 110 10 0))',
            bus(10, 30, 40, 30), '(global_label "{GX GY}" (at 40 30 0))',
            component('RAX', 100, 30, 'rax', f'/{ROOT_ID}/{sa}'), wire(100, 30, 110, 30), '(label "GX" (at 110 30 0))'),
            encoding='utf-8')
        b.write_text(content('5ddddddd-0000-0000-0000-000000000000',
            bus(10, 10, 40, 10), '(hierarchical_label "D[0..3]" (at 40 10 0))',
            component('RB0', 100, 10, 'rb0', f'/{ROOT_ID}/{sb}'), wire(100, 10, 110, 10), '(label "D0" (at 110 10 0))',
            component('RBX', 100, 30, 'rbx', f'/{ROOT_ID}/{sb}'), wire(100, 30, 110, 30), '(global_label "GX" (at 110 30 0))'),
            encoding='utf-8')
        self.files.extend([a, b])
        self.before.update({a: sha(a), b: sha(b)})
        self.assertEqual(self.pins_on(root, 'RA0'), {('RA0', '1'), ('RB0', '1')})
        self.assertEqual(self.pins_on(root, 'RAX'), {('RAX', '1'), ('RBX', '1')})
        self.assertEqual(self.pins_on(root, 'R3'), {('R3', '1')})
        self.assertEqual(self.pins_on(root, 'R4'), {('R4', '1')})

    def test_49_a_bus_with_a_plain_name_has_no_members(self):
        child = self.dir / 'plain a.kicad_sch'
        sid = '6aaaaaaa-0000-0000-0000-000000000000'
        root = self.write_root('plain top.kicad_sch', lib_symbols(),
            multi_sheet('A', child.name, sid, [('{AL}', 50, 10)]),
            bus(50, 10, 80, 10), '(label "AL" (at 70 10 0))',
            wire(10, 100, 20, 100), component('R2', 10, 100, 'r2', f'/{ROOT_ID}'), '(label "SIG_A" (at 20 100 0))')
        child.write_text(content('6bbbbbbb-0000-0000-0000-000000000000',
            bus(10, 10, 40, 10), '(hierarchical_label "{AL}" (at 40 10 0))',
            component('RAS', 100, 10, 'ras', f'/{ROOT_ID}/{sid}'), wire(100, 10, 110, 10), '(label "SIG_A" (at 110 10 0))'),
            encoding='utf-8')
        pro = root.with_suffix('.kicad_pro')
        pro.write_text(json.dumps({'schematic': {'bus_aliases': {'AL': ['SIG_A', 'SIG_B']}}}), encoding='utf-8')
        self.files.extend([child, pro])
        self.before.update({child: sha(child), pro: sha(pro)})
        self.assertEqual(self.pins_on(root, 'R2'), {('R2', '1')})
        warnings = self.call('bus', project=root)['warnings']
        self.assertTrue(any(w['name'] == 'AL' for w in warnings), warnings)
        # Odd project JSON gives a JSON error, not a traceback.
        for text in ('{"schematic": null}', '{"schematic": {"bus_aliases": null}}', '[]'):
            with self.subTest(project=text):
                pro.write_text(text, encoding='utf-8')
                self.before[pro] = sha(pro)
                self.call('net', 'SIG_A', project=root)



FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'netlist_small'


class NetlistCommands(unittest.TestCase):
    """netlist and netlist-compare against a real KiCad 10.0.8 XML export.

    fixtures/netlist_small: a root sheet and one child sheet joined by the bus
    D[0..1], plus the global label COM. netlist_small.xml is the unchanged
    `kicad-cli sch export netlist --format kicadxml` output of it, except the
    <source> path and <date>, which were made machine-neutral.
    """

    def run_cli(self, *args, ok=True):
        cmd = [sys.executable, str(SCRIPT), *args, '--project', str(FIXTURE / 'netlist_small.kicad_sch')]
        done = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
        if ok:
            self.assertEqual(done.returncode, 0, done.stderr)
            return json.loads(done.stdout)
        self.assertEqual(done.returncode, 2, done.stdout)
        error = json.loads(done.stderr)
        self.assertEqual(error['verification'], 'NOT_VERIFIED')
        return error

    def module(self):
        spec = importlib.util.spec_from_file_location('_query_sch_netlist', SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_netlist_lookup_by_net_and_reference(self):
        r = self.run_cli('netlist', 'D0', '--netlist', str(FIXTURE / 'netlist_small.xml'))
        self.assertEqual(r['verification'], 'KICAD_NETLIST_EVIDENCE')
        self.assertEqual([(n['reference'], n['pin_number']) for n in r['results'][0]['nodes']],
                         [('R1', '1'), ('R3', '1')])
        self.assertEqual(r['results'][0]['netlist_tool'], 'Eeschema 10.0.8')
        refs = self.run_cli('netlist', 'R1', '--netlist', str(FIXTURE / 'netlist_small.xml'))['results']
        self.assertEqual({x['net_name'] for x in refs}, {'/D0', 'COM'})
        self.assertTrue(all(x['matched_by'] == 'reference' for x in refs))
        missing = self.run_cli('netlist', 'NOPE', '--netlist', str(FIXTURE / 'netlist_small.xml'))['results']
        self.assertEqual(missing[0]['status'], 'NET_OR_REFERENCE_NOT_FOUND')

    def test_compare_matches_kicad_on_bus_and_global(self):
        r = self.run_cli('netlist-compare', '--netlist', str(FIXTURE / 'netlist_small.xml'))
        self.assertEqual(r['verification'], 'KICAD_NETLIST_COMPARISON')
        summary = r['results'][0]
        self.assertEqual(summary['status'], 'NETLIST_COMPARISON_SUMMARY')
        self.assertEqual((summary['multi_pin_kicad_nets_compared'], summary['pins_compared'],
                          summary['differences']), (3, 8, 0))
        self.assertEqual(summary['instance_count'], 2)

    def test_compare_reports_split_and_merged(self):
        text = (FIXTURE / 'netlist_small.xml').read_text(encoding='utf-8')
        # Move R3 pin 1 from /D0 to /D1 in the KiCad netlist only.
        moved = text.replace('<node ref="R3" pin="1"', '<node ref="R3" pin="9"', 1)
        moved = moved.replace('<node ref="R2" pin="1"',
                              '<node ref="R3" pin="1" pintype="passive"/><node ref="R2" pin="1"', 1)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / 'moved.xml'
            f.write_text(moved, encoding='utf-8')
            r = self.run_cli('netlist-compare', '--netlist', str(f))
        kinds = {(d['kind'], d.get('kicad_net') or d.get('sch_inspect_net')) for d in r['results'][1:]}
        self.assertIn(('split', '/D1'), kinds)  # KiCad joins R2.1, R4.1 and R3.1
        self.assertTrue(any(k == 'merged' for k, _ in kinds))  # sch-inspect joins R1.1 and R3.1
        self.assertEqual(r['results'][0]['differences'], len(r['results']) - 1)

    def test_errors_are_json(self):
        self.run_cli('summary', '--netlist', str(FIXTURE / 'netlist_small.xml'), ok=False)
        self.run_cli('netlist-compare', 'D0', '--netlist', str(FIXTURE / 'netlist_small.xml'), ok=False)
        self.run_cli('netlist', '--netlist', str(FIXTURE / 'netlist_small.xml'), ok=False)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'bad.xml'
            bad.write_text('<nope/>', encoding='utf-8')
            error = self.run_cli('netlist', 'D0', '--netlist', str(bad), ok=False)
            self.assertIn('not a KiCad XML netlist', error['error'])

    def test_find_kicad_cli_order_and_failure(self):
        mod = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / 'kicad-cli'
            fake.write_text('', encoding='utf-8')
            with mock.patch.dict(os.environ, {'KICAD_CLI': str(fake)}):
                self.assertEqual(mod.find_kicad_cli(), str(fake))
                self.assertEqual(mod.find_kicad_cli(str(fake)), str(fake))
        with mock.patch.dict(os.environ, {'KICAD_CLI': ''}), \
                mock.patch.object(mod.shutil, 'which', return_value=None), \
                mock.patch.object(mod.glob, 'glob', return_value=[]), \
                mock.patch.object(mod.sys, 'platform', 'linux'):
            with self.assertRaises(mod.QueryError):
                mod.find_kicad_cli()

    def test_export_netlist_uses_temp_folder(self):
        mod = self.module()
        xml_text = (FIXTURE / 'netlist_small.xml').read_text(encoding='utf-8')
        seen = {}

        def fake_run(cmd, **kw):
            out = Path(cmd[cmd.index('-o') + 1])
            seen['out'], seen['target'] = out, Path(cmd[-1])
            seen['copied'] = sorted(p.name for p in seen['target'].parent.iterdir())
            out.write_text(xml_text, encoding='utf-8')
            return subprocess.CompletedProcess(cmd, 0, '', '')
        sheets = [FIXTURE / 'netlist_small.kicad_sch', FIXTURE / 'child.kicad_sch']
        with mock.patch.object(mod.subprocess, 'run', side_effect=fake_run):
            self.assertEqual(mod.export_netlist(FIXTURE / 'netlist_small.kicad_sch', 'kicad-cli', sheets), xml_text)
        self.assertFalse(seen['out'].exists())  # temp folder removed
        self.assertNotEqual(seen['target'].parent, FIXTURE)  # kicad-cli runs on a copy
        self.assertEqual(seen['copied'], ['child.kicad_sch', 'netlist_small.kicad_pro', 'netlist_small.kicad_sch'])
        with mock.patch.object(mod.subprocess, 'run',
                               return_value=subprocess.CompletedProcess([], 1, '', 'load error')):
            with self.assertRaises(mod.QueryError):
                mod.export_netlist(FIXTURE / 'netlist_small.kicad_sch', 'kicad-cli')

    def test_live_kicad_cli_export(self):
        mod = self.module()
        try:
            mod.find_kicad_cli()
        except mod.QueryError:
            self.skipTest('kicad-cli not installed')
        # Run on a copy, so a stray file from an earlier run cannot hide a write.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / 'p'
            proj.mkdir()
            for name in ('netlist_small.kicad_sch', 'child.kicad_sch', 'netlist_small.kicad_pro'):
                (proj / name).write_bytes((FIXTURE / name).read_bytes())
            before = {q.name: q.stat().st_mtime_ns for q in proj.iterdir()}
            done = subprocess.run([sys.executable, str(SCRIPT), 'netlist-compare', '--project',
                                   str(proj / 'netlist_small.kicad_sch')],
                                  capture_output=True, text=True, encoding='utf-8', timeout=180)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(json.loads(done.stdout)['results'][0]['differences'], 0)
            # kicad-cli writes a .kicad_prl next to a project without one: it must run on a temp copy
            self.assertEqual({q.name: q.stat().st_mtime_ns for q in proj.iterdir()}, before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
