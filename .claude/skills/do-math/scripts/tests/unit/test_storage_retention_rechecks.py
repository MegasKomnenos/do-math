"""삭제 직전 현재 상태가 없거나 사라진 실행은 정확한 실패로 보존한다."""
from pathlib import Path
import tempfile
import unittest

from do_math.retention import cleanup, retention_inputs
from support.state_builders import current_state
from support.storage_records import record_store


class RetentionRechecks(unittest.TestCase):
    def test_cleanup_never_deletes_without_current_prerequisites_or_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / 'runs/EX-gone'
            run.mkdir(parents=True)
            (run / 'evidence').write_bytes(b'keep')
            candidate = {'execution_id': 'EX-gone', 'path': 'runs/EX-gone', 'eligible': True, 'inventory': {}}
            for state, reason in ((None, 'current cleanup prerequisites are required'),
                                   (lambda: {'executions': {}}, 'execution disappeared from current state')):
                result = cleanup(root, [candidate], current_state=state)
                self.assertEqual(result, {'deleted': [], 'status': 'degraded', 'failures': [{
                    'path': 'runs/EX-gone', 'error': reason, 'status': 'degraded', 'next_owner': 'maintenance'}]})
                self.assertEqual((run / 'evidence').read_bytes(), b'keep')
            self.assertEqual(cleanup(root, [{**candidate, 'eligible': False}]),
                             {'deleted': [], 'failures': [], 'status': 'healthy'})

    def test_source_aliases_and_protected_roots_come_from_stored_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = record_store(Path(directory))
            head = repo.initialize(*current_state({'sources': [{'id': 'SO-one', 'name': 'lemma',
                'path': 'runtime/artifacts/BA-source/lemma.txt', 'sha256': 'a' * 64}]}))
            _, instance, runtime = repo.load(head)
            rows = repo.load_records(head)[3]
            records, protected = retention_inputs(instance, runtime, rows)
            self.assertEqual(records['lemma'], {'references': ['SO-one']})
            self.assertEqual(records['source:lemma'], {'references': ['SO-one']})
            self.assertEqual(records['SO-one'], {'references': ['runtime/artifacts/BA-source/lemma.txt']})
            self.assertEqual(protected, [row['id'] for row in rows if row.get('id') and
                (row['root'] == 'research' or row['family'] in {'tasks', 'question_links', 'review_cycles'})])


    def test_produced_archive_rejections_preserve_run_then_pinned_cleanup_removes_only_local_bytes(self):
        """Real admission, termination, archive and Repository; no reduced archive or fsync settings."""
        from copy import deepcopy
        import hashlib

        from do_math.activities import finish_activity
        from do_math.execution_lifecycle import transition_execution
        from do_math.retention import archive_run, cleanup_candidates
        from do_math.session_slots import SessionSlots
        from support.entry import entry
        from support.fakes.clock import FakeClock
        from support.fakes.jobs import FakeJobs
        from support.record_builders import execution_state

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'
            run = workspace / 'runs/EX-1'
            run.mkdir(parents=True)
            raw = b'\x00\xff\r\n' + '보관 원문'.encode('utf-8')
            (run / 'evidence.bin').write_bytes(raw)
            clock, jobs = FakeClock(), FakeJobs([])
            instance, runtime = execution_state()
            execution = runtime['executions']['EX-1']
            profile = instance['execution_profiles'][execution['execution_profile_ref']['id']]
            repo = record_store(root / 'repository', clock=clock)
            slots = SessionSlots(runtime, instance, clock=clock, jobs=jobs, host_id=entry().host_id)
            with repo.writer_lock():
                self.assertIs(slots.acquire('EX-1', profile=profile, execution=execution), True)
                self.assertIs(slots.release('EX-1'), True)
                transition_execution(execution, 'stopping', at=clock.now(), reason='cancel before launch')
                transition_execution(execution, 'ended', at=clock.now(), outcome='cancelled')
                finish_activity(runtime, 'AT-1', result_refs=[], unresolved=[], followups=[], at=clock.now())
                head = repo.initialize(instance, runtime)
                artifacts, manifest, termination = archive_run(
                    workspace, 'EX-1', execution, 'runtime/artifacts/BA-local')
                other_run = workspace / 'runs/EX-other'
                other_run.mkdir()
                other_artifacts, _, other_termination = archive_run(
                    workspace, 'EX-other', execution, 'runtime/artifacts/BA-other')
                other_run.rmdir()
                archived = repo.save_with_state(head, instance, runtime,
                    artifacts={**artifacts, **other_artifacts})[0]
                execution['termination'] = {**termination, 'snapshot': archived}
                execution['collection'] = {'retention_manifest': [
                    {**row, 'snapshot': archived} for row in manifest]}
                final = repo.save_with_state(archived, instance, runtime)[0]
                _, stored_i, stored_r = repo.load(final)
                state = {'executions': stored_r['executions'], 'protected_references': [],
                    'approved_execution_ids': {'EX-1'}, 'runtime': stored_r}
                read = lambda path, snapshot: repo.read(path, snapshot)
                good = cleanup_candidates(workspace, **state, read_artifact=read)
                proof = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                self.assertEqual(good, [{'execution_id': 'EX-1', 'path': 'runs/EX-1',
                    'eligible': True, 'reasons': [], 'inventory': {'evidence.bin': proof}}])
                self.assertIs(type(good[0]['eligible']), bool)
                self.assertIs(type(good[0]['inventory']['evidence.bin']['bytes']), int)
                cases = (
                    ('nonobject', ['artifacts_not_verified', 'execution_not_ended',
                                   'invalid_execution_record', 'termination_unconfirmed']),
                    ('identity', ['artifacts_not_verified', 'execution_not_ended',
                                  'invalid_execution_record', 'termination_unconfirmed']),
                    ('live', ['execution_not_ended']),
                    ('termination', ['termination_unconfirmed']),
                    ('foreign_receipt', ['termination_unverified: termination receipt does not confirm this execution']),
                    ('duplicate_path', ['archive_unverified: invalid archive reference']),
                    ('namespace', ['archive_does_not_cover_current_files',
                                   'archive_unverified: invalid immutable archive reference']),
                )
                for mutation, reasons in cases:
                    with self.subTest(mutation=mutation):
                        changed = deepcopy(state)
                        record = changed['executions']['EX-1']
                        if mutation == 'nonobject':
                            changed['executions']['EX-1'] = []
                        elif mutation == 'identity':
                            record['id'] = 'EX-other'
                        elif mutation == 'live':
                            record['status'] = 'running'
                        elif mutation == 'termination':
                            record['termination'] = None
                        elif mutation == 'foreign_receipt':
                            record['termination'] = {**other_termination, 'snapshot': archived}
                        elif mutation == 'duplicate_path':
                            record['collection']['retention_manifest'].append(
                                deepcopy(record['collection']['retention_manifest'][0]))
                        else:
                            record['collection']['retention_manifest'][0]['artifact_ref'] = 'runtime/evidence.bin'
                        candidates = cleanup_candidates(workspace, **changed, read_artifact=read)
                        self.assertEqual(candidates, [{**good[0], 'eligible': False, 'reasons': reasons}])
                        result = cleanup(workspace, good, current_state=lambda: changed, read_artifact=read)
                        self.assertEqual(result, {'deleted': [], 'status': 'degraded', 'failures': [{
                            'path': 'runs/EX-1', 'error': 'cleanup prerequisites changed: ' + ', '.join(reasons),
                            'status': 'degraded', 'next_owner': 'maintenance'}]})
                        self.assertEqual((run / 'evidence.bin').read_bytes(), raw)
                        self.assertEqual(repo.load(), (final, stored_i, stored_r))
                        self.assertEqual({path: repo.read(path, archived) for path in artifacts}, artifacts)
                result = cleanup(workspace, good, current_state=lambda: state, read_artifact=read)
                self.assertEqual(result, {'deleted': ['runs/EX-1'], 'failures': [], 'status': 'healthy'})
                self.assertFalse(run.exists())
                self.assertEqual(repo.load(), (final, stored_i, stored_r))
                self.assertEqual({path: repo.read(path, archived) for path in artifacts}, artifacts)
                self.assertEqual(jobs.launched, [])


if __name__ == '__main__':
    unittest.main()
