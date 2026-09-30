"""An interrupted maintenance cleanup names its unfinished paths without reopening what it deleted (``retention``, layer 1)."""
import unittest

from do_math import retention


class CleanupInterruptionTests(unittest.TestCase):
    def test_later_exact_deletion_resolves_an_interrupted_attempt(self):
        runtime = {'history': []}
        retention.record_cleanup_interruption(runtime, ['EX-one'], 'EX-maint', 'inaccessible', history_start=0)
        pending = retention.pending_cleanup_failures(runtime)
        self.assertEqual(pending[0]['path'], 'runs/EX-one')
        self.assertEqual([row['path'] for row in pending], ['runs/EX-one'])
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-next',
            'result': {'deleted': ['runs/other'], 'failures': []}})
        # An unrelated healthy attempt does not clear the older failure.
        self.assertEqual(len(retention.pending_cleanup_failures(runtime)), 1)
        self.assertEqual(retention.pending_cleanup_failures(runtime), pending)
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-next',
            'result': {'deleted': ['runs/EX-one'], 'failures': []}})
        self.assertEqual(retention.pending_cleanup_failures(runtime), [])

    def test_failed_final_save_does_not_reopen_already_deleted_paths(self):
        runtime = {'history': [{'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint',
            'result': {'deleted': ['runs/EX-one'], 'failures': []}}]}
        retention.record_cleanup_interruption(runtime, ['EX-one', 'EX-two'], 'EX-maint',
                                             'save interrupted', history_start=0)
        self.assertEqual([row['path'] for row in retention.pending_cleanup_failures(runtime)], ['runs/EX-two'])
        self.assertEqual(runtime['history'][-1]['completed_paths'], ['runs/EX-one'])


if __name__ == '__main__':
    unittest.main()
