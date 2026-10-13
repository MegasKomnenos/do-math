"""T5: own absent OS tasks, real pythonw freeze/start/time trigger and cleanup."""
import unittest

from support.scheduler_live import run_scheduler_smoke
from test_categories import test_group


@test_group('resource')
class SchedulerLiveTests(unittest.TestCase):
    def test_held_pythonw_tasks_start_wake_and_uninstall(self):
        report = run_scheduler_smoke()
        self.assertTrue(report['passed'], {'checks': report['checks'],
            'error': report.get('error'), 'evidence': report['evidence_directory']})
