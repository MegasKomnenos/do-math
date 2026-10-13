"""T5: one real Codex scholarly list_sources completion, files and local Job reclamation.

External initialization/model latency is expected; no time limit or retry.
Explicit provider inputs and scratch evidence follow 시험-지침.md.
"""
import os
import unittest

from test_categories import test_group
from support.scholarly_live import run_scholarly_smoke


@test_group('resource')
class ScholarlyLiveTests(unittest.TestCase):
    def test_list_sources_completes_with_installed_registry_in_isolated_workspace(self):
        report = run_scholarly_smoke(environment=dict(os.environ))
        self.assertTrue(report['passed'], {'checks': report['checks'], 'evidence': report['evidence_directory']})
