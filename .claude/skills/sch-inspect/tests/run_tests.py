#!/usr/bin/env python3
"""Run one sch-inspect test group and emit explicit audit-status counts.

The test cases use unittest's normal pass/fail/skip semantics.  NOT_VERIFIED is
reported separately because it is a tool/evidence state, not a test outcome;
this runner reserves the category for future evidence-classified cases.
"""
import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


TESTS = Path(__file__).resolve().parent


class AuditResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.not_verified = 0

    @property
    def passed(self):
        return self.testsRun - len(self.failures) - len(self.errors) - len(self.skipped)


class AuditRunner(unittest.TextTestRunner):
    resultclass = AuditResult


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', required=True, help='Test filename pattern, for example test_query_sch.py')
    parser.add_argument('--label', required=True, help='Human-readable group label')
    args = parser.parse_args()

    suite = unittest.TestSuite()
    for path in sorted(TESTS.glob(args.pattern)):
        module_name = f'_sch_inspect_{path.stem}'
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f'Cannot load test module: {path}')
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    result = AuditRunner(verbosity=2).run(suite)
    failed = len(result.failures) + len(result.errors)
    print(
        f'AUDIT_COUNTS label={args.label} PASS={result.passed} FAIL={failed} '
        f'SKIP={len(result.skipped)} NOT_VERIFIED={result.not_verified}',
        flush=True,
    )
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
