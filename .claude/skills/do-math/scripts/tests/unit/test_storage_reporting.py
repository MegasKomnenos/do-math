"""Status and wait projections of one snapshot (``reporting``, layer 2).

``status_report`` receives the store it reads artifacts through, so the status
batch runs on the real ``ResearchRepository`` over the Git port's in-process
fake (설계 4.3). The legacy test replaced ``reporting.ResearchRepository`` with
an autospec double inside ``snapshot_report``; here the repository calls are
observed on the unchanged product (``ObservedCalls``), a changed and a missing
artifact are another writer's commit (``storage_git.rewrite_commit``), and the
wiring of ``snapshot_report`` (open the repository, load, report) runs over the
real Git process in ``boundary/test_storage_reporting.py``.
"""
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math import reporting
from do_math.git_store import GitStateStore
from do_math.repository import ResearchRepository
from record_fixtures import approved_task, stored_surface_state
from support.provider_probes import ObservedCalls
from support.storage_git import rewrite_commit
from support.storage_records import INSTANCE_ID, record_store


def size_query(arguments):
    return list(arguments['paths']), arguments['snapshot'], arguments['missing']


class ReportingTests(unittest.TestCase):
    def test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes(self):
        """About 0.4 s, over the 0.2 s unit budget: three publications and two full status projections of the stored state."""
        raw = b'preserved result'
        paths = ['runtime/artifacts/BA-1/' + str(index) for index in range(12)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = record_store(root / 'repository')
            instance, runtime = stored_surface_state()
            instance.update(id=INSTANCE_ID, workspace=str(root / 'workspace'))
            runtime['activities']['AC-1']['owner_ref'] = INSTANCE_ID
            runtime['executions']['EX-1']['output_files'] = [
                {'path': str(index), 'artifact_ref': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                for index, path in enumerate(paths)]
            head = store.initialize(instance, runtime)
            head = store.save_with_state(head, *store.load(head)[1:], artifacts=dict.fromkeys(paths, raw))[0]

            def report(snapshot):
                _, instance, runtime = store.load(snapshot)
                with ObservedCalls(sizes=ResearchRepository.blob_sizes, read=ResearchRepository.read,
                                   read_many=ResearchRepository.read_many, blob=GitStateStore.read_bytes,
                                   blobs=GitStateStore.read_many, capture={'sizes': size_query}) as calls:
                    value = reporting.status_report(store, snapshot, instance, runtime, requested_areas=['record_storage'])
                # Status reads no artifact bytes, through the repository or below it.
                self.assertEqual([calls.count(name) for name in ('read', 'read_many', 'blob', 'blobs')], [0, 0, 0, 0])
                return value, calls.captured('sizes')
            healthy, queries = report(head)
            self.assertEqual(healthy['inspection']['status'], 'healthy')
            self.assertEqual(queries, [(paths, head, 'omit')])
            # A changed length or a missing artifact blocks; same-length byte changes are for check.
            changed = rewrite_commit(store, head, {paths[0]: raw + b'!', paths[1]: None})
            blocked, queries = report(changed)
        self.assertEqual(queries, [(paths, changed, 'omit')])
        self.assertEqual(blocked['inspection']['status'], 'blocked')
        evidence = {item for row in blocked['inspection']['findings'] for item in row['evidence']}
        self.assertEqual(evidence & set(paths), {paths[0], paths[1]})

    def test_non_task_wait_projection_is_detached_and_printable(self):
        runtime = {'executions': {}, 'queue': [{'id': 'AC-prep', 'role': 'research_preparation',
            'dispatch_wait': {'kind': 'capacity', 'constraint_id': 'BC-old', 'next_owner': 'user'}}]}
        rows = reporting.dispatch_waits(runtime)
        text = '\n'.join(reporting.render_dispatch_waits({'tasks': [], 'dispatch_waits': rows}))
        self.assertIn('AC-prep', text)
        self.assertIn('capacity', text)
        self.assertIn('BC-old', text)
        rows[0]['wait']['kind'] = 'changed'
        self.assertEqual(runtime['queue'][0]['dispatch_wait']['kind'], 'capacity')
        runtime['executions']['EX-live'] = {'status': 'running', 'action': {'id': 'AC-prep'}}
        self.assertEqual(reporting.dispatch_waits(runtime), [])

    def test_task_rows_of_an_ended_instance_carry_no_readiness(self):
        task, instance, runtime = approved_task()
        task['status'] = 'active'
        self.assertEqual(reporting.task_status(instance, runtime)[0]['readiness']['state'], 'ready')
        for ended in ('closed', 'completed'):
            with self.subTest(status=ended):
                row, = reporting.task_status(instance, {**runtime, 'status': ended})
                self.assertIsNone(row['readiness'])
                self.assertEqual(row['waits'], [])


if __name__ == '__main__':
    unittest.main()
