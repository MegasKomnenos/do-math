"""T5: one real maintenance call per provider, including disk read, checkpoint and local termination.

External provider latency is expected; there is no timeout. See 시험-지침.md for
the explicit DO_MATH_SMOKE_* inputs and persistent evidence under runner scratch.
"""
import os
import unittest

from test_categories import test_group
from support.provider_live import run_provider_smoke


@test_group('resource')
class ProviderLiveTests(unittest.TestCase):
    def test_codex_maintenance_files_and_termination(self):
        report = run_provider_smoke('codex', environment=dict(os.environ))
        self.assertTrue(report['passed'], {'checks': report['checks'], 'evidence': report['evidence_directory']})

    def test_claude_maintenance_files_and_termination(self):
        report = run_provider_smoke('claude', environment=dict(os.environ))
        self.assertTrue(report['passed'], {'checks': report['checks'], 'evidence': report['evidence_directory']})
