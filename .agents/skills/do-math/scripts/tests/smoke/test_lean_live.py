"""T5 real installed Mathlib representative compile and verifier success/type error.

This may exceed the 30 s boundary reference on a cold Mathlib file cache.
No downloads, record adoption, model calls or scheduler changes are performed.
"""
import unittest

from support.lean_live import run_lean_smoke
from test_categories import test_group


@test_group('lean')
class LeanLiveTests(unittest.TestCase):
    def test_installed_mathlib_compiles_and_verifier_checks_success_and_type_error(self):
        report = run_lean_smoke()
        self.assertTrue(report['passed'], {'checks':report['checks'],
            'error':report.get('error'), 'evidence':report['evidence_directory']})
