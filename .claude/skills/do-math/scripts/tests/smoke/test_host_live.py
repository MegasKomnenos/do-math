"""T5 Windows installation assumptions: actual worker ownership and windowless command output.

Local deterministic CLI processes incur no provider calls. No OS tasks change.
Raw kernel/worker/read observations persist in the official resource scratch.
"""
import os
from pathlib import Path
import unittest

from test_categories import test_group
from support.host_live import run_job_smoke, run_pythonw_smoke


@test_group('resource')
class HostLiveTests(unittest.TestCase):
    def test_real_worker_collects_normal_output_and_exact_nonzero_exit(self):
        for mode in ('normal', 'nonzero'):
            with self.subTest(mode=mode):
                report = run_job_smoke(mode, environment=dict(os.environ))
                self.assertTrue(report['passed'], {'checks':report['checks'], 'evidence':report['evidence_directory']})

    def test_explicit_stop_ends_owned_worker_cli_and_descendants(self):
        report = run_job_smoke('cancel', environment=dict(os.environ))
        self.assertTrue(report['passed'], {'checks':report['checks'], 'evidence':report['evidence_directory']})

    def test_pythonw_powershell_collects_installed_read_success_and_refusal(self):
        report = run_pythonw_smoke(environment=dict(os.environ), scripts=Path(__file__).resolve().parents[2])
        self.assertTrue(report['passed'], {'checks':report['checks'], 'evidence':report['evidence_directory']})
