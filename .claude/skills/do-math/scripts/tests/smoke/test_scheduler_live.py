"""T5: owned OS tasks, held/startup evidence, real pythonw/time trigger and cleanup."""
import unittest

from support.scheduler_live import run_scheduler_smoke
from test_categories import test_group


@test_group('resource')
class SchedulerLiveTests(unittest.TestCase):
    def test_held_pythonw_tasks_start_wake_and_uninstall(self):
        report = run_scheduler_smoke()
        self.assertTrue(report['passed'], {'checks': report['checks'],
            'error': report.get('error'), 'evidence': report['evidence_directory']})
        self.assertEqual(set(report['held_outputs']), {'check', 'run-engine', 'wake'})
        for mode, result in report['held_outputs'].items():
            with self.subTest(mode=mode):
                self.assertTrue(report['checks']['held_' + mode + '_startup'])
                self.assertEqual(result, {'outcome': 'held', 'startup': report['held_startups'][mode]})
